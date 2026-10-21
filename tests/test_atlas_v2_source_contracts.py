"""R47 SDK-first SpriteAtlas V2 source safety tests (not Unity runtime)."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class VufAtlasV2SourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src = (ROOT / "unity_package/Editor/"
                   "VufSpriteAtlasV2Window.cs").read_text(encoding="utf-8")
        cls.nunit = (ROOT / "unity_package/Tests/Editor/"
                     "VufSpriteAtlasV2EditModeTests.cs").read_text(encoding="utf-8")
        cls.ledger = (ROOT / "docs/VUF_DONOR_SOURCE_LEDGER.md").read_text()

    def test_actual_unity_6000_6_native_v2_api_not_rewritten(self):
        self.assertIn("new SpriteAtlasAsset()", self.src)
        self.assertIn("SpriteAtlasAsset.Save(candidate, path)", self.src)
        self.assertIn("importer.includeInBuild = false;", self.src)
        self.assertIn("importer.SaveAndReimport();", self.src)
        self.assertIn("SDK_REUSE", self.src)
        self.assertIn("SpriteAtlasAsset.bindings.cs", self.ledger)

    def test_no_writes_to_source_importers_existing_assets_or_gameplay(self):
        self.assertIn("AssetDatabase.LoadMainAssetAtPath(path) != null", self.src)
        self.assertIn("File.Exists(path)", self.src)
        self.assertIn("TextureImporterType.Sprite", self.src)
        self.assertNotIn("textureImporter.SaveAndReimport", self.src)
        self.assertNotIn("AssetDatabase.DeleteAsset", self.src)
        self.assertNotIn("UnityWebRequest", self.src)
        self.assertNotIn("includeInBuild = true", self.src)

    def test_readonly_importer_inspection_and_platform_uncertainty(self):
        src=self.src
        for token in ("ReadImportedSettings(", "SpriteImportMode.Single",
                      "importer.spritePivot", "importer.spriteBorder",
                      "importer.spritePixelsPerUnit", "importer.mipmapEnabled",
                      'GetPlatformTextureSettings("iPhone")',
                      'GetPlatformTextureSettings("Android")',
                      "IndividualSpritePivotsVerified",
                      "AssetDatabase.LoadAllAssetsAtPath(path)",
                      "sprite.pivot", "sprite.border", "sprite.rect",
                      "SpriteSliceSnapshot", "HasPhysicalDeviceProof = false",
                      "OriginalRightsVerified = false",
                      "RealDeviceTextureVerified = false"):
            with self.subTest(token=token):
                self.assertIn(token,src)
        self.assertIn("ActualImportedSpriteSnapshotPreservesBytesGuidAndAllImporterSettings",
                      self.nunit)
        self.assertIn("UnimportedTextureCannotMasqueradeAsRealImporterEvidence",
                      self.nunit)
        self.assertNotIn("SetPlatformTextureSettings(",src)
        self.assertNotIn("importer.spritePivot =",src)

    def test_real_editor_nunit_and_meta_source_defined(self):
        self.assertGreaterEqual(self.nunit.count("[Test]"), 5)
        self.assertIn("CreatesOnlyNewV2CandidateAndPreservesImportedSource",
                      self.nunit)
        self.assertTrue((ROOT/"unity_package/Editor/"
                         "VufSpriteAtlasV2Window.cs.meta").is_file())
        self.assertTrue((ROOT/"unity_package/Tests/Editor/"
                         "VufSpriteAtlasV2EditModeTests.cs.meta").is_file())


if __name__ == "__main__":
    unittest.main()
