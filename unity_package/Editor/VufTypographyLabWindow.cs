using System;
using UnityEditor;
using UnityEngine;

namespace Match3.VisualFactory.Editor
{
    // Source-only text metrics: never saves, publishes or approves a prefab.
    public sealed class VufTypographyLabWindow : EditorWindow
    {
        private GameObject candidate;
        private int preset;
        private VufTypographyAudit.Report report;
        private string error;
        private Vector2 scroll;

        [MenuItem("Tools/MATCH3/Typography and Contrast Lab")]
        public static void Open()
        {
            var window = GetWindow<VufTypographyLabWindow>("VUF Text QA");
            window.minSize = new Vector2(630f, 500f);
            window.Show();
        }

        private void OnGUI()
        {
            EditorGUILayout.LabelField("VF-08 | Draft Typography & Contrast",
                EditorStyles.boldLabel);
            EditorGUILayout.HelpBox(
                "Read-only TextGenerator estimates on synthetic device ratios. " +
                "Not a rendered screenshot, localization, real phone or art acceptance.",
                MessageType.Warning);
            EditorGUI.BeginChangeCheck();
            candidate = (GameObject)EditorGUILayout.ObjectField(
                "Unapproved candidate", candidate, typeof(GameObject), true);
            string[] names = new string[VufResponsiveGeometry.Presets.Length];
            for (int i = 0; i < names.Length; ++i)
                names[i] = VufResponsiveGeometry.Presets[i].Name;
            preset = EditorGUILayout.Popup("Synthetic device", preset, names);
            if (EditorGUI.EndChangeCheck()) Inspect();
            using (new EditorGUI.DisabledScope(candidate == null))
                if (GUILayout.Button("Inspect candidate read-only"))
                    Inspect();
            if (!String.IsNullOrEmpty(error))
                EditorGUILayout.HelpBox(error, MessageType.Error);
            if (report == null) return;
            EditorGUILayout.LabelField("Text nodes", report.Items.Count.ToString());
            EditorGUILayout.LabelField("Overflow risks", report.OverflowCount.ToString());
            EditorGUILayout.LabelField("Low-contrast hints",
                report.LowContrastCount.ToString());
            EditorGUILayout.LabelField("Unknown text metrics",
                report.UnmeasuredCount.ToString());
            scroll = EditorGUILayout.BeginScrollView(scroll);
            foreach (string warning in report.Warnings)
                EditorGUILayout.HelpBox(warning, MessageType.Warning);
            foreach (VufTypographyAudit.Finding item in report.Items)
            {
                EditorGUILayout.BeginVertical("box");
                EditorGUILayout.LabelField(item.Path, EditorStyles.boldLabel);
                EditorGUILayout.LabelField("Draft text: " + item.Copy,
                    EditorStyles.wordWrappedLabel);
                EditorGUILayout.LabelField("Bounds: " +
                    item.BoundsWidth.ToString("F1") + "x" +
                    item.BoundsHeight.ToString("F1"));
                EditorGUILayout.LabelField("Text preferred height: " +
                    (item.MeasurementAvailable ?
                        item.PreferredHeight.ToString("F1") : "UNKNOWN"));
                EditorGUILayout.LabelField("Approx contrast: " +
                    (item.BackgroundKnown ?
                        item.ContrastRatio.ToString("F2") + ":1" : "UNKNOWN"));
                EditorGUILayout.EndVertical();
            }
            EditorGUILayout.EndScrollView();
            EditorGUILayout.HelpBox(
                "Human GUI, actual fonts, localization, performance, rights " +
                "and mobile device reviews remain required.", MessageType.Info);
        }

        private void Inspect()
        {
            report = null;
            error = null;
            if (candidate == null) return;
            try
            {
                report = VufTypographyAudit.Analyze(candidate,
                    VufResponsiveGeometry.Presets[preset]);
            }
            catch (Exception e)
            {
                error = e.Message;
            }
        }
    }
}
