// VUF R47 | VF-10 / M05-004 / M08-003 | Unity SpriteAtlas V2 candidate.
// SDK_REUSE: Unity's built-in SpriteAtlasAsset / SpriteAtlasImporter APIs.
// NO copying UnityCsReference (reference-only license); source originals,
// TextureImporter settings, player builds and existing atlases are untouched.
using System;
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEditor.U2D;
using UnityEngine;

namespace Match3.VisualFactory.Editor
{
    public sealed class VufSpriteAtlasV2Window : EditorWindow
    {
        private Texture2D[] selected = new Texture2D[6];
        private string error;
        private string lastCandidate;
        private ImporterSnapshot[] lastInspection;

        internal sealed class ImporterSnapshot
        {
            internal string SourcePath;
            internal string SourceGuid;
            internal int Width, Height, MaxSourceTextureSize;
            internal SpriteImportMode SpriteMode;
            internal Vector2 SourcePivot;
            internal Vector4 SourceBorder;
            internal float PixelsPerUnit;
            internal bool MipMapsEnabled, AlphaTransparency;
            internal bool IOSOverride, AndroidOverride;
            internal bool IndividualSpritePivotsVerified;
            internal bool OriginalRightsVerified, RealDeviceTextureVerified;
            internal bool ReleaseAllowed;
        }


        [MenuItem("Tools/MATCH3/SpriteAtlas V2 Candidate Builder")]
        public static void Open()
        {
            var w = GetWindow<VufSpriteAtlasV2Window>("VUF Atlas V2");
            w.minSize = new Vector2(600, 530);
            w.Show();
        }

        private void OnGUI()
        {
            EditorGUILayout.LabelField("VF-10 | Unity SpriteAtlas V2 Candidate",
                EditorStyles.boldLabel);
            EditorGUILayout.HelpBox(
                "Uses Unity's real built-in SpriteAtlasAsset APIs. Only creates " +
                "a NEW .spriteatlasv2 in Assets; Include In Build is disabled. " +
                "No importer changes to original art and no claim of release, " +
                "ownership, pixel quality, atlas memory or phone GPU approval.",
                MessageType.Warning);
            int count = EditorGUILayout.IntSlider(
                "Imported Sprite textures", selected.Length, 1, 32);
            if (count != selected.Length)
                Array.Resize(ref selected, count);
            for (int i = 0; i < selected.Length; i++)
                selected[i] = (Texture2D)EditorGUILayout.ObjectField(
                    "Packable " + (i + 1), selected[i], typeof(Texture2D), false);
            if (GUILayout.Button("Create NEW SpriteAtlas V2 candidate",
                    GUILayout.Height(32f)))
            {
                error = null; lastCandidate = null;
                try { SaveNew(); }
                catch (Exception exception)
                {
                    error = "Atlas candidate refused: " + exception.Message;
                }
            }
            if (GUILayout.Button("Inspect existing PNG Sprite importer settings (READ-ONLY)",
                    GUILayout.Height(28f)))
            {
                try { lastInspection = ReadImportedSettings(selected); error = null; }
                catch (Exception ex)
                {
                    lastInspection = null;
                    error = "Source importer QA blocked: " + ex.Message;
                }
            }
            if (lastInspection != null)
            {
                foreach (var item in lastInspection)
                {
                    EditorGUILayout.LabelField(item.SourcePath, EditorStyles.boldLabel);
                    EditorGUILayout.LabelField(
                        "GUID " + item.SourceGuid + " | " + item.Width +
                        "x" + item.Height + " | mode=" + item.SpriteMode);
                    EditorGUILayout.LabelField(
                        "Pivot " + item.SourcePivot + " | border " + item.SourceBorder +
                        " | PPU " + item.PixelsPerUnit.ToString("F1"));
                    EditorGUILayout.LabelField(
                        "Mips=" + item.MipMapsEnabled + " / alpha-transparent=" +
                        item.AlphaTransparency + " / max size=" +
                        item.MaxSourceTextureSize);
                    EditorGUILayout.LabelField(
                        "iPhone override=" + item.IOSOverride +
                        " / Android override=" + item.AndroidOverride);
                    EditorGUILayout.HelpBox(
                        item.IndividualSpritePivotsVerified ?
                        "Single Sprite: imported pivot/border metadata available; " +
                        "actual per-pixel rendering/device not verified." :
                        "Multiple Sprite source: individual slice pivots/borders " +
                        "require separate Sprite inspection; NOT VERIFIED.",
                        MessageType.Warning);
                }
                EditorGUILayout.HelpBox(
                    "Source-only READ: no source importer modified. Real 1x/2x/3x, " +
                    "atlas bleeding, GPU compression and owner art/device acceptance OPEN.",
                    MessageType.Info);
            }
            if (!String.IsNullOrEmpty(error))
                EditorGUILayout.HelpBox(error, MessageType.Error);
            if (!String.IsNullOrEmpty(lastCandidate))
                EditorGUILayout.HelpBox("New draft: " + lastCandidate +
                    " | includeInBuild FALSE; manual art/import QA still required.",
                    MessageType.Info);
        }

        // Zero AssetDatabase writes; safe to use with in-memory EditMode
        // synthetic textures. The actual saving path has stricter checks.
        internal static Texture2D[] ValidateDraft(Texture2D[] textures)
        {
            if (textures == null || textures.Length < 1 || textures.Length > 32)
                throw new ArgumentException("expected 1..32 draft textures");
            var result = new Texture2D[textures.Length];
            var seen = new HashSet<Texture2D>();
            for (int i = 0; i < textures.Length; i++)
            {
                Texture2D texture = textures[i];
                if (texture == null || texture.width < 1 || texture.height < 1 ||
                    texture.width > 4096 || texture.height > 4096 ||
                    !seen.Add(texture))
                    throw new ArgumentException("null, duplicate or oversized texture");
                result[i] = texture;
            }
            return result;
        }

