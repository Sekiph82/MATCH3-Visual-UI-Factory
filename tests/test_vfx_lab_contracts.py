"""Offline structural VF-06 and Unity editor boundaries; not Unity runtime approval."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from factory.vfx_builder.validate_presets import validate_vfx, VfxContractError


class VfxLabContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads(
            (ROOT / "factory/vfx_builder/presets.v1.json").read_text(encoding="utf-8"))

    def test_five_presentational_presets(self):
        self.assertEqual(validate_vfx(self.document)["preset_count"], 5)

    def test_self_approved_effect_fails(self):
        candidate = copy.deepcopy(self.document)
        candidate["presets"][0]["state"] = "APPROVED"
        with self.assertRaises(VfxContractError):
            validate_vfx(candidate)

    def test_effect_grant_fails(self):
        candidate = copy.deepcopy(self.document)
        candidate["engine_side_effects_allowed"] = True
        with self.assertRaises(VfxContractError):
            validate_vfx(candidate)
        candidate = copy.deepcopy(self.document)
        candidate["presets"][0]["events"].append("GRANT_REWARD")
        with self.assertRaises(VfxContractError):
            validate_vfx(candidate)

    def test_particle_budgets_fails(self):
        for field, value in [("count", 161), ("count", True), ("count", 4.4),
                             ("lifetime_seconds", 12.0), ("lifetime_seconds", float("nan")),
                             ("start_speed", -1), ("start_size", .001)]:
            candidate = copy.deepcopy(self.document)
            candidate["presets"][0][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(VfxContractError):
                validate_vfx(candidate)

    def test_reduced_motion_is_mandatory(self):
        candidate = copy.deepcopy(self.document)
        candidate["presets"][0].pop("reduced_motion_fallback")
        with self.assertRaises(VfxContractError):
            validate_vfx(candidate)

    def test_vfx_editor_candidate_creation_is_isolated(self):
        code = (ROOT / "unity_package/Editor/VufVfxLabWindow.cs").read_text(encoding="utf-8")
        self.assertIn("PrefabUtility.SaveAsPrefabAsset", code)
        self.assertIn("AssetDatabase.LoadMainAssetAtPath(path)", code)
        self.assertIn("reducedMotion", code)
        self.assertIn("DETERMINISTIC 2D SKETCH", code)
        self.assertNotIn("ApplyScore", code)
        self.assertNotIn("RewardGrant", code)

    def test_ui_composer_creates_actual_unbound_button(self):
        code = (ROOT / "unity_package/Editor/VufUiComposerWindow.cs").read_text(encoding="utf-8")
        self.assertIn("AddComponent<Button>()", code)
        self.assertIn("button.interactable = false", code)
        self.assertIn("AddComponent<VufSafeAreaFitter>()", code)
        self.assertIn("PrefabUtility.SaveAsPrefabAsset", code)

    def test_manual_qa_studio_never_self_approves(self):
        code = (ROOT / "unity_package/Editor/VufQaStudioWindow.cs").read_text(encoding="utf-8")
        self.assertIn("VufSafeAreaFitter", code)
        self.assertIn("ParticleSystem", code)
        self.assertIn("GetPersistentEventCount", code)
        self.assertIn("FINAL STATUS: REVIEW_REQUIRED", code)
        self.assertIn("AssetDatabase.OpenAsset", code)

    def test_runtime_safe_area_has_no_gameplay_ownership(self):
        code = (ROOT / "unity_package/Runtime/VufSafeAreaFitter.cs").read_text(encoding="utf-8")
        self.assertIn("Screen.safeArea", code)
        self.assertIn("target.anchorMin", code)
        self.assertIn("target.anchorMax", code)
        self.assertNotIn("PlayerPrefs", code)


if __name__ == "__main__":
    unittest.main()
