// VUF-M09-001/002/003/004/006/012: OWNER-CLICKABLE VISUAL QA DESKTOP.
// Reuses 28 Coral draft screens + five UNAPPROVED style skins, the M07 real
// Sprite/VFX manual Studio, M06 scene/parallax Editor and M08 UI inspector.
// Generates real Unity uGUI pixels in a temporary RenderTexture via
// VufM09RenderCapture, exports receipts/synthetic render ONLY after explicit
// user command. NEVER claims Android/iOS screenshot, final game support,
// licence, accessibility certification or owner artistic acceptance.
using System;
using System.Collections.Generic;
using System.IO;
using System.Security.Cryptography;
using UnityEditor;
using UnityEngine;
using UnityEngine.UI;

namespace Match3.VisualFactory.Editor
{
    public sealed class VufM09OwnerVisualQaWindow : EditorWindow
    {
        [Serializable]
        internal sealed class ReviewReceipt
        {
            public string stage = "OWNER_REVIEW_CANDIDATE_NOT_APPROVED";
            public string profile_id, screen_id, state_id, locale, synthetic_device;
            public string visual_event, event_trace, screenshot_sha256;
            public string original_rights_receipt = "NOT_PROVIDED";
            public int level_mock, seed_mock, width, height, matrix_start;
            public int matrix_count, geometry_warnings, typography_overflows;
            public int contrast_risks, text_unmeasured, simulated_touch_count;
            public double review_cpu_ms;
            public bool real_unity_render_observed, actual_device_verified;
            public bool production_engine_lfx_bound, signed_art_approved;
            public bool human_aesthetic_approved, release_allowed;
            public string missing_acceptance =
                "Owner visual approval, source licence, real phones/GPU, " +
                "final Engine/LFX game parity and all independent device evidence";
        }
        private static readonly string[] Speeds =
            { "0.25x", "0.5x", "1x", "2x" };
        private VufScreenCatalog.ScreenInfo[] screens;
        private int profile, screen = 26, state, locale, device, speed = 2;
        private int eventIndex, levelMock = 1, seedMock = 7, frame;
        private bool reducedMotion = true, showOverlay = true;
        private GameObject candidate;
        private Button mockTapButton;
        private VufUiTween tween;
        private Texture2D captured, comparison;
        private byte[] capturedPng;
        private readonly List<string> trace = new List<string>();
        private VufM09MatrixAudit.Cell matrixCell;
        private int batchStart, batchCount = 8;
        private List<VufM09MatrixAudit.Cell> lastBatch;
        private double renderCpuMs;
        private int fakeTaps;
        private string message = "Unapproved. Choose a draft screen then Build.";
        private Vector2 scroll;
        private static readonly string[] Events = EventNames();

        [MenuItem("Tools/MATCH3/M09 Owner Visual QA Studio")]
        public static void Open()
        {
            var window = GetWindow<VufM09OwnerVisualQaWindow>("M09 Visual QA");
            window.minSize = new Vector2(870, 760);
            window.Show();
        }

        private static string[] EventNames()
        {
            var arr = new string[VufVisualEventCatalog.Events.Length];
            for (int i = 0; i < arr.Length; i++)
                arr[i] = VufVisualEventCatalog.Events[i].Name;
            return arr;
        }

        private void OnEnable()
        {
            try { screens = VufScreenCatalog.LoadScreens(); }
            catch (Exception ex) { message = "SCREEN CONTRACT BLOCKED: " + ex.Message; }
        }
        private void OnDisable() { DisposeOnlyMine(); }

        private static void Temporary(GameObject root)
        {
            foreach (Transform child in root.GetComponentsInChildren<Transform>(true))
                child.gameObject.hideFlags =
                    HideFlags.DontSaveInEditor | HideFlags.DontSaveInBuild;
        }

        private void ClearCaptured()
        {
            if (captured != null) DestroyImmediate(captured);
            captured = null; capturedPng = null;
        }

