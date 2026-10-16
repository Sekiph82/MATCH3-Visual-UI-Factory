using System;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.UI;
using Match3.VisualFactory.Editor;

namespace Match3.VisualFactory.Tests
{
    public sealed class VufReviewStateEditModeTests
    {
        private static Text FindText(GameObject root, string name)
        {
            foreach (Text text in root.GetComponentsInChildren<Text>(true))
                if (text.name == name) return text;
            Assert.Fail("Missing review-only text slot: " + name);
            return null;
        }

        [Test]
        public void AllCoralScreensKeepActionsUnboundInEightStatesAndThreeMockLocales()
        {
            var screens = VufScreenCatalog.LoadScreens();
            var style = VufScreenCatalog.LoadStyle("Coral_Rescue");
            int reviewed = 0;
            foreach (var contract in screens)
            {
                var root = VufScreenShellBuilderWindow.BuildCandidateHierarchy(
                    contract, style, true);
                try
                {
                    string gateOriginal = FindText(root, "FeatureGate_AlwaysVisible").text;
                    foreach (string state in VufReviewStateCatalog.States)
                    foreach (string locale in VufReviewStateCatalog.Locales)
                    {
                        VufReviewStateCatalog.Apply(root, contract, state, locale);
                        var marker = root.GetComponent<VufCandidateScreenMarker>();
                        Assert.That(marker.CandidateStatus,
                            Is.EqualTo("CANDIDATE_NOT_APPROVED"));
                        Assert.That(marker.FeatureGate, Is.EqualTo(contract.feature_gate));
                        Assert.That(FindText(root, "ReviewState_AlwaysVisible").text,
                            Does.Contain("NOT GAME STATE"));
                        Assert.That(FindText(root, "FeatureGate_AlwaysVisible").text,
                            Is.EqualTo(gateOriginal));
                        foreach (Button button in root.GetComponentsInChildren<Button>(true))
                        {
                            Assert.That(button.interactable, Is.False);
                            Assert.That(button.onClick.GetPersistentEventCount(), Is.Zero);
                        }
                        reviewed++;
                    }
                }
                finally
                {
                    UnityEngine.Object.DestroyImmediate(root);
                }
            }
            Assert.That(reviewed, Is.EqualTo(28 * 8 * 3));
        }

        [Test]
        public void UnknownStatesAndLocalesCannotAlterExistingCopy()
        {
            var screen = VufScreenCatalog.LoadScreens()[26];
            var style = VufScreenCatalog.LoadStyle("Coral_Rescue");
            var root = VufScreenShellBuilderWindow.BuildCandidateHierarchy(
                screen, style, false);
            try
            {
                string baseline = FindText(root, "Heading").text;
                Assert.Throws<ArgumentException>(() =>
                    VufReviewStateCatalog.Apply(root, screen, "RewardGranted", "en"));
                Assert.Throws<ArgumentException>(() =>
                    VufReviewStateCatalog.Apply(root, screen, "Ready", "production"));
                Assert.That(FindText(root, "Heading").text, Is.EqualTo(baseline));
                VufReviewStateCatalog.Apply(root, screen, "Offline", "tr");
                Assert.That(FindText(root, "Heading").text, Is.EqualTo("Ana Sayfa"));
                Assert.That(FindText(root, "ActionLabel").text, Is.EqualTo("BAGLI DEGIL"));
                Assert.That(FindText(root, "ReviewState_AlwaysVisible").text,
                    Does.Contain("OFFLINE"));
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(root);
            }
        }

        [Test]
        public void MockCopyPreservesFiveDistinctTitleStylePalettes()
        {
            var home = VufScreenCatalog.LoadScreens()[26];
            string[] profiles = {
                "Coral_Rescue", "Garage_Legends", "Dino_Islands",
                "The_Fractured_Realms", "Wonder_Pop"
            };
            foreach (string id in profiles)
            {
                var root = VufScreenShellBuilderWindow.BuildCandidateHierarchy(
                    home, VufScreenCatalog.LoadStyle(id), false);
                try
                {
                    Image[] images = root.GetComponentsInChildren<Image>(true);
                    var saved = new Color[images.Length];
                    for (int i = 0; i < images.Length; i++) saved[i] = images[i].color;
                    VufReviewStateCatalog.Apply(root, home, "Pending", "stress");
                    Assert.That(root.GetComponent<VufCandidateScreenMarker>().ProfileId,
                        Is.EqualTo(id));
                    for (int i = 0; i < images.Length; i++)
                        Assert.That(images[i].color, Is.EqualTo(saved[i]));
                    Assert.That(FindText(root, "Heading").text,
                        Does.StartWith("[EXPANDED TEXT QA]"));
                }
                finally
                {
                    UnityEngine.Object.DestroyImmediate(root);
                }
            }
        }
    }
}
