"""VF-08 source structural guard; does NOT execute Unity TextGenerator."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TypographySourceContracts(unittest.TestCase):
    def test_typography_uses_real_unity_font_metrics_without_gameplay_effects(self):
        code = (ROOT / "unity_package/Editor/VufTypographyAudit.cs").read_text()
        for needle in (
            "GetGenerationSettings", "GetPreferredHeight", "TextGenerator",
            "TEXT_OVERFLOW_RISK", "LOW_CONTRAST_REVIEW",
            "TYPOGRAPHY_UNMEASURED", "CANDIDATE_ONLY"
        ):
            if needle == "CANDIDATE_ONLY":
                self.assertIn("candidate-only marker", code)
            else:
                self.assertIn(needle, code)
        self.assertNotIn("AssetDatabase.CreateAsset", code)
        self.assertNotIn("PlayerPrefs", code)
        self.assertNotIn("GrantReward", code)

    def test_typography_window_is_read_only_and_exposes_synthetic_profiles(self):
        window = (ROOT / "unity_package/Editor/VufTypographyLabWindow.cs").read_text()
        dashboard = (ROOT / "unity_package/Editor/VufDashboardWindow.cs").read_text()
        self.assertIn("VufTypographyAudit.Analyze", window)
        self.assertIn("VufResponsiveGeometry.Presets", window)
        self.assertIn("VufTypographyLabWindow.Open()", dashboard)
        self.assertNotIn("PrefabUtility.SaveAsPrefabAsset", window)
        self.assertNotIn("AssetDatabase.CreateAsset", window)

    def test_unity_editmode_tests_cover_real_font_and_no_text_mutation(self):
        test = (ROOT / "unity_package/Tests/Editor/VufTypographyEditModeTests.cs").read_text()
        self.assertEqual(test.count("[Test]"), 5)
        self.assertIn("ContrastMetricMatchesBasicWcagLuminanceExamples", test)
        self.assertIn("AllCoralDraftScreenTextCanBeAnalyzedInThreeMockModes", test)
        self.assertIn("MissingFontIsFlaggedAsUnmeasurableWithoutRewritingText", test)


if __name__ == "__main__":
    unittest.main()
