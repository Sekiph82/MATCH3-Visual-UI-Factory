"""M04 owner-original versus candidate mechanical comparison (read-only).

INTERNAL_REUSE: M09 exact RGBA pixel verifier, M02 fixed five-title IDs,
M09 strict provenance receipt-shape check. Does not approve originality,
creator identity, licenses, rights, design quality, or gameplay assets.
No file-system mutation, cloud provider or preview export occurs here.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any

from factory.qa.m09_pixel_diff import (
    PixelReviewError, compare, verify_receipt_source,
)
from factory.visual_director.m02_style_bible import PROFILES

SHA = re.compile(r"[0-9a-f]{64}\Z")
ASSET_ID = re.compile(r"[A-Za-z][A-Za-z0-9_]{2,60}\.[a-z][a-z0-9_.]{0,75}\Z")
STAGE = "M04_SOURCE_REVIEW_UNAPPROVED"
EXPECTED_KEYS = {
    "schema_version", "stage", "profile_id", "asset_id",
    "reference_sha256", "candidate_sha256", "provenance",
    "owner_originality_approved", "owner_legal_rights_approved",
    "creator_verified", "source_release_allowed",
}


class OriginalReviewError(ValueError):
    """Source comparison refused; not an artistic judgement."""


def _pairs(entries: list[tuple[str, Any]]) -> dict:
    doc = {}
    for key, value in entries:
        if key in doc:
            raise OriginalReviewError("duplicate rights/reference manifest key")
        doc[key] = value
    return doc


def parse_review_contract(raw: bytes) -> dict:
    """Strict no-authority schema, including nested duplicate-key detection."""
    if not isinstance(raw, bytes) or not 0 < len(raw) <= 64 * 1024:
        raise OriginalReviewError("empty or oversized M04 candidate source manifest")
    try:
        obj = json.loads(raw.decode("utf-8", "strict"),
                         object_pairs_hook=_pairs,
                         parse_constant=lambda _: (_ for _ in ()).throw(
                             OriginalReviewError("nonfinite JSON forbidden")))
    except (UnicodeError, ValueError) as exc:
        raise OriginalReviewError("invalid M04 review JSON") from exc
    if not isinstance(obj, dict) or set(obj) != EXPECTED_KEYS:
        raise OriginalReviewError("unexpected or missing M04 source fields")
    profile = obj["profile_id"]
    asset = obj["asset_id"]
    if (obj["schema_version"] != 1 or type(obj["schema_version"]) is not int
            or obj["stage"] != STAGE or profile not in PROFILES or
            not isinstance(asset, str) or ASSET_ID.fullmatch(asset) is None or
            asset.split(".", 1)[0] != profile):
        raise OriginalReviewError("unknown/relabelled five-game asset identity")
    for name in ("reference_sha256", "candidate_sha256"):
        if not isinstance(obj[name], str) or not SHA.fullmatch(obj[name]):
            raise OriginalReviewError("invalid pinned M04 source SHA256")
    for name in ("owner_originality_approved", "owner_legal_rights_approved",
                 "creator_verified", "source_release_allowed"):
        if obj[name] is not False:
            raise OriginalReviewError("source manifest forged human owner authority")
    if not isinstance(obj["provenance"], dict):
        raise OriginalReviewError("original creator provenance missing")
    return obj


def inspect_original_candidate(original_png: bytes, candidate_png: bytes,
                               manifest_bytes: bytes) -> dict:
    """Pure bounded pixel/metadata check. Human acceptance always remains OPEN."""
    contract = parse_review_contract(manifest_bytes)
    original_sha = hashlib.sha256(original_png).hexdigest()
    candidate_sha = hashlib.sha256(candidate_png).hexdigest()
    if (original_sha != contract["reference_sha256"] or
            candidate_sha != contract["candidate_sha256"]):
        raise OriginalReviewError("original/candidate SHA changed since intake")
    original = contract["provenance"]
    try:
        rights = verify_receipt_source(
            original_png, declared_sha=original_sha, provenance=original)
        diff, _ = compare(
            original_png, candidate_png, expected_sha=original_sha)
    except PixelReviewError as exc:
        raise OriginalReviewError("M04 source compare rejected: " + str(exc)) from exc
    if (original.get("asset_id") != contract["asset_id"] or
            original.get("profile_id") != contract["profile_id"]):
        raise OriginalReviewError("creator receipt belongs to another art family")
    if rights["image_use_authorized_for_release"] is not False:
        raise OriginalReviewError("upstream must never auto-approve original art")
    identity_input = "\n".join((
        contract["profile_id"], contract["asset_id"],
        original_sha, candidate_sha,
    )).encode("utf-8")
    return {
        "schema_version": 1,
        "stage": STAGE,
        "profile_id": contract["profile_id"],
        "asset_id": contract["asset_id"],
        "source_lineage_sha256": hashlib.sha256(identity_input).hexdigest(),
        "reference_sha256": original_sha,
        "candidate_sha256": candidate_sha,
        "reference_byte_hash_verified": True,
        "candidate_byte_hash_verified": True,
        "source_shape_provenance_present": rights["provenance_fields_present"],
        "dimensions": diff["dimensions"],
        "changed_pixels": diff["mismatched_pixels"],
        "changed_alpha_pixels": diff["alpha_changed_pixels"],
        "semialpha_edge_candidates": diff["semialpha_edge_candidates"],
        "pixel_identical_to_reference": diff["mismatched_pixels"] == 0,
        "original_artist_identity_verified": False,
        "human_originality_approved": False,
        "legal_licence_reviewed": False,
        "owner_visual_review_performed": False,
        "physical_device_qa_passed": False,
        "release_allowed": False,
    }
