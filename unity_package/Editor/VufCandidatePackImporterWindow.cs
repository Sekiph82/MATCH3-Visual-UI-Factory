// VUF-M08-001/003 | Explicit owner-directed source-hashed candidate import.
// A complete nonshipping VUF M08 offline bundle may be copied into
// Assets/Editor/VUF_ReviewImports (automatically excluded from player builds).
// No Addressables fetch, no gameplay authority, no original/source overwrite.
// Every digest is checked before import and AGAIN on the copied byte stream.
using System;
using System.Collections.Generic;
using System.IO;
using System.Security.Cryptography;
using UnityEditor;
using UnityEngine;

namespace Match3.VisualFactory.Editor
{
    public sealed class VufCandidatePackImporterWindow : EditorWindow
    {
        [Serializable]
        internal sealed class Entry
        {
            public string path;
            public string sha256;
        }
        [Serializable]
        internal sealed class Receipt
        {
            public string generator;
            public string stage;
            public string profile_id;
            public bool owner_visual_approved, rights_approved;
            public bool real_engine_lfx_sha_pinned, device_gpu_approved;
            public bool actual_game_actions, release_allowed;
            public int image_count;
            public Entry[] file_entries;
        }

        private string selectedReceipt;
        private string outcome = "Select external candidate_pack_receipt.json.";
        private string importedManifest;

        [MenuItem("Tools/MATCH3/Import External TEST_ONLY Pack Copies")]
        public static void Open()
        {
            var window = GetWindow<VufCandidatePackImporterWindow>(
                "VUF Offline Import");
            window.minSize = new Vector2(630, 330);
            window.Show();
        }

        internal static Receipt ValidateReceipt(string json)
        {
            if (String.IsNullOrEmpty(json) || json.Length > 512 * 1024)
                throw new ArgumentException("missing/oversized bundle receipt");
            Receipt parsed;
            try { parsed = JsonUtility.FromJson<Receipt>(json); }
            catch (Exception error)
            { throw new ArgumentException("invalid receipt JSON", error); }
            if (parsed == null ||
                parsed.generator != "VUF_M08_OFFLINE_CANDIDATE_PACK_V01" ||
                parsed.stage != "TEST_ONLY" ||
                parsed.owner_visual_approved || parsed.rights_approved ||
                parsed.real_engine_lfx_sha_pinned || parsed.device_gpu_approved ||
                parsed.actual_game_actions || parsed.release_allowed ||
                parsed.file_entries == null ||
                parsed.file_entries.Length < 40 ||
                parsed.file_entries.Length > 160 ||
                parsed.image_count < 40 || parsed.image_count > 128)
                throw new ArgumentException("unauthorized owner/game stage or source count");
            var validProfiles = new [] {
                "Coral_Rescue", "Garage_Legends", "Dino_Islands",
                "The_Fractured_Realms", "Wonder_Pop"
            };
            if (Array.IndexOf(validProfiles, parsed.profile_id) < 0)
                throw new ArgumentException("not one of the five game namespaces");
            bool seenManifest = false;
            var names = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            foreach (Entry entry in parsed.file_entries)
            {
                if (entry == null || !SafePath(entry.path) ||
                    !VufExternalPackSandboxWindow.IsSha(entry.sha256) ||
                    !names.Add(entry.path))
                    throw new ArgumentException("unsafe/duplicate/missing receipt file");
                if (entry.path == "visual_manifest.json") seenManifest = true;
            }
            if (!seenManifest)
                throw new ArgumentException("actual VisualAssetManifest missing");
            return parsed;
        }

        internal static bool SafePath(string path)
        {
            if (String.IsNullOrEmpty(path) || path.Length > 180 ||
                path.Contains("%") || path.Contains(":") ||
                path.Contains("\\") || path.StartsWith("/", StringComparison.Ordinal) ||
                path.Contains("//") ||
                !(path.EndsWith(".png", StringComparison.Ordinal) ||
                  path.EndsWith(".json", StringComparison.Ordinal)))
                return false;
            string[] parts = path.Split('/');
            if (parts.Length > 10) return false;
            foreach (string part in parts)
            {
                if (part.Length == 0 || part.Length > 75 ||
                    part == "." || part == ".." || part[0] == '.')
                    return false;
                foreach (char c in part)
                    if (!(c >= 'a' && c <= 'z') &&
                        !(c >= 'A' && c <= 'Z') &&
                        !(c >= '0' && c <= '9') &&
                        c != '_' && c != '-' && c != '.')
                        return false;
            }
            return true;
        }

        private static string ShaFile(string filename)
        {
            var source = new FileInfo(filename);
            if (!source.Exists ||
                (source.Attributes & FileAttributes.ReparsePoint) != 0 ||
                source.Length <= 0 || source.Length > 16 * 1024 * 1024)
                throw new ArgumentException("invalid linked/missing/oversized source file");
            using (var stream = new FileStream(filename, FileMode.Open,
                FileAccess.Read, FileShare.Read))
            using (var sha = SHA256.Create())
                return BitConverter.ToString(sha.ComputeHash(stream))
                    .Replace("-", "").ToLowerInvariant();
        }

