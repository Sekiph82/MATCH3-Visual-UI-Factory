// VUF-M07-005/006/009/013 | Unified manual owner Sprite & VFX Studio.
// INTERNAL_REUSE: VufSpritePlaybackPreview (real SpriteRenderer), existing
// VufVfxLabWindow five real Unity ParticleSystem presets, VufFxSheetPreviewWindow
// validated synthetic atlas, and the M07 Python fourteen-event visual taxonomy.
// All assets are manually selected IMPORTED COPIES. NO authoritative Engine
// events, production art/rights, network, save/reward, audio/haptic playback,
// scene file edits, implicit asset creation, or owner autoapproval.
//
// EDITOR PREVIEW ONLY. "Real" means actual in-memory Unity SpriteRenderer
// and ParticleSystem playback, NOT phone GPU/production FPS or owner QA PASS.
using System;
using System.Collections.Generic;
using System.IO;
using System.Security.Cryptography;
using System.Text;
using UnityEditor;
using UnityEngine;
using UnityEngine.Profiling;

namespace Match3.VisualFactory.Editor
{
    public sealed class VufUnifiedVisualStudioWindow : EditorWindow
    {
        private static readonly string[] SpeedLabels =
            { "0.25x", "0.5x", "1x", "2x" };
        private static readonly float[] Speeds = { .25f, .5f, 1f, 2f };
        private static readonly string[] EventLabels = EventNames();
        private static readonly string[] Devices = {
            "Phone 9:16 SYNTHETIC", "Tall phone 6:13 SYNTHETIC",
            "Tablet 3:4 SYNTHETIC"
        };
        private int profileIndex, eventIndex, speedIndex = 2, deviceIndex;
        private int firstSpecialIndex, secondSpecialIndex;
        private bool reducedMotion, muteAudioHaptic = true, loop = true, pingPong;
        private bool showAlpha = true, showGuides = true;
        private float fps = 12f, previewZoom = 1f;
        private Texture2D sourceSheet, alternateSheet;
        private TextAsset fxManifest;
        private Texture2D fxAtlas, fxStill;
        private Sprite[] primaryFrames, alternateFrames;
        private VufFxSheetPreviewWindow.FxManifest verifiedFx;
        private GameObject tempSpriteObject, tempParticlesObject;
        private VufSpritePlaybackPreview spritePlayback;
        private ParticleSystem particles;
        private int displayedFxFrame;
        private double fxElapsed, lastTick, lastStepMs;
        private long frameTickCount, sampledEditorAlloc;
        private string info = "Select imported Sprite (Multiple) COPY and Load Candidate.";
        private string lastCue = "NO AUDIO/HAPTIC EVER FIRED";
        private bool fxPlaying;
        private Vector2 scroll;

        private static string[] EventNames()
        {
            var arr = new string[VufVisualEventCatalog.Events.Length];
            for (int i = 0; i < arr.Length; i++)
                arr[i] = VufVisualEventCatalog.Events[i].Name;
            return arr;
        }

        [MenuItem("Tools/MATCH3/Unified Sprite and VFX Review Studio")]
        public static void Open()
        {
            var view = GetWindow<VufUnifiedVisualStudioWindow>(
                "VUF Unified Visual QA");
            view.minSize = new Vector2(740, 780);
            view.Show();
        }

        private void OnEnable()
        {
            lastTick = EditorApplication.timeSinceStartup;
            EditorApplication.update += Tick;
        }

        private void OnDisable()
        {
            EditorApplication.update -= Tick;
            DestroyOnlyTemporary();
        }

        private void Tick()
        {
            double now = EditorApplication.timeSinceStartup;
            float delta = (float)Math.Max(0d, Math.Min(.15d, now - lastTick));
            lastTick = now;
            if ((spritePlayback == null || !spritePlayback.IsPlaying) && !fxPlaying)
                return;
            var watch = System.Diagnostics.Stopwatch.StartNew();
            if (spritePlayback != null && spritePlayback.IsPlaying)
                spritePlayback.Advance(delta, Speeds[speedIndex]);
            if (fxPlaying && !reducedMotion)
            {
                float seconds = delta * Speeds[speedIndex];
                if (verifiedFx != null)
                {
                    fxElapsed += seconds;
                    var frameStep = 1d / verifiedFx.fps;
                    if (fxElapsed >= frameStep)
                    {
                        int steps = (int)(fxElapsed / frameStep);
                        fxElapsed -= steps * frameStep;
                        displayedFxFrame = (displayedFxFrame + steps) %
                                           verifiedFx.frame_count;
                    }
                }
                if (particles != null)
                    particles.Simulate(seconds, true, false, true);
            }
            watch.Stop();
            lastStepMs = watch.Elapsed.TotalMilliseconds;
            frameTickCount++;
            // Editor allocation is a view-only approximate telemetry reading.
            if (frameTickCount % 10 == 0)
                sampledEditorAlloc = Profiler.GetTotalAllocatedMemoryLong();
            Repaint();
        }

