"""VUF R49 / M05-005: bounded, read-only audit of actual VF-04 atlas candidates.

INTERNAL_REUSE: atlas_pipeline manifest and png_pipeline.decode_png; the
existing generated-kit verifier covers other candidate families. No copied
donor source or new Unity/paid dependency. This is CPU/RGBA8 estimation,
never a measured platform/GPU/rights/owner acceptance result.
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
from factory.image_processor.png_pipeline import decode_png, ImageError

KEY = re.compile(r"[a-z][a-z0-9_.-]{0,99}\Z")
SHA = re.compile(r"[0-9a-f]{64}\Z")
MAX_MANIFEST_BYTES = 256 * 1024
MAX_ATLAS_FILE_BYTES = 64 * 1024 * 1024
MAX_SPRITES = 128
MAX_SIDE = 4096
DEFAULT_BUDGET = 64 * 1024 * 1024


class AtlasAuditError(ValueError):
    pass


def _object_pairs(rows):
    obj = {}
    for k, v in rows:
        if k in obj:
            raise AtlasAuditError("duplicate JSON key")
        obj[k] = v
    return obj


def _linked(path: Path) -> bool:
    try:
        info = path.stat(follow_symlinks=False)
        return (path.is_symlink() or
                (hasattr(path, "is_junction") and path.is_junction()) or
                bool(getattr(info, "st_file_attributes", 0) &
                     getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)))
    except OSError as exc:
        raise AtlasAuditError("cannot inspect candidate path") from exc


def _safe_file(path: Path, limit: int) -> bytes:
    if not path.is_file() or _linked(path):
        raise AtlasAuditError("expected ordinary unlinked candidate file")
    before = path.stat()
    if before.st_size > limit:
        raise AtlasAuditError("candidate exceeds bounded byte limit")
    raw = path.read_bytes()
    after = path.stat()
    if len(raw) != before.st_size or after.st_size != before.st_size or after.st_mtime_ns != before.st_mtime_ns:
        raise AtlasAuditError("candidate changed during read")
    return raw


def _safe_folder(directory: Path) -> Path:
    folder = Path(directory)
    if not folder.is_dir() or _linked(folder):
        raise AtlasAuditError("candidate folder must be an ordinary directory")
    if any(_linked(parent) for parent in folder.parents if parent.exists()):
        raise AtlasAuditError("linked ancestor not allowed")
    real = folder.resolve(strict=True)
    if real == ROOT or real.is_relative_to(ROOT):
        raise AtlasAuditError("must audit a candidate outside the source repository")
    return real


def _integer(value, label: str, low: int, high: int) -> int:
    if type(value) is not int or not low <= value <= high:
        raise AtlasAuditError(label + " out of bounds")
    return value


def _rectangle(value, label: str) -> tuple[int, int, int, int]:
    if not isinstance(value, list) or len(value) != 4:
        raise AtlasAuditError(label + " must be four integers")
    return tuple(_integer(v, label, 0, MAX_SIDE) for v in value)


def _sprite_rgba(atlas: bytes, width: int, x: int, y: int, w: int, h: int) -> bytes:
    out = bytearray(w * h * 4)
    for row in range(h):
        left = ((y + row) * width + x) * 4
        out[row * w * 4:(row + 1) * w * 4] = atlas[left:left + w * 4]
    return bytes(out)


def audit_candidate(directory: Path, *, required_ids=(),
                    max_memory_bytes: int = DEFAULT_BUDGET,
                    distinct_alpha_masks: bool = False) -> dict:
    """Verify a generated candidate atlas against its own recorded bytes.

    required_ids detects absent expected sprites/states. This NEVER compares
    original artist source files or claims authentic provenance or GPU memory.
    """
    _integer(max_memory_bytes, "memory limit", 1, 512 * 1024 * 1024)
    folder = _safe_folder(Path(directory))
    try:
        manifest = json.loads(
            _safe_file(folder / "atlas_manifest.json", MAX_MANIFEST_BYTES),
            object_pairs_hook=_object_pairs)
    except (ValueError, UnicodeDecodeError) as exc:
        raise AtlasAuditError("invalid or duplicate atlas manifest") from exc
    if not isinstance(manifest, dict):
        raise AtlasAuditError("manifest must be object")
    if (manifest.get("schema_version") != 1 or
            manifest.get("stage") != "CANDIDATE_NOT_APPROVED" or
            manifest.get("generator") != "VF04_SHELF_PACK_V01" or
            manifest.get("format") != "RGBA8_UNROTATED" or
            manifest.get("atlas_path") != "atlas.png"):
        raise AtlasAuditError("unexpected atlas schema/stage/format/path")
    width = _integer(manifest.get("width"), "width", 1, MAX_SIDE)
    height = _integer(manifest.get("height"), "height", 1, MAX_SIDE)
    if width * height > 16_777_216:
        raise AtlasAuditError("too many atlas pixels")
    estimated_rgba_bytes = width * height * 4
    estimated_mip_rgba_bytes = (estimated_rgba_bytes * 4 + 2) // 3
    if estimated_mip_rgba_bytes > max_memory_bytes:
        raise AtlasAuditError("estimated uncompressed RGBA8 mip memory budget exceeded")
    expected_hash = manifest.get("atlas_sha256")
    if not isinstance(expected_hash, str) or not SHA.fullmatch(expected_hash):
        raise AtlasAuditError("invalid atlas hash")
    data = _safe_file(folder / "atlas.png", MAX_ATLAS_FILE_BYTES)
    if hashlib.sha256(data).hexdigest() != expected_hash:
        raise AtlasAuditError("atlas file SHA256 mismatch")
    try:
        png_w, png_h, rgba = decode_png(data)
    except ImageError as exc:
        raise AtlasAuditError("invalid candidate atlas PNG") from exc
    if (png_w, png_h) != (width, height):
        raise AtlasAuditError("atlas dimensions mismatch")
    entries = manifest.get("sprites")
    if not isinstance(entries, list) or not 1 <= len(entries) <= MAX_SPRITES:
        raise AtlasAuditError("invalid sprite count")
    ids, boxes, pixel_hashes, alpha_hashes = set(), [], set(), set()
    alpha_positive, alpha_partial = 0, 0
    for e in entries:
        if not isinstance(e, dict):
            raise AtlasAuditError("sprite must be object")
        key = e.get("asset_id")
        if not isinstance(key, str) or not KEY.fullmatch(key) or key in ids:
            raise AtlasAuditError("duplicate or invalid sprite ID")
        ids.add(key)
        original = e.get("original_sha256")
        if not isinstance(original, str) or not SHA.fullmatch(original):
            raise AtlasAuditError("missing valid source hash receipt")
        x, y, w, h = _rectangle(e.get("pixel_rect_top_left"), "sprite rectangle")
        if not w or not h or x + w > width or y + h > height:
            raise AtlasAuditError("sprite missing pixels or outside atlas")
        if (_integer(e.get("width"), "sprite width", 1, MAX_SIDE) != w or
                _integer(e.get("height"), "sprite height", 1, MAX_SIDE) != h or
                e.get("rotated") is not False):
            raise AtlasAuditError("sprite dimensions/rotation mismatch")
        for prev_x, prev_y, prev_w, prev_h in boxes:
            if x < prev_x + prev_w and prev_x < x + w and y < prev_y + prev_h and prev_y < y + h:
                raise AtlasAuditError("overlapping sprite regions")
        boxes.append((x, y, w, h))
        uv = e.get("uv_rect_bottom_left")
        if (not isinstance(uv, list) or len(uv) != 4 or
                any(type(v) not in (float, int) for v in uv)):
            raise AtlasAuditError("invalid sprite UV coordinates")
        expected_uv = (x / width, (height - y - h) / height,
                       w / width, h / height)
        if any(abs(float(a) - b) > 1e-8 for a, b in zip(uv, expected_uv)):
            raise AtlasAuditError("sprite UV/geometry mismatch")
        crop = _sprite_rgba(rgba, width, x, y, w, h)
        crop_sha = hashlib.sha256(crop).hexdigest()
        if crop_sha in pixel_hashes:
            raise AtlasAuditError("duplicate exact sprite pixels")
        pixel_hashes.add(crop_sha)
        alphas = crop[3::4]
        if not any(v > 0 for v in alphas):
            raise AtlasAuditError("entirely transparent sprite")
        alpha_positive += sum(v > 0 for v in alphas)
        alpha_partial += sum(0 < v < 255 for v in alphas)
        alpha_sha = hashlib.sha256(alphas).hexdigest()
        if distinct_alpha_masks and alpha_sha in alpha_hashes:
            raise AtlasAuditError("duplicate alpha silhouette")
        alpha_hashes.add(alpha_sha)
    if not isinstance(required_ids, (list, tuple, set, frozenset)):
        raise AtlasAuditError("required IDs must be a sequence")
    wanted = list(required_ids)
    if any(not isinstance(v, str) or not KEY.fullmatch(v) for v in wanted) or len(wanted) != len(set(wanted)):
        raise AtlasAuditError("invalid or duplicate required sprite/state ID")
    missing = sorted(set(wanted) - ids)
    if missing:
        raise AtlasAuditError("missing required sprite/state IDs: " + ", ".join(missing[:16]))
    return {
        "stage": "CANDIDATE_NOT_APPROVED",
        "atlas_sha256": expected_hash,
        "atlas_dimensions": [width, height],
        "sprite_count": len(ids),
        "alpha_nonzero_pixels": alpha_positive,
        "alpha_partial_pixels": alpha_partial,
        "estimated_rgba8_bytes": estimated_rgba_bytes,
        "estimated_rgba8_with_mips_bytes": estimated_mip_rgba_bytes,
        "max_memory_bytes": max_memory_bytes,
        "required_ids_present": True,
        "source_original_bytes_reverified": False,
        "estimated_not_measured_gpu_memory": True,
        "owner_art_approved": False,
        "licensed_rights_verified": False,
        "real_device_verified": False,
        "release_allowed": False,
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--candidate-dir", required=True, type=Path)
    p.add_argument("--required-id", action="append", default=[])
    p.add_argument("--budget-mib", type=int, default=64)
    p.add_argument("--distinct-alpha", action="store_true")
    args = p.parse_args(argv)
    try:
        _integer(args.budget_mib, "MiB budget", 1, 512)
        report = audit_candidate(
            args.candidate_dir, required_ids=args.required_id,
            max_memory_bytes=args.budget_mib * 1024 * 1024,
            distinct_alpha_masks=args.distinct_alpha)
    except (AtlasAuditError, OSError) as exc:
        print("FAIL: " + str(exc), file=sys.stderr)
        return 2
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
