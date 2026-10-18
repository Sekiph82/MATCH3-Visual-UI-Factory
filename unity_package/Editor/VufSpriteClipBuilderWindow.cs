// VF-05: manual sprite-sheet/sub-sprite clip authoring, Editor only.
// No gameplay events, reward grants, save writes, paid services or auto-replace.
using System;
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEngine;

namespace Match3.VisualFactory.Editor
{
    public sealed class VufSpriteClipBuilderWindow : EditorWindow
    {
        private Texture2D source;
        private readonly List<Sprite> sprites = new List<Sprite>();
        private int frameIndex;
        private int sequenceCursor;
        private float fps = 12f;
        private static readonly float[] PreviewSpeeds = { .25f, .5f, 1f, 2f };
        private static readonly string[] SpeedLabels = { "0.25×", "0.5×", "1×", "2×" };
        private int previewSpeedIndex = 2;
        private bool showPivotGuide = true;
        private bool showAlphaCheckerboard = true;
        private float previewZoom = 1f;
        private Texture2D alternateAtlas;
        private bool loop = true;
        private bool pingPong;
        private bool reducedMotion;
        private double lastTick;
        private double elapsed;
        private bool playing;
        private Vector2 scroll;
        private GameObject temporaryScenePreview;
        private VufSpritePlaybackPreview temporaryPlayback;
        private string previewIssue;

        [MenuItem("Tools/MATCH3/Sprite Animation Builder")]
        public static void Open()
        {
            var window = GetWindow<VufSpriteClipBuilderWindow>("VUF Animation Builder");
            window.minSize = new Vector2(520f, 460f);
            window.Show();
        }

        private void OnEnable()
        {
            lastTick = EditorApplication.timeSinceStartup;
            EditorApplication.update += Tick;
        }

        private void OnDisable()
        {
            EditorApplication.update -= Tick;
            RemoveTemporaryScenePreview();
        }

        private void Tick()
        {
            double now = EditorApplication.timeSinceStartup;
            double delta = Math.Max(0d, Math.Min(0.25d, now - lastTick));
            lastTick = now;
            if (!playing || reducedMotion || sprites.Count == 0)
                return;
            elapsed += delta * PreviewSpeeds[previewSpeedIndex];
            double step = 1d / fps;
            if (elapsed >= step)
            {
                int count = (int)(elapsed / step);
                elapsed -= count * step;
                int[] sequence = BuildFrameSequence(sprites.Count, pingPong);
                sequenceCursor = (sequenceCursor + count) % sequence.Length;
                frameIndex = sequence[sequenceCursor];
                SyncTemporarySceneFrame();
                Repaint();
            }
        }

