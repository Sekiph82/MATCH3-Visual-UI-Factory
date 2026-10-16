using System;
using System.Collections.Generic;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;
using Match3.VisualFactory.Editor;

namespace Match3.VisualFactory.Tests
{
    public sealed class VufFxClipExporterEditModeTests
    {
        private Texture2D atlas;
        private Texture2D still;
        private readonly List<Sprite> sprites = new List<Sprite>();

        [SetUp]
        public void CreateGeneratedSpriteFixture()
        {
            atlas = new Texture2D(64, 64, TextureFormat.RGBA32, false);
            still = new Texture2D(32, 32, TextureFormat.RGBA32, false);
            for (int i = 0; i < 4; i++)
            {
                int x = i % 2 * 32;
                int y = 64 - (i / 2 + 1) * 32;
                sprites.Add(Sprite.Create(atlas, new Rect(x, y, 32, 32),
                    new Vector2(.5f, .5f), 100f));
            }
        }

        [TearDown]
        public void DestroyOnlyTestOwnedObjects()
        {
            foreach (Sprite sprite in sprites)
                if (sprite != null) UnityEngine.Object.DestroyImmediate(sprite);
            sprites.Clear();
            if (atlas != null) UnityEngine.Object.DestroyImmediate(atlas);
            if (still != null) UnityEngine.Object.DestroyImmediate(still);
        }

        private static VufFxSheetPreviewWindow.FxManifest Manifest()
        {
            return new VufFxSheetPreviewWindow.FxManifest {
                schema_version = 1, stage = "CANDIDATE_NOT_OWNER_APPROVED",
                generator = "VF06_PROCEDURAL_FX_SHEET_V01",
                preset_id = "BubbleRise", presets_source_sha256 = new string('a', 64),
                fps = 12, frame_rate = 12, frame_count = 4,
                frame_side = 32, columns = 2, rows = 2,
                atlas_width = 64, atlas_height = 64,
                atlas_path = "fx_sheet.png", atlas_sha256 = new string('b', 64),
                reduced_motion_path = "reduced_motion.png",
                reduced_motion_sha256 = new string('c', 64),
                reduced_motion_policy = "STATIC_VIEW_ONLY",
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
        public void ScrambledImportedSpritesAreMatchedByRectAndNotName()
        {
            sprites.Reverse();
            List<Sprite> selected = VufFxClipExporterWindow.MatchFrames(
                Manifest(), atlas, sprites);
            Assert.That(selected.Count, Is.EqualTo(4));
            Assert.That(selected[0].rect.y, Is.EqualTo(32f));
            Assert.That(selected[3].rect.y, Is.EqualTo(0f));
        }

        [Test]
        public void CreatesInMemoryTrueUnitySpriteRendererCurve()
        {
            AnimationClip clip = VufFxClipExporterWindow.BuildVerifiedClip(
                "TEST_ONLY_FX", Manifest(), atlas, still, sprites, true);
            try
            {
                Assert.That(clip.name, Is.EqualTo("TEST_ONLY_FX"));
                var bindings = AnimationUtility.GetObjectReferenceCurveBindings(clip);
                Assert.That(bindings.Length, Is.EqualTo(1));
                Assert.That(bindings[0].propertyName, Is.EqualTo("m_Sprite"));
                var keys = AnimationUtility.GetObjectReferenceCurve(clip, bindings[0]);
                Assert.That(keys.Length, Is.EqualTo(5));
                Assert.That(keys[0].value, Is.EqualTo(sprites[0]));
                Assert.That(keys[4].value, Is.EqualTo(sprites[0]));
            }
            finally { UnityEngine.Object.DestroyImmediate(clip); }
        }

        [Test]
        public void RefusesWrongImporterSliceAndMissingStill()
        {
            var incomplete = new List<Sprite>(sprites);
            incomplete.RemoveAt(3);
            Assert.Throws<ArgumentException>(() =>
                VufFxClipExporterWindow.MatchFrames(Manifest(), atlas, incomplete));
            var invalid = Manifest();
            invalid.reduced_motion_policy = "NONE";
            Assert.Throws<ArgumentException>(() =>
                VufFxClipExporterWindow.BuildVerifiedClip("bad", invalid,
                    atlas, still, sprites, false));
        }

        [Test]
        public void DuplicateRectsCannotSilentlyProduceFakeFrames()
        {
            var wrong = new List<Sprite>(sprites);
            wrong[3] = wrong[0];
            Assert.Throws<ArgumentException>(() =>
                VufFxClipExporterWindow.MatchFrames(Manifest(), atlas, wrong));
        }
    }
}