        private void DisposeOnlyMine()
        {
            ClearCaptured();
            if (comparison != null) DestroyImmediate(comparison);
            comparison = null;
            if (candidate != null) DestroyImmediate(candidate);
            candidate = null; mockTapButton = null; tween = null;
            fakeTaps = 0;
        }

        private void AddTrace(string description)
        {
            trace.Add("STEP " + trace.Count.ToString("D3") +
                " / profile=" + VufM09MatrixAudit.Profiles[profile] +
                " / " + screens[screen].id + " / " +
                VufReviewStateCatalog.States[state] + " / " +
                VufReviewStateCatalog.Locales[locale] + " / " +
                description + " / NO_ENGINE_EVENTS");
            if (trace.Count > 128) trace.RemoveAt(0);
        }

        private void Build()
        {
            DisposeOnlyMine();
            trace.Clear();
            if (screens == null) return;
            GameObject built = null;
            try
            {
                var selected = screens[screen];
                var style = VufScreenCatalog.LoadStyle(
                    VufM09MatrixAudit.Profiles[profile]);
                built = VufScreenShellBuilderWindow.BuildCandidateHierarchy(
                    selected, style, true);
                VufReviewStateCatalog.Apply(built, selected,
                    VufReviewStateCatalog.States[state],
                    VufReviewStateCatalog.Locales[locale]);
                Temporary(built);
                candidate = built;
                var shield = candidate.transform.Find(
                    "SafeArea_ReviewOnly/VUF_28ScreenInputShield");
                var graphic = shield == null ? null : shield.GetComponent<Graphic>();
                Button[] buttons = candidate.GetComponentsInChildren<Button>(true);
                if (buttons.Length != 1 || graphic == null)
                    throw new InvalidOperationException("button/shield structural drift");
                if (selected.feature_gate !=
                    "OFF_UNTIL_ENGINE_POLICY_CONFIRMED")
                {
                    if (VufInteractiveUiReviewWindow.EnableOnlyPreviewButton(
                        candidate, buttons[0], () => {
                            fakeTaps++;
                            AddTrace("LOCAL ONLY test button press " + fakeTaps);
                        }))
                    {
                        graphic.raycastTarget = false;
                        mockTapButton = buttons[0];
                    }
                }
                tween = candidate.GetComponentInChildren<VufUiTween>(true);
                if (tween != null) tween.SetReducedMotion(reducedMotion);
                AuditCurrent();
                AddTrace("CANDIDATE BUILT: style preview, NOT released screen");
                message = profile == 0 ?
                    "Coral contract candidate only, ALL gameplay actions unbound." :
                    "N/A: reused CORAL screen taxonomy under another style skin; " +
                    "independent game screen NOT DEFINED. Never approve this as final.";
                Selection.activeGameObject = candidate;
            }
            catch (Exception ex)
            {
                if (built != null) DestroyImmediate(built);
                candidate = null; mockTapButton = null;
                message = "CANDIDATE REJECTED: " + ex.Message;
            }
        }

        private void AuditCurrent()
        {
            if (candidate == null) return;
            var geometry = VufResponsiveGeometry.Analyze(candidate,
                VufResponsiveGeometry.Presets[device]);
            var typography = VufTypographyAudit.Analyze(candidate,
                VufResponsiveGeometry.Presets[device]);
            matrixCell = new VufM09MatrixAudit.Cell {
                Profile = VufM09MatrixAudit.Profiles[profile],
                ScreenId = screens[screen].id, ScreenKey = screens[screen].key,
                State = VufReviewStateCatalog.States[state],
                Locale = VufReviewStateCatalog.Locales[locale],
                Device = VufResponsiveGeometry.Presets[device].Name,
                FeatureGate = screens[screen].feature_gate,
                Scope = profile == 0 ?
                    "CORAL_DRAFT_SCREEN_NOT_AVAILABLE_IN_DEMO" :
                    "N_A_FOREIGN_GAME_USING_CORAL_DRAFT_CONTRACT",
                GeometryWarnings = geometry.Warnings.Count,
                OverflowRisks = typography.OverflowCount,
                ContrastRisks = typography.LowContrastCount,
                TextUnmeasured = typography.UnmeasuredCount,
                ButtonCount = geometry.ButtonCount
            };
            matrixCell.Warnings.AddRange(geometry.Warnings);
            matrixCell.Warnings.AddRange(typography.Warnings);
        }

