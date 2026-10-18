"""M08 source-only cross-language preview pack consistency negatives.

These checks do not execute C# or confirm Unity Player/test execution.
"""
import re
import unittest
from pathlib import Path

from factory.asset_packaging.candidate_pack import (
    PACK_GENERATOR, STAGE, SAFE,
)

ROOT = Path(__file__).resolve().parents[1]
EDITOR = ROOT / "unity_package" / "Editor"
RUNTIME = ROOT / "unity_package" / "Runtime"


class M08UnitySourceParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.importer = (EDITOR / "VufCandidatePackImporterWindow.cs").read_text()
        cls.sandbox = (EDITOR / "VufExternalPackSandboxWindow.cs").read_text()
        cls.actions = (EDITOR / "VufInteractiveUiReviewWindow.cs").read_text()
        cls.runtime = (RUNTIME / "VisualAssetManifest.cs").read_text()

    def test_python_bundle_id_stages_and_unicode_free_paths_match_unity(self):
        self.assertIn(PACK_GENERATOR, self.importer)
        self.assertIn('parsed.stage != "TEST_ONLY"', self.importer)
        self.assertIn('parsed.stage != "TEST_ONLY"', self.runtime)
        self.assertTrue(SAFE.fullmatch("fx/bubblerise/fx_sheet.png"))
        self.assertTrue(SAFE.fullmatch("sprite_atlas/atlas_manifest.json"))
        self.assertFalse(SAFE.fullmatch("../secrets.json"))

    def test_import_only_under_unity_editor_assets_and_new_files(self):
        self.assertIn('"VUF_ReviewImports"', self.importer)
        self.assertIn('"Editor", "VUF_ReviewImports"', self.importer)
        self.assertIn("FileMode.CreateNew", self.importer)
        self.assertIn("source file SHA mismatch", self.importer)
        self.assertIn("copied candidate hash changed", self.importer)
        self.assertIn("FileAttributes.ReparsePoint", self.importer)
        self.assertNotIn("FileMode.Create,", self.importer)
        self.assertNotIn("AssetDatabase.DeleteAsset(", self.importer)

    def test_disabled_gameplay_action_still_editor_only_and_auditable(self):
        self.assertIn("EnableOnlyPreviewButton", self.actions)
        self.assertIn("VufScreenShellBuilderWindow.BuildCandidateHierarchy", self.actions)
        self.assertIn("VufReviewStateCatalog.Apply", self.actions)
        self.assertIn("VufResponsiveGeometry.Analyze", self.actions)
        self.assertIn("HideFlags.DontSaveInEditor", self.actions)
        self.assertIn("ACTION_NOT_BOUND_TO_ENGINE", self.actions)
        self.assertNotIn("SaveAsPrefabAsset(", self.actions)

    def test_offline_locale_is_draft_fallback_not_real_language_contract(self):
        self.assertIn("ReadDraftLocale", self.sandbox)
        self.assertIn("OFFLINE_DRAFT_FALLBACK", self.sandbox)
        self.assertIn("DRAFT_NOT_LOCALIZATION_APPROVED", self.sandbox)
        self.assertIn("NOT TRANSLATION APPROVED", self.sandbox)
        self.assertIn("OpenImportedManifest", self.sandbox)
        self.assertIn("VufUnifiedVisualStudioWindow.Open", self.sandbox)


if __name__ == "__main__":
    unittest.main()
