"""M09 desktop viewer pure contract tests; no headless Tk/window claims."""
import tempfile
import unittest
from pathlib import Path
from Tools.vuf_m09_windows_viewer import (
    EVENTS, SPEEDS, STAGE, WindowsViewerError,
    frame_region, receipt, create_new_receipt,
)


class M09WindowsViewerTests(unittest.TestCase):
    def test_fx_sheet_crop_4x2_eight_frames_no_invalid_sample(self):
        self.assertEqual(frame_region("fx/bubblerise/fx_sheet.png",
                                      0, 128, 64), (0, 0, 32, 32))
        self.assertEqual(frame_region("fx/bubblerise/fx_sheet.png",
                                      7, 128, 64), (96, 32, 128, 64))
        for invalid in (-1, 8, True):
            with self.assertRaises(WindowsViewerError):
                frame_region("fx/bubblerise/fx_sheet.png",
                             invalid, 128, 64)

    def test_only_vf06_source_sheets_are_frame_cropped(self):
        for bad in ("sprites/sample_circle.png", "fx/bubblerise/reduced_motion.png"):
            with self.assertRaises(WindowsViewerError):
                frame_region(bad, 0, 128, 64)
        with self.assertRaises(WindowsViewerError):
            frame_region("fx/bubblerise/fx_sheet.png", 0, 129, 64)

    def test_event_review_record_does_not_fake_art_engine_or_phone(self):
        source = {
            "manifest": {"profile_id": "Coral_Rescue"},
            "images": {"sprites/sample_001.png": {
                "sha256": "a" * 64,
                "asset_id": "Coral_Rescue.sample.circle",
                "path": Path("unused_by_pure_test")}}
        }
        data = receipt(source, "sprites/sample_001.png", screen_index=26,
                       state="Loading", locale="tr", device="Android (approx 20:9)",
                       event="tile_match", level=4, seed=3, speed=2.0, frame=0)
        self.assertEqual(data["stage"], STAGE)
        self.assertEqual(data["candidate_case"]["coral_draft_screen_id"], "COR-27")
        self.assertFalse(data["actual_unity_gui_render"])
        self.assertFalse(data["release_allowed"])
        self.assertFalse(data["real_device_gpu_verified"])
        self.assertEqual(len(EVENTS), 14)
        self.assertEqual(len(SPEEDS), 4)
        with self.assertRaises(WindowsViewerError):
            receipt(source, "sprites/sample_001.png", screen_index=26,
                    state="Loading", locale="tr", device="Android (approx 20:9)",
                    event="purchase_reward", level=4, seed=3, speed=2, frame=0)

    def test_receipt_export_is_create_only_and_cannot_self_approve(self):
        source = {
            "manifest": {"profile_id": "Coral_Rescue"},
            "images": {"sprites/sample_001.png": {
                "sha256": "a" * 64,
                "asset_id": "Coral_Rescue.sample.circle",
                "path": Path("unused_by_pure_test")}}
        }
        data = receipt(source, "sprites/sample_001.png", screen_index=26,
                       state="Ready", locale="en", device="Tall phone (approx 19.5:9)",
                       event="ui_open", level=1, seed=7, speed=1.0, frame=0)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "source_candidate.json"
            create_new_receipt(path, data)
            self.assertTrue(path.is_file())
            with self.assertRaises(WindowsViewerError):
                create_new_receipt(path, data)
            wrong = dict(data, release_allowed=True)
            with self.assertRaises(WindowsViewerError):
                create_new_receipt(Path(tmp) / "forged.json", wrong)


if __name__ == "__main__":
    unittest.main()
