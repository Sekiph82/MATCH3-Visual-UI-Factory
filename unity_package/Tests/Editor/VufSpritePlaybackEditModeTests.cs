// VUF-M07-002/M07-009 | Genuine Unity SpriteRenderer candidate parity tests.
// These are SOURCE NUnit tests until owner-local Unity 6000.6.5f1 runs them.
// No Animator Controller or Match3 Engine type, reward/save/level hooks.
using System;
using NUnit.Framework;
using UnityEngine;

namespace Match3.VisualFactory.Tests
{
    public sealed class VufSpritePlaybackEditModeTests
    {
        private GameObject host;
        private Texture2D firstTexture;
        private Texture2D secondTexture;
        private Sprite[] original;
        private Sprite[] alternate;
        private SpriteRenderer renderer;
        private VufSpritePlaybackPreview preview;

        private static Sprite[] MakeFrames(Texture2D texture, int count,
                                           float ppu = 32f,
                                           Vector2? pivot = null)
        {
            var result = new Sprite[count];
            for (int i = 0; i < count; i++)
                result[i] = Sprite.Create(
                    texture, new Rect(i * 8, 0, 8, 8),
                    pivot ?? new Vector2(.5f, .5f), ppu);
            return result;
        }

        [SetUp]
        public void SetUp()
        {
            firstTexture = new Texture2D(32, 8, TextureFormat.RGBA32, false);
            secondTexture = new Texture2D(32, 8, TextureFormat.RGBA32, false);
            original = MakeFrames(firstTexture, 4);
            alternate = MakeFrames(secondTexture, 4);
            host = new GameObject("VUF_VIEW_ONLY_SPRITE_PLAYBACK_TEST",
                typeof(SpriteRenderer), typeof(VufSpritePlaybackPreview));
            renderer = host.GetComponent<SpriteRenderer>();
            preview = host.GetComponent<VufSpritePlaybackPreview>();
            renderer.sprite = original[3]; // pre-bind owner reference
        }

        [TearDown]
        public void TearDown()
        {
            if (host != null) UnityEngine.Object.DestroyImmediate(host);
            foreach (Sprite item in original)
                if (item != null) UnityEngine.Object.DestroyImmediate(item);
            foreach (Sprite item in alternate)
                if (item != null) UnityEngine.Object.DestroyImmediate(item);
            if (firstTexture != null) UnityEngine.Object.DestroyImmediate(firstTexture);
            if (secondTexture != null) UnityEngine.Object.DestroyImmediate(secondTexture);
        }

        [Test]
        public void EditorAndRuntimeUseIdenticalEndpointSafeFrameOrder()
        {
            CollectionAssert.AreEqual(new[] { 0, 1, 2, 3, 2, 1 },
                VufSpritePlaybackPreview.FrameSequence(4, true));
            CollectionAssert.AreEqual(new[] { 0, 1, 2, 3 },
                VufSpritePlaybackPreview.FrameSequence(4, false));
            CollectionAssert.AreEqual(new[] { 0, 1 },
                VufSpritePlaybackPreview.FrameSequence(2, true));
            CollectionAssert.AreEqual(
                VufSpritePlaybackPreview.FrameSequence(4, true),
                Match3.VisualFactory.Editor.VufSpriteClipBuilderWindow
                    .BuildFrameSequence(4, true));
            Assert.Throws<ArgumentOutOfRangeException>(() =>
                VufSpritePlaybackPreview.FrameSequence(4097, true));
        }

        [Test]
        public void TrueSpriteRendererManualTickPauseResumeAndScrubAreDeterministic()
        {
            preview.Bind(original, 4f, true, false);
            Assert.That(renderer.sprite, Is.SameAs(original[0]));
            Assert.That(preview.ControlsGameplayOrRewards, Is.False);
            preview.Play();
            preview.Advance(.25f);
            Assert.That(renderer.sprite, Is.SameAs(original[1]));
            preview.Pause();
            preview.Advance(2f);
            Assert.That(preview.CurrentFrameIndex, Is.EqualTo(1));
            preview.Play();
            preview.Advance(.25f);
            Assert.That(renderer.sprite, Is.SameAs(original[2]));
            preview.ScrubFrame(3);
            Assert.That(preview.IsPlaying, Is.False);
            Assert.That(renderer.sprite, Is.SameAs(original[3]));
            preview.Replay();
            Assert.That(renderer.sprite, Is.SameAs(original[0]));
            Assert.That(preview.CurrentFrameIndex, Is.Zero);
        }

