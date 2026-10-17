// VF-07 / R43: reuse the *existing* R35-R42 licensed donor-backed
// composition/motif/motion modules in the original 28-screen shell builder.
// No new layout algorithm, copied source, game bindings or asset writes.
using System;
using UnityEngine;
using UnityEngine.UI;
using Match3.VisualFactory.Editor.ThirdParty;

namespace Match3.VisualFactory.Editor
{
    internal static class VufScreenShellLayoutBridge
    {
        internal static void Enhance(GameObject root,
            VufScreenCatalog.ScreenInfo screen,
            VufScreenCatalog.StyleInfo style)
        {
            if (root == null || screen == null || style == null ||
                style.palettes == null)
                throw new ArgumentException("missing original owner-unapproved shell");
            VufCandidateScreenMarker marker =
                root.GetComponent<VufCandidateScreenMarker>();
            Transform safe = root.transform.Find("SafeArea_ReviewOnly");
            if (marker == null || safe == null ||
                safe.GetComponent<VufSafeAreaFitter>() == null ||
                marker.CandidateStatus != "CANDIDATE_NOT_APPROVED" ||
                marker.ProfileId != style.id ||
                marker.ScreenId != screen.id ||
                marker.ScreenKey != screen.key ||
                marker.FeatureGate != screen.feature_gate ||
                (screen.feature_gate != "REQUIRES_ENGINE_OR_GAME_BINDING" &&
                 screen.feature_gate != "OFF_UNTIL_ENGINE_POLICY_CONFIRMED"))
                throw new ArgumentException("shell identity/rights/feature gate changed");
            if (safe.Find("ThemeMotifs_" + style.id) != null ||
                safe.Find("VUF_28ScreenInputShield") != null)
                throw new InvalidOperationException("shell already enhanced");

            // Use the five game-specific mathematically generated editable
            // art motifs on all 28 draft pages (not final licensed art).
            VufThemeMotifDecor.Apply(safe, style);

            // Reuse one of three established page-specific real uGUI
            // compositions only when the actual Coral contract supports it.
            string page = null;
            if (screen.key == "home") page = "home";
            else if (screen.key == "world_map") page = "world_map";
            else if (screen.key == "gameplay_hud" ||
                     screen.key == "endless_mode" ||
                     screen.key == "time_attack")
                page = "gameplay";
            if (page != null)
            {
                VufPageComposition.Compose(safe, style, page);
                // Attach the existing VufUiTween with reduced motion ON,
                // never implement another easing/timing mechanism.
                VufCandidateMotionKit.Attach(safe, page);
            }

            // Reuse the exact BSD3 UIExtensions NonDrawingGraphic primitive
            // for the final raycast blocking layer. This is *not* visible
            // and never activates disabled or policy-locked actions.
            GameObject blocker = new GameObject("VUF_28ScreenInputShield",
                typeof(RectTransform), typeof(NonDrawingGraphic));
            RectTransform rect = blocker.GetComponent<RectTransform>();
            rect.SetParent(safe, false);
            rect.anchorMin = Vector2.zero;
            rect.anchorMax = Vector2.one;
            rect.offsetMin = Vector2.zero;
            rect.offsetMax = Vector2.zero;
            NonDrawingGraphic shield = blocker.GetComponent<NonDrawingGraphic>();
            shield.raycastTarget = true;
        }
    }
}
