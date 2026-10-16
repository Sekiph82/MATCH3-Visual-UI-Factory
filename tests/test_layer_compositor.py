"""VF-04 deterministic layered PNG scene candidate composition tests."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from contextlib import redirect_stdout
from io import StringIO

from factory.image_processor.png_pipeline import encode_png, decode_png
from factory.image_processor.layer_compositor import (
    CompositorError, render_candidate, write_candidate, main
)


class SceneCompositorTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.originals = self.root / "original"
        self.originals.mkdir()
        self.background = self.originals / "sky.png"
        self.foreground = self.originals / "coral.png"
        self.background.write_bytes(encode_png(2, 2,
            bytes((20, 40, 60, 255)) * 4))
        self.foreground.write_bytes(encode_png(2, 2, bytes((
            240, 10, 20, 255,
            240, 10, 20, 128,
            0, 0, 0, 0,
            240, 10, 20, 255
        ))))
        self.manifest = self.root / "compose.json"
        self.data = {
            "schema_version": 1, "stage": "CANDIDATE_NOT_OWNER_APPROVED",
            "profile_id": "Coral_Rescue", "width": 3, "height": 3,
            "background": None, "layers": [
                self.layer("background", self.background, 0, 0),
                self.layer("foreground", self.foreground, 1, 1)
            ]
        }
        self.save()

    @staticmethod
    def layer(key, file, x, y, opacity=255):
        return {"id": key, "file": file.name,
                "sha256": hashlib.sha256(file.read_bytes()).hexdigest(),
                "x": x, "y": y, "opacity": opacity}

    def save(self):
        self.manifest.write_text(json.dumps(self.data), encoding="utf-8")

    def test_exact_opaque_and_translucent_composite(self):
        receipt, png = render_candidate(self.manifest, self.originals)
        w, h, rgba = decode_png(png)
        self.assertEqual((w, h), (3, 3))
        self.assertEqual(rgba[:4], bytes((20, 40, 60, 255)))
        self.assertEqual(rgba[(1 * 3 + 1) * 4:(1 * 3 + 1) * 4 + 4],
                         bytes((240, 10, 20, 255)))
        self.assertEqual(rgba[(1 * 3 + 2) * 4:(1 * 3 + 2) * 4 + 4],
                         bytes((240, 10, 20, 128)))
        self.assertEqual(receipt["image_sha256"], hashlib.sha256(png).hexdigest())
        self.assertFalse(receipt["owner_visual_approved"])

    def test_fully_transparent_source_does_not_modify_destination(self):
        self.data["layers"] = [self.data["layers"][0]]
        self.save()
        _, png = render_candidate(self.manifest, self.originals)
        _, _, pixels = decode_png(png)
        self.assertEqual(pixels[(1 * 3 + 1) * 4:(1 * 3 + 1) * 4 + 4],
                         bytes((20, 40, 60, 255)))
        self.assertEqual(pixels[(2 * 3 + 2) * 4:(2 * 3 + 2) * 4 + 4],
                         bytes(4))

    def test_opacity_zero_is_equivalent_to_absent_layer(self):
        self.data["layers"][1]["opacity"] = 0
        self.save()
        _, one = render_candidate(self.manifest, self.originals)
        self.data["layers"].pop()
        self.save()
        _, two = render_candidate(self.manifest, self.originals)
        self.assertEqual(one, two)

    def test_original_layer_order_changes_output(self):
        _, normal = render_candidate(self.manifest, self.originals)
        self.data["layers"].reverse()
        self.save()
        _, reversed_png = render_candidate(self.manifest, self.originals)
        self.assertNotEqual(normal, reversed_png)

    def test_negative_top_left_clips_outside_scene(self):
        self.data["layers"][1]["x"] = -1
        self.data["layers"][1]["y"] = -1
        self.save()
        _, png = render_candidate(self.manifest, self.originals)
        _, _, rgba = decode_png(png)
        self.assertEqual(len(rgba), 3 * 3 * 4)

    def test_source_hash_tamper_rejected_without_writes(self):
        self.background.write_bytes(encode_png(2, 2, bytes((99, 4, 5, 255))*4))
        with self.assertRaises(CompositorError):
            render_candidate(self.manifest, self.originals)
        self.assertFalse((self.root / "candidate").exists())

    def test_duplicate_keys_and_duplicate_json_are_rejected(self):
        self.data["layers"][1]["id"] = "background"
        self.save()
        with self.assertRaises(CompositorError):
            render_candidate(self.manifest, self.originals)
        self.manifest.write_text('{"schema_version":1,"schema_version":1}')
        with self.assertRaises(CompositorError):
            render_candidate(self.manifest, self.originals)

    def test_invalid_paths_profile_opacity_stage_and_canvas_bounds(self):
        for key, value in (
            ("stage", "OWNER_APPROVED"),
            ("profile_id", "unknown"),
            ("width", 3000),
            ("width", True),
            ("layers", []),
            ("background", "none")
        ):
            with self.subTest(key=key):
                original = self.data[key]
                self.data[key] = value
                self.save()
                with self.assertRaises(CompositorError):
                    render_candidate(self.manifest, self.originals)
                self.data[key] = original
        self.data["layers"][0]["file"] = "../secret.png"
        self.save()
        with self.assertRaises(CompositorError):
            render_candidate(self.manifest, self.originals)

    def test_write_once_does_not_overwrite_existing_files(self):
        receipt, png = render_candidate(self.manifest, self.originals)
        destination = self.root / "candidate"
        write_candidate(destination, receipt, png, [self.manifest])
        original = (destination / "scene.png").read_bytes()
        with self.assertRaises(CompositorError):
            write_candidate(destination, receipt, b"changed", [self.manifest])
        self.assertEqual((destination / "scene.png").read_bytes(), original)

    def test_dry_run_does_not_create_any_assets(self):
        out = StringIO()
        with redirect_stdout(out):
            self.assertEqual(main(["--manifest", str(self.manifest),
                                   "--source-root", str(self.originals)]), 0)
        self.assertFalse(json.loads(out.getvalue())["output_saved"])
        self.assertFalse((self.root / "scene.png").exists())

    def test_repeated_runs_are_pixel_and_receipt_deterministic(self):
        self.assertEqual(render_candidate(self.manifest, self.originals),
                         render_candidate(self.manifest, self.originals))

    def test_cannot_write_composed_asset_inside_checkout(self):
        from factory.image_processor.layer_compositor import ROOT
        receipt, png = render_candidate(self.manifest, self.originals)
        with self.assertRaises(CompositorError):
            write_candidate(ROOT / "bad-scene", receipt, png, [self.manifest])


if __name__ == "__main__":
    unittest.main()
