// VF-07 single-source-draft screen and style catalogs mirrored from root schemas.
// Separate root-vs-package byte parity is enforced by Python source checks.
using System;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;

namespace Match3.VisualFactory.Editor
{
    internal static class VufScreenCatalog
    {
        private const string Root = "Packages/com.match3.visual-factory/Editor/Resources/";
        private static readonly string[] KnownProfiles = {
            "Coral_Rescue", "Garage_Legends", "Dino_Islands",
            "The_Fractured_Realms", "Wonder_Pop"
        };

        [Serializable]
        internal sealed class ScreenInfo
        {
            public string id;
            public string key;
            public string kind;
            public bool runtime_ui_required;
            public bool available_in_demo;
            public string feature_gate;
        }

        [Serializable]
        private sealed class ScreenDocument
        {
            public int schema_version;
            public string status;
            public string profile_id;
            public ScreenInfo[] screens;
        }

        [Serializable]
        internal sealed class Palette
        {
            public string background;
            public string surface;
            public string accent;
            public string cta;
            public string cta_label;
            public string text;
        }

        [Serializable]
        internal sealed class StyleInfo
        {
            public string id;
            public Palette palettes;
        }

        [Serializable]
        private sealed class StyleDocument
        {
            public int schema_version;
            public string status;
            public StyleInfo[] profiles;
        }

        internal static ScreenInfo[] LoadScreens()
        {
            TextAsset resource = AssetDatabase.LoadAssetAtPath<TextAsset>(
                Root + "coral-experiences.v1.json");
            if (resource == null)
                throw new InvalidOperationException("Coral draft catalog missing in Unity package");
            ScreenDocument doc = JsonUtility.FromJson<ScreenDocument>(resource.text);
            if (doc == null || doc.schema_version != 1 ||
                doc.status != "CONTRACT_DRAFT_NOT_IMPLEMENTED" ||
                doc.profile_id != "Coral_Rescue" ||
                doc.screens == null || doc.screens.Length != 28)
                throw new InvalidOperationException("Coral catalog schema/owner stage changed");
            HashSet<string> keys = new HashSet<string>(StringComparer.Ordinal);
            for (int i = 0; i < 28; ++i)
            {
                ScreenInfo screen = doc.screens[i];
                string expectedId = "COR-" + (i + 1).ToString("D2");
                if (screen == null || screen.id != expectedId ||
                    String.IsNullOrEmpty(screen.key) || !keys.Add(screen.key) ||
                    !screen.runtime_ui_required || screen.available_in_demo ||
                    (screen.kind != "page" && screen.kind != "modal" &&
                     screen.kind != "ceremony" && screen.kind != "overlay" &&
                     screen.kind != "mode" && screen.kind != "playable") ||
                    (screen.feature_gate != "REQUIRES_ENGINE_OR_GAME_BINDING" &&
                     screen.feature_gate != "OFF_UNTIL_ENGINE_POLICY_CONFIRMED"))
                    throw new InvalidOperationException("Invalid Coral screen contract: " + expectedId);
            }
            if (doc.screens[26].key != "home" || doc.screens[27].key != "gameplay_hud")
                throw new InvalidOperationException("Home and Gameplay/HUD contract missing");
            return doc.screens;
        }

        internal static StyleInfo LoadStyle(string profileId)
        {
            TextAsset resource = AssetDatabase.LoadAssetAtPath<TextAsset>(
                Root + "style_profiles.v1.json");
            if (resource == null)
                throw new InvalidOperationException("Style Bible draft missing from Unity package");
            StyleDocument doc = JsonUtility.FromJson<StyleDocument>(resource.text);
            if (doc == null || doc.schema_version != 1 ||
                doc.status != "DRAFT_NOT_OWNER_APPROVED" ||
                doc.profiles == null || doc.profiles.Length != 5)
                throw new InvalidOperationException("Invalid five-game draft Style Bible");
            var known = new HashSet<string>(KnownProfiles, StringComparer.Ordinal);
            StyleInfo selected = null;
            foreach (StyleInfo style in doc.profiles)
            {
                if (style == null || style.palettes == null || !known.Remove(style.id))
                    throw new InvalidOperationException("Unknown/duplicate game Style Bible");
                if (style.id == profileId) selected = style;
            }
            if (known.Count != 0 || selected == null)
                throw new InvalidOperationException("Incomplete game Style Bible set");
            return selected;
        }

        internal static Color ParseColor(string html, string field)
        {
            Color color;
            if (String.IsNullOrEmpty(html) ||
                !html.StartsWith("#", StringComparison.Ordinal) ||
                !ColorUtility.TryParseHtmlString(html, out color))
                throw new InvalidOperationException("Style color invalid: " + field);
            return color;
        }

        internal static string DisplayName(ScreenInfo screen)
        {
            if (screen == null) return "Unknown";
            string[] pieces = screen.key.Split('_');
            for (int i = 0; i < pieces.Length; ++i)
                if (pieces[i].Length > 0)
                    pieces[i] = Char.ToUpperInvariant(pieces[i][0]) + pieces[i].Substring(1);
            return String.Join(" ", pieces);
        }
    }
}
