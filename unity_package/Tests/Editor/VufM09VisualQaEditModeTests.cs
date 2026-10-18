// Existing M09-001/002/003/006/012 source tests.
// Real Unity component geometry/typography; screenshot capture is manual GUI.
// No GameObject can be persisted or claim an owner/art/physical device PASS.
using System;
using NUnit.Framework;
using UnityEngine;
using Match3.VisualFactory.Editor;

namespace Match3.VisualFactory.Tests
{
    public sealed class VufM09VisualQaEditModeTests
    {
        [Test]
        public void FullFiveProfileCoralDraftStateLocaleDeviceGridIs16800AndBounded()
        {
            Assert.That(VufM09MatrixAudit.MatrixSize(28), Is.EqualTo(16800));
            Assert.Throws<ArgumentException>(() =>
                VufM09MatrixAudit.MatrixSize(29));
            Assert.That(VufM09MatrixAudit.Profiles.Length, Is.EqualTo(5));
            Assert.That(VufReviewStateCatalog.States.Length, Is.EqualTo(8));
            Assert.That(VufReviewStateCatalog.Locales.Length, Is.EqualTo(3));
            Assert.That(VufResponsiveGeometry.Presets.Length, Is.EqualTo(5));
        }

        [Test]
        public void ActualUnityMatrixCellUsesCoralScreenContractAndNeverSelfApproves()
        {
            var row = VufM09MatrixAudit.Inspect(0);
            Assert.That(row.Profile, Is.EqualTo("Coral_Rescue"));
            Assert.That(row.ScreenId, Is.EqualTo("COR-01"));
            Assert.That(row.State, Is.EqualTo("Ready"));
            Assert.That(row.Locale, Is.EqualTo("en"));
            Assert.That(row.Scope, Is.EqualTo(
                "CORAL_DRAFT_SCREEN_NOT_AVAILABLE_IN_DEMO"));
            Assert.That(row.OwnerApproved, Is.False);
            Assert.That(row.ReleaseAllowed, Is.False);
            Assert.That(row.DeviceVerified, Is.False);
            Assert.That(row.ArtRightsVerified, Is.False);
        }

        [Test]
        public void OtherFourGamesCannotClaimIndependentCoralScreenContract()
        {
            // One full game's rows: 28 * 8 * 3 * 5 = 3360.
            var row = VufM09MatrixAudit.Inspect(3360);
            Assert.That(row.Profile, Is.EqualTo("Garage_Legends"));
            Assert.That(row.ScreenId, Is.EqualTo("COR-01"));
            Assert.That(row.Scope, Is.EqualTo(
                "N_A_FOREIGN_GAME_USING_CORAL_DRAFT_CONTRACT"));
            Assert.That(row.Warnings,
                Does.Contain("NO_OWN_GAME_SCREEN_TAXONOMY: Coral shell is style preview"));
            Assert.That(VufM09MatrixAudit.MechanicallyClean(row), Is.False);
        }

        [Test]
        public void EightStateThreeLocaleCellOrderIsDeterministicForRealUnityPreview()
        {
            var first = VufM09MatrixAudit.Inspect(0);
            var secondDevice = VufM09MatrixAudit.Inspect(1);
            var localeTr = VufM09MatrixAudit.Inspect(5);
            var stateLoading = VufM09MatrixAudit.Inspect(15);
            Assert.That(first.Device, Is.Not.EqualTo(secondDevice.Device));
            Assert.That(localeTr.Locale, Is.EqualTo("tr"));
            Assert.That(stateLoading.State, Is.EqualTo("Loading"));
            Assert.That(first.ScreenKey, Is.EqualTo(stateLoading.ScreenKey));
        }

        [Test]
        public void PolicyOffFeatureGateRemainsNonActionableEvenWithCleanTypography()
        {
            // COR-13 events_hub is policy OFF, 12*8*3*5 (12th screen).
            var row = VufM09MatrixAudit.Inspect(12 * 8 * 3 * 5);
            Assert.That(row.ScreenId, Is.EqualTo("COR-13"));
            Assert.That(row.FeatureGate,
                Is.EqualTo("OFF_UNTIL_ENGINE_POLICY_CONFIRMED"));
            Assert.That(row.Warnings, Does.Contain("POLICY_OFF_NO_GAME_ACTION"));
            Assert.That(VufM09MatrixAudit.MechanicallyClean(row), Is.False);
        }

        [Test]
        public void MatrixSlicesRejectUnknownOrOverlongRequestsFailClosed()
        {
            Assert.Throws<ArgumentOutOfRangeException>(() =>
                VufM09MatrixAudit.Inspect(-1));
            Assert.Throws<ArgumentOutOfRangeException>(() =>
                VufM09MatrixAudit.Inspect(16800));
            Assert.Throws<ArgumentOutOfRangeException>(() =>
                VufM09MatrixAudit.InspectBatch(0, 33));
            Assert.Throws<ArgumentOutOfRangeException>(() =>
                VufM09MatrixAudit.InspectBatch(16799, 2));
            var batch = VufM09MatrixAudit.InspectBatch(0, 2);
            Assert.That(batch.Count, Is.EqualTo(2));
            Assert.That(batch[0].Index, Is.Zero);
            Assert.That(batch[1].Index, Is.EqualTo(1));
        }

        [Test]
        public void RenderCaptureCannotUseUnapprovedPersistentSceneOrAbsurdResolution()
        {
            var source = new GameObject("NOT_EDITOR_CANDIDATE",
                typeof(RectTransform), typeof(Canvas));
            try
            {
                Assert.Throws<ArgumentException>(() =>
                    VufM09RenderCapture.CaptureCandidate(source, 360, 640, true));
                Assert.Throws<ArgumentException>(() =>
                    VufM09RenderCapture.CaptureCandidate(source, 36000, 640, false));
                Assert.Throws<ArgumentException>(() =>
                    VufM09RenderCapture.CaptureCandidate(null, 360, 640, false));
            }
            finally { UnityEngine.Object.DestroyImmediate(source); }
        }

        [Test]
        public void PhoneTabletLandscapeReviewPixelsPreserveSyntheticDeviceAspect()
        {
            foreach (var device in VufResponsiveGeometry.Presets)
            {
                Vector2Int size = VufM09OwnerVisualQaWindow.ReviewSize(device);
                Assert.That(size.x, Is.InRange(160, 720));
                Assert.That(size.y, Is.InRange(160, 1280));
                Assert.That((float)size.x / size.y,
                    Is.EqualTo((float)device.Width / device.Height)
                    .Within(.004f), device.Name);
            }
        }

        [Test]
        public void MechanicalPassCanNeverSignOffHumanOrRealHardwareEvidence()
        {
            var row = VufM09MatrixAudit.Inspect(0);
            Assert.That(VufM09MatrixAudit.HumanApproved(row), Is.False);
            Assert.That(VufM09MatrixAudit.RealDeviceAccepted(row), Is.False);
            Assert.That(row.ScreenshotCaptured, Is.False);
        }
    }
}
