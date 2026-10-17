"""VUF R51 / M05-003: view-only, Engine-pinned obstacle/goal/booster states.

The exact Engine declarations are inspected READ-ONLY from
Packages/com.match3.engine/Runtime/ObstacleLifecycleContracts.cs
blob 0a882ec44e6ecfcb840971efad187515f44ef9b3.
Definition/goal/booster IDs are PROVIDED by trusted upstream fixtures; VUF
never invents their authority and never changes durability or rewards.
"""
from __future__ import annotations

import re
from collections.abc import Mapping

from factory.visual_director.special_skin_map import PROFILES

SOURCE_BLOB = "0a882ec44e6ecfcb840971efad187515f44ef9b3"
SOURCE_PATH = "Packages/com.match3.engine/Runtime/ObstacleLifecycleContracts.cs"
LAYER_KINDS = ("Underlay", "Overlay", "Piece", "Cell")
DAMAGE_KINDS = ("Normal", "Line", "Area", "Color", "Targeted")
ASSET_ROLES = ("obstacle", "collectible", "goal", "equipment", "booster")
SLUG = re.compile(r"[a-z][a-z0-9_.-]{0,79}\Z")
MAX_DEFINITIONS = 64
MAX_DURABILITY = 16


class ObstacleSkinError(ValueError):
    pass


def _slug(raw):
    if not isinstance(raw, str) or not SLUG.fullmatch(raw):
        raise ObstacleSkinError("source key must be a portable lowercase semantic ID")
    return raw


def build_state_map(profile: str, definitions: list[Mapping]) -> dict:
    """Create deterministic, nonfunctional skin lookups for supplied semantic IDs.

    Missing actual upstream definitions are not replaced by generated guesses.
    Sprite keys are candidate names; callers must bind approved art separately.
    """
    if profile not in PROFILES:
        raise ObstacleSkinError("unknown five-game profile")
    if not isinstance(definitions, list) or not 1 <= len(definitions) <= MAX_DEFINITIONS:
        raise ObstacleSkinError("1..64 actual definition metadata rows required")
    rows = []
    seen = set()
    for item in definitions:
        if not isinstance(item, Mapping):
            raise ObstacleSkinError("definition must be mapping")
        semantic_id = _slug(item.get("id"))
        role = item.get("role")
        if role not in ASSET_ROLES:
            raise ObstacleSkinError("unknown artwork role")
        key = (role, semantic_id)
        if key in seen:
            raise ObstacleSkinError("duplicate asset role and ID")
        seen.add(key)
        durability = item.get("max_durability")
        if type(durability) is not int or not 1 <= durability <= MAX_DURABILITY:
            raise ObstacleSkinError("invalid durability stage limit")
        if role != "obstacle" and durability != 1:
            raise ObstacleSkinError("non-obstacle semantic assets have no inferred HP logic")
        layer = item.get("layer")
        if layer not in LAYER_KINDS:
            raise ObstacleSkinError("unknown actual Engine layer enum")
        allowed_damage = item.get("damage_kinds", [])
        if (not isinstance(allowed_damage, list) or
                any(not isinstance(x, str) or x not in DAMAGE_KINDS
                    for x in allowed_damage) or
                len(allowed_damage) != len(set(allowed_damage))):
            raise ObstacleSkinError("invalid or duplicate actual Engine damage enum")
        stem = profile.lower() + "." + role + "." + semantic_id
        phases = [{"durability": n, "sprite_key": stem + ".hp" + str(n)}
                  for n in range(durability, -1, -1)]
        hits = [
            {"engine_damage_kind": damage,
             "event_skin_key": stem + ".hit." + damage.lower()}
            for damage in DAMAGE_KINDS if damage in allowed_damage
        ]
        rows.append({
            "id": semantic_id,
            "role": role,
            "engine_layer_kind": layer,
            "max_durability": durability,
            "states": phases,
            "damage_visuals": hits,
            "gameplay_durability_mutations": False,
            "save_or_reward_authority": False,
        })
    rows.sort(key=lambda x: (x["role"], x["id"]))
    return {
        "schema_version": 1,
        "stage": "CANDIDATE_SYMBOLIC_NOT_OWNER_APPROVED",
        "profile_id": profile,
        "engine_obstacle_source_blob_sha": SOURCE_BLOB,
        "engine_obstacle_source_path": SOURCE_PATH,
        "actual_upstream_definition_ids_verified": False,
        "gameplay_durability_mutations": False,
        "save_or_reward_authority": False,
        "release_allowed": False,
        "assets": rows,
    }


def verify_state_map(doc: dict, definitions: list[Mapping]) -> None:
    if not isinstance(doc, dict) or doc.get("profile_id") not in PROFILES:
        raise ObstacleSkinError("invalid candidate state map")
    if doc != build_state_map(doc["profile_id"], definitions):
        raise ObstacleSkinError("state map missing, modified or forged")


def source_example_definitions() -> list[dict]:
    """Explicitly FAKE demo keys. Never assert these belong to the Engine registry."""
    return [
        {"id": "sample_ice", "role": "obstacle", "layer": "Overlay",
         "max_durability": 3, "damage_kinds": ["Normal", "Line", "Area"]},
        {"id": "sample_rescue", "role": "collectible", "layer": "Piece",
         "max_durability": 1, "damage_kinds": []},
        {"id": "sample_goal", "role": "goal", "layer": "Cell",
         "max_durability": 1, "damage_kinds": []},
        {"id": "sample_tool", "role": "equipment", "layer": "Underlay",
         "max_durability": 1, "damage_kinds": []},
        {"id": "sample_booster", "role": "booster", "layer": "Piece",
         "max_durability": 1, "damage_kinds": []},
    ]
