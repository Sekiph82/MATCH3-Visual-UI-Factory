"""Independent source-to-output candidate checks, no authoring approval."""
import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from factory.image_processor.png_pipeline import encode_png, decode_png
from factory.image_processor.atlas_pipeline import create_atlas_candidate
from factory.image_processor.alpha_mask import create_mask_candidate
from factory.validators.verify_candidates import (
    CandidateVerificationError, verify_atlas_candidate, verify_mask_candidate
)


class CandidateVerificationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.first = self.root / "original_one.png"
        self.second = self.root / "original_two.png"
        self.mask = self.root / "alpha_mask.png"
        self.first.write_bytes(encode_png(2, 2, bytes((255, 64, 11, 200)) * 4))
        self.second.write_bytes(encode_png(1, 2, bytes((11, 99, 255, 255)) * 2))
        self.mask.write_bytes(encode_png(2, 2, bytes((0, 0, 0, 128)) * 4))
        self.origins = {"tile.one": self.first, "tile.two": self.second}

    def test_independent_atlas_pixel_verification(self):
        folder = self.root / "atlas"
        create_atlas_candidate(self.origins, folder)
        result = verify_atlas_candidate(folder, self.origins)
        self.assertEqual(result["stage"], "REVIEW_REQUIRED")
        self.assertEqual(result["sprites_verified"], 2)

    def test_independent_mask_pixel_verification(self):
        folder = self.root / "masked"
        create_mask_candidate(self.first, self.mask, folder)
        result = verify_mask_candidate(folder, self.first, self.mask)
        self.assertEqual(result["stage"], "REVIEW_REQUIRED")
        self.assertEqual(result["masked_pixels_verified"], 4)

    def test_tampered_original_rejected(self):
        folder = self.root / "atlas"
        create_atlas_candidate(self.origins, folder)
        self.first.write_bytes(encode_png(2, 2, bytes((255, 44, 44, 200)) * 4))
        with self.assertRaises(CandidateVerificationError):
            verify_atlas_candidate(folder, self.origins)

    def test_tampered_atlas_bytes_rejected(self):
        folder = self.root / "atlas"
        create_atlas_candidate(self.origins, folder)
        atlas = folder / "atlas.png"
        bytes_ = bytearray(atlas.read_bytes())
        bytes_[23] ^= 1
        atlas.write_bytes(bytes_)
        with self.assertRaises(CandidateVerificationError):
            verify_atlas_candidate(folder, self.origins)

    def test_forged_atlas_receipt_hash_rejected(self):
        folder = self.root / "atlas"
        create_atlas_candidate(self.origins, folder)
        receipt = folder / "atlas_manifest.json"
        payload = json.loads(receipt.read_text())
        payload["atlas_sha256"] = "0" * 64
        receipt.write_text(json.dumps(payload))
        with self.assertRaises(CandidateVerificationError):
            verify_atlas_candidate(folder, self.origins)

    def test_forged_uv_rejected(self):
        folder = self.root / "atlas"
        create_atlas_candidate(self.origins, folder)
        receipt = folder / "atlas_manifest.json"
        payload = json.loads(receipt.read_text())
        payload["sprites"][0]["uv_rect_bottom_left"][0] = 0.99
        receipt.write_text(json.dumps(payload))
        with self.assertRaises(CandidateVerificationError):
            verify_atlas_candidate(folder, self.origins)

    def test_missing_original_from_ledger_rejected(self):
        folder = self.root / "atlas"
        create_atlas_candidate(self.origins, folder)
        with self.assertRaises(CandidateVerificationError):
            verify_atlas_candidate(folder, {"tile.one": self.first})

    def test_self_approved_atlas_rejected(self):
        folder = self.root / "atlas"
        create_atlas_candidate(self.origins, folder)
        receipt = folder / "atlas_manifest.json"
        payload = json.loads(receipt.read_text())
        payload["stage"] = "APPROVED"
        receipt.write_text(json.dumps(payload))
        with self.assertRaises(CandidateVerificationError):
            verify_atlas_candidate(folder, self.origins)

    def test_mask_metadata_and_content_tamper_rejected(self):
        folder = self.root / "masked"
        create_mask_candidate(self.first, self.mask, folder)
        new_pixels = bytes((255, 0, 0, 255)) * 4
        changed = encode_png(2, 2, new_pixels)
        target = folder / "masked_candidate.png"
        target.write_bytes(changed)
        receipt = folder / "mask_receipt.json"
        payload = json.loads(receipt.read_text())
        payload["output_sha256"] = hashlib.sha256(changed).hexdigest()
        receipt.write_text(json.dumps(payload))
        with self.assertRaises(CandidateVerificationError):
            verify_mask_candidate(folder, self.first, self.mask)

    def test_symlinked_candidate_input_fails(self):
        folder = self.root / "atlas"
        create_atlas_candidate(self.origins, folder)
        link = self.root / "source_link.png"
        try:
            link.symlink_to(self.first)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        with self.assertRaises(CandidateVerificationError):
            verify_atlas_candidate(folder, {"tile.one": link, "tile.two": self.second})


if __name__ == "__main__":
    unittest.main()
