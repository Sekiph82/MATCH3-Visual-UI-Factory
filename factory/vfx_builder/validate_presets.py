"""VF-06 cheap, offline contract validation. Not a real Unity performance test."""
from __future__ import annotations

import json
import math
from pathlib import Path

EXPECTED = ("BubbleRise", "MatchBurst", "StarSparkle", "SoftDrift", "PortalPulse")
FALLBACKS = {"static_bubble", "single_flash", "static_star", "static_ring", "none"}


class VfxContractError(ValueError):
    pass


def _numeric(value, lower, upper, description):
    if (isinstance(value, bool) or not isinstance(value, (int, float))
            or not math.isfinite(value) or not lower <= value <= upper):
        raise VfxContractError(description + " is invalid")


def validate_vfx(doc):
    if not isinstance(doc, dict) or doc.get("schema_version") != 1:
        raise VfxContractError("unknown VFX schema")
    if doc.get("stage") != "AUTHORING_ONLY" or doc.get("engine_side_effects_allowed") is not False:
        raise VfxContractError("VFX must never grant gameplay/reward changes")
    if doc.get("profile_scope") != "ANY_OF_FIVE" or doc.get("max_particle_count") != 160:
        raise VfxContractError("profile or particle budget mismatch")
    presets = doc.get("presets")
    if not isinstance(presets, list) or [x.get("id") for x in presets] != list(EXPECTED):
        raise VfxContractError("missing/duplicate/reordered preset")
    for item in presets:
        if item.get("state") != "CANDIDATE_NOT_OWNER_APPROVED":
            raise VfxContractError("VFX may not mark itself approved")
        _numeric(item.get("count"), 1, 160, "count")
        if int(item["count"]) != item["count"]:
            raise VfxContractError("fractional particle count")
        _numeric(item.get("lifetime_seconds"), .1, 2.5, "lifetime")
        _numeric(item.get("start_speed"), .1, 8.0, "speed")
        _numeric(item.get("start_size"), .03, .5, "size")
        if item.get("reduced_motion_fallback") not in FALLBACKS:
            raise VfxContractError("missing reduced-motion fallback")
        if item.get("events") != ["VIEW_ONLY"]:
            raise VfxContractError("VFX events require strict view-only treatment")
    return {"preset_count": len(presets), "stage": "AUTHORING_ONLY"}


def main():
    path = Path(__file__).with_name("presets.v1.json")
    print(validate_vfx(json.loads(path.read_text(encoding="utf-8"))))


if __name__ == "__main__":
    main()