        private void StepTween()
        {
            if (tween == null)
            {
                message = "N/A: this candidate screen has no CanvasGroup tween.";
                return;
            }
            tween.SetReducedMotion(reducedMotion);
            if (!tween.IsAnimating) tween.Hide();
            // Force manual owner stepping only, never Editor autoplay.
            tween.Advance(speed == 0 ? .05f : speed == 1 ?
                .10f : speed == 2 ? .20f : .40f);
            frame++;
            AddTrace("TWEEN STEP " + frame + " / speed=" + Speeds[speed] +
                " / reducedMotion=" + reducedMotion);
            ClearCaptured();
        }

        private void Render()
        {
            ClearCaptured();
            if (candidate == null)
            {
                message = "Build disposable candidate first.";
                return;
            }
            var profileDevice = VufResponsiveGeometry.Presets[device];
            double start = EditorApplication.timeSinceStartup;
            int w = Mathf.Clamp(profileDevice.Width / 3, 160, 720);
            int h = Mathf.Clamp(profileDevice.Height / 3, 160, 1280);
            try
            {
                byte[] png = VufM09RenderCapture.CaptureCandidate(
                    candidate, w, h, reducedMotion);
                if (png == null || png.Length < 60)
                    throw new InvalidOperationException("no actual rendered PNG");
                var img = new Texture2D(2, 2, TextureFormat.RGBA32, false);
                if (!img.LoadImage(png, false))
                {
                    DestroyImmediate(img);
                    throw new InvalidOperationException("Unity produced invalid PNG");
                }
                captured = img;
                capturedPng = png;
                renderCpuMs = (EditorApplication.timeSinceStartup - start) * 1000;
                AddTrace("ACTUAL UNITY RenderTexture PNG " + w + "x" + h +
                    " / EDITOR ONLY; NEVER PHYSICAL DEVICE SCREENSHOT");
                message = "Unity Editor synthetic uGUI pixel preview captured. " +
                    "This is NOT a real device capture or owner visual signoff.";
            }
            catch (Exception ex)
            {
                message = "RENDER BLOCKED: " + ex.Message;
            }
        }

        private static string Hash(byte[] data)
        {
            using (var sha = SHA256.Create())
                return BitConverter.ToString(sha.ComputeHash(data))
                    .Replace("-", "").ToLowerInvariant();
        }

        private static string ExternalNewFile(string purpose, string ext)
        {
            string name = EditorUtility.SaveFilePanel(
                purpose + " - NEW outside checkout",
                Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments),
                "VUF_M09_CANDIDATE_UNAPPROVED", ext);
            if (String.IsNullOrEmpty(name)) return null;
            if (!Path.IsPathRooted(name) ||
                !String.Equals(Path.GetExtension(name), "." + ext,
                    StringComparison.OrdinalIgnoreCase) ||
                File.Exists(name) || Directory.Exists(name))
                throw new IOException("must choose a NEW external file");
            string canonical = Path.GetFullPath(name);
            string root = Path.GetFullPath(Directory.GetCurrentDirectory())
                .TrimEnd(Path.DirectorySeparatorChar) + Path.DirectorySeparatorChar;
            if (canonical.StartsWith(root, StringComparison.OrdinalIgnoreCase))
                throw new IOException("cannot write inside Unity workspace");
            for (var dir = new DirectoryInfo(Path.GetDirectoryName(canonical));
                dir != null; dir = dir.Parent)
                if (!dir.Exists ||
                    (dir.Attributes & FileAttributes.ReparsePoint) != 0)
                    throw new IOException("symlink/junction/nonexistent folder rejected");
            return canonical;
        }

