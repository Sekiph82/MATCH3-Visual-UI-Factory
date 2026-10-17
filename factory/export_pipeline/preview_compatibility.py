"""R45 / VUF-M08-004: offline manifest compatibility/difference inspector.

INTERNAL_REUSE of Tools.validate_manifest.validate_manifest and existing
sha-pinned asset schemas. No VUF, Engine or LFX production acceptance. Reads
only explicit external existing paths; creates no assets, rollback writes,
permission grants or inferred owner approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from Tools.validate_manifest import validate_manifest, PROFILES

SHA = re.compile(r"^[a-f0-9]{40}$")
MAX_JSON_BYTES = 2 * 1024 * 1024
MAX_ASSETS = 512


class CompatibilityError(ValueError):
    pass


def _nonlinked(path: Path) -> Path:
    candidate = Path(path)
    if (not candidate.is_file() or candidate.is_symlink() or
            any(p.is_symlink() for p in candidate.parents) or
            getattr(candidate.stat(follow_symlinks=False),
                    "st_file_attributes", 0) &
            getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)):
        raise CompatibilityError("manifest must be an ordinary nonlinked existing file")
    real = candidate.resolve(strict=True)
    if real == ROOT or ROOT in real.parents:
        raise CompatibilityError("existing source repo is not an external candidate manifest")
    if candidate.stat().st_size > MAX_JSON_BYTES:
        raise CompatibilityError("oversized candidate manifest")
    return candidate


def _read_manifest(path: Path) -> tuple[dict, str]:
    raw = _nonlinked(path).read_bytes()
    if len(raw) > MAX_JSON_BYTES:
        raise CompatibilityError("manifest size changed during read")
    try:
        doc = json.loads(raw, object_pairs_hook=_no_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError) as exc:
        raise CompatibilityError("invalid or duplicate JSON") from exc
    if not isinstance(doc, dict):
        raise CompatibilityError("manifest must be object")
    assets = doc.get("assets")
    if not isinstance(assets, list) or len(assets) > MAX_ASSETS:
        raise CompatibilityError("too many or malformed assets")
    try:
        validate_manifest(doc)
    except ValueError as exc:
        raise CompatibilityError("source manifest invalid: " + str(exc)) from exc
    return doc, hashlib.sha256(raw).hexdigest()


def _no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise CompatibilityError("duplicate JSON field")
        result[key] = value
    return result


def inspect_compatibility(
    path: Path, profile: str, engine_sha: str, level_factory_sha: str,
    previous_manifest: Path | None = None
) -> dict:
    if profile not in PROFILES:
        raise CompatibilityError("unknown game profile")
    for digest in (engine_sha, level_factory_sha):
        if not isinstance(digest, str) or SHA.fullmatch(digest) is None:
            raise CompatibilityError("exact 40-character upstream git SHA required")
    doc, digest = _read_manifest(path)
    if doc["profile_id"] != profile:
        raise CompatibilityError("cross-theme manifest refused")
    if doc["stage"] not in ("TEST_ONLY", "CANDIDATE"):
        raise CompatibilityError("received approved declaration cannot be independently authenticated")
    expected = {"engine_sha": engine_sha, "level_factory_sha": level_factory_sha}
    mismatches = [field for field, sha in expected.items() if doc[field] != sha]
    rollback = {"previous_manifest_present": False,
                "previous_assets_reverified": False,
                "previous_release_available": False,
                "asset_differences": []}
    if previous_manifest is not None:
        before, before_sha = _read_manifest(previous_manifest)
        if before["profile_id"] != profile:
            raise CompatibilityError("previous snapshot is from wrong game")
        if before["stage"] not in ("TEST_ONLY", "CANDIDATE"):
            raise CompatibilityError("cannot claim approved rollback without independent owner authority")
        old = {a["asset_id"]: a["sha256"] for a in before["assets"]}
        now = {a["asset_id"]: a["sha256"] for a in doc["assets"]}
        rows = []
        for key in sorted(set(old) | set(now)):
            if old.get(key) != now.get(key):
                rows.append({"asset_id": key, "change":
                             "ADDED" if key not in old else
                             "REMOVED" if key not in now else
                             "CHANGED"})
        rollback = {
            "previous_manifest_present": True,
            "previous_manifest_sha256": before_sha,
            "previous_assets_reverified": False,
            "previous_release_available": False,
            "asset_differences": rows
        }
    return {
        "schema_version": 1,
        "status": "MECHANICAL_PREVIEW_ONLY",
        "manifest_sha256": digest,
        "profile_id": profile,
        "manifest_stage": doc["stage"],
        "manifest_asset_count": len(doc["assets"]),
        "upstream_pins_exactly_match": not mismatches,
        "pin_mismatches": mismatches,
        "manifest_file_bytes_reverified": True,
        "asset_file_bytes_reverified": False,
        "engine_lfx_independent_pass": False,
        "original_rights_verified": False,
        "owner_visual_approval": False,
        "real_device_verified": False,
        "release_allowed": False,
        "rollback": rollback,
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--candidate-manifest", required=True, type=Path)
    p.add_argument("--profile", required=True)
    p.add_argument("--engine-sha", required=True)
    p.add_argument("--level-factory-sha", required=True)
    p.add_argument("--previous-manifest", type=Path)
    args = p.parse_args(argv)
    try:
        report = inspect_compatibility(args.candidate_manifest, args.profile,
                                       args.engine_sha, args.level_factory_sha,
                                       args.previous_manifest)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    except (CompatibilityError, OSError) as exc:
        print("VUF_M08_COMPATIBILITY_REJECTED: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
