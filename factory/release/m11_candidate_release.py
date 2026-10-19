"""M11-001/003/004/005: reproducible TEST_ONLY release-candidate handoff.

A release CANDIDATE is not a shipping release. This reuses the exact M08
SHA-verified source pack and adds deterministic content-addressed compatibility
metadata. No cloud, new libraries, credentials, real Engine/LFX replay or rights
approval. Create-only external destinations. A "rollback" is a NEW immutable
copy of a previously verified candidate, never an overwrite of a live game.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
from pathlib import Path

from factory.asset_packaging.candidate_pack import ROOT
from factory.asset_packaging.verify_offline_bundle import verify_exported_pack

STAGE = "VUF_M11_REVIEW_ONLY_NOT_PRODUCTION"
SCHEMA = 1
PROFILES = ("Coral_Rescue", "Garage_Legends", "Dino_Islands",
            "The_Fractured_Realms", "Wonder_Pop")
HEX = re.compile(r"[0-9a-f]{64}\Z")
SAFE = re.compile(r"[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)*\.(?:png|json)\Z")
MAX_SOURCE_TOTAL = 128 * 1024 * 1024
MAX_FILES = 180
MANIFEST_FILE = "m11_candidate_manifest.json"
ORIGINAL_RECEIPT = "candidate_pack_receipt.json"
PIN_STATE = "OBSERVED_UNACCEPTED_NOT_REPLAY_VERIFIED"


class M11ReleaseError(ValueError):
    pass


def digest(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def canonical(obj: dict) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False) + "\n").encode("utf-8")


def strict_json(data: bytes):
    def pairs(entries):
        result = {}
        for name, value in entries:
            if name in result:
                raise M11ReleaseError("duplicate JSON manifest field")
            result[name] = value
        return result
    try:
        return json.loads(data.decode("utf-8"), object_pairs_hook=pairs)
    except (ValueError, UnicodeError) as exc:
        raise M11ReleaseError("malformed JSON file") from exc


def _checked_external(directory: Path, *, exists: bool) -> Path:
    path = Path(directory)
    if not path.is_absolute():
        raise M11ReleaseError("must provide absolute external path")
    normalized = path.resolve(strict=exists)
    if normalized == ROOT or normalized.is_relative_to(ROOT):
        raise M11ReleaseError("repository/Unity source is not an export destination")
    for p in (path, *path.parents):
        if p.is_symlink() or (hasattr(p, "is_junction") and p.is_junction()):
            raise M11ReleaseError("symlink/junction source or destination rejected")
        if p.exists():
            flag = getattr(p.stat(follow_symlinks=False),
                           "st_file_attributes", 0)
            if flag & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0):
                raise M11ReleaseError("reparse directory rejected")
    if exists:
        if not path.is_dir():
            raise M11ReleaseError("source directory missing")
    elif path.exists() or not path.parent.is_dir():
        raise M11ReleaseError("destination must be NEW under existing external parent")
    return path


def _file_inventory(folder: Path, expected: dict[str, str],
                    *extra_filenames: str) -> None:
    # Stronger than a single receipt check: reject unexpected hidden files,
    # source/Editor assemblies, raw reference art and symlinked extras.
    allowed = set(expected) | {ORIGINAL_RECEIPT, *extra_filenames}
    observed = set()
    total = 0
    for entry in folder.rglob("*"):
        if entry.is_symlink() or (hasattr(entry, "is_junction") and entry.is_junction()):
            raise M11ReleaseError("linked file/directory in candidate")
        if entry.is_dir():
            continue
        if not entry.is_file():
            raise M11ReleaseError("nonregular source in pack")
        rel = entry.relative_to(folder).as_posix()
        if (rel not in allowed or
                (rel not in (MANIFEST_FILE, ORIGINAL_RECEIPT) and
                 not SAFE.fullmatch(rel))):
            raise M11ReleaseError("unsanctioned source file, secret, test, Editor or art")
        observed.add(rel)
        total += entry.stat().st_size
        if total > MAX_SOURCE_TOTAL or len(observed) > MAX_FILES:
            raise M11ReleaseError("candidate file/byte budget exceeded")
        if rel in expected and digest(entry.read_bytes()) != expected[rel]:
            raise M11ReleaseError("asset changed since source SHA receipt")
    if observed != allowed:
        raise M11ReleaseError("manifest file set incomplete")


def _source_inventory(source: Path) -> tuple[dict, dict]:
    proof = verify_exported_pack(source)
    receipt = strict_json((source / ORIGINAL_RECEIPT).read_bytes())
    hashes = receipt.get("file_sha256")
    if not isinstance(hashes, dict) or not 45 <= len(hashes) <= 160:
        raise M11ReleaseError("source receipt missing complete hash mapping")
    if (not isinstance(receipt.get("file_entries"), list) or
            set(hashes) != {entry.get("path") for entry in receipt["file_entries"]
                          if isinstance(entry, dict)}):
        raise M11ReleaseError("typed Unity receipt and Python manifest differ")
    _file_inventory(source, hashes)
    return proof, hashes


def plan(source_dir: Path, engine_sha: str, lfx_sha: str) -> dict:
    """Deterministic plan; observed Git SHAs NEVER assert ABI/acceptance."""
    source = _checked_external(source_dir, exists=True)
    if (not isinstance(engine_sha, str) or not HEX.fullmatch(engine_sha) or
            not isinstance(lfx_sha, str) or not HEX.fullmatch(lfx_sha)):
        raise M11ReleaseError("require independently observed full 40? source IDs")
    # Git revision is 40 hexadecimal characters, while assets use SHA256.
    # No source in the VUF candidate manifest may override this unapproved gate.
    if len(engine_sha) != 40 or len(lfx_sha) != 40:
        raise M11ReleaseError("Engine/LFX must be exact Git SHA1 identifiers")
    proof, hashes = _source_inventory(source)
    body = {
        "schema_version": SCHEMA,
        "stage": STAGE,
        "profile_id": proof["profile_id"],
        "source_manifest_sha256": hashes["visual_manifest.json"],
        "source_receipt_sha256": digest((source / ORIGINAL_RECEIPT).read_bytes()),
        "engine_observed_git_sha": engine_sha,
        "lfx_observed_git_sha": lfx_sha,
        "upstream_pin_state": PIN_STATE,
        "engine_abi_accepted": False,
        "lfx_replay_accepted": False,
        "final_game_action_bound": False,
        "licensed_art_approved": False,
        "owner_visual_approved": False,
        "player_build_tested": False,
        "device_gpu_approved": False,
        "release_allowed": False,
        "artifacts": [{"path": name, "sha256": hashes[name]}
                      for name in sorted(hashes)],
    }
    # Hash self-excluding manifest payload for reproducible identity.
    identity = digest(canonical(body))
    return {**body, "content_identity_sha256": identity}


def validate_manifest(manifest: dict) -> None:
    if not isinstance(manifest, dict):
        raise M11ReleaseError("invalid release manifest")
    allowed = {"schema_version", "stage", "profile_id",
               "source_manifest_sha256", "source_receipt_sha256",
               "engine_observed_git_sha", "lfx_observed_git_sha",
               "upstream_pin_state", "engine_abi_accepted",
               "lfx_replay_accepted", "final_game_action_bound",
               "licensed_art_approved", "owner_visual_approved",
               "player_build_tested", "device_gpu_approved",
               "release_allowed", "artifacts", "content_identity_sha256"}
    if (set(manifest) != allowed or manifest.get("schema_version") != SCHEMA or
            manifest.get("stage") != STAGE or
            manifest.get("profile_id") not in PROFILES or
            manifest.get("upstream_pin_state") != PIN_STATE):
        raise M11ReleaseError("unknown schema/stage/pin status")
    for key in ("engine_abi_accepted", "lfx_replay_accepted",
                "final_game_action_bound", "licensed_art_approved",
                "owner_visual_approved", "player_build_tested",
                "device_gpu_approved", "release_allowed"):
        if manifest.get(key) is not False:
            raise M11ReleaseError("forged owner/Engine/game rights claim")
    for k in ("source_manifest_sha256", "source_receipt_sha256",
              "content_identity_sha256"):
        if not isinstance(manifest.get(k), str) or not HEX.fullmatch(manifest[k]):
            raise M11ReleaseError("invalid digest")
    for k in ("engine_observed_git_sha", "lfx_observed_git_sha"):
        v = manifest.get(k)
        if not isinstance(v, str) or len(v) != 40 or not re.fullmatch("[0-9a-f]{40}", v):
            raise M11ReleaseError("invalid observed Git pin")
    refs = manifest.get("artifacts")
    if not isinstance(refs, list) or not 45 <= len(refs) <= 160:
        raise M11ReleaseError("incomplete file list")
    paths = set()
    for item in refs:
        if not isinstance(item, dict) or set(item) != {"path", "sha256"}:
            raise M11ReleaseError("invalid artifact entry")
        p, sha = item["path"], item["sha256"]
        if (not isinstance(p, str) or not SAFE.fullmatch(p) or
                not isinstance(sha, str) or not HEX.fullmatch(sha) or p in paths):
            raise M11ReleaseError("duplicate/invalid artifact path or hash")
        paths.add(p)
    if [item["path"] for item in refs] != sorted(paths):
        raise M11ReleaseError("noncanonical artifact order")
    base = {k: v for k, v in manifest.items() if k != "content_identity_sha256"}
    if digest(canonical(base)) != manifest["content_identity_sha256"]:
        raise M11ReleaseError("candidate identity changed")


def verify_release(directory: Path) -> dict:
    folder = _checked_external(directory, exists=True)
    manifest = strict_json((folder / MANIFEST_FILE).read_bytes())
    validate_manifest(manifest)
    by_path = {v["path"]: v["sha256"] for v in manifest["artifacts"]}
    _file_inventory(folder, by_path, MANIFEST_FILE)
    proof, original = _source_inventory_released(folder)
    if (original != by_path or
            digest((folder / ORIGINAL_RECEIPT).read_bytes()) !=
            manifest["source_receipt_sha256"] or
            original["visual_manifest.json"] != manifest["source_manifest_sha256"] or
            proof["profile_id"] != manifest["profile_id"]):
        raise M11ReleaseError("underlying source does not match release plan")
    return {
        "content_identity_sha256": manifest["content_identity_sha256"],
        "stage": STAGE, "profile_id": manifest["profile_id"],
        "artifact_count": len(by_path),
        "real_engine_lfx_accepted": False,
        "licensed_art_approved": False,
        "external_release_owner_approved": False,
        "player_build_exclusion_approved": False,
        "release_allowed": False,
    }


def _source_inventory_released(directory: Path):
    """Verify M08 source contract without misreading our own extra manifest."""
    proof = verify_exported_pack(directory)
    receipt = strict_json((directory / ORIGINAL_RECEIPT).read_bytes())
    hashes = receipt["file_sha256"]
    _file_inventory(directory, hashes, MANIFEST_FILE)
    return proof, hashes


def _write_exact(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())


def export_review_candidate(source_dir: Path, destination_dir: Path,
                            engine_sha: str, lfx_sha: str) -> dict:
    source = _checked_external(source_dir, exists=True)
    target = _checked_external(destination_dir, exists=False)
    manifest = plan(source, engine_sha, lfx_sha)
    target.mkdir()
    try:
        for record in manifest["artifacts"]:
            rel = record["path"]
            raw = (source / rel).read_bytes()
            if digest(raw) != record["sha256"]:
                raise M11ReleaseError("source changed during release export")
            _write_exact(target / rel, raw)
        raw_receipt = (source / ORIGINAL_RECEIPT).read_bytes()
        if digest(raw_receipt) != manifest["source_receipt_sha256"]:
            raise M11ReleaseError("source receipt changed during export")
        _write_exact(target / ORIGINAL_RECEIPT, raw_receipt)
        _write_exact(target / MANIFEST_FILE, canonical(manifest))
        return verify_release(target)
    except Exception:
        # Deliberately NO DELETE: leave only our rejected new destination
        # for owner-safe inspection, never silently remove evidence.
        raise


def import_new_copy(release_dir: Path, new_slot_dir: Path,
                    *, rollback_from: Path | None = None) -> dict:
    """Append-only dry-review import. Rollback = NEW older release copy, not
    changing any running game's active pointer or removing any current slot.
    """
    incoming = _checked_external(release_dir, exists=True)
    proof = verify_release(incoming)
    if rollback_from is not None:
        prior = verify_release(_checked_external(rollback_from, exists=True))
        if prior["profile_id"] != proof["profile_id"]:
            raise M11ReleaseError("cannot rollback across game profiles")
    slot = _checked_external(new_slot_dir, exists=False)
    slot.mkdir()
    manifest = strict_json((incoming / MANIFEST_FILE).read_bytes())
    for record in manifest["artifacts"]:
        raw = (incoming / record["path"]).read_bytes()
        if digest(raw) != record["sha256"]:
            raise M11ReleaseError("release changed while staging import")
        _write_exact(slot / record["path"], raw)
    _write_exact(slot / ORIGINAL_RECEIPT,
                 (incoming / ORIGINAL_RECEIPT).read_bytes())
    _write_exact(slot / MANIFEST_FILE, canonical(manifest))
    checked = verify_release(slot)
    checked["operation"] = ("ROLLBACK_NEW_COPY_ONLY" if
                             rollback_from is not None else "IMPORT_NEW_COPY_ONLY")
    checked["modified_active_game_pointer"] = False
    checked["deleted_previous_revision"] = False
    return checked


def release_audit(directory: Path) -> dict:
    proof = verify_release(directory)
    return {
        **proof,
        "rights_evidence_legal_verified": False,
        "independent_audit_signed": False,
        "consumer_G01_G02_G09_G11_handoff_signed": False,
        "reproducible_source_identity_verified": True,
        "all_package_source_hashes_verified": True,
        "cloud_paid_dependencies_used": False,
        "owner_approval_required": True,
        "release_allowed": False,
        "blocked_gates": [
            "ENGINE_M12_FINAL_NEUTRAL_REPLAY",
            "LFX_ENGINE_M24_FINAL_REPRESENTATIVE_PACK",
            "ORIGINAL_ART_FONT_LICENCE_OWNER_SIGNATURE",
            "ACTUAL_UNITY_GUI_PLAYMODE_PLAYER_BUILD",
            "PHYSICAL_MOBILE_GPU_AND_GAME_TITLE_HANDOFF",
        ],
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="action", required=True)
    e = sub.add_parser("export")
    e.add_argument("--source", type=Path, required=True)
    e.add_argument("--new-dir", type=Path, required=True)
    e.add_argument("--engine-sha", required=True)
    e.add_argument("--lfx-sha", required=True)
    a = sub.add_parser("audit")
    a.add_argument("--candidate", type=Path, required=True)
    i = sub.add_parser("import")
    i.add_argument("--candidate", type=Path, required=True)
    i.add_argument("--new-slot", type=Path, required=True)
    i.add_argument("--rollback-from", type=Path)
    args = p.parse_args(argv)
    try:
        if args.action == "export":
            result = export_review_candidate(
                args.source, args.new_dir, args.engine_sha, args.lfx_sha)
        elif args.action == "audit":
            result = release_audit(args.candidate)
        else:
            result = import_new_copy(
                args.candidate, args.new_slot,
                rollback_from=args.rollback_from)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (M11ReleaseError, ValueError, OSError) as exc:
        p.exit(2, "VUF_M11_REVIEW_RELEASE_REJECTED: " + str(exc) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
