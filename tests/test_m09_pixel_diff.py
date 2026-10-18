"""M09 PNG regression and art provenance source tests; no human/device PASS."""
from __future__ import annotations

import hashlib
import unittest

from factory.image_processor.png_pipeline import encode_png, decode_png
from factory.qa.m09_pixel_diff import (
    compare, compare_scaled_candidate, compare_frame_sequence,
    verify_receipt_source, PixelReviewError,
)


def png(w=8, h=8, rgba=(255, 80, 70, 255)):
    return encode_png(w, h, bytes(rgba) * (w * h))


class M09PixelDiffTests(unittest.TestCase):
    def test_same_image_has_zero_changed_pixels_and_no_unneeded_diff_artifact(self):
        source = png()
        result, diff = compare(source, source)
        self.assertIsNone(diff)
        self.assertEqual(result["mismatched_pixels"], 0)
        self.assertEqual(result["dimensions"], [8, 8])
        self.assertFalse(result["owner_aesthetic_approved"])
        self.assertFalse(result["release_allowed"])

    def test_rgba_alpha_change_is_detected_as_distinct_from_rgb_change(self):
        source = png()
        changed = bytearray(bytes((255, 80, 70, 255)) * 64)
        changed[3] = 80
        b = encode_png(8, 8, bytes(changed))
        result, diff = compare(source, b)
        self.assertEqual(result["mismatched_pixels"], 1)
        self.assertEqual(result["alpha_changed_pixels"], 1)
        self.assertEqual(result["semialpha_edge_candidates"], 1)
        self.assertEqual(decode_png(diff)[:2], (8, 8))
        self.assertEqual(result["mismatch_ratio_milli"], 15)

    def test_rgba_color_change_without_alpha_does_not_fake_transparency_bug(self):
        a = png()
        b = png(rgba=(50, 80, 70, 255))
        result, _ = compare(a, b, tolerance=0)
        self.assertEqual(result["mismatched_pixels"], 64)
        self.assertEqual(result["alpha_changed_pixels"], 0)

    def test_tolerance_never_grants_aesthetic_acceptance(self):
        a = png()
        b = png(rgba=(254, 80, 70, 255))
        result, diff = compare(a, b, tolerance=1)
        self.assertEqual(result["mismatched_pixels"], 0)
        self.assertIsNone(diff)
        self.assertNotEqual(result["before_sha256"], result["after_sha256"])
        self.assertFalse(result["owner_aesthetic_approved"])

    def test_resize_and_corrupt_png_are_rejected_not_silently_stretched(self):
        with self.assertRaises(PixelReviewError):
            compare(png(), png(9, 8))
        with self.assertRaises(PixelReviewError):
            compare(png(), b"not a PNG")
        with self.assertRaises(PixelReviewError):
            compare(png(), png(), tolerance=30)

    def test_original_hash_pin_prevents_comparing_changed_source_as_original(self):
        a, b = png(), png(rgba=(0, 0, 0, 255))
        with self.assertRaises(PixelReviewError):
            compare(b, b, expected_sha=hashlib.sha256(a).hexdigest())
        result, _ = compare(a, b, expected_sha=hashlib.sha256(a).hexdigest())
        self.assertEqual(result["before_sha256"], hashlib.sha256(a).hexdigest())

    def test_2x_3x_source_review_uses_explicit_resolution_not_false_device_pass(self):
        a = png(8, 8, rgba=(255, 80, 70, 255))
        for factor in (2, 3):
            with self.subTest(factor=factor):
                b = png(8 * factor, 8 * factor,
                        rgba=(255, 80, 70, 255))
                result = compare_scaled_candidate(a, b, factor)
                self.assertEqual(result["mismatched_pixels_after_nearest"], 0)
                self.assertFalse(result["real_device_resolution_sharpness_verified"])
        with self.assertRaises(PixelReviewError):
            compare_scaled_candidate(a, png(8, 8), 3)

    def test_source_frame_sequence_reports_missing_or_changed_frames_without_replay_pass(self):
        a = png(8, 8)
        b = png(8, 8, rgba=(0, 0, 0, 255))
        result = compare_frame_sequence([a, a, a], [a, b, a])
        self.assertEqual(result["changed_frames"], 1)
        self.assertEqual(result["frame_count"], 3)
        self.assertFalse(result["real_unity_playback_proven"])
        self.assertFalse(result["release_allowed"])
        with self.assertRaises(PixelReviewError):
            compare_frame_sequence([a, a], [a])

    def test_art_creator_fields_only_check_presence_not_actual_legal_approval(self):
        source = png()
        digest = hashlib.sha256(source).hexdigest()
        fields = {
            "profile_id": "Coral_Rescue",
            "asset_id": "Coral_Rescue.sample.circle",
            "source_filename": "original_candidate.png",
            "creator": "EXAMPLE_NOT_VERIFIED",
            "licence_text_location": "OWNER_REVIEW_PENDING",
            "consent_reference": None,
            "usage_scope": "candidate review only",
            "source_sha256": digest,
            "stage": "OWNER_ART_SOURCE_REVIEW_PENDING",
        }
        evidence = verify_receipt_source(source,
            declared_sha=digest, provenance=fields)
        self.assertTrue(evidence["source_bytes_sha256_verified"])
        self.assertFalse(evidence["image_use_authorized_for_release"])
        bad = dict(fields, stage="OWNER_APPROVED")
        with self.assertRaises(PixelReviewError):
            verify_receipt_source(source, declared_sha=digest, provenance=bad)
        bad = dict(fields, source_sha256="a" * 64)
        with self.assertRaises(PixelReviewError):
            verify_receipt_source(source, declared_sha=digest, provenance=bad)


if __name__ == "__main__":
    unittest.main()
