"""VUF-M06 original-source artist pose intake tests, never art-owner approval."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from factory.image_processor.png_pipeline import decode_png, encode_png
from factory.visual_director.character_pose_review import (
    POSES, STAGE, PoseReviewError, _manifest, inspect_character,
    write_contact_sheet,
)


def _sample_png(r, g, b, x):
    width, height = 16, 16
    pixels = bytearray(width * height * 4)
    for y in range(3, 13):
        for col in range(2 + (x % 3), 14):
            at = (y * width + col) * 4
            pixels[at:at + 4] = bytes((r, g, b, 255))
    return encode_png(width, height, bytes(pixels))


class CharacterPoseReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="vuf_m06_pose_")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "artist_originals"
        self.source.mkdir()
        self.manifest_file = self.root / "originals.json"
        ref = _sample_png(11, 80, 160, 0)
        (self.source / "reference.png").write_bytes(ref)
        rows = []
        for i, pose in enumerate(POSES):
            name = "pose_" + pose + ".png"
            png = _sample_png((i * 41 + 7) % 255, (i * 53 + 30) % 255,
                              (i * 31 + 50) % 255, i)
            (self.source / name).write_bytes(png)
            rows.append({"pose": pose, "file": name,
                         "sha256": hashlib.sha256(png).hexdigest(),
                         "anchor_xy": [8, 12]})
        self.spec = {
            "schema_version": 1, "stage": STAGE,
            "profile_id": "Coral_Rescue",
            "character_id": "mascot_primary",
            "rights_receipt_id": "owner_source_001",
            "reference": {
                "file": "reference.png",
                "sha256": hashlib.sha256(ref).hexdigest(),
            },
            "poses": rows,
        }
        self._write_manifest()

    def _write_manifest(self):
        self.manifest_file.write_text(json.dumps(self.spec),
                                      encoding="utf-8")

    def test_original_alpha_pose_sheet_and_no_false_authority(self):
        receipt, png = inspect_character(self.manifest_file, self.source)
        self.assertEqual(receipt["profile_id"], "Coral_Rescue")
        self.assertEqual(receipt["frame_canvas"], [16, 16])
        self.assertEqual(receipt["sheet_canvas"], [48, 32])
        self.assertEqual(decode_png(png)[:2], (48, 32))
        self.assertEqual(len(receipt["pose_geometry"]), 5)
        self.assertEqual([p["pose"] for p in receipt["pose_geometry"]],
                         list(POSES))
        for flag in ("owner_art_identity_accepted", "legal_rights_authenticated",
                     "device_qa_verified", "runtime_gameplay_binding",
                     "release_allowed"):
            self.assertIs(receipt[flag], False)

    def test_deterministic_full_six_panel_sheet(self):
        first = inspect_character(self.manifest_file, self.source)
        second = inspect_character(self.manifest_file, self.source)
        self.assertEqual(first, second)
        self.assertEqual(first[0]["contact_sheet_sha256"],
                         hashlib.sha256(first[1]).hexdigest())

    def test_source_sha_mutation_does_not_silently_pass(self):
        (self.source / "pose_idle.png").write_bytes(_sample_png(9, 9, 9, 1))
        with self.assertRaises(PoseReviewError):
            inspect_character(self.manifest_file, self.source)

    def test_duplicate_or_missing_pose_never_inferred(self):
        self.spec["poses"][-1]["pose"] = "idle"
        self._write_manifest()
        with self.assertRaises(PoseReviewError):
            inspect_character(self.manifest_file, self.source)

    def test_unsafe_path_and_duplicate_source_filename_rejected(self):
        self.spec["poses"][0]["file"] = "../private.png"
        self._write_manifest()
        with self.assertRaises(PoseReviewError):
            inspect_character(self.manifest_file, self.source)
        self.spec["poses"][0]["file"] = "reference.png"
        self._write_manifest()
        with self.assertRaises(PoseReviewError):
            inspect_character(self.manifest_file, self.source)

    def test_reject_approval_forgery_and_duplicate_json_fields(self):
        bad = copy.deepcopy(self.spec)
        bad["stage"] = "APPROVED"
        with self.assertRaises(PoseReviewError):
            _manifest(json.dumps(bad).encode())
        with self.assertRaises(PoseReviewError):
            _manifest(b'{"schema_version":1,"schema_version":1}')

    def test_anchor_canvas_and_original_canvas_mismatch_rejected(self):
        self.spec["poses"][0]["anchor_xy"] = [99, 99]
        self._write_manifest()
        with self.assertRaises(PoseReviewError):
            inspect_character(self.manifest_file, self.source)
        self.spec["poses"][0]["anchor_xy"] = [8, 12]
        replacement = encode_png(15, 16, bytes((11, 50, 50, 255)) * 15 * 16)
        (self.source / "pose_idle.png").write_bytes(replacement)
        self.spec["poses"][0]["sha256"] = hashlib.sha256(replacement).hexdigest()
        self._write_manifest()
        with self.assertRaises(PoseReviewError):
            inspect_character(self.manifest_file, self.source)

    def test_new_review_output_only_no_overwrite(self):
        receipt, png = inspect_character(self.manifest_file, self.source)
        output = self.root / "candidate_review"
        write_contact_sheet(output, receipt, png)
        self.assertTrue((output / "pose_contact_sheet.png").is_file())
        self.assertTrue((output / "pose_review_receipt.json").is_file())
        self.assertTrue((self.source / "reference.png").is_file())
        with self.assertRaises(PoseReviewError):
            write_contact_sheet(output, receipt, png)
        forged = dict(receipt)
        forged["owner_art_identity_accepted"] = True
        with self.assertRaises(PoseReviewError):
            write_contact_sheet(self.root / "unapproved", forged, png)


if __name__ == "__main__":
    unittest.main()
