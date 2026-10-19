"""Read-only three-factory REAL SOURCE interoperability check.

Consume an LFXV1 JSON produced from real strict LevelDraftJson.Parse,
the corresponding canonical LevelDraftJson source bytes and an M3P1
receipt produced from actual Engine PresentationEvent objects.
Optionally revalidate an M08 VUF image pack. NO matching or scoring
simulation, NO WIN/replay or artwork/player approval.

Usage:
 python -B -m Tools.verify_three_factory_handoff
   --lfx-canonical <canonical.json> --lfx-view <LFXV1.json>
   --engine-events <M3P1.txt> [--vuf-test-pack <external_dir>]
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

from factory.asset_packaging.candidate_pack import ROOT as VUF_REPO_ROOT
from factory.integration.three_factory_visual_plan import compile_view_plan

from factory.integration.cross_factory_contract import (
    CrossFactoryError, bind_readonly, read_lfxv1, read_m3p1,
)


def evaluate(lfx_canonical: bytes, lfx_visual: bytes, m3p1: bytes,
             optional_vuf_pack: Path | None = None) -> dict:
    level = read_lfxv1(lfx_visual)
    canonical_sha = hashlib.sha256(lfx_canonical).hexdigest()
    if canonical_sha != level["sourceDraftSha256"]:
        raise CrossFactoryError(
            "actual LFX canonical LevelDraft SHA != visual handoff receipt")
    events = read_m3p1(m3p1, level["gameProfileId"])
    source_sha = hashlib.sha256(m3p1).hexdigest()
    bound = bind_readonly(level, events, source_sha=source_sha)
    pack_info = None
    if optional_vuf_pack is not None:
        from factory.asset_packaging.verify_offline_bundle import verify_exported_pack
        pack_info = verify_exported_pack(optional_vuf_pack)
        if (pack_info.get("stage") != "TEST_ONLY" or
                pack_info.get("profile_id") != level["gameProfileId"] or
                pack_info.get("release_allowed") is not False):
            raise CrossFactoryError("VUF artwork pack profile or TEST_ONLY stage mismatch")
    return {
        **bound,
        "canonicalLevelDraftSourceSha256Verified": True,
        "levelFactoryVisualEnvelopeSha256":
            hashlib.sha256(lfx_visual).hexdigest(),
        "vufCandidatePackChecked": pack_info is not None,
        "vufCandidatePackStage": (None if pack_info is None else pack_info["stage"]),
        "engineSourceAuthenticated": False,
        "engineSettledReplayAuthenticated": False,
        "actualGameScoreOrWinVerified": False,
        "realVufAnimationAssetPlayed": False,
        "engineReleaseAccepted": False,
        "levelFactoryProductionReleaseAccepted": False,
        "ownerLicensedArtAccepted": False,
        "releaseAllowed": False,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lfx-canonical", type=Path, required=True)
    parser.add_argument("--lfx-view", type=Path, required=True)
    parser.add_argument("--engine-events", type=Path, required=True)
    parser.add_argument("--vuf-test-pack", type=Path)
    parser.add_argument("--explicit-test-art-map", type=Path,
                        help="existing UTF8 JSON LFX content ID -> M08 asset_id mapping")
    parser.add_argument("--new-view-plan", type=Path,
                        help="NEW external non-shipping visual plan JSON; create only")
    args = parser.parse_args(argv)
    try:
        paths=(args.lfx_canonical,args.lfx_view,args.engine_events)
        if any(not p.is_file() or p.is_symlink() or
               p.stat().st_size > 2_000_000 for p in paths):
            raise CrossFactoryError("missing/linked/oversized source file")
        inputs=tuple(p.read_bytes() for p in paths)
        result=evaluate(*inputs,optional_vuf_pack=args.vuf_test_pack)
        if args.explicit_test_art_map is not None or args.new_view_plan is not None:
            if args.new_view_plan is None:
                raise CrossFactoryError(
                    "explicit mapping requires an explicit NEW external output")
            mapping={}
            if args.explicit_test_art_map is not None:
                artfile=args.explicit_test_art_map
                if (not artfile.is_file() or artfile.is_symlink() or
                        artfile.stat().st_size>64*1024):
                    raise CrossFactoryError("missing/linked/oversized art mapping")
                def unique(items):
                    data={}
                    for key,value in items:
                        if key in data:
                            raise CrossFactoryError("duplicate art binding ID")
                        data[key]=value
                    return data
                mapping=json.loads(artfile.read_text("utf-8"),
                                   object_pairs_hook=unique)
            plan=compile_view_plan(canonical_lfx=inputs[0],lfxv1=inputs[1],
                                   m3p1=inputs[2],
                                   vuf_pack=args.vuf_test_pack,
                                   explicit_content_map=mapping)
            output=args.new_view_plan
            if (not output.is_absolute() or output.suffix.lower()!=".json" or
                    output.exists() or output.is_symlink() or
                    not output.parent.is_dir() or
                    output.resolve(strict=False).is_relative_to(VUF_REPO_ROOT)):
                raise CrossFactoryError("plan must be NEW external JSON")
            for directory in (output.parent,*output.parent.parents):
                if directory.is_symlink() or (
                        hasattr(directory,"is_junction") and directory.is_junction()):
                    raise CrossFactoryError("linked plan folder rejected")
            serialized=(json.dumps(plan,indent=2,sort_keys=True,
                                   ensure_ascii=False)+"\\n").encode("utf-8")
            with output.open("xb") as file:
                file.write(serialized)
            result["newUnapprovedVisualPlan"]=str(output)
            result["explicitTestArtBindingCount"]=plan["explicitArtBindingCount"]
    except (CrossFactoryError, ValueError, OSError) as exc:
        parser.exit(2, "THREE_FACTORY_INTEGRATION_REJECTED: "+str(exc)+"\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
