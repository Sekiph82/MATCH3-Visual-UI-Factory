"""Three-repo exact wire compatibility tests. Sources under test are
contract fixtures, not a fabricated engine-authoritative gameplay WIN.
"""
from __future__ import annotations
import base64
import hashlib
import json
import unittest

from factory.integration.cross_factory_contract import (
    CrossFactoryError, EVENT_CUES, bind_readonly, read_lfxv1, read_m3p1,
)


def sample_level():
    obj = {
        "schemaVersion": 1, "stage": "LFXV1_VALIDATED_DRAFT_NOT_ENGINE_REPLAY",
        "gameProfileId": "Coral_Rescue", "levelId": "level.fixture-r01",
        "width": 2, "height": 2, "layers": 1, "moveBudget": 17,
        "seed": 731, "sourceDraftSha256": "a"*64,
        "sourceLevelFactoryGitSha": "UNPINNED",
        "cells": [
            {"row": r, "column": c, "layer": 0, "active": (r,c)!=(1,0),
             "locked": False,
             "contentId": {
                 (0,0):"gem.猫", (0,1):'gem."quoted"', (1,1):"gem.green"
             }.get((r,c)),
             "obstacleId": None,"specialId": None,
             "obstacleDurability":0,"lockDurability":0}
            for r in range(2) for c in range(2)
        ],
        "goals":[{"goalId":"goal.primary","targetId":"sample.score",
                  "targetCount":321}],
        "actualSdkWinVerified":False, "engineM24ReleaseAccepted":False,
        "realPlayableLevel":False, "assetRightsApproved":False,
        "releaseAllowed":False,
    }
    return obj


def parse_lfx(obj):
    return read_lfxv1(json.dumps(obj,ensure_ascii=False).encode())


def wire(events):
    lines = ["M3P1", "Coral_Rescue", str(len(events))]
    for i, (kind, pos) in enumerate(events, 1):
        b64 = lambda value: base64.b64encode(value.encode()).decode()
        lines.append(f"{i}|{b64('eng-'+str(i))}|{kind}|"
                     f"{b64('actual.content.猫')}|1|{pos}")
    body = ("\n".join(lines)+"\n").encode()
    return body+hashlib.sha256(body).hexdigest().encode()


class ThreeFactoryInteropTests(unittest.TestCase):
    def test_actual_lfxv1_contract_unicode_hole_and_goal_shape(self):
        result = parse_lfx(sample_level())
        self.assertEqual(result["cells"][0]["contentId"],"gem.猫")
        self.assertEqual(result["cells"][1]["contentId"],'gem."quoted"')
        self.assertFalse(result["cells"][2]["active"])
        self.assertEqual(result["goals"][0]["targetCount"],321)
        self.assertFalse(result["actualSdkWinVerified"])

    def test_duplicated_or_outside_lfx_positions_rejected(self):
        obj=sample_level()
        obj["cells"][3]["row"]=0
        with self.assertRaises(CrossFactoryError):parse_lfx(obj)
        obj=sample_level();obj["cells"][0]["layer"]=3
        with self.assertRaises(CrossFactoryError):parse_lfx(obj)

    def test_lfx_holes_cannot_carry_lock_obstacle_or_assets(self):
        for field,value in (("locked",True),("contentId","gem.bad"),
                            ("obstacleDurability",4),("specialId","line")):
            obj=sample_level();obj["cells"][2][field]=value
            with self.subTest(field=field),self.assertRaises(CrossFactoryError):
                parse_lfx(obj)

    def test_lfx_prototype_never_promotes_engine_rights_or_prod(self):
        for key in ("realPlayableLevel","releaseAllowed",
                    "engineM24ReleaseAccepted","actualSdkWinVerified",
                    "assetRightsApproved"):
            obj=sample_level();obj[key]=True
            with self.subTest(key=key),self.assertRaises(CrossFactoryError):
                parse_lfx(obj)

    def test_real_presentation_wire_event_mapping_from_engine_kind_ordinals(self):
        level=parse_lfx(sample_level())
        receipt=wire([(0,"0:0:0"),(1,"0:0:1"),(5,"0:1:1"),(6,"0:0:0")])
        events=read_m3p1(receipt,"Coral_Rescue")
        self.assertEqual([e["vufCue"] for e in events],
                         [None,"tile_match","combo_chain","tile_spawn"])
        self.assertEqual(events[1]["positions"],[(0,0,1)])
        binding=bind_readonly(level,events,
                              source_sha=hashlib.sha256(receipt).hexdigest())
        self.assertTrue(binding["actualLfxDraftGeometry"])
        self.assertFalse(binding["authoritativeEventOriginAuthenticated"])
        self.assertFalse(binding["realGameplayReplayValidated"])
        self.assertEqual(binding["unboundSwapEvents"],1)
        self.assertFalse(binding["releaseAllowed"])

    def test_m3p1_checksum_and_cross_title_mismatches_rejected(self):
        data=wire([(1,"0:0:0")])
        with self.assertRaises(CrossFactoryError):
            read_m3p1(data,"Wonder_Pop")
        data=bytearray(data)
        data[-1]=ord("0") if data[-1]!=ord("0") else ord("1")
        with self.assertRaises(CrossFactoryError):
            read_m3p1(bytes(data),"Coral_Rescue")

    def test_real_event_cells_must_fit_actual_lfx_geometry(self):
        level=parse_lfx(sample_level())
        events=read_m3p1(wire([(1,"0:8:0")]),"Coral_Rescue")
        with self.assertRaises(CrossFactoryError):
            bind_readonly(level,events,source_sha="e"*64)

    def test_duplicate_engine_coordinates_and_wrong_sequence_fail(self):
        with self.assertRaises(CrossFactoryError):
            read_m3p1(wire([(1,"0:0:0,0:0:0")]),"Coral_Rescue")
        data=wire([(1,"0:0:0")])
        data=data.replace(b"1|",b"2|",1)
        with self.assertRaises(CrossFactoryError):
            read_m3p1(data,"Coral_Rescue")

    def test_source_hash_approval_is_not_an_origin_signature(self):
        level=parse_lfx(sample_level())
        events=read_m3p1(wire([(1,"0:0:0")]),"Coral_Rescue")
        result=bind_readonly(level,events,source_sha="a"*64)
        self.assertFalse(result["engineSdkSettledSnapshotsChecked"])
        self.assertFalse(result["levelFactoryEngineM24Approved"])
        self.assertFalse(result["actualVisualAssetsLoaded"])
        self.assertFalse(result["ownerArtApproved"])

    def test_untrusted_json_overrides_duplicates_or_bools_are_rejected(self):
        obj=sample_level()
        encoded=json.dumps(obj).encode()
        with self.assertRaises(CrossFactoryError):
            read_lfxv1(encoded[:-1]+b',"releaseAllowed":true}')
        obj["width"]=True
        with self.assertRaises(CrossFactoryError):
            parse_lfx(obj)


if __name__ == "__main__":
    unittest.main()
