// VF-04 / VF-09 read-only atlas candidate inspector. No changes to source art.
using System;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;

namespace Match3.VisualFactory.Editor
{
    public sealed class VufAtlasPreviewWindow : EditorWindow
    {
        [Serializable]
        internal sealed class AtlasSprite
        {
            public string asset_id;
            public int width;
            public int height;
            public int[] pixel_rect_top_left;
            public float[] uv_rect_bottom_left;
            public bool rotated;
        }

        [Serializable]
        internal sealed class AtlasManifest
        {
            public int schema_version;
            public string stage;
            public string generator;
            public string atlas_sha256;
            public int width;
            public int height;
            public AtlasSprite[] sprites;
        }

        private Texture2D atlas;
        private TextAsset manifestText;
        private AtlasManifest manifest;
        private string error;
        private int selected;
        private Vector2 scroll;
        private bool drawGrid = true;
        private bool drawLabels = true;
        private readonly List<Rect> mappedRects = new List<Rect>();

        [MenuItem("Tools/MATCH3/Sprite Atlas Inspector")]
        public static void Open()
        {
            var window = GetWindow<VufAtlasPreviewWindow>("VF-04 Atlas Inspector");
            window.minSize = new Vector2(610f, 540f);
            window.Show();
        }

        private void OnGUI()
        {
            GUILayout.Label("VF-04 | Atlas Geometry & Pixel Preview", EditorStyles.boldLabel);
            EditorGUILayout.HelpBox(
                "Read-only preview of VF04 atlas.png + atlas_manifest.json imported into " +
                "Unity as candidate files. This is NOT an atlas exporter, rights verifier, " +
                "device memory profiler or approved SpriteAtlas asset.", MessageType.Info);
            EditorGUI.BeginChangeCheck();
            atlas = (Texture2D)EditorGUILayout.ObjectField(
                "Atlas Texture", atlas, typeof(Texture2D), false);
            manifestText = (TextAsset)EditorGUILayout.ObjectField(
                "Atlas JSON", manifestText, typeof(TextAsset), false);
            if (EditorGUI.EndChangeCheck())
                Recheck();
            drawGrid = EditorGUILayout.Toggle("Show sprite bounding boxes", drawGrid);
            drawLabels = EditorGUILayout.Toggle("Show sprite names", drawLabels);
            if (GUILayout.Button("Revalidate candidate geometry"))
                Recheck();

            if (error != null)
            {
                EditorGUILayout.HelpBox(error, MessageType.Warning);
                return;
            }
            if (manifest == null)
            {
                EditorGUILayout.HelpBox("Select both candidate files to inspect.", MessageType.None);
                return;
            }

            EditorGUILayout.LabelField("Candidate state", manifest.stage, EditorStyles.boldLabel);
            EditorGUILayout.LabelField("Sprites", manifest.sprites.Length.ToString());
            if (manifest.sprites.Length > 0)
            {
                string[] names = Array.ConvertAll(manifest.sprites, x => x.asset_id);
                selected = Mathf.Clamp(selected, 0, names.Length - 1);
                selected = EditorGUILayout.Popup("Highlighted sprite", selected, names);
            }
            float w = Mathf.Max(100f, position.width - 40f);
            float h = Mathf.Min(430f, w * atlas.height / atlas.width);
            Rect outer = GUILayoutUtility.GetRect(w, h + 10f,
                GUILayout.ExpandWidth(true), GUILayout.Height(h + 10f));
            Rect draw = new Rect(
                outer.x + (outer.width - w) / 2f, outer.y + 3f, w, h);
            EditorGUI.DrawRect(draw, new Color(.10f, .10f, .13f));
            GUI.DrawTexture(draw, atlas, ScaleMode.StretchToFill, true);
            if (drawGrid)
                DrawRects(draw);
            scroll = EditorGUILayout.BeginScrollView(scroll);
            foreach (AtlasSprite item in manifest.sprites)
            {
                int[] rect = item.pixel_rect_top_left;
                EditorGUILayout.LabelField(item.asset_id,
                    "X=" + rect[0] + " Y=" + rect[1] +
                    " W=" + rect[2] + " H=" + rect[3]);
            }
            EditorGUILayout.EndScrollView();
            EditorGUILayout.HelpBox(
                "The manifest SHA is source metadata. This Unity importer preview " +
                "does not independently hash imported PNG bytes. Verify original " +
                "SHA using the offline VF04 tools before approval.", MessageType.None);
        }

