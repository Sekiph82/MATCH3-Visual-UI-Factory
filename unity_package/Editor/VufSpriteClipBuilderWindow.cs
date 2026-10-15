// VF-05: manual sprite-sheet/sub-sprite clip authoring, Editor only.
// No gameplay events, reward grants, save writes, paid services or auto-replace.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
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
        private bool loop = true;
        private bool pingPong;
        private bool reducedMotion;
        private double lastTick;
        private double elapsed;
        private bool playing;
        private Vector2 scroll;

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
        }

        private void Tick()
        {
            double now = EditorApplication.timeSinceStartup;
            double delta = Math.Max(0d, Math.Min(0.25d, now - lastTick));
            lastTick = now;
            if (!playing || reducedMotion || sprites.Count == 0)
                return;
            elapsed += delta;
            double step = 1d / fps;
            if (elapsed >= step)
            {
                int count = (int)(elapsed / step);
                elapsed -= count * step;
                int[] sequence = BuildFrameSequence(sprites.Count, pingPong);
                sequenceCursor = (sequenceCursor + count) % sequence.Length;
                frameIndex = sequence[sequenceCursor];
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

            fps = EditorGUILayout.Slider("Frames per second", fps, 1f, 60f);
            loop = EditorGUILayout.Toggle("Loop", loop);
            pingPong = EditorGUILayout.Toggle("Ping-pong", pingPong);
            reducedMotion = EditorGUILayout.Toggle("Reduced-motion preview", reducedMotion);

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
                }
                if (GUILayout.Button("Next"))
                {
                    playing = false;
                    frameIndex = (frameIndex + 1) % sprites.Count;
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
            }
            if (reducedMotion) playing = false;
            Sprite current = sprites[frameIndex];
            Rect target = GUILayoutUtility.GetRect(250, 400, 165, 400,
                GUILayout.ExpandWidth(true), GUILayout.ExpandHeight(true));
            EditorGUI.DrawRect(target, new Color(.09f, .13f, .16f));
            DrawUnpackedSprite(current, target);
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

        private static void DrawUnpackedSprite(Sprite sprite, Rect target)
        {
            if (sprite == null || sprite.texture == null)
                return;
            Rect pixel = sprite.textureRect;
            Texture tex = sprite.texture;
            float aspect = pixel.width / Mathf.Max(1f, pixel.height);
            float h = Mathf.Min(target.height - 12f, (target.width - 12f) / aspect);
            float w = h * aspect;
            Rect drawRect = new Rect(target.center.x - w / 2f, target.center.y - h / 2f, w, h);
            Rect uv = new Rect(pixel.x / tex.width, pixel.y / tex.height,
                pixel.width / tex.width, pixel.height / tex.height);
            GUI.DrawTextureWithTexCoords(drawRect, tex, uv, true);
        }

        private void ReloadSprites()
        {
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
            if (spriteCount < 2 || spriteCount > 4096)
                throw new ArgumentOutOfRangeException(nameof(spriteCount));
            List<int> sequence = Enumerable.Range(0, spriteCount).ToList();
            if (usePingPong && spriteCount > 2)
                for (int n = spriteCount - 2; n > 0; n--)
                    sequence.Add(n);
            return sequence.ToArray();
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
