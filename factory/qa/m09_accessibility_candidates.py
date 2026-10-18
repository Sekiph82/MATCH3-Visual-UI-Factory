"""M09 candidate accessibility probes: six alpha silhouettes + palette contrast.

Internal reuse: VF04 mathematically authored six shapes and Style Bibles.
Does NOT infer WCAG conformance of actual games/screens/devices, typography
quality, disability accessibility or rights to final illustration sources.
"""
from __future__ import annotations

from factory.image_processor.png_pipeline import decode_png
from factory.visual_director.silhouette_kit import (
    PROFILES, SHAPES, _style, build_theme_kit,
)


def _rgb(color: str):
    if not isinstance(color, str) or len(color) != 7 or color[0] != "#":
        raise ValueError("invalid HTML draft palette")
    return [int(color[p:p + 2], 16) / 255 for p in (1, 3, 5)]


def _luminance(rgb):
    def linear(x):
        return x / 12.92 if x <= .04045 else ((x + .055) / 1.055) ** 2.4
    return sum(v * w for v, w in zip(map(linear, rgb),
                                    (.2126, .7152, .0722)))


def contrast(one: str, other: str) -> float:
    a, b = _luminance(_rgb(one)), _luminance(_rgb(other))
    return (max(a, b) + .05) / (min(a, b) + .05)


def accessibility_candidate(profile: str, side: int = 48) -> dict:
    if profile not in PROFILES or type(side) is not int or not 24 <= side <= 128:
        raise ValueError("invalid title/shape size")
    palette, pinned_sha = _style(profile)
    manifest, images = build_theme_kit(profile, side)
    masks: dict[str, bytes] = {}
    for shape in SHAPES:
        w, h, rgba = decode_png(images[f"tile_{shape}.png"])
        if (w, h) != (side, side):
            raise ValueError("candidate silhouette dimensions changed")
        masks[shape] = bytes(int(a >= 128) for a in rgba[3::4])
    if len({mask for mask in masks.values()}) != len(SHAPES):
        raise ValueError("colour-independent tile silhouettes are not unique")
    smallest = 1000
    for i, first in enumerate(SHAPES):
        for second in SHAPES[i + 1:]:
            a, b = masks[first], masks[second]
            symmetric = sum(x != y for x, y in zip(a, b))
            union = sum(bool(x or y) for x, y in zip(a, b))
            if union == 0:
                raise ValueError("alpha-only blank tile cannot identify shape")
            smallest = min(smallest, symmetric * 1000 // union)
    cta = contrast(palette["cta_label"], palette["cta"])
    text = contrast(palette["text"], palette["background"])
    return {
        "schema_version": 1,
        "stage": "ACCESSIBILITY_CANDIDATE_NOT_DEVICE_OR_OWNER_APPROVED",
        "profile_id": profile,
        "style_sha256": pinned_sha,
        "shape_keys": list(SHAPES),
        "unique_binary_alpha_silhouette_count": len(masks),
        "minimum_pairwise_alpha_dissimilarity_milli": smallest,
        "cta_draft_contrast_ratio": round(cta, 3),
        "background_text_draft_contrast_ratio": round(text, 3),
        "cta_below_4_5_heuristic": cta < 4.5,
        "text_below_4_5_heuristic": text < 4.5,
        "shape_distinguishable_without_hue_candidate": smallest > 0,
        "final_game_font_measured": False,
        "actual_color_vision_testing": False,
        "physical_touch_dp_measured": False,
        "real_world_accessibility_certified": False,
        "source_art_rights_approved": False,
        "release_allowed": False,
    }
