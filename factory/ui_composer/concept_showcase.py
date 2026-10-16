"""VF-01/VF-07: offline five-game concept-screen PNG showcase.

Renders actual noninteractive original-math UI *concept images*, not
prefabs, imported game assets, flattened interactive UI or premium art.
Every screen remains CANDIDATE_NOT_OWNER_APPROVED. Python stdlib only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import stat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from factory.image_processor.png_pipeline import decode_png, encode_png, ImageError
from factory.visual_director.silhouette_kit import (
    PROFILES, SHAPES, STYLE_BIBLE, build_theme_kit,
)

PAGES = ("home", "gameplay", "world_map")
ALLOWED_SCALES = (1, 2)
BASE_WIDTH, BASE_HEIGHT = 360, 640
STAGE = "CANDIDATE_NOT_OWNER_APPROVED"
GENERATOR = "VF07_FIVE_GAME_CONCEPT_SCREENS_V01"
MAX_PACK_FILES = 15


class ShowcaseError(ValueError):
    pass


def _linked(path: Path) -> bool:
    if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
        return True
    try:
        meta = path.stat(follow_symlinks=False)
    except OSError:
        return False
    return bool(getattr(meta, "st_file_attributes", 0) &
                getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def _rgb(value: str) -> tuple[int, int, int]:
    if not isinstance(value, str) or len(value) != 7 or value[0] != "#":
        raise ShowcaseError("invalid draft theme RGB")
    try:
        return tuple(int(value[i:i + 2], 16) for i in (1, 3, 5))
    except ValueError as exc:
        raise ShowcaseError("invalid theme color") from exc


class Painter:
    def __init__(self, width: int, height: int, bg: tuple[int, int, int],
                 surface: tuple[int, int, int]):
        self.width, self.height = width, height
        self.buffer = bytearray(width * height * 4)
        for y in range(height):
            t = y / max(height - 1, 1)
            t = .22 + .48 * t
            r, g, b = (int(bg[i] * (1 - t) + surface[i] * t) for i in range(3))
            line = bytes((r, g, b, 255)) * width
            start = y * width * 4
            self.buffer[start:start + width * 4] = line

    def rect(self, x: int, y: int, w: int, h: int,
             rgb: tuple[int, int, int], opacity: int = 255):
        x0, x1 = max(0, x), min(self.width, x + w)
        y0, y1 = max(0, y), min(self.height, y + h)
        if x0 >= x1 or y0 >= y1 or not 0 <= opacity <= 255:
            return
        for row in range(y0, y1):
            for col in range(x0, x1):
                pos = (row * self.width + col) * 4
                for channel in range(3):
                    self.buffer[pos + channel] = (
                        rgb[channel] * opacity +
                        self.buffer[pos + channel] * (255 - opacity) + 127
                    ) // 255

    def disk(self, cx: int, cy: int, radius: int,
             rgb: tuple[int, int, int], opacity: int = 255, hollow=False):
        if radius <= 0:
            return
        left = max(0, cx - radius)
        top = max(0, cy - radius)
        right = min(self.width, cx + radius + 1)
        bottom = min(self.height, cy + radius + 1)
        inner = max(0, radius - max(2, radius // 7))
        for y in range(top, bottom):
            for x in range(left, right):
                squared = (x - cx) ** 2 + (y - cy) ** 2
                if squared > radius ** 2 or (hollow and squared < inner ** 2):
                    continue
                pos = (y * self.width + x) * 4
                for c in range(3):
                    self.buffer[pos + c] = (
                        rgb[c] * opacity + self.buffer[pos + c] *
                        (255 - opacity) + 127
                    ) // 255

    def tile(self, tile_rgba: bytes, source_side: int,
             x: int, y: int, side: int):
        for dy in range(side):
            py = y + dy
            if not 0 <= py < self.height:
                continue
            ty = min(source_side - 1, dy * source_side // side)
            for dx in range(side):
                px = x + dx
                if not 0 <= px < self.width:
                    continue
                tx = min(source_side - 1, dx * source_side // side)
                source = (ty * source_side + tx) * 4
                alpha = tile_rgba[source + 3]
                if alpha == 0:
                    continue
                dst = (py * self.width + px) * 4
                for c in range(3):
                    self.buffer[dst + c] = (
                        tile_rgba[source + c] * alpha +
                        self.buffer[dst + c] * (255 - alpha) + 127
                    ) // 255

    def png(self) -> bytes:
        return encode_png(self.width, self.height, bytes(self.buffer))


def _visual_motifs(paint: Painter, profile: str, accent: tuple[int, int, int],
                   unit: int, seed: int):
    # Different geometric environment languages, NOT just recolored templates.
    # Bubbles, garage rivets, dinosaur foliage, magical portals, toy confetti.
    for index in range(12):
        x = (31 + index * 73 + seed * 11) % BASE_WIDTH * unit
        y = (70 + index * 127 + seed * 7) % BASE_HEIGHT * unit
        if profile == "Coral_Rescue":
            paint.disk(x, y, (7 + index % 5 * 4) * unit, accent, 95, True)
        elif profile == "Garage_Legends":
            size = (4 + index % 3 * 2) * unit
            paint.rect(x - size, y - size, size * 2, size * 2, accent, 110)
            paint.disk(x, y, 2 * unit, (12, 20, 30), 190)
        elif profile == "Dino_Islands":
            paint.disk(x, y, (9 + index % 4 * 4) * unit, accent, 75)
            paint.rect(x, y, 3 * unit, 17 * unit, accent, 105)
        elif profile == "The_Fractured_Realms":
            paint.disk(x, y, (9 + index % 3 * 7) * unit, accent, 80, True)
            paint.disk(x, y, 2 * unit, accent, 180)
        else:
            paint.rect(x, y, (4 + index % 5 * 2) * unit,
                       (4 + index % 4 * 2) * unit, accent, 145)


def _labels(paint: Painter, unit: int, text: tuple[int, int, int],
            accent: tuple[int, int, int], page: str):
    # Semantic placeholder bars only. Actual text, Buttons, touch targets
    # and accessibility belong to real Unity uGUI, not to this PNG.
    paint.rect(24 * unit, 42 * unit, 145 * unit, 7 * unit, text, 220)
    paint.rect(24 * unit, 58 * unit, 92 * unit, 5 * unit, accent, 210)
    paint.rect(285 * unit, 44 * unit, 50 * unit, 21 * unit, accent, 180)
    paint.rect(22 * unit, 574 * unit, 316 * unit, 49 * unit,
               accent, 45)
    for x in (59, 138, 217, 296):
        paint.disk(x * unit, 601 * unit, 11 * unit, text, 115)


def _draw_gameplay(p: Painter, unit: int, tiles: dict[str, bytes],
                   color: tuple[int, int, int], surface: tuple[int, int, int],
                   seed: int):
    p.rect(22 * unit, 96 * unit, 316 * unit, 39 * unit, surface, 190)
    p.rect(32 * unit, 110 * unit, 223 * unit, 11 * unit, color, 205)
    p.rect(22 * unit, 151 * unit, 316 * unit, 398 * unit, surface, 200)
    side = 44 * unit
    for row in range(8):
        for col in range(6):
            x = (32 + col * 49) * unit
            y = (160 + row * 48) * unit
            p.rect(x, y, side, side, (4, 13, 27), 65)
            key = SHAPES[(row * 5 + col * 3 + seed) % 6]
            p.tile(tiles[key], 40, x + 2 * unit, y + 2 * unit, 40 * unit)
    # No score, matches, input handling or win-state generated.


def _draw_home(p: Painter, unit: int, tiles: dict[str, bytes],
               cta: tuple[int, int, int], surface: tuple[int, int, int],
               seed: int):
    p.disk(180 * unit, 258 * unit, 120 * unit, cta, 58, True)
    p.disk(180 * unit, 258 * unit, 97 * unit, cta, 48)
    for i, shape in enumerate(SHAPES):
        angle = math.tau * i / 6 - math.pi / 2
        x = int(180 + math.cos(angle) * 83 - 25) * unit
        y = int(258 + math.sin(angle) * 83 - 25) * unit
        p.tile(tiles[shape], 40, x, y, 52 * unit)
    p.rect(75 * unit, 425 * unit, 210 * unit, 57 * unit, cta, 220)
    p.rect(106 * unit, 442 * unit, 148 * unit, 16 * unit, surface, 165)
    for idx in range(3):
        p.disk((102 + 78 * idx) * unit, 516 * unit, 23 * unit, cta, 110, True)


def _draw_world(p: Painter, unit: int, tiles: dict[str, bytes],
                color: tuple[int, int, int], surface: tuple[int, int, int],
                seed: int):
    p.rect(27 * unit, 104 * unit, 306 * unit, 444 * unit, surface, 130)
    stops = ((180, 492), (93, 421), (245, 357),
             (120, 290), (238, 224), (164, 156))
    for i, (x, y) in enumerate(stops):
        if i:
            px, py = stops[i - 1]
            for step in range(1, 11):
                t = step / 10
                p.disk(int(px + (x - px) * t) * unit,
                       int(py + (y - py) * t) * unit,
                       3 * unit, color, 150)
        p.disk(x * unit, y * unit, 28 * unit, color, 140)
        p.tile(tiles[SHAPES[(i + seed) % 6]], 40,
               (x - 24) * unit, (y - 24) * unit, 48 * unit)


def render_preview(profile: str, page: str, scale: int = 1,
                   seed: int = 0) -> tuple[dict, bytes]:
    if profile not in PROFILES or page not in PAGES:
        raise ShowcaseError("unknown game/profile or conceptual screen")
    if type(scale) is not int or scale not in ALLOWED_SCALES:
        raise ShowcaseError("only 360x640 and 720x1280 viewport previews allowed")
    if type(seed) is not int or not 0 <= seed <= 9999:
        raise ShowcaseError("seed must be integer 0..9999")
    raw = STYLE_BIBLE.read_bytes()
    bible = json.loads(raw.decode("utf-8"))
    if bible.get("status") != "DRAFT_NOT_OWNER_APPROVED":
        raise ShowcaseError("Style Bible is no longer a nonapproved draft")
    entries = [x for x in bible.get("profiles", []) if x.get("id") == profile]
    if len(entries) != 1:
        raise ShowcaseError("invalid or duplicate draft profile")
    colors = entries[0]["palettes"]
    bg, surface = _rgb(colors["background"]), _rgb(colors["surface"])
    accent, cta, text = (_rgb(colors[k]) for k in ("accent", "cta", "text"))
    kit, sources = build_theme_kit(profile, side=40)
    tiles = {}
    for shape in SHAPES:
        w, h, data = decode_png(sources["tile_" + shape + ".png"])
        if (w, h) != (40, 40):
            raise ShowcaseError("silhouette source contract changed")
        tiles[shape] = data
    width, height = BASE_WIDTH * scale, BASE_HEIGHT * scale
    paint = Painter(width, height, bg, surface)
    _visual_motifs(paint, profile, accent, scale, seed)
    _labels(paint, scale, text, accent, page)
    if page == "home":
        _draw_home(paint, scale, tiles, cta, surface, seed)
    elif page == "gameplay":
        _draw_gameplay(paint, scale, tiles, accent, surface, seed)
    else:
        _draw_world(paint, scale, tiles, cta, surface, seed)
    png = paint.png()
    return {
        "profile_id": profile, "screen_key": page,
        "dimensions": [width, height],
        "png_sha256": hashlib.sha256(png).hexdigest(),
        "style_source_sha256": hashlib.sha256(raw).hexdigest(),
        "tile_kit_atlas_sha256": kit["atlas_sha256"],
        "seed": seed, "render_scale": scale,
        "interactive": False,
        "screen_state": "VISUAL_CONCEPT_NOT_INTERACTIVE"
    }, png


def build_showcase(scale: int = 1, seed: int = 0) -> tuple[dict, dict[str, bytes]]:
    """Fifteen source concept PNGs (five themes x three screens), no writes."""
    files = {}
    scenes = []
    for profile in PROFILES:
        for page in PAGES:
            row, png = render_preview(profile, page, scale, seed)
            filename = "preview_" + profile + "_" + page + ".png"
            row["file"] = filename
            scenes.append(row)
            files[filename] = png
    return {
        "schema_version": 1,
        "stage": STAGE,
        "generator": GENERATOR,
        "screens": scenes,
        "profile_ids": list(PROFILES),
        "screen_keys": list(PAGES),
        "file_count": len(files),
        "dimensions": [BASE_WIDTH * scale, BASE_HEIGHT * scale],
        "interactive_ui_enabled": False,
        "owner_visual_approval": False,
        "asset_rights_verified": False,
        "original_art": "MATHEMATICAL_CONCEPT_ONLY",
        "real_device_verified": False,
    }, files


def write_showcase(directory: Path, manifest: dict, images: dict[str, bytes]) -> None:
    if (manifest.get("stage") != STAGE or
            manifest.get("generator") != GENERATOR or
            manifest.get("file_count") != MAX_PACK_FILES or
            set(images) != {r.get("file") for r in manifest.get("screens", [])} or
            manifest.get("interactive_ui_enabled") is not False or
            manifest.get("owner_visual_approval") is not False or
            manifest.get("asset_rights_verified") is not False):
        raise ShowcaseError("invalid source candidate pack contract")
    for row in manifest["screens"]:
        name = row["file"]
        if (not isinstance(name, str) or "/" in name or "\\" in name or
                not name.startswith("preview_") or not name.endswith(".png")):
            raise ShowcaseError("unsafe candidate file name")
        if hashlib.sha256(images[name]).hexdigest() != row["png_sha256"]:
            raise ShowcaseError("candidate image SHA receipt changed")
    path = Path(directory)
    if (path.exists() or path.is_symlink() or
            not path.parent.is_dir() or
            any(_linked(x) for x in (path.parent, *path.parent.parents)) or
            path.parent.resolve(strict=True).is_relative_to(ROOT)):
        raise ShowcaseError("output must be NEW directory outside Git, no linked parents")
    path.mkdir()
    for key, raw in images.items():
        with (path / key).open("xb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
    with (path / "showcase_manifest.json").open("x", encoding="utf-8",
                                               newline="\n") as handle:
        json.dump(manifest, handle, sort_keys=True, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scale", type=int, choices=ALLOWED_SCALES, default=1)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args(argv)
    try:
        receipt, pngs = build_showcase(args.scale, args.seed)
        if args.output_dir is not None:
            write_showcase(args.output_dir, receipt, pngs)
        receipt["output_saved"] = args.output_dir is not None
        print(json.dumps(receipt, sort_keys=True, indent=2))
        return 0
    except (ShowcaseError, ImageError, OSError, ValueError) as exc:
        print("VF07_SHOWCASE_REJECTED: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
