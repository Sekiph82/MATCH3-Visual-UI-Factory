// VF-07: build an EDITABLE Unity uGUI candidate stage from a concept reference.
// Concept PNG stays a NONINTERACTIVE RawImage, never a flattened game UI.
// Screen title/action/policy/safe-area are distinct editable components.
using System;
using System.IO;
using System.Security.Cryptography;
using UnityEditor;
using UnityEngine;
using UnityEngine.UI;

namespace Match3.VisualFactory.Editor
{
    public sealed class VufConceptStageBuilderWindow : EditorWindow
    {
        private static readonly string[] Profiles = {
            "Coral_Rescue", "Garage_Legends", "Dino_Islands",
            "The_Fractured_Realms", "Wonder_Pop"
        };
        private static readonly string[] Pages = { "home", "gameplay", "world_map" };
        private const string Gate = "REQUIRES_ENGINE_OR_GAME_BINDING";
        private TextAsset manifestJson;
        private DefaultAsset candidateFolder;
        private int profile;
        private int page;
        private bool includeConcept = true;
        private string error;
        private VufConceptShowcaseWindow.Manifest verified;

        [MenuItem("Tools/MATCH3/Editable Concept UI Stage Builder")]
        public static void Open()
        {
            var window = GetWindow<VufConceptStageBuilderWindow>("VUF Stage Builder");
            window.minSize = new Vector2(630, 520);
            window.Show();
        }

        private void OnGUI()
        {
            EditorGUILayout.LabelField("VF-07 | Editable Five-Game UI Concept Stages",
                EditorStyles.boldLabel);
            EditorGUILayout.HelpBox(
                "Creates a NEW, genuinely editable uGUI prefab with distinct " +
                "Text, disabled Button, safe-area metadata, and an optional " +
                "RawImage reference underneath. The imported PNG is only a " +
                "visual sketch. No Engine calls, active game Buttons, approved " +
                "art, screenshot/device certification or original-art rights.",
                MessageType.Warning);
            EditorGUI.BeginChangeCheck();
            manifestJson = (TextAsset)EditorGUILayout.ObjectField(
                "15-screen concept manifest", manifestJson,
                typeof(TextAsset), false);
            candidateFolder = (DefaultAsset)EditorGUILayout.ObjectField(
                "Imported reference Assets folder", candidateFolder,
                typeof(DefaultAsset), false);
            profile = EditorGUILayout.Popup("Game", profile, Profiles);
            page = EditorGUILayout.Popup("Editable screen", page, Pages);
            includeConcept = EditorGUILayout.Toggle(
                "Include visible reference RawImage", includeConcept);
            if (EditorGUI.EndChangeCheck()) Reload();
            if (GUILayout.Button("Revalidate selected concept identity"))
                Reload();
            if (!String.IsNullOrEmpty(error))
                EditorGUILayout.HelpBox(error, MessageType.Error);
            EditorGUILayout.HelpBox(
                "Authoring only: draw new real UI elements in the prefab and " +
                "replace the reference image after visual review. No flattened " +
                "PNG is wired to touches, gameplay, rewards or the Match3 Engine.",
                MessageType.Info);
            using (new EditorGUI.DisabledScope(verified == null))
            {
                if (GUILayout.Button("Create NEW editable candidate prefab",
                    GUILayout.Height(34)))
                    Create();
            }
        }

        private void Reload()
        {
            verified = null;
            error = null;
            if (manifestJson == null || candidateFolder == null) return;
            try
            {
                verified = VufConceptShowcaseWindow.Parse(manifestJson.text);
                string root = AssetDatabase.GetAssetPath(candidateFolder);
                if (String.IsNullOrEmpty(root) ||
                    !root.StartsWith("Assets/", StringComparison.Ordinal) ||
                    !AssetDatabase.IsValidFolder(root))
                    throw new ArgumentException("imported folder must be under Assets");
                // Source report is validated, but PNG content hashes MUST still be
                // independently verified by Python before owner art review.
                if (includeConcept) FindTexture(verified, root, profile, page);
            }
            catch (Exception e)
            {
                error = "Candidate concept not ready: " + e.Message;
                verified = null;
            }
        }

        private static Texture2D FindTexture(
            VufConceptShowcaseWindow.Manifest report,
            string folder, int game, int screen)
        {
            if (game < 0 || game >= Profiles.Length ||
                screen < 0 || screen >= Pages.Length)
                throw new ArgumentOutOfRangeException("game/screen");
            var entry = report.screens[game * Pages.Length + screen];
            string target = folder + "/" + entry.file;
            var texture = AssetDatabase.LoadAssetAtPath<Texture2D>(target);
            if (texture == null ||
                texture.width != report.dimensions[0] ||
                texture.height != report.dimensions[1])
                throw new ArgumentException("missing/different imported concept: " + target);
            VerifyImportedPng(texture, entry.png_sha256);
            return texture;
        }

