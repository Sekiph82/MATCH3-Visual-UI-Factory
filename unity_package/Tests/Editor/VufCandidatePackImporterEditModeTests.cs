// M08: Unity source-receipt importer contracts; NO filesystem writes in tests.
using System;
using NUnit.Framework;
using UnityEngine;
using Match3.VisualFactory.Editor;

namespace Match3.VisualFactory.Tests
{
    public sealed class VufCandidatePackImporterEditModeTests
    {
        private const string Sha =
            "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef";

        private static VufCandidatePackImporterWindow.Receipt Receipt()
        {
            var r = new VufCandidatePackImporterWindow.Receipt {
                generator = "VUF_M08_OFFLINE_CANDIDATE_PACK_V01",
                stage = "TEST_ONLY",
                profile_id = "Coral_Rescue",
                image_count = 40,
                file_entries = new VufCandidatePackImporterWindow.Entry[40]
            };
            r.file_entries[0] = new VufCandidatePackImporterWindow.Entry {
                path = "visual_manifest.json", sha256 = Sha
            };
            for (int i = 1; i < r.file_entries.Length; ++i)
                r.file_entries[i] = new VufCandidatePackImporterWindow.Entry {
                    path = "sprites/sample_" + i.ToString("D3") + ".png",
                    sha256 = Sha
                };
            return r;
        }

        [Test]
        public void UnityJsonUtilityAcceptsOnlyUnapprovedExternalReceiptArray()
        {
            var r = VufCandidatePackImporterWindow.ValidateReceipt(
                JsonUtility.ToJson(Receipt()));
            Assert.That(r.file_entries.Length, Is.EqualTo(40));
            Assert.That(r.profile_id, Is.EqualTo("Coral_Rescue"));
            Assert.That(r.release_allowed, Is.False);
            Assert.That(r.owner_visual_approved, Is.False);
        }

        [Test]
        public void ShippingRightsOrGameAuthorityCannotBeEmbeddedInImportedPack()
        {
            var r = Receipt();
            r.release_allowed = true;
            Assert.Throws<ArgumentException>(() =>
                VufCandidatePackImporterWindow.ValidateReceipt(
                    JsonUtility.ToJson(r)));
            r = Receipt();
            r.real_engine_lfx_sha_pinned = true;
            Assert.Throws<ArgumentException>(() =>
                VufCandidatePackImporterWindow.ValidateReceipt(
                    JsonUtility.ToJson(r)));
            r = Receipt();
            r.actual_game_actions = true;
            Assert.Throws<ArgumentException>(() =>
                VufCandidatePackImporterWindow.ValidateReceipt(
                    JsonUtility.ToJson(r)));
        }

        [Test]
        public void MissingManifestDuplicatePathsOrBadHashRefuseWholeBundle()
        {
            var r = Receipt();
            r.file_entries[0].path = "missing_manifest.json";
            Assert.Throws<ArgumentException>(() =>
                VufCandidatePackImporterWindow.ValidateReceipt(
                    JsonUtility.ToJson(r)));
            r = Receipt();
            r.file_entries[1].path = r.file_entries[2].path;
            Assert.Throws<ArgumentException>(() =>
                VufCandidatePackImporterWindow.ValidateReceipt(
                    JsonUtility.ToJson(r)));
            r = Receipt();
            r.file_entries[1].sha256 = "not_sha";
            Assert.Throws<ArgumentException>(() =>
                VufCandidatePackImporterWindow.ValidateReceipt(
                    JsonUtility.ToJson(r)));
        }

        [Test]
        public void TraversalAbsoluteUrlHiddenOrUnsupportedImporterFilesRefused()
        {
            foreach (string unsafePath in new [] {
                "../secrets.json", "image/../../pass.png", "/etc/private.png",
                "https://example.org/p.png", "C:\\Secrets\\a.png",
                "%2e%2e/secret.png", ".hidden.json", "face.psd",
                "A//double.png", "bad file.png"
            })
                Assert.That(VufCandidatePackImporterWindow.SafePath(unsafePath),
                    Is.False, "bad path " + unsafePath);
            Assert.That(VufCandidatePackImporterWindow.SafePath(
                "sprite_atlas/atlas_manifest.json"), Is.True);
            Assert.That(VufCandidatePackImporterWindow.SafePath(
                "fx/bubblerise/reduced_motion.png"), Is.True);
        }
    }
}
