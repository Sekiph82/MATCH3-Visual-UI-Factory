"""VUF-M09-001/004: immutable five-style draft visual-review inventory.

Uses existing 28-screen Coral-only schema and five draft Style Bibles.
Cross-title art-skin demos are explicitly N/A for each other title's
independent unprovided screen contract. 16,800 is a *source-coverage*
count, NOT actual rendered Unity/phone screenshots or a game implementation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCREEN = ROOT / "schemas" / "coral-experiences.v1.json"
STYLE = ROOT / "factory" / "visual_director" / "style_profiles.v1.json"
PROFILES = ("Coral_Rescue", "Garage_Legends", "Dino_Islands",
            "The_Fractured_Realms", "Wonder_Pop")
STATES = ("Ready", "Loading", "Offline", "Error", "Owned",
          "Claimed", "Disabled", "Pending")
LOCALES = ("en", "tr", "stress")
DEVICES = ("Tall phone (approx 19.5:9)", "Android (approx 20:9)",
           "Compact phone (16:9)", "Tablet portrait (4:3)",
           "Landscape phone (20:9)")
STAGE = "CANDIDATE_SOURCE_MATRIX_NOT_RENDERED"
EXPECTED = 5 * 28 * 8 * 3 * 5


class ReviewInventoryError(ValueError):
    pass


def _load():
    raw_screen = SCREEN.read_bytes()
    raw_style = STYLE.read_bytes()
    screen = json.loads(raw_screen)
    style = json.loads(raw_style)
    if (screen.get("schema_version") != 1 or
            screen.get("status") != "CONTRACT_DRAFT_NOT_IMPLEMENTED" or
            screen.get("profile_id") != "Coral_Rescue" or
            style.get("status") != "DRAFT_NOT_OWNER_APPROVED" or
            style.get("schema_version") != 1 or
            len(screen.get("screens", ())) != 28 or
            tuple(p.get("id") for p in style.get("profiles", ())) != PROFILES):
        raise ReviewInventoryError("screen/style draft schema drift")
    seen = set()
    for index, row in enumerate(screen["screens"]):
        if (row.get("id") != f"COR-{index+1:02}" or
                not isinstance(row.get("key"), str) or
                row["key"] in seen or
                row.get("available_in_demo") is not False or
                row.get("feature_gate") not in (
                    "REQUIRES_ENGINE_OR_GAME_BINDING",
                    "OFF_UNTIL_ENGINE_POLICY_CONFIRMED")):
            raise ReviewInventoryError("screen or owner action policy changed")
        seen.add(row["key"])
    return screen["screens"], {
        "coral_schema_sha256": hashlib.sha256(raw_screen).hexdigest(),
        "five_style_bibles_sha256": hashlib.sha256(raw_style).hexdigest()
    }


def index_to_case(index: int) -> dict:
    """Exact same flat order as VufM09MatrixAudit Inspect, no imports."""
    screens, source = _load()
    if type(index) is not int or index < 0 or index >= EXPECTED:
        raise ReviewInventoryError("case index outside 16,800 source matrix")
    remaining = index
    device = remaining % len(DEVICES)
    remaining //= len(DEVICES)
    locale = remaining % len(LOCALES)
    remaining //= len(LOCALES)
    state = remaining % len(STATES)
    remaining //= len(STATES)
    screen = remaining % len(screens)
    profile = remaining // len(screens)
    row = screens[screen]
    policy_off = row["feature_gate"] == "OFF_UNTIL_ENGINE_POLICY_CONFIRMED"
    return {
        "case_index": index,
        "profile_id": PROFILES[profile],
        "coral_draft_screen_id": row["id"],
        "coral_draft_screen_key": row["key"],
        "state_mock": STATES[state],
        "locale_mock": LOCALES[locale],
        "synthetic_device": DEVICES[device],
        "stage": STAGE,
        "feature_gate": row["feature_gate"],
        "feature_available_in_demo": False,
        "independent_screen_taxonomy_available": profile == 0,
        "rendered_gui_verified": False,
        "final_engine_lfx_state_verified": False,
        "original_art_rights_verified": False,
        "owner_visual_approved": False,
        "real_device_gpu_verified": False,
        "release_allowed": False,
        "coverage_status": (
            "N_A_FOREIGN_GAME_USING_CORAL_DRAFT_CONTRACT" if profile else
            "POLICY_OFF_NO_GAME_ACTION" if policy_off else
            "CORAL_DRAFT_NOT_IN_GAME"),
        **source,
    }


def inventory_report() -> dict:
    screens, pins = _load()
    gated = sum(1 for s in screens if s["feature_gate"] ==
                "OFF_UNTIL_ENGINE_POLICY_CONFIRMED")
    return {
        "schema_version": 1,
        "stage": STAGE,
        "source_pins": pins,
        "profiles": list(PROFILES),
        "coral_draft_screen_count": len(screens),
        "screen_contracts_for_other_titles": "NOT_PROVIDED",
        "mock_state_count": len(STATES),
        "mock_locale_count": len(LOCALES),
        "synthetic_device_count": len(DEVICES),
        "coverage_cases_not_rendered": EXPECTED,
        "policy_off_coral_screen_count": gated,
        "cross_title_source_preview_N_A_cases": 4 * 28 * 8 * 3 * 5,
        "original_creator_licence_receipts_checked": False,
        "human_aesthetic_acceptance": False,
        "device_gpu_acceptance": False,
        "gameplay_availability_verified": False,
        "release_allowed": False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", type=int)
    args = parser.parse_args(argv)
    try:
        answer = inventory_report() if args.index is None else index_to_case(args.index)
    except (ReviewInventoryError, OSError, ValueError, TypeError) as e:
        parser.error(str(e))
    print(json.dumps(answer, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
