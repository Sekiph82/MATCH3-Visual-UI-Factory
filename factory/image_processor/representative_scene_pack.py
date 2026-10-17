"""VUF-M06: layered, deterministic *candidate* scenery for five game profiles.

This is NOT a shipping game screen, owner-approved art, parallax runtime, or
text/button/Engine renderer. INTERNAL_REUSE: existing draft Style Bible via
silhouette_kit._style, PNG encode/decode, and the project's fail-closed
candidate-only workflow. Geometric primitives are authored here, not scraped.
No file is created unless --output-dir names a NEW folder outside this repo.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import stat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from factory.image_processor.png_pipeline import encode_png, decode_png, ImageError
from factory.visual_director.silhouette_kit import PROFILES, _style, _rgb

BASE_SIZE = (180, 320)
SCALES = (1, 2)
COMMON_SCENES = ("world_map", "chapter_map", "gameplay")
CORAL_EXTRA = ("reef_restoration", "marine_collection", "my_aquarium", "new_region")
LAYER_ORDER = ("backdrop", "distant_environment", "near_decoration")
PARALLAX_MILLI = (0, 120, 340)
STAGE = "CANDIDATE_NOT_OWNER_APPROVED"
GENERATOR = "VUF_M06_MATH_LAYERED_SCENES_V01"
NAME = re.compile(r"[a-z][a-z0-9_]{0,75}\.png\Z")


class ScenePackError(ValueError):
    pass


def _scenes(profile: str) -> tuple[str, ...]:
    if profile not in PROFILES:
        raise ScenePackError("unknown five-theme profile")
    return COMMON_SCENES + (CORAL_EXTRA if profile == "Coral_Rescue" else ())


def _validate(profile: str, scene: str, scale: int, seed: int) -> None:
    if scene not in _scenes(profile):
        raise ScenePackError("unknown or cross-theme environment scene")
    if type(scale) is not int or scale not in SCALES:
        raise ScenePackError("only source preview 1x/2x scale supported")
    if type(seed) is not int or not 0 <= seed <= 9999:
        raise ScenePackError("seed must be an integer in 0..9999")


def _linked(path: Path) -> bool:
    if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
        return True
    try:
        info = path.stat(follow_symlinks=False)
        return bool(getattr(info, "st_file_attributes", 0) &
                    getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))
    except OSError:
        return True


def _put(pixels: bytearray, w: int, h: int, x: int, y: int,
         rgb: tuple[int, int, int], alpha: int) -> None:
    if not (0 <= x < w and 0 <= y < h and 0 < alpha <= 255):
        return
    index = (y * w + x) * 4
    previous = pixels[index + 3]
    if previous == 0 or alpha == 255:
        pixels[index:index + 4] = bytes((*rgb, alpha))
        return
    # Straight-alpha 'source over'; integer, deterministic and bounded.
    out = alpha * 255 + previous * (255 - alpha)
    for c in range(3):
        num = rgb[c] * alpha * 255 + pixels[index + c] * previous * (255 - alpha)
        pixels[index + c] = (num + out // 2) // out
    pixels[index + 3] = (out + 127) // 255


def _disk(pixels: bytearray, w: int, h: int, cx: int, cy: int, radius: int,
          color: tuple[int, int, int], alpha: int, hollow: bool = False) -> None:
    radius = max(2, radius)
    thickness = max(2, radius // 5)
    for y in range(max(0, cy - radius), min(h, cy + radius + 1)):
        for x in range(max(0, cx - radius), min(w, cx + radius + 1)):
            d = (x - cx) ** 2 + (y - cy) ** 2
            if d <= radius ** 2 and (not hollow or d >= (radius - thickness) ** 2):
                _put(pixels, w, h, x, y, color, alpha)


def _rect(pixels: bytearray, w: int, h: int, x: int, y: int,
          rw: int, rh: int, color: tuple[int, int, int], alpha: int) -> None:
    for iy in range(max(0, y), min(h, y + rh)):
        for ix in range(max(0, x), min(w, x + rw)):
            _put(pixels, w, h, ix, iy, color, alpha)


def _geometry(pixels: bytearray, w: int, h: int, profile: str, scene: str,
              layer: str, palette: dict, seed: int) -> None:
    accent, surface, cta = (_rgb(palette[k]) for k in ("accent", "surface", "cta"))
    scene_index = _scenes(profile).index(scene)
    phase = scene_index * 11 + seed * 7
    if layer == "backdrop":
        top = _rgb(palette["background"])
        for y in range(h):
            t = (y * 1000) // max(1, h - 1)
            color = tuple((top[c] * (1000 - t) + surface[c] * t) // 1000
                          for c in range(3))
            pixels[y * w * 4:(y + 1) * w * 4] = bytes((*color, 255)) * w
        return
    if layer == "distant_environment":
        # A transparent horizon-like terrain plane, not a flattened UI page.
        mid = h * (53 + scene_index * 3 % 13) // 100
        for x in range(w):
            bend = int(9 * math.sin(x * 0.035 + phase * .1))
            horizon = max(0, min(h, mid + bend))
            for y in range(horizon, h):
                _put(pixels, w, h, x, y, accent, 88)
        for i in range(4):
            cx = (phase * 13 + (i + 1) * w // 5) % w
            cy = h // 3 + ((i * 23 + phase) % max(1, h // 5))
            _disk(pixels, w, h, cx, cy, max(3, w // 30),
                  cta if i % 2 else surface, 110, hollow=True)
        return
    for i in range(9):
        x = (phase * 19 + i * 73 + (i * i * 17)) % w
        y = (h // 4 + phase * 3 + i * 49) % h
        size = max(3, min(w, h) // (16 + i % 5))
        if profile == "Coral_Rescue":
            # Bubble rings + small coral branches, all view-only geometry.
            _disk(pixels, w, h, x, y, size, cta, 200, hollow=True)
            if i % 2 == 0:
                _rect(pixels, w, h, x, y + size, max(2, w // 95),
                      size * 2, accent, 170)
        elif profile == "Garage_Legends":
            _rect(pixels, w, h, x, y, size * 2, max(3, size // 3),
                  cta, 200)
            _disk(pixels, w, h, x + size // 2, y, max(2, size // 3),
                  accent, 235, hollow=True)
        elif profile == "Dino_Islands":
            _disk(pixels, w, h, x, y, size + 2, accent, 175)
            _rect(pixels, w, h, x, y, max(2, size // 3),
                  size * 3, cta, 180)
        elif profile == "The_Fractured_Realms":
            _disk(pixels, w, h, x, y, size + 3, cta, 200, hollow=True)
            _rect(pixels, w, h, x, y, max(2, size // 3),
                  size, accent, 195)
        else:
            _rect(pixels, w, h, x, y, size, size, accent, 235)
            _disk(pixels, w, h, x + size // 2, y + size // 2,
                  max(2, size // 4), cta, 215)


def render_scene_layer(profile: str, scene: str, layer: str,
                       scale: int = 1, seed: int = 0) -> tuple[dict, bytes]:
    """Return original mathematical layer PNG + safe, non-shipping receipt."""
    _validate(profile, scene, scale, seed)
    if layer not in LAYER_ORDER:
        raise ScenePackError("invalid parallax layer")
    palette, style_sha = _style(profile)
    w, h = (BASE_SIZE[0] * scale, BASE_SIZE[1] * scale)
    pixels = bytearray(w * h * 4)
    _geometry(pixels, w, h, profile, scene, layer, palette, seed)
    png = encode_png(w, h, bytes(pixels))
    if not any(pixels[3::4]):
        raise ScenePackError("generated layer cannot be fully transparent")
    filename = (profile.lower() + "_" + scene + "_" + layer + ".png")
    return {
        "profile_id": profile,
        "scene_id": scene,
        "layer_id": layer,
        "file": filename,
        "draw_order": LAYER_ORDER.index(layer),
        "parallax_factor_milli": PARALLAX_MILLI[LAYER_ORDER.index(layer)],
        "png_sha256": hashlib.sha256(png).hexdigest(),
        "style_source_sha256": style_sha,
        "dimensions": [w, h],
        "interactive": False,
        "contains_runtime_text": False,
        "contains_runtime_buttons": False,
        "not_owner_approved": True,
    }, png


def build_representative_pack(scale: int = 1, seed: int = 0) -> tuple[dict, dict[str, bytes]]:
    """19 scene previews (5×3 + 4 Coral); each uses THREE independent PNGs."""
    if type(scale) is not int or scale not in SCALES:
        raise ScenePackError("invalid pack scale")
    if type(seed) is not int or not 0 <= seed <= 9999:
        raise ScenePackError("invalid pack seed")
    images: dict[str, bytes] = {}
    scenes = []
    for profile in PROFILES:
        for scene in _scenes(profile):
            layers = []
            for layer in LAYER_ORDER:
                row, png = render_scene_layer(profile, scene, layer, scale, seed)
                images[row["file"]] = png
                layers.append(row)
            scenes.append({"profile_id": profile, "scene_id": scene, "layers": layers,
                           "owner_visual_approved": False,
                           "runtime_ui_separate": True})
    manifest = {
        "schema_version": 1,
        "stage": STAGE,
        "generator": GENERATOR,
        "profile_ids": list(PROFILES),
        "scene_count": len(scenes),
        "file_count": len(images),
        "scale": scale,
        "seed": seed,
        "scenes": scenes,
        "owner_visual_approval": False,
        "art_rights_verified": False,
        "real_device_verified": False,
        "parallax_runtime_validated": False,
        "real_engine_visual_binding": False,
        "release_allowed": False,
    }
    return manifest, images


def verify_representative_pack(manifest: dict, images: dict[str, bytes]) -> None:
    """Check shape, hash, PNG CRC and candidate-only identity before export."""
    if not isinstance(manifest, dict) or not isinstance(images, dict):
        raise ScenePackError("candidate pack must contain manifest and PNG map")
    scale, seed = manifest.get("scale"), manifest.get("seed")
    if (type(scale) is not int or scale not in SCALES or
            type(seed) is not int or not 0 <= seed <= 9999):
        raise ScenePackError("invalid pack scale/seed")
    if (manifest.get("schema_version") != 1 or
            manifest.get("stage") != STAGE or
            manifest.get("generator") != GENERATOR or
            manifest.get("profile_ids") != list(PROFILES) or
            manifest.get("scene_count") != 19 or
            manifest.get("file_count") != 57 or
            set(manifest) != {"schema_version", "stage", "generator", "profile_ids",
                             "scene_count", "file_count", "scale", "seed", "scenes",
                             "owner_visual_approval", "art_rights_verified",
                             "real_device_verified", "parallax_runtime_validated",
                             "real_engine_visual_binding", "release_allowed"}):
        raise ScenePackError("invalid five-theme scene manifest")
    for flag in ("owner_visual_approval", "art_rights_verified",
                 "real_device_verified", "parallax_runtime_validated",
                 "real_engine_visual_binding", "release_allowed"):
        if manifest[flag] is not False:
            raise ScenePackError("approval or runtime evidence cannot be forged")
    scene_rows = manifest["scenes"]
    if not isinstance(scene_rows, list) or len(scene_rows) != 19:
        raise ScenePackError("missing/duplicate representative scene")
    expected_keys = set()
    ix = 0
    for profile in PROFILES:
        _, expected_style_sha = _style(profile)
        for scene in _scenes(profile):
            row = scene_rows[ix]
            if (not isinstance(row, dict) or
                    set(row) != {"profile_id", "scene_id", "layers",
                                 "owner_visual_approved", "runtime_ui_separate"} or
                    row["profile_id"] != profile or row["scene_id"] != scene or
                    row["owner_visual_approved"] is not False or
                    row["runtime_ui_separate"] is not True or
                    not isinstance(row["layers"], list) or
                    len(row["layers"]) != 3):
                raise ScenePackError("scene order/identity or approval mismatch")
            for n, layer in enumerate(LAYER_ORDER):
                item = row["layers"][n]
                key = profile.lower() + "_" + scene + "_" + layer + ".png"
                if (not isinstance(item, dict) or
                        set(item) != {"profile_id", "scene_id", "layer_id", "file",
                                      "draw_order", "parallax_factor_milli",
                                      "png_sha256", "style_source_sha256",
                                      "dimensions", "interactive", "contains_runtime_text",
                                      "contains_runtime_buttons", "not_owner_approved"} or
                        item["profile_id"] != profile or
                        item["scene_id"] != scene or
                        item["layer_id"] != layer or
                        item["file"] != key or
                        not NAME.fullmatch(key) or
                        item["draw_order"] != n or
                        item["parallax_factor_milli"] != PARALLAX_MILLI[n] or
                        item["style_source_sha256"] != expected_style_sha or
                        item["dimensions"] != [BASE_SIZE[0]*scale, BASE_SIZE[1]*scale] or
                        item["interactive"] is not False or
                        item["contains_runtime_text"] is not False or
                        item["contains_runtime_buttons"] is not False or
                        item["not_owner_approved"] is not True):
                    raise ScenePackError("unsafe scene layer identity, scale or behavior")
                if key in expected_keys:
                    raise ScenePackError("duplicate scene layer")
                expected_keys.add(key)
                png = images.get(key)
                if not isinstance(png, bytes) or len(png) > 4 * 1024 * 1024:
                    raise ScenePackError("missing or oversized generated PNG")
                if hashlib.sha256(png).hexdigest() != item["png_sha256"]:
                    raise ScenePackError("layer source PNG SHA mismatch")
                try:
                    w, h, data = decode_png(png)
                except ImageError as exc:
                    raise ScenePackError("invalid layer PNG") from exc
                if [w, h] != item["dimensions"] or not any(data[3::4]):
                    raise ScenePackError("empty or mismatched candidate layer")
            ix += 1
    if expected_keys != set(images):
        raise ScenePackError("extra or missing candidate image")


def write_representative_pack(folder: Path, manifest: dict,
                              images: dict[str, bytes]) -> None:
    """Create only a NEW external folder; never delete or overwrite owner data."""
    verify_representative_pack(manifest, images)
    folder = Path(folder)
    if (folder.exists() or folder.is_symlink() or
            not folder.parent.is_dir() or
            any(_linked(p) for p in (folder.parent, *folder.parent.parents)) or
            folder.parent.resolve(strict=True).is_relative_to(ROOT)):
        raise ScenePackError("destination must be NEW directory outside checkout")
    folder.mkdir()
    for key, raw in sorted(images.items()):
        with (folder / key).open("xb") as out:
            out.write(raw)
            out.flush()
            os.fsync(out.fileno())
    with (folder / "scene_pack_manifest.json").open(
            "x", encoding="utf-8", newline="\n") as out:
        json.dump(manifest, out, sort_keys=True, indent=2)
        out.write("\n")
        out.flush()
        os.fsync(out.fileno())


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scale", type=int, default=1, choices=SCALES)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args(argv)
    try:
        receipt, pngs = build_representative_pack(args.scale, args.seed)
        verify_representative_pack(receipt, pngs)
        if args.output_dir is not None:
            write_representative_pack(args.output_dir, receipt, pngs)
        print(json.dumps({"scene_count": receipt["scene_count"],
                          "file_count": receipt["file_count"],
                          "stage": STAGE, "output_saved": args.output_dir is not None,
                          "release_allowed": False}, sort_keys=True))
        return 0
    except (ScenePackError, ImageError, OSError, ValueError) as exc:
        print("SCENE_PACK_REJECTED: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
