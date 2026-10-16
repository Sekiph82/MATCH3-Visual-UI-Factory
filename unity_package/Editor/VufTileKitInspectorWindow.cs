// VF-01/VF-04: visually inspect mathematical six-tile candidate atlas.
// Does not validate art ownership, actual texture bytes or game rules.
using System;
using UnityEditor;
using UnityEngine;

namespace Match3.VisualFactory.Editor
{
    public sealed class VufTileKitInspectorWindow : EditorWindow
    {
        [Serializable]
        internal sealed class Tile
        {
            public string shape;
            public string file;
            public string file_sha256;
            public string rgba_sha256;
            public int[] pixel_rect_top_left;
        }

        [Serializable]
        internal sealed class Manifest
        {
            public int schema_version;
            public string stage;
            public string generator;
            public string profile_id;
            public string style_source_sha256;
            public string[] silhouette_keys;
            public int side;
            public string format;
            public string atlas_path;
            public int[] atlas_dimensions;
            public string atlas_sha256;
            public Tile[] tiles;
            public string original_art;
            public bool asset_rights_verified;
            public bool gameplay_bindings_enabled;
            public bool owner_visual_approval;
        }

        private static readonly string[] Profiles = {
            "Coral_Rescue", "Garage_Legends", "Dino_Islands",
            "The_Fractured_Realms", "Wonder_Pop"
        };
        private static readonly string[] Shapes = {
            "circle", "triangle", "diamond", "star", "crescent", "shield"
        };

        private Texture2D atlas;
        private TextAsset manifestJson;
        private Manifest manifest;
        private string error;
        private int selected;

        [MenuItem("Tools/MATCH3/Five-Game Tile Kit Inspector")]
        public static void Open()
        {
            var window = GetWindow<VufTileKitInspectorWindow>("VF-04 Six Tiles");
            window.minSize = new Vector2(580f, 520f);
            window.Show();
        }

        private void OnGUI()
        {
            EditorGUILayout.LabelField("VF-01 / VF-04 | Five-Game Silhouette Kit",
                EditorStyles.boldLabel);
            EditorGUILayout.HelpBox(
                "Inspect generated PNG candidate atlas, not final premium artwork. " +
                "This viewer cannot verify original PNG bytes against recorded " +
                "hashes; run verify_generated_kits.py tiles BEFORE source review. " +
                "No gameplay binding, SpriteImporter change or owner approval.",
                MessageType.Warning);
            EditorGUI.BeginChangeCheck();
            atlas = (Texture2D)EditorGUILayout.ObjectField(
                "Atlas imported Texture2D", atlas, typeof(Texture2D), false);
            manifestJson = (TextAsset)EditorGUILayout.ObjectField(
                "Tile manifest JSON", manifestJson, typeof(TextAsset), false);
            if (EditorGUI.EndChangeCheck())
                Inspect();
            if (GUILayout.Button("Read-only geometry validation"))
                Inspect();
            if (!String.IsNullOrEmpty(error))
                EditorGUILayout.HelpBox(error, MessageType.Error);
            if (manifest == null || atlas == null) return;
            EditorGUILayout.LabelField("Theme", manifest.profile_id);
            EditorGUILayout.LabelField("Candidate status", manifest.stage);
            EditorGUILayout.LabelField("Source art", "MATHEMATICAL PROTOTYPE");
            selected = EditorGUILayout.Popup("Highlighted silhouette", selected, Shapes);
            Rect area = GUILayoutUtility.GetRect(250f, 540f, 190f, 400f,
                GUILayout.ExpandWidth(true), GUILayout.ExpandHeight(true));
            float width = Mathf.Min(area.width - 12f, (area.height - 12f) * 3f / 2f);
            float height = width * 2f / 3f;
            Rect surface = new Rect(area.center.x - width * .5f,
                area.center.y - height * .5f, width, height);
            EditorGUI.DrawRect(area, new Color(.09f, .13f, .20f));
            GUI.DrawTexture(surface, atlas, ScaleMode.StretchToFill, true);
            for (int i = 0; i < manifest.tiles.Length; i++)
            {
                int[] r = manifest.tiles[i].pixel_rect_top_left;
                float x = surface.x + r[0] / (float)manifest.atlas_dimensions[0] * surface.width;
                float y = surface.y + r[1] / (float)manifest.atlas_dimensions[1] * surface.height;
                Rect box = new Rect(x, y,
                    r[2] / (float)manifest.atlas_dimensions[0] * surface.width,
                    r[3] / (float)manifest.atlas_dimensions[1] * surface.height);
                Color stroke = i == selected ? Color.yellow : new Color(1f, 1f, 1f, .55f);
                EditorGUI.DrawRect(new Rect(box.x, box.y, box.width, 1f), stroke);
                EditorGUI.DrawRect(new Rect(box.x, box.yMax - 1f, box.width, 1f), stroke);
                EditorGUI.DrawRect(new Rect(box.x, box.y, 1f, box.height), stroke);
                EditorGUI.DrawRect(new Rect(box.xMax - 1f, box.y, 1f, box.height), stroke);
            }
            EditorGUILayout.HelpBox(
                "Actual iPhone/Android GPU display, premium graphic quality, " +
                "copyright/asset rights and owner artistic approval remain OPEN.",
                MessageType.Info);
        }

