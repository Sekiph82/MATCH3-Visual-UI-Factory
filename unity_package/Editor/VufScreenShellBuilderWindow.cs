// VF-07 experimental data-driven screen shell editor.
// Every exported shell remains a candidate. NO screens are game-ready.
using System;
using System.IO;
using UnityEditor;
using UnityEngine;
using UnityEngine.UI;

namespace Match3.VisualFactory.Editor
{
    public sealed class VufScreenShellBuilderWindow : EditorWindow
    {
        private static readonly string[] Profiles = {
            "Coral_Rescue", "Garage_Legends", "Dino_Islands",
            "The_Fractured_Realms", "Wonder_Pop"
        };
        private VufScreenCatalog.ScreenInfo[] screens;
        private string error;
        private int profileIndex;
        private int screenIndex;
        private int previewStateIndex;
        private int previewLocaleIndex;
        private string[] labels;
        private bool showCandidateGate = true;

        [MenuItem("Tools/MATCH3/28-Screen Shell Builder")]
        public static void Open()
        {
            var window = GetWindow<VufScreenShellBuilderWindow>("VUF 28 Screens");
            window.minSize = new Vector2(610f, 520f);
            window.Show();
        }

        private void OnEnable()
        {
            ReloadContract();
        }

        private void ReloadContract()
        {
            screens = null;
            error = null;
            try
            {
                screens = VufScreenCatalog.LoadScreens();
                labels = new string[screens.Length];
                for (int i = 0; i < screens.Length; ++i)
                    labels[i] = screens[i].id + "  " +
                        VufScreenCatalog.DisplayName(screens[i]) +
                        "  [" + screens[i].kind + "]";
                screenIndex = Mathf.Clamp(screenIndex, 0, screens.Length - 1);
            }
            catch (Exception ex)
            {
                error = ex.Message;
                labels = new string[0];
            }
        }

        private void OnGUI()
        {
            EditorGUILayout.LabelField("VF-07 | 28 Coral Experience Shells", EditorStyles.boldLabel);
            EditorGUILayout.HelpBox(
                "This tool reads the exact draft 28-ID Coral Rescue contract and five draft " +
                "Style Bibles. It creates NON-OVERRIDING candidate uGUI prefabs with real " +
                "Canvas, Images, Text and disabled Button. These are layout skeletons, " +
                "not approved game screens, illustrations, animations, gameplay or rewards.",
                MessageType.Info);
            if (GUILayout.Button("Reload checked schema and style catalog"))
                ReloadContract();
            if (error != null || screens == null)
            {
                EditorGUILayout.HelpBox("Cannot author candidate: " + error, MessageType.Error);
                return;
            }
            profileIndex = EditorGUILayout.Popup("Draft Style Bible", profileIndex, Profiles);
            screenIndex = EditorGUILayout.Popup("Screen", screenIndex, labels);
            previewStateIndex = EditorGUILayout.Popup("Review-only state",
                previewStateIndex, VufReviewStateCatalog.States);
            previewLocaleIndex = EditorGUILayout.Popup("Draft copy locale",
                previewLocaleIndex, new[] { "English mock", "Turkish mock", "Expanded stress mock" });
            showCandidateGate = EditorGUILayout.Toggle("Show binding warning", showCandidateGate);
            var selected = screens[screenIndex];
            EditorGUILayout.LabelField("Stable ID", selected.id);
            EditorGUILayout.LabelField("Surface kind", selected.kind);
            EditorGUILayout.LabelField("Feature gate", selected.feature_gate);
            EditorGUILayout.HelpBox(
                "State selector is a review label only. It does not simulate " +
                "Engine state or allow real purchases, friend invitations or tournaments.",
                MessageType.Warning);
            GUILayout.Space(10f);
            if (GUILayout.Button("Create NEW Candidate uGUI Prefab", GUILayout.Height(36f)))
            {
                try { CreateCandidate(selected); }
                catch (Exception ex) { Debug.LogError("VUF 28-screen candidate failed: " + ex); }
            }
        }

        private static GameObject Element(string name, Transform parent)
        {
            GameObject instance = new GameObject(name, typeof(RectTransform));
            instance.transform.SetParent(parent, false);
            return instance;
        }

