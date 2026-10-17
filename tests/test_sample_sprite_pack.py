"""R52 five-game physically materialized mathematical sample atlas tests."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from factory.image_processor.png_pipeline import decode_png
from factory.visual_director.sample_sprite_pack import (
    PROFILES, SamplePackError, build_sample_pack, export_sample_pack,
)
from factory.validators.atlas_candidate_audit import audit_candidate


class SampleSpritePackTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def test_all_five_have_38_distinct_original_candidate_pngs(self):
        checks = []
        for profile in PROFILES:
            manifest, sprites = build_sample_pack(profile, side=32)
            self.assertEqual(manifest["profile_id"], profile)
            self.assertEqual(manifest["prototype_count"], 38)
            self.assertEqual(len(sprites), 38)
            self.assertFalse(manifest["release_allowed"])
            self.assertFalse(manifest["owner_aesthetic_approval"])
            self.assertFalse(manifest["engine_final_sha_verified"])
            self.assertEqual(len({hashlib.sha256(b).hexdigest() for b in
                                  sprites.values()}), 38)
            checks.append(next(iter(sprites.values())))
        self.assertEqual(len({hashlib.sha256(s).hexdigest()
                              for s in checks}), 5)

    def test_real_rgba8_alpha_in_all_sprites(self):
        _, images = build_sample_pack("Coral_Rescue", 48)
        for item in images.values():
            width, height, rgba = decode_png(item)
            self.assertEqual((width, height), (48, 48))
            self.assertEqual(len(rgba), 48 * 48 * 4)
            self.assertTrue(any(a != 0 for a in rgba[3::4]))

    def test_externally_exported_real_atlas_passes_byte_audit(self):
        out = self.root / "coral_candidate"
        report = export_sample_pack("Coral_Rescue", out, side=32)
        self.assertEqual(report["sample_count"], 38)
        self.assertFalse(report["release_allowed"])
        manifest = json.loads((out / "sample_manifest.json").read_text("utf-8"))
        self.assertEqual(len(manifest["assets"]), 38)
        expected = [r["file"][:-4] for r in manifest["assets"]]
        verification = audit_candidate(out / "atlas", required_ids=expected)
        self.assertEqual(verification["sprite_count"], 38)
        self.assertFalse(verification["owner_art_approved"])
        self.assertFalse(verification["real_device_verified"])

    def test_five_sample_packs_have_separate_theme_identity(self):
        themes = set()
        for theme in PROFILES:
            out = self.root / theme
            receipt = export_sample_pack(theme, out, side=32)
            themes.add(receipt["atlas_sha256"])
            self.assertTrue((out / "atlas/atlas_manifest.json").is_file())
        self.assertEqual(len(themes), 5)

    def test_refuse_existing_output_and_protect_original(self):
        source = self.root / "existing"
        source.mkdir()
        sentinel = source / "owner.txt"
        sentinel.write_text("preserve", encoding="utf-8")
        with self.assertRaisesRegex(SamplePackError, "overwrite"):
            export_sample_pack("Garage_Legends", source)
        self.assertEqual(sentinel.read_text("utf-8"), "preserve")

    def test_bad_game_id_and_size(self):
        with self.assertRaises(SamplePackError):
            build_sample_pack("Bad_Game", 48)
        with self.assertRaises(SamplePackError):
            build_sample_pack("Wonder_Pop", side=-2)
        with self.assertRaises(SamplePackError):
            build_sample_pack("Wonder_Pop", side=9999)

    def test_no_writes_until_explicit_export(self):
        before = set(self.root.iterdir())
        build_sample_pack("Garage_Legends", 32)
        self.assertEqual(before, set(self.root.iterdir()))

    def test_missing_actual_sample_file_detected_in_atlas_audit(self):
        export_sample_pack("Coral_Rescue", self.root / "real_pack", 32)
        atlas = self.root / "real_pack/atlas"
        with self.assertRaisesRegex(ValueError, "missing required"):
            audit_candidate(atlas, required_ids=["sample_999"])

    def test_output_is_never_approved_production_art(self):
        manifest, _ = build_sample_pack("The_Fractured_Realms", 32)
        self.assertEqual(manifest["source_art"], "ORIGINAL_MATHEMATICAL_PLACEHOLDER")
        self.assertFalse(manifest["right_to_production_assets_verified"])
        self.assertFalse(manifest["gameplay_or_rewards_authority"])


if __name__ == "__main__":
    unittest.main()
