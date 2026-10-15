"""VF-04 deterministic, bounded alpha-aware sprite atlas candidates.

No third-party services or image libraries. The original RGBA sprite bytes remain
immutable; every atlas must be reviewed before catalog approval/Unity export.
Only strict supported PNGs from png_pipeline.decode_png are accepted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from factory.image_processor.png_pipeline import (
    ImageError, MAX_INPUT_BYTES, decode_png, encode_png
)

MAX_SPRITES = 128
MAX_ATLAS_SIDE = 4096
MAX_ATLAS_PIXELS = 16_777_216
ASSET_KEY = re.compile(r"[a-z][a-z0-9_.-]{0,99}\Z")


@dataclass(frozen=True)
class Sprite:
    key: str
    width: int
    height: int
    pixels: bytes
    sha256: str


def _load_sources(sources: Mapping[str, Path]) -> list[Sprite]:
    if not isinstance(sources, dict) or not 1 <= len(sources) <= MAX_SPRITES:
        raise ImageError("sprite atlas requires 1 to 128 explicitly named originals")
    loaded = []
    for key, name in sources.items():
        if not isinstance(key, str) or not ASSET_KEY.fullmatch(key):
            raise ImageError("asset key must be a lowercase safe semantic slug")
        path = Path(name)
        if path.is_symlink() or not path.is_file() or path.suffix.lower() != ".png":
            raise ImageError("atlas input must be a regular PNG original, not a symlink")
        if path.stat().st_size > MAX_INPUT_BYTES:
            raise ImageError("atlas input exceeds bounded source size")
        raw = path.read_bytes()
        width, height, pixels = decode_png(raw)
        loaded.append(Sprite(key, width, height, pixels,
                             hashlib.sha256(raw).hexdigest()))
    return sorted(loaded, key=lambda item: (-item.height, -item.width, item.key))


def _pack_shelves(sprites: list[Sprite], padding: int,
                  max_width: int, max_height: int) -> tuple[int, int, list[tuple[Sprite, int, int]]]:
    """Deterministic shelf pack with top-left source pixel bounds."""
    current_x = 0
    current_y = 0
    shelf_height = 0
    occupied_width = 0
    placements = []
    for sprite in sprites:
        box_w = sprite.width + 2 * padding
        box_h = sprite.height + 2 * padding
        if box_w > max_width or box_h > max_height:
            raise ImageError("a sprite cannot fit requested atlas dimensions")
        if current_x + box_w > max_width:
            current_y += shelf_height
            current_x = 0
            shelf_height = 0
        if current_y + box_h > max_height:
            raise ImageError("atlas overflow: reduce artwork or use multiple atlases")
        x = current_x + padding
        y = current_y + padding
        placements.append((sprite, x, y))
        current_x += box_w
        shelf_height = max(shelf_height, box_h)
        occupied_width = max(occupied_width, current_x)
    final_h = current_y + shelf_height
    if occupied_width * final_h > MAX_ATLAS_PIXELS:
        raise ImageError("atlas would exceed maximum RGBA pixel budget")
    return occupied_width, final_h, placements


def _safe_candidate_folder(directory: Path, sprites: Mapping[str, Path]) -> Path:
    directory = Path(directory)
    repo_root = Path(__file__).resolve().parents[2]
    root = directory.resolve()
    if directory.is_symlink() or root.is_relative_to(repo_root):
        raise ImageError("candidate atlas output must be outside GitHub repository")
    if any(Path(p).resolve().is_relative_to(root) for p in sprites.values()):
        raise ImageError("atlas candidate output cannot contain any input original")
    if directory.exists() and not directory.is_dir():
        raise ImageError("atlas candidate destination must be a directory")
    return directory


def create_atlas_candidate(sources: Mapping[str, Path], directory: Path, *,
                           padding: int = 2, extrude: int = 1,
                           max_width: int = 2048,
                           max_height: int = 2048) -> dict:
    if (type(padding) is not int or not 0 <= padding <= 16
            or type(extrude) is not int or not 0 <= extrude <= padding):
        raise ImageError("padding must be 0..16 and extrusion <= padding")
    if (type(max_width) is not int or type(max_height) is not int
            or not 1 <= max_width <= MAX_ATLAS_SIDE
            or not 1 <= max_height <= MAX_ATLAS_SIDE
            or max_width * max_height > MAX_ATLAS_PIXELS):
        raise ImageError("maximum atlas size exceeds memory budget")
    folder = _safe_candidate_folder(Path(directory), sources)
    sprites = _load_sources(sources)
    width, height, placements = _pack_shelves(sprites, padding, max_width, max_height)
    canvas = bytearray(width * height * 4)
    atlas_entries = []
    for sprite, x, y in placements:
        # RGBA full alpha pixel copying. PNG rows are top-down.
        for row in range(sprite.height):
            src = row * sprite.width * 4
            dest = ((y + row) * width + x) * 4
            canvas[dest:dest + sprite.width * 4] = sprite.pixels[src:src + sprite.width * 4]
        # Edge extrusion duplicates source pixels, including their original alpha.
        # No scaled/blurred/resampled pixels are ever introduced into the sprite rect.
        for offset_y in range(-extrude, sprite.height + extrude):
            safe_y = min(sprite.height - 1, max(0, offset_y))
            for offset_x in range(-extrude, sprite.width + extrude):
                if 0 <= offset_x < sprite.width and 0 <= offset_y < sprite.height:
                    continue
                safe_x = min(sprite.width - 1, max(0, offset_x))
                src = (safe_y * sprite.width + safe_x) * 4
                dst = ((y + offset_y) * width + x + offset_x) * 4
                canvas[dst:dst + 4] = sprite.pixels[src:src + 4]
        atlas_entries.append({
            "asset_id": sprite.key,
            "original_sha256": sprite.sha256,
            "width": sprite.width, "height": sprite.height,
            "pixel_rect_top_left": [x, y, sprite.width, sprite.height],
            "uv_rect_bottom_left": [x / width, (height - y - sprite.height) / height,
                                    sprite.width / width, sprite.height / height],
            "rotated": False,
        })
    atlas_png = encode_png(width, height, bytes(canvas))
    manifest = {
        "schema_version": 1,
        "stage": "CANDIDATE_NOT_APPROVED",
        "generator": "VF04_SHELF_PACK_V01",
        "width": width, "height": height,
        "padding": padding, "extrude": extrude,
        "format": "RGBA8_UNROTATED",
        "atlas_path": "atlas.png",
        "atlas_sha256": hashlib.sha256(atlas_png).hexdigest(),
        "sprites": sorted(atlas_entries, key=lambda entry: entry["asset_id"]),
    }
    payloads = {
        "atlas.png": atlas_png,
        "atlas_manifest.json": (json.dumps(
            manifest, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
        ).encode("utf-8")
    }
    if folder.exists() and any((folder / name).exists() or
                               (folder / name).is_symlink() for name in payloads):
        raise ImageError("refusing to overwrite existing candidate atlas")
    folder.mkdir(parents=True, exist_ok=True)
    if folder.is_symlink():
        raise ImageError("unsafe output symlink")
    newly_created = []
    try:
        for name, content in payloads.items():
            target = folder / name
            with target.open("xb") as stream:
                newly_created.append(target)
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
    except OSError:
        # Only delete files created by this call, never user originals or other candidates.
        for path in newly_created:
            path.unlink(missing_ok=True)
        raise
    return manifest


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-manifest", type=Path, required=True,
                        help="UTF-8 JSON object mapping semantic sprite IDs to PNG paths")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--padding", type=int, default=2)
    parser.add_argument("--extrude", type=int, default=1)
    parser.add_argument("--max-width", type=int, default=2048)
    parser.add_argument("--max-height", type=int, default=2048)
    args = parser.parse_args(argv)
    try:
        manifest = json.loads(args.input_manifest.read_text(encoding="utf-8"))
        if not isinstance(manifest, dict):
            raise ImageError("input-manifest must be a semantic ID -> PNG path mapping")
        sources = {}
        for key, value in manifest.items():
            if not isinstance(value, str):
                raise ImageError("sprite path values must be strings")
            source = Path(value)
            if not source.is_absolute():
                source = args.input_manifest.parent / source
            sources[key] = source
        result = create_atlas_candidate(
            sources, args.output_dir, padding=args.padding, extrude=args.extrude,
            max_width=args.max_width, max_height=args.max_height
        )
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0
    except (ImageError, ValueError, OSError, json.JSONDecodeError) as exc:
        parser.exit(2, "VF04_ATLAS_REJECTED: " + str(exc) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
