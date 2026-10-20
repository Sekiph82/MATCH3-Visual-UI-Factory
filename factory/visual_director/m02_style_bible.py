"""M02: source-pinned, human-unapproved premium identity/style bible compiler.

Reads existing draft palette source and distinct five original creative-brief
identities. All creative family/reference slots are requirements, NOT actual
commissioned/licensed art. No file write unless explicitly exporting to a
NEW external directory; no providers/credentials/game/runtime effects.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STYLE_PATH = ROOT / "factory/visual_director/style_profiles.v1.json"
IDENTITY_PATH = ROOT / "factory/visual_director/m02_identity_catalog.v1.json"
PROFILES = ("Coral_Rescue", "Garage_Legends", "Dino_Islands",
            "The_Fractured_Realms", "Wonder_Pop")
HEX = re.compile(r"#[A-F0-9]{6}\Z")
TOKEN = re.compile(r"[a-z][a-z0-9_]{2,80}\Z")
REQUIRED_PALETTE = ("background", "surface", "accent", "cta",
                    "cta_label", "text")
REQUIRED_COMPONENTS = ("primary_cta", "secondary_cta", "card", "modal",
                       "badge", "counter", "tab", "progress",
                       "disabled_reason", "pending_state")
POSES = ("idle", "greet", "celebrate", "concerned", "action")
SHAPES = ("circle", "triangle", "diamond", "star", "crescent", "shield")


class StyleBibleError(ValueError):
    pass


def _pairs(items):
    data = {}
    for key, value in items:
        if key in data:
            raise StyleBibleError("duplicate JSON key")
        data[key] = value
    return data


def _read(doc: bytes) -> dict:
    if not isinstance(doc, bytes) or len(doc) == 0 or len(doc) > 128 * 1024:
        raise StyleBibleError("empty/oversized creative source")
    try:
        value = json.loads(doc.decode("utf-8", "strict"),
                           object_pairs_hook=_pairs,
                           parse_constant=lambda _: (_ for _ in ()).throw(
                               StyleBibleError("nonfinite JSON")))
    except (UnicodeError, ValueError) as exc:
        raise StyleBibleError("invalid creative JSON") from exc
    if not isinstance(value, dict):
        raise StyleBibleError("creative source must be an object")
    return value


def _check_keys(obj, allowed):
    if not isinstance(obj, dict) or set(obj) != set(allowed):
        raise StyleBibleError("identity fields do not match versioned contract")


def _ratio(a: str, b: str) -> float:
    def luminance(h):
        vals = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        vals = [x / 12.92 if x <= .04045 else ((x + .055) / 1.055)**2.4
                for x in vals]
        return .2126 * vals[0] + .7152 * vals[1] + .0722 * vals[2]
    x, y = sorted((luminance(a), luminance(b)), reverse=True)
    return (x + .05) / (y + .05)


def _check_tokens(common: dict):
    keys = {"schema_version", "stage", "reference_style_document",
            "font_license_status", "min_touch_dp", "min_body_contrast_ratio",
            "min_large_text_contrast_ratio", "typography_dp", "spacing_dp",
            "corner_radius_dp", "grid", "screen_modes", "responsive_rules",
            "owner_auth"}
    _check_keys(common, keys)
    if (type(common["schema_version"]) is not int or common["schema_version"] != 1
            or common["stage"] != "DRAFT_IDENTITY_CONTRACT_OWNER_ART_NOT_PROVIDED"
            or common["reference_style_document"] !=
            "factory/visual_director/style_profiles.v1.json"
            or common["font_license_status"] !=
            "SYSTEM_FALLBACK_ONLY_UNTIL_CREATOR_PROOF"
            or type(common["min_touch_dp"]) is not int or
            common["min_touch_dp"] < 44 or common["min_touch_dp"] > 72
            or common["min_body_contrast_ratio"] < 4.5
            or common["min_large_text_contrast_ratio"] < 3):
        raise StyleBibleError("design accessibility, stage or font provenance spoof")
    _check_keys(common["typography_dp"],
                ("hero", "page_title", "section", "body", "caption", "button"))
    sizes = common["typography_dp"]
    if any(type(s) is not int or not 12 <= s <= 72 for s in sizes.values()):
        raise StyleBibleError("invalid typography scale")
    if sizes["hero"] < sizes["page_title"] or sizes["body"] < 16:
        raise StyleBibleError("unreadable responsive typography")
    spacing = common["spacing_dp"]
    if (not isinstance(spacing, list) or
            spacing != [4, 8, 12, 16, 24, 32, 48]):
        raise StyleBibleError("unexpected spacing scale")
    _check_keys(common["corner_radius_dp"], ("card", "modal", "button", "pill"))
    if any(type(x) is not int or x < 4 or x > 999
           for x in common["corner_radius_dp"].values()):
        raise StyleBibleError("unsafe component geometry")
    _check_keys(common["grid"],
                ("columns_phone", "columns_tablet", "gutter_dp",
                 "outer_margin_phone_dp", "outer_margin_tablet_dp"))
    grid = common["grid"]
    if (grid["columns_phone"] != 4 or grid["columns_tablet"] != 8 or
            grid["gutter_dp"] < 12 or grid["outer_margin_phone_dp"] < 12 or
            grid["outer_margin_tablet_dp"] < 24):
        raise StyleBibleError("invalid safe-area grid")
    modes = common["screen_modes"]
    if (not isinstance(modes, list) or
            [x.get("id") for x in modes] != [
                "compact_phone", "tall_phone", "large_phone", "portrait_tablet"]):
        raise StyleBibleError("four source device layouts required")
    for mode in modes:
        _check_keys(mode, ("id", "width_dp", "height_dp",
                           "min_safe_top_dp", "min_safe_bottom_dp"))
        for field in ("width_dp", "height_dp", "min_safe_top_dp",
                      "min_safe_bottom_dp"):
            if type(mode[field]) is not int or mode[field] < 0:
                raise StyleBibleError("invalid device safe area")
        if (mode["width_dp"] < 320 or mode["height_dp"] < 568 or
                mode["min_safe_top_dp"] + mode["min_safe_bottom_dp"] >=
                mode["height_dp"]):
            raise StyleBibleError("unsafe device layout")
        inner = mode["width_dp"] - 2 * (grid["outer_margin_tablet_dp"]
                    if mode["id"] == "portrait_tablet" else
                    grid["outer_margin_phone_dp"])
        cols = 8 if mode["id"] == "portrait_tablet" else 4
        cell = (inner - (cols - 1) * grid["gutter_dp"]) / cols
        if cell < 44:
            raise StyleBibleError("component grid below minimum 44 dp touch")
    if (not isinstance(common["responsive_rules"], list) or
            len(common["responsive_rules"]) < 6 or
            any(not isinstance(x, str) or len(x) < 12
                for x in common["responsive_rules"])):
        raise StyleBibleError("missing accessibility design rules")
    owners = common["owner_auth"]
    _check_keys(owners, ("all_approved", "original_art_received",
                        "font_rights_verified", "device_visual_qa_verified",
                        "engine_lfx_gameplay_verified", "production_release_allowed"))
    if any(value is not False for value in owners.values()):
        raise StyleBibleError("self-approved art/device/rights forbidden")


def _check_identity(row):
    fields = {"id", "bible_title", "creative_direction", "surface_material",
              "mascot_role", "world_restoration_identity",
              "particle_language", "lighting_finish",
              "symbol_silhouettes", "original_reference_requirements",
              "required_character_poses", "master_sheet_slots",
              "forbidden_visual_patterns", "ui_components", "right_to_use"}
    _check_keys(row, fields)
    if row["id"] not in PROFILES:
        raise StyleBibleError("unsupported creative game profile")
    for k in ("bible_title", "creative_direction", "surface_material",
              "mascot_role", "world_restoration_identity",
              "particle_language", "lighting_finish"):
        if not isinstance(row[k], str) or not 3 <= len(row[k]) <= 300:
            raise StyleBibleError("missing original creative brief")
    if (not isinstance(row["symbol_silhouettes"], list) or
            len(row["symbol_silhouettes"]) != 5 or
            len(set(row["symbol_silhouettes"])) != 5 or
            any(not TOKEN.fullmatch(x) for x in row["symbol_silhouettes"])):
        raise StyleBibleError("missing five non-hue game icon identities")
    refs = row["original_reference_requirements"]
    if (not isinstance(refs, list) or len(refs) < 6 or len(set(refs)) != len(refs)
            or any(not TOKEN.fullmatch(x) for x in refs)):
        raise StyleBibleError("incomplete owner original reference families")
    if row["required_character_poses"] != list(POSES):
        raise StyleBibleError("source artist 5-pose identity contract changed")
    slots = row["master_sheet_slots"]
    if (not isinstance(slots, list) or len(slots) < 5 or
            len(slots) != len(set(slots)) or
            any(not TOKEN.fullmatch(x) for x in slots)):
        raise StyleBibleError("original owner art master sheet slots absent")
    if (not isinstance(row["forbidden_visual_patterns"], list) or
            len(row["forbidden_visual_patterns"]) != 2 or
            any(not isinstance(x, str) or len(x) < 30
                for x in row["forbidden_visual_patterns"])):
        raise StyleBibleError("theme specificity and restrictions required")
    if row["ui_components"] != list(REQUIRED_COMPONENTS):
        raise StyleBibleError("theme would silently alter semantic UI components")
    if row["right_to_use"] != "NO_OWNER_ORIGINAL_ASSET_OR_FONT_LICENCE_EVIDENCE":
        raise StyleBibleError("false owner art rights")


def compile_bibles(style_source: bytes | None = None,
                   identity_source: bytes | None = None) -> dict:
    if style_source is None:
        style_source = STYLE_PATH.read_bytes()
    if identity_source is None:
        identity_source = IDENTITY_PATH.read_bytes()
    styles = _read(style_source)
    identities = _read(identity_source)
    _check_keys(styles, ("schema_version", "status", "common", "profiles"))
    if (styles["schema_version"] != 1 or type(styles["schema_version"]) is not int or
            styles["status"] != "DRAFT_NOT_OWNER_APPROVED" or
            styles["common"].get("minimum_touch_target_dp", 0) < 44 or
            styles["common"].get("tile_silhouettes") != list(SHAPES) or
            styles["common"].get("reduced_motion") is not True or
            styles["common"].get("no_flattened_interactive_ui") is not True):
        raise StyleBibleError("old source style authority or accessible silhouettes changed")
    _check_keys(identities, ("common", "profiles"))
    common = identities["common"]
    _check_tokens(common)
    style_rows = styles["profiles"]
    id_rows = identities["profiles"]
    if (not isinstance(style_rows, list) or not isinstance(id_rows, list) or
            [x.get("id") for x in style_rows] != list(PROFILES) or
            [x.get("id") for x in id_rows] != list(PROFILES)):
        raise StyleBibleError("missing, repeated or reordered five-game style profiles")
    result = []
    for style, identity in zip(style_rows, id_rows):
        _check_identity(identity)
        palette = style.get("palettes")
        if (not isinstance(palette, dict) or
                set(palette) != set(REQUIRED_PALETTE) or
                any(not isinstance(v, str) or not HEX.fullmatch(v)
                    for v in palette.values())):
            raise StyleBibleError("invalid inherited actual draft palette")
        contrasts = {
            "body_surface": round(_ratio(palette["text"], palette["surface"]), 3),
            "cta_label": round(_ratio(palette["cta_label"], palette["cta"]), 3),
            "text_background": round(_ratio(palette["text"], palette["background"]), 3),
        }
        if min(contrasts.values()) < common["min_body_contrast_ratio"]:
            raise StyleBibleError("theme fails minimum body/CTA contrast")
        if (not isinstance(style.get("mascot_roles"), list) or
                len(style["mascot_roles"]) < 1 or
                not isinstance(style.get("environment_layers"), list) or
                len(style["environment_layers"]) < 3 or
                not isinstance(style.get("art_direction"), str)):
            raise StyleBibleError("draft source lacks environmental or character art direction")
        if identity["id"] == "Wonder_Pop":
            restrictions = set(style.get("restrictions", []))
            if restrictions != {"no_child_public_social", "no_premium_pressure",
                                "no_fake_urgency"}:
                raise StyleBibleError("Wonder Pop family-safety owner policy changed")
        result.append({
            "profile_id": identity["id"],
            "title": style["title"],
            "palette": palette,
            "contrasts_wcag": contrasts,
            "source_art_direction": style["art_direction"],
            "environment_layers": style["environment_layers"],
            "source_mascot_roles": style["mascot_roles"],
            "original_brief": identity,
            "actual_original_art_received": False,
            "owner_design_approved": False,
            "font_license_verified": False,
            "release_allowed": False,
        })
    return {
        "schema_version": 1,
        "stage": "SOURCE_STYLE_BIBLES_REVIEW_ONLY",
        "source_draft_style_sha256": hashlib.sha256(style_source).hexdigest(),
        "source_identity_sha256": hashlib.sha256(identity_source).hexdigest(),
        "common": common,
        "profiles": result,
        "owner_art_approved": False,
        "real_unity_gui_approved": False,
        "actual_physical_device_approved": False,
        "release_allowed": False,
    }


def render_json(output: dict) -> bytes:
    return (json.dumps(output, sort_keys=True, indent=2,
                       ensure_ascii=False) + "\n").encode("utf-8")


def write_new_bibles(new_external_folder: Path) -> tuple[str, ...]:
    """Create ONLY new external folder and five profile documents + receipt."""
    from factory.visual_director.character_pose_review import _is_link
    folder = Path(new_external_folder)
    if not folder.is_absolute() or folder.exists() or folder.is_symlink():
        raise StyleBibleError("owner must choose an absolute NEW directory")
    parent = folder.parent
    if (not parent.is_dir() or any(_is_link(x) for x in (parent, *parent.parents)) or
            folder.resolve(strict=False).is_relative_to(ROOT)):
        raise StyleBibleError("no linked/project/repo output allowed")
    bible = compile_bibles()
    items = [(p["profile_id"] + "_SOURCE_STYLE_BIBLE.json", render_json({
        "schema_version": 1,
        "stage": "SOURCE_STYLE_BIBLES_REVIEW_ONLY",
        "source_draft_style_sha256": bible["source_draft_style_sha256"],
        "source_identity_sha256": bible["source_identity_sha256"],
        "common": bible["common"],
        "profile": p,
        "owner_art_approved": False,
        "release_allowed": False,
    })) for p in bible["profiles"]]
    receipt = {name: hashlib.sha256(data).hexdigest() for name, data in items}
    items.append(("SOURCE_BIBLES_SHA256.json", render_json({
        "stage": "OWNER_SOURCE_REVIEW_NOT_PRODUCTION",
        "files": receipt, "release_allowed": False,
    })))
    folder.mkdir(mode=0o700)
    for name, data in items:
        # Never overwrite even if a concurrent owner file appears.
        with (folder / name).open("xb") as stream:
            stream.write(data)
    return tuple(name for name, _ in items)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--new-external-folder", type=Path)
    args = parser.parse_args(argv)
    if args.new_external_folder is None:
        print(render_json(compile_bibles()).decode("utf-8"))
    else:
        print(json.dumps({
            "stage": "SOURCE_STYLE_BIBLES_REVIEW_ONLY",
            "created": write_new_bibles(args.new_external_folder),
            "owner_art_approved": False, "release_allowed": False,
        }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
