// VF-07 / VF-08: read-only coverage inspector for external EN/TR draft QA.
// No translator, prefab mutator, gameplay binder or owner-approval button.
using System;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;

namespace Match3.VisualFactory.Editor
{
    public sealed class VufLocaleCoverageWindow : EditorWindow
    {
        [Serializable]
        internal sealed class LocaleStatus
        {
            public string locale;
            public int covered;
            public int total;
            public int coverage_basis_points;
            public string[] missing_keys;
            public string[] long_copy_review_keys;
        }

        [Serializable]
        internal sealed class Report
        {
            public int schema_version;
            public string stage;
            public string profile_id;
            public string report_type;
            public string source_manifest_sha256;
            public string source_contract_sha256;
            public LocaleStatus[] locales;
            public string[] shared_placeholder_checked_keys;
            public string[] policy_off_keys;
            public string[] warning_codes;
            public bool owner_translation_approved;
            public bool game_bindings_enabled;
        }

        private TextAsset draftReport;
        private Report result;
        private string error;
        private Vector2 scroll;

        [MenuItem("Tools/MATCH3/Localization Coverage Studio")]
        public static void Open()
        {
            var window = GetWindow<VufLocaleCoverageWindow>("VF-07 Locale QA");
            window.minSize = new Vector2(600f, 520f);
            window.Show();
        }

        private void OnGUI()
        {
            EditorGUILayout.LabelField("VF-07 | Draft EN/TR Localization Coverage",
                EditorStyles.boldLabel);
            EditorGUILayout.HelpBox(
                "Read-only inspection of external locale_audit.py metadata. " +
                "No actual game translations are imported or enabled, no " +
                "approval/rights sign-off is implied. Real translated UI " +
                "rendering, truncation and owner language review remain OPEN.",
                MessageType.Warning);
            EditorGUI.BeginChangeCheck();
            draftReport = (TextAsset)EditorGUILayout.ObjectField(
                "Draft report JSON", draftReport, typeof(TextAsset), false);
            if (EditorGUI.EndChangeCheck())
                Inspect();
            if (GUILayout.Button("Validate imported coverage (read-only)"))
                Inspect();
            if (!String.IsNullOrEmpty(error))
                EditorGUILayout.HelpBox(error, MessageType.Error);
            if (result == null) return;
            EditorGUILayout.LabelField("Profile", result.profile_id);
            EditorGUILayout.LabelField("Product state", "DRAFT / NOT APPROVED");
            scroll = EditorGUILayout.BeginScrollView(scroll);
            foreach (LocaleStatus locale in result.locales)
            {
                EditorGUILayout.BeginVertical("box");
                EditorGUILayout.LabelField(locale.locale.ToUpperInvariant(),
                    EditorStyles.boldLabel);
                EditorGUILayout.LabelField("Screen headings entered",
                    locale.covered + " / " + locale.total);
                EditorGUILayout.LabelField("Coverage",
                    (locale.coverage_basis_points / 100f).ToString("F2") + "%");
                if (locale.missing_keys.Length != 0)
                    EditorGUILayout.HelpBox("Missing: " +
                        String.Join(", ", locale.missing_keys), MessageType.Warning);
                if (locale.long_copy_review_keys.Length != 0)
                    EditorGUILayout.HelpBox("Copy length review: " +
                        String.Join(", ", locale.long_copy_review_keys),
                        MessageType.Warning);
                EditorGUILayout.EndVertical();
            }
            foreach (string warning in result.warning_codes)
                EditorGUILayout.HelpBox(warning, MessageType.Warning);
            EditorGUILayout.HelpBox(
                "OFF BY POLICY remains OFF even if a heading is translated. " +
                "No actual translation text, visuals, gameplay actions or asset " +
                "authorizations are enabled by this report.",
                MessageType.Warning);
            EditorGUILayout.EndScrollView();
        }

        private void Inspect()
        {
            result = null;
            error = null;
            if (draftReport == null) return;
            try { result = Parse(draftReport.text); }
            catch (Exception exception)
            {
                error = "Invalid or forged locale report: " + exception.Message;
            }
        }

