"""R32 editor source contracts: genuinely editable concept uGUI reference stages."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ConceptUiStageSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.code = (ROOT / "unity_package/Editor/VufConceptStageBuilderWindow.cs").read_text()
        cls.editor_tests = (ROOT / "unity_package/Tests/Editor/VufConceptStageEditModeTests.cs").read_text()

    def test_reference_layer_is_not_a_flattened_interactive_button(self):
        self.assertIn("typeof(RectTransform)", self.code)
        self.assertIn("typeof(CanvasScaler)", self.code)
        self.assertIn("typeof(VufCandidateScreenMarker)", self.code)
        self.assertIn("ConceptReference_NONINTERACTIVE_REPLACE_ME", self.code)
        self.assertIn("raw.raycastTarget = false;", self.code)
        self.assertIn("button.interactable = false;", self.code)
        self.assertIn("VufSafeAreaFitter", self.code)
        self.assertIn("CANDIDATE", self.code)

    def test_new_editor_prefab_only_and_original_reference_sha_validation(self):
        self.assertIn("PrefabUtility.SaveAsPrefabAsset", self.code)
        self.assertIn("File.Exists(path)", self.code)
        self.assertIn("VerifyImportedPng(texture, entry.png_sha256)", self.code)
        self.assertIn("SHA256.Create()", self.code)
        self.assertIn("FileAttributes.ReparsePoint", self.code)
        self.assertIn("StartsWith(\"Assets/\"", self.code)
        self.assertNotIn("TextureImporter", self.code)
        self.assertNotIn("PlayerPrefs", self.code)

    def test_editor_nunit_variants_cover_fifteen_and_bad_manifest(self):
        self.assertEqual(self.editor_tests.count("[Test]"), 4)
        self.assertIn("AllFifteenProfilesPagesCreateSeparateEditableUnboundUi",
                      self.editor_tests)
        self.assertIn("ManifestOwnerApprovalForgeryNeverBuildsUi",
                      self.editor_tests)
        self.assertIn("Assert.That(checkedStages, Is.EqualTo(15))",
                      self.editor_tests)


if __name__ == "__main__":
    unittest.main()
