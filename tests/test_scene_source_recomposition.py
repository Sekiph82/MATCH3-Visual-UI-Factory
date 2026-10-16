"""R33 opt-in source-original recomposition proof, never copyright approval."""
from __future__ import annotations
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from factory.image_processor.png_pipeline import encode_png
from factory.image_processor.layer_compositor import render_candidate, write_candidate
from factory.validators.verify_generated_kits import (
    BundleError, verify_scene, verify_scene_sources, main
)


class SceneSourceRecompositionTests(unittest.TestCase):
    def setUp(self):
        cache = tempfile.TemporaryDirectory()
        self.addCleanup(cache.cleanup)
        self.work = Path(cache.name)
        self.originals = self.work / "licensed_originals"
        self.originals.mkdir()
        self.source = self.originals / "layer.png"
        self.source.write_bytes(encode_png(3, 2, bytes((10, 100, 55, 120)) * 6))
        self.manifest = self.work / "scene_sources.json"
        self.write_source_spec()
        self.output = self.work / "scene"
        receipt, png = render_candidate(self.manifest, self.originals)
        write_candidate(self.output, receipt, png, [self.manifest])

    def write_source_spec(self, offset=0):
        self.manifest.write_text(json.dumps({
            "schema_version": 1,
            "stage": "CANDIDATE_NOT_OWNER_APPROVED",
            "profile_id": "Dino_Islands",
            "width": 8, "height": 8, "background": "#163D31",
            "layers": [{
                "id": "foreground", "file": "layer.png",
                "sha256": hashlib.sha256(self.source.read_bytes()).hexdigest(),
                "x": offset, "y": 2, "opacity": 170
            }]
        }), encoding="utf-8")

    def test_recomposed_bytes_match_exact_saved_candidate(self):
        report = verify_scene_sources(self.output, self.manifest, self.originals)
        self.assertTrue(report["original_source_bytes_reverified"])
        self.assertEqual(report["original_layers_reverified"], 1)
        self.assertFalse(report["rights_verified"])
        self.assertFalse(report["visual_approved"])

    def test_simple_receipt_only_audit_does_not_claim_source_reverification(self):
        report = verify_scene(self.output)
        self.assertFalse(report["original_source_bytes_reverified"])

    def test_tampering_with_original_png_fails_even_if_scene_receipt_still_matches(self):
        self.source.write_bytes(encode_png(3, 2, bytes((10, 100, 55, 121)) * 6))
        self.assertEqual(verify_scene(self.output)["kind"], "scene")
        with self.assertRaises(BundleError):
            verify_scene_sources(self.output, self.manifest, self.originals)

    def test_reordered_or_shifted_source_manifest_fails(self):
        self.write_source_spec(offset=1)
        with self.assertRaises(BundleError):
            verify_scene_sources(self.output, self.manifest, self.originals)

    def test_missing_original_source_fails_closed(self):
        self.source.rename(self.originals / "moved.png")
        with self.assertRaises(BundleError):
            verify_scene_sources(self.output, self.manifest, self.originals)


if __name__ == "__main__":
    unittest.main()
