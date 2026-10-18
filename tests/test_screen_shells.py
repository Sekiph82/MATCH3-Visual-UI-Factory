"""R08 authoring-only 28-screen contract and byte-parity checks."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Tools"))
from validate_repo_structure import validate_structure

CANONICAL = ROOT / "schemas/coral-experiences.v1.json"
MIRROR = ROOT / "unity_package/Editor/Resources/coral-experiences.v1.json"
STYLES = ROOT / "factory/visual_director/style_profiles.v1.json"
STYLE_MIRROR = ROOT / "unity_package/Editor/Resources/style_profiles.v1.json"


class CoralScreenShellContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.screens = json.loads(CANONICAL.read_text())["screens"]

    def test_28_coral_draft_experiences_present(self):
        self.assertEqual(len(self.screens), 28)
        self.assertEqual([s["id"] for s in self.screens],
                         ["COR-%02d" % i for i in range(1, 29)])
        self.assertEqual([s["key"] for s in self.screens][-2:],
                         ["home", "gameplay_hud"])

    def test_all_28_remain_gated_and_not_claimed_complete(self):
        self.assertTrue(all(s["available_in_demo"] is False for s in self.screens))
        self.assertTrue(all(s["runtime_ui_required"] is True for s in self.screens))
        self.assertTrue(all(s["feature_gate"] in (
            "REQUIRES_ENGINE_OR_GAME_BINDING",
            "OFF_UNTIL_ENGINE_POLICY_CONFIRMED"
        ) for s in self.screens))

    def test_social_and_event_pages_default_off(self):
        features = {s["key"]: s for s in self.screens}
        for key in ("friends", "leaderboard", "tournament", "season_pass", "events_hub"):
            self.assertEqual(features[key]["feature_gate"],
                             "OFF_UNTIL_ENGINE_POLICY_CONFIRMED")

    def test_coral_unity_package_mirror_is_byte_identical(self):
        self.assertEqual(CANONICAL.read_bytes(), MIRROR.read_bytes())
        self.assertEqual(STYLES.read_bytes(), STYLE_MIRROR.read_bytes())

    def test_repo_structure_pins_mirrors_and_unity_meta(self):
        result = validate_structure()
        self.assertGreaterEqual(result["unique_guids"], 15)

    def test_real_uGUI_buttons_are_disabled_in_screen_shell_source(self):
        script = (ROOT / "unity_package/Editor/VufScreenShellBuilderWindow.cs").read_text()
        self.assertIn("AddComponent<Button>()", script)
        self.assertIn("button.interactable = false", script)
        self.assertIn("PrefabUtility.SaveAsPrefabAsset", script)
        self.assertIn("VufCandidateScreenMarker", script)
        self.assertIn("VufSafeAreaFitter", script)
        self.assertIn("OFF_UNTIL_ENGINE_POLICY_CONFIRMED", script)
        self.assertNotIn("PlayerPrefs", script)

    def test_runtime_marker_always_remains_unapproved(self):
        script = (ROOT / "unity_package/Runtime/VufCandidateScreenMarker.cs").read_text()
        self.assertIn('candidateStatus = "CANDIDATE_NOT_APPROVED"', script)
        self.assertNotIn('candidateStatus = "APPROVED"', script)
        self.assertNotIn("GrantReward", script)

    def test_editor_loader_rejects_unexpected_schema_or_status(self):
        script = (ROOT / "unity_package/Editor/VufScreenCatalog.cs").read_text()
        self.assertIn("CONTRACT_DRAFT_NOT_IMPLEMENTED", script)
        self.assertIn("DRAFT_NOT_OWNER_APPROVED", script)
        self.assertIn("doc.screens.Length != 28", script)
        self.assertIn("Incomplete game Style Bible set", script)

    def test_unity_editmode_test_suite_is_source_only_and_discoverable(self):
        package = json.loads((ROOT / "Packages/manifest.json").read_text())
        self.assertEqual(package["testables"], ["com.match3.visual-factory"])
        test_source = (ROOT / "unity_package/Tests/Editor/VufCatalogEditModeTests.cs").read_text()
        self.assertEqual(test_source.count("[Test]"), 19)
        asm = json.loads((ROOT / "unity_package/Tests/Editor/Match3.VisualFactory.Editor.Tests.asmdef").read_text())
        self.assertEqual(asm["name"], "Match3.VisualFactory.Editor.Tests")
        self.assertEqual(asm["defineConstraints"], ["UNITY_INCLUDE_TESTS"])
        self.assertIn("TestAssemblies", asm["optionalUnityReferences"])

    def test_production_queue_is_view_only_and_cannot_approve(self):
        code = (ROOT / "unity_package/Editor/VufProductionQueueWindow.cs").read_text()
        self.assertIn("READ_ONLY_NOT_OWNER_APPROVAL", code)
        self.assertIn("pending_review_count", code)
        self.assertIn("approval_receipts_count", code)
        self.assertNotIn("AssetDatabase.CreateAsset", code)
        self.assertNotIn("PrefabUtility.SaveAsPrefabAsset", code)
        self.assertNotIn("GrantReward", code)

    def test_presentation_only_tween_has_reduced_motion_controls(self):
        runtime = (ROOT / "unity_package/Runtime/VufUiTween.cs").read_text()
        editor = (ROOT / "unity_package/Editor/VufUiTweenInspector.cs").read_text()
        screen = (ROOT / "unity_package/Editor/VufScreenShellBuilderWindow.cs").read_text()
        self.assertIn("SetReducedMotion(bool enabled)", runtime)
        self.assertIn("public void Advance(float seconds)", runtime)
        self.assertIn("Group.blocksRaycasts", runtime)
        self.assertIn("Application.isPlaying", editor)
        self.assertIn("AddComponent<VufUiTween>()", screen)
        self.assertNotIn("GrantReward", runtime)
        self.assertNotIn("PlayerPrefs", runtime)

    def test_review_state_contract_guards_synthetic_locales_and_actions(self):
        code = (ROOT / "unity_package/Editor/VufReviewStateCatalog.cs").read_text()
        self.assertIn('"en", "tr", "stress"', code)
        self.assertIn('"Owned", "Claimed", "Disabled", "Pending"', code)
        self.assertIn('CANDIDATE_NOT_APPROVED', code)
        self.assertIn('GetPersistentEventCount()', code)
        self.assertIn('!Contains(States, state)', code)
        self.assertNotIn('PlayerPrefs', code)
        self.assertNotIn('GrantReward', code)

    def test_shell_builder_binds_review_copy_to_visible_mock_only(self):
        shell = (ROOT / "unity_package/Editor/VufScreenShellBuilderWindow.cs").read_text()
        self.assertIn('ReviewState_AlwaysVisible', shell)
        self.assertIn('VufReviewStateCatalog.Apply(root, spec,', shell)
        self.assertIn('VufReviewStateCatalog.Locales[previewLocaleIndex]', shell)
        self.assertIn('button.interactable = false', shell)
        self.assertIn('OFF_UNTIL_ENGINE_POLICY_CONFIRMED', shell)

    def test_four_page_types_have_distinct_shell_layouts(self):
        script = (ROOT / "unity_package/Editor/VufScreenShellBuilderWindow.cs").read_text()
        for section in ("MODAL OR REWARD CEREMONY", "ENGINE BOARD SLOT",
                        "HERO / COLLECTION SLOT", "BOOSTER / SCORE HUD SLOT"):
            self.assertIn(section, script)


if __name__ == "__main__":
    unittest.main()
