"""M09 cross-language Editor QA matrix source contracts (NOT executed Unity GUI)."""
import re
import unittest
from pathlib import Path

from factory.qa.m09_review_inventory import (
    PROFILES, STATES, LOCALES, DEVICES, EXPECTED,
    inventory_report,
)

ROOT = Path(__file__).resolve().parents[1]
EDITOR = ROOT / "unity_package" / "Editor"


class M09EditorSourceParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.matrix = (EDITOR / "VufM09MatrixAudit.cs").read_text("utf-8")
        cls.window = (EDITOR / "VufM09OwnerVisualQaWindow.cs").read_text("utf-8")
        cls.capture = (EDITOR / "VufM09RenderCapture.cs").read_text("utf-8")
        cls.states = (EDITOR / "VufReviewStateCatalog.cs").read_text("utf-8")
        cls.geometry = (EDITOR / "VufResponsiveGeometry.cs").read_text("utf-8")

    def test_source_profiles_state_locale_device_constants_match_real_draft_matrix(self):
        self.assertEqual(EXPECTED, 16800)
        for profile in PROFILES:
            self.assertIn(f'"{profile}"', self.matrix)
        for state in STATES:
            self.assertIn(f'"{state}"', self.states)
        for locale in LOCALES:
            self.assertIn(f'"{locale}"', self.states)
        for device in DEVICES:
            self.assertIn(f'"{device}"', self.geometry)
        self.assertIn("VufReviewStateCatalog.States.Length", self.matrix)
        self.assertIn("VufResponsiveGeometry.Presets.Length", self.matrix)

    def test_real_unity_candidate_render_capture_does_not_fake_phone_signoff(self):
        self.assertIn("RenderTexture", self.capture)
        self.assertIn("cam.Render()", self.capture)
        self.assertIn("EncodeToPNG()", self.capture)
        self.assertIn("Camera", self.capture)
        self.assertIn("DontSaveInEditor", self.capture)
        self.assertIn("canvas.renderMode = oldMode", self.capture)
        self.assertIn("RenderTexture.active = oldActive", self.capture)
        self.assertIn("real_unity_render_observed = capturedPng != null", self.window)
        self.assertIn("human_aesthetic_approved", self.window)
        self.assertIn("release_allowed", self.window)

    def test_full_studio_reuses_six_existing_workflows_and_has_no_engine_writer(self):
        for symbol in (
            "VufScreenShellBuilderWindow.BuildCandidateHierarchy",
            "VufReviewStateCatalog.Apply",
            "VufResponsiveGeometry.Analyze",
            "VufTypographyAudit.Analyze",
            "VufUnifiedVisualStudioWindow.Open()",
            "VufSceneLayerReviewWindow.Open()",
            "VufExternalPackSandboxWindow.Open()",
            "VufReadinessBoardWindow.Open()",
            "VufM09MatrixAudit.InspectBatch",
            "VufM09RenderCapture.CaptureCandidate",
        ):
            with self.subTest(symbol=symbol):
                self.assertIn(symbol, self.window + self.matrix)
        self.assertNotIn("AssetDatabase.CreateAsset(", self.window)
        self.assertNotIn("AssetDatabase.DeleteAsset(", self.window)
        self.assertNotIn("SaveAsPrefabAsset(", self.window)
        self.assertNotIn("SubmitScore(", self.window)

    def test_no_owner_release_claim_and_external_create_only_export(self):
        for value in (
            "OWNER_REVIEW_CANDIDATE_NOT_APPROVED",
            "M09_EDITOR_TWEEN_SEQUENCE_NOT_OWNER_APPROVED",
            "FileMode.CreateNew",
            "ScreenshotCaptured, OwnerApproved, DeviceVerified",
        ):
            self.assertIn(value, self.window + self.matrix)
        self.assertIn("release_allowed", self.window)
        report = inventory_report()
        self.assertFalse(report["release_allowed"])
        self.assertEqual(report["screen_contracts_for_other_titles"], "NOT_PROVIDED")


if __name__ == "__main__":
    unittest.main()
