// VUF-M10-001..006 source-only Unity Editor candidate slice tests.
// NOT MATCH3 Engine/LFX integration or actual gameplay/PlayMode/device QA.
using System;
using System.Linq;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.UI;
using Match3.VisualFactory.Editor;

namespace Match3.VisualFactory.Tests
{
    public sealed class VufM10VerticalSliceEditModeTests
    {
        [Test]
        public void AllFiveProfilesHaveSourceOnlyVerticalRoutesAndCoralOnlyExtra()
        {
            Assert.That(VufM10VerticalSliceStudio.Profiles.Length, Is.EqualTo(5));
            foreach (var profile in VufM10VerticalSliceStudio.Profiles)
            {
                var routes = VufM10VerticalSliceStudio.RouteForProfile(profile);
                Assert.That(routes[0], Is.EqualTo("home"));
                Assert.That(routes[3], Is.EqualTo("gameplay_hud"));
                Assert.That(routes, Does.Contain("level_won"));
                Assert.That(routes, Does.Contain("daily_rewards"));
                Assert.That(routes, Does.Contain("shop"));
                Assert.That(routes, Does.Contain("offline"));
                Assert.That(routes.Length,
                    Is.EqualTo(profile == "Coral_Rescue" ? 12 : 9));
            }
        }

        [Test]
        public void ExactCoralScreenKeysAreNotInventedWhenOfflineMockIsShown()
        {
            var screens = VufScreenCatalog.LoadScreens();
            var home = VufM10VerticalSliceStudio.ResolveCoralDraftRoute(
                screens, "home");
            var board = VufM10VerticalSliceStudio.ResolveCoralDraftRoute(
                screens, "gameplay_hud");
            var offline = VufM10VerticalSliceStudio.ResolveCoralDraftRoute(
                screens, "offline");
            Assert.That(home.id, Is.EqualTo("COR-27"));
            Assert.That(board.id, Is.EqualTo("COR-28"));
            Assert.That(offline.id, Is.EqualTo("COR-22"));
            Assert.That(offline.key, Is.EqualTo("splash_loading"));
            Assert.Throws<ArgumentException>(() =>
                VufM10VerticalSliceStudio.ResolveCoralDraftRoute(
                    screens, "tournament"));
            Assert.Throws<ArgumentException>(() =>
                VufM10VerticalSliceStudio.ResolveCoralDraftRoute(
                    screens, "fabricated_screen"));
        }

        [Test]
        public void FiveDraftThemeSkinsBuildActualNoSaveUnityUguiDisabledGameButtons()
        {
            foreach (var profile in VufM10VerticalSliceStudio.Profiles)
            {
                var page = VufM10VerticalSliceStudio.CreateCandidate(
                    profile, "home", "Ready", "en");
                try
                {
                    Assert.That(page.GetComponent<Canvas>(), Is.Not.Null);
                    var marker = page.GetComponent<VufCandidateScreenMarker>();
                    Assert.That(marker.ProfileId, Is.EqualTo(profile));
                    Assert.That(marker.ScreenId, Is.EqualTo("COR-27"));
                    Assert.That(marker.CandidateStatus, Is.EqualTo(
                        "CANDIDATE_NOT_APPROVED"));
                    Assert.That(page.hideFlags & HideFlags.DontSaveInEditor,
                        Is.Not.EqualTo(HideFlags.None));
                    var buttons = page.GetComponentsInChildren<Button>(true);
                    Assert.That(buttons.Length, Is.EqualTo(1));
                    Assert.That(buttons[0].interactable, Is.False);
                    Assert.That(buttons[0].onClick.GetPersistentEventCount(), Is.Zero);
                }
                finally { UnityEngine.Object.DestroyImmediate(page); }
            }
        }

        [Test]
        public void OfflineStepUsesActualUnconnectedOfflineMockNotNetworkOrAwards()
        {
            var page = VufM10VerticalSliceStudio.CreateCandidate(
                "Coral_Rescue", "offline", "Ready", "tr");
            try
            {
                var labels = page.GetComponentsInChildren<Text>(true);
                Assert.That(labels.Any(t => t.text.Contains("Offline") ||
                    t.text.Contains("OFFLINE")), Is.True);
                Assert.That(page.GetComponent<VufCandidateScreenMarker>()
                    .ScreenId, Is.EqualTo("COR-22"));
                Assert.That(page.GetComponentsInChildren<Button>(true)[0].interactable,
                    Is.False);
            }
            finally { UnityEngine.Object.DestroyImmediate(page); }
        }

        [Test]
        public void FrozenReferenceIsUnchangedWhenOnlyThemeAssetsOrColorsSwap()
        {
            var a = VufM10VerticalSliceStudio.FrozenMockReference(
                "Coral_Rescue", 11, 42);
            var b = VufM10VerticalSliceStudio.FrozenMockReference(
                "Coral_Rescue", 11, 42);
            Assert.That(a, Is.EqualTo(b));
            Assert.That(a, Does.Contain("actualScore=NONE"));
            Assert.That(a, Does.Contain("actualWin=NONE"));
            Assert.That(a, Does.Contain("productionReplay=UNVERIFIED"));
            Assert.That(a, Does.Not.Contain("RELEASE_APPROVED"));
        }

        [Test]
        public void FakeGameNamesAndInvalidMockLevelSeedsAlwaysReject()
        {
            Assert.Throws<ArgumentException>(() =>
                VufM10VerticalSliceStudio.RouteForProfile("Unknown_Game"));
            Assert.Throws<ArgumentException>(() =>
                VufM10VerticalSliceStudio.FrozenMockReference(
                    "Coral_Rescue", 0, 42));
            Assert.Throws<ArgumentException>(() =>
                VufM10VerticalSliceStudio.FrozenMockReference(
                    "Coral_Rescue", 11, -3));
        }

        [Test]
        public void OpaqueExternalBytesDigestIsBoundedAndNotAnLfxSchemaProof()
        {
            Assert.That(VufM10VerticalSliceStudio.SourceSha(
                new byte[]{1, 2, 3}), Is.EqualTo(
                "039058c6f2c0cb492c533b0a4d14ef77cc0f78abccced5287d84a1a2011cfb81"));
            Assert.Throws<ArgumentException>(() =>
                VufM10VerticalSliceStudio.SourceSha(null));
            Assert.Throws<ArgumentException>(() =>
                VufM10VerticalSliceStudio.SourceSha(new byte[0]));
        }

        [Test]
        public void BorrowedCoralReefAndAquariumAreNeverOtherGameRoutes()
        {
            var coral = VufM10VerticalSliceStudio.RouteForProfile("Coral_Rescue");
            var dino = VufM10VerticalSliceStudio.RouteForProfile("Dino_Islands");
            Assert.That(coral, Does.Contain("reef_restoration"));
            Assert.That(coral, Does.Contain("my_aquarium"));
            Assert.That(coral, Does.Contain("region_unlocked"));
            Assert.That(dino, Does.Not.Contain("reef_restoration"));
            Assert.That(dino, Does.Not.Contain("my_aquarium"));
            Assert.That(dino, Does.Not.Contain("region_unlocked"));
            Assert.Throws<ArgumentException>(() =>
                VufM10VerticalSliceStudio.CreateCandidate(
                    "Dino_Islands", "reef_restoration", "Ready", "en"));
        }
    }
}
