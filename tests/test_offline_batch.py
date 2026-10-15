"""VF-03 offline-batch preflight, write-once candidate and transaction tests."""
from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import hashlib
import io
import json
import struct
import tempfile
import unittest
import zlib
from pathlib import Path
from unittest.mock import patch

from factory.asset_catalog.catalog import AssetCatalog, CatalogError
from factory.asset_generator.offline_batch import (
    BatchError, load_plan, apply_plan, main,
)


def chunk(kind: bytes, payload: bytes) -> bytes:
    return (struct.pack(">I", len(payload)) + kind + payload
            + struct.pack(">I", zlib.crc32(kind + payload) & 0xffffffff))


def tiny_png(rgb=b"\x10\x20\x40\xff") -> bytes:
    raw = b"\x00" + rgb
    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(
        b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")


class OfflineBatchTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.home = Path(temp.name)
        self.root = self.home / "art"
        self.root.mkdir()
        self.store = self.home / "store"
        self.catalog = AssetCatalog(self.store)
        self.catalog.init()
        self.manifest = self.home / "batch.json"
        self.items = []
        self.add("coral/blue.png", "Coral_Rescue", "tile.blue", tiny_png())

    def add(self, relpath, profile, key, data, receipt="local-owner-source"):
        target = self.root / relpath
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        self.items.append({
            "file": relpath, "profile_id": profile, "asset_key": key,
            "rights": "original", "source_receipt": receipt,
            "sha256": hashlib.sha256(data).hexdigest()
        })
        self.write_manifest()
        return target

    def write_manifest(self, **changes):
        data = {"schema_version": 1, "stage": "CANDIDATE_ONLY", "items": self.items}
        data.update(changes)
        self.manifest.write_text(json.dumps(data), encoding="utf-8")

    def plan(self):
        return load_plan(self.manifest, self.root, self.store)[0]

    def apply(self, sha=None):
        return apply_plan(self.manifest, self.root, self.store,
                          self.plan()["plan_sha256"] if sha is None else sha)

    def test_dry_run_never_creates_candidate_or_blob(self):
        preview = self.plan()
        self.assertEqual(preview["stage"], "DRY_RUN_ONLY")
        self.assertEqual(preview["candidate_count"], 1)
        self.assertEqual(preview["catalog_revision_baseline"], 0)
        self.assertFalse((self.store / "blobs").exists())
        self.assertEqual(self.catalog.verify()["verified_revisions"], 0)

    def test_commit_creates_only_unapproved_revisions(self):
        self.add("garage/orange.png", "Garage_Legends", "tile.orange",
                 tiny_png(b"\xaa\xbb\xcc\xff"))
        plan = self.plan()
        result = self.apply(plan["plan_sha256"])
        self.assertEqual(result["candidate_count"], 2)
        self.assertEqual(result["stage"], "CANDIDATES_CREATED_NOT_APPROVED")
        self.assertEqual([i["stage"] for i in result["items"]],
                         ["CANDIDATE_NOT_APPROVED"] * 2)
        self.assertEqual(self.catalog.verify(), {
            "verified_revisions": 2, "active_assets": 0
        })
        self.assertEqual(self.catalog.preview_manifest("Coral_Rescue")["assets"], [])
        self.assertEqual(self.catalog.portfolio_report()["total_verified_revisions"], 2)

    def test_commit_needs_matching_sha_receipt(self):
        with self.assertRaises(BatchError):
            self.apply("0" * 64)
        with self.assertRaises(BatchError):
            apply_plan(self.manifest, self.root, self.store, "")
        self.assertEqual(self.catalog.verify()["verified_revisions"], 0)

    def test_stale_plan_rejects_second_submission(self):
        original = self.plan()["plan_sha256"]
        self.apply(original)
        with self.assertRaises(BatchError):
            self.apply(original)
        self.assertEqual(self.catalog.verify()["verified_revisions"], 1)

    def test_previous_catalog_update_invalidates_plan(self):
        original = self.plan()["plan_sha256"]
        extra = self.add("other.png", "Dino_Islands", "tile.other",
                         tiny_png(b"\x01\x02\x03\xff"))
        self.catalog.ingest(extra, "Dino_Islands", "tile.other", "original", "first")
        self.items.pop()
        self.write_manifest()
        with self.assertRaises(BatchError):
            self.apply(original)
        self.assertEqual(self.catalog.verify()["verified_revisions"], 1)

    def test_source_changes_after_preflight_fail_closed(self):
        original = self.plan()["plan_sha256"]
        (self.root / self.items[0]["file"]).write_bytes(tiny_png(b"\x07\x08\x09\xff"))
        with self.assertRaises(BatchError):
            self.apply(original)
        self.assertEqual(self.catalog.verify()["verified_revisions"], 0)

    def test_invalid_second_source_does_not_partially_write(self):
        self.add("bad.png", "Dino_Islands", "tile.bad", b"not a PNG")
        with self.assertRaises(BatchError):
            self.plan()
        self.assertFalse((self.store / "blobs").exists())
        self.assertEqual(self.catalog.verify()["verified_revisions"], 0)

    def test_database_transaction_rolls_back_if_second_blob_is_tampered(self):
        bad = tiny_png(b"\x99\x77\x55\xff")
        self.add("tamper.png", "Wonder_Pop", "tile.tamper", bad)
        second_sha = hashlib.sha256(bad).hexdigest()
        blob = self.catalog._blob(second_sha)
        blob.parent.mkdir(parents=True, exist_ok=True)
        blob.write_bytes(b"malicious-existing-collision")
        with self.assertRaises(BatchError):
            self.apply()
        self.assertEqual(self.catalog.verify()["verified_revisions"], 0)
        self.assertTrue(blob.exists())  # Never auto-delete existing user files

    def test_duplicate_asset_key_rejected_across_distinct_paths(self):
        self.add("duplicate.png", "Coral_Rescue", "tile.blue",
                 tiny_png(b"\x03\x03\x03\xff"))
        with self.assertRaises(BatchError):
            self.plan()

    def test_same_semantic_key_in_different_games_is_valid(self):
        self.add("second.png", "Garage_Legends", "tile.blue",
                 tiny_png(b"\x03\x03\x03\xff"))
        self.assertEqual(self.plan()["candidate_count"], 2)

    def test_rejects_traversal_drive_backslash_and_absolute_paths(self):
        for invalid in ("../outside.png", "./blue.png", "/tmp/blue.png",
                        "C:/a.png", "coral\\blue.png", "coral//blue.png"):
            with self.subTest(invalid=invalid):
                self.items[0]["file"] = invalid
                self.write_manifest()
                with self.assertRaises(BatchError):
                    self.plan()

    def test_rejects_manifest_extra_fields_and_approval_stage(self):
        for change in ({"stage": "APPROVED"}, {"schema_version": 2},
                       {"extra": True}, {"items": []}):
            with self.subTest(change=change):
                self.write_manifest(**change)
                with self.assertRaises(BatchError):
                    self.plan()

    def test_rejects_bad_profile_rights_receipt_and_hash(self):
        original = self.items[0].copy()
        for change in ({"profile_id": "Other_Game"}, {"profile_id": ["bad"]},
                       {"rights": "unlicensed"}, {"source_receipt": " "},
                       {"sha256": "0" * 64}, {"asset_key": "../escape"}):
            with self.subTest(change=change):
                self.items[0] = {**original, **change}
                self.write_manifest()
                with self.assertRaises((BatchError, CatalogError)):
                    self.plan()

    def test_manifest_without_initialized_store_rejected(self):
        (self.store / "catalog.sqlite3").rename(self.store / "catalog.sqlite3.bak")
        with self.assertRaises(BatchError):
            self.plan()

    def test_simulated_directory_link_rejected_without_windows_privileges(self):
        from factory.asset_generator import offline_batch
        candidate = self.root / "coral"
        actual = offline_batch._reparse
        with patch.object(offline_batch, "_reparse",
                          side_effect=lambda path: path == candidate or actual(path)):
            with self.assertRaises(BatchError):
                self.plan()

    def test_corrupted_png_crc_rejected(self):
        source = self.root / "coral/blue.png"
        broken = bytearray(source.read_bytes())
        broken[20] ^= 1
        source.write_bytes(broken)
        self.items[0]["sha256"] = hashlib.sha256(broken).hexdigest()
        self.write_manifest()
        with self.assertRaises(BatchError):
            self.plan()

    def test_fingerprint_includes_owner_receipt_without_leaking_it(self):
        one = self.plan()
        self.items[0]["source_receipt"] = "different-owner-evidence"
        self.write_manifest()
        two = self.plan()
        self.assertNotEqual(one["plan_sha256"], two["plan_sha256"])
        self.assertNotIn("different-owner-evidence", json.dumps(two))

    def test_cli_dry_run_and_explicit_commit(self):
        argv = ["--manifest", str(self.manifest), "--source-root", str(self.root),
                "--store", str(self.store)]
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(main(argv), 0)
        expected = json.loads(out.getvalue())["plan_sha256"]
        with redirect_stdout(io.StringIO()):
            self.assertEqual(main(argv + ["--commit", "--expected-plan-sha256", expected]), 0)
        self.assertEqual(self.catalog.verify()["verified_revisions"], 1)

    def test_cli_rejects_commit_without_plan_receipt(self):
        argv = ["--manifest", str(self.manifest), "--source-root", str(self.root),
                "--store", str(self.store), "--commit"]
        with redirect_stderr(io.StringIO()):
            self.assertEqual(main(argv), 2)
        self.assertEqual(self.catalog.verify()["verified_revisions"], 0)


if __name__ == "__main__":
    unittest.main()