        private static Sprite[] ReadImportedFrames(Texture2D texture)
        {
            if (texture == null) throw new ArgumentException(
                "Choose imported copy Sprite (Multiple) sheet.");
            string path = AssetDatabase.GetAssetPath(texture);
            if (String.IsNullOrEmpty(path) ||
                !path.StartsWith("Assets/", StringComparison.Ordinal) ||
                !path.EndsWith(".png", StringComparison.OrdinalIgnoreCase))
                throw new ArgumentException("Select a PNG copied to Assets/");
            var importer = AssetImporter.GetAtPath(path) as TextureImporter;
            if (importer == null || importer.textureType != TextureImporterType.Sprite)
                throw new ArgumentException("Source importer must already be Sprite.");
            var found = new List<Sprite>();
            foreach (UnityEngine.Object item in AssetDatabase.LoadAllAssetsAtPath(path))
            {
                Sprite sprite = item as Sprite;
                if (sprite != null && !sprite.packed) found.Add(sprite);
            }
            // No new numerical/UV/slicing algorithm. Existing frame geometry is
            // never changed. Explicit alphabetical order is deterministic.
            found.Sort((a, b) => String.Compare(a.name, b.name,
                                                StringComparison.Ordinal));
            if (found.Count < 2 || found.Count > 4096)
                throw new ArgumentException("Expected 2..4096 unpacked imported sprites");
            return found.ToArray();
        }

        // The existing FX sheet validator intentionally checks geometry and
        // receipt SHAPE, but not disk bytes. This Studio checks imported COPY
        // PNG hashes as well, without changing source TextureImporter.
        private void VerifyImportedFxReceipts()
        {
            string manifestPath = AssetDatabase.GetAssetPath(fxManifest);
            string atlasPath = AssetDatabase.GetAssetPath(fxAtlas);
            string stillPath = AssetDatabase.GetAssetPath(fxStill);
            if (String.IsNullOrEmpty(manifestPath) ||
                !manifestPath.StartsWith("Assets/", StringComparison.Ordinal) ||
                !manifestPath.EndsWith(".json", StringComparison.OrdinalIgnoreCase) ||
                String.IsNullOrEmpty(atlasPath) ||
                !atlasPath.StartsWith("Assets/", StringComparison.Ordinal) ||
                !atlasPath.EndsWith(".png", StringComparison.OrdinalIgnoreCase) ||
                String.IsNullOrEmpty(stillPath) ||
                !stillPath.StartsWith("Assets/", StringComparison.Ordinal) ||
                !stillPath.EndsWith(".png", StringComparison.OrdinalIgnoreCase) ||
                !String.Equals(Path.GetFileName(atlasPath),
                    verifiedFx.atlas_path, StringComparison.Ordinal) ||
                !String.Equals(Path.GetFileName(stillPath),
                    verifiedFx.reduced_motion_path, StringComparison.Ordinal) ||
                !String.Equals(SourceDigest(fxAtlas),
                    verifiedFx.atlas_sha256, StringComparison.Ordinal) ||
                !String.Equals(SourceDigest(fxStill),
                    verifiedFx.reduced_motion_sha256, StringComparison.Ordinal))
                throw new ArgumentException(
                    "FX imported-copy atlas/still path or SHA-256 mismatch");
        }

        private void DestroyOnlyTemporary()
        {
            fxPlaying = false;
            if (tempParticlesObject != null)
                DestroyImmediate(tempParticlesObject);
            if (tempSpriteObject != null)
                DestroyImmediate(tempSpriteObject);
            tempParticlesObject = null;
            tempSpriteObject = null;
            spritePlayback = null;
            particles = null;
            primaryFrames = null;
            alternateFrames = null;
            verifiedFx = null;
            displayedFxFrame = 0;
            fxElapsed = 0;
        }

