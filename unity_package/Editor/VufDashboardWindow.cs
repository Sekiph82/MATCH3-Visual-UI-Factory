using UnityEditor;
using UnityEngine;

namespace Match3.VisualFactory.Editor
{
    public sealed class VufDashboardWindow : EditorWindow
    {
        private static readonly string[] Profiles = {
            "Coral Rescue", "Garage Legends", "Dino Islands",
            "The Fractured Realms", "Wonder Pop"
        };
        private static readonly string[] Modules = {
            "VF-01  Style Bible & Visual Director",
            "VF-02  Asset Catalog, Versioning & Receipts",
            "VF-03  Provider-neutral AI / Manual Intake",
            "VF-04  Image Processing & Atlases",
            "VF-05  Character Animation",
            "VF-06  VFX, Shader & Particles",
            "VF-07  Interactive Screen / UI Composer",
            "VF-08  Responsive Layout & Safe Areas",
            "VF-09  Visual Quality & Performance QA",
            "VF-10  Unity Integration / Export"
        };
        private static readonly string[] States = {
            "DRAFT STYLE CONTRACTS", "OFFLINE CATALOG + READ-ONLY FIVE-GAME QUEUE", "MANUAL PNG INTAKE VIA CLI",
            "PNG TRIM, DETERMINISTIC SHELF ATLAS + UNITY INSPECTOR", "SPRITE CLIP BUILDER SOURCE", "PARTICLE PREFAB LAB SOURCE",
            "7 COMMON ARCHETYPES + 28 DRAFT CORAL SHELLS", "RUNTIME SAFE AREA + FIVE DEVICE LAYOUT WIREFRAME", "MANUAL PREFAB STRUCTURAL INSPECTOR",
            "LOCAL PACKAGE PREVIEW ONLY"
        };
        private int profile;
        private Vector2 scroll;

        [MenuItem("Tools/MATCH3/Visual Factory Dashboard")]
        public static void Open()
        {
            var window = GetWindow<VufDashboardWindow>("Visual Factory");
            window.minSize = new Vector2(550, 530);
            window.Show();
        }

        private void OnGUI()
        {
            EditorGUILayout.Space(10);
            EditorGUILayout.LabelField("MATCH3 VISUAL FACTORY", EditorStyles.boldLabel);
            EditorGUILayout.HelpBox(
                "Five games. One shared toolchain. M00 foundation under construction. " +
                "No approved artwork or production exports. Upstream integration is gated.",
                MessageType.Info);
            profile = EditorGUILayout.Popup("Selected game", profile, Profiles);
            if (GUILayout.Button("Five-Game Production Queue (read-only)", GUILayout.Height(32)))
                VufProductionQueueWindow.Open();
            if (GUILayout.Button("Offline Sprite Pixel QA Report (read-only)", GUILayout.Height(30)))
                VufSpriteQaReportWindow.Open();
            if (GUILayout.Button("Device & Safe-Area Layout Wireframe", GUILayout.Height(30)))
                VufResponsivePreviewWindow.Open();
            if (GUILayout.Button("Typography and Contrast Lab", GUILayout.Height(30)))
                VufTypographyLabWindow.Open();
            if (GUILayout.Button("Localization Coverage Studio (read-only)", GUILayout.Height(30)))
                VufLocaleCoverageWindow.Open();
            if (GUILayout.Button("Review Evidence Board (all QA gates)", GUILayout.Height(32)))
                VufReadinessBoardWindow.Open();
            if (GUILayout.Button("Version/Manifest Compatibility (read-only)",
                GUILayout.Height(30)))
                VufPreviewCompatibilityWindow.Open();
            using (new EditorGUILayout.HorizontalScope())
            {
                if (GUILayout.Button("Sprite Preview", GUILayout.Height(34)))
                    VufStudioWindow.Open();
                if (GUILayout.Button("Sprite Animation Builder", GUILayout.Height(34)))
                    VufSpriteClipBuilderWindow.Open();
                GUI.enabled = false;
                GUILayout.Button("Publish (NOT READY)", GUILayout.Height(34));
                GUI.enabled = true;
            }
            using (new EditorGUILayout.HorizontalScope())
            {
                if (GUILayout.Button("Particle VFX Lab", GUILayout.Height(34)))
                    VufVfxLabWindow.Open();
                if (GUILayout.Button("Interactive UI Composer", GUILayout.Height(34)))
                    VufUiComposerWindow.Open();
            }
            if (GUILayout.Button("Procedural FX Sheet Player", GUILayout.Height(30)))
                VufFxSheetPreviewWindow.Open();
            if (GUILayout.Button("Procedural FX to .anim Exporter", GUILayout.Height(30)))
                VufFxClipExporterWindow.Open();
            if (GUILayout.Button("Five-Game Tile Kit Inspector", GUILayout.Height(30)))
                VufTileKitInspectorWindow.Open();
            if (GUILayout.Button("NEW Unity SpriteAtlas V2 Candidate (unshipped)",
                GUILayout.Height(30)))
                VufSpriteAtlasV2Window.Open();
            if (GUILayout.Button("Five-Game Concept Showcase (15 PNGs)", GUILayout.Height(30)))
                VufConceptShowcaseWindow.Open();
            if (GUILayout.Button("Editable Concept UI Stage Builder", GUILayout.Height(30)))
                VufConceptStageBuilderWindow.Open();
            using (new EditorGUILayout.HorizontalScope())
            {
                if (GUILayout.Button("Sprite Atlas Inspector", GUILayout.Height(32)))
                    VufAtlasPreviewWindow.Open();
                if (GUILayout.Button("28-Screen Shell Builder", GUILayout.Height(32)))
                    VufScreenShellBuilderWindow.Open();
                if (GUILayout.Button("Manual Visual QA Studio", GUILayout.Height(32)))
                    VufQaStudioWindow.Open();
            }
            GUILayout.Space(8);
            EditorGUILayout.LabelField("VF MODULES | IMPLEMENTATION STATE", EditorStyles.boldLabel);
            scroll = EditorGUILayout.BeginScrollView(scroll);
            for (int i = 0; i < Modules.Length; ++i)
            {
                EditorGUILayout.BeginVertical("box");
                EditorGUILayout.LabelField(Modules[i], EditorStyles.boldLabel);
                EditorGUILayout.LabelField(States[i], EditorStyles.miniLabel);
                EditorGUILayout.EndVertical();
            }
            EditorGUILayout.EndScrollView();
            EditorGUILayout.HelpBox(
                "Approval receipt strings are audit metadata, not proof of an owner sign-off. " +
                "Game rules, saves and rewards remain owned by Engine/game repos.",
                MessageType.Warning);
        }
    }
}
