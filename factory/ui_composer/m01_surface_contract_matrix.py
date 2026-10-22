"""VUF-M01 candidate matrix: 5 draft games x 17 real Engine UI surface kinds x
8 real Engine player-facing states; 28 canonical Coral screen references.

This is a read-only *design* contract, never a UiActionDefinition authorizer.
Game-specific screens, Engine callbacks, rewards, consent and production
binding cannot be synthesized from five color palettes.

Provenance inspected read-only in MATCH3_ENGINE main:
PresentationUiContracts.cs Git blob b7c3c05d0c073e40f8dc1c4799a8bc1d869100f6
PresentationSurfaceContracts.cs Git blob 7598366d6eca3401ac461cb557ebd576fd09be72
Source enums do not prove that ANY real SDK UiSurfaceState is bound.
"""
from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path

from factory.visual_director.m02_style_bible import compile_bibles

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "schemas" / "coral-experiences.v1.json"
CANONICAL_CATALOG_GIT_BLOB = "7e1459c0262500be54b6bbaa658638338baf704a"
SOURCE_BLOBS = {
    "Packages/com.match3.engine/Runtime/PresentationUiContracts.cs":
        "b7c3c05d0c073e40f8dc1c4799a8bc1d869100f6",
    "Packages/com.match3.engine/Runtime/PresentationSurfaceContracts.cs":
        "7598366d6eca3401ac461cb557ebd576fd09be72",
}
ENGINE_SURFACES = (
    "Home", "WorldMap", "Hud", "Results", "Pause", "Settings",
    "Shop", "DailyRewards", "Tasks", "Fail", "Life", "Booster",
    "Collection", "Achievements", "Store", "Account", "Consent",
)
ENGINE_STATES = (
    "Ready", "Loading", "Offline", "Error", "Owned",
    "Claimed", "Disabled", "Pending",
)
ENGINE_ACTION_KINDS = ("Navigate", "Command", "Back", "Close")
SCREEN_SURFACES = {
    "world_map": "WorldMap", "level_start": "WorldMap",
    "level_won": "Results", "level_failed": "Fail",
    "reef_restoration": "Collection", "marine_collection": "Collection",
    "my_aquarium": "Collection", "region_unlocked": "WorldMap",
    "daily_rewards": "DailyRewards", "tasks_missions": "Tasks",
    "shop": "Shop", "treasure_rewards": "Results",
    "events_hub": "WorldMap", "season_pass": "Shop",
    "endless_mode": "WorldMap", "time_attack": "WorldMap",
    "tournament": "WorldMap", "weekly_records": "Achievements",
    "friends": "Account", "leaderboard": "Achievements",
    "player_profile": "Account", "splash_loading": "Home",
    "tutorial": "Hud", "pause_settings": "Pause",
    "out_of_lives": "Life", "welcome_back": "Home",
    "home": "Home", "gameplay_hud": "Hud",
}
STAGE = "M01_UI_SYMBOLIC_SOURCE_CANDIDATE_NOT_ENGINE_BINDING"
MAX_CATALOG_BYTES = 64 * 1024
AUTH_FALSE = (
    "runtime_navigation_enabled", "engine_actions_bound",
    "consent_granted", "purchases_enabled", "rewards_granted",
    "live_player_state_verified", "owner_art_approved",
    "real_engine_sdk_surface_verified", "real_device_verified",
    "release_allowed",
)


class M01MatrixError(ValueError):
    pass


def _blob_sha(source: bytes) -> str:
    return hashlib.sha1(
        b"blob " + str(len(source)).encode("ascii") + b"\0" + source
    ).hexdigest()


