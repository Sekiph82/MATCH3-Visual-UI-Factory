"""M05 actual Engine enum kind source contracts, NOT instance/level IDs."""
from __future__ import annotations

import copy
import hashlib
import unittest
from pathlib import Path

from factory.visual_director.m05_engine_kind_intake import (
    PATH_ROOT, REQUIRED_ENUMS, SOURCE_PINS, EngineKindError,
    _inspect, draft_five_title_role_bindings, git_blob_sha,
    inspect_pinned_engine_kinds, parse_declared_enum,
    read_pinned_engine_sources, _canonical_checkout_source_eol,
    read_pinned_engine_sources_with_receipts,
)


def fixture_sources():
    """Synthetic explicit enums only; never evidence of the real Engine bytes."""
    data = {}
    for filename, enums in REQUIRED_ENUMS.items():
        content = "namespace UntrustedSynthetic {\n"
        for enum, keys in enums.items():
            content += "public enum " + enum + " { " + ", ".join(
                "%s = %d" % (name, i) for i, name in enumerate(keys)) + " }\n"
        data[PATH_ROOT + filename] = (content + "}\n").encode()
    return data


class M05EngineKindIntakeTests(unittest.TestCase):
    def setUp(self):
        self.sources = fixture_sources()
        self.pins = {name: git_blob_sha(value)
                     for name, value in self.sources.items()}

    def test_pinned_declaration_receipt_are_actual_inspected_engine_blobs(self):
        self.assertEqual(SOURCE_PINS[PATH_ROOT + "ObstacleLifecycleContracts.cs"],
                         "0a882ec44e6ecfcb840971efad187515f44ef9b3")
        self.assertEqual(SOURCE_PINS[PATH_ROOT + "GoalScoreContracts.cs"],
                         "dbc36103437786a5020b43e1e00d18e27374126b")
        self.assertEqual(SOURCE_PINS[PATH_ROOT + "BoosterEconomyContracts.cs"],
                         "9d184e0a964c354e9038c1946bd36377d4c1fe23")
        self.assertEqual(SOURCE_PINS[PATH_ROOT + "SpecialEffectContracts.cs"],
                         "5ad6e1dcd50d707614ecf258207c2f09e3538a3e")
        self.assertEqual(set(SOURCE_PINS), set(self.sources))

    def test_only_synthetic_pin_override_cannot_claim_official_upstream_evidence(self):
        report = _inspect(self.sources, self.pins)
        self.assertFalse(report["observed_verified_against_pinned_engine_sources"])
        self.assertEqual(len(report["engine_declared_kinds"]), 5)
        for key in ("actual_obstacle_definition_ids_verified",
                    "actual_goal_definition_ids_verified",
                    "actual_booster_instance_ids_verified",
                    "owner_art_mapping_verified", "engine_lfx_final_abi_verified",
                    "release_allowed"):
            self.assertIs(report[key], False)
        with self.assertRaises(EngineKindError):
            draft_five_title_role_bindings(self.sources)

    def test_real_official_source_check_rejects_synthetic_enum_files(self):
        with self.assertRaises(EngineKindError):
            inspect_pinned_engine_kinds(self.sources)

    def test_missing_extra_or_modified_upstream_files_fail_closed(self):
        for candidate in (
            dict(list(self.sources.items())[:-1]),
            {**self.sources, "extra.cs": b"not a source"},
            {**self.sources,
             PATH_ROOT + "GoalScoreContracts.cs": b"misleading"},
        ):
            with self.assertRaises(EngineKindError):
                _inspect(candidate, self.pins)

    def test_duplicate_wrong_order_or_noncanonical_members_fail_closed(self):
        raw = b"public enum GoalKind { CollectPiece = 0, ClearObstacle = 1 }"
        self.assertEqual(parse_declared_enum(raw, "GoalKind"),
                         ("CollectPiece", "ClearObstacle"))
        for bad in (
            b"public enum GoalKind { CollectPiece = 0, CollectPiece = 1 }",
            b"public enum GoalKind { CollectPiece = 0, Other = 0 }",
            b"public enum GoalKind { CollectPiece = 1 }",
            b"public enum GoalKind { CollectPiece = 0, }"
            b" public enum GoalKind { ClearObstacle = 1 }",
            b"public enum GoalKind { Value }",
        ):
            with self.subTest(bad=bad), self.assertRaises(EngineKindError):
                parse_declared_enum(bad, "GoalKind")
        altered = dict(self.sources)
        altered[PATH_ROOT + "GoalScoreContracts.cs"] = altered[
            PATH_ROOT + "GoalScoreContracts.cs"].replace(
            b"ClearObstacle = 1", b"ClearObstacle = 4")
        forged_pins = {p: git_blob_sha(b) for p, b in altered.items()}
        with self.assertRaises(EngineKindError):
            _inspect(altered, forged_pins)

    def test_exact_lf_source_yields_exact_blob_and_no_authority(self):
        raw = self.sources[PATH_ROOT + "GoalScoreContracts.cs"]
        canonical, receipt = _canonical_checkout_source_eol(
            raw, git_blob_sha(raw))
        self.assertEqual(canonical, raw)
        self.assertEqual(receipt["checkout_transport_eol"], "EXACT_PINNED_BYTES")
        self.assertEqual(receipt["raw_checkout_blob_sha1"], git_blob_sha(raw))
        self.assertTrue(receipt["canonical_bytes_match_pin"])
        self.assertFalse(receipt["final_registry_ids_verified"])
        self.assertFalse(receipt["release_allowed"])
        self.assertFalse(receipt["worktree_file_modified"])

    def test_pure_windows_crlf_equivalent_normalized_only_in_memory(self):
        original = self.sources[PATH_ROOT + "GoalScoreContracts.cs"]
        windows = original.replace(b"\\n", b"\\r\\n")
        self.assertNotEqual(git_blob_sha(windows), git_blob_sha(original))
        canonical, receipt = _canonical_checkout_source_eol(
            windows, git_blob_sha(original))
        self.assertEqual(canonical, original)
        self.assertEqual(receipt["checkout_transport_eol"],
                         "PURE_CRLF_NORMALIZED_IN_MEMORY")
        self.assertEqual(receipt["canonical_git_blob_sha1"], git_blob_sha(original))
        self.assertEqual(receipt["raw_checkout_blob_sha1"], git_blob_sha(windows))
        self.assertFalse(receipt["worktree_file_modified"])
        self.assertFalse(receipt["release_allowed"])

    def test_mixed_eol_or_lone_cr_or_mismatched_pinned_bytes_fail_closed(self):
        original = self.sources[PATH_ROOT + "GoalScoreContracts.cs"]
        good_crlf = original.replace(b"\\n", b"\\r\\n")
        mutated = good_crlf.replace(b"CollectPiece", b"FakeCollect", 1)
        variants = (
            good_crlf.replace(b"\\r\\n", b"\\n", 1),
            good_crlf.replace(b"\\r\\n", b"\\r", 1),
            good_crlf.replace(b"\\r\\n", b"\\r\\r\\n", 1),
            mutated, original + b"\\n",
        )
        for case in variants:
            with self.subTest(raw=case[:60]), self.assertRaises(EngineKindError):
                _canonical_checkout_source_eol(case, git_blob_sha(original))
        with self.assertRaises(EngineKindError):
            _canonical_checkout_source_eol(good_crlf, "0" * 40)
        with self.assertRaises(EngineKindError):
            _canonical_checkout_source_eol(good_crlf, "not_a_sha")

    def test_checkout_intake_does_not_call_git_write_or_mutate_sibling(self):
        import inspect
        reader = inspect.getsource(read_pinned_engine_sources_with_receipts)
        self.assertIn("source.read_bytes()", reader)
        for prohibited in ("subprocess", "checkout", ".write_bytes(",
                           ".write_text(", "unlink(", "mkdir(", "shutil"):
            if prohibited == "checkout":
                # Documentation says checkout; it is not an executable call.
                continue
            self.assertNotIn(prohibited, reader)
        self.assertIn("read_pinned_engine_sources_with_receipts", inspect.getsource(
            read_pinned_engine_sources))

    def test_engine_local_read_path_is_explicit_never_autoclones_or_writes(self):
        with self.assertRaises(EngineKindError):
            read_pinned_engine_sources(Path("not-a-real-engine-directory"))
        with self.assertRaises(EngineKindError):
            read_pinned_engine_sources(Path(__file__).resolve().parents[1])
        import inspect
        code = inspect.getsource(read_pinned_engine_sources)
        self.assertNotIn(".write_", code)
        self.assertNotIn("mkdir(", code)
        self.assertNotIn("subprocess", code)
        self.assertNotIn("shutil", code)

    def test_git_blob_hash_checks_exact_source_bytes_not_just_semantics(self):
        name = PATH_ROOT + "GoalScoreContracts.cs"
        self.assertEqual(len(self.pins[name]), 40)
        self.assertEqual(self.pins[name], hashlib.sha1(
            b"blob " + str(len(self.sources[name])).encode() + b"\0" +
            self.sources[name]).hexdigest())
        changed = dict(self.sources)
        changed[name] = changed[name] + b"\n"
        with self.assertRaises(EngineKindError):
            _inspect(changed, self.pins)
        with self.assertRaises(EngineKindError):
            git_blob_sha(b"")
        with self.assertRaises(EngineKindError):
            git_blob_sha(b"x" * (128 * 1024 + 1))

    def test_forged_json_receipt_is_not_accepted_in_place_of_original_cs(self):
        result = _inspect(self.sources, self.pins)
        # Hand-editing the result flags or source SHA strings must not
        # replace the real .cs byte-identical input requirement.
        result["observed_verified_against_pinned_engine_sources"] = True
        result["source_blob_sha1"] = {
            path: SOURCE_PINS[path] for path in sorted(SOURCE_PINS)}
        with self.assertRaises(EngineKindError):
            draft_five_title_role_bindings(result)
        with self.assertRaises(EngineKindError):
            draft_five_title_role_bindings(self.sources)
        self.assertFalse(_inspect(self.sources,self.pins)["release_allowed"])


if __name__ == "__main__":
    unittest.main()
