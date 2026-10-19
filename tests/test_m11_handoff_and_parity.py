"""M11 four consumer handoffs: cannot invent game-title mappings or signoff."""
from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from factory.asset_packaging.candidate_pack import export_pack
from factory.release.m11_candidate_release import (
    M11ReleaseError, export_review_candidate,
)
from factory.release.m11_game_handoff import (
    TARGETS, generate_handoff, save_new_external_handoff, validate_handoff,
)

ENG = "e84d65ab712dddc534cbdb3a30cfe2d7930cea8a"
LFX = "d8d0b37ce71c4e2c0bdb72f9ed1d2a48068281c3"
ROOT = Path(__file__).resolve().parents[1]


class M11HandoffAndSourceParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="vuf_m11_handoff_")
        cls.parent = Path(cls.tmp.name)
        cls.source = cls.parent / "m08"
        cls.candidate = cls.parent / "m11"
        export_pack("Coral_Rescue", cls.source)
        export_review_candidate(cls.source, cls.candidate, ENG, LFX)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_exact_four_consumer_ids_without_fabricated_owner_mapping(self):
        assert TARGETS == ("G01", "G02", "G09", "G11")
        handoff = generate_handoff(self.candidate)
        validate_handoff(handoff)
        self.assertEqual(len(handoff["game_ids"]), 4)
        self.assertFalse(handoff["actual_player_build_verified"])
        self.assertFalse(handoff["release_allowed"])
        for row in handoff["game_ids"]:
            self.assertEqual(row["owner_game_title_mapping"],
                             "UNCONFIRMED_NOT_IN_VUF_SOURCE")
            self.assertFalse(row["approved_logo_fonts_and_original_art"])
            self.assertFalse(row["game_content_import_performed"])

    def test_owner_mapping_rights_and_release_spoof_are_rejected(self):
        data = generate_handoff(self.candidate)
        for key, value in (
            ("owner_game_title_mapping", "Coral_Rescue"),
            ("matching_released_theme_pack", "production"),
            ("engine_lfx_accepted_abi", True),
            ("approved_logo_fonts_and_original_art", True),
        ):
            forged = copy.deepcopy(data)
            forged["game_ids"][0][key] = value
            with self.subTest(field=key), self.assertRaises(M11ReleaseError):
                validate_handoff(forged)

    def test_deterministic_create_only_external_handoff_and_no_overwrite(self):
        target = self.parent / "consumer_receipt.json"
        result = save_new_external_handoff(self.candidate, target)
        self.assertEqual(json.loads(target.read_text()), result)
        with self.assertRaises(M11ReleaseError):
            save_new_external_handoff(self.candidate, target)

    def test_unity_editor_source_matches_m11_candidate_pin_and_safety_rules(self):
        source = (ROOT / "unity_package" / "Editor" /
                  "VufM11CandidateReleaseReviewWindow.cs").read_text("utf-8")
        from factory.release.m11_candidate_release import STAGE, PIN_STATE
        self.assertIn(STAGE, source)
        self.assertIn(PIN_STATE, source)
        for item in ("engine_observed_git_sha", "lfx_observed_git_sha",
                     "source_manifest_sha256", "source_receipt_sha256",
                     "content_identity_sha256", "release_allowed",
                     "SHA256.Create()", "FileAttributes.ReparsePoint",
                     "VufCandidatePackImporterWindow.Open",
                     "VufReadinessBoardWindow.Open"):
            self.assertIn(item, source)
        self.assertNotIn("AssetDatabase.CreateAsset(", source)
        self.assertNotIn("SaveAsPrefabAsset(", source)


if __name__ == "__main__":
    unittest.main()
