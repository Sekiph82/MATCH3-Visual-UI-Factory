// VUF-M08-001/003/006 | Read-only external visual-pack sandbox, not Engine.
// This opens only manually imported TEST_ONLY VUF manifest/assets COPIES
// inside Assets/, validates bytes and presents five-theme A/B preview.
// NO Engine/LFX dependency or parity claim, no Addressables download,
// no Unity importer writes, no player asset packaging or gameplay authority.
using System;
using System.Collections.Generic;
using System.IO;
using System.Security.Cryptography;
using UnityEditor;
using UnityEngine;

namespace Match3.VisualFactory.Editor
{
    public sealed class VufExternalPackSandboxWindow : EditorWindow
    {
        internal sealed class InspectedPack
        {
            internal VisualAssetManifest Manifest;
            internal string Folder;
            internal readonly Dictionary<string, string> AssetPaths =
                new Dictionary<string, string>(StringComparer.Ordinal);
            internal readonly Dictionary<string, string> SourceHashes =
                new Dictionary<string, string>(StringComparer.Ordinal);
        }

        private TextAsset leftManifest;
        private TextAsset rightManifest;
        private InspectedPack left, right;
        private int selected, localeIndex, viewEventIndex;
        private bool stageRightPack;
        private GameObject stagedTemporary;
        private Sprite stagedOwnedSprite;
        private Vector2 scroll;
        private static readonly string[] LocaleKeys = { "en", "tr" };
        private string result = "Not reviewed. Import TEST_ONLY pack COPIES under Assets/.";
        private static readonly string[] Profiles = {
            "Coral_Rescue", "Garage_Legends", "Dino_Islands",
            "The_Fractured_Realms", "Wonder_Pop"
        };

        [MenuItem("Tools/MATCH3/External Visual Pack Sandbox")]
        public static void Open()
        {
            var window = GetWindow<VufExternalPackSandboxWindow>("VUF Pack Sandbox");
            window.minSize = new Vector2(720f, 680f);
            window.Show();
        }

        [Serializable] internal sealed class DraftTexts
        {
            public string title, action, offline, loading, disabled;
        }
        [Serializable] internal sealed class DraftLocale
        {
            public int schema_version;
            public string profile_id, locale, stage;
            public bool actual_gameplay_labels_verified, release_allowed;
            public DraftTexts texts;
        }

        internal static string ReadDraftLocale(string json, string expectedProfile,
            string expectedLocale)
        {
            // Missing locale is a clearly inert offline placeholder, never
            // language/account fallback that activates a real Engine action.
            if (String.IsNullOrEmpty(json))
                return "[OFFLINE_DRAFT_FALLBACK / ACTION_DISABLED]";
            if (json.Length > 64 * 1024)
                throw new ArgumentException("candidate locale too large");
            DraftLocale parsed;
            try { parsed = JsonUtility.FromJson<DraftLocale>(json); }
            catch (Exception ex)
            { throw new ArgumentException("invalid draft locale JSON", ex); }
            if (parsed == null || parsed.schema_version != 1 ||
                parsed.profile_id != expectedProfile ||
                parsed.locale != expectedLocale ||
                (expectedLocale != "en" && expectedLocale != "tr") ||
                parsed.stage != "DRAFT_NOT_LOCALIZATION_APPROVED" ||
                parsed.actual_gameplay_labels_verified ||
                parsed.release_allowed ||
                parsed.texts == null ||
                String.IsNullOrWhiteSpace(parsed.texts.title) ||
                String.IsNullOrWhiteSpace(parsed.texts.action) ||
                String.IsNullOrWhiteSpace(parsed.texts.offline) ||
                String.IsNullOrWhiteSpace(parsed.texts.loading) ||
                String.IsNullOrWhiteSpace(parsed.texts.disabled))
                throw new ArgumentException("invalid draft language identity/authority");
            return parsed.texts.title + " | " + parsed.texts.action +
                " | " + parsed.texts.offline +
                " (DRAFT, NO ENGINE ACTION, NOT TRANSLATION APPROVED)";
        }

        private static string LocalePreview(InspectedPack pack, string locale)
        {
            if (pack == null) return "[NO VERIFIED PACK / ACTION_DISABLED]";
            string path = pack.Folder + "/locales/" + locale + ".json";
            var imported = AssetDatabase.LoadAssetAtPath<TextAsset>(path);
            return ReadDraftLocale(imported == null ? null : imported.text,
                                   pack.Manifest.profile_id, locale);
        }

        internal static void OpenImportedManifest(string importedPath)
        {
            var window = GetWindow<VufExternalPackSandboxWindow>(
                "VUF Pack Sandbox");
            window.leftManifest =
                AssetDatabase.LoadAssetAtPath<TextAsset>(importedPath);
            window.rightManifest = null;
            window.ValidateBoth();
            window.Show();
        }

