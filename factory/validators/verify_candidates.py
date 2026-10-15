"""VF-09 offline candidate pixel parity verifier, separate from the authoring path.

Re-reads original PNG bytes, SHA-256 receipts and output pixel geometry.
This can detect accidental corruption; it is not a rights/owner signature or
a substitute for actual Unity/device visual acceptance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from typing import Mapping

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from factory.image_processor.png_pipeline import (
    ImageError, MAX_INPUT_BYTES, decode_png
)
from factory.image_processor.alpha_mask import mask_rgba

NAME = re.compile(r"[a-z][a-z0-9_.-]{0,99}\Z")


class CandidateVerificationError(ValueError):
    pass


def _read_bytes(path: Path) -> bytes:
    path = Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_INPUT_BYTES:
        raise CandidateVerificationError("missing/unsafe/oversized candidate or source file")
    return path.read_bytes()


def _read_json(path: Path) -> dict:
    raw = _read_bytes(path)
    if len(raw) > 1_048_576:
        raise CandidateVerificationError("candidate JSON too large")
    doc = json.loads(raw)
    if not isinstance(doc, dict) or doc.get("schema_version") != 1:
        raise CandidateVerificationError("unknown candidate manifest schema")
    if doc.get("stage") != "CANDIDATE_NOT_APPROVED":
        raise CandidateVerificationError("candidate must not self-declare approval")
    return doc


def _bytes_equal(name: str, real: bytes, receipt: str):
    if not isinstance(receipt, str) or hashlib.sha256(real).hexdigest() != receipt:
        raise CandidateVerificationError(name + " SHA-256 mismatch")


def _rect_value(value, label):
    if (not isinstance(value, list) or len(value) != 4
            or any(type(v) is not int for v in value)):
        raise CandidateVerificationError(label + " not a four-integer pixel rect")
    return value


def verify_atlas_candidate(directory: Path, original_sources: Mapping[str, Path]) -> dict:
    if not isinstance(original_sources, dict) or not original_sources:
        raise CandidateVerificationError("original source mapping required")
    directory = Path(directory)
    doc = _read_json(directory / "atlas_manifest.json")
    if doc.get("generator") != "VF04_SHELF_PACK_V01":
        raise CandidateVerificationError("unknown atlas builder/algorithm")
    encoded = _read_bytes(directory / "atlas.png")
    _bytes_equal("atlas", encoded, doc.get("atlas_sha256"))
    width, height, pixels = decode_png(encoded)
    if doc.get("width") != width or doc.get("height") != height:
        raise CandidateVerificationError("atlas dimension mismatch")
    sprites = doc.get("sprites")
    if not isinstance(sprites, list) or len(sprites) != len(original_sources) or len(sprites) > 128:
        raise CandidateVerificationError("atlas/source cardinality mismatch")
    visited = set()
    rectangles = []
    for sprite in sprites:
        if not isinstance(sprite, dict) or sprite.get("rotated") is not False:
            raise CandidateVerificationError("unsupported rotated or invalid sprite")
        name = sprite.get("asset_id")
        if not isinstance(name, str) or not NAME.fullmatch(name):
            raise CandidateVerificationError("unsafe sprite id")
        if name in visited or name not in original_sources:
            raise CandidateVerificationError("duplicate/unknown sprite in candidate")
        visited.add(name)
        raw = _read_bytes(Path(original_sources[name]))
        _bytes_equal(name + " original", raw, sprite.get("original_sha256"))
        iw, ih, original = decode_png(raw)
        x, y, sw, sh = _rect_value(sprite.get("pixel_rect_top_left"), name)
        if (x < 0 or y < 0 or sw <= 0 or sh <= 0 or
                x + sw > width or y + sh > height or
                (iw, ih) != (sw, sh) or
                sprite.get("width") != sw or sprite.get("height") != sh):
            raise CandidateVerificationError("sprite geometry/dimensions mismatch")
        coords = sprite.get("uv_rect_bottom_left")
        expect = [x / width, (height - y - sh) / height, sw / width, sh / height]
        if (not isinstance(coords, list) or len(coords) != 4 or
                any(type(n) not in (float, int) or not math.isfinite(n)
                    or abs(n - m) > 1e-7 for n, m in zip(coords, expect))):
            raise CandidateVerificationError("sprite UV coordinate mismatch")
        for ox, oy, ow, oh in rectangles:
            if x < ox + ow and ox < x + sw and y < oy + oh and oy < y + sh:
                raise CandidateVerificationError("overlapping sprite pixel rectangles")
        rectangles.append((x, y, sw, sh))
        for row in range(sh):
            offset = ((y + row) * width + x) * 4
            before = row * sw * 4
            if pixels[offset:offset + sw * 4] != original[before:before + sw * 4]:
                raise CandidateVerificationError("sprite pixel mismatch: " + name)
    return {"stage": "REVIEW_REQUIRED", "sprites_verified": len(visited),
            "atlas_sha256": doc["atlas_sha256"]}


def verify_mask_candidate(directory: Path, source: Path, mask: Path) -> dict:
    directory = Path(directory)
    doc = _read_json(directory / "mask_receipt.json")
    if doc.get("generator") != "VF04_ALPHA_MASK_V01":
        raise CandidateVerificationError("unknown alpha mask builder")
    original, masked = _read_bytes(source), _read_bytes(mask)
    _bytes_equal("original", original, doc.get("source_sha256"))
    _bytes_equal("mask", masked, doc.get("mask_sha256"))
    w, h, rgba = decode_png(original)
    mw, mh, mask_rgba_input = decode_png(masked)
    if (w, h) != (mw, mh) or [w, h] != [doc.get("width"), doc.get("height")]:
        raise CandidateVerificationError("mask/source geometry mismatch")
    expected = mask_rgba(w, h, rgba, mask_rgba_input, doc.get("operation"))
    encoded = _read_bytes(directory / "masked_candidate.png")
    _bytes_equal("masked PNG", encoded, doc.get("output_sha256"))
    ow, oh, actual = decode_png(encoded)
    if (ow, oh) != (w, h) or actual != expected:
        raise CandidateVerificationError("mask candidate did not preserve source RGB/alpha arithmetic")
    return {"stage": "REVIEW_REQUIRED", "masked_pixels_verified": w * h,
            "output_sha256": doc["output_sha256"]}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="operation", required=True)
    atlas = sub.add_parser("atlas")
    atlas.add_argument("--candidate", type=Path, required=True)
    atlas.add_argument("--sources-json", type=Path, required=True)
    mask = sub.add_parser("mask")
    mask.add_argument("--candidate", type=Path, required=True)
    mask.add_argument("--source", type=Path, required=True)
    mask.add_argument("--mask", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.operation == "atlas":
            origin_path = args.sources_json
            sources_doc = json.loads(_read_bytes(origin_path))
            if not isinstance(sources_doc, dict) or not all(
                    isinstance(v, str) for v in sources_doc.values()):
                raise CandidateVerificationError("invalid original source list")
            sources = {
                key: (Path(path) if Path(path).is_absolute()
                      else origin_path.parent / path)
                for key, path in sources_doc.items()
            }
            result = verify_atlas_candidate(args.candidate, sources)
        else:
            result = verify_mask_candidate(args.candidate, args.source, args.mask)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (CandidateVerificationError, ImageError, OSError, ValueError) as exc:
        parser.exit(2, "VF09_REVIEW_REQUIRED: " + str(exc) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