def _unique(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise M01MatrixError("duplicate canonical UI field: " + key)
        out[key] = value
    return out


def _catalog(source: bytes) -> dict:
    if not isinstance(source, bytes) or not 0 < len(source) <= MAX_CATALOG_BYTES:
        raise M01MatrixError("missing/oversize canonical Coral source")
    if _blob_sha(source) != CANONICAL_CATALOG_GIT_BLOB:
        raise M01MatrixError("Coral 28-screen source blob has drifted")
    try:
        doc = json.loads(source.decode("utf-8", errors="strict"),
                         object_pairs_hook=_unique)
    except (ValueError, UnicodeError) as exc:
        raise M01MatrixError("malformed/duplicate canonical Coral source") from exc
    if (not isinstance(doc, dict) or
            set(doc) != {"schema_version", "status", "profile_id", "screens"} or
            type(doc["schema_version"]) is not int or doc["schema_version"] != 1 or
            doc["status"] != "CONTRACT_DRAFT_NOT_IMPLEMENTED" or
            doc["profile_id"] != "Coral_Rescue" or
            not isinstance(doc["screens"], list) or len(doc["screens"]) != 28):
        raise M01MatrixError("missing or elevated original Coral draft schema")
    names, ids = [], []
    for index, row in enumerate(doc["screens"], 1):
        if (not isinstance(row, dict) or
                set(row) != {"id", "key", "kind", "runtime_ui_required",
                             "available_in_demo", "feature_gate"} or
                row["id"] != "COR-" + format(index, "02d") or
                not isinstance(row["key"], str) or
                row["key"] not in SCREEN_SURFACES or
                row["kind"] not in {"page", "modal", "ceremony",
                                    "overlay", "mode", "playable"} or
                row["runtime_ui_required"] is not True or
                row["available_in_demo"] is not False or
                row["feature_gate"] not in {
                    "REQUIRES_ENGINE_OR_GAME_BINDING",
                    "OFF_UNTIL_ENGINE_POLICY_CONFIRMED"}):
            raise M01MatrixError("unsafe/renumbered original Coral screen")
        names.append(row["key"])
        ids.append(row["id"])
    if (len(set(names)) != 28 or len(set(ids)) != 28 or
            set(names) != set(SCREEN_SURFACES) or
            names[-2:] != ["home", "gameplay_hud"]):
        raise M01MatrixError("canonical Coral screen identity incomplete")
    return doc


def _build(source: bytes) -> dict:
    doc = _catalog(source)
    profiles = compile_bibles()
    ids = tuple(p["profile_id"] for p in profiles["profiles"])
    if (len(ids) != 5 or len(set(ids)) != 5 or
            len(ENGINE_SURFACES) != 17 or len(set(ENGINE_SURFACES)) != 17 or
            len(ENGINE_STATES) != 8 or len(set(ENGINE_STATES)) != 8 or
            len(ENGINE_ACTION_KINDS) != 4 or
            len(set(ENGINE_ACTION_KINDS)) != 4):
        raise M01MatrixError("missing/duplicate profile or Engine enum")
    master = []
    for row in doc["screens"]:
        screen = row["key"]
        surface = SCREEN_SURFACES[screen]
        is_off = row["feature_gate"] == "OFF_UNTIL_ENGINE_POLICY_CONFIRMED"
        master.append({
            "screen_id": row["id"],
            "screen_key": screen,
            "original_coral_kind": row["kind"],
            "candidate_engine_surface_kind": surface,
            "candidate_overlay_kind":
                "Modal" if row["kind"] in ("modal", "ceremony")
                else ("Modal" if row["kind"] == "overlay" else None),
            "feature_gate": row["feature_gate"],
            "policy_feature_off": is_off,
            "text_key": "ui." + screen + ".title",
            "icon_key": "ui." + screen + ".icon",
            "title_fallback": "SOURCE_ONLY_" + screen.upper(),
            "disabled_reason_fallback": (
                "FEATURE_POLICY_NOT_APPROVED" if is_off
                else "ENGINE_GAME_BINDING_NOT_AUTHORIZED"
            ),
            "action_preview_id": "preview." + screen + ".inspect",
            "preview_action_kind": "Command",
            "actual_engine_action_id": None,
            "actual_engine_command_key": None,
            "actual_engine_destination": None,
            "action_visible_in_design_only": True,
            "action_enabled": False,
            "screen_real_binding_available": False,
            "owner_review_required": True,
        })
    screen_states = []
    for profile in ids:
        for screen in master:
            for state in ENGINE_STATES:
                screen_states.append({
                    "profile_id": profile,
                    "screen_id": screen["screen_id"],
                    "screen_key": screen["screen_key"],
                    "engine_surface_kind": screen["candidate_engine_surface_kind"],
                    "engine_player_state_kind": state,
                    "candidate_overlay_kind": screen["candidate_overlay_kind"],
                    "feature_gate": screen["feature_gate"],
                    "policy_feature_off": screen["policy_feature_off"],
                    "dynamic_text_key": screen["text_key"] + "." + state.lower(),
                    "dynamic_icon_key": screen["icon_key"],
                    "locale_fallback_text": screen["title_fallback"] +
                                            "_" + state.upper(),
                    "visible_disabled_reason_key":
                        "ui.disabled." + screen["screen_key"],
                    "disabled_reason_fallback":
                        screen["disabled_reason_fallback"],
                    "source_preview_action_id": screen["action_preview_id"],
                    "actual_engine_action_id": None,
                    "actual_engine_route": None,
                    "actual_game_binding": None,
                    "action_enabled": False,
                    "screen_view_only": True,
                    "owner_design_approved": False,
                    "release_allowed": False,
                })
    surface_bindings = {}
    for kind in ENGINE_SURFACES:
        refs = [r["screen_id"] for r in master
                if r["candidate_engine_surface_kind"] == kind]
        surface_bindings[kind] = refs
    matrix = []
    for profile in ids:
        for surface in ENGINE_SURFACES:
            for state in ENGINE_STATES:
                matrix.append({
                    "profile_id": profile,
                    "engine_surface_kind": surface,
                    "engine_player_state_kind": state,
                    "candidate_coral_screen_ids": list(surface_bindings[surface]),
                    "source_screens_absent": len(surface_bindings[surface]) == 0,
                    "missing_real_screen_reason": (
                        None if surface_bindings[surface]
                        else "NO_CANONICAL_CORAL_SCREEN_FOR_ENGINE_SURFACE"
                    ),
                    "text_key": "ui.surface." + surface.lower() + "." +
                                state.lower(),
                    "icon_key": "ui.surface." + surface.lower() + ".icon",
                    "localized_fallback": "SOURCE_ONLY_" + state.upper(),
                    "disabled_reason": "SOURCE_ONLY_ENGINE_STATE_NOT_BOUND",
                    "engine_action_kind_namespace": list(ENGINE_ACTION_KINDS),
                    "actual_engine_action_id": None,
                    "action_enabled": False,
                    "route_enabled": False,
                    "real_player_state_bound": False,
                    "runtime_screen_binding_available": False,
                })
    packet = {
        "schema_version": 1,
        "stage": STAGE,
        "source_catalog_blob_sha1": CANONICAL_CATALOG_GIT_BLOB,
        "engine_enum_declaration_blobs": dict(SOURCE_BLOBS),
        "engine_ui_surface_kinds": list(ENGINE_SURFACES),
        "engine_player_state_kinds": list(ENGINE_STATES),
        "engine_action_kinds": list(ENGINE_ACTION_KINDS),
        "profile_ids": list(ids),
        "screens": master,
        "screen_states": screen_states,
        "matrix": matrix,
        "surface_state_count_per_profile": len(ENGINE_SURFACES)*len(ENGINE_STATES),
        "screen_state_count_per_profile": 28*len(ENGINE_STATES),
        "screen_count_source_coral": 28,
        **{flag: False for flag in AUTH_FALSE},
    }
    return packet


def build_m01_matrix(catalog_source: bytes) -> dict:
    """Build a deterministic source-only candidate from exact 28-screen bytes."""
    report = _build(catalog_source)
    canonical = json.dumps(
        report, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    report["matrix_sha256"] = hashlib.sha256(canonical).hexdigest()
    return report


def verify_m01_matrix(candidate: Mapping, catalog_source: bytes) -> None:
    """Fail closed on any forged route, missing row or approval field."""
    if type(candidate) is not dict:
        raise M01MatrixError("source matrix must be unmodified plain JSON object")
    if candidate != build_m01_matrix(catalog_source):
        raise M01MatrixError("matrix route/action/state or approval fields changed")


def main() -> int:
    matrix = build_m01_matrix(CATALOG.read_bytes())
    verify_m01_matrix(matrix, CATALOG.read_bytes())
    print(json.dumps({
        "stage": matrix["stage"],
        "matrix_sha256": matrix["matrix_sha256"],
        "profiles": len(matrix["profile_ids"]),
        "surfaces": len(matrix["engine_ui_surface_kinds"]),
        "states": len(matrix["engine_player_state_kinds"]),
        "matrix_rows": len(matrix["matrix"]),
        "screen_state_rows": len(matrix["screen_states"]),
        "original_screens": len(matrix["screens"]),
        "real_engine_ui_bound": matrix["real_engine_sdk_surface_verified"],
        "release_allowed": matrix["release_allowed"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
