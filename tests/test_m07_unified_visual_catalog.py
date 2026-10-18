"""M07 milestone cross-language source contract parity, not Unity runtime QA.

Reads the actual C# Editor catalog (as source), not a hand-copied golden,
and checks every named event and symbol against the existing Python R50/R54
view-only timeline. A verified test here checks SOURCE only: human Editor GUI,
mobile performance, Engine final release parity and art ownership remain OPEN.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

from factory.visual_director.special_skin_map import SPECIAL_KINDS, pair_key
from factory.vfx_builder.view_event_timeline import (
    CHANNELS, DURATIONS_MS, EVENTS, PRESET_FOR_EVENT, PRIORITIES,
    PROFILES, build_timeline, verify_timeline,
)

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "unity_package" / "Editor" / "VufVisualEventCatalog.cs"
STUDIO = ROOT / "unity_package" / "Editor" / "VufUnifiedVisualStudioWindow.cs"
PARSER = re.compile(
    r'new Entry\("([a-z_]+)", "([a-z_]+)", (\d+), (\d+), (null|"[A-Za-z]+")\)'
)
PAIR_ORDER = [x[0] for x in SPECIAL_KINDS]


class UnifiedVisualCatalogSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = CATALOG.read_text(encoding="utf-8")
        cls.studio = STUDIO.read_text(encoding="utf-8")

    def test_fourteen_event_channels_priorities_durations_and_donor_presets_match(self):
        seen = PARSER.findall(self.catalog)
        self.assertEqual(len(seen), 14)
        self.assertEqual([row[0] for row in seen], list(EVENTS))
        for name, channel, priority, duration, preset in seen:
            with self.subTest(event=name):
                self.assertEqual(channel, CHANNELS[name])
                self.assertEqual(int(priority), PRIORITIES[name])
                self.assertEqual(int(duration), DURATIONS_MS[name])
                self.assertEqual(
                    None if preset == "null" else preset.strip('"'),
                    PRESET_FOR_EVENT[name])

    def test_five_profiles_and_exact_engine_specials_match_python_contracts(self):
        for profile in PROFILES:
            self.assertIn(f'"{profile}"', self.catalog)
        self.assertEqual(len(PROFILES), 5)
        for name in PAIR_ORDER:
            self.assertIn(f'"{name}"', self.catalog)
        self.assertIn("pair", self.catalog.lower())
        self.assertEqual(len({pair_key(a, b) for a in PAIR_ORDER
                              for b in PAIR_ORDER}), 15)

    def test_mute_audio_haptic_are_log_only_never_engine_cues(self):
        self.assertIn("MUTED_NO_AUDIO", self.catalog)
        self.assertIn("MUTED_NO_HAPTIC", self.catalog)
        self.assertIn("LOG ONLY, AUDIO NOT PLAYED", self.catalog)
        self.assertIn("LOG ONLY, HAPTIC NOT PLAYED", self.catalog)
        self.assertIn("MayMutateGameplay => false", self.catalog)
        self.assertIn("ArtRightsOwnerApproved => false", self.catalog)
        self.assertIn("ProductionEventParityProven => false", self.catalog)
        self.assertIn("actual_device_fps_verified = false", self.studio)
        self.assertIn("actual_gpu_draw_calls_verified = false", self.studio)
        self.assertIn("release_allowed = false", self.studio)

    def test_studio_consumes_actual_existing_sdk_modules_and_guards_disk(self):
        # The Editor canvas uses the already-in-repo procedural presets and
        # runtime preview, rather than mutating MATCH3_ENGINE or installing FX.
        self.assertIn("VufSpritePlaybackPreview", self.studio)
        self.assertIn("VufVfxLabWindow.BuildCandidateParticleSystem", self.studio)
        self.assertIn("VufFxSheetPreviewWindow.Parse", self.studio)
        self.assertIn("VufVisualEventCatalog.ViewEventKey", self.studio)
        self.assertIn("FileMode.CreateNew", self.studio)
        self.assertIn("DontSaveInEditor", self.studio)
        self.assertIn("DontSaveInBuild", self.studio)
        self.assertIn("void ExportOwnerReviewReceipt()", self.studio)
        self.assertNotIn("AssetDatabase.CreateAsset(", self.studio)
        self.assertNotIn("AssetDatabase.DeleteAsset(", self.studio)
        self.assertNotIn("TextureImporter.SaveAndReimport(", self.studio)

    def test_all_five_python_profile_view_events_still_verify_strict_candidates(self):
        for profile in PROFILES:
            for event in EVENTS:
                kwargs = (
                    {"special": "HorizontalLine"} if event == "special_trigger"
                    else {"special": "Area", "second_special": "Targeted"}
                    if event == "combo_chain" else {}
                )
                packet = build_timeline(profile, event, **kwargs)
                verify_timeline(packet)
                self.assertFalse(packet["owner_art_approved"])
                self.assertFalse(packet["engine_board_mutations"])
                self.assertFalse(packet["device_audio_haptic_verified"])
                self.assertFalse(packet["release_allowed"])


if __name__ == "__main__":
    unittest.main()
