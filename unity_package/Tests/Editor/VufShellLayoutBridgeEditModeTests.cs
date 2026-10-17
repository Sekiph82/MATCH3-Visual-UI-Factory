using System;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.UI;
using Match3.VisualFactory.Editor;
using Match3.VisualFactory.Editor.ThirdParty;

namespace Match3.VisualFactory.Tests
{
    public sealed class VufShellLayoutBridgeEditModeTests
    {
        private static readonly string[] Profiles = {
            "Coral_Rescue", "Garage_Legends", "Dino_Islands",
            "The_Fractured_Realms", "Wonder_Pop"
        };

        [Test]
        public void AllFiveThemesAndTwentyEightCoralShellsReuseRealDonorComponents()
        {
            var screens = VufScreenCatalog.LoadScreens();
            int inspected = 0;
            foreach (string profile in Profiles)
            foreach (var screen in screens)
            {
                var root = VufScreenShellBuilderWindow.BuildCandidateHierarchy(
                    screen, VufScreenCatalog.LoadStyle(profile), true);
                try
                {
                    Transform safe = root.transform.Find("SafeArea_ReviewOnly");
                    Assert.That(safe, Is.Not.Null);
                    Assert.That(safe.Find("ThemeMotifs_" + profile), Is.Not.Null);
                    var shield = safe.Find("VUF_28ScreenInputShield");
                    Assert.That(shield, Is.Not.Null);
                    Assert.That(shield.GetSiblingIndex(),
                        Is.EqualTo(safe.childCount - 1));
                    Assert.That(shield.GetComponent<NonDrawingGraphic>().raycastTarget,
                        Is.True);
                    var marker = root.GetComponent<VufCandidateScreenMarker>();
                    Assert.That(marker.CandidateStatus,
                        Is.EqualTo("CANDIDATE_NOT_APPROVED"));
                    Assert.That(marker.FeatureGate, Is.EqualTo(screen.feature_gate));
                    var buttons = root.GetComponentsInChildren<Button>(true);
                    Assert.That(buttons.Length, Is.EqualTo(1));
                    Assert.That(buttons[0].interactable, Is.False);
                    Assert.That(buttons[0].onClick.GetPersistentEventCount(), Is.Zero);
                    inspected++;
                }
                finally { UnityEngine.Object.DestroyImmediate(root); }
            }
            Assert.That(inspected, Is.EqualTo(140));
        }

        [Test]
        public void ThreeInteractiveLookingScreensRemainPurelyVisualCandidates()
        {
            var screens = VufScreenCatalog.LoadScreens();
            var style = VufScreenCatalog.LoadStyle("Coral_Rescue");
            foreach (string key in new [] {
                "home", "world_map", "gameplay_hud",
                "endless_mode", "time_attack"
            })
            {
                var chosen = Array.Find(screens, entry => entry.key == key);
                Assert.That(chosen, Is.Not.Null);
                var root = VufScreenShellBuilderWindow.BuildCandidateHierarchy(
                    chosen, style, true);
                try
                {
                    Transform safe = root.transform.Find("SafeArea_ReviewOnly");
                    string target = key == "home" ? "HOME_HeroArtworkPlaceholder" :
                        key == "world_map" ? "WORLD_EditableMapCanvas" :
                        "GAMEPLAY_Grid6x7_VISUAL_ONLY";
                    var node = safe.Find(target);
                    Assert.That(node, Is.Not.Null, "missing real editable stage " + key);
                    Assert.That(root.GetComponent<VufCandidateScreenMarker>().FeatureGate,
                        Is.EqualTo("REQUIRES_ENGINE_OR_GAME_BINDING"));
                    Assert.That(root.GetComponentsInChildren<VufUiTween>(true).Length,
                        Is.GreaterThanOrEqualTo(1));
                    foreach (Button button in root.GetComponentsInChildren<Button>(true))
                        Assert.That(button.interactable, Is.False);
                }
                finally { UnityEngine.Object.DestroyImmediate(root); }
            }
        }

        [Test]
        public void PolicyLockedSocialPagesNeverGainRealInteraction()
        {
            var screens = VufScreenCatalog.LoadScreens();
            int blocked = 0;
            foreach (var entry in screens)
            {
                if (entry.feature_gate != "OFF_UNTIL_ENGINE_POLICY_CONFIRMED")
                    continue;
                var root = VufScreenShellBuilderWindow.BuildCandidateHierarchy(
                    entry, VufScreenCatalog.LoadStyle("Wonder_Pop"), true);
                try
                {
                    Assert.That(root.GetComponent<VufCandidateScreenMarker>().FeatureGate,
                        Is.EqualTo("OFF_UNTIL_ENGINE_POLICY_CONFIRMED"));
                    foreach (var btn in root.GetComponentsInChildren<Button>(true))
                        Assert.That(btn.interactable, Is.False);
                    Assert.That(root.GetComponentInChildren<NonDrawingGraphic>(),
                        Is.Not.Null);
                    blocked++;
                }
                finally { UnityEngine.Object.DestroyImmediate(root); }
            }
            Assert.That(blocked, Is.EqualTo(5));
        }

        [Test]
        public void EnhancementCannotBeAppliedTwiceOrUsedWithForgedIdentity()
        {
            var screen = VufScreenCatalog.LoadScreens()[26];
            var style = VufScreenCatalog.LoadStyle("Garage_Legends");
            var root = VufScreenShellBuilderWindow.BuildCandidateHierarchy(
                screen, style, true);
            try
            {
                Assert.Throws<InvalidOperationException>(() =>
                    VufScreenShellLayoutBridge.Enhance(root, screen, style));
                var wrong = VufScreenCatalog.LoadScreens()[0];
                Assert.Throws<ArgumentException>(() =>
                    VufScreenShellLayoutBridge.Enhance(root, wrong, style));
                Assert.That(root.GetComponentsInChildren<NonDrawingGraphic>().Length,
                    Is.EqualTo(1));
            }
            finally { UnityEngine.Object.DestroyImmediate(root); }
        }
    }
}
