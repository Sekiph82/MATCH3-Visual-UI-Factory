"""VUF-M08-003 | Five-theme TEST_ONLY offline asset pack assembler.

INTERNAL REUSE: M06 real scene RGBA layers, M05 R52 sample Sprite candidates,
VF04 shelf PNG atlas packer, VF06 procedural FX and VUF's strict TEST_ONLY
VisualAssetManifest C# schema. Does NOT download Addressables, fetch vendor
art, create runtime game actions, claim production licences or write to any
repo directory. Exports ONLY to a NEW user-chosen external folder.

Unity: import *copies* of the generated directory into Assets/ and select
visual_manifest.json in "External Visual Pack Sandbox". Avoid copying its
test-only content into a shipping game/player. Atlas source importer settings,
actual SpriteAtlas V2 object, locales and device/GPU art QA remain separate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
from pathlib import Path

from factory.image_processor.atlas_pipeline import create_atlas_candidate
from factory.image_processor.png_pipeline import decode_png
from factory.image_processor.representative_scene_pack import (
    ROOT, _scenes, build_representative_pack,
)
from factory.visual_director.sample_sprite_pack import build_sample_pack
from factory.visual_director.silhouette_kit import PROFILES
from factory.vfx_builder.procedural_fx_sheet import (
    COLORS, build_candidate,
)

STAGE = "TEST_ONLY"
PACK_GENERATOR = "VUF_M08_OFFLINE_CANDIDATE_PACK_V01"
MAX_RAW_BYTES = 8 * 1024 * 1024
SAFE = re.compile(r"[a-zA-Z0-9_-]+(?:/[a-zA-Z0-9_-]+)*\.(?:png|json)\Z")


class CandidatePackError(ValueError):
    pass


def _json(value: dict) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) +
            "\n").encode("utf-8")


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _link(folder: Path) -> bool:
    if folder.is_symlink() or (hasattr(folder, "is_junction") and folder.is_junction()):
        return True
    try:
        attr = getattr(folder.stat(follow_symlinks=False),
                       "st_file_attributes", 0)
        return bool(attr & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))
    except OSError:
        return True


def _locale(profile: str, locale: str) -> dict:
    # No claim to finished translations; synthetic review strings only.
    if locale not in ("en", "tr"):
        raise CandidatePackError("invalid draft locale")
    pairs = {
        "en": {
            "title": "Candidate visual review",
            "action": "NOT CONNECTED",
            "offline": "Offline (simulation)",
            "loading": "Loading (simulation)",
            "disabled": "Preview action disabled",
        },
        "tr": {
            "title": "Aday gorsel inceleme",
            "action": "BAGLI DEGIL",
            "offline": "Cevrimdisi (simulasyon)",
            "loading": "Yukleniyor (simulasyon)",
            "disabled": "Onizleme islemi devre disi",
        },
    }
    return {
        "schema_version": 1,
        "profile_id": profile,
        "locale": locale,
        "stage": "DRAFT_NOT_LOCALIZATION_APPROVED",
        "actual_gameplay_labels_verified": False,
        "texts": pairs[locale],
        "release_allowed": False,
    }


def build_pack(profile: str) -> tuple[dict, dict[str, bytes], dict]:
    """Return immutable nonshipping bundle without touching disk."""
    if profile not in PROFILES:
        raise CandidatePackError("unknown game profile")
    scene_manifest, scenes = build_representative_pack(scale=1)
    sprite_manifest, sprites = build_sample_pack(profile)
    assets = []
    files: dict[str, bytes] = {}

    def add(asset_id: str, path: str, raw: bytes) -> None:
        if (not SAFE.fullmatch(path) or path in files or
                not isinstance(raw, bytes) or not 0 < len(raw) <= MAX_RAW_BYTES):
            raise CandidatePackError("invalid, duplicate or oversized source")
        w, h, decoded = decode_png(raw)
        if w < 1 or h < 1 or not any(decoded[3::4]):
            raise CandidatePackError("candidate PNG has no visible image")
        files[path] = raw
        assets.append({
            "asset_id": profile + "." + asset_id,
            "path": path,
            "sha256": _sha(raw),
            "state": "CANDIDATE",
            "rights": "REVIEW_PENDING",
            "source_receipt": "MATHEMATICAL_PLACEHOLDER_NOT_FINAL",
        })

    count_scenes = 0
    selected_style_sha = None
    for row in scene_manifest["scenes"]:
        if row["profile_id"] != profile:
            continue
        count_scenes += 1
        selected_style_sha = row["layers"][0]["style_source_sha256"]
        for layer in row["layers"]:
            filename = "scenes/" + row["scene_id"] + "_" + layer["layer_id"] + ".png"
            add("scene." + row["scene_id"] + "." + layer["layer_id"],
                filename, scenes[layer["file"]])

    for row in sprite_manifest["assets"]:
        add("sample." + row["file"][:-4],
            "sprites/" + row["file"], sprites[row["file"]])

    for preset in sorted(COLORS):
        fx, sheet, still = build_candidate(
            preset, frames=8, frame_side=32, columns=4, seed=0)
        folder = "fx/" + preset.lower()
        add("fx." + preset.lower() + ".sheet",
            folder + "/fx_sheet.png", sheet)
        add("fx." + preset.lower() + ".still",
            folder + "/reduced_motion.png", still)
        files[folder + "/fx_manifest.json"] = _json(fx)

    files["locales/en.json"] = _json(_locale(profile, "en"))
    files["locales/tr.json"] = _json(_locale(profile, "tr"))
    files["receipts/scene_sources.json"] = _json({
        "source_generator_id": scene_manifest["generator"],
        "style_bible_sha256": selected_style_sha,
        "source_stage": scene_manifest["stage"],
        "profile_id": profile,
        "scene_count": count_scenes,
        "owner_approved": False,
    })
    files["receipts/sprite_sources.json"] = _json(sprite_manifest)
    manifest = {
        "schema_version": 1,
        "profile_id": profile,
        "theme_version": "vuf_m08_candidate_v1",
        "engine_sha": "UNPINNED_TEST_ONLY",
        "level_factory_sha": "UNPINNED_TEST_ONLY",
        "stage": STAGE,
        "assets": sorted(assets, key=lambda row: row["asset_id"]),
    }
    if len({x["asset_id"] for x in assets}) != len(assets):
        raise CandidatePackError("duplicate asset identifiers")
    if count_scenes != (7 if profile == "Coral_Rescue" else 3):
        raise CandidatePackError("missing five-theme environment screens")
    summary = {
        "generator": PACK_GENERATOR,
        "stage": STAGE,
        "profile_id": profile,
        "scenes": count_scenes,
        "sprite_prototypes": len(sprites),
        "fx_presets": len(COLORS),
        "image_count": len(assets),
        "owner_visual_approved": False,
        "rights_approved": False,
        "real_engine_lfx_sha_pinned": False,
        "device_gpu_approved": False,
        "actual_game_actions": False,
        "release_allowed": False,
    }
    verify_pack(manifest, files, summary)
    return manifest, files, summary


def verify_pack(manifest: dict, files: dict[str, bytes], summary: dict) -> None:
    """Verify ALL source PNG, draft locales and every false-approval gate."""
    if (not isinstance(manifest, dict) or not isinstance(files, dict) or
            not isinstance(summary, dict)):
        raise CandidatePackError("invalid candidate bundle types")
    if (manifest.get("stage") != STAGE or
            manifest.get("profile_id") not in PROFILES or
            manifest.get("schema_version") != 1 or
            manifest.get("engine_sha") != "UNPINNED_TEST_ONLY" or
            manifest.get("level_factory_sha") != "UNPINNED_TEST_ONLY" or
            summary.get("generator") != PACK_GENERATOR or
            summary.get("profile_id") != manifest["profile_id"] or
            summary.get("stage") != STAGE or
            type(summary.get("release_allowed")) is not bool or
            summary["release_allowed"] is not False):
        raise CandidatePackError("stage, profile or final SHA spoof")
    for key in ("owner_visual_approved", "rights_approved",
                "real_engine_lfx_sha_pinned", "device_gpu_approved",
                "actual_game_actions"):
        if summary.get(key) is not False:
            raise CandidatePackError("unauthorized approval/game action")
    assets = manifest.get("assets")
    if (not isinstance(assets, list) or
            summary.get("image_count") != len(assets) or
            len(assets) > 128 or len(assets) < 40):
        raise CandidatePackError("missing/oversized candidate image catalog")
    seen_ids, seen_paths = set(), set()
    for row in assets:
        if not isinstance(row, dict):
            raise CandidatePackError("invalid sprite receipt")
        key, filename = row.get("asset_id"), row.get("path")
        if (not isinstance(key, str) or
                not key.startswith(manifest["profile_id"] + ".") or
                key in seen_ids or
                not isinstance(filename, str) or
                filename in seen_paths or not SAFE.fullmatch(filename) or
                not filename.endswith(".png") or
                row.get("state") != "CANDIDATE" or
                row.get("rights") != "REVIEW_PENDING" or
                row.get("source_receipt") != "MATHEMATICAL_PLACEHOLDER_NOT_FINAL"):
            raise CandidatePackError("duplicate/unsafe/approved image contract")
        seen_ids.add(key)
        seen_paths.add(filename)
        raw = files.get(filename)
        if not isinstance(raw, bytes) or not 0 < len(raw) <= MAX_RAW_BYTES:
            raise CandidatePackError("source image missing/oversized")
        if _sha(raw) != row.get("sha256"):
            raise CandidatePackError("corrupt PNG SHA")
        try:
            decode_png(raw)
        except ValueError as ex:
            raise CandidatePackError("invalid source PNG") from ex
    for locale in ("en", "tr"):
        item = "locales/" + locale + ".json"
        try:
            sheet = json.loads(files[item].decode("utf-8"))
        except (KeyError, TypeError, ValueError, UnicodeError) as ex:
            raise CandidatePackError("draft locale missing/invalid") from ex
        if (sheet.get("locale") != locale or
                sheet.get("profile_id") != manifest["profile_id"] or
                sheet.get("stage") != "DRAFT_NOT_LOCALIZATION_APPROVED" or
                sheet.get("release_allowed") is not False):
            raise CandidatePackError("false locale shipping approval")
    for filename, raw in files.items():
        if not isinstance(filename, str) or not SAFE.fullmatch(filename) or not isinstance(raw, bytes):
            raise CandidatePackError("unauthorized sidecar file")
    for row in assets:
        if not row["path"].startswith("fx/"): continue
        preset = row["path"].split("/")[1]
        data = json.loads(files["fx/" + preset + "/fx_manifest.json"])
        if data.get("owner_visual_approval") is not False:
            raise CandidatePackError("false FX art approval")


def export_pack(profile: str, destination: Path) -> dict:
    """Create-only; use the real VF04 atlas packer, no temp and no cleanup."""
    path = Path(destination)
    if (path.exists() or path.is_symlink() or
            not path.parent.is_dir() or
            any(_link(p) for p in (path.parent, *path.parent.parents)) or
            path.parent.resolve(strict=True).is_relative_to(ROOT)):
        raise CandidatePackError("must use NEW external directory, never overwrite")
    manifest, files, summary = build_pack(profile)
    path.mkdir()
    for name, payload in sorted(files.items()):
        target = path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    # Every R52 sample source is exactly the original bytes loaded into VF04.
    source_files = {
        k[:-4]: path / "sprites" / k
        for k in sorted(p.name for p in (path / "sprites").glob("*.png"))
    }
    atlas = create_atlas_candidate(
        source_files, path / "sprite_atlas", padding=2, extrude=1)
    atlas_name = "sprite_atlas/atlas.png"
    manifest["assets"].append({
        "asset_id": profile + ".sample.candidate_atlas",
        "path": atlas_name,
        "sha256": atlas["atlas_sha256"],
        "state": "CANDIDATE",
        "rights": "REVIEW_PENDING",
        "source_receipt": "MATHEMATICAL_PLACEHOLDER_NOT_FINAL",
    })
    manifest["assets"].sort(key=lambda row: row["asset_id"])
    summary["image_count"] = len(manifest["assets"])
    files[atlas_name] = (path / atlas_name).read_bytes()
    files["sprite_atlas/atlas_manifest.json"] = (
        path / "sprite_atlas/atlas_manifest.json").read_bytes()
    verify_pack(manifest, files, summary)
    all_manifest = _json(manifest)
    with (path / "visual_manifest.json").open("xb") as handle:
        handle.write(all_manifest)
        handle.flush()
        os.fsync(handle.fileno())
    digest_files = {
        filename: _sha(payload) for filename, payload in sorted({
            **files, "visual_manifest.json": all_manifest
        }.items())
    }
    summary["file_sha256"] = digest_files
    # Unity's built-in JsonUtility cannot deserialize dynamic JSON
    # dictionaries: expose the SAME immutable digest map as a typed array.
    summary["file_entries"] = [
        {"path": name, "sha256": digest}
        for name, digest in sorted(digest_files.items())
    ]
    with (path / "candidate_pack_receipt.json").open("xb") as handle:
        handle.write(_json(summary))
        handle.flush()
        os.fsync(handle.fileno())
    return summary


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--profile", required=True, choices=PROFILES)
    p.add_argument("--new-external-dir", type=Path, required=True)
    args = p.parse_args(argv)
    try:
        print(json.dumps(export_pack(args.profile, args.new_external_dir),
                         indent=2, sort_keys=True))
        return 0
    except (CandidatePackError, OSError, ValueError) as ex:
        p.exit(2, "CANDIDATE_PACK_REJECTED: " + str(ex) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
