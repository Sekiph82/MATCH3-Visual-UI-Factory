"""M04 offline human-unapproved source comparison regression cases."""
from __future__ import annotations

import copy
import hashlib
import json
import unittest

from factory.image_processor.png_pipeline import encode_png
from factory.visual_director.m04_original_comparison import (
    OriginalReviewError, inspect_original_candidate, parse_review_contract,
)


def sample_png(change: bool = False) -> bytes:
    pixels = bytearray()
    for y in range(8):
        for x in range(8):
            pixels.extend((30 + (40 if change and x == 3 and y == 4 else 0),
                           130, 170, 255 if x > 0 else 0))
    return encode_png(8, 8, bytes(pixels))


def contract(reference: bytes, candidate: bytes) -> dict:
    profile = "Coral_Rescue"
    key = "Coral_Rescue.mascot.pose_idle"
    original_sha = hashlib.sha256(reference).hexdigest()
    return {
        "schema_version": 1,
        "stage": "M04_SOURCE_REVIEW_UNAPPROVED",
        "profile_id": profile,
        "asset_id": key,
        "reference_sha256": original_sha,
        "candidate_sha256": hashlib.sha256(candidate).hexdigest(),
        "provenance": {
            "profile_id": profile, "asset_id": key,
            "source_filename": "creator_original.png",
            "creator": "OWNER_DEFINED_ARTIST_UNVERIFIED",
            "licence_text_location": "OWNER_MUST_SUPPLY_ACTUAL_CONTRACT",
            "consent_reference": None,
            "usage_scope": "PENDING_OWNER_RIGHTS_REVIEW",
            "source_sha256": original_sha,
            "stage": "OWNER_ART_SOURCE_REVIEW_PENDING",
        },
        "owner_originality_approved": False,
        "owner_legal_rights_approved": False,
        "creator_verified": False,
        "source_release_allowed": False,
    }


def encoded(data: dict) -> bytes:
    return json.dumps(data, sort_keys=True).encode("utf-8")


class M04OriginalSourceReviewTests(unittest.TestCase):
    def setUp(self):
        self.a = sample_png()
        self.b = sample_png(True)
        self.m = contract(self.a, self.b)

    def test_m02_five_game_id_and_source_lineage_are_mechanical_not_approval(self):
        r = inspect_original_candidate(self.a, self.b, encoded(self.m))
        self.assertEqual(r["profile_id"], "Coral_Rescue")
        self.assertEqual(r["changed_pixels"], 1)
        self.assertFalse(r["pixel_identical_to_reference"])
        self.assertEqual(len(r["source_lineage_sha256"]), 64)
        self.assertTrue(r["source_shape_provenance_present"])
        for flag in ("original_artist_identity_verified",
                     "human_originality_approved", "legal_licence_reviewed",
                     "owner_visual_review_performed", "physical_device_qa_passed",
                     "release_allowed"):
            self.assertIs(r[flag], False)

    def test_even_identical_reference_and_candidate_are_not_license_approval(self):
        data = contract(self.a, self.a)
        result = inspect_original_candidate(self.a, self.a, encoded(data))
        self.assertTrue(result["pixel_identical_to_reference"])
        self.assertEqual(result["changed_pixels"], 0)
        self.assertFalse(result["release_allowed"])
        self.assertFalse(result["human_originality_approved"])

    def test_mismatched_source_or_candidate_sha_fails_before_pixel_diff(self):
        for kind in ("reference_sha256", "candidate_sha256"):
            data = copy.deepcopy(self.m)
            data[kind] = "0" * 64
            with self.subTest(kind=kind), self.assertRaises(OriginalReviewError):
                inspect_original_candidate(self.a, self.b, encoded(data))
        with self.assertRaises(OriginalReviewError):
            inspect_original_candidate(self.a, self.a, encoded(self.m))

    def test_all_forged_owner_creator_release_flags_rejected(self):
        for name in ("owner_originality_approved", "owner_legal_rights_approved",
                     "creator_verified", "source_release_allowed"):
            m = copy.deepcopy(self.m)
            m[name] = True
            with self.subTest(name=name), self.assertRaises(OriginalReviewError):
                parse_review_contract(encoded(m))
        m = copy.deepcopy(self.m)
        m["provenance"]["stage"] = "OWNER_ART_APPROVED"
        with self.assertRaises(OriginalReviewError):
            inspect_original_candidate(self.a, self.b, encoded(m))

    def test_cross_title_and_extra_duplicate_fields_rejected(self):
        for corrupt in (
            lambda d: d.__setitem__("profile_id", "Wonder_Pop"),
            lambda d: d.__setitem__("asset_id", "Wonder_Pop.tile.star"),
            lambda d: d.__setitem__("ignored_approval", True),
            lambda d: d.pop("provenance"),
        ):
            m = copy.deepcopy(self.m)
            corrupt(m)
            with self.assertRaises(OriginalReviewError):
                parse_review_contract(encoded(m))
        duplicate = encoded(self.m).replace(
            b'"creator_verified": false',
            b'"creator_verified": false, "creator_verified": true'
        )
        with self.assertRaises(OriginalReviewError):
            parse_review_contract(duplicate)

    def test_creator_receipt_must_match_image_and_candidate_dimensions(self):
        m = copy.deepcopy(self.m)
        m["provenance"]["source_sha256"] = "0" * 64
        with self.assertRaises(OriginalReviewError):
            inspect_original_candidate(self.a, self.b, encoded(m))
        different = encode_png(7, 8, bytes((10, 30, 80, 255) * 56))
        mm = contract(self.a, different)
        with self.assertRaises(OriginalReviewError):
            inspect_original_candidate(self.a, different, encoded(mm))
        with self.assertRaises(OriginalReviewError):
            inspect_original_candidate(b"NOT PNG", self.b, encoded(self.m))


if __name__ == "__main__":
    unittest.main()
