"""R49 / M05-005 adversarial tests. No Unity/phone/rights PASS implied."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from factory.image_processor.png_pipeline import encode_png
from factory.image_processor.atlas_pipeline import create_atlas_candidate
from factory.validators.atlas_candidate_audit import (
    AtlasAuditError, audit_candidate,
)


class AtlasCandidateAuditTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.first = self.root / "first.png"
        self.second = self.root / "second.png"
        self.first.write_bytes(encode_png(2, 2, bytes([
            250, 40, 35, 255,
            10, 80, 10, 0,
            40, 100, 200, 128,
            80, 30, 140, 255,
        ])))
        self.second.write_bytes(encode_png(2, 2, bytes([
            10, 20, 240, 255,
            100, 30, 20, 255,
            130, 240, 120, 255,
            40, 90, 250, 0,
        ])))
        self.target = self.root / "candidate"
        create_atlas_candidate(
            {"tile.red": self.first, "tile.blue": self.second},
            self.target, padding=2, extrude=1)

    def _manifest(self):
        return json.loads((self.target / "atlas_manifest.json").read_text("utf-8"))

    def _replace(self, doc):
        (self.target / "atlas_manifest.json").write_text(
            json.dumps(doc, sort_keys=True) + "\n", encoding="utf-8")

    def test_real_bytes_geometry_alpha_budget_and_fail_closed_gates(self):
        outcome = audit_candidate(
            self.target, required_ids=["tile.red", "tile.blue"],
            distinct_alpha_masks=True)
        self.assertEqual(outcome["sprite_count"], 2)
        self.assertGreater(outcome["alpha_nonzero_pixels"], 0)
        self.assertGreater(outcome["alpha_partial_pixels"], 0)
        self.assertFalse(outcome["release_allowed"])
        self.assertFalse(outcome["licensed_rights_verified"])
        self.assertFalse(outcome["source_original_bytes_reverified"])
        self.assertTrue(outcome["estimated_not_measured_gpu_memory"])

    def test_missing_required_state_refused(self):
        with self.assertRaisesRegex(AtlasAuditError, "missing required"):
            audit_candidate(self.target, required_ids=["tile.red", "tile.missing"])

    def test_atlas_memory_budget_fails_closed(self):
        with self.assertRaisesRegex(AtlasAuditError, "memory budget"):
            audit_candidate(self.target, max_memory_bytes=1)

    def test_modified_atlas_bytes_refused(self):
        target = self.target / "atlas.png"
        data = bytearray(target.read_bytes())
        data[-1] ^= 0x01
        target.write_bytes(data)
        with self.assertRaisesRegex(AtlasAuditError, "SHA256"):
            audit_candidate(self.target)

    def test_duplicate_sprite_id_refused(self):
        doc = self._manifest()
        doc["sprites"].append(dict(doc["sprites"][0]))
        self._replace(doc)
        with self.assertRaisesRegex(AtlasAuditError, "duplicate"):
            audit_candidate(self.target)

    def test_invalid_uv_and_overlap_are_rejected(self):
        doc = self._manifest()
        doc["sprites"][0]["uv_rect_bottom_left"][0] = 0.99
        self._replace(doc)
        with self.assertRaisesRegex(AtlasAuditError, "UV"):
            audit_candidate(self.target)
        doc = self._manifest()
        doc["sprites"][0]["uv_rect_bottom_left"][0] = (
            doc["sprites"][0]["pixel_rect_top_left"][0] / doc["width"])
        doc["sprites"][1]["pixel_rect_top_left"] = list(
            doc["sprites"][0]["pixel_rect_top_left"])
        self._replace(doc)
        with self.assertRaisesRegex(AtlasAuditError, "overlapping"):
            audit_candidate(self.target)

    def test_claimed_approved_stage_refused(self):
        doc = self._manifest()
        doc["stage"] = "APPROVED"
        self._replace(doc)
        with self.assertRaisesRegex(AtlasAuditError, "schema/stage"):
            audit_candidate(self.target)

    def test_manifest_duplicate_json_key_refused(self):
        doc = self._manifest()
        raw = json.dumps(doc)
        raw = '{"schema_version": 1,' + raw[1:]
        (self.target / "atlas_manifest.json").write_text(raw, encoding="utf-8")
        with self.assertRaisesRegex(AtlasAuditError, "invalid or duplicate"):
            audit_candidate(self.target)

    def test_fully_transparent_sprite_fails(self):
        blank = self.root / "blank.png"
        blank.write_bytes(encode_png(2, 2, bytes([0, 0, 0, 0]) * 4))
        candidate = self.root / "blank_candidate"
        create_atlas_candidate({"tile.blank": blank}, candidate)
        with self.assertRaisesRegex(AtlasAuditError, "entirely transparent"):
            audit_candidate(candidate)

    def test_duplicate_pixel_art_fails(self):
        dup = self.root / "dupe.png"
        dup.write_bytes(self.first.read_bytes())
        candidate = self.root / "dupe_candidate"
        create_atlas_candidate({"tile.first": self.first, "tile.dupe": dup}, candidate)
        with self.assertRaisesRegex(AtlasAuditError, "duplicate exact"):
            audit_candidate(candidate)

    def test_refuses_symlinked_atlas_when_supported(self):
        source = self.target / "atlas.png"
        original = self.target / "genuine.png"
        source.rename(original)
        try:
            source.symlink_to(original)
        except (OSError, NotImplementedError):
            original.rename(source)
            self.skipTest("OS does not permit unprivileged symlinks")
        with self.assertRaisesRegex(AtlasAuditError, "unlinked"):
            audit_candidate(self.target)

    def test_duplicate_required_id_refused(self):
        with self.assertRaisesRegex(AtlasAuditError, "duplicate required"):
            audit_candidate(self.target, required_ids=["tile.red", "tile.red"])


if __name__ == "__main__":
    unittest.main()
