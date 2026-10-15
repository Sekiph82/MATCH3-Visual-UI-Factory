// VF-07: non-destructive uGUI starter prefab authoring. Real Canvas/Image/Button/Text.
// Disabled actions are intentionally unbound, not counterfeit gameplay.
using System;
using System.IO;
using UnityEditor;
using UnityEngine;
using UnityEngine.UI;

namespace Match3.VisualFactory.Editor
{
    public sealed class VufUiComposerWindow : EditorWindow
    {
        private static readonly string[] Profiles =
        {
            "Coral_Rescue", "Garage_Legends", "Dino_Islands",
            "The_Fractured_Realms", "Wonder_Pop"
        };
        private static readonly string[] Screens =
        {
            "Home", "Gameplay HUD", "World Map", "Shop", "Events",
            "Collection", "Settings"
        };
        private int selectedProfile;
        private int selectedScreen;
        private Color accent = new Color(.25f, .86f, .8f, 1f);
        private Color surface = new Color(.07f, .25f, .35f, 1f);

        [MenuItem("Tools/MATCH3/Interactive UI Composer")]
        public static void Open()
        {
            var window = GetWindow<VufUiComposerWindow>("VF-07 UI Composer");
            window.minSize = new Vector2(530f, 360f);
            window.Show();
        }

        private void OnGUI()
        {
            GUILayout.Label("VF-07  |  Interactive UI Composer (CANDIDATES)", EditorStyles.boldLabel);
            EditorGUILayout.HelpBox(
                "Creates real Unity uGUI prefabs: responsive Canvas, Image panels, Text, " +
                "Raycaster and Button. All actions remain DISABLED until approved " +
                "Engine action bindings exist. This is an unstyled skeletal composition, " +
                "not one of the 28 finished Coral experiences.", MessageType.Info);
            selectedProfile = EditorGUILayout.Popup("Art profile", selectedProfile, Profiles);
            selectedScreen = EditorGUILayout.Popup("Screen type", selectedScreen, Screens);
            accent = EditorGUILayout.ColorField("Accent (draft)", accent);
            surface = EditorGUILayout.ColorField("Surface (draft)", surface);
            EditorGUILayout.LabelField("Reference portrait", "720 x 1280 (scale with screen)");
            EditorGUILayout.LabelField("Safe area", "VufSafeAreaFitter on interactive content root");
            EditorGUILayout.LabelField("Button state", "DISABLED / Unbound Engine action", EditorStyles.miniLabel);
            GUILayout.Space(12f);
            if (GUILayout.Button("Create new interactive UI candidate prefab", GUILayout.Height(36)))
                BuildCandidate();
        }

        private static GameObject CreateElement(string name, Transform parent)
        {
            GameObject obj = new GameObject(name, typeof(RectTransform));
            obj.transform.SetParent(parent, false);
            return obj;
        }

        private static void Stretch(RectTransform rect, Vector2 min, Vector2 max)
        {
            rect.anchorMin = min;
            rect.anchorMax = max;
            rect.pivot = new Vector2(.5f, .5f);
            rect.offsetMin = Vector2.zero;
            rect.offsetMax = Vector2.zero;
        }

