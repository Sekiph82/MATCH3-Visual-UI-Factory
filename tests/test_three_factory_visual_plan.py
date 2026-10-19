"""Real three-factory contracts -> review-only VUF art/timeline/source plan."""
from __future__ import annotations

import base64
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from factory.asset_packaging.candidate_pack import export_pack
from factory.integration.cross_factory_contract import CrossFactoryError
from factory.integration.three_factory_visual_plan import compile_view_plan


def fixture():
    canonical = b'{"canonical":"LFX draft external bytes, not gameplay"}'
    value = {
        "schemaVersion":1, "stage":"LFXV1_VALIDATED_DRAFT_NOT_ENGINE_REPLAY",
        "gameProfileId":"Coral_Rescue","levelId":"draft.source.test",
        "width":2,"height":1,"layers":1,"moveBudget":9,"seed":731,
        "sourceDraftSha256":hashlib.sha256(canonical).hexdigest(),
        "sourceLevelFactoryGitSha":"UNPINNED",
        "cells":[
            dict(row=0,column=0,layer=0,active=True,locked=False,
                 contentId="gem.猫",obstacleId=None,specialId=None,
                 obstacleDurability=0,lockDurability=0),
            dict(row=0,column=1,layer=0,active=True,locked=False,
                 contentId="gem.blue",obstacleId="rock.one",specialId=None,
                 obstacleDurability=2,lockDurability=0),
        ],
        "goals":[dict(goalId="match",targetId="gem.blue",targetCount=4)],
        "actualSdkWinVerified":False,"engineM24ReleaseAccepted":False,
        "realPlayableLevel":False,"assetRightsApproved":False,
        "releaseAllowed":False,
    }
    return canonical,json.dumps(value,ensure_ascii=False).encode()


def wire():
    b64=lambda s:base64.b64encode(s.encode()).decode()
    body=("M3P1\nCoral_Rescue\n2\n" +
          f"1|{b64('evt.a')}|1|{b64('tile.gem.猫')}|1|0:0:0\n" +
          f"2|{b64('evt.b')}|0|{b64('tile.gem.blue')}|0|0:0:1\n").encode()
    return body+hashlib.sha256(body).hexdigest().encode()


class ThreeFactoryVisualPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory(prefix="vuf_cross_factory_plan_")
        cls.folder=Path(cls.tmp.name)/"pack"
        export_pack("Coral_Rescue",cls.folder)
        manifest=json.loads((cls.folder/"visual_manifest.json").read_text())
        cls.asset=next(a for a in manifest["assets"]
                       if a["path"].startswith("sprites/"))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def _go(self,pack=None,mapping=None):
        original,lfx=fixture()
        return compile_view_plan(canonical_lfx=original,lfxv1=lfx,
                                 m3p1=wire(),vuf_pack=pack,
                                 explicit_content_map=mapping)

    def test_real_source_coordinates_and_engine_presentation_no_replay_claim(self):
        result=self._go()
        self.assertEqual(result["width"],2)
        self.assertEqual(result["initialDraftCells"][0]["contentId"],"gem.猫")
        self.assertEqual(result["initialDraftCells"][1]["obstacleDurability"],2)
        self.assertEqual([e["viewOnlyCue"] for e in result["viewTimeline"]],
                         ["tile_match",None])
        self.assertFalse(result["engineFinalSettledReplayVerified"])
        self.assertFalse(result["actualMoveOutcomeOrWinVerified"])
        self.assertFalse(result["releaseAllowed"])

    def test_full_sha_verified_m08_source_pack_requires_explicit_real_cell_binding(self):
        result=self._go(self.folder,{"gem.猫":self.asset["asset_id"]})
        self.assertTrue(result["vufPackShaVerified"])
        self.assertEqual(result["explicitArtBindingCount"],1)
        asset=result["initialDraftCells"][0]["selectedCandidateVisuals"]["contentId"]
        self.assertEqual(asset["assetSha256"],self.asset["sha256"])
        self.assertFalse(asset["ownerLicensed"])
        self.assertFalse(result["actualVisualFxPlayed"])

    def test_missing_pack_cannot_invent_a_synthetic_sprite_source(self):
        with self.assertRaises(CrossFactoryError):
            self._go(None,{"gem.猫":"Coral_Rescue.sample.tile_blue"})
        with self.assertRaises(CrossFactoryError):
            self._go(self.folder,{"invented.source":self.asset["asset_id"]})
        with self.assertRaises(CrossFactoryError):
            self._go(self.folder,{"gem.猫":"Dino_Islands.sample.tile_x"})

    def test_vuf_candidate_draft_mathematical_placeholder_never_grants_rights(self):
        data=self._go(self.folder)
        self.assertEqual(data["explicitArtBindingCount"],0)
        self.assertFalse(data["licensedOriginalArtworkApproved"])
        self.assertFalse(data["ownerAestheticApproved"])
        self.assertFalse(data["engineFinalSettledReplayVerified"])
        self.assertFalse(data["sourceAuthenticationIndependentlyProven"])

    def test_lfx_canonical_changed_blocks_even_with_valid_engine_sha_and_art(self):
        _,level=fixture()
        with self.assertRaises(CrossFactoryError):
            compile_view_plan(canonical_lfx=b"changed",lfxv1=level,
                              m3p1=wire(),vuf_pack=self.folder)

    def test_plan_bytes_are_deterministic_without_actual_gameplay_mutation(self):
        x=self._go(self.folder,{"gem.猫":self.asset["asset_id"]})
        y=self._go(self.folder,{"gem.猫":self.asset["asset_id"]})
        self.assertEqual(json.dumps(x,sort_keys=True),
                         json.dumps(y,sort_keys=True))
        self.assertEqual(x["draftGoals"][0]["targetCount"],4)
        self.assertFalse(x["realSourceContract"]["realGameplayReplayValidated"])


if __name__ == "__main__":
    unittest.main()
