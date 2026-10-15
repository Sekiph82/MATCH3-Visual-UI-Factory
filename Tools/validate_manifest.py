"""Fail-closed local validation for VUF preview/asset manifests (stdlib only).

Not an art licence verifier and not Engine/LFX compatibility certification.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath

PROFILES = {
    "Coral_Rescue", "Garage_Legends", "Dino_Islands",
    "The_Fractured_Realms", "Wonder_Pop",
}
STATES = {
    "Ready", "Loading", "Offline", "Error",
    "Owned", "Claimed", "Disabled", "Pending",
}
STAGES = {"TEST_ONLY", "CANDIDATE", "APPROVED"}
SHA256 = re.compile(r"^[0-9a-f]{64}$")
GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
KEY = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]{0,127}$")
SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")


def _reject(message: str) -> None:
    raise ValueError(message)


def _plain_object(value: object, name: str) -> dict:
    if not isinstance(value, dict):
        _reject(f"{name}: expected object")
    return value


def _nonempty_string(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        _reject(f"{name}: expected nonempty string")
    return value


def _safe_relative_path(value: object) -> str:
    path = _nonempty_string(value, "path")
    if (path.startswith("/") or "\\" in path or ":" in path or
            "//" in path or "\x00" in path):
        _reject("asset path is not portable relative POSIX path")
    parts = path.split("/")
    if (any(part in ("", ".", "..") or part.rstrip(" .") != part for part in parts)
            or PurePosixPath(path).as_posix() != path):
        _reject("asset path is not canonical or contains traversal")
    if any(part.split(".")[0].upper() in {"CON", "PRN", "AUX", "NUL",
            "COM1", "COM2", "COM3", "LPT1", "LPT2", "LPT3"} for part in parts):
        _reject("asset path uses reserved Windows device name")
    if parts[0] in {"Assets", "ProjectSettings", "Packages", ".github"}:
        _reject("asset path points at source/runtime configuration")
    return path


def validate_manifest(doc: object, source_root: Path | None = None) -> None:
    manifest = _plain_object(doc, "manifest")
    required = {
        "schema_version", "profile_id", "theme_version",
        "engine_sha", "level_factory_sha", "stage", "assets",
    }
    if set(manifest) != required | ({"owner_approval_receipt"} if "owner_approval_receipt" in manifest else set()):
        _reject("unexpected or missing top-level fields")
    if type(manifest["schema_version"]) is not int or manifest["schema_version"] != 1:
        _reject("unsupported schema_version")
    if manifest["profile_id"] not in PROFILES:
        _reject("unknown game profile")
    if not isinstance(manifest["theme_version"], str) or not SEMVER.fullmatch(manifest["theme_version"]):
        _reject("theme_version must be numeric SemVer")
    stage = manifest["stage"]
    if stage not in STAGES:
        _reject("invalid stage")
    for field in ("engine_sha", "level_factory_sha"):
        sha = manifest[field]
        if stage == "APPROVED":
            if not isinstance(sha, str) or not GIT_SHA.fullmatch(sha):
                _reject(f"{field} requires pinned full commit hash")
        elif sha != "UNPINNED" and (not isinstance(sha, str) or not GIT_SHA.fullmatch(sha)):
            _reject(f"{field} invalid")
    if stage == "APPROVED":
        _nonempty_string(manifest.get("owner_approval_receipt"), "owner_approval_receipt")
    elif "owner_approval_receipt" in manifest:
        _reject("unapproved candidate cannot claim owner receipt")
    assets = manifest["assets"]
    if not isinstance(assets, list):
        _reject("assets must be list")
    if stage == "APPROVED" and not assets:
        _reject("empty asset pack cannot be approved")
    seen_ids, seen_paths = set(), set()
    for i, item in enumerate(assets):
        a = _plain_object(item, f"assets[{i}]")
        if set(a) != {"asset_id", "path", "sha256", "state", "rights", "source_receipt"}:
            _reject(f"assets[{i}]: missing or unexpected fields")
        asset_id = _nonempty_string(a["asset_id"], "asset_id")
        if not KEY.fullmatch(asset_id) or not asset_id.startswith(manifest["profile_id"] + "."):
            _reject("invalid or cross-theme asset_id")
        if asset_id in seen_ids:
            _reject("duplicate asset_id")
        seen_ids.add(asset_id)
        path = _safe_relative_path(a["path"])
        if path in seen_paths:
            _reject("duplicate asset path")
        seen_paths.add(path)
        digest = a["sha256"]
        if not isinstance(digest, str) or not SHA256.fullmatch(digest):
            _reject("invalid SHA-256")
        if a["state"] not in STATES:
            _reject("unknown UI state")
        if a["rights"] not in ("original", "licensed", "placeholder"):
            _reject("unknown rights classification")
        _nonempty_string(a["source_receipt"], "source_receipt")
        if stage == "APPROVED" and a["rights"] == "placeholder":
            _reject("placeholder not allowed in approved pack")
        if source_root is not None:
            resolved_root = source_root.resolve(strict=True)
            resolved = (resolved_root / path).resolve(strict=True)
            if not resolved.is_relative_to(resolved_root) or not resolved.is_file():
                _reject("asset file escapes root or is not regular")
            if hashlib.sha256(resolved.read_bytes()).hexdigest() != digest:
                _reject("asset file hash mismatch")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--source-root", type=Path)
    args = parser.parse_args(argv)
    try:
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
        validate_manifest(data, args.source_root)
    except (ValueError, OSError, json.JSONDecodeError) as error:
        print(f"VUF_MANIFEST_REJECTED: {error}", file=sys.stderr)
        return 2
    print("VUF_MANIFEST_VALID: structural checks only, NOT creative/rights approval")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
