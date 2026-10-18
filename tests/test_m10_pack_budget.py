"""Source-only external pack texture budget; no physical player/GPU PASS."""
import tempfile
import unittest
from pathlib import Path

from factory.asset_packaging.candidate_pack import export_pack
from factory.integration.m10_pack_budget import (
    analyze_external_candidate, M10BudgetError,
)


class M10CandidateBudgetTests(unittest.TestCase):
    def test_real_vf04_coral_opaque_external_bundle_has_bounded_sha_png_budget(self):
        with tempfile.TemporaryDirectory(prefix="vuf_m10_budget_") as parent:
            pack = Path(parent) / "real_coral_candidate"
            export_pack("Coral_Rescue", pack)
            result = analyze_external_candidate(pack)
            self.assertEqual(result["profile_id"], "Coral_Rescue")
            self.assertGreater(result["source_png_count"], 40)
            self.assertGreater(result["uncompressed_rgba32_estimated_bytes_no_mips"], 0)
            self.assertTrue(result["all_manifest_sha256_checked"])
            self.assertFalse(result["actual_level_factory_pack_consumer_verified"])
            self.assertFalse(result["release_allowed"])
            for device in ("Windows_Editor", "Android", "iOS"):
                self.assertFalse(result["platform_profiles"][device]
                                 ["actual_gpu_peak_measured"])
                self.assertFalse(result["platform_profiles"][device]
                                 ["player_build_built_and_scanned"])

    def test_missing_bundle_is_not_a_player_profiling_success(self):
        with tempfile.TemporaryDirectory(prefix="vuf_m10_badbudget_") as parent:
            with self.assertRaises((OSError, ValueError)):
                analyze_external_candidate(Path(parent) / "not_a_pack")


if __name__ == "__main__":
    unittest.main()
