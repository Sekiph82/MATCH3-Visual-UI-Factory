// VF-06 | Local Unity particle authoring. This tool only creates new CANDIDATE prefabs.
// Does not bind gameplay, mutate scores, use premium API, or overwrite approved assets.
using System;
using System.IO;
using UnityEditor;
using UnityEngine;

namespace Match3.VisualFactory.Editor
{
    public sealed class VufVfxLabWindow : EditorWindow
    {
        private enum Preset { BubbleRise, MatchBurst, StarSparkle, SoftDrift, PortalPulse }
        private Preset preset = Preset.BubbleRise;
        private Color tint = new Color(0.20f, 0.89f, 0.98f, 0.90f);
        private int burstCount = 20;
        private float lifetime = 0.85f;
        private float speed = 2.1f;
        private float particleSize = 0.16f;
        private bool reducedMotion;
        private bool previewPlaying;
        private double startedAt;
        private float manualTime;
        private readonly Vector2[] seeds = new Vector2[160];

        [MenuItem("Tools/MATCH3/VFX Particle Lab")]
        public static void Open()
        {
            var window = GetWindow<VufVfxLabWindow>("VF-06 VFX Lab");
            window.minSize = new Vector2(560, 610);
            window.Show();
        }

        private void OnEnable()
        {
            var random = new System.Random(10061982);
            for (int i = 0; i < seeds.Length; ++i)
                seeds[i] = new Vector2((float)random.NextDouble(),
                    (float)random.NextDouble());
            EditorApplication.update += Tick;
        }

        private void OnDisable()
        {
            EditorApplication.update -= Tick;
        }

        private void Tick()
        {
            if (!previewPlaying || reducedMotion) return;
            manualTime = (float)Math.Max(0.0, EditorApplication.timeSinceStartup - startedAt);
            if (manualTime > lifetime + 1.0f)
            {
                previewPlaying = false;
                manualTime = lifetime;
            }
            Repaint();
        }

        private void ApplyPreset(Preset next)
        {
            preset = next;
            switch (next)
            {
                case Preset.BubbleRise:
                    tint = new Color(.2f, .89f, .98f, .8f);
                    burstCount = 20; lifetime = .85f; speed = 2.1f; particleSize = .16f;
                    break;
                case Preset.MatchBurst:
                    tint = new Color(1f, .73f, .35f, 1f);
                    burstCount = 42; lifetime = .50f; speed = 4.5f; particleSize = .21f;
                    break;
                case Preset.StarSparkle:
                    tint = new Color(1f, .95f, .64f, 1f);
                    burstCount = 25; lifetime = 1f; speed = 1.2f; particleSize = .10f;
                    break;
                case Preset.SoftDrift:
                    tint = new Color(.79f, .64f, 1f, .65f);
                    burstCount = 12; lifetime = 1.75f; speed = .65f; particleSize = .14f;
                    break;
                case Preset.PortalPulse:
                    tint = new Color(.73f, .84f, 1f, .95f);
                    burstCount = 36; lifetime = .75f; speed = 2.9f; particleSize = .18f;
                    break;
            }
            previewPlaying = false;
            manualTime = 0;
        }

        private void OnGUI()
        {
            GUILayout.Label("VF-06  |  Manual Particle Lab", EditorStyles.boldLabel);
            EditorGUILayout.HelpBox(
                "Editable Unity ParticleSystem candidate prefab builder. The preview below is a " +
                "deterministic 2D MOTION SKETCH, not Unity's real particle renderer. " +
                "Use the generated prefab in Unity's Scene/Game view for final particle and shader QA. " +
                "No Engine rule/reward integration is included.", MessageType.Info);
            Preset selected = (Preset)EditorGUILayout.EnumPopup("Preset", preset);
            if (selected != preset) ApplyPreset(selected);
            tint = EditorGUILayout.ColorField("Tint", tint);
            burstCount = EditorGUILayout.IntSlider("Particles per burst", burstCount, 1, 160);
            lifetime = EditorGUILayout.Slider("Particle lifetime (seconds)", lifetime, .1f, 2.5f);
            speed = EditorGUILayout.Slider("Particle speed", speed, .1f, 8f);
            particleSize = EditorGUILayout.Slider("Particle size", particleSize, .03f, .5f);
            reducedMotion = EditorGUILayout.Toggle(
                "Reduced-motion preview (static)", reducedMotion);
            EditorGUILayout.HelpBox(
                "Burst <=160, lifetime <=2.5s. No audio, haptics, shaders or chained match events " +
                "implemented yet. Prefabs are unapproved CANDIDATES.", MessageType.None);
            GUILayout.BeginHorizontal();
            GUI.enabled = !reducedMotion;
            if (GUILayout.Button(previewPlaying ? "Pause sketch" : "Play sketch"))
            {
                if (previewPlaying) previewPlaying = false;
                else
                {
                    startedAt = EditorApplication.timeSinceStartup - manualTime;
                    previewPlaying = true;
                }
            }
            GUI.enabled = true;
            if (GUILayout.Button("Reset sketch"))
            {
                previewPlaying = false;
                manualTime = 0f;
            }
            GUILayout.EndHorizontal();
            float oldTime = manualTime;
            manualTime = EditorGUILayout.Slider("Sketch time", manualTime, 0f, lifetime);
            if (Math.Abs(oldTime - manualTime) > .0001f && previewPlaying)
            {
                previewPlaying = false;
            }
            Rect canvas = GUILayoutUtility.GetRect(500f, 240f,
                GUILayout.ExpandWidth(true));
            EditorGUI.DrawRect(canvas, new Color(.06f, .10f, .14f));
            DrawSketch(canvas);
            GUILayout.Space(12f);
            if (GUILayout.Button("Create new Unity ParticleSystem candidate prefab", GUILayout.Height(38)))
                SaveCandidatePrefab();
        }

