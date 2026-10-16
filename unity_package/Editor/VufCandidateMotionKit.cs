// VF-05 R38: extend existing tested VufUiTween, not another tween engine.
// Adds metadata-safe authoring motion to editable candidate uGUI panels.
// Runtime logic remains in existing VufUiTween; no new easing algorithms.
using System;
using UnityEngine;
using UnityEngine.UI;
using Match3.VisualFactory;

namespace Match3.VisualFactory.Editor
{
    internal static class VufCandidateMotionKit
    {
        private static readonly string[] Pages = { "home", "gameplay", "world_map" };
        private static readonly string[] TargetNames = {
            "HOME_HeroArtworkPlaceholder",
            "GAMEPLAY_ReadOnlyHUD",
            "WORLD_EditableMapCanvas"
        };

        internal static VufUiTween Attach(Transform safeArea, string page)
        {
            int index = Array.IndexOf(Pages, page);
            if (safeArea == null || index < 0 ||
                safeArea.GetComponent<VufSafeAreaFitter>() == null)
                throw new ArgumentException("motion preview requires known candidate safe area");
            Transform target = safeArea.Find(TargetNames[index]);
            if (target == null || target.GetComponent<RectTransform>() == null)
                throw new ArgumentException("missing real editable authoring panel");
            if (target.GetComponent<VufUiTween>() != null ||
                target.GetComponent<CanvasGroup>() != null)
                throw new InvalidOperationException("candidate motion already exists");

            // Same small established VUF primitive used throughout Factory,
            // with reduced motion ON by default. No actual game animations
            // are triggered and no callbacks or rewards are wired.
            CanvasGroup group = target.gameObject.AddComponent<CanvasGroup>();
            VufUiTween tween = target.gameObject.AddComponent<VufUiTween>();
            tween.SetReducedMotion(true);
            group.alpha = 1f;
            group.interactable = false;
            group.blocksRaycasts = false;
            return tween;
        }
    }
}
