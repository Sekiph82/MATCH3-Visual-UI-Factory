"""VF-06 deterministic procedural VFX sprite-sheet candidate authoring.

Generates mathematical bubble/ring/spark/burst/dust animations from the five
existing AUTHORING_ONLY presets. No donor art, providers, model inference,
gameplay callbacks, ownership approval or automatic shipping. Python stdlib.
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

PRESETS = ROOT / "factory/vfx_builder/presets.v1.json"
COLORS = {
    "BubbleRise": "#64E5FF",
    "MatchBurst": "#FFD260",
    "StarSparkle": "#FFF2B4",
    "SoftDrift": "#C3EBEA",
    "PortalPulse": "#AF92FF",
}
MAX_FRAMES = 32
MAX_SIDE = 128
MAX_ATLAS_PIXELS = 2_097_152
HEX_COLOR = re.compile(r"#[0-9a-fA-F]{6}\Z")


class VfxCandidateError(ValueError):
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


def _destination(destination: Path) -> Path:
    path = Path(destination)
    if path.exists() or path.is_symlink():
        raise VfxCandidateError("output directory already exists, never overwrite")
    parent = path.parent
    if not parent.is_dir() or any(_linked(x) for x in
                                  (parent, *parent.parents)):
        raise VfxCandidateError("output must be beneath an existing real directory")
    canonical = parent.resolve(strict=True)
    if canonical.is_relative_to(ROOT):
        raise VfxCandidateError("candidate output must be outside Git repository")
    return path


def _preset(name: str) -> tuple[dict, str]:
    if name not in COLORS:
        raise VfxCandidateError("unknown authoring-only VFX preset")
    data = PRESETS.read_bytes()
    settings = json.loads(data.decode("utf-8"))
    if (settings.get("schema_version") != 1 or
            settings.get("stage") != "AUTHORING_ONLY" or
            settings.get("engine_side_effects_allowed") is not False):
        raise VfxCandidateError("VFX preset safety authority changed")
    matches = [p for p in settings["presets"] if p.get("id") == name]
    if len(matches) != 1:
        raise VfxCandidateError("preset missing or duplicated")
    preset = matches[0]
    if (preset.get("events") != ["VIEW_ONLY"] or
            preset.get("state") != "CANDIDATE_NOT_OWNER_APPROVED" or
            not preset.get("reduced_motion_fallback")):
        raise VfxCandidateError("VFX cannot generate gameplay state/effects")
    return preset, hashlib.sha256(data).hexdigest()


def _glow(distance: float, spread: float) -> float:
    return math.exp(-((distance / max(spread, .0001)) ** 2) * 3.5)


def _field(name: str, x: float, y: float, t: float, seed: int) -> float:
    radius = math.hypot(x, y)
    angle = math.atan2(y, x)
    if name == "BubbleRise":
        # Single rising ring with an offset glossy specular dot.
        cy = .58 - 1.18 * t
        cx = .09 * math.sin(t * math.tau + seed * .13)
        r = math.hypot(x - cx, y - cy)
        fade = math.sin(math.pi * max(0., min(1., t))) ** .5
        return min(1., fade * (.94 * _glow(abs(r - .29), .083) +
                          .75 * _glow(math.hypot(x - cx + .10,
                                               y - cy + .13), .10)))
    if name == "MatchBurst":
        fade = (1. - t) ** .65
        brightness = 0.
        for arm in range(8):
            theta = (arm * math.tau / 8. + seed * .07)
            px = math.cos(theta) * (.15 + .73 * t)
            py = math.sin(theta) * (.15 + .73 * t)
            brightness += _glow(math.hypot(x - px, y - py),
                                .13 * (1 - .5 * t))
        return min(1., fade * brightness)
    if name == "StarSparkle":
        rotation = t * .20 + seed * .017
        phi = angle - rotation
        silhouette = .23 + .39 * abs(math.cos(2 * phi)) ** 12
        pulse = .65 + .35 * math.sin(math.pi * t)
        return min(1., pulse * _glow(max(0., radius - silhouette),
                                    .15) * (1. if radius < silhouette else .7))
    if name == "SoftDrift":
        haze = 0.
        for i in range(4):
            phase = (seed * .037 + i * 1.7)
            px = .46 * math.cos(phase + t * .8) + .12 * t
            py = .42 * math.sin(phase * 1.3 + t * .6) - .16 * t
            haze += _glow(math.hypot(x - px, y - py), .37)
        return min(.48, .16 * haze) * (1 - .35 * t)
    if name == "PortalPulse":
        r = .15 + .67 * t
        fading = math.sin(math.pi * (.2 + .8 * t)) ** 2
        return min(1., fading * _glow(abs(radius - r), .085))
    raise VfxCandidateError("unsupported mathematical preset")


def _rgba_frame(name: str, size: int, t: float, seed: int,
                color: tuple[int, int, int]) -> bytes:
    pixels = bytearray(size * size * 4)
    for y in range(size):
        ny = (y + .5) / size * 2 - 1
        for x in range(size):
            nx = (x + .5) / size * 2 - 1
            brightness = max(0., min(1., _field(name, nx, ny, t, seed)))
            offset = (y * size + x) * 4
            pixels[offset:offset + 3] = bytes(color)
            pixels[offset + 3] = round(brightness * 255)
    return bytes(pixels)


def build_candidate(name: str, *, frames: int = 12,
                    frame_side: int = 64, columns: int = 4,
                    fps: int = 12, seed: int = 0,
                    color: str | None = None) -> tuple[dict, bytes, bytes]:
    """Generate a deterministic candidate RGBA sheet plus reduced-motion still.

    Return (metadata, sheet PNG, static PNG), without writing any files.
    """
    _, preset_sha = _preset(name)
    if (type(frames) is not int or not 2 <= frames <= MAX_FRAMES or
            type(frame_side) is not int or not 16 <= frame_side <= MAX_SIDE or
            type(columns) is not int or not 1 <= columns <= frames or
            type(fps) is not int or not 1 <= fps <= 60 or
            type(seed) is not int or not 0 <= seed <= 65535):
        raise VfxCandidateError("frames/size/columns/fps/seed exceed authoring bounds")
    chosen = color if color is not None else COLORS[name]
    if not isinstance(chosen, str) or HEX_COLOR.fullmatch(chosen) is None:
        raise VfxCandidateError("expected opaque six-digit RGB color")
    rgb = tuple(int(chosen[i:i + 2], 16) for i in (1, 3, 5))
    rows = (frames + columns - 1) // columns
    width, height = columns * frame_side, rows * frame_side
    if width * height > MAX_ATLAS_PIXELS:
        raise VfxCandidateError("sprite sheet exceeds 2Mi-pixel budget")
    sheet = bytearray(width * height * 4)
    frame_rects = []
    for i in range(frames):
        t = (i + .5) / frames
        data = _rgba_frame(name, frame_side, t, seed, rgb)
        dx, dy = (i % columns) * frame_side, (i // columns) * frame_side
        for row in range(frame_side):
            src = row * frame_side * 4
            dst = ((dy + row) * width + dx) * 4
            sheet[dst:dst + frame_side * 4] = data[src:src + frame_side * 4]
        frame_rects.append({
            "frame": i,
            "pixel_rect_top_left": [dx, dy, frame_side, frame_side],
            "rgba_sha256": hashlib.sha256(data).hexdigest()
        })
    # Reduced-motion still has no moving particle or animated reward state.
    still = _rgba_frame(name, frame_side, .5, seed, rgb)
    still_png = encode_png(frame_side, frame_side, still)
    sheet_png = encode_png(width, height, bytes(sheet))
    manifest = {
        "schema_version": 1,
        "stage": "CANDIDATE_NOT_OWNER_APPROVED",
        "generator": "VF06_PROCEDURAL_FX_SHEET_V01",
        "preset_id": name,
        "presets_source_sha256": preset_sha,
        "color": chosen.upper(),
        "seed": seed,
        "fps": fps, "frame_count": frames, "frame_side": frame_side,
        "columns": columns, "rows": rows,
        "atlas_width": width, "atlas_height": height,
        "atlas_path": "fx_sheet.png",
        "atlas_sha256": hashlib.sha256(sheet_png).hexdigest(),
        "reduced_motion_path": "reduced_motion.png",
        "reduced_motion_sha256": hashlib.sha256(still_png).hexdigest(),
        "reduced_motion_policy": "STATIC_VIEW_ONLY",
        "animation_frames": frame_rects,
        "pixel_format": "RGBA8_UNROTATED",
        "frame_rate": fps,
        "asset_rights_verified": False,
        "engine_side_effects_allowed": False,
        "owner_visual_approval": False
    }
    return manifest, sheet_png, still_png


def write_candidate(directory: Path, manifest: dict, atlas: bytes,
                    reduced: bytes) -> None:
    target = _destination(directory)
    payloads = {
        "fx_sheet.png": atlas,
        "reduced_motion.png": reduced,
        "fx_manifest.json": (json.dumps(manifest, sort_keys=True, indent=2) +
                             "\n").encode("utf-8")
    }
    # No overwrite and only new candidate folder. A write failure leaves
    # what has been written in place for forensic review: NO auto-delete.
    target.mkdir()
    for name, content in payloads.items():
        with (target / name).open("xb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preset", required=True, choices=sorted(COLORS))
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--frames", type=int, default=12)
    parser.add_argument("--frame-side", type=int, default=64)
    parser.add_argument("--columns", type=int, default=4)
    parser.add_argument("--fps", type=int, default=12)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--color", type=str)
    args = parser.parse_args(argv)
    try:
        result, atlas, still = build_candidate(
            args.preset, frames=args.frames, frame_side=args.frame_side,
            columns=args.columns, fps=args.fps, seed=args.seed,
            color=args.color)
        if args.output_dir is not None:
            write_candidate(args.output_dir, result, atlas, still)
            result["output_saved"] = True
        else:
            result["output_saved"] = False
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0
    except (VfxCandidateError, ImageError, OSError, ValueError) as exc:
        print("VF06_PROCEDURAL_CANDIDATE_REJECTED: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
