"""VUF-M06-003: responsive layer review preview tests, no real device PASS."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from factory.image_processor.png_pipeline import decode_png
from factory.image_processor.representative_scene_pack import (
    build_representative_pack, render_scene_layer,
)
from factory.image_processor.scene_viewport_export import (
    ViewportPreviewError, _target_size, render_viewport, write_preview,
)


class SceneViewportExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest, cls.images = build_representative_pack(scale=1, seed=37)

    def render(self, profile="Coral_Rescue", scene="gameplay", **kw):
        return render_viewport(self.manifest, self.images, profile, scene, **kw)

    def test_all_three_aspect_outputs_keep_source_identity_and_no_ui_authority(self):
        expected = {
            "portrait": (180, 320), "tall_phone": (180, 390),
            "tablet": (240, 320),
        }
        for aspect, size in expected.items():
            with self.subTest(aspect=aspect):
                receipt, png = self.render(aspect=aspect)
                self.assertEqual(tuple(receipt["output_dimensions"]), size)
                self.assertEqual(decode_png(png)[:2], size)
                self.assertEqual(receipt["profile_id"], "Coral_Rescue")
                self.assertFalse(receipt["is_runnable_runtime_ui"])
                self.assertTrue(receipt["ui_stays_interactive_in_separate_unity_layers"])
                self.assertFalse(receipt["owner_visual_approval"])
                self.assertFalse(receipt["release_allowed"])

    def test_five_themes_are_independent_and_can_be_reviewed_in_one_aspect(self):
        digests = set()
        for profile in ("Coral_Rescue", "Garage_Legends", "Dino_Islands",
                        "The_Fractured_Realms", "Wonder_Pop"):
            with self.subTest(profile=profile):
                result, png = self.render(
                    profile=profile, scene="world_map", aspect="portrait")
                self.assertEqual(result["profile_id"], profile)
                self.assertFalse(result["owner_visual_approval"])
                self.assertNotIn(result["png_sha256"], digests)
                digests.add(result["png_sha256"])
                w, h, rgba = decode_png(png)
                self.assertEqual((w, h), (180, 320))
                self.assertTrue(all(a == 255 for a in rgba[3::4]))
        self.assertEqual(len(digests), 5)

    def test_original_source_cover_geometry_does_not_stretch_aspect(self):
        self.assertEqual(_target_size(180, 320, "portrait"), (180, 320))
        self.assertEqual(_target_size(180, 320, "tall_phone"), (180, 390))
        self.assertEqual(_target_size(180, 320, "tablet"), (240, 320))
        self.assertEqual(_target_size(360, 640, "tablet"), (480, 640))
        self.assertEqual(_target_size(540, 960, "tall_phone"), (540, 1170))

    def test_deterministic_sha_and_camera_shift_reproducible(self):
        first = self.render(aspect="tall_phone", offset_px=64)
        second = self.render(aspect="tall_phone", offset_px=64)
        self.assertEqual(first, second)
        self.assertEqual(first[0]["png_sha256"], hashlib.sha256(first[1]).hexdigest())
        baseline = self.render(aspect="tall_phone", offset_px=0)
        self.assertNotEqual(first[0]["png_sha256"], baseline[0]["png_sha256"])

    def test_guide_is_synthetic_and_does_not_approve_art_or_device(self):
        receipt, png = self.render(aspect="tablet", safe_guides=True)
        self.assertTrue(receipt["synthetic_safe_guides"]["synthetic_not_device_safe_area"])
        self.assertFalse(receipt["actual_device_safe_area_verified"])
        self.assertFalse(receipt["real_device_gpu_parallax_verified"])
        width, height, pixels = decode_png(png)
        guide = receipt["synthetic_safe_guides"]
        at = (guide["top"] * width + guide["left"]) * 4
        self.assertEqual(pixels[at:at+4], bytes((255, 211, 40, 255)))

    def test_excluded_source_and_tampered_png_digests_fail(self):
        fake = self.images.copy()
        key = next(iter(fake))
        fake[key] = fake[key][:-1] + b"z"
        with self.assertRaises(ViewportPreviewError):
            render_viewport(self.manifest, fake, "Coral_Rescue", "gameplay")
        bad = copy.deepcopy(self.manifest)
        bad["owner_visual_approval"] = True
        with self.assertRaises(ViewportPreviewError):
            render_viewport(bad, self.images, "Coral_Rescue", "gameplay")

    def test_invalid_profile_scene_aspect_offset_and_guide_fail_closed(self):
        cases = (
            {"profile": "../private"},
            {"scene": "private_editor"},
            {"aspect": "device_certified"},
            {"offset_px": 161},
            {"offset_px": True},
            {"safe_guides": 1},
        )
        for params in cases:
            args = {"profile": "Coral_Rescue", "scene": "gameplay"}
            args.update(params)
            with self.subTest(params=params), self.assertRaises(ViewportPreviewError):
                render_viewport(self.manifest, self.images, **args)

    def test_write_only_new_external_review_directory_and_preserve_sources(self):
        receipt, png = self.render(aspect="portrait", safe_guides=True)
        with tempfile.TemporaryDirectory(prefix="vuf_m06_responsive_") as temp:
            dest = Path(temp) / "artwork_review"
            write_preview(dest, receipt, png)
            self.assertEqual((dest / "artwork_review_only.png").read_bytes(), png)
            self.assertEqual(json.loads(
                (dest / "artwork_review_receipt.json").read_text()), receipt)
            with self.assertRaises(ViewportPreviewError):
                write_preview(dest, receipt, png)
            forged = dict(receipt)
            forged["owner_visual_approval"] = True
            with self.assertRaises(ViewportPreviewError):
                write_preview(Path(temp) / "forged", forged, png)

    def test_independent_three_x_source_generation_is_supported(self):
        receipt, png = render_scene_layer(
            "Wonder_Pop", "world_map", "near_decoration", scale=3, seed=12)
        self.assertEqual(receipt["dimensions"], [540, 960])
        self.assertEqual(decode_png(png)[:2], (540, 960))


if __name__ == "__main__":
    unittest.main()
