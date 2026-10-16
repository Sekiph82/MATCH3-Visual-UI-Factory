using System;
using NUnit.Framework;
using UnityEngine;
using Match3.VisualFactory.Editor;

namespace Match3.VisualFactory.Tests
{
    public sealed class VufFxSheetEditModeTests
    {
        private static VufFxSheetPreviewWindow.FxManifest Fixture()
        {
            return new VufFxSheetPreviewWindow.FxManifest {
                schema_version = 1,
                stage = "CANDIDATE_NOT_OWNER_APPROVED",
                generator = "VF06_PROCEDURAL_FX_SHEET_V01",
                preset_id = "BubbleRise",
                presets_source_sha256 = new string('a', 64),
                color = "#64E5FF",
                fps = 12, frame_rate = 12, frame_count = 4,
                frame_side = 32, columns = 2, rows = 2,
                atlas_width = 64, atlas_height = 64,
                atlas_path = "fx_sheet.png",
                atlas_sha256 = new string('b', 64),
                reduced_motion_path = "reduced_motion.png",
                reduced_motion_sha256 = new string('c', 64),
                reduced_motion_policy = "STATIC_VIEW_ONLY",
                asset_rights_verified = false,
                engine_side_effects_allowed = false,
                owner_visual_approval = false,
                animation_frames = new [] {
                    Frame(0, 0, 0), Frame(1, 32, 0),
                    Frame(2, 0, 32), Frame(3, 32, 32)
                }
            };
        }

        private static VufFxSheetPreviewWindow.FxFrame Frame(int n, int x, int y)
        {
            return new VufFxSheetPreviewWindow.FxFrame {
                frame = n, pixel_rect_top_left = new [] {x, y, 32, 32},
                rgba_sha256 = new string('d', 64)
            };
        }

        [Test]
        public void CorrectSourceSheetGeometryOpensInCandidateOnlyMode()
        {
            var manifest = Fixture();
            var parsed = VufFxSheetPreviewWindow.Parse(
                JsonUtility.ToJson(manifest), 64, 64, 32, 32);
            Assert.That(parsed.animation_frames.Length, Is.EqualTo(4));
            Assert.That(parsed.engine_side_effects_allowed, Is.False);
            Assert.That(parsed.owner_visual_approval, Is.False);
        }

        [Test]
        public void ForgedApprovalOrEngineAuthorityIsAlwaysRejected()
        {
            var obj = Fixture();
            obj.stage = "OWNER_APPROVED";
            Assert.Throws<ArgumentException>(() =>
                VufFxSheetPreviewWindow.Parse(JsonUtility.ToJson(obj), 64, 64, 32, 32));
            obj = Fixture();
            obj.engine_side_effects_allowed = true;
            Assert.Throws<ArgumentException>(() =>
                VufFxSheetPreviewWindow.Parse(JsonUtility.ToJson(obj), 64, 64, 32, 32));
            obj = Fixture();
            obj.asset_rights_verified = true;
            Assert.Throws<ArgumentException>(() =>
                VufFxSheetPreviewWindow.Parse(JsonUtility.ToJson(obj), 64, 64, 32, 32));
        }

        [Test]
        public void WrongFrameRectsSizesAndHashesAreRejected()
        {
            var obj = Fixture();
            obj.animation_frames[3].pixel_rect_top_left[0] = 20;
            Assert.Throws<ArgumentException>(() =>
                VufFxSheetPreviewWindow.Parse(JsonUtility.ToJson(obj), 64, 64, 32, 32));
            obj = Fixture();
            obj.atlas_sha256 = "fake";
            Assert.Throws<ArgumentException>(() =>
                VufFxSheetPreviewWindow.Parse(JsonUtility.ToJson(obj), 64, 64, 32, 32));
            obj = Fixture();
            Assert.Throws<ArgumentException>(() =>
                VufFxSheetPreviewWindow.Parse(JsonUtility.ToJson(obj), 128, 64, 32, 32));
        }
    }
}
