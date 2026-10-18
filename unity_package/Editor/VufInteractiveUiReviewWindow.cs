// VUF-M08-001/002 | Temporary REAL uGUI screen/state/localization inspector.
// INTERNAL_REUSE ONLY: 28 exact Coral schema IDs, five draft Style Bibles,
// original 28-screen VufScreenShellBuilderWindow.BuildCandidateHierarchy,
// VufReviewStateCatalog, VufResponsiveGeometry, VufSafeAreaFitter and
// VufUiTween. No new composition system and no existing asset/prefab writes.
// Only Editor TEST TAP logs. NEVER an Engine action, revenue or game binding.
using System;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.UI;

namespace Match3.VisualFactory.Editor
{
    public sealed class VufInteractiveUiReviewWindow : EditorWindow
    {
        private VufScreenCatalog.ScreenInfo[] screens;
        private readonly List<string> audit = new List<string>();
        private readonly List<string> taps = new List<string>();
        private GameObject disposable;
        private Button manualButton;
        private int themeIndex, screenIndex = 26, stateIndex, localeIndex, deviceIndex;
        private bool reducedMotionPreview = true;
        private string message = "Not loaded. Choose a screen and build a disposable preview.";
        private Vector2 scroll;
        private static readonly string[] Profiles = {
            "Coral_Rescue", "Garage_Legends", "Dino_Islands",
            "The_Fractured_Realms", "Wonder_Pop"
        };

        [MenuItem("Tools/MATCH3/Interactive UI Layout & State Review")]
        public static void Open()
        {
            var w = GetWindow<VufInteractiveUiReviewWindow>("VUF UI Inspector");
            w.minSize = new Vector2(670, 680);
            w.Show();
        }

        private void OnEnable()
        {
            try { screens = VufScreenCatalog.LoadScreens(); }
            catch (Exception error)
            { screens = null; message = "BLOCKED: " + error.Message; }
        }

        private void OnDisable() { ClearOnlyOwnedPreview(); }

        private void ClearOnlyOwnedPreview()
        {
            if (disposable != null)
                DestroyImmediate(disposable);
            disposable = null;
            manualButton = null;
            taps.Clear();
            audit.Clear();
        }

        private static void ProtectTree(GameObject root)
        {
            foreach (Transform item in root.GetComponentsInChildren<Transform>(true))
                item.gameObject.hideFlags =
                    HideFlags.DontSaveInEditor | HideFlags.DontSaveInBuild;
        }

        // Synthetic/editor-only callback. A test button is never connected to
        // an Engine/gameplay/reward/save/purchase event, even in Play mode.
        private void OnPreviewTap()
        {
            if (disposable == null || manualButton == null) return;
            var marker = disposable.GetComponent<VufCandidateScreenMarker>();
            if (marker == null ||
                marker.CandidateStatus != "CANDIDATE_NOT_APPROVED" ||
                marker.FeatureGate != "REQUIRES_ENGINE_OR_GAME_BINDING" ||
                !manualButton.interactable)
                throw new InvalidOperationException("locked or noncandidate tap refused");
            string note = "EDITOR_ONLY_TAP / " + marker.ProfileId +
                " / " + marker.ScreenId + " / " +
                VufReviewStateCatalog.States[stateIndex] +
                " / ACTION_NOT_BOUND_TO_ENGINE";
            taps.Add(note);
            if (taps.Count > 40) taps.RemoveAt(0);
        }

        // Source builder leaves ALL gameplay buttons disabled by design.
        // Only a disposable in-memory Editor clone may get this test listener.
        internal static bool EnableOnlyPreviewButton(GameObject candidate,
            Button button, Action onTap)
        {
            if (candidate == null || button == null || onTap == null ||
                !button.transform.IsChildOf(candidate.transform))
                throw new ArgumentException("preview button must belong to a candidate");
            var marker = candidate.GetComponent<VufCandidateScreenMarker>();
            if (marker == null ||
                marker.CandidateStatus != "CANDIDATE_NOT_APPROVED" ||
                marker.FeatureGate != "REQUIRES_ENGINE_OR_GAME_BINDING" ||
                button.onClick.GetPersistentEventCount() != 0)
                return false;
            if ((candidate.hideFlags & HideFlags.DontSaveInEditor) == 0 ||
                (candidate.hideFlags & HideFlags.DontSaveInBuild) == 0)
                throw new InvalidOperationException("persistent source must never be bound");
            button.interactable = true;
            button.onClick.AddListener(() => onTap());
            return true;
        }

