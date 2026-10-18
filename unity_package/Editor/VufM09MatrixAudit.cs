// VUF-M09-001/002/003 | bounded REAL Unity uGUI in-memory matrix.
// Reuses VufScreenCatalog, VufReviewStateCatalog, VufResponsiveGeometry and
// VufTypographyAudit; does NOT invent final screen IDs for other 4 games.
// Results are SYNTHETIC GEOMETRY/TEXT DIAGNOSTICS, not actual rendered
// owner/iOS/Android approval. All generated candidate objects are destroyed.
using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace Match3.VisualFactory.Editor
{
    internal static class VufM09MatrixAudit
    {
        internal static readonly string[] Profiles = {
            "Coral_Rescue", "Garage_Legends", "Dino_Islands",
            "The_Fractured_Realms", "Wonder_Pop"
        };
        internal const int MaxBatch = 32;
        internal sealed class Cell
        {
            internal int Index;
            internal string Profile, ScreenId, ScreenKey, State, Locale, Device;
            internal string FeatureGate, Scope;
            internal int GeometryWarnings, OverflowRisks, ContrastRisks;
            internal int TextUnmeasured, ButtonCount;
            internal bool ScreenshotCaptured, OwnerApproved, DeviceVerified;
            internal bool ArtRightsVerified, ReleaseAllowed;
            internal readonly List<string> Warnings = new List<string>();
        }

        internal static int MatrixSize(int count)
        {
            if (count != 28)
                throw new ArgumentException("only source-pinned 28 Coral draft IDs");
            return checked(Profiles.Length * count *
                VufReviewStateCatalog.States.Length *
                VufReviewStateCatalog.Locales.Length *
                VufResponsiveGeometry.Presets.Length);
        }

        internal static Cell Inspect(int index)
        {
            var screens = VufScreenCatalog.LoadScreens();
            int full = MatrixSize(screens.Length);
            if (index < 0 || index >= full)
                throw new ArgumentOutOfRangeException(nameof(index));
            int cursor = index;
            int device = cursor % VufResponsiveGeometry.Presets.Length;
            cursor /= VufResponsiveGeometry.Presets.Length;
            int locale = cursor % VufReviewStateCatalog.Locales.Length;
            cursor /= VufReviewStateCatalog.Locales.Length;
            int state = cursor % VufReviewStateCatalog.States.Length;
            cursor /= VufReviewStateCatalog.States.Length;
            int screen = cursor % screens.Length;
            int profile = cursor / screens.Length;
            var source = screens[screen];
            var style = VufScreenCatalog.LoadStyle(Profiles[profile]);
            var candidate = VufScreenShellBuilderWindow.BuildCandidateHierarchy(
                source, style, true);
            try
            {
                var marker = candidate.GetComponent<VufCandidateScreenMarker>();
                if (marker == null ||
                    marker.CandidateStatus != "CANDIDATE_NOT_APPROVED" ||
                    marker.FeatureGate != source.feature_gate)
                    throw new InvalidOperationException("candidate policy changed");
                VufReviewStateCatalog.Apply(candidate, source,
                    VufReviewStateCatalog.States[state],
                    VufReviewStateCatalog.Locales[locale]);
                var geom = VufResponsiveGeometry.Analyze(candidate,
                    VufResponsiveGeometry.Presets[device]);
                var type = VufTypographyAudit.Analyze(candidate,
                    VufResponsiveGeometry.Presets[device]);
                var row = new Cell {
                    Index = index,
                    Profile = Profiles[profile], ScreenId = source.id,
                    ScreenKey = source.key, State = VufReviewStateCatalog.States[state],
                    Locale = VufReviewStateCatalog.Locales[locale],
                    Device = VufResponsiveGeometry.Presets[device].Name,
                    FeatureGate = source.feature_gate,
                    Scope = profile == 0 ?
                        "CORAL_DRAFT_SCREEN_NOT_AVAILABLE_IN_DEMO" :
                        "N_A_FOREIGN_GAME_USING_CORAL_DRAFT_CONTRACT",
                    GeometryWarnings = geom.Warnings.Count,
                    OverflowRisks = type.OverflowCount,
                    ContrastRisks = type.LowContrastCount,
                    TextUnmeasured = type.UnmeasuredCount,
                    ButtonCount = geom.ButtonCount
                };
                row.Warnings.AddRange(geom.Warnings);
                row.Warnings.AddRange(type.Warnings);
                if (source.feature_gate ==
                    "OFF_UNTIL_ENGINE_POLICY_CONFIRMED")
                    row.Warnings.Add("POLICY_OFF_NO_GAME_ACTION");
                if (profile != 0)
                    row.Warnings.Add(
                        "NO_OWN_GAME_SCREEN_TAXONOMY: Coral shell is style preview");
                return row;
            }
            finally { UnityEngine.Object.DestroyImmediate(candidate); }
        }

        internal static List<Cell> InspectBatch(int start, int count)
        {
            int total = MatrixSize(VufScreenCatalog.LoadScreens().Length);
            if (start < 0 || start >= total ||
                count < 1 || count > MaxBatch ||
                start + count > total)
                throw new ArgumentOutOfRangeException("bounded matrix batch");
            var rows = new List<Cell>();
            for (int i = 0; i < count; ++i)
                rows.Add(Inspect(start + i));
            return rows;
        }

        internal static bool MechanicallyClean(Cell row) =>
            row != null && row.GeometryWarnings == 0 &&
            row.OverflowRisks == 0 && row.ContrastRisks == 0 &&
            row.TextUnmeasured == 0 &&
            row.FeatureGate != "OFF_UNTIL_ENGINE_POLICY_CONFIRMED" &&
            row.Scope == "CORAL_DRAFT_SCREEN_NOT_AVAILABLE_IN_DEMO";

        internal static bool HumanApproved(Cell row) => false;
        internal static bool RealDeviceAccepted(Cell row) => false;
    }
}
