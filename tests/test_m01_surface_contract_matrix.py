"""M01 read-only five-title Engine UI surface source grid; not Unity runtime."""
from __future__ import annotations

import copy
import hashlib
import json
import unittest

from factory.ui_composer.m01_surface_contract_matrix import (
    AUTH_FALSE, CATALOG, CANONICAL_CATALOG_GIT_BLOB,
    ENGINE_ACTION_KINDS, ENGINE_STATES, ENGINE_SURFACES,
    M01MatrixError, SCREEN_SURFACES, STAGE, _blob_sha,
    build_m01_matrix, verify_m01_matrix,
)


class M01CanonicalSurfaceSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = CATALOG.read_bytes()
        cls.matrix = build_m01_matrix(cls.source)

    def test_exact_original_coral_screen_schema_git_blob_pinned(self):
        self.assertEqual(_blob_sha(self.source), CANONICAL_CATALOG_GIT_BLOB)
        self.assertEqual(self.matrix["source_catalog_blob_sha1"],
                         CANONICAL_CATALOG_GIT_BLOB)
        self.assertEqual(len(self.matrix["screens"]), 28)
        self.assertEqual([s["screen_id"] for s in self.matrix["screens"]],
                         ["COR-%02d" % i for i in range(1, 29)])
        self.assertEqual(set(SCREEN_SURFACES),
                         {s["screen_key"] for s in self.matrix["screens"]})
        self.assertEqual([s["screen_key"] for s in self.matrix["screens"][-2:]],
                         ["home", "gameplay_hud"])

    def test_exact_680_five_theme_x_17_official_engine_surface_x_8_states(self):
        self.assertEqual(self.matrix["stage"], STAGE)
        self.assertEqual(len(self.matrix["profile_ids"]), 5)
        self.assertEqual(len(ENGINE_SURFACES), 17)
        self.assertEqual(len(ENGINE_STATES), 8)
        self.assertEqual(len(ENGINE_ACTION_KINDS), 4)
        self.assertEqual(self.matrix["surface_state_count_per_profile"], 136)
        self.assertEqual(len(self.matrix["matrix"]), 680)
        self.assertEqual(len({(m["profile_id"], m["engine_surface_kind"],
                              m["engine_player_state_kind"])
                              for m in self.matrix["matrix"]}), 680)
        self.assertEqual(set(self.matrix["engine_ui_surface_kinds"]),
                         set(ENGINE_SURFACES))
        self.assertEqual(set(self.matrix["engine_player_state_kinds"]),
                         set(ENGINE_STATES))

    def test_engine_surface_candidates_do_not_forge_gameplay_binds(self):
        for row in self.matrix["matrix"]:
            self.assertFalse(row["route_enabled"])
            self.assertFalse(row["action_enabled"])
            self.assertFalse(row["real_player_state_bound"])
            self.assertFalse(row["runtime_screen_binding_available"])
            self.assertIsNone(row["actual_engine_action_id"])
            self.assertTrue(row["disabled_reason"])
            self.assertTrue(row["localized_fallback"])
        for flag in AUTH_FALSE:
            self.assertIs(self.matrix[flag], False)

    def test_inert_28_screen_actions_policy_and_localized_fallback(self):
        protected = {s["screen_key"] for s in self.matrix["screens"]
                     if s["policy_feature_off"]}
        self.assertEqual(
            protected,
            {"events_hub", "season_pass", "tournament",
             "friends", "leaderboard"},
        )
        for row in self.matrix["screens"]:
            self.assertFalse(row["action_enabled"])
            self.assertFalse(row["screen_real_binding_available"])
            self.assertIsNone(row["actual_engine_command_key"])
            self.assertIsNone(row["actual_engine_destination"])
            self.assertIsNone(row["actual_engine_action_id"])
            self.assertEqual(row["policy_feature_off"],
                             row["screen_key"] in protected)
            self.assertTrue(row["text_key"].startswith("ui."))
            self.assertTrue(row["icon_key"].endswith(".icon"))
            self.assertTrue(row["disabled_reason_fallback"])
            self.assertTrue(row["owner_review_required"])

    def test_five_draft_themes_inherit_identical_semantic_route_grid(self):
        anchor = [(row["engine_surface_kind"], row["engine_player_state_kind"],
                   row["candidate_coral_screen_ids"], row["action_enabled"])
                  for row in self.matrix["matrix"]
                  if row["profile_id"] == "Coral_Rescue"]
        self.assertEqual(len(anchor), 136)
        for profile in self.matrix["profile_ids"]:
            view = [(row["engine_surface_kind"], row["engine_player_state_kind"],
                     row["candidate_coral_screen_ids"], row["action_enabled"])
                    for row in self.matrix["matrix"]
                    if row["profile_id"] == profile]
            self.assertEqual(view, anchor)
        absent = {row["engine_surface_kind"]
                  for row in self.matrix["matrix"]
                  if row["source_screens_absent"]}
        self.assertEqual(absent, {"Settings", "Booster", "Store", "Consent"})
        for row in self.matrix["matrix"]:
            self.assertEqual(row["source_screens_absent"],
                             row["missing_real_screen_reason"] is not None)

    def test_read_only_deterministic_sha_receipt_and_no_source_writes(self):
        first = build_m01_matrix(self.source)
        second = build_m01_matrix(self.source)
        verify_m01_matrix(first, self.source)
        self.assertEqual(first, second)
        self.assertEqual(len(first["matrix_sha256"]), 64)
        self.assertEqual(hashlib.sha256(json.dumps(
            {key: val for key, val in first.items() if key != "matrix_sha256"},
            sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        ).encode()).hexdigest(), first["matrix_sha256"])

    def test_missing_or_changed_canonical_screen_bytes_fail_closed(self):
        for source in (
            b"", b"{}",
            self.source.replace(b"gameplay_hud", b"new_gameplay"),
            self.source.replace(b"world_map", b"world_maP"),
            self.source + b"\n",
        ):
            with self.subTest(source=source[:24]), self.assertRaises(M01MatrixError):
                build_m01_matrix(source)

    def test_forged_owner_permission_surface_or_route_rejected(self):
        for path, value in (
            (("release_allowed",), True),
            (("engine_actions_bound",), True),
            (("matrix", 0, "route_enabled"), True),
            (("matrix", 1, "engine_surface_kind"), "NotOfficial"),
            (("matrix", 0, "candidate_coral_screen_ids"), []),
            (("screens", 0, "action_enabled"), True),
            (("screens", 0, "feature_gate"), "PRODUCTION_ON"),
            (("matrix_sha256",), "0" * 64),
        ):
            with self.subTest(path=path):
                changed = copy.deepcopy(self.matrix)
                node = changed
                for part in path[:-1]:
                    node = node[part]
                node[path[-1]] = value
                with self.assertRaises(M01MatrixError):
                    verify_m01_matrix(changed, self.source)

    def test_unbound_engine_surfaces_still_have_explicit_disabled_fallback(self):
        for row in self.matrix["matrix"]:
            if row["source_screens_absent"]:
                self.assertEqual(row["candidate_coral_screen_ids"], [])
                self.assertEqual(row["missing_real_screen_reason"],
                                 "NO_CANONICAL_CORAL_SCREEN_FOR_ENGINE_SURFACE")
            else:
                self.assertGreater(len(row["candidate_coral_screen_ids"]), 0)
            self.assertEqual(set(row["engine_action_kind_namespace"]),
                             set(ENGINE_ACTION_KINDS))


if __name__ == "__main__":
    unittest.main()
