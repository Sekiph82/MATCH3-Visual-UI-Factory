// Real VUF M08 TEST_ONLY art source binding for REAL LFXV1 grid cells.
// Each binding is owner-explicit, exact content ID -> exact prototype asset ID.
// Requires M08 receipt + all full SHA source bytes, Editor-only imported copy.
// NO guessed tile match, runtime asset import, rights grant, gameplay mutation.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using UnityEditor;
using UnityEngine;
using UnityEngine.UI;
using Match3.VisualFactory;

namespace Match3.VisualFactory.Editor
{
    internal static class VufCrossFactoryImportedArt
    {
        internal sealed class VerifiedPack
        {
            internal VisualAssetManifest Manifest;
            internal string ImportedFolder;
            internal Dictionary<string, VisualAssetManifest.Asset> ById;
        }

        private static string RawHash(string path)
        {
            var f = new FileInfo(path);
            if (!f.Exists || (f.Attributes & FileAttributes.ReparsePoint) != 0 ||
                f.Length < 1 || f.Length > 16 * 1024 * 1024)
                throw new ArgumentException("missing/symlinked/bounded imported file");
            for (DirectoryInfo dir = f.Directory; dir != null; dir = dir.Parent)
                if ((dir.Attributes & FileAttributes.ReparsePoint) != 0)
                    throw new ArgumentException("imported path under reparse/junction folder");
            using (var stream = new FileStream(path, FileMode.Open,
                FileAccess.Read, FileShare.Read))
            using (var sha = SHA256.Create())
                return BitConverter.ToString(sha.ComputeHash(stream)).Replace("-", "")
                    .ToLowerInvariant();
        }

        internal static VerifiedPack VerifyImportedM08Pack(
            TextAsset json, string expectedProfile)
        {
            if (json == null || String.IsNullOrEmpty(json.text) ||
                !VufVisualEventCatalog.Profiles.Contains(expectedProfile))
                throw new ArgumentException("select real imported TEST_ONLY source");
            string manifestPath = AssetDatabase.GetAssetPath(json);
            const string expectedPrefix = "Assets/Editor/VUF_ReviewImports/";
            if (String.IsNullOrEmpty(manifestPath) ||
                !manifestPath.StartsWith(expectedPrefix, StringComparison.Ordinal) ||
                !manifestPath.EndsWith("/visual_manifest.json", StringComparison.Ordinal) ||
                manifestPath.IndexOf("..", StringComparison.Ordinal) >= 0)
                throw new ArgumentException(
                    "only original M08 Editor-only imported manifest is allowed");
            string folder = manifestPath.Substring(0,
                manifestPath.LastIndexOf('/'));
            string physical = Path.GetFullPath(Path.Combine(
                Directory.GetCurrentDirectory(),
                folder.Replace('/', Path.DirectorySeparatorChar)));
            string root = Path.GetFullPath(Path.Combine(
                Directory.GetCurrentDirectory(), "Assets", "Editor",
                "VUF_ReviewImports")) + Path.DirectorySeparatorChar;
            if (!physical.StartsWith(root, StringComparison.OrdinalIgnoreCase))
                throw new ArgumentException("imported source escaped M08 sandbox");

            string receiptPath = Path.Combine(physical,
                "candidate_pack_receipt.json");
            var receipt = VufCandidatePackImporterWindow.ValidateReceipt(
                File.ReadAllText(receiptPath));
            if (receipt.profile_id != expectedProfile)
                throw new ArgumentException("candidate pack wrong game namespace");
            long sum = 0;
            var checkedHashes = new Dictionary<string, string>(
                StringComparer.Ordinal);
            foreach (var entry in receipt.file_entries)
            {
                if (!VufCandidatePackImporterWindow.SafePath(entry.path))
                    throw new ArgumentException("bad imported receipt path");
                string file = Path.GetFullPath(Path.Combine(physical,
                    entry.path.Replace('/', Path.DirectorySeparatorChar)));
                if (!file.StartsWith(physical+Path.DirectorySeparatorChar,
                        StringComparison.OrdinalIgnoreCase))
                    throw new ArgumentException("imported asset escaped pack");
                string actual = RawHash(file);
                if (actual != entry.sha256)
                    throw new ArgumentException("M08 copy SHA changed: "+entry.path);
                checkedHashes.Add(entry.path, actual);
                sum += new FileInfo(file).Length;
                if (sum > 128L*1024*1024)
                    throw new ArgumentException("candidate art too large");
            }
            if (!checkedHashes.ContainsKey("visual_manifest.json") ||
                RawHash(Path.Combine(physical,"visual_manifest.json")) !=
                    checkedHashes["visual_manifest.json"])
                throw new ArgumentException("manifest changed since M08 receipt");
            VisualAssetManifest parsed;
            string error;
            if (!VisualAssetManifest.TryParsePreview(
                json.text, out parsed, out error))
                throw new ArgumentException("candidate manifest rejected: "+error);
            if (parsed.profile_id != expectedProfile ||
                parsed.engine_sha != "UNPINNED_TEST_ONLY" ||
                parsed.level_factory_sha != "UNPINNED_TEST_ONLY")
                throw new ArgumentException("fake final Engine/LFX art authority");
            VufExternalPackSandboxWindow.ValidateSymbolicPack(parsed);
            var byId = new Dictionary<string,VisualAssetManifest.Asset>(
                StringComparer.Ordinal);
            foreach (var a in parsed.assets)
            {
                if (a.state != "CANDIDATE" || a.rights != "REVIEW_PENDING" ||
                    a.source_receipt != "MATHEMATICAL_PLACEHOLDER_NOT_FINAL" ||
                    !checkedHashes.TryGetValue(a.path, out string digest) ||
                    digest != a.sha256)
                    throw new ArgumentException(
                        "unapproved candidate source rights or PNG SHA mismatch");
                byId.Add(a.asset_id, a);
            }
            return new VerifiedPack {
                Manifest=parsed, ImportedFolder=folder, ById=byId
            };
        }

