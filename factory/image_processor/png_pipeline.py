"""VF-04: lossless, reproducible PNG alpha trim and nearest-neighbor scale.

Deliberately supports non-interlaced, 8-bit RGB/RGBA PNG only in V01.
Unsupported images fail closed rather than being silently misrendered.
This module creates isolated candidate outputs; it cannot approve/publish art.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
import zlib
from pathlib import Path

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_INPUT_BYTES = 64 * 1024 * 1024
MAX_INPUT_PIXELS = 16_000_000
MAX_OUTPUT_PIXELS = 32_000_000
MAX_DIMENSION = 8192


class ImageError(ValueError):
    pass


def _chunk(name: bytes, data: bytes) -> bytes:
    return (struct.pack(">I", len(data)) + name + data
            + struct.pack(">I", zlib.crc32(name + data) & 0xffffffff))


def _paeth(left: int, above: int, upper_left: int) -> int:
    p = left + above - upper_left
    a, b, c = abs(p - left), abs(p - above), abs(p - upper_left)
    if a <= b and a <= c:
        return left
    if b <= c:
        return above
    return upper_left


def decode_png(data: bytes) -> tuple[int, int, bytes]:
    """Return (width,height, tightly packed RGBA). PNG CRC is checked for every chunk."""
    if not isinstance(data, bytes) or len(data) > MAX_INPUT_BYTES:
        raise ImageError("PNG input size exceeds limit")
    if not data.startswith(PNG_SIGNATURE):
        raise ImageError("bad PNG signature")
    index, width, height, bpp = 8, 0, 0, 0
    compressed = bytearray()
    has_ihdr, has_idat, has_iend, idat_closed = False, False, False, False
    while index < len(data):
        if index + 12 > len(data):
            raise ImageError("truncated PNG chunk")
        size = struct.unpack(">I", data[index:index + 4])[0]
        name = data[index + 4:index + 8]
        if (len(name) != 4 or not all(65 <= c <= 90 or 97 <= c <= 122 for c in name)
                or size > MAX_INPUT_BYTES or index + size + 12 > len(data)):
            raise ImageError("invalid PNG chunk header")
        payload = data[index + 8:index + 8 + size]
        crc = struct.unpack(">I", data[index + 8 + size:index + 12 + size])[0]
        if zlib.crc32(name + payload) & 0xffffffff != crc:
            raise ImageError("PNG chunk CRC mismatch")
        index += size + 12
        if name == b"IHDR":
            if has_ihdr or has_idat or size != 13:
                raise ImageError("duplicated or malformed IHDR")
            width, height, depth, kind, method, flt, interlace = struct.unpack(
                ">IIBBBBB", payload
            )
            if (depth != 8 or kind not in (2, 6) or method != 0
                    or flt != 0 or interlace != 0):
                raise ImageError("only non-interlaced 8-bit RGB/RGBA PNG supported")
            if (width == 0 or height == 0 or width > MAX_DIMENSION
                    or height > MAX_DIMENSION or width * height > MAX_INPUT_PIXELS):
                raise ImageError("unsafe PNG pixel dimensions")
            bpp = 4 if kind == 6 else 3
            has_ihdr = True
        elif not has_ihdr:
            raise ImageError("IHDR must be first")
        elif name == b"IDAT":
            if idat_closed:
                raise ImageError("non-contiguous IDAT chunks")
            if len(compressed) + size > MAX_INPUT_BYTES:
                raise ImageError("compressed PNG exceeds limit")
            compressed.extend(payload)
            has_idat = True
        elif name == b"tRNS":
            # RGB colorkey transparency must not silently become opaque on decode.
            # Indexed/palette images already fail closed at IHDR.
            raise ImageError("PNG tRNS transparency not supported; convert to RGBA first")
        elif name == b"IEND":
            if size or not has_idat or has_iend or index != len(data):
                raise ImageError("invalid PNG end")
            has_iend = True
            break
        elif name[0] & 32 == 0:
            raise ImageError("unknown critical PNG chunk")
        elif has_idat:
            idat_closed = True
    if not (has_ihdr and has_idat and has_iend):
        raise ImageError("PNG required chunks missing")

    stride = width * bpp
    expected = height * (stride + 1)
    try:
        decoder = zlib.decompressobj()
        raw = decoder.decompress(bytes(compressed), expected + 1)
        if not decoder.eof or decoder.unused_data or decoder.unconsumed_tail or len(raw) != expected:
            raise ImageError("compressed PNG output length or end marker invalid")
        if decoder.flush():
            raise ImageError("unexpected trailing decoded bytes")
    except zlib.error as exc:
        raise ImageError("bad compressed pixel stream") from exc

    rgba = bytearray(width * height * 4)
    previous = bytearray(stride)
    cursor = 0
    for y in range(height):
        filter_id = raw[cursor]
        cursor += 1
        if filter_id > 4:
            raise ImageError("unsupported PNG filter")
        row = bytearray(raw[cursor:cursor + stride])
        cursor += stride
        for x in range(stride):
            left = row[x - bpp] if x >= bpp else 0
            above = previous[x]
            upper_left = previous[x - bpp] if x >= bpp else 0
            if filter_id == 1:
                row[x] = (row[x] + left) & 255
            elif filter_id == 2:
                row[x] = (row[x] + above) & 255
            elif filter_id == 3:
                row[x] = (row[x] + ((left + above) // 2)) & 255
            elif filter_id == 4:
                row[x] = (row[x] + _paeth(left, above, upper_left)) & 255
        for x in range(width):
            src = x * bpp
            dst = (y * width + x) * 4
            rgba[dst:dst + 3] = row[src:src + 3]
            rgba[dst + 3] = row[src + 3] if bpp == 4 else 255
        previous = row
    return width, height, bytes(rgba)


def encode_png(width: int, height: int, rgba: bytes) -> bytes:
    if (not 1 <= width <= MAX_DIMENSION or not 1 <= height <= MAX_DIMENSION
            or width * height > MAX_OUTPUT_PIXELS or len(rgba) != width * height * 4):
        raise ImageError("unsafe output dimensions")
    stride = width * 4
    scanlines = b"".join(
        b"\0" + rgba[y * stride:(y + 1) * stride] for y in range(height)
    )
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return (PNG_SIGNATURE + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", zlib.compress(scanlines, 9))
            + _chunk(b"IEND", b""))


def trim_rgba(width: int, height: int, rgba: bytes,
              padding: int = 0, alpha_cutoff: int = 0) -> tuple[int, int, bytes, dict]:
    if not 0 <= padding <= 64 or not 0 <= alpha_cutoff <= 254:
        raise ImageError("invalid padding or alpha cutoff")
    # Constant auxiliary memory, including a large 4096x4096 texture.
    min_x, min_y, max_x, max_y = width, height, -1, -1
    for y in range(height):
        for x in range(width):
            if rgba[(y * width + x) * 4 + 3] > alpha_cutoff:
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
    if max_x < 0:
        raise ImageError("entire image is transparent at selected alpha cutoff")
    new_w, new_h = max_x - min_x + 1 + 2 * padding, max_y - min_y + 1 + 2 * padding
    if new_w > MAX_DIMENSION or new_h > MAX_DIMENSION or new_w * new_h > MAX_OUTPUT_PIXELS:
        raise ImageError("padded sprite is too large")
    out = bytearray(new_w * new_h * 4)
    row_bytes = (max_x - min_x + 1) * 4
    for y in range(min_y, max_y + 1):
        old_at = (y * width + min_x) * 4
        new_at = ((y - min_y + padding) * new_w + padding) * 4
        out[new_at:new_at + row_bytes] = rgba[old_at:old_at + row_bytes]
    bounds = {"x": min_x, "y": min_y, "width": max_x - min_x + 1,
              "height": max_y - min_y + 1, "padding": padding,
              "alpha_cutoff": alpha_cutoff}
    return new_w, new_h, bytes(out), bounds


def scale_nearest(width: int, height: int, rgba: bytes, multiplier: int) -> tuple[int, int, bytes]:
    if multiplier not in (1, 2, 3):
        raise ImageError("only 1x/2x/3x nearest-neighbor exports supported")
    tw, th = width * multiplier, height * multiplier
    if tw > MAX_DIMENSION or th > MAX_DIMENSION or tw * th > MAX_OUTPUT_PIXELS:
        raise ImageError("scaled sprite exceeds size budget")
    if multiplier == 1:
        return width, height, rgba
    row_data = []
    for y in range(height):
        row = bytearray()
        for x in range(width):
            p = rgba[(y * width + x) * 4:(y * width + x + 1) * 4]
            row.extend(p * multiplier)
        row_data.extend([bytes(row)] * multiplier)
    return tw, th, b"".join(row_data)


def create_candidate_exports(source: Path, output_dir: Path,
                             padding: int = 0, alpha_cutoff: int = 0,
                             multipliers: tuple[int, ...] = (1, 2, 3)) -> dict:
    """Write a never-overwritten candidate with source SHA lineage. No approval."""
    source, output_dir = Path(source), Path(output_dir)
    if source.is_symlink() or not source.is_file() or source.suffix.lower() != ".png":
        raise ImageError("regular original PNG file required")
    if source.stat().st_size > MAX_INPUT_BYTES:
        raise ImageError("source too large")
    raw_source = source.read_bytes()
    width, height, rgba = decode_png(raw_source)
    w, h, cropped, bounds = trim_rgba(width, height, rgba, padding, alpha_cutoff)
    if not multipliers or len(set(multipliers)) != len(multipliers):
        raise ImageError("missing/duplicated scale")
    if any(n not in (1, 2, 3) for n in multipliers):
        raise ImageError("unsupported scale")
    # Generate and inspect everything before creating a single output.
    outputs = {}
    entries = []
    for scale in sorted(multipliers):
        sw, sh, sr = scale_nearest(w, h, cropped, scale)
        encoded = encode_png(sw, sh, sr)
        name = "sprite_%dx.png" % scale
        outputs[name] = encoded
        entries.append({"path": name, "width": sw, "height": sh,
                        "sha256": hashlib.sha256(encoded).hexdigest()})
    receipt = {
        "schema_version": 1,
        "stage": "CANDIDATE_NOT_APPROVED",
        "operation": "alpha_trim_and_nearest_scale_v1",
        "source_sha256": hashlib.sha256(raw_source).hexdigest(),
        "source_dimensions": [width, height],
        "trimmed_bounds": bounds,
        "outputs": entries,
    }
    outputs["candidate_manifest.json"] = (json.dumps(
        receipt, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")
    root = output_dir.resolve()
    repo_root = Path(__file__).resolve().parents[2]
    if (output_dir.is_symlink() or root.is_relative_to(repo_root)
            or source.resolve().is_relative_to(root)):
        raise ImageError("candidates must be outside repo and separate from original source")
    if output_dir.exists() and not output_dir.is_dir():
        raise ImageError("candidate output is not directory")
    output_dir.mkdir(parents=True, exist_ok=True)
    if output_dir.is_symlink():
        raise ImageError("unsafe candidate output symlink")
    for name in outputs:
        if (output_dir / name).exists() or (output_dir / name).is_symlink():
            raise ImageError("refusing to overwrite candidate file " + name)
    created = []
    try:
        for name, payload in outputs.items():
            destination = output_dir / name
            with destination.open("xb") as stream:
                created.append(destination)
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
    except (OSError, ValueError):
        # Roll back only exact candidate files written by this attempt.
        for owned_file in created:
            owned_file.unlink(missing_ok=True)
        raise
    return receipt


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--padding", type=int, default=0)
    parser.add_argument("--alpha-cutoff", type=int, default=0)
    parser.add_argument("--scales", type=int, nargs="+", default=[1, 2, 3])
    options = parser.parse_args(argv)
    try:
        receipt = create_candidate_exports(
            options.source, options.output_dir,
            options.padding, options.alpha_cutoff, tuple(options.scales)
        )
        print(json.dumps(receipt, indent=2, sort_keys=True))
        return 0
    except (ImageError, OSError) as exc:
        parser.exit(status=2, message="VF04_REJECTED: %s\n" % exc)


if __name__ == "__main__":
    raise SystemExit(main())
