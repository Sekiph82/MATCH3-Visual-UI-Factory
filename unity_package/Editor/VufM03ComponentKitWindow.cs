// VUF-M03: five-theme real uGUI component kit, SOURCE REVIEW ONLY.
// Does not bind actions, create persistent assets, consume game events,
// infer owner art rights or change the 28-screen builder contract.
using System;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.UI;

namespace Match3.VisualFactory.Editor
{
    public sealed class VufM03ComponentKitWindow : EditorWindow
    {
        internal static readonly string[] Semantics = {
            "primary_cta", "secondary_cta", "card", "modal", "badge",
            "counter", "tab", "progress", "disabled_reason", "pending_state"
        };
        internal static readonly string[] Profiles = {
            "Coral_Rescue", "Garage_Legends", "Dino_Islands",
            "The_Fractured_Realms", "Wonder_Pop"
        };
        private VufM02StyleBibleStudioWindow.Catalog catalog;
        private GameObject preview;
        private int profileIndex, deviceIndex, stateIndex;
        private string status = "No preview built. All kit actions are unbound.";
        private Vector2 scroll;

        [MenuItem("Tools/MATCH3/M03 Five-Game Semantic Component Kit")]
        public static void Open()
        {
            var window = GetWindow<VufM03ComponentKitWindow>("M03 Component Kit");
            window.minSize = new Vector2(560, 600);
            window.Show();
        }

        private static VufM02StyleBibleStudioWindow.Catalog LoadCatalog()
        {
            var file = AssetDatabase.LoadAssetAtPath<TextAsset>(
                "Packages/com.match3.visual-factory/Editor/Resources/" +
                "m02_identity_catalog.v1.json");
            if (file == null) throw new InvalidOperationException(
                "M02 original draft identity catalog is missing");
            return VufM02StyleBibleStudioWindow.ValidateAndParse(file.text);
        }

        internal static void ValidateSemantics(
            VufM02StyleBibleStudioWindow.Identity identity)
        {
            if (identity == null || identity.ui_components == null ||
                identity.ui_components.Length != Semantics.Length ||
                identity.right_to_use !=
                "NO_OWNER_ORIGINAL_ASSET_OR_FONT_LICENCE_EVIDENCE")
                throw new ArgumentException("Missing or falsely approved M03 component contract");
            for (int i = 0; i < Semantics.Length; i++)
                if (identity.ui_components[i] != Semantics[i])
                    throw new ArgumentException(
                        "M03 semantic role missing/duplicate/reordered: " + Semantics[i]);
        }

        private static RectTransform NewRect(
            Transform parent, string name, Vector2 min, Vector2 max)
        {
            var go = new GameObject(name, typeof(RectTransform));
            var rect = go.GetComponent<RectTransform>();
            rect.SetParent(parent, false);
            rect.anchorMin = min;
            rect.anchorMax = max;
            rect.pivot = new Vector2(.5f, .5f);
            rect.offsetMin = Vector2.zero;
            rect.offsetMax = Vector2.zero;
            go.hideFlags = HideFlags.DontSaveInEditor | HideFlags.DontSaveInBuild;
            return rect;
        }

        private static Text TextNode(Transform parent, string name, string value,
            Vector2 min, Vector2 max, Color ink, int size)
        {
            var rect = NewRect(parent, name, min, max);
            var text = rect.gameObject.AddComponent<Text>();
            text.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            text.fontSize = size;
            text.text = value;
            text.color = ink;
            text.alignment = TextAnchor.MiddleCenter;
            text.horizontalOverflow = HorizontalWrapMode.Wrap;
            text.verticalOverflow = VerticalWrapMode.Truncate;
            text.raycastTarget = false;
            return text;
        }

        private static Image Panel(RectTransform rect, Color ink)
        {
            var graphic = rect.gameObject.AddComponent<Image>();
            graphic.color = ink;
            graphic.raycastTarget = false;
            return graphic;
        }

