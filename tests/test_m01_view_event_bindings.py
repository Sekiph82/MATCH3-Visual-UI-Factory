"""M01 genuine-format M3P1 parser wired ONLY to inert M07 timeline previews."""
from __future__ import annotations

import base64
import copy
import hashlib
import unittest

from factory.ui_composer.m01_view_event_bindings import (
    FLAG_FALSE, MAX_PREVIEW_EVENTS, M01EventError, STAGE, UNBOUND_REASON,
    build_event_preview, build_unbound_family_slot, verify_event_preview
)
from factory.integration.cross_factory_contract import PROFILES


def wire(profile="Coral_Rescue", kinds=(1, 6, 0, 2, 3, 4, 5)):
    lines = ["M3P1", profile, str(len(kinds))]
    for i, kind in enumerate(kinds, 1):
        name = base64.b64encode(("source_event_%d" % i).encode()).decode()
        key = base64.b64encode(b"draft_source_key").decode()
        lines.append("%d|%s|%d|%s|0|0:0:0" % (i, name, kind, key))
    body = ("\n".join(lines) + "\n").encode()
    return body + hashlib.sha256(body).hexdigest().encode()


class M01VisualEventSourceTests(unittest.TestCase):
    def setUp(self):
        self.wire = wire()

    def test_known_source_event_kind_cues_only_tile_match_and_spawn_preview(self):
        packet = build_event_preview(self.wire, "Coral_Rescue")
        verify_event_preview(packet, self.wire)
        self.assertEqual(packet["stage"], STAGE)
        self.assertEqual(packet["candidate_event_count"], 7)
        self.assertEqual(packet["unbound_events"], 5)
        rows = packet["candidate_events"]
        self.assertEqual([r["engine_event_kind_ordinal"] for r in rows],
                         [1, 6, 0, 2, 3, 4, 5])
        self.assertEqual([r["candidate_vuf_cue"] for r in rows],
                         ["tile_match", "tile_spawn", None, "special_trigger",
                          "special_trigger", "special_trigger", "combo_chain"])
        self.assertTrue(rows[0]["cue_renderable_in_visual_preview"])
        self.assertTrue(rows[1]["cue_renderable_in_visual_preview"])
        self.assertFalse(any(r["cue_renderable_in_visual_preview"]
                             for r in rows[2:]))
        for flag in FLAG_FALSE:
            self.assertIs(packet[flag], False)

    def test_special_swap_combo_unbound_not_fake_authenticated_variants(self):
        packet = build_event_preview(self.wire, "Coral_Rescue")
        for row in packet["candidate_events"][2:]:
            self.assertIsNone(row["view_timeline"])
            self.assertEqual(row["unbound_reason"],
                             UNBOUND_REASON[row["engine_event_kind_ordinal"]])
            self.assertFalse(row["real_gameplay_event_verified"])
            self.assertFalse(row["actual_engine_instance_id_bound"])

    def test_reduced_motion_and_muted_are_visual_only_no_device_activation(self):
        full = build_event_preview(self.wire, "Coral_Rescue")
        lite = build_event_preview(
            self.wire, "Coral_Rescue", reduced_motion=True, muted=True)
        verify_event_preview(lite, self.wire)
        self.assertNotEqual(full["preview_sha256"], lite["preview_sha256"])
        self.assertTrue(lite["reduced_motion"])
        for row in lite["candidate_events"][:2]:
            timeline = row["view_timeline"]
            self.assertEqual(timeline["duration_ms"], 40)
            self.assertTrue(timeline["reduced_motion_static_fallback"])
            self.assertIsNone(timeline["audio_cue_log_only"])
            self.assertIsNone(timeline["haptic_cue_log_only"])
            self.assertFalse(timeline["audio_or_haptic_actuated"])
            self.assertFalse(timeline["engine_board_mutations"])
            self.assertFalse(timeline["reward_or_save_mutations"])

    def test_five_profiles_all_share_visual_cue_taxonomy_and_no_owner_approval(self):
        for profile in PROFILES:
            packet = build_event_preview(wire(profile), profile)
            verify_event_preview(packet, wire(profile))
            self.assertEqual(packet["candidate_event_count"], 7)
            self.assertEqual(packet["unbound_events"], 5)
            self.assertFalse(packet["owner_art_approved"])
            self.assertFalse(packet["release_allowed"])
            self.assertTrue(packet["candidate_events"][0]["view_timeline"][
                "visual_key"].startswith(profile.lower() + ".anim."))

    def test_goal_obstacle_booster_mapping_explicitly_unbound_not_synthesized(self):
        for profile in PROFILES:
            for family in ("goal_progress", "obstacle_hit", "booster_activate"):
                slot = build_unbound_family_slot(profile, family)
                self.assertIsNone(slot["actual_engine_instance_id"])
                self.assertFalse(slot["candidate_animation_bindable"])
                self.assertFalse(slot["engine_event_origin_authenticated"])
                self.assertFalse(slot["release_allowed"])
        for name, family in (("Unrecognized", "goal_progress"),
                             ("Coral_Rescue", "actual_reward")):
            with self.assertRaises(M01EventError):
                build_unbound_family_slot(name, family)

    def test_reject_invalid_m3p1_checksum_profile_and_event_kind(self):
        for bad, profile in (
            (self.wire + b"x", "Coral_Rescue"),
            (self.wire, "Garage_Legends"),
            (wire(kinds=(9,)), "Coral_Rescue"),
            (wire(kinds=(1,))[:-1] + b"0", "Coral_Rescue"),
        ):
            with self.subTest(bad=bad[:20]), self.assertRaises(M01EventError):
                build_event_preview(bad, profile)
        with self.assertRaises(M01EventError):
            build_event_preview(self.wire, "Coral_Rescue", muted="false")

    def test_bounded_preview_fails_closed_above_128_actual_wire_events(self):
        too_many = wire(kinds=(1,) * (MAX_PREVIEW_EVENTS + 1))
        with self.assertRaises(M01EventError):
            build_event_preview(too_many, "Coral_Rescue")

    def test_forged_source_event_owner_release_timeline_and_sha_rejected(self):
        original = build_event_preview(self.wire, "Coral_Rescue")
        cases = (
            (("release_allowed",), True),
            (("engine_event_origin_authenticated",), True),
            (("candidate_events", 0, "real_gameplay_event_verified"), True),
            (("candidate_events", 0, "view_timeline", "release_allowed"), True),
            (("candidate_events", 0, "source_event_id"), "fake_event"),
            (("preview_sha256",), "a" * 64),
        )
        for path, value in cases:
            with self.subTest(path=path):
                changed = copy.deepcopy(original)
                node = changed
                for part in path[:-1]:
                    node = node[part]
                node[path[-1]] = value
                with self.assertRaises(M01EventError):
                    verify_event_preview(changed, self.wire)


if __name__ == "__main__":
    unittest.main()
