"""Strict source alpha/trim/pivot 1x/2x/3x receipts, not Unity execution."""
from __future__ import annotations

import hashlib
import unittest

from factory.image_processor.png_pipeline import (
    encode_png, trim_rgba, scale_nearest,
)
from factory.visual_director.m05_sprite_scale_receipt import (
    SpriteScaleError, audit_pinned_scale_set,
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sample(alpha: bool = True) -> tuple[bytes, dict[int, bytes]]:
    w, h = 12, 10
    rgba = bytearray(w * h * 4)
    for y in range(2, 8):
        for x in range(3, 9):
            i = (y * w + x) * 4
            rgba[i:i+4] = bytes((40 + x, 100 + y, 240, 255 if alpha else 0))
    original = encode_png(w, h, bytes(rgba))
    if not alpha:
        return original, {}
    tw, th, trimmed, _ = trim_rgba(w, h, bytes(rgba), padding=1)
    exports = {}
    for k in (1, 2, 3):
        ew, eh, values = scale_nearest(tw, th, trimmed, k)
        exports[k] = encode_png(ew, eh, values)
    return original, exports


class M05SpriteScaleReceiptTests(unittest.TestCase):
    def setUp(self):
        self.source, self.exports = sample()
        self.receipts = {k: sha(png) for k, png in self.exports.items()}

    def audit(self, **params):
        return audit_pinned_scale_set(
            self.source, sha(self.source),
            self.exports, self.receipts, (6, 5),
            padding=1, **params,
        )

    def test_whole_rgba_pixels_and_pivots_verified_in_three_export_sizes(self):
        result = self.audit()
        self.assertEqual(result["trim_source_rect_top_left"], [3, 2, 6, 6])
        self.assertEqual([r["dimensions"] for r in result["exports"]],
                         [[8, 8], [16, 16], [24, 24]])
        self.assertEqual([r["sprite_pivot_pixels_bottom_left"]
                          for r in result["exports"]],
                         [[4.0, 4.0], [8.0, 8.0], [12.0, 12.0]])
        self.assertTrue(all(r["whole_rgba_nearest_verified"]
                            for r in result["exports"]))
        for key in ("original_creator_rights_verified",
                    "unity_sprite_importer_verified",
                    "real_atlas_gpu_bleeding_verified",
                    "engine_final_asset_id_verified", "release_allowed"):
            self.assertFalse(result[key])

    def test_nearest_center_only_sample_cannot_hide_wrong_edge_subpixels(self):
        corrupted = dict(self.exports)
        w, h = 16, 16
        _, _, expected = scale_nearest(8, 8, bytes([0, 0, 0, 0] * 64), 2)
        # Corrupt the first pixel only; center-of-cell downsample could miss it.
        from factory.image_processor.png_pipeline import decode_png
        x, y, pixels = decode_png(corrupted[2])
        changed = bytearray(pixels)
        changed[0:4] = b"\xff\x00\x00\xff"
        corrupted[2] = encode_png(x, y, bytes(changed))
        with self.assertRaises(SpriteScaleError):
            audit_pinned_scale_set(
                self.source, sha(self.source), corrupted,
                {k: sha(v) for k, v in corrupted.items()}, (6, 5),
                padding=1)

    def test_broken_sha_and_missing_scale_are_rejected(self):
        with self.assertRaises(SpriteScaleError):
            audit_pinned_scale_set(self.source, "0" * 64,
                                   self.exports, self.receipts, (6, 5), padding=1)
        with self.assertRaises(SpriteScaleError):
            audit_pinned_scale_set(self.source, sha(self.source),
                                   {1: self.exports[1], 2: self.exports[2]},
                                   self.receipts, (6, 5), padding=1)
        bad = dict(self.receipts)
        bad[3] = "a" * 64
        with self.assertRaises(SpriteScaleError):
            audit_pinned_scale_set(self.source, sha(self.source),
                                   self.exports, bad, (6, 5), padding=1)

    def test_pivot_outside_trim_and_source_canvas_is_rejected(self):
        for pivot in ((1, 5), (6, 9), (-1, 4), (13, 2),
                      (float("nan"), 5), (float("inf"), 5)):
            with self.subTest(pivot=pivot), self.assertRaises(SpriteScaleError):
                audit_pinned_scale_set(
                    self.source, sha(self.source),
                    self.exports, self.receipts, pivot, padding=1)

    def test_all_transparent_and_unsafe_inputs_fail_closed(self):
        transparent, _ = sample(alpha=False)
        with self.assertRaises(SpriteScaleError):
            audit_pinned_scale_set(
                transparent, sha(transparent),
                self.exports, self.receipts, (6, 5), padding=1)
        for invalid in (True, 1.5, -1, 90):
            with self.subTest(padding=invalid), self.assertRaises(SpriteScaleError):
                audit_pinned_scale_set(
                    self.source, sha(self.source),
                    self.exports, self.receipts, (6, 5),
                    padding=invalid)

    def test_dimensions_alpha_cutoff_or_wrong_nearest_raster_rejected(self):
        altered = dict(self.exports)
        altered[3] = self.exports[2]
        with self.assertRaises(SpriteScaleError):
            audit_pinned_scale_set(
                self.source, sha(self.source), altered,
                {k: sha(v) for k, v in altered.items()}, (6, 5),
                padding=1)
        with self.assertRaises(SpriteScaleError):
            audit_pinned_scale_set(
                self.source, sha(self.source),
                self.exports, self.receipts, (6, 5), padding=1,
                alpha_cutoff=254)


if __name__ == "__main__":
    unittest.main()
