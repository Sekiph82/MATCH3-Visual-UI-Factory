// VF-05 / VF-06: explicit author-only procedural FX -> real Unity AnimationClip.
// Requires importer-sliced user sprites. Never modifies importer or overwrites
// existing clips. Cannot enable gameplay, publish or verify source ownership.
using System;
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEngine;

namespace Match3.VisualFactory.Editor
{
    public sealed class VufFxClipExporterWindow : EditorWindow
    {
        private Texture2D sheet;
        private Texture2D still;
        private TextAsset manifestJson;
        private VufFxSheetPreviewWindow.FxManifest parsed;
        private List<Sprite> resolved;
        private string error;
        private bool loop = true;

        [MenuItem("Tools/MATCH3/Procedural FX Clip Exporter")]
        public static void Open()
        {
            var window = GetWindow<VufFxClipExporterWindow>("VF-05 FX Clip");
            window.minSize = new Vector2(620f, 450f);
            window.Show();
        }

        private void OnGUI()
        {
            EditorGUILayout.LabelField("VF-05 | Procedural FX to SpriteRenderer Clip",
                EditorStyles.boldLabel);
            EditorGUILayout.HelpBox(
                "Import a COPY of candidate fx_sheet.png using Sprite (Multiple), " +
                "open Sprite Editor and manually slice every square frame; keep " +
                "frame pixels, rotation and order unchanged. This tool NEVER edits " +
                "TextureImporter. Manifest/rects must exactly match. Creates only " +
                "a new candidate SpriteRenderer .anim on explicit save. An " +
                "independent reduced-motion still must remain available.",
                MessageType.Warning);
            EditorGUI.BeginChangeCheck();
            manifestJson = (TextAsset)EditorGUILayout.ObjectField("FX manifest JSON",
                manifestJson, typeof(TextAsset), false);
            sheet = (Texture2D)EditorGUILayout.ObjectField("Sliced Sprite (Multiple) atlas",
                sheet, typeof(Texture2D), false);
            still = (Texture2D)EditorGUILayout.ObjectField("Reduced-motion still",
                still, typeof(Texture2D), false);
            loop = EditorGUILayout.Toggle("Loop candidate clip", loop);
            if (EditorGUI.EndChangeCheck()) Revalidate();
            if (GUILayout.Button("Revalidate exact frame/texture contract"))
                Revalidate();
            if (!String.IsNullOrEmpty(error))
                EditorGUILayout.HelpBox(error, MessageType.Error);
            if (parsed == null || resolved == null) return;
            EditorGUILayout.LabelField("Candidate state", parsed.stage);
            EditorGUILayout.LabelField("Preset", parsed.preset_id);
            EditorGUILayout.LabelField("Frames", resolved.Count.ToString());
            EditorGUILayout.LabelField("FPS", parsed.fps.ToString());
            EditorGUILayout.LabelField("Reduced-motion still",
                still.name + " (SEPARATE, NOT AUTO-LINKED)");
            EditorGUILayout.HelpBox(
                "These are synthetic authoring FX. Real 2D sprite clip will be " +
                "written only if you choose a new path; no source rights or " +
                "owner sign-off are inferred. Real UI, GPU, physical phones " +
                "and motion-accessibility testing remain OPEN.",
                MessageType.Info);
            if (GUILayout.Button("Create new candidate SpriteRenderer .anim",
                GUILayout.Height(32f)))
            {
                string path = EditorUtility.SaveFilePanelInProject(
                    "Create NEW procedural FX candidate clip",
                    parsed.preset_id + "_VUF_Candidate", "anim",
                    "Existing animation clips cannot be overwritten.");
                if (String.IsNullOrEmpty(path)) return;
                if (AssetDatabase.LoadMainAssetAtPath(path) != null || File.Exists(path))
                {
                    EditorUtility.DisplayDialog("Target protected",
                        "An asset already exists at this path. Choose a new candidate name.",
                        "OK");
                    return;
                }
                try
                {
                    // Re-read imported sprites immediately before creating any asset;
                    // don't trust stale selections after a TextureImporter change.
                    List<Sprite> actual = ReadImportedSprites(sheet);
                    AnimationClip clip = BuildVerifiedClip(
                        path, parsed, sheet, still, actual, loop);
                    AssetDatabase.CreateAsset(clip, path);
                    AssetDatabase.SaveAssets();
                    Selection.activeObject = clip;
                    EditorGUIUtility.PingObject(clip);
                }
                catch (Exception ex)
                {
                    error = "Candidate clip refused: " + ex.Message;
                }
            }
        }

