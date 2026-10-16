using System;
using NUnit.Framework;
using UnityEngine;
using Match3.VisualFactory.Editor;

namespace Match3.VisualFactory.Tests
{
    public sealed class VufConceptShowcaseEditModeTests
    {
        private static readonly string[] Themes = {
            "Coral_Rescue", "Garage_Legends", "Dino_Islands",
            "The_Fractured_Realms", "Wonder_Pop"
        };
        private static readonly string[] Screens = {"home", "gameplay", "world_map"};

        private static VufConceptShowcaseWindow.Manifest Candidate()
        {
            var rows = new VufConceptShowcaseWindow.Screen[15];
            for (int i = 0; i < 5; i++)
            for (int j = 0; j < 3; j++)
            {
                rows[i * 3 + j] = new VufConceptShowcaseWindow.Screen {
                    profile_id = Themes[i],
                    screen_key = Screens[j],
                    file = "preview_" + Themes[i] + "_" + Screens[j] + ".png",
                    dimensions = new[] {360, 640},
                    png_sha256 = new string('a', 64),
                    style_source_sha256 = new string('b', 64),
                    tile_kit_atlas_sha256 = new string('c', 64),
                    screen_state = "VISUAL_CONCEPT_NOT_INTERACTIVE",
                    render_scale = 1,
                    seed = 0
                };
            }
            return new VufConceptShowcaseWindow.Manifest {
                schema_version = 1,
                stage = "CANDIDATE_NOT_OWNER_APPROVED",
                generator = "VF07_FIVE_GAME_CONCEPT_SCREENS_V01",
                profile_ids = Themes,
                screen_keys = Screens,
                file_count = 15,
                dimensions = new[] {360, 640},
                original_art = "MATHEMATICAL_CONCEPT_ONLY",
                screens = rows
            };
        }

        [Test]
        public void FifteenStrictlyOrderedScreensStayNoninteractive()
        {
            var result = VufConceptShowcaseWindow.Parse(JsonUtility.ToJson(Candidate()));
            Assert.That(result.screens.Length, Is.EqualTo(15));
            Assert.That(result.interactive_ui_enabled, Is.False);
            Assert.That(result.owner_visual_approval, Is.False);
            Assert.That(result.real_device_verified, Is.False);
        }

        [Test]
        public void ForgedApprovalGameplayOrDeviceReportFails()
        {
            var broken = Candidate();
            broken.asset_rights_verified = true;
            Assert.Throws<ArgumentException>(() =>
                VufConceptShowcaseWindow.Parse(JsonUtility.ToJson(broken)));
            broken = Candidate();
            broken.interactive_ui_enabled = true;
            Assert.Throws<ArgumentException>(() =>
                VufConceptShowcaseWindow.Parse(JsonUtility.ToJson(broken)));
            broken = Candidate();
            broken.real_device_verified = true;
            Assert.Throws<ArgumentException>(() =>
                VufConceptShowcaseWindow.Parse(JsonUtility.ToJson(broken)));
        }

        [Test]
        public void SwappedScreenAndDimensionsAreRejected()
        {
            var broken = Candidate();
            broken.screens[2].screen_key = "gameplay";
            Assert.Throws<ArgumentException>(() =>
                VufConceptShowcaseWindow.Parse(JsonUtility.ToJson(broken)));
            broken = Candidate();
            broken.dimensions = new[] {540, 960};
            Assert.Throws<ArgumentException>(() =>
                VufConceptShowcaseWindow.Parse(JsonUtility.ToJson(broken)));
        }

        [Test]
        public void HashReceiptAndScaleCannotBeForged()
        {
            var broken = Candidate();
            broken.screens[7].png_sha256 = "not-a-hash";
            Assert.Throws<ArgumentException>(() =>
                VufConceptShowcaseWindow.Parse(JsonUtility.ToJson(broken)));
            broken = Candidate();
            broken.screens[9].render_scale = 2;
            Assert.Throws<ArgumentException>(() =>
                VufConceptShowcaseWindow.Parse(JsonUtility.ToJson(broken)));
        }
    }
}
