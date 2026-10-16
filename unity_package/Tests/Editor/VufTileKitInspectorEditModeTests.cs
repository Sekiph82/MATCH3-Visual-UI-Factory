using System;
using NUnit.Framework;
using UnityEngine;
using Match3.VisualFactory.Editor;

namespace Match3.VisualFactory.Tests
{
    public sealed class VufTileKitInspectorEditModeTests
    {
        private static VufTileKitInspectorWindow.Manifest Prototype()
        {
            var shapes = new [] {"circle", "triangle", "diamond",
                                 "star", "crescent", "shield"};
            var tiles = new VufTileKitInspectorWindow.Tile[6];
            for (int i = 0; i < 6; i++)
            {
                tiles[i] = new VufTileKitInspectorWindow.Tile {
                    shape = shapes[i], file = "tile_" + shapes[i] + ".png",
                    file_sha256 = new string('b', 64),
                    rgba_sha256 = new string('c', 64),
                    pixel_rect_top_left = new [] {i % 3 * 32, i / 3 * 32, 32, 32}
                };
            }
            return new VufTileKitInspectorWindow.Manifest {
                schema_version = 1, stage = "CANDIDATE_NOT_OWNER_APPROVED",
                generator = "VF04_SIX_SILHOUETTE_TILE_KIT_V01",
                profile_id = "Wonder_Pop",
                style_source_sha256 = new string('a', 64),
                atlas_sha256 = new string('d', 64),
                silhouette_keys = shapes,
                side = 32, format = "RGBA8_UNROTATED",
                atlas_path = "tile_atlas.png",
                atlas_dimensions = new[] {96,64},
                original_art = "MATHEMATICAL_PROTOTYPE_NOT_OWNER_ART",
                tiles = tiles
            };
        }

        [Test]
        public void SixPrototypeTilesLoadWithExactNonoverlappingCells()
        {
            var parsed = VufTileKitInspectorWindow.Parse(
                JsonUtility.ToJson(Prototype()), 96, 64);
            Assert.That(parsed.tiles.Length, Is.EqualTo(6));
            Assert.That(parsed.profile_id, Is.EqualTo("Wonder_Pop"));
            Assert.That(parsed.asset_rights_verified, Is.False);
        }

        [Test]
        public void ForgedRightsAndApprovalAreRejected()
        {
            var forged = Prototype();
            forged.owner_visual_approval = true;
            Assert.Throws<ArgumentException>(() =>
                VufTileKitInspectorWindow.Parse(JsonUtility.ToJson(forged), 96, 64));
            forged = Prototype();
            forged.gameplay_bindings_enabled = true;
            Assert.Throws<ArgumentException>(() =>
                VufTileKitInspectorWindow.Parse(JsonUtility.ToJson(forged), 96, 64));
        }

        [Test]
        public void SwappedShapeRectAndMismatchedTextureFailClosed()
        {
            var broken = Prototype();
            broken.tiles[0].shape = "star";
            Assert.Throws<ArgumentException>(() =>
                VufTileKitInspectorWindow.Parse(JsonUtility.ToJson(broken), 96, 64));
            broken = Prototype();
            broken.tiles[5].pixel_rect_top_left[1] = 0;
            Assert.Throws<ArgumentException>(() =>
                VufTileKitInspectorWindow.Parse(JsonUtility.ToJson(broken), 96, 64));
            broken = Prototype();
            Assert.Throws<ArgumentException>(() =>
                VufTileKitInspectorWindow.Parse(JsonUtility.ToJson(broken), 128, 64));
        }
    }
}