        private void Revalidate()
        {
            parsed = null;
            resolved = null;
            error = null;
            if (manifestJson == null || sheet == null || still == null) return;
            try
            {
                parsed = VufFxSheetPreviewWindow.Parse(manifestJson.text,
                    sheet.width, sheet.height, still.width, still.height);
                resolved = MatchFrames(parsed, sheet, ReadImportedSprites(sheet));
            }
            catch (Exception e)
            {
                error = "Source/texture/clip contract mismatch: " + e.Message;
                parsed = null;
            }
        }

        private static List<Sprite> ReadImportedSprites(Texture2D atlas)
        {
            string path = AssetDatabase.GetAssetPath(atlas);
            if (String.IsNullOrEmpty(path))
                throw new ArgumentException("Atlas must be imported as a project asset");
            var found = new List<Sprite>();
            foreach (UnityEngine.Object asset in AssetDatabase.LoadAllAssetsAtPath(path))
            {
                Sprite sprite = asset as Sprite;
                if (sprite != null) found.Add(sprite);
            }
            return found;
        }

        internal static List<Sprite> MatchFrames(
            VufFxSheetPreviewWindow.FxManifest manifest,
            Texture2D atlas, IList<Sprite> available)
        {
            if (manifest == null || atlas == null || available == null)
                throw new ArgumentNullException("manifest/atlas/sprites");
            if (available.Count != manifest.frame_count)
                throw new ArgumentException("expected precisely one Unity Sprite per FX frame");
            if (atlas.width != manifest.atlas_width ||
                atlas.height != manifest.atlas_height)
                throw new ArgumentException("atlas resized/recompressed unexpectedly");
            var sorted = new List<Sprite>();
            var used = new HashSet<Sprite>();
            foreach (var entry in manifest.animation_frames)
            {
                int[] rect = entry.pixel_rect_top_left;
                // Generated PNG manifests use top-left pixels, Unity Sprite.rect
                // uses bottom-left origin. Require exact unrotated unit rects.
                float bx = rect[0], by = manifest.atlas_height - rect[1] - rect[3];
                Sprite match = null;
                foreach (Sprite sprite in available)
                {
                    if (sprite == null || sprite.packed ||
                        sprite.texture != atlas || used.Contains(sprite)) continue;
                    Rect current = sprite.rect;
                    if (Mathf.Abs(current.x - bx) <= .01f &&
                        Mathf.Abs(current.y - by) <= .01f &&
                        Mathf.Abs(current.width - rect[2]) <= .01f &&
                        Mathf.Abs(current.height - rect[3]) <= .01f)
                    {
                        if (match != null)
                            throw new ArgumentException("ambiguous overlapping imported sprite rectangles");
                        match = sprite;
                    }
                }
                if (match == null)
                    throw new ArgumentException("missing exact unrotated candidate frame " + entry.frame);
                sorted.Add(match);
                used.Add(match);
            }
            return sorted;
        }

        internal static AnimationClip BuildVerifiedClip(string name,
            VufFxSheetPreviewWindow.FxManifest manifest,
            Texture2D atlas, Texture2D reducedMotion,
            IList<Sprite> imported, bool loop)
        {
            if (manifest == null || atlas == null || reducedMotion == null)
                throw new ArgumentNullException("manifest/atlas/reducedMotion");
            // Internal callers and NUnit fixtures must not bypass the
            // candidate-only safety/parser checks used by the GUI.
            VufFxSheetPreviewWindow.Parse(JsonUtility.ToJson(manifest),
                atlas.width, atlas.height, reducedMotion.width, reducedMotion.height);
            if (reducedMotion.width != manifest.frame_side ||
                reducedMotion.height != manifest.frame_side ||
                manifest.reduced_motion_policy != "STATIC_VIEW_ONLY")
                throw new ArgumentException("missing reduced-motion fallback");
            List<Sprite> frames = MatchFrames(manifest, atlas, imported);
            return VufSpriteClipBuilderWindow.BuildCandidateClip(
                name, frames, manifest.fps, false, loop);
        }
    }
}
