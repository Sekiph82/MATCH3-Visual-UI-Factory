"""VUF-M09-002/003/004: strict source-byte image regression gate.

Reuses existing VUF PNG decoder, no Pillow, no fake perceptual/owner scoring.
Never treats a transparent/RGBA numeric mismatch as art quality acceptance.
All previews/math are source candidates; no game renders or device simulation.
"""
from __future__ import annotations

import hashlib
import math
import re
from pathlib import Path
from factory.image_processor.png_pipeline import decode_png, encode_png

SHA = re.compile(r"[0-9a-f]{64}\Z")
MAX_PIXELS = 4_000_000


class PixelReviewError(ValueError):
    pass


def _rgba(png: bytes):
    if not isinstance(png, bytes) or len(png) > 16 * 1024 * 1024:
        raise PixelReviewError("missing/oversized source PNG")
    try:
        w, h, pixels = decode_png(png)
    except (ValueError, IndexError, TypeError) as e:
        raise PixelReviewError("source PNG decoder rejected bytes") from e
    if w * h > MAX_PIXELS or w < 1 or h < 1:
        raise PixelReviewError("image exceeds bounded review budget")
    if len(pixels) != w * h * 4:
        raise PixelReviewError("decoded RGBA dimensions changed")
    return w, h, pixels


def compare(before: bytes, after: bytes, *, expected_sha: str | None = None,
            tolerance: int = 0) -> tuple[dict, bytes | None]:
    """Return deterministic per-channel differences and bright visual diff PNG.

    If unchanged, difference source is None to avoid uploading a redundant
    "all green" generated approval screenshot.
    """
    if type(tolerance) is not int or not 0 <= tolerance <= 16:
        raise PixelReviewError("tolerance outside bounded exact byte range")
    if expected_sha is not None:
        if not isinstance(expected_sha, str) or not SHA.fullmatch(expected_sha):
            raise PixelReviewError("invalid pinned source hash")
        if hashlib.sha256(before).hexdigest() != expected_sha:
            raise PixelReviewError("original source bytes changed before review")
    w0, h0, a = _rgba(before)
    w1, h1, b = _rgba(after)
    if (w0, h0) != (w1, h1):
        raise PixelReviewError("resolution changed: compare scaled versions separately")
    changed_pixels = alpha_changed = blended_edges = 0
    max_delta = 0
    diff = bytearray(w0 * h0 * 4)
    for pixel in range(w0 * h0):
        idx = pixel * 4
        diff_channels = [abs(a[idx + j] - b[idx + j]) for j in range(4)]
        peak = max(diff_channels)
        max_delta = max(peak, max_delta)
        mismatch = peak > tolerance
        if mismatch:
            changed_pixels += 1
            if diff_channels[3] > tolerance:
                alpha_changed += 1
            # Signal alpha/RGB disagreement at the transparent edge,
            # not a certified colour-fringing/artifact severity measure.
            if (0 < a[idx + 3] < 255 or 0 < b[idx + 3] < 255):
                blended_edges += 1
            diff[idx:idx + 4] = bytes((255, 35 if diff_channels[3] else 140,
                                       35 if diff_channels[3] else 0, 255))
        else:
            diff[idx:idx + 4] = bytes((0, 0, 0, 255))
    report = {
        "schema_version": 1,
        "stage": "PIXEL_REGRESSION_CANDIDATE_NOT_APPROVED",
        "dimensions": [w0, h0],
        "before_sha256": hashlib.sha256(before).hexdigest(),
        "after_sha256": hashlib.sha256(after).hexdigest(),
        "tolerance_per_channel": tolerance,
        "mismatched_pixels": changed_pixels,
        "alpha_changed_pixels": alpha_changed,
        "semialpha_edge_candidates": blended_edges,
        "max_channel_delta": max_delta,
        "mismatch_ratio_milli": changed_pixels * 1000 // (w0 * h0),
        "real_unity_render_verified": False,
        "physical_gpu_verified": False,
        "source_licence_reviewed": False,
        "owner_aesthetic_approved": False,
        "release_allowed": False,
    }
    return report, encode_png(w0, h0, bytes(diff)) if changed_pixels else None


def verify_receipt_source(source: bytes, *, declared_sha: str,
                          provenance: dict) -> dict:
    """Strict receipt SHAPE + source byte identity, not a legal licence grant."""
    if not isinstance(provenance, dict):
        raise PixelReviewError("source rights provenance missing")
    if (not isinstance(declared_sha, str) or
            not SHA.fullmatch(declared_sha) or
            hashlib.sha256(source).hexdigest() != declared_sha):
        raise PixelReviewError("original source SHA conflict")
    _rgba(source)
    allowed = {"profile_id", "asset_id", "source_filename", "creator",
               "licence_text_location", "consent_reference", "usage_scope",
               "source_sha256", "stage"}
    if set(provenance) != allowed:
        raise PixelReviewError("invalid/overprivileged source rights schema")
    if provenance["source_sha256"] != declared_sha or             provenance["stage"] != "OWNER_ART_SOURCE_REVIEW_PENDING":
        raise PixelReviewError("source receipt forged")
    for key in ("profile_id", "asset_id", "source_filename", "creator",
                "licence_text_location", "usage_scope"):
        if not isinstance(provenance.get(key), str) or                 not 1 <= len(provenance[key]) <= 240:
            raise PixelReviewError("missing source creator/licence/scope evidence")
    if provenance["asset_id"].split(".")[0] != provenance["profile_id"]:
        raise PixelReviewError("cross-title source attribution mismatch")
    if provenance.get("consent_reference") is not None and             (not isinstance(provenance["consent_reference"], str) or
             len(provenance["consent_reference"]) > 240):
        raise PixelReviewError("invalid consent reference")
    return {
        "source_bytes_sha256_verified": True,
        "provenance_fields_present": True,
        "licence_text_legal_reviewed": False,
        "source_creator_independently_verified": False,
        "owner_art_originality_approved": False,
        "image_use_authorized_for_release": False,
        "release_allowed": False,
    }
