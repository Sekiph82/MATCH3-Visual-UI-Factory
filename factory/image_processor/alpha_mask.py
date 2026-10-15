"""VF-04 non-destructive, pixel-exact alpha mask candidate compositor.

The mask's alpha channel controls visibility. Source RGB is copied unchanged;
only source alpha is multiplied by the mask or its complement. No AI/network.
Input original and mask bytes are never edited, approvals are not implied.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from factory.image_processor.png_pipeline import (
    MAX_INPUT_BYTES, ImageError, decode_png, encode_png
)


def _read_original(path: Path) -> tuple[bytes, int, int, bytes]:
    path = Path(path)
    if path.is_symlink() or not path.is_file() or path.suffix.lower() != ".png":
        raise ImageError("source and mask must be regular original PNGs")
    if path.stat().st_size > MAX_INPUT_BYTES:
        raise ImageError("PNG exceeds 64 MiB intake limit")
    raw = path.read_bytes()
    width, height, pixels = decode_png(raw)
    return raw, width, height, pixels


def mask_rgba(width: int, height: int, source: bytes, mask: bytes,
              mode: str = "keep") -> bytes:
    if mode not in ("keep", "remove"):
        raise ImageError("only keep/remove alpha masking is supported")
    if (width < 1 or height < 1 or len(source) != width * height * 4
            or len(mask) != width * height * 4):
        raise ImageError("source/mask dimension or pixel length mismatch")
    result = bytearray(source)
    for i in range(3, len(source), 4):
        alpha = mask[i]
        if mode == "remove":
            alpha = 255 - alpha
        # Round-half-up: deterministic integer operation, no platform float noise.
        result[i] = (source[i] * alpha + 127) // 255
    return bytes(result)


def create_mask_candidate(source: Path, mask: Path,
                          output_dir: Path, mode: str = "keep") -> dict:
    source, mask, output_dir = Path(source), Path(mask), Path(output_dir)
    if mode not in ("keep", "remove"):
        raise ImageError("mode must be keep/remove")
    repo_root = Path(__file__).resolve().parents[2]
    root = output_dir.resolve()
    if (output_dir.is_symlink() or root.is_relative_to(repo_root)
            or source.resolve().is_relative_to(root)
            or mask.resolve().is_relative_to(root)):
        raise ImageError("mask output must be external and separate from original images")
    if output_dir.exists() and not output_dir.is_dir():
        raise ImageError("mask output must be a directory")
    source_raw, w, h, pixels = _read_original(source)
    mask_raw, mw, mh, mask_pixels = _read_original(mask)
    if (w, h) != (mw, mh):
        raise ImageError("mask and source image dimensions must match")
    composed = mask_rgba(w, h, pixels, mask_pixels, mode=mode)
    candidate_png = encode_png(w, h, composed)
    manifest = {
        "schema_version": 1,
        "stage": "CANDIDATE_NOT_APPROVED",
        "generator": "VF04_ALPHA_MASK_V01",
        "operation": mode,
        "width": w, "height": h,
        "source_sha256": hashlib.sha256(source_raw).hexdigest(),
        "mask_sha256": hashlib.sha256(mask_raw).hexdigest(),
        "output_path": "masked_candidate.png",
        "output_sha256": hashlib.sha256(candidate_png).hexdigest(),
    }
    payloads = {
        "masked_candidate.png": candidate_png,
        "mask_receipt.json": (json.dumps(manifest, sort_keys=True, indent=2) + "\n").encode("utf-8")
    }
    for file_name in payloads:
        candidate = output_dir / file_name
        if candidate.exists() or candidate.is_symlink():
            raise ImageError("refusing to overwrite existing mask candidate")
    output_dir.mkdir(parents=True, exist_ok=True)
    if output_dir.is_symlink():
        raise ImageError("unsafe candidate folder symlink")
    created = []
    try:
        for file_name, payload in payloads.items():
            dest = output_dir / file_name
            with dest.open("xb") as stream:
                created.append(dest)
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
    except OSError:
        for dest in created:
            dest.unlink(missing_ok=True)
        raise
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--mask", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--mode", choices=["keep", "remove"], default="keep")
    args = parser.parse_args(argv)
    try:
        print(json.dumps(create_mask_candidate(args.source, args.mask,
                                               args.output_dir, args.mode),
                         sort_keys=True, indent=2))
        return 0
    except (ImageError, OSError) as exc:
        parser.exit(2, "VF04_MASK_REJECTED: " + str(exc) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
