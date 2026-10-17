// VUF R46 / VF-10: runtime-contract-based, read-only version drift GUI.
// INTERNAL_REUSE: VisualAssetManifest.TryParsePreview, no duplicate JSON
// parser and no production/approved owner packs accepted from arbitrary text.
using System;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using Match3.VisualFactory;

namespace Match3.VisualFactory.Editor
{
    public sealed class VufPreviewCompatibilityWindow : EditorWindow
    {
        private static readonly string[] Profiles = {
            "Coral_Rescue", "Garage_Legends", "Dino_Islands",
            "The_Fractured_Realms", "Wonder_Pop"
        };
        private TextAsset current;
        private TextAsset previous;
        private int selectedProfile;
        private string expectedEngine = "";
        private string expectedLfx = "";
        private Result result;
        private string error;
        private Vector2 scroll;

        internal sealed class Result
        {
            internal string ProfileId;
            internal int CurrentAssets;
            internal bool PinsMatch;
            internal bool PreviousCompared;
            internal readonly List<string> Mismatches = new List<string>();
            internal readonly List<string> AssetChanges = new List<string>();
            internal bool ReleaseAllowed => false;
            internal bool RightsVerified => false;
            internal bool DeviceVerified => false;
            internal bool EngineLfxIndependentlyAccepted => false;
        }

        [MenuItem("Tools/MATCH3/Preview Version Compatibility")]
        public static void Open()
        {
            var window = GetWindow<VufPreviewCompatibilityWindow>(
                "VUF Compatibility");
            window.minSize = new Vector2(620, 520);
            window.Show();
        }

        private void OnGUI()
        {
            EditorGUILayout.LabelField(
                "VF-10 | Read-Only Draft Version / Compatibility", EditorStyles.boldLabel);
            EditorGUILayout.HelpBox(
                "Compares explicitly imported TEST_ONLY visual manifests with exact " +
                "declared Engine/LFX SHA pins. This is NOT Engine compatibility, " +
                "actual asset-byte verification, approved art, real rollback or " +
                "a release action. Only an independent owner can close gates.",
                MessageType.Warning);
            current = (TextAsset)EditorGUILayout.ObjectField(
                "Imported current TEST_ONLY manifest", current, typeof(TextAsset), false);
            previous = (TextAsset)EditorGUILayout.ObjectField(
                "Optional previous TEST_ONLY manifest", previous,
                typeof(TextAsset), false);
            selectedProfile = EditorGUILayout.Popup("Expected game profile",
                selectedProfile, Profiles);
            expectedEngine = EditorGUILayout.TextField(
                "Expected Engine full SHA", expectedEngine);
            expectedLfx = EditorGUILayout.TextField(
                "Expected LevelFactory full SHA", expectedLfx);
            if (GUILayout.Button("Compare metadata without writing anything",
                    GUILayout.Height(32f)))
            {
                result = null; error = null;
                try
                {
                    result = Evaluate(current != null ? current.text : null,
                        previous != null ? previous.text : null,
                        Profiles[selectedProfile], expectedEngine, expectedLfx);
                }
                catch (Exception exception)
                {
                    error = "Manifest comparison BLOCKED: " + exception.Message;
                }
            }
            if (!String.IsNullOrEmpty(error))
                EditorGUILayout.HelpBox(error, MessageType.Error);
            if (result == null) return;
            EditorGUILayout.LabelField("Game", result.ProfileId);
            EditorGUILayout.LabelField("Current listed asset IDs",
                result.CurrentAssets.ToString());
            EditorGUILayout.LabelField("Declared SHA matches expected pins",
                result.PinsMatch ? "YES (UNAUTHENTICATED)" : "NO");
            EditorGUILayout.LabelField("Release permitted", "NO / OWNER GATES OPEN");
            scroll = EditorGUILayout.BeginScrollView(scroll);
            foreach (string item in result.Mismatches)
                EditorGUILayout.HelpBox(item, MessageType.Error);
            foreach (string item in result.AssetChanges)
                EditorGUILayout.SelectableLabel(item, GUILayout.Height(20f));
            EditorGUILayout.EndScrollView();
        }

        private static bool IsSha(string value)
        {
            if (String.IsNullOrEmpty(value) || value.Length != 40) return false;
            foreach (char c in value)
                if (!((c >= '0' && c <= '9') ||
                      (c >= 'a' && c <= 'f')))
                    return false;
            return true;
        }

        internal static Result Evaluate(string currentJson, string previousJson,
            string profile, string engineSha, string lfxSha)
        {
            if (Array.IndexOf(Profiles, profile) < 0 ||
                !IsSha(engineSha) || !IsSha(lfxSha))
                throw new ArgumentException("known profile and exact lowercase SHA required");
            VisualAssetManifest current;
            string reason;
            if (!VisualAssetManifest.TryParsePreview(currentJson, out current,
                    out reason) || current.profile_id != profile ||
                current.assets.Length > 512)
                throw new ArgumentException("invalid current TEST_ONLY preview manifest");
            Dictionary<string, string> latest = Snapshot(current);
            var report = new Result { ProfileId = profile,
                                      CurrentAssets = latest.Count };
            if (current.engine_sha != engineSha)
                report.Mismatches.Add("Engine SHA differs from expected pin");
            if (current.level_factory_sha != lfxSha)
                report.Mismatches.Add("LevelFactory SHA differs from expected pin");
            report.PinsMatch = report.Mismatches.Count == 0;
            if (previousJson != null)
            {
                VisualAssetManifest previous;
                if (!VisualAssetManifest.TryParsePreview(previousJson, out previous,
                        out reason) || previous.profile_id != profile ||
                    previous.assets.Length > 512)
                    throw new ArgumentException("invalid previous TEST_ONLY manifest");
                Dictionary<string, string> before = Snapshot(previous);
                report.PreviousCompared = true;
                var keys = new SortedSet<string>(before.Keys, StringComparer.Ordinal);
                keys.UnionWith(latest.Keys);
                foreach (string key in keys)
                {
                    string oldDigest, newDigest;
                    bool oldPresent = before.TryGetValue(key, out oldDigest);
                    bool newPresent = latest.TryGetValue(key, out newDigest);
                    if (!oldPresent)
                        report.AssetChanges.Add("ADDED: " + key);
                    else if (!newPresent)
                        report.AssetChanges.Add("REMOVED: " + key);
                    else if (oldDigest != newDigest)
                        report.AssetChanges.Add("CHANGED: " + key);
                }
            }
            return report;
        }

        private static Dictionary<string, string> Snapshot(VisualAssetManifest data)
        {
            var result = new Dictionary<string, string>(StringComparer.Ordinal);
            foreach (VisualAssetManifest.Asset asset in data.assets)
            {
                if (!result.TryAdd(asset.asset_id, asset.sha256))
                    throw new ArgumentException("duplicate asset ID");
                if (asset.path == null || asset.path.StartsWith("/", StringComparison.Ordinal)
                    || asset.path.IndexOf("..", StringComparison.Ordinal) >= 0
                    || asset.path.Contains("\\") || asset.path.Contains(":"))
                    throw new ArgumentException("unsafe asset path");
            }
            return result;
        }
    }
}
