"""R43 reuses the established BSD3/MIT donor-backed screen composers.

Source-only regression. Does not replace real local Unity EditMode test.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ShellBridgeContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        folder = ROOT / "unity_package/Editor"
        cls.bridge = (folder / "VufScreenShellLayoutBridge.cs").read_text()
        cls.shell = (folder / "VufScreenShellBuilderWindow.cs").read_text()
        cls.tests = (ROOT / "unity_package/Tests/Editor/"
                     "VufShellLayoutBridgeEditModeTests.cs").read_text()
        cls.ledger = (ROOT / "docs/VUF_DONOR_SOURCE_LEDGER.md").read_text()

    def test_existing_twenty_eight_screen_shells_now_use_internal_donors(self):
        self.assertIn("VufScreenShellLayoutBridge.Enhance(root, spec, style);",
                      self.shell)
        self.assertIn("VufThemeMotifDecor.Apply(safe, style)", self.bridge)
        self.assertIn("VufPageComposition.Compose(safe, style, page);",
                      self.bridge)
        self.assertIn("VufCandidateMotionKit.Attach(safe, page);",
                      self.bridge)
        self.assertIn("AddComponent<NonDrawingGraphic>()", self.bridge)

    def test_policy_locked_and_candidate_only_status_stay_immutable(self):
        self.assertIn('marker.CandidateStatus != "CANDIDATE_NOT_APPROVED"',
                      self.bridge)
        self.assertIn('"OFF_UNTIL_ENGINE_POLICY_CONFIRMED"', self.bridge)
        self.assertIn("VUF_28ScreenInputShield", self.bridge)
        self.assertIn("shield.raycastTarget = true;", self.bridge)
        self.assertIn("marker.FeatureGate != screen.feature_gate", self.bridge)
        self.assertNotIn("AssetDatabase", self.bridge)
        self.assertNotIn("PrefabUtility", self.bridge)
        self.assertNotIn("UnityWebRequest", self.bridge)

    def test_editor_suite_is_actual_multi_theme_and_policy_regression_source(self):
        self.assertEqual(self.tests.count("[Test]"), 4)
        self.assertIn("Assert.That(inspected, Is.EqualTo(140))", self.tests)
        self.assertIn("PolicyLockedSocialPagesNeverGainRealInteraction", self.tests)
        self.assertIn("AllFiveThemesAndTwentyEightCoralShells", self.tests)

    def test_donor_first_decision_and_guid_source_safety(self):
        self.assertIn("R43", self.ledger)
        for name in ("VufScreenShellLayoutBridge.cs.meta",
                     "VufShellLayoutBridgeEditModeTests.cs.meta"):
            matches = list((ROOT / "unity_package").rglob(name))
            self.assertEqual(len(matches), 1, name)
            self.assertIn("guid:", matches[0].read_text())


if __name__ == "__main__":
    unittest.main()
