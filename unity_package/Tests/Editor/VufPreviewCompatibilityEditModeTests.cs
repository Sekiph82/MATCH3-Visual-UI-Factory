using System;
using NUnit.Framework;
using UnityEngine;
using Match3.VisualFactory;
using Match3.VisualFactory.Editor;

namespace Match3.VisualFactory.Tests
{
    public sealed class VufPreviewCompatibilityEditModeTests
    {
        private static readonly string Engine = new string('a', 40);
        private static readonly string Lfx = new string('b', 40);

        private static string Manifest(params VisualAssetManifest.Asset[] assets)
        {
            return JsonUtility.ToJson(new VisualAssetManifest {
                schema_version = 1, profile_id = "Coral_Rescue",
                theme_version = "0.1.0", stage = "TEST_ONLY",
                engine_sha = Engine, level_factory_sha = Lfx,
                assets = assets
            });
        }

        private static VisualAssetManifest.Asset Asset(string id, char digit)
        {
            return new VisualAssetManifest.Asset {
                asset_id = "Coral_Rescue." + id,
                path = "icons/" + id + ".png",
                sha256 = new string(digit, 64),
                state = "Ready", rights = "placeholder",
                source_receipt = "source not yet owner approved"
            };
        }

        [Test]
        public void ValidPreviewPinsAreNotActualReleaseOrOwnerAuthority()
        {
            var result = VufPreviewCompatibilityWindow.Evaluate(
                Manifest(Asset("star", 'c')), null,
                "Coral_Rescue", Engine, Lfx);
            Assert.That(result.PinsMatch, Is.True);
            Assert.That(result.CurrentAssets, Is.EqualTo(1));
            Assert.That(result.ReleaseAllowed, Is.False);
            Assert.That(result.RightsVerified, Is.False);
            Assert.That(result.DeviceVerified, Is.False);
            Assert.That(result.EngineLfxIndependentlyAccepted, Is.False);
        }

        [Test]
        public void DriftAndRollbackComparisonRemainReadOnlyData()
        {
            string before = Manifest(Asset("old", 'c'), Asset("star", 'd'));
            string latest = Manifest(Asset("star", 'e'), Asset("new", 'f'));
            var result = VufPreviewCompatibilityWindow.Evaluate(
                latest, before, "Coral_Rescue",
                new string('f', 40), Lfx);
            Assert.That(result.PinsMatch, Is.False);
            Assert.That(result.Mismatches.Count, Is.EqualTo(1));
            Assert.That(result.PreviousCompared, Is.True);
            CollectionAssert.AreEquivalent(new [] {
                "REMOVED: Coral_Rescue.old", "CHANGED: Coral_Rescue.star",
                "ADDED: Coral_Rescue.new"
            }, result.AssetChanges);
            Assert.That(result.ReleaseAllowed, Is.False);
        }

        [Test]
        public void DuplicateIdsAndWrongThemeAreRejected()
        {
            Assert.Throws<ArgumentException>(() =>
                VufPreviewCompatibilityWindow.Evaluate(
                    Manifest(Asset("same", 'a'), Asset("same", 'b')),
                    null, "Coral_Rescue", Engine, Lfx));
            Assert.Throws<ArgumentException>(() =>
                VufPreviewCompatibilityWindow.Evaluate(
                    Manifest(), null, "Wonder_Pop", Engine, Lfx));
        }

        [Test]
        public void UnsafePathAndPretendApprovedManifestCannotBeLoaded()
        {
            var unsafeAsset = Asset("suspicious", 'c');
            unsafeAsset.path = "../credentials.json";
            Assert.Throws<ArgumentException>(() =>
                VufPreviewCompatibilityWindow.Evaluate(
                    Manifest(unsafeAsset), null,
                    "Coral_Rescue", Engine, Lfx));
            var approved = new VisualAssetManifest {
                schema_version = 1, stage = "APPROVED",
                profile_id = "Coral_Rescue", engine_sha = Engine,
                level_factory_sha = Lfx, assets = new VisualAssetManifest.Asset[0]
            };
            Assert.Throws<ArgumentException>(() =>
                VufPreviewCompatibilityWindow.Evaluate(
                    JsonUtility.ToJson(approved), null,
                    "Coral_Rescue", Engine, Lfx));
        }
    }
}
