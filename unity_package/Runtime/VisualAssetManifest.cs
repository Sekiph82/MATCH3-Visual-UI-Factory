using System;
using UnityEngine;

namespace Match3.VisualFactory
{
    // Read-only data contract, not gameplay or owner-approval authority.
    [Serializable]
    public sealed class VisualAssetManifest
    {
        public int schema_version;
        public string profile_id;
        public string theme_version;
        public string engine_sha;
        public string level_factory_sha;
        public string stage;
        public Asset[] assets;

        [Serializable]
        public sealed class Asset
        {
            public string asset_id;
            public string path;
            public string sha256;
            public string state;
            public string rights;
            public string source_receipt;
        }

        public static bool TryParsePreview(string json, out VisualAssetManifest result, out string error)
        {
            result = null;
            error = "Unrecognized or unsafe visual pack";
            if (string.IsNullOrWhiteSpace(json) || json.Length > 2 * 1024 * 1024)
                return false;

            try
            {
                VisualAssetManifest parsed = JsonUtility.FromJson<VisualAssetManifest>(json);
                if (parsed == null || parsed.schema_version != 1 || parsed.stage != "TEST_ONLY")
                    return false;
                if (!KnownProfile(parsed.profile_id) || parsed.assets == null)
                    return false;
                if (parsed.assets.Length > 20000)
                    return false;
                for (int i = 0; i < parsed.assets.Length; ++i)
                {
                    Asset a = parsed.assets[i];
                    if (a == null || string.IsNullOrEmpty(a.asset_id) ||
                        !a.asset_id.StartsWith(parsed.profile_id + ".", StringComparison.Ordinal) ||
                        string.IsNullOrEmpty(a.sha256) || a.sha256.Length != 64 ||
                        string.IsNullOrEmpty(a.path) || a.path.StartsWith("/", StringComparison.Ordinal) ||
                        a.path.Contains("..") || a.path.Contains("\\") || a.path.Contains(":"))
                        return false;
                }
                result = parsed;
                error = null;
                return true;
            }
            catch (Exception)
            {
                // Invalid imported JSON is a non-fatal, fail-closed preview error.
                return false;
            }
        }

        private static bool KnownProfile(string profile)
        {
            return profile == "Coral_Rescue" ||
                   profile == "Garage_Legends" ||
                   profile == "Dino_Islands" ||
                   profile == "The_Fractured_Realms" ||
                   profile == "Wonder_Pop";
        }
    }
}