        private void BuildAllForSelectedScreen()
        {
            ClearOnlyOwnedPreview();
            if (screens == null) { message = "Missing 28-screen catalog"; return; }
            GameObject temporary = null;
            try
            {
                VufScreenCatalog.ScreenInfo screen = screens[screenIndex];
                var palette = VufScreenCatalog.LoadStyle(Profiles[themeIndex]);
                temporary = VufScreenShellBuilderWindow.BuildCandidateHierarchy(
                    screen, palette, true);
                // Apply localized review copy BEFORE binding any test button.
                VufReviewStateCatalog.Apply(
                    temporary, screen, VufReviewStateCatalog.States[stateIndex],
                    VufReviewStateCatalog.Locales[localeIndex]);
                ProtectTree(temporary);
                var shield = temporary.transform.Find(
                    "SafeArea_ReviewOnly/VUF_28ScreenInputShield");
                if (shield == null)
                    throw new InvalidOperationException("original input shield missing");
                // Original nonpersistent input shield blocks unbound buttons;
                // in test-only disposable mode it may be bypassed.
                var graphic = shield.GetComponent<Graphic>();
                if (graphic == null)
                    throw new InvalidOperationException("missing source shield graphic");
                var buttons = temporary.GetComponentsInChildren<Button>(true);
                if (buttons.Length != 1)
                    throw new InvalidOperationException(
                        "expected exactly one disabled candidate test button");
                bool enabled = EnableOnlyPreviewButton(
                    temporary, buttons[0], OnPreviewTap);
                if (enabled)
                {
                    graphic.raycastTarget = false;
                    manualButton = buttons[0];
                }
                temporary.name = "VUF_TEMP_UI_NO_SAVE_" + screen.id;
                disposable = temporary;
                // Actual Unity uGUI component, not imported screenshot or UXML.
                var inspection = VufResponsiveGeometry.Analyze(disposable,
                    VufResponsiveGeometry.Presets[deviceIndex]);
                audit.Add("REAL Canvas=" +
                    disposable.GetComponentsInChildren<Canvas>(true).Length +
                    " | Buttons=" + buttons.Length +
                    " | safe-fit=" +
                    disposable.GetComponentsInChildren<VufSafeAreaFitter>(true).Length);
                audit.Add("Theme=" + palette.id + " Screen=" + screen.id +
                    " | " + screen.key + " | state/locale are MOCK only");
                audit.Add("Simulated screen: " + inspection.Device.Name +
                    " | rectangles=" + inspection.Nodes.Count +
                    " | warnings=" + inspection.Warnings.Count);
                foreach (var finding in inspection.Warnings)
                    audit.Add(finding);
                foreach (var node in inspection.Nodes)
                {
                    if (node.IsButton)
                        audit.Add("TOUCH RECT: " + node.Path +
                            " W=" + node.Bounds.width.ToString("F1") +
                            " H=" + node.Bounds.height.ToString("F1") +
                            " (simulated px, not device evidence)");
                }
                foreach (RectTransform rect in
                    disposable.GetComponentsInChildren<RectTransform>(true))
                {
                    if (rect == null || rect == disposable.transform) continue;
                    if (rect.GetComponent<Button>() == null &&
                        rect.GetComponent<VufSafeAreaFitter>() == null &&
                        rect.GetComponent<CanvasGroup>() == null) continue;
                    audit.Add("Z/ANCHOR: " + rect.name +
                        " sibling=" + rect.GetSiblingIndex() +
                        " min=(" + rect.anchorMin.x.ToString("F2") +
                        "," + rect.anchorMin.y.ToString("F2") + ")" +
                        " max=(" + rect.anchorMax.x.ToString("F2") +
                        "," + rect.anchorMax.y.ToString("F2") + ")" +
                        " raycast=" + (rect.GetComponent<Graphic>() != null ?
                            rect.GetComponent<Graphic>().raycastTarget.ToString() :
                            "no Graphic"));
                }
                var cg = disposable.GetComponentInChildren<CanvasGroup>(true);
                audit.Add("Tween/transition: " + (cg == null ?
                    "no CanvasGroup on this page" :
                    "real CanvasGroup, VufUiTween; no Engine state"));
                message = enabled ?
                    "Nonpersistent Editor test button enabled. SIMULATE TAP " +
                    "only writes local log, NOT navigation or gameplay." :
                    "POLICY-OFF: all action buttons remain disabled.";
                Selection.activeGameObject = disposable;
            }
            catch (Exception error)
            {
                if (temporary != null) DestroyImmediate(temporary);
                disposable = null; manualButton = null;
                message = "BLOCKED: " + error.Message;
            }
        }

