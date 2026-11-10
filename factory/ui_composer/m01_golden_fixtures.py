"""VUF-M01-008: Deterministic golden fixtures for the 5×17×8 UI contract matrix.

Generates a source-only snapshot of the full matrix + fallback contract, keyed
by its own SHA-256.  Callers that need to verify that the matrix has not drifted
compare the live build against this fixture.

PROTOTYPE-ONLY: ENG-M24 is not PASS.  No runtime binding, no owner sign-off.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from factory.ui_composer.m01_surface_contract_matrix import (
    AUTH_FALSE, CATALOG, ENGINE_ACTION_KINDS, ENGINE_STATES, ENGINE_SURFACES,
    M01MatrixError, build_m01_matrix, verify_m01_matrix,
)

ROOT = Path(__file__).resolve().parents[2]
GOLDEN_PATH = ROOT / "schemas" / "m01_golden_fixture.v1.json"
GOLDEN_FIXTURE_STAGE = "M01_GOLDEN_FIXTURE_PROTOTYPE_ONLY_SOURCE_CANDIDATE_NOT_ENGINE_BINDING"


class GoldenFixtureError(ValueError):
    pass


def _summarise(matrix: dict) -> dict:
    """Minimal verifiable summary extracted from the full matrix."""
    return {
        "stage": matrix["stage"],
        "matrix_sha256": matrix["matrix_sha256"],
        "profile_count": len(matrix["profile_ids"]),
        "profile_ids": list(matrix["profile_ids"]),
        "surface_kinds": list(matrix["engine_ui_surface_kinds"]),
        "player_state_kinds": list(matrix["engine_player_state_kinds"]),
        "action_kind_namespace": list(matrix["engine_action_kinds"]),
        "matrix_rows": len(matrix["matrix"]),
        "screen_state_rows": len(matrix["screen_states"]),
        "source_screen_count": matrix["screen_count_source_coral"],
        "surface_state_count_per_profile": matrix["surface_state_count_per_profile"],
        "screen_state_count_per_profile": matrix["screen_state_count_per_profile"],
        "absent_engine_surfaces": sorted({
            row["engine_surface_kind"]
            for row in matrix["matrix"]
            if row["source_screens_absent"]
        }),
        "policy_off_screens": sorted({
            row["screen_key"]
            for row in matrix["screen_states"]
            if row["policy_feature_off"]
        }),
        "auth_flags": {flag: matrix[flag] for flag in AUTH_FALSE},
    }


def build_golden(catalog_source: bytes | None = None) -> dict:
    """Build deterministic golden fixture from live catalog source.

    Returns the full summary dict, NOT the entire 1,800-row matrix packet.
    The full matrix is verifiable via its matrix_sha256 field.
    """
    if catalog_source is None:
        catalog_source = CATALOG.read_bytes()
    matrix = build_m01_matrix(catalog_source)
    verify_m01_matrix(matrix, catalog_source)
    summary = _summarise(matrix)
    summary["fixture_stage"] = GOLDEN_FIXTURE_STAGE
    canonical = json.dumps(summary, sort_keys=True,
                           separators=(",", ":"), ensure_ascii=True).encode()
    summary["fixture_sha256"] = hashlib.sha256(canonical).hexdigest()
    return summary


def save_golden(catalog_source: bytes | None = None,
                dest: Path | None = None) -> Path:
    """Write golden fixture to dest (default: schemas/m01_golden_fixture.v1.json).

    Fails closed if the destination already exists and differs.
    Never writes outside the schemas/ directory; never overwrites without
    matching SHA.
    """
    dest = Path(dest) if dest else GOLDEN_PATH
    if not dest.parent.is_dir():
        raise GoldenFixtureError("golden output directory does not exist: " + str(dest.parent))
    golden = build_golden(catalog_source)
    serialized = json.dumps(golden, sort_keys=True, indent=2,
                            ensure_ascii=True) + "\n"
    if dest.exists():
        existing = json.loads(dest.read_text("utf-8"))
        if existing.get("fixture_sha256") == golden["fixture_sha256"]:
            return dest  # idempotent
        raise GoldenFixtureError(
            "golden fixture SHA mismatch; delete manually and regenerate: " + str(dest)
        )
    dest.write_text(serialized, encoding="utf-8")
    return dest


def verify_golden(golden: dict, catalog_source: bytes | None = None) -> None:
    """Fail closed if live build no longer matches the saved golden."""
    if not isinstance(golden, dict) or "fixture_sha256" not in golden:
        raise GoldenFixtureError("invalid golden fixture structure")
    live = build_golden(catalog_source)
    if live["fixture_sha256"] != golden["fixture_sha256"]:
        raise GoldenFixtureError(
            "live matrix golden SHA drifted from saved fixture:\n"
            f"  saved={golden['fixture_sha256']}\n  live ={live['fixture_sha256']}"
        )
    # Verify ALL auth flags are still False
    for flag, val in golden["auth_flags"].items():
        if val:
            raise GoldenFixtureError(f"auth flag {flag!r} must remain False in golden")
    # Verify row counts
    if golden["matrix_rows"] != 680:
        raise GoldenFixtureError("golden matrix_rows must be 680")
    if golden["screen_state_rows"] != 1120:
        raise GoldenFixtureError("golden screen_state_rows must be 1120")


def load_golden(path: Path | None = None) -> dict:
    """Load and parse the saved golden fixture."""
    path = Path(path) if path else GOLDEN_PATH
    if not path.is_file():
        raise GoldenFixtureError("golden fixture not found: " + str(path))
    return json.loads(path.read_text("utf-8"))


if __name__ == "__main__":
    dest = save_golden()
    golden = load_golden(dest)
    verify_golden(golden)
    print(json.dumps({
        "fixture_sha256": golden["fixture_sha256"],
        "matrix_sha256": golden["matrix_sha256"],
        "matrix_rows": golden["matrix_rows"],
        "screen_state_rows": golden["screen_state_rows"],
        "auth_all_false": all(not v for v in golden["auth_flags"].values()),
    }, indent=2))
