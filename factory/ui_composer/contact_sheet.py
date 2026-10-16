"""VF-07 read-only five-game contact sheet from a VERIFIED showcase folder.

Displays five game columns x three conceptual screens at fixed thumbnail
size, drawing an original 5x7 ASCII raster label. Output is a single
external NEW PNG only upon explicit request; it never approves artwork,
modifies the source images or creates interactive UI.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from factory.image_processor.png_pipeline import encode_png, decode_png, ImageError
from factory.validators.verify_generated_kits import verify_showcase, BundleError

PROFILES = ("Coral_Rescue", "Garage_Legends", "Dino_Islands",
            "The_Fractured_Realms", "Wonder_Pop")
PAGES = ("home", "gameplay", "world_map")
THUMB_W, THUMB_H = 144, 256
HEADER = 25
PAD = 12
CELL_W = THUMB_W + 2 * PAD
CELL_H = THUMB_H + HEADER + 2 * PAD
STAGE = "CANDIDATE_NOT_OWNER_APPROVED"
# Compact hand-authored five by seven pixel glyphs, no fonts or providers.
FONT = {
    "A": ("01110","10001","10001","11111","10001","10001","10001"),
    "B": ("11110","10001","10001","11110","10001","10001","11110"),
    "C": ("01111","10000","10000","10000","10000","10000","01111"),
    "D": ("11110","10001","10001","10001","10001","10001","11110"),
    "E": ("11111","10000","10000","11110","10000","10000","11111"),
    "F": ("11111","10000","10000","11110","10000","10000","10000"),
    "G": ("01111","10000","10000","10111","10001","10001","01111"),
    "H": ("10001","10001","10001","11111","10001","10001","10001"),
    "I": ("11111","00100","00100","00100","00100","00100","11111"),
    "J": ("00111","00010","00010","00010","10010","10010","01100"),
    "K": ("10001","10010","10100","11000","10100","10010","10001"),
    "L": ("10000","10000","10000","10000","10000","10000","11111"),
    "M": ("10001","11011","10101","10101","10001","10001","10001"),
    "N": ("10001","11001","10101","10011","10001","10001","10001"),
    "O": ("01110","10001","10001","10001","10001","10001","01110"),
    "P": ("11110","10001","10001","11110","10000","10000","10000"),
    "Q": ("01110","10001","10001","10001","10101","10010","01101"),
    "R": ("11110","10001","10001","11110","10100","10010","10001"),
    "S": ("01111","10000","10000","01110","00001","00001","11110"),
    "T": ("11111","00100","00100","00100","00100","00100","00100"),
    "U": ("10001","10001","10001","10001","10001","10001","01110"),
    "V": ("10001","10001","10001","10001","10001","01010","00100"),
    "W": ("10001","10001","10001","10101","10101","10101","01010"),
    "X": ("10001","10001","01010","00100","01010","10001","10001"),
    "Y": ("10001","10001","01010","00100","00100","00100","00100"),
    "Z": ("11111","00001","00010","00100","01000","10000","11111"),
    "0": ("01110","10011","10101","10101","11001","10001","01110"),
    "1": ("00100","01100","00100","00100","00100","00100","01110"),
    "2": ("01110","10001","00001","00110","01000","10000","11111"),
    "3": ("11110","00001","00001","00110","00001","00001","11110"),
    "4": ("00010","00110","01010","10010","11111","00010","00010"),
    "5": ("11111","10000","10000","11110","00001","00001","11110"),
    "6": ("00111","01000","10000","11110","10001","10001","01110"),
    "7": ("11111","00001","00010","00100","01000","01000","01000"),
    "8": ("01110","10001","10001","01110","10001","10001","01110"),
    "9": ("01110","10001","10001","01111","00001","00010","11100"),
    " ": ("00000",)*7,
    "_": ("00000","00000","00000","00000","00000","00000","11111")
}


class ContactSheetError(ValueError):
    pass


def _place(canvas: bytearray, width: int, height: int, x: int, y: int,
           rgb: tuple[int,int,int]):
    if 0 <= x < width and 0 <= y < height:
        offset = (y * width + x) * 4
        canvas[offset:offset+4] = bytes((*rgb,255))


def _text(canvas: bytearray, width: int, height: int,
          text: str, x: int, y: int, rgb: tuple[int,int,int]):
    for char in text.upper():
        glyph = FONT.get(char)
        if glyph is None:
            raise ContactSheetError("unsupported label character")
        for row, bits in enumerate(glyph):
            for col, bit in enumerate(bits):
                if bit == "1":
                    _place(canvas, width, height, x+col, y+row, rgb)
        x += 6


def build_contact_sheet(source_folder: Path) -> tuple[dict, bytes]:
    valid = verify_showcase(source_folder)
    if valid["screen_count"] != 15:
        raise ContactSheetError("source showcase incomplete")
    folder = Path(source_folder)
    cols, rows = 5, 3
    width, height = cols * CELL_W + PAD, rows * CELL_H + PAD
    canvas = bytearray(bytes((20, 25, 36, 255)) * (width * height))
    cells = []
    for row,page in enumerate(PAGES):
        for col,profile in enumerate(PROFILES):
            filename = "preview_" + profile + "_" + page + ".png"
            source = (folder / filename).read_bytes()
            src_w, src_h, rgba = decode_png(source)
            x0 = col * CELL_W + PAD
            y0 = row * CELL_H + PAD
            for dy in range(THUMB_H):
                src_y = min(src_h - 1, dy * src_h // THUMB_H)
                for dx in range(THUMB_W):
                    src_x = min(src_w - 1, dx * src_w // THUMB_W)
                    src = (src_y * src_w + src_x) * 4
                    dst = ((y0 + HEADER + dy) * width + (x0 + dx)) * 4
                    canvas[dst:dst + 4] = rgba[src:src + 4]
            title = profile.replace("_", " ")
            # Clear human-readable label by tiny hand-drawn raster.
            _text(canvas, width, height, title[:22], x0, y0+2,
                  (237, 243, 255))
            _text(canvas, width, height, page.replace("_", " ").upper(),
                  x0, y0+13, (155, 224, 242))
            cells.append({
                "profile_id":profile, "screen_key":page,
                "source_png_sha256":hashlib.sha256(source).hexdigest(),
                "thumb_rect_top_left":[x0, y0 + HEADER, THUMB_W, THUMB_H]
            })
    png = encode_png(width,height,bytes(canvas))
    return {
        "schema_version":1, "stage":STAGE,
        "generator":"VF07_FIVE_GAME_CONTACT_SHEET_V01",
        "source_showcase_status":"VERIFIED_CANDIDATE_ONLY",
        "columns":cols,"rows":rows,"dimensions":[width,height],
        "cells":cells,"cell_count":15,
        "contact_png_sha256":hashlib.sha256(png).hexdigest(),
        "interactive_ui_enabled":False,
        "owner_visual_approval":False,
        "asset_rights_verified":False,
        "real_device_verified":False,
    },png


def _link(path: Path)->bool:
    if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
        return True
    try:
        info=path.stat(follow_symlinks=False)
    except OSError:
        return False
    return bool(getattr(info,"st_file_attributes",0) &
                getattr(stat,"FILE_ATTRIBUTE_REPARSE_POINT",0))


def save_once(target: Path, report: dict, png: bytes) -> None:
    path=Path(target)
    if (path.exists() or path.is_symlink() or
            path.suffix.lower()!=".png" or not path.parent.is_dir() or
            any(_link(x) for x in (path.parent,*path.parent.parents)) or
            path.parent.resolve(strict=True).is_relative_to(ROOT) or
            report.get("stage")!=STAGE or
            report.get("owner_visual_approval") is not False or
            hashlib.sha256(png).hexdigest()!=report.get("contact_png_sha256")):
        raise ContactSheetError("contact sheet target must be NEW unapproved external PNG")
    with path.open("xb") as stream:
        stream.write(png)
        stream.flush()
        os.fsync(stream.fileno())


def main(argv=None)->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate",type=Path,required=True)
    parser.add_argument("--output-file",type=Path)
    args=parser.parse_args(argv)
    try:
        report,png=build_contact_sheet(args.candidate)
        if args.output_file:
            save_once(args.output_file,report,png)
        report["output_saved"]=args.output_file is not None
        print(json.dumps(report,indent=2,sort_keys=True))
        return 0
    except (BundleError,ContactSheetError,ImageError,OSError,ValueError) as exc:
        print("VUF_CONTACT_SHEET_REJECTED: "+str(exc),file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
