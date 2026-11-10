"""VUF-M01-008: Tests for deterministic golden fixtures and fallback contract.

PROTOTYPE-ONLY: ENG-M24 is not PASS.  No runtime binding, no owner sign-off.
"""
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from factory.ui_composer.m01_golden_fixtures import (
    GOLDEN_FIXTURE_STAGE, GoldenFixtureError,
    build_golden, save_golden, verify_golden, load_golden,
)
from factory.ui_composer.m01_surface_contract_matrix import (
    AUTH_FALSE, CATALOG, ENGINE_ACTION_KINDS, ENGINE_STATES, ENGINE_SURFACES,
    build_m01_matrix,
)


class M01GoldenFixtureTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.source = CATALOG.read_bytes()
        cls.golden = build_golden(cls.source)
        cls.matrix = build_m01_matrix(cls.source)

    def test_golden_deterministic_sha_matches_live_matrix(self):
        """The golden fixture_sha256 is derived from the same live build."""
        second = build_golden(self.source)
        self.assertEqual(self.golden["fixture_sha256"], second["fixture_sha256"])
        self.assertEqual(self.golden["matrix_sha256"], self.matrix["matrix_sha256"])

    def test_golden_exact_counts_680_matrix_rows_1120_screen_states(self):
        self.assertEqual(self.golden["matrix_rows"], 680)
        self.assertEqual(self.golden["screen_state_rows"], 1120)
        self.assertEqual(self.golden["profile_count"], 5)
        self.assertEqual(self.golden["surface_state_count_per_profile"], 136)
        self.assertEqual(self.golden["screen_state_count_per_profile"], 224)
        self.assertEqual(self.golden["source_screen_count"], 28)

    def test_golden_enums_match_live_engine_constants(self):
        self.assertEqual(set(self.golden["surface_kinds"]), set(ENGINE_SURFACES))
        self.assertEqual(len(self.golden["surface_kinds"]), 17)
        self.assertEqual(set(self.golden["player_state_kinds"]), set(ENGINE_STATES))
        self.assertEqual(len(self.golden["player_state_kinds"]), 8)
        self.assertEqual(set(self.golden["action_kind_namespace"]),
                         set(ENGINE_ACTION_KINDS))
        self.assertEqual(len(self.golden["action_kind_namespace"]), 4)

    def test_all_auth_flags_false_in_golden_prototype_marker(self):
        """ENG-M24 not PASS: no auth flag may be True in golden fixture."""
        for flag in AUTH_FALSE:
            with self.subTest(flag=flag):
                self.assertFalse(self.golden["auth_flags"][flag])
        self.assertEqual(set(self.golden["auth_flags"]), set(AUTH_FALSE))
        self.assertIn("PROTOTYPE", self.golden.get("fixture_stage", ""))

    def test_absent_engine_surfaces_and_policy_off_screens_stable(self):
        self.assertEqual(
            self.golden["absent_engine_surfaces"],
            sorted(["Booster", "Consent", "Settings", "Store"]),
        )
        self.assertEqual(
            self.golden["policy_off_screens"],
            sorted(["events_hub", "friends", "leaderboard",
                    "season_pass", "tournament"]),
        )

    def test_save_and_load_golden_roundtrip_in_temp_dir(self):
        with tempfile.TemporaryDirectory(prefix="vuf_m01_golden_") as tmp:
            dest = Path(tmp) / "m01_golden_fixture.v1.json"
            # schemas dir not present — use temp path directly after creating parent
            path = save_golden(self.source, dest)
            self.assertTrue(path.is_file())
            loaded = load_golden(path)
            self.assertEqual(loaded["fixture_sha256"], self.golden["fixture_sha256"])
            # Idempotent: second save with same SHA returns without error
            path2 = save_golden(self.source, dest)
            self.assertEqual(path, path2)

    def test_verify_golden_rejects_mutated_auth_flags(self):
        import copy
        bad = copy.deepcopy(self.golden)
        bad["auth_flags"]["release_allowed"] = True
        with self.assertRaises(GoldenFixtureError):
            verify_golden(bad, self.source)

    def test_verify_golden_rejects_mismatched_sha(self):
        import copy
        bad = copy.deepcopy(self.golden)
        bad["fixture_sha256"] = "0" * 64
        with self.assertRaises(GoldenFixtureError):
            verify_golden(bad, self.source)

    def test_route_fallback_contract_all_screen_states_have_disabled_reason(self):
        """VUF-M01-008: every row in the matrix must have an explicit fallback.

        This exercises the route/dynamic-action fallback contract binding
        described in the task: each of the 680 matrix rows and 1120 screen-state
        rows must carry a non-empty disabled_reason or locale_fallback.
        """
        for row in self.matrix["matrix"]:
            with self.subTest(surface=row["engine_surface_kind"],
                              state=row["engine_player_state_kind"],
                              profile=row["profile_id"]):
                self.assertTrue(row["disabled_reason"])
                self.assertTrue(row["localized_fallback"])
                self.assertFalse(row["route_enabled"])
                self.assertFalse(row["action_enabled"])
        for row in self.matrix["screen_states"]:
            with self.subTest(screen=row["screen_key"], state=row["engine_player_state_kind"],
                              profile=row["profile_id"]):
                self.assertTrue(row["disabled_reason_fallback"])
                self.assertFalse(row["action_enabled"])
                self.assertIsNone(row["actual_engine_route"])


if __name__ == "__main__":
    unittest.main()
