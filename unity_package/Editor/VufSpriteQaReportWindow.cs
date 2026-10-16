// VF-09 offline, read-only PNG pixel-health report inspector.
// Parsing a report is not art approval or actual Unity render/device QA.
using System;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;

namespace Match3.VisualFactory.Editor
{
    public sealed class VufSpriteQaReportWindow : EditorWindow
    {
        [Serializable]
        internal sealed class SpriteFinding
        {
            public string filename;
            public string source_sha256_recorded;
            public int[] dimensions;
            public int[] visible_bbox_top_left;
            public int alpha_coverage_basis_points;
            public int visible_pixels;
            public int partial_alpha_visible_pixels;
            public int edge_visible_pixels;
            public int transparent_colored_pixels;
            public int transparent_black_adjacent_visible;
            public int distinct_visible_rgb_capped;
            public string[] warnings;
        }

        [Serializable]
        internal sealed class ContrastFinding
        {
            public string pair;
            public float ratio;
            public float advisory_minimum;
            public bool review;
        }

        [Serializable]
        internal sealed class PaletteFinding
        {
            public string profile_id;
            public string stage;
            public ContrastFinding[] contrast_checks;
        }

        [Serializable]
        internal sealed class Report
        {
            public int schema_version;
            public string stage;
            public string generator;
            public int file_count;
            public int total_source_bytes;
            public int warning_count;
            public bool source_rights_verified;
            public SpriteFinding[] sprites;
            public PaletteFinding palette_review;
        }

        private TextAsset candidate;
        private Report report;
        private string error;
        private int selected;
        private Vector2 scroll;

        [MenuItem("Tools/MATCH3/Sprite Pixel Health QA")]
        public static void Open()
        {
            var window = GetWindow<VufSpriteQaReportWindow>("VF-09 Sprite Pixel QA");
            window.minSize = new Vector2(590, 520);
            window.Show();
        }

        private void OnGUI()
        {
            EditorGUILayout.LabelField("VF-09 | Offline Sprite Pixel-Health Report",
                EditorStyles.boldLabel);
            EditorGUILayout.HelpBox(
                "Import a COPY of an external report from visual_qa.py as a TextAsset. " +
                "This is READ-ONLY and heuristic. It does not judge actual image style, " +
                "content rights, game performance, original approvals or mobile render.",
                MessageType.Warning);
            EditorGUI.BeginChangeCheck();
            candidate = (TextAsset)EditorGUILayout.ObjectField(
                "Imported VF09 JSON", candidate, typeof(TextAsset), false);
            if (EditorGUI.EndChangeCheck())
                ReadReport();
            if (GUILayout.Button("Revalidate selected read-only report"))
                ReadReport();
            if (!String.IsNullOrEmpty(error))
                EditorGUILayout.HelpBox(error, MessageType.Error);
            if (report == null) return;

            EditorGUILayout.LabelField("Owner/art approval", "NOT APPROVED");
            EditorGUILayout.LabelField("Source original/rights", "NOT VERIFIED");
            EditorGUILayout.LabelField("Sprites", report.file_count.ToString());
            EditorGUILayout.LabelField("Heuristic warnings", report.warning_count.ToString());
            string[] names = new string[report.sprites.Length];
            for (int i = 0; i < names.Length; ++i)
                names[i] = report.sprites[i].filename;
            selected = EditorGUILayout.Popup("Sprite", selected, names);
            SpriteFinding item = report.sprites[selected];

            scroll = EditorGUILayout.BeginScrollView(scroll);
            EditorGUILayout.LabelField("Original SHA-256 (recorded, not attested)");
            EditorGUILayout.SelectableLabel(item.source_sha256_recorded,
                EditorStyles.textField, GUILayout.Height(20));
            EditorGUILayout.LabelField("Image", item.dimensions[0] + " × " + item.dimensions[1]);
            EditorGUILayout.LabelField("Alpha coverage", (item.alpha_coverage_basis_points / 100f).ToString("F2") + "%");
            EditorGUILayout.LabelField("Visible pixels", item.visible_pixels.ToString());
            EditorGUILayout.LabelField("Edge pixels", item.edge_visible_pixels.ToString());
            EditorGUILayout.LabelField("Partial alpha pixels", item.partial_alpha_visible_pixels.ToString());
            EditorGUILayout.LabelField("Black matte near visible sprite",
                item.transparent_black_adjacent_visible.ToString());
            if (item.visible_bbox_top_left != null)
            {
                int[] box = item.visible_bbox_top_left;
                EditorGUILayout.LabelField("Visible top-left bbox",
                    box[0] + "," + box[1] + "  " + box[2] + "×" + box[3]);
            }
            else
                EditorGUILayout.HelpBox("Fully transparent or below alpha cutoff",
                    MessageType.Warning);
            foreach (string warning in item.warnings)
                EditorGUILayout.HelpBox(warning, MessageType.Warning);

            if (report.palette_review != null)
            {
                EditorGUILayout.LabelField("DRAFT palette: " +
                    report.palette_review.profile_id, EditorStyles.boldLabel);
                foreach (ContrastFinding entry in report.palette_review.contrast_checks)
                {
                    string line = entry.pair + ": " + entry.ratio.ToString("F3") +
                        " : 1 (advisory " + entry.advisory_minimum + ":1)";
                    EditorGUILayout.HelpBox(line,
                        entry.review ? MessageType.Warning : MessageType.Info);
                }
            }
            EditorGUILayout.HelpBox(
                "Original/licensed art source, Unity rendered preview, on-device UI, " +
                "font layout and final aesthetic approval still require human review.",
                MessageType.Info);
            EditorGUILayout.EndScrollView();
        }

