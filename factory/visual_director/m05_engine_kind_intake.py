"""M05 read-only exact Engine enum provenance for visual binding drafts.

Enumerated *kinds* are real declarations, but actual obstacle/goal/booster
instance/definition IDs are NOT published in these four interface files.
Do not promote symbolic visual candidates to production IDs or art rights.

The caller supplies original C# bytes read without writing to the sibling
MATCH3_ENGINE repository. Git blob SHA verifies provenance, not an ABI release.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
from pathlib import Path
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


def draft_five_title_role_bindings(original_engine_sources: Mapping[str, bytes]) -> dict:
    """Require REAL original C# bytes, not a forgeable JSON summary."""
    verified_declarations = inspect_pinned_engine_kinds(original_engine_sources)
    if verified_declarations["observed_verified_against_pinned_engine_sources"] is not True:
        raise EngineKindError("missing authenticated exact Engine source pins")
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


def _link_or_junction(path: Path) -> bool:
    if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
        return True
    try:
        details = path.stat(follow_symlinks=False)
    except OSError as exc:
        raise EngineKindError("unable to inspect Engine source path") from exc
    return bool(getattr(details, "st_file_attributes", 0) &
                getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def _canonical_checkout_source_eol(
    raw: bytes, pinned_blob_sha: str
) -> tuple[bytes, dict]:
    """Accept only exact pinned LF bytes or a pure-CRLF checkout rendering.

    Git hashes canonical blob bytes after checkout EOL conversion.
    This does NOT relax byte identity: normalized bytes must be exactly
    the pinned Git blob. Never modify the working-tree file.
    """
    if (not isinstance(raw, bytes) or
            not 0 < len(raw) <= 2 * MAX_BYTES_PER_SOURCE or
            not isinstance(pinned_blob_sha, str) or
            re.fullmatch(r"[0-9a-f]{40}", pinned_blob_sha) is None):
        raise EngineKindError("unsafe Engine source bytes / invalid pinned blob SHA")
    if len(raw) <= MAX_BYTES_PER_SOURCE:
        observed = git_blob_sha(raw)
        if observed == pinned_blob_sha:
            return raw, {
                "checkout_transport_eol": "EXACT_PINNED_BYTES",
                "raw_checkout_blob_sha1": observed,
                "canonical_git_blob_sha1": pinned_blob_sha,
                "canonical_bytes_match_pin": True,
                "worktree_file_modified": False,
                "final_registry_ids_verified": False,
                "release_allowed": False,
            }
    # Reject mixed CRLF/LF, bare CR, and LF-only but edited source.
    # Every newline must be CRLF before converting in memory.
    if (b"\r\n" not in raw or
            raw.count(b"\r\n") != raw.count(b"\r") or
            raw.count(b"\r\n") != raw.count(b"\n")):
        raise EngineKindError("Engine checkout bytes do not match LF pin, not pure CRLF")
    canonical = raw.replace(b"\r\n", b"\n")
    if len(canonical) > MAX_BYTES_PER_SOURCE or git_blob_sha(canonical) != pinned_blob_sha:
        raise EngineKindError("pure CRLF checkout normalization does not match exact pinned Git blob")
    raw_blob_sha = hashlib.sha1(
        b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw
    ).hexdigest()
    return canonical, {
        "checkout_transport_eol": "PURE_CRLF_NORMALIZED_IN_MEMORY",
        "raw_checkout_blob_sha1": raw_blob_sha,
        "canonical_git_blob_sha1": pinned_blob_sha,
        "canonical_bytes_match_pin": True,
        "worktree_file_modified": False,
        "final_registry_ids_verified": False,
        "release_allowed": False,
    }


def read_pinned_engine_sources_with_receipts(
    runtime_directory: Path,
) -> tuple[dict[str, bytes], dict[str, dict]]:
    """Read existing separate Engine checkout, accepting only pinned EOL.

    Sources are canonical bytes. Receipts distinguish LF-exact versus
    CRLF-equivalent checkout files. No Git commands, writes or cloning.
    """
    folder = Path(runtime_directory)
    if (not folder.is_dir() or _link_or_junction(folder) or
            folder.name != "Runtime" or
            folder.parent.name != "com.match3.engine" or
            folder.parent.parent.name != "Packages"):
        raise EngineKindError("must select real local Engine Packages/.../Runtime")
    repo_root = Path(__file__).resolve().parents[2]
    if folder.resolve().is_relative_to(repo_root):
        raise EngineKindError("Engine original source must not be copied into VUF")
    if any(_link_or_junction(p) for p in folder.parents if p.exists()):
        raise EngineKindError("linked/junction Engine ancestor refused")
    inputs = {}
    receipts = {}
    for full_path in sorted(SOURCE_PINS):
        source = folder / full_path.rsplit("/", 1)[-1]
        if source.is_symlink() or not source.is_file() or _link_or_junction(source):
            raise EngineKindError("missing/untrusted original Engine C# source")
        before = source.stat()
        if not 0 < before.st_size <= 2 * MAX_BYTES_PER_SOURCE:
            raise EngineKindError("Engine source has unsafe byte size")
        raw = source.read_bytes()
        after = source.stat()
        if (before.st_size != after.st_size or
                before.st_mtime_ns != after.st_mtime_ns or
                len(raw) != before.st_size):
            raise EngineKindError("Engine source changed during read-only audit")
        canonical, receipt = _canonical_checkout_source_eol(raw, SOURCE_PINS[full_path])
        inputs[full_path] = canonical
        receipts[full_path] = receipt
    return inputs, receipts


def read_pinned_engine_sources(runtime_directory: Path) -> dict[str, bytes]:
    """Backwards-compatible, source-only API; read no checkout writes."""
    canonical, _receipts = read_pinned_engine_sources_with_receipts(runtime_directory)
    return canonical


def main(argv=None) -> int:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--engine-runtime", required=True, type=Path,
                     help="External sibling MATCH3_ENGINE Packages/.../Runtime")
    args = cli.parse_args(argv)
    try:
        sources, checkout_receipts = read_pinned_engine_sources_with_receipts(
            args.engine_runtime)
        report = inspect_pinned_engine_kinds(sources)
        report["engine_checkout_eol_receipts"] = checkout_receipts
        report["five_game_role_candidates"] = draft_five_title_role_bindings(sources)
        print(json.dumps(report, sort_keys=True, indent=2))
        return 0
    except (EngineKindError, OSError) as exc:
        cli.exit(2, "M05_ENGINE_SOURCE_BLOCKED: " + str(exc) + "\\n")


if __name__ == "__main__":
    raise SystemExit(main())
