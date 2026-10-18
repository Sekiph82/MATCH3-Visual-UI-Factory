"""Independent read-only verification for a VUF-M08 TEST_ONLY export.

Consumes only source path and JSON bytes already exported; checks every
receipt SHA including the real VF04 atlas source. Never builds missing
assets, repairs originals, follows symlinks, signs licenses, approves art
or writes anything. A success here is NOT Unity player/device acceptance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
from pathlib import Path

from factory.asset_packaging.candidate_pack import (
    ROOT, PACK_GENERATOR, CandidatePackError, verify_pack,
)
from factory.validators.atlas_candidate_audit import audit_candidate

HASH = re.compile(r"[0-9a-f]{64}\Z")
FILE = re.compile(r"[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)*\.(?:png|json)\Z")


def _pairs(values):
    d = {}
    for name, value in values:
        if name in d:
            raise CandidatePackError("duplicate exported JSON field")
        d[name] = value
    return d


def _linked(path: Path) -> bool:
    if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
        return True
    try:
        flags = getattr(path.stat(follow_symlinks=False),
                        "st_file_attributes", 0)
        return bool(flags & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))
    except OSError:
        return True


def _data(folder: Path, filename: str, *, max_bytes: int = 16 * 1024 * 1024):
    if not FILE.fullmatch(filename):
        raise CandidatePackError("invalid receipt relative path")
    path = folder / filename
    if (any(_linked(p) for p in (path, *path.parents)) or
            not path.is_file() or path.stat().st_size > max_bytes):
        raise CandidatePackError("missing/linked/oversized exported source")
    return path.read_bytes()


def verify_exported_pack(directory: Path) -> dict:
    folder = Path(directory)
    if (not folder.is_dir() or
            any(_linked(p) for p in (folder, *folder.parents)) or
            folder.resolve(strict=True).is_relative_to(ROOT)):
        raise CandidatePackError("export must be an external real directory")
    data = _data(folder, "candidate_pack_receipt.json", max_bytes=512 * 1024)
    receipt = json.loads(data.decode("utf-8"), object_pairs_hook=_pairs)
    if (not isinstance(receipt, dict) or
            receipt.get("generator") != PACK_GENERATOR or
            receipt.get("stage") != "TEST_ONLY" or
            receipt.get("release_allowed") is not False or
            receipt.get("rights_approved") is not False):
        raise CandidatePackError("candidate receipt forged")
    entries, mapping = receipt.get("file_entries"), receipt.get("file_sha256")
    if (not isinstance(entries, list) or
            not isinstance(mapping, dict) or not 45 <= len(entries) <= 160 or
            len(entries) != len(mapping)):
        raise CandidatePackError("invalid receipt source listing")
    files = {}
    seen = set()
    for item in entries:
        if not isinstance(item, dict) or set(item) != {"path", "sha256"}:
            raise CandidatePackError("invalid or extra receipt entry")
        path, expected = item["path"], item["sha256"]
        if (not isinstance(path, str) or path in seen or
                not isinstance(expected, str) or not HASH.fullmatch(expected) or
                mapping.get(path) != expected):
            raise CandidatePackError("mismatched/duplicate external receipt")
        seen.add(path)
        raw = _data(folder, path)
        if hashlib.sha256(raw).hexdigest() != expected:
            raise CandidatePackError("export source hash mismatch: " + path)
        files[path] = raw
    if set(mapping) != seen or "visual_manifest.json" not in files:
        raise CandidatePackError("source manifest not in complete receipt")
    manifest = json.loads(files.pop("visual_manifest.json").decode("utf-8"),
                          object_pairs_hook=_pairs)
    verify_pack(manifest, files, receipt)
    atlas = json.loads(files["sprite_atlas/atlas_manifest.json"].decode("utf-8"),
                       object_pairs_hook=_pairs)
    if (atlas.get("stage") != "CANDIDATE_NOT_APPROVED" or
            atlas.get("atlas_sha256") !=
            hashlib.sha256(files["sprite_atlas/atlas.png"]).hexdigest()):
        raise CandidatePackError("VF04 atlas metadata/digest changed")
    required = [
        row["path"].split("/")[-1][:-4]
        for row in manifest["assets"]
        if row["path"].startswith("sprites/") and
           row["path"].endswith(".png")
    ]
    if not required:
        raise CandidatePackError("R52 sample references absent")
    audit = audit_candidate(folder / "sprite_atlas", required_ids=required)
    return {
        "stage": "TEST_ONLY",
        "profile_id": manifest["profile_id"],
        "verified_images": len(manifest["assets"]),
        "verified_files": len(seen),
        "vf04_atlas_audit": audit,
        "real_unity_import_tested": False,
        "owner_rights_approved": False,
        "final_engine_lfx_parity": False,
        "release_allowed": False,
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pack-dir", required=True, type=Path)
    args = p.parse_args(argv)
    try:
        print(json.dumps(verify_exported_pack(args.pack_dir),
                         sort_keys=True, indent=2))
        return 0
    except (CandidatePackError, ValueError, OSError) as exc:
        p.exit(2, "M08_PACK_VERIFY_REJECTED: " + str(exc) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