        private void DrawSketch(Rect box)
        {
            float t = reducedMotion ? 0f : manualTime;
            int count = reducedMotion ? Math.Min(8, burstCount) : burstCount;
            Vector2 origin = box.center;
            for (int i = 0; i < count; ++i)
            {
                float angle = seeds[i].x * Mathf.PI * 2f;
                float radius = speed * t * 23f * (.6f + .4f * seeds[i].y);
                float dx = Mathf.Cos(angle) * radius;
                float dy = Mathf.Sin(angle) * radius;
                if (preset == Preset.BubbleRise)
                {
                    dx *= .2f;
                    dy = -Mathf.Abs(dy) - t * speed * 24f;
                }
                else if (preset == Preset.SoftDrift)
                {
                    dx *= .45f; dy *= .45f;
                }
                float size = Mathf.Max(2f, particleSize * 55f * (1f - .3f * t / lifetime));
                Rect dot = new Rect(origin.x + dx, origin.y + dy, size, size);
                if (box.Contains(dot.center))
                    EditorGUI.DrawRect(dot, tint);
            }
            GUI.Label(new Rect(box.x + 8f, box.y + 8f, box.width - 16f, 18f),
                reducedMotion ? "REDUCED MOTION | Static fallback sketch" :
                "DETERMINISTIC 2D SKETCH | Real particles require Unity scene preview");
        }

        private void SaveCandidatePrefab()
        {
            string path = EditorUtility.SaveFilePanelInProject(
                "New VFX candidate prefab", "VUF_" + preset + "_CANDIDATE",
                "prefab", "Choose a NEW path for an unapproved ParticleSystem candidate.");
            if (string.IsNullOrEmpty(path)) return;
            if (AssetDatabase.LoadMainAssetAtPath(path) != null || File.Exists(path))
            {
                EditorUtility.DisplayDialog("Protected existing asset",
                    "An asset already exists at this path. Select a new candidate name.", "OK");
                return;
            }
            GameObject particleObject = new GameObject(
                "VUF_" + preset + "_CANDIDATE");
            try
            {
                ParticleSystem system = particleObject.AddComponent<ParticleSystem>();
                var main = system.main;
                main.playOnAwake = false;
                main.loop = false;
                main.duration = Mathf.Max(.11f, lifetime + .1f);
                main.startLifetime = lifetime;
                main.startSpeed = speed;
                main.startSize = particleSize;
                main.startColor = tint;
                main.maxParticles = 160;
                main.simulationSpace = ParticleSystemSimulationSpace.Local;
                var emission = system.emission;
                emission.rateOverTime = 0f;
                emission.SetBursts(new[] {
                    new ParticleSystem.Burst(0f, (short)burstCount)
                });
                var shape = system.shape;
                shape.enabled = true;
                shape.shapeType = ParticleSystemShapeType.Cone;
                shape.angle = preset == Preset.BubbleRise ? 8f : 60f;
                shape.radius = preset == Preset.SoftDrift ? .45f : .12f;
                var sizeOverLifetime = system.sizeOverLifetime;
                sizeOverLifetime.enabled = true;
                sizeOverLifetime.size = new ParticleSystem.MinMaxCurve(1f,
                    AnimationCurve.EaseInOut(0f, 1f, 1f, 0f));
                // The ParticleSystem exists even if the active render pipeline has no
                // compatible material; scene preview must explicitly report that.
                ParticleSystemRenderer renderer = particleObject.GetComponent<ParticleSystemRenderer>();
                if (renderer != null)
                {
                    Shader shader = Shader.Find("Universal Render Pipeline/Particles/Unlit")
                        ?? Shader.Find("Particles/Standard Unlit")
                        ?? Shader.Find("Sprites/Default");
                    if (shader != null)
                    {
                        string matPath = Path.ChangeExtension(path, ".mat");
                        if (AssetDatabase.LoadMainAssetAtPath(matPath) == null && !File.Exists(matPath))
                        {
                            Material material = new Material(shader);
                            if (material.HasProperty("_BaseColor"))
                                material.SetColor("_BaseColor", tint);
                            else if (material.HasProperty("_Color"))
                                material.SetColor("_Color", tint);
                            try
                            {
                                AssetDatabase.CreateAsset(material, matPath);
                                renderer.sharedMaterial = material;
                            }
                            catch
                            {
                                DestroyImmediate(material);
                                throw;
                            }
                        }
                        else
                        {
                            // Do not reuse or alter possibly owner-approved materials.
                            renderer.sharedMaterial = null;
                            Debug.LogWarning("VUF VFX: matching material path is occupied; " +
                                "the candidate prefab requires a separately reviewed material.");
                        }
                    }
                }
                GameObject saved = PrefabUtility.SaveAsPrefabAsset(particleObject, path);
                if (saved == null)
                    throw new InvalidOperationException("Unity failed to create candidate prefab");
                AssetDatabase.SaveAssets();
                Selection.activeObject = saved;
                EditorGUIUtility.PingObject(saved);
            }
            finally
            {
                DestroyImmediate(particleObject);
            }
        }
    }
}
