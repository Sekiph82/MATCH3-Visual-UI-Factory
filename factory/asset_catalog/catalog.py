"""VF-02 content-addressed asset catalog. Standard library, offline, no art generation.

Approved revisions are append-only approval records. Replacements require explicit
expected active revision and owner receipt; original blobs are never overwritten.
Structural receipts are NOT cryptographic evidence of actual owner approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import struct
import sys
import zlib
from pathlib import Path
from datetime import datetime, timezone

PROFILES = frozenset((
    "Coral_Rescue", "Garage_Legends", "Dino_Islands",
    "The_Fractured_Realms", "Wonder_Pop",
))
KEY_PATTERN = re.compile(r"^[a-z][a-z0-9_.-]{0,99}$")
MAX_FILE_BYTES = 64 * 1024 * 1024
PNG_SIG = b"\x89PNG\r\n\x1a\n"
SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS revisions (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 profile TEXT NOT NULL,
 asset_key TEXT NOT NULL,
 revision INTEGER NOT NULL CHECK(revision > 0),
 sha256 TEXT NOT NULL,
 width INTEGER NOT NULL CHECK(width > 0),
 height INTEGER NOT NULL CHECK(height > 0),
 rights TEXT NOT NULL CHECK(rights IN ('original','licensed')),
 source_receipt TEXT NOT NULL,
 created_utc TEXT NOT NULL,
 UNIQUE(profile, asset_key, revision)
);
CREATE TABLE IF NOT EXISTS approvals (
 revision_id INTEGER PRIMARY KEY REFERENCES revisions(id),
 owner_receipt TEXT NOT NULL,
 replaced_revision_id INTEGER REFERENCES revisions(id),
 approved_utc TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS active (
 profile TEXT NOT NULL,
 asset_key TEXT NOT NULL,
 revision_id INTEGER NOT NULL REFERENCES approvals(revision_id),
 PRIMARY KEY(profile, asset_key)
);
"""

class CatalogError(ValueError):
    pass


def png_dimensions(data: bytes) -> tuple[int, int]:
    """Validate full CRC-filtered/decompressed PNG, not merely 33 header bytes."""
    # Direct catalog CLI execution has the factory subtree on sys.path, not repo root.
    root = str(Path(__file__).resolve().parents[2])
    if root not in sys.path:
        sys.path.insert(0, root)
    from factory.image_processor.png_pipeline import decode_png, ImageError
    try:
        width, height, _ = decode_png(data)
        return width, height
    except ImageError as exc:
        raise CatalogError("invalid/unsupported source PNG: " + str(exc)) from exc