        // A hash receipt proves byte consistency with its manifest, NOT
        // originality, copyright, license or human creative approval.
        internal static void VerifyImportedPng(Texture2D texture, string expectedSha)
        {
            if (texture == null || String.IsNullOrEmpty(expectedSha) ||
                expectedSha.Length != 64)
                throw new ArgumentException("missing imported texture or hash");
            string path = AssetDatabase.GetAssetPath(texture);
            if (String.IsNullOrEmpty(path) ||
                !path.StartsWith("Assets/", StringComparison.Ordinal) ||
                !path.EndsWith(".png", StringComparison.OrdinalIgnoreCase))
                throw new ArgumentException("expected imported Assets PNG");
            string assetsRoot = Path.GetFullPath(Application.dataPath);
            string full = Path.GetFullPath(Path.Combine(
                assetsRoot, path.Substring("Assets/".Length)));
            if (!full.StartsWith(
                    assetsRoot.TrimEnd(Path.DirectorySeparatorChar) +
                    Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase))
                throw new ArgumentException("reference escapes Unity Assets");
            string cursor = full;
            while (true)
            {
                if ((File.GetAttributes(cursor) & FileAttributes.ReparsePoint) != 0)
                    throw new ArgumentException("linked imported source forbidden");
                if (String.Equals(cursor, assetsRoot,
                    StringComparison.OrdinalIgnoreCase))
                    break;
                string parent = Path.GetDirectoryName(cursor);
                if (String.IsNullOrEmpty(parent))
                    throw new ArgumentException("asset path ancestry invalid");
                cursor = parent;
            }
            var info = new FileInfo(full);
            if (!info.Exists || info.Length > 16 * 1024 * 1024 || info.Length < 16)
                throw new ArgumentException("imported PNG missing/oversized");
            using (SHA256 sha = SHA256.Create())
            using (FileStream stream = File.OpenRead(full))
            {
                byte[] digest = sha.ComputeHash(stream);
                string actual = BitConverter.ToString(digest).Replace("-", "")
                    .ToLowerInvariant();
                if (!String.Equals(actual, expectedSha, StringComparison.Ordinal))
                    throw new ArgumentException("imported PNG SHA-256 differs from manifest");
            }
        }

        private void Create()
        {
            Reload();
            if (verified == null) return;
            string folder = AssetDatabase.GetAssetPath(candidateFolder);
            Texture2D texture = includeConcept ?
                FindTexture(verified, folder, profile, page) : null;
            string title = "VUF_" + Profiles[profile] + "_" +
                Pages[page] + "_EDITABLE_CANDIDATE";
            string path = EditorUtility.SaveFilePanelInProject(
                "Create NEW editable concept uGUI stage", title, "prefab",
                "No old candidate/prefab can be overwritten.");
            if (String.IsNullOrEmpty(path)) return;
            if (!path.StartsWith("Assets/", StringComparison.Ordinal) ||
                AssetDatabase.LoadMainAssetAtPath(path) != null ||
                File.Exists(path))
            {
                error = "Refused existing or non-Assets prefab destination";
                return;
            }
            GameObject stage = null;
            try
            {
                stage = BuildStage(verified, profile, page, texture,
                    VufScreenCatalog.LoadStyle(Profiles[profile]));
                var result = PrefabUtility.SaveAsPrefabAsset(stage, path);
                if (result == null)
                    throw new InvalidOperationException("Unity returned null prefab");
                AssetDatabase.SaveAssets();
                Selection.activeObject = result;
                EditorGUIUtility.PingObject(result);
            }
            catch (Exception e) { error = "Prefab not created: " + e.Message; }
            finally
            {
                if (stage != null) DestroyImmediate(stage);
            }
        }

        private static RectTransform Node(Transform parent, string name,
            Vector2 min, Vector2 max)
        {
            var root = new GameObject(name, typeof(RectTransform));
            var rect = root.GetComponent<RectTransform>();
            rect.SetParent(parent, false);
            rect.anchorMin = min;
            rect.anchorMax = max;
            rect.offsetMin = Vector2.zero;
            rect.offsetMax = Vector2.zero;
            rect.pivot = new Vector2(.5f, .5f);
            return rect;
        }

        private static Text Label(Transform parent, string name, string value,
            Vector2 min, Vector2 max, int size, Color ink)
        {
            RectTransform rect = Node(parent, name, min, max);
            Text label = rect.gameObject.AddComponent<Text>();
            label.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            label.fontSize = size;
            label.alignment = TextAnchor.MiddleCenter;
            label.text = value;
            label.color = ink;
            label.horizontalOverflow = HorizontalWrapMode.Wrap;
            label.verticalOverflow = VerticalWrapMode.Truncate;
            label.raycastTarget = false;
            return label;
        }