        private void DrawRects(Rect canvas)
        {
            float sx = canvas.width / manifest.width;
            float sy = canvas.height / manifest.height;
            for (int i = 0; i < mappedRects.Count; ++i)
            {
                Rect rect = mappedRects[i];
                Rect box = new Rect(canvas.x + rect.x * sx, canvas.y + rect.y * sy,
                    rect.width * sx, rect.height * sy);
                Color c = i == selected ?
                    new Color(.99f, .75f, .14f, .98f) :
                    new Color(.49f, .94f, .91f, .88f);
                const float border = 2f;
                EditorGUI.DrawRect(new Rect(box.x, box.y, box.width, border), c);
                EditorGUI.DrawRect(new Rect(box.x, box.yMax - border, box.width, border), c);
                EditorGUI.DrawRect(new Rect(box.x, box.y, border, box.height), c);
                EditorGUI.DrawRect(new Rect(box.xMax - border, box.y, border, box.height), c);
                if (drawLabels)
                    GUI.Label(new Rect(box.x + 3f, box.y + 3f, box.width, 18f),
                        manifest.sprites[i].asset_id, EditorStyles.miniBoldLabel);
            }
        }

        private void Recheck()
        {
            error = null;
            manifest = null;
            mappedRects.Clear();
            selected = 0;
            if (manifestText == null || atlas == null)
                return;
            try
            {
                mappedRects.AddRange(ValidateCandidateGeometry(
                    manifestText.text, atlas.width, atlas.height, out manifest));
            }
            catch (Exception ex)
            {
                manifest = null;
                error = "VF-04 Atlas inspection rejected: " + ex.Message;
            }
        }

        // Same geometry validation used by the inspector, callable with in-memory
        // synthetic metadata and actual Texture2D dimensions without asset writes.
        internal static Rect[] ValidateCandidateGeometry(string json,
            int atlasWidth, int atlasHeight, out AtlasManifest document)
        {
            document = JsonUtility.FromJson<AtlasManifest>(json);
            if (document == null || document.schema_version != 1 ||
                document.stage != "CANDIDATE_NOT_APPROVED" ||
                document.generator != "VF04_SHELF_PACK_V01" ||
                document.width < 1 || document.height < 1 ||
                document.width != atlasWidth || document.height != atlasHeight ||
                document.sprites == null || document.sprites.Length == 0 ||
                document.sprites.Length > 128)
                throw new ArgumentException("candidate schema/texture dimension mismatch");
            var ids = new HashSet<string>(StringComparer.Ordinal);
            var rectangles = new List<Rect>();
            foreach (AtlasSprite item in document.sprites)
            {
                if (item == null || String.IsNullOrEmpty(item.asset_id) ||
                    !ids.Add(item.asset_id) || item.rotated ||
                    item.pixel_rect_top_left == null || item.pixel_rect_top_left.Length != 4 ||
                    item.uv_rect_bottom_left == null || item.uv_rect_bottom_left.Length != 4)
                    throw new ArgumentException("duplicate/unsupported sprite entry");
                int[] r = item.pixel_rect_top_left;
                if (r[0] < 0 || r[1] < 0 || r[2] <= 0 || r[3] <= 0 ||
                    r[0] + r[2] > document.width || r[1] + r[3] > document.height ||
                    item.width != r[2] || item.height != r[3])
                    throw new ArgumentException("sprite rect outside atlas");
                float[] uv = item.uv_rect_bottom_left;
                float[] expected = {
                    (float)r[0] / document.width,
                    (float)(document.height - r[1] - r[3]) / document.height,
                    (float)r[2] / document.width,
                    (float)r[3] / document.height
                };
                for (int i = 0; i < 4; i++)
                    if (float.IsNaN(uv[i]) || float.IsInfinity(uv[i]) ||
                        Mathf.Abs(expected[i] - uv[i]) > 0.00001f)
                        throw new ArgumentException("sprite rect UV mapping mismatch");
                Rect box = new Rect(r[0], r[1], r[2], r[3]);
                foreach (Rect other in rectangles)
                    if (box.Overlaps(other))
                        throw new ArgumentException("overlapping sprite rectangles");
                rectangles.Add(box);
            }
            return rectangles.ToArray();
        }
    }
}
