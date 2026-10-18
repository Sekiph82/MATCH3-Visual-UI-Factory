// M08: actual Unity SpriteRenderer staging unit cases; not real device proof.
using System;
using NUnit.Framework;
using UnityEngine;
using Match3.VisualFactory.Editor;

namespace Match3.VisualFactory.Tests
{
    public sealed class VufExternalPackViewStageEditModeTests
    {
        [Test]
        public void ValidSHAReviewedCandidateTextureCreatesTemporaryRealSpriteRenderer()
        {
            var texture = new Texture2D(16, 16, TextureFormat.RGBA32, false);
            Sprite owner;
            GameObject candidate = null;
            try
            {
                candidate = VufExternalPackViewStage.Create(
                    texture, "Coral_Rescue", "Coral_Rescue.scene.gameplay.backdrop",
                    "tile_match", out owner);
                Assert.That(candidate, Is.Not.Null);
                Assert.That(candidate.GetComponent<SpriteRenderer>().sprite,
                    Is.SameAs(owner));
                Assert.That(owner.texture, Is.SameAs(texture));
                Assert.That((candidate.hideFlags & HideFlags.DontSaveInEditor) != 0,
                    Is.True);
                Assert.That((owner.hideFlags & HideFlags.DontSaveInBuild) != 0,
                    Is.True);
            }
            finally
            {
                if (candidate != null)
                {
                    Sprite sprite = candidate.GetComponent<SpriteRenderer>().sprite;
                    VufExternalPackViewStage.Dispose(candidate, sprite);
                }
                UnityEngine.Object.DestroyImmediate(texture);
            }
        }

        [Test]
        public void WrongNamespaceAndUnknownEventsAreRejectedBeforeSceneCreation()
        {
            var t = new Texture2D(16, 16);
            Sprite ignored;
            try
            {
                Assert.Throws<ArgumentException>(() =>
                    VufExternalPackViewStage.Create(
                        t, "Wonder_Pop", "Coral_Rescue.scene.home",
                        "level_win", out ignored));
                Assert.Throws<ArgumentException>(() =>
                    VufExternalPackViewStage.Create(
                        t, "Coral_Rescue", "Coral_Rescue.scene.home",
                        "purchase_rewards", out ignored));
            }
            finally { UnityEngine.Object.DestroyImmediate(t); }
        }

        [Test]
        public void MissingExternalPackTextureFailsWithoutAnyMockArtCreation()
        {
            Sprite ignored;
            Assert.Throws<ArgumentException>(() =>
                VufExternalPackViewStage.Create(
                    null, "Dino_Islands", "Dino_Islands.fx.matchburst.sheet",
                    "tile_match", out ignored));
        }
    }
}