        private void LoadCandidate()
        {
            DestroyOnlyTemporary();
            info = "CANDIDATE REJECTED: no assets/engine state modified";
            GameObject built = null;
            try
            {
                Sprite[] candidate = ReadImportedFrames(sourceSheet);
                Sprite[] alt = null;
                if (alternateSheet != null) alt = ReadImportedFrames(alternateSheet);
                if (fxManifest != null || fxAtlas != null || fxStill != null)
                {
                    if (fxManifest == null || fxAtlas == null || fxStill == null)
                        throw new ArgumentException(
                            "FX candidate requires manifest, atlas AND static still.");
                    verifiedFx = VufFxSheetPreviewWindow.Parse(
                        fxManifest.text, fxAtlas.width, fxAtlas.height,
                        fxStill.width, fxStill.height);
                    VerifyImportedFxReceipts();
                }
                built = new GameObject("VUF_TEMP_UnifiedView_DONT_SAVE",
                    typeof(SpriteRenderer), typeof(VufSpritePlaybackPreview));
                built.hideFlags = HideFlags.DontSaveInEditor |
                                  HideFlags.DontSaveInBuild;
                built.transform.localScale = Vector3.one * previewZoom;
                var target = built.GetComponent<SpriteRenderer>();
                target.sortingOrder = 1000;
                var playback = built.GetComponent<VufSpritePlaybackPreview>();
                playback.Bind(candidate, fps, loop, pingPong, reducedMotion);
                primaryFrames = candidate;
                alternateFrames = alt;
                spritePlayback = playback;
                tempSpriteObject = built;
                info = "READY: real candidate SpriteRenderer loaded in temporary Scene. " +
                       "Click Test Event or Play; no gameplay event or authority. " +
                       "Click F in Scene to focus manually.";
                Selection.activeGameObject = built; // explicit Load button
                lastTick = EditorApplication.timeSinceStartup;
            }
            catch (Exception exception)
            {
                if (built != null) DestroyImmediate(built);
                DestroyOnlyTemporary();
                info = "SOURCE CANDIDATE REJECTED: " + exception.Message;
            }
        }

        private void TestEvent()
        {
            var e = VufVisualEventCatalog.Events[eventIndex];
            lastCue = VufVisualEventCatalog.AudioCueLog(
                VufVisualEventCatalog.Profiles[profileIndex],
                e.Name, muteAudioHaptic) + " / " +
                VufVisualEventCatalog.HapticCueLog(
                    VufVisualEventCatalog.Profiles[profileIndex],
                    e.Name, muteAudioHaptic);
            if (spritePlayback == null || primaryFrames == null)
            {
                info = "Import candidate Sprite Multiple COPY first.";
                return;
            }
            try
            {
                string key = VufVisualEventCatalog.ViewEventKey(
                    VufVisualEventCatalog.Profiles[profileIndex], e.Name,
                    e.Name == "special_trigger" || e.Name == "combo_chain" ?
                        VufVisualEventCatalog.EngineSpecials[firstSpecialIndex] : null,
                    e.Name == "combo_chain" ?
                        VufVisualEventCatalog.EngineSpecials[secondSpecialIndex] : null);
                // Reject an unrelated imported FX first. Event arbitration
                // must not change even one Sprite before all view inputs pass.
                if (verifiedFx != null && !reducedMotion &&
                    verifiedFx.preset_id != e.Preset)
                    throw new ArgumentException("Imported FX preset is not " +
                        "the current view event's verified preset.");
                bool accepted = spritePlayback.TryPresentViewEvent(
                    key, e.Channel, e.Priority, primaryFrames, fps, loop,
                    pingPong, reducedMotion);
                if (!accepted)
                {
                    info = "Lower priority SAME-channel visual event REJECTED; " +
                           "current SpriteRenderer unchanged.";
                    return;
                }
                if (tempParticlesObject != null)
                {
                    DestroyImmediate(tempParticlesObject);
                    tempParticlesObject = null;
                    particles = null;
                }
                fxPlaying = false;
                fxElapsed = 0;
                displayedFxFrame = 0;
                if (!reducedMotion && e.Preset != null)
                {
                    var built = VufVfxLabWindow.BuildCandidateParticleSystem(
                        e.Preset, 24, .65f, 1.8f, .12f, Color.cyan);
                    built.hideFlags = HideFlags.DontSaveInEditor |
                                      HideFlags.DontSaveInBuild;
                    tempParticlesObject = built;
                    particles = built.GetComponent<ParticleSystem>();
                    particles.Stop(true, ParticleSystemStopBehavior.StopEmittingAndClear);
                    particles.Simulate(0f, true, true, true);
                    fxPlaying = particles != null;
                }
                info = key + " view ONLY, channel=" + e.Channel +
                    ", priority=" + e.Priority + ", duration guideline=" +
                    e.DurationMs + " ms (manual preview != runtime contract).";
            }
            catch (Exception ex)
            {
                info = "EVENT REFUSED: " + ex.Message;
            }
        }

