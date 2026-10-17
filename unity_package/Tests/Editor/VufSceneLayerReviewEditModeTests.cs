// VUF-M06-012: pure Editor candidate layer-manifest contract tests.
// No Unity GUI, physical device, art-rights or real parallax performance PASS.
using System;
using NUnit.Framework;
using UnityEngine;
using Match3.VisualFactory.Editor;

namespace Match3.VisualFactory.Tests
{
    public sealed class VufSceneLayerReviewEditModeTests
    {
        private static readonly string[] Profiles = {
            "Coral_Rescue", "Garage_Legends", "Dino_Islands",
            "The_Fractured_Realms", "Wonder_Pop"
        };
        private static readonly string[] CommonScenes = {
            "world_map", "chapter_map", "gameplay"
        };
        private static readonly string[] CoralExtra = {
            "reef_restoration", "marine_collection", "my_aquarium", "new_region"
        };
        private static readonly string[] Layers = {
            "backdrop", "distant_environment", "near_decoration"
        };
        private static readonly int[] Factors = { 0, 120, 340 };
        private const string Digest =
            "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef";

        private static VufSceneLayerReviewWindow.SceneManifest Candidate()
        {
            var result = new VufSceneLayerReviewWindow.SceneManifest
            {
                schema_version = 1,
                stage = "CANDIDATE_NOT_OWNER_APPROVED",
                generator = "VUF_M06_MATH_LAYERED_SCENES_V01",
                scene_count = 19,
                file_count = 57,
                owner_visual_approval = false,
                art_rights_verified = false,
                real_device_verified = false,
                parallax_runtime_validated = false,
                real_engine_visual_binding = false,
                release_allowed = false,
                scenes = new VufSceneLayerReviewWindow.SceneItem[19]
            };
            int at = 0;
            for (int profile = 0; profile < Profiles.Length; profile++)
            {
                string[] pages = profile == 0
                    ? new[] { CommonScenes[0], CommonScenes[1], CommonScenes[2],
                              CoralExtra[0], CoralExtra[1], CoralExtra[2], CoralExtra[3] }
                    : CommonScenes;
                foreach (string page in pages)
                {
                    var row = new VufSceneLayerReviewWindow.SceneItem
                    {
                        profile_id = Profiles[profile],
                        scene_id = page,
                        runtime_ui_separate = true,
                        owner_visual_approved = false,
                        layers = new VufSceneLayerReviewWindow.SceneLayer[3]
                    };
                    for (int layer = 0; layer < 3; layer++)
                    {
                        row.layers[layer] = new VufSceneLayerReviewWindow.SceneLayer
                        {
                            profile_id = Profiles[profile],
                            scene_id = page,
                            layer_id = Layers[layer],
                            file = Profiles[profile].ToLowerInvariant() + "_" +
                                   page + "_" + Layers[layer] + ".png",
                            png_sha256 = Digest,
                            style_source_sha256 = Digest,
                            draw_order = layer,
                            parallax_factor_milli = Factors[layer],
                            dimensions = new[] { 180, 320 },
                            interactive = false,
                            contains_runtime_text = false,
                            contains_runtime_buttons = false,
                            not_owner_approved = true
                        };
                    }
                    result.scenes[at++] = row;
                }
            }
            Assert.That(at, Is.EqualTo(19));
            return result;
        }

        private static string Json(VufSceneLayerReviewWindow.SceneManifest value) =>
            JsonUtility.ToJson(value);

        [Test]
        public void CandidateNineteenScenesAndFiftySevenLayersAreAcceptedStructurally()
        {
            var accepted = VufSceneLayerReviewWindow.ValidateJson(Json(Candidate()));
            Assert.That(accepted.scenes.Length, Is.EqualTo(19));
            Assert.That(accepted.file_count, Is.EqualTo(57));
            Assert.That(accepted.release_allowed, Is.False);
        }

        [Test]
        public void OwnerApprovalAndReleaseSpoofingFailClosed()
        {
            var m = Candidate();
            m.owner_visual_approval = true;
            Assert.Throws<ArgumentException>(
                () => VufSceneLayerReviewWindow.ValidateJson(Json(m)));
            m = Candidate();
            m.release_allowed = true;
            Assert.Throws<ArgumentException>(
                () => VufSceneLayerReviewWindow.ValidateJson(Json(m)));
        }

        [Test]
        public void RuntimeUiButtonsCannotBeBundledAsBackgroundLayerPixels()
        {
            var m = Candidate();
            m.scenes[0].layers[0].contains_runtime_buttons = true;
            Assert.Throws<ArgumentException>(
                () => VufSceneLayerReviewWindow.ValidateJson(Json(m)));
            m = Candidate();
            m.scenes[0].runtime_ui_separate = false;
            Assert.Throws<ArgumentException>(
                () => VufSceneLayerReviewWindow.ValidateJson(Json(m)));
        }

        [Test]
        public void MissingReorderedOrCrossThemeSceneIsRefused()
        {
            var m = Candidate();
            m.scenes[0].scene_id = "my_aquarium";
            Assert.Throws<ArgumentException>(
                () => VufSceneLayerReviewWindow.ValidateJson(Json(m)));
            m = Candidate();
            m.scenes[0] = null;
            Assert.Throws<ArgumentException>(
                () => VufSceneLayerReviewWindow.ValidateJson(Json(m)));
            m = Candidate();
            m.scenes[0].profile_id = "Dino_Islands";
            Assert.Throws<ArgumentException>(
                () => VufSceneLayerReviewWindow.ValidateJson(Json(m)));
        }

        [Test]
        public void TamperedHashGeometryAndParallaxFailClosed()
        {
            var m = Candidate();
            m.scenes[0].layers[0].png_sha256 = "deadbeef";
            Assert.Throws<ArgumentException>(
                () => VufSceneLayerReviewWindow.ValidateJson(Json(m)));
            m = Candidate();
            m.scenes[0].layers[0].dimensions = new[] { 360, 320 };
            Assert.Throws<ArgumentException>(
                () => VufSceneLayerReviewWindow.ValidateJson(Json(m)));
            m = Candidate();
            m.scenes[0].layers[2].parallax_factor_milli = 999;
            Assert.Throws<ArgumentException>(
                () => VufSceneLayerReviewWindow.ValidateJson(Json(m)));
        }

        [Test]
        public void EmptyOrOversizedManifestIsRejectedWithoutAssetDatabaseWrites()
        {
            Assert.Throws<ArgumentException>(
                () => VufSceneLayerReviewWindow.ValidateJson(null));
            Assert.Throws<ArgumentException>(
                () => VufSceneLayerReviewWindow.ValidateJson("{}"));
            Assert.Throws<ArgumentException>(
                () => VufSceneLayerReviewWindow.ValidateJson(
                    new string('x', 256 * 1024 + 1)));
        }
    }
}
