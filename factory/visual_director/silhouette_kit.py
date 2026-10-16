"""VF-01/VF-04: mathematically authored six-silhouette theme tile candidates.

These are intentionally original PROTOTYPE sprites, not premium art or a
replacement for commissioned/licensed production textures. No providers,
network, owner-rights inference, Unity import edits or game gameplay rules.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import stat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from factory.image_processor.png_pipeline import encode_png, ImageError

STYLE_BIBLE = ROOT / "factory/visual_director/style_profiles.v1.json"
PROFILES = ("Coral_Rescue", "Garage_Legends", "Dino_Islands",
            "The_Fractured_Realms", "Wonder_Pop")
SHAPES = ("circle", "triangle", "diamond", "star", "crescent", "shield")
MAX_SIDE = 128
MIN_SIDE = 24
HEX = re.compile(r"#[A-Fa-f0-9]{6}\Z")


class PrototypeError(ValueError):
    pass


def _linked(path: Path) -> bool:
    if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
        return True
    try:
        metadata = path.stat(follow_symlinks=False)
    except OSError:
        return False
    return bool(getattr(metadata, "st_file_attributes", 0) &
                getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def _style(profile: str) -> tuple[dict, str]:
    if profile not in PROFILES:
        raise PrototypeError("unknown theme profile")
    raw = STYLE_BIBLE.read_bytes()
    bible = json.loads(raw.decode("utf-8"))
    if (bible.get("schema_version") != 1 or
            bible.get("status") != "DRAFT_NOT_OWNER_APPROVED" or
            bible.get("common", {}).get("tile_silhouettes") != list(SHAPES)):
        raise PrototypeError("draft-only Style Bible silhouette contract changed")
    rows = [x for x in bible["profiles"] if x.get("id") == profile]
    if len(rows) != 1:
        raise PrototypeError("missing or duplicated theme profile")
    palette = rows[0]["palettes"]
    for name in ("accent", "cta", "surface"):
        if not isinstance(palette.get(name), str) or HEX.fullmatch(palette[name]) is None:
            raise PrototypeError("invalid draft color " + name)
    return palette, hashlib.sha256(raw).hexdigest()


def _rgb(hex_color: str) -> tuple[int, int, int]:
    return tuple(int(hex_color[i:i + 2], 16) for i in (1, 3, 5))


def _polygon(x: float, y: float, vertices: tuple[tuple[float, float], ...]) -> bool:
    odd = False
    for i, (ax, ay) in enumerate(vertices):
        bx, by = vertices[(i + 1) % len(vertices)]
        if (ay > y) != (by > y) and x < (bx - ax) * (y - ay) / (by - ay) + ax:
            odd = not odd
    return odd


def _inside(shape: str, x: float, y: float) -> bool:
    if shape == "circle":
        return x * x + y * y <= .67 ** 2
    if shape == "triangle":
        return _polygon(x, y, ((0, -.82), (.83, .70), (-.83, .70)))
    if shape == "diamond":
        return abs(x) / .85 + abs(y) / .88 <= 1
    if shape == "star":
        points = []
        for i in range(10):
            theta = -math.pi / 2 + math.pi * i / 5
            r = .86 if i % 2 == 0 else .39
            points.append((math.cos(theta) * r, math.sin(theta) * r))
        return _polygon(x, y, tuple(points))
    if shape == "crescent":
        return ((x + .06) ** 2 + y * y < .79 ** 2
                and (x - .32) ** 2 + (y + .10) ** 2 >= .66 ** 2)
    if shape == "shield":
        return _polygon(x, y, ((-.74, -.69), (.74, -.69), (.72, .19),
                                (.45, .56), (0, .88), (-.45, .56), (-.72, .19)))
    raise PrototypeError("unknown common silhouette")


def _raster(shape: str, size: int, palette: dict) -> bytes:
    accent = _rgb(palette["accent"])
    gold = _rgb(palette["cta"])
    pixels = bytearray(size * size * 4)
    samples = ((.25, .25), (.75, .25), (.25, .75), (.75, .75))
    for y in range(size):
        for x in range(size):
            covered = 0
            for u, v in samples:
                xx, yy = 2 * (x + u) / size - 1, 2 * (y + v) / size - 1
                covered += int(_inside(shape, xx, yy))
            if not covered:
                continue
            # A mild, deterministic highlight. Shape is primary cue, not hue.
            high = max(0., min(1., (.78 - y / size) * .50 + .12))
            offset = (y * size + x) * 4
            for channel in range(3):
                shade = accent[channel] * (1 - high) + gold[channel] * high
                pixels[offset + channel] = int(max(0, min(255, shade + .5)))
            pixels[offset + 3] = min(255, covered * 255 // 4)
    return bytes(pixels)


def build_theme_kit(profile: str, side: int = 64) -> tuple[dict, dict[str, bytes]]:
    """Generate candidate PNG bytes entirely in memory. No file writes."""
    if type(side) is not int or not MIN_SIDE <= side <= MAX_SIDE:
        raise PrototypeError("tile size must be integer 24..128")
    palette, source_sha = _style(profile)
    atlas_w, atlas_h = 3 * side, 2 * side
    atlas = bytearray(atlas_w * atlas_h * 4)
    outputs = {}
    frames = []
    for n, shape in enumerate(SHAPES):
        rgba = _raster(shape, side, palette)
        png = encode_png(side, side, rgba)
        filename = "tile_" + shape + ".png"
        outputs[filename] = png
        ox, oy = n % 3 * side, n // 3 * side
        for row in range(side):
            source = row * side * 4
            destination = ((oy + row) * atlas_w + ox) * 4
            atlas[destination:destination + side * 4] = rgba[source:source + side * 4]
        frames.append({
            "shape": shape,
            "file": filename,
            "file_sha256": hashlib.sha256(png).hexdigest(),
            "rgba_sha256": hashlib.sha256(rgba).hexdigest(),
            "pixel_rect_top_left": [ox, oy, side, side]
        })
    atlas_png = encode_png(atlas_w, atlas_h, bytes(atlas))
    outputs["tile_atlas.png"] = atlas_png
    manifest = {
        "schema_version": 1,
        "stage": "CANDIDATE_NOT_OWNER_APPROVED",
        "generator": "VF04_SIX_SILHOUETTE_TILE_KIT_V01",
        "profile_id": profile,
        "style_source_sha256": source_sha,
        "silhouette_keys": list(SHAPES),
        "side": side,
        "format": "RGBA8_UNROTATED",
        "atlas_path": "tile_atlas.png",
        "atlas_dimensions": [atlas_w, atlas_h],
        "atlas_sha256": hashlib.sha256(atlas_png).hexdigest(),
        "tiles": frames,
        "original_art": "MATHEMATICAL_PROTOTYPE_NOT_OWNER_ART",
        "asset_rights_verified": False,
        "gameplay_bindings_enabled": False,
        "owner_visual_approval": False
    }
    return manifest, outputs


def write_once(path: Path, manifest: dict, pngs: dict[str, bytes]) -> None:
    folder = Path(path)
    if folder.exists() or folder.is_symlink():
        raise PrototypeError("refusing to overwrite existing asset output")
    parent = folder.parent
    if (not parent.is_dir() or
            any(_linked(p) for p in (parent, *parent.parents)) or
            parent.resolve(strict=True).is_relative_to(ROOT)):
        raise PrototypeError("candidate output parent must be existing external real directory")
    folder.mkdir()
    payloads = dict(pngs)
    payloads["tile_manifest.json"] = (
        json.dumps(manifest, sort_keys=True, indent=2) + "\n").encode("utf-8")
    for filename, data in payloads.items():
        with (folder / filename).open("xb") as target:
            target.write(data)
            target.flush()
            os.fsync(target.fileno())


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=PROFILES, required=True)
    parser.add_argument("--side", type=int, default=64)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args(argv)
    try:
        manifest, pngs = build_theme_kit(args.profile, args.side)
        if args.output_dir is not None:
            write_once(args.output_dir, manifest, pngs)
        manifest["output_saved"] = args.output_dir is not None
        print(json.dumps(manifest, sort_keys=True, indent=2))
        return 0
    except (PrototypeError, ImageError, OSError, ValueError) as exc:
        print("VF04_SIX_SHAPES_REJECTED: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
