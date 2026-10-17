"""R50 visual-only special contracts from pinned real Engine C# enum."""
import json
import unittest
from contextlib import redirect_stdout
from io import StringIO

from factory.visual_director.special_skin_map import (
    ENGINE_BLOB, PROFILES, SPECIAL_KINDS, SkinMapError,
    build_skin_contract, build_five_profile_contracts,
    pair_key, verify_skin_contract, main,
)


class SpecialSkinMapTests(unittest.TestCase):
    def test_exact_upstream_enum_ordinals(self):
        self.assertEqual(SPECIAL_KINDS, (
            ("HorizontalLine", 0), ("VerticalLine", 1),
            ("Area", 2), ("Color", 3), ("Targeted", 4)))
        self.assertEqual(len(ENGINE_BLOB), 40)

    def test_all_five_complete_5_plus_15_view_only_contracts(self):
        collection = build_five_profile_contracts()
        self.assertEqual(len(collection["contracts"]), 5)
        self.assertFalse(collection["release_allowed"])
        self.assertEqual(set(PROFILES),
                         {m["profile_id"] for m in collection["contracts"]})
        for m in collection["contracts"]:
            verify_skin_contract(m)
            self.assertEqual(len(m["single_specials"]), 5)
            self.assertEqual(len(m["unordered_special_pairs"]), 15)
            self.assertEqual(len({x["sprite_key"] for x in
                                  m["single_specials"] +
                                  m["unordered_special_pairs"]}), 20)
            self.assertFalse(m["gameplay_logic_embedded"])
            self.assertFalse(m["engine_mutations_allowed"])

    def test_pair_orientation_same_contract(self):
        self.assertEqual(pair_key("Color", "HorizontalLine"),
                         pair_key("HorizontalLine", "Color"))
        self.assertEqual(pair_key("Targeted", "Area"), "area__targeted")

    def test_real_optional_targeted_capability_explicit(self):
        m = build_skin_contract("Wonder_Pop")
        targeted = [x for x in m["single_specials"]
                    if x["engine_enum_name"] == "Targeted"][0]
        self.assertEqual(targeted["optional_engine_capability"],
                         "targeted_missile")
        for combo in m["unordered_special_pairs"]:
            contains = "Targeted" in combo["engine_pair"]
            self.assertEqual(bool(combo["optional_engine_capabilities"]), contains)

    def test_no_cross_theme_leaks(self):
        keys = [
            {x["sprite_key"] for x in build_skin_contract(p)["single_specials"]}
            for p in PROFILES]
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                self.assertFalse(keys[i] & keys[j])

    def test_unknown_engine_kind_and_profile_are_rejected(self):
        with self.assertRaises(SkinMapError):
            pair_key("Missile", "Color")  # real enum uses Targeted
        with self.assertRaises(SkinMapError):
            build_skin_contract("Unknown_Game")

    def test_missing_forged_or_altered_binding_refused(self):
        candidate = build_skin_contract("Coral_Rescue")
        candidate["single_specials"][0]["engine_enum_ordinal"] = 55
        with self.assertRaises(SkinMapError):
            verify_skin_contract(candidate)
        candidate = build_skin_contract("Coral_Rescue")
        candidate["stage"] = "APPROVED"
        with self.assertRaises(SkinMapError):
            verify_skin_contract(candidate)
        candidate = build_skin_contract("Coral_Rescue")
        candidate["unordered_special_pairs"].pop()
        with self.assertRaises(SkinMapError):
            verify_skin_contract(candidate)

    def test_cli_is_stdout_only_and_still_candidate(self):
        out = StringIO()
        with redirect_stdout(out):
            self.assertEqual(main(["--profile", "Garage_Legends"]), 0)
        candidate = json.loads(out.getvalue())
        self.assertEqual(candidate["profile_id"], "Garage_Legends")
        self.assertFalse(candidate["verified_current_engine_release"])
        verify_skin_contract(candidate)


if __name__ == "__main__":
    unittest.main()