        private void DrawFx(Rect outer)
        {
            EditorGUI.DrawRect(outer, new Color(.09f, .11f, .16f, 1f));
            if (verifiedFx == null)
            {
                GUI.Label(outer, "Optional FX sheet + manifest not loaded. " +
                    "Unity particle preset still available.");
                return;
            }
            if (reducedMotion)
            {
                GUI.DrawTexture(outer, fxStill, ScaleMode.ScaleToFit, true);
                return;
            }
            var coords = verifiedFx.animation_frames[
                Mathf.Clamp(displayedFxFrame, 0, verifiedFx.frame_count - 1)]
                .pixel_rect_top_left;
            Rect uv = new Rect(
                (float)coords[0] / verifiedFx.atlas_width,
                (float)(verifiedFx.atlas_height - coords[1] - coords[3]) /
                    verifiedFx.atlas_height,
                (float)coords[2] / verifiedFx.atlas_width,
                (float)coords[3] / verifiedFx.atlas_height);
            GUI.DrawTextureWithTexCoords(outer, fxAtlas, uv, true);
        }

        private void DrawSprite(Rect outer, Sprite comparisonFrame = null)
        {
            EditorGUI.DrawRect(outer, new Color(.10f, .12f, .16f));
            if (showAlpha)
            {
                for (int y = 0; y < (int)outer.height / 20 + 1; y++)
                    for (int x = 0; x < (int)outer.width / 20 + 1; x++)
                        EditorGUI.DrawRect(new Rect(
                            outer.x + x * 20, outer.y + y * 20, 20, 20),
                            (x + y) % 2 == 0 ? new Color(.27f, .29f, .32f) :
                                               new Color(.42f, .44f, .48f));
            }
            if (spritePlayback == null || tempSpriteObject == null) return;
            var sprite = comparisonFrame != null ? comparisonFrame :
                tempSpriteObject.GetComponent<SpriteRenderer>().sprite;
            if (sprite == null) return;
            // Imported Sprite texture rect may not be readable for packed
            // rotated assets, which are excluded at asset intake above.
            Rect rect = sprite.textureRect;
            float ratio = rect.width / Mathf.Max(1f, rect.height);
            float h = Mathf.Min(outer.height, outer.width / ratio) * previewZoom;
            float w = h * ratio;
            Rect dst = new Rect(outer.center.x - w/2f, outer.center.y - h/2f, w, h);
            Rect uv = new Rect(rect.x / sprite.texture.width,
                               rect.y / sprite.texture.height,
                               rect.width / sprite.texture.width,
                               rect.height / sprite.texture.height);
            GUI.DrawTextureWithTexCoords(dst, sprite.texture, uv, true);
            if (showGuides)
            {
                float x = dst.x + w * sprite.pivot.x / rect.width;
                float y = dst.y + h * (1f - sprite.pivot.y / rect.height);
                EditorGUI.DrawRect(new Rect(x - 1f, dst.y, 2f, h), Color.yellow);
                EditorGUI.DrawRect(new Rect(dst.x, y - 1f, w, 2f), Color.yellow);
                // Synthetic guide is NOT the OS safe inset on a real device.
                float gx = outer.width * .07f, gy = outer.height * .065f;
                var line = new Color(.2f, 1f, .65f, .85f);
                EditorGUI.DrawRect(new Rect(outer.x + gx, outer.y + gy,
                    outer.width - gx * 2f, 2f), line);
                EditorGUI.DrawRect(new Rect(outer.x + gx,
                    outer.y + outer.height - gy - 2f,
                    outer.width - gx * 2f, 2f), line);
                EditorGUI.DrawRect(new Rect(outer.x + gx, outer.y + gy,
                    2f, outer.height - gy * 2f), line);
                EditorGUI.DrawRect(new Rect(outer.x + outer.width - gx - 2f,
                    outer.y + gy, 2f, outer.height - gy * 2f), line);
            }
        }

        [Serializable] private sealed class ReviewReceipt
        {
            public string stage, profile, view_event, view_key, view_channel;
            public string source_sprite_path, alternative_sprite_path, fx_source_path;
            public string source_png_sha256, alternative_png_sha256, fx_manifest_sha256;
            public int frame_cursor, sprite_count, fx_frame_cursor, simulated_device_index;
            public int visual_priority;
            public long unity_editor_allocated_bytes, estimated_sprite_rgba_bytes;
            public long estimated_fx_rgba_bytes;
            public int preview_particle_count, fx_frame_count;
            public double last_editor_visual_step_ms;
            public long measured_editor_updates;
            public bool reduced_motion, muted, real_unity_spriterenderer_bound;
            public bool actual_device_fps_verified, actual_gpu_draw_calls_verified;
            public bool owner_visual_accepted, art_rights_verified, engine_parity_verified;
            public bool real_audio_or_haptic_fired, release_allowed;
            public string audio_haptic_cue_log, missing_evidence;
        }

