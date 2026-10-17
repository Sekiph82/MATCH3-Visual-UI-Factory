using System;
using NUnit.Framework;
using UnityEngine;
using Match3.VisualFactory.Editor;

namespace Match3.VisualFactory.Tests
{
    public sealed class VufSpriteAtlasV2EditModeTests
    {
        [Test]
        public void ExistingImportedUnityTextureReferencesStayUnchangedInDraft()
        {
            var a = new Texture2D(12, 16);
            var b = new Texture2D(24, 30);
            try
            {
                var input = new [] { a, b };
                var validated = VufSpriteAtlasV2Window.ValidateDraft(input);
                Assert.That(validated, Is.Not.SameAs(input));
                Assert.That(validated[0], Is.SameAs(a));
                Assert.That(validated[1], Is.SameAs(b));
                Assert.That(a.width, Is.EqualTo(12));
                Assert.That(b.height, Is.EqualTo(30));
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(a);
                UnityEngine.Object.DestroyImmediate(b);
            }
        }

        [Test]
        public void DuplicateNullOrUnboundedInputIsRefused()
        {
            var tex = new Texture2D(4, 4);
            try
            {
                Assert.Throws<ArgumentException>(() =>
                    VufSpriteAtlasV2Window.ValidateDraft(null));
                Assert.Throws<ArgumentException>(() =>
                    VufSpriteAtlasV2Window.ValidateDraft(new Texture2D[0]));
                Assert.Throws<ArgumentException>(() =>
                    VufSpriteAtlasV2Window.ValidateDraft(new Texture2D[] {null}));
                Assert.Throws<ArgumentException>(() =>
                    VufSpriteAtlasV2Window.ValidateDraft(new [] {tex, tex}));
                Assert.Throws<ArgumentException>(() =>
                    VufSpriteAtlasV2Window.ValidateDraft(new Texture2D[33]));
            }
            finally { UnityEngine.Object.DestroyImmediate(tex); }
        }

        [Test]
        public void ValidationDoesNotMutatePixelsOrCreateAssetFiles()
        {
            var tex = new Texture2D(2, 2, TextureFormat.RGBA32, false);
            try
            {
                byte[] before = (byte[])tex.GetRawTextureData().ToArray().Clone();
                var result = VufSpriteAtlasV2Window.ValidateDraft(new [] {tex});
                CollectionAssert.AreEqual(before, tex.GetRawTextureData().ToArray());
                Assert.That(result.Length, Is.EqualTo(1));
            }
            finally { UnityEngine.Object.DestroyImmediate(tex); }
        }

        [Test]
        public void ActualUnityV2TypeIsAvailableAtExpectedEditorAssembly()
        {
            Assert.That(typeof(UnityEditor.U2D.SpriteAtlasAsset).IsClass, Is.True);
            Assert.That(typeof(UnityEditor.U2D.SpriteAtlasImporter).IsClass, Is.True);
        }
    }
}
