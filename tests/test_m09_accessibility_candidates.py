"""M09 source palette + silhouette morphology, NOT WCAG/device certification."""
import unittest
from factory.qa.m09_accessibility_candidates import (
    accessibility_candidate, contrast,
)
from factory.visual_director.silhouette_kit import PROFILES


class M09AccessibilitySourceTests(unittest.TestCase):
    def test_all_five_draft_styles_have_unique_color_independent_shape_masks(self):
        for profile in PROFILES:
            with self.subTest(profile=profile):
                audit = accessibility_candidate(profile)
                self.assertEqual(audit["unique_binary_alpha_silhouette_count"], 6)
                self.assertGreater(audit["minimum_pairwise_alpha_dissimilarity_milli"], 0)
                self.assertTrue(audit["shape_distinguishable_without_hue_candidate"])
                self.assertFalse(audit["real_world_accessibility_certified"])
                self.assertFalse(audit["source_art_rights_approved"])

    def test_contrast_helper_is_bounded_not_production_font_certification(self):
        self.assertAlmostEqual(contrast("#FFFFFF", "#000000"), 21, places=4)
        self.assertAlmostEqual(contrast("#000000", "#000000"), 1, places=4)
        self.assertGreaterEqual(contrast("#FFFFFF", "#777777"), 1)
        c = accessibility_candidate("Coral_Rescue")
        self.assertGreaterEqual(c["cta_draft_contrast_ratio"], 1)
        self.assertFalse(c["final_game_font_measured"])
        self.assertFalse(c["physical_touch_dp_measured"])
        self.assertFalse(c["actual_color_vision_testing"])

    def test_unknown_style_and_bad_size_are_rejected(self):
        for prof, size in (("MadeUp", 48), ("Coral_Rescue", 12),
                           ("Coral_Rescue", True)):
            with self.subTest(profile=prof, size=size), self.assertRaises(ValueError):
                accessibility_candidate(prof, size)


if __name__ == "__main__":
    unittest.main()
