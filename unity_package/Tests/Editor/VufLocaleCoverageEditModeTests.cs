using System;
using System.Linq;
using NUnit.Framework;
using UnityEngine;
using Match3.VisualFactory.Editor;

namespace Match3.VisualFactory.Tests
{
    public sealed class VufLocaleCoverageEditModeTests
    {
        private static VufLocaleCoverageWindow.Report Build()
        {
            var screens = VufScreenCatalog.LoadScreens();
            var missing = screens.Select(s => s.key)
                .Where(s => s != "home" && s != "gameplay_hud").ToArray();
            var off = screens.Where(s =>
                s.feature_gate == "OFF_UNTIL_ENGINE_POLICY_CONFIRMED")
                .Select(s => s.key).ToArray();
            return new VufLocaleCoverageWindow.Report {
                schema_version = 1,
                stage = "REVIEW_REQUIRED_NOT_APPROVED",
                profile_id = "Coral_Rescue",
                report_type = "OFFLINE_DRAFT_COVERAGE_V01",
                source_manifest_sha256 = new string('a', 64),
                source_contract_sha256 = new string('b', 64),
                policy_off_keys = off,
                shared_placeholder_checked_keys = new string[0],
                warning_codes = new [] {"INCOMPLETE_LOCALE: en", "INCOMPLETE_LOCALE: tr"},
                locales = new [] {
                    new VufLocaleCoverageWindow.LocaleStatus {
                        locale = "en", covered = 2, total = 28,
                        coverage_basis_points = 714,
                        missing_keys = missing, long_copy_review_keys = new string[0]
                    },
                    new VufLocaleCoverageWindow.LocaleStatus {
                        locale = "tr", covered = 2, total = 28,
                        coverage_basis_points = 714,
                        missing_keys = missing, long_copy_review_keys = new string[0]
                    }
                }
            };
        }

        [Test]
        public void DraftEnTrCoverageReadsWithoutEnablingGameBindings()
        {
            var parsed = VufLocaleCoverageWindow.Parse(JsonUtility.ToJson(Build()));
            Assert.That(parsed.locales[0].covered, Is.EqualTo(2));
            Assert.That(parsed.locales[1].locale, Is.EqualTo("tr"));
            Assert.That(parsed.owner_translation_approved, Is.False);
            Assert.That(parsed.game_bindings_enabled, Is.False);
        }

        [Test]
        public void FakeTranslationApprovalOrLiveBindingIsRejected()
        {
            var report = Build();
            report.owner_translation_approved = true;
            Assert.Throws<ArgumentException>(() =>
                VufLocaleCoverageWindow.Parse(JsonUtility.ToJson(report)));
            report.owner_translation_approved = false;
            report.game_bindings_enabled = true;
            Assert.Throws<ArgumentException>(() =>
                VufLocaleCoverageWindow.Parse(JsonUtility.ToJson(report)));
        }

        [Test]
        public void DisabledPolicyAndCoverageMismatchAreRejected()
        {
            var report = Build();
            report.policy_off_keys = new [] {"friends"};
            Assert.Throws<ArgumentException>(() =>
                VufLocaleCoverageWindow.Parse(JsonUtility.ToJson(report)));
            report = Build();
            report.locales[1].coverage_basis_points = 10000;
            Assert.Throws<ArgumentException>(() =>
                VufLocaleCoverageWindow.Parse(JsonUtility.ToJson(report)));
            report = Build();
            report.locales[0].missing_keys = new [] {"not_real"};
            Assert.Throws<ArgumentException>(() =>
                VufLocaleCoverageWindow.Parse(JsonUtility.ToJson(report)));
        }
    }
}
