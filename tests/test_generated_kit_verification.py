"""Read-only verification of synthetic image bundles and tamper evidence."""
import json
import tempfile
import unittest
from pathlib import Path
from factory.vfx_builder.procedural_fx_sheet import build_candidate as build_fx, write_candidate as write_fx
from factory.visual_director.silhouette_kit import build_theme_kit, write_once as write_tiles
from factory.image_processor.png_pipeline import encode_png
from factory.image_processor.layer_compositor import render_candidate, write_candidate as write_scene
from factory.validators.verify_generated_kits import (
    BundleError, verify_fx, verify_tiles, verify_scene
)


class GeneratedBundleVerificationTests(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.root = Path(t.name)

    def fx(self):
        folder = self.root / "fx"
        write_fx(folder, *build_fx("BubbleRise", frames=4, frame_side=24,
                                   columns=2))
        return folder

    def tiles(self):
        folder = self.root / "tiles"
        manifest, pngs = build_theme_kit("Coral_Rescue", side=24)
        write_tiles(folder, manifest, pngs)
        return folder

    def scene(self):
        original = self.root / "source"
        original.mkdir()
        layer = original / "layer.png"
        layer.write_bytes(encode_png(2, 2, bytes((4, 20, 44, 128)) * 4))
        import hashlib
        specs = {
            "schema_version": 1, "stage": "CANDIDATE_NOT_OWNER_APPROVED",
            "profile_id": "Coral_Rescue", "width": 4, "height": 4,
            "background": None,
            "layers": [{
                "id": "base", "file": "layer.png",
                "sha256": hashlib.sha256(layer.read_bytes()).hexdigest(),
                "x": 1, "y": 1, "opacity": 255
            }]
        }
        descriptor = self.root / "manifest.json"
        descriptor.write_text(json.dumps(specs), encoding="utf-8")
        receipt, png = render_candidate(descriptor, original)
        output = self.root / "scene"
        write_scene(output, receipt, png, [layer])
        return output

    def test_each_real_bundle_verifies_as_candidate_only(self):
        fx = verify_fx(self.fx())
        tiles = verify_tiles(self.tiles())
        scene = verify_scene(self.scene())
        self.assertEqual(fx["frames_checked"], 4)
        self.assertEqual(tiles["shapes_checked"], 6)
        self.assertEqual(scene["layers_recorded"], 1)
        for result in (fx, tiles, scene):
            self.assertEqual(result["stage"], "VERIFIED_CANDIDATE_ONLY")
            self.assertFalse(result["rights_verified"])
            self.assertFalse(result["visual_approved"])

    def test_fx_corrupted_atlas_cannot_pass(self):
        folder = self.fx()
        target = folder / "fx_sheet.png"
        raw = bytearray(target.read_bytes())
        raw[24] ^= 8
        target.write_bytes(raw)
        with self.assertRaises(BundleError):
            verify_fx(folder)

    def test_fx_frame_digest_forgery_rejected(self):
        folder = self.fx()
        manifest = folder / "fx_manifest.json"
        obj = json.loads(manifest.read_text())
        obj["animation_frames"][0]["rgba_sha256"] = "0" * 64
        manifest.write_text(json.dumps(obj))
        with self.assertRaises(BundleError):
            verify_fx(folder)

    def test_fx_forged_gameplay_or_rights_rejected(self):
        folder = self.fx()
        manifest = folder / "fx_manifest.json"
        obj = json.loads(manifest.read_text())
        obj["engine_side_effects_allowed"] = True
        manifest.write_text(json.dumps(obj))
        with self.assertRaises(BundleError):
            verify_fx(folder)

    def test_tile_shape_image_corruption_cannot_pass(self):
        folder = self.tiles()
        sprite = folder / "tile_star.png"
        sprite.write_bytes(b"fake")
        with self.assertRaises(BundleError):
            verify_tiles(folder)

    def test_tile_forged_owner_approval_rejected(self):
        folder = self.tiles()
        path = folder / "tile_manifest.json"
        obj = json.loads(path.read_text())
        obj["owner_visual_approval"] = True
        path.write_text(json.dumps(obj))
        with self.assertRaises(BundleError):
            verify_tiles(folder)

    def test_scene_sha_mutation_rejected(self):
        folder = self.scene()
        path = folder / "scene.png"
        path.write_bytes(path.read_bytes() + b"extra")
        with self.assertRaises(BundleError):
            verify_scene(folder)

    def test_scene_claims_original_source_hash_but_does_not_reverify_rights(self):
        folder = self.scene()
        outcome = verify_scene(folder)
        self.assertFalse(outcome["original_source_bytes_reverified"])
        self.assertFalse(outcome["rights_verified"])

    def test_duplicate_manifest_object_fields_rejected(self):
        folder = self.fx()
        descriptor = folder / "fx_manifest.json"
        descriptor.write_text('{"schema_version":1,"schema_version":1}')
        with self.assertRaises(BundleError):
            verify_fx(folder)


if __name__ == "__main__":
    unittest.main()
