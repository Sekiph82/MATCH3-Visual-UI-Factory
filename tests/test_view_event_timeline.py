"""VUF-M07 view-only replay/event source contracts, not Unity GUI/device tests."""
import copy
import unittest

from factory.vfx_builder.view_event_timeline import (
    DURATIONS_MS, EVENTS, FULL_SPEEDS, PRESET_FOR_EVENT, PRIORITIES,
    PROFILES, STAGE, TimelineError, build_timeline, sample_timeline,
    verify_timeline,
)
from factory.visual_director.special_skin_map import SPECIAL_KINDS


class ViewEventTimelineTests(unittest.TestCase):
    def test_all_five_titles_cover_fourteen_typed_events_without_gameplay_authority(self):
        self.assertEqual(len(EVENTS), 14)
        self.assertEqual(len(PROFILES), 5)
        self.assertEqual(set(EVENTS), set(PRESET_FOR_EVENT))
        self.assertEqual(set(EVENTS), set(DURATIONS_MS))
        self.assertEqual(set(EVENTS), set(PRIORITIES))
        all_keys = set()
        for profile in PROFILES:
            for event in EVENTS:
                args = {"special": "HorizontalLine"} if event == "special_trigger" else (
                    {"special": "Area", "second_special": "Color"}
                    if event == "combo_chain" else {})
                packet = build_timeline(profile, event, **args)
                verify_timeline(packet)
                self.assertEqual(packet["stage"], STAGE)
                self.assertFalse(packet["engine_board_mutations"])
                self.assertFalse(packet["reward_or_save_mutations"])
                self.assertFalse(packet["audio_or_haptic_actuated"])
                self.assertFalse(packet["owner_art_approved"])
                self.assertFalse(packet["release_allowed"])
                self.assertNotIn(packet["visual_key"], all_keys)
                all_keys.add(packet["visual_key"])
        self.assertEqual(len(all_keys), 70)

    def test_normalized_frame_times_are_monotonic_and_exactly_bounded(self):
        for event in EVENTS:
            args = {"special": "Area"} if event == "special_trigger" else (
                {"special": "Area", "second_special": "Targeted"}
                if event == "combo_chain" else {})
            p = build_timeline(PROFILES[0], event, **args)
            stamps = [f["time_ms"] for f in p["keyframes"]]
            self.assertEqual(len(stamps), 5)
            self.assertEqual(stamps[0], 0)
            self.assertEqual(stamps[-1], p["duration_ms"])
            self.assertEqual(stamps, sorted(stamps))
            self.assertEqual(p["keyframes"][0]["normalized_progress_milli"], 0)
            self.assertEqual(p["keyframes"][-1]["normalized_progress_milli"], 1000)

    def test_reduced_motion_static_fallback_never_runs_particles(self):
        p = build_timeline("Coral_Rescue", "level_win",
                           reduced_motion=True, seed=42)
        self.assertEqual(p["duration_ms"], 40)
        self.assertEqual(len(p["keyframes"]), 2)
        self.assertIsNone(p["vfx_preset_id"])
        self.assertTrue(p["reduced_motion_static_fallback"])
        verify_timeline(p)

    def test_muted_preview_only_logs_none_and_never_activates_audio(self):
        p = build_timeline("Wonder_Pop", "reward_claim", muted=True)
        self.assertIsNone(p["audio_cue_log_only"])
        self.assertIsNone(p["haptic_cue_log_only"])
        self.assertFalse(p["audio_or_haptic_actuated"])
        verify_timeline(p)

    def test_real_engine_special_and_unordered_combo_are_symbolically_canonical(self):
        self.assertEqual(len(SPECIAL_KINDS), 5)
        a = build_timeline("Garage_Legends", "combo_chain",
                           special="Area", second_special="Targeted")
        b = build_timeline("Garage_Legends", "combo_chain",
                           special="Targeted", second_special="Area")
        self.assertEqual(a, b)
        self.assertIn("area__targeted", a["visual_key"])
        verify_timeline(a)
        single = build_timeline("Coral_Rescue", "special_trigger",
                                special="HorizontalLine")
        self.assertIn("horizontal_line", single["visual_key"])
        verify_timeline(single)

    def test_unrelated_event_cannot_pretend_to_be_engine_special(self):
        with self.assertRaises(TimelineError):
            build_timeline("Dino_Islands", "tile_match", special="Area")
        with self.assertRaises(TimelineError):
            build_timeline("Dino_Islands", "special_trigger", special="Color",
                           second_special="Targeted")
        with self.assertRaises(TimelineError):
            build_timeline("Dino_Islands", "combo_chain", special="Area")

    def test_unknown_title_event_and_invalid_seed_mode_rejected(self):
        for args in [
            ("made_up", "tile_spawn", {}),
            ("Coral_Rescue", "purchase_rewards", {}),
            ("Coral_Rescue", "tile_spawn", {"seed": -1}),
            ("Coral_Rescue", "tile_spawn", {"seed": True}),
            ("Coral_Rescue", "tile_spawn", {"reduced_motion": 1}),
        ]:
            with self.subTest(params=args), self.assertRaises(TimelineError):
                build_timeline(args[0], args[1], **args[2])

    def test_forged_signature_frames_owner_approval_or_runtime_authority_rejected(self):
        src = build_timeline("Coral_Rescue", "level_fail")
        for key, forged in [
            ("replay_sha256", "f" * 64),
            ("release_allowed", True),
            ("engine_board_mutations", True),
            ("view_channel", "paywall"),
            ("visual_priority_only", 200),
        ]:
            m = copy.deepcopy(src)
            m[key] = forged
            with self.subTest(key=key), self.assertRaises(TimelineError):
                verify_timeline(m)
        m = copy.deepcopy(src)
        m["keyframes"][2]["frame_index"] = 100
        with self.assertRaises(TimelineError):
            verify_timeline(m)

    def test_manual_preview_speed_interrupt_and_fixed_replay_cursor(self):
        p = build_timeline("The_Fractured_Realms", "level_win", seed=41)
        for speed in FULL_SPEEDS:
            out = sample_timeline(p, elapsed_ms=250, speed=speed)
            self.assertEqual(out["replay_sha256"], p["replay_sha256"])
            self.assertFalse(out["gameplay_mutations"])
            self.assertFalse(out["save_or_reward_mutations"])
            self.assertFalse(out["sound_or_haptic_playback"])
        stopped = sample_timeline(p, elapsed_ms=250, speed=1.0,
                                  interrupted=True)
        self.assertFalse(stopped["draw_candidate_frame"])
        self.assertTrue(stopped["view_canceled_only"])
        self.assertEqual(stopped, sample_timeline(
            p, elapsed_ms=250, speed=1.0, interrupted=True))

    def test_unsafe_speed_time_or_unverified_packet_rejected(self):
        p = build_timeline("Coral_Rescue", "ui_open")
        for opts in [
            {"elapsed_ms": -1},
            {"elapsed_ms": 100, "speed": 5},
            {"elapsed_ms": 100, "speed": True},
            {"elapsed_ms": 100, "interrupted": 0},
        ]:
            with self.subTest(opts=opts), self.assertRaises(TimelineError):
                sample_timeline(p, **opts)
        forged = copy.deepcopy(p)
        forged["stage"] = "APPROVED"
        with self.assertRaises(TimelineError):
            sample_timeline(forged, elapsed_ms=100)


if __name__ == "__main__":
    unittest.main()