        private static void DrawSemantic(
            RectTransform root, string key, string state, Color surface,
            Color action, Color actionText, Color body, Color icon)
        {
            bool button = key == "primary_cta" ||
                          key == "secondary_cta" || key == "tab";
            bool actionFill = key == "primary_cta";
            var image = Panel(root, actionFill ? action : surface);
            // An actual uGUI Button component exists for the action roles,
            // but NEVER becomes interactive or obtains persistent listeners.
            if (button)
            {
                var control = root.gameObject.AddComponent<Button>();
                control.targetGraphic = image;
                control.interactable = false;
                control.navigation = new Navigation { mode = Navigation.Mode.None };
            }
            var ink = actionFill ? actionText : body;
            string message = key == "pending_state" ?
                "MOCK " + state.ToUpperInvariant() + "\nNO ENGINE STATE" :
                key == "disabled_reason" ? "DISABLED\nENGINE BINDING MISSING" :
                key == "counter" ? "COUNTER --\nNO GAME VALUE" :
                key == "progress" ? "PROGRESS --\nNO GAME VALUE" :
                key == "modal" ? "MODAL CONTENT\nNOT CONNECTED" :
                key == "card" ? "CARD / ART SLOT\nNOT APPROVED" :
                key == "tab" ? "TAB / UNBOUND" :
                key == "badge" ? "◇ BADGE / MOCK" :
                key.Replace('_', ' ').ToUpperInvariant() + "\nUNBOUND";
            TextNode(root, "M03_Label_" + key, message,
                new Vector2(.05f, .12f), new Vector2(.95f, .88f), ink, 17);
            if (key == "progress")
            {
                var track = NewRect(root, "M03_ProgressTrack",
                    new Vector2(.1f, .08f), new Vector2(.9f, .14f));
                Panel(track, icon);
                var fill = NewRect(track, "M03_ProgressFill_MOCK",
                    Vector2.zero, new Vector2(.35f, 1f));
                Panel(fill, action);
            }
            else if (key == "badge" || key == "counter")
            {
                var swatch = NewRect(root, "M03_SymbolInk_SOURCE_ONLY",
                    new Vector2(.02f, .35f), new Vector2(.075f, .65f));
                Panel(swatch, icon);
            }
        }

