"""VUF-M07 view-only event/animation timeline for manual Studio consumers.

Reuses VF-06 AUTHORING_ONLY procedural VFX preset schema and R50 actual Engine
special names. No gameplay event dispatch or board mutations, no asset import,
audio/haptic activation, purchase/save/reward callbacks or self-approval.
Every effect is a deterministic SOURCE candidate awaiting real Unity GUI/replay QA.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Mapping

from factory.visual_director.special_skin_map import (
    PROFILES, SPECIAL_KINDS, pair_key, _key,
)
from factory.vfx_builder.procedural_fx_sheet import _preset

STAGE = "VIEW_ONLY_CANDIDATE_NOT_OWNER_APPROVED"
EVENTS = (
    "ui_open", "ui_close", "tile_spawn", "tile_match",
    "special_trigger", "combo_chain", "obstacle_hit", "booster_activate",
    "level_win", "level_fail", "reward_claim",
    "character_idle", "character_celebrate", "region_reveal",
)
# Deterministic mapping to five existing upstream VF06 authoring presets.
# None deliberately uses existing runtime VufUiTween with no new FX package.
PRESET_FOR_EVENT = {
    "ui_open": None, "ui_close": None,
    "tile_spawn": "SoftDrift", "tile_match": "MatchBurst",
    "special_trigger": "StarSparkle", "combo_chain": "MatchBurst",
    "obstacle_hit": "SoftDrift", "booster_activate": "StarSparkle",
    "level_win": "StarSparkle", "level_fail": "SoftDrift",
    "reward_claim": "StarSparkle",
    "character_idle": "BubbleRise", "character_celebrate": "StarSparkle",
    "region_reveal": "PortalPulse",
}
DURATIONS_MS = {
    "ui_open": 220, "ui_close": 180, "tile_spawn": 320, "tile_match": 420,
    "special_trigger": 650, "combo_chain": 850, "obstacle_hit": 280,
    "booster_activate": 540, "level_win": 1180, "level_fail": 870,
    "reward_claim": 920, "character_idle": 1500,
    "character_celebrate": 1100, "region_reveal": 1250,
}
CHANNELS = {
    "ui_open": "ui", "ui_close": "ui",
    "tile_spawn": "board_visual", "tile_match": "board_visual",
    "special_trigger": "board_visual", "combo_chain": "board_visual",
    "obstacle_hit": "board_visual", "booster_activate": "board_visual",
    "level_win": "results_visual", "level_fail": "results_visual",
    "reward_claim": "rewards_visual",
    "character_idle": "character_visual",
    "character_celebrate": "character_visual",
    "region_reveal": "environment_visual",
}
# Order only determines *view* interruptions; it cannot prioritize game logic.
PRIORITIES = {
    "ui_open": 20, "ui_close": 30, "tile_spawn": 10, "tile_match": 45,
    "special_trigger": 60, "combo_chain": 70, "obstacle_hit": 40,
    "booster_activate": 65, "level_win": 100, "level_fail": 100,
    "reward_claim": 90, "character_idle": 1,
    "character_celebrate": 85, "region_reveal": 75,
}
SPECIAL_NAMES = frozenset(x[0] for x in SPECIAL_KINDS)
FULL_SPEEDS = (0.25, 0.5, 1.0, 2.0)


class TimelineError(ValueError):
    pass


def _verify_params(event: str, special: str | None,
                   second_special: str | None) -> str | None:
    if event not in EVENTS:
        raise TimelineError("unknown view-only presentation event")
    if event in ("special_trigger", "combo_chain"):
        if special not in SPECIAL_NAMES:
            raise TimelineError("special event requires actual Engine enum kind")
        if event == "special_trigger":
            if second_special is not None:
                raise TimelineError("single special cannot name a second kind")
            return _key(special)
        if second_special not in SPECIAL_NAMES:
            raise TimelineError("combo event requires two actual Engine kinds")
        return pair_key(special, second_special)
    if special is not None or second_special is not None:
        raise TimelineError("non-special view event cannot claim Engine combo IDs")
    return None


def build_timeline(profile: str, event: str, *,
                   special: str | None = None,
                   second_special: str | None = None,
                   reduced_motion: bool = False, muted: bool = False,
                   seed: int = 0) -> dict:
    if profile not in PROFILES:
        raise TimelineError("unknown five-title visual namespace")
    if type(seed) is not int or not 0 <= seed <= 65535:
        raise TimelineError("seed must be 0..65535 integer")
    if type(reduced_motion) is not bool or type(muted) is not bool:
        raise TimelineError("motion/mute settings must be explicit bool")
    asset_variant = _verify_params(event, special, second_special)
    preset = PRESET_FOR_EVENT[event]
    upstream_preset_sha = _preset(preset)[1] if preset else None
    duration = 40 if reduced_motion else DURATIONS_MS[event]
    times = [0, duration] if reduced_motion else [
        0, duration // 4, duration // 2, (3 * duration) // 4, duration
    ]
    suffix = event if asset_variant is None else event + "." + asset_variant
    namespace = profile.lower()
    packet = {
        "schema_version": 1,
        "stage": STAGE,
        "profile_id": profile,
        "event_id": event,
        "event_variant": asset_variant,
        "visual_key": namespace + ".anim." + suffix,
        "view_channel": CHANNELS[event],
        "visual_priority_only": PRIORITIES[event],
        "interrupt_policy": "CANCEL_LOWER_PRIORITY_SAME_VIEW_CHANNEL",
        "replay_seed": seed,
        "reduced_motion": reduced_motion,
        "muted": muted,
        "duration_ms": duration,
        "keyframes": [
            {"time_ms": t, "normalized_progress_milli": (t * 1000 // duration),
             "frame_index": i, "screen_effect_only": True}
            for i, t in enumerate(times)
        ],
        "vfx_preset_id": None if reduced_motion else preset,
        "vfx_preset_source_sha256": upstream_preset_sha,
        "reduced_motion_static_fallback": bool(reduced_motion),
        "runtime_tween_primitive": "VufUiTween" if preset is None else None,
        "audio_cue_log_only": None if muted else namespace + ".audio." + event,
        "haptic_cue_log_only": None if muted else namespace + ".haptic." + event,
        "audio_or_haptic_actuated": False,
        "engine_board_mutations": False,
        "reward_or_save_mutations": False,
        "external_event_dispatch": False,
        "owner_art_approved": False,
        "device_audio_haptic_verified": False,
        "release_allowed": False,
    }
    # The signature fingerprints a purely symbolic, side-effect-free replay.
    canonical = json.dumps(packet, sort_keys=True, separators=(",", ":")).encode()
    packet["replay_sha256"] = hashlib.sha256(canonical).hexdigest()
    return packet


def verify_timeline(packet: Mapping) -> None:
    """Recreate canonical packet from verified Engine symbolic enum names."""
    if not isinstance(packet, dict):
        raise TimelineError("candidate timeline must be a plain mapping")
    try:
        event = packet["event_id"]
        variant = packet["event_variant"]
        first = second = None
        if event == "special_trigger":
            first = next((name for name, _ in SPECIAL_KINDS
                          if _key(name) == variant), None)
            if first is None:
                raise TimelineError("unknown actual single Engine enum variant")
        elif event == "combo_chain":
            for a, _ in SPECIAL_KINDS:
                for b, _ in SPECIAL_KINDS:
                    if pair_key(a, b) == variant:
                        first, second = a, b
                        break
                if first is not None:
                    break
            if first is None:
                raise TimelineError("unknown canonical Engine combo pair variant")
        expected = build_timeline(
            packet["profile_id"], event, special=first,
            second_special=second, reduced_motion=packet["reduced_motion"],
            muted=packet["muted"], seed=packet["replay_seed"])
    except (KeyError, TypeError, ValueError) as exc:
        raise TimelineError("invalid/forged candidate packet") from exc
    if packet != expected:
        raise TimelineError("event/frames/effects/approval/replay changed or forged")


def sample_timeline(packet: dict, *, elapsed_ms: int,
                    speed: float = 1.0, interrupted: bool = False) -> dict:
    """Manual Studio stepper, NOT Unity real-time playback or an event callback.

    Derives a frame cursor from the same immutable verified packet, allowing
    0.25x/0.5x/1x/2x scrubbing and interruption simulation without executing
    any effects, sounds, haptics, game-board logic or reward actions.
    """
    verify_timeline(packet)
    if type(elapsed_ms) is not int or not 0 <= elapsed_ms <= 60_000:
        raise TimelineError("elapsed preview time must be integer milliseconds")
    if type(speed) not in (float, int) or speed not in FULL_SPEEDS:
        raise TimelineError("manual preview speed must be 0.25/0.5/1/2")
    if type(interrupted) is not bool:
        raise TimelineError("interrupted must be explicit bool")
    t = min(packet["duration_ms"], round(elapsed_ms * speed))
    ix = max(i for i, frame in enumerate(packet["keyframes"])
             if frame["time_ms"] <= t)
    return {
        "profile_id": packet["profile_id"],
        "event_id": packet["event_id"],
        "replay_sha256": packet["replay_sha256"],
        "elapsed_scaled_ms": t,
        "frame_index": ix,
        "normalized_progress_milli": packet["keyframes"][ix]["normalized_progress_milli"],
        "complete": bool(t == packet["duration_ms"]),
        "view_canceled_only": interrupted,
        "draw_candidate_frame": not interrupted,
        "gameplay_mutations": False,
        "sound_or_haptic_playback": False,
        "save_or_reward_mutations": False,
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--profile", required=True, choices=PROFILES)
    p.add_argument("--event", required=True, choices=EVENTS)
    p.add_argument("--special", choices=sorted(SPECIAL_NAMES))
    p.add_argument("--second-special", choices=sorted(SPECIAL_NAMES))
    p.add_argument("--reduced-motion", action="store_true")
    p.add_argument("--muted", action="store_true")
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args(argv)
    try:
        packet = build_timeline(
            args.profile, args.event, special=args.special,
            second_special=args.second_special,
            reduced_motion=args.reduced_motion,
            muted=args.muted, seed=args.seed)
        verify_timeline(packet)
    except TimelineError as exc:
        p.error(str(exc))
    print(json.dumps(packet, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
