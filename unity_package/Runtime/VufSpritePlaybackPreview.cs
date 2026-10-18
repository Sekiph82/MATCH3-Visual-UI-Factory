// VUF-M07-002/M07-009 | View-only Unity SpriteRenderer animation consumer.
//
// INTERNAL_REUSE: Unity SpriteRenderer, Sprite/Rect and pre-existing
// VUF SpriteClipBuilder's 0..N-1 ping-pong rules. No gameplay events,
// Engine assembly reference, save/reward/purchase hooks or importer writes.
// Ticks are explicit and deterministic; autoplay is intentionally absent.
// Production rights, owner visual approval, device/GPU timing: NOT VERIFIED.
using System;
using System.Collections.Generic;
using UnityEngine;

namespace Match3.VisualFactory
{
    [DisallowMultipleComponent]
    [RequireComponent(typeof(SpriteRenderer))]
    public sealed class VufSpritePlaybackPreview : MonoBehaviour
    {
        private const int MaxFrames = 4096;
        private const double TickEpsilon = 1e-9;

        private SpriteRenderer target;
        private Sprite original;
        private Sprite[] frames;
        private int[] sequence;
        private int cursor;
        private double elapsed;
        private double fps;
        private bool loops;
        private bool reducedMotion;
        private bool playing;
        private bool interrupted;
        private bool bound;

        public bool IsBound => bound;
        public bool IsPlaying => bound && playing;
        public bool IsInterrupted => bound && interrupted;
        public bool ControlsGameplayOrRewards => false;
        public int CurrentFrameIndex => bound ? sequence[cursor] : -1;
        public int SequenceLength => bound ? sequence.Length : 0;
        public double ElapsedFraction => bound ? elapsed * fps : 0d;

        // Single shared frame order for Editor clip authoring and Runtime
        // view-only scene preview. Ping-pong does not duplicate endpoints.
        public static int[] FrameSequence(int count, bool pingPong)
        {
            if (count < 2 || count > MaxFrames)
                throw new ArgumentOutOfRangeException(nameof(count));
            var entries = new List<int>(count * (pingPong ? 2 : 1));
            for (int i = 0; i < count; ++i) entries.Add(i);
            if (pingPong)
                for (int i = count - 2; i > 0; --i) entries.Add(i);
            return entries.ToArray();
        }

        private static bool ValidNumber(float number) =>
            !float.IsNaN(number) && !float.IsInfinity(number);

        private static void ValidateFrames(Sprite[] source, int expectedCount = -1)
        {
            if (source == null || source.Length < 2 ||
                source.Length > MaxFrames ||
                (expectedCount >= 0 && source.Length != expectedCount))
                throw new ArgumentException(
                    "View-only preview needs 2..4096 frames with stable count.");
            foreach (Sprite frame in source)
            {
                if (frame == null || frame.rect.width <= 0 ||
                    frame.rect.height <= 0 || frame.pixelsPerUnit <= 0 ||
                    !ValidNumber(frame.pixelsPerUnit))
                    throw new ArgumentException("Null or malformed Sprite source.");
            }
        }

        public void Bind(Sprite[] source, float framesPerSecond,
                         bool loop, bool pingPong, bool reduceMotion = false)
        {
            ValidateFrames(source);
            if (!ValidNumber(framesPerSecond) ||
                framesPerSecond < 1f || framesPerSecond > 60f)
                throw new ArgumentOutOfRangeException(nameof(framesPerSecond));

            int[] planned = FrameSequence(source.Length, pingPong);
            // Validate BEFORE mutating any previously bound frame/renderer.
            var copy = (Sprite[])source.Clone();
            if (bound) Clear();
            target = GetComponent<SpriteRenderer>();
            if (target == null)
                throw new InvalidOperationException("SpriteRenderer missing.");
            original = target.sprite;
            frames = copy;
            sequence = planned;
            fps = framesPerSecond;
            loops = loop;
            reducedMotion = reduceMotion;
            playing = false;
            interrupted = false;
            elapsed = 0;
            cursor = 0;
            bound = true;
            target.sprite = frames[0];
        }

        public void Play()
        {
            RequireBound();
            if (interrupted) throw new InvalidOperationException(
                "An interrupted preview needs Replay before Play.");
            // Repeated calls do not reset or duplicate a view event.
            if (!reducedMotion) playing = true;
        }

        public void Pause()
        {
            RequireBound();
            playing = false;
        }

