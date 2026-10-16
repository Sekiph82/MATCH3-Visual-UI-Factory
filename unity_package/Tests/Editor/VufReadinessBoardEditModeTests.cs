using System;
using NUnit.Framework;
using UnityEngine;
using Match3.VisualFactory.Editor;

namespace Match3.VisualFactory.Tests
{
    public sealed class VufReadinessBoardEditModeTests
    {
        [Test]
        public void MissingEvidenceLeavesAllMandatoryGatesOpen()
        {
            var report = VufReadinessBoardWindow.Evaluate(null, null, null);
            Assert.That(report.ProductionApproved, Is.False);
            Assert.That(report.RequiredGates.Count, Is.GreaterThanOrEqualTo(7));
            Assert.That(report.SpriteCount, Is.Zero);
            Assert.That(report.CandidateProfile, Is.EqualTo("NO CANDIDATE"));
        }

        [Test]
        public void StaticCandidateReviewNeverBecomesOwnerAcceptance()
        {
            var screen = VufScreenCatalog.LoadScreens()[26];
            var root = VufScreenShellBuilderWindow.BuildCandidateHierarchy(
                screen, VufScreenCatalog.LoadStyle("Coral_Rescue"), true);
            try
            {
                var marker = root.GetComponent<VufCandidateScreenMarker>();
                var result = VufReadinessBoardWindow.Evaluate(root, null, null);
                Assert.That(result.ProductionApproved, Is.False);
                Assert.That(result.CandidateProfile, Is.EqualTo("Coral_Rescue"));
                Assert.That(result.RequiredGates, Has.Some.Contains("PHYSICAL_DEVICE"));
                Assert.That(result.RequiredGates, Has.Some.Contains("ENGINE_LFX"));
                Assert.That(marker.CandidateStatus, Is.EqualTo("CANDIDATE_NOT_APPROVED"));
            }
            finally { UnityEngine.Object.DestroyImmediate(root); }
        }

        [Test]
        public void ForgedOrIncompleteImportedEvidenceRejected()
        {
            Assert.Throws<ArgumentException>(() =>
                VufReadinessBoardWindow.Evaluate(null,
                    "{\"schema_version\":1,\"stage\":\"OWNER_APPROVED\"}", null));
            Assert.Throws<ArgumentException>(() =>
                VufReadinessBoardWindow.Evaluate(null, null,
                    "{\"stage\":\"PRODUCTION_TRANSLATED\"}"));
        }
    }
}
