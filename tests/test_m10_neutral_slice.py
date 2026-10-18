"""M10 whole-milestone neutral fixture tests; no fabricated Engine WIN."""
from __future__ import annotations
import copy
import hashlib
import unittest

from factory.integration.m10_neutral_slice import (
    BASE_ROUTE, CORAL_EXTRA, CORAL_IDS, PROFILES,
    STAGE, NeutralSliceError, assert_theme_isolation,
    build_slice, inspect_attached_external_bytes, verify_slice,
)


class M10NeutralSliceTests(unittest.TestCase):
    def test_five_titles_have_nine_source_routes_but_only_coral_has_three_more(self):
        for profile in PROFILES:
            with self.subTest(profile=profile):
                s = build_slice(profile)
                self.assertEqual(s["stage"], STAGE)
                self.assertEqual(len(s["visual_review_routes"]),
                                 12 if profile == "Coral_Rescue" else 9)
                self.assertEqual(s["visual_review_routes"][0]["route_key"], "home")
                self.assertIn("gameplay_hud", [x["route_key"] for x in s["visual_review_routes"]])
                self.assertFalse(s["real_engine_replay_verified"])
                self.assertFalse(s["level_won_or_reward_claimed"])
                self.assertFalse(s["release_allowed"])
                verify_slice(s)

    def test_coral_real_source_schema_route_alias_is_not_an_offline_game_service(self):
        s = build_slice("Coral_Rescue")
        routes = {r["route_key"]: r for r in s["visual_review_routes"]}
        self.assertEqual(routes["home"]["coral_schema_screen_id"], "COR-27")
        self.assertEqual(routes["gameplay_hud"]["coral_schema_screen_id"], "COR-28")
        self.assertEqual(routes["offline"]["coral_schema_screen_id"], "COR-22")
        self.assertIn("reef_restoration", routes)
        self.assertIn("my_aquarium", routes)
        self.assertIn("region_unlocked", routes)
        self.assertEqual(routes["level_won"]["screen_binding"], "CANDIDATE_UNBOUND")

    def test_visual_revision_changes_cannot_touch_frozen_synthetic_reference(self):
        a = build_slice("Wonder_Pop", theme_revision="blue_01")
        b = build_slice("Wonder_Pop", theme_revision="amber_02")
        check = assert_theme_isolation(a, b)
        self.assertEqual(check["theme_a"], "blue_01")
        self.assertEqual(check["theme_b"], "amber_02")
        self.assertFalse(check["checked_real_engine_game_state"])
        self.assertFalse(check["production_replay_parity"])

    def test_replay_win_score_save_difficulty_forgery_is_rejected(self):
        for field, value in [
            ("score", 100), ("has_real_win", True), ("has_real_moves", True),
            ("save_revision", "fake"), ("difficulty", 0.14),
            ("replay_sha256", "a"*64), ("mock_seed", 35),
        ]:
            s = build_slice("Coral_Rescue")
            s["frozen_reference"][field] = value
            with self.subTest(field=field), self.assertRaises(NeutralSliceError):
                verify_slice(s)

    def test_false_approvals_and_cross_game_screen_ids_rejected(self):
        s = build_slice("Coral_Rescue")
        s["release_allowed"] = True
        with self.assertRaises(NeutralSliceError):
            verify_slice(s)
        s = build_slice("Dino_Islands")
        s["visual_review_routes"][0]["runtime_screen_defined_for_this_profile"] = True
        with self.assertRaises(NeutralSliceError):
            verify_slice(s)
        s = build_slice("Dino_Islands")
        s["visual_review_routes"][0]["coral_schema_screen_id"] = "COR-99"
        with self.assertRaises(NeutralSliceError):
            verify_slice(s)

    def test_bad_theme_level_seed_input_never_synthesizes_gameplay(self):
        for kwargs in (
            {"profile":"Unknown"}, {"profile":"Coral_Rescue","mock_level":True},
            {"profile":"Coral_Rescue","mock_level":0},
            {"profile":"Coral_Rescue","mock_seed":-1},
            {"profile":"Coral_Rescue","theme_revision":"../../private"},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(NeutralSliceError):
                build_slice(**kwargs)

    def test_real_external_candidate_blob_is_only_sha_pinned_opaque_data(self):
        raw = b'{"level":7, "winning":true, "claimedEngine":true}'
        sha = hashlib.sha256(raw).hexdigest()
        result = inspect_attached_external_bytes(raw, sha)
        self.assertEqual(result["source_sha256"], sha)
        self.assertFalse(result["schema_verified_as_lfx"])
        self.assertFalse(result["engine_sha_pinned"])
        self.assertFalse(result["neutral_replay_verified"])
        with self.assertRaises(NeutralSliceError):
            inspect_attached_external_bytes(raw+b"x", sha)
        with self.assertRaises(NeutralSliceError):
            inspect_attached_external_bytes(raw, "f"*64)

    def test_frozen_reference_is_not_gameplay_authority_or_replay_hash(self):
        fixture = build_slice("Coral_Rescue", mock_level=11, mock_seed=42)
        self.assertEqual(fixture["frozen_reference"]["score"], None)
        self.assertEqual(fixture["frozen_reference"]["difficulty"], None)
        self.assertEqual(fixture["frozen_reference"]["replay_sha256"], None)
        self.assertTrue(fixture["frozen_reference_sha256"])
        self.assertFalse(assert_theme_isolation(
            fixture, build_slice("Coral_Rescue"))["owner_art_approved"])


if __name__ == "__main__":
    unittest.main()
