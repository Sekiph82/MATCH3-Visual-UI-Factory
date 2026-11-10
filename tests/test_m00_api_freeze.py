"""
VUF-M00-001 | Engine M09 and LFX M08 API freeze tests.

Authoring: 2026-11-10 by Visual Factory specialist.
Tests exact SHA pins, enum counts, key set membership, and legal
restriction presence. No cross-repo writes; read-only source inspection.
"""
import unittest

from factory.integration.m00_api_freeze import (
    FREEZE,
    ENGINE_UI_SURFACE_COUNT,
    ENGINE_UI_ACTION_COUNT,
    ENGINE_PLAYER_STATE_COUNT,
    LFX_DRAFT_ROOT_KEY_COUNT,
    LFX_CELL_KEY_COUNT,
    LFX_GOAL_KEY_COUNT,
    ENGINE_M09_COMMIT_SHA,
    LFX_M08_COMMIT_SHA,
    assert_invariants,
)


class M00ApiFreezeTests(unittest.TestCase):

    def test_assert_invariants_pass(self) -> None:
        """assert_invariants() must pass with current constants."""
        assert_invariants()  # raises on failure

    def test_engine_m09_sha_is_40_hex(self) -> None:
        sha = FREEZE.engine_m09_sha
        self.assertEqual(len(sha), 40, "Engine M09 SHA must be 40 hex characters.")
        self.assertTrue(all(c in "0123456789abcdef" for c in sha), "Engine M09 SHA must be lowercase hex.")

    def test_lfx_m08_sha_is_40_hex(self) -> None:
        sha = FREEZE.lfx_m08_sha
        self.assertEqual(len(sha), 40, "LFX M08 SHA must be 40 hex characters.")
        self.assertTrue(all(c in "0123456789abcdef" for c in sha), "LFX M08 SHA must be lowercase hex.")

    def test_engine_m09_sha_exact_value(self) -> None:
        self.assertEqual(FREEZE.engine_m09_sha, ENGINE_M09_COMMIT_SHA)
        self.assertEqual(FREEZE.engine_m09_sha, "9af6e16eafd2dc6b3d764a53aee2ff1e15c21a7c")

    def test_lfx_m08_sha_exact_value(self) -> None:
        self.assertEqual(FREEZE.lfx_m08_sha, LFX_M08_COMMIT_SHA)
        self.assertEqual(FREEZE.lfx_m08_sha, "d8d0b37ce71c4e2c0bdb72f9ed1d2a48068281c3")

    def test_ui_surface_kind_count_is_17(self) -> None:
        self.assertEqual(len(FREEZE.engine_ui_surfaces), ENGINE_UI_SURFACE_COUNT)
        self.assertEqual(ENGINE_UI_SURFACE_COUNT, 17)

    def test_ui_surface_kind_no_duplicates(self) -> None:
        self.assertEqual(len(set(FREEZE.engine_ui_surfaces)), len(FREEZE.engine_ui_surfaces))

    def test_ui_surface_kind_exact_members(self) -> None:
        expected = {
            "Home", "WorldMap", "Hud", "Results", "Pause", "Settings",
            "Shop", "DailyRewards", "Tasks", "Fail", "Life", "Booster",
            "Collection", "Achievements", "Store", "Account", "Consent",
        }
        self.assertEqual(set(FREEZE.engine_ui_surfaces), expected)

    def test_ui_action_kind_count_is_4(self) -> None:
        self.assertEqual(len(FREEZE.engine_ui_actions), ENGINE_UI_ACTION_COUNT)
        self.assertEqual(ENGINE_UI_ACTION_COUNT, 4)

    def test_ui_action_kind_exact_members(self) -> None:
        self.assertEqual(set(FREEZE.engine_ui_actions), {"Navigate", "Command", "Back", "Close"})

    def test_player_surface_state_kind_count_is_8(self) -> None:
        self.assertEqual(len(FREEZE.engine_player_states), ENGINE_PLAYER_STATE_COUNT)
        self.assertEqual(ENGINE_PLAYER_STATE_COUNT, 8)

    def test_player_surface_state_kind_exact_members(self) -> None:
        expected = {"Ready", "Loading", "Offline", "Error", "Owned", "Claimed", "Disabled", "Pending"}
        self.assertEqual(set(FREEZE.engine_player_states), expected)

    def test_lfx_draft_root_key_count_is_31(self) -> None:
        self.assertEqual(len(FREEZE.lfx_draft_root_keys), LFX_DRAFT_ROOT_KEY_COUNT)
        self.assertEqual(LFX_DRAFT_ROOT_KEY_COUNT, 31)

    def test_lfx_draft_root_keys_include_required_fields(self) -> None:
        required = {
            "draftVersion", "gameProfileId", "seed", "width", "height",
            "cells", "goals", "engineSchemaVersion", "sourceRevision",
        }
        self.assertTrue(required.issubset(set(FREEZE.lfx_draft_root_keys)))

    def test_lfx_cell_key_count_is_10(self) -> None:
        self.assertEqual(len(FREEZE.lfx_cell_keys), LFX_CELL_KEY_COUNT)
        self.assertEqual(LFX_CELL_KEY_COUNT, 10)

    def test_lfx_cell_keys_include_required_fields(self) -> None:
        required = {"row", "column", "contentId", "obstacleId"}
        self.assertTrue(required.issubset(set(FREEZE.lfx_cell_keys)))

    def test_lfx_goal_key_count_is_3(self) -> None:
        self.assertEqual(len(FREEZE.lfx_goal_keys), LFX_GOAL_KEY_COUNT)
        self.assertEqual(LFX_GOAL_KEY_COUNT, 3)

    def test_legal_restrictions_present(self) -> None:
        self.assertGreater(len(FREEZE.legal_restrictions), 0, "Legal restrictions must be non-empty.")
        combined = " ".join(FREEZE.legal_restrictions).lower()
        self.assertIn("rimaethon", combined, "Rimaethon restriction must be recorded.")
        self.assertIn("proprietary", combined, "Engine/LFX proprietary restriction must be recorded.")

    def test_freeze_is_immutable(self) -> None:
        """ApiFreeze is a frozen dataclass; writes must raise."""
        with self.assertRaises((AttributeError, TypeError)):
            FREEZE.engine_m09_sha = "0" * 40  # type: ignore[misc]

    def test_negative_fake_surface_rejected(self) -> None:
        """A fabricated surface name must not be in the freeze."""
        self.assertNotIn("FakeSurface", FREEZE.engine_ui_surfaces)
        self.assertNotIn("GameOver", FREEZE.engine_ui_surfaces)

    def test_negative_fake_state_rejected(self) -> None:
        self.assertNotIn("Win", FREEZE.engine_player_states)
        self.assertNotIn("Score", FREEZE.engine_player_states)


if __name__ == "__main__":
    unittest.main()