        internal static bool IsSafeRelativeAssetPath(string path)
        {
            if (String.IsNullOrEmpty(path) || path.Length > 180 ||
                path.StartsWith("/", StringComparison.Ordinal) ||
                path.Contains("\\") || path.Contains(":") ||
                path.Contains("%") || path.Contains("//"))
                return false;
            string[] parts = path.Split('/');
            if (parts.Length > 10) return false;
            foreach (string part in parts)
            {
                if (part.Length == 0 || part == "." || part == ".." ||
                    part[0] == '.' || part.Length > 75)
                    return false;
                foreach (char c in part)
                    if (!((c >= 'a' && c <= 'z') ||
                          (c >= 'A' && c <= 'Z') ||
                          (c >= '0' && c <= '9') ||
                          c == '_' || c == '-' || c == '.'))
                        return false;
            }
            return path.EndsWith(".png", StringComparison.OrdinalIgnoreCase) ||
                   path.EndsWith(".webp", StringComparison.OrdinalIgnoreCase);
        }

        internal static void ValidateSymbolicPack(VisualAssetManifest pack)
        {
            if (pack == null || pack.schema_version != 1 ||
                pack.stage != "TEST_ONLY" || pack.assets == null ||
                pack.assets.Length == 0 || pack.assets.Length > 20000)
                throw new ArgumentException("invalid TEST_ONLY manifest or empty asset pack");
            if (Array.IndexOf(Profiles, pack.profile_id) < 0 ||
                String.IsNullOrWhiteSpace(pack.theme_version))
                throw new ArgumentException("unknown theme or missing revision");
            // A final external Engine/LFX SHA cannot be verified by this
            // preview sandbox. Validate shape, expose parity as NOT VERIFIED.
            var ids = new HashSet<string>(StringComparer.Ordinal);
            var paths = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            foreach (var asset in pack.assets)
            {
                if (asset == null || String.IsNullOrEmpty(asset.asset_id) ||
                    !asset.asset_id.StartsWith(pack.profile_id + ".", StringComparison.Ordinal) ||
                    !ids.Add(asset.asset_id) || !IsSafeRelativeAssetPath(asset.path) ||
                    !paths.Add(asset.path) || !IsSha(asset.sha256))
                    throw new ArgumentException("duplicate/invalid TEST_ONLY asset binding");
                if (!String.IsNullOrEmpty(asset.rights) &&
                    (asset.rights.IndexOf("APPROVED", StringComparison.OrdinalIgnoreCase) >= 0 ||
                     asset.rights.IndexOf("SHIPPING", StringComparison.OrdinalIgnoreCase) >= 0))
                    throw new ArgumentException("unverified preview cannot claim owner art rights");
            }
        }

        internal static bool IsSha(string sha)
        {
            if (String.IsNullOrEmpty(sha) || sha.Length != 64) return false;
            foreach (char c in sha)
                if (!(c >= '0' && c <= '9') &&
                    !(c >= 'a' && c <= 'f'))
                    return false;
            return true;
        }

        internal static string CheckAssetHashes(VisualAssetManifest pack,
            Func<string, string> relativeAssetToSha)
        {
            ValidateSymbolicPack(pack);
            if (relativeAssetToSha == null)
                throw new ArgumentNullException(nameof(relativeAssetToSha));
            foreach (var asset in pack.assets)
            {
                string actual = relativeAssetToSha(asset.path);
                if (!IsSha(actual) ||
                    !String.Equals(actual, asset.sha256, StringComparison.Ordinal))
                    throw new ArgumentException(
                        "source SHA-256 differs, asset unavailable or asset path unsafe");
            }
            return "TEST_ONLY source bytes matched; device/Engine/rights NOT VERIFIED";
        }

        private static string DiskDigest(string assetPath)
        {
            if (!assetPath.StartsWith("Assets/", StringComparison.Ordinal) ||
                assetPath.Contains("..") || assetPath.Contains("\\"))
                throw new ArgumentException("only an imported Assets copy can be read");
            string full = Path.GetFullPath(
                Path.Combine(Directory.GetCurrentDirectory(), assetPath));
            string root = Path.GetFullPath(
                Path.Combine(Directory.GetCurrentDirectory(), "Assets")) +
                Path.DirectorySeparatorChar;
            if (!full.StartsWith(root, StringComparison.OrdinalIgnoreCase))
                throw new ArgumentException("asset escaped the Assets sandbox");
            string folder = Path.GetDirectoryName(full);
            for (var p = new DirectoryInfo(folder); p != null; p = p.Parent)
                if ((p.Attributes & FileAttributes.ReparsePoint) != 0)
                    throw new ArgumentException("reparse/symlinked source folder refused");
            var file = new FileInfo(full);
            if (!file.Exists ||
                (file.Attributes & FileAttributes.ReparsePoint) != 0 ||
                file.Length < 8 || file.Length > 16 * 1024 * 1024)
                throw new ArgumentException("missing/linked/oversized source");
            using (var stream = new FileStream(full, FileMode.Open, FileAccess.Read, FileShare.Read))
            using (var sha = SHA256.Create())
                return BitConverter.ToString(sha.ComputeHash(stream))
                    .Replace("-", "").ToLowerInvariant();
        }

