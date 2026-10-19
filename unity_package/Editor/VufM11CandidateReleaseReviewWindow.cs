// M11-001/002/003/005 | Owner-facing TEST_ONLY release-candidate audit.
// Read-only Unity Editor inspector of externally produced M11 files.
// No production importer, no Unity game actions, no File.Write/AssetDatabase
// mutation. A C# source SHA inspection is NOT the independent full Python
// canonical/content-identity verifier and does not confer owner approval.
using System;
using System.Collections.Generic;
using System.IO;
using System.Security.Cryptography;
using UnityEditor;
using UnityEngine;

namespace Match3.VisualFactory.Editor
{
    public sealed class VufM11CandidateReleaseReviewWindow : EditorWindow
    {
        private const string Stage = "VUF_M11_REVIEW_ONLY_NOT_PRODUCTION";
        private const string PinState =
            "OBSERVED_UNACCEPTED_NOT_REPLAY_VERIFIED";
        [Serializable]
        internal sealed class Asset
        {
            public string path, sha256;
        }
        [Serializable]
        internal sealed class Candidate
        {
            public int schema_version;
            public string stage, profile_id, engine_observed_git_sha;
            public string lfx_observed_git_sha, upstream_pin_state;
            public string source_manifest_sha256, source_receipt_sha256;
            public string content_identity_sha256;
            public bool engine_abi_accepted, lfx_replay_accepted;
            public bool final_game_action_bound, licensed_art_approved;
            public bool owner_visual_approved, player_build_tested;
            public bool device_gpu_approved, release_allowed;
            public Asset[] artifacts;
        }
        private string chosen;
        private Candidate current;
        private string outcome = "No M11 candidate inspected. Select external manifest.";
        private Vector2 scroll;
        [MenuItem("Tools/MATCH3/M11 Release Candidate and Rights Audit")]
        public static void Open()
        {
            var w = GetWindow<VufM11CandidateReleaseReviewWindow>("M11 Release QA");
            w.minSize = new Vector2(670, 600);
            w.Show();
        }

        internal static bool ValidHex(string text, int count)
        {
            if (text == null || text.Length != count) return false;
            foreach (char c in text)
                if (!((c >= '0' && c <= '9') ||
                      (c >= 'a' && c <= 'f'))) return false;
            return true;
        }

        internal static bool SafeRelativeFile(string name)
        {
            if (String.IsNullOrEmpty(name) || name.Length > 180 ||
                name.StartsWith("/", StringComparison.Ordinal) ||
                name.Contains("\\") || name.Contains(":") ||
                name.Contains("%") || name.Contains("//") ||
                !(name.EndsWith(".json", StringComparison.Ordinal) ||
                  name.EndsWith(".png", StringComparison.Ordinal)))
                return false;
            foreach (var part in name.Split('/'))
            {
                if (part.Length == 0 || part.Length > 70 ||
                    part == "." || part == ".." || part[0] == '.')
                    return false;
                foreach (char c in part)
                    if (!(c >= 'a' && c <= 'z') &&
                        !(c >= 'A' && c <= 'Z') &&
                        !(c >= '0' && c <= '9') &&
                        c != '-' && c != '_' && c != '.')
                        return false;
            }
            return true;
        }

        internal static Candidate ValidateManifest(string json)
        {
            if (String.IsNullOrEmpty(json) || json.Length > 128 * 1024)
                throw new ArgumentException("missing/oversized candidate JSON");
            Candidate c;
            try { c = JsonUtility.FromJson<Candidate>(json); }
            catch (Exception ex)
            { throw new ArgumentException("invalid candidate release JSON", ex); }
            if (c == null || c.schema_version != 1 ||
                c.stage != Stage || c.upstream_pin_state != PinState ||
                c.engine_abi_accepted || c.lfx_replay_accepted ||
                c.final_game_action_bound || c.licensed_art_approved ||
                c.owner_visual_approved || c.player_build_tested ||
                c.device_gpu_approved || c.release_allowed ||
                !ValidHex(c.engine_observed_git_sha, 40) ||
                !ValidHex(c.lfx_observed_git_sha, 40) ||
                !ValidHex(c.content_identity_sha256, 64) ||
                !ValidHex(c.source_manifest_sha256, 64) ||
                !ValidHex(c.source_receipt_sha256, 64) ||
                c.artifacts == null || c.artifacts.Length < 45 ||
                c.artifacts.Length > 160)
                throw new ArgumentException("unsafe/staged production release claim");
            string[] profiles = { "Coral_Rescue", "Garage_Legends",
                "Dino_Islands", "The_Fractured_Realms", "Wonder_Pop" };
            if (Array.IndexOf(profiles, c.profile_id) < 0)
                throw new ArgumentException("unknown game identity");
            var seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            foreach (Asset item in c.artifacts)
                if (item == null || !SafeRelativeFile(item.path) ||
                    !ValidHex(item.sha256, 64) || !seen.Add(item.path))
                    throw new ArgumentException("duplicate/missing/unsafe source image");
            if (!seen.Contains("visual_manifest.json"))
                throw new ArgumentException("original VUF candidate manifest missing");
            return c;
        }

        private static void ProtectDirectory(string source)
        {
            for (var dir = new DirectoryInfo(source);
                dir != null; dir = dir.Parent)
                if (!dir.Exists ||
                    (dir.Attributes & FileAttributes.ReparsePoint) != 0)
                    throw new IOException("linked or missing candidate source folder");
        }

