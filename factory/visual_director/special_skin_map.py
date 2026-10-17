"""VUF R50 / M05-002: deterministic, view-only Engine special skin matrix.

Pin inspected READ-ONLY Engine SpecialEffectContracts.cs blob:
5ad6e1dcd50d707614ecf258207c2f09e3538a3e at Engine repository
Sekiph82/MATCH3_ENGINE. The enum ordinals below are its ACTUAL contract,
not invented visual effects. No match logic is implemented in the VUF.

Downstream compatibility MUST revalidate blob and Engine/LFX final SHA
before accepting an asset package. Output is symbolic candidate metadata
and not actual production artwork, gameplay events or monetization.
"""
from __future__ import annotations

import argparse
import itertools
import json
import re
from pathlib import Path

ENGINE_SOURCE = "Packages/com.match3.engine/Runtime/SpecialEffectContracts.cs"
ENGINE_BLOB = "5ad6e1dcd50d707614ecf258207c2f09e3538a3e"
ENGINE_REPOSITORY = "Sekiph82/MATCH3_ENGINE"
ENGINE_HEAD_AT_INSPECTION = "098e6342df9a97c04382926087efffe2f1f8bf91"
PROFILES = (
    "Coral_Rescue", "Garage_Legends", "Dino_Islands",
    "The_Fractured_Realms", "Wonder_Pop",
)
# Exact upstream C# enum name and ordinal; Targeted is optional missile.
SPECIAL_KINDS = (
    ("HorizontalLine", 0),
    ("VerticalLine", 1),
    ("Area", 2),
    ("Color", 3),
    ("Targeted", 4),
)
PROTOTYPE_STAGE = "CANDIDATE_SYMBOLIC_NOT_OWNER_APPROVED"


class SkinMapError(ValueError):
    pass


def _key(kind: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", kind).lower()


def pair_key(first: str, second: str) -> str:
    actual = {name: index for index, (name, _) in enumerate(SPECIAL_KINDS)}
    if first not in actual or second not in actual:
        raise SkinMapError("unknown actual Engine special kind")
    a, b = sorted((first, second), key=actual.__getitem__)
    return _key(a) + "__" + _key(b)


def build_skin_contract(profile: str) -> dict:
    if profile not in PROFILES:
        raise SkinMapError("unknown profile")
    namespace = profile.lower()
    singles = []
    for name, ordinal in SPECIAL_KINDS:
        key = _key(name)
        singles.append({
            "engine_enum": "SpecialActivationKind",
            "engine_enum_name": name,
            "engine_enum_ordinal": ordinal,
            "sprite_key": namespace + ".special." + key,
            "vfx_key": namespace + ".vfx.special." + key,
            "optional_engine_capability": (
                "targeted_missile" if name == "Targeted" else None),
            "candidate_only": True,
        })
    combos = []
    for (first, first_num), (second, second_num) in itertools.combinations_with_replacement(
            SPECIAL_KINDS, 2):
        key = pair_key(first, second)
        combos.append({
            "engine_pair": [first, second],
            "engine_pair_ordinals": [first_num, second_num],
            "sprite_key": namespace + ".combo." + key,
            "vfx_key": namespace + ".vfx.combo." + key,
            "optional_engine_capabilities": (
                ["targeted_missile"] if "Targeted" in (first, second) else []),
            "candidate_only": True,
        })
    return {
        "schema_version": 1,
        "stage": PROTOTYPE_STAGE,
        "profile_id": profile,
        "engine_repository": ENGINE_REPOSITORY,
        "engine_source": ENGINE_SOURCE,
        "engine_source_blob_sha": ENGINE_BLOB,
        "engine_head_at_inspection": ENGINE_HEAD_AT_INSPECTION,
        "verified_current_engine_release": False,
        "engine_mutations_allowed": False,
        "gameplay_logic_embedded": False,
        "owner_approved": False,
        "single_specials": singles,
        "unordered_special_pairs": combos,
    }


def verify_skin_contract(doc: dict) -> None:
    if not isinstance(doc, dict) or doc.get("schema_version") != 1:
        raise SkinMapError("invalid contract schema")
    profile = doc.get("profile_id")
    expected = build_skin_contract(profile)
    if doc != expected:
        raise SkinMapError("special-skin map changed, missing, duplicated or forged")
    if len(doc["single_specials"]) != 5 or len(doc["unordered_special_pairs"]) != 15:
        raise SkinMapError("incomplete Engine special cross-product")
    if len({x["sprite_key"] for x in doc["single_specials"] +
            doc["unordered_special_pairs"]}) != 20:
        raise SkinMapError("duplicate sprite binding key")


def build_five_profile_contracts() -> dict:
    maps = [build_skin_contract(p) for p in PROFILES]
    for mapping in maps:
        verify_skin_contract(mapping)
    return {
        "schema_version": 1,
        "stage": PROTOTYPE_STAGE,
        "contracts": maps,
        "engine_final_compatibility_verified": False,
        "owner_art_approval": False,
        "release_allowed": False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=PROFILES)
    args = parser.parse_args(argv)
    doc = build_skin_contract(args.profile) if args.profile else build_five_profile_contracts()
    print(json.dumps(doc, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