        private static void ProtectDirectories(string directory)
        {
            for (DirectoryInfo current = new DirectoryInfo(directory);
                current != null; current = current.Parent)
            {
                if (!current.Exists ||
                    (current.Attributes & FileAttributes.ReparsePoint) != 0)
                    throw new ArgumentException("missing or reparse/symlinked folder");
            }
        }

        internal static string ImportNewExternalCopy(string receiptFilename)
        {
            if (String.IsNullOrEmpty(receiptFilename) ||
                !Path.IsPathRooted(receiptFilename) ||
                Path.GetFileName(receiptFilename) != "candidate_pack_receipt.json")
                throw new ArgumentException("select a VUF candidate receipt file");
            var receiptFile = new FileInfo(receiptFilename);
            if (!receiptFile.Exists || receiptFile.Length > 512 * 1024 ||
                (receiptFile.Attributes & FileAttributes.ReparsePoint) != 0)
                throw new ArgumentException("receipt is missing/oversized/symlinked");
            string source = receiptFile.DirectoryName;
            ProtectDirectories(source);
            string checkout = Path.GetFullPath(Directory.GetCurrentDirectory()) +
                Path.DirectorySeparatorChar;
            string sourceFull = Path.GetFullPath(source) +
                Path.DirectorySeparatorChar;
            if (sourceFull.StartsWith(checkout, StringComparison.OrdinalIgnoreCase))
                throw new ArgumentException("external source must live outside Unity checkout");
            Receipt receipt = ValidateReceipt(File.ReadAllText(receiptFilename));
            long total = 0;
            foreach (Entry entry in receipt.file_entries)
            {
                string name = Path.GetFullPath(Path.Combine(source,
                    entry.path.Replace('/', Path.DirectorySeparatorChar)));
                if (!name.StartsWith(sourceFull, StringComparison.OrdinalIgnoreCase))
                    throw new ArgumentException("path escaped source");
                ProtectDirectories(Path.GetDirectoryName(name));
                if (ShaFile(name) != entry.sha256)
                    throw new ArgumentException("source file SHA mismatch: " + entry.path);
                total += new FileInfo(name).Length;
                if (total > 128L * 1024 * 1024)
                    throw new ArgumentException("preview pack exceeds 128MiB source limit");
            }
            string destinationRoot = Path.Combine(Application.dataPath,
                "Editor", "VUF_ReviewImports");
            string receiptSHA = ShaFile(receiptFilename);
            string target = Path.Combine(destinationRoot,
                receipt.profile_id + "_" + receiptSHA.Substring(0, 12));
            if (Directory.Exists(target) || File.Exists(target))
                throw new IOException("import destination already exists, no overwrite");
            // Owners explicitly pressed Import. The only destination is the
            // Editor-only Assets subtree, thus NEVER included in the game player.
            Directory.CreateDirectory(destinationRoot);
            ProtectDirectories(destinationRoot);
            Directory.CreateDirectory(target);
            foreach (Entry entry in receipt.file_entries)
            {
                string from = Path.Combine(source,
                    entry.path.Replace('/', Path.DirectorySeparatorChar));
                string to = Path.Combine(target,
                    entry.path.Replace('/', Path.DirectorySeparatorChar));
                Directory.CreateDirectory(Path.GetDirectoryName(to));
                using (var input = new FileStream(from, FileMode.Open,
                    FileAccess.Read, FileShare.Read))
                using (var output = new FileStream(to, FileMode.CreateNew,
                    FileAccess.Write, FileShare.None))
                    input.CopyTo(output);
                if (ShaFile(to) != entry.sha256)
                    throw new IOException("copied candidate hash changed: " + entry.path);
            }
            AssetDatabase.Refresh();
            string relative = "Assets/Editor/VUF_ReviewImports/" +
                Path.GetFileName(target) + "/visual_manifest.json";
            return relative;
        }

        private void OnGUI()
        {
            EditorGUILayout.LabelField("M08 | Import review-only pack COPIES",
                EditorStyles.boldLabel);
            EditorGUILayout.HelpBox(
                "Import only a VUF generated TEST_ONLY mathematical prototype. " +
                "Files go under Assets/Editor/VUF_ReviewImports and are excluded " +
                "from a normal Unity player. A new folder is required, and no " +
                "existing file/importer/GUID is overwritten. The copy is NOT " +
                "production art or a real Engine asset pack.",
                MessageType.Warning);
            if (GUILayout.Button("Select EXTERNAL candidate_pack_receipt.json"))
                selectedReceipt = EditorUtility.OpenFilePanel(
                    "Choose original immutable candidate pack receipt",
                    Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments),
                    "json");
            EditorGUILayout.SelectableLabel(selectedReceipt ?? "(nothing selected)");
            if (GUILayout.Button("Validate ALL source hashes and import NEW copies"))
            {
                try
                {
                    importedManifest = ImportNewExternalCopy(selectedReceipt);
                    outcome = "Imported manifest (TEST_ONLY): " + importedManifest;
                }
                catch (Exception ex)
                {
                    importedManifest = null;
                    outcome = "REFUSED: " + ex.Message;
                }
            }
            EditorGUILayout.HelpBox(outcome,
                importedManifest == null ? MessageType.Info : MessageType.Warning);
            if (!String.IsNullOrEmpty(importedManifest) &&
                GUILayout.Button("Open read-only External Visual Pack Sandbox"))
                VufExternalPackSandboxWindow.Open();
        }
    }
}