def required_text(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 1024:
        raise CatalogError(name + " required (max 1024 characters)")
    return value.strip()


class AssetCatalog:
    def __init__(self, store: Path):
        self.store = Path(store)
        self.db_path = self.store / "catalog.sqlite3"

    def _connect(self):
        if self.store.is_symlink() or self.db_path.is_symlink():
            raise CatalogError("catalog path must not be a symlink")
        if not self.db_path.is_file():
            raise CatalogError("Catalog missing: run 'init' explicitly")
        con = sqlite3.connect(str(self.db_path), timeout=10)
        con.execute("PRAGMA foreign_keys=ON")
        con.row_factory = sqlite3.Row
        return con

    def init(self):
        if self.store.resolve().is_relative_to(Path(__file__).resolve().parents[2]):
            raise CatalogError("asset store must be outside the GitHub source repository")
        self.store.mkdir(parents=True, exist_ok=True)
        if self.store.is_symlink():
            raise CatalogError("catalog root must not be symlink")
        with sqlite3.connect(str(self.db_path)) as con:
            con.executescript(SCHEMA)

    def _blob(self, digest: str) -> Path:
        blob_root = self.store / "blobs"
        sha_root = blob_root / "sha256"
        prefix_root = sha_root / digest[:2]
        if any(p.is_symlink() for p in (self.store, blob_root, sha_root, prefix_root)):
            raise CatalogError("unsafe content-store symlink")
        return prefix_root / (digest + ".png")

    def ingest(self, source: Path, profile: str, asset_key: str,
               rights: str, source_receipt: str) -> dict:
        if profile not in PROFILES:
            raise CatalogError("unknown game profile")
        if not isinstance(asset_key, str) or not KEY_PATTERN.fullmatch(asset_key):
            raise CatalogError("invalid semantic asset key")
        if rights not in ("original", "licensed"):
            raise CatalogError("must declare original or licensed rights")
        source_receipt = required_text(source_receipt, "source receipt")
        source = Path(source)
        if source.is_symlink() or not source.is_file() or source.suffix.lower() != ".png":
            raise CatalogError("source must be a regular PNG, not a symlink")
        if source.stat().st_size > MAX_FILE_BYTES:
            raise CatalogError("file exceeds 64 MiB intake limit")
        data = source.read_bytes()
        if len(data) > MAX_FILE_BYTES:
            raise CatalogError("file exceeds 64 MiB intake limit")
        width, height = png_dimensions(data)
        # No content-store writes before successful explicit catalog initialization.
        if self.store.is_symlink() or self.db_path.is_symlink() or not self.db_path.is_file():
            raise CatalogError("Catalog missing or unsafe: run 'init' before ingest")
        digest = hashlib.sha256(data).hexdigest()
        dest = self._blob(digest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.is_symlink():
            raise CatalogError("unsafe blob symlink")
        try:
            with dest.open("xb") as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
        except FileExistsError:
            pass
        if dest.is_symlink() or hashlib.sha256(dest.read_bytes()).hexdigest() != digest:
            raise CatalogError("content-addressed blob mismatch; cannot overwrite")
        with self._connect() as con:
            con.execute("BEGIN IMMEDIATE")
            revision = con.execute(
                "SELECT COALESCE(MAX(revision),0)+1 FROM revisions WHERE profile=? AND asset_key=?",
                (profile, asset_key)).fetchone()[0]
            cursor = con.execute(
                """INSERT INTO revisions
                (profile,asset_key,revision,sha256,width,height,rights,source_receipt,created_utc)
                VALUES (?,?,?,?,?,?,?,?,?)""",
                (profile, asset_key, revision, digest, width, height,
                 rights, source_receipt, datetime.now(timezone.utc).isoformat()))
        return {"revision_id": cursor.lastrowid, "revision": revision,
                "profile": profile, "asset_key": asset_key, "sha256": digest,
                "stage": "CANDIDATE"}

    def approve(self, revision_id: int, owner_receipt: str,
                replaces_revision_id: int | None = None) -> dict:
        owner_receipt = required_text(owner_receipt, "owner approval receipt")
        with self._connect() as con:
            con.execute("BEGIN IMMEDIATE")
            revision = con.execute(
                "SELECT * FROM revisions WHERE id=?", (revision_id,)).fetchone()
            if revision is None:
                raise CatalogError("unknown asset revision")
            if con.execute("SELECT 1 FROM approvals WHERE revision_id=?",
                           (revision_id,)).fetchone():
                raise CatalogError("revision already approved")
            blob = self._blob(revision["sha256"])
            if blob.is_symlink() or not blob.is_file() or hashlib.sha256(blob.read_bytes()).hexdigest() != revision["sha256"]:
                raise CatalogError("approved source bytes unavailable or modified")
            active = con.execute(
                "SELECT revision_id FROM active WHERE profile=? AND asset_key=?",
                (revision["profile"], revision["asset_key"])).fetchone()
            current = active["revision_id"] if active else None
            if current != replaces_revision_id:
                raise CatalogError("explicit expected-active revision required; no implicit replacement")
            con.execute(
                "INSERT INTO approvals(revision_id,owner_receipt,replaced_revision_id,approved_utc) VALUES (?,?,?,?)",
                (revision_id, owner_receipt, current, datetime.now(timezone.utc).isoformat()))
            con.execute(
                """INSERT INTO active(profile,asset_key,revision_id) VALUES(?,?,?)
                ON CONFLICT(profile,asset_key) DO UPDATE SET revision_id=excluded.revision_id""",
                (revision["profile"], revision["asset_key"], revision_id))
        return {"active_revision_id": revision_id, "previous_active_revision_id": current}

    def verify(self) -> dict:
        with self._connect() as con:
            rows = con.execute("SELECT id,sha256 FROM revisions ORDER BY id").fetchall()
            active = con.execute(
                """SELECT a.profile, a.asset_key, a.revision_id
                FROM active a LEFT JOIN approvals p ON a.revision_id=p.revision_id
                WHERE p.revision_id IS NULL"""
            ).fetchall()
            if active:
                raise CatalogError("active revision missing approval record")
            for row in rows:
                blob = self._blob(row["sha256"])
                if blob.is_symlink() or not blob.is_file() or hashlib.sha256(blob.read_bytes()).hexdigest() != row["sha256"]:
                    raise CatalogError("missing, unsafe or altered blob for revision " + str(row["id"]))
            return {"verified_revisions": len(rows), "active_assets":
                    con.execute("SELECT COUNT(*) FROM active").fetchone()[0]}

    def preview_manifest(self, profile: str) -> dict:
        if profile not in PROFILES:
            raise CatalogError("unknown game profile")
        self.verify()
        with self._connect() as con:
            rows = con.execute(
                """SELECT r.* FROM revisions r JOIN active a ON a.revision_id=r.id
                WHERE a.profile=? ORDER BY r.asset_key""", (profile,)).fetchall()
        return {
            "schema_version": 1, "profile_id": profile, "theme_version": "0.1.0",
            "engine_sha": "UNPINNED", "level_factory_sha": "UNPINNED",
            "stage": "TEST_ONLY",
            "assets": [
                {"asset_id": profile + "." + row["asset_key"],
                 "path": "sha256/" + row["sha256"][:2] + "/" + row["sha256"] + ".png",
                 "sha256": row["sha256"], "state": "Ready",
                 "rights": row["rights"], "source_receipt": row["source_receipt"]}
                for row in rows
            ],
        }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--store", type=Path, required=True,
                        help="External content-addressed store, outside GitHub working tree")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    ingest = sub.add_parser("ingest")
    ingest.add_argument("--file", required=True, type=Path)
    ingest.add_argument("--profile", required=True, choices=sorted(PROFILES))
    ingest.add_argument("--key", required=True)
    ingest.add_argument("--rights", required=True, choices=["original", "licensed"])
    ingest.add_argument("--source-receipt", required=True)
    approve = sub.add_parser("approve")
    approve.add_argument("--revision-id", required=True, type=int)
    approve.add_argument("--owner-receipt", required=True)
    approve.add_argument("--replaces-revision-id", type=int)
    sub.add_parser("verify")
    preview = sub.add_parser("export-preview")
    preview.add_argument("--profile", required=True, choices=sorted(PROFILES))
    args = parser.parse_args(argv)
    try:
        catalog = AssetCatalog(args.store)
        if args.command == "init":
            catalog.init()
            result = {"status": "initialized", "store": str(args.store)}
        elif args.command == "ingest":
            result = catalog.ingest(args.file, args.profile, args.key,
                                    args.rights, args.source_receipt)
        elif args.command == "approve":
            result = catalog.approve(args.revision_id, args.owner_receipt,
                                     args.replaces_revision_id)
        elif args.command == "verify":
            result = catalog.verify()
        else:
            result = catalog.preview_manifest(args.profile)
        print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
        return 0
    except (CatalogError, OSError, sqlite3.Error) as exc:
        print("VUF_CATALOG_REJECTED: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
