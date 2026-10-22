"""M01 source-only Engine M3P1 typed presentation -> VUF visual preview.

Reuses the existing true M3P1 wire parser, actual Engine 0..6 event-kind
mapping and VUF-M07 verified symbolic animation timeline. This never
registers a runtime event handler, executes gameplay, or invents
unknown special/combo/goal/booster instance bindings.
"""
from __future__ import annotations

import hashlib
import json

from factory.integration.cross_factory_contract import (
    M3P1, EVENT_CUES, PROFILES, CrossFactoryError, read_m3p1
)
from factory.vfx_builder.view_event_timeline import (
    EVENTS, TimelineError, build_timeline, verify_timeline,
)
from factory.visual_director.special_skin_map import (
    SPECIAL_KINDS, pair_key,
)

STAGE = "M01_M3P1_VISUAL_CUES_CANDIDATE_NOT_ACTUAL_EVENT_ORIGIN"
MAX_PREVIEW_EVENTS = 128
SHA256_N = 64
UNBOUND_REASON = {
    0: "ENGINE_SWAP_HAS_NO_VUF_ANIMATION_KEY",
    2: "SPECIAL_VARIANT_IS_NOT_AUTHENTICATED_BY_M3P1",
    3: "SPECIAL_VARIANT_IS_NOT_AUTHENTICATED_BY_M3P1",
    4: "SPECIAL_VARIANT_IS_NOT_AUTHENTICATED_BY_M3P1",
    5: "COMBO_PAIR_IS_NOT_AUTHENTICATED_BY_M3P1",
}
# The official Engine M3P1 wire does not carry final goal, obstacle or
# booster instance assets. Unbound is deliberate, not a synthetic success.
SOURCE_ONLY_FAMILIES = ("goal_progress", "obstacle_hit", "booster_activate")
FLAG_FALSE = (
    "engine_event_origin_authenticated", "engine_sdk_gameplay_mutated",
    "real_goal_or_booster_instance_id_bound", "audio_haptic_actuated",
    "owner_art_approved", "reward_save_changed",
    "physical_device_verified", "release_allowed",
)


class M01EventError(ValueError):
    pass


def build_event_preview(
    wire: bytes, profile: str, *, reduced_motion: bool = False,
    muted: bool = False
) -> dict:
    """Bounded M3P1 source parsing, inert animation preview packet only."""
    if (not isinstance(wire, bytes) or profile not in PROFILES or
            type(reduced_motion) is not bool or type(muted) is not bool):
        raise M01EventError("invalid VUF M01 visual-source arguments")
    try:
        events = read_m3p1(wire, profile)
    except CrossFactoryError as exc:
        raise M01EventError("invalid typed M3P1 checksum/identity/geometry") from exc
    if len(events) > MAX_PREVIEW_EVENTS:
        raise M01EventError("M01 manual preview budget exceeded")
    previews = []
    for row in events:
        kind = row["kind"]
        cue = EVENT_CUES[kind]
        if cue is not None and cue not in EVENTS:
            raise M01EventError("M07 visual cue declared but unavailable")
        # A valid M3P1 checksum is NOT signature of an Engine-derived
        # gameplay event nor is it an authenticated special enum variant.
        if kind in UNBOUND_REASON:
            timeline = None
            reason = UNBOUND_REASON[kind]
        else:
            if cue not in ("tile_match", "tile_spawn"):
                raise M01EventError("unsupported direct visual-only event")
            timeline = build_timeline(
                profile, cue, reduced_motion=reduced_motion,
                muted=muted, seed=0
            )
            verify_timeline(timeline)
            reason = None
        previews.append({
            "sequence": row["sequence"],
            "source_event_id": row["eventId"],
            "source_presentation_key": row["presentationKey"],
            "engine_event_kind_ordinal": kind,
            "engine_view_positions": [list(x) for x in row["positions"]],
            "candidate_vuf_cue": cue,
            "cue_renderable_in_visual_preview": timeline is not None,
            "unbound_reason": reason,
            "view_timeline": timeline,
            "real_gameplay_event_verified": False,
            "actual_engine_instance_id_bound": False,
            "audio_haptic_actuated": False,
        })
    packet = {
        "schema_version": 1,
        "stage": STAGE,
        "profile_id": profile,
        "wire_format": M3P1,
        "source_wire_sha256": hashlib.sha256(wire).hexdigest(),
        "candidate_events": previews,
        "candidate_event_count": len(previews),
        "unbound_events": sum(x["unbound_reason"] is not None for x in previews),
        "no_real_goal_obstacle_booster_instance_mapping": list(SOURCE_ONLY_FAMILIES),
        "reduced_motion": reduced_motion,
        "muted": muted,
        **{key: False for key in FLAG_FALSE},
    }
    data = json.dumps(packet, sort_keys=True, separators=(",", ":")).encode()
    packet["preview_sha256"] = hashlib.sha256(data).hexdigest()
    return packet


def verify_event_preview(packet: dict, wire: bytes) -> None:
    if not isinstance(packet, dict):
        raise M01EventError("candidate preview must be an exact plain mapping")
    try:
        expected = build_event_preview(
            wire, packet["profile_id"],
            reduced_motion=packet["reduced_motion"], muted=packet["muted"])
    except (KeyError, TypeError, ValueError) as exc:
        raise M01EventError("altered candidate metadata") from exc
    if expected != packet:
        raise M01EventError("preview cue, route, timeline or approval forged")


def build_unbound_family_slot(profile: str, family: str) -> dict:
    """Explicit independent goal/obstacle/booster visual source gap."""
    if profile not in PROFILES or family not in SOURCE_ONLY_FAMILIES:
        raise M01EventError("unknown game or unverified Engine visual family")
    return {
        "stage": STAGE,
        "profile_id": profile,
        "family": family,
        "actual_engine_instance_id": None,
        "engine_event_origin_authenticated": False,
        "vuf_visual_slot_key": profile.lower() + ".view." + family,
        "candidate_animation_bindable": False,
        "unbound_reason": "NEEDS_REAL_ENGINE_EVENT_AND_INSTANCE_MAPPING",
        "owner_art_approved": False,
        "release_allowed": False,
    }
