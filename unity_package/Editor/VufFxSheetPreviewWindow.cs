// VF-05/VF-06: source-generated FX animation candidate preview.
// Absolutely no sprite importer edits, paid models, or production gameplay.
using System;
using UnityEditor;
using UnityEngine;

namespace Match3.VisualFactory.Editor
{
    public sealed class VufFxSheetPreviewWindow : EditorWindow
    {
        [Serializable]
        internal sealed class FxFrame
        {
            public int frame;
            public int[] pixel_rect_top_left;
            public string rgba_sha256;
        }

        [Serializable]
        internal sealed class FxManifest
        {
            public int schema_version;
            public string stage;
            public string generator;
            public string preset_id;
            public string presets_source_sha256;
            public string color;
            public int seed;
            public int fps;
            public int frame_rate;
            public int frame_count;
            public int frame_side;
            public int columns;
            public int rows;
            public int atlas_width;
            public int atlas_height;
            public string atlas_path;
            public string atlas_sha256;
            public string reduced_motion_path;
            public string reduced_motion_sha256;
            public string reduced_motion_policy;
            public bool asset_rights_verified;
            public bool engine_side_effects_allowed;
            public bool owner_visual_approval;
            public FxFrame[] animation_frames;
        }

        private static readonly string[] Presets = {
            "BubbleRise", "MatchBurst", "StarSparkle",
            "SoftDrift", "PortalPulse"
        };

        private TextAsset manifestJson;
        private Texture2D spriteSheet;
        private Texture2D reducedStill;
        private FxManifest verified;
        private string error;
        private bool play;
        private bool reducedMotion = true;
        private int frame;
        private double elapsed;
        private double lastTime;

        [MenuItem("Tools/MATCH3/Procedural FX Sheet Player")]
        public static void Open()
        {
            var window = GetWindow<VufFxSheetPreviewWindow>("VF-06 FX Frames");
            window.minSize = new Vector2(600f, 500f);
            window.Show();
        }

        private void OnEnable()
        {
            lastTime = EditorApplication.timeSinceStartup;
            EditorApplication.update += Tick;
        }

        private void OnDisable()
        {
            EditorApplication.update -= Tick;
        }

        private void Tick()
        {
            double now = EditorApplication.timeSinceStartup;
            double delta = Math.Max(0d, Math.Min(.25d, now - lastTime));
            lastTime = now;
            if (!play || reducedMotion || verified == null) return;
            elapsed += delta;
            double duration = 1d / verified.fps;
            if (elapsed >= duration)
            {
                int step = (int)(elapsed / duration);
                elapsed -= step * duration;
                frame = (frame + step) % verified.frame_count;
                Repaint();
            }
        }

        private void OnGUI()
        {
            EditorGUILayout.LabelField("VF-06 | Procedural FX Frame Player",
                EditorStyles.boldLabel);
            EditorGUILayout.HelpBox(
                "Loads existing candidate fx_sheet.png, reduced_motion.png and " +
                "fx_manifest.json imported into Unity. No package edits, game " +
                "events, approved art, GPU shaders, or commercial sprite output. " +
                "Source SHA receipts are metadata, NOT cryptographically checked here.",
                MessageType.Warning);
            EditorGUI.BeginChangeCheck();
            manifestJson = (TextAsset)EditorGUILayout.ObjectField(
                "Candidate FX JSON", manifestJson, typeof(TextAsset), false);
            spriteSheet = (Texture2D)EditorGUILayout.ObjectField(
                "Frame atlas", spriteSheet, typeof(Texture2D), false);
            reducedStill = (Texture2D)EditorGUILayout.ObjectField(
                "Reduced-motion still", reducedStill, typeof(Texture2D), false);
            if (EditorGUI.EndChangeCheck()) Revalidate();
            if (GUILayout.Button("Validate frame geometry (read-only)")) Revalidate();
            if (!String.IsNullOrEmpty(error))
                EditorGUILayout.HelpBox(error, MessageType.Error);
            if (verified == null) return;

            EditorGUILayout.LabelField("VFX draft preset", verified.preset_id);
            EditorGUILayout.LabelField("Candidate status", verified.stage);
            reducedMotion = EditorGUILayout.Toggle("Reduced-motion still", reducedMotion);
            using (new EditorGUI.DisabledScope(reducedMotion))
            {
                if (GUILayout.Button(play ? "Pause" : "Play"))
                {
                    play = !play;
                    elapsed = 0;
                }
            }
            if (reducedMotion) play = false;
            frame = EditorGUILayout.IntSlider("Frame scrub", frame, 0,
                verified.frame_count - 1);
            GUILayout.Space(10f);
            Rect outer = GUILayoutUtility.GetRect(220f, 360f, 170f, 360f,
                GUILayout.ExpandWidth(true), GUILayout.ExpandHeight(true));
            float square = Mathf.Min(outer.width - 12f, outer.height - 12f);
            Rect canvas = new Rect(outer.center.x - square * .5f,
                outer.center.y - square * .5f, square, square);
            EditorGUI.DrawRect(outer, new Color(.09f, .12f, .20f));
            if (reducedMotion)
            {
                GUI.DrawTexture(canvas, reducedStill, ScaleMode.ScaleToFit, true);
            }
            else
            {
                FxFrame selected = verified.animation_frames[frame];
                int[] rect = selected.pixel_rect_top_left;
                Rect uv = new Rect((float)rect[0] / verified.atlas_width,
                    (float)(verified.atlas_height - rect[1] - rect[3]) /
                        verified.atlas_height,
                    (float)rect[2] / verified.atlas_width,
                    (float)rect[3] / verified.atlas_height);
                GUI.DrawTextureWithTexCoords(canvas, spriteSheet, uv, true);
            }
            EditorGUILayout.LabelField("Playback", "EDITOR VIEW ONLY");
            EditorGUILayout.LabelField("Reduced-motion fallback",
                verified.reduced_motion_policy);
            EditorGUILayout.HelpBox(
                "Real Sprite importer slicing, SpriteRenderer AnimationClip, " +
                "shader blending, VFX lifecycle, mobile GPU cost and owner " +
                "asset approval remain independent tests.",
                MessageType.Info);
        }

