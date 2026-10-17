// VUF-M06 | Manual candidate environment layer/parallax review.
// INTERNAL_REUSE: Unity EditorWindow, JsonUtility and AssetDatabase.
// READ-ONLY inspector for copies imported into Assets. Not real Engine UI,
// no runtime parallax logic, no owner rights/art/GPU/device approval.
using System;
using System.IO;
using System.Security.Cryptography;
using UnityEditor;
using UnityEngine;

namespace Match3.VisualFactory.Editor
{
    public sealed class VufSceneLayerReviewWindow : EditorWindow
    {
        [Serializable]
        public sealed class SceneManifest
        {
            public int schema_version;
            public string stage;
            public string generator;
            public int scene_count;
            public int file_count;
            public bool release_allowed;
            public bool owner_visual_approval;
            public bool art_rights_verified;
            public bool real_device_verified;
            public bool real_engine_visual_binding;
            public bool parallax_runtime_validated;
            public SceneItem[] scenes;
        }

        [Serializable]
        public sealed class SceneItem
        {
            public string profile_id;
            public string scene_id;
            public bool runtime_ui_separate;
            public bool owner_visual_approved;
            public SceneLayer[] layers;
        }

        [Serializable]
        public sealed class SceneLayer
        {
            public string profile_id;
            public string scene_id;
            public string layer_id;
            public string file;
            public string png_sha256;
            public string style_source_sha256;
            public int draw_order;
            public int parallax_factor_milli;
            public int[] dimensions;
            public bool interactive;
            public bool contains_runtime_text;
            public bool contains_runtime_buttons;
            public bool not_owner_approved;
        }

        private static readonly string[] Profiles = {
            "Coral_Rescue", "Garage_Legends", "Dino_Islands",
            "The_Fractured_Realms", "Wonder_Pop"
        };
        private static readonly string[] CommonScenes = {
            "world_map", "chapter_map", "gameplay"
        };
        private static readonly string[] CoralExtra = {
            "reef_restoration", "marine_collection", "my_aquarium", "new_region"
        };
        private static readonly string[] LayerNames = {
            "backdrop", "distant_environment", "near_decoration"
        };
        private static readonly int[] ParallaxMilli = { 0, 120, 340 };

        [SerializeField] private TextAsset manifestSource;
        [SerializeField] private int profileIndex;
        [SerializeField] private int sceneIndex;
        [SerializeField] private int aspectIndex;
        [SerializeField] private float parallaxPixels;
        [SerializeField] private bool showSafeGuide = true;
        private SceneManifest validated;
        private string validationMessage;
        private string inspectedHashes;
        private readonly Texture2D[] loaded = new Texture2D[3];

        [MenuItem("Tools/MATCH3/Environment Layer & Parallax Review")]
        public static void Open()
        {
            var window = GetWindow<VufSceneLayerReviewWindow>("VUF Scene Layers");
            window.minSize = new Vector2(660, 690);
            window.Show();
        }

        public static SceneManifest ValidateJson(string json)
        {
            if (String.IsNullOrEmpty(json) || json.Length > 256 * 1024)
                throw new ArgumentException("candidate JSON missing or oversized");
            SceneManifest manifest;
            try { manifest = JsonUtility.FromJson<SceneManifest>(json); }
            catch (ArgumentException e)
            {
                throw new ArgumentException("invalid Unity scene-layer JSON", e);
            }
            if (manifest == null || manifest.schema_version != 1 ||
                manifest.stage != "CANDIDATE_NOT_OWNER_APPROVED" ||
                manifest.generator != "VUF_M06_MATH_LAYERED_SCENES_V01" ||
                manifest.scene_count != 19 || manifest.file_count != 57 ||
                manifest.release_allowed || manifest.owner_visual_approval ||
                manifest.art_rights_verified || manifest.real_device_verified ||
                manifest.real_engine_visual_binding ||
                manifest.parallax_runtime_validated ||
                manifest.scenes == null || manifest.scenes.Length != 19)
                throw new ArgumentException("invalid or claimed-approved scene manifest");
            int index = 0;
            for (int p = 0; p < Profiles.Length; p++)
            {
                string[] scenes = ScenesFor(p);
                for (int page = 0; page < scenes.Length; page++)
                {
                    SceneItem row = manifest.scenes[index++];
                    if (row == null || row.profile_id != Profiles[p] ||
                        row.scene_id != scenes[page] || !row.runtime_ui_separate ||
                        row.owner_visual_approved ||
                        row.layers == null || row.layers.Length != 3)
                        throw new ArgumentException("incorrect scene order or owner flag");
                    for (int i = 0; i < 3; i++)
                    {
                        SceneLayer layer = row.layers[i];
                        string expectedFile =
                            Profiles[p].ToLowerInvariant() + "_" + row.scene_id +
                            "_" + LayerNames[i] + ".png";
                        if (layer == null ||
                            layer.profile_id != Profiles[p] ||
                            layer.scene_id != row.scene_id ||
                            layer.layer_id != LayerNames[i] ||
                            layer.file != expectedFile ||
                            layer.draw_order != i ||
                            layer.parallax_factor_milli != ParallaxMilli[i] ||
                            layer.dimensions == null || layer.dimensions.Length != 2 ||
                            (layer.dimensions[0] != 180 && layer.dimensions[0] != 360) ||
                            layer.dimensions[1] != layer.dimensions[0] * 320 / 180 ||
                            !IsSha(layer.png_sha256) ||
                            !IsSha(layer.style_source_sha256) ||
                            layer.interactive || layer.contains_runtime_text ||
                            layer.contains_runtime_buttons || !layer.not_owner_approved)
                            throw new ArgumentException("invalid layer/PNG/presentation metadata");
                    }
                }
            }
            return manifest;
        }

