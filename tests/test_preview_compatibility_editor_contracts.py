"""R45-R46 minimal inherited typed Unity and Python manifest guards."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class TypedPreviewContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.editor = (ROOT / "unity_package/Editor/"
                      "VufPreviewCompatibilityWindow.cs").read_text()
        cls.runtime = (ROOT / "unity_package/Runtime/"
                       "VisualAssetManifest.cs").read_text()
        cls.test_source = (ROOT / "unity_package/Tests/Editor/"
                           "VufPreviewCompatibilityEditModeTests.cs").read_text()

    def test_existing_runtime_contract_used_instead_of_custom_json(self):
        self.assertIn("VisualAssetManifest.TryParsePreview", self.editor)
        self.assertIn('parsed.stage != "TEST_ONLY"', self.runtime)
        self.assertIn('report.PinsMatch = report.Mismatches.Count == 0', self.editor)
        self.assertNotIn("AssetDatabase.CreateAsset", self.editor)
        self.assertNotIn("EditorPrefs.Set", self.editor)

    def test_draft_metadata_is_never_release_approved(self):
        for condition in ("ReleaseAllowed => false",
                          "RightsVerified => false",
                          "DeviceVerified => false",
                          "EngineLfxIndependentlyAccepted => false"):
            self.assertIn(condition, self.editor)
        self.assertIn("cannot be independently authenticated",
                      (ROOT / "factory/export_pipeline/"
                       "preview_compatibility.py").read_text())

    def test_new_editor_uses_real_nunit_negative_cases_and_guid(self):
        self.assertEqual(self.test_source.count("[Test]"), 4)
        self.assertIn("PretendApprovedManifestCannotBeLoaded", self.test_source)
        self.assertIn("DuplicateIdsAndWrongThemeAreRejected", self.test_source)
        self.assertTrue((ROOT / "unity_package/Editor/"
                         "VufPreviewCompatibilityWindow.cs.meta").is_file())
        self.assertTrue((ROOT / "unity_package/Tests/Editor/"
                         "VufPreviewCompatibilityEditModeTests.cs.meta").is_file())


if __name__ == "__main__":
    unittest.main()