        private static RectTransform Place(Transform root, string name,
            Vector2 from, Vector2 to)
        {
            var rect = (RectTransform)Element(name, root).transform;
            rect.anchorMin = from;
            rect.anchorMax = to;
            rect.pivot = new Vector2(.5f, .5f);
            rect.offsetMin = Vector2.zero;
            rect.offsetMax = Vector2.zero;
            return rect;
        }

        private static Image Colored(RectTransform rect, Color color, bool raycast = false)
        {
            Image image = rect.gameObject.AddComponent<Image>();
            image.color = color;
            image.raycastTarget = raycast;
            return image;
        }

        private static Text Label(Transform root, string name, string message,
            Vector2 min, Vector2 max, int fontSize, Color color)
        {
            RectTransform rect = Place(root, name, min, max);
            Text label = rect.gameObject.AddComponent<Text>();
            label.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            label.text = message;
            label.fontSize = fontSize;
            label.alignment = TextAnchor.MiddleCenter;
            label.horizontalOverflow = HorizontalWrapMode.Wrap;
            label.verticalOverflow = VerticalWrapMode.Truncate;
            label.color = color;
            label.raycastTarget = false;
            return label;
        }

        private static void DisabledAction(Transform root, string name,
            string label, Color accent, Color onAccent, Vector2 min, Vector2 max)
        {
            RectTransform rect = Place(root, name + "_UNBOUND", min, max);
            Image image = Colored(rect, accent, true);
            Button button = rect.gameObject.AddComponent<Button>();
            button.targetGraphic = image;
            button.interactable = false;
            Label(rect, "ActionLabel", label, Vector2.zero, Vector2.one, 28, onAccent);
        }

        private static void ContentCard(Transform root, string title,
            Color color, Color font, Vector2 min, Vector2 max)
        {
            RectTransform panel = Place(root, "PlaceholderCard_" + title, min, max);
            Colored(panel, color);
            Label(panel, "PlaceholderText", title + "\nORIGINAL ART NOT YET REVIEWED",
                new Vector2(.04f, .12f), new Vector2(.96f, .88f), 24, font);
        }

        private void CreateCandidate(VufScreenCatalog.ScreenInfo spec)
        {
            VufScreenCatalog.StyleInfo style = VufScreenCatalog.LoadStyle(
                Profiles[profileIndex]);
            string assetName = "VUF_" + style.id + "_" + spec.id + "_" +
                spec.key + "_CANDIDATE";
            string path = EditorUtility.SaveFilePanelInProject(
                "New 28-Screen Candidate", assetName, "prefab",
                "Choose a unique new prefab path. Existing approved/candidate files are protected.");
            if (String.IsNullOrEmpty(path))
                return;
            if (AssetDatabase.LoadMainAssetAtPath(path) != null || File.Exists(path))
            {
                EditorUtility.DisplayDialog("Protected existing prefab",
                    "Target already exists. Select another candidate path. No file was modified.",
                    "OK");
                return;
            }
            GameObject root = BuildCandidateHierarchy(spec, style, showCandidateGate);
            try
            {
                VufReviewStateCatalog.Apply(root, spec,
                    VufReviewStateCatalog.States[previewStateIndex],
                    VufReviewStateCatalog.Locales[previewLocaleIndex]);
                GameObject asset = PrefabUtility.SaveAsPrefabAsset(root, path);
                if (asset == null)
                    throw new InvalidOperationException("Unity prefab writer returned null");
                AssetDatabase.SaveAssets();
                Selection.activeObject = asset;
                EditorGUIUtility.PingObject(asset);
            }
            finally
            {
                DestroyImmediate(root);
            }
        }

