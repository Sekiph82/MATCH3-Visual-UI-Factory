// VF-07: read-only editor gallery of fifteen imported concept-screen PNGs.
// It is not interactive uGUI, original owner art, physical device QA or export.
using System;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;

namespace Match3.VisualFactory.Editor
{
    public sealed class VufConceptShowcaseWindow : EditorWindow
    {
        [Serializable]
        internal sealed class Screen
        {
            public string profile_id;
            public string screen_key;
            public string file;
            public int[] dimensions;
            public string png_sha256;
            public string style_source_sha256;
            public string tile_kit_atlas_sha256;
            public int seed;
            public int render_scale;
            public bool interactive;
            public string screen_state;
        }

        [Serializable]
        internal sealed class Manifest
        {
            public int schema_version;
            public string stage;
            public string generator;
            public Screen[] screens;
            public string[] profile_ids;
            public string[] screen_keys;
            public int file_count;
            public int[] dimensions;
            public bool interactive_ui_enabled;
            public bool owner_visual_approval;
            public bool asset_rights_verified;
            public string original_art;
            public bool real_device_verified;
        }

        private static readonly string[] Profiles = {
            "Coral_Rescue", "Garage_Legends", "Dino_Islands",
            "The_Fractured_Realms", "Wonder_Pop"
        };
        private static readonly string[] Pages = {"home", "gameplay", "world_map"};

        private TextAsset receipt;
        private DefaultAsset folder;
        private Texture2D[] images;
        private Manifest parsed;
        private string error;
        private bool compareFive = false;
        private int profile;
        private int focusedPage = 1;
        private Vector2 scroll;

        [MenuItem("Tools/MATCH3/Five-Game Concept Showcase")]
        public static void Open()
        {
            var window = GetWindow<VufConceptShowcaseWindow>("VUF Concept Gallery");
            window.minSize = new Vector2(750, 530);
            window.Show();
        }

        private void OnGUI()
        {
            EditorGUILayout.LabelField("VF-07 | Fifteen Mathematical Concept Screens",
                EditorStyles.boldLabel);
            EditorGUILayout.HelpBox(
                "Import COPIES of 15 PNGs and showcase_manifest.json into " +
                "an Assets folder. Preview five draft games x Home, Gameplay, " +
                "World Map. These are NONINTERACTIVE flattened concept PNGs, " +
                "never commercial artwork or uGUI Buttons. Texture pixels " +
                "are not SHA-verified in this window; use the Python verifier.",
                MessageType.Warning);
            EditorGUI.BeginChangeCheck();
            receipt = (TextAsset)EditorGUILayout.ObjectField(
                "Showcase JSON TextAsset", receipt, typeof(TextAsset), false);
            folder = (DefaultAsset)EditorGUILayout.ObjectField(
                "Imported candidate Assets folder", folder,
                typeof(DefaultAsset), false);
            if (EditorGUI.EndChangeCheck()) Reload();
            if (GUILayout.Button("Validate candidate pack read-only"))
                Reload();
            if (!String.IsNullOrEmpty(error))
                EditorGUILayout.HelpBox(error, MessageType.Error);
            if (parsed == null || images == null) return;

            EditorGUILayout.LabelField("Approval", "NOT OWNER APPROVED");
            EditorGUILayout.LabelField("Device testing", "NOT RUN");
            EditorGUILayout.LabelField("Preview size",
                parsed.dimensions[0] + " x " + parsed.dimensions[1]);
            compareFive = EditorGUILayout.Toggle("Compare five game themes", compareFive);
            if (compareFive)
                focusedPage = EditorGUILayout.Popup("Same conceptual page", focusedPage, Pages);
            else
                profile = EditorGUILayout.Popup("Game profile", profile, Profiles);

            scroll = EditorGUILayout.BeginScrollView(scroll);
            if (compareFive)
            {
                for (int i = 0; i < Profiles.Length; i++)
                {
                    EditorGUILayout.LabelField(Profiles[i], EditorStyles.boldLabel);
                    DrawImage(images[i * 3 + focusedPage], 190f);
                }
            }
            else
            {
                for (int page = 0; page < Pages.Length; page++)
                {
                    EditorGUILayout.LabelField(Pages[page], EditorStyles.boldLabel);
                    DrawImage(images[profile * 3 + page], 265f);
                }
            }
            EditorGUILayout.EndScrollView();
            EditorGUILayout.HelpBox(
                "A mathematically rasterized reference has NO real interactive " +
                "buttons, accessible text or live game state. Production art, " +
                "copyright, Unity GUI, GPU and iOS/Android approvals remain OPEN.",
                MessageType.Info);
        }