        // Synthetic aspect framing only. No platform notch, actual device
        // dimensions, display pixel density, canvas/layout or GPU inference.
        internal static Rect SyntheticViewport(Rect available, int index)
        {
            if (index < 0 || index >= 3 || available.width <= 0f ||
                available.height <= 0f)
                throw new ArgumentOutOfRangeException(nameof(index));
            float aspect = index == 0 ? 9f / 16f :
                           index == 1 ? 6f / 13f : 3f / 4f;
            float width = Mathf.Min(available.width, available.height * aspect);
            float height = width / aspect;
            return new Rect(available.center.x - width * .5f,
                            available.center.y - height * .5f, width, height);
        }

        private static bool CanExportOwnerReviewReceipt(string filepath)
        {
            if (String.IsNullOrWhiteSpace(filepath) ||
                !Path.IsPathRooted(filepath) ||
                !filepath.EndsWith(".json", StringComparison.OrdinalIgnoreCase) ||
                File.Exists(filepath) || Directory.Exists(filepath))
                return false;
            string full = Path.GetFullPath(filepath);
            string checkout = Path.GetFullPath(Directory.GetCurrentDirectory())
                .TrimEnd(Path.DirectorySeparatorChar) +
                Path.DirectorySeparatorChar;
            if (full.StartsWith(checkout, StringComparison.OrdinalIgnoreCase))
                return false;
            string folder = Path.GetDirectoryName(full);
            if (String.IsNullOrEmpty(folder) || !Directory.Exists(folder))
                return false;
            // No following reparse points through the chosen export ancestry.
            for (var parent = new DirectoryInfo(folder); parent != null;
                 parent = parent.Parent)
            {
                if ((parent.Attributes & FileAttributes.ReparsePoint) != 0)
                    return false;
            }
            return true;
        }

        private void ExportOwnerReviewReceipt()
        {
            string path = EditorUtility.SaveFilePanel(
                "Create NEW unapproved VUF M07 review receipt OUTSIDE checkout",
                Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments),
                "VUF_M07_OWNER_REVIEW_UNAPPROVED", "json");
            if (String.IsNullOrEmpty(path)) return;
            if (!CanExportOwnerReviewReceipt(path))
            {
                info = "Receipt export refused: choose NEW .json outside " +
                       "Unity checkout; no existing file may be overwritten.";
                return;
            }
            try
            {
                // CreateNew is race-safe against an existing owner file.
                using (var outFile = new FileStream(path, FileMode.CreateNew,
                    FileAccess.Write, FileShare.None))
                using (var writer = new StreamWriter(outFile, new UTF8Encoding(false)))
                    writer.Write(ReceiptJson());
                info = "Saved candidate receipt only: " + path +
                    ". No art/owner/device PASS certified.";
            }
            catch (Exception error)
            {
                info = "Receipt export blocked: " + error.Message;
            }
        }

        private static string SourceDigest(UnityEngine.Object asset)
        {
            if (asset == null) return "NOT_SELECTED";
            string path = AssetDatabase.GetAssetPath(asset);
            if (String.IsNullOrEmpty(path) ||
                !path.StartsWith("Assets/", StringComparison.Ordinal))
                return "UNVERIFIED_ASSET_PATH";
            string file = Path.Combine(Directory.GetCurrentDirectory(), path);
            if (!File.Exists(file) ||
                (File.GetAttributes(file) & FileAttributes.ReparsePoint) != 0 ||
                new FileInfo(file).Length > 16 * 1024 * 1024)
                return "SOURCE_BYTES_NOT_VERIFIED";
            using (var sha = SHA256.Create())
                return BitConverter.ToString(sha.ComputeHash(File.ReadAllBytes(file)))
                    .Replace("-", "").ToLowerInvariant();
        }