        public void SetReducedMotion(bool value)
        {
            RequireBound();
            reducedMotion = value;
            if (value)
            {
                playing = false;
                elapsed = 0;
                cursor = 0;
                target.sprite = frames[sequence[0]];
            }
        }

        public void Replay()
        {
            RequireBound();
            playing = false;
            interrupted = false;
            elapsed = 0;
            cursor = 0;
            target.sprite = frames[sequence[0]];
        }

        // Interruption never plays a reward/sound, calls an Engine hook
        // or changes a Sprite/Texture importer.
        public void Interrupt()
        {
            RequireBound();
            playing = false;
            interrupted = true;
            elapsed = 0;
        }

        public void ScrubSequence(int requestedCursor)
        {
            RequireBound();
            if (requestedCursor < 0 || requestedCursor >= sequence.Length)
                throw new ArgumentOutOfRangeException(nameof(requestedCursor));
            playing = false;
            interrupted = false;
            cursor = requestedCursor;
            elapsed = 0;
            target.sprite = frames[sequence[cursor]];
        }

        public void ScrubFrame(int frameIndex)
        {
            RequireBound();
            if (frameIndex < 0 || frameIndex >= frames.Length)
                throw new ArgumentOutOfRangeException(nameof(frameIndex));
            // First timeline occurrence is deterministic for ping-pong.
            int found = Array.IndexOf(sequence, frameIndex);
            ScrubSequence(found);
        }

        public void Advance(float seconds, float previewSpeed = 1f)
        {
            RequireBound();
            if (!ValidNumber(seconds) || seconds < 0f || seconds > 300f)
                throw new ArgumentOutOfRangeException(nameof(seconds));
            if (previewSpeed != .25f && previewSpeed != .5f &&
                previewSpeed != 1f && previewSpeed != 2f)
                throw new ArgumentOutOfRangeException(nameof(previewSpeed));
            if (!playing || interrupted || reducedMotion || seconds == 0f)
                return;
            elapsed += (double)seconds * previewSpeed;
            double countDouble = Math.Floor(elapsed * fps + TickEpsilon);
            if (countDouble < 1d) return;
            int stepCount = (int)Math.Min(countDouble, int.MaxValue);
            elapsed -= stepCount / fps;
            elapsed = Math.Max(0d, elapsed);
            if (loops)
            {
                cursor = (int)((cursor + (long)stepCount) % sequence.Length);
            }
            else
            {
                int remaining = sequence.Length - 1 - cursor;
                if (stepCount >= remaining)
                {
                    cursor = sequence.Length - 1;
                    elapsed = 0d;
                    playing = false;
                }
                else cursor += stepCount;
            }
            target.sprite = frames[sequence[cursor]];
        }

        // A real atlas/texture swap is allowed only on imported Sprite
        // objects with matching frame geometry. Never edits source importers.
        // Invalid swaps are transactional: original frames remain active.
        public void SwapCandidateAtlas(Sprite[] replacement)
        {
            RequireBound();
            ValidateFrames(replacement, frames.Length);
            for (int i = 0; i < frames.Length; i++)
            {
                Sprite oldFrame = frames[i], newFrame = replacement[i];
                if (Mathf.Abs(oldFrame.rect.width - newFrame.rect.width) > .01f ||
                    Mathf.Abs(oldFrame.rect.height - newFrame.rect.height) > .01f ||
                    Mathf.Abs(oldFrame.pixelsPerUnit - newFrame.pixelsPerUnit) > .0001f ||
                    Mathf.Abs(oldFrame.pivot.x / oldFrame.rect.width -
                              newFrame.pivot.x / newFrame.rect.width) > .0001f ||
                    Mathf.Abs(oldFrame.pivot.y / oldFrame.rect.height -
                              newFrame.pivot.y / newFrame.rect.height) > .0001f)
                    throw new ArgumentException(
                        "Frame/PPU/normalized pivot mismatch; atlas swap refused.");
            }
            frames = (Sprite[])replacement.Clone();
            target.sprite = frames[sequence[cursor]];
        }

        public void Clear()
        {
            if (bound && target != null) target.sprite = original;
            frames = null;
            sequence = null;
            original = null;
            target = null;
            elapsed = 0d;
            cursor = 0;
            playing = false;
            interrupted = false;
            bound = false;
        }

        private void RequireBound()
        {
            if (!bound || target == null || frames == null)
                throw new InvalidOperationException(
                    "Preview requires explicitly bound candidate Sprites.");
        }

        private void OnDisable() { Clear(); }
        private void OnDestroy() { Clear(); }
    }
}
