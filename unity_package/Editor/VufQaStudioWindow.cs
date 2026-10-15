// VF-09 prototype: manual prefab audit browser, not an automated Unity acceptance test.
using System;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.UI;

namespace Match3.VisualFactory.Editor
{
    public sealed class VufQaStudioWindow : EditorWindow
    {
        private static readonly string[] Profiles = {
            "Coral Rescue", "Garage Legends", "Dino Islands",
            "The Fractured Realms", "Wonder Pop"
        };
        private static readonly string[] States = {
            "Ready", "Loading", "Offline", "Error",
            "Owned", "Claimed", "Disabled", "Pending"
        };
        private GameObject candidate;
        private Texture2D image;
        private AnimationClip clip;
        private int profileIndex;
        private int stateIndex;
        private readonly List<string> findings = new List<string>();
        private Vector2 scroll;

        [MenuItem("Tools/MATCH3/Manual Visual QA Studio")]
        public static void Open()
        {
            var window = GetWindow<VufQaStudioWindow>("VF-09 Manual QA");
            window.minSize = new Vector2(590f, 520f);
            window.Show();
        }

        private void OnGUI()
        {
            GUILayout.Label("VF-09 | Manual Asset/Prefab Inspection", EditorStyles.boldLabel);
            EditorGUILayout.HelpBox(
                "Candidate structural inspection only. Game/state dropdowns change the audit " +
                "label; they do NOT simulate Engine gameplay. Real Unity prefab render, " +
                "GPU/device QA, tactile button actions, shader performance, rights and " +
                "owner aesthetic approval remain separate required tests.", MessageType.Info);
            profileIndex = EditorGUILayout.Popup("Review profile label", profileIndex, Profiles);
            stateIndex = EditorGUILayout.Popup("Review state label", stateIndex, States);
            candidate = (GameObject)EditorGUILayout.ObjectField(
                "Prefab / scene asset", candidate, typeof(GameObject), false);
            image = (Texture2D)EditorGUILayout.ObjectField(
                "Original sprite texture", image, typeof(Texture2D), false);
            clip = (AnimationClip)EditorGUILayout.ObjectField(
                "Animation clip", clip, typeof(AnimationClip), false);
            using (new EditorGUILayout.HorizontalScope())
            {
                if (GUILayout.Button("Inspect selected candidates", GUILayout.Height(32f)))
                    Inspect();
                GUI.enabled = candidate != null && PrefabUtility.IsPartOfPrefabAsset(candidate);
                if (GUILayout.Button("Open actual Unity prefab", GUILayout.Height(32f)))
                    AssetDatabase.OpenAsset(candidate);
                GUI.enabled = true;
            }
            GUILayout.Space(12f);
            EditorGUILayout.LabelField("QA findings (no automatic approval)", EditorStyles.boldLabel);
            scroll = EditorGUILayout.BeginScrollView(scroll);
            if (findings.Count == 0)
            {
                EditorGUILayout.HelpBox("No inspection performed. Select a candidate and press Inspect.",
                    MessageType.None);
            }
            foreach (string finding in findings)
                EditorGUILayout.SelectableLabel(finding, EditorStyles.wordWrappedLabel,
                    GUILayout.MinHeight(25f));
            EditorGUILayout.EndScrollView();
            EditorGUILayout.HelpBox(
                "Manual acceptance is always BLOCKED until signed original-asset licence, " +
                "Unity render/functional QA, real device and owner review evidence exist.",
                MessageType.Warning);
        }

        private void Inspect()
        {
            findings.Clear();
            findings.Add("PROFILE: " + Profiles[profileIndex] + " | STATE: " + States[stateIndex]);
            if (candidate != null)
            {
                string path = AssetDatabase.GetAssetPath(candidate);
                bool prefab = PrefabUtility.IsPartOfPrefabAsset(candidate);
                findings.Add("PREFAB: " + (prefab ? path : "NOT A PREFAB ASSET"));
                Canvas[] canvases = candidate.GetComponentsInChildren<Canvas>(true);
                Button[] buttons = candidate.GetComponentsInChildren<Button>(true);
                Text[] labels = candidate.GetComponentsInChildren<Text>(true);
                Image[] images = candidate.GetComponentsInChildren<Image>(true);
                VufSafeAreaFitter[] safe = candidate.GetComponentsInChildren<VufSafeAreaFitter>(true);
                ParticleSystem[] particles = candidate.GetComponentsInChildren<ParticleSystem>(true);
                findings.Add("uGUI Canvas=" + canvases.Length + " Button=" + buttons.Length +
                    " Text=" + labels.Length + " Image=" + images.Length);
                findings.Add("Safe area fitter=" + safe.Length +
                    " Particle systems=" + particles.Length);
                int enabledUnbound = 0;
                foreach (Button button in buttons)
                {
                    if (button == null) continue;
                    int calls = button.onClick == null ? 0 : button.onClick.GetPersistentEventCount();
                    if (button.interactable && calls == 0) enabledUnbound++;
                }
                if (enabledUnbound > 0)
                    findings.Add("BLOCKED: " + enabledUnbound +
                        " enabled button(s) lack serialized callbacks. " +
                        "Runtime-only bindings must be reviewed separately.");
                else if (buttons.Length > 0)
                    findings.Add("Buttons have no enabled-without-persistent-binding findings. " +
                        "Actual action tests still REQUIRED.");
                if (canvases.Length > 0 && safe.Length == 0)
                    findings.Add("BLOCKED: Canvas has no VUF safe-area fitter. " +
                        "Alternative proven safe-area policy must be reviewed.");
                foreach (ParticleSystem ps in particles)
                {
                    var main = ps.main;
                    findings.Add("ParticleSystem " + ps.name + ": maxParticles=" +
                        main.maxParticles + ", startLifetime max=" + main.startLifetime.constantMax);
                    if (main.maxParticles > 160)
                        findings.Add("BLOCKED: effect exceeds default 160-particle prototype budget.");
                    var renderer = ps.GetComponent<ParticleSystemRenderer>();
                    if (renderer == null || renderer.sharedMaterial == null)
                        findings.Add("BLOCKED: ParticleSystem has no reviewed renderer material.");
                }
                Component[] all = candidate.GetComponentsInChildren<Component>(true);
                foreach (Component component in all)
                    if (component == null)
                        findings.Add("BLOCKED: missing serialized component/script.");
            }
            if (image != null)
            {
                string path = AssetDatabase.GetAssetPath(image);
                findings.Add("TEXTURE: " + path + " | " + image.width + "x" + image.height);
                TextureImporter importer = AssetImporter.GetAtPath(path) as TextureImporter;
                if (importer == null)
                    findings.Add("BLOCKED: texture has no Unity TextureImporter.");
                else
                {
                    findings.Add("Importer: " + importer.textureType +
                        " | Sprite mode: " + importer.spriteImportMode +
                        " | readable: " + importer.isReadable);
                    if (importer.textureType != TextureImporterType.Sprite)
                        findings.Add("BLOCKED: image is not imported as a Sprite.");
                }
            }
            if (clip != null)
            {
                findings.Add("CLIP: " + AssetDatabase.GetAssetPath(clip) +
                    " | length=" + clip.length.ToString("F3") + "s" +
                    " | frameRate=" + clip.frameRate.ToString("F2"));
                if (clip.length <= 0f)
                    findings.Add("BLOCKED: animation length <= 0.");
            }
            if (candidate == null && image == null && clip == null)
                findings.Add("No candidates selected.");
            findings.Add("FINAL STATUS: REVIEW_REQUIRED (never auto-approved)");
        }
    }
}