        private void OnGUI()
        {
            EditorGUILayout.LabelField("VF-05  |  Sprite Animation Builder", EditorStyles.boldLabel);
            EditorGUILayout.HelpBox(
                "Manual Unity Sprite -> SpriteRenderer .anim clip. Input must be original/licensed " +
                "and imported as Sprite (Multiple). No skeletal/3D rig editor yet. " +
                "Generated clips are candidates until owner acceptance.",
                MessageType.Info);
            EditorGUI.BeginChangeCheck();
            source = (Texture2D)EditorGUILayout.ObjectField("Imported sheet", source,
                typeof(Texture2D), false);
            if (EditorGUI.EndChangeCheck())
                ReloadSprites();

            EditorGUI.BeginChangeCheck();
            fps = EditorGUILayout.Slider("Frames per second", fps, 1f, 60f);
            loop = EditorGUILayout.Toggle("Loop", loop);
            pingPong = EditorGUILayout.Toggle("Ping-pong", pingPong);
            reducedMotion = EditorGUILayout.Toggle("Reduced-motion preview", reducedMotion);
            previewSpeedIndex = EditorGUILayout.Popup("View-only playback speed",
                previewSpeedIndex, SpeedLabels);
            showPivotGuide = EditorGUILayout.Toggle("Show source pivot crosshair",
                showPivotGuide);
            bool changedPlayback = EditorGUI.EndChangeCheck();
            showAlphaCheckerboard = EditorGUILayout.Toggle(
                "Check transparent edge pixels", showAlphaCheckerboard);
            previewZoom = EditorGUILayout.Slider("Preview-only zoom",
                previewZoom, .25f, 3f);
            if (temporaryScenePreview != null)
                temporaryScenePreview.transform.localScale = Vector3.one * previewZoom;
            if (changedPlayback && temporaryPlayback != null)
                RebindTemporaryScenePreview();

            if (source == null)
            {
                EditorGUILayout.HelpBox("Select a Sprite (Multiple) sheet imported in Unity.", MessageType.Warning);
                return;
            }
            EditorGUILayout.LabelField("Detected sub-sprites", sprites.Count.ToString());
            if (sprites.Count < 2)
            {
                EditorGUILayout.HelpBox("At least two unrotated sprites are required. " +
                    "In the Unity Texture Importer, choose Sprite (2D and UI), Multiple, " +
                    "open Sprite Editor, slice the sheet and Apply.", MessageType.Warning);
                return;
            }
            string alignmentMessage;
            if (!CheckFrameAlignment(sprites, out alignmentMessage))
                EditorGUILayout.HelpBox(alignmentMessage + " No sprite/importer is modified.",
                    MessageType.Warning);
            using (new EditorGUILayout.HorizontalScope())
            {
                GUI.enabled = !reducedMotion;
                if (GUILayout.Button(playing ? "Pause" : "Play"))
                {
                    if (!playing)
                        sequenceCursor = Array.IndexOf(
                            BuildFrameSequence(sprites.Count, pingPong), frameIndex);
                    playing = !playing;
                }
                GUI.enabled = true;
                if (GUILayout.Button("Previous"))
                {
                    playing = false;
                    frameIndex = (frameIndex + sprites.Count - 1) % sprites.Count;
                    SyncTemporarySceneFrame();
                }
                if (GUILayout.Button("Next"))
                {
                    playing = false;
                    frameIndex = (frameIndex + 1) % sprites.Count;
                    SyncTemporarySceneFrame();
                }
            }
            int scrubbedFrame = EditorGUILayout.IntSlider(
                "Frame scrub", frameIndex, 0, sprites.Count - 1);
            if (scrubbedFrame != frameIndex)
            {
                playing = false;
                frameIndex = scrubbedFrame;
                sequenceCursor = Array.IndexOf(
                    BuildFrameSequence(sprites.Count, pingPong), frameIndex);
                SyncTemporarySceneFrame();
            }
            if (reducedMotion) playing = false;
            Sprite current = sprites[frameIndex];
            Rect target = GUILayoutUtility.GetRect(250, 400, 165, 400,
                GUILayout.ExpandWidth(true), GUILayout.ExpandHeight(true));
            EditorGUI.DrawRect(target, new Color(.09f, .13f, .16f));
            DrawUnpackedSprite(current, target, showPivotGuide,
                previewZoom, showAlphaCheckerboard);
            alternateAtlas = (Texture2D)EditorGUILayout.ObjectField(
                "Optional alternative atlas (read only)",
                alternateAtlas, typeof(Texture2D), false);
            using (new EditorGUI.DisabledScope(temporaryPlayback == null ||
                alternateAtlas == null))
            {
                if (GUILayout.Button("Preview safe in-memory atlas swap"))
                    TrySwapTemporaryAtlas();
            }
            if (GUILayout.Button(temporaryScenePreview == null ?
                    "Create TEMPORARY real SpriteRenderer preview in Scene" :
                    "Remove TEMPORARY real SpriteRenderer preview"))
            {
                if (temporaryScenePreview != null) RemoveTemporaryScenePreview();
                else CreateTemporaryScenePreview();
            }
            if (!String.IsNullOrEmpty(previewIssue))
                EditorGUILayout.HelpBox(previewIssue, MessageType.Warning);
            EditorGUILayout.LabelField("Current frame", current.name);
            EditorGUILayout.LabelField("Pivot (normalized)", current.pivot.ToString());
            EditorGUILayout.LabelField("Animation build authority: presentation only", EditorStyles.miniLabel);
            GUI.enabled = sprites.Count >= 2;
            if (GUILayout.Button("Create candidate SpriteRenderer animation (.anim)", GUILayout.Height(32)))
                SaveClip();
            GUI.enabled = true;

            scroll = EditorGUILayout.BeginScrollView(scroll, GUILayout.MaxHeight(70));
            foreach (Sprite sprite in sprites)
                EditorGUILayout.LabelField(sprite.name, EditorStyles.miniLabel);
            EditorGUILayout.EndScrollView();
        }

