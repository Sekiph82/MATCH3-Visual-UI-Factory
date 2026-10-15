// VF-02: read-only portfolio view of manually imported offline catalog reports.
// Buttons never approve artwork, call paid providers, publish or mutate games.
using System;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;

namespace Match3.VisualFactory.Editor
{
    public sealed class VufProductionQueueWindow : EditorWindow
    {
        [Serializable]
        internal sealed class Pending
        {
            public int id;
            public string asset_key;
            public int revision;
            public string sha256;
        }

        [Serializable]
        internal sealed class Profile
        {
            public string profile_id;
            public int revision_count;
            public int pending_review_count;
            public int approval_receipts_count;
            public int active_asset_count;
            public int rollback_events_count;
            public Pending[] pending_preview;
        }

        [Serializable]
        internal sealed class Portfolio
        {
            public int schema_version;
            public string stage;
            public string generated_utc;
            public bool source_integrity_verified;
            public int total_verified_revisions;
            public Profile[] profiles;
        }

        private TextAsset importedReport;
        private Portfolio view;
        private string error;
        private int selectedProfile;
        private Vector2 scroll;

        [MenuItem("Tools/MATCH3/Visual Production Queue")]
        public static void Open()
        {
            var window = GetWindow<VufProductionQueueWindow>("VUF Production Queue");
            window.minSize = new Vector2(570f, 520f);
            window.Show();
        }

        private void OnGUI()
        {
            EditorGUILayout.LabelField("VF-02 | Five-Game Production Queue", EditorStyles.boldLabel);
            EditorGUILayout.HelpBox(
                "Load an explicitly exported, external, read-only portfolio-report from " +
                "the offline SHA-256 catalog. Counts/receipts are NOT authenticated " +
                "owner signatures. This window cannot approve, delete, publish, " +
                "call AI providers, change Unity prefabs or replace existing assets.",
                MessageType.Info);
            EditorGUI.BeginChangeCheck();
            importedReport = (TextAsset)EditorGUILayout.ObjectField(
                "Imported portfolio JSON", importedReport, typeof(TextAsset), false);
            if (EditorGUI.EndChangeCheck())
                Parse();
            if (GUILayout.Button("Re-read and validate imported report"))
                Parse();
            if (error != null)
            {
                EditorGUILayout.HelpBox(error, MessageType.Error);
                return;
            }
            if (view == null)
            {
                EditorGUILayout.HelpBox(
                    "First run catalog.py --store <EXTERNAL_STORE> portfolio-report " +
                    "and save stdout into a JSON file outside GitHub. Import a COPY " +
                    "into the Unity authoring project for read-only inspection.",
                    MessageType.None);
                return;
            }

            EditorGUILayout.LabelField("Snapshot", view.generated_utc);
            EditorGUILayout.LabelField("Stored source revisions", view.total_verified_revisions.ToString());
            EditorGUILayout.HelpBox(
                "READ-ONLY SNAPSHOT, NOT LIVE APPROVAL. No production publish authority.",
                MessageType.Warning);
            string[] labels = new string[view.profiles.Length];
            for (int i = 0; i < labels.Length; i++)
                labels[i] = view.profiles[i].profile_id;
            selectedProfile = EditorGUILayout.Popup("Game", selectedProfile, labels);

            Profile profile = view.profiles[selectedProfile];
            EditorGUILayout.BeginVertical("box");
            EditorGUILayout.LabelField("Candidate review backlog", profile.pending_review_count.ToString());
            EditorGUILayout.LabelField("Stored approval receipts", profile.approval_receipts_count.ToString());
            EditorGUILayout.LabelField("Currently selected assets", profile.active_asset_count.ToString());
            EditorGUILayout.LabelField("Explicit rollback events", profile.rollback_events_count.ToString());
            EditorGUILayout.EndVertical();

            EditorGUILayout.LabelField("Candidate Review Queue (first 100, read-only)",
                EditorStyles.boldLabel);
            scroll = EditorGUILayout.BeginScrollView(scroll);
            foreach (Pending candidate in profile.pending_preview)
            {
                EditorGUILayout.BeginVertical("box");
                EditorGUILayout.LabelField(candidate.asset_key,
                    "Revision " + candidate.revision + " | ID " + candidate.id);
                EditorGUILayout.SelectableLabel(candidate.sha256, EditorStyles.miniLabel);
                EditorGUILayout.EndVertical();
            }
            EditorGUILayout.EndScrollView();
            EditorGUILayout.HelpBox(
                "Review every candidate's genuine original rights, per-title style, " +
                "resolution, alpha and actual Unity/device behavior before a human " +
                "may explicitly record the approval outside this dashboard.",
                MessageType.Warning);
        }

        private void Parse()
        {
            view = null;
            error = null;
            selectedProfile = 0;
            if (importedReport == null) return;
            try
            {
                view = ParsePortfolioReport(importedReport.text);
            }
            catch (Exception ex)
            {
                error = "Cannot display untrusted/incomplete portfolio JSON: " + ex.Message;
            }
        }

        // Pure validation shared by the read-only window and synthetic EditMode tests.
        // It parses an imported snapshot only; it has no catalog or approval side effects.
        internal static Portfolio ParsePortfolioReport(string reportJson)
        {
            Portfolio document = JsonUtility.FromJson<Portfolio>(reportJson);
            if (document == null || document.schema_version != 1 ||
                document.stage != "READ_ONLY_NOT_OWNER_APPROVAL" ||
                !document.source_integrity_verified ||
                document.profiles == null || document.profiles.Length != 5 ||
                document.total_verified_revisions < 0)
                throw new ArgumentException("invalid portfolio report schema/status");
            HashSet<string> allowed = new HashSet<string>(new[] {
                "Coral_Rescue", "Garage_Legends", "Dino_Islands",
                "The_Fractured_Realms", "Wonder_Pop"
            }, StringComparer.Ordinal);
            int total = 0;
            foreach (Profile profile in document.profiles)
            {
                if (profile == null || !allowed.Remove(profile.profile_id) ||
                    profile.revision_count < 0 || profile.pending_review_count < 0 ||
                    profile.approval_receipts_count < 0 || profile.active_asset_count < 0 ||
                    profile.rollback_events_count < 0 ||
                    profile.revision_count !=
                        profile.pending_review_count + profile.approval_receipts_count ||
                    profile.active_asset_count > profile.approval_receipts_count ||
                    profile.pending_preview == null || profile.pending_preview.Length > 100 ||
                    profile.pending_preview.Length > profile.pending_review_count)
                    throw new ArgumentException("invalid profile totals or duplicate game");
                HashSet<int> ids = new HashSet<int>();
                foreach (Pending item in profile.pending_preview)
                {
                    if (item == null || item.id < 1 || item.revision < 1 ||
                        String.IsNullOrEmpty(item.asset_key) ||
                        String.IsNullOrEmpty(item.sha256) || item.sha256.Length != 64 ||
                        !ids.Add(item.id))
                        throw new ArgumentException("invalid pending revision record");
                }
                total += profile.revision_count;
            }
            if (allowed.Count != 0 || total != document.total_verified_revisions)
                throw new ArgumentException("portfolio total/profiles mismatch");
            return document;
        }
    }
}
