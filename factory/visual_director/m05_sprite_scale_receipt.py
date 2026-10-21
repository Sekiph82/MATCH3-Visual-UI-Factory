"""M05 read-only per-pixel 1x/2x/3x trim, pivot and alpha source audit.

INTERNAL_REUSE: existing VF04 PNG decoder/trim/nearest exporter.
This verifies raster *source* pixels, not imported Unity sprite pivots,
physical iOS/Android texture quality, creator rights or actual gameplay.
No file I/O, new dependencies, mutation, paid services or release.
"""
from __future__ import annotations

import hashlib
import math
import re
from collections.abc import Mapping

from factory.image_processor.png_pipeline import (
    ImageError, decode_png, trim_rgba, scale_nearest,
)

STAGE = "M05_SOURCE_SCALE_AND_PIVOT_CANDIDATE_NOT_APPROVED"
SHA = re.compile(r"[0-9a-f]{64}\Z")
MAX_SOURCE_SIDE = 2048
MAX_SOURCE_PIXELS = 1_000_000
MAX_BYTES = 8 * 1024 * 1024


class SpriteScaleError(ValueError):
    pass


def _checked_png(raw: bytes, pinned_sha: str):
    if (not isinstance(raw, bytes) or not 0 < len(raw) <= MAX_BYTES or
            not isinstance(pinned_sha, str) or not SHA.fullmatch(pinned_sha) or
            hashlib.sha256(raw).hexdigest() != pinned_sha):
        raise SpriteScaleError("missing/broken exact source PNG SHA receipt")
    try:
        w, h, pixels = decode_png(raw)
    except ImageError as exc:
        raise SpriteScaleError("invalid source PNG: " + str(exc)) from exc
    if (w > MAX_SOURCE_SIDE * 3 or h > MAX_SOURCE_SIDE * 3 or
            w * h > MAX_SOURCE_PIXELS * 9):
        raise SpriteScaleError("oversized raster source review")
    return w, h, pixels


def audit_pinned_scale_set(
    source_png: bytes,
    source_sha256: str,
    exports: Mapping[int, bytes],
    export_shas: Mapping[int, str],
    source_pivot_bottom_left: tuple[float, float],
    *, padding: int = 0, alpha_cutoff: int = 0,
) -> dict:
    """Strict full RGBA nearest replay, source pivot translation, no writes."""
    if (not isinstance(exports, Mapping) or not isinstance(export_shas, Mapping)
            or set(exports) != {1, 2, 3} or set(export_shas) != {1, 2, 3}
            or any(type(k) is not int for k in exports)
            or type(padding) is not int or not 0 <= padding <= 16
            or type(alpha_cutoff) is not int or not 0 <= alpha_cutoff <= 254
            or not isinstance(source_pivot_bottom_left, (list, tuple))
            or len(source_pivot_bottom_left) != 2
            or any(type(v) not in (int, float) or not math.isfinite(v)
                   for v in source_pivot_bottom_left)):
        raise SpriteScaleError("incomplete scale set or unsafe pivot metadata")
    sw, sh, source = _checked_png(source_png, source_sha256)
    if sw > MAX_SOURCE_SIDE or sh > MAX_SOURCE_SIDE or sw * sh > MAX_SOURCE_PIXELS:
        raise SpriteScaleError("source exceeds sprite review allocation")
    x, y = source_pivot_bottom_left
    if not 0 <= x <= sw or not 0 <= y <= sh:
        raise SpriteScaleError("source pivot outside original image")
    try:
        w, h, trimmed, bounds = trim_rgba(
            sw, sh, source, padding=padding, alpha_cutoff=alpha_cutoff)
    except ImageError as exc:
        raise SpriteScaleError("transparent/unsupported source trim") from exc
    bottom_cutoff = sh - bounds["y"] - bounds["height"]
    pivot_x = x - bounds["x"] + padding
    pivot_y = y - bottom_cutoff + padding
    if not 0 <= pivot_x <= w or not 0 <= pivot_y <= h:
        raise SpriteScaleError("pivot excluded by alpha trim: re-author source anchor")
    rows = []
    for scale in (1, 2, 3):
        ow, oh, actual = _checked_png(exports[scale], export_shas[scale])
        try:
            ew, eh, expected = scale_nearest(w, h, trimmed, scale)
        except ImageError as exc:
            raise SpriteScaleError("source scaled sprite would exceed budget") from exc
        if (ow, oh) != (ew, eh) or actual != expected:
            raise SpriteScaleError(
                str(scale) + "x source pixels, padding or alpha diverged")
        rows.append({
            "scale": scale, "dimensions": [ow, oh],
            "source_sha256": export_shas[scale],
            "sprite_pivot_pixels_bottom_left":
                [round(pivot_x * scale, 5), round(pivot_y * scale, 5)],
            "normalized_pivot":
                [round(pivot_x / w, 7), round(pivot_y / h, 7)],
            "margin_pixels": padding * scale,
            "whole_rgba_nearest_verified": True,
            "unity_importer_pivot_verified": False,
            "physical_device_verified": False,
            "owner_art_approved": False,
        })
    return {
        "schema_version": 1,
        "stage": STAGE,
        "original_source_sha256": source_sha256,
        "original_dimensions": [sw, sh],
        "trim_source_rect_top_left": [
            bounds["x"], bounds["y"], bounds["width"], bounds["height"]],
        "padding": padding, "alpha_cutoff": alpha_cutoff,
        "exports": rows,
        "original_creator_rights_verified": False,
        "unity_sprite_importer_verified": False,
        "real_atlas_gpu_bleeding_verified": False,
        "engine_final_asset_id_verified": False,
        "release_allowed": False,
    }
