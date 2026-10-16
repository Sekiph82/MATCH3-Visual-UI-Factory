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
        public void ForgedOrInconsistentPixelReportsAreRejected()
        {
            var report = Synthetic();
            report.stage = "OWNER_APPROVED";
            Assert.Throws<ArgumentException>(() =>
                VufSpriteQaReportWindow.ParseReport(JsonUtility.ToJson(report)));

            report = Synthetic();
            report.source_rights_verified = true;
            Assert.Throws<ArgumentException>(() =>
                VufSpriteQaReportWindow.ParseReport(JsonUtility.ToJson(report)));

            report = Synthetic();
            report.warning_count = 0;
            Assert.Throws<ArgumentException>(() =>
                VufSpriteQaReportWindow.ParseReport(JsonUtility.ToJson(report)));

            report = Synthetic();
            report.sprites[0].visible_bbox_top_left = null;
            Assert.Throws<ArgumentException>(() =>
                VufSpriteQaReportWindow.ParseReport(JsonUtility.ToJson(report)));

            report = Synthetic();
            report.sprites[0].alpha_coverage_basis_points = 4999;
            Assert.Throws<ArgumentException>(() =>
                VufSpriteQaReportWindow.ParseReport(JsonUtility.ToJson(report)));

            report = Synthetic();
            report.sprites[0].source_sha256_recorded = new string('g', 64);
            Assert.Throws<ArgumentException>(() =>
                VufSpriteQaReportWindow.ParseReport(JsonUtility.ToJson(report)));

            report = Synthetic();
            report.palette_review = new VufSpriteQaReportWindow.PaletteFinding {
                profile_id = "Coral_Rescue", stage = "DRAFT_NOT_OWNER_APPROVED",
                contrast_checks = new[] {
                    new VufSpriteQaReportWindow.ContrastFinding {
                        pair = "text_on_surface", ratio = 5f,
                        advisory_minimum = 4.5f, review = false
                    },
                    new VufSpriteQaReportWindow.ContrastFinding {
                        pair = "cta_label_on_cta", ratio = 5f,
                        advisory_minimum = 4.5f, review = false
                    },
                    new VufSpriteQaReportWindow.ContrastFinding {
                        pair = "accent_on_background", ratio = 4f,
                        advisory_minimum = 3f, review = false
                    }
                }
            };
            Assert.DoesNotThrow(() =>
                VufSpriteQaReportWindow.ParseReport(JsonUtility.ToJson(report)));
            report.palette_review.contrast_checks[0].ratio = 1f;
            Assert.Throws<ArgumentException>(() =>
                VufSpriteQaReportWindow.ParseReport(JsonUtility.ToJson(report)));
        }
    }
}
