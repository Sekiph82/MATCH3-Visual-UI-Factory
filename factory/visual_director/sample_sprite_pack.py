"""VUF R52 / M05: five-theme candidate sprite samples and real VF-04 atlas pack.

Original mathematical prototypes, never production art. INTERNAL_REUSE:
silhouette_kit._style/_raster, real Engine enum skin contracts,
obstacle_skin_states, png_pipeline and atlas_pipeline. No copied artwork,
new provider, game rule fork, importer modifications or payment.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
from pathlib import Path

from factory.visual_director.silhouette_kit import (
    PROFILES, SHAPES, MIN_SIDE, MAX_SIDE, _raster, _style,
)
from factory.visual_director.special_skin_map import build_skin_contract
from factory.visual_director.obstacle_skin_states import (
    build_state_map, source_example_definitions,
)
from factory.image_processor.png_pipeline import encode_png
from factory.image_processor.atlas_pipeline import create_atlas_candidate
from factory.validators.atlas_candidate_audit import audit_candidate

ROOT = Path(__file__).resolve().parents[2]
ROLES = ("obstacle", "collectible", "goal", "equipment", "booster")


class SamplePackError(ValueError):
    pass


def _stamp(rgba: bytes, side: int, number: int, hp: int | None = None) -> bytes:
    """Immutable source shape + tiny unique visible white/bar identifying mark."""
    pixels = bytearray(rgba)
    for bit in range(12):
        x = 2 + bit * max(1, (side - 5) // 12)
        y = 1
        tint = (245, 245, 245, 200) if (number >> bit) & 1 else (40, 50, 60, 85)
        for yy in (y, y + 1):
            at = (yy * side + x) * 4
            pixels[at:at + 4] = bytes(tint)
    if hp is not None:
        for i in range(max(1, hp)):
            x = 2 + i * 3
            if x >= side - 2:
                break
            at = ((side - 2) * side + x) * 4
            pixels[at:at + 4] = bytes((245, 245, 245, 180))
    return bytes(pixels)


def _mixed(left: bytes, right: bytes, side: int) -> bytes:
    if len(left) != side * side * 4 or len(right) != len(left):
        raise SamplePackError("sprite source shape dimensions invalid")
    out = bytearray(side * side * 4)
    for y in range(side):
        for x in range(side):
            index = (y * side + x) * 4
            source = left if x < side // 2 else right
            out[index:index + 4] = source[index:index + 4]
    return bytes(out)


def build_sample_pack(profile: str, side: int = 48) -> tuple[dict, dict[str, bytes]]:
    """Build sample sprites without file writes. No assertions of polished art."""
    if profile not in PROFILES or type(side) is not int or not MIN_SIDE <= side <= MAX_SIDE:
        raise SamplePackError("invalid five-game profile or prototype tile size")
    palette, style_sha = _style(profile)
    base = {s: _raster(s, side, palette) for s in SHAPES}
    specials = build_skin_contract(profile)
    obstacles = build_state_map(profile, source_example_definitions())
    files = {}
    receipts = []
    counter = 1

    def add(semantic: str, pixels: bytes, *, family: str, hp=None):
        nonlocal counter
        if not isinstance(semantic, str) or not semantic or len(semantic) > 180:
            raise SamplePackError("invalid prototype ID")
        name = "sample_" + format(counter, "03d") + ".png"
        stamped = _stamp(pixels, side, counter, hp)
        png = encode_png(side, side, stamped)
        files[name] = png
        receipts.append({
            "asset_id": semantic,
            "family": family,
            "file": name,
            "png_sha256": hashlib.sha256(png).hexdigest(),
            "rgba_sha256": hashlib.sha256(stamped).hexdigest(),
            "sample_not_final": True,
        })
        counter += 1

    for i, shape in enumerate(SHAPES):
        add(profile.lower() + ".tile." + shape, base[shape], family="tile")

    for i, row in enumerate(specials["single_specials"]):
        add(row["sprite_key"], base[SHAPES[i]], family="special")

    names = {row["engine_enum_name"]: i for i, row in enumerate(specials["single_specials"])}
    for row in specials["unordered_special_pairs"]:
        a, b = row["engine_pair"]
        pixels = _mixed(base[SHAPES[names[a]]], base[SHAPES[names[b]]], side)
        add(row["sprite_key"], pixels, family="combo")

    for i, row in enumerate(obstacles["assets"]):
        shape = SHAPES[i % len(SHAPES)]
        for state in row["states"]:
            add(state["sprite_key"], base[shape], family=row["role"],
                hp=state["durability"] if row["role"] == "obstacle" else None)
    expected = 6 + 5 + 15 + sum(len(a["states"]) for a in obstacles["assets"])
    if len(receipts) != expected or len({r["asset_id"] for r in receipts}) != expected:
        raise SamplePackError("incomplete or duplicate sample skin assets")
    return {
        "schema_version": 1,
        "stage": "CANDIDATE_NOT_OWNER_APPROVED",
        "generator": "VUF_R52_SAMPLE_SPRITE_PACK_V1",
        "profile_id": profile,
        "side": side,
        "style_bible_sha256": style_sha,
        "engine_special_source_blob_sha": specials["engine_source_blob_sha"],
        "engine_obstacle_source_blob_sha": obstacles["engine_obstacle_source_blob_sha"],
        "prototype_count": expected,
        "assets": receipts,
        "source_art": "ORIGINAL_MATHEMATICAL_PLACEHOLDER",
        "right_to_production_assets_verified": False,
        "owner_aesthetic_approval": False,
        "engine_final_sha_verified": False,
        "gameplay_or_rewards_authority": False,
        "real_device_verified": False,
        "release_allowed": False,
    }, files


def _linked(path: Path) -> bool:
    if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
        return True
    try:
        flag = getattr(path.stat(follow_symlinks=False), "st_file_attributes", 0)
    except OSError as exc:
        raise SamplePackError("cannot inspect output path") from exc
    return bool(flag & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def export_sample_pack(profile: str, output: Path, side: int = 48) -> dict:
    """Write only to one NEW external folder, then use VF04 real atlas packer."""
    output = Path(output)
    if output.exists() or output.is_symlink():
        raise SamplePackError("refusing to overwrite existing sample pack")
    parent = output.parent
    if not parent.is_dir() or _linked(parent) or any(
            _linked(p) for p in parent.parents if p.exists()):
        raise SamplePackError("sample destination must have an unlinked existing parent")
    if parent.resolve(strict=True).is_relative_to(ROOT):
        raise SamplePackError("sample packs must remain outside repository")
    manifest, contents = build_sample_pack(profile, side)
    output.mkdir()
    sources = {}
    for name, png in sorted(contents.items()):
        file = output / name
        with file.open("xb") as handle:
            handle.write(png)
            handle.flush()
            os.fsync(handle.fileno())
        sources[name[:-4]] = file
    with (output / "sample_manifest.json").open("xb") as handle:
        handle.write((json.dumps(manifest, sort_keys=True, indent=2) + "\n").encode())
        handle.flush()
        os.fsync(handle.fileno())
    atlas_dir = output / "atlas"
    atlas_manifest = create_atlas_candidate(sources, atlas_dir, padding=2, extrude=1)
    required = [r["file"][:-4] for r in manifest["assets"]]
    report = audit_candidate(atlas_dir, required_ids=required)
    return {
        "profile_id": profile,
        "sample_count": len(contents),
        "atlas_sha256": atlas_manifest["atlas_sha256"],
        "atlas_audit": report,
        "release_allowed": False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True, choices=PROFILES)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--side", type=int, default=48)
    args = parser.parse_args(argv)
    try:
        report = export_sample_pack(args.profile, args.output_dir, args.side)
    except (SamplePackError, OSError, ValueError) as exc:
        parser.exit(2, "FAIL: " + str(exc) + "\n")
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
