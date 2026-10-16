"""R34 source-generated five-game one-image contact-sheet regression."""
from __future__ import annotations
import hashlib
import tempfile
import unittest
from pathlib import Path

from factory.image_processor.png_pipeline import decode_png
from factory.ui_composer.concept_showcase import build_showcase, write_showcase
from factory.ui_composer.contact_sheet import (
    ContactSheetError, build_contact_sheet, save_once,
)


class ConceptContactSheetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.folder = Path(cls.tmp.name)
        cls.source = cls.folder / "showcase"
        manifest, images = build_showcase(seed=2)
        write_showcase(cls.source, manifest, images)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_contact_sheet_contains_fifteen_labeled_cells(self):
        manifest, png = build_contact_sheet(self.source)
        self.assertEqual(manifest["cell_count"], 15)
        self.assertEqual(manifest["columns"], 5)
        self.assertEqual(manifest["rows"], 3)
        self.assertEqual(len(manifest["cells"]), 15)
        self.assertEqual(manifest["cells"][0]["screen_key"], "home")
        self.assertEqual(manifest["cells"][0]["profile_id"], "Coral_Rescue")
        self.assertEqual(manifest["cells"][-1]["screen_key"], "world_map")
        self.assertEqual(manifest["stage"], "CANDIDATE_NOT_OWNER_APPROVED")
        self.assertFalse(manifest["interactive_ui_enabled"])
        self.assertFalse(manifest["owner_visual_approval"])
        width, height, rgba = decode_png(png)
        self.assertEqual([width, height], manifest["dimensions"])
        self.assertGreater(width, height // 2)
        self.assertTrue(all(a == 255 for a in rgba[3::4]))
        self.assertEqual(hashlib.sha256(png).hexdigest(),
                         manifest["contact_png_sha256"])

    def test_byte_deterministic_with_fixed_source(self):
        self.assertEqual(build_contact_sheet(self.source),
                         build_contact_sheet(self.source))

    def test_opt_in_write_cannot_overwrite_sheet(self):
        manifest, png = build_contact_sheet(self.source)
        target = self.folder / "review-only.png"
        save_once(target, manifest, png)
        old = target.read_bytes()
        self.assertEqual(old, png)
        with self.assertRaises(ContactSheetError):
            save_once(target, manifest, png)
        self.assertEqual(target.read_bytes(), old)

    def test_changed_candidate_file_rejected_before_contact_sheet(self):
        png_path = self.source / "preview_Coral_Rescue_home.png"
        before = png_path.read_bytes()
        try:
            png_path.write_bytes(before + b"tampered")
            with self.assertRaises(ValueError):
                build_contact_sheet(self.source)
        finally:
            png_path.write_bytes(before)

    def test_forged_owner_approval_rejected_on_save(self):
        manifest, png = build_contact_sheet(self.source)
        manifest["owner_visual_approval"] = True
        target = self.folder / "forbidden.png"
        with self.assertRaises(ContactSheetError):
            save_once(target, manifest, png)
        self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
