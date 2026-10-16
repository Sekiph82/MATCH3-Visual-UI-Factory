"""VF-04: offline original-layer RGBA scene compositor (candidate-only).

Exact-source hash pins, explicit layer ordering, clipped top-left coordinates
and deterministic straight-alpha 'source over' blending. Never reads a game
repo, changes original files, generates ownership receipts or auto-approves art.
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

MAX_LAYERS = 16
MAX_SOURCE_BYTES = 64 * 1024 * 1024
MAX_CANVAS_PIXELS = 4_194_304
MAX_CANVAS_SIDE = 2048
ASSET_KEY = re.compile(r"[a-z][a-z0-9_.-]{0,99}\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
HEX = re.compile(r"#[0-9a-fA-F]{6}\Z")
PROFILES = frozenset(("Coral_Rescue", "Garage_Legends", "Dino_Islands",
                      "The_Fractured_Realms", "Wonder_Pop"))


class CompositorError(ValueError):
    pass


def _linked(path: Path) -> bool:
    if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
        return True
    try:
        info = path.stat(follow_symlinks=False)
    except OSError:
        return False
    return bool(getattr(info, "st_file_attributes", 0) &
                getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def _safe_file(path: Path, *, outside_repo: bool = True) -> Path:
    path = Path(path)
    if not path.is_file() or _linked(path) or any(_linked(p) for p in path.parents):
        raise CompositorError("source must be an existing nonlinked regular file")
    real = path.resolve(strict=True)
    if outside_repo and real.is_relative_to(ROOT):
        raise CompositorError("source originals must remain outside checkout")
    if path.stat().st_size > MAX_INPUT_BYTES:
        raise CompositorError("input exceeds 64 MiB individual limit")
    return real


def _safe_output(folder: Path, originals: list[Path]) -> Path:
    folder = Path(folder)
    if folder.exists() or folder.is_symlink():
        raise CompositorError("candidate destination already exists")
    if (not folder.parent.is_dir() or
            any(_linked(p) for p in (folder.parent, *folder.parent.parents))):
        raise CompositorError("candidate destination parent must be real directory")
    parent = folder.parent.resolve(strict=True)
    if parent.is_relative_to(ROOT):
        raise CompositorError("output must be outside Git checkout")
    # The newly created folder can't contain any existing input file.
    if any(x.is_relative_to(folder.resolve()) for x in originals):
        raise CompositorError("output cannot contain original art sources")
    return folder


def _manifest(data: bytes) -> dict:
    if len(data) > 128 * 1024:
        raise CompositorError("compositor manifest exceeds 128KiB")
    try:
        spec = json.loads(data.decode("utf-8"), object_pairs_hook=_unique)
    except (ValueError, UnicodeError) as exc:
        raise CompositorError("invalid or duplicate JSON manifest keys") from exc
    if (not isinstance(spec, dict) or
            set(spec) != {"schema_version", "stage", "profile_id",
                          "width", "height", "background", "layers"} or
            type(spec["schema_version"]) is not int or
            spec["schema_version"] != 1 or
            spec["stage"] != "CANDIDATE_NOT_OWNER_APPROVED" or
            not isinstance(spec["profile_id"], str) or
            spec["profile_id"] not in PROFILES):
        raise CompositorError("unknown or approved compositor contract")
    w, h = spec["width"], spec["height"]
    if (type(w) is not int or type(h) is not int or
            not 1 <= w <= MAX_CANVAS_SIDE or
            not 1 <= h <= MAX_CANVAS_SIDE or
            w * h > MAX_CANVAS_PIXELS):
        raise CompositorError("canvas dimensions exceed approved authoring budget")
    if (spec["background"] is not None and
            (not isinstance(spec["background"], str) or
             HEX.fullmatch(spec["background"]) is None)):
        raise CompositorError("background must be hex RGB or null for transparent")
    if (not isinstance(spec["layers"], list) or
            not 1 <= len(spec["layers"]) <= MAX_LAYERS):
        raise CompositorError("expected one to 16 sorted source layers")
    seen = set()
    for layer in spec["layers"]:
        if not isinstance(layer, dict) or set(layer) != {
                "id", "file", "sha256", "x", "y", "opacity"}:
            raise CompositorError("layer requires exact known fields")
        key, rel, digest = layer["id"], layer["file"], layer["sha256"]
        if (not isinstance(key, str) or not ASSET_KEY.fullmatch(key)
                or key in seen or not isinstance(rel, str) or not rel
                or len(rel) > 255 or rel.startswith("/") or "\\" in rel
                or ":" in rel or "\x00" in rel
                or any(p in ("", ".", "..") for p in rel.split("/"))
                or not rel.lower().endswith(".png")
                or not isinstance(digest, str) or SHA256.fullmatch(digest) is None):
            raise CompositorError("unsafe layer id/path/hash")
        seen.add(key)
        if (any(type(layer[k]) is not int for k in ("x", "y", "opacity")) or
                any(abs(layer[k]) > 8192 for k in ("x", "y")) or
                not 0 <= layer["opacity"] <= 255):
            raise CompositorError("layer placement or opacity invalid")
    return spec


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise CompositorError("duplicate JSON key " + key)
        result[key] = value
    return result


def _color_from_hex(value: str | None) -> bytes:
    return b"\0\0\0\0" if value is None else bytes(
        [int(value[1:3], 16), int(value[3:5], 16), int(value[5:7], 16), 255]
    )


def _composite(canvas: bytearray, width: int, height: int, source: bytes,
               source_width: int, source_height: int,
               x: int, y: int, opacity: int) -> None:
    if opacity == 0:
        return
    left, right = max(0, x), min(width, x + source_width)
    top, bottom = max(0, y), min(height, y + source_height)
    if right <= left or bottom <= top:
        return
    for target_y in range(top, bottom):
        source_y = target_y - y
        for target_x in range(left, right):
            src = (source_y * source_width + target_x - x) * 4
            dst = (target_y * width + target_x) * 4
            src_a = (source[src + 3] * opacity + 127) // 255
            if src_a == 0:
                continue
            dst_a = canvas[dst + 3]
            numerator = src_a * 255 + dst_a * (255 - src_a)
            for channel in range(3):
                channel_num = (source[src + channel] * src_a * 255 +
                               canvas[dst + channel] * dst_a * (255 - src_a))
                canvas[dst + channel] = (channel_num + numerator // 2) // numerator
            canvas[dst + 3] = (numerator + 127) // 255


def render_candidate(manifest_file: Path, original_root: Path) -> tuple[dict, bytes]:
    """Make pixels in memory, no IO writes; layers stack in declared order."""
    manifest_file = _safe_file(Path(manifest_file))
    original_root = Path(original_root)
    if not original_root.is_dir() or _linked(original_root) or any(
            _linked(p) for p in original_root.parents):
        raise CompositorError("original source root must be a real directory")
    source_root = original_root.resolve(strict=True)
    if source_root.is_relative_to(ROOT):
        raise CompositorError("original source root must be outside repository")
    manifest_raw = manifest_file.read_bytes()
    spec = _manifest(manifest_raw)
    width, height = spec["width"], spec["height"]
    background = _color_from_hex(spec["background"])
    buffer = bytearray(background * (width * height))
    seen_paths, source_bytes, records = set(), 0, []
    for depth, layer in enumerate(spec["layers"]):
        candidate = original_root
        for part in layer["file"].split("/"):
            candidate = candidate / part
            if _linked(candidate):
                raise CompositorError("linked original or source directory")
        source_path = _safe_file(candidate)
        if not source_path.is_relative_to(source_root):
            raise CompositorError("layer escapes source root")
        if source_path in seen_paths:
            raise CompositorError("duplicate input source file")
        seen_paths.add(source_path)
        raw = source_path.read_bytes()
        source_bytes += len(raw)
        if source_bytes > MAX_SOURCE_BYTES:
            raise CompositorError("combined originals exceed 64 MiB")
        digest = hashlib.sha256(raw).hexdigest()
        if digest != layer["sha256"]:
            raise CompositorError("original bytes changed since manifest pin")
        try:
            sw, sh, rgba = decode_png(raw)
        except ImageError as exc:
            raise CompositorError("unsupported source PNG: " + str(exc)) from exc
        _composite(buffer, width, height, rgba, sw, sh,
                   layer["x"], layer["y"], layer["opacity"])
        records.append({
            "id": layer["id"], "source_sha256": digest,
            "source_size": [sw, sh], "top_left": [layer["x"], layer["y"]],
            "opacity_byte": layer["opacity"], "draw_order": depth
        })
    png = encode_png(width, height, bytes(buffer))
    return {
        "schema_version": 1,
        "stage": "CANDIDATE_NOT_OWNER_APPROVED",
        "generator": "VF04_RGBA_LAYER_COMPOSITOR_V01",
        "profile_id": spec["profile_id"],
        "original_manifest_sha256": hashlib.sha256(manifest_raw).hexdigest(),
        "image_path": "scene.png",
        "image_sha256": hashlib.sha256(png).hexdigest(),
        "dimensions": [width, height],
        "source_bytes": source_bytes,
        "layers": records,
        "original_rights_verified": False,
        "owner_visual_approved": False
    }, png


def write_candidate(directory: Path, receipt: dict, png: bytes,
                    source_paths: list[Path]) -> None:
    directory = _safe_output(directory, source_paths)
    directory.mkdir()
    payloads = {
        "scene.png": png,
        "scene_receipt.json": (json.dumps(receipt, sort_keys=True, indent=2) +
                               "\n").encode("utf-8")
    }
    for name, raw in payloads.items():
        with (directory / name).open("xb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args(argv)
    try:
        receipt, png = render_candidate(args.manifest, args.source_root)
        if args.output_dir is not None:
            # render_candidate has already verified every original source.
            write_candidate(args.output_dir, receipt, png, [args.manifest])
            receipt["output_saved"] = True
        else:
            receipt["output_saved"] = False
        print(json.dumps(receipt, indent=2, sort_keys=True))
        return 0
    except (CompositorError, ImageError, ValueError, OSError) as exc:
        print("VF04_SCENE_COMPOSITOR_REJECTED: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
