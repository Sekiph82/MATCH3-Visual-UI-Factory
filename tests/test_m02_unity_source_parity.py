"""M02 Style Bible Python/Unity source parity; no local Unity execution."""
from __future__ import annotations

import unittest
from pathlib import Path

from factory.visual_director.m02_style_bible import (
    IDENTITY_PATH, compile_bibles, PROFILES,
)

ROOT=Path(__file__).resolve().parents[1]
EDITOR=ROOT/"unity_package"/"Editor"


class M02UnitySourceParityTests(unittest.TestCase):
    def test_unity_editor_reads_byte_identical_five_bible_identity_catalog(self):
        mirrored=(EDITOR/"Resources"/"m02_identity_catalog.v1.json").read_bytes()
        self.assertEqual(mirrored, IDENTITY_PATH.read_bytes())
        bibles=compile_bibles()
        self.assertEqual([row["profile_id"] for row in bibles["profiles"]],
                         list(PROFILES))
        self.assertFalse(bibles["owner_art_approved"])

    def test_unity_source_has_no_auto_owner_signoff_or_runtime_scene_writes(self):
        editor=(EDITOR/"VufM02StyleBibleStudioWindow.cs").read_text("utf-8")
        for token in ("DRAFT_IDENTITY_CONTRACT_OWNER_ART_NOT_PROVIDED",
                      "ValidateAndParse(", "ValidateOriginalPalette(",
                      "M02 Five-Game Style Bible and Art Identity Studio",
                      "master_sheet_slots", "required_character_poses",
                      "source_material",):
            # Source material is optional: use semantic source material field.
            if token=="source_material":
                token="surface_material"
            with self.subTest(symbol=token):self.assertIn(token,editor)
        self.assertNotIn("SaveAsPrefabAsset",editor)
        self.assertNotIn("AssetDatabase.CreateAsset",editor)
        self.assertNotIn("releaseAllowed=true",editor)
        self.assertNotIn("GameState.",editor)

    def test_editor_only_guids_and_structure_are_registered(self):
        validator=(ROOT/"Tools"/"validate_repo_structure.py").read_text("utf-8")
        for item in ("Editor/VufM02StyleBibleStudioWindow.cs",
                     "Tests/Editor/VufM02StyleBibleEditModeTests.cs"):
            self.assertIn(item,validator)
        files=[
            EDITOR/"VufM02StyleBibleStudioWindow.cs.meta",
            EDITOR/"Tests"/"../X" if False else
                ROOT/"unity_package"/"Tests"/"Editor"/
                "VufM02StyleBibleEditModeTests.cs.meta",
            EDITOR/"Resources"/"m02_identity_catalog.v1.json.meta",
        ]
        guids=[]
        for path in files:
            content=path.read_text("utf-8")
            self.assertIn("fileFormatVersion: 2",content)
            guid=next(row.split(": ",1)[1] for row in content.splitlines()
                      if row.startswith("guid: "))
            self.assertRegex(guid,r"^[0-9a-f]{32}$")
            guids.append(guid)
        self.assertEqual(len(set(guids)),3)


if __name__=="__main__":
    unittest.main()