        private void Revalidate()
        {
            verified = null;
            error = null;
            play = false;
            frame = 0;
            elapsed = 0;
            if (manifestJson == null || spriteSheet == null || reducedStill == null)
                return;
            try
            {
                verified = Parse(manifestJson.text,
                    spriteSheet.width, spriteSheet.height,
                    reducedStill.width, reducedStill.height);
            }
            catch (Exception exception)
            {
                error = exception.Message;
            }
        }

        internal static FxManifest Parse(string json, int width, int height,
            int stillWidth, int stillHeight)
        {
            if (String.IsNullOrEmpty(json) || json.Length > 64000)
                throw new ArgumentException("missing or oversized FX manifest");
            FxManifest result = JsonUtility.FromJson<FxManifest>(json);
            if (result == null || result.schema_version != 1 ||
                result.stage != "CANDIDATE_NOT_OWNER_APPROVED" ||
                result.generator != "VF06_PROCEDURAL_FX_SHEET_V01" ||
                result.asset_rights_verified || result.owner_visual_approval ||
                result.engine_side_effects_allowed ||
                result.reduced_motion_policy != "STATIC_VIEW_ONLY" ||
                result.atlas_path != "fx_sheet.png" ||
                result.reduced_motion_path != "reduced_motion.png" ||
                Array.IndexOf(Presets, result.preset_id) < 0 ||
                result.frame_count < 2 || result.frame_count > 32 ||
                result.frame_side < 16 || result.frame_side > 128 ||
                result.columns < 1 || result.columns > result.frame_count ||
                result.rows != (result.frame_count + result.columns - 1) / result.columns ||
                result.fps < 1 || result.fps > 60 ||
                result.frame_rate != result.fps ||
                result.atlas_width != result.frame_side * result.columns ||
                result.atlas_height != result.frame_side * result.rows ||
                width != result.atlas_width || height != result.atlas_height ||
                stillWidth != result.frame_side || stillHeight != result.frame_side ||
                result.animation_frames == null ||
                result.animation_frames.Length != result.frame_count)
                throw new ArgumentException("invalid FX candidate geometry/policy");
            Sha(result.atlas_sha256);
            Sha(result.reduced_motion_sha256);
            Sha(result.presets_source_sha256);
            for (int i = 0; i < result.animation_frames.Length; ++i)
            {
                FxFrame item = result.animation_frames[i];
                if (item == null || item.frame != i ||
                    item.pixel_rect_top_left == null ||
                    item.pixel_rect_top_left.Length != 4)
                    throw new ArgumentException("frame sequence missing/reordered");
                int[] rect = item.pixel_rect_top_left;
                if (rect[0] != i % result.columns * result.frame_side ||
                    rect[1] != i / result.columns * result.frame_side ||
                    rect[2] != result.frame_side || rect[3] != result.frame_side)
                    throw new ArgumentException("frame has wrong atlas rect");
                Sha(item.rgba_sha256);
            }
            return result;
        }

        private static void Sha(string value)
        {
            if (String.IsNullOrEmpty(value) || value.Length != 64)
                throw new ArgumentException("missing content SHA-256");
            foreach (char c in value)
                if (!(c >= '0' && c <= '9') && !(c >= 'a' && c <= 'f'))
                    throw new ArgumentException("bad lowercase SHA-256 receipt");
        }
    }
}