        private void ReadReport()
        {
            report = null;
            error = null;
            selected = 0;
            if (candidate == null) return;
            try
            {
                report = ParseReport(candidate.text);
            }
            catch (Exception ex)
            {
                error = "Untrusted/incomplete VF09 report rejected: " + ex.Message;
            }
        }

        internal static Report ParseReport(string source)
        {
            if (String.IsNullOrEmpty(source) || source.Length > 800000)
                throw new ArgumentException("missing or oversized report text");
            var result = JsonUtility.FromJson<Report>(source);
            if (result == null || result.schema_version != 1 ||
                result.stage != "REVIEW_REQUIRED_NOT_OWNER_APPROVED" ||
                result.generator != "VF09_PIXEL_HEALTH_V01" ||
                result.source_rights_verified ||
                result.sprites == null || result.sprites.Length < 1 ||
                result.sprites.Length > 32 ||
                result.file_count != result.sprites.Length ||
                result.total_source_bytes < 1 || result.total_source_bytes > 64 * 1024 * 1024 ||
                result.warning_count < 0)
                throw new ArgumentException("invalid report contract or false approval");
            int warnings = 0;
            var names = new HashSet<string>(StringComparer.Ordinal);
            var allowedWarnings = new HashSet<string>(StringComparer.Ordinal) {
                "EMPTY_ALPHA", "CANVAS_BOUNDARY_TOUCH", "SPARSE_VISIBLE_CANVAS",
                "LARGE_TEXTURE_HEURISTIC", "POSSIBLE_BLACK_MATTE_FRINGE"
            };
            foreach (SpriteFinding item in result.sprites)
            {
                long pixels = item == null || item.dimensions == null ||
                    item.dimensions.Length != 2 ? 0L :
                    (long)item.dimensions[0] * item.dimensions[1];
                if (item == null || String.IsNullOrEmpty(item.filename) ||
                    item.filename.Contains("/") || item.filename.Contains("\\") ||
                    !item.filename.EndsWith(".png", StringComparison.OrdinalIgnoreCase) ||
                    !names.Add(item.filename) ||
                    item.source_sha256_recorded == null ||
                    item.source_sha256_recorded.Length != 64 ||
                    item.dimensions == null || item.dimensions.Length != 2 ||
                    item.dimensions[0] < 1 || item.dimensions[1] < 1 ||
                    item.warnings == null || item.alpha_coverage_basis_points < 0 ||
                    item.alpha_coverage_basis_points > 10000 ||
                    item.visible_pixels < 0 || item.visible_pixels > pixels ||
                    item.alpha_coverage_basis_points !=
                        (int)((long)item.visible_pixels * 10000 / pixels) ||
                    item.partial_alpha_visible_pixels < 0 ||
                    item.partial_alpha_visible_pixels > item.visible_pixels ||
                    item.edge_visible_pixels < 0 ||
                    item.edge_visible_pixels > item.visible_pixels ||
                    item.transparent_colored_pixels < 0 ||
                    item.transparent_colored_pixels > pixels - item.visible_pixels ||
                    item.transparent_black_adjacent_visible < 0 ||
                    item.transparent_black_adjacent_visible > pixels - item.visible_pixels ||
                    item.distinct_visible_rgb_capped < 0 ||
                    item.distinct_visible_rgb_capped > Math.Min(257, item.visible_pixels) ||
                    (item.visible_pixels == 0) != (item.visible_bbox_top_left == null))
                    throw new ArgumentException("invalid per-sprite pixel metrics");
                foreach (char c in item.source_sha256_recorded)
                    if (!(c >= '0' && c <= '9') && !(c >= 'a' && c <= 'f'))
                        throw new ArgumentException("invalid recorded SHA-256");
                if (item.visible_bbox_top_left != null)
                {
                    int[] b = item.visible_bbox_top_left;
                    if (b.Length != 4 || b[0] < 0 || b[1] < 0 || b[2] < 1 ||
                        b[3] < 1 || (long)b[0] + b[2] > item.dimensions[0] ||
                        (long)b[1] + b[3] > item.dimensions[1])
                        throw new ArgumentException("invalid sprite bounding box");
                }
                foreach (string warning in item.warnings)
                {
                    if (!allowedWarnings.Contains(warning))
                        throw new ArgumentException("unknown sprite warning");
                    warnings++;
                }
            }
            if (result.palette_review != null)
            {
                var allowedProfiles = new HashSet<string>(StringComparer.Ordinal) {
                    "Coral_Rescue", "Garage_Legends", "Dino_Islands",
                    "The_Fractured_Realms", "Wonder_Pop"
                };
                if (!allowedProfiles.Contains(result.palette_review.profile_id) ||
                    result.palette_review.stage != "DRAFT_NOT_OWNER_APPROVED" ||
                    result.palette_review.contrast_checks == null ||
                    result.palette_review.contrast_checks.Length != 3)
                    throw new ArgumentException("unexpected palette profile contract");
                var expectedMinimums = new Dictionary<string, float>(StringComparer.Ordinal) {
                    {"text_on_surface", 4.5f}, {"cta_label_on_cta", 4.5f},
                    {"accent_on_background", 3f}
                };
                var seenPairs = new HashSet<string>(StringComparer.Ordinal);
                foreach (ContrastFinding contrast in result.palette_review.contrast_checks)
                {
                    if (contrast == null || String.IsNullOrEmpty(contrast.pair) ||
                        !expectedMinimums.ContainsKey(contrast.pair) ||
                        !seenPairs.Add(contrast.pair) ||
                        Single.IsNaN(contrast.ratio) || Single.IsInfinity(contrast.ratio) ||
                        Single.IsNaN(contrast.advisory_minimum) ||
                        Single.IsInfinity(contrast.advisory_minimum) ||
                        contrast.ratio < 1f || contrast.ratio > 21.001f ||
                        Math.Abs(contrast.advisory_minimum - expectedMinimums[contrast.pair]) > .0001f)
                        throw new ArgumentException("invalid palette diagnostic");
                    float tolerance = .00051f; // Python exporter rounds ratios to 3 decimals.
                    if ((!contrast.review && contrast.ratio + tolerance < contrast.advisory_minimum) ||
                        (contrast.review && contrast.ratio - tolerance >= contrast.advisory_minimum))
                        throw new ArgumentException("palette review flag contradicts contrast ratio");
                    warnings += contrast.review ? 1 : 0;
                }
            }
            if (warnings != result.warning_count)
                throw new ArgumentException("advisory warning count mismatch");
            return result;
        }
    }
}
