"""VF-04 deterministic atlas regression and adversarial controls."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from factory.image_processor.png_pipeline import decode_png, encode_png, ImageError
from factory.image_processor.atlas_pipeline import create_atlas_candidate


class AtlasTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.red = self.root / "source_red.png"
        self.blue = self.root / "source_blue.png"
        self.red_rgba = bytes((224, 16, 40, 255)) * 4
        self.blue_rgba = bytes((12, 180, 210, 96)) * 6
        self.red.write_bytes(encode_png(2, 2, self.red_rgba))
        self.blue.write_bytes(encode_png(3, 2, self.blue_rgba))

    @staticmethod
    def subrect(w, rgba, x, y, sub_w, sub_h):
        result = bytearray()
        for row in range(y, y + sub_h):
            first = (row * w + x) * 4
            result.extend(rgba[first:first + sub_w * 4])
        return bytes(result)

    def test_exact_source_pixels_in_atlas_and_uv(self):
        manifest = create_atlas_candidate(
            {"tile.red": self.red, "tile.blue": self.blue},
            self.root / "candidate", padding=2, extrude=1)
        width, height, pixels = decode_png((self.root / "candidate/atlas.png").read_bytes())
        self.assertEqual((manifest["width"], manifest["height"]), (width, height))
        self.assertEqual(width, 13)
        self.assertEqual(height, 6)
        self.assertEqual(manifest["stage"], "CANDIDATE_NOT_APPROVED")
        lookup = {entry["asset_id"]: entry for entry in manifest["sprites"]}
        for name, source, rgba in (
            ("tile.red", self.red, self.red_rgba),
            ("tile.blue", self.blue, self.blue_rgba),
        ):
            entry = lookup[name]
            x, y, w, h = entry["pixel_rect_top_left"]
            self.assertEqual(self.subrect(width, pixels, x, y, w, h), rgba)
            self.assertEqual(entry["original_sha256"],
                             hashlib.sha256(source.read_bytes()).hexdigest())
            u, v, uw, vh = entry["uv_rect_bottom_left"]
            self.assertEqual([u * width, v * height, uw * width, vh * height],
                             [x, height - y - h, w, h])

    def test_strict_stability_independent_input_order(self):
        left = create_atlas_candidate(
            {"tile.red": self.red, "tile.blue": self.blue},
            self.root / "first")
        right = create_atlas_candidate(
            {"tile.blue": self.blue, "tile.red": self.red},
            self.root / "second")
        self.assertEqual(left, right)
        self.assertEqual((self.root / "first/atlas.png").read_bytes(),
                         (self.root / "second/atlas.png").read_bytes())

    def test_bleed_duplicates_edge_rgba_including_alpha(self):
        manifest = create_atlas_candidate(
            {"tile.blue": self.blue}, self.root / "bleed",
            padding=2, extrude=1)
        width, _, px = decode_png((self.root / "bleed/atlas.png").read_bytes())
        entry = manifest["sprites"][0]
        x, y, _, _ = entry["pixel_rect_top_left"]
        offset = ((y - 1) * width + x - 1) * 4
        self.assertEqual(px[offset:offset + 4], self.blue_rgba[:4])
        outside = ((y - 2) * width + x - 2) * 4
        self.assertEqual(px[outside:outside + 4], b"\x00\x00\x00\x00")

    def test_different_shelves_when_width_exceeded(self):
        result = create_atlas_candidate(
            {"tile.red": self.red, "tile.blue": self.blue},
            self.root / "shelves", max_width=7, max_height=12,
            padding=2, extrude=1)
        self.assertEqual((result["width"], result["height"]), (7, 12))
        self.assertEqual(len(result["sprites"]), 2)

    def test_overflow_is_closed_and_writes_nothing(self):
        dest = self.root / "overflow"
        with self.assertRaises(ImageError):
            create_atlas_candidate(
                {"tile.red": self.red, "tile.blue": self.blue},
                dest, max_width=7, max_height=6)
        self.assertFalse(dest.exists())

    def test_approved_candidate_is_not_overwritten(self):
        destination = self.root / "output"
        original = create_atlas_candidate({"tile.red": self.red}, destination)
        original_png = (destination / "atlas.png").read_bytes()
        with self.assertRaises(ImageError):
            create_atlas_candidate({"tile.blue": self.blue}, destination)
        self.assertEqual((destination / "atlas.png").read_bytes(), original_png)
        self.assertEqual(json.loads((destination / "atlas_manifest.json").read_text()),
                         original)

    def test_multiple_external_originals_with_same_pixel_hash_are_legal(self):
        twin = self.root / "another.png"
        twin.write_bytes(self.red.read_bytes())
        result = create_atlas_candidate(
            {"tile.red": self.red, "tile.red_alt": twin}, self.root / "twins")
        self.assertEqual(len(result["sprites"]), 2)

    def test_bad_key_and_bad_inputs_rejected(self):
        for label in ("INVALID", "../bad", "space key", "", "tile/red"):
            with self.subTest(label=label), self.assertRaises(ImageError):
                create_atlas_candidate({label: self.red},
                                       self.root / ("bad_" + str(len(label))))
        with self.assertRaises(ImageError):
            create_atlas_candidate({}, self.root / "empty")
        with self.assertRaises(ImageError):
            create_atlas_candidate({"tile": self.root / "absent.png"},
                                   self.root / "missing")

    def test_unbounded_specs_rejected(self):
        for data in (
            {"padding": 17}, {"padding": -1},
            {"padding": 1, "extrude": 2},
            {"max_width": 0}, {"max_height": 5000},
            {"max_width": 4096, "max_height": 4097}
        ):
            with self.subTest(data=data), self.assertRaises(ImageError):
                create_atlas_candidate({"tile.red": self.red},
                                       self.root / "invalid", **data)

    def test_input_and_output_symlinks_are_rejected(self):
        input_link = self.root / "linked.png"
        output_link = self.root / "linked_folder"
        real_dir = self.root / "real"
        real_dir.mkdir()
        try:
            input_link.symlink_to(self.red)
            output_link.symlink_to(real_dir, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks not permitted")
        with self.assertRaises(ImageError):
            create_atlas_candidate({"tile.red": input_link}, self.root / "candidate")
        with self.assertRaises(ImageError):
            create_atlas_candidate({"tile.red": self.red}, output_link)

    def test_source_parent_and_repository_output_rejected(self):
        with self.assertRaises(ImageError):
            create_atlas_candidate({"tile.red": self.red}, self.root)
        with self.assertRaises(ImageError):
            create_atlas_candidate({"tile.red": self.red}, ROOT / "auto_asset_output")

    def test_bad_png_checksum_blocks_atlas(self):
        corrupted = bytearray(self.red.read_bytes())
        corrupted[23] ^= 1
        self.red.write_bytes(corrupted)
        with self.assertRaises(ImageError):
            create_atlas_candidate({"tile.red": self.red}, self.root / "badpng")


if __name__ == "__main__":
    unittest.main()