        // Returns a 10-component NATIVE Unity uGUI hierarchy. No asset writes.
        // Five profiles share exact semantic keys; only visual tokens change.
        internal static GameObject BuildCandidate(
            VufM02StyleBibleStudioWindow.Catalog input, string profileId,
            int screenIndex, string mockState)
        {
            if (input == null || input.common == null ||
                input.common.owner_auth == null ||
                input.common.owner_auth.all_approved ||
                input.common.owner_auth.original_art_received ||
                input.common.owner_auth.font_rights_verified ||
                input.common.owner_auth.device_visual_qa_verified ||
                input.common.owner_auth.engine_lfx_gameplay_verified ||
                input.common.owner_auth.production_release_allowed ||
                input.common.stage !=
                    VufM02StyleBibleStudioWindow.ExpectedStage ||
                input.common.font_license_status !=
                    "SYSTEM_FALLBACK_ONLY_UNTIL_CREATOR_PROOF" ||
                input.common.screen_modes == null ||
                input.common.screen_modes.Length != 4 ||
                input.profiles == null || input.profiles.Length != Profiles.Length ||
                Array.IndexOf(Profiles, profileId) < 0 ||
                Array.IndexOf(VufReviewStateCatalog.States, mockState) < 0 ||
                screenIndex < 0 || screenIndex >= input.common.screen_modes.Length)
                throw new ArgumentException("Unknown M03 prototype, screen or false owner authority");
            for (int i = 0; i < Profiles.Length; i++)
                if (input.profiles[i] == null ||
                    input.profiles[i].id != Profiles[i])
                    throw new ArgumentException("M03 five-game identity contract mutated");
                else ValidateSemantics(input.profiles[i]);
            VufM02StyleBibleStudioWindow.ValidateOriginalPalette(profileId);
            var mode = input.common.screen_modes[screenIndex];
            var grid = VufM02StyleBibleStudioWindow.BuildSourceGridGuide(
                input.common, mode);
            var palette = VufScreenCatalog.LoadStyle(profileId).palettes;
            var surface = VufScreenCatalog.ParseColor(palette.surface, "surface");
            var action = VufScreenCatalog.ParseColor(palette.cta, "cta");
            var actionText = VufScreenCatalog.ParseColor(
                palette.cta_label, "cta_label");
            var body = VufScreenCatalog.ParseColor(palette.text, "text");
            var icon = VufM02StyleBibleStudioWindow.GetAccessibleSymbolInk(profileId);
            var background = VufScreenCatalog.ParseColor(
                palette.background, "background");

            var root = new GameObject(
                "VUF_M03_EDITOR_ONLY_" + profileId + "_" + mode.id,
                typeof(RectTransform), typeof(Canvas), typeof(CanvasScaler));
            root.hideFlags = HideFlags.DontSaveInEditor | HideFlags.DontSaveInBuild;
            try
            {
                var rootRect = root.GetComponent<RectTransform>();
                rootRect.sizeDelta = new Vector2(mode.width_dp, mode.height_dp);
                var canvas = root.GetComponent<Canvas>();
                canvas.renderMode = RenderMode.ScreenSpaceOverlay;
                var scaler = root.GetComponent<CanvasScaler>();
                scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
                scaler.referenceResolution = rootRect.sizeDelta;

                var ground = NewRect(root.transform, "M03_Background",
                    Vector2.zero, Vector2.one);
                Panel(ground, background);
                var safe = NewRect(root.transform, "M03_SourceSafeArea",
                    new Vector2(0f, grid.Safe.yMin / mode.height_dp),
                    new Vector2(1f, grid.Safe.yMax / mode.height_dp));
                var minTouch = input.common.min_touch_dp;
                int perRow = mode.id == "portrait_tablet" ? 4 : 2;
                int margin = mode.id == "portrait_tablet" ?
                    input.common.grid.outer_margin_tablet_dp :
                    input.common.grid.outer_margin_phone_dp;
                int rows = (Semantics.Length + perRow - 1) / perRow;
                // Candidate geometry, not physical pixel/device validation.
                float gap = 8f;
                float cellWidth = (mode.width_dp - 2f * margin -
                    (perRow - 1) * gap) / perRow;
                float rowHeight = 60f;
                float totalHeight = rows * rowHeight + (rows - 1) * gap;
                if (cellWidth < minTouch || totalHeight + 92f > grid.Safe.height)
                    throw new InvalidOperationException(
                        "M03 source kit cannot fit 44dp+ cells in safe area");
                var title = NewRect(safe, "M03_ReviewBanner",
                    new Vector2(margin / (float)mode.width_dp, .88f),
                    new Vector2(1f - margin / (float)mode.width_dp, .98f));
                TextNode(title, "M03_BannerText",
                    "EDITOR KIT / DRAFT / NO OWNER ART", Vector2.zero,
                    Vector2.one, body, 17);
                float left = margin;
                float bottomBase = 55f;
                for (int i = 0; i < Semantics.Length; i++)
                {
                    int col = i % perRow;
                    int row = i / perRow;
                    float x0 = left + col * (cellWidth + gap);
                    float y0 = bottomBase + (rows - 1 - row) * (rowHeight + gap);
                    var rect = NewRect(safe, "M03_" + Semantics[i] + "_UNBOUND",
                        new Vector2(x0 / mode.width_dp,
                                    y0 / grid.Safe.height),
                        new Vector2((x0 + cellWidth) / mode.width_dp,
                                    (y0 + rowHeight) / grid.Safe.height));
                    DrawSemantic(rect, Semantics[i], mockState, surface,
                                 action, actionText, body, icon);
                }
                TextNode(safe, "M03_AlwaysVisibleRightsAndBindingGate",
                    "SOURCE MOCK / NO REAL PURCHASE, REWARD, CONSENT OR NAVIGATION",
                    new Vector2(.04f, .005f), new Vector2(.96f, .08f),
                    body, 14);
                foreach (var control in root.GetComponentsInChildren<Button>(true))
                    if (control.interactable ||
                        control.onClick.GetPersistentEventCount() != 0)
                        throw new InvalidOperationException("Unexpected live M03 control");
                return root;
            }
            catch
            {
                UnityEngine.Object.DestroyImmediate(root);
                throw;
            }
        }

        private void OnEnable()
        {
            try { catalog = LoadCatalog(); }
            catch (Exception ex) { status = "BLOCKED: " + ex.Message; }
        }

        private void DisposePreview()
        {
            if (preview != null) DestroyImmediate(preview);
            preview = null;
        }

        private void OnDisable() { DisposePreview(); }