        private string ReceiptJson()
        {
            var e = VufVisualEventCatalog.Events[eventIndex];
            string profile = VufVisualEventCatalog.Profiles[profileIndex];
            long bytes = sourceSheet == null ? 0L :
                (long)sourceSheet.width * sourceSheet.height * 4L;
            long fxBytes = fxAtlas == null ? 0L :
                (long)fxAtlas.width * fxAtlas.height * 4L;
            if (fxStill != null)
                fxBytes += (long)fxStill.width * fxStill.height * 4L;
            var receipt = new ReviewReceipt {
                stage = "CANDIDATE_ONLY_NOT_OWNER_APPROVED",
                profile = profile, view_event = e.Name,
                view_key = VufVisualEventCatalog.ViewEventKey(
                    profile, e.Name,
                    e.Name == "special_trigger" || e.Name == "combo_chain" ?
                        VufVisualEventCatalog.EngineSpecials[firstSpecialIndex] : null,
                    e.Name == "combo_chain" ?
                        VufVisualEventCatalog.EngineSpecials[secondSpecialIndex] : null),
                view_channel = e.Channel, visual_priority = e.Priority,
                source_sprite_path = AssetDatabase.GetAssetPath(sourceSheet),
                alternative_sprite_path = AssetDatabase.GetAssetPath(alternateSheet),
                fx_source_path = AssetDatabase.GetAssetPath(fxManifest),
                source_png_sha256 = SourceDigest(sourceSheet),
                alternative_png_sha256 = SourceDigest(alternateSheet),
                fx_manifest_sha256 = SourceDigest(fxManifest),
                sprite_count = primaryFrames == null ? 0 : primaryFrames.Length,
                frame_cursor = spritePlayback == null ? -1 : spritePlayback.CurrentFrameIndex,
                fx_frame_cursor = displayedFxFrame,
                simulated_device_index = deviceIndex, reduced_motion = reducedMotion,
                muted = muteAudioHaptic,
                real_unity_spriterenderer_bound =
                    spritePlayback != null && spritePlayback.IsBound,
                unity_editor_allocated_bytes = sampledEditorAlloc,
                estimated_sprite_rgba_bytes = bytes,
                estimated_fx_rgba_bytes = fxBytes,
                preview_particle_count = particles == null ? 0 : particles.particleCount,
                fx_frame_count = verifiedFx == null ? 0 : verifiedFx.frame_count,
                last_editor_visual_step_ms = lastStepMs,
                measured_editor_updates = frameTickCount,
                actual_device_fps_verified = false,
                actual_gpu_draw_calls_verified = false,
                owner_visual_accepted = false, art_rights_verified = false,
                engine_parity_verified = false,
                real_audio_or_haptic_fired = false, release_allowed = false,
                audio_haptic_cue_log = lastCue,
                missing_evidence = "Owner GUI signoff, real device/GPU draw calls, " +
                    "Engine/LFX final parity, source art rights and playable state NOT RUN"
            };
            return JsonUtility.ToJson(receipt, true);
        }

