"""VF-04 alpha-mask compositing pixel/integrity regression tests."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from factory.image_processor.alpha_mask import mask_rgba, create_mask_candidate
from factory.image_processor.png_pipeline import ImageError, decode_png, encode_png


class MaskTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / "source.png"
        self.mask = self.root / "mask.png"
        self.original_pixels = bytes([
            10, 20, 30, 255,
            40, 50, 60, 128,
            70, 80, 90, 90,
        ])
        self.mask_pixels = bytes([
            0, 0, 0, 255,
            0, 0, 0, 128,
            0, 0, 0, 0,
        ])
        self.source.write_bytes(encode_png(3, 1, self.original_pixels))
        self.mask.write_bytes(encode_png(3, 1, self.mask_pixels))

    def test_keep_multiplies_alpha_preserves_rgb(self):
        result = mask_rgba(3, 1, self.original_pixels, self.mask_pixels)
        self.assertEqual(result, bytes([
            10, 20, 30, 255,
            40, 50, 60, 64,
            70, 80, 90, 0,
        ]))

    def test_remove_complement_preserves_rgb(self):
        result = mask_rgba(3, 1, self.original_pixels, self.mask_pixels, "remove")
        self.assertEqual(result, bytes([
            10, 20, 30, 0,
            40, 50, 60, 64,
            70, 80, 90, 90,
        ]))

    def test_candidate_output_is_png_and_receipt_immutable(self):
        before = self.source.read_bytes()
        mask_before = self.mask.read_bytes()
        folder = self.root / "candidate"
        receipt = create_mask_candidate(self.source, self.mask, folder, "keep")
        self.assertEqual(receipt["stage"], "CANDIDATE_NOT_APPROVED")
        self.assertEqual(receipt["source_sha256"], hashlib.sha256(before).hexdigest())
        self.assertEqual(receipt["mask_sha256"], hashlib.sha256(mask_before).hexdigest())
        output = (folder / "masked_candidate.png").read_bytes()
        self.assertEqual(receipt["output_sha256"], hashlib.sha256(output).hexdigest())
        self.assertEqual(decode_png(output)[2],
                         mask_rgba(3, 1, self.original_pixels, self.mask_pixels))
        self.assertEqual(json.loads((folder / "mask_receipt.json").read_text()),
                         receipt)
        self.assertEqual(self.source.read_bytes(), before)
        self.assertEqual(self.mask.read_bytes(), mask_before)

    def test_existing_candidate_protected(self):
        dest = self.root / "candidate"
        create_mask_candidate(self.source, self.mask, dest)
        before = (dest / "masked_candidate.png").read_bytes()
        with self.assertRaises(ImageError):
            create_mask_candidate(self.source, self.mask, dest)
        self.assertEqual(before, (dest / "masked_candidate.png").read_bytes())

    def test_dimension_mismatch_rejected_without_output(self):
        self.mask.write_bytes(encode_png(2, 1, b"\x00\x00\x00\xff" * 2))
        dest = self.root / "mismatch"
        with self.assertRaises(ImageError):
            create_mask_candidate(self.source, self.mask, dest)
        self.assertFalse(dest.exists())

    def test_empty_and_incorrect_masks_fail_closed(self):
        for mode in ("unknown", "", None):
            with self.subTest(mode=mode), self.assertRaises(ImageError):
                mask_rgba(3, 1, self.original_pixels, self.mask_pixels, mode)
        with self.assertRaises(ImageError):
            mask_rgba(3, 1, self.original_pixels, b"")
        with self.assertRaises(ImageError):
            mask_rgba(0, 1, self.original_pixels, self.mask_pixels)

    def test_original_folder_and_repository_output_blocked(self):
        with self.assertRaises(ImageError):
            create_mask_candidate(self.source, self.mask, self.root)
        with self.assertRaises(ImageError):
            create_mask_candidate(self.source, self.mask, ROOT / "unapproved_art")

    def test_mask_and_original_symlink_rejected(self):
        linked = self.root / "linked.png"
        try:
            linked.symlink_to(self.source)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        with self.assertRaises(ImageError):
            create_mask_candidate(linked, self.mask, self.root / "linked_src_out")
        with self.assertRaises(ImageError):
            create_mask_candidate(self.source, linked, self.root / "linked_mask_out")

    def test_bad_png_mask_crc_rejected(self):
        data = bytearray(self.mask.read_bytes())
        data[29] ^= 1
        self.mask.write_bytes(data)
        with self.assertRaises(ImageError):
            create_mask_candidate(self.source, self.mask, self.root / "invalid_png")

    def test_round_half_up_alpha_is_repeatable(self):
        a = bytes((1, 2, 3, 255))
        m = bytes((4, 5, 6, 127))
        result = mask_rgba(1, 1, a, m)
        self.assertEqual(result[3], 127)
        self.assertEqual(mask_rgba(1, 1, a, m), result)


if __name__ == "__main__":
    unittest.main()
