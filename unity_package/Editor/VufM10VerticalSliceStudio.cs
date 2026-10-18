// M10-001/002/003/005/006: read-only in-memory vertical slice of
// TEST_ONLY screen/asset CANDIDATES. Absolutely NOT a Match3 Engine/LFX
// consumer or gameplay implementation: final source SHA / ENG-M12/ENG-M24
// replay/level contracts must be accepted in upstream projects first.
// INTERNAL REUSE: 28 Coral screen source IDs, 5 draft Style Bibles, M08
// real uGUI temporary builder, M09 QA RenderTexture, M07 FX Studio.
// No persistent scene/prefab, score, network, purchase or player writes.
using System;
using System.Collections.Generic;
using System.IO;
using System.Security.Cryptography;
using UnityEditor;
using UnityEngine;
using UnityEngine.UI;

namespace Match3.VisualFactory.Editor
{
    public sealed class VufM10VerticalSliceStudio : EditorWindow
    {
        internal static readonly string[] Profiles = {
            "Coral_Rescue", "Garage_Legends", "Dino_Islands",
            "The_Fractured_Realms", "Wonder_Pop"
        };
        internal static readonly string[] Routes = {
            "home", "world_map", "level_start", "gameplay_hud", "level_won",
            "marine_collection", "daily_rewards", "shop", "offline"
        };
        internal static readonly string[] CoralExtras = {
            "reef_restoration", "my_aquarium", "region_unlocked"
        };
        internal static readonly string[] ViewEvents = {
            "ui_open", "tile_spawn", "tile_match", "obstacle_hit",
            "booster_activate", "special_trigger", "combo_chain",
            "level_win", "reward_claim", "region_reveal"
        };
        internal const string Stage = "VUF_M10_TEST_ONLY_NONAUTHORITATIVE";
        internal const string NoAuthority = "NO_ENGINE_LFX_SCORE_SAVE_REPLAY";
        private VufScreenCatalog.ScreenInfo[] sourceScreens;
        private GameObject current;
        private string currentScreenId, lastCue, status;
        private int profileIndex, routeIndex, mockLevel = 11, mockSeed = 42;
        private int localeIndex, stateIndex, deviceIndex, eventIndex;
        private bool reducedMotion = true;
        private TextAsset optionalOpaqueExternalLevel;
        private string externalDigest = "NOT_ATTACHED";
        private string immutableInputs;
        private Vector2 scroll;
        private readonly List<string> trace = new List<string>();

        [MenuItem("Tools/MATCH3/M10 Five-Theme Vertical Slice Review")]
        public static void Open()
        {
            var window = GetWindow<VufM10VerticalSliceStudio>("M10 Slice Review");
            window.minSize = new Vector2(740f, 690f);
            window.Show();
        }

        private void OnEnable()
        {
            try { sourceScreens = VufScreenCatalog.LoadScreens(); }
            catch (Exception ex)
            { sourceScreens = null; status = "BLOCKED: " + ex.Message; }
        }
        private void OnDisable() { DestroyOnlyMine(); }

        internal static string[] RouteForProfile(string profile)
        {
            if (Array.IndexOf(Profiles, profile) < 0)
                throw new ArgumentException("unknown game theme");
            var routes = new List<string>(Routes);
            if (profile == "Coral_Rescue") routes.AddRange(CoralExtras);
            return routes.ToArray();
        }

        internal static VufScreenCatalog.ScreenInfo ResolveCoralDraftRoute(
            VufScreenCatalog.ScreenInfo[] screens, string key)
        {
            if (screens == null || screens.Length != 28 ||
                String.IsNullOrEmpty(key))
                throw new ArgumentException("invalid pinned draft Coral route");
            string actualKey = key == "offline" ? "splash_loading" : key;
            foreach (var row in screens)
            {
                if (row != null && row.key == actualKey &&
                    row.feature_gate == "REQUIRES_ENGINE_OR_GAME_BINDING" &&
                    !row.available_in_demo)
                    return row;
            }
            throw new ArgumentException("route unavailable, forbidden or unpinned");
        }

        private void DestroyOnlyMine()
        {
            if (current != null) DestroyImmediate(current);
            current = null;
            currentScreenId = null;
        }

        // Neither theme nor imported art is allowed to enter this reference.
        internal static string FrozenMockReference(string profile, int level, int seed)
        {
            if (Array.IndexOf(Profiles, profile) < 0 ||
                level < 1 || level > 1000 || seed < 0 || seed > 65535)
                throw new ArgumentException("non-authoritative reference invalid");
            return "VUF_ONLY;profile=" + profile + ";mockLevel=" + level +
                   ";mockSeed=" + seed + ";actualMoves=NONE;" +
                   "actualScore=NONE;actualWin=NONE;actualDifficulty=NONE;" +
                   "actualSave=NONE;productionReplay=UNVERIFIED";
        }

