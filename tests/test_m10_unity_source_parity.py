"""M10 Python↔Unity TEST_ONLY route syntax and no-game-authority contracts.

These are SOURCE assertions, not a real Engine/LFX neutral replay consumer.
"""
import unittest
from pathlib import Path

from factory.integration.m10_neutral_slice import (
    PROFILES, BASE_ROUTE, CORAL_EXTRA, CORAL_IDS, STAGE,
)

ROOT = Path(__file__).resolve().parents[1]
CS = ROOT / "unity_package" / "Editor" / "VufM10VerticalSliceStudio.cs"


class M10CSharpSourceParity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cs = CS.read_text(encoding="utf-8")

    def test_same_five_names_and_source_only_route_keys_across_python_unity(self):
        for name in PROFILES:
            self.assertIn('"' + name + '"', self.cs)
        for key in BASE_ROUTE + CORAL_EXTRA:
            self.assertIn('"' + key + '"', self.cs)
        self.assertIn("CORAL DRAFT borrowed", self.cs)
        self.assertIn("N/A", self.cs)

    def test_same_unconnected_coral_screen_alias_and_non_gameplay_contract(self):
        self.assertEqual(CORAL_IDS["offline"], "COR-22")
        self.assertIn('key == "offline" ? "splash_loading"', self.cs)
        self.assertIn("REQUIRES_ENGINE_OR_GAME_BINDING", self.cs)
        self.assertIn("VufScreenShellBuilderWindow.BuildCandidateHierarchy", self.cs)
        self.assertIn("VufReviewStateCatalog.Apply", self.cs)
        self.assertIn("VufResponsiveGeometry.Analyze", self.cs)
        self.assertIn("VufTypographyAudit.Analyze", self.cs)
        self.assertIn("GetPersistentEventCount()", self.cs)
        self.assertNotIn("SaveAsPrefabAsset(", self.cs)
        self.assertNotIn("AssetDatabase.CreateAsset(", self.cs)

    def test_source_sha_and_theme_reference_are_not_advertised_as_verified_wins(self):
        self.assertIn(STAGE, self.cs)
        self.assertIn("SHA256.Create()", self.cs)
        self.assertIn("actualScore=NONE", self.cs)
        self.assertIn("productionReplay=UNVERIFIED", self.cs)
        self.assertIn("LFX", self.cs)
        self.assertIn("NOT BOUND", self.cs)
        self.assertIn("VufExternalPackSandboxWindow.Open()", self.cs)
        self.assertIn("VufM09OwnerVisualQaWindow.Open()", self.cs)
        self.assertIn("VufUnifiedVisualStudioWindow.Open()", self.cs)


if __name__ == "__main__":
    unittest.main()
