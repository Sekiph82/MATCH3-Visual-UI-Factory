// VF-08: manual wireframe-only preview of authored RectTransform geometry.
// No native Unity render, dynamic text layout or physical device simulation.
using System;
using UnityEditor;
using UnityEngine;

namespace Match3.VisualFactory.Editor
{
    public sealed class VufResponsivePreviewWindow : EditorWindow
    {
        private GameObject prefab;
        private int deviceIndex;
        private bool showLabels = true;
        private bool showButtons = true;
        private bool showOtherRects;
        private Vector2 warningsScroll;
        private VufResponsiveGeometry.Audit report;
        private string error;

        [MenuItem("Tools/MATCH3/Responsive Layout Wireframe")]
        public static void Open()
        {
            var window = GetWindow<VufResponsivePreviewWindow>("VF-08 Layout Wireframe");
            window.minSize = new Vector2(670f, 590f);
            window.Show();
        }

        private void OnGUI()
        {
            EditorGUILayout.LabelField("VF-08 | Device Ratio & Safe-Area WIREFRAME",
                EditorStyles.boldLabel);
            EditorGUILayout.HelpBox(
                "This is an approximate RectTransform anchor/offset and touch-target " +
                "diagnostic. It does NOT render Unity UI, actual fonts, shader effects, " +
                "localized layout groups, physical notch measurements or phone pixels. " +
                "Rendered previews, real device tests and owner visual acceptance " +
                "remain NOT RUN.",
                MessageType.Warning);
            EditorGUI.BeginChangeCheck();
            prefab = (GameObject)EditorGUILayout.ObjectField(
                "Candidate prefab / GameObject", prefab, typeof(GameObject), true);
            string[] names = new string[VufResponsiveGeometry.Presets.Length];
            for (int i = 0; i < names.Length; ++i)
                names[i] = VufResponsiveGeometry.Presets[i].Name;
            deviceIndex = EditorGUILayout.Popup("Synthetic device preset", deviceIndex, names);
            showLabels = EditorGUILayout.Toggle("Draw text bounds", showLabels);
            showButtons = EditorGUILayout.Toggle("Draw clickable region bounds", showButtons);
            showOtherRects = EditorGUILayout.Toggle("Show other UI rectangles", showOtherRects);
            if (EditorGUI.EndChangeCheck())
                AuditSelection();
            using (new EditorGUI.DisabledScope(prefab == null))
            {
                if (GUILayout.Button("Audit candidate (read-only)", GUILayout.Height(28f)))
                    AuditSelection();
            }
            if (!String.IsNullOrEmpty(error))
                EditorGUILayout.HelpBox("Cannot audit: " + error, MessageType.Error);
            if (prefab != null && report != null)
            {
                EditorGUILayout.LabelField(
                    "Candidate-only marker", report.CandidateOnly ? "YES" : "BLOCKED");
                EditorGUILayout.LabelField("Buttons (NOT gameplay bindings)",
                    report.ButtonCount.ToString());
                EditorGUILayout.LabelField("Geometry warnings", report.Warnings.Count.ToString());
                GUILayout.Space(5f);
                var space = GUILayoutUtility.GetRect(250f, 440f, 120f, 440f,
                    GUILayout.ExpandWidth(true), GUILayout.ExpandHeight(true));
                RenderWireframe(space);
                GUILayout.Space(5f);
                EditorGUILayout.LabelField("Diagnostics (no automatic approval)",
                    EditorStyles.boldLabel);
                warningsScroll = EditorGUILayout.BeginScrollView(
                    warningsScroll, GUILayout.Height(110f));
                if (report.Warnings.Count == 0)
                    EditorGUILayout.LabelField("No static warnings; real Unity/device QA still required.");
                foreach (string warning in report.Warnings)
                    EditorGUILayout.SelectableLabel(warning, EditorStyles.wordWrappedLabel,
                        GUILayout.MinHeight(26f));
                EditorGUILayout.EndScrollView();
            }
        }

        private void AuditSelection()
        {
            report = null;
            error = null;
            if (prefab == null) return;
            try
            {
                report = VufResponsiveGeometry.Analyze(prefab,
                    VufResponsiveGeometry.Presets[deviceIndex]);
            }
            catch (Exception exception)
            {
                error = exception.Message;
            }
        }

        private void RenderWireframe(Rect area)
        {
            VufResponsiveGeometry.Device device = report.Device;
            float factor = Mathf.Min((area.width - 16f) / device.Width,
                                      (area.height - 16f) / device.Height);
            float width = device.Width * factor;
            float height = device.Height * factor;
            Rect frame = new Rect(area.center.x - width * .5f,
                area.center.y - height * .5f, width, height);
            EditorGUI.DrawRect(frame, new Color(.075f, .115f, .18f));
            GUI.Box(frame, GUIContent.none);

            Rect safe = device.SafeRect;
            Rect safeDraw = Convert(safe, frame, device);
            EditorGUI.DrawRect(safeDraw, new Color(.11f, .22f, .22f, .30f));
            DrawEdges(safeDraw, new Color(.20f, .90f, .70f));
            foreach (VufResponsiveGeometry.Node node in report.Nodes)
            {
                if (node.IsSafeArea) continue;
                if (node.IsButton && !showButtons) continue;
                if (node.IsText && !showLabels) continue;
                if (!node.IsButton && !node.IsText && !showOtherRects) continue;
                Rect projected = Convert(node.Bounds, frame, device);
                if (projected.width < 1f || projected.height < 1f) continue;
                Color color = node.IsButton
                    ? new Color(.95f, .67f, .22f, .78f)
                    : node.IsText ? new Color(.52f, .76f, 1f, .72f)
                    : new Color(.71f, .55f, .95f, .40f);
                DrawEdges(projected, color);
                if (node.IsButton && projected.width > 55f && projected.height > 10f)
                {
                    GUI.Label(new Rect(projected.x + 2f, projected.y + 2f,
                        projected.width - 4f, 14f), "DISABLED CANDIDATE", EditorStyles.miniLabel);
                }
            }
            GUI.Label(new Rect(frame.x + 4f, frame.y + 4f,
                Mathf.Max(50f, frame.width - 8f), 24f),
                device.Name, EditorStyles.miniLabel);
        }

        private static Rect Convert(Rect source, Rect frame,
            VufResponsiveGeometry.Device device)
        {
            return new Rect(
                frame.x + source.xMin / device.Width * frame.width,
                frame.y + (device.Height - source.yMax) / device.Height * frame.height,
                source.width / device.Width * frame.width,
                source.height / device.Height * frame.height);
        }

        private static void DrawEdges(Rect rect, Color color)
        {
            const float stroke = 1f;
            EditorGUI.DrawRect(new Rect(rect.x, rect.y, rect.width, stroke), color);
            EditorGUI.DrawRect(new Rect(rect.x, rect.yMax - stroke, rect.width, stroke), color);
            EditorGUI.DrawRect(new Rect(rect.x, rect.y, stroke, rect.height), color);
            EditorGUI.DrawRect(new Rect(rect.xMax - stroke, rect.y, stroke, rect.height), color);
        }
    }
}
