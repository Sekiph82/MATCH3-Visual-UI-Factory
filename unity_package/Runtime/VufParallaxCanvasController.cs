// VUF-M06 | View-only parallax transform preview on externally supplied layers.
// No Engine event subscription, gameplay, inventory, reward or save authority.
// Only the three explicitly bound candidate RectTransforms can be moved.
// No image import/asset write, rights approval or device/GPU claim.
using System;
using System.Collections.Generic;
using UnityEngine;

namespace Match3.VisualFactory.Runtime
{
    [DisallowMultipleComponent]
    public sealed class VufParallaxCanvasController : MonoBehaviour
    {
        private const float FactorEpsilon = 0.00001f;
        private const float OffsetLimit = 4096f;
        private static readonly float[] CandidateFactors = { 0f, 0.12f, 0.34f };
        private RectTransform[] targets;
        private Vector2[] baselines;
        private bool bound;

        public int BoundLayerCount => bound ? CandidateFactors.Length : 0;
        public bool ControlsGameplayOrRewards => false;

        private static bool Finite(float value) =>
            !float.IsNaN(value) && !float.IsInfinity(value);

        /// <summary>
        /// Called by the external visual consumer, never by Match3 rules.
        /// Binds precisely three geometrical candidate layers from background
        /// to near decoration. Does not create GameObjects or edit source art.
        /// </summary>
        public void BindPreviewLayers(RectTransform[] layers, float[] factors)
        {
            if (layers == null || factors == null ||
                layers.Length != CandidateFactors.Length ||
                factors.Length != CandidateFactors.Length)
                throw new ArgumentException("exactly three view-only layer inputs required");
            var seen = new HashSet<RectTransform>();
            for (int i = 0; i < CandidateFactors.Length; i++)
            {
                if (layers[i] == null || !seen.Add(layers[i]) ||
                    !Finite(factors[i]) ||
                    Mathf.Abs(factors[i] - CandidateFactors[i]) > FactorEpsilon)
                    throw new ArgumentException(
                        "missing/duplicate layer or incorrect parallax factor");
            }
            // Validate ALL inputs before touching any prior Transform.
            ResetPreview();
            targets = (RectTransform[])layers.Clone();
            baselines = new Vector2[targets.Length];
            for (int i = 0; i < targets.Length; i++)
                baselines[i] = targets[i].anchoredPosition;
            bound = true;
        }

        public void ApplyPreviewOffset(Vector2 offset)
        {
            if (!bound || targets == null || baselines == null)
                throw new InvalidOperationException("view-only preview layers not bound");
            if (!Finite(offset.x) || !Finite(offset.y) ||
                Mathf.Abs(offset.x) > OffsetLimit ||
                Mathf.Abs(offset.y) > OffsetLimit)
                throw new ArgumentOutOfRangeException(
                    nameof(offset), "preview offset must be finite and bounded");
            for (int i = 0; i < targets.Length; i++)
            {
                if (targets[i] == null)
                {
                    ResetPreview();
                    throw new InvalidOperationException("preview layer was destroyed");
                }
            }
            for (int i = 0; i < targets.Length; i++)
                targets[i].anchoredPosition =
                    baselines[i] - offset * CandidateFactors[i];
        }

        /// <summary>
        /// Restore original positions. No save/reward callbacks are emitted.
        /// Idempotent even if a view-only Unity object was destroyed.
        /// </summary>
        public void ResetPreview()
        {
            if (bound && targets != null && baselines != null)
                for (int i = 0; i < targets.Length; i++)
                    if (targets[i] != null)
                        targets[i].anchoredPosition = baselines[i];
            bound = false;
            targets = null;
            baselines = null;
        }

        private void OnDisable() { ResetPreview(); }
        private void OnDestroy() { ResetPreview(); }
    }
}
