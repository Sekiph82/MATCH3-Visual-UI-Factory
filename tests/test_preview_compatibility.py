"""R45 read-only M08 compatibility and rollback-diff source tests."""
import json
import tempfile
import unittest
from pathlib import Path

from factory.export_pipeline.preview_compatibility import (
    CompatibilityError, inspect_compatibility,
)

ENGINE = "a" * 40
LEVEL_FACTORY = "b" * 40
PROFILE = "Coral_Rescue"


class PreviewCompatibilityTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.folder = Path(temp.name)
        self.path = self.folder / "latest.json"
        self.create()

    def create(self, assets=None, profile=PROFILE, stage="CANDIDATE",
               engine=ENGINE, level_factory=LEVEL_FACTORY):
        doc = {
            "schema_version": 1,
            "profile_id": profile,
            "theme_version": "0.1.0",
            "engine_sha": engine,
            "level_factory_sha": level_factory,
            "stage": stage,
            "assets": assets if assets is not None else []
        }
        self.path.write_text(json.dumps(doc), encoding="utf-8")
        return doc

    @staticmethod
    def asset(name, digest="c" * 64):
        return {
            "asset_id": PROFILE + "." + name,
            "path": "art/" + name + ".png",
            "sha256": digest,
            "state": "Ready",
            "rights": "placeholder",
            "source_receipt": "owner review pending"
        }

    def test_matching_pins_never_imply_production_approval(self):
        report = inspect_compatibility(self.path, PROFILE, ENGINE, LEVEL_FACTORY)
        self.assertTrue(report["upstream_pins_exactly_match"])
        self.assertFalse(report["release_allowed"])
        self.assertFalse(report["original_rights_verified"])
        self.assertFalse(report["asset_file_bytes_reverified"])
        self.assertEqual(report["status"], "MECHANICAL_PREVIEW_ONLY")

    def test_unknown_sha_or_profile_rejected(self):
        for sha in ("UNPINNED", "f" * 39, "g" * 40, "F" * 40):
            with self.subTest(sha=sha), self.assertRaises(CompatibilityError):
                inspect_compatibility(self.path, PROFILE, sha, LEVEL_FACTORY)
        with self.assertRaises(CompatibilityError):
            inspect_compatibility(self.path, "WrongGame", ENGINE, LEVEL_FACTORY)

    def test_pin_mismatch_shows_exactly_which_sources_differ(self):
        self.create(engine="d" * 40)
        report = inspect_compatibility(self.path, PROFILE, ENGINE, LEVEL_FACTORY)
        self.assertEqual(report["pin_mismatches"], ["engine_sha"])
        self.assertFalse(report["upstream_pins_exactly_match"])

    def test_reject_cross_theme_manifest(self):
        self.create(profile="Wonder_Pop")
        with self.assertRaises(CompatibilityError):
            inspect_compatibility(self.path, PROFILE, ENGINE, LEVEL_FACTORY)

    def test_duplicate_json_fields_rejected_not_silently_last_wins(self):
        self.path.write_text('{"schema_version":1,"schema_version":1}')
        with self.assertRaises(CompatibilityError):
            inspect_compatibility(self.path, PROFILE, ENGINE, LEVEL_FACTORY)

    def test_reject_forged_approved_stage(self):
        doc = self.create(assets=[self.asset("reef")], stage="APPROVED")
        doc["owner_approval_receipt"] = "not an actual owner signature"
        self.path.write_text(json.dumps(doc))
        with self.assertRaises(CompatibilityError):
            inspect_compatibility(self.path, PROFILE, ENGINE, LEVEL_FACTORY)

    def test_preview_rollback_diff_is_not_an_executable_rollback(self):
        self.create(assets=[self.asset("bubble"), self.asset("star")])
        old = self.folder / "before.json"
        old.write_bytes(self.path.read_bytes())
        self.create(assets=[self.asset("star", "e" * 64), self.asset("fish")])
        now = self.path.read_bytes()
        previous = old.read_bytes()
        report = inspect_compatibility(
            self.path, PROFILE, ENGINE, LEVEL_FACTORY, old)
        self.assertTrue(report["rollback"]["previous_manifest_present"])
        self.assertFalse(report["rollback"]["previous_release_available"])
        self.assertFalse(report["rollback"]["previous_assets_reverified"])
        changes = {a["asset_id"]: a["change"]
                   for a in report["rollback"]["asset_differences"]}
        self.assertEqual(changes[PROFILE + ".bubble"], "REMOVED")
        self.assertEqual(changes[PROFILE + ".star"], "CHANGED")
        self.assertEqual(changes[PROFILE + ".fish"], "ADDED")
        self.assertEqual(self.path.read_bytes(), now)
        self.assertEqual(old.read_bytes(), previous)

    def test_previous_theme_must_match_candidate(self):
        self.create()
        old = self.folder / "before.json"
        former = json.loads(self.path.read_text())
        former["profile_id"] = "Wonder_Pop"
        old.write_text(json.dumps(former))
        with self.assertRaises(CompatibilityError):
            inspect_compatibility(self.path, PROFILE, ENGINE, LEVEL_FACTORY, old)

    def test_invalid_asset_traversal_and_duplicate_keys_fail_closed(self):
        for assets in (
            [self.asset("../unsafe")],
            [self.asset("a"), self.asset("a")]
        ):
            with self.subTest(assets=assets), self.assertRaises(CompatibilityError):
                self.create(assets=assets)
                inspect_compatibility(self.path, PROFILE, ENGINE, LEVEL_FACTORY)

    def test_absent_manifest_rejected(self):
        self.path.unlink()
        with self.assertRaises(CompatibilityError):
            inspect_compatibility(self.path, PROFILE, ENGINE, LEVEL_FACTORY)


if __name__ == "__main__":
    unittest.main()
