"""M10-004 bounded REAL TEST_ONLY PNG source memory/texture budget report.

Reuses the independent M08 full hash/indexed candidate bundle verifier.
Output is explicitly NOT a Unity Player build, device GPU or real FPS test.
Use only reviewed EXTERNAL candidate directories; no source writes. Buffer
estimates (RGBA32 mip-free) are upper-bound bookkeeping, not measured VRAM.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from factory.asset_packaging.verify_offline_bundle import verify_exported_pack
from factory.image_processor.png_pipeline import decode_png

MAX_SOURCE_BYTES = 128 * 1024 * 1024
MAX_RGBA_ESTIMATE = 512 * 1024 * 1024


class M10BudgetError(ValueError):
    pass


def analyze_external_candidate(directory: Path) -> dict:
    evidence = verify_exported_pack(directory)
    folder = Path(directory)
    manifest = json.loads((folder / "visual_manifest.json").read_text("utf-8"))
    assets = manifest["assets"]
    total_source = 0
    raw_rgba = 0
    widest = 0
    tallest = 0
    dimensions = {}
    for item in assets:
        path = item["path"]
        payload = (folder / path).read_bytes()
        width, height, _ = decode_png(payload)
        total_source += len(payload)
        raw_rgba += width * height * 4
        widest, tallest = max(widest, width), max(tallest, height)
        dimensions[path] = (width, height)
        if total_source > MAX_SOURCE_BYTES or raw_rgba > MAX_RGBA_ESTIMATE:
            raise M10BudgetError("source review budget exceeded")
    if (not assets or evidence.get("stage") != "TEST_ONLY" or
            evidence.get("release_allowed") is not False):
        raise M10BudgetError("source not a review-only candidate")
    return {
        "schema_version": 1,
        "stage": "SOURCE_ONLY_NOT_PLAYER_BUDGET_PASS",
        "profile_id": manifest["profile_id"],
        "source_png_count": len(assets),
        "all_manifest_sha256_checked": True,
        "decoded_source_png_bytes": total_source,
        "uncompressed_rgba32_estimated_bytes_no_mips": raw_rgba,
        "max_source_width": widest, "max_source_height": tallest,
        "maximum_2d_texture_size_source_only": max(widest, tallest),
        "platform_profiles": {
            platform: {
                "native_actual_texture_import": False,
                "actual_gpu_peak_measured": False,
                "real_frame_budget_tested": False,
                "actual_draw_calls_measured": False,
                "player_build_built_and_scanned": False,
                "art_licence_approved": False,
                "release_allowed": False,
            } for platform in ("Windows_Editor", "iOS", "Android")
        },
        "neutral_engine_replay_pinned": False,
        "actual_level_factory_pack_consumer_verified": False,
        "physical_mobile_smoke_tested": False,
        "release_allowed": False,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    answer = analyze_external_candidate(args.pack_dir)
    print(json.dumps(answer, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
