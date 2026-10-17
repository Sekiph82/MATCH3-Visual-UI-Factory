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

        private void SaveNew()
        {
            Texture2D[] textures = ValidateDraft(selected);
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
            string path = EditorUtility.SaveFilePanelInProject(
                "Create NEW unapproved SpriteAtlas V2",
                "VUF_SpriteAtlasV2_CANDIDATE", "spriteatlasv2",
                "Pick an unused Assets path. NEVER overwrite an atlas.");
            if (String.IsNullOrEmpty(path)) return;
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
                lastCandidate = path;
                Selection.activeObject = AssetDatabase.LoadMainAssetAtPath(path);
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
