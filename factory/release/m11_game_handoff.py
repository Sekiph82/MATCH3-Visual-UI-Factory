"""M11-004: four exact consumer-ID REVIEW handoff dossiers, not shipping.

G01/G02/G09/G11 are stable handoff target IDs. This repository does not
contain authenticated owner mapping from those IDs to names/profiles; never
invent that mapping. A human game owner must supply an independently proven
mapping, art rights, ABI and real player evidence before game import.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from factory.release.m11_candidate_release import (
    M11ReleaseError, STAGE, _checked_external, verify_release,
)

TARGETS = ("G01", "G02", "G09", "G11")
DOC_STAGE = "M11_FOUR_GAME_HANDOFF_REVIEW_ONLY"


def generate_handoff(release: Path) -> dict:
    info = verify_release(release)
    return {
        "schema_version": 1,
        "stage": DOC_STAGE,
        "source_vuf_candidate_identity_sha256": info["content_identity_sha256"],
        "source_vuf_candidate_profile": info["profile_id"],
        "vuf_candidate_stage": STAGE,
        "game_ids": [{
            "game_id": gid,
            "owner_game_title_mapping": "UNCONFIRMED_NOT_IN_VUF_SOURCE",
            "matching_released_theme_pack": "NOT_PROVIDED",
            "approved_logo_fonts_and_original_art": False,
            "engine_lfx_accepted_abi": False,
            "game_content_import_performed": False,
            "manual_device_and_gui_owner_signoff": False,
            "release_allowed": False,
        } for gid in TARGETS],
        "no_cost_boundary": {
            "requires_paid_cloud_service": False,
            "creates_game_server": False,
            "downloads_third_party_assets": False,
            "alters_existing_project": False,
        },
        "read_only_consumer_quickstart": [
            "Verify exact M11 candidate SHA via m11_candidate_release audit",
            "Verify actual consumer ID/profile mapping from owner source",
            "Approve separate original art, fonts and legal rights records",
            "Confirm released Engine M12 and LevelFactory final replay ABI",
            "In Unity use M11 Release Candidate and Rights Audit read-only tool",
            "Import only TEST_ONLY copies with existing M08 importer to Editor",
            "Run original title PlayMode/device/full GUI/real gameplay suites",
            "Accept title release only in its own original authority tracker",
        ],
        "owner_approval": False,
        "independent_audit_signed": False,
        "actual_player_build_verified": False,
        "release_allowed": False,
    }


def validate_handoff(handoff: dict) -> None:
    if (not isinstance(handoff, dict) or
            handoff.get("schema_version") != 1 or
            handoff.get("stage") != DOC_STAGE or
            not isinstance(handoff.get("game_ids"), list) or
            [row.get("game_id") for row in handoff["game_ids"]] != list(TARGETS)):
        raise M11ReleaseError("handoff identity list changed")
    for key in ("owner_approval", "independent_audit_signed",
                "actual_player_build_verified", "release_allowed"):
        if handoff.get(key) is not False:
            raise M11ReleaseError("forged owner/handoff signoff")
    for row in handoff["game_ids"]:
        if (row.get("owner_game_title_mapping") !=
                "UNCONFIRMED_NOT_IN_VUF_SOURCE" or
                row.get("matching_released_theme_pack") != "NOT_PROVIDED"):
            raise M11ReleaseError("unsupported cross-project title assignment")
        for key in ("approved_logo_fonts_and_original_art",
                    "engine_lfx_accepted_abi",
                    "game_content_import_performed",
                    "manual_device_and_gui_owner_signoff", "release_allowed"):
            if row.get(key) is not False:
                raise M11ReleaseError("game-specific acceptance forged")


def save_new_external_handoff(release: Path, new_json: Path) -> dict:
    data = generate_handoff(release)
    validate_handoff(data)
    output = Path(new_json)
    if (output.suffix != ".json" or
            output.name.startswith(".") or not output.is_absolute()):
        raise M11ReleaseError("must choose NEW named external .json")
    _checked_external(output, exists=False)
    payload = (json.dumps(data, sort_keys=True, indent=2) + "\n").encode("utf-8")
    with output.open("xb") as f:
        f.write(payload)
        f.flush()
        os.fsync(f.fileno())
    return data


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--review-candidate", type=Path, required=True)
    p.add_argument("--new-handoff-json", type=Path, required=True)
    args = p.parse_args(argv)
    try:
        result = save_new_external_handoff(
            args.review_candidate, args.new_handoff_json)
    except (ValueError, OSError) as exc:
        p.exit(2, "M11_HANDOFF_REJECTED: " + str(exc) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
