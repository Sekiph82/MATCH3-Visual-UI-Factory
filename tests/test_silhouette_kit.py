"""Five-profile six-silhouette generated candidate pixel regression."""
import hashlib
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from factory.image_processor.png_pipeline import decode_png
from factory.visual_director.silhouette_kit import (
    PROFILES, SHAPES, PrototypeError, build_theme_kit, write_once, main
)


class SilhouetteKitTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.directory = Path(temp.name)

    def test_all_five_profiles_generate_six_original_math_sprites(self):
        seen = set()
        for profile in PROFILES:
            with self.subTest(profile=profile):
                manifest, files = build_theme_kit(profile, side=32)
                self.assertEqual(set(manifest["silhouette_keys"]), set(SHAPES))
                self.assertEqual(len(files), 7)
                self.assertFalse(manifest["asset_rights_verified"])
                self.assertFalse(manifest["owner_visual_approval"])
                self.assertEqual(manifest["stage"], "CANDIDATE_NOT_OWNER_APPROVED")
                self.assertEqual(manifest["atlas_dimensions"], [96, 64])
                _, _, rgba = decode_png(files["tile_circle.png"])
                seen.add(hashlib.sha256(rgba).hexdigest())
        self.assertEqual(len(seen), 5)

    def test_shapes_are_really_different_silhouettes(self):
        _, files = build_theme_kit("Coral_Rescue", 48)
        masks = []
        for shape in SHAPES:
            w, h, pixels = decode_png(files["tile_" + shape + ".png"])
            self.assertEqual((w, h), (48, 48))
            alpha = bytes(pixels[3::4])
            self.assertGreater(max(alpha), 0)
            self.assertEqual(alpha[0], 0)
            masks.append(hashlib.sha256(alpha).hexdigest())
        self.assertEqual(len(set(masks)), 6)

    def test_atlas_matches_each_png_rgba_exactly(self):
        manifest, pngs = build_theme_kit("Dino_Islands", side=32)
        width, _, combined = decode_png(pngs["tile_atlas.png"])
        for tile in manifest["tiles"]:
            x, y, size, _ = tile["pixel_rect_top_left"]
            _, _, source = decode_png(pngs[tile["file"]])
            region = b"".join(
                combined[((y + line) * width + x) * 4:
                         ((y + line) * width + x + size) * 4]
                for line in range(size))
            self.assertEqual(region, source)
            self.assertEqual(hashlib.sha256(source).hexdigest(),
                             tile["rgba_sha256"])
            self.assertEqual(hashlib.sha256(pngs[tile["file"]]).hexdigest(),
                             tile["file_sha256"])

    def test_identical_invocations_are_byte_for_byte_deterministic(self):
        self.assertEqual(build_theme_kit("Garage_Legends", 32),
                         build_theme_kit("Garage_Legends", 32))

    def test_different_profiles_produce_distinct_color_bytes(self):
        _, coral = build_theme_kit("Coral_Rescue", 32)
        _, garage = build_theme_kit("Garage_Legends", 32)
        self.assertNotEqual(coral["tile_star.png"], garage["tile_star.png"])

    def test_source_style_bible_pinned_in_manifest(self):
        from factory.visual_director.silhouette_kit import STYLE_BIBLE
        manifest, pngs = build_theme_kit("Wonder_Pop", 32)
        self.assertEqual(manifest["style_source_sha256"],
                         hashlib.sha256(STYLE_BIBLE.read_bytes()).hexdigest())
        self.assertEqual(manifest["atlas_sha256"],
                         hashlib.sha256(pngs["tile_atlas.png"]).hexdigest())

    def test_reject_invalid_size_profile_boolean(self):
        for kwargs in ({"side": 0}, {"side": 129}, {"side": True},
                       {"side": 24.0}):
            with self.subTest(kwargs=kwargs), self.assertRaises(PrototypeError):
                build_theme_kit("Coral_Rescue", **kwargs)
        with self.assertRaises(PrototypeError):
            build_theme_kit("Unknown_Game")

    def test_no_save_is_default_on_cli(self):
        out = StringIO()
        with redirect_stdout(out):
            self.assertEqual(main(["--profile", "Coral_Rescue", "--side", "24"]), 0)
        receipt = json.loads(out.getvalue())
        self.assertFalse(receipt["output_saved"])
        self.assertFalse(list(self.directory.iterdir()))

    def test_write_once_and_preserve_previous_bytes(self):
        manifest, pngs = build_theme_kit("Wonder_Pop", 24)
        path = self.directory / "prototype"
        write_once(path, manifest, pngs)
        first = (path / "tile_atlas.png").read_bytes()
        self.assertEqual(first, pngs["tile_atlas.png"])
        self.assertEqual(json.loads((path / "tile_manifest.json").read_text()),
                         manifest)
        with self.assertRaises(PrototypeError):
            write_once(path, manifest, pngs)
        self.assertEqual(first, (path / "tile_atlas.png").read_bytes())

    def test_git_checkout_output_is_forbidden(self):
        from factory.visual_director.silhouette_kit import ROOT
        data, pngs = build_theme_kit("The_Fractured_Realms", 24)
        with self.assertRaises(PrototypeError):
            write_once(ROOT / "do-not-create", data, pngs)


if __name__ == "__main__":
    unittest.main()
