using System;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.UI;
using Match3.VisualFactory.Editor;

namespace Match3.VisualFactory.Tests
{
    public sealed class VufConceptStageEditModeTests
    {
        private static readonly string[] Themes = {
            "Coral_Rescue", "Garage_Legends", "Dino_Islands",
            "The_Fractured_Realms", "Wonder_Pop"
        };
        private static readonly string[] Pages = { "home", "gameplay", "world_map" };

        private static VufConceptShowcaseWindow.Manifest Manifest()
        {
            var rows = new VufConceptShowcaseWindow.Screen[15];
            for (int game = 0; game < 5; game++)
            for (int screen = 0; screen < 3; screen++)
                rows[game * 3 + screen] = new VufConceptShowcaseWindow.Screen {
                    profile_id = Themes[game], screen_key = Pages[screen],
                    file = "preview_" + Themes[game] + "_" + Pages[screen] + ".png",
                    dimensions = new [] {360, 640},
                    png_sha256 = new string('a', 64),
                    style_source_sha256 = new string('b', 64),
                    tile_kit_atlas_sha256 = new string('c', 64),
                    seed = 0, render_scale = 1,
                    screen_state = "VISUAL_CONCEPT_NOT_INTERACTIVE"
                };
            return new VufConceptShowcaseWindow.Manifest {
                schema_version = 1, stage = "CANDIDATE_NOT_OWNER_APPROVED",
                generator = "VF07_FIVE_GAME_CONCEPT_SCREENS_V01",
                profile_ids = Themes, screen_keys = Pages,
                screens = rows, file_count = 15, dimensions = new [] {360, 640},
                original_art = "MATHEMATICAL_CONCEPT_ONLY"
            };
        }

        [Test]
        public void AllFifteenProfilesPagesCreateSeparateEditableUnboundUi()
        {
            var document = Manifest();
            var texture = new Texture2D(360, 640, TextureFormat.RGBA32, false);
            try
            {
                int checkedStages = 0;
                for (int game = 0; game < 5; game++)
                for (int screen = 0; screen < 3; screen++)
                {
                    var prefab = VufConceptStageBuilderWindow.BuildStage(
                        document, game, screen, texture,
                        VufScreenCatalog.LoadStyle(Themes[game]));
                    try
                    {
                        var marker = prefab.GetComponent<VufCandidateScreenMarker>();
                        Assert.That(marker.CandidateStatus,
                            Is.EqualTo("CANDIDATE_NOT_APPROVED"));
                        Assert.That(marker.ProfileId, Is.EqualTo(Themes[game]));
                        Assert.That(marker.ScreenKey, Is.EqualTo(Pages[screen]));
                        Assert.That(marker.FeatureGate,
                            Is.EqualTo("REQUIRES_ENGINE_OR_GAME_BINDING"));
                        Assert.That(prefab.GetComponent<Canvas>(), Is.Not.Null);
                        Assert.That(prefab.GetComponent<CanvasScaler>(), Is.Not.Null);
                        Assert.That(prefab.GetComponentInChildren<VufSafeAreaFitter>(),
                            Is.Not.Null);
                        Assert.That(prefab.GetComponentsInChildren<RawImage>().Length,
                            Is.EqualTo(1));
                        var raw = prefab.GetComponentInChildren<RawImage>();
                        Assert.That(raw.texture, Is.SameAs(texture));
                        Assert.That(raw.raycastTarget, Is.False);
                        Assert.That(prefab.GetComponentsInChildren<Text>().Length,
                            Is.GreaterThanOrEqualTo(4));
                        var buttons = prefab.GetComponentsInChildren<Button>();
                        Assert.That(buttons.Length, Is.EqualTo(1));
                        Assert.That(buttons[0].interactable, Is.False);
                        Assert.That(buttons[0].onClick.GetPersistentEventCount(),
                            Is.EqualTo(0));
                        checkedStages++;
                    }
                    finally { UnityEngine.Object.DestroyImmediate(prefab); }
                }
                Assert.That(checkedStages, Is.EqualTo(15));
            }
            finally { UnityEngine.Object.DestroyImmediate(texture); }
        }

        [Test]
        public void BadStageIdentityAndImageDimensionsAreRejectedBeforeCreation()
        {
            var manifest = Manifest();
            var wrongTexture = new Texture2D(128, 128);
            try
            {
                Assert.Throws<ArgumentException>(() =>
                    VufConceptStageBuilderWindow.BuildStage(manifest, 0, 0,
                        wrongTexture, VufScreenCatalog.LoadStyle("Coral_Rescue")));
                Assert.Throws<ArgumentException>(() =>
                    VufConceptStageBuilderWindow.BuildStage(manifest, 0, 0, null,
                        VufScreenCatalog.LoadStyle("Garage_Legends")));
                manifest.screens[0].screen_key = "gameplay";
                Assert.Throws<ArgumentException>(() =>
                    VufConceptStageBuilderWindow.BuildStage(manifest, 0, 0, null,
                        VufScreenCatalog.LoadStyle("Coral_Rescue")));
            }
            finally { UnityEngine.Object.DestroyImmediate(wrongTexture); }
        }

        [Test]
        public void StageWithoutReferenceIsStillRealEditableAndUnapproved()
        {
            var root = VufConceptStageBuilderWindow.BuildStage(
                Manifest(), 4, 2, null,
                VufScreenCatalog.LoadStyle("Wonder_Pop"));
            try
            {
                Assert.That(root.GetComponentsInChildren<RawImage>().Length, Is.Zero);
                Text banner = null;
                foreach (Text label in root.GetComponentsInChildren<Text>())
                    if (label.name == "OwnerReviewWarning") banner = label;
                Assert.That(banner, Is.Not.Null);
                Assert.That(banner.text, Does.Contain("DEVICE QA OPEN"));
                Assert.That(root.GetComponent<VufCandidateScreenMarker>().ScreenId,
                    Is.EqualTo("CONCEPT-03"));
                Assert.That(root.GetComponentInChildren<Button>().interactable,
                    Is.False);
            }
            finally { UnityEngine.Object.DestroyImmediate(root); }
        }

        [Test]
        public void ManifestOwnerApprovalForgeryNeverBuildsUi()
        {
            var altered = Manifest();
            altered.owner_visual_approval = true;
            Assert.Throws<ArgumentException>(() =>
                VufConceptStageBuilderWindow.BuildStage(altered, 0, 0, null,
                    VufScreenCatalog.LoadStyle("Coral_Rescue")));
        }
    }
}
