using System;
using System.IO;
using System.Linq;
using NUnit.Framework;
using UnityEditor;
using UnityEditor.U2D;
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

        [Test]
        public void UnimportedTextureCannotMasqueradeAsRealImporterEvidence()
        {
            var texture=new Texture2D(16,16,TextureFormat.RGBA32,false);
            try
            {
                Assert.Throws<ArgumentException>(() =>
                    VufSpriteAtlasV2Window.ReadImportedSettings(
                        new [] {texture}));
            }
            finally { UnityEngine.Object.DestroyImmediate(texture); }
        }

        [Test]
        public void ActualImportedSpriteSnapshotPreservesBytesGuidAndAllImporterSettings()
        {
            string name="__VUF_M05_READONLY_"+Guid.NewGuid().ToString("N");
            string folder="Assets/"+name;
            Assert.That(AssetDatabase.IsValidFolder(folder),Is.False);
            AssetDatabase.CreateFolder("Assets",name);
            try
            {
                string path=folder+"/source.png";
                var initial=new Texture2D(16,16,TextureFormat.RGBA32,false);
                try
                {
                    var pixels=new Color[16*16];
                    for(int i=0;i<pixels.Length;i++) pixels[i]=Color.cyan;
                    initial.SetPixels(pixels);
                    initial.Apply();
                    File.WriteAllBytes(path,initial.EncodeToPNG());
                }
                finally { UnityEngine.Object.DestroyImmediate(initial); }
                AssetDatabase.ImportAsset(path,ImportAssetOptions.ForceUpdate);
                var importer=AssetImporter.GetAtPath(path) as TextureImporter;
                Assert.That(importer,Is.Not.Null);
                importer.textureType=TextureImporterType.Sprite;
                importer.spriteImportMode=SpriteImportMode.Single;
                importer.SaveAndReimport();
                var imported=AssetDatabase.LoadAssetAtPath<Texture2D>(path);
                Assert.That(imported,Is.Not.Null);
                var bytes=File.ReadAllBytes(path);
                var guid=AssetDatabase.AssetPathToGUID(path);
                var settings=EditorJsonUtility.ToJson(importer);
                var snapshots=VufSpriteAtlasV2Window.ReadImportedSettings(
                    new [] { imported });
                Assert.That(snapshots.Length,Is.EqualTo(1));
                Assert.That(snapshots[0].SourcePath,Is.EqualTo(path));
                Assert.That(snapshots[0].SourceGuid,Is.EqualTo(guid));
                Assert.That(snapshots[0].IndividualSpritePivotsVerified,Is.True);
                Assert.That(snapshots[0].Slices,Is.Not.Null);
                Assert.That(snapshots[0].Slices.Length,Is.EqualTo(1));
                Assert.That(snapshots[0].Slices[0].RectPixels.width,
                    Is.EqualTo(16f).Within(.001f));
                Assert.That(snapshots[0].Slices[0].RectPixels.height,
                    Is.EqualTo(16f).Within(.001f));
                Assert.That(snapshots[0].Slices[0].PivotPixels.x,
                    Is.EqualTo(8f).Within(.01f));
                Assert.That(snapshots[0].Slices[0].PivotPixels.y,
                    Is.EqualTo(8f).Within(.01f));
                Assert.That(snapshots[0].Slices[0].HasPhysicalDeviceProof,Is.False);
                Assert.That(snapshots[0].OriginalRightsVerified,Is.False);
                Assert.That(snapshots[0].RealDeviceTextureVerified,Is.False);
                Assert.That(snapshots[0].ReleaseAllowed,Is.False);
                Assert.That(EditorJsonUtility.ToJson(importer),
                    Is.EqualTo(settings));
                Assert.That(File.ReadAllBytes(path),Is.EqualTo(bytes));
                Assert.That(AssetDatabase.AssetPathToGUID(path),Is.EqualTo(guid));
            }
            finally
            {
                AssetDatabase.DeleteAsset(folder);
                AssetDatabase.Refresh();
            }
        }

        [Test]
        public void CreatesOnlyNewV2CandidateAndPreservesImportedSource()
        {
            string folderName = "__VUF_M05_015_" + Guid.NewGuid().ToString("N");
            string folder = "Assets/" + folderName;
            Assert.That(AssetDatabase.IsValidFolder(folder), Is.False);
            Assert.That(Directory.Exists(folder), Is.False);
            AssetDatabase.CreateFolder("Assets", folderName);
            try
            {
                string sourcePath = folder + "/candidate.png";
                string atlasPath = folder + "/candidate.spriteatlasv2";
                var source = new Texture2D(2, 2, TextureFormat.RGBA32, false);
                try
                {
                    source.SetPixels(new[] { Color.red, Color.green,
                        Color.blue, Color.white });
                    source.Apply();
                    File.WriteAllBytes(sourcePath, source.EncodeToPNG());
                }
                finally { UnityEngine.Object.DestroyImmediate(source); }
                AssetDatabase.ImportAsset(sourcePath, ImportAssetOptions.ForceUpdate);
                var sourceImporter = AssetImporter.GetAtPath(sourcePath) as TextureImporter;
                Assert.That(sourceImporter, Is.Not.Null);
                sourceImporter.textureType = TextureImporterType.Sprite;
                sourceImporter.SaveAndReimport();

                var texture = AssetDatabase.LoadAssetAtPath<Texture2D>(sourcePath);
                Assert.That(texture, Is.Not.Null);
                byte[] sourceBytes = File.ReadAllBytes(sourcePath);
                string sourceGuid = AssetDatabase.AssetPathToGUID(sourcePath);
                string sourceImporterBefore = EditorJsonUtility.ToJson(sourceImporter);

                Assert.That(VufSpriteAtlasV2Window.CreateNewCandidate(
                    new[] { texture }, atlasPath), Is.EqualTo(atlasPath));
                Assert.That(File.Exists(atlasPath), Is.True);
                var atlasImporter = AssetImporter.GetAtPath(atlasPath) as SpriteAtlasImporter;
                Assert.That(atlasImporter, Is.Not.Null);
                Assert.That(atlasImporter.includeInBuild, Is.False);
                string atlasGuid = AssetDatabase.AssetPathToGUID(atlasPath);
                Assert.That(atlasGuid, Is.Not.Empty);
                byte[] atlasBytes = File.ReadAllBytes(atlasPath);

                Assert.Throws<ArgumentException>(() =>
                    VufSpriteAtlasV2Window.CreateNewCandidate(
                        new[] { texture }, atlasPath));
                Assert.That(File.ReadAllBytes(atlasPath), Is.EqualTo(atlasBytes));
                AssetDatabase.ImportAsset(atlasPath, ImportAssetOptions.ForceUpdate);
                Assert.That(AssetDatabase.AssetPathToGUID(atlasPath), Is.EqualTo(atlasGuid));
                Assert.That(File.ReadAllBytes(sourcePath), Is.EqualTo(sourceBytes));
                Assert.That(AssetDatabase.AssetPathToGUID(sourcePath), Is.EqualTo(sourceGuid));
                Assert.That(EditorJsonUtility.ToJson(sourceImporter),
                    Is.EqualTo(sourceImporterBefore));
            }
            finally
            {
                AssetDatabase.DeleteAsset(folder);
                AssetDatabase.Refresh();
            }
        }
    }
}
