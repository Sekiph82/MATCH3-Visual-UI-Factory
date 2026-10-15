"""VUF VF-04 actual pixel, PNG corruption and candidate-output tests."""
import hashlib
import json
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from factory.image_processor.png_pipeline import (
    ImageError, PNG_SIGNATURE, _chunk, _paeth, decode_png, encode_png,
    trim_rgba, scale_nearest, create_candidate_exports,
)


def synthetic(width, height, pixels, filter_number=0, kind=6):
    bpp = 4 if kind == 6 else 3
    stride = width * bpp
    previous = b"\0" * stride
    scans = []
    for y in range(height):
        row = bytes(pixels[y * stride:(y + 1) * stride])
        filtered = bytearray(row)
        if filter_number:
            for i, value in enumerate(row):
                left = row[i - bpp] if i >= bpp else 0
                above = previous[i]
                upper_left = previous[i - bpp] if i >= bpp else 0
                predict = {
                    1: left,
                    2: above,
                    3: (left + above) // 2,
                    4: _paeth(left, above, upper_left),
                }[filter_number]
                filtered[i] = (value - predict) & 255
        scans.append(bytes([filter_number]) + bytes(filtered))
        previous = row
    ihdr = struct.pack(">IIBBBBB", width, height, 8, kind, 0, 0, 0)
    return PNG_SIGNATURE + _chunk(b"IHDR", ihdr) + _chunk(
        b"IDAT", zlib.compress(b"".join(scans))
    ) + _chunk(b"IEND", b"")


class PngPipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.original = self.root / "original.png"
        transparent = bytes((0, 0, 0, 0))
        colored = bytes((45, 165, 212, 200))
        pixels = transparent * 9
        pixels = pixels[:4 * 4] + colored + pixels[4 * 5:]
        self.rgba = pixels
        self.original.write_bytes(encode_png(3, 3, pixels))

    def test_roundtrip_real_alpha_pixels(self):
        width, height, data = decode_png(self.original.read_bytes())
        self.assertEqual((width, height, data), (3, 3, self.rgba))

    def test_all_png_filter_modes_decode_to_same_pixels(self):
        pixels = bytes([20, 33, 41, 255, 80, 100, 120, 0] * 3)
        for mode in range(5):
            with self.subTest(filter=mode):
                data = synthetic(2, 3, pixels, mode)
                self.assertEqual(decode_png(data), (2, 3, pixels))

    def test_rgb_import_becomes_opaque_rgba(self):
        imported = synthetic(1, 1, bytes([12, 56, 78]), kind=2)
        self.assertEqual(decode_png(imported), (1, 1, bytes([12, 56, 78, 255])))

    def test_trim_and_padding_keep_original_alpha(self):
        width, height, data, bounds = trim_rgba(3, 3, self.rgba, padding=1)
        self.assertEqual((width, height), (3, 3))
        self.assertEqual(bounds["x"], 1)
        self.assertEqual(bounds["y"], 1)
        self.assertEqual(data[4 * 4:4 * 5], bytes((45, 165, 212, 200)))
        self.assertEqual(data[0:4], b"\0\0\0\0")

    def test_nearest_2x_and_3x_pixel_fidelity(self):
        one_pixel = bytes((10, 20, 30, 200))
        for scale in (2, 3):
            w, h, out = scale_nearest(1, 1, one_pixel, scale)
            self.assertEqual((w, h), (scale, scale))
            self.assertEqual(out, one_pixel * (scale * scale))

    def test_candidate_outputs_and_receipt_immutable(self):
        before = self.original.read_bytes()
        directory = self.root / "candidate"
        result = create_candidate_exports(self.original, directory, multipliers=(1, 2, 3))
        self.assertEqual(result["stage"], "CANDIDATE_NOT_APPROVED")
        self.assertEqual(result["source_sha256"], hashlib.sha256(before).hexdigest())
        self.assertEqual(self.original.read_bytes(), before)
        self.assertEqual([(e["width"], e["height"]) for e in result["outputs"]],
                         [(1, 1), (2, 2), (3, 3)])
        self.assertEqual(json.loads((directory / "candidate_manifest.json").read_text()), result)
        for entry in result["outputs"]:
            self.assertEqual(hashlib.sha256((directory / entry["path"]).read_bytes()).hexdigest(),
                             entry["sha256"])
        with self.assertRaises(ImageError):
            create_candidate_exports(self.original, directory)
        self.assertEqual((directory / "sprite_1x.png").read_bytes(),
                         encode_png(1, 1, bytes((45, 165, 212, 200))))

    def test_transparent_and_cutoff_images_fail(self):
        with self.assertRaises(ImageError):
            trim_rgba(1, 1, bytes((1, 2, 3, 0)))
        with self.assertRaises(ImageError):
            trim_rgba(1, 1, bytes((1, 2, 3, 5)), alpha_cutoff=5)

    def test_reject_invalid_scales_and_padding(self):
        with self.assertRaises(ImageError):
            scale_nearest(1, 1, self.rgba[:4], 4)
        with self.assertRaises(ImageError):
            trim_rgba(3, 3, self.rgba, padding=65)
        with self.assertRaises(ImageError):
            create_candidate_exports(self.original, self.root / "bad", multipliers=(1, 1))

    def test_bad_crc_and_unknown_critical_chunk(self):
        corrupted = bytearray(self.original.read_bytes())
        corrupted[21] ^= 1
        with self.assertRaises(ImageError):
            decode_png(bytes(corrupted))
        data = self.original.read_bytes()
        pos = len(PNG_SIGNATURE) + 25
        self.assertTrue(pos < len(data))
        extra = _chunk(b"ABCD", b"x")
        with self.assertRaises(ImageError):
            decode_png(data[:33] + extra + data[33:])

    def test_disallow_trailing_garbage(self):
        with self.assertRaises(ImageError):
            decode_png(self.original.read_bytes() + b"trailing")

    def test_disallow_interlaced_png_and_huge_dimensions(self):
        header = struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 1)
        blob = PNG_SIGNATURE + _chunk(b"IHDR", header) + _chunk(
            b"IDAT", zlib.compress(b"\x00\x00\x00\x00\x00")
        ) + _chunk(b"IEND", b"")
        with self.assertRaises(ImageError):
            decode_png(blob)
        with self.assertRaises(ImageError):
            encode_png(9999, 1, b"\0" * 39996)

    def test_reject_export_into_original_source_parent(self):
        with self.assertRaises(ImageError):
            create_candidate_exports(self.original, self.root)

    def test_reject_export_inside_git_checkout(self):
        with self.assertRaises(ImageError):
            create_candidate_exports(self.original, ROOT / "generated")

    def test_output_symlink_is_rejected(self):
        outside = self.root / "outside"
        outside.mkdir()
        link = self.root / "link"
        try:
            link.symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        with self.assertRaises(ImageError):
            create_candidate_exports(self.original, link)

    def test_input_symlink_is_rejected(self):
        linked = self.root / "linked.png"
        try:
            linked.symlink_to(self.original)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        with self.assertRaises(ImageError):
            create_candidate_exports(linked, self.root / "candidate")


if __name__ == "__main__":
    unittest.main()
