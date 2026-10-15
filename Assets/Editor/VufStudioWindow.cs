// M00: isolated authoring preview. No Engine or LevelFactory dependency.
using System;
using UnityEditor;
using UnityEngine;

namespace Match3.VisualFactory.Editor
{
    public sealed class VufStudioWindow : EditorWindow
    {
        private static readonly string[] Profiles = {
            "Coral Rescue", "Garage Legends", "Dino Islands",
            "The Fractured Realms", "Wonder Pop"
        };
        private static readonly string[] Views = {
            "Board", "Sprite", "Animation", "VFX", "UI", "World",
            "Audio", "Device", "Performance", "Replay", "Asset QA"
        };
        private static readonly string[] States = {
            "Ready", "Loading", "Offline", "Error", "Owned",
            "Claimed", "Disabled", "Pending"
        };
        private static readonly string[] Devices = {
            "Tall Phone 19.5:9", "Android 20:9", "Compact Phone 16:9", "Tablet 4:3"
        };
        private static readonly float[] Aspects = { 9f / 19.5f, 9f / 20f, 9f / 16f, 3f / 4f };
        private static readonly float[] Speeds = { .25f, .5f, 1f, 2f };

        private Texture2D source;
        private int profileIndex;
        private int viewIndex = 1;
        private int stateIndex;
        private int deviceIndex;
        private int frames = 1;
        private int frame;
        private int speedIndex = 2;
        private float framesPerSecond = 12f;
        private bool playing;
        private bool showSafeArea = true;
        private bool reducedMotion;
        private double lastUpdate;
        private double frameAccumulator;

        [MenuItem("Tools/MATCH3/Visual & UI Factory Studio")]
        public static void Open()
        {
            var window = GetWindow<VufStudioWindow>("MATCH3 Visual Factory");
            window.minSize = new Vector2(680, 540);
            window.Show();
        }

        private void OnEnable()
        {
            lastUpdate = EditorApplication.timeSinceStartup;
            EditorApplication.update += Tick;
        }

        private void OnDisable()
        {
            EditorApplication.update -= Tick;
        }

        private void Tick()
        {
            double now = EditorApplication.timeSinceStartup;
            double elapsed = Math.Max(0, Math.Min(.25, now - lastUpdate));
            lastUpdate = now;
            if (!playing || reducedMotion || source == null || frames < 2)
                return;
            frameAccumulator += elapsed * framesPerSecond * Speeds[speedIndex];
            if (frameAccumulator >= 1d)
            {
                int advance = (int)frameAccumulator;
                frame = (frame + advance) % frames;
                frameAccumulator -= advance;
                Repaint();
            }
        }

        private void OnGUI()
        {
            EditorGUILayout.Space(8);
            EditorGUILayout.LabelField("VISUAL & UI FACTORY  |  M00 PREVIEW", EditorStyles.boldLabel);
            EditorGUILayout.HelpBox(
                "Manual source preview only. Art generation, VFX simulation, runtime bindings, audio/haptics and export are NOT IMPLEMENTED.",
                MessageType.Info);
            profileIndex = EditorGUILayout.Popup("Game profile", profileIndex, Profiles);
            viewIndex = EditorGUILayout.Popup("Inspection lab", viewIndex, Views);
            stateIndex = EditorGUILayout.Popup("Symbolic UI state", stateIndex, States);
            deviceIndex = EditorGUILayout.Popup("Device ratio (simulated)", deviceIndex, Devices);
            showSafeArea = EditorGUILayout.Toggle("Simulated safe-area guide", showSafeArea);
            reducedMotion = EditorGUILayout.Toggle("Reduced motion", reducedMotion);
            source = (Texture2D)EditorGUILayout.ObjectField("Original/licensed texture", source, typeof(Texture2D), false);

            if (viewIndex != 1 && viewIndex != 2 && viewIndex != 7)
            {
                EditorGUILayout.HelpBox(Views[viewIndex] +
                    " Lab is UNSUPPORTED in M00. A named tab is not an implemented test.",
                    MessageType.Warning);
            }

            DrawFrameControls();

            GUILayout.Space(6);
            Rect outer = GUILayoutUtility.GetRect(100, 10000, 140, 10000,
                GUILayout.ExpandWidth(true), GUILayout.ExpandHeight(true));
            EditorGUI.DrawRect(outer, new Color(.08f, .10f, .14f));
            float aspect = Aspects[deviceIndex];
            float height = Mathf.Min(outer.height - 14f, (outer.width - 14f) / aspect);
            float width = height * aspect;
            Rect portrait = new Rect(outer.center.x - width * .5f,
                outer.center.y - height * .5f, width, height);
            EditorGUI.DrawRect(portrait, new Color(.14f, .19f, .23f));
            if (source != null)
            {
                float fraction = 1f / Mathf.Max(1, frames);
                Rect texCoords = new Rect(frame * fraction, 0f, fraction, 1f);
                GUI.DrawTextureWithTexCoords(portrait, source, texCoords, true);
            }
            else
            {
                GUI.Label(portrait, "Select an imported Texture2D for preview",
                    CenteredWhite());
            }
            if (showSafeArea)
            {
                Rect safe = new Rect(portrait.x + portrait.width * .035f,
                    portrait.y + portrait.height * .045f,
                    portrait.width * .93f, portrait.height * .91f);
                Handles.BeginGUI();
                Handles.color = Color.cyan;
                Handles.DrawSolidRectangleWithOutline(safe, Color.clear,
                    new Color(0f, 1f, 1f, .7f));
                Handles.EndGUI();
            }
            EditorGUILayout.LabelField(
                Profiles[profileIndex] + " / " + Views[viewIndex] + " / " +
                States[stateIndex] + " / frame " + (frame + 1) + "/" + frames);
            EditorGUILayout.LabelField(
                "PREVIEW ONLY  |  No real-device, provenance or owner-approval PASS",
                EditorStyles.miniLabel);
        }

        private void DrawFrameControls()
        {
            frames = Mathf.Clamp(EditorGUILayout.IntField("Horizontal sheet frames", frames), 1, 512);
            frame = Mathf.Clamp(frame, 0, frames - 1);
            framesPerSecond = EditorGUILayout.Slider("Animation FPS", framesPerSecond, 1f, 60f);
            speedIndex = EditorGUILayout.Popup("Playback speed", speedIndex,
                new[] { "0.25x", "0.5x", "1x", "2x" });
            using (new EditorGUILayout.HorizontalScope())
            {
                GUI.enabled = source != null && !reducedMotion && frames > 1;
                if (GUILayout.Button(playing ? "Pause" : "Play"))
                {
                    playing = !playing;
                    frameAccumulator = 0;
                }
                if (GUILayout.Button("Previous")) { playing = false; frame = (frame + frames - 1) % frames; }
                if (GUILayout.Button("Next")) { playing = false; frame = (frame + 1) % frames; }
                GUI.enabled = true;
            }
            frame = EditorGUILayout.IntSlider("Scrub frame", frame, 0, frames - 1);
            if (reducedMotion && playing) playing = false;
        }

        private static GUIStyle CenteredWhite()
        {
            var style = new GUIStyle(EditorStyles.centeredGreyMiniLabel);
            style.normal.textColor = Color.white;
            style.wordWrap = true;
            return style;
        }
    }
}
