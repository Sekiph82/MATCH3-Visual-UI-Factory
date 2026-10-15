import copy
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Tools"))
from validate_manifest import validate_manifest, main  # noqa: E402


def fixture():
    return {
        "schema_version": 1,
        "profile_id": "Coral_Rescue",
        "theme_version": "0.1.0",
        "engine_sha": "UNPINNED",
        "level_factory_sha": "UNPINNED",
        "stage": "TEST_ONLY",
        "assets": [],
    }


def entry(path="original/tile.png"):
    return {
        "asset_id": "Coral_Rescue.tile_01",
        "path": path,
        "sha256": hashlib.sha256(b"sample").hexdigest(),
        "state": "Ready",
        "rights": "original",
        "source_receipt": "owner_source_pending_review",
    }


class ManifestTests(unittest.TestCase):
    def test_empty_preview_manifest_allowed(self):
        validate_manifest(fixture())

    def test_five_profiles_valid_for_test_only(self):
        for profile in (
            "Coral_Rescue", "Garage_Legends", "Dino_Islands",
            "The_Fractured_Realms", "Wonder_Pop"
        ):
            x = fixture()
            x["profile_id"] = profile
            validate_manifest(x)

    def assert_rejected(self, update):
        x = fixture()
        update(x)
        with self.assertRaises(ValueError):
            validate_manifest(x)

    def test_reject_unrecognized_profile(self):
        self.assert_rejected(lambda x: x.update(profile_id="Unknown"))

    def test_reject_bool_schema_version(self):
        self.assert_rejected(lambda x: x.update(schema_version=True))

    def test_reject_unknown_state(self):
        self.assert_rejected(lambda x: x["assets"].append({**entry(), "state": "Awarded"}))

    def test_reject_theme_leak(self):
        self.assert_rejected(lambda x: x["assets"].append({**entry(), "asset_id": "Wonder_Pop.tile_01"}))

    def test_reject_traversal_and_windows_path(self):
        for path in ("../foo.png", "assets/../../bad.png", "C:/bad.png",
                     "assets\\bad.png", "/tmp/art.png"):
            self.assert_rejected(lambda x, p=path: x["assets"].append(entry(p)))

    def test_reject_noncanonical_and_windows_device_paths(self):
        for path in ("original/./tile.png", "original//tile.png",
                     "original/tile.png ", "CON.png", "assets/LPT1.png"):
            self.assert_rejected(lambda x, p=path: x["assets"].append(entry(p)))

    def test_reject_duplicate_ids(self):
        self.assert_rejected(lambda x: x["assets"].extend([entry(), entry("original/other.png")]))

    def test_reject_duplicate_paths(self):
        self.assert_rejected(lambda x: x["assets"].extend([
            entry(), {**entry(), "asset_id": "Coral_Rescue.tile_02"},
        ]))

    def test_reject_bogus_sha(self):
        self.assert_rejected(lambda x: x["assets"].append({**entry(), "sha256": "0" * 10}))

    def test_reject_unknown_rights(self):
        self.assert_rejected(lambda x: x["assets"].append({**entry(), "rights": "internet"}))

    def test_reject_unpinned_approval(self):
        self.assert_rejected(lambda x: x.update(stage="APPROVED", owner_approval_receipt="owner"))

    def test_reject_approved_placeholder(self):
        def update(x):
            x["stage"] = "APPROVED"
            x["engine_sha"] = "a" * 40
            x["level_factory_sha"] = "b" * 40
            x["owner_approval_receipt"] = "recorded-owner-decision"
            x["assets"] = [{**entry(), "rights": "placeholder"}]
        self.assert_rejected(update)

    def test_reject_fake_owner_receipt_before_approval(self):
        self.assert_rejected(lambda x: x.update(owner_approval_receipt="fake"))

    def test_source_hash_positive_and_negative(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "original").mkdir()
            (root / "original" / "tile.png").write_bytes(b"sample")
            x = fixture()
            x["assets"].append(entry())
            validate_manifest(x, root)
            (root / "original" / "tile.png").write_bytes(b"changed")
            with self.assertRaises(ValueError):
                validate_manifest(x, root)

    def test_symlink_escape_is_rejected(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base) / "source"
            root.mkdir()
            outside = Path(base) / "outside.png"
            outside.write_bytes(b"sample")
            folder = root / "original"
            folder.mkdir()
            try:
                (folder / "tile.png").symlink_to(outside)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable")
            x = fixture()
            x["assets"].append(entry())
            with self.assertRaises(ValueError):
                validate_manifest(x, root)

    def test_cli_bad_missing_file_returns_nonzero(self):
        self.assertEqual(main(["does-not-exist-vuf.json"]), 2)


if __name__ == "__main__":
    unittest.main()
