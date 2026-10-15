import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "factory" / "validators"))
from validate_design import DesignError, validate_profiles, validate_experiences, parse


class DesignContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.styles = parse(ROOT / "factory/visual_director/style_profiles.v1.json")
        cls.screens = parse(ROOT / "schemas/coral-experiences.v1.json")

    def test_valid_five_draft_styles(self):
        self.assertEqual(validate_profiles(self.styles)["profile_count"], 5)

    def test_valid_28_coral_experiences(self):
        self.assertEqual(validate_experiences(self.screens)["coral_experience_count"], 28)

    def test_unknown_game_rejected(self):
        x = copy.deepcopy(self.styles)
        x["profiles"][0]["id"] = "Unknown"
        with self.assertRaises(DesignError):
            validate_profiles(x)

    def test_self_approved_style_rejected(self):
        x = copy.deepcopy(self.styles)
        x["status"] = "APPROVED"
        with self.assertRaises(DesignError):
            validate_profiles(x)

    def test_duplicate_tile_shapes_rejected(self):
        x = copy.deepcopy(self.styles)
        x["common"]["tile_silhouettes"][-1] = "circle"
        with self.assertRaises(DesignError):
            validate_profiles(x)

    def test_low_contrast_rejected(self):
        x = copy.deepcopy(self.styles)
        x["profiles"][0]["palettes"]["cta_label"] = "#FFE47A"
        with self.assertRaises(DesignError):
            validate_profiles(x)

    def test_reduced_motion_mandatory(self):
        x = copy.deepcopy(self.styles)
        x["common"]["reduced_motion"] = False
        with self.assertRaises(DesignError):
            validate_profiles(x)

    def test_child_public_social_blocked(self):
        x = copy.deepcopy(self.styles)
        x["profiles"][-1]["restrictions"].remove("no_child_public_social")
        with self.assertRaises(DesignError):
            validate_profiles(x)

    def test_missing_home_rejected(self):
        x = copy.deepcopy(self.screens)
        x["screens"][-2]["key"] = "wrong"
        with self.assertRaises(DesignError):
            validate_experiences(x)

    def test_unbuilt_screens_cannot_claim_availability(self):
        x = copy.deepcopy(self.screens)
        x["screens"][0]["available_in_demo"] = True
        with self.assertRaises(DesignError):
            validate_experiences(x)

    def test_corrupt_id_and_duplicate_screen_rejected(self):
        x = copy.deepcopy(self.screens)
        x["screens"][0]["id"] = "COR-12"
        with self.assertRaises(DesignError):
            validate_experiences(x)
        x = copy.deepcopy(self.screens)
        x["screens"][0]["key"] = x["screens"][1]["key"]
        with self.assertRaises(DesignError):
            validate_experiences(x)


if __name__ == "__main__":
    unittest.main()
