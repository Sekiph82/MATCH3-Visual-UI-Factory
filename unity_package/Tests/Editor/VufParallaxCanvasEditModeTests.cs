// VUF-M06: real isolated RectTransform candidate parallax EditMode tests.
// These tests never instantiate a Match3 board or claim device/GUI/art PASS.
using System;
using NUnit.Framework;
using UnityEngine;
using Match3.VisualFactory.Runtime;

namespace Match3.VisualFactory.Tests
{
    public sealed class VufParallaxCanvasEditModeTests
    {
        private GameObject host;
        private RectTransform[] layers;
        private VufParallaxCanvasController controller;

        [SetUp]
        public void SetUp()
        {
            host = new GameObject("candidate-view-only-host",
                                  typeof(RectTransform),
                                  typeof(VufParallaxCanvasController));
            controller = host.GetComponent<VufParallaxCanvasController>();
            layers = new RectTransform[3];
            for (int i = 0; i < 3; i++)
            {
                var layer = new GameObject("candidate-layer-" + i,
                                            typeof(RectTransform));
                layer.transform.SetParent(host.transform, false);
                layers[i] = layer.GetComponent<RectTransform>();
                layers[i].anchoredPosition = new Vector2(5f + i, 10f + i);
            }
        }

        [TearDown]
        public void TearDown()
        {
            if (host != null) UnityEngine.Object.DestroyImmediate(host);
        }

        [Test]
        public void ExactThreeLayerFactorsMoveOnlyCandidateTransforms()
        {
            controller.BindPreviewLayers(layers, new[] { 0f, .12f, .34f });
            Assert.That(controller.BoundLayerCount, Is.EqualTo(3));
            Assert.That(controller.ControlsGameplayOrRewards, Is.False);
            controller.ApplyPreviewOffset(new Vector2(100f, 50f));
            Assert.That(layers[0].anchoredPosition, Is.EqualTo(new Vector2(5f, 10f)));
            Assert.That(layers[1].anchoredPosition,
                        Is.EqualTo(new Vector2(6f - 12f, 11f - 6f)).Using(Vector2Comparer.Instance));
            Assert.That(layers[2].anchoredPosition,
                        Is.EqualTo(new Vector2(7f - 34f, 12f - 17f)).Using(Vector2Comparer.Instance));
        }

        [Test]
        public void PreviewResetRestoresOriginalPositionsExactly()
        {
            Vector2[] before = { layers[0].anchoredPosition,
                                 layers[1].anchoredPosition,
                                 layers[2].anchoredPosition };
            controller.BindPreviewLayers(layers, new[] { 0f, .12f, .34f });
            controller.ApplyPreviewOffset(new Vector2(-55f, 75f));
            controller.ResetPreview();
            controller.ResetPreview();
            Assert.That(controller.BoundLayerCount, Is.Zero);
            for (int i = 0; i < 3; i++)
                Assert.That(layers[i].anchoredPosition, Is.EqualTo(before[i]));
        }

        [Test]
        public void DuplicateNullAndFalseFactorInputCannotBind()
        {
            Assert.Throws<ArgumentException>(() =>
                controller.BindPreviewLayers(null, new[] { 0f, .12f, .34f }));
            Assert.Throws<ArgumentException>(() =>
                controller.BindPreviewLayers(new RectTransform[] { layers[0], null, layers[2] },
                                             new[] { 0f, .12f, .34f }));
            Assert.Throws<ArgumentException>(() =>
                controller.BindPreviewLayers(new[] { layers[0], layers[0], layers[2] },
                                             new[] { 0f, .12f, .34f }));
            Assert.Throws<ArgumentException>(() =>
                controller.BindPreviewLayers(layers, new[] { 0f, .99f, .34f }));
            Assert.That(controller.BoundLayerCount, Is.Zero);
        }

        [Test]
        public void UnboundInvalidAndNonfiniteOffsetsNeverMutateTransforms()
        {
            Assert.Throws<InvalidOperationException>(() =>
                controller.ApplyPreviewOffset(new Vector2(10f, 20f)));
            controller.BindPreviewLayers(layers, new[] { 0f, .12f, .34f });
            Vector2 stable = layers[1].anchoredPosition;
            Assert.Throws<ArgumentOutOfRangeException>(() =>
                controller.ApplyPreviewOffset(new Vector2(float.NaN, 0f)));
            Assert.Throws<ArgumentOutOfRangeException>(() =>
                controller.ApplyPreviewOffset(new Vector2(5000f, 0f)));
            Assert.That(layers[1].anchoredPosition, Is.EqualTo(stable));
        }

        [Test]
        public void RebindingAfterOffsetResetsEarlierThreeLayerPreview()
        {
            Vector2 old = layers[1].anchoredPosition;
            controller.BindPreviewLayers(layers, new[] { 0f, .12f, .34f });
            controller.ApplyPreviewOffset(new Vector2(100f, 100f));
            controller.BindPreviewLayers(layers, new[] { 0f, .12f, .34f });
            Assert.That(layers[1].anchoredPosition, Is.EqualTo(old));
            controller.ApplyPreviewOffset(Vector2.zero);
            Assert.That(layers[1].anchoredPosition, Is.EqualTo(old));
        }

        private sealed class Vector2Comparer : System.Collections.IComparer
        {
            internal static readonly Vector2Comparer Instance = new Vector2Comparer();

            public int Compare(object lhs, object rhs)
            {
                if (!(lhs is Vector2) || !(rhs is Vector2)) return -1;
                Vector2 a = (Vector2)lhs, b = (Vector2)rhs;
                return Vector2.Distance(a, b) < 0.0001f ? 0 : -1;
            }
        }
    }
}
