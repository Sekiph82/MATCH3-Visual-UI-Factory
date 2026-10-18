"""VUF-M06 real candidate layer-pack tests; no Editor/device/owner PASS inferred."""
import copy
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from factory.image_processor.png_pipeline import decode_png
from factory.image_processor.representative_scene_pack import (
    BASE_SIZE, CORAL_EXTRA, LAYER_ORDER, PROFILES, ScenePackError,
    build_representative_pack, main, render_scene_layer,
    verify_representative_pack, write_representative_pack,
)


class RepresentativeScenePackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest, cls.images = build_representative_pack()

    def test_five_theme_real_three_layer_png_coverage(self):
        m = self.manifest
        self.assertEqual(m["scene_count"], 19)
        self.assertEqual(m["file_count"], 57)
        self.assertEqual(len(self.images), 57)
        self.assertEqual(len(m["scenes"]), 19)
        self.assertEqual(len([s for s in m["scenes"]
                              if s["profile_id"] == "Coral_Rescue"]), 7)
        for profile in PROFILES[1:]:
            self.assertEqual(len([s for s in m["scenes"]
                                  if s["profile_id"] == profile]), 3)
        self.assertEqual(
            {s["scene_id"] for s in m["scenes"]
             if s["profile_id"] == "Coral_Rescue"},
            set(CORAL_EXTRA) | {"world_map", "chapter_map", "gameplay"})
        verify_representative_pack(m, self.images)

    def test_layers_are_distinct_raw_bytes_and_not_a_flat_interactive_page(self):
        for scene in self.manifest["scenes"]:
            self.assertTrue(scene["runtime_ui_separate"])
            self.assertFalse(scene["owner_visual_approved"])
            self.assertEqual([x["layer_id"] for x in scene["layers"]],
                             list(LAYER_ORDER))
            seen = set()
            for row in scene["layers"]:
                self.assertFalse(row["interactive"])
                self.assertFalse(row["contains_runtime_text"])
                self.assertFalse(row["contains_runtime_buttons"])
                w, h, pixels = decode_png(self.images[row["file"]])
                self.assertEqual([w, h], list(BASE_SIZE))
                self.assertGreater(sum(a > 0 for a in pixels[3::4]), 0)
                seen.add(row["png_sha256"])
            self.assertEqual(len(seen), 3)

    def test_candidate_never_misstates_owner_rights_engine_or_device(self):
        m = self.manifest
        for flag in ("owner_visual_approval", "art_rights_verified",
                     "real_device_verified", "parallax_runtime_validated",
                     "real_engine_visual_binding", "release_allowed"):
            self.assertIs(m[flag], False)
            counterfeit = copy.deepcopy(m)
            counterfeit[flag] = True
            with self.subTest(flag=flag), self.assertRaises(ScenePackError):
                verify_representative_pack(counterfeit, self.images)

    def test_mutated_raw_png_byte_or_missing_or_extra_file_fails(self):
        name = next(iter(self.images))
        bad = self.images.copy()
        bad[name] = bad[name][:-2] + b"xy"
        with self.assertRaises(ScenePackError):
            verify_representative_pack(self.manifest, bad)
        bad = self.images.copy()
        bad.pop(name)
        with self.assertRaises(ScenePackError):
            verify_representative_pack(self.manifest, bad)
        bad = self.images.copy()
        bad["untracked.png"] = b"x"
        with self.assertRaises(ScenePackError):
            verify_representative_pack(self.manifest, bad)

    def test_reordered_layers_and_forged_parallax_or_style_are_rejected(self):
        cases = ("parallax_factor_milli", "style_source_sha256", "draw_order")
        for key in cases:
            bad = copy.deepcopy(self.manifest)
            bad["scenes"][0]["layers"][1][key] = "FORGED"
            with self.subTest(field=key), self.assertRaises(ScenePackError):
                verify_representative_pack(bad, self.images)
        bad = copy.deepcopy(self.manifest)
        bad["scenes"][0]["layers"].reverse()
        with self.assertRaises(ScenePackError):
            verify_representative_pack(bad, self.images)

    def test_cross_theme_and_unknown_scene_are_refused(self):
        for profile, scene in [
                ("Wonder_Pop", "my_aquarium"),
                ("Garage_Legends", "reef_restoration"),
                ("Coral_Rescue", "store_login"),
                ("../private", "gameplay")]:
            with self.subTest(profile=profile, scene=scene):
                with self.assertRaises(ScenePackError):
                    render_scene_layer(profile, scene, "backdrop")
        with self.assertRaises(ScenePackError):
            render_scene_layer(PROFILES[0], "gameplay", "HUD")

    def test_invalid_seed_scale_fail_closed(self):
        for bad in (0, -1, 4, True, "2"):
            with self.subTest(scale=bad), self.assertRaises(ScenePackError):
                render_scene_layer(PROFILES[0], "gameplay", "backdrop", scale=bad)
        for bad in (-1, 10000, 0.2, True):
            with self.subTest(seed=bad), self.assertRaises(ScenePackError):
                render_scene_layer(PROFILES[0], "gameplay", "backdrop", seed=bad)

    def test_repeated_single_layer_bytes_are_deterministic(self):
        for profile in PROFILES:
            first = render_scene_layer(profile, "world_map", "near_decoration",
                                       scale=1, seed=41)
            second = render_scene_layer(profile, "world_map", "near_decoration",
                                        scale=1, seed=41)
            self.assertEqual(first, second)

    def test_2x_layer_dimensions_and_three_parallax_states(self):
        for layer in LAYER_ORDER:
            receipt, png = render_scene_layer("Coral_Rescue", "my_aquarium",
                                              layer, scale=2, seed=12)
            self.assertEqual(receipt["dimensions"], [360, 640])
            self.assertEqual(decode_png(png)[:2], (360, 640))
            self.assertNotIn("runtime", receipt["layer_id"])

    def test_export_to_new_isolated_directory_without_overwriting(self):
        with tempfile.TemporaryDirectory(prefix="vuf_m06_owner_safe_") as root:
            dst = Path(root) / "scene_candidate"
            write_representative_pack(dst, self.manifest, self.images)
            self.assertTrue((dst / "scene_pack_manifest.json").is_file())
            self.assertEqual(len(list(dst.glob("*.png"))), 57)
            file_manifest = json.loads((dst / "scene_pack_manifest.json").read_text())
            self.assertEqual(file_manifest, self.manifest)
            with self.assertRaises(ScenePackError):
                write_representative_pack(dst, self.manifest, self.images)

    def test_no_default_cli_write(self):
        stream = io.StringIO()
        with redirect_stdout(stream):
            rc = main(["--scale", "1", "--seed", "17"])
        self.assertEqual(rc, 0)
        outcome = json.loads(stream.getvalue())
        self.assertFalse(outcome["output_saved"])
        self.assertFalse(outcome["release_allowed"])
        self.assertEqual(outcome["file_count"], 57)


if __name__ == "__main__":
    unittest.main()
