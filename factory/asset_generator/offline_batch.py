"""VF-03: consent-driven offline, write-once batch import into VF-02 candidates.

Python stdlib only. DRY RUN is the default and never changes catalog state.
The --commit path requires a matching SHA-256 plan receipt and a catalog that
was separately initialized. No network, API costs, approval, or game publishing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from factory.asset_catalog.catalog import (
    AssetCatalog, CatalogError, PROFILES, KEY_PATTERN,
    MAX_FILE_BYTES, png_dimensions, required_text,
)
MAX_MANIFEST_BYTES = 512 * 1024
MAX_BATCH_BYTES = 64 * 1024 * 1024
MAX_ITEMS = 64
HEX_SHA256 = re.compile(r"^[0-9a-f]{64}$")
MANIFEST_KEYS = frozenset(("schema_version", "stage", "items"))
ITEM_KEYS = frozenset(("file", "profile_id", "asset_key", "rights",
                       "source_receipt", "sha256"))


class BatchError(ValueError):
    pass


def _reparse(path: Path) -> bool:
    if path.is_symlink():
        return True
    if hasattr(path, "is_junction") and path.is_junction():
        return True
    try:
        info = path.stat(follow_symlinks=False)
    except OSError as exc:
        raise BatchError("cannot inspect source path: " + str(exc)) from exc
    return bool(getattr(info, "st_file_attributes", 0)
                & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def _outside_checkout(folder: Path, field: str) -> Path:
    if not folder.is_dir() or _reparse(folder):
        raise BatchError(field + " must be an existing real directory")
    canonical = folder.resolve(strict=True)
    if canonical.is_relative_to(ROOT):
        raise BatchError(field + " must be outside the Git source checkout")
    return canonical


def _safe_source(root: Path, relative: str) -> Path:
    if (not isinstance(relative, str) or not relative or len(relative) > 255
            or "\\" in relative or ":" in relative
            or relative.startswith("/") or "\x00" in relative):
        raise BatchError("invalid portable relative PNG path")
    pieces = relative.split("/")
    if any(p in ("", ".", "..") for p in pieces):
        raise BatchError("source path traversal/empty component rejected")
    pure = PurePosixPath(relative)
    if pure.suffix.lower() != ".png":
        raise BatchError("offline batch accepts only original PNG sources")
    current = root
    for part in pieces:
        current = current / part
        if not current.exists() and not current.is_symlink():
            raise BatchError("source file/directory does not exist")
        if _reparse(current):
            raise BatchError("linked source component rejected")
    if not current.is_file() or not current.resolve(strict=True).is_relative_to(root):
        raise BatchError("source is not a regular contained file")
    if current.stat().st_size > MAX_FILE_BYTES:
        raise BatchError("source exceeds 64 MiB individual PNG bound")
    return current


def load_plan(manifest_path: Path, source_root: Path, store: Path) -> tuple[dict, list[dict]]:
    """Fully validate every candidate before any data-store write."""
    source_root = _outside_checkout(Path(source_root), "source root")
    store = _outside_checkout(Path(store), "asset store")
    manifest_path = Path(manifest_path)
    if (not manifest_path.is_file() or _reparse(manifest_path)
            or manifest_path.stat().st_size > MAX_MANIFEST_BYTES):
        raise BatchError("manifest must be an existing nonlinked JSON <= 512 KiB")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (UnicodeError, ValueError) as exc:
        raise BatchError("invalid UTF-8 JSON batch manifest") from exc
    if (not isinstance(manifest, dict)
            or set(manifest) != MANIFEST_KEYS
            or type(manifest["schema_version"]) is not int
            or manifest["schema_version"] != 1
            or manifest["stage"] != "CANDIDATE_ONLY"
            or not isinstance(manifest["items"], list)
            or not 1 <= len(manifest["items"]) <= MAX_ITEMS):
        raise BatchError("unknown batch schema, stage or invalid item count")

    catalog = AssetCatalog(store)
    try:
        baseline = catalog.verify()
    except (CatalogError, OSError) as exc:
        raise BatchError("initialize and verify external asset catalog first: " + str(exc)) from exc
    rows, fingerprint_rows, public_rows = [], [], []
    seen = set()
    byte_total = 0
    for index, row in enumerate(manifest["items"]):
        if not isinstance(row, dict) or set(row) != ITEM_KEYS:
            raise BatchError("batch item has missing/unknown fields at index " + str(index))
        profile, key, rights = row["profile_id"], row["asset_key"], row["rights"]
        if not isinstance(profile, str) or profile not in PROFILES or not isinstance(key, str) or not KEY_PATTERN.fullmatch(key):
            raise BatchError("invalid profile/key in batch item " + str(index))
        if (profile, key) in seen:
            raise BatchError("duplicate profile/asset key within batch")
        seen.add((profile, key))
        if rights not in ("original", "licensed"):
            raise BatchError("asset rights must be declared as original or licensed")
        receipt = required_text(row["source_receipt"], "source receipt")
        expected = row["sha256"]
        if not isinstance(expected, str) or not HEX_SHA256.fullmatch(expected):
            raise BatchError("each original PNG must have a lowercase SHA-256 pin")
        filepath = _safe_source(source_root, row["file"])
        original = filepath.read_bytes()
        byte_total += len(original)
        if byte_total > MAX_BATCH_BYTES:
            raise BatchError("batch exceeds 64 MiB total source bytes")
        actual = hashlib.sha256(original).hexdigest()
        if actual != expected:
            raise BatchError("source PNG hash mismatch at item " + str(index))
        try:
            width, height = png_dimensions(original)
        except CatalogError as exc:
            raise BatchError("invalid/unsupported PNG at item " + str(index) + ": " + str(exc)) from exc
        rows.append({
            "profile": profile, "asset_key": key, "rights": rights,
            "source_receipt": receipt, "png_bytes": original, "sha256": expected
        })
        fingerprint_rows.append({
            "file": row["file"], "profile_id": profile, "asset_key": key,
            "rights": rights, "source_receipt": receipt,
            "sha256": actual, "width": width, "height": height
        })
        public_rows.append({
            "profile_id": profile, "asset_key": key, "sha256": actual,
            "width": width, "height": height, "status": "CANDIDATE_ONLY"
        })

    fingerprint = {
        "schema_version": 1, "stage": "CANDIDATE_ONLY",
        "baseline_revision_count": baseline["verified_revisions"],
        "items": fingerprint_rows
    }
    plan_sha = hashlib.sha256(
        json.dumps(fingerprint, sort_keys=True, ensure_ascii=True,
                   separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return {
        "schema_version": 1, "stage": "DRY_RUN_ONLY",
        "plan_sha256": plan_sha,
        "catalog_revision_baseline": baseline["verified_revisions"],
        "catalog_active_asset_count": baseline["active_assets"],
        "source_bytes": byte_total,
        "candidate_count": len(rows),
        "items": public_rows,
        "warning": "Dry run is not art/rights approval; no production assets exported."
    }, rows


def apply_plan(manifest_path: Path, source_root: Path, store: Path,
               expected_plan_sha256: str) -> dict:
    """All revisions commit in a single SQLite transaction; approvals stay unchanged.

    If writing an immutable blob fails, SQLite rolls back the entire candidate
    batch. Already-created orphan blobs are deliberately left untouched.
    """
    if (not isinstance(expected_plan_sha256, str)
            or not HEX_SHA256.fullmatch(expected_plan_sha256)):
        raise BatchError("commit needs the exact dry-run plan SHA-256")
    plan, rows = load_plan(manifest_path, source_root, store)
    if plan["plan_sha256"] != expected_plan_sha256:
        raise BatchError("plan changed; run the dry-run preflight again")
    try:
        results = AssetCatalog(store).ingest_batch(
            rows, expected_revision_count=plan["catalog_revision_baseline"])
    except (CatalogError, OSError) as exc:
        raise BatchError("batch rejected; no database revisions committed: " + str(exc)) from exc
    return {
        "schema_version": 1, "stage": "CANDIDATES_CREATED_NOT_APPROVED",
        "plan_sha256": plan["plan_sha256"],
        "candidate_count": len(results), "items": results,
        "warning": "These are pending candidate revisions; no owner approval or game export."
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--store", type=Path, required=True)
    parser.add_argument("--commit", action="store_true",
                        help="Explicitly append candidates after a matching dry-run plan")
    parser.add_argument("--expected-plan-sha256", default=None)
    args = parser.parse_args(argv)
    try:
        if args.commit:
            result = apply_plan(args.manifest, args.source_root, args.store,
                                args.expected_plan_sha256)
        else:
            if args.expected_plan_sha256 is not None:
                raise BatchError("--expected-plan-sha256 only applies to --commit")
            result, _ = load_plan(args.manifest, args.source_root, args.store)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
        return 0
    except (BatchError, CatalogError, OSError, UnicodeError) as exc:
        print("VUF_OFFLINE_BATCH_REJECTED: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
