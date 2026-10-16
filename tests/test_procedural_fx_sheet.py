"""VF-06 deterministic offline VFX candidate generation safeguards."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from factory.image_processor.png_pipeline import decode_png
from factory.vfx_builder.procedural_fx_sheet import (
    COLORS, VfxCandidateError, build_candidate, write_candidate, main,
)


class ProceduralVfxSheetTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.folder = Path(temp.name)

    def test_five_presets_generate_bounded_nonempty_original_pngs(self):
        for name in COLORS:
            with self.subTest(name=name):
                manifest, atlas, still = build_candidate(name, frames=8,
                                                           frame_side=24, columns=4)
                width, height, rgba = decode_png(atlas)
                sw, sh, static_rgba = decode_png(still)
                self.assertEqual((width, height), (96, 48))
                self.assertEqual((sw, sh), (24, 24))
                self.assertEqual(len(manifest["animation_frames"]), 8)
                self.assertGreater(max(rgba[3::4]), 0)
                self.assertGreater(max(static_rgba[3::4]), 0)
                self.assertFalse(manifest["asset_rights_verified"])
                self.assertFalse(manifest["engine_side_effects_allowed"])
                self.assertEqual(manifest["reduced_motion_policy"], "STATIC_VIEW_ONLY")
                self.assertEqual(manifest["stage"], "CANDIDATE_NOT_OWNER_APPROVED")

    def test_exact_determinism_independent_invocation(self):
        first = build_candidate("StarSparkle", seed=17)
        second = build_candidate("StarSparkle", seed=17)
        self.assertEqual(first, second)

    def test_frame_sha_matches_atlas_subrect_bytes(self):
        manifest, png, _ = build_candidate("MatchBurst", frames=6,
                                           frame_side=24, columns=3)
        w, h, rgba = decode_png(png)
        self.assertEqual((w, h), (72, 48))
        for frame in manifest["animation_frames"]:
            x, y, fw, fh = frame["pixel_rect_top_left"]
            pixels = b"".join(
                rgba[((y + row) * w + x) * 4:
                     ((y + row) * w + x + fw) * 4]
                for row in range(fh))
            self.assertEqual(hashlib.sha256(pixels).hexdigest(),
                             frame["rgba_sha256"])

    def test_must_keep_separate_reduced_motion_still(self):
        manifest, _, still = build_candidate("PortalPulse")
        self.assertEqual(hashlib.sha256(still).hexdigest(),
                         manifest["reduced_motion_sha256"])
        self.assertNotIn("GrantedReward", str(manifest))

    def test_write_once_and_preserve_original_assets(self):
        folder = self.folder / "candidate-001"
        manifest, atlas, reduced = build_candidate("BubbleRise")
        write_candidate(folder, manifest, atlas, reduced)
        self.assertEqual((folder / "fx_sheet.png").read_bytes(), atlas)
        self.assertEqual((folder / "reduced_motion.png").read_bytes(), reduced)
        self.assertEqual(json.loads((folder / "fx_manifest.json").read_text()),
                         manifest)
        with self.assertRaises(VfxCandidateError):
            write_candidate(folder, manifest, b"malicious", reduced)
        self.assertEqual((folder / "fx_sheet.png").read_bytes(), atlas)

    def test_no_write_without_explicit_output_dir(self):
        from contextlib import redirect_stdout
        from io import StringIO
        stdout = StringIO()
        with redirect_stdout(stdout):
            self.assertEqual(main(["--preset", "SoftDrift", "--frames", "4",
                                   "--frame-side", "16"]), 0)
        self.assertFalse(json.loads(stdout.getvalue())["output_saved"])
        self.assertEqual(list(self.folder.iterdir()), [])

    def test_altered_seed_or_color_changes_frames_not_preset_scope(self):
        a, pnga, _ = build_candidate("MatchBurst", seed=0, frames=4, frame_side=24)
        b, pngb, _ = build_candidate("MatchBurst", seed=21, frames=4, frame_side=24)
        self.assertNotEqual(pnga, pngb)
        self.assertEqual(a["preset_id"], b["preset_id"])
        self.assertEqual(a["presets_source_sha256"], b["presets_source_sha256"])
        colored, other, _ = build_candidate("BubbleRise", color="#FF0088",
                                           frames=4, frame_side=24)
        self.assertEqual(colored["color"], "#FF0088")
        self.assertNotEqual(other, pngb)

    def test_reject_unknown_preset(self):
        with self.assertRaises(VfxCandidateError):
            build_candidate("MakeRewardOnWin")

    def test_reject_invalid_frames_size_columns_fps_seed(self):
        for data in ({"frames": 1}, {"frames": 33}, {"frames": True},
                     {"frame_side": 15}, {"frame_side": 129},
                     {"columns": 0}, {"columns": 80},
                     {"fps": 0}, {"fps": 61}, {"seed": -1}, {"seed": 65536},
                     {"color": "#FFF"}, {"color": "transparent"}):
            with self.subTest(data=data), self.assertRaises(VfxCandidateError):
                build_candidate("MatchBurst", **data)

    def test_no_write_to_source_checkout(self):
        repo_root = Path(__file__).resolve().parents[1]
        with self.assertRaises(VfxCandidateError):
            write_candidate(repo_root / "forbidden-fx", *build_candidate("SoftDrift"))

    def test_bad_existing_destination_fails_closed(self):
        folder = self.folder / "fx"
        folder.mkdir()
        with self.assertRaises(VfxCandidateError):
            write_candidate(folder, *build_candidate("PortalPulse"))

    def test_generated_manifest_has_fixed_source_receipts(self):
        m, data, still = build_candidate("SoftDrift", frames=6, columns=2)
        self.assertEqual(m["generator"], "VF06_PROCEDURAL_FX_SHEET_V01")
        self.assertEqual(m["atlas_sha256"], hashlib.sha256(data).hexdigest())
        self.assertEqual(m["reduced_motion_sha256"], hashlib.sha256(still).hexdigest())
        self.assertEqual(m["rows"], 3)
        self.assertEqual(m["pixel_format"], "RGBA8_UNROTATED")


if __name__ == "__main__":
    unittest.main()
