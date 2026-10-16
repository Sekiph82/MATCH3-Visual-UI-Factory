"""VF-07 mathematical concept-screen batch source regression.

Actual image pixels are synthetic mockups, not Unity GUI or premium art.
"""
from __future__ import annotations
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from factory.image_processor.png_pipeline import decode_png
from factory.ui_composer.concept_showcase import (
    GENERATOR, PAGES, PROFILES, ShowcaseError,
    build_showcase, render_preview, write_showcase,
)


class ConceptShowcaseTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.base = Path(tmp.name)

    def test_fifteen_real_pngs_and_per_profile_three_pages(self):
        manifest, files = build_showcase(scale=1, seed=1)
        self.assertEqual(manifest["file_count"], 15)
        self.assertEqual(len(files), 15)
        self.assertEqual(manifest["generator"], GENERATOR)
        self.assertEqual(manifest["dimensions"], [360, 640])
        self.assertFalse(manifest["interactive_ui_enabled"])
        self.assertFalse(manifest["owner_visual_approval"])
        self.assertEqual({row["profile_id"] for row in manifest["screens"]},
                         set(PROFILES))
        for profile in PROFILES:
            self.assertEqual({row["screen_key"] for row in manifest["screens"]
                              if row["profile_id"] == profile}, set(PAGES))

    def test_each_page_produces_actual_rgba_png_with_sha_receipt(self):
        for page in PAGES:
            with self.subTest(page=page):
                receipt, raw = render_preview("Coral_Rescue", page)
                w, h, rgba = decode_png(raw)
                self.assertEqual((w, h), (360, 640))
                self.assertEqual(hashlib.sha256(raw).hexdigest(),
                                 receipt["png_sha256"])
                self.assertTrue(all(alpha == 255 for alpha in rgba[3::4]))
                self.assertFalse(receipt["interactive"])
                self.assertEqual(receipt["screen_state"],
                                 "VISUAL_CONCEPT_NOT_INTERACTIVE")

    def test_five_themes_use_different_actual_pixels_not_only_names(self):
        pngs = [render_preview(profile, "gameplay")[1] for profile in PROFILES]
        self.assertEqual(len({hashlib.sha256(p).hexdigest() for p in pngs}), 5)

    def test_same_seed_creates_exact_reproducible_png(self):
        self.assertEqual(render_preview("Wonder_Pop", "world_map", seed=21),
                         render_preview("Wonder_Pop", "world_map", seed=21))

    def test_distinct_seed_changes_composition_not_contract(self):
        a, x = render_preview("Dino_Islands", "gameplay", seed=1)
        b, y = render_preview("Dino_Islands", "gameplay", seed=4)
        self.assertNotEqual(x, y)
        self.assertEqual(a["dimensions"], b["dimensions"])
        self.assertEqual(a["style_source_sha256"], b["style_source_sha256"])

    def test_720x1280_portrait_supported(self):
        manifest, img = render_preview("Garage_Legends", "home", scale=2)
        w, h, _ = decode_png(img)
        self.assertEqual([w, h], manifest["dimensions"])
        self.assertEqual((w, h), (720, 1280))

    def test_invalid_profile_page_scale_and_seed_fail_closed(self):
        for kwargs in ({"profile": "nonexistent", "page": "home"},
                       {"profile": "Coral_Rescue", "page": "VIP"},
                       {"profile": "Coral_Rescue", "page": "home", "scale": True},
                       {"profile": "Coral_Rescue", "page": "home", "scale": 3},
                       {"profile": "Coral_Rescue", "page": "home", "seed": -1},
                       {"profile": "Coral_Rescue", "page": "home", "seed": 10000}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ShowcaseError):
                render_preview(**kwargs)

    def test_write_once_protects_existing_showcase(self):
        manifest, files = build_showcase()
        dest = self.base / "showcase"
        write_showcase(dest, manifest, files)
        first = (dest / "preview_Coral_Rescue_home.png").read_bytes()
        self.assertEqual(json.loads((dest / "showcase_manifest.json").read_text()),
                         manifest)
        with self.assertRaises(ShowcaseError):
            write_showcase(dest, manifest, files)
        self.assertEqual((dest / "preview_Coral_Rescue_home.png").read_bytes(),
                         first)

    def test_forged_approval_and_swapped_hash_refuse_write(self):
        manifest, files = build_showcase()
        dest = self.base / "forgery"
        manifest["owner_visual_approval"] = True
        with self.assertRaises(ShowcaseError):
            write_showcase(dest, manifest, files)
        self.assertFalse(dest.exists())
        manifest["owner_visual_approval"] = False
        manifest["screens"][0]["png_sha256"] = "0" * 64
        with self.assertRaises(ShowcaseError):
            write_showcase(dest, manifest, files)
        self.assertFalse(dest.exists())

    def test_checkout_paths_are_not_writable_targets(self):
        from factory.ui_composer.concept_showcase import ROOT
        manifest, files = build_showcase()
        with self.assertRaises(ShowcaseError):
            write_showcase(ROOT / "invalid-showcase", manifest, files)


if __name__ == "__main__":
    unittest.main()