        [Test]
        public void NonLoopingPingPongStopsAtFinalViewFrameAndReplayIsIndependent()
        {
            preview.Bind(original, 4f, false, true);
            Assert.That(preview.SequenceLength, Is.EqualTo(6));
            preview.Play();
            preview.Advance(1.25f);
            Assert.That(preview.CurrentFrameIndex, Is.EqualTo(1));
            Assert.That(preview.IsPlaying, Is.False);
            preview.Replay();
            Assert.That(renderer.sprite, Is.SameAs(original[0]));
            preview.ScrubSequence(4);
            Assert.That(renderer.sprite, Is.SameAs(original[2]));
            preview.ScrubSequence(5);
            Assert.That(renderer.sprite, Is.SameAs(original[1]));
        }

        [Test]
        public void QuarterToDoubleSpeedChangesOnlyPreviewCursor()
        {
            preview.Bind(original, 4f, true, false);
            preview.Play();
            preview.Advance(.5f, .5f);
            Assert.That(preview.CurrentFrameIndex, Is.EqualTo(1));
            preview.Advance(.125f, 2f);
            Assert.That(preview.CurrentFrameIndex, Is.EqualTo(2));
            preview.Advance(.25f, .25f);
            Assert.That(preview.CurrentFrameIndex, Is.EqualTo(2));
            preview.Advance(.75f, 1f);
            Assert.That(preview.CurrentFrameIndex, Is.EqualTo(1));
        }

        [Test]
        public void AtlasSwapActuallyRebindsSpriteRendererAndPreservesReplayCursor()
        {
            preview.Bind(original, 4f, true, true);
            preview.ScrubSequence(4);
            Assert.That(renderer.sprite, Is.SameAs(original[2]));
            preview.SwapCandidateAtlas(alternate);
            Assert.That(renderer.sprite, Is.SameAs(alternate[2]));
            Assert.That(preview.CurrentFrameIndex, Is.EqualTo(2));
            Assert.That(preview.SequenceLength, Is.EqualTo(6));
            preview.Replay();
            Assert.That(renderer.sprite, Is.SameAs(alternate[0]));
            // Original Sprite objects/importers have not been modified.
            Assert.That(original[2].texture, Is.SameAs(firstTexture));
            Assert.That(alternate[2].texture, Is.SameAs(secondTexture));
        }

        [Test]
        public void InvalidAtlasSwapIsTransactionalAndPreservesCurrentSource()
        {
            preview.Bind(original, 4f, true, false);
            preview.ScrubFrame(1);
            Sprite before = renderer.sprite;
            Sprite mismatch = Sprite.Create(secondTexture,
                new Rect(0, 0, 8, 8), Vector2.zero, 32f);
            try
            {
                var bad = (Sprite[])alternate.Clone();
                bad[1] = mismatch;
                Assert.Throws<ArgumentException>(() =>
                    preview.SwapCandidateAtlas(bad));
                Assert.That(renderer.sprite, Is.SameAs(before));
                Assert.That(preview.CurrentFrameIndex, Is.EqualTo(1));
                Assert.Throws<ArgumentException>(() =>
                    preview.SwapCandidateAtlas(new[] { alternate[0], alternate[1] }));
                Assert.That(renderer.sprite, Is.SameAs(before));
            }
            finally { UnityEngine.Object.DestroyImmediate(mismatch); }
        }

        [Test]
        public void ReducedMotionSnapsAndInterruptionCannotResumeWithoutReplay()
        {
            preview.Bind(original, 4f, true, false);
            preview.Play();
            preview.Advance(.5f);
            preview.SetReducedMotion(true);
            Assert.That(renderer.sprite, Is.SameAs(original[0]));
            Assert.That(preview.IsPlaying, Is.False);
            preview.Play();
            preview.Advance(.75f);
            Assert.That(preview.CurrentFrameIndex, Is.Zero);
            preview.SetReducedMotion(false);
            preview.Play();
            preview.Advance(.25f);
            Assert.That(preview.CurrentFrameIndex, Is.EqualTo(1));
            preview.Interrupt();
            Assert.That(preview.IsInterrupted, Is.True);
            Assert.That(preview.IsPlaying, Is.False);
            Assert.Throws<InvalidOperationException>(() => preview.Play());
            preview.Replay();
            preview.Play();
            preview.Advance(.25f);
            Assert.That(preview.CurrentFrameIndex, Is.EqualTo(1));
        }

