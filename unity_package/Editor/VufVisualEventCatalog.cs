// VUF-M07-006/009/013: owner-review-only 5-profile × 14-event catalog.
// Mirrors Python factory/vfx_builder/view_event_timeline.py symbolic metadata.
// This is a closed presentation key allowlist, NOT an Engine event adapter.
// Source rights, actual rendered art, callbacks and owner approval: OPEN.
using System;
using System.Collections.Generic;

namespace Match3.VisualFactory.Editor
{
    internal static class VufVisualEventCatalog
    {
        internal sealed class Entry
        {
            internal readonly string Name;
            internal readonly string Channel;
            internal readonly int Priority;
            internal readonly int DurationMs;
            internal readonly string Preset;
            internal Entry(string name, string channel, int priority,
                int durationMs, string preset)
            {
                Name = name; Channel = channel; Priority = priority;
                DurationMs = durationMs; Preset = preset;
            }
        }

        internal static readonly string[] Profiles = {
            "Coral_Rescue", "Garage_Legends", "Dino_Islands",
            "The_Fractured_Realms", "Wonder_Pop"
        };
        internal static readonly Entry[] Events = {
            new Entry("ui_open", "ui", 20, 220, null),
            new Entry("ui_close", "ui", 30, 180, null),
            new Entry("tile_spawn", "board_visual", 10, 320, "SoftDrift"),
            new Entry("tile_match", "board_visual", 45, 420, "MatchBurst"),
            new Entry("special_trigger", "board_visual", 60, 650, "StarSparkle"),
            new Entry("combo_chain", "board_visual", 70, 850, "MatchBurst"),
            new Entry("obstacle_hit", "board_visual", 40, 280, "SoftDrift"),
            new Entry("booster_activate", "board_visual", 65, 540, "StarSparkle"),
            new Entry("level_win", "results_visual", 100, 1180, "StarSparkle"),
            new Entry("level_fail", "results_visual", 100, 870, "SoftDrift"),
            new Entry("reward_claim", "rewards_visual", 90, 920, "StarSparkle"),
            new Entry("character_idle", "character_visual", 1, 1500, "BubbleRise"),
            new Entry("character_celebrate", "character_visual", 85, 1100, "StarSparkle"),
            new Entry("region_reveal", "environment_visual", 75, 1250, "PortalPulse")
        };

        private static readonly HashSet<string> ProfilesSet =
            new HashSet<string>(Profiles, StringComparer.Ordinal);
        // Verified source-pinned Engine SpecialActivationKind ordinals, NOT
        // final Engine/LFX release parity. Exact Python R50 keys and order.
        internal static readonly string[] EngineSpecials = {
            "HorizontalLine", "VerticalLine", "Area", "Color", "Targeted"
        };
        private static readonly string[] SpecialKeys = {
            "horizontal_line", "vertical_line", "area", "color", "targeted"
        };
        private static int SpecialIndex(string kind)
        {
            for (int i = 0; i < EngineSpecials.Length; ++i)
                if (String.Equals(EngineSpecials[i], kind, StringComparison.Ordinal))
                    return i;
            throw new ArgumentException("unknown source-pinned Engine special name");
        }

        internal static string ViewEventKey(string profile, string eventName,
            string firstSpecial, string secondSpecial = null)
        {
            string baseKey = EventKey(profile, eventName);
            if (eventName == "special_trigger")
            {
                if (secondSpecial != null)
                    throw new ArgumentException("one special only");
                return baseKey + "." + SpecialKeys[SpecialIndex(firstSpecial)];
            }
            if (eventName == "combo_chain")
            {
                int first = SpecialIndex(firstSpecial);
                int second = SpecialIndex(secondSpecial);
                return baseKey + "." + SpecialKeys[Math.Min(first, second)] +
                       "__" + SpecialKeys[Math.Max(first, second)];
            }
            if (firstSpecial != null || secondSpecial != null)
                throw new ArgumentException("non-special events cannot carry special IDs");
            return baseKey;
        }

        internal static Entry Get(string eventName)
        {
            foreach (Entry row in Events)
                if (String.Equals(row.Name, eventName, StringComparison.Ordinal))
                    return row;
            throw new ArgumentException("Unknown view-only event");
        }

        internal static string EventKey(string profile, string eventName)
        {
            if (!ProfilesSet.Contains(profile)) throw new ArgumentException(
                "Unknown or unapproved game namespace");
            Get(eventName);
            return profile.ToLowerInvariant() + ".anim." + eventName;
        }

        internal static string AudioCueLog(string profile, string eventName, bool mute)
        {
            EventKey(profile, eventName);
            return mute ? "MUTED_NO_AUDIO" :
                profile.ToLowerInvariant() + ".audio." + eventName +
                " (LOG ONLY, AUDIO NOT PLAYED)";
        }

        internal static string HapticCueLog(string profile, string eventName, bool mute)
        {
            EventKey(profile, eventName);
            return mute ? "MUTED_NO_HAPTIC" :
                profile.ToLowerInvariant() + ".haptic." + eventName +
                " (LOG ONLY, HAPTIC NOT PLAYED)";
        }

        internal static bool ProductionEventParityProven => false;
        internal static bool MayMutateGameplay => false;
        internal static bool ArtRightsOwnerApproved => false;
    }
}
