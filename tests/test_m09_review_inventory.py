"""Exact source-pinned M09 diagnostic grid, never a rendered game screen."""
from __future__ import annotations
import unittest
from factory.qa.m09_review_inventory import (
    PROFILES, STATES, LOCALES, DEVICES, EXPECTED,
    ReviewInventoryError, index_to_case, inventory_report,
)


class M09MatrixSourceTests(unittest.TestCase):
    def test_exact_five_by_corals28_by_8_by_3_by_5(self):
        summary = inventory_report()
        self.assertEqual(EXPECTED, 16800)
        self.assertEqual(summary["coverage_cases_not_rendered"], EXPECTED)
        self.assertEqual(summary["cross_title_source_preview_N_A_cases"], 13440)
        self.assertEqual(summary["coral_draft_screen_count"], 28)
        self.assertEqual(len(PROFILES), 5)
        self.assertEqual(len(STATES), 8)
        self.assertEqual(len(LOCALES), 3)
        self.assertEqual(len(DEVICES), 5)

    def test_matches_unity_mixed_radix_order_at_start_and_one_profile_edge(self):
        row = index_to_case(0)
        self.assertEqual((row["profile_id"], row["coral_draft_screen_id"],
                          row["state_mock"], row["locale_mock"]),
                         ("Coral_Rescue", "COR-01", "Ready", "en"))
        self.assertEqual(index_to_case(5)["locale_mock"], "tr")
        self.assertEqual(index_to_case(15)["state_mock"], "Loading")
        self.assertEqual(index_to_case(3360)["profile_id"], "Garage_Legends")
        self.assertEqual(index_to_case(16799)["profile_id"], "Wonder_Pop")
        self.assertEqual(index_to_case(16799)["coral_draft_screen_id"], "COR-28")

    def test_foreign_titles_cannot_approve_corals28_game_screen_contract(self):
        foreign = index_to_case(3360)
        self.assertFalse(foreign["independent_screen_taxonomy_available"])
        self.assertEqual(
            foreign["coverage_status"],
            "N_A_FOREIGN_GAME_USING_CORAL_DRAFT_CONTRACT")
        self.assertFalse(foreign["owner_visual_approved"])
        self.assertFalse(foreign["real_device_gpu_verified"])

    def test_policy_blocked_coral_event_pages_remain_unavailable(self):
        event_screen = index_to_case(12 * 8 * 3 * 5)
        self.assertEqual(event_screen["coral_draft_screen_id"], "COR-13")
        self.assertEqual(event_screen["coverage_status"], "POLICY_OFF_NO_GAME_ACTION")
        self.assertFalse(event_screen["feature_available_in_demo"])
        self.assertFalse(event_screen["release_allowed"])

    def test_boundaries_and_noninteger_indices_fail_closed(self):
        for n in (-1, 16800, 1.5, True, "0", None):
            with self.subTest(index=n), self.assertRaises(ReviewInventoryError):
                index_to_case(n)
        report = inventory_report()
        self.assertEqual(len(report["source_pins"]["coral_schema_sha256"]), 64)
        self.assertFalse(report["owner_art_originality_verified"]
                         if "owner_art_originality_verified" in report else
                         report["human_aesthetic_acceptance"])


if __name__ == "__main__":
    unittest.main()