        private static bool IsSha(string digest)
        {
            if (String.IsNullOrEmpty(digest) || digest.Length != 64) return false;
            foreach (char c in digest)
                if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f')))
                    return false;
            return true;
        }

        private static string[] ScenesFor(int profile)
        {
            if (profile != 0) return CommonScenes;
            var all = new string[CommonScenes.Length + CoralExtra.Length];
            Array.Copy(CommonScenes, all, CommonScenes.Length);
            Array.Copy(CoralExtra, 0, all, CommonScenes.Length, CoralExtra.Length);
            return all;
        }

        private SceneItem Selected()
        {
            if (validated == null) return null;
            int idx = 0;
            for (int n = 0; n < profileIndex; n++) idx += ScenesFor(n).Length;
            return validated.scenes[idx + sceneIndex];
        }

        private static string Sha256(byte[] data)
        {
            using (var sha = SHA256.Create())
            {
                return BitConverter.ToString(sha.ComputeHash(data))
                    .Replace("-", "").ToLowerInvariant();
            }
        }

        private void ValidateSourceAssets()
        {
            for (int i = 0; i < loaded.Length; i++) loaded[i] = null;
            inspectedHashes = null;
            var scene = Selected();
            if (scene == null || manifestSource == null)
                throw new InvalidOperationException("select a candidate manifest");
            string path = AssetDatabase.GetAssetPath(manifestSource);
            if (String.IsNullOrEmpty(path) ||
                !path.StartsWith("Assets/", StringComparison.Ordinal) ||
                !path.EndsWith(".json", StringComparison.OrdinalIgnoreCase))
                throw new ArgumentException("manifest must be imported into Assets as JSON");
            string folder = path.Substring(0, path.LastIndexOf('/'));
            for (int i = 0; i < 3; i++)
            {
                SceneLayer spec = scene.layers[i];
                string pngPath = folder + "/" + spec.file;
                var texture = AssetDatabase.LoadAssetAtPath<Texture2D>(pngPath);
                if (texture == null || texture.width != spec.dimensions[0] ||
                    texture.height != spec.dimensions[1])
                    throw new ArgumentException("missing/mis-sized imported layer: " + pngPath);
                // The source original bytes are the imported-copy PNG on disk,
                // not the Unity decompressed platform texture.
                var file = Path.Combine(Directory.GetCurrentDirectory(), pngPath);
                if (!File.Exists(file) ||
                    (File.GetAttributes(file) & FileAttributes.ReparsePoint) != 0 ||
                    new FileInfo(file).Length > 4 * 1024 * 1024 ||
                    Sha256(File.ReadAllBytes(file)) != spec.png_sha256)
                    throw new ArgumentException("source PNG SHA differs from manifest: " + pngPath);
                loaded[i] = texture;
            }
            inspectedHashes = "3 imported-copy PNG byte hashes matched; " +
                "Editor screenshot and platform GPU are NOT verified";
        }

