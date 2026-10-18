// VUF-M08-001/003/006: one bounded real Unity EditMode contract suite.
// Source authored, NOT executed by ChatGPT. Engine/LFX production parity OPEN.
using System;
using System.Collections.Generic;
using NUnit.Framework;
using Match3.VisualFactory.Editor;

namespace Match3.VisualFactory.Tests
{
    public sealed class VufExternalPackSandboxEditModeTests
    {
        private const string A =
            "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef";
        private const string B =
            "abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789";
        private static VisualAssetManifest Pack()
        {
            return new VisualAssetManifest
            {
                schema_version = 1,
                profile_id = "Coral_Rescue",
                theme_version = "vuf_test_only_1",
                engine_sha = "UNPINNED_NOT_ACCEPTED",
                level_factory_sha = "UNPINNED_NOT_ACCEPTED",
                stage = "TEST_ONLY",
                assets = new [] {
                    new VisualAssetManifest.Asset {
                        asset_id = "Coral_Rescue.ui.home",
                        path = "ui/home.png", sha256 = A,
                        state = "Ready", rights = "REVIEW_PENDING",
                        source_receipt = "artist_source_missing"
                    },
                    new VisualAssetManifest.Asset {
                        asset_id = "Coral_Rescue.fx.tile",
                        path = "fx/tile.png", sha256 = B,
                        state = "Ready", rights = "REVIEW_PENDING",
                        source_receipt = "artist_source_missing"
                    }
                }
            };
        }

        [Test]
        public void TwoSourceAssetsPassUnderTESTONLYNamespaceWithoutEngineClaims()
        {
            var pack = Pack();
            Assert.DoesNotThrow(
                () => VufExternalPackSandboxWindow.ValidateSymbolicPack(pack));
            var map = new Dictionary<string, string> {
                ["ui/home.png"] = A,
                ["fx/tile.png"] = B
            };
            Assert.That(VufExternalPackSandboxWindow.CheckAssetHashes(
                pack, path => map[path]),
                Does.Contain("NOT VERIFIED"));
        }

        [Test]
        public void InvalidPackProfileStageAndEmptyAssetsCannotBeAccepted()
        {
            var pack = Pack();
            pack.profile_id = "Other";
            Assert.Throws<ArgumentException>(() =>
                VufExternalPackSandboxWindow.ValidateSymbolicPack(pack));
            pack = Pack();
            pack.stage = "SHIPPING";
            Assert.Throws<ArgumentException>(() =>
                VufExternalPackSandboxWindow.ValidateSymbolicPack(pack));
            pack = Pack();
            pack.assets = new VisualAssetManifest.Asset[0];
            Assert.Throws<ArgumentException>(() =>
                VufExternalPackSandboxWindow.ValidateSymbolicPack(pack));
        }

        [Test]
        public void MalformedOrDuplicateAssetIDsAndPathsRejectTheEntirePack()
        {
            var pack = Pack();
            pack.assets[1].asset_id = pack.assets[0].asset_id;
            Assert.Throws<ArgumentException>(() =>
                VufExternalPackSandboxWindow.ValidateSymbolicPack(pack));
            pack = Pack();
            pack.assets[1].path = pack.assets[0].path;
            Assert.Throws<ArgumentException>(() =>
                VufExternalPackSandboxWindow.ValidateSymbolicPack(pack));
            pack = Pack();
            pack.assets[1].sha256 = "NOTSHA";
            Assert.Throws<ArgumentException>(() =>
                VufExternalPackSandboxWindow.ValidateSymbolicPack(pack));
        }

        [Test]
        public void TraversalAbsoluteUrlsAndHiddenFilesAreNeverAssetPreviewPaths()
        {
            foreach (string bad in new [] {
                "../secrets.png", "/secret.png", "http://not-trusted.png",
                "private\\source.png", "%2e%2e/secret.png", ".hidden.png",
                "alpha//image.png", "image.psd", "bad/../file.png"
            })
            {
                Assert.That(VufExternalPackSandboxWindow.IsSafeRelativeAssetPath(bad),
                    Is.False, "unsafe: " + bad);
            }
            Assert.That(VufExternalPackSandboxWindow.IsSafeRelativeAssetPath(
                "ui/home.png"), Is.True);
        }

