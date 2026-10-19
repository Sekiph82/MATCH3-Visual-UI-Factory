// M11: actual Unity JSON candidate/review gates. Source tests do NOT sign
// rights, exercise a production build, import Engine or verify M08 atlas.
using System;
using NUnit.Framework;
using UnityEngine;
using Match3.VisualFactory.Editor;

namespace Match3.VisualFactory.Tests
{
    public sealed class VufM11CandidateReleaseEditModeTests
    {
        private const string Hex64 =
            "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef";
        private const string Engine =
            "e84d65ab712dddc534cbdb3a30cfe2d7930cea8a";
        private const string Lfx =
            "d8d0b37ce71c4e2c0bdb72f9ed1d2a48068281c3";

        private static VufM11CandidateReleaseReviewWindow.Candidate Candidate()
        {
            var c = new VufM11CandidateReleaseReviewWindow.Candidate {
                schema_version = 1,
                stage = "VUF_M11_REVIEW_ONLY_NOT_PRODUCTION",
                profile_id = "Coral_Rescue",
                engine_observed_git_sha = Engine,
                lfx_observed_git_sha = Lfx,
                upstream_pin_state =
                    "OBSERVED_UNACCEPTED_NOT_REPLAY_VERIFIED",
                source_manifest_sha256 = Hex64,
                source_receipt_sha256 = Hex64,
                content_identity_sha256 = Hex64,
                artifacts = new VufM11CandidateReleaseReviewWindow.Asset[45]
            };
            c.artifacts[0] = new VufM11CandidateReleaseReviewWindow.Asset {
                path = "visual_manifest.json", sha256 = Hex64
            };
            for (int i=1; i<45; ++i)
                c.artifacts[i] = new VufM11CandidateReleaseReviewWindow.Asset {
                    path = "sprites/sample_" + i.ToString("D3") + ".png",
                    sha256 = Hex64
                };
            return c;
        }

        [Test]
        public void ValidUnapprovedCandidateMetadataCanOnlyMeanReviewStage()
        {
            var payload = JsonUtility.ToJson(Candidate());
            var parsed =
                VufM11CandidateReleaseReviewWindow.ValidateManifest(payload);
            Assert.That(parsed.profile_id, Is.EqualTo("Coral_Rescue"));
            Assert.That(parsed.engine_observed_git_sha, Is.EqualTo(Engine));
            Assert.That(parsed.lfx_observed_git_sha, Is.EqualTo(Lfx));
            Assert.That(parsed.release_allowed, Is.False);
            Assert.That(parsed.owner_visual_approved, Is.False);
        }

        [Test]
        public void FabricatedProductionRightsOrFinalReplayClaimsAreRejected()
        {
            foreach (string key in new [] {
                "release_allowed", "owner_visual_approved", "licensed_art_approved",
                "engine_abi_accepted", "lfx_replay_accepted",
                "final_game_action_bound", "player_build_tested",
                "device_gpu_approved"
            })
            {
                var c = Candidate();
                var field = typeof(VufM11CandidateReleaseReviewWindow.Candidate)
                    .GetField(key);
                Assert.That(field, Is.Not.Null, key);
                field.SetValue(c, true);
                Assert.Throws<ArgumentException>(() =>
                    VufM11CandidateReleaseReviewWindow.ValidateManifest(
                        JsonUtility.ToJson(c)), key);
            }
        }

        [Test]
        public void UnknownProfilesAndWrongPinLengthFailClosed()
        {
            var c = Candidate();
            c.profile_id = "Illegal_Original_Game";
            Assert.Throws<ArgumentException>(() =>
                VufM11CandidateReleaseReviewWindow.ValidateManifest(
                    JsonUtility.ToJson(c)));
            c = Candidate();
            c.lfx_observed_git_sha = Hex64;
            Assert.Throws<ArgumentException>(() =>
                VufM11CandidateReleaseReviewWindow.ValidateManifest(
                    JsonUtility.ToJson(c)));
            c = Candidate();
            c.upstream_pin_state = "RELEASE_ACCEPTED";
            Assert.Throws<ArgumentException>(() =>
                VufM11CandidateReleaseReviewWindow.ValidateManifest(
                    JsonUtility.ToJson(c)));
        }

        [Test]
        public void DuplicateSourcesHiddenSecretsAndTraversalAreRejected()
        {
            var c = Candidate();
            c.artifacts[1].path = c.artifacts[0].path;
            Assert.Throws<ArgumentException>(() =>
                VufM11CandidateReleaseReviewWindow.ValidateManifest(
                    JsonUtility.ToJson(c)));
            foreach (var bad in new [] {
                "../PRIVATE/license.json", "secrets/.password.json",
                "Assets\\Private\\original.png",
                "https://bad.test/art.png", ".env.json",
                "C:\\Owner\\source.png", "%2e%2e/owner.json",
                "original.psd", "A//image.png"
            })
                Assert.That(
                    VufM11CandidateReleaseReviewWindow.SafeRelativeFile(bad),
                    Is.False, bad);
            Assert.That(
                VufM11CandidateReleaseReviewWindow.SafeRelativeFile(
                    "sprite_atlas/atlas.png"), Is.True);
        }

        [Test]
        public void EmptyAndOversizeMetadataCannotBeAccepted()
        {
            Assert.Throws<ArgumentException>(() =>
                VufM11CandidateReleaseReviewWindow.ValidateManifest(null));
            var c = Candidate();
            c.artifacts = new VufM11CandidateReleaseReviewWindow.Asset[0];
            Assert.Throws<ArgumentException>(() =>
                VufM11CandidateReleaseReviewWindow.ValidateManifest(
                    JsonUtility.ToJson(c)));
            Assert.That(VufM11CandidateReleaseReviewWindow.ValidHex(
                Engine, 40), Is.True);
            Assert.That(VufM11CandidateReleaseReviewWindow.ValidHex(
                Hex64, 40), Is.False);
        }
    }
}
