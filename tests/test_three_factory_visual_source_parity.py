"""M10 cross-factory source-only regressions, not an executed Unity GUI."""
from __future__ import annotations

import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ED=ROOT/"unity_package"/"Editor"
RT=ROOT/"unity_package"/"Runtime"


class ThreeFactorySourceParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.studio=(ED/"VufCrossFactoryContractWindow.cs").read_text("utf-8")
        cls.art=(ED/"VufCrossFactoryImportedArt.cs").read_text("utf-8")
        cls.m08=(ED/"VufCandidatePackImporterWindow.cs").read_text("utf-8")
        cls.m07=(ED/"VufUnifiedVisualStudioWindow.cs").read_text("utf-8")
        cls.codec=(RT/"VisualAssetManifest.cs").read_text("utf-8")
        cls.capture=(ED/"VufThreeFactoryGridCapture.cs").read_text("utf-8")

    def test_real_lfx_and_actual_engine_events_use_existing_reusable_preview(self):
        for part in ("ParseLevel(", "ParseEvents(", "BuildRealDraftBoard(",
                     "sourceDraftSha256", "LFXV1_VALIDATED_DRAFT_NOT_ENGINE_REPLAY",
                     "M3P1", "Sha(canonicalDraft)",
                     "HighlightCurrentEvent()", "selectedLayer",
                     "SuggestedReviewDelayMs("):
            with self.subTest(part=part):
                self.assertIn(part,self.studio)
        self.assertIn("VufVisualEventCatalog.EventKey",self.studio)
        self.assertIn("VufUnifiedVisualStudioWindow.OpenForExternalViewCue",
                      self.studio)
        self.assertIn("EditorApplication.update -= TickOwnerReview",self.studio)
        self.assertNotIn("AssetDatabase.CreateAsset(",self.studio)
        self.assertNotIn("SaveAsPrefabAsset(",self.studio)

    def test_m08_import_receipt_is_preserved_for_full_byte_sha_inspection(self):
        for part in ("candidate_pack_receipt.json", "ShaFile(receiptCopy)",
                     "FileMode.CreateNew", "copied original M08 receipt SHA"):
            self.assertIn(part,self.m08)
        for part in ("VerifyImportedM08Pack(", "ValidateReceipt(",
                     "candidate_pack_receipt.json", "RawHash(receiptPath)",
                     "RawHash(file)", "checkedHashes",
                     "Assets/Editor/VUF_ReviewImports/",
                     "CANDIDATE", "REVIEW_PENDING",
                     "MATHEMATICAL_PLACEHOLDER_NOT_FINAL"):
            self.assertIn(part,self.art)
        self.assertIn("TryParsePreview",self.art)
        self.assertIn("stage != \"TEST_ONLY\"",self.codec)

    def test_explicit_art_not_guessed_and_never_player_materialized(self):
        for part in ("ValidateOwnerMapping(", "ApplyExplicitSourceBindings(",
                     "sourceLayer", "manualArt[source]=target",
                     "DestroyOnlyTemporary()"):
            with self.subTest(part=part):
                self.assertIn(part,self.art+self.studio+self.m07)
        self.assertIn("Sprite.Create(",self.art)
        self.assertIn("HideFlags.DontSaveInBuild",self.art)
        self.assertIn("Editor/VUF_ReviewImports",self.art)
        self.assertNotIn("Addressables.Load",self.art)
        self.assertNotIn("SubmitScore(",self.studio)
        self.assertNotIn("SetPlayerData(",self.studio)

    def test_real_editor_grid_capture_keeps_owner_release_and_device_flags_false(self):
        for part in ("VufThreeFactoryGridCapture.CaptureSourcePreview",
                     "FileMode.CreateNew", "screenshotSha256",
                     "actualPlayableGameScreenshot",
                     "ownerAestheticApproved",
                     "physicalDeviceGpuVerified",
                     "releaseAllowed", "NOT an iPhone/Android"):
            with self.subTest(part=part):
                self.assertIn(part,self.studio)
        for part in ("VUF_THREE_FACTORY_REAL_DRAFT_TEMP",
                     "HideFlags.DontSaveInEditor",
                     "Real_LFXV1_Source_Grid",
                     "RenderTexture", "EncodeToPNG",
                     "canvas.worldCamera=oldCamera",
                     "RenderTexture.active=oldActive"):
            with self.subTest(part=part):
                self.assertIn(part,self.capture)
        self.assertIn("Editor/VufThreeFactoryGridCapture.cs",
            (ROOT/"Tools"/"validate_repo_structure.py").read_text("utf-8"))

    def test_theme_focused_m07_studio_drops_old_imported_sprites(self):
        self.assertIn("OpenForExternalViewCue",self.m07)
        self.assertIn("view.DestroyOnlyTemporary()",self.m07)
        self.assertIn("view.sourceSheet=null",self.m07)
        self.assertIn("view.fxManifest=null",self.m07)
        self.assertIn("no automatic gameplay event",self.m07)
        meta=(ED/"VufCrossFactoryImportedArt.cs.meta").read_text("utf-8")
        self.assertIn("guid: 2071d07d1a1a4b75a5b877f70fe4112b",meta)


if __name__=="__main__":
    unittest.main()