        [Test]
        public void MissingChangedOrForgedShaIsAlwaysRefusedWithoutAssetWrites()
        {
            var pack = Pack();
            Assert.Throws<ArgumentException>(() =>
                VufExternalPackSandboxWindow.CheckAssetHashes(
                    pack, path => path == "ui/home.png" ? A : A));
            Assert.Throws<ArgumentException>(() =>
                VufExternalPackSandboxWindow.CheckAssetHashes(
                    pack, path => null));
            Assert.Throws<ArgumentNullException>(() =>
                VufExternalPackSandboxWindow.CheckAssetHashes(pack, null));
        }

        [Test]
        public void RightsClaimingApprovedOrShippingIsRejectedUntilOwnerReview()
        {
            var pack = Pack();
            pack.assets[0].rights = "OWNER_APPROVED";
            Assert.Throws<ArgumentException>(() =>
                VufExternalPackSandboxWindow.ValidateSymbolicPack(pack));
            pack = Pack();
            pack.assets[1].rights = "SHIPPING";
            Assert.Throws<ArgumentException>(() =>
                VufExternalPackSandboxWindow.ValidateSymbolicPack(pack));
        }

        [Test]
        public void DraftEnglishTurkishAndMissingOfflineLocaleRemainNonGameActions()
        {
            var item = new VufExternalPackSandboxWindow.DraftLocale {
                schema_version = 1,
                profile_id = "Wonder_Pop", locale = "tr",
                stage = "DRAFT_NOT_LOCALIZATION_APPROVED",
                release_allowed = false,
                actual_gameplay_labels_verified = false,
                texts = new VufExternalPackSandboxWindow.DraftTexts {
                    title = "Aday gorsel", action = "BAGLI DEGIL",
                    offline = "Cevrimdisi", loading = "Yukleniyor",
                    disabled = "Devre disi"
                }
            };
            string json = UnityEngine.JsonUtility.ToJson(item);
            Assert.That(VufExternalPackSandboxWindow.ReadDraftLocale(
                json, "Wonder_Pop", "tr"), Does.Contain("NOT TRANSLATION APPROVED"));
            Assert.That(VufExternalPackSandboxWindow.ReadDraftLocale(
                null, "Wonder_Pop", "tr"), Does.Contain("ACTION_DISABLED"));
        }

        [Test]
        public void LocaleCannotForgeReadyToShipIdentityOrWrongGameNamespace()
        {
            var item = new VufExternalPackSandboxWindow.DraftLocale {
                schema_version = 1, profile_id = "Coral_Rescue",
                locale = "en", stage = "DRAFT_NOT_LOCALIZATION_APPROVED",
                texts = new VufExternalPackSandboxWindow.DraftTexts {
                    title = "Candidate", action = "NOT CONNECTED",
                    offline = "Offline", loading = "Loading", disabled = "Disabled"
                }
            };
            string json = UnityEngine.JsonUtility.ToJson(item);
            Assert.Throws<ArgumentException>(() =>
                VufExternalPackSandboxWindow.ReadDraftLocale(
                    json, "Wonder_Pop", "en"));
            item.release_allowed = true;
            Assert.Throws<ArgumentException>(() =>
                VufExternalPackSandboxWindow.ReadDraftLocale(
                    UnityEngine.JsonUtility.ToJson(item), "Coral_Rescue", "en"));
        }

        [Test]
        public void AllFiveExternalProfileNamespacesUseSameNonApprovedRules()
        {
            foreach (string profile in new [] {
                "Coral_Rescue", "Garage_Legends", "Dino_Islands",
                "The_Fractured_Realms", "Wonder_Pop"
            })
            {
                var pack = Pack();
                pack.profile_id = profile;
                foreach (var asset in pack.assets)
                    asset.asset_id = profile + asset.asset_id.Substring(
                        "Coral_Rescue".Length);
                Assert.DoesNotThrow(
                    () => VufExternalPackSandboxWindow.ValidateSymbolicPack(pack));
                Assert.That(pack.stage, Is.EqualTo("TEST_ONLY"));
            }
        }
    }
}