        [Test]
        public void InvalidInputsDoNotChangeAlreadyBoundPreviewOrRenderer()
        {
            preview.Bind(original, 12f, true, false);
            Sprite before = renderer.sprite;
            Assert.Throws<ArgumentOutOfRangeException>(() =>
                preview.Advance(float.NaN));
            Assert.Throws<ArgumentOutOfRangeException>(() =>
                preview.Advance(-.1f));
            Assert.Throws<ArgumentOutOfRangeException>(() =>
                preview.Advance(1f, 8f));
            Assert.Throws<ArgumentOutOfRangeException>(() =>
                preview.ScrubSequence(99));
            Assert.Throws<ArgumentException>(() =>
                preview.Bind(new Sprite[] { null, original[1] }, 12f, true, false));
            Assert.That(renderer.sprite, Is.SameAs(before));
            Assert.That(preview.IsBound, Is.True);
        }

        [Test]
        public void LowerPriorityOnSameVisualChannelCannotInterruptOrChangeSprites()
        {
            Assert.That(preview.TryPresentViewEvent(
                "coral_rescue.anim.tile_match", "board_visual", 45,
                original, 4f, true, false), Is.True);
            preview.Advance(.25f);
            Assert.That(renderer.sprite, Is.SameAs(original[1]));
            Sprite before = renderer.sprite;
            Assert.That(preview.TryPresentViewEvent(
                "coral_rescue.anim.tile_spawn", "board_visual", 10,
                alternate, 4f, true, false), Is.False);
            Assert.That(renderer.sprite, Is.SameAs(before));
            Assert.That(preview.VisualPriority, Is.EqualTo(45));
            Assert.That(preview.ViewChannel, Is.EqualTo("board_visual"));
            Assert.That(preview.ViewEventKey, Is.EqualTo("coral_rescue.anim.tile_match"));
            Assert.That(preview.ControlsGameplayOrRewards, Is.False);
            Assert.That(preview.TryPresentViewEvent(
                "coral_rescue.anim.combo_chain", "board_visual", 70,
                alternate, 4f, true, false), Is.True);
            Assert.That(renderer.sprite, Is.SameAs(alternate[0]));
            Assert.That(preview.VisualPriority, Is.EqualTo(70));
            preview.Advance(.25f);
            Assert.That(renderer.sprite, Is.SameAs(alternate[1]));
        }

        [Test]
        public void InvalidViewEventMetadataFailsBeforeChangingCurrentPlayback()
        {
            preview.Bind(original, 4f, true, false);
            Sprite stable = renderer.sprite;
            Assert.Throws<ArgumentException>(() => preview.TryPresentViewEvent(
                "engine.score.write", "gameplay", 100,
                alternate, 4f, true, false));
            Assert.Throws<ArgumentException>(() => preview.TryPresentViewEvent(
                "../private", "board_visual", 40,
                alternate, 4f, true, false));
            Assert.Throws<ArgumentException>(() => preview.TryPresentViewEvent(
                "coral_rescue.anim.tile_match", "board_visual", 101,
                alternate, 4f, true, false));
            Assert.Throws<ArgumentOutOfRangeException>(() => preview.TryPresentViewEvent(
                "coral_rescue.anim.tile_match", "board_visual", 40,
                alternate, float.NaN, true, false));
            Assert.That(renderer.sprite, Is.SameAs(stable));
            Assert.That(preview.IsBound, Is.True);
            Assert.That(preview.ViewEventKey, Is.Null);
            Assert.That(preview.VisualPriority, Is.EqualTo(0));
        }

        [Test]
        public void ClearAndDisableRestoreThePreExistingSpriteWithoutFileWrites()
        {
            preview.Bind(original, 4f, true, false);
            preview.Play();
            preview.Advance(.25f);
            preview.Clear();
            Assert.That(renderer.sprite, Is.SameAs(original[3]));
            Assert.That(preview.IsBound, Is.False);
            Assert.Throws<InvalidOperationException>(() =>
                preview.Play());
            preview.Bind(original, 4f, true, false);
            preview.enabled = false;
            Assert.That(renderer.sprite, Is.SameAs(original[3]));
            Assert.That(preview.IsBound, Is.False);
        }
    }
}
