using System;
using NUnit.Framework;
using UnityEngine;
using Match3.VisualFactory.Editor;

namespace Match3.VisualFactory.Tests
{
    public class VufSpriteQaEditModeTests
    {
        private static VufSpriteQaReportWindow.Report Synthetic()
        {
            return new VufSpriteQaReportWindow.Report {
                schema_version = 1, stage = "REVIEW_REQUIRED_NOT_OWNER_APPROVED",
                generator = "VF09_PIXEL_HEALTH_V01",
                file_count = 1, total_source_bytes = 120, warning_count = 1,
                sprites = new[] { new VufSpriteQaReportWindow.SpriteFinding {
                    filename = "test.png", source_sha256_recorded = new string('a', 64),
                    dimensions = new[] {2, 2}, visible_bbox_top_left = new[] {0, 0, 2, 2},
                    visible_pixels = 2, alpha_coverage_basis_points = 5000,
                    warnings = new[] {"CANVAS_BOUNDARY_TOUCH"}
                }}
            };
        }

        [Test]
        public void ReadOnlyPixelReportParses()
        {
            var parsed = VufSpriteQaReportWindow.ParseReport(JsonUtility.ToJson(Synthetic()));
            Assert.That(parsed.file_count, Is.EqualTo(1));
            Assert.That(parsed.source_rights_verified, Is.False);
        }

        [Test]
        public void ForgedApprovalOrWarningsAreRejected()
        {
            var report = Synthetic();
            report.stage = "OWNER_APPROVED";
            Assert.Throws<ArgumentException>(() =>
                VufSpriteQaReportWindow.ParseReport(JsonUtility.ToJson(report)));
            report.stage = "REVIEW_REQUIRED_NOT_OWNER_APPROVED";
            report.warning_count = 0;
            Assert.Throws<ArgumentException>(() =>
                VufSpriteQaReportWindow.ParseReport(JsonUtility.ToJson(report)));
        }
    }
}