        internal static Candidate InspectExistingExternal(string file)
        {
            if (String.IsNullOrEmpty(file) ||
                !Path.IsPathRooted(file) ||
                Path.GetFileName(file) != "m11_candidate_manifest.json")
                throw new ArgumentException("select original external M11 manifest");
            var source = new FileInfo(file);
            if (!source.Exists || source.Length > 128 * 1024 ||
                (source.Attributes & FileAttributes.ReparsePoint) != 0)
                throw new ArgumentException("candidate manifest missing/linked/oversized");
            string parent = source.DirectoryName;
            ProtectDirectory(parent);
            string sourceRoot = Path.GetFullPath(parent) +
                Path.DirectorySeparatorChar;
            string checkout = Path.GetFullPath(Directory.GetCurrentDirectory()) +
                Path.DirectorySeparatorChar;
            if (sourceRoot.StartsWith(checkout, StringComparison.OrdinalIgnoreCase))
                throw new ArgumentException("use NEW external candidate outside checkout");
            Candidate candidate = ValidateManifest(File.ReadAllText(file));
            long size = 0;
            foreach (Asset artifact in candidate.artifacts)
            {
                string path = Path.GetFullPath(Path.Combine(parent,
                    artifact.path.Replace('/', Path.DirectorySeparatorChar)));
                if (!path.StartsWith(sourceRoot, StringComparison.OrdinalIgnoreCase))
                    throw new IOException("candidate source escaped folder");
                ProtectDirectory(Path.GetDirectoryName(path));
                var info = new FileInfo(path);
                if (!info.Exists || (info.Attributes & FileAttributes.ReparsePoint) != 0 ||
                    info.Length > 16 * 1024 * 1024)
                    throw new IOException("missing/unsafe candidate file: " + artifact.path);
                size += info.Length;
                if (size > 128L * 1024 * 1024)
                    throw new IOException("release-candidate source byte limit");
                using (var input = new FileStream(path, FileMode.Open,
                    FileAccess.Read, FileShare.Read))
                using (var sha = SHA256.Create())
                {
                    string digest = BitConverter.ToString(sha.ComputeHash(input))
                        .Replace("-", "").ToLowerInvariant();
                    if (digest != artifact.sha256)
                        throw new IOException("SOURCE HASH MISMATCH: " + artifact.path);
                }
            }
            // SHA entries verified. Independent Python MUST also check the
            // canonical manifest identity, M08 receipt, VF04 atlas, all
            // unlisted files, legal evidence and actual Engine/LFX parity.
            return candidate;
        }

        private void OnGUI()
        {
            EditorGUILayout.LabelField("M11 | TEST_ONLY Release Candidate Audit",
                EditorStyles.boldLabel);
            EditorGUILayout.HelpBox(
                "Read-only. A hash-verified candidate is NOT shippable; observed " +
                "Git SHAs are NOT final Engine/LFX compatibility. Full Python " +
                "canonical audit, owner artwork and original fonts/rights, " +
                "GUI and physical devices remain required.",
                MessageType.Warning);
            if (GUILayout.Button("Select external M11 candidate manifest"))
            {
                chosen = EditorUtility.OpenFilePanel(
                    "M11 generated review-only release manifest",
                    Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments),
                    "json");
                current = null;
            }
            EditorGUILayout.SelectableLabel(chosen ?? "(not selected)");
            if (GUILayout.Button("Read and verify ALL referenced source SHA-256"))
            {
                current = null;
                try
                {
                    current = InspectExistingExternal(chosen);
                    outcome = "SOURCE SHA audit passed. " +
                        "Full canonical/rights/replay/platform acceptance STILL OPEN.";
                }
                catch (Exception ex) { outcome = "BLOCKED: " + ex.Message; }
            }
            EditorGUILayout.HelpBox(outcome,
                current == null ? MessageType.Info : MessageType.Warning);
            if (current != null)
            {
                scroll = EditorGUILayout.BeginScrollView(scroll);
                EditorGUILayout.LabelField("Candidate profile", current.profile_id);
                EditorGUILayout.LabelField("Content identity (unchecked here)",
                    current.content_identity_sha256);
                EditorGUILayout.LabelField("Observed Engine SHA (not accepted)",
                    current.engine_observed_git_sha);
                EditorGUILayout.LabelField("Observed LFX SHA (not accepted)",
                    current.lfx_observed_git_sha);
                EditorGUILayout.LabelField("Independently hash-bound source assets",
                    current.artifacts.Length.ToString());
                EditorGUILayout.LabelField("Engine/LFX ABI accepted", "FALSE");
                EditorGUILayout.LabelField("Licensed artwork/owner accepted", "FALSE");
                EditorGUILayout.LabelField("Player release allowed", "FALSE");
                EditorGUILayout.LabelField("Active game rollback performed", "NO");
                foreach (var asset in current.artifacts)
                    EditorGUILayout.SelectableLabel(
                        asset.path + "   " + asset.sha256.Substring(0, 16),
                        GUILayout.MinHeight(18));
                EditorGUILayout.EndScrollView();
            }
            if (GUILayout.Button("Open existing M08 review-only Unity importer"))
                VufCandidatePackImporterWindow.Open();
            if (GUILayout.Button("Open owner evidence and rights board"))
                VufReadinessBoardWindow.Open();
            EditorGUILayout.HelpBox(
                "M11 source rollback = append-only NEW candidate slot; no " +
                "active player pointer is changed, no source folder overwritten. " +
                "Real G01/G02/G09/G11 consumer handoff needs separate owner approval.",
                MessageType.Warning);
        }
    }
}