        internal static string SourceSha(byte[] bytes)
        {
            if (bytes == null || bytes.Length == 0 ||
                bytes.Length > 4 * 1024 * 1024)
                throw new ArgumentException("external candidate input too large");
            using (var sha = SHA256.Create())
                return BitConverter.ToString(sha.ComputeHash(bytes))
                    .Replace("-", "").ToLowerInvariant();
        }

        private void AddTrace(string eventName)
        {
            VufVisualEventCatalog.EventKey(Profiles[profileIndex], eventName);
            trace.Add("VIEW ONLY " + trace.Count.ToString("D3") +
                " " + Profiles[profileIndex] + " " +
                (currentScreenId ?? "NO_SCREEN") + " " + eventName +
                " / " + NoAuthority);
            if (trace.Count > 60) trace.RemoveAt(0);
        }

        internal static GameObject CreateCandidate(string profile,
            string route, string mockState, string mockLocale)
        {
            VufScreenCatalog.ScreenInfo[] screen = VufScreenCatalog.LoadScreens();
            if (Array.IndexOf(RouteForProfile(profile), route) < 0)
                throw new ArgumentException("not a bounded slice route");
            var spec = ResolveCoralDraftRoute(screen, route);
            var draftStyle = VufScreenCatalog.LoadStyle(profile);
            GameObject candidate = null;
            try
            {
                candidate = VufScreenShellBuilderWindow.BuildCandidateHierarchy(
                    spec, draftStyle, true);
                string appliedState = route == "offline" ? "Offline" : mockState;
                VufReviewStateCatalog.Apply(candidate, spec,
                    appliedState, mockLocale);
                foreach (Transform child in
                    candidate.GetComponentsInChildren<Transform>(true))
                    child.gameObject.hideFlags =
                        HideFlags.DontSaveInEditor | HideFlags.DontSaveInBuild;
                foreach (Button action in candidate.GetComponentsInChildren<Button>(true))
                    if (action.interactable ||
                        action.onClick.GetPersistentEventCount() != 0)
                        throw new InvalidOperationException(
                            "gameplay action unexpectedly enabled or bound");
                return candidate;
            }
            catch
            {
                if (candidate != null) UnityEngine.Object.DestroyImmediate(candidate);
                throw;
            }
        }

        private void Build()
        {
            DestroyOnlyMine();
            string profile = Profiles[profileIndex];
            string[] routes = RouteForProfile(profile);
            string route = routes[Mathf.Clamp(routeIndex, 0, routes.Length-1)];
            try
            {
                immutableInputs = FrozenMockReference(profile, mockLevel, mockSeed);
                current = CreateCandidate(profile, route,
                    VufReviewStateCatalog.States[stateIndex],
                    VufReviewStateCatalog.Locales[localeIndex]);
                var marker = current.GetComponent<VufCandidateScreenMarker>();
                currentScreenId = marker.ScreenId;
                externalDigest = optionalOpaqueExternalLevel == null ?
                    "NOT_ATTACHED" : SourceSha(optionalOpaqueExternalLevel.bytes);
                AddTrace("ui_open");
                status = "Real uGUI draft candidate in Editor Scene: " +
                    route + " (" + marker.ScreenId + "). " +
                    (profile == "Coral_Rescue" ?
                        "Original Coral draft ID, NOT a functioning level." :
                        "BORROWED CORAL SCREEN, THIS TITLE'S OWN ROUTE N/A.") +
                    " Actual Engine/LFX neutral replay: NOT BOUND.";
                Selection.activeGameObject = current;
            }
            catch (Exception ex)
            {
                DestroyOnlyMine();
                status = "BUILD BLOCKED: " + ex.Message;
            }
        }

        private void SelectNext()
        {
            int count = RouteForProfile(Profiles[profileIndex]).Length;
            routeIndex = (routeIndex + 1) % count;
            Build();
        }

