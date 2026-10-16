"""Read-only independent checks of generated VF04/VF06 candidate PNG bundles.

These checks detect corrupted or mismatched candidate outputs. They cannot
prove visual quality, rights, device performance or owner approval. No writes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from factory.image_processor.png_pipeline import decode_png, ImageError

SHA = re.compile(r"[0-9a-f]{64}\Z")
FX_PRESETS = frozenset(("BubbleRise", "MatchBurst", "StarSparkle",
                        "SoftDrift", "PortalPulse"))
SHAPES = ("circle", "triangle", "diamond", "star", "crescent", "shield")
PROFILES = frozenset(("Coral_Rescue", "Garage_Legends", "Dino_Islands",
                      "The_Fractured_Realms", "Wonder_Pop"))
MAX_MANIFEST = 128 * 1024


class BundleError(ValueError):
    pass


def _pairs(pairs):
    output = {}
    for key, value in pairs:
        if key in output:
            raise BundleError("duplicate manifest key")
        output[key] = value
    return output


def _link(path: Path) -> bool:
    if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
        return True
    return bool(getattr(path.stat(follow_symlinks=False),
                        "st_file_attributes", 0) &
                getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def _bundle(directory: Path) -> Path:
    folder = Path(directory)
    if not folder.is_dir() or _link(folder) or any(_link(x) for x in folder.parents):
        raise BundleError("expected unlinked existing candidate directory")
    real = folder.resolve(strict=True)
    if real.is_relative_to(ROOT):
        raise BundleError("candidate should not live inside Git source")
    return real


def _read(folder: Path, name: str, limit: int) -> bytes:
    if not isinstance(name, str) or "/" in name or "\\" in name or name in ("", ".", ".."):
        raise BundleError("only direct expected candidate filenames allowed")
    path = folder / name
    if not path.is_file() or _link(path) or path.stat().st_size > limit:
        raise BundleError("missing, linked or oversized candidate " + name)
    return path.read_bytes()


def _sha(raw: bytes, expected: str) -> None:
    if not isinstance(expected, str) or SHA.fullmatch(expected) is None:
        raise BundleError("bad SHA256 receipt")
    if hashlib.sha256(raw).hexdigest() != expected:
        raise BundleError("candidate content differs from SHA256 receipt")


def _manifest(folder: Path, name: str) -> dict:
    try:
        result = json.loads(_read(folder, name, MAX_MANIFEST).decode("utf-8"),
                            object_pairs_hook=_pairs)
    except (UnicodeError, ValueError) as exc:
        raise BundleError("invalid candidate manifest: " + str(exc)) from exc
    if not isinstance(result, dict) or result.get("schema_version") != 1:
        raise BundleError("unsupported bundle manifest")
    return result


def _region(pixels: bytes, atlas_width: int, rect: list[int]) -> bytes:
    if not isinstance(rect, list) or len(rect) != 4 or any(
            type(x) is not int for x in rect):
        raise BundleError("invalid rectangle")
    x, y, width, height = rect
    if (x < 0 or y < 0 or width < 1 or height < 1 or
            x + width > atlas_width):
        raise BundleError("rectangle exceeds atlas bounds")
    return b"".join(
        pixels[((y + row) * atlas_width + x) * 4:
               ((y + row) * atlas_width + x + width) * 4]
        for row in range(height))


def verify_fx(directory: Path) -> dict:
    folder = _bundle(directory)
    receipt = _manifest(folder, "fx_manifest.json")
    if (receipt.get("stage") != "CANDIDATE_NOT_OWNER_APPROVED" or
            receipt.get("generator") != "VF06_PROCEDURAL_FX_SHEET_V01" or
            receipt.get("preset_id") not in FX_PRESETS or
            receipt.get("asset_rights_verified") is not False or
            receipt.get("owner_visual_approval") is not False or
            receipt.get("engine_side_effects_allowed") is not False or
            receipt.get("reduced_motion_policy") != "STATIC_VIEW_ONLY" or
            receipt.get("atlas_path") != "fx_sheet.png" or
            receipt.get("reduced_motion_path") != "reduced_motion.png"):
        raise BundleError("FX bundle approval/rights/feature safety guard failed")
    frames, side, cols, rows = (receipt.get(x) for x in
                                ("frame_count", "frame_side", "columns", "rows"))
    if (any(type(x) is not int for x in (frames, side, cols, rows)) or
            not 2 <= frames <= 32 or not 16 <= side <= 128 or
            not 1 <= cols <= frames or rows != (frames + cols - 1) // cols):
        raise BundleError("FX frame count/grid invalid")
    atlas = _read(folder, "fx_sheet.png", 64 * 1024 * 1024)
    still = _read(folder, "reduced_motion.png", 64 * 1024 * 1024)
    _sha(atlas, receipt.get("atlas_sha256"))
    _sha(still, receipt.get("reduced_motion_sha256"))
    w, h, pixels = decode_png(atlas)
    sw, sh, _ = decode_png(still)
    if (w, h) != (cols * side, rows * side) or (sw, sh) != (side, side):
        raise BundleError("FX sheet/still actual PNG dimensions wrong")
    entries = receipt.get("animation_frames")
    if not isinstance(entries, list) or len(entries) != frames:
        raise BundleError("FX frame index count changed")
    for i, item in enumerate(entries):
        if (not isinstance(item, dict) or type(item.get("frame")) is not int or
                item["frame"] != i or
                item.get("pixel_rect_top_left") !=
                    [(i % cols) * side, (i // cols) * side, side, side]):
            raise BundleError("FX frame rectangle/order changed")
        block = _region(pixels, w, item["pixel_rect_top_left"])
        _sha(block, item.get("rgba_sha256"))
    return {"stage": "VERIFIED_CANDIDATE_ONLY", "kind": "fx",
            "preset_id": receipt["preset_id"], "frames_checked": frames,
            "rights_verified": False, "visual_approved": False}


def verify_tiles(directory: Path) -> dict:
    folder = _bundle(directory)
    receipt = _manifest(folder, "tile_manifest.json")
    if (receipt.get("stage") != "CANDIDATE_NOT_OWNER_APPROVED" or
            receipt.get("generator") != "VF04_SIX_SILHOUETTE_TILE_KIT_V01" or
            receipt.get("profile_id") not in PROFILES or
            receipt.get("silhouette_keys") != list(SHAPES) or
            receipt.get("asset_rights_verified") is not False or
            receipt.get("gameplay_bindings_enabled") is not False or
            receipt.get("owner_visual_approval") is not False or
            receipt.get("original_art") != "MATHEMATICAL_PROTOTYPE_NOT_OWNER_ART"):
        raise BundleError("tile kit policy or profile violation")
    side = receipt.get("side")
    if type(side) is not int or not 24 <= side <= 128:
        raise BundleError("invalid tile side")
    atlas_png = _read(folder, "tile_atlas.png", 64 * 1024 * 1024)
    _sha(atlas_png, receipt.get("atlas_sha256"))
    w, h, pixels = decode_png(atlas_png)
    if (w, h) != (3 * side, 2 * side) or receipt.get("atlas_dimensions") != [w, h]:
        raise BundleError("wrong tile atlas bounds")
    tiles = receipt.get("tiles")
    if not isinstance(tiles, list) or len(tiles) != 6:
        raise BundleError("expected exactly six silhouette prototypes")
    alpha_masks = set()
    for i, item in enumerate(tiles):
        shape = SHAPES[i]
        filename = "tile_" + shape + ".png"
        expected = [i % 3 * side, i // 3 * side, side, side]
        if (not isinstance(item, dict) or item.get("shape") != shape or
                item.get("file") != filename or
                item.get("pixel_rect_top_left") != expected):
            raise BundleError("wrong shape order/bounds")
        source = _read(folder, filename, 8 * 1024 * 1024)
        _sha(source, item.get("file_sha256"))
        tw, th, rgba = decode_png(source)
        if ((tw, th) != (side, side) or
                rgba != _region(pixels, w, expected)):
            raise BundleError("tile pixels differ from atlas rect")
        _sha(rgba, item.get("rgba_sha256"))
        alpha_masks.add(hashlib.sha256(rgba[3::4]).hexdigest())
    if len(alpha_masks) != 6:
        raise BundleError("six tiles are not distinct in silhouette")
    return {"stage": "VERIFIED_CANDIDATE_ONLY", "kind": "tiles",
            "profile_id": receipt["profile_id"], "shapes_checked": 6,
            "rights_verified": False, "visual_approved": False}


def verify_scene(directory: Path) -> dict:
    folder = _bundle(directory)
    receipt = _manifest(folder, "scene_receipt.json")
    if (receipt.get("stage") != "CANDIDATE_NOT_OWNER_APPROVED" or
            receipt.get("generator") != "VF04_RGBA_LAYER_COMPOSITOR_V01" or
            receipt.get("profile_id") not in PROFILES or
            receipt.get("original_rights_verified") is not False or
            receipt.get("owner_visual_approved") is not False or
            receipt.get("image_path") != "scene.png"):
        raise BundleError("scene candidate must remain not approved")
    actual = _read(folder, "scene.png", 64 * 1024 * 1024)
    _sha(actual, receipt.get("image_sha256"))
    w, h, _ = decode_png(actual)
    if receipt.get("dimensions") != [w, h] or w > 2048 or h > 2048:
        raise BundleError("scene canvas dimensions mismatch")
    layers = receipt.get("layers")
    if not isinstance(layers, list) or not 1 <= len(layers) <= 16:
        raise BundleError("scene receipt source layers missing")
    for index, item in enumerate(layers):
        if (not isinstance(item, dict) or item.get("draw_order") != index or
                not isinstance(item.get("source_sha256"), str) or
                SHA.fullmatch(item["source_sha256"]) is None):
            raise BundleError("scene source receipt missing/invalid")
    return {"stage": "VERIFIED_CANDIDATE_ONLY", "kind": "scene",
            "profile_id": receipt["profile_id"], "layers_recorded": len(layers),
            "original_source_bytes_reverified": False,
            "rights_verified": False, "visual_approved": False}



def verify_showcase(directory: Path) -> dict:
    """Verify all fifteen actual five-game concept PNGs, never approve them."""
    folder = _bundle(directory)
    manifest = _manifest(folder, "showcase_manifest.json")
    profiles = ("Coral_Rescue", "Garage_Legends", "Dino_Islands",
                "The_Fractured_Realms", "Wonder_Pop")
    pages = ("home", "gameplay", "world_map")
    dims = manifest.get("dimensions")
    if (manifest.get("stage") != "CANDIDATE_NOT_OWNER_APPROVED" or
            manifest.get("generator") != "VF07_FIVE_GAME_CONCEPT_SCREENS_V01" or
            manifest.get("file_count") != 15 or
            manifest.get("profile_ids") != list(profiles) or
            manifest.get("screen_keys") != list(pages) or
            dims not in ([360, 640], [720, 1280]) or
            manifest.get("interactive_ui_enabled") is not False or
            manifest.get("owner_visual_approval") is not False or
            manifest.get("asset_rights_verified") is not False or
            manifest.get("real_device_verified") is not False or
            manifest.get("original_art") != "MATHEMATICAL_CONCEPT_ONLY"):
        raise BundleError("showcase is not a strictly unapproved five-game concept")
    rows = manifest.get("screens")
    if not isinstance(rows, list) or len(rows) != 15:
        raise BundleError("expected exactly fifteen concept screens")
    scale = dims[0] // 360
    seen = set()
    for idx, row in enumerate(rows):
        profile, page = profiles[idx // 3], pages[idx % 3]
        name = "preview_" + profile + "_" + page + ".png"
        if (not isinstance(row, dict) or row.get("profile_id") != profile or
                row.get("screen_key") != page or row.get("file") != name or
                row.get("dimensions") != dims or
                row.get("screen_state") != "VISUAL_CONCEPT_NOT_INTERACTIVE" or
                row.get("interactive") is not False or
                type(row.get("render_scale")) is not int or
                row["render_scale"] != scale or
                type(row.get("seed")) is not int or
                not 0 <= row["seed"] <= 9999 or name in seen):
            raise BundleError("concept screenshot identity/safety contract mismatch")
        seen.add(name)
        for field in ("style_source_sha256", "tile_kit_atlas_sha256"):
            value = row.get(field)
            if not isinstance(value, str) or SHA.fullmatch(value) is None:
                raise BundleError("concept source SHA receipt format invalid")
        raw = _read(folder, name, 12 * 1024 * 1024)
        _sha(raw, row.get("png_sha256"))
        w, h, rgba = decode_png(raw)
        if [w, h] != dims or any(alpha != 255 for alpha in rgba[3::4]):
            raise BundleError("concept PNG dimensions or opacity wrong")
    return {
        "stage": "VERIFIED_CANDIDATE_ONLY", "kind": "showcase",
        "screen_count": len(seen), "profile_count": len(profiles),
        "original_rights_verified": False,
        "interactive_ui_enabled": False,
        "real_device_verified": False,
        "visual_approved": False
    }



def verify_scene_sources(directory: Path, original_manifest: Path,
                         original_root: Path) -> dict:
    """Re-render from intact original source layers, not copyright proof.

    Requires explicit, separately supplied original manifest and source root.
    A source hash can match without granting commercial usage rights.
    """
    previous = verify_scene(directory)
    folder = _bundle(directory)
    stored = _manifest(folder, "scene_receipt.json")
    from factory.image_processor.layer_compositor import (
        CompositorError, render_candidate
    )
    try:
        expected_receipt, expected_png = render_candidate(
            Path(original_manifest), Path(original_root))
    except (CompositorError, OSError, ImageError, ValueError) as exc:
        raise BundleError("scene originals cannot be verified: " + str(exc)) from exc
    if (expected_receipt["original_manifest_sha256"] !=
            stored.get("original_manifest_sha256") or
            expected_receipt["image_sha256"] != stored.get("image_sha256") or
            expected_receipt["source_bytes"] != stored.get("source_bytes") or
            expected_receipt["layers"] != stored.get("layers") or
            expected_receipt["profile_id"] != stored.get("profile_id") or
            expected_png != _read(folder, "scene.png", 64 * 1024 * 1024)):
        raise BundleError("recomposited original source bytes differ from candidate")
    previous["original_source_bytes_reverified"] = True
    previous["original_layers_reverified"] = len(expected_receipt["layers"])
    previous["rights_verified"] = False
    previous["visual_approved"] = False
    return previous


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=("fx", "tiles", "scene", "showcase"))
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--original-manifest", type=Path)
    parser.add_argument("--original-root", type=Path)
    args = parser.parse_args(argv)
    try:
        original_inputs = (args.original_manifest is not None,
                           args.original_root is not None)
        if any(original_inputs) and (
                args.kind != "scene" or not all(original_inputs)):
            raise BundleError("originals audit requires scene plus BOTH source paths")
        fn = {"fx": verify_fx, "tiles": verify_tiles,
              "scene": verify_scene, "showcase": verify_showcase}[args.kind]
        receipt = (verify_scene_sources(args.candidate,
                   args.original_manifest, args.original_root)
                   if all(original_inputs) else fn(args.candidate))
        print(json.dumps(receipt, indent=2, sort_keys=True))
        return 0
    except (BundleError, ImageError, OSError, UnicodeError, ValueError) as exc:
        print("VUF_BUNDLE_REJECTED: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