        // Read ONLY existing imported source settings. This method must not
        // call SetPlatformTextureSettings, SaveAndReimport or AssetDatabase
        // writes. Multiple sprites have per-slice pivots which are explicitly
        // NOT certified by TextureImporter.spritePivot.
        internal static ImporterSnapshot[] ReadImportedSettings(Texture2D[] input)
        {
            var sources = ValidateDraft(input);
            var result = new ImporterSnapshot[sources.Length];
            var seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            for (int i=0;i<sources.Length;i++)
            {
                var tex = sources[i];
                var path = AssetDatabase.GetAssetPath(tex);
                if (String.IsNullOrEmpty(path) ||
                    !path.StartsWith("Assets/",StringComparison.Ordinal) ||
                    !path.EndsWith(".png",StringComparison.OrdinalIgnoreCase) ||
                    !seen.Add(path))
                    throw new ArgumentException(
                        "Only distinct already imported PNG Sprite source COPIES may be inspected");
                var importer = AssetImporter.GetAtPath(path) as TextureImporter;
                if (importer == null ||
                    importer.textureType != TextureImporterType.Sprite)
                    throw new ArgumentException(
                        "Source importer is missing or is not Sprite");
                var ios = importer.GetPlatformTextureSettings("iPhone");
                var android = importer.GetPlatformTextureSettings("Android");
                result[i] = new ImporterSnapshot {
                    SourcePath = path,
                    SourceGuid = AssetDatabase.AssetPathToGUID(path),
                    Width = tex.width,
                    Height = tex.height,
                    MaxSourceTextureSize = importer.maxTextureSize,
                    SpriteMode = importer.spriteImportMode,
                    SourcePivot = importer.spritePivot,
                    SourceBorder = importer.spriteBorder,
                    PixelsPerUnit = importer.spritePixelsPerUnit,
                    MipMapsEnabled = importer.mipmapEnabled,
                    AlphaTransparency = importer.alphaIsTransparency,
                    IOSOverride = ios != null && ios.overridden,
                    AndroidOverride = android != null && android.overridden,
                    IndividualSpritePivotsVerified =
                        importer.spriteImportMode == SpriteImportMode.Single,
                    OriginalRightsVerified = false,
                    RealDeviceTextureVerified = false,
                    ReleaseAllowed = false
                };
                if (String.IsNullOrEmpty(result[i].SourceGuid))
                    throw new ArgumentException("source importer GUID unavailable");
            }
            return result;
        }

        private void SaveNew()
        {
            Texture2D[] textures = ValidateDraft(selected);
            string path = EditorUtility.SaveFilePanelInProject(
                "Create NEW unapproved SpriteAtlas V2",
                "VUF_SpriteAtlasV2_CANDIDATE", "spriteatlasv2",
                "Pick an unused Assets path. NEVER overwrite an atlas.");
            if (String.IsNullOrEmpty(path)) return;
            lastCandidate = CreateNewCandidate(textures, path);
            Selection.activeObject = AssetDatabase.LoadMainAssetAtPath(path);
        }

        // The same guarded save path is exercised by EditMode tests with
        // isolated temporary source textures and a unique candidate path.
        internal static string CreateNewCandidate(Texture2D[] input, string path)
        {
            Texture2D[] textures = ValidateDraft(input);
            var unique = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            foreach (Texture2D texture in textures)
            {
                string assetPath = AssetDatabase.GetAssetPath(texture);
                if (String.IsNullOrEmpty(assetPath) ||
                    !assetPath.StartsWith("Assets/", StringComparison.Ordinal) ||
                    !assetPath.EndsWith(".png", StringComparison.OrdinalIgnoreCase) ||
                    !unique.Add(assetPath))
                    throw new ArgumentException(
                        "packables must be unique imported Assets PNG copies");
                var importer = AssetImporter.GetAtPath(assetPath) as TextureImporter;
                if (importer == null || importer.textureType != TextureImporterType.Sprite)
                    throw new ArgumentException(
                        "packable is not already imported as Unity Sprite");
            }
            if (!path.StartsWith("Assets/", StringComparison.Ordinal) ||
                !path.EndsWith(".spriteatlasv2", StringComparison.OrdinalIgnoreCase) ||
                AssetDatabase.LoadMainAssetAtPath(path) != null ||
                File.Exists(path))
                throw new ArgumentException("existing or unsafe atlas destination");

            SpriteAtlasAsset candidate = new SpriteAtlasAsset();
            bool saved = false;
            try
            {
                var packables = new UnityEngine.Object[textures.Length];
                for (int i = 0; i < textures.Length; i++) packables[i] = textures[i];
                candidate.Add(packables);
                // Native Unity method; writes only the explicit NEW file.
                SpriteAtlasAsset.Save(candidate, path);
                saved = true;
                AssetDatabase.ImportAsset(path);
                var importer = AssetImporter.GetAtPath(path) as SpriteAtlasImporter;
                if (importer == null)
                    throw new InvalidOperationException(
                        "candidate written but SpriteAtlasImporter is missing; inspect manually");
                importer.includeInBuild = false;
                importer.SaveAndReimport();
                AssetDatabase.SaveAssets();
                return path;
            }
            finally
            {
                // Do NOT delete the new file if the importer cannot complete.
                // Never touch existing assets or user source textures.
                if (!saved && candidate != null)
                    DestroyImmediate(candidate);
            }
        }
    }
}