        private void OnGUI()
        {
            EditorGUILayout.LabelField("M06 | Layered environment candidate Studio",
                                       EditorStyles.boldLabel);
            EditorGUILayout.HelpBox(
                "Import COPIES of scene_pack_manifest.json and its 57 PNGs " +
                "together into an Assets folder. This window NEVER writes importer " +
                "settings or game state. Preview is a synthetic parallax/safe-area " +
                "aid, NOT real device, owner artistic or runtime acceptance.",
                MessageType.Warning);
            TextAsset newManifest = (TextAsset)EditorGUILayout.ObjectField(
                "Scene pack manifest", manifestSource, typeof(TextAsset), false);
            if (newManifest != manifestSource)
            {
                manifestSource = newManifest;
                validated = null;
                inspectedHashes = null;
                for (int i = 0; i < loaded.Length; i++) loaded[i] = null;
            }
            if (GUILayout.Button("Validate 19-scene candidate metadata"))
            {
                try
                {
                    validated = ValidateJson(manifestSource != null ?
                                             manifestSource.text : null);
                    for (int i = 0; i < loaded.Length; i++) loaded[i] = null;
                    validationMessage = "Structural manifest accepted as UNAPPROVED CANDIDATE";
                }
                catch (Exception e)
                {
                    validated = null;
                    validationMessage = "REJECTED: " + e.Message;
                }
                inspectedHashes = null;
            }
            if (!String.IsNullOrEmpty(validationMessage))
                EditorGUILayout.HelpBox(validationMessage,
                    validated == null ? MessageType.Error : MessageType.Info);
            if (validated == null) return;

            int nextProfile = EditorGUILayout.Popup("Game theme", profileIndex, Profiles);
            if (nextProfile != profileIndex)
            {
                profileIndex = nextProfile;
                sceneIndex = 0;
                inspectedHashes = null;
                for (int i = 0; i < loaded.Length; i++) loaded[i] = null;
            }
            int nextScene = EditorGUILayout.Popup("Scene", sceneIndex, ScenesFor(profileIndex));
            if (nextScene != sceneIndex)
            {
                sceneIndex = nextScene;
                inspectedHashes = null;
                for (int i = 0; i < loaded.Length; i++) loaded[i] = null;
            }
            aspectIndex = EditorGUILayout.Popup("Synthetic preview ratio", aspectIndex,
                new[] { "9:16 phone", "9:19.5 tall phone", "3:4 tablet" });
            parallaxPixels = EditorGUILayout.Slider(
                "Manual camera offset px", parallaxPixels, -160f, 160f);
            showSafeGuide = EditorGUILayout.Toggle("Show synthetic safe zone", showSafeGuide);
            if (GUILayout.Button("Verify 3 imported PNG SHA256 + load preview"))
            {
                try { ValidateSourceAssets(); validationMessage = null; }
                catch (Exception e) { inspectedHashes = null; validationMessage = e.Message; }
            }
            if (!String.IsNullOrEmpty(inspectedHashes))
                EditorGUILayout.HelpBox(inspectedHashes, MessageType.Info);
            else if (!String.IsNullOrEmpty(validationMessage))
                EditorGUILayout.HelpBox("Layer verification: " + validationMessage,
                                        MessageType.Warning);
            Rect available = GUILayoutUtility.GetRect(
                320f, 460f, GUILayout.ExpandWidth(true));
            EditorGUI.DrawRect(available, new Color(0.08f, 0.09f, 0.13f, 1f));
            float ratio = aspectIndex == 0 ? 9f / 16f :
                          aspectIndex == 1 ? 9f / 19.5f : 3f / 4f;
            float outW = Mathf.Min(available.width, available.height * ratio);
            float outH = outW / ratio;
            Rect rect = new Rect(available.center.x - outW / 2f,
                                 available.center.y - outH / 2f, outW, outH);
            GUI.BeginGroup(rect);
            for (int i = 0; i < loaded.Length; i++)
            {
                if (loaded[i] != null)
                {
                    float dx = parallaxPixels * ParallaxMilli[i] / 1000f;
                    GUI.DrawTexture(new Rect(dx, 0f, rect.width, rect.height),
                                    loaded[i], ScaleMode.StretchToFill, true);
                }
            }
            if (showSafeGuide)
            {
                float insetX = rect.width * .07f, insetY = rect.height * .065f;
                var guide = new Rect(insetX, insetY, rect.width - 2f * insetX,
                                     rect.height - 2f * insetY);
                Color line = new Color(1f, 0.85f, 0.12f, 0.85f);
                EditorGUI.DrawRect(new Rect(guide.xMin, guide.yMin, guide.width, 2f), line);
                EditorGUI.DrawRect(new Rect(guide.xMin, guide.yMax - 2f, guide.width, 2f), line);
                EditorGUI.DrawRect(new Rect(guide.xMin, guide.yMin, 2f, guide.height), line);
                EditorGUI.DrawRect(new Rect(guide.xMax - 2f, guide.yMin, 2f, guide.height), line);
                GUI.Label(new Rect(guide.xMin + 4f, guide.yMin + 4f,
                                   guide.width - 8f, 20f), "SYNTHETIC SAFE AREA");
            }
            GUI.EndGroup();
        }
    }
}
