"""M03 candidate-only native uGUI component source contracts; not Unity execution."""
from __future__ import annotations

import json
import unittest
from pathlib import Path, PureWindowsPath

from factory.visual_director.m02_style_bible import compile_bibles

ROOT = Path(__file__).resolve().parents[1]
EDITOR = ROOT / "unity_package" / "Editor"
TESTS = ROOT / "unity_package" / "Tests" / "Editor"
SEMANTICS = (
    "primary_cta", "secondary_cta", "card", "modal", "badge",
    "counter", "tab", "progress", "disabled_reason", "pending_state",
)


class M03SemanticComponentSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.code = (EDITOR / "VufM03ComponentKitWindow.cs").read_text("utf-8")
        cls.unity_tests = (
            TESTS / "VufM03ComponentKitEditModeTests.cs"
        ).read_text("utf-8")
        cls.bibles = compile_bibles()

    def test_exact_five_style_bibles_share_ten_semantic_roles_without_approval(self):
        self.assertEqual(len(self.bibles["profiles"]), 5)
        for profile in self.bibles["profiles"]:
            with self.subTest(title=profile["profile_id"]):
                self.assertEqual(
                    tuple(profile["original_brief"]["ui_components"]), SEMANTICS
                )
                self.assertFalse(profile["owner_design_approved"])
                self.assertFalse(profile["release_allowed"])

    def test_real_editor_ugui_controls_are_unbound_and_duplicated_roles_blocked(self):
        code = self.code
        for token in (
            "ValidateSemantics(", "BuildCandidate(", "AddComponent<Button>()",
            "control.interactable = false",
            "GetPersistentEventCount()", "Navigation.Mode.None",
            "M03_AlwaysVisibleRightsAndBindingGate",
            "NO REAL PURCHASE, REWARD, CONSENT OR NAVIGATION",
            "Unknown M03 prototype", "Unknown M03",
        ):
            with self.subTest(token=token):
                self.assertIn(token, code)
        self.assertNotIn("onClick.AddListener", code)
        self.assertNotIn("SaveAsPrefabAsset", code)
        self.assertNotIn("CreateAsset(", code)
        self.assertNotIn("PlayerPrefs", code)
        self.assertNotIn("UnityWebRequest", code)

    def test_four_grid_profiles_safely_reuse_m02_and_keep_shell_invariance(self):
        self.assertEqual(
            [m["width_dp"] for m in self.bibles["common"]["screen_modes"]],
            [320, 393, 430, 768],
        )
        self.assertIn("BuildSourceGridGuide(", self.code)
        self.assertIn("GetAccessibleSymbolInk(", self.code)
        self.assertIn("VufReviewStateCatalog.States", self.code)
        # No change to the canonical 28-screen source or its R43 integration.
        catalog = json.loads(
            (ROOT / "schemas/coral-experiences.v1.json").read_text("utf-8")
        )
        self.assertEqual(len(catalog["screens"]), 28)
        shell = (EDITOR / "VufScreenShellBuilderWindow.cs").read_text("utf-8")
        self.assertIn("VufScreenShellLayoutBridge.Enhance(root, spec, style)", shell)

    def test_factory_dashboard_surfaces_m02_and_m03_without_release_link(self):
        dashboard = (EDITOR / "VufDashboardWindow.cs").read_text("utf-8")
        self.assertIn("VufM03ComponentKitWindow.Open();", dashboard)
        self.assertIn("VufM02StyleBibleStudioWindow.Open();", dashboard)
        self.assertIn("Publish (NOT READY)", dashboard)
        self.assertIn("DrawSourceSchematic(", self.code)

    def test_editor_only_stable_meta_and_structure_registration(self):
        source = EDITOR / "VufM03ComponentKitWindow.cs"
        tests = TESTS / "VufM03ComponentKitEditModeTests.cs"
        validator = (ROOT / "Tools/validate_repo_structure.py").read_text("utf-8")
        guids = []
        for file in (source, tests):
            meta = file.with_name(file.name + ".meta").read_text("utf-8")
            self.assertIn("fileFormatVersion: 2", meta)
            guid = next(
                line.removeprefix("guid: ") for line in meta.splitlines()
                if line.startswith("guid: ")
            )
            self.assertEqual(len(guid), 32)
            # Validator source stores portable / paths on all host OSes.
            # A Windows PurePath fixture catches separator drift even when
            # this regression is run from a Linux/macOS developer machine.
            source_relative = file.relative_to(ROOT / "unity_package")
            portable = source_relative.as_posix()
            self.assertEqual(
                PureWindowsPath(*source_relative.parts).as_posix(), portable
            )
            self.assertIn(portable, validator)
            guids.append(guid)
        self.assertEqual(len(set(guids)), 2)

    def test_unity_negative_and_five_theme_editmode_cases_are_authored(self):
        for name in (
            "FiveThemesAndFourDeviceGuidesProduceTenRealUnboundComponents",
            "EightStatesCannotCauseActiveButtonsOrRealProgress",
            "NoUnknownProfileStateOrForgedOwnerApproval",
            "DuplicatedOrChangedSemanticRoleIsRejectedBeforeAuthoring",
        ):
            with self.subTest(test_name=name):
                self.assertIn(name, self.unity_tests)
        self.assertEqual(self.unity_tests.count("[Test]"), 4)


if __name__ == "__main__":
    unittest.main()
