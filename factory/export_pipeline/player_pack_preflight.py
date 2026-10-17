"""VF-10 / R44: strictly read-only player-package content quarantine preflight.

Scans only an explicitly supplied EXISTING, nonlinked, external candidate
directory. Even a clean scan CANNOT authorize a shipping release: owner
art-rights signoff, Engine/LFX pins, mobile QA and release audits are separate.
This module creates no archives, assets, stdout files, approvals or manifests.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAX_FILES = 512
MAX_BYTES = 128 * 1024 * 1024
MAX_FILE_BYTES = 16 * 1024 * 1024
ALLOWED = {".prefab", ".png", ".spriteatlasv2", ".anim",
           ".controller", ".asset", ".mat", ".json", ".meta"}
BLOCKED_PARTS = {
    "editor", "tests", "tools", "docs", "coordination", "references",
    "candidates", "evidence", "captures", "screenshots", "logs",
    "temp", "tmp", "library", "obj", "build", "userSettings",
    "projectsettings", "packages", "samples~", ".github", ".git",
    ".hiveai", ".codex", "__pycache__", "third_party"
}
BLOCKED_NAMES = {
    "tasks.md", "readme.md", ".env", "id_rsa", "id_ed25519",
    "packages-lock.json", "package-lock.json", "credentials.json",
    "service-account.json", "settings.json", "debug.log"
}
FORBIDDEN_TEXT = re.compile(
    rb"(?i)(-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"
    rb"|aws_secret_access_key\s*[:=]"
    rb"|(?:api[_-]?key|secret[_-]?key|access[_-]?token|password)"
    rb"\s*[\"']?\s*[:=]\s*[\"']?[^\"'\r\n\s]{6,})"
)


class PlayerPackError(ValueError):
    pass


def _linked(path: Path) -> bool:
    if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
        return True
    try:
        attrs = getattr(path.stat(follow_symlinks=False),
                        "st_file_attributes", 0)
    except OSError as exc:
        raise PlayerPackError("unable to inspect filesystem: " + str(exc)) from exc
    return bool(attrs & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def audit_candidate(root: Path) -> dict:
    root = Path(root)
    if (not root.is_dir() or _linked(root) or
            any(_linked(p) for p in root.parents)):
        raise PlayerPackError("expected existing nonlinked external candidate folder")
    resolved = root.resolve(strict=True)
    if resolved == ROOT or ROOT in resolved.parents:
        raise PlayerPackError("source repository cannot be scanned as candidate player pack")
    seen = set()
    files = []
    findings = []
    total = 0
    count = 0
    for base, folders, filenames in os.walk(root, topdown=True, followlinks=False):
        parent = Path(base)
        if _linked(parent):
            raise PlayerPackError("linked candidate subfolder not allowed")
        for folder in sorted(folders):
            path = parent / folder
            if _linked(path):
                raise PlayerPackError("linked candidate subdirectory: " + folder)
            rel = path.relative_to(root).as_posix()
            if any(part.casefold() in BLOCKED_PARTS for part in path.relative_to(root).parts):
                findings.append({"path": rel, "reason": "PROHIBITED_DIRECTORY"})
        # Do NOT recurse into forbidden trees or inspect their contents.
        folders[:] = sorted(p for p in folders if
                            p.casefold() not in BLOCKED_PARTS)
        for name in sorted(filenames):
            count += 1
            if count > MAX_FILES:
                raise PlayerPackError("candidate has too many files")
            path = parent / name
            relative = path.relative_to(root)
            item = relative.as_posix()
            canonical = item.casefold()
            if canonical in seen:
                findings.append({"path": item, "reason": "CASE_INSENSITIVE_COLLISION"})
            seen.add(canonical)
            if _linked(path) or not path.is_file():
                raise PlayerPackError("linked/special file in candidate: " + item)
            st = path.stat(follow_symlinks=False)
            if st.st_size > MAX_FILE_BYTES or st.st_size == 0:
                findings.append({"path": item, "reason": "OVERSIZE_OR_EMPTY_FILE"})
                continue
            total += st.st_size
            if total > MAX_BYTES:
                raise PlayerPackError("candidate aggregate byte budget exceeded")
            if (name.casefold() in BLOCKED_NAMES or name.startswith(".") or
                    path.suffix.casefold() not in ALLOWED or
                    any(part.casefold() in BLOCKED_PARTS for part in relative.parts[:-1])):
                findings.append({"path": item, "reason": "FORBIDDEN_RELEASE_CONTENT"})
                continue
            with path.open("rb") as stream:
                raw = stream.read(MAX_FILE_BYTES + 1)
            if len(raw) != st.st_size:
                raise PlayerPackError("file changed during preflight: " + item)
            # Detect misplaced Unity editor-only and test development assets.
            if path.suffix.casefold() in {".json", ".asset", ".prefab", ".mat",
                                           ".anim", ".controller"}:
                if FORBIDDEN_TEXT.search(raw):
                    findings.append({"path": item, "reason": "POTENTIAL_SECRET"})
                if re.search(rb"(?i)(TEST_ONLY|CANDIDATE_NOT_OWNER_APPROVED"
                             rb"|AUTHORING_ONLY|UnityEditor\.)", raw):
                    findings.append({"path": item, "reason": "NON_SHIPPING_MARKER"})
            files.append({"path": item, "sha256": hashlib.sha256(raw).hexdigest(),
                          "size_bytes": st.st_size})
    findings.sort(key=lambda x: (x["path"], x["reason"]))
    files.sort(key=lambda x: x["path"])
    return {
        "schema_version": 1,
        "kind": "VF10_PLAYER_PACK_PREFLIGHT",
        "status": "REVIEW_ONLY_NOT_PRODUCTION_RELEASE",
        "content_clean": not findings,
        "release_allowed": False,
        "independent_engine_lfx_gate": "NOT_VERIFIED",
        "original_art_rights_gate": "NOT_VERIFIED",
        "owner_visual_gate": "NOT_VERIFIED",
        "mobile_device_gate": "NOT_VERIFIED",
        "file_count": len(files),
        "total_scanned_bytes": total,
        "files": files,
        "findings": findings,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        print(json.dumps(audit_candidate(args.candidate),
                         sort_keys=True, indent=2))
        return 0
    except (OSError, PlayerPackError) as exc:
        print("VF10_PREFLIGHT_REJECTED: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