        private static void DrawImage(Texture2D tex, float maxHeight)
        {
            Rect area = GUILayoutUtility.GetRect(200f, maxHeight,
                GUILayout.ExpandWidth(true));
            EditorGUI.DrawRect(area, new Color(.09f, .12f, .18f));
            GUI.DrawTexture(area, tex, ScaleMode.ScaleToFit, true);
        }

        private void Reload()
        {
            parsed = null;
            images = null;
            error = null;
            if (receipt == null || folder == null) return;
            try
            {
                Manifest candidate = Parse(receipt.text);
                string root = AssetDatabase.GetAssetPath(folder);
                if (String.IsNullOrEmpty(root) || !root.StartsWith("Assets/",
                        StringComparison.Ordinal) ||
                    !AssetDatabase.IsValidFolder(root))
                    throw new ArgumentException("select an existing imported Assets folder");
                var loaded = new Texture2D[candidate.screens.Length];
                for (int i = 0; i < loaded.Length; i++)
                {
                    string path = root + "/" + candidate.screens[i].file;
                    Texture2D texture = AssetDatabase.LoadAssetAtPath<Texture2D>(path);
                    if (texture == null || texture.width != candidate.dimensions[0] ||
                        texture.height != candidate.dimensions[1])
                        throw new ArgumentException("missing/incorrect imported PNG: " + path);
                    loaded[i] = texture;
                }
                images = loaded;
                parsed = candidate;
            }
            catch (Exception exception)
            {
                error = "Concept gallery source rejected: " + exception.Message;
            }
        }

        internal static Manifest Parse(string json)
        {
            if (String.IsNullOrEmpty(json) || json.Length > 128000)
                throw new ArgumentException("missing/oversized concept gallery JSON");
            var result = JsonUtility.FromJson<Manifest>(json);
            if (result == null || result.schema_version != 1 ||
                result.stage != "CANDIDATE_NOT_OWNER_APPROVED" ||
                result.generator != "VF07_FIVE_GAME_CONCEPT_SCREENS_V01" ||
                result.interactive_ui_enabled || result.owner_visual_approval ||
                result.asset_rights_verified || result.real_device_verified ||
                result.original_art != "MATHEMATICAL_CONCEPT_ONLY" ||
                result.file_count != 15 ||
                result.screens == null || result.screens.Length != 15 ||
                result.profile_ids == null || result.profile_ids.Length != 5 ||
                result.screen_keys == null || result.screen_keys.Length != 3 ||
                result.dimensions == null || result.dimensions.Length != 2 ||
                ((result.dimensions[0] != 360 || result.dimensions[1] != 640) &&
                 (result.dimensions[0] != 720 || result.dimensions[1] != 1280)))
                throw new ArgumentException("gallery candidate/read-only safety contract");
            for (int i = 0; i < Profiles.Length; i++)
                if (result.profile_ids[i] != Profiles[i])
                    throw new ArgumentException("unsupported/misordered game profile");
            for (int j = 0; j < Pages.Length; j++)
                if (result.screen_keys[j] != Pages[j])
                    throw new ArgumentException("unsupported/misordered page");
            for (int n = 0; n < result.screens.Length; n++)
            {
                int game = n / Pages.Length;
                int page = n % Pages.Length;
                Screen s = result.screens[n];
                if (s == null || s.profile_id != Profiles[game] ||
                    s.screen_key != Pages[page] ||
                    s.file != "preview_" + Profiles[game] + "_" + Pages[page] + ".png" ||
                    s.interactive || s.screen_state != "VISUAL_CONCEPT_NOT_INTERACTIVE" ||
                    s.dimensions == null || s.dimensions.Length != 2 ||
                    s.dimensions[0] != result.dimensions[0] ||
                    s.dimensions[1] != result.dimensions[1] ||
                    s.render_scale != result.dimensions[0] / 360 ||
                    s.seed < 0 || s.seed > 9999)
                    throw new ArgumentException("incorrect screen geometry or identity");
                CheckSha(s.png_sha256);
                CheckSha(s.style_source_sha256);
                CheckSha(s.tile_kit_atlas_sha256);
            }
            return result;
        }

        private static void CheckSha(string value)
        {
            if (String.IsNullOrEmpty(value) || value.Length != 64)
                throw new ArgumentException("missing 64-char SHA256 receipt");
            foreach (char c in value)
                if (!(c >= '0' && c <= '9') && !(c >= 'a' && c <= 'f'))
                    throw new ArgumentException("invalid lower-case SHA256");
        }
    }
}