        // No writes, no AssetDatabase calls and no active game interactivity.
        // Caller owns the returned in-memory GameObject and must destroy it.
        internal static GameObject BuildStage(
            VufConceptShowcaseWindow.Manifest report,
            int profileIndex, int pageIndex, Texture2D reference,
            VufScreenCatalog.StyleInfo style)
        {
            if (report == null || style == null || style.palettes == null ||
                profileIndex < 0 || profileIndex >= Profiles.Length ||
                pageIndex < 0 || pageIndex >= Pages.Length ||
                style.id != Profiles[profileIndex])
                throw new ArgumentException("unknown concept profile, page or style");
            // Validate the *entire* owner-unapproved 15-screen source
            // again. Never trust a manually constructed mutable report.
            report = VufConceptShowcaseWindow.Parse(JsonUtility.ToJson(report));
            var selected = report.screens[profileIndex * Pages.Length + pageIndex];
            if (selected.profile_id != style.id ||
                selected.screen_key != Pages[pageIndex] ||
                (reference != null &&
                 (reference.width != report.dimensions[0] ||
                  reference.height != report.dimensions[1])))
                throw new ArgumentException("concept texture/profile identity mismatch");
            Color background = VufScreenCatalog.ParseColor(
                style.palettes.background, "background");
            Color accent = VufScreenCatalog.ParseColor(style.palettes.cta, "cta");
            Color surface = VufScreenCatalog.ParseColor(
                style.palettes.surface, "surface");
            Color ink = VufScreenCatalog.ParseColor(style.palettes.text, "text");
            var root = new GameObject("VUF_" + style.id + "_" + selected.screen_key +
                "_EDITABLE_CANDIDATE", typeof(RectTransform), typeof(Canvas),
                typeof(CanvasScaler), typeof(GraphicRaycaster),
                typeof(VufCandidateScreenMarker));
            try
            {
                var rect = root.GetComponent<RectTransform>();
                rect.sizeDelta = new Vector2(720, 1280);
                root.GetComponent<Canvas>().renderMode = RenderMode.ScreenSpaceOverlay;
                var scaler = root.GetComponent<CanvasScaler>();
                scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
                scaler.referenceResolution = new Vector2(720, 1280);
                scaler.screenMatchMode = CanvasScaler.ScreenMatchMode.MatchWidthOrHeight;
                scaler.matchWidthOrHeight = .5f;
                root.GetComponent<VufCandidateScreenMarker>().SetCandidate(
                    style.id, "CONCEPT-" + (pageIndex + 1).ToString("D2"),
                    selected.screen_key, "page", Gate);

                RectTransform bg = Node(root.transform, "BackgroundColor",
                    Vector2.zero, Vector2.one);
                var fill = bg.gameObject.AddComponent<Image>();
                fill.color = background;
                fill.raycastTarget = false;

                RectTransform safe = Node(root.transform, "SafeArea_ReviewOnly",
                    Vector2.zero, Vector2.one);
                safe.gameObject.AddComponent<VufSafeAreaFitter>();
                if (reference != null)
                {
                    RectTransform refLayer = Node(safe,
                        "ConceptReference_NONINTERACTIVE_REPLACE_ME",
                        new Vector2(.02f, .10f), new Vector2(.98f, .88f));
                    var raw = refLayer.gameObject.AddComponent<RawImage>();
                    raw.texture = reference;
                    raw.color = new Color(1, 1, 1, .60f);
                    raw.raycastTarget = false;
                }
                RectTransform header = Node(safe, "EditableTitleBanner",
                    new Vector2(.04f, .88f), new Vector2(.96f, .955f));
                var band = header.gameObject.AddComponent<Image>();
                band.color = surface;
                band.raycastTarget = false;
                Label(header, "EditableHeading", style.id.Replace('_', ' ') +
                    " / " + selected.screen_key.Replace('_', ' '),
                    Vector2.zero, Vector2.one, 32, ink);
                RectTransform cta = Node(safe, "EditablePrimaryAction_UNBOUND",
                    new Vector2(.13f, .075f), new Vector2(.87f, .145f));
                var buttonBg = cta.gameObject.AddComponent<Image>();
                buttonBg.color = accent;
                buttonBg.raycastTarget = true;
                var button = cta.gameObject.AddComponent<Button>();
                button.targetGraphic = buttonBg;
                button.interactable = false;
                Label(cta, "ActionLabel", "NOT CONNECTED TO GAME",
                    Vector2.zero, Vector2.one, 24, background);
                Label(safe, "FeatureGate_AlwaysVisible",
                    Gate + " | NOT AN INTERACTIVE UI | CANDIDATE",
                    new Vector2(.025f, .008f), new Vector2(.975f, .066f), 17, ink);
                Label(safe, "OwnerReviewWarning",
                    "CONCEPT IMAGE ONLY / ORIGINAL ART AND DEVICE QA OPEN",
                    new Vector2(.04f, .81f), new Vector2(.96f, .875f), 15, ink);
                return root;
            }
            catch
            {
                UnityEngine.Object.DestroyImmediate(root);
                throw;
            }
        }
    }
}