        internal static void ValidateOwnerMapping(
            VufCrossFactoryContractWindow.Level level,
            VerifiedPack pack, string sourceContentId, string candidateAssetId)
        {
            if (level == null || pack == null ||
                pack.Manifest.profile_id != level.gameProfileId ||
                String.IsNullOrEmpty(sourceContentId) ||
                String.IsNullOrEmpty(candidateAssetId) ||
                !level.cells.Any(c => c.active &&
                    (c.contentId == sourceContentId ||
                     c.obstacleId == sourceContentId ||
                     c.specialId == sourceContentId)) ||
                !pack.ById.TryGetValue(candidateAssetId,out var asset) ||
                !asset.path.StartsWith("sprites/",StringComparison.Ordinal) ||
                !asset.path.EndsWith(".png",StringComparison.Ordinal))
                throw new ArgumentException(
                    "explicit source LFX cell ID to imported M08 sprite required");
        }

        internal static void ApplyExplicitSourceBindings(
            GameObject board, VufCrossFactoryContractWindow.Level level,
            VerifiedPack pack, Dictionary<string,string> selected,
            List<Sprite> ownerSprites)
        {
            if (board == null || level == null || pack == null ||
                selected == null || ownerSprites == null ||
                selected.Count > 1024 ||
                (board.hideFlags & HideFlags.DontSaveInEditor) == 0)
                throw new ArgumentException("not a temporary inspected draft grid");
            var grid = board.transform.Find("Real_LFXV1_Source_Grid");
            if (grid == null) throw new ArgumentException("source uGUI grid changed");
            // Two-phase validation: refuse ANY inconsistent binding before
            // setting even one Image, so partial art state is not accepted.
            foreach (var kv in selected)
                ValidateOwnerMapping(level,pack,kv.Key,kv.Value);
            var cells = level.cells.Where(c => c.layer == 0)
                .OrderBy(c => c.row).ThenBy(c => c.column).ToArray();
            if (grid.childCount != cells.Length)
                throw new ArgumentException("grid is not the original LFX draft");
            var acquired = new Dictionary<string, Sprite>(StringComparer.Ordinal);
            try
            {
                foreach (string id in selected.Values.Distinct())
                {
                    var src=pack.ById[id];
                    string source=pack.ImportedFolder+"/"+src.path;
                    var tex=AssetDatabase.LoadAssetAtPath<Texture2D>(source);
                    if (tex==null || tex.width<=0 || tex.height<=0)
                        throw new ArgumentException("M08 selected sprite cannot load");
                    var sprite=Sprite.Create(tex,
                        new Rect(0,0,tex.width,tex.height),
                        new Vector2(.5f,.5f),100f);
                    sprite.hideFlags=HideFlags.DontSaveInEditor |
                        HideFlags.DontSaveInBuild;
                    acquired[id]=sprite;
                }
                for (int i=0;i<cells.Length;i++)
                {
                    var c=cells[i];
                    var identifier=c.contentId ?? c.obstacleId;
                    var image=grid.GetChild(i).GetComponent<Image>();
                    if (image==null) throw new ArgumentException("source cell Image missing");
                    image.sprite=null;
                    if (identifier!=null && selected.TryGetValue(identifier,out string id))
                    {
                        image.sprite=acquired[id];
                        image.type=Image.Type.Simple;
                        image.preserveAspect=true;
                        image.color=Color.white;
                    }
                }
                ownerSprites.AddRange(acquired.Values);
            }
            catch
            {
                foreach (var sprite in acquired.Values)
                    if (sprite!=null) UnityEngine.Object.DestroyImmediate(sprite);
                throw;
            }
        }
    }
}
