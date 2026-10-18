"""M08 milestone real candidate pack unit negatives; source only until Codex."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from factory.asset_packaging.candidate_pack import (
    PACK_GENERATOR, STAGE, CandidatePackError, build_pack, export_pack,
    verify_pack,
)
from factory.image_processor.png_pipeline import decode_png


class M08CandidatePackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest, cls.files, cls.receipt = build_pack("Wonder_Pop")

    def test_one_whole_game_pack_includes_real_images_scene_sprite_and_fx(self):
        m, files, receipt = self.manifest, self.files, self.receipt
        self.assertEqual(m["stage"], STAGE)
        self.assertEqual(receipt["generator"], PACK_GENERATOR)
        self.assertEqual(receipt["scenes"], 3)
        self.assertEqual(receipt["sprite_prototypes"], 38)
        self.assertEqual(receipt["fx_presets"], 5)
        self.assertEqual(len(m["assets"]), 57)
        self.assertFalse(receipt["release_allowed"])
        self.assertFalse(receipt["real_engine_lfx_sha_pinned"])
        self.assertEqual(m["engine_sha"], "UNPINNED_TEST_ONLY")
        self.assertEqual(m["level_factory_sha"], "UNPINNED_TEST_ONLY")
        verify_pack(m, files, receipt)

    def test_all_manifest_images_are_verified_real_rgba_pngs(self):
        for row in self.manifest["assets"]:
            with self.subTest(asset=row["asset_id"]):
                raw = self.files[row["path"]]
                self.assertEqual(hashlib.sha256(raw).hexdigest(), row["sha256"])
                w, h, rgba = decode_png(raw)
                self.assertGreater(w, 0)
                self.assertGreater(h, 0)
                self.assertTrue(any(rgba[3::4]))
                self.assertEqual(row["rights"], "REVIEW_PENDING")
                self.assertEqual(row["state"], "CANDIDATE")

    def test_draft_locales_are_not_real_game_translation_contracts(self):
        for locale in ("en", "tr"):
            row = json.loads(self.files["locales/" + locale + ".json"])
            self.assertEqual(row["stage"], "DRAFT_NOT_LOCALIZATION_APPROVED")
            self.assertFalse(row["release_allowed"])
            self.assertFalse(row["actual_gameplay_labels_verified"])
        self.assertNotEqual(
            self.files["locales/en.json"], self.files["locales/tr.json"])

    def test_corrupted_source_and_missing_locale_rejected(self):
        files = self.files.copy()
        name = self.manifest["assets"][0]["path"]
        files[name] = files[name][:-2] + b"ZZ"
        with self.assertRaises(CandidatePackError):
            verify_pack(self.manifest, files, self.receipt)
        files = self.files.copy()
        files.pop("locales/tr.json")
        with self.assertRaises(CandidatePackError):
            verify_pack(self.manifest, files, self.receipt)

    def test_duplicate_id_bad_path_and_fake_rights_fail_closed(self):
        for field, value in (
            ("asset_id", self.manifest["assets"][0]["asset_id"]),
            ("path", "../owner/private.png"),
            ("rights", "OWNER_APPROVED"),
            ("state", "SHIPPING"),
        ):
            bad = copy.deepcopy(self.manifest)
            bad["assets"][1][field] = value
            with self.subTest(field=field), self.assertRaises(CandidatePackError):
                verify_pack(bad, self.files, self.receipt)

    def test_receipt_cannot_self_approve_or_claim_final_engine_shas(self):
        for field in ("rights_approved", "owner_visual_approved",
                      "device_gpu_approved", "real_engine_lfx_sha_pinned",
                      "actual_game_actions", "release_allowed"):
            forged = dict(self.receipt)
            forged[field] = True
            with self.subTest(field=field), self.assertRaises(CandidatePackError):
                verify_pack(self.manifest, self.files, forged)
        forged = copy.deepcopy(self.manifest)
        forged["engine_sha"] = "f" * 40
        with self.assertRaises(CandidatePackError):
            verify_pack(forged, self.files, self.receipt)

    def test_real_vf04_atlas_export_no_overwrite_and_hash_receipt(self):
        with tempfile.TemporaryDirectory(prefix="vuf_m08_pack_") as parent:
            destination = Path(parent) / "review_candidate"
            receipt = export_pack("Wonder_Pop", destination)
            self.assertFalse(receipt["release_allowed"])
            self.assertEqual(receipt["image_count"], 58)
            self.assertTrue((destination / "sprite_atlas/atlas.png").is_file())
            self.assertTrue((destination / "sprite_atlas/atlas_manifest.json").is_file())
            manifest = json.loads((destination / "visual_manifest.json").read_text())
            self.assertEqual(len(manifest["assets"]), 58)
            for rel, digest in receipt["file_sha256"].items():
                self.assertEqual(
                    hashlib.sha256((destination / rel).read_bytes()).hexdigest(),
                    digest)
            with self.assertRaises(CandidatePackError):
                export_pack("Wonder_Pop", destination)

    def test_illegal_theme_and_implicit_write_not_possible(self):
        with self.assertRaises(CandidatePackError):
            build_pack("../Coral_Rescue")
        self.assertTrue(all(
            isinstance(value, bytes) and len(value) > 0
            for value in self.files.values()
        ))
        self.assertNotIn("release_allowed", self.manifest)


if __name__ == "__main__":
    unittest.main()