        private static InspectedPack Inspect(TextAsset json)
        {
            if (json == null || json.text == null)
                throw new ArgumentException("select imported manifest copy");
            string manifestPath = AssetDatabase.GetAssetPath(json);
            if (String.IsNullOrEmpty(manifestPath) ||
                !manifestPath.StartsWith("Assets/", StringComparison.Ordinal) ||
                !manifestPath.EndsWith(".json", StringComparison.OrdinalIgnoreCase))
                throw new ArgumentException("manifest must be a .json copy inside Assets/");
            VisualAssetManifest contract;
            string error;
            if (!VisualAssetManifest.TryParsePreview(
                json.text, out contract, out error))
                throw new ArgumentException("preview manifest schema rejected: " + error);
            ValidateSymbolicPack(contract);
            var pack = new InspectedPack
            {
                Manifest = contract,
                Folder = manifestPath.Substring(0, manifestPath.LastIndexOf('/'))
            };
            // First ensure EVERY candidate file exists, is a Texture2D imported
            // under the same folder and its original PNG SHA matches exactly.
            CheckAssetHashes(contract, relative =>
            {
                string assetPath = pack.Folder + "/" + relative;
                if (AssetDatabase.LoadAssetAtPath<Texture2D>(assetPath) == null)
                    throw new ArgumentException("missing image import: " + relative);
                string sha = DiskDigest(assetPath);
                pack.AssetPaths[relative] = assetPath;
                pack.SourceHashes[relative] = sha;
                return sha;
            });
            return pack;
        }

        private void OnDisable() { DestroyOnlyMyStage(); }

        private void DestroyOnlyMyStage()
        {
            VufExternalPackViewStage.Dispose(stagedTemporary, stagedOwnedSprite);
            stagedTemporary = null;
            stagedOwnedSprite = null;
        }

        private void StageVerifiedSelection()
        {
            DestroyOnlyMyStage();
            InspectedPack pack = stageRightPack ? right : left;
            if (pack == null) pack = left ?? right;
            if (pack == null) throw new ArgumentException("verify a pack first");
            var item = pack.Manifest.assets[
                Mathf.Clamp(selected, 0, pack.Manifest.assets.Length - 1)];
            string assetPath = pack.AssetPaths[item.path];
            // Recheck bytes at time of stage; source may have changed since
            // the owner last pressed Validate (fail-closed, no stale hash).
            if (DiskDigest(assetPath) != item.sha256)
                throw new ArgumentException("verified source bytes changed since inspect");
            var texture = AssetDatabase.LoadAssetAtPath<Texture2D>(assetPath);
            if (texture == null) throw new ArgumentException("imported image is unavailable");
            stagedTemporary = VufExternalPackViewStage.Create(
                texture, pack.Manifest.profile_id, item.asset_id,
                VufVisualEventCatalog.Events[viewEventIndex].Name,
                out stagedOwnedSprite);
            Selection.activeGameObject = stagedTemporary;
            result = "Actual temporary SpriteRenderer source staged. " +
                "VIEW ONLY, no Engine/LFX/gameplay callbacks, save or rights.";
        }

        private void ValidateBoth()
        {
            DestroyOnlyMyStage();
            // Drop stale acceptance before every new source/switch.
            left = null; right = null;
            try
            {
                if (leftManifest == null && rightManifest == null)
                    throw new ArgumentException("load at least one pack");
                InspectedPack proposedLeft = leftManifest == null ? null : Inspect(leftManifest);
                InspectedPack proposedRight = rightManifest == null ? null : Inspect(rightManifest);
                left = proposedLeft;
                right = proposedRight;
                selected = 0;
                result = "Read-only manifest and source hashes verified for " +
                    (left == null ? 0 : left.Manifest.assets.Length) + " left and " +
                    (right == null ? 0 : right.Manifest.assets.Length) +
                    " right assets. Engine/LFX FINAL PARITY, OWNER RIGHTS, GUI DEVICE " +
                    "AND PRODUCTION RELEASE: NOT VERIFIED.";
            }
            catch (Exception ex)
            {
                left = null; right = null;
                result = "FAIL CLOSED: " + ex.Message;
            }
        }

