"""VF-09 offline source sprite quality diagnostics.

Read-only and heuristic; never certifies rights, visual quality or device QA.
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
from factory.image_processor.png_pipeline import decode_png, ImageError, MAX_INPUT_BYTES

MAX_FILES = 32
MAX_BATCH_BYTES = 64 * 1024 * 1024
STAGE = "REVIEW_REQUIRED_NOT_OWNER_APPROVED"
PROFILES = ("Coral_Rescue", "Garage_Legends", "Dino_Islands",
            "The_Fractured_Realms", "Wonder_Pop")


class SpriteQaError(ValueError):
    pass


def _link(path: Path) -> bool:
    if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
        return True
    stat_result = path.stat(follow_symlinks=False)
    return bool(getattr(stat_result, "st_file_attributes", 0) &
                getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def sprite_metrics(width: int, height: int, pixels: bytes) -> dict:
    if (type(width) is not int or type(height) is not int or width < 1 or
            height < 1 or len(pixels) != width * height * 4):
        raise SpriteQaError("invalid pixel buffer")
    minx, miny, maxx, maxy = width, height, -1, -1
    visible = partial = border = transparent_colored = adjacent_black = 0
    unique = set()
    for y in range(height):
        for x in range(width):
            offset = (y * width + x) * 4
            r, g, b, alpha = pixels[offset:offset + 4]
            if alpha >= 16:
                visible += 1
                partial += int(alpha < 255)
                minx, miny = min(minx, x), min(miny, y)
                maxx, maxy = max(maxx, x), max(maxy, y)
                border += int(x == 0 or y == 0 or x == width - 1 or y == height - 1)
                if len(unique) <= 256:
                    unique.add((r, g, b))
            if alpha == 0:
                transparent_colored += int(bool(r or g or b))
                if not (r or g or b):
                    neighbors = []
                    if x > 0: neighbors.append(offset - 4)
                    if x + 1 < width: neighbors.append(offset + 4)
                    if y > 0: neighbors.append(offset - width * 4)
                    if y + 1 < height: neighbors.append(offset + width * 4)
                    adjacent_black += int(any(pixels[n + 3] >= 16 for n in neighbors))
    warnings = []
    if not visible:
        warnings.append("EMPTY_ALPHA")
    if border:
        warnings.append("CANVAS_BOUNDARY_TOUCH")
    if visible and visible * 8 < width * height:
        warnings.append("SPARSE_VISIBLE_CANVAS")
    if width > 2048 or height > 2048:
        warnings.append("LARGE_TEXTURE_HEURISTIC")
    if adjacent_black and partial:
        warnings.append("POSSIBLE_BLACK_MATTE_FRINGE")
    return {
        "dimensions": [width, height],
        "visible_bbox_top_left": None if not visible else
            [minx, miny, maxx - minx + 1, maxy - miny + 1],
        "alpha_coverage_basis_points": visible * 10000 // (width * height),
        "visible_pixels": visible, "partial_alpha_visible_pixels": partial,
        "edge_visible_pixels": border,
        "transparent_colored_pixels": transparent_colored,
        "transparent_black_adjacent_visible": adjacent_black,
        "distinct_visible_rgb_capped": min(len(unique), 257),
        "warnings": warnings,
    }


def contrast_ratio(fg: str, bg: str) -> float:
    def lum(color):
        if not isinstance(color, str) or re.fullmatch(r"#[0-9A-Fa-f]{6}", color) is None:
            raise SpriteQaError("invalid Style Bible RGB color")
        rgb = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        linear = [c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4
                  for c in rgb]
        return sum(x * factor for x, factor in zip(linear, (.2126, .7152, .0722)))
    a, b = lum(fg), lum(bg)
    return (max(a, b) + .05) / (min(a, b) + .05)


def palette_review(profile: str) -> dict:
    if profile not in PROFILES:
        raise SpriteQaError("unknown profile")
    data = json.loads((ROOT / "factory/visual_director/style_profiles.v1.json").read_text(
        encoding="utf-8"))
    if data.get("status") != "DRAFT_NOT_OWNER_APPROVED":
        raise SpriteQaError("Style Bible contract drift")
    matches = [row for row in data["profiles"] if row.get("id") == profile]
    if len(matches) != 1:
        raise SpriteQaError("missing or duplicate profile")
    colors = matches[0]["palettes"]
    pairs = (("text_on_surface", "text", "surface", 4.5),
             ("cta_label_on_cta", "cta_label", "cta", 4.5),
             ("accent_on_background", "accent", "background", 3.0))
    checks = []
    for label, a, b, limit in pairs:
        ratio = contrast_ratio(colors[a], colors[b])
        checks.append({"pair": label, "ratio": round(ratio, 3),
                       "advisory_minimum": limit, "review": ratio < limit})
    return {"profile_id": profile, "stage": "DRAFT_NOT_OWNER_APPROVED",
            "contrast_checks": checks}


def audit_files(sources: list[Path], profile: str | None = None) -> dict:
    if not isinstance(sources, list) or not 1 <= len(sources) <= MAX_FILES:
        raise SpriteQaError("1..32 sources required")
    seen, names, items, total = set(), set(), [], 0
    for source in sources:
        path = Path(source)
        if not path.is_file() or _link(path) or path.suffix.lower() != ".png":
            raise SpriteQaError("regular PNG source required")
        if any(_link(parent) for parent in path.parents):
            raise SpriteQaError("linked source directory is forbidden")
        canonical = path.resolve(strict=True)
        if canonical in seen or path.name in names:
            raise SpriteQaError("duplicate source/filename")
        seen.add(canonical)
        names.add(path.name)
        if path.stat().st_size > MAX_INPUT_BYTES:
            raise SpriteQaError("oversized source")
        raw = path.read_bytes()
        total += len(raw)
        if total > MAX_BATCH_BYTES:
            raise SpriteQaError("combined source limit exceeded")
        try:
            w, h, pixels = decode_png(raw)
        except ImageError as err:
            raise SpriteQaError("invalid source PNG: " + str(err)) from err
        items.append({"filename": path.name,
                      "source_sha256_recorded": hashlib.sha256(raw).hexdigest(),
                      **sprite_metrics(w, h, pixels)})
    report = {
        "schema_version": 1, "stage": STAGE,
        "generator": "VF09_PIXEL_HEALTH_V01", "file_count": len(items),
        "total_source_bytes": total, "sprites": items,
        "warning_count": sum(len(item["warnings"]) for item in items),
        "source_rights_verified": False,
    }
    if profile is not None:
        report["palette_review"] = palette_review(profile)
        report["warning_count"] += sum(
            int(c["review"]) for c in report["palette_review"]["contrast_checks"])
    return report


def save_report_once(report: dict, output: Path) -> None:
    target = Path(output)
    if target.resolve().is_relative_to(ROOT) or target.exists() or target.is_symlink():
        raise SpriteQaError("output must be a new external file")
    if not target.parent.is_dir() or any(_link(x) for x in (target.parent, *target.parent.parents)):
        raise SpriteQaError("unsafe report output directory")
    with target.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(report, stream, sort_keys=True, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", action="append", type=Path, required=True)
    parser.add_argument("--profile", choices=PROFILES)
    parser.add_argument("--output-file", type=Path)
    args = parser.parse_args(argv)
    try:
        report = audit_files(args.source, args.profile)
        if args.output_file:
            save_report_once(report, args.output_file)
            report = {"stage": STAGE, "file_count": report["file_count"],
                      "warning_count": report["warning_count"], "report_written": True}
        print(json.dumps(report, sort_keys=True, indent=2))
        return 0
    except (SpriteQaError, OSError, ValueError) as exc:
        print("VF09_REJECTED: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
