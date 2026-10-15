"""VF-02 controls: original bytes, candidate isolation, explicit replacement and replay."""
from __future__ import annotations

import hashlib
import json
import sqlite3
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "factory" / "asset_catalog"))
from catalog import AssetCatalog, CatalogError, png_dimensions, main


def _chunk(name: bytes, data: bytes) -> bytes:
    return (struct.pack(">I", len(data)) + name + data +
            struct.pack(">I", zlib.crc32(name + data) & 0xffffffff))


def sample_png(color=b"\x09\x31\x99\xff", width=1, height=1) -> bytes:
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    raw_scanline = b"\x00" + color * width
    compressed = zlib.compress(raw_scanline * height)
    return (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr) +
            _chunk(b"IDAT", compressed) + _chunk(b"IEND", b""))


class AssetCatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.store = root / "external-store"
        self.source = root / "test-original.png"
        self.source.write_bytes(sample_png())
        self.catalog = AssetCatalog(self.store)
        self.catalog.init()

    def ingest(self, color=None, game="Coral_Rescue", key="tile.star"):
        if color:
            self.source.write_bytes(sample_png(color))
        return self.catalog.ingest(self.source, game, key, "original", "source-test-fixture")

    def test_real_png_ihdr_accepts(self):
        self.assertEqual(png_dimensions(sample_png()), (1, 1))

    def test_corrupt_png_crc_rejected(self):
        bad = bytearray(sample_png())
        bad[20] ^= 1
        with self.assertRaises(CatalogError):
            png_dimensions(bytes(bad))

    def test_invalid_png_and_dimension_bounds_rejected(self):
        with self.assertRaises(CatalogError):
            png_dimensions(b"not a png")
        with self.assertRaises(CatalogError):
            png_dimensions(sample_png(width=9000))

    def test_first_candidate_and_manual_owner_approval(self):
        candidate = self.ingest()
        self.assertEqual(candidate["stage"], "CANDIDATE")
        self.assertEqual(self.catalog.verify()["active_assets"], 0)
        self.assertEqual(self.catalog.preview_manifest("Coral_Rescue")["assets"], [])
        approval = self.catalog.approve(candidate["revision_id"], "owner-test-approval")
        self.assertIsNone(approval["previous_active_revision_id"])
        manifest = self.catalog.preview_manifest("Coral_Rescue")
        self.assertEqual(manifest["stage"], "TEST_ONLY")
        self.assertEqual(len(manifest["assets"]), 1)
        self.assertEqual(manifest["assets"][0]["sha256"], candidate["sha256"])
        self.assertEqual(self.catalog.verify()["verified_revisions"], 1)

    def test_approved_asset_never_silently_replaced(self):
        v1 = self.ingest()
        self.catalog.approve(v1["revision_id"], "owner-v1")
        v2 = self.ingest(b"\x05\x22\x77\xff")
        with self.assertRaises(CatalogError):
            self.catalog.approve(v2["revision_id"], "owner-v2")
        with self.assertRaises(CatalogError):
            self.catalog.approve(v2["revision_id"], "owner-v2", replaces_revision_id=987)
        manifest = self.catalog.preview_manifest("Coral_Rescue")
        self.assertEqual(manifest["assets"][0]["sha256"], v1["sha256"])
        self.catalog.approve(v2["revision_id"], "owner-v2-explicit", v1["revision_id"])
        updated = self.catalog.preview_manifest("Coral_Rescue")
        self.assertEqual(updated["assets"][0]["sha256"], v2["sha256"])
        with sqlite3.connect(self.catalog.db_path) as con:
            self.assertEqual(con.execute("SELECT COUNT(*) FROM approvals").fetchone()[0], 2)
        self.assertTrue(self.catalog._blob(v1["sha256"]).exists())

    def test_duplicate_approval_rejected(self):
        first = self.ingest()
        self.catalog.approve(first["revision_id"], "first")
        with self.assertRaises(CatalogError):
            self.catalog.approve(first["revision_id"], "again", first["revision_id"])

    def test_source_and_blob_mutation_rejected(self):
        result = self.ingest()
        self.catalog.approve(result["revision_id"], "owner")
        blob = self.catalog._blob(result["sha256"])
        blob.write_bytes(b"tampered")
        with self.assertRaises(CatalogError):
            self.catalog.verify()
        with self.assertRaises(CatalogError):
            self.catalog.preview_manifest("Coral_Rescue")

    def test_wrong_profile_and_key_are_rejected(self):
        for profile, key in (
            ("WrongGame", "tile.star"), ("Wonder Pop", "tile.star"),
            ("Coral_Rescue", "../escape"), ("Coral_Rescue", "UPPERCASE"),
        ):
            with self.assertRaises(CatalogError):
                self.catalog.ingest(self.source, profile, key, "original", "receipt")

    def test_license_receipts_mandatory(self):
        for rights, receipt in (("unknown", "receipt"), ("original", ""),
                                ("claimed", "anything")):
            with self.assertRaises(CatalogError):
                self.catalog.ingest(self.source, "Coral_Rescue", "tile.star", rights, receipt)

    def test_source_symlink_rejected(self):
        link = Path(self.temp.name) / "linked.png"
        try:
            link.symlink_to(self.source)
        except (OSError, NotImplementedError):
            self.skipTest("symbolic links unavailable")
        with self.assertRaises(CatalogError):
            self.catalog.ingest(link, "Coral_Rescue", "tile.star", "original", "receipt")

    def test_uninitialized_catalog_fails_closed(self):
        with self.assertRaises(CatalogError):
            AssetCatalog(Path(self.temp.name) / "missing").verify()

    def test_isolation_of_five_profiles(self):
        for profile in sorted(self.catalog.preview_manifest("Coral_Rescue")["profile_id"] for _ in range(1)):
            self.assertEqual(profile, "Coral_Rescue")
        versions = []
        for profile in ("Coral_Rescue", "Garage_Legends", "Dino_Islands",
                        "The_Fractured_Realms", "Wonder_Pop"):
            versions.append(self.ingest(game=profile))
        for version in versions:
            self.catalog.approve(version["revision_id"], "test-owner")
        for profile in ("Coral_Rescue", "Garage_Legends", "Dino_Islands",
                        "The_Fractured_Realms", "Wonder_Pop"):
            manifest = self.catalog.preview_manifest(profile)
            self.assertEqual(len(manifest["assets"]), 1)
            self.assertTrue(manifest["assets"][0]["asset_id"].startswith(profile + "."))

    def test_invalid_idat_crc_fails_without_catalog_pollution(self):
        broken = bytearray(sample_png())
        broken[50] ^= 1
        self.source.write_bytes(broken)
        with self.assertRaises(CatalogError):
            self.ingest()
        self.assertEqual(self.catalog.verify()["verified_revisions"], 0)

    def test_uninitialized_catalog_ingest_creates_no_blob(self):
        fresh = AssetCatalog(Path(self.temp.name) / "new-uninitialized")
        with self.assertRaises(CatalogError):
            fresh.ingest(self.source, "Coral_Rescue", "tile.star", "original", "receipt")
        self.assertFalse((fresh.store / "blobs").exists())

    def test_rollback_to_previously_approved_revision(self):
        v1 = self.ingest()
        self.catalog.approve(v1["revision_id"], "owner-accept-v1")
        v2 = self.ingest(b"\\x19\\x22\\x33\\xff")
        self.catalog.approve(v2["revision_id"], "owner-accept-v2", v1["revision_id"])
        restored = self.catalog.rollback(v1["revision_id"], v2["revision_id"], "owner-restore-v1")
        self.assertEqual(restored["active_revision_id"], v1["revision_id"])
        self.assertEqual(self.catalog.preview_manifest("Coral_Rescue")["assets"][0]["sha256"],
                         v1["sha256"])
        self.assertTrue(self.catalog._blob(v2["sha256"]).is_file())
        history = self.catalog.history("Coral_Rescue", "tile.star")
        self.assertEqual(len(history["revisions"]), 2)
        self.assertEqual(len(history["restorations"]), 1)
        self.assertEqual(history["restorations"][0]["to_revision_id"], v1["revision_id"])

    def test_rollback_wrong_expected_active_fails_closed(self):
        v1 = self.ingest()
        self.catalog.approve(v1["revision_id"], "owner-accept-v1")
        v2 = self.ingest(b"\\x19\\x22\\x33\\xff")
        self.catalog.approve(v2["revision_id"], "owner-accept-v2", v1["revision_id"])
        with self.assertRaises(CatalogError):
            self.catalog.rollback(v1["revision_id"], v1["revision_id"], "stale-receipt")
        with self.assertRaises(CatalogError):
            self.catalog.rollback(v1["revision_id"], 999, "stale-receipt")
        self.assertEqual(self.catalog.history("Coral_Rescue", "tile.star")["restorations"], [])
        self.assertEqual(self.catalog.history("Coral_Rescue", "tile.star")["active_revision_id"],
                         v2["revision_id"])

    def test_rollback_unapproved_candidate_is_rejected(self):
        v1 = self.ingest()
        self.catalog.approve(v1["revision_id"], "owner-v1")
        v2 = self.ingest(b"\\x19\\x22\\x33\\xff")
        with self.assertRaises(CatalogError):
            self.catalog.rollback(v2["revision_id"], v1["revision_id"], "owner-v2")
        self.assertEqual(self.catalog.verify()["active_assets"], 1)

    def test_rollback_preserves_profile_and_asset_isolation(self):
        v1 = self.ingest()
        self.catalog.approve(v1["revision_id"], "owner-v1")
        other = self.ingest(game="Garage_Legends")
        self.catalog.approve(other["revision_id"], "garage-owner")
        with self.assertRaises(CatalogError):
            self.catalog.rollback(other["revision_id"], v1["revision_id"], "wrong-owner")
        self.assertEqual(self.catalog.history("Garage_Legends", "tile.star")["restorations"], [])

    def test_revision_and_approval_history_are_sqlite_append_only(self):
        revision = self.ingest()
        self.catalog.approve(revision["revision_id"], "owner-v1")
        with sqlite3.connect(self.catalog.db_path) as con:
            with self.assertRaises(sqlite3.IntegrityError):
                con.execute("UPDATE revisions SET rights='licensed' WHERE id=?",
                            (revision["revision_id"],))
            with self.assertRaises(sqlite3.IntegrityError):
                con.execute("DELETE FROM approvals WHERE revision_id=?",
                            (revision["revision_id"],))
        self.assertEqual(self.catalog.verify()["verified_revisions"], 1)

    def test_restoration_events_are_sqlite_append_only(self):
        v1 = self.ingest()
        self.catalog.approve(v1["revision_id"], "owner-v1")
        v2 = self.ingest(b"\\x19\\x22\\x33\\xff")
        self.catalog.approve(v2["revision_id"], "owner-v2", v1["revision_id"])
        self.catalog.rollback(v1["revision_id"], v2["revision_id"], "owner-restore")
        with sqlite3.connect(self.catalog.db_path) as con:
            with self.assertRaises(sqlite3.IntegrityError):
                con.execute("DELETE FROM restorations")
            with self.assertRaises(sqlite3.IntegrityError):
                con.execute("UPDATE restorations SET owner_receipt='fake'")

    def test_rollback_rejects_modified_target_bytes(self):
        v1 = self.ingest()
        self.catalog.approve(v1["revision_id"], "owner-v1")
        v2 = self.ingest(b"\\x19\\x22\\x33\\xff")
        self.catalog.approve(v2["revision_id"], "owner-v2", v1["revision_id"])
        self.catalog._blob(v1["sha256"]).write_bytes(b"corrupt")
        with self.assertRaises(CatalogError):
            self.catalog.rollback(v1["revision_id"], v2["revision_id"], "owner-restore")

    def test_history_wrong_profile_and_key_rejected(self):
        with self.assertRaises(CatalogError):
            self.catalog.history("nonexistent", "tile.star")
        with self.assertRaises(CatalogError):
            self.catalog.history("Coral_Rescue", "../escape")

    def test_portfolio_report_lists_all_five_without_approving(self):
        report = self.catalog.portfolio_report()
        self.assertEqual(report["stage"], "READ_ONLY_NOT_OWNER_APPROVAL")
        self.assertEqual(len(report["profiles"]), 5)
        self.assertEqual(report["total_verified_revisions"], 0)
        self.assertTrue(all(p["pending_review_count"] == 0 for p in report["profiles"]))

    def test_portfolio_report_keeps_candidate_and_approval_counts_separate(self):
        v1 = self.ingest()
        report = self.catalog.portfolio_report()
        coral = next(p for p in report["profiles"] if p["profile_id"] == "Coral_Rescue")
        self.assertEqual(coral["pending_review_count"], 1)
        self.assertEqual(coral["active_asset_count"], 0)
        self.assertEqual(coral["pending_preview"][0]["id"], v1["revision_id"])
        self.catalog.approve(v1["revision_id"], "human-reviewed")
        v2 = self.ingest(b"\\x44\\x55\\x66\\xff")
        report = self.catalog.portfolio_report()
        coral = next(p for p in report["profiles"] if p["profile_id"] == "Coral_Rescue")
        self.assertEqual(coral["pending_review_count"], 1)
        self.assertEqual(coral["approval_receipts_count"], 1)
        self.assertEqual(coral["active_asset_count"], 1)
        self.assertEqual(coral["revision_count"], 2)

    def test_portfolio_report_rejects_corrupted_store_bytes(self):
        v1 = self.ingest()
        self.catalog._blob(v1["sha256"]).write_bytes(b"corrupted")
        with self.assertRaises(CatalogError):
            self.catalog.portfolio_report()

    def test_portfolio_cli_writes_utf8_json_without_overwriting(self):
        external = Path(self.temp.name) / "portfolio_read_only.json"
        args = ["--store", str(self.store), "portfolio-report",
                "--output-file", str(external)]
        self.assertEqual(main(args), 0)
        raw = external.read_bytes()
        report = json.loads(raw.decode("utf-8"))
        self.assertEqual(report["stage"], "READ_ONLY_NOT_OWNER_APPROVAL")
        self.assertEqual(len(report["profiles"]), 5)
        self.assertEqual(main(args), 2)
        self.assertEqual(external.read_bytes(), raw)

    def test_cli_initializes_and_verifies(self):
        with tempfile.TemporaryDirectory() as folder:
            store = Path(folder) / "new"
            self.assertEqual(main(["--store", str(store), "init"]), 0)
            self.assertEqual(main(["--store", str(store), "verify"]), 0)

    def test_cli_missing_catalog_nonzero(self):
        bad_store = Path(self.temp.name) / "missing"
        self.assertEqual(main(["--store", str(bad_store), "verify"]), 2)


if __name__ == "__main__":
    unittest.main()