        private static void DrawUnpackedSprite(Sprite sprite, Rect target,
            bool drawPivotGuide, float zoom, bool alphaCheckerboard)
        {
            if (sprite == null || sprite.texture == null)
                return;
            Rect pixel = sprite.textureRect;
            Texture tex = sprite.texture;
            float aspect = pixel.width / Mathf.Max(1f, pixel.height);
            float h = Mathf.Min(target.height - 12f, (target.width - 12f) / aspect) * zoom;
            float w = h * aspect;
            GUI.BeginGroup(target); // clips intentionally zoomed Sprite edges
            if (alphaCheckerboard)
            {
                const float square = 18f;
                int cols = Mathf.CeilToInt(target.width / square);
                int rows = Mathf.CeilToInt(target.height / square);
                for (int row = 0; row < rows; ++row)
                    for (int col = 0; col < cols; ++col)
                        EditorGUI.DrawRect(new Rect(col * square, row * square,
                            square, square), (row + col) % 2 == 0 ?
                            new Color(.27f, .28f, .31f, 1f) :
                            new Color(.46f, .47f, .51f, 1f));
            }
            Rect drawRect = new Rect((target.width - w) / 2f,
                (target.height - h) / 2f, w, h);
            Rect uv = new Rect(pixel.x / tex.width, pixel.y / tex.height,
                pixel.width / tex.width, pixel.height / tex.height);
            GUI.DrawTextureWithTexCoords(drawRect, tex, uv, true);
            if (drawPivotGuide)
            {
                // Imported Sprite.pivot is in bottom-left sprite pixels;
                // Unity IMGUI preview is top-left. This guide is visual only.
                float px = drawRect.x + drawRect.width * sprite.pivot.x / pixel.width;
                float py = drawRect.y + drawRect.height *
                    (1f - sprite.pivot.y / pixel.height);
                Color tint = new Color(.2f, 1f, .75f, .8f);
                EditorGUI.DrawRect(new Rect(px - .5f, drawRect.y, 1f,
                    drawRect.height), tint);
                EditorGUI.DrawRect(new Rect(drawRect.x, py - .5f,
                    drawRect.width, 1f), tint);
            }
            GUI.EndGroup();
        }

        private void ReloadSprites()
        {
            RemoveTemporaryScenePreview();
            playing = false;
            frameIndex = 0;
            sequenceCursor = 0;
            elapsed = 0;
            sprites.Clear();
            if (source == null) return;
            string path = AssetDatabase.GetAssetPath(source);
            if (string.IsNullOrEmpty(path)) return;
            foreach (UnityEngine.Object item in AssetDatabase.LoadAllAssetsAtPath(path))
            {
                Sprite sprite = item as Sprite;
                if (sprite != null && !sprite.packed)
                    sprites.Add(sprite);
            }
            sprites.Sort((a, b) => NaturalSpriteNameOrder(a.name, b.name));
        }


        // New nonserialized, Editor-only SpriteRenderer preview. Never persists
        // in a scene or asset. No existing scene objects are touched.
        private void CreateTemporaryScenePreview()
        {
            previewIssue = null;
            if (sprites.Count < 2 || temporaryScenePreview != null) return;
            GameObject created = null;
            try
            {
                created = new GameObject(
                    "VUF_TEMP_RealSpritePreview_DONT_SAVE",
                    typeof(SpriteRenderer), typeof(VufSpritePlaybackPreview));
                created.hideFlags = HideFlags.DontSaveInEditor | HideFlags.DontSaveInBuild;
                created.transform.localScale = Vector3.one * previewZoom;
                var renderer = created.GetComponent<SpriteRenderer>();
                renderer.sortingOrder = 999;
                var playback = created.GetComponent<VufSpritePlaybackPreview>();
                playback.Bind(sprites.ToArray(), fps, loop, pingPong, reducedMotion);
                temporaryScenePreview = created;
                temporaryPlayback = playback;
                SyncTemporarySceneFrame();
                Selection.activeGameObject = created; // explicit owner button
                previewIssue = "VIEW ONLY: real Unity SpriteRenderer in Scene. " +
                    "Never saved. Press F in Scene view to frame. " +
                    "Closing this Builder removes only this temporary preview.";
            }
            catch (Exception e)
            {
                if (created != null) DestroyImmediate(created);
                temporaryScenePreview = null;
                temporaryPlayback = null;
                previewIssue = "Scene preview could not be created: " + e.Message;
            }
        }