        private void OnGUI()
        {
            EditorGUILayout.LabelField("VUF | Unified Sprite & VFX Manual Studio",
                EditorStyles.boldLabel);
            EditorGUILayout.HelpBox(
                "Real Unity preview, NOT a playable screen. You must manually load " +
                "original/licensed IMPORTED COPY Sprites; game score, rewards, " +
                "persistent scene, importer, audio and haptics remain untouched. " +
                "Preview telemetry is Editor-only, NOT physical GPU/FPS proof.",
                MessageType.Warning);
            scroll = EditorGUILayout.BeginScrollView(scroll);
            profileIndex = EditorGUILayout.Popup("Game profile", profileIndex,
                VufVisualEventCatalog.Profiles);
            eventIndex = EditorGUILayout.Popup("View event (14)", eventIndex,
                EventLabels);
            if (EventLabels[eventIndex] == "special_trigger" ||
                EventLabels[eventIndex] == "combo_chain")
            {
                firstSpecialIndex = EditorGUILayout.Popup("Source-pinned Engine special",
                    firstSpecialIndex, VufVisualEventCatalog.EngineSpecials);
                if (EventLabels[eventIndex] == "combo_chain")
                    secondSpecialIndex = EditorGUILayout.Popup(
                        "Second source-pinned special", secondSpecialIndex,
                        VufVisualEventCatalog.EngineSpecials);
                EditorGUILayout.HelpBox(
                    "5 Engine kinds and 15 canonical unordered pair keys only. " +
                    "Final Engine release compatibility is NOT established.",
                    MessageType.Info);
            }
            deviceIndex = EditorGUILayout.Popup("Synthetic device ratio",
                deviceIndex, Devices);
            speedIndex = EditorGUILayout.Popup("Playback speed", speedIndex,
                SpeedLabels);
            bool nextReduced = EditorGUILayout.Toggle(
                "Reduced motion (static first frame)", reducedMotion);
            if (reducedMotion != nextReduced && spritePlayback != null)
                spritePlayback.SetReducedMotion(nextReduced);
            reducedMotion = nextReduced;
            muteAudioHaptic = EditorGUILayout.Toggle("Mute audio/haptic LOGS",
                muteAudioHaptic);
            showAlpha = EditorGUILayout.Toggle("Alpha checkerboard", showAlpha);
            showGuides = EditorGUILayout.Toggle("Pivot + safe guide", showGuides);
            previewZoom = EditorGUILayout.Slider("Manual zoom", previewZoom, .25f, 3f);
            if (tempSpriteObject != null)
                tempSpriteObject.transform.localScale = Vector3.one * previewZoom;

            EditorGUILayout.LabelField("Actual imported COPY Sprite candidate",
                EditorStyles.boldLabel);
            EditorGUI.BeginChangeCheck();
            sourceSheet = (Texture2D)EditorGUILayout.ObjectField(
                "Sprite (Multiple) PNG", sourceSheet, typeof(Texture2D), false);
            alternateSheet = (Texture2D)EditorGUILayout.ObjectField(
                "Alternative atlas PNG", alternateSheet, typeof(Texture2D), false);
            fps = EditorGUILayout.Slider("Frames/sec", fps, 1f, 60f);
            loop = EditorGUILayout.Toggle("Loop preview", loop);
            pingPong = EditorGUILayout.Toggle("Ping-pong", pingPong);
            fxManifest = (TextAsset)EditorGUILayout.ObjectField(
                "Optional procedural FX receipt", fxManifest, typeof(TextAsset), false);
            fxAtlas = (Texture2D)EditorGUILayout.ObjectField(
                "Optional FX sheet", fxAtlas, typeof(Texture2D), false);
            fxStill = (Texture2D)EditorGUILayout.ObjectField(
                "Optional reduced-motion still", fxStill, typeof(Texture2D), false);
            if (EditorGUI.EndChangeCheck())
            {
                DestroyOnlyTemporary();
                info = "Asset, clip timing, or FX input changed. " +
                    "Revalidate imported COPY before testing any view event.";
                lastCue = "NO AUDIO/HAPTIC EVER FIRED";
            }
            EditorGUILayout.BeginHorizontal();
            if (GUILayout.Button("Load/revalidate imported COPY", GUILayout.Height(30f)))
                LoadCandidate();
            if (GUILayout.Button("Clear TEMP Scene objects"))
            {
                DestroyOnlyTemporary();
                info = "Only Studio-owned temporary Scene objects cleared.";
            }
            EditorGUILayout.EndHorizontal();
            EditorGUILayout.BeginHorizontal();
            if (GUILayout.Button("Test view-only event"))
                TestEvent();
            using (new EditorGUI.DisabledScope(spritePlayback == null))
            {
                if (GUILayout.Button("Play"))
                {
                    try { spritePlayback.Play(); fxPlaying = !reducedMotion; }
                    catch (Exception e) { info = e.Message; }
                }
                if (GUILayout.Button("Pause"))
                {
                    spritePlayback.Pause(); fxPlaying = false;
                }
                if (GUILayout.Button("Interrupt"))
                {
                    spritePlayback.Interrupt(); fxPlaying = false;
                }
                if (GUILayout.Button("Replay"))
                {
                    spritePlayback.Replay();
                    displayedFxFrame = 0; fxElapsed = 0;
                    spritePlayback.Play(); fxPlaying = !reducedMotion;
                }
            }
            EditorGUILayout.EndHorizontal();

            if (spritePlayback != null)
            {
                int index = spritePlayback.CurrentFrameIndex;
                int wanted = EditorGUILayout.IntSlider(
                    "Manual sprite frame scrub", index, 0, primaryFrames.Length - 1);
                if (wanted != index) spritePlayback.ScrubFrame(wanted);
                EditorGUILayout.BeginHorizontal();
                if (GUILayout.Button("Previous Sprite"))
                    spritePlayback.ScrubFrame((index + primaryFrames.Length - 1) %
                                               primaryFrames.Length);
                if (GUILayout.Button("Next Sprite"))
                    spritePlayback.ScrubFrame((index + 1) % primaryFrames.Length);
                using (new EditorGUI.DisabledScope(alternateFrames == null))
                {
                    if (GUILayout.Button("Swap compatible atlas"))
                    {
                        try { spritePlayback.SwapCandidateAtlas(alternateFrames); }
                        catch (Exception e) { info = "Swap refused: " + e.Message; }
                    }
                }
                EditorGUILayout.EndHorizontal();
            }
            if (verifiedFx != null)
                displayedFxFrame = EditorGUILayout.IntSlider(
                    "Manual FX frame scrub", displayedFxFrame, 0,
                    verifiedFx.frame_count - 1);

            EditorGUILayout.BeginHorizontal();
            Rect left = GUILayoutUtility.GetRect(300f, 310f, GUILayout.ExpandWidth(true));
            Rect leftViewport = SyntheticViewport(left, deviceIndex);
            EditorGUI.DrawRect(left, new Color(.055f, .07f, .10f, 1f));
            DrawSprite(leftViewport);
            Rect right = GUILayoutUtility.GetRect(300f, 310f, GUILayout.ExpandWidth(true));
            Rect rightViewport = SyntheticViewport(right, deviceIndex);
            EditorGUI.DrawRect(right, new Color(.055f, .07f, .10f, 1f));
            DrawFx(rightViewport);
            EditorGUILayout.EndHorizontal();
            if (alternateFrames != null && primaryFrames != null &&
                spritePlayback != null && spritePlayback.IsBound)
            {
                int frame = spritePlayback.CurrentFrameIndex;
                int next = Mathf.Clamp(frame, 0, alternateFrames.Length - 1);
                EditorGUILayout.LabelField(
                    "A/B Imported Atlas Source: currently bound vs alternative",
                    EditorStyles.boldLabel);
                EditorGUILayout.BeginHorizontal();
                Rect a = GUILayoutUtility.GetRect(300f, 160f,
                    GUILayout.ExpandWidth(true));
                Rect b = GUILayoutUtility.GetRect(300f, 160f,
                    GUILayout.ExpandWidth(true));
                DrawSprite(a);
                DrawSprite(b, alternateFrames[next]);
                EditorGUILayout.EndHorizontal();
                EditorGUILayout.LabelField("Left=current SpriteRenderer, " +
                    "Right=alternative imported candidate frame " + next +
                    " (preview only, not source parity approval)");
            }
            if (showGuides)
                EditorGUILayout.HelpBox(
                    "SYNTHETIC SAFE-AREA GUIDE ONLY: device=" + Devices[deviceIndex] +
                    ". Actual notch, navigation bar, touch, phone, tablet and GPU " +
                    "validation NOT RUN.", MessageType.Info);
            EditorGUILayout.HelpBox(info, MessageType.Info);
            EditorGUILayout.LabelField("Cue trace", lastCue, EditorStyles.wordWrappedLabel);
            EditorGUILayout.LabelField("Read-only candidate diagnostics",
                EditorStyles.boldLabel);
            EditorGUILayout.LabelField("Sprite frames", primaryFrames == null ?
                "NOT LOADED" : primaryFrames.Length.ToString());
            EditorGUILayout.LabelField("Editor last visual update (ms)",
                lastStepMs.ToString("F4"));
            EditorGUILayout.LabelField("Editor allocated bytes (approx)",
                sampledEditorAlloc.ToString());
            EditorGUILayout.LabelField("Preview particle count",
                particles == null ? "0 / no source" : particles.particleCount.ToString());
            long sourceBytes = sourceSheet == null ? 0L :
                (long)sourceSheet.width * sourceSheet.height * 4L;
            long fxBytes = fxAtlas == null ? 0L :
                (long)fxAtlas.width * fxAtlas.height * 4L;
            EditorGUILayout.LabelField("Uncompressed sprite source bytes (estimate)",
                sourceBytes.ToString());
            EditorGUILayout.LabelField("Uncompressed FX sheet bytes (estimate)",
                fxBytes.ToString());
            EditorGUILayout.LabelField("Frame preview target/CPU", 
                "FPS " + fps.ToString("F0") +
                " / Editor last visual update " + lastStepMs.ToString("F4") + " ms");
            EditorGUILayout.LabelField("GPU draw calls / real device FPS",
                "NOT VERIFIED / NOT RUN");
            EditorGUILayout.LabelField("Scene/Game state and score writes",
                "NONE. Preview-only.");
            if (GUILayout.Button("Copy UNAPPROVED review receipt to clipboard"))
            {
                EditorGUIUtility.systemCopyBuffer = ReceiptJson();
                info = "Copied review receipt JSON to clipboard. " +
                       "All owner/device/Engine/rights PASS fields are FALSE.";
            }
            if (GUILayout.Button("Export UNAPPROVED receipt as NEW file (outside repo)"))
                ExportOwnerReviewReceipt();
            EditorGUILayout.EndScrollView();
        }
    }
}
