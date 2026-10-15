using System;
using System.Collections.Generic;
using NUnit.Framework;
using UnityEngine;
using Match3.VisualFactory.Editor;

namespace Match3.VisualFactory.Tests
{
    public class VufCatalogEditModeTests
    {
        private static readonly string[] Profiles =
        {
            "Coral_Rescue", "Garage_Legends", "Dino_Islands",
            "The_Fractured_Realms", "Wonder_Pop"
        };

        [Test]
        public void CoralContractHasExactly28StableNeverApprovedEntries()
        {
            VufScreenCatalog.ScreenInfo[] screens = VufScreenCatalog.LoadScreens();
            Assert.That(screens.Length, Is.EqualTo(28));
            var ids = new HashSet<string>(StringComparer.Ordinal);
            foreach (var screen in screens)
            {
                Assert.That(ids.Add(screen.id), Is.True);
                Assert.That(screen.runtime_ui_required, Is.True);
                Assert.That(screen.available_in_demo, Is.False);
            }
            Assert.That(screens[26].key, Is.EqualTo("home"));
            Assert.That(screens[27].key, Is.EqualTo("gameplay_hud"));
        }

        [Test]
        public void FiveDraftStylePalettesHaveValidFields()
        {
            foreach (string id in Profiles)
            {
                var profile = VufScreenCatalog.LoadStyle(id);
                Assert.That(profile.id, Is.EqualTo(id));
                Assert.That(VufScreenCatalog.ParseColor(
                    profile.palettes.background, "background").a, Is.EqualTo(1f));
                Assert.That(VufScreenCatalog.ParseColor(
                    profile.palettes.cta, "cta").a, Is.EqualTo(1f));
            }
        }

        [Test]
        public void SocialAndPolicyPagesCannotPretendToBeEnabled()
        {
            var screens = VufScreenCatalog.LoadScreens();
            var expectedOff = new HashSet<string> {
                "season_pass", "tournament", "friends", "leaderboard", "events_hub"
            };
            int blocked = 0;
            foreach (var screen in screens)
            {
                if (!expectedOff.Contains(screen.key)) continue;
                Assert.That(screen.feature_gate,
                    Is.EqualTo("OFF_UNTIL_ENGINE_POLICY_CONFIRMED"));
                blocked++;
            }
            Assert.That(blocked, Is.EqualTo(5));
        }

        [Test]
        public void CandidateMarkerDoesNotApproveItself()
        {
            var obj = new GameObject("VUF_TEST_MARKER");
            try
            {
                var marker = obj.AddComponent<VufCandidateScreenMarker>();
                marker.SetCandidate("Coral_Rescue", "COR-27", "home",
                    "page", "REQUIRES_ENGINE_OR_GAME_BINDING");
                Assert.That(marker.ScreenId, Is.EqualTo("COR-27"));
                Assert.That(marker.CandidateStatus, Is.EqualTo("CANDIDATE_NOT_APPROVED"));
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(obj);
            }
        }

        [Test]
        public void SpriteLoopFrameSequenceHasNoDuplicateEdges()
        {
            CollectionAssert.AreEqual(
                new [] {0, 1, 2, 3, 2, 1},
                VufSpriteClipBuilderWindow.BuildFrameSequence(4, true));
            CollectionAssert.AreEqual(
                new [] {0, 1},
                VufSpriteClipBuilderWindow.BuildFrameSequence(2, true));
            CollectionAssert.AreEqual(
                new [] {0, 1, 2},
                VufSpriteClipBuilderWindow.BuildFrameSequence(3, false));
        }

        [Test]
        public void InvalidSpriteFrameSequenceRejected()
        {
            Assert.Throws<ArgumentOutOfRangeException>(
                () => VufSpriteClipBuilderWindow.BuildFrameSequence(1, true));
            Assert.Throws<ArgumentOutOfRangeException>(
                () => VufSpriteClipBuilderWindow.BuildFrameSequence(4097, true));
        }
    }
}
