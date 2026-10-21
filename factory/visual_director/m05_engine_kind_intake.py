"""M05 read-only exact Engine enum provenance for visual binding drafts.

Enumerated *kinds* are real declarations, but actual obstacle/goal/booster
instance/definition IDs are NOT published in these four interface files.
Do not promote symbolic visual candidates to production IDs or art rights.

The caller supplies original C# bytes read without writing to the sibling
MATCH3_ENGINE repository. Git blob SHA verifies provenance, not an ABI release.
"""
from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping

from factory.visual_director.special_skin_map import PROFILES

STAGE = "M05_ENGINE_KINDS_SOURCE_ONLY_NOT_FINAL_IDS"
ENGINE_REPOSITORY = "Sekiph82/MATCH3_ENGINE"
PATH_ROOT = "Packages/com.match3.engine/Runtime/"
# Exact upstream public Git blobs, inspected read-only 2026-10-21.
SOURCE_PINS = {
    PATH_ROOT + "ObstacleLifecycleContracts.cs":
        "0a882ec44e6ecfcb840971efad187515f44ef9b3",
    PATH_ROOT + "GoalScoreContracts.cs":
        "dbc36103437786a5020b43e1e00d18e27374126b",
    PATH_ROOT + "BoosterEconomyContracts.cs":
        "9d184e0a964c354e9038c1946bd36377d4c1fe23",
    PATH_ROOT + "SpecialEffectContracts.cs":
        "5ad6e1dcd50d707614ecf258207c2f09e3538a3e",
}
# Full ordinals, not fabricated gameplay statuses or collectible registry keys.
REQUIRED_ENUMS = {
    "ObstacleLifecycleContracts.cs": {
        "ObstacleLayerKind": ("Underlay", "Overlay", "Piece", "Cell"),
        "ObstacleDamageKind": ("Normal", "Line", "Area", "Color", "Targeted"),
    },
    "GoalScoreContracts.cs": {
        "GoalKind": ("CollectPiece", "ClearObstacle", "RescueDrop", "Composite"),
    },
    "BoosterEconomyContracts.cs": {
        "BoosterKind": ("Hammer", "HorizontalLine", "VerticalLine", "Area",
                        "Color", "Shuffle", "Swap", "TargetedMissile"),
    },
    "SpecialEffectContracts.cs": {
        "SpecialActivationKind": ("HorizontalLine", "VerticalLine", "Area",
                                  "Color", "Targeted"),
    },
}
ENUM_MEMBER = re.compile(r"\A([A-Za-z][A-Za-z0-9_]*)\s*=\s*(\d+)\Z")
ENUM_DECL = re.compile(
    r"\bpublic\s+enum\s+([A-Za-z][A-Za-z0-9_]*)\s*\{([^{}]*)\}",
    re.MULTILINE,
)
MAX_BYTES_PER_SOURCE = 128 * 1024


class EngineKindError(ValueError):
    pass


def git_blob_sha(source: bytes) -> str:
    if not isinstance(source, bytes) or not 1 <= len(source) <= MAX_BYTES_PER_SOURCE:
        raise EngineKindError("Engine C# source missing or outside read-only size budget")
    return hashlib.sha1(
        b"blob " + str(len(source)).encode("ascii") + b"\0" + source
    ).hexdigest()


def parse_declared_enum(source: bytes, name: str) -> tuple[str, ...]:
    if not isinstance(source, bytes) or len(source) > MAX_BYTES_PER_SOURCE:
        raise EngineKindError("invalid bounded Engine C# source")
    try:
        code = source.decode("utf-8", "strict")
    except UnicodeError as exc:
        raise EngineKindError("non-UTF8 Engine source") from exc
    matches = [(n, body) for n, body in ENUM_DECL.findall(code) if n == name]
    if len(matches) != 1:
        raise EngineKindError("required official Engine enum missing or duplicated: " + name)
    members = []
    ordinals = set()
    for field in matches[0][1].split(","):
        value = field.strip()
        if not value:
            continue
        match = ENUM_MEMBER.fullmatch(value)
        if match is None:
            raise EngineKindError("unsupported Engine enum syntax, review upstream manually")
        identifier, index = match.group(1), int(match.group(2))
        if identifier in members or index in ordinals:
            raise EngineKindError("duplicate Engine member or ordinal")
        members.append(identifier)
        ordinals.add(index)
        if index != len(members) - 1:
            raise EngineKindError("noncanonical ordinal changed: " + name)
    if not members:
        raise EngineKindError("empty official Engine enum")
    return tuple(members)