        private static Font BuiltinFont()
        {
            try { return Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf"); }
            catch (Exception) { return null; }
        }

        private static Text AddText(Transform parent, string name,
            string message, Vector2 min, Vector2 max, int fontSize, Color color)
        {
            GameObject obj = CreateElement(name, parent);
            Stretch((RectTransform)obj.transform, min, max);
            Text text = obj.AddComponent<Text>();
            text.font = BuiltinFont();
            text.text = message;
            text.fontSize = fontSize;
            text.color = color;
            text.alignment = TextAnchor.MiddleCenter;
            text.horizontalOverflow = HorizontalWrapMode.Wrap;
            text.verticalOverflow = VerticalWrapMode.Truncate;
            text.raycastTarget = false;
            return text;
        }

        private void BuildCandidate()
        {
            string baseName = "VUF_" + Profiles[selectedProfile] + "_"
                + Screens[selectedScreen].Replace(' ', '_') + "_CANDIDATE";
            string path = EditorUtility.SaveFilePanelInProject(
                "Save new UI candidate", baseName, "prefab",
                "Choose a unique destination. An existing prefab cannot be overwritten.");
            if (string.IsNullOrEmpty(path)) return;
            if (AssetDatabase.LoadMainAssetAtPath(path) != null || File.Exists(path))
            {
                EditorUtility.DisplayDialog("Candidate protected",
                    "That path already contains an asset. Choose a new file name.", "OK");
                return;
            }
            GameObject root = new GameObject(baseName, typeof(RectTransform),
                typeof(Canvas), typeof(CanvasScaler), typeof(GraphicRaycaster));
            try
            {
                RectTransform rootRect = root.GetComponent<RectTransform>();
                rootRect.sizeDelta = new Vector2(720f, 1280f);
                Canvas canvas = root.GetComponent<Canvas>();
                canvas.renderMode = RenderMode.ScreenSpaceOverlay;
                canvas.pixelPerfect = false;
                CanvasScaler scaler = root.GetComponent<CanvasScaler>();
                scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
                scaler.referenceResolution = new Vector2(720f, 1280f);
                scaler.screenMatchMode = CanvasScaler.ScreenMatchMode.MatchWidthOrHeight;
                scaler.matchWidthOrHeight = .5f;

                GameObject background = CreateElement("Background", root.transform);
                RectTransform bgRect = (RectTransform)background.transform;
                Stretch(bgRect, Vector2.zero, Vector2.one);
                Image bg = background.AddComponent<Image>();
                bg.color = surface;
                bg.raycastTarget = false;

                GameObject safe = CreateElement("SafeArea_Content", root.transform);
                Stretch((RectTransform)safe.transform, Vector2.zero, Vector2.one);
                safe.AddComponent<VufSafeAreaFitter>();

                GameObject header = CreateElement("Header", safe.transform);
                Stretch((RectTransform)header.transform,
                    new Vector2(.06f, .83f), new Vector2(.94f, .95f));
                Image headerImage = header.AddComponent<Image>();
                headerImage.color = new Color(0f, 0f, 0f, .16f);
                headerImage.raycastTarget = false;
                AddText(header.transform, "Title", Screens[selectedScreen],
                    Vector2.zero, Vector2.one, 50, Color.white);

                GameObject panel = CreateElement("Content_Panel", safe.transform);
                Stretch((RectTransform)panel.transform,
                    new Vector2(.06f, .21f), new Vector2(.94f, .79f));
                Image panelImage = panel.AddComponent<Image>();
                panelImage.color = new Color(1f, 1f, 1f, .14f);
                panelImage.raycastTarget = false;
                AddText(panel.transform, "UnboundNotice",
                    "VIEW TEMPLATE ONLY\nNo Gameplay Binding",
                    new Vector2(.08f, .3f), new Vector2(.92f, .7f),
                    30, Color.white);

                GameObject action = CreateElement("Primary_Action_UNBOUND", safe.transform);
                Stretch((RectTransform)action.transform,
                    new Vector2(.17f, .08f), new Vector2(.83f, .16f));
                Image buttonImage = action.AddComponent<Image>();
                buttonImage.color = accent;
                Button button = action.AddComponent<Button>();
                button.targetGraphic = buttonImage;
                button.interactable = false;
                AddText(action.transform, "Label", "NOT CONNECTED",
                    Vector2.zero, Vector2.one, 30, Color.black);

                GameObject saved = PrefabUtility.SaveAsPrefabAsset(root, path);
                if (saved == null)
                    throw new InvalidOperationException("Unity could not create UI candidate prefab");
                AssetDatabase.SaveAssets();
                Selection.activeObject = saved;
                EditorGUIUtility.PingObject(saved);
            }
            finally
            {
                DestroyImmediate(root);
            }
        }
    }
}