        private void TrySwapTemporaryAtlas()
        {
            if (temporaryPlayback == null || alternateAtlas == null)
                return;
            try
            {
                string path = AssetDatabase.GetAssetPath(alternateAtlas);
                if (String.IsNullOrEmpty(path) ||
                    !path.StartsWith("Assets/", StringComparison.Ordinal) ||
                    !path.EndsWith(".png", StringComparison.OrdinalIgnoreCase))
                    throw new ArgumentException("Alternate must be an imported Assets PNG copy");
                var replacements = new List<Sprite>();
                foreach (UnityEngine.Object asset in AssetDatabase.LoadAllAssetsAtPath(path))
                {
                    Sprite frame = asset as Sprite;
                    if (frame != null && !frame.packed) replacements.Add(frame);
                }
                replacements.Sort((a, b) => NaturalSpriteNameOrder(a.name, b.name));
                temporaryPlayback.SwapCandidateAtlas(replacements.ToArray());
                previewIssue = "Actual temporary Scene SpriteRenderer now uses " +
                    "alternative imported sprites; immutable Sprite geometry " +
                    "was checked. No TextureImporter or project asset changed.";
            }
            catch (Exception error)
            {
                // Runtime swap is transactional. Invalid alternatives leave
                // the previous atlas and renderer unchanged.
                previewIssue = "Candidate atlas swap REFUSED: " + error.Message;
            }
        }

        private void RebindTemporaryScenePreview()
        {
            if (temporaryPlayback == null || sprites.Count < 2) return;
            try
            {
                temporaryPlayback.Bind(sprites.ToArray(), fps, loop, pingPong, reducedMotion);
                SyncTemporarySceneFrame();
            }
            catch (Exception error)
            {
                previewIssue = "Read-only Scene preview rebind refused: " + error.Message;
                RemoveTemporaryScenePreview();
            }
        }

        private void SyncTemporarySceneFrame()
        {
            if (temporaryPlayback != null && temporaryPlayback.IsBound &&
                frameIndex >= 0 && frameIndex < sprites.Count)
                temporaryPlayback.ScrubFrame(frameIndex);
        }

        private void RemoveTemporaryScenePreview()
        {
            if (temporaryScenePreview != null)
                DestroyImmediate(temporaryScenePreview);
            temporaryScenePreview = null;
            temporaryPlayback = null;
        }


        // Diagnostics only. Real artist frames may intentionally vary; report
        // drift rather than silently aligning or mutating source importers.
        internal static bool CheckFrameAlignment(IList<Sprite> frames,
            out string explanation)
        {
            explanation = "Candidate frames ready for manual visual review";
            if (frames == null || frames.Count < 2)
            {
                explanation = "At least two source sprites are required";
                return false;
            }
            Sprite original = frames[0];
            if (original == null || original.rect.width <= 0f ||
                original.rect.height <= 0f || original.pixelsPerUnit <= 0f)
            {
                explanation = "Reference sprite rect or PPU is invalid";
                return false;
            }
            Vector2 origin = new Vector2(
                original.pivot.x / original.rect.width,
                original.pivot.y / original.rect.height);
            float ppu = original.pixelsPerUnit;
            for (int i = 1; i < frames.Count; i++)
            {
                Sprite frame = frames[i];
                if (frame == null || frame.rect.width <= 0f ||
                    frame.rect.height <= 0f || frame.pixelsPerUnit <= 0f)
                {
                    explanation = "Null or malformed sprite frame at " + i;
                    return false;
                }
                Vector2 center = new Vector2(
                    frame.pivot.x / frame.rect.width,
                    frame.pivot.y / frame.rect.height);
                if ((origin - center).sqrMagnitude > .000001f ||
                    Mathf.Abs(ppu - frame.pixelsPerUnit) > .0001f)
                {
                    explanation = "Candidate pivot/PPU drift near frame " + i +
                        "; verify intentional motion with pivot crosshair";
                    return false;
                }
            }
            return true;
        }