        private ReviewReceipt Receipt()
        {
            var d = VufResponsiveGeometry.Presets[device];
            return new ReviewReceipt {
                profile_id = VufM09MatrixAudit.Profiles[profile],
                screen_id = screens[screen].id,
                state_id = VufReviewStateCatalog.States[state],
                locale = VufReviewStateCatalog.Locales[locale],
                synthetic_device = d.Name,
                level_mock = levelMock, seed_mock = seedMock,
                visual_event = Events[eventIndex],
                width = captured == null ? 0 : captured.width,
                height = captured == null ? 0 : captured.height,
                screenshot_sha256 = capturedPng == null ? "NOT_CAPTURED" :
                    Hash(capturedPng),
                real_unity_render_observed = capturedPng != null,
                event_trace = String.Join("\n", trace.ToArray()),
                geometry_warnings = matrixCell == null ? -1 :
                    matrixCell.GeometryWarnings,
                typography_overflows = matrixCell == null ? -1 :
                    matrixCell.OverflowRisks,
                contrast_risks = matrixCell == null ? -1 :
                    matrixCell.ContrastRisks,
                text_unmeasured = matrixCell == null ? -1 :
                    matrixCell.TextUnmeasured,
                simulated_touch_count = fakeTaps,
                review_cpu_ms = renderCpuMs,
                matrix_start = batchStart,
                matrix_count = lastBatch == null ? 0 : lastBatch.Count
            };
        }

        private void ExportCaptured()
        {
            if (capturedPng == null)
                throw new InvalidOperationException("Capture a real Unity Editor preview first");
            string path = ExternalNewFile("M09 Editor-only rendered preview", "png");
            if (path == null) return;
            string receipt = Path.ChangeExtension(path, ".json");
            if (File.Exists(receipt))
                throw new IOException("review receipt filename already exists");
            using (var f = new FileStream(path, FileMode.CreateNew))
                f.Write(capturedPng, 0, capturedPng.Length);
            using (var f = new FileStream(receipt, FileMode.CreateNew))
            using (var writer = new StreamWriter(f, new System.Text.UTF8Encoding(false)))
                writer.Write(JsonUtility.ToJson(Receipt(), true));
            message = "Saved new Editor-only PNG + unapproved JSON. " +
                "Real physical device/owner/human rights flags remain FALSE.";
        }

        [Serializable]
        internal sealed class FrameEntry
        {
            public string path, sha256;
            public int step, elapsed_milli;
        }
        [Serializable]
        internal sealed class FrameSequenceReceipt
        {
            public string stage = "M09_EDITOR_TWEEN_SEQUENCE_NOT_OWNER_APPROVED";
            public string profile_id, coral_draft_screen_id, state, locale;
            public string synthetic_device, unsupported_video_reason =
                "Not encoded as video: these are manually stepped Unity " +
                "Editor candidates, not runtime gameplay or device FPS.";
            public int steps;
            public FrameEntry[] frames;
            public bool gameplay_recorded, real_device_recorded;
            public bool sound_or_haptic_recorded, owner_art_approved;
            public bool production_parity_approved, release_allowed;
        }