def _inspect(files: Mapping[str, bytes],
             pins: Mapping[str, str]) -> dict:
    if not isinstance(files, Mapping) or set(files) != set(SOURCE_PINS) or (
            not isinstance(pins, Mapping) or set(pins) != set(SOURCE_PINS)):
        raise EngineKindError("incomplete or unexpected Engine declaration files")
    kinds = {}
    for filename in sorted(SOURCE_PINS):
        content = files[filename]
        observed = git_blob_sha(content)
        expected = pins[filename]
        if (not isinstance(expected, str) or
                re.fullmatch(r"[0-9a-f]{40}", expected) is None or
                observed != expected):
            raise EngineKindError("Engine declaration SHA drift: " + filename)
        for enum, expected_names in REQUIRED_ENUMS[filename.rsplit("/", 1)[-1]].items():
            observed_names = parse_declared_enum(content, enum)
            if observed_names != expected_names:
                raise EngineKindError("Engine enum definition diverged: " + enum)
            kinds[enum] = [{"name": name, "ordinal": i}
                           for i, name in enumerate(observed_names)]
    return {
        "schema_version": 1,
        "stage": STAGE,
        "engine_repository": ENGINE_REPOSITORY,
        "source_blob_sha1": {name: pins[name] for name in sorted(SOURCE_PINS)},
        "observed_verified_against_pinned_engine_sources":
            dict(pins) == SOURCE_PINS,
        "engine_declared_kinds": kinds,
        "actual_obstacle_definition_ids_verified": False,
        "actual_goal_definition_ids_verified": False,
        "actual_booster_instance_ids_verified": False,
        "owner_art_mapping_verified": False,
        "engine_lfx_final_abi_verified": False,
        "release_allowed": False,
    }


def inspect_pinned_engine_kinds(files: Mapping[str, bytes]) -> dict:
    """Verify true, exactly pinned Engine source bytes; never infer actual IDs."""
    return _inspect(files, SOURCE_PINS)


def draft_five_title_role_bindings(verified_declarations: dict) -> dict:
    """Source schema hints, NOT resolved actual asset IDs or player-state data."""
    if (not isinstance(verified_declarations, dict) or
            verified_declarations.get("stage") != STAGE or
            verified_declarations.get("schema_version") != 1 or
            verified_declarations.get("source_blob_sha1") !=
                {name: SOURCE_PINS[name] for name in sorted(SOURCE_PINS)} or
            verified_declarations.get("observed_verified_against_pinned_engine_sources") is not True or
            any(verified_declarations.get(flag) is not False for flag in (
                "actual_obstacle_definition_ids_verified",
                "actual_goal_definition_ids_verified",
                "actual_booster_instance_ids_verified",
                "owner_art_mapping_verified",
                "engine_lfx_final_abi_verified", "release_allowed"))):
        raise EngineKindError("untrusted Engine source/owner release claims")
    # This preserves engine enum kind names only. No hidden sample IDs
    # become actual gameplay definitions, and no goal/booster reward exists.
    return {
        "schema_version": 1,
        "stage": STAGE,
        "game_candidates": [{
            "profile_id": profile,
            "goal_kind_visual_slots": list(REQUIRED_ENUMS["GoalScoreContracts.cs"]["GoalKind"]),
            "booster_kind_visual_slots": list(REQUIRED_ENUMS["BoosterEconomyContracts.cs"]["BoosterKind"]),
            "damage_kind_visual_slots": list(REQUIRED_ENUMS[
                "ObstacleLifecycleContracts.cs"]["ObstacleDamageKind"]),
            "actual_instance_ids": None,
            "actual_registry_verified": False,
            "original_art_rights_verified": False,
            "gameplay_mutations_allowed": False,
        } for profile in PROFILES],
        "real_engine_lfx_replay_verified": False,
        "owner_approved": False,
        "release_allowed": False,
    }