        // Shared by the manual save action and in-memory EditMode tests. This method
        // never writes an asset; callers own and must destroy the returned hierarchy.
        internal static GameObject BuildCandidateHierarchy(
            VufScreenCatalog.ScreenInfo spec, VufScreenCatalog.StyleInfo style,
            bool includeOwnerReviewWarning)
        {
            if (spec == null) throw new ArgumentNullException(nameof(spec));
            if (style == null || style.palettes == null)
                throw new ArgumentNullException(nameof(style));
            var colors = style.palettes;
            Color background = VufScreenCatalog.ParseColor(colors.background, "background");
            Color surface = VufScreenCatalog.ParseColor(colors.surface, "surface");
            Color accent = VufScreenCatalog.ParseColor(colors.cta, "cta");
            Color ctaLabel = VufScreenCatalog.ParseColor(colors.cta_label, "cta_label");
            Color font = VufScreenCatalog.ParseColor(colors.text, "text");
            string assetName = "VUF_" + style.id + "_" + spec.id + "_" +
                spec.key + "_CANDIDATE";
            GameObject root = new GameObject(assetName, typeof(RectTransform),
                typeof(Canvas), typeof(CanvasScaler), typeof(GraphicRaycaster),
                typeof(VufCandidateScreenMarker));
            try
            {
                RectTransform rect = root.GetComponent<RectTransform>();
                rect.sizeDelta = new Vector2(720f, 1280f);
                Canvas canvas = root.GetComponent<Canvas>();
                canvas.renderMode = RenderMode.ScreenSpaceOverlay;
                var scaler = root.GetComponent<CanvasScaler>();
                scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
                scaler.referenceResolution = new Vector2(720f, 1280f);
                scaler.screenMatchMode = CanvasScaler.ScreenMatchMode.MatchWidthOrHeight;
                scaler.matchWidthOrHeight = .5f;
                root.GetComponent<VufCandidateScreenMarker>().SetCandidate(
                    style.id, spec.id, spec.key, spec.kind, spec.feature_gate);

                RectTransform bg = Place(root.transform, "BackgroundColor",
                    Vector2.zero, Vector2.one);
                Colored(bg, background);
                RectTransform safe = Place(root.transform, "SafeArea_ReviewOnly",
                    Vector2.zero, Vector2.one);
                safe.gameObject.AddComponent<VufSafeAreaFitter>();

                RectTransform title = Place(safe, "TitleBanner",
                    new Vector2(.05f, .86f), new Vector2(.95f, .96f));
                Colored(title, surface);
                Label(title, "Heading", VufScreenCatalog.DisplayName(spec),
                    Vector2.zero, Vector2.one, 42, font);

                bool isDialog = spec.kind == "modal" || spec.kind == "ceremony" ||
                    spec.kind == "overlay";
                bool isBoard = spec.kind == "playable" || spec.kind == "mode";
                if (isDialog)
                {
                    safe.gameObject.AddComponent<CanvasGroup>();
                    safe.gameObject.AddComponent<VufUiTween>();
                    ContentCard(safe, "MODAL OR REWARD CEREMONY", surface, font,
                        new Vector2(.07f, .28f), new Vector2(.93f, .75f));
                }
                else if (isBoard)
                {
                    ContentCard(safe, "ENGINE BOARD SLOT (UNBOUND)", surface, font,
                        new Vector2(.05f, .28f), new Vector2(.95f, .82f));
                    ContentCard(safe, "BOOSTER / SCORE HUD SLOT", surface, font,
                        new Vector2(.05f, .18f), new Vector2(.95f, .26f));
                }
                else
                {
                    ContentCard(safe, "HERO / COLLECTION SLOT", surface, font,
                        new Vector2(.07f, .47f), new Vector2(.93f, .82f));
                    ContentCard(safe, "CONTENT CARDS / ORIGINAL ART", surface, font,
                        new Vector2(.07f, .24f), new Vector2(.93f, .44f));
                }
                DisabledAction(safe, "PrimaryAction", "NOT CONNECTED",
                    accent, ctaLabel, new Vector2(.16f, .08f), new Vector2(.84f, .17f));

                string gate = spec.feature_gate == "OFF_UNTIL_ENGINE_POLICY_CONFIRMED" ?
                    "POLICY OFF: NOT AVAILABLE IN DEMO" :
                    "ENGINE/GAME BINDING REQUIRED";
                Label(safe, "FeatureGate_AlwaysVisible",
                    spec.id + " | " + gate + " | CANDIDATE",
                    new Vector2(.04f, .015f), new Vector2(.96f, .07f),
                    19, font);
                Label(safe, "ReviewState_AlwaysVisible",
                    "MOCK READY / EN / NOT GAME STATE",
                    new Vector2(.06f, .765f), new Vector2(.94f, .802f),
                    17, font);
                if (includeOwnerReviewWarning)
                    Label(safe, "OwnerReviewWarning",
                        "OWNER ART AND DEVICE QA NOT COMPLETE",
                        new Vector2(.06f, .79f), new Vector2(.94f, .855f),
                        20, font);
                return root;
            }
            catch
            {
                DestroyImmediate(root);
                throw;
            }
        }
    }
}
