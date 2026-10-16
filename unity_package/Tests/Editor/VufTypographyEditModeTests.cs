using System;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.UI;
using Match3.VisualFactory.Editor;

namespace Match3.VisualFactory.Tests
{
    public sealed class VufTypographyEditModeTests
    {
        private static Text FindText(GameObject root, string slot)
        {
            foreach (Text label in root.GetComponentsInChildren<Text>(true))
                if (label.name == slot) return label;
            throw new InvalidOperationException("missing label: " + slot);
        }

        [Test]
        public void ContrastMetricMatchesBasicWcagLuminanceExamples()
        {
            Assert.That(VufTypographyAudit.Contrast(Color.white, Color.black),
                Is.EqualTo(21f).Within(.002f));
            Assert.That(VufTypographyAudit.Contrast(Color.black, Color.black),
                Is.EqualTo(1f).Within(.001f));
            Assert.That(VufTypographyAudit.Contrast(
                new Color(1f, 1f, 1f, .5f), Color.black), Is.EqualTo(0f));
        }

        [Test]
        public void AllCoralDraftScreenTextCanBeAnalyzedInThreeMockModes()
        {
            var profiles = VufScreenCatalog.LoadStyle("Coral_Rescue");
            int count = 0;
            foreach (var screen in VufScreenCatalog.LoadScreens())
            foreach (string locale in VufReviewStateCatalog.Locales)
            {
                GameObject root = VufScreenShellBuilderWindow.BuildCandidateHierarchy(
                    screen, profiles, false);
                try
                {
                    VufReviewStateCatalog.Apply(root, screen, "Ready", locale);
                    string heading = FindText(root, "Heading").text;
                    var report = VufTypographyAudit.Analyze(root,
                        VufResponsiveGeometry.Presets[0]);
                    Assert.That(report.DeviceName,
                        Is.EqualTo(VufResponsiveGeometry.Presets[0].Name));
                    Assert.That(report.Items.Count, Is.GreaterThanOrEqualTo(4),
                        "Each candidate screen exposes at least its four primary text slots.");
                    Assert.That(report.Items.TrueForAll(item => item.MeasurementAvailable),
                        Is.True, "Every authored text slot must receive a real TextGenerator measurement.");
                    Assert.That(root.GetComponent<VufCandidateScreenMarker>().CandidateStatus,
                        Is.EqualTo("CANDIDATE_NOT_APPROVED"));
                    Assert.That(FindText(root, "Heading").text, Is.EqualTo(heading));
                    count++;
                }
                finally { UnityEngine.Object.DestroyImmediate(root); }
            }
            Assert.That(count, Is.EqualTo(28 * 3));
        }

        [Test]
        public void MissingFontIsFlaggedAsUnmeasurableWithoutRewritingText()
        {
            var screen = VufScreenCatalog.LoadScreens()[26];
            var root = VufScreenShellBuilderWindow.BuildCandidateHierarchy(screen,
                VufScreenCatalog.LoadStyle("Wonder_Pop"), true);
            try
            {
                var heading = FindText(root, "Heading");
                string before = heading.text;
                heading.font = null;
                var report = VufTypographyAudit.Analyze(root,
                    VufResponsiveGeometry.Presets[1]);
                Assert.That(report.UnmeasuredCount, Is.GreaterThan(0));
                Assert.That(report.Warnings.Exists(w =>
                    w.StartsWith("TYPOGRAPHY_UNMEASURED:")), Is.True);
                Assert.That(heading.text, Is.EqualTo(before));
            }
            finally { UnityEngine.Object.DestroyImmediate(root); }
        }

        [Test]
        public void LowContrastTestColorsProduceReviewWarning()
        {
            var screen = VufScreenCatalog.LoadScreens()[26];
            var root = VufScreenShellBuilderWindow.BuildCandidateHierarchy(screen,
                VufScreenCatalog.LoadStyle("Dino_Islands"), false);
            try
            {
                var label = FindText(root, "Heading");
                var image = label.GetComponentInParent<Image>();
                Assert.That(image, Is.Not.Null);
                label.color = image.color;
                var report = VufTypographyAudit.Analyze(root,
                    VufResponsiveGeometry.Presets[0]);
                Assert.That(report.LowContrastCount, Is.GreaterThan(0));
                Assert.That(report.Warnings.Exists(w =>
                    w.StartsWith("LOW_CONTRAST_REVIEW:")), Is.True);
            }
            finally { UnityEngine.Object.DestroyImmediate(root); }
        }

        [Test]
        public void StressCopyCanBeMeasuredOnFiveSimulatedDeviceShapes()
        {
            var screen = VufScreenCatalog.LoadScreens()[26];
            var root = VufScreenShellBuilderWindow.BuildCandidateHierarchy(screen,
                VufScreenCatalog.LoadStyle("Coral_Rescue"), false);
            try
            {
                VufReviewStateCatalog.Apply(root, screen, "Pending", "stress");
                foreach (var device in VufResponsiveGeometry.Presets)
                {
                    var report = VufTypographyAudit.Analyze(root, device);
                    Assert.That(report.Items.Count, Is.EqualTo(4),
                        "Each candidate screen exposes four authored text slots.");
                    Assert.That(report.Items.TrueForAll(item => item.MeasurementAvailable),
                        Is.True, "Every authored text slot must receive a real TextGenerator measurement.");
                    Assert.That(report.OverflowCount, Is.GreaterThanOrEqualTo(0));
                    Assert.That(report.LowContrastCount, Is.GreaterThanOrEqualTo(0));
                    Assert.That(report.DeviceName, Is.EqualTo(device.Name));
                }
            }
            finally { UnityEngine.Object.DestroyImmediate(root); }
        }
    }
}
