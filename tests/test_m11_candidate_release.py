"""M11 end-to-end create-only REVIEW candidate export/import/rollback.

All output lives only in test-owned tempfile dirs. No game/owner files or
running release pointers are modified and TEST_ONLY never becomes shipping.
"""
from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from factory.asset_packaging.candidate_pack import export_pack
from factory.release.m11_candidate_release import (
    STAGE, MANIFEST_FILE, M11ReleaseError, canonical, digest,
    export_review_candidate, import_new_copy, plan, release_audit,
    validate_manifest, verify_release,
)

ENG = "e84d65ab712dddc534cbdb3a30cfe2d7930cea8a"
LFX = "d8d0b37ce71c4e2c0bdb72f9ed1d2a48068281c3"


class M11RealCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="vuf_m11_qa_")
        cls.base = Path(cls.tmp.name)
        cls.source = cls.base / "m08_original_source"
        cls.release = cls.base / "m11_candidate_copy"
        export_pack("Coral_Rescue", cls.source)
        cls.out = export_review_candidate(cls.source, cls.release, ENG, LFX)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_real_original_pack_and_vf04_atlas_reverified_under_candidate(self):
        verified = verify_release(self.release)
        self.assertEqual(verified["stage"], STAGE)
        self.assertEqual(verified["profile_id"], "Coral_Rescue")
        self.assertGreater(verified["artifact_count"], 70)
        self.assertFalse(verified["release_allowed"])
        self.assertFalse(verified["real_engine_lfx_accepted"])
        self.assertEqual(verified["content_identity_sha256"],
                         self.out["content_identity_sha256"])

    def test_two_deterministic_plans_identical_and_source_pins_only_observed(self):
        first = plan(self.source, ENG, LFX)
        again = plan(self.source, ENG, LFX)
        self.assertEqual(canonical(first), canonical(again))
        self.assertEqual(digest(canonical(first)), digest(canonical(again)))
        self.assertEqual(first["engine_observed_git_sha"], ENG)
        self.assertEqual(first["lfx_observed_git_sha"], LFX)
        self.assertEqual(first["upstream_pin_state"],
                         "OBSERVED_UNACCEPTED_NOT_REPLAY_VERIFIED")
        self.assertFalse(first["engine_abi_accepted"])
        self.assertFalse(first["lfx_replay_accepted"])

    def test_existing_release_path_never_overwritten(self):
        with self.assertRaises(M11ReleaseError):
            export_review_candidate(self.source, self.release, ENG, LFX)
        self.assertEqual(self.out["content_identity_sha256"],
                         verify_release(self.release)["content_identity_sha256"])

    def test_import_new_slot_preserves_previous_and_does_not_activate_game(self):
        slot = self.base / "import_A"
        result = import_new_copy(self.release, slot)
        self.assertEqual(result["operation"], "IMPORT_NEW_COPY_ONLY")
        self.assertFalse(result["modified_active_game_pointer"])
        self.assertFalse(result["deleted_previous_revision"])
        self.assertEqual(verify_release(slot)["content_identity_sha256"],
                         self.out["content_identity_sha256"])
        with self.assertRaises(M11ReleaseError):
            import_new_copy(self.release, slot)

    def test_rollback_is_a_new_copy_and_keeps_previous_revision(self):
        previous = self.base / "rollback_previous"
        current = self.base / "rollback_current"
        import_new_copy(self.release, previous)
        rollback = import_new_copy(self.release, current, rollback_from=previous)
        self.assertEqual(rollback["operation"], "ROLLBACK_NEW_COPY_ONLY")
        self.assertTrue(previous.is_dir())
        self.assertTrue(current.is_dir())
        self.assertFalse(rollback["modified_active_game_pointer"])
        self.assertFalse(rollback["release_allowed"])

    def test_corrupted_import_source_never_reuses_forged_hash_receipt(self):
        with tempfile.TemporaryDirectory(prefix="vuf_m11_corrupt_") as tmp:
            target = Path(tmp) / "modified_copy"
            import_new_copy(self.release, target)
            original = target / "sprite_atlas/atlas.png"
            b = original.read_bytes()
            original.write_bytes(b[:-4] + b"BAD!")
            with self.assertRaises((M11ReleaseError, ValueError)):
                verify_release(target)

    def test_extra_forbidden_player_or_secret_file_detected(self):
        with tempfile.TemporaryDirectory(prefix="vuf_m11_secret_") as tmp:
            target = Path(tmp) / "modified_copy"
            import_new_copy(self.release, target)
            (target / ".secret.env").write_text("not a real secret")
            with self.assertRaises(M11ReleaseError):
                verify_release(target)

    def test_forged_license_game_wins_and_accepted_engine_rejected(self):
        template = plan(self.source, ENG, LFX)
        for name in ("release_allowed", "engine_abi_accepted",
                     "lfx_replay_accepted", "owner_visual_approved",
                     "licensed_art_approved", "player_build_tested"):
            forged = copy.deepcopy(template)
            forged[name] = True
            with self.subTest(field=name), self.assertRaises(M11ReleaseError):
                validate_manifest(forged)

    def test_wrong_sha_wrong_profile_unknown_paths_and_duplicates_rejected(self):
        m = plan(self.source, ENG, LFX)
        bad = dict(m, engine_observed_git_sha="a" * 64)
        with self.assertRaises(M11ReleaseError):
            validate_manifest(bad)
        bad = copy.deepcopy(m)
        bad["artifacts"][1]["path"] = bad["artifacts"][0]["path"]
        with self.assertRaises(M11ReleaseError):
            validate_manifest(bad)
        bad = copy.deepcopy(m)
        bad["artifacts"][1]["path"] = "../credentials"
        with self.assertRaises(M11ReleaseError):
            validate_manifest(bad)
        with self.assertRaises(M11ReleaseError):
            plan(self.source, "BAD", LFX)

    def test_independent_audit_never_self_signs_rights_or_no_cost_certification(self):
        result = release_audit(self.release)
        self.assertTrue(result["reproducible_source_identity_verified"])
        self.assertTrue(result["all_package_source_hashes_verified"])
        self.assertTrue(result["owner_approval_required"])
        self.assertFalse(result["consumer_G01_G02_G09_G11_handoff_signed"])
        self.assertFalse(result["independent_audit_signed"])
        self.assertFalse(result["rights_evidence_legal_verified"])
        self.assertFalse(result["release_allowed"])


if __name__ == "__main__":
    unittest.main()