        private static int NaturalSpriteNameOrder(string a, string b)
        {
            int aStart = a.Length;
            int bStart = b.Length;
            while (aStart > 0 && char.IsDigit(a[aStart - 1])) aStart--;
            while (bStart > 0 && char.IsDigit(b[bStart - 1])) bStart--;
            string prefixA = a.Substring(0, aStart);
            string prefixB = b.Substring(0, bStart);
            int prefix = string.Compare(prefixA, prefixB, StringComparison.Ordinal);
            if (prefix != 0) return prefix;
            if (aStart < a.Length && bStart < b.Length)
            {
                long numberA, numberB;
                if (long.TryParse(a.Substring(aStart), out numberA)
                    && long.TryParse(b.Substring(bStart), out numberB))
                {
                    int numberOrder = numberA.CompareTo(numberB);
                    if (numberOrder != 0) return numberOrder;
                }
            }
            return string.Compare(a, b, StringComparison.Ordinal);
        }

        internal static int[] BuildFrameSequence(int spriteCount, bool usePingPong)
        {
            // One identical view-only frame-order implementation is shared
            // with the new real SpriteRenderer runtime preview component.
            return VufSpritePlaybackPreview.FrameSequence(spriteCount, usePingPong);
        }

        private void SaveClip()
        {
            if (sprites.Count < 2)
                return;
            string path = EditorUtility.SaveFilePanelInProject(
                "Save new candidate animation", source.name + "_Candidate",
                "anim", "Choose a new asset path. Existing clips cannot be overwritten.");
            if (string.IsNullOrEmpty(path)) return;
            if (AssetDatabase.LoadMainAssetAtPath(path) != null || File.Exists(path))
            {
                EditorUtility.DisplayDialog("Candidate protected",
                    "The target asset exists. Select a new path to avoid overwriting an approved clip.",
                    "OK");
                return;
            }
            AnimationClip clip = BuildCandidateClip(
                Path.GetFileNameWithoutExtension(path), sprites, fps, pingPong, loop);
            AssetDatabase.CreateAsset(clip, path);
            AssetDatabase.SaveAssets();
            Selection.activeObject = clip;
            EditorGUIUtility.PingObject(clip);
        }

        // Builds a genuine Unity sprite-reference AnimationClip without creating an
        // AssetDatabase file, so tests can inspect keyframes entirely in memory.
        internal static AnimationClip BuildCandidateClip(string clipName,
            IList<Sprite> sourceSprites, float framesPerSecond, bool usePingPong, bool shouldLoop)
        {
            if (sourceSprites == null || sourceSprites.Count < 2)
                throw new ArgumentException("At least two sprites are required.", nameof(sourceSprites));
            if (float.IsNaN(framesPerSecond) || float.IsInfinity(framesPerSecond) ||
                framesPerSecond <= 0f)
                throw new ArgumentOutOfRangeException(nameof(framesPerSecond));
            for (int i = 0; i < sourceSprites.Count; ++i)
                if (sourceSprites[i] == null)
                    throw new ArgumentException("Sprite frames must not be null.", nameof(sourceSprites));

            int[] sequence = BuildFrameSequence(sourceSprites.Count, usePingPong);
            var keys = new ObjectReferenceKeyframe[sequence.Length + 1];
            for (int i = 0; i < sequence.Length; i++)
            {
                keys[i] = new ObjectReferenceKeyframe {
                    time = i / framesPerSecond, value = sourceSprites[sequence[i]]
                };
            }
            keys[sequence.Length] = new ObjectReferenceKeyframe {
                time = sequence.Length / framesPerSecond,
                value = sourceSprites[shouldLoop ? sequence[0] : sequence[sequence.Length - 1]]
            };
            AnimationClip clip = new AnimationClip {
                frameRate = framesPerSecond,
                name = String.IsNullOrEmpty(clipName) ? "VUF_Candidate_Animation" : clipName
            };
            AnimationUtility.SetObjectReferenceCurve(clip,
                EditorCurveBinding.PPtrCurve("", typeof(SpriteRenderer), "m_Sprite"),
                keys);
            AnimationClipSettings settings = AnimationUtility.GetAnimationClipSettings(clip);
            settings.loopTime = shouldLoop;
            AnimationUtility.SetAnimationClipSettings(clip, settings);
            return clip;
        }
    }
}
