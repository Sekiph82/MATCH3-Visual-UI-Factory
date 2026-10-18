"""M10 five-theme VUF-only vertical-slice review contract.

GATE: This is NOT MATCH3_ENGINE, not an authoritative Level Factory export,
not a solved replay and NOT the same as a running game. The independent
Engine/LFX repositories still have separate final QA/release gates.
This module can attach immutable EXTERNAL candidate bytes, but it never
claims to interpret a future ENG-M12 neutral replay schema.

Deliberately no game-state mutation, score calculation, goal resolution,
save/purchase APIs, internet connection or original artwork rights.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re

PROFILES = ("Coral_Rescue", "Garage_Legends", "Dino_Islands",
            "The_Fractured_Realms", "Wonder_Pop")
STAGE = "VUF_M10_TEST_ONLY_NONAUTHORITATIVE"
BASE_ROUTE = ("home", "world_map", "level_start", "gameplay_hud",
              "level_won", "marine_collection", "daily_rewards", "shop",
              "offline")
CORAL_EXTRA = ("reef_restoration", "my_aquarium", "region_unlocked")
# Only CORAL screens have independent exact source IDs in original schema.
CORAL_IDS = {
    "home": "COR-27", "world_map": "COR-01", "level_start": "COR-02",
    "gameplay_hud": "COR-28", "level_won": "COR-03",
    "marine_collection": "COR-06", "daily_rewards": "COR-09",
    "shop": "COR-11", "reef_restoration": "COR-05",
    "my_aquarium": "COR-07", "region_unlocked": "COR-08",
    "offline": "COR-22",  # a loading shell with offline mock, NOT own screen
}
EVENTS = ("ui_open", "tile_spawn", "tile_match", "obstacle_hit",
          "booster_activate", "special_trigger", "combo_chain",
          "level_win", "reward_claim", "region_reveal")
HEX = re.compile(r"[0-9a-f]{64}\Z")
REVIEW_LEVEL = {
    "schema_version": 1,
    "stage": "SYNTHETIC_LAYOUT_ONLY",
    "width": 8, "height": 8,
    "row_count": 8, "goal_kind": "NOT_CONNECTED",
    "obstacle_count": 2,
    "boosters": ["NOT_CONNECTED"],
    "actual_level_factory_export": False,
    "authoritative_seed": False,
}


class NeutralSliceError(ValueError):
    pass


def _canonical(value) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False) + "\n").encode()


def _digest(source: bytes) -> str:
    return hashlib.sha256(source).hexdigest()


def build_slice(profile: str, *, mock_level: int = 11,
                mock_seed: int = 42, theme_revision: str = "candidate_v1") -> dict:
    """Construct VUF-only layout and presentation/event intent for one title."""
    if profile not in PROFILES or type(mock_level) is not int or not 1 <= mock_level <= 1000 or             type(mock_seed) is not int or not 0 <= mock_seed <= 65535 or             not isinstance(theme_revision, str) or not re.fullmatch(
                r"[a-zA-Z0-9_-]{1,40}", theme_revision):
        raise NeutralSliceError("unsafe title/level/seed/revision")
    routes = list(BASE_ROUTE)
    if profile == "Coral_Rescue":
        routes.extend(CORAL_EXTRA)
    steps = [{
        "step": i,
        "route_key": key,
        "coral_schema_screen_id": CORAL_IDS[key],
        "runtime_screen_defined_for_this_profile": profile == "Coral_Rescue",
        "screen_binding": "CANDIDATE_UNBOUND",
        "event": EVENTS[min(i, len(EVENTS)-1)],
        "level_resolved_from_lfx": False,
        "game_state_updated": False,
        "rendered_on_device": False,
        "owner_approved": False,
    } for i, key in enumerate(routes)]
    # Frozen neutral *reference inputs*: a hash, not a fabricated WIN/score.
    gameplay_authority = {
        "source": "VUF_SYNTHETIC_NOT_ENGINE_OR_LFX",
        "profile_id": profile,
        "mock_level": mock_level,
        "mock_seed": mock_seed,
        "goal_kind": REVIEW_LEVEL["goal_kind"],
        "has_real_moves": False,
        "has_real_win": False,
        "score": None,
        "save_revision": None,
        "difficulty": None,
        "replay_sha256": None,
    }
    fixed_sha = _digest(_canonical(gameplay_authority))
    result = {
        "schema_version": 1,
        "stage": STAGE,
        "profile_id": profile,
        "theme_revision": theme_revision,
        "mock_level": mock_level, "mock_seed": mock_seed,
        "visual_review_routes": steps,
        "coral_extra_screen_sample_only": profile == "Coral_Rescue",
        "source_level": copy.deepcopy(REVIEW_LEVEL),
        "frozen_reference": gameplay_authority,
        "frozen_reference_sha256": fixed_sha,
        "real_engine_replay_verified": False,
        "real_lfx_level_imported": False,
        "obstacle_damage_measured": False,
        "booster_changes_gameplay": False,
        "level_won_or_reward_claimed": False,
        "real_navigation_works": False,
        "player_build_verified": False,
        "owner_art_rights_verified": False,
        "physical_gpu_performance_verified": False,
        "release_allowed": False,
    }
    verify_slice(result)
    return result


def verify_slice(value: dict) -> None:
    if (not isinstance(value, dict) or value.get("schema_version") != 1 or
            value.get("stage") != STAGE or
            value.get("profile_id") not in PROFILES or
            value.get("coral_extra_screen_sample_only") is not
                (value.get("profile_id") == "Coral_Rescue")):
        raise NeutralSliceError("invalid slice identity")
    for field in ("real_engine_replay_verified", "real_lfx_level_imported",
                  "obstacle_damage_measured", "booster_changes_gameplay",
                  "level_won_or_reward_claimed", "real_navigation_works",
                  "player_build_verified", "owner_art_rights_verified",
                  "physical_gpu_performance_verified", "release_allowed"):
        if value.get(field) is not False:
            raise NeutralSliceError("forged real gameplay/device/owner acceptance")
    if (not isinstance(value.get("theme_revision"), str) or
            not re.fullmatch(r"[a-zA-Z0-9_-]{1,40}", value["theme_revision"])):
        raise NeutralSliceError("invalid theme revision")
    profile = value["profile_id"]
    expected = list(BASE_ROUTE) + (list(CORAL_EXTRA) if profile == "Coral_Rescue" else [])
    steps = value.get("visual_review_routes")
    if not isinstance(steps, list) or len(steps) != len(expected):
        raise NeutralSliceError("missing vertical slice route")
    for i, (row, expected_key) in enumerate(zip(steps, expected)):
        if (not isinstance(row, dict) or
                row.get("step") != i or row.get("route_key") != expected_key or
                row.get("coral_schema_screen_id") != CORAL_IDS[expected_key] or
                row.get("event") != EVENTS[min(i, len(EVENTS)-1)] or
                row.get("runtime_screen_defined_for_this_profile") is not
                (profile == "Coral_Rescue") or
                row.get("screen_binding") != "CANDIDATE_UNBOUND"):
            raise NeutralSliceError("invented or mismatched route")
        for flag in ("level_resolved_from_lfx", "game_state_updated",
                     "rendered_on_device", "owner_approved"):
            if row.get(flag) is not False:
                raise NeutralSliceError("forged independent route game authority")
    if (value.get("source_level") != REVIEW_LEVEL or
            value.get("frozen_reference") is None or
            _digest(_canonical(value["frozen_reference"])) !=
                value.get("frozen_reference_sha256")):
        raise NeutralSliceError("source/reference corrupted")
    authority = value["frozen_reference"]
    if (authority != {
            "source": "VUF_SYNTHETIC_NOT_ENGINE_OR_LFX",
            "profile_id": profile,
            "mock_level": value.get("mock_level"),
            "mock_seed": value.get("mock_seed"),
            "goal_kind": REVIEW_LEVEL["goal_kind"],
            "has_real_moves": False, "has_real_win": False,
            "score": None, "save_revision": None,
            "difficulty": None, "replay_sha256": None} or
            type(value.get("mock_level")) is not int or
            type(value.get("mock_seed")) is not int):
        raise NeutralSliceError("unauthorized score, replay or seed edits")


def assert_theme_isolation(a: dict, b: dict) -> dict:
    """Compare source-only theme switch against untrusted gameplay fields."""
    verify_slice(a)
    verify_slice(b)
    if (a["profile_id"] != b["profile_id"] or
            a["frozen_reference_sha256"] != b["frozen_reference_sha256"] or
            a["visual_review_routes"] != b["visual_review_routes"]):
        raise NeutralSliceError("theme change touched reference fields")
    return {
        "stage": STAGE,
        "profile_id": a["profile_id"],
        "theme_a": a["theme_revision"], "theme_b": b["theme_revision"],
        "unchanged_synthetic_reference_sha256": a["frozen_reference_sha256"],
        "checked_real_engine_game_state": False,
        "checked_real_lfx_difficulty": False,
        "owner_art_approved": False,
        "production_replay_parity": False,
        "release_allowed": False,
    }


def inspect_attached_external_bytes(payload: bytes, expected_sha: str) -> dict:
    """Opaque SHA-bound LevelFactory candidate bytes; NO fabricated schema parse.

    An actual producer adapter must be authored against a verified Engine/LFX
    release contract in M10-001. Until then an attachment is a blob, not a
    resolved board, goal or replay.
    """
    if (not isinstance(payload, bytes) or not 0 < len(payload) <= 4*1024*1024 or
            not isinstance(expected_sha, str) or not HEX.fullmatch(expected_sha) or
            _digest(payload) != expected_sha):
        raise NeutralSliceError("external source digest mismatch or unsafe bytes")
    return {
        "source_sha256": expected_sha,
        "source_bytes": len(payload),
        "stage": "UNINTERPRETED_EXTERNAL_BYTES",
        "schema_verified_as_lfx": False,
        "engine_sha_pinned": False,
        "neutral_replay_verified": False,
        "release_allowed": False,
    }
