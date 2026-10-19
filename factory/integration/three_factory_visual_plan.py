"""Deterministic VUF visual review plan for *real* LFX source + Engine event receipt.

The input LFXV1 must be produced by the actual LevelDraftJson exporter and
M3P1 must be encoded from actual Engine PresentationEvent objects. A valid SHA
shows data integrity, not trusted origin or actual settled gameplay.

Only explicit user-selected TEST_ONLY VUF art bindings may appear. No guessing
that a LevelFactory `contentId` maps to licensed or production image.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from factory.integration.cross_factory_contract import (
    CrossFactoryError, read_lfxv1, read_m3p1, bind_readonly,
)
from factory.asset_packaging.verify_offline_bundle import verify_exported_pack

STAGE = "VUF_THREE_FACTORY_VIEW_PLAN_UNAPPROVED"
MAX_CELLS = 4096
MAX_EVENTS = 2048
MAX_BINDINGS = 1024


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _validate_map(value: object, content_keys: set[str],
                  lookup: dict[str, dict], profile: str) -> dict[str, dict]:
    if not isinstance(value, dict) or len(value) > MAX_BINDINGS:
        raise CrossFactoryError("explicit mapping must be bounded JSON object")
    if not set(value).issubset(content_keys):
        raise CrossFactoryError("mapping includes source ID absent from real LFX draft")
    out = {}
    for source_key, asset_id in sorted(value.items()):
        if not isinstance(source_key, str) or not isinstance(asset_id, str):
            raise CrossFactoryError("invalid source/asset id")
        if not asset_id.startswith(profile + ".") or asset_id not in lookup:
            raise CrossFactoryError("VUF source ID has no matching TEST_ONLY namespace asset")
        a = lookup[asset_id]
        if (a["state"] != "CANDIDATE" or a["rights"] != "REVIEW_PENDING" or
                a["source_receipt"] != "MATHEMATICAL_PLACEHOLDER_NOT_FINAL"):
            raise CrossFactoryError("art rights must remain pending")
        out[source_key] = {
            "assetId": asset_id,
            "relativePath": a["path"],
            "assetSha256": a["sha256"],
            "candidateOnly": True,
            "ownerLicensed": False,
        }
    return out


def compile_view_plan(*, canonical_lfx: bytes, lfxv1: bytes, m3p1: bytes,
                      vuf_pack: Path | None = None,
                      explicit_content_map: dict[str, str] | None = None) -> dict[str, Any]:
    level = read_lfxv1(lfxv1)
    if not isinstance(canonical_lfx, bytes) or _sha(canonical_lfx) != level["sourceDraftSha256"]:
        raise CrossFactoryError("canonical real LevelFactory source mismatch")
    event_list = read_m3p1(m3p1, level["gameProfileId"])
    basic = bind_readonly(level, event_list, source_sha=_sha(m3p1))
    pack_proof = None
    lookup: dict[str, dict] = {}
    if vuf_pack is not None:
        pack_proof = verify_exported_pack(vuf_pack)
        if (pack_proof.get("profile_id") != level["gameProfileId"] or
                pack_proof.get("stage") != "TEST_ONLY" or
                pack_proof.get("release_allowed") is not False):
            raise CrossFactoryError("cross-title or promoted visual source rejected")
        manifest = json.loads((Path(vuf_pack) / "visual_manifest.json").read_text("utf-8"))
        if (manifest.get("profile_id") != level["gameProfileId"] or
                manifest.get("stage") != "TEST_ONLY"):
            raise CrossFactoryError("visual manifest has unsafe authority")
        for row in manifest.get("assets", []):
            if not isinstance(row, dict) or row.get("asset_id") in lookup:
                raise CrossFactoryError("duplicate or missing candidate visual ID")
            lookup[row["asset_id"]] = row
    content_keys = {
        field
        for c in level["cells"]
        for field in (c["contentId"], c["obstacleId"], c["specialId"])
        if field is not None
    }
    binding = _validate_map(
        explicit_content_map if explicit_content_map is not None else {},
        content_keys, lookup, level["gameProfileId"])

    # Do not invent evolution of the board after a clear or refill. Snapshot
    # is the genuine LevelDraft starting-state geometry and the event positions
    # are observed immutable Engine presentation source. No synthetic WIN.
    cells = []
    for c in sorted(level["cells"],
                    key=lambda c: (c["layer"], c["row"], c["column"])):
        candidates = {
            field: binding.get(c[field])
            for field in ("contentId", "obstacleId", "specialId")
            if c[field] is not None
        }
        cells.append({
            "position": [c["layer"], c["row"], c["column"]],
            "active": c["active"], "locked": c["locked"],
            "contentId": c["contentId"], "obstacleId": c["obstacleId"],
            "specialId": c["specialId"],
            "obstacleDurability": c["obstacleDurability"],
            "lockDurability": c["lockDurability"],
            "selectedCandidateVisuals": candidates,
        })
    timeline = []
    for e in event_list:
        timeline.append({
            "index": e["sequence"]-1,
            "eventId": e["eventId"],
            "presentationKey": e["presentationKey"],
            "actualEngineKindOrdinal": e["kind"],
            "intensityOrdinal": e["intensity"],
            "viewOnlyCue": e["vufCue"],
            "positions": [[layer, row, col] for layer, row, col in e["positions"]],
            "previewAction": "HIGHLIGHT_COORDINATES_ONLY",
            "changesBoard": False,
            "awardsCoins": False,
            "settledGameSnapshotProven": False,
        })
    return {
        "schemaVersion": 1,
        "stage": STAGE,
        "profileId": level["gameProfileId"],
        "levelId": level["levelId"],
        "width": level["width"], "height": level["height"],
        "layers": level["layers"], "sourceMoveBudget": level["moveBudget"],
        "sourceSeed": level["seed"],
        "lfxCanonicalSha256": _sha(canonical_lfx),
        "lfxVisualEnvelopeSha256": _sha(lfxv1),
        "engineVisualReceiptSha256": _sha(m3p1),
        "realSourceContract": basic,
        "initialDraftCells": cells,
        "draftGoals": level["goals"],
        "viewTimeline": timeline,
        "explicitArtBindingCount": len(binding),
        "vufPackShaVerified": pack_proof is not None,
        "candidateVisualsOnly": True,
        "sourceAuthenticationIndependentlyProven": False,
        "engineFinalSettledReplayVerified": False,
        "actualMoveOutcomeOrWinVerified": False,
        "actualVisualFxPlayed": False,
        "licensedOriginalArtworkApproved": False,
        "ownerAestheticApproved": False,
        "releaseAllowed": False,
    }
