"""
VUF-M00-001 | Engine M09 and LFX M08 API Freeze
Read-only source inventory extracted 2026-11-10.

Purpose: pin the exact commit SHAs and public API surfaces that VUF is
permitted to consume from Engine (M09 close) and Level Factory (M08 close).
No game logic, no cross-repo write.

Legal restrictions (see TASKS.md VUF-M00-004 and donor ledger):
  - Rimaethon assets/code: CC BY-NC-ND — NOT an import candidate.
  - Engine source: internal proprietary; read-only VUF reference only.
  - LFX source: internal proprietary; read-only VUF reference only.
  - Original licensed art, fonts, real device SHAs: OWNER gate, not VUF.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Tuple

# ---------------------------------------------------------------------------
# Engine M09 milestone close
# Source repo:  Sekiph82/MATCH3_ENGINE
# Commit SHA:   9af6e16eafd2dc6b3d764a53aee2ff1e15c21a7c
# Subject:      docs(tasks): close M09 neutral contract R02 after verified
#               source parity; unlock M10
# API file SHAs at that commit:
#   PresentationUiContracts.cs      b7c3c05d0c073e40f8dc1c4799a8bc1d869100f6
#   PresentationSurfaceContracts.cs 7598366d6eca3401ac461cb557ebd576fd09be72
# ---------------------------------------------------------------------------

ENGINE_M09_COMMIT_SHA: str = "9af6e16eafd2dc6b3d764a53aee2ff1e15c21a7c"
ENGINE_M09_UI_CONTRACTS_BLOB: str = "b7c3c05d0c073e40f8dc1c4799a8bc1d869100f6"
ENGINE_M09_SURFACE_CONTRACTS_BLOB: str = "7598366d6eca3401ac461cb557ebd576fd09be72"

# UiSurfaceKind enum — 17 members; namespace Match3.Engine.Runtime
# Source: PresentationUiContracts.cs enum UiSurfaceKind
ENGINE_UI_SURFACE_KIND: Tuple[str, ...] = (
    "Home",           # 0
    "WorldMap",       # 1
    "Hud",            # 2
    "Results",        # 3
    "Pause",          # 4
    "Settings",       # 5
    "Shop",           # 6
    "DailyRewards",   # 7
    "Tasks",          # 8
    "Fail",           # 9
    "Life",           # 10
    "Booster",        # 11
    "Collection",     # 12
    "Achievements",   # 13
    "Store",          # 14
    "Account",        # 15
    "Consent",        # 16
)

# UiActionKind enum — 4 members; namespace Match3.Engine.Runtime
# Source: PresentationUiContracts.cs enum UiActionKind
ENGINE_UI_ACTION_KIND: Tuple[str, ...] = (
    "Navigate",   # 0
    "Command",    # 1
    "Back",       # 2
    "Close",      # 3
)

# PlayerSurfaceStateKind enum — 8 members; namespace Match3.Engine.Runtime
# Source: PresentationSurfaceContracts.cs enum PlayerSurfaceStateKind
ENGINE_PLAYER_SURFACE_STATE_KIND: Tuple[str, ...] = (
    "Ready",     # 0
    "Loading",   # 1
    "Offline",   # 2
    "Error",     # 3
    "Owned",     # 4
    "Claimed",   # 5
    "Disabled",  # 6
    "Pending",   # 7
)

# ---------------------------------------------------------------------------
# LFX M08 milestone close
# Source repo:  Sekiph82/Match3-Level-Factory
# Commit SHA:   d8d0b37ce71c4e2c0bdb72f9ed1d2a48068281c3
# Subject:      fix(lfx-m08-007): correct Unity inspector banner to
#               distinguish padded tail counters
# API file blob at that commit:
#   Assets/Match3Factory/Editor/LevelDraftJson.cs  ae9acff76aa5d616290d0b237c1d5f1d01c047c1
# Note: LevelDraftVisualHandoff.cs was added AFTER d8d0b37; not in M08.
# ---------------------------------------------------------------------------

LFX_M08_COMMIT_SHA: str = "d8d0b37ce71c4e2c0bdb72f9ed1d2a48068281c3"
LFX_M08_DRAFT_JSON_BLOB: str = "ae9acff76aa5d616290d0b237c1d5f1d01c047c1"

# LevelDraftJson root keys — extracted from LevelDraftJson.cs DraftKeys array
LFX_LEVEL_DRAFT_ROOT_KEYS: Tuple[str, ...] = (
    "draftVersion", "validationStatus", "gameProfileId", "profileVersion",
    "worldId", "chapterId", "levelId", "releaseChannel", "platform", "locale",
    "minEngineVersion", "maxEngineVersion", "seed", "width", "height",
    "layers", "activeMask", "moveBudget", "timedMode", "timeLimitSeconds",
    "oneStarThreshold", "twoStarThreshold", "threeStarThreshold",
    "difficultyLabel", "editorHintKey", "cells", "goals",
    "engineSchemaVersion", "sourceRepository", "sourceRevision", "sourceKind",
)

# LevelDraftJson cell keys — extracted from CellKeys array
LFX_CELL_KEYS: Tuple[str, ...] = (
    "row", "column", "layer", "active", "locked",
    "contentId", "obstacleId", "obstacleDurability",
    "lockDurability", "specialId",
)

# LevelDraftJson goal keys — extracted from GoalKeys array
LFX_GOAL_KEYS: Tuple[str, ...] = (
    "goalId", "targetId", "targetCount",
)

# ---------------------------------------------------------------------------
# Canonical counts (invariants for negative tests)
# ---------------------------------------------------------------------------

ENGINE_UI_SURFACE_COUNT: int = 17   # must equal len(ENGINE_UI_SURFACE_KIND)
ENGINE_UI_ACTION_COUNT: int = 4     # must equal len(ENGINE_UI_ACTION_KIND)
ENGINE_PLAYER_STATE_COUNT: int = 8  # must equal len(ENGINE_PLAYER_SURFACE_STATE_KIND)
LFX_DRAFT_ROOT_KEY_COUNT: int = 31  # must equal len(LFX_LEVEL_DRAFT_ROOT_KEYS)
LFX_CELL_KEY_COUNT: int = 10        # must equal len(LFX_CELL_KEYS)
LFX_GOAL_KEY_COUNT: int = 3         # must equal len(LFX_GOAL_KEYS)


@dataclass(frozen=True)
class ApiFreeze:
    """Read-only snapshot of Engine M09 and LFX M08 API surfaces."""

    engine_m09_sha: str
    engine_ui_surfaces: Tuple[str, ...]
    engine_ui_actions: Tuple[str, ...]
    engine_player_states: Tuple[str, ...]
    lfx_m08_sha: str
    lfx_draft_root_keys: Tuple[str, ...]
    lfx_cell_keys: Tuple[str, ...]
    lfx_goal_keys: Tuple[str, ...]

    # Hard limits from source
    legal_restrictions: Tuple[str, ...] = field(default_factory=tuple)


FREEZE: ApiFreeze = ApiFreeze(
    engine_m09_sha=ENGINE_M09_COMMIT_SHA,
    engine_ui_surfaces=ENGINE_UI_SURFACE_KIND,
    engine_ui_actions=ENGINE_UI_ACTION_KIND,
    engine_player_states=ENGINE_PLAYER_SURFACE_STATE_KIND,
    lfx_m08_sha=LFX_M08_COMMIT_SHA,
    lfx_draft_root_keys=LFX_LEVEL_DRAFT_ROOT_KEYS,
    lfx_cell_keys=LFX_CELL_KEYS,
    lfx_goal_keys=LFX_GOAL_KEYS,
    legal_restrictions=(
        "Rimaethon/MATCH3 assets: CC BY-NC-ND — not an import candidate.",
        "Engine/LFX source: internal proprietary — read-only VUF reference.",
        "No production release, no paid CI, no store submission.",
        "Owner art/font rights: separate gate; never assumed by this freeze.",
    ),
)


def assert_invariants() -> None:
    """Fail fast if the freeze constants drift from the tuples above."""
    assert len(FREEZE.engine_ui_surfaces) == ENGINE_UI_SURFACE_COUNT, (
        f"UiSurfaceKind count drifted: {len(FREEZE.engine_ui_surfaces)}"
    )
    assert len(FREEZE.engine_ui_actions) == ENGINE_UI_ACTION_COUNT, (
        f"UiActionKind count drifted: {len(FREEZE.engine_ui_actions)}"
    )
    assert len(FREEZE.engine_player_states) == ENGINE_PLAYER_STATE_COUNT, (
        f"PlayerSurfaceStateKind count drifted: {len(FREEZE.engine_player_states)}"
    )
    assert len(FREEZE.lfx_draft_root_keys) == LFX_DRAFT_ROOT_KEY_COUNT, (
        f"LFX root key count drifted: {len(FREEZE.lfx_draft_root_keys)}"
    )
    assert len(FREEZE.lfx_cell_keys) == LFX_CELL_KEY_COUNT, (
        f"LFX cell key count drifted: {len(FREEZE.lfx_cell_keys)}"
    )
    assert len(FREEZE.lfx_goal_keys) == LFX_GOAL_KEY_COUNT, (
        f"LFX goal key count drifted: {len(FREEZE.lfx_goal_keys)}"
    )
    # No duplicate surface names
    assert len(set(FREEZE.engine_ui_surfaces)) == len(FREEZE.engine_ui_surfaces), (
        "UiSurfaceKind has duplicate entries."
    )
    # SHA format sanity
    assert len(FREEZE.engine_m09_sha) == 40 and all(c in "0123456789abcdef" for c in FREEZE.engine_m09_sha), (
        "Engine M09 SHA is not a valid 40-hex SHA-1."
    )
    assert len(FREEZE.lfx_m08_sha) == 40 and all(c in "0123456789abcdef" for c in FREEZE.lfx_m08_sha), (
        "LFX M08 SHA is not a valid 40-hex SHA-1."
    )


if __name__ == "__main__":
    assert_invariants()
    print(f"Engine M09 SHA : {FREEZE.engine_m09_sha}")
    print(f"  UiSurfaceKind ({ENGINE_UI_SURFACE_COUNT}): {', '.join(FREEZE.engine_ui_surfaces)}")
    print(f"  UiActionKind  ({ENGINE_UI_ACTION_COUNT}): {', '.join(FREEZE.engine_ui_actions)}")
    print(f"  PlayerSurfaceStateKind ({ENGINE_PLAYER_STATE_COUNT}): {', '.join(FREEZE.engine_player_states)}")
    print(f"LFX M08 SHA    : {FREEZE.lfx_m08_sha}")
    print(f"  LevelDraft root keys ({LFX_DRAFT_ROOT_KEY_COUNT}): {', '.join(FREEZE.lfx_draft_root_keys)}")
    print(f"  Cell keys ({LFX_CELL_KEY_COUNT}): {', '.join(FREEZE.lfx_cell_keys)}")
    print(f"  Goal keys ({LFX_GOAL_KEY_COUNT}): {', '.join(FREEZE.lfx_goal_keys)}")
    print("Legal restrictions:")
    for r in FREEZE.legal_restrictions:
        print(f"  - {r}")
    print("All invariants OK.")