        private void ExportFrameSequence()
        {
            if (candidate == null || tween == null)
                throw new InvalidOperationException(
                    "N/A: select a disposable modal/overlay with CanvasGroup tween");
            string parent = EditorUtility.OpenFolderPanel(
                "Choose EXISTING external parent for NEW M09 candidate frames",
                Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments), "");
            if (String.IsNullOrEmpty(parent)) return;
            string checkout = Path.GetFullPath(Directory.GetCurrentDirectory())
                .TrimEnd(Path.DirectorySeparatorChar) + Path.DirectorySeparatorChar;
            parent = Path.GetFullPath(parent);
            if (!Directory.Exists(parent) ||
                (parent + Path.DirectorySeparatorChar).StartsWith(
                    checkout, StringComparison.OrdinalIgnoreCase))
                throw new IOException("frame export parent must be external real directory");
            for (var dir = new DirectoryInfo(parent); dir != null; dir = dir.Parent)
                if ((dir.Attributes & FileAttributes.ReparsePoint) != 0)
                    throw new IOException("linked export folders are forbidden");
            // This folder is never temporary/auto-cleaned, so the owner has
            // full control of exported review evidence. Zero overwrites.
            string newFolder = Path.Combine(parent,
                "VUF_M09_UNAPPROVED_" + DateTime.UtcNow.ToString("yyyyMMddTHHmmssfff"));
            if (Directory.Exists(newFolder) || File.Exists(newFolder))
                throw new IOException("frame sequence folder already exists");
            var d = VufResponsiveGeometry.Presets[device];
            int w = Mathf.Clamp(d.Width / 3, 160, 720);
            int h = Mathf.Clamp(d.Height / 3, 160, 1280);
            var receipt = new FrameSequenceReceipt {
                profile_id = VufM09MatrixAudit.Profiles[profile],
                coral_draft_screen_id = screens[screen].id,
                state = VufReviewStateCatalog.States[state],
                locale = VufReviewStateCatalog.Locales[locale],
                synthetic_device = d.Name, steps = 8,
                frames = new FrameEntry[8]
            };
            Directory.CreateDirectory(newFolder);
            try
            {
                tween.SetReducedMotion(false);
                tween.Show();
                tween.Advance(tween.Duration);
                tween.Hide();
                for (int i = 0; i < receipt.steps; i++)
                {
                    if (i > 0) tween.Advance(tween.Duration / 7f);
                    byte[] image = VufM09RenderCapture.CaptureCandidate(
                        candidate, w, h, false);
                    string name = "frame_" + i.ToString("D2") + ".png";
                    string target = Path.Combine(newFolder, name);
                    using (var output = new FileStream(target,
                        FileMode.CreateNew, FileAccess.Write, FileShare.None))
                        output.Write(image, 0, image.Length);
                    receipt.frames[i] = new FrameEntry {
                        step = i,
                        elapsed_milli = Mathf.RoundToInt(
                            tween.Duration * i / 7f * 1000f),
                        path = name, sha256 = Hash(image)
                    };
                }
                string metadata = Path.Combine(newFolder,
                    "M09_UNAPPROVED_FRAME_SEQUENCE.json");
                using (var output = new FileStream(metadata,
                    FileMode.CreateNew, FileAccess.Write, FileShare.None))
                using (var writer = new StreamWriter(output,
                    new System.Text.UTF8Encoding(false)))
                    writer.Write(JsonUtility.ToJson(receipt, true));
                AddTrace("8 REAL Editor candidate tween frames exported. " +
                    "NOT owner/gameplay/device approved, NO MP4 produced");
                message = "Created NEW 8-frame PNG sequence and hash receipt: " +
                    newFolder + " . Not a video or physical device recording.";
            }
            finally
            {
                tween.Show();
                tween.Advance(tween.Duration);
                tween.SetReducedMotion(reducedMotion);
            }
        }

        private void RunMatrixChunk()
        {
            if (screens == null) return;
            try
            {
                lastBatch = VufM09MatrixAudit.InspectBatch(batchStart, batchCount);
                int warnings = 0;
                foreach (var row in lastBatch)
                    warnings += row.GeometryWarnings + row.OverflowRisks +
                        row.ContrastRisks + row.TextUnmeasured;
                AddTrace("MATRIX BATCH " + batchStart + " count=" + lastBatch.Count +
                    " risks=" + warnings + " / NOT RENDERED/NOT APPROVED");
                message = "REAL candidate component geometry + typography evaluated " +
                    lastBatch.Count + " cells; no device rendering or owner PASS.";
            }
            catch (Exception e) { message = "MATRIX BLOCKED: " + e.Message; }
        }

        private void OnGUI()
        {
            EditorGUILayout.LabelField(
                "M09 | OWNER VISUAL QA, REAL UNITY EDITOR CANDIDATES",
                EditorStyles.boldLabel);
            EditorGUILayout.HelpBox(
                "Every unsupported feature is N/A. 28 Coral draft screens " +
                "can be styled for 5 themes, but OTHER GAMES have NO separate " +
                "28-screen contracts. Visual/rights/device/gameplay acceptance " +
                "is NEVER inferred. Do not export this candidate as a player.",
                MessageType.Warning);
            if (screens == null)
            {
                EditorGUILayout.HelpBox(message, MessageType.Error);
                return;
            }
            scroll = EditorGUILayout.BeginScrollView(scroll);
            EditorGUI.BeginChangeCheck();
            profile = EditorGUILayout.Popup("Draft visual profile", profile,
                VufM09MatrixAudit.Profiles);
            string[] names = new string[screens.Length];
            for (int i = 0; i < screens.Length; i++)
                names[i] = screens[i].id + " / " + screens[i].key +
                    " [" + screens[i].feature_gate + "]";
            screen = EditorGUILayout.Popup("Coral 28-screen ID", screen, names);
            state = EditorGUILayout.Popup("MOCK state", state,
                VufReviewStateCatalog.States);
            locale = EditorGUILayout.Popup("MOCK locale + stress", locale,
                VufReviewStateCatalog.Locales);
            string[] devices = new string[VufResponsiveGeometry.Presets.Length];
            for (int i = 0; i < devices.Length; i++)
                devices[i] = VufResponsiveGeometry.Presets[i].Name;
            device = EditorGUILayout.Popup("Synthetic device safe-area", device, devices);
            if (EditorGUI.EndChangeCheck())
            {
                DisposeOnlyMine();
                matrixCell = null;
                trace.Clear();
                message = "Source/theme/screen/state/locale/device changed; " +
                    "previous screenshot and temporary UI invalidated. BUILD again.";
            }
            levelMock = EditorGUILayout.IntSlider("Manual mock level (NO gameplay)",
                levelMock, 1, 100);
            seedMock = EditorGUILayout.IntSlider("Manual mock seed (NO Engine RNG)",
                seedMock, 0, 65535);
            eventIndex = EditorGUILayout.Popup("Presentation cue (symbolic)", eventIndex, Events);
            speed = EditorGUILayout.Popup("Manual transition speed", speed, Speeds);
            reducedMotion = EditorGUILayout.Toggle("Reduced-motion mock", reducedMotion);
            showOverlay = EditorGUILayout.Toggle("Show synthetic guides", showOverlay);
            using (new EditorGUILayout.HorizontalScope())
            {
                if (GUILayout.Button("Build selected real TEMP uGUI", GUILayout.Height(28)))
                    Build();
                if (GUILayout.Button("Inspect geometry + contrast"))
                    AuditCurrent();
                if (GUILayout.Button("DESTROY MY TEMP uGUI"))
                {
                    DisposeOnlyMine();
                    message = "Only this Studio's nonpersistent preview was removed.";
                }
            }
            using (new EditorGUILayout.HorizontalScope())
            {
                if (GUILayout.Button("Manual mock button TAP") && mockTapButton != null)
                    mockTapButton.onClick.Invoke();
                if (GUILayout.Button("Single-step CanvasGroup transition"))
                    StepTween();
                if (GUILayout.Button("Log symbolic audio/haptic cue"))
                {
                    AddTrace(VufVisualEventCatalog.AudioCueLog(
                        VufM09MatrixAudit.Profiles[profile], Events[eventIndex], true));
                    AddTrace(VufVisualEventCatalog.HapticCueLog(
                        VufM09MatrixAudit.Profiles[profile], Events[eventIndex], true));
                }
            }
            using (new EditorGUILayout.HorizontalScope())
            {
                if (GUILayout.Button("RENDER actual Unity candidate PNG"))
                    Render();
                if (GUILayout.Button("Capture A for side-by-side") && captured != null)
                {
                    if (comparison != null) DestroyImmediate(comparison);
                    comparison = new Texture2D(2, 2, TextureFormat.RGBA32, false);
                    comparison.LoadImage(capturedPng, false);
                    AddTrace("A/B snapshot pinned in-memory, no source overwrite");
                }
                if (GUILayout.Button("Export NEW PNG + JSON receipt"))
                {
                    try { ExportCaptured(); }
                    catch (Exception e) { message = "EXPORT BLOCKED: " + e.Message; }
                }
                if (GUILayout.Button("Export 8 REAL Editor tween PNG frames"))
                {
                    try { ExportFrameSequence(); }
                    catch (Exception e) { message = "FRAMES BLOCKED: " + e.Message; }
                }
            }
            if (captured != null)
            {
                using (new EditorGUILayout.HorizontalScope())
                {
                    if (comparison != null)
                        GUILayout.Label(comparison, GUILayout.Width(260),
                            GUILayout.Height(360));
                    GUILayout.Label(captured, GUILayout.Width(260),
                        GUILayout.Height(360));
                }
                EditorGUILayout.HelpBox("LEFT pinned A, RIGHT current B. " +
                    "These are real Unity Editor candidate pixels, NOT device QA. " +
                    "No genuine gameplay asset/polished art has been supplied.",
                    MessageType.Info);
            }
            if (showOverlay && matrixCell != null)
                EditorGUILayout.HelpBox("SYNTHETIC SAFE-AREA: " + matrixCell.Device +
                    " | geometry=" + matrixCell.GeometryWarnings +
                    " | text overflow=" + matrixCell.OverflowRisks +
                    " | contrast=" + matrixCell.ContrastRisks +
                    " | text unknown=" + matrixCell.TextUnmeasured +
                    " | N/A=" + matrixCell.Scope, MessageType.Info);
            EditorGUILayout.Space();
            EditorGUILayout.LabelField("Bounded complete matrix (5 x 28 x 8 x 3 x 5)",
                EditorStyles.boldLabel);
            EditorGUILayout.LabelField("Total candidate style rows",
                VufM09MatrixAudit.MatrixSize(screens.Length).ToString() +
                " / 16,800. 4 titles use Coral draft IDs only.");
            batchStart = EditorGUILayout.IntSlider("Batch start", batchStart, 0,
                VufM09MatrixAudit.MatrixSize(screens.Length) - 32);
            batchCount = EditorGUILayout.IntSlider("Single-click count", batchCount, 1, 32);
            if (GUILayout.Button("Audit next bounded real Unity batch"))
            {
                RunMatrixChunk();
                batchStart = Mathf.Min(batchStart + batchCount,
                    VufM09MatrixAudit.MatrixSize(screens.Length) - 32);
            }
            if (lastBatch != null)
                foreach (var row in lastBatch)
                    EditorGUILayout.LabelField("CELL #" + row.Index + " " +
                        row.Profile + "/" + row.ScreenId + "/" + row.State +
                        "/" + row.Locale + "/" + row.Device +
                        " risks=" + (row.GeometryWarnings + row.OverflowRisks +
                            row.ContrastRisks + row.TextUnmeasured) +
                        " / OWNER & DEVICE NOT APPROVED");
            EditorGUILayout.Space();
            using (new EditorGUILayout.HorizontalScope())
            {
                if (GUILayout.Button("Open M07 REAL Sprite/VFX timeline"))
                    VufUnifiedVisualStudioWindow.Open();
                if (GUILayout.Button("Open M06 layer/parallax viewer"))
                    VufSceneLayerReviewWindow.Open();
                if (GUILayout.Button("Open M08 external pack A/B"))
                    VufExternalPackSandboxWindow.Open();
                if (GUILayout.Button("Open readiness/rights board"))
                    VufReadinessBoardWindow.Open();
            }
            EditorGUILayout.HelpBox(message, MessageType.Info);
            EditorGUILayout.LabelField("Read-only simulated event trace");
            foreach (var item in trace)
                EditorGUILayout.SelectableLabel(item,
                    EditorStyles.wordWrappedLabel, GUILayout.MinHeight(24f));
            EditorGUILayout.HelpBox(
                "NO GAME BINDING / NO ORIGINAL ART RIGHTS / NO PHYSICAL " +
                "DEVICE-GPU TEST / NO HUMAN CREATIVE APPROVAL / NO RELEASE. " +
                "Candidate pixel capture alone is not a verified production UI.",
                MessageType.Warning);
            EditorGUILayout.EndScrollView();
        }
    }
}