        // Synthetic Editor diagram only. The native GameObject hierarchy
        // remains the authoritative source prototype; this is NOT a GameView
        // capture, font-fit proof, or physical device rendering.
        private void DrawSourceSchematic(string profileId, bool tablet)
        {
            var palette = VufScreenCatalog.LoadStyle(profileId).palettes;
            var surface = VufScreenCatalog.ParseColor(palette.surface, "surface");
            var accent = VufScreenCatalog.ParseColor(palette.cta, "cta");
            var ink = VufScreenCatalog.ParseColor(palette.text, "text");
            EditorGUILayout.Space();
            EditorGUILayout.LabelField(
                "Source-only semantic widget wireframe (NOT actual device render)",
                EditorStyles.boldLabel);
            var frame = GUILayoutUtility.GetRect(140f, tablet ? 200f : 310f,
                GUILayout.ExpandWidth(true));
            EditorGUI.DrawRect(frame, surface);
            int cols = tablet ? 4 : 2;
            int rows = (Semantics.Length + cols - 1) / cols;
            float padding = 12f;
            float gap = 7f;
            float w = (frame.width - padding * 2f - gap * (cols - 1)) / cols;
            float h = (frame.height - padding * 2f - gap * (rows - 1)) / rows;
            var labelStyle = new GUIStyle(EditorStyles.centeredGreyMiniLabel) {
                wordWrap = true, alignment = TextAnchor.MiddleCenter,
                normal = { textColor = ink }
            };
            for (int i = 0; i < Semantics.Length; i++)
            {
                var r = new Rect(
                    frame.x + padding + (i % cols) * (w + gap),
                    frame.y + padding + (i / cols) * (h + gap), w, h);
                EditorGUI.DrawRect(r, i == 0 ? accent :
                    new Color(surface.r, surface.g, surface.b, .75f));
                GUI.Label(r, Semantics[i].Replace('_', ' '), labelStyle);
            }
            EditorGUILayout.LabelField(
                "Draft only: rights/owner art/real buttons/Engine actions NOT approved.",
                EditorStyles.wordWrappedMiniLabel);
        }

        private void OnGUI()
        {
            EditorGUILayout.LabelField(
                "M03 | Five-game source semantic uGUI component kit",
                EditorStyles.boldLabel);
            EditorGUILayout.HelpBox(
                "Ten actual native Unity component prototypes. Source review only: " +
                "neither original licensed art nor game bindings. The five game " +
                "profiles reuse one semantic role set; no prefab/scene is written.",
                MessageType.Warning);
            if (catalog == null)
            {
                EditorGUILayout.HelpBox(status, MessageType.Error);
                if (GUILayout.Button("Re-read M02 source catalog"))
                    OnEnable();
                return;
            }
            profileIndex = EditorGUILayout.Popup("Draft game", profileIndex, Profiles);
            deviceIndex = EditorGUILayout.Popup(
                "Source portrait layout", deviceIndex,
                Array.ConvertAll(catalog.common.screen_modes, m => m.id));
            stateIndex = EditorGUILayout.Popup(
                "Mock state", stateIndex, VufReviewStateCatalog.States);
            EditorGUILayout.BeginHorizontal();
            if (GUILayout.Button("Build TEMP native uGUI kit"))
            {
                DisposePreview();
                try
                {
                    preview = BuildCandidate(catalog, Profiles[profileIndex],
                        deviceIndex, VufReviewStateCatalog.States[stateIndex]);
                    status = "Created in-memory native Canvas + 10 semantic " +
                        "controls. No asset saved. No Button is interactive.";
                }
                catch (Exception ex) { status = "BLOCKED: " + ex.Message; }
            }
            if (GUILayout.Button("Destroy my TEMP kit only"))
            {
                DisposePreview();
                status = "Temporary kit disposed.";
            }
            EditorGUILayout.EndHorizontal();
            EditorGUILayout.HelpBox(status, MessageType.Info);
            scroll = EditorGUILayout.BeginScrollView(scroll);
            var profile = catalog.profiles[profileIndex];
            EditorGUILayout.LabelField(
                profile.bible_title + " | " + profile.surface_material,
                EditorStyles.boldLabel);
            DrawSourceSchematic(Profiles[profileIndex],
                catalog.common.screen_modes[deviceIndex].id == "portrait_tablet");
            foreach (var key in Semantics)
                EditorGUILayout.LabelField(
                    key + "   •   EDITABLE uGUI CANDIDATE / NO ENGINE ACTION");
            EditorGUILayout.LabelField(
                "M02 source min touch", catalog.common.min_touch_dp + " dp");
            EditorGUILayout.LabelField(
                "Real Unity GUI/device/owner art/rights", "NOT RUN / NOT APPROVED");
            if (preview != null)
            {
                EditorGUILayout.LabelField(
                    "TEMP RectTransforms",
                    preview.GetComponentsInChildren<RectTransform>(true).Length.ToString());
                EditorGUILayout.LabelField(
                    "TEMP disabled native Buttons",
                    preview.GetComponentsInChildren<Button>(true).Length.ToString());
            }
            EditorGUILayout.EndScrollView();
        }
    }
}
