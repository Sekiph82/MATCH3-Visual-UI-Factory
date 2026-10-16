"""R35-R36 source-only guardrails for editable five-game Unity stage layouts.

These Python checks cannot substitute for real local Unity C# compilation,
NUnit, live GUI rendering or physical device acceptance.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class EditableCompositionSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        editor = ROOT / "unity_package/Editor"
        cls.stage = (editor / "VufConceptStageBuilderWindow.cs").read_text()
        cls.layout = (editor / "VufPageComposition.cs").read_text()
        cls.motifs = (editor / "VufThemeMotifDecor.cs").read_text()

    def test_real_editable_layouts_are_not_flat_png_runtime_gameplay(self):
        self.assertIn("VufPageComposition.Compose(safe, style, selected.screen_key)", self.stage)
        self.assertIn("VufThemeMotifDecor.Apply(safe, style)", self.stage)
        self.assertIn("GAMEPLAY_Grid6x7_VISUAL_ONLY", self.layout)
        self.assertIn("HOME_DailyMissionCard", self.layout)
        self.assertIn("WORLD_EditableMapCanvas", self.layout)
        self.assertIn("GAMEPLAY_StaticTile_", self.layout)
        self.assertIn("button.interactable = false", self.stage)
        for source in (self.layout, self.motifs):
            self.assertIn("raycastTarget = false", source)
            self.assertNotIn("AssetDatabase.CreateAsset", source)
            self.assertNotIn("SaveAsPrefabAsset", source)
            self.assertNotIn("PlayerPrefs", source)
            self.assertNotIn("UnityWebRequest", source)

    def test_theme_motif_identity_has_five_separate_geometries(self):
        for marker in ("CORAL_BubbleOutline_", "GARAGE_RivetPlate_",
                       "DINO_FrondStem_", "REALMS_PortalDiamond_",
                       "WONDER_Confetti_"):
            self.assertIn(marker, self.motifs)
        self.assertIn("theme motifs already authored", self.motifs)
        self.assertIn("REQUIRES_ENGINE_OR_GAME_BINDING", self.stage)

    def test_editor_unit_suites_are_authored_and_guards_registered(self):
        p = ROOT / "unity_package/Tests/Editor"
        a = (p / "VufPageCompositionEditModeTests.cs").read_text()
        b = (p / "VufThemeMotifEditModeTests.cs").read_text()
        self.assertEqual(a.count("[Test]"), 4)
        self.assertEqual(b.count("[Test]"), 4)
        self.assertIn("AllFifteenDraftThemePageLayoutsAreDistinctAndEditable", a)
        self.assertIn("FiveThemesProduceDistinctEditableGeometricMotifs", b)
        structure = (ROOT / "Tools/validate_repo_structure.py").read_text()
        self.assertIn('"Editor/VufPageComposition.cs"', structure)
        self.assertIn('"Editor/VufThemeMotifDecor.cs"', structure)


if __name__ == "__main__":
    unittest.main()
