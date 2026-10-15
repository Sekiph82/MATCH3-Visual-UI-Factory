using System;
using System.Collections.Generic;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;
using UnityEngine.UI;
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
            var backgrounds = new HashSet<string>(StringComparer.Ordinal);
            var accents = new HashSet<string>(StringComparer.Ordinal);
            foreach (string id in Profiles)
            {
                var profile = VufScreenCatalog.LoadStyle(id);
                Assert.That(profile.id, Is.EqualTo(id));
                Assert.That(backgrounds.Add(profile.palettes.background), Is.True);
                Assert.That(accents.Add(profile.palettes.accent), Is.True);
                Assert.That(VufScreenCatalog.ParseColor(
                    profile.palettes.background, "background").a, Is.EqualTo(1f));
                Assert.That(VufScreenCatalog.ParseColor(
                    profile.palettes.cta, "cta").a, Is.EqualTo(1f));
            }
            Assert.That(backgrounds.Count, Is.EqualTo(5));
            Assert.That(accents.Count, Is.EqualTo(5));
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
        public void CandidateShellsUseRealComponentsForAllScreensAndFiveStyles()
        {
            VufScreenCatalog.ScreenInfo[] screens = VufScreenCatalog.LoadScreens();
            foreach (string profileId in Profiles)
            {
                VufScreenCatalog.StyleInfo style = VufScreenCatalog.LoadStyle(profileId);
                Color expectedBackground = VufScreenCatalog.ParseColor(
                    style.palettes.background, "background");
                foreach (VufScreenCatalog.ScreenInfo screen in screens)
                {
                    GameObject root = VufScreenShellBuilderWindow.BuildCandidateHierarchy(
                        screen, style, true);
                    try
                    {
                        Assert.That(root.name, Does.Contain("CANDIDATE"));
                        Assert.That(root.GetComponent<Canvas>().renderMode,
                            Is.EqualTo(RenderMode.ScreenSpaceOverlay));
                        Assert.That(root.GetComponent<CanvasScaler>().uiScaleMode,
                            Is.EqualTo(CanvasScaler.ScaleMode.ScaleWithScreenSize));
                        Assert.That(root.GetComponent<CanvasScaler>().referenceResolution,
                            Is.EqualTo(new Vector2(720f, 1280f)));
                        Assert.That(root.GetComponent<GraphicRaycaster>(), Is.Not.Null);

                        VufCandidateScreenMarker marker =
                            root.GetComponent<VufCandidateScreenMarker>();
                        Assert.That(marker.ProfileId, Is.EqualTo(profileId));
                        Assert.That(marker.ScreenId, Is.EqualTo(screen.id));
                        Assert.That(marker.ScreenKey, Is.EqualTo(screen.key));
                        Assert.That(marker.CandidateStatus,
                            Is.EqualTo("CANDIDATE_NOT_APPROVED"));
                        Assert.That(marker.FeatureGate, Is.EqualTo(screen.feature_gate));

                        Transform safe = root.transform.Find("SafeArea_ReviewOnly");
                        Assert.That(safe, Is.Not.Null);
                        Assert.That(safe.GetComponent<VufSafeAreaFitter>(), Is.Not.Null);
                        Assert.That(safe.Find("OwnerReviewWarning"), Is.Not.Null);
                        Assert.That(safe.Find("BackgroundColor"), Is.Null);
                        Image background = root.transform.Find("BackgroundColor").GetComponent<Image>();
                        Assert.That(background, Is.Not.Null);
                        Assert.That(background.color.r,
                            Is.EqualTo(expectedBackground.r).Within(.0001f));
                        Assert.That(background.color.g,
                            Is.EqualTo(expectedBackground.g).Within(.0001f));
                        Assert.That(background.color.b,
                            Is.EqualTo(expectedBackground.b).Within(.0001f));

                        Text[] texts = root.GetComponentsInChildren<Text>(true);
                        Image[] images = root.GetComponentsInChildren<Image>(true);
                        Button[] buttons = root.GetComponentsInChildren<Button>(true);
                        Assert.That(texts.Length, Is.GreaterThanOrEqualTo(4));
                        Assert.That(images.Length, Is.GreaterThanOrEqualTo(4));
                        Assert.That(buttons.Length, Is.EqualTo(1));
                        foreach (Button button in buttons)
                        {
                            Assert.That(button.interactable, Is.False);
                            Assert.That(button.onClick.GetPersistentEventCount(), Is.EqualTo(0));
                        }

                        Text gateLabel = safe.Find("FeatureGate_AlwaysVisible").GetComponent<Text>();
                        if (screen.feature_gate == "OFF_UNTIL_ENGINE_POLICY_CONFIRMED")
                            Assert.That(gateLabel.text,
                                Does.Contain("POLICY OFF: NOT AVAILABLE IN DEMO"));
                        else
                            Assert.That(gateLabel.text,
                                Does.Contain("ENGINE/GAME BINDING REQUIRED"));

                        bool dialog = screen.kind == "modal" || screen.kind == "ceremony" ||
                            screen.kind == "overlay";
                        bool board = screen.kind == "playable" || screen.kind == "mode";
                        Assert.That(safe.GetComponent<CanvasGroup>() != null, Is.EqualTo(dialog));
                        Assert.That(safe.GetComponent<VufUiTween>() != null, Is.EqualTo(dialog));
                        if (dialog)
                        {
                            Assert.That(HasDirectChild(safe,
                                "PlaceholderCard_MODAL OR REWARD CEREMONY"),
                                Is.True);
                            Assert.That(HasDirectChild(safe,
                                "PlaceholderCard_HERO / COLLECTION SLOT"),
                                Is.False);
                        }
                        else if (board)
                        {
                            Assert.That(HasDirectChild(safe,
                                "PlaceholderCard_ENGINE BOARD SLOT (UNBOUND)"),
                                Is.True);
                            Assert.That(HasDirectChild(safe,
                                "PlaceholderCard_BOOSTER / SCORE HUD SLOT"),
                                Is.True);
                        }
                        else
                        {
                            Assert.That(HasDirectChild(safe,
                                "PlaceholderCard_HERO / COLLECTION SLOT"),
                                Is.True);
                            Assert.That(HasDirectChild(safe,
                                "PlaceholderCard_CONTENT CARDS / ORIGINAL ART"),
                                Is.True);
                        }
                    }
                    finally
                    {
                        UnityEngine.Object.DestroyImmediate(root);
                    }
                }
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
        public void UiTweenReducedMotionSnapsWithoutGameplay()
        {
            var go = new GameObject("VUF_TEST_TWEEN");
            try
            {
                var tween = go.AddComponent<VufUiTween>();
                var group = go.GetComponent<CanvasGroup>();
                tween.SetReducedMotion(true);
                tween.Hide();
                Assert.That(group.alpha, Is.EqualTo(0f));
                Assert.That(group.interactable, Is.False);
                Assert.That(group.blocksRaycasts, Is.False);
                tween.Show();
                Assert.That(group.alpha, Is.EqualTo(1f));
                Assert.That(group.interactable, Is.True);
                Assert.That(tween.IsAnimating, Is.False);
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(go);
            }
        }

        [Test]
        public void UiTweenInterruptionsReachDeterministicEndState()
        {
            var go = new GameObject("VUF_TEST_TWEEN_INTERRUPT");
            try
            {
                var tween = go.AddComponent<VufUiTween>();
                var group = go.GetComponent<CanvasGroup>();
                tween.SetReducedMotion(false);
                tween.Hide();
                Assert.That(group.interactable, Is.False);
                Assert.That(group.blocksRaycasts, Is.False);
                tween.Advance(tween.Duration / 2f);
                Assert.That(group.alpha, Is.InRange(0.01f, 0.99f));
                tween.Show();
                tween.Advance(tween.Duration);
                Assert.That(group.alpha, Is.EqualTo(1f).Within(0.0001f));
                Assert.That(tween.IsAnimating, Is.False);
                Assert.That(group.interactable, Is.True);
                Assert.That(group.blocksRaycasts, Is.True);
                tween.Hide();
                tween.Advance(tween.Duration / 2f);
                tween.Hide();
                tween.Advance(tween.Duration);
                Assert.That(group.alpha, Is.EqualTo(0f).Within(0.0001f));
                Assert.That(group.interactable, Is.False);
                Assert.That(group.blocksRaycasts, Is.False);
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(go);
            }
        }

        [Test]
        public void InvalidSpriteFrameSequenceRejected()
        {
            Assert.Throws<ArgumentOutOfRangeException>(
                () => VufSpriteClipBuilderWindow.BuildFrameSequence(1, true));
            Assert.Throws<ArgumentOutOfRangeException>(
                () => VufSpriteClipBuilderWindow.BuildFrameSequence(4097, true));
        }

        [Test]
        public void SpriteClipBuilderCreatesRealAnimationClipAndLoopKeysInMemory()
        {
            Texture2D texture = new Texture2D(6, 2, TextureFormat.RGBA32, false);
            Sprite[] sprites = new Sprite[3];
            AnimationClip clip = null;
            try
            {
                for (int i = 0; i < sprites.Length; ++i)
                    sprites[i] = Sprite.Create(texture,
                        new Rect(i * 2, 0, 2, 2), new Vector2(.5f, .5f), 1f);
                clip = VufSpriteClipBuilderWindow.BuildCandidateClip(
                    "VUF_TEST_SPRITE_LOOP", sprites, 12f, true, true);
                Assert.That(clip.frameRate, Is.EqualTo(12f));
                Assert.That(clip.length, Is.GreaterThan(0f));
                Assert.That(AnimationUtility.GetAnimationClipSettings(clip).loopTime, Is.True);
                EditorCurveBinding binding = EditorCurveBinding.PPtrCurve(
                    "", typeof(SpriteRenderer), "m_Sprite");
                ObjectReferenceKeyframe[] keys =
                    AnimationUtility.GetObjectReferenceCurve(clip, binding);
                CollectionAssert.AreEqual(
                    new UnityEngine.Object[] { sprites[0], sprites[1], sprites[2], sprites[1], sprites[0] },
                    Array.ConvertAll(keys, key => key.value));
                Assert.That(keys[1].time, Is.EqualTo(1f / 12f).Within(.0001f));
                Assert.That(keys[4].time, Is.EqualTo(4f / 12f).Within(.0001f));
            }
            finally
            {
                if (clip != null) UnityEngine.Object.DestroyImmediate(clip);
                foreach (Sprite sprite in sprites)
                    if (sprite != null) UnityEngine.Object.DestroyImmediate(sprite);
                UnityEngine.Object.DestroyImmediate(texture);
            }
        }

        [Test]
        public void VfxCandidateBuilderCreatesConfiguredUnityParticleSystemInMemory()
        {
            GameObject candidate = VufVfxLabWindow.BuildCandidateParticleSystem(
                "MatchBurst", 42, .5f, 4.5f, .21f, new Color(1f, .73f, .35f, 1f));
            try
            {
                ParticleSystem system = candidate.GetComponent<ParticleSystem>();
                Assert.That(system, Is.Not.Null);
                Assert.That(candidate.GetComponent<ParticleSystemRenderer>(), Is.Not.Null);
                ParticleSystem.MainModule main = system.main;
                Assert.That(main.playOnAwake, Is.False);
                Assert.That(main.loop, Is.False);
                Assert.That(main.maxParticles, Is.EqualTo(160));
                Assert.That(main.simulationSpace,
                    Is.EqualTo(ParticleSystemSimulationSpace.Local));
                Assert.That(main.startLifetime.constant, Is.EqualTo(.5f).Within(.0001f));
                Assert.That(main.startSpeed.constant, Is.EqualTo(4.5f).Within(.0001f));
                ParticleSystem.EmissionModule emission = system.emission;
                Assert.That(emission.rateOverTime.constant, Is.EqualTo(0f));
                var bursts = new ParticleSystem.Burst[1];
                Assert.That(emission.GetBursts(bursts), Is.EqualTo(1));
                Assert.That(bursts[0].count.constant, Is.EqualTo(42));
                Assert.That(system.shape.enabled, Is.True);
                Assert.That(system.shape.shapeType, Is.EqualTo(ParticleSystemShapeType.Cone));
                Assert.That(system.shape.angle, Is.EqualTo(60f));
                Assert.That(system.sizeOverLifetime.enabled, Is.True);
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(candidate);
            }
        }

        [Test]
        public void AtlasInspectorValidatesSyntheticTextureGeometryAndRejectsOverlap()
        {
            Texture2D atlas = new Texture2D(16, 16, TextureFormat.RGBA32, false);
            try
            {
                string valid = AtlasManifestJson("[8,8,4,4]", "[0.5,0.25,0.25,0.25]");
                VufAtlasPreviewWindow.AtlasManifest document;
                Rect[] rectangles = VufAtlasPreviewWindow.ValidateCandidateGeometry(
                    valid, atlas.width, atlas.height, out document);
                Assert.That(document.stage, Is.EqualTo("CANDIDATE_NOT_APPROVED"));
                Assert.That(rectangles.Length, Is.EqualTo(2));
                Assert.That(rectangles[1], Is.EqualTo(new Rect(8, 8, 4, 4)));

                string overlap = AtlasManifestJson("[2,0,4,4]", "[0.125,0.75,0.25,0.25]");
                Assert.That(() => VufAtlasPreviewWindow.ValidateCandidateGeometry(
                    overlap, atlas.width, atlas.height, out document),
                    Throws.ArgumentException.With.Message.Contains("overlapping"));
                Assert.That(() => VufAtlasPreviewWindow.ValidateCandidateGeometry(
                    valid, 32, 16, out document),
                    Throws.ArgumentException.With.Message.Contains("dimension"));
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(atlas);
            }
        }

        [Test]
        public void FiveGameProductionQueueAcceptsOnlyConsistentReadOnlySnapshot()
        {
            string[] ids = {
                "Coral_Rescue", "Garage_Legends", "Dino_Islands",
                "The_Fractured_Realms", "Wonder_Pop"
            };
            var report = new VufProductionQueueWindow.Portfolio {
                schema_version = 1,
                stage = "READ_ONLY_NOT_OWNER_APPROVAL",
                source_integrity_verified = true,
                total_verified_revisions = 0,
                profiles = new VufProductionQueueWindow.Profile[ids.Length]
            };
            for (int i = 0; i < ids.Length; ++i)
            {
                report.profiles[i] = new VufProductionQueueWindow.Profile {
                    profile_id = ids[i], pending_preview = new VufProductionQueueWindow.Pending[0]
                };
            }
            string valid = JsonUtility.ToJson(report);
            VufProductionQueueWindow.Portfolio parsed =
                VufProductionQueueWindow.ParsePortfolioReport(valid);
            CollectionAssert.AreEqual(ids,
                Array.ConvertAll(parsed.profiles, profile => profile.profile_id));
            Assert.That(parsed.stage, Is.EqualTo("READ_ONLY_NOT_OWNER_APPROVAL"));

            report.total_verified_revisions = 1;
            Assert.Throws<ArgumentException>(
                () => VufProductionQueueWindow.ParsePortfolioReport(JsonUtility.ToJson(report)));
            report.total_verified_revisions = 0;
            report.stage = "OWNER_APPROVED";
            Assert.Throws<ArgumentException>(
                () => VufProductionQueueWindow.ParsePortfolioReport(JsonUtility.ToJson(report)));
        }

        private static string AtlasManifestJson(string secondRect, string secondUv)
        {
            return "{\"schema_version\":1,\"stage\":\"CANDIDATE_NOT_APPROVED\"," +
                "\"generator\":\"VF04_SHELF_PACK_V01\",\"atlas_sha256\":\"synthetic\"," +
                "\"width\":16,\"height\":16,\"sprites\":[" +
                "{\"asset_id\":\"sprite_a\",\"width\":4,\"height\":4," +
                "\"pixel_rect_top_left\":[0,0,4,4]," +
                "\"uv_rect_bottom_left\":[0,0.75,0.25,0.25],\"rotated\":false}," +
                "{\"asset_id\":\"sprite_b\",\"width\":4,\"height\":4," +
                "\"pixel_rect_top_left\":" + secondRect + "," +
                "\"uv_rect_bottom_left\":" + secondUv + ",\"rotated\":false}]}";
        }

        private static bool HasDirectChild(Transform parent, string name)
        {
            for (int i = 0; i < parent.childCount; ++i)
                if (parent.GetChild(i).name == name)
                    return true;
            return false;
        }
    }
}
