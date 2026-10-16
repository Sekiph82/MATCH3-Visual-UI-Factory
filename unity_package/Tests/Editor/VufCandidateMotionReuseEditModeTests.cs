using System;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.UI;
using Match3.VisualFactory.Editor;

namespace Match3.VisualFactory.Tests
{
    public sealed class VufCandidateMotionReuseEditModeTests
    {
        private static readonly string[] Pages = { "home", "gameplay", "world_map" };
        private static readonly string[] Targets = {
            "HOME_HeroArtworkPlaceholder",
            "GAMEPLAY_ReadOnlyHUD",
            "WORLD_EditableMapCanvas"
        };

        [Test]
        public void ReusesExistingTweenAcrossAllThreeEditableLayouts()
        {
            for (int i = 0; i < Pages.Length; i++)
            {
                var root = new GameObject("TEST_ONLY_Stage",
                    typeof(RectTransform), typeof(VufSafeAreaFitter));
                try
                {
                    VufPageComposition.Compose(root.transform,
                        VufScreenCatalog.LoadStyle("Wonder_Pop"), Pages[i]);
                    VufUiTween tween = VufCandidateMotionKit.Attach(root.transform, Pages[i]);
                    Assert.That(tween, Is.Not.Null);
                    Assert.That(tween, Is.EqualTo(root.transform.Find(Targets[i])
                        .GetComponent<VufUiTween>()));
                    Assert.That(tween.ReducedMotion, Is.True);
                    Assert.That(tween.IsAnimating, Is.False);
                    CanvasGroup canvas = tween.GetComponent<CanvasGroup>();
                    Assert.That(canvas.alpha, Is.EqualTo(1f));
                    Assert.That(canvas.interactable, Is.False);
                    Assert.That(canvas.blocksRaycasts, Is.False);
                }
                finally { UnityEngine.Object.DestroyImmediate(root); }
            }
        }

        [Test]
        public void ReducedMotionImmediatelyFinalizesWithoutTweening()
        {
            var root = new GameObject("TEST_ONLY_Fade",
                typeof(RectTransform), typeof(VufSafeAreaFitter));
            try
            {
                VufPageComposition.Compose(root.transform,
                    VufScreenCatalog.LoadStyle("Coral_Rescue"), "home");
                VufUiTween tween = VufCandidateMotionKit.Attach(root.transform, "home");
                tween.Hide();
                Assert.That(tween.IsAnimating, Is.False);
                Assert.That(tween.GetComponent<CanvasGroup>().alpha, Is.EqualTo(0f));
                tween.Show();
                Assert.That(tween.IsAnimating, Is.False);
                Assert.That(tween.GetComponent<CanvasGroup>().alpha, Is.EqualTo(1f));
            }
            finally { UnityEngine.Object.DestroyImmediate(root); }
        }

        [Test]
        public void MissingPageOrSecondAttachmentCannotAddDuplicateMotion()
        {
            var root = new GameObject("TEST_ONLY_FailClosed",
                typeof(RectTransform), typeof(VufSafeAreaFitter));
            try
            {
                Assert.Throws<ArgumentException>(() =>
                    VufCandidateMotionKit.Attach(root.transform, "gameplay"));
                VufPageComposition.Compose(root.transform,
                    VufScreenCatalog.LoadStyle("Garage_Legends"), "gameplay");
                VufCandidateMotionKit.Attach(root.transform, "gameplay");
                Assert.Throws<InvalidOperationException>(() =>
                    VufCandidateMotionKit.Attach(root.transform, "gameplay"));
                Assert.Throws<ArgumentException>(() =>
                    VufCandidateMotionKit.Attach(root.transform, "reward"));
                Assert.That(root.GetComponentsInChildren<VufUiTween>().Length, Is.EqualTo(1));
            }
            finally { UnityEngine.Object.DestroyImmediate(root); }
        }
    }
}
