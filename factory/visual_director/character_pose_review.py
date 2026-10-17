"""VUF-M06: fail-closed ORIGINAL artist character/mascot pose review.

This is *not* a character generator or automated artistic identity approval.
It accepts one externally held reference PNG and exactly five pose PNGs,
validates pinned source hashes, dimensions, alpha and safe-area anchors,
then constructs an in-memory six-panel PNG contact sheet. Any editorial
identity similarity, licence provenance and owner signature remain OPEN.

INTERNAL_REUSE: existing RGBA PNG codec and Style Bible five-theme IDs.
No unlicensed reference scraping, no game repo reads or writes, no overwrite.
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
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from factory.image_processor.png_pipeline import (
    ImageError, decode_png, encode_png, MAX_INPUT_BYTES
)
from factory.visual_director.silhouette_kit import PROFILES

POSES = ("idle", "greet", "celebrate", "concerned", "action")
STAGE = "EXTERNAL_ORIGINAL_OWNER_REVIEW_REQUIRED"
ID = re.compile(r"[a-z][a-z0-9_]{0,63}\Z")
SHA = re.compile(r"[0-9a-f]{64}\Z")
PNG = re.compile(r"[a-z][a-z0-9_]{0,75}\.png\Z")
MAX_SHEET_PIXELS = 16_000_000


class PoseReviewError(ValueError):
    pass


def _is_link(path: Path) -> bool:
    if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
        return True
    try:
        st = path.stat(follow_symlinks=False)
    except OSError:
        return True
    return bool(getattr(st, "st_file_attributes", 0) &
                getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def _source_root(root: Path) -> Path:
    root = Path(root)
    if not root.is_dir() or any(_is_link(x) for x in (root, *root.parents)):
        raise PoseReviewError("artist original source root must be real, not linked")
    real = root.resolve(strict=True)
    if real.is_relative_to(ROOT):
        raise PoseReviewError("artist originals must be held outside the Git repository")
    return real


def _pairs(items):
    doc = {}
    for k, v in items:
        if k in doc:
            raise PoseReviewError("duplicate manifest key")
        doc[k] = v
    return doc


def _manifest(data: bytes) -> dict:
    if not isinstance(data, bytes) or len(data) > 128 * 1024:
        raise PoseReviewError("source character manifest must be under 128 KiB")
    try:
        doc = json.loads(data.decode("utf-8"), object_pairs_hook=_pairs)
    except (UnicodeError, ValueError) as exc:
        raise PoseReviewError("invalid character manifest JSON") from exc
    required = {"schema_version", "stage", "profile_id", "character_id",
                "reference", "poses", "rights_receipt_id"}
    if (not isinstance(doc, dict) or set(doc) != required or
            doc.get("schema_version") != 1 or type(doc.get("schema_version")) is not int or
            doc.get("stage") != STAGE or doc.get("profile_id") not in PROFILES or
            not isinstance(doc.get("character_id"), str) or
            not ID.fullmatch(doc["character_id"]) or
            not isinstance(doc.get("rights_receipt_id"), str) or
            not ID.fullmatch(doc["rights_receipt_id"])):
        raise PoseReviewError("invalid or preapproved character identity contract")
    rows = doc.get("poses")
    if not isinstance(rows, list) or len(rows) != len(POSES):
        raise PoseReviewError("exactly five defined character pose images required")
    if (not isinstance(doc["reference"], dict) or
            set(doc["reference"]) != {"file", "sha256"}):
        raise PoseReviewError("explicit pinned reference original required")
    names = []
    for row in [doc["reference"], *rows]:
        if (not isinstance(row, dict) or
                (row is not doc["reference"] and
                 set(row) != {"pose", "file", "sha256", "anchor_xy"})):
            raise PoseReviewError("invalid frame data/pose")
        filename, digest = row.get("file"), row.get("sha256")
        if (not isinstance(filename, str) or not PNG.fullmatch(filename) or
                not isinstance(digest, str) or not SHA.fullmatch(digest)):
            raise PoseReviewError("invalid source filename or SHA")
        names.append(filename)
    if len(set(names)) != 6:
        raise PoseReviewError("duplicated original PNG filename")
    if [r["pose"] for r in rows] != list(POSES):
        raise PoseReviewError("missing or reordered character pose type")
    for r in rows:
        pivot = r.get("anchor_xy")
        if (not isinstance(pivot, list) or len(pivot) != 2 or
                any(type(x) is not int or not 0 <= x <= 2048 for x in pivot)):
            raise PoseReviewError("pose anchor must be normalized integral pixel coordinate")
    return doc


def _read_png(root: Path, file: str, sha: str) -> tuple[int, int, bytes, bytes]:
    path = root / file
    if _is_link(path) or not path.is_file():
        raise PoseReviewError("missing or symlinked artist PNG")
    st = path.stat()
    if st.st_size > MAX_INPUT_BYTES:
        raise PoseReviewError("source image exceeds bounded byte limit")
    original = path.read_bytes()
    after = path.stat()
    if after.st_size != st.st_size or after.st_mtime_ns != st.st_mtime_ns:
        raise PoseReviewError("artist PNG modified during inspection")
    if hashlib.sha256(original).hexdigest() != sha:
        raise PoseReviewError("artist PNG source SHA changed")
    try:
        width, height, pixels = decode_png(original)
    except ImageError as exc:
        raise PoseReviewError("unsupported original PNG encoding") from exc
    if (width < 12 or height < 12 or width > 2048 or height > 2048 or
            width * height > 2_500_000 or not any(pixels[3::4])):
        raise PoseReviewError("transparent or dimensionally unsupported character PNG")
    return width, height, pixels, original


def _coverage(width: int, height: int, pixels: bytes) -> dict:
    low_x, low_y, high_x, high_y = width, height, -1, -1
    count, weighted_x, weighted_y = 0, 0, 0
    for y in range(height):
        for x in range(width):
            alpha = pixels[(y * width + x) * 4 + 3]
            if alpha > 0:
                count += 1
                weighted_x += alpha * x
                weighted_y += alpha * y
                low_x = min(low_x, x)
                low_y = min(low_y, y)
                high_x = max(high_x, x)
                high_y = max(high_y, y)
    if high_x < low_x:
        raise PoseReviewError("zero-alpha character source")
    total_alpha = sum(pixels[3::4])
    return {
        "visible_pixels": count,
        "alpha_bounds_top_left": [low_x, low_y, high_x + 1, high_y + 1],
        "alpha_center_per_mille": [
            weighted_x * 1000 // max(1, total_alpha * width),
            weighted_y * 1000 // max(1, total_alpha * height),
        ],
    }


def inspect_character(manifest_file: Path, source_root: Path) -> tuple[dict, bytes]:
    """Read originals only; return (candidate receipt, six-panel image bytes)."""
    root = _source_root(source_root)
    manifest_file = Path(manifest_file)
    if (_is_link(manifest_file) or not manifest_file.is_file() or
            any(_is_link(p) for p in manifest_file.parents) or
            manifest_file.resolve(strict=True).is_relative_to(ROOT)):
        raise PoseReviewError("source manifest must be ordinary external file")
    if manifest_file.stat().st_size > 128 * 1024:
        raise PoseReviewError("source manifest exceeds bounded byte limit")
    data = manifest_file.read_bytes()
    spec = _manifest(data)
    frames = []
    for row in [spec["reference"], *spec["poses"]]:
        frames.append(_read_png(root, row["file"], row["sha256"]))
    widths = {x[0] for x in frames}
    heights = {x[1] for x in frames}
    if len(widths) != 1 or len(heights) != 1:
        raise PoseReviewError("reference and poses require exact same source canvas")
    w, h = frames[0][:2]
    if 3 * w * 2 * h > MAX_SHEET_PIXELS:
        raise PoseReviewError("six-frame sheet exceeds export pixel budget")
    seen_hashes = {x["sha256"] for x in [spec["reference"], *spec["poses"]]}
    if len(seen_hashes) != 6:
        raise PoseReviewError("duplicate art image across distinct poses")
    # One source-normalized placement contract; do not auto-register gameplay.
    positions = []
    for i, row in enumerate(spec["poses"]):
        x, y = row["anchor_xy"]
        if x >= w or y >= h:
            raise PoseReviewError("pose anchor outside actual PNG canvas")
        positions.append({
            "pose": row["pose"],
            "sha256": row["sha256"],
            "anchor_xy": [x, y],
            **_coverage(w, h, frames[i + 1][2]),
        })
    canvas = bytearray(w * 3 * h * 2 * 4)
    stride = w * 3
    for i, (_, _, rgba, _) in enumerate(frames):
        col, row = i % 3, i // 3
        for y in range(h):
            src = y * w * 4
            dst = ((row * h + y) * stride + col * w) * 4
            canvas[dst:dst + w * 4] = rgba[src:src + w * 4]
    sheet = encode_png(w * 3, h * 2, bytes(canvas))
    return {
        "schema_version": 1,
        "stage": STAGE,
        "profile_id": spec["profile_id"],
        "character_id": spec["character_id"],
        "source_manifest_sha256": hashlib.sha256(data).hexdigest(),
        "reference_png_sha256": spec["reference"]["sha256"],
        "rights_receipt_id_unverified": spec["rights_receipt_id"],
        "frame_canvas": [w, h],
        "sheet_canvas": [w * 3, h * 2],
        "contact_sheet_sha256": hashlib.sha256(sheet).hexdigest(),
        "pose_geometry": positions,
        "owner_art_identity_accepted": False,
        "legal_rights_authenticated": False,
        "device_qa_verified": False,
        "runtime_gameplay_binding": False,
        "release_allowed": False,
    }, sheet


def write_contact_sheet(directory: Path, receipt: dict, png: bytes) -> None:
    """Write a new external review folder ONLY, with no source modifications."""
    if (not isinstance(receipt, dict) or
            receipt.get("stage") != STAGE or
            hashlib.sha256(png).hexdigest() != receipt.get("contact_sheet_sha256") or
            any(receipt.get(flag) is not False
                for flag in ("owner_art_identity_accepted", "legal_rights_authenticated",
                             "device_qa_verified", "runtime_gameplay_binding",
                             "release_allowed"))):
        raise PoseReviewError("invalid or forged unapproved sheet")
    path = Path(directory)
    if (path.exists() or path.is_symlink() or
            not path.parent.is_dir() or
            any(_is_link(p) for p in (path.parent, *path.parent.parents)) or
            path.parent.resolve(strict=True).is_relative_to(ROOT)):
        raise PoseReviewError("review destination must be new and outside repository")
    path.mkdir()
    with (path / "pose_contact_sheet.png").open("xb") as out:
        out.write(png)
        out.flush()
        os.fsync(out.fileno())
    with (path / "pose_review_receipt.json").open(
            "x", encoding="utf-8", newline="\n") as out:
        json.dump(receipt, out, sort_keys=True, indent=2)
        out.write("\n")
        out.flush()
        os.fsync(out.fileno())


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", required=True, type=Path)
    p.add_argument("--source-root", required=True, type=Path)
    p.add_argument("--output-dir", type=Path)
    args = p.parse_args(argv)
    try:
        receipt, sheet = inspect_character(args.manifest, args.source_root)
        if args.output_dir:
            write_contact_sheet(args.output_dir, receipt, sheet)
        print(json.dumps({"stage": STAGE, "profile_id": receipt["profile_id"],
                          "pose_count": len(receipt["pose_geometry"]),
                          "contact_sheet_sha256": receipt["contact_sheet_sha256"],
                          "owner_approved": False, "output_saved": bool(args.output_dir)},
                         sort_keys=True))
        return 0
    except (PoseReviewError, ImageError, OSError, ValueError) as exc:
        print("CHARACTER_REVIEW_REJECTED: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
