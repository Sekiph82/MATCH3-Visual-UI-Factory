"""VF-01 / VF-09 draft contract validator, standard library only."""
import json
import re
from pathlib import Path

PROFILES = ("Coral_Rescue", "Garage_Legends", "Dino_Islands",
            "The_Fractured_Realms", "Wonder_Pop")
PALETTE_KEYS = {"background", "surface", "accent", "cta", "cta_label", "text"}
HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")
SLUG = re.compile(r"^[a-z][a-z0-9_]*$")


class DesignError(ValueError):
    pass


def parse(path: Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def contrast_ratio(foreground: str, background: str) -> float:
    def luminance(value):
        components = [int(value[n:n + 2], 16) / 255 for n in (1, 3, 5)]
        channels = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
                    for c in components]
        return .2126 * channels[0] + .7152 * channels[1] + .0722 * channels[2]
    a, b = sorted([luminance(foreground), luminance(background)], reverse=True)
    return (a + .05) / (b + .05)


def validate_profiles(doc):
    if not isinstance(doc, dict) or doc.get("schema_version") != 1:
        raise DesignError("invalid design schema")
    if doc.get("status") != "DRAFT_NOT_OWNER_APPROVED":
        raise DesignError("style bible cannot self-approve")
    common = doc.get("common")
    if not isinstance(common, dict):
        raise DesignError("missing common design rules")
    if common.get("minimum_touch_target_dp", 0) < 44 or not common.get("reduced_motion"):
        raise DesignError("touch / reduced-motion rules invalid")
    shapes = common.get("tile_silhouettes")
    if not isinstance(shapes, list) or len(shapes) != 6 or len(set(shapes)) != 6:
        raise DesignError("need six distinct non-color tile shapes")
    if not {"en", "tr"}.issubset(set(common.get("locales", []))):
        raise DesignError("must include TR/EN locale")
    profiles = doc.get("profiles")
    if not isinstance(profiles, list) or len(profiles) != 5:
        raise DesignError("need exactly five profiles")
    if tuple(sorted(p.get("id") for p in profiles)) != tuple(sorted(PROFILES)):
        raise DesignError("profile ID mismatch")
    for p in profiles:
        palette = p.get("palettes")
        if not isinstance(palette, dict) or set(palette) != PALETTE_KEYS:
            raise DesignError("incomplete palette: " + p["id"])
        if any(not isinstance(value, str) or not HEX.fullmatch(value)
               for value in palette.values()):
            raise DesignError("palette hex invalid")
        if contrast_ratio(palette["cta_label"], palette["cta"]) < 4.5:
            raise DesignError("CTA label contrast below 4.5:1")
        if contrast_ratio(palette["text"], palette["surface"]) < 4.5:
            raise DesignError("surface text contrast below 4.5:1")
        for field in ("art_direction", "silhouette_language", "motion"):
            if not isinstance(p.get(field), str) or not p[field].strip():
                raise DesignError("missing design rule " + field)
        for field in ("mascot_roles", "environment_layers"):
            if not isinstance(p.get(field), list) or not p[field]:
                raise DesignError("missing visual roles/layers")
    wonder = next(p for p in profiles if p["id"] == "Wonder_Pop")
    if "no_child_public_social" not in wonder.get("restrictions", []):
        raise DesignError("Wonder Pop cannot expose child social")
    return {"profile_count": len(profiles), "silhouette_count": len(shapes)}


def validate_experiences(doc):
    if not isinstance(doc, dict) or doc.get("schema_version") != 1:
        raise DesignError("invalid screen inventory schema")
    if doc.get("status") != "CONTRACT_DRAFT_NOT_IMPLEMENTED" or doc.get("profile_id") != "Coral_Rescue":
        raise DesignError("screen inventory must remain unimplemented draft")
    screens = doc.get("screens")
    if not isinstance(screens, list) or len(screens) != 28:
        raise DesignError("Coral needs 28 experience IDs")
    if [s.get("id") for s in screens] != ["COR-" + str(i).zfill(2) for i in range(1, 29)]:
        raise DesignError("screens must have stable ordered IDs")
    keys = [s.get("key") for s in screens]
    if len(set(keys)) != 28 or any(not SLUG.fullmatch(key) for key in keys):
        raise DesignError("duplicate/invalid screen keys")
    if keys[-2:] != ["home", "gameplay_hud"]:
        raise DesignError("Home and Gameplay/HUD required")
    for s in screens:
        if s.get("available_in_demo") is not False:
            raise DesignError("unbuilt feature cannot be marked available")
        if s.get("runtime_ui_required") is not True or not s.get("feature_gate"):
            raise DesignError("layered runtime and policy gate required")
    return {"coral_experience_count": len(screens)}


def main():
    root = Path(__file__).resolve().parents[2]
    print(validate_profiles(parse(root / "factory/visual_director/style_profiles.v1.json")))
    print(validate_experiences(parse(root / "schemas/coral-experiences.v1.json")))


if __name__ == "__main__":
    main()