        private static void DrawPack(InspectedPack pack, int selection)
        {
            if (pack == null)
            {
                EditorGUILayout.HelpBox("No verified TEST_ONLY pack.", MessageType.None);
                return;
            }
            var assets = pack.Manifest.assets;
            var item = assets[Mathf.Clamp(selection, 0, assets.Length - 1)];
            EditorGUILayout.LabelField(
                pack.Manifest.profile_id + " / " + pack.Manifest.theme_version,
                EditorStyles.boldLabel);
            EditorGUILayout.LabelField("Asset ID", item.asset_id);
            EditorGUILayout.LabelField("Hash", item.sha256);
            EditorGUILayout.LabelField("Source", item.path);
            var image = AssetDatabase.LoadAssetAtPath<Texture2D>(
                pack.AssetPaths[item.path]);
            if (image != null)
            {
                Rect rect = GUILayoutUtility.GetRect(
                    250f, 340f, GUILayout.ExpandWidth(true));
                GUI.DrawTexture(rect, image, ScaleMode.ScaleToFit, true);
            }
            EditorGUILayout.HelpBox(
                "CANDIDATE / Owner visual, original art rights, GPU and real " +
                "device acceptance NOT VERIFIED. No importer modification.",
                MessageType.Warning);
        }

        private void OnGUI()
        {
            EditorGUILayout.LabelField("M08 | TEST_ONLY Visual Pack Sandbox",
                EditorStyles.boldLabel);
            EditorGUILayout.HelpBox(
                "Compare imported TEST_ONLY asset pack copies. Real source bytes " +
                "must match manifest SHA-256. A theme swap changes only this " +
                "Editor preview, NEVER the game, Engine rules or user saves.",
                MessageType.Warning);
            EditorGUI.BeginChangeCheck();
            leftManifest = (TextAsset)EditorGUILayout.ObjectField(
                "Candidate pack A JSON", leftManifest, typeof(TextAsset), false);
            rightManifest = (TextAsset)EditorGUILayout.ObjectField(
                "Candidate pack B JSON", rightManifest, typeof(TextAsset), false);
            if (EditorGUI.EndChangeCheck())
            {
                DestroyOnlyMyStage();
                left = null; right = null;
                result = "Pack input changed: reload/hash-check before preview.";
            }
            if (GUILayout.Button("Read ALL manifest + imported image SHA-256"))
                ValidateBoth();
            EditorGUILayout.HelpBox(result, MessageType.Info);
            var focus = left ?? right;
            if (focus == null) return;
            int max = Math.Max(left == null ? 0 : left.Manifest.assets.Length,
                               right == null ? 0 : right.Manifest.assets.Length);
            selected = EditorGUILayout.IntSlider(
                "A/B candidate index (no gameplay)", selected, 0, max - 1);
            localeIndex = EditorGUILayout.Popup("Draft locale and offline fallback",
                localeIndex, LocaleKeys);
            try
            {
                EditorGUILayout.LabelField("Pack A draft",
                    LocalePreview(left, LocaleKeys[localeIndex]), EditorStyles.wordWrappedLabel);
                EditorGUILayout.LabelField("Pack B draft",
                    LocalePreview(right, LocaleKeys[localeIndex]), EditorStyles.wordWrappedLabel);
            }
            catch (ArgumentException ex)
            {
                EditorGUILayout.HelpBox(
                    "LOCALE REJECTED: " + ex.Message +
                    " / NOT PRODUCTION TEXT", MessageType.Error);
            }
            if (GUILayout.Button("Open existing Unified Sprite & VFX manual Studio"))
                VufUnifiedVisualStudioWindow.Open();
            stageRightPack = EditorGUILayout.Toggle(
                "Stage pack B instead of pack A", stageRightPack);
            var viewEvents = new string[VufVisualEventCatalog.Events.Length];
            for (int i = 0; i < viewEvents.Length; i++)
                viewEvents[i] = VufVisualEventCatalog.Events[i].Name;
            viewEventIndex = EditorGUILayout.Popup(
                "Presentation-only view-event label", viewEventIndex, viewEvents);
            EditorGUILayout.BeginHorizontal();
            if (GUILayout.Button("Stage verified PNG as TEMP real SpriteRenderer"))
            {
                try { StageVerifiedSelection(); }
                catch (Exception ex)
                {
                    DestroyOnlyMyStage();
                    result = "STAGE REFUSED: " + ex.Message;
                }
            }
            if (GUILayout.Button("Remove only staged TEMP"))
                DestroyOnlyMyStage();
            EditorGUILayout.EndHorizontal();
            scroll = EditorGUILayout.BeginScrollView(scroll);
            EditorGUILayout.BeginHorizontal();
            EditorGUILayout.BeginVertical();
            DrawPack(left, selected);
            EditorGUILayout.EndVertical();
            EditorGUILayout.BeginVertical();
            DrawPack(right, selected);
            EditorGUILayout.EndVertical();
            EditorGUILayout.EndHorizontal();
            EditorGUILayout.EndScrollView();
        }
    }
}
