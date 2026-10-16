"""R31 deterministic RGB bleed without changing alpha or owner originals."""
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from contextlib import redirect_stdout
from io import StringIO

from factory.image_processor.png_pipeline import decode_png, encode_png
from factory.image_processor.transparent_rgb_extrusion import (
    FringeError, extrude_rgb, process_png, save_candidate, main
)


class TransparentRgbExtrusionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        self.source = self.work / "alpha.png"
        # One solid red pixel surrounded by five transparent black pixels.
        self.buffer = (b"\0\0\0\0" * 2 +
                       b"\xfa\x10\x08\xff" +
                       b"\0\0\0\0" * 3)
        self.source.write_bytes(encode_png(6, 1, self.buffer))

    def test_transparency_and_nontransparent_pixels_never_change(self):
        output, altered = extrude_rgb(6, 1, self.buffer, 2)
        self.assertEqual(altered, 4)
        self.assertEqual(output[3::4], self.buffer[3::4])
        self.assertEqual(output[8:12], self.buffer[8:12])
        self.assertEqual(output[0:3], b"\xfa\x10\x08")

    def test_radius_one_does_not_bleed_two_pixels(self):
        output, affected = extrude_rgb(6, 1, self.buffer, 1)
        self.assertEqual(affected, 2)
        self.assertEqual(output[0:4], b"\0\0\0\0")

    def test_fully_transparent_image_cannot_gain_alpha_or_color(self):
        image = bytes(7 * 5 * 4)
        out, changed = extrude_rgb(7, 5, image, 4)
        self.assertEqual(out, image)
        self.assertEqual(changed, 0)

    def test_fully_opaque_image_is_unchanged(self):
        image = bytes((40, 50, 60, 255)) * 24
        out, changed = extrude_rgb(6, 4, image, 8)
        self.assertEqual(out, image)
        self.assertEqual(changed, 0)

    def test_partial_alpha_pixel_preserves_all_channels(self):
        src = (b"\x00\x00\x00\x00" +
               b"\x99\x88\x77\x01" +
               b"\x00\x00\x00\x00")
        result, count = extrude_rgb(3, 1, src, 1)
        self.assertEqual(result[4:8], src[4:8])
        self.assertEqual(result[0:3], src[4:7])
        self.assertEqual(result[8:11], src[4:7])
        self.assertEqual(count, 2)

    def test_deterministic_output_and_stable_hashes(self):
        self.assertEqual(process_png(self.source, 4),
                         process_png(self.source, 4))

    def test_processed_candidate_is_valid_rgba_png(self):
        before = self.source.read_bytes()
        manifest, png = process_png(self.source, 3)
        w, h, pixels = decode_png(png)
        self.assertEqual((w, h), (6, 1))
        self.assertEqual(pixels[3::4], self.buffer[3::4])
        self.assertEqual(manifest["source_png_sha256"],
                         hashlib.sha256(before).hexdigest())
        self.assertEqual(manifest["candidate_png_sha256"],
                         hashlib.sha256(png).hexdigest())
        self.assertEqual(before, self.source.read_bytes())
        self.assertFalse(manifest["asset_rights_verified"])

    def test_source_and_output_must_not_be_overwritten(self):
        manifest, png = process_png(self.source, 2)
        out = self.work / "new_candidate.png"
        save_candidate(out, manifest, png)
        expected = out.read_bytes()
        with self.assertRaises(FringeError):
            save_candidate(out, manifest, b"garbage")
        self.assertEqual(out.read_bytes(), expected)
        self.assertEqual(self.source.read_bytes(),
                         encode_png(6, 1, self.buffer))

    def test_reject_invalid_radius_and_dimensions(self):
        for radius in (0, 9, True, 1.0, -1):
            with self.subTest(radius=radius), self.assertRaises(FringeError):
                extrude_rgb(6, 1, self.buffer, radius)
        with self.assertRaises(FringeError):
            extrude_rgb(6, 1, b"wrong", 2)
        with self.assertRaises(FringeError):
            extrude_rgb(0, 1, self.buffer, 2)

    def test_non_png_source_refused(self):
        wrong = self.work / "source.jpg"
        wrong.write_bytes(self.source.read_bytes())
        with self.assertRaises(FringeError):
            process_png(wrong)

    def test_no_output_by_default(self):
        stdout = StringIO()
        with redirect_stdout(stdout):
            self.assertEqual(main(["--source", str(self.source)]), 0)
        result = json.loads(stdout.getvalue())
        self.assertFalse(result["output_saved"])
        self.assertEqual(list(self.work.glob("*")), [self.source])


if __name__ == "__main__":
    unittest.main()