        private void OnGUI()
        {
            EditorGUILayout.LabelField("M08 | Interactive uGUI candidate QA",
                EditorStyles.boldLabel);
            EditorGUILayout.HelpBox(
                "Reuses existing 28 Coral draft screens for each draft visual " +
                "style; other games do NOT have 28 approved screen contracts. " +
                "Actual uGUI components and touch geometry, but NO real Engine " +
                "bindings, owner art, localized shipped text or real safe-area device.",
                MessageType.Warning);
            if (screens == null)
            {
                EditorGUILayout.HelpBox(message, MessageType.Error);
                return;
            }
            themeIndex = EditorGUILayout.Popup("Draft theme", themeIndex, Profiles);
            string[] labels = new string[screens.Length];
            for (int i = 0; i < screens.Length; i++)
                labels[i] = screens[i].id + " / " + screens[i].key;
            screenIndex = EditorGUILayout.Popup("Draft Coral screen contract",
                screenIndex, labels);
            stateIndex = EditorGUILayout.Popup("MOCK state",
                stateIndex, VufReviewStateCatalog.States);
            localeIndex = EditorGUILayout.Popup("MOCK locale",
                localeIndex, VufReviewStateCatalog.Locales);
            var deviceLabels = new string[VufResponsiveGeometry.Presets.Length];
            for (int i = 0; i < deviceLabels.Length; i++)
                deviceLabels[i] = VufResponsiveGeometry.Presets[i].Name;
            deviceIndex = EditorGUILayout.Popup("Synthetic safe-area preset",
                deviceIndex, deviceLabels);
            EditorGUILayout.BeginHorizontal();
            if (GUILayout.Button("Create NEW temporary uGUI screen"))
                BuildAllForSelectedScreen();
            if (GUILayout.Button("Destroy only my TEMP screen"))
            {
                ClearOnlyOwnedPreview();
                message = "Temporary preview disposed. No scene file saved.";
            }
            EditorGUILayout.EndHorizontal();
            EditorGUILayout.HelpBox(message, MessageType.Info);
            using (new EditorGUI.DisabledScope(manualButton == null))
                if (GUILayout.Button("SIMULATE TEST TAP (local log ONLY)"))
                {
                    manualButton.onClick.Invoke();
                    message = "VIEW ACTION ONLY: local log updated.";
                }
            reducedMotionPreview = EditorGUILayout.Toggle(
                "Reduced-motion MOCK transition", reducedMotionPreview);
            using (new EditorGUI.DisabledScope(disposable == null))
            {
                if (GUILayout.Button("Test candidate CanvasGroup transition (view only)"))
                {
                    var tween = disposable.GetComponentInChildren<VufUiTween>(true);
                    if (tween != null)
                    {
                        tween.SetReducedMotion(reducedMotionPreview);
                        tween.Hide();
                        tween.Advance(.5f);
                        tween.Show();
                        tween.Advance(.5f);
                        var cg = tween.GetComponent<CanvasGroup>();
                        message = "Pure preview tween / CanvasGroup alpha=" +
                            cg.alpha.ToString("F2") +
                            " / no Engine event dispatched.";
                    }
                    else
                        message = "No modal transition on this screen. " +
                            "Choose modal/overlay/ceremony page.";
                }
            }
            EditorGUILayout.LabelField("Bound real Engine actions", "ZERO");
            EditorGUILayout.LabelField("Persistent scene/prefab writes", "ZERO");
            scroll = EditorGUILayout.BeginScrollView(scroll);
            foreach (string result in audit)
                EditorGUILayout.SelectableLabel(result,
                    EditorStyles.wordWrappedLabel, GUILayout.MinHeight(26));
            foreach (string tap in taps)
                EditorGUILayout.SelectableLabel(tap,
                    EditorStyles.wordWrappedLabel, GUILayout.MinHeight(26));
            EditorGUILayout.EndScrollView();
            EditorGUILayout.HelpBox(
                "M08 real game action bindings, native iPhone safe area, GUI touch " +
                "testing, localization validation, final UI Toolkit decision, " +
                "owner art rights and release are OPEN.",
                MessageType.Warning);
        }
    }
}
