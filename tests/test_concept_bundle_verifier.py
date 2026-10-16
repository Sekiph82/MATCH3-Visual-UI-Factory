"""R30 independent fifteen-image concept bundle byte verification."""
from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path

from factory.ui_composer.concept_showcase import build_showcase, write_showcase
from factory.validators.verify_generated_kits import BundleError, verify_showcase


class ConceptBundleVerifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.folder = Path(cls.temp.name) / "batch"
        receipt, files = build_showcase(scale=1, seed=3)
        write_showcase(cls.folder, receipt, files)
        cls.original_manifest = (cls.folder / "showcase_manifest.json").read_bytes()
        cls.original_screen = (cls.folder / "preview_Coral_Rescue_home.png").read_bytes()

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def tearDown(self):
        (self.folder / "showcase_manifest.json").write_bytes(self.original_manifest)
        (self.folder / "preview_Coral_Rescue_home.png").write_bytes(
            self.original_screen)

    def test_all_fifteen_bytes_and_pngs_verified(self):
        result = verify_showcase(self.folder)
        self.assertEqual(result["kind"], "showcase")
        self.assertEqual(result["screen_count"], 15)
        self.assertEqual(result["profile_count"], 5)
        self.assertFalse(result["visual_approved"])
        self.assertFalse(result["interactive_ui_enabled"])

    def test_corrupted_original_image_rejected(self):
        path = self.folder / "preview_Coral_Rescue_home.png"
        image = bytearray(path.read_bytes())
        image[-20] ^= 3
        path.write_bytes(image)
        with self.assertRaises(BundleError):
            verify_showcase(self.folder)

    def test_image_sha_forgery_rejected(self):
        path = self.folder / "showcase_manifest.json"
        receipt = json.loads(path.read_text())
        receipt["screens"][0]["png_sha256"] = "f" * 64
        path.write_text(json.dumps(receipt))
        with self.assertRaises(BundleError):
            verify_showcase(self.folder)

    def test_swapped_screens_rejected(self):
        path = self.folder / "showcase_manifest.json"
        receipt = json.loads(path.read_text())
        receipt["screens"][2], receipt["screens"][3] = (
            receipt["screens"][3], receipt["screens"][2])
        path.write_text(json.dumps(receipt))
        with self.assertRaises(BundleError):
            verify_showcase(self.folder)

    def test_forged_approval_or_live_ui_rejected(self):
        path = self.folder / "showcase_manifest.json"
        for key in ("asset_rights_verified", "real_device_verified",
                    "owner_visual_approval", "interactive_ui_enabled"):
            receipt = json.loads(self.original_manifest)
            receipt[key] = True
            path.write_text(json.dumps(receipt))
            with self.subTest(key=key), self.assertRaises(BundleError):
                verify_showcase(self.folder)

    def test_duplicate_manifest_json_field_rejected(self):
        path = self.folder / "showcase_manifest.json"
        path.write_text('{"schema_version":1,"schema_version":1}')
        with self.assertRaises(BundleError):
            verify_showcase(self.folder)

    def test_unexpected_scale_rejected(self):
        path = self.folder / "showcase_manifest.json"
        receipt = json.loads(self.original_manifest)
        receipt["screens"][0]["render_scale"] = 3
        path.write_text(json.dumps(receipt))
        with self.assertRaises(BundleError):
            verify_showcase(self.folder)


if __name__ == "__main__":
    unittest.main()