        private void OnGUI()
        {
            EditorGUILayout.LabelField("M10 | Five-theme non-gameplay slice Studio",
                EditorStyles.boldLabel);
            EditorGUILayout.HelpBox(
                "Not an Engine/LFX vertical slice. Exact LevelFactory release/" +
                "real neutral replay is not integrated. Real uGUI TEMP display " +
                "only; source Coral draft screens borrowed by four other styles " +
                "are N/A as title-approved independent UI. No rewards or game save.",
                MessageType.Warning);
            if (sourceScreens == null)
            {
                EditorGUILayout.HelpBox(status, MessageType.Error);
                return;
            }
            scroll = EditorGUILayout.BeginScrollView(scroll);
            EditorGUI.BeginChangeCheck();
            profileIndex = EditorGUILayout.Popup("Draft theme", profileIndex, Profiles);
            var routes = RouteForProfile(Profiles[profileIndex]);
            routeIndex = EditorGUILayout.Popup("Manual draft route",
                Mathf.Clamp(routeIndex, 0, routes.Length-1), routes);
            mockLevel = EditorGUILayout.IntSlider("NOT ENGINE mock level", mockLevel, 1, 1000);
            mockSeed = EditorGUILayout.IntSlider("NOT LFX mock seed", mockSeed, 0, 65535);
            stateIndex = EditorGUILayout.Popup("Mock state", stateIndex,
                VufReviewStateCatalog.States);
            localeIndex = EditorGUILayout.Popup("Draft locale", localeIndex,
                VufReviewStateCatalog.Locales);
            string[] devices = new string[VufResponsiveGeometry.Presets.Length];
            for (int i=0;i<devices.Length;i++)
                devices[i] = VufResponsiveGeometry.Presets[i].Name;
            deviceIndex = EditorGUILayout.Popup("Synthetic device", deviceIndex, devices);
            optionalOpaqueExternalLevel = (TextAsset)EditorGUILayout.ObjectField(
                "Optional opaque LFX bytes (NOT PARSED)",
                optionalOpaqueExternalLevel, typeof(TextAsset), false);
            reducedMotion = EditorGUILayout.Toggle(
                "Reduced motion mock", reducedMotion);
            if (EditorGUI.EndChangeCheck())
            {
                DestroyOnlyMine();
                status = "Changed source/route/theme/device. BUILD to reload.";
                externalDigest = "NOT_VERIFIED";
            }
            EditorGUILayout.BeginHorizontal();
            if (GUILayout.Button("BUILD TEMP real uGUI candidate"))
                Build();
            if (GUILayout.Button("NEXT manual route"))
                SelectNext();
            if (GUILayout.Button("CLEAR only own TEMP"))
            {
                DestroyOnlyMine();
                status = "Only Studio temporary scene objects disposed.";
            }
            EditorGUILayout.EndHorizontal();
            EditorGUILayout.LabelField("Source authority", NoAuthority);
            EditorGUILayout.LabelField("Original LevelFactory source SHA",
                externalDigest + " (OPAQUE INPUT; schema NOT VERIFIED)");
            EditorGUILayout.LabelField("Route", routes[routeIndex]);
            EditorGUILayout.LabelField("Independent title UI taxonomy",
                profileIndex==0 ? "CORAL DRAFT ONLY" :
                "N/A: CORAL DRAFT borrowed for this theme");
            if (current != null)
            {
                var screenInfo = ResolveCoralDraftRoute(
                    sourceScreens, routes[routeIndex]);
                var geometry = VufResponsiveGeometry.Analyze(
                    current, VufResponsiveGeometry.Presets[deviceIndex]);
                var type = VufTypographyAudit.Analyze(
                    current, VufResponsiveGeometry.Presets[deviceIndex]);
                EditorGUILayout.LabelField("Synthetic component/layout risk",
                    "geometry=" + geometry.Warnings.Count +
                    " typography=" + type.Warnings.Count);
                var animator = current.GetComponentInChildren<VufUiTween>(true);
                if (animator != null)
                {
                    animator.SetReducedMotion(reducedMotion);
                    if (GUILayout.Button("STEP transient CanvasGroup tween"))
                    {
                        animator.Hide(); animator.Advance(.12f);
                        animator.Show(); animator.Advance(.12f);
                    }
                }
                EditorGUILayout.HelpBox(
                    screenInfo.id + " " + screenInfo.key +
                    " NOT IMPLEMENTED IN DEMO / game tap disabled", MessageType.Info);
            }
            eventIndex = EditorGUILayout.Popup("Symbolic presentation cue", eventIndex,
                ViewEvents);
            if (GUILayout.Button("TRACE ONLY view event, NO Engine dispatch"))
            {
                try
                {
                    AddTrace(ViewEvents[eventIndex]);
                    lastCue = ViewEvents[eventIndex] + " not dispatched";
                }
                catch (Exception ex) { lastCue = ex.Message; }
            }
            if (GUILayout.Button("Open verified imported A/B visual pack sandbox"))
                VufExternalPackSandboxWindow.Open();
            if (GUILayout.Button("Open M09 real Unity Editor render/QA"))
                VufM09OwnerVisualQaWindow.Open();
            if (GUILayout.Button("Open M07 real Sprite/VFX editor playback"))
                VufUnifiedVisualStudioWindow.Open();
            EditorGUILayout.HelpBox(status ?? "Not built.", MessageType.Info);
            EditorGUILayout.LabelField("Immutable test-only reference",
                immutableInputs ?? "NOT LOADED", EditorStyles.wordWrappedLabel);
            EditorGUILayout.LabelField("View cue trace", lastCue ?? "NO CUE");
            foreach (var line in trace)
                EditorGUILayout.SelectableLabel(line, GUILayout.MinHeight(20f));
            EditorGUILayout.LabelField("Real Engine moves / WIN / score / save",
                "UNVERIFIED, NOT RUN");
            EditorGUILayout.LabelField("Real mobile GPU/player/owner rights",
                "NOT RUN / NO APPROVAL");
            EditorGUILayout.EndScrollView();
        }
    }
}