        private void Inspect()
        {
            manifest = null;
            error = null;
            if (atlas == null || manifestJson == null) return;
            try
            {
                manifest = Parse(manifestJson.text, atlas.width, atlas.height);
                selected = Mathf.Clamp(selected, 0, manifest.tiles.Length - 1);
            }
            catch (Exception e) { error = "Unsafe/invalid kit: " + e.Message; }
        }

        internal static Manifest Parse(string json, int width, int height)
        {
            if (String.IsNullOrEmpty(json) || json.Length > 64000)
                throw new ArgumentException("missing or too large tile kit manifest");
            Manifest parsed = JsonUtility.FromJson<Manifest>(json);
            if (parsed == null || parsed.schema_version != 1 ||
                parsed.stage != "CANDIDATE_NOT_OWNER_APPROVED" ||
                parsed.generator != "VF04_SIX_SILHOUETTE_TILE_KIT_V01" ||
                Array.IndexOf(Profiles, parsed.profile_id) < 0 ||
                parsed.asset_rights_verified || parsed.owner_visual_approval ||
                parsed.gameplay_bindings_enabled ||
                parsed.original_art != "MATHEMATICAL_PROTOTYPE_NOT_OWNER_ART" ||
                parsed.side < 24 || parsed.side > 128 ||
                parsed.format != "RGBA8_UNROTATED" ||
                parsed.atlas_path != "tile_atlas.png" ||
                parsed.atlas_dimensions == null || parsed.atlas_dimensions.Length != 2 ||
                parsed.atlas_dimensions[0] != parsed.side * 3 ||
                parsed.atlas_dimensions[1] != parsed.side * 2 ||
                width != parsed.atlas_dimensions[0] ||
                height != parsed.atlas_dimensions[1] ||
                parsed.silhouette_keys == null || parsed.silhouette_keys.Length != 6 ||
                parsed.tiles == null || parsed.tiles.Length != 6)
                throw new ArgumentException("tile contract/approval/atlas geometry mismatch");
            Sha(parsed.style_source_sha256);
            Sha(parsed.atlas_sha256);
            for (int i = 0; i < 6; i++)
            {
                if (parsed.silhouette_keys[i] != Shapes[i])
                    throw new ArgumentException("silhouette identity contract changed");
                Tile tile = parsed.tiles[i];
                if (tile == null || tile.shape != Shapes[i] ||
                    tile.file != "tile_" + Shapes[i] + ".png" ||
                    tile.pixel_rect_top_left == null ||
                    tile.pixel_rect_top_left.Length != 4)
                    throw new ArgumentException("wrong tile shape or file");
                int[] r = tile.pixel_rect_top_left;
                if (r[0] != i % 3 * parsed.side ||
                    r[1] != i / 3 * parsed.side ||
                    r[2] != parsed.side || r[3] != parsed.side)
                    throw new ArgumentException("wrong sprite atlas cell");
                Sha(tile.file_sha256);
                Sha(tile.rgba_sha256);
            }
            return parsed;
        }

        private static void Sha(string value)
        {
            if (String.IsNullOrEmpty(value) || value.Length != 64)
                throw new ArgumentException("missing SHA256 receipt");
            foreach (char c in value)
                if (!(c >= '0' && c <= '9') && !(c >= 'a' && c <= 'f'))
                    throw new ArgumentException("invalid lowercase SHA256 receipt");
        }
    }
}
