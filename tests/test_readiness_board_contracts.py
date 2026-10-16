"""VF-09 cross-module evidence board contracts (source only, not GUI tests)."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ReadinessBoardSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / "unity_package/Editor/VufReadinessBoardWindow.cs").read_text()

    def test_never_offers_production_approval_or_gameplay_state(self):
        self.assertIn("ProductionApproved => false", self.source)
        self.assertIn("ORIGINAL_ART_RIGHTS:", self.source)
        self.assertIn("OWNER_VISUAL_APPROVAL:", self.source)
        self.assertIn("PHYSICAL_DEVICE:", self.source)
        self.assertIn("ENGINE_LFX:", self.source)
        self.assertNotIn("AssetDatabase.CreateAsset", self.source)
        self.assertNotIn("PrefabUtility.SaveAsPrefabAsset", self.source)
        self.assertNotIn("PlayerPrefs", self.source)

    def test_validated_read_only_reports_feed_five_device_checks(self):
        self.assertIn("VufSpriteQaReportWindow.ParseReport", self.source)
        self.assertIn("VufLocaleCoverageWindow.Parse", self.source)
        self.assertIn("VufTypographyAudit.Analyze", self.source)
        self.assertIn("VufResponsiveGeometry.Analyze", self.source)
        self.assertIn("VufResponsiveGeometry.Presets.Length", self.source)

    def test_board_appears_in_editor_and_has_negative_nunit_tests(self):
        dashboard = (ROOT / "unity_package/Editor/VufDashboardWindow.cs").read_text()
        self.assertIn("VufReadinessBoardWindow.Open()", dashboard)
        tests = (ROOT / "unity_package/Tests/Editor/VufReadinessBoardEditModeTests.cs").read_text()
        self.assertEqual(tests.count("[Test]"), 3)
        self.assertIn("ForgedOrIncompleteImportedEvidenceRejected", tests)


if __name__ == "__main__":
    unittest.main()