        private static void CheckSha(string sha)
        {
            if (sha == null || sha.Length != 64)
                throw new ArgumentException("SHA-256 receipt missing");
            foreach (char c in sha)
                if (!(c >= '0' && c <= '9') && !(c >= 'a' && c <= 'f'))
                    throw new ArgumentException("SHA-256 receipt invalid");
        }

        internal static Report Parse(string json)
        {
            if (String.IsNullOrEmpty(json) || json.Length > 100000)
                throw new ArgumentException("missing or oversized coverage");
            Report parsed = JsonUtility.FromJson<Report>(json);
            if (parsed == null || parsed.schema_version != 1 ||
                parsed.stage != "REVIEW_REQUIRED_NOT_APPROVED" ||
                parsed.profile_id != "Coral_Rescue" ||
                parsed.report_type != "OFFLINE_DRAFT_COVERAGE_V01" ||
                parsed.owner_translation_approved || parsed.game_bindings_enabled ||
                parsed.locales == null || parsed.locales.Length != 2 ||
                parsed.warning_codes == null ||
                parsed.policy_off_keys == null ||
                parsed.shared_placeholder_checked_keys == null)
                throw new ArgumentException("draft stage/locale contract changed");
            CheckSha(parsed.source_manifest_sha256);
            CheckSha(parsed.source_contract_sha256);

            var screens = VufScreenCatalog.LoadScreens();
            var known = new HashSet<string>(StringComparer.Ordinal);
            var policyOff = new HashSet<string>(StringComparer.Ordinal);
            foreach (var screen in screens)
            {
                if (!known.Add(screen.key))
                    throw new ArgumentException("duplicate source contract");
                if (screen.feature_gate == "OFF_UNTIL_ENGINE_POLICY_CONFIRMED")
                    policyOff.Add(screen.key);
            }
            var foundPolicy = new HashSet<string>(parsed.policy_off_keys,
                StringComparer.Ordinal);
            if (foundPolicy.Count != policyOff.Count || !foundPolicy.SetEquals(policyOff)
                || parsed.policy_off_keys.Length != policyOff.Count)
                throw new ArgumentException("disabled feature gates missing");

            var names = new HashSet<string>(StringComparer.Ordinal);
            foreach (LocaleStatus locale in parsed.locales)
            {
                if (locale == null ||
                    (locale.locale != "en" && locale.locale != "tr") ||
                    !names.Add(locale.locale) || locale.covered < 0 ||
                    locale.total != 28 || locale.covered > locale.total ||
                    locale.coverage_basis_points != locale.covered * 10000 / locale.total ||
                    locale.missing_keys == null || locale.long_copy_review_keys == null)
                    throw new ArgumentException("invalid locale coverage");
                var missing = new HashSet<string>(locale.missing_keys,
                    StringComparer.Ordinal);
                if (missing.Count != locale.missing_keys.Length ||
                    missing.Count != locale.total - locale.covered ||
                    !known.IsSupersetOf(missing))
                    throw new ArgumentException("invalid or duplicate missing keys");
                var longReview = new HashSet<string>(locale.long_copy_review_keys,
                    StringComparer.Ordinal);
                if (longReview.Count != locale.long_copy_review_keys.Length ||
                    !known.IsSupersetOf(longReview))
                    throw new ArgumentException("unknown long-copy keys");
                foreach (string key in longReview)
                    if (missing.Contains(key))
                        throw new ArgumentException("missing key cannot have text-length review");
            }
            if (names.Count != 2 ||
                parsed.locales[0].locale != "en" ||
                parsed.locales[1].locale != "tr")
                throw new ArgumentException("EN/TR ordering missing");
            foreach (string key in parsed.shared_placeholder_checked_keys)
                if (!known.Contains(key))
                    throw new ArgumentException("unknown placeholder screen");
            foreach (string warning in parsed.warning_codes)
                if (String.IsNullOrEmpty(warning) ||
                    (!warning.StartsWith("INCOMPLETE_LOCALE: ", StringComparison.Ordinal)
                     && !warning.StartsWith("EXPANDED_COPY_REVIEW: ", StringComparison.Ordinal)))
                    throw new ArgumentException("unknown warning type");
            return parsed;
        }
    }
}
