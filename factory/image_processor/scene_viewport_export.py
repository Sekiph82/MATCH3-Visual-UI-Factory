"""VUF-M06-003 | Nonshipping responsive/parallax composite review previews.

Consumes the EXISTING five-theme layered candidate pack and its 57 real PNGs.
Internal reuse: representative_scene_pack receipt verification + png_pipeline
CRC-checked RGBA codec. No game UI flattening: this creates a separately
marked, optional READ-ONLY artwork review image, never a runtime UI prefab.

Unlike simply stretching a portrait JPEG, letterless viewports use centered
cover cropping with source aspect preserved. Parallax offsets affect only
transparent environment layer samples. A synthetic safe-area frame is an
independent optional QA overlay, NOT authored gameplay text/buttons.

All images are original mathematical candidates. Neither manual GUI review,
real GPU memory, audio/haptic nor owner art/rights acceptance is inferred.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

from factory.image_processor.png_pipeline import encode_png, decode_png
from factory.image_processor.representative_scene_pack import (
    ROOT, PROFILES, STAGE, LAYER_ORDER, PARALLAX_MILLI,
    _scenes, _linked, build_representative_pack, verify_representative_pack,
)

ASPECTS = ("portrait", "tall_phone", "tablet")
GENERATOR = "VUF_M06_RESPONSIVE_PREVIEW_V01"
ASPECT_RATIO = {"portrait": (9, 16), "tall_phone": (6, 13), "tablet": (3, 4)}
MAX_OUTPUT_PIXELS = 1_800_000


class ViewportPreviewError(ValueError):
    pass


def _check_params(manifest, profile, scene, aspect, offset_px, safe_guides):
    if not isinstance(manifest, dict):
        raise ViewportPreviewError("missing candidate source manifest")
    if profile not in PROFILES or scene not in _scenes(profile):
        raise ViewportPreviewError("unknown title/scene combination")
    if aspect not in ASPECTS:
        raise ViewportPreviewError("unsupported preview aspect")
    if type(offset_px) is not int or not -160 <= offset_px <= 160:
        raise ViewportPreviewError("offset must be bounded integer in source pixels")
    if type(safe_guides) is not bool:
        raise ViewportPreviewError("guides must be an explicit boolean")


def _target_size(width: int, height: int, aspect: str) -> tuple[int, int]:
    numerator, denominator = ASPECT_RATIO[aspect]
    # Portrait is 9:16. For narrower canvases, add vertical review area;
    # for tablet canvas preserve source height, expose added horizontal area.
    if width * denominator >= height * numerator:
        w = width
        h = (width * denominator + numerator // 2) // numerator
    else:
        h = height
        w = (height * numerator + denominator // 2) // denominator
    if w < 1 or h < 1 or w * h > MAX_OUTPUT_PIXELS:
        raise ViewportPreviewError("output dimensions exceed candidate budget")
    return w, h


def _blend(canvas: bytearray, index: int, source: bytes, offset: int) -> None:
    alpha = source[offset + 3]
    if alpha == 0:
        return
    if alpha == 255:
        canvas[index:index + 4] = source[offset:offset + 4]
        return
    prev = canvas[index + 3]
    denominator = alpha * 255 + prev * (255 - alpha)
    if denominator == 0:
        return
    for channel in range(3):
        weighted = (source[offset + channel] * alpha * 255 +
                    canvas[index + channel] * prev * (255 - alpha))
        canvas[index + channel] = (weighted + denominator // 2) // denominator
    canvas[index + 3] = (denominator + 127) // 255


def _draw_guides(canvas: bytearray, width: int, height: int) -> dict:
    left = round(width * .07)
    top = round(height * .065)
    right, bottom = width - left, height - top
    if right <= left + 3 or bottom <= top + 3:
        raise ViewportPreviewError("invalid synthetic safe-area frame")
    # Alpha-backed border; never contains actual game button or text.
    border = bytes((255, 211, 40, 255))
    for x in range(left, right):
        for y in (top, top + 1, bottom - 2, bottom - 1):
            canvas[(y * width + x) * 4:(y * width + x) * 4 + 4] = border
    for y in range(top, bottom):
        for x in (left, left + 1, right - 2, right - 1):
            canvas[(y * width + x) * 4:(y * width + x) * 4 + 4] = border
    return {"left": left, "top": top, "right": right, "bottom": bottom,
            "synthetic_not_device_safe_area": True}


def render_viewport(manifest: dict, images: dict[str, bytes], profile: str,
                    scene: str, *, aspect: str = "portrait", offset_px: int = 0,
                    safe_guides: bool = False) -> tuple[dict, bytes]:
    """Render a derived NONINTERACTIVE artwork review, never a gameplay asset."""
    _check_params(manifest, profile, scene, aspect, offset_px, safe_guides)
    # Validates all 57 candidate source PNGs, their SHA, style pin, dimensions,
    # ordering, no-authority flags and decoded alpha before compositing any.
    try:
        verify_representative_pack(manifest, images)
    except (ValueError, TypeError, KeyError, OSError) as exc:
        raise ViewportPreviewError("layer source integrity failed") from exc
    rows = [row for row in manifest["scenes"]
            if row["profile_id"] == profile and row["scene_id"] == scene]
    if len(rows) != 1:
        raise ViewportPreviewError("scene cannot be uniquely resolved")
    layers = rows[0]["layers"]
    width, height = layers[0]["dimensions"]
    out_w, out_h = _target_size(width, height, aspect)
    # The whole scene uses ONE cover transform; a mere aspect change never
    # distorts the shape of a tile/bubble/character in review.
    # Integer rational mapping avoids platform-specific float noise.
    cover_num = max(out_w * height, out_h * width)
    cover_den = width * height
    if cover_num <= 0:
        raise ViewportPreviewError("invalid source cover geometry")

    canvas = bytearray(out_w * out_h * 4)
    source_sha = []
    for layer_no, row in enumerate(layers):
        name = row["file"]
        src_w, src_h, rgba = decode_png(images[name])
        source_sha.append(row["png_sha256"])
        shift = round(offset_px * manifest["scale"] *
                      PARALLAX_MILLI[layer_no] / 1000)
        for dy in range(out_h):
            # Center-aligned deterministic nearest-neighbor image cover.
            sy = min(src_h - 1, max(0, (
                (2 * dy + 1 - out_h) * cover_den * src_h //
                (2 * cover_num) + src_h // 2)))
            for dx in range(out_w):
                sx = min(src_w - 1, max(0, (
                    (2 * (dx - shift) + 1 - out_w) * cover_den * src_w //
                    (2 * cover_num) + src_w // 2)))
                source_offset = (sy * src_w + sx) * 4
                dest_offset = (dy * out_w + dx) * 4
                _blend(canvas, dest_offset, rgba, source_offset)
    guides = _draw_guides(canvas, out_w, out_h) if safe_guides else None
    png = encode_png(out_w, out_h, bytes(canvas))
    return {
        "schema_version": 1,
        "stage": STAGE,
        "generator": GENERATOR,
        "profile_id": profile,
        "scene_id": scene,
        "aspect": aspect,
        "scale": manifest["scale"],
        "camera_offset_source_px": offset_px,
        "layer_ids": list(LAYER_ORDER),
        "parallax_milli": list(PARALLAX_MILLI),
        "source_png_sha256": source_sha,
        "source_style_sha256": layers[0]["style_source_sha256"],
        "output_dimensions": [out_w, out_h],
        "png_sha256": hashlib.sha256(png).hexdigest(),
        "synthetic_safe_guides": guides,
        "ui_stays_interactive_in_separate_unity_layers": True,
        "is_runnable_runtime_ui": False,
        "owner_visual_approval": False,
        "art_rights_verified": False,
        "actual_device_safe_area_verified": False,
        "real_device_gpu_parallax_verified": False,
        "release_allowed": False,
    }, png


def write_preview(folder: Path, receipt: dict, png: bytes) -> None:
    """Write only an explicitly requested NEW external folder; never overwrite."""
    if (not isinstance(receipt, dict) or
            receipt.get("stage") != STAGE or
            receipt.get("generator") != GENERATOR or
            hashlib.sha256(png).hexdigest() != receipt.get("png_sha256") or
            any(receipt.get(k) is not False for k in (
                "owner_visual_approval", "art_rights_verified",
                "actual_device_safe_area_verified",
                "real_device_gpu_parallax_verified", "release_allowed")) or
            receipt.get("is_runnable_runtime_ui") is not False):
        raise ViewportPreviewError("forged or invalid nonshipping preview")
    folder = Path(folder)
    if (folder.exists() or folder.is_symlink() or
            not folder.parent.is_dir() or
            any(_linked(p) for p in (folder.parent, *folder.parent.parents)) or
            folder.parent.resolve(strict=True).is_relative_to(ROOT)):
        raise ViewportPreviewError("destination must be NEW and outside Git")
    folder.mkdir()
    with (folder / "artwork_review_only.png").open("xb") as handle:
        handle.write(png)
        handle.flush()
        os.fsync(handle.fileno())
    with (folder / "artwork_review_receipt.json").open(
            "x", encoding="utf-8", newline="\n") as handle:
        json.dump(receipt, handle, sort_keys=True, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True, choices=PROFILES)
    parser.add_argument("--scene", required=True)
    parser.add_argument("--scale", type=int, choices=(1, 2, 3), default=1)
    parser.add_argument("--aspect", choices=ASPECTS, default="portrait")
    parser.add_argument("--camera-offset-px", type=int, default=0)
    parser.add_argument("--safe-guides", action="store_true")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args(argv)
    try:
        manifest, imgs = build_representative_pack(scale=args.scale)
        receipt, png = render_viewport(
            manifest, imgs, args.profile, args.scene,
            aspect=args.aspect, offset_px=args.camera_offset_px,
            safe_guides=args.safe_guides)
        if args.output_dir is not None:
            write_preview(args.output_dir, receipt, png)
        print(json.dumps({
            "profile": receipt["profile_id"], "scene": receipt["scene_id"],
            "aspect": receipt["aspect"], "size": receipt["output_dimensions"],
            "png_sha256": receipt["png_sha256"],
            "output_saved": args.output_dir is not None,
            "release_allowed": False
        }, sort_keys=True))
        return 0
    except (ViewportPreviewError, OSError, ValueError) as exc:
        print("VIEWPORT_REVIEW_REJECTED: " + str(exc), file=__import__("sys").stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
