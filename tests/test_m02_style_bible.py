"""M02 real source Style Bible contract: independent mechanical tests only."""
from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from factory.visual_director.m02_style_bible import (
    STYLE_PATH, IDENTITY_PATH, PROFILES, StyleBibleError,
    compile_bibles, render_json, write_new_bibles,
)


class StyleBibleSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.style = STYLE_PATH.read_bytes()
        cls.identity = IDENTITY_PATH.read_bytes()
        cls.bible = compile_bibles()

    def mutated(self, modify, *, style=False):
        source = self.style if style else self.identity
        data = json.loads(source)
        modify(data)
        encoded = json.dumps(data, ensure_ascii=False).encode("utf-8")
        return compile_bibles(style_source=encoded) if style else compile_bibles(
            identity_source=encoded)

    def test_five_distinct_original_source_identity_briefs_without_approved_rights(self):
        profiles = self.bible["profiles"]
        self.assertEqual([x["profile_id"] for x in profiles], list(PROFILES))
        self.assertEqual(len({x["original_brief"]["bible_title"] for x in profiles}), 5)
        self.assertEqual(len({x["original_brief"]["surface_material"] for x in profiles}),5)
        self.assertFalse(self.bible["release_allowed"])
        for p in profiles:
            self.assertFalse(p["actual_original_art_received"])
            self.assertFalse(p["owner_design_approved"])
            self.assertFalse(p["font_license_verified"])
            self.assertFalse(p["release_allowed"])
            self.assertGreaterEqual(len(p["original_brief"]["original_reference_requirements"]),6)
            self.assertEqual(len(p["original_brief"]["required_character_poses"]),5)

    def test_all_five_draft_palette_contrasts_reach_wcag_aa_body(self):
        for p in self.bible["profiles"]:
            for name,ratio in p["contrasts_wcag"].items():
                with self.subTest(profile=p["profile_id"],pair=name):
                    self.assertGreaterEqual(ratio,4.5)

    def test_four_safe_area_modes_and_accessible_touch_design_tokens(self):
        c = self.bible["common"]
        self.assertEqual(c["min_touch_dp"],44)
        self.assertEqual([x["id"] for x in c["screen_modes"]],
                         ["compact_phone","tall_phone","large_phone","portrait_tablet"])
        self.assertEqual([x["width_dp"] for x in c["screen_modes"]],[320,393,430,768])
        self.assertEqual(c["grid"]["columns_phone"],4)
        self.assertEqual(c["grid"]["columns_tablet"],8)
        self.assertIn("EN/TR", " ".join(c["responsive_rules"]))

    def test_source_digest_and_canonical_json_are_reproducible(self):
        first=render_json(compile_bibles())
        second=render_json(compile_bibles())
        self.assertEqual(first,second)
        decoded=json.loads(first)
        self.assertEqual(decoded["source_draft_style_sha256"],
                         hashlib.sha256(self.style).hexdigest())
        self.assertEqual(decoded["source_identity_sha256"],
                         hashlib.sha256(self.identity).hexdigest())

    def test_missing_duplicate_or_unknown_five_theme_profiles_rejected(self):
        for mutation in (
            lambda d: d["profiles"].pop(),
            lambda d: d["profiles"].__setitem__(1,copy.deepcopy(d["profiles"][0])),
            lambda d: d["profiles"][0].__setitem__("id","Unapproved_Game"),
        ):
            with self.subTest(which=str(mutation)), self.assertRaises(StyleBibleError):
                self.mutated(mutation)

    def test_self_approved_original_art_or_font_evidence_refused(self):
        for field in self.bible["common"]["owner_auth"]:
            with self.subTest(field=field), self.assertRaises(StyleBibleError):
                self.mutated(lambda d:d["common"]["owner_auth"].__setitem__(field,True))
        with self.assertRaises(StyleBibleError):
            self.mutated(lambda d:d["profiles"][0].__setitem__("right_to_use","APPROVED"))

    def test_unsafe_font_touch_and_accessibility_tokens_rejected(self):
        with self.assertRaises(StyleBibleError):
            self.mutated(lambda d:d["common"].__setitem__("min_touch_dp",24))
        with self.assertRaises(StyleBibleError):
            self.mutated(lambda d:d["common"].__setitem__("font_license_status","OWNED"))
        with self.assertRaises(StyleBibleError):
            self.mutated(lambda d:d["common"]["screen_modes"][0].__setitem__("width_dp",100))
        with self.assertRaises(StyleBibleError):
            self.mutated(lambda d:d["common"].__setitem__("min_body_contrast_ratio",2.0))

    def test_child_safety_specific_rules_must_remain(self):
        def changed(d):
            d["profiles"][4]["forbidden_visual_patterns"]=[]
        with self.assertRaises(StyleBibleError):
            self.mutated(changed)
        with self.assertRaises(StyleBibleError):
            self.mutated(lambda d:d["profiles"][4].__setitem__("right_to_use","OWNER_APPROVED"))
        with self.assertRaises(StyleBibleError):
            self.mutated(lambda d:d["profiles"][4]["ui_components"].pop())

    def test_draft_palette_contrast_mutation_is_fatal(self):
        with self.assertRaises(StyleBibleError):
            self.mutated(lambda d:d["profiles"][0]["palettes"].__setitem__(
                "cta_label","#FFE47A"),style=True)

    def test_creates_only_six_files_in_new_external_owner_folder(self):
        with tempfile.TemporaryDirectory(prefix="vuf_m02_source_test_") as tmp:
            new=Path(tmp)/"review"
            files=write_new_bibles(new)
            self.assertEqual(len(files),6)
            self.assertFalse(json.loads((new/files[0]).read_text())["release_allowed"])
            for name in files:
                self.assertTrue((new/name).is_file())
            receipt=json.loads((new/"SOURCE_BIBLES_SHA256.json").read_text())
            self.assertEqual(len(receipt["files"]),5)
            for name, digest in receipt["files"].items():
                self.assertEqual(hashlib.sha256((new/name).read_bytes()).hexdigest(),
                                 digest)
            with self.assertRaises(StyleBibleError):
                write_new_bibles(new)

    def test_duplicate_json_key_cannot_shadow_art_owner_authority(self):
        data=self.identity.replace(b'"schema_version": 1',
                                    b'"schema_version": 1')
        # Inject into the top-level common dict, never relying on JSON's last key wins.
        bad=data.replace(b'"min_touch_dp": 44',
                         b'"min_touch_dp": 44, "min_touch_dp": 24')
        with self.assertRaises(StyleBibleError):
            compile_bibles(identity_source=bad)

    def test_source_runtime_styles_remain_unmodified(self):
        result=self.mutated(lambda d:d["profiles"][0].__setitem__("bible_title","Changed"))
        self.assertNotEqual(result["source_identity_sha256"],
                            self.bible["source_identity_sha256"])
        self.assertEqual(result["source_draft_style_sha256"],
                         self.bible["source_draft_style_sha256"])


if __name__=="__main__":
    unittest.main()
