// VF-09 evidence triage for the five-game Visual Factory.
// Input data is advisory and never establishes release/owner acceptance.
using System;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;

namespace Match3.VisualFactory.Editor
{
    public sealed class VufReadinessBoardWindow : EditorWindow
    {
        internal sealed class Summary
        {
            internal readonly List<string> RequiredGates = new List<string>();
            internal readonly List<string> Findings = new List<string>();
            internal int SpriteCount;
            internal int PixelWarnings;
            internal int LocaleCoveredEnglish;
            internal int LocaleCoveredTurkish;
            internal int GeometryWarnings;
            internal int TypographyOverflowRisks;
            internal int TypographyContrastRisks;
            internal string CandidateProfile = "NO CANDIDATE";
            internal bool ProductionApproved => false;
        }

        private GameObject prefab;
        private TextAsset spriteReport;
        private TextAsset localeReport;
        private Summary current;
        private string error;
        private Vector2 scroll;

        [MenuItem("Tools/MATCH3/Review Evidence Board")]
        public static void Open()
        {
            var window = GetWindow<VufReadinessBoardWindow>("VUF Evidence");
            window.minSize = new Vector2(650f, 560f);
            window.Show();
        }

        private void OnGUI()
        {
            EditorGUILayout.LabelField("VF-09 | Cross-Module Review Evidence Board",
                EditorStyles.boldLabel);
            EditorGUILayout.HelpBox(
                "This board always reports production acceptance as OPEN. " +
                "It combines optional candidate, external pixel-health report " +
                "and draft locale coverage metadata without writing any assets. " +
                "Actual Unity GUI, licensed source art, real devices and owner " +
                "creative review are mandatory separate gates.",
                MessageType.Warning);
            prefab = (GameObject)EditorGUILayout.ObjectField(
                "Unapproved candidate", prefab, typeof(GameObject), false);
            spriteReport = (TextAsset)EditorGUILayout.ObjectField(
                "Pixel QA JSON TextAsset", spriteReport, typeof(TextAsset), false);
            localeReport = (TextAsset)EditorGUILayout.ObjectField(
                "Locale QA JSON TextAsset", localeReport, typeof(TextAsset), false);
            if (GUILayout.Button("Evaluate independent review evidence (read-only)",
                GUILayout.Height(34f)))
            {
                current = null;
                error = null;
                try
                {
                    current = Evaluate(prefab,
                        spriteReport != null ? spriteReport.text : null,
                        localeReport != null ? localeReport.text : null);
                }
                catch (Exception exception)
                {
                    error = "Evidence rejected: " + exception.Message;
                }
            }
            if (!String.IsNullOrEmpty(error))
                EditorGUILayout.HelpBox(error, MessageType.Error);
            if (current == null) return;
            EditorGUILayout.LabelField("Production acceptance", "OPEN / NOT APPROVED");
            EditorGUILayout.LabelField("Candidate profile", current.CandidateProfile);
            EditorGUILayout.LabelField("Sprite report sources", current.SpriteCount.ToString());
            EditorGUILayout.LabelField("Pixel warning count", current.PixelWarnings.ToString());
            EditorGUILayout.LabelField("Draft EN headings", current.LocaleCoveredEnglish.ToString());
            EditorGUILayout.LabelField("Draft TR headings", current.LocaleCoveredTurkish.ToString());
            EditorGUILayout.LabelField("Synthetic viewport warnings",
                current.GeometryWarnings.ToString());
            EditorGUILayout.LabelField("Text overflow risks",
                current.TypographyOverflowRisks.ToString());
            EditorGUILayout.LabelField("Text contrast risks",
                current.TypographyContrastRisks.ToString());
            scroll = EditorGUILayout.BeginScrollView(scroll);
            EditorGUILayout.LabelField("Mandatory remaining evidence",
                EditorStyles.boldLabel);
            foreach (string item in current.RequiredGates)
                EditorGUILayout.HelpBox(item, MessageType.Warning);
            EditorGUILayout.LabelField("Read-only findings", EditorStyles.boldLabel);
            foreach (string item in current.Findings)
                EditorGUILayout.HelpBox(item, MessageType.Info);
            EditorGUILayout.EndScrollView();
        }

        internal static Summary Evaluate(GameObject candidate,
            string spriteJson, string localeJson)
        {
            var summary = new Summary();
            summary.RequiredGates.Add("ORIGINAL_ART_RIGHTS: actual source/usage review OPEN");
            summary.RequiredGates.Add("OWNER_VISUAL_APPROVAL: real screen design OPEN");
            summary.RequiredGates.Add("LIVE_UNITY_GUI: actual interaction/render OPEN");
            summary.RequiredGates.Add("PHYSICAL_DEVICE: iOS and Android OPEN");
            summary.RequiredGates.Add("ENGINE_LFX: independent downstream integration OPEN");

            if (!String.IsNullOrEmpty(spriteJson))
            {
                var qa = VufSpriteQaReportWindow.ParseReport(spriteJson);
                summary.SpriteCount = qa.file_count;
                summary.PixelWarnings = qa.warning_count;
                summary.Findings.Add("VF-09 pixel-health report VALID DRAFT, not rights proof");
            }
            else
                summary.RequiredGates.Add("PIXEL_REPORT: no source-health JSON supplied");

            if (!String.IsNullOrEmpty(localeJson))
            {
                var locale = VufLocaleCoverageWindow.Parse(localeJson);
                summary.LocaleCoveredEnglish = locale.locales[0].covered;
                summary.LocaleCoveredTurkish = locale.locales[1].covered;
                summary.Findings.Add("VF-07 EN/TR coverage accepted as DRAFT, never shipping");
                if (summary.LocaleCoveredEnglish < 28 || summary.LocaleCoveredTurkish < 28)
                    summary.RequiredGates.Add("LOCALIZATION: incomplete EN/TR headings");
            }
            else
                summary.RequiredGates.Add("LOCALIZATION: no draft coverage report supplied");

            if (candidate == null)
            {
                summary.RequiredGates.Add("PREFAB_AUDIT: no source candidate supplied");
                return summary;
            }
            var marker = candidate.GetComponent<VufCandidateScreenMarker>();
            if (marker == null ||
                marker.CandidateStatus != "CANDIDATE_NOT_APPROVED")
                throw new InvalidOperationException("candidate-only marker is missing or modified");
            summary.CandidateProfile = marker.ProfileId;
            if (!String.IsNullOrEmpty(localeJson) && marker.ProfileId != "Coral_Rescue")
                throw new InvalidOperationException("Coral locale report applied to different game");

            for (int i = 0; i < VufResponsiveGeometry.Presets.Length; ++i)
            {
                var device = VufResponsiveGeometry.Presets[i];
                var geometry = VufResponsiveGeometry.Analyze(candidate, device);
                summary.GeometryWarnings += geometry.Warnings.Count;
                var typography = VufTypographyAudit.Analyze(candidate, device);
                summary.TypographyOverflowRisks += typography.OverflowCount;
                summary.TypographyContrastRisks += typography.LowContrastCount;
                if (typography.UnmeasuredCount != 0)
                    summary.RequiredGates.Add(
                        "TEXT_METRICS_UNKNOWN: " + device.Name + " " +
                        typography.UnmeasuredCount + " items");
            }
            summary.Findings.Add("VF-08: five synthetic layouts reviewed, not phone screenshots");
            if (summary.GeometryWarnings != 0 ||
                summary.TypographyOverflowRisks != 0 ||
                summary.TypographyContrastRisks != 0)
                summary.RequiredGates.Add("UI_LAYOUT_AND_COPY: static warnings require inspection");
            return summary;
        }
    }
}
