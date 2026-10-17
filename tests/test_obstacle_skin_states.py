"""R51 M05-003 symbolic candidate obstacle/goal/booster contract checks."""
import copy
import unittest

from factory.visual_director.obstacle_skin_states import (
    DAMAGE_KINDS, LAYER_KINDS, PROFILES, SOURCE_BLOB, ObstacleSkinError,
    build_state_map, source_example_definitions, verify_state_map,
)


class ObstacleSkinStateTests(unittest.TestCase):
    def setUp(self):
        self.demo = source_example_definitions()

    def test_each_five_profile_covers_all_five_art_roles(self):
        all_keys = set()
        for p in PROFILES:
            m = build_state_map(p, self.demo)
            verify_state_map(m, self.demo)
            self.assertEqual(len(m["assets"]), 5)
            self.assertEqual({x["role"] for x in m["assets"]},
                             {"obstacle", "goal", "collectible", "equipment", "booster"})
            self.assertFalse(m["release_allowed"])
            self.assertFalse(m["actual_upstream_definition_ids_verified"])
            self.assertEqual(m["engine_obstacle_source_blob_sha"], SOURCE_BLOB)
            keys = {state["sprite_key"] for a in m["assets"]
                    for state in a["states"]}
            self.assertFalse(keys & all_keys)
            all_keys.update(keys)

    def test_damage_stages_are_visual_only(self):
        row = next(a for a in build_state_map(
            "Coral_Rescue", self.demo)["assets"] if a["role"] == "obstacle")
        self.assertEqual([x["durability"] for x in row["states"]], [3, 2, 1, 0])
        self.assertFalse(row["gameplay_durability_mutations"])
        self.assertFalse(row["save_or_reward_authority"])
        self.assertEqual([x["engine_damage_kind"] for x in row["damage_visuals"]],
                         ["Normal", "Line", "Area"])

    def test_actual_engine_enum_contracts_pinned(self):
        self.assertEqual(LAYER_KINDS, ("Underlay", "Overlay", "Piece", "Cell"))
        self.assertEqual(DAMAGE_KINDS, ("Normal", "Line", "Area", "Color", "Targeted"))
        self.assertEqual(len(SOURCE_BLOB), 40)

    def test_duplicate_semantic_role_is_rejected(self):
        with self.assertRaises(ObstacleSkinError):
            build_state_map("Dino_Islands", self.demo + [self.demo[0]])

    def test_invalid_durability_or_non_obstacle_hp_is_rejected(self):
        bad = copy.deepcopy(self.demo)
        bad[0]["max_durability"] = 0
        with self.assertRaises(ObstacleSkinError):
            build_state_map("Dino_Islands", bad)
        bad = copy.deepcopy(self.demo)
        bad[1]["max_durability"] = 3
        with self.assertRaises(ObstacleSkinError):
            build_state_map("Dino_Islands", bad)

    def test_unknown_engine_layer_and_damage_are_rejected(self):
        bad = copy.deepcopy(self.demo)
        bad[0]["layer"] = "Tile"
        with self.assertRaises(ObstacleSkinError):
            build_state_map("Coral_Rescue", bad)
        bad = copy.deepcopy(self.demo)
        bad[0]["damage_kinds"] = ["Missile"]
        with self.assertRaises(ObstacleSkinError):
            build_state_map("Coral_Rescue", bad)
        bad[0]["damage_kinds"] = [{"malformed": True}]
        with self.assertRaises(ObstacleSkinError):
            build_state_map("Coral_Rescue", bad)

    def test_unsafe_ids_and_many_definitions_rejected(self):
        bad = copy.deepcopy(self.demo)
        bad[0]["id"] = "../private"
        with self.assertRaises(ObstacleSkinError):
            build_state_map("Garage_Legends", bad)
        with self.assertRaises(ObstacleSkinError):
            build_state_map("Garage_Legends", self.demo * 15)

    def test_cannot_forge_approval_or_change_visual_state(self):
        m = build_state_map("Wonder_Pop", self.demo)
        m["stage"] = "APPROVED"
        with self.assertRaises(ObstacleSkinError):
            verify_state_map(m, self.demo)
        m = build_state_map("Wonder_Pop", self.demo)
        m["assets"][0]["states"][0]["sprite_key"] = "other_game.sprite"
        with self.assertRaises(ObstacleSkinError):
            verify_state_map(m, self.demo)


if __name__ == "__main__":
    unittest.main()
