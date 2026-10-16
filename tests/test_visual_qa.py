"""VF-09 pixel-health diagnostics are advisory, deterministic and read-only."""
from __future__ import annotations

from contextlib import redirect_stdout, redirect_stderr
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from factory.image_processor.png_pipeline import encode_png
from factory.validators.visual_qa import (
    SpriteQaError, sprite_metrics, contrast_ratio, palette_review,
    audit_files, save_report_once, main,
)

ROOT = Path(__file__).resolve().parents[1]


class VisualQaTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.directory = Path(tmp.name)
        self.source = self.directory / "synthetic.png"
        self.rgba = bytes((
            0, 0, 0, 0,
            255, 0, 0, 255,
            12, 3, 9, 0,
            0, 255, 0, 255,
        ))
        self.source.write_bytes(encode_png(2, 2, self.rgba))

    def test_bbox_and_alpha_coverage_are_exact(self):
        metrics = sprite_metrics(2, 2, self.rgba)
        self.assertEqual(metrics["visible_bbox_top_left"], [0, 0, 2, 2])
        self.assertEqual(metrics["visible_pixels"], 2)
        self.assertEqual(metrics["alpha_coverage_basis_points"], 5000)
        self.assertEqual(metrics["transparent_colored_pixels"], 1)
        self.assertEqual(metrics["distinct_visible_rgb_capped"], 2)

    def test_empty_alpha_flags_review(self):
        metrics = sprite_metrics(2, 2, bytes(16))
        self.assertIsNone(metrics["visible_bbox_top_left"])
        self.assertEqual(metrics["warnings"], ["EMPTY_ALPHA"])

    def test_centered_sprite_has_no_border_warning(self):
        pixels = bytearray(4 * 4 * 4)
        pixels[(1 * 4 + 1) * 4:(1 * 4 + 1) * 4 + 4] = b"\xff\x80\x00\xff"
        result = sprite_metrics(4, 4, bytes(pixels))
        self.assertEqual(result["visible_bbox_top_left"], [1, 1, 1, 1])
        self.assertEqual(result["edge_visible_pixels"], 0)
        self.assertNotIn("CANVAS_BOUNDARY_TOUCH", result["warnings"])

    def test_border_is_advisory(self):
        out = sprite_metrics(2, 2, self.rgba)
        self.assertIn("CANVAS_BOUNDARY_TOUCH", out["warnings"])
        self.assertEqual(out["edge_visible_pixels"], 2)

    def test_alpha_fringe_risk_is_not_auto_rejection(self):
        rgba = (b"\0\0\0\0" + b"\xff\xff\xff\x80" +
                b"\0\0\0\0")
        metrics = sprite_metrics(3, 1, rgba)
        self.assertIn("POSSIBLE_BLACK_MATTE_FRINGE", metrics["warnings"])
        self.assertEqual(metrics["transparent_black_adjacent_visible"], 2)

    def test_sized_large_texture_warns(self):
        rgba = bytes(2049 * 4)
        result = sprite_metrics(2049, 1, rgba)
        self.assertIn("LARGE_TEXTURE_HEURISTIC", result["warnings"])

    def test_invalid_raw_length_is_rejected(self):
        with self.assertRaises(SpriteQaError):
            sprite_metrics(2, 2, b"bad")

    def test_white_black_contrast_near_21(self):
        self.assertAlmostEqual(contrast_ratio("#FFFFFF", "#000000"), 21, places=5)
        self.assertAlmostEqual(contrast_ratio("#777777", "#777777"), 1)

    def test_five_draft_palettes_are_analyzed_not_approved(self):
        for profile in ("Coral_Rescue", "Garage_Legends", "Dino_Islands",
                        "The_Fractured_Realms", "Wonder_Pop"):
            data = palette_review(profile)
            self.assertEqual(data["stage"], "DRAFT_NOT_OWNER_APPROVED")
            self.assertEqual(len(data["contrast_checks"]), 3)
            self.assertTrue(all(check["ratio"] >= 1 for check in data["contrast_checks"]))

    def test_unknown_palette_rejected(self):
        with self.assertRaises(SpriteQaError):
            palette_review("Unknown_Game")
        with self.assertRaises(SpriteQaError):
            contrast_ratio("badhex", "#FFFFFF")

    def test_file_report_contains_source_hash_but_no_approval(self):
        raw = self.source.read_bytes()
        report = audit_files([self.source], profile="Coral_Rescue")
        self.assertEqual(report["stage"], "REVIEW_REQUIRED_NOT_OWNER_APPROVED")
        self.assertFalse(report["source_rights_verified"])
        self.assertEqual(report["file_count"], 1)
        self.assertEqual(report["sprites"][0]["source_sha256_recorded"],
                         hashlib.sha256(raw).hexdigest())
        self.assertEqual(raw, self.source.read_bytes())
        self.assertIn("palette_review", report)
        self.assertNotIn(str(self.directory), json.dumps(report))

    def test_duplicate_files_rejected(self):
        with self.assertRaises(SpriteQaError):
            audit_files([self.source, self.source])

    def test_bad_png_crc_rejected(self):
        raw = bytearray(self.source.read_bytes())
        raw[20] ^= 1
        self.source.write_bytes(raw)
        with self.assertRaises(SpriteQaError):
            audit_files([self.source])

    def test_unsupported_format_rejected(self):
        other = self.directory / "bad.jpeg"
        other.write_bytes(self.source.read_bytes())
        with self.assertRaises(SpriteQaError):
            audit_files([other])

    def test_linked_input_simulated_without_windows_rights(self):
        from factory.validators import visual_qa
        old_link = visual_qa._link
        with patch.object(visual_qa, "_link",
                          side_effect=lambda p: Path(p) == self.source or old_link(p)):
            with self.assertRaises(SpriteQaError):
                audit_files([self.source])

    def test_report_create_once_preserves_existing(self):
        report = audit_files([self.source])
        target = self.directory / "visual-qa.json"
        save_report_once(report, target)
        initial = target.read_bytes()
        self.assertEqual(json.loads(initial)["file_count"], 1)
        with self.assertRaises(SpriteQaError):
            save_report_once(report, target)
        self.assertEqual(initial, target.read_bytes())

    def test_output_inside_checkout_rejected(self):
        with self.assertRaises(SpriteQaError):
            save_report_once(audit_files([self.source]), ROOT / "visual-qa.json")

    def test_cli_stdout_does_not_write_files(self):
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(["--source", str(self.source)]), 0)
        self.assertEqual(json.loads(output.getvalue())["file_count"], 1)
        self.assertEqual(list(self.directory.glob("*.json")), [])

    def test_cli_invalid_input_returns_error(self):
        with redirect_stderr(io.StringIO()):
            self.assertEqual(main(["--source", str(self.source) + ".missing"]), 2)


if __name__ == "__main__":
    unittest.main()
