"""VF-04 deterministic RGB edge-extrusion for transparent PNG halo mitigation.

Only RGB of alpha==0 pixels may be changed. Original source and alpha
channels are never changed; output is a NEW outside-Git optional file.
This is an asset candidate filter aid, not an automatically approved art edit.
"""
from __future__ import annotations

import argparse
from collections import deque
import hashlib
import json
import os
import stat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from factory.image_processor.png_pipeline import decode_png, encode_png, ImageError

MAX_PIXELS = 4_194_304
MAX_RADIUS = 8
STAGE = "CANDIDATE_NOT_OWNER_APPROVED"


class FringeError(ValueError):
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


def _safe_source(path: Path) -> Path:
    path = Path(path)
    if (not path.is_file() or path.suffix.lower() != ".png" or
            _linked(path) or any(_linked(p) for p in path.parents) or
            path.resolve(strict=True).is_relative_to(ROOT)):
        raise FringeError("source must be nonlinked external PNG original")
    return path


def _neighbors(index: int, width: int, height: int):
    x, y = index % width, index // width
    if x > 0:
        yield index - 1
    if x + 1 < width:
        yield index + 1
    if y > 0:
        yield index - width
    if y + 1 < height:
        yield index + width


def extrude_rgb(width: int, height: int, rgba: bytes,
                radius: int = 2) -> tuple[bytes, int]:
    """4-connected deterministic outward RGB propagation, alpha invariant.

    Nearest original visible pixel wins with fixed top-left raster and
    left/right/up/down tie ordering. Only alpha=0 receives source RGB;
    no alpha or alpha>0 color is changed. Max radius 1..8 pixels.
    """
    if (type(width) is not int or type(height) is not int or
            width < 1 or height < 1 or width * height > MAX_PIXELS or
            len(rgba) != width * height * 4 or type(radius) is not int or
            not 1 <= radius <= MAX_RADIUS):
        raise FringeError("invalid dimensions, buffer or extrusion radius")
    pixels = width * height
    output = bytearray(rgba)
    distance = bytearray(pixels)
    queue = deque()

    # Queue only original visible boundary pixels, not the entire opaque
    # texture. Their original alpha/RGB remains immutable throughout.
    for index in range(pixels):
        if rgba[index * 4 + 3] == 0:
            continue
        if any(rgba[neighbor * 4 + 3] == 0
               for neighbor in _neighbors(index, width, height)):
            distance[index] = 1
            queue.append(index)

    changed = 0
    while queue:
        current = queue.popleft()
        depth = distance[current] - 1
        if depth >= radius:
            continue
        src = current * 4
        for neighbor in _neighbors(current, width, height):
            dst = neighbor * 4
            if rgba[dst + 3] != 0 or distance[neighbor] != 0:
                continue
            distance[neighbor] = depth + 2
            output[dst:dst + 3] = output[src:src + 3]
            # output[dst+3] MUST remain original zero; no hidden alpha.
            changed += 1
            queue.append(neighbor)

    for idx in range(pixels):
        if output[idx * 4 + 3] != rgba[idx * 4 + 3]:
            raise FringeError("internal alpha invariant violated")
    return bytes(output), changed


def process_png(source: Path, radius: int = 2) -> tuple[dict, bytes]:
    original = _safe_source(source).read_bytes()
    width, height, rgba = decode_png(original)
    result, changed = extrude_rgb(width, height, rgba, radius)
    png = encode_png(width, height, result)
    return {
        "schema_version": 1,
        "stage": STAGE,
        "generator": "VF04_TRANSPARENT_RGB_EXTRUSION_V01",
        "source_png_sha256": hashlib.sha256(original).hexdigest(),
        "candidate_png_sha256": hashlib.sha256(png).hexdigest(),
        "image_dimensions": [width, height],
        "radius_pixels": radius,
        "transparent_pixels_rgb_processed": changed,
        "alpha_bytes_identical": True,
        "nontransparent_rgba_identical": True,
        "changes_source_file": False,
        "asset_rights_verified": False,
        "owner_visual_approval": False,
        "device_render_verified": False,
    }, png


def save_candidate(destination: Path, receipt: dict, png: bytes) -> None:
    target = Path(destination)
    if (target.suffix.lower() != ".png" or target.exists() or target.is_symlink()
            or not target.parent.is_dir() or
            any(_linked(p) for p in (target.parent, *target.parent.parents)) or
            target.parent.resolve(strict=True).is_relative_to(ROOT) or
            receipt.get("stage") != STAGE or
            receipt.get("asset_rights_verified") is not False or
            receipt.get("owner_visual_approval") is not False or
            hashlib.sha256(png).hexdigest() != receipt.get("candidate_png_sha256")):
        raise FringeError("output requires NEW external PNG and nonapproved candidate")
    with target.open("xb") as stream:
        stream.write(png)
        stream.flush()
        os.fsync(stream.fileno())


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--radius", type=int, default=2)
    p.add_argument("--output-file", type=Path)
    args = p.parse_args(argv)
    try:
        result, candidate = process_png(args.source, args.radius)
        if args.output_file:
            save_candidate(args.output_file, result, candidate)
            result["output_saved"] = True
        else:
            result["output_saved"] = False
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0
    except (FringeError, ImageError, OSError, ValueError) as exc:
        print("VF04_RGB_EXTRUSION_REJECTED: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
