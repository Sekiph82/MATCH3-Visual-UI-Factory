// Three-factory READ-ONLY actual-data review.
// LFXV1: genuine LevelDraftJson.Parse-validated board/goal projection.
// M3P1: actual Engine PresentationEvent types/positions/sequence receipt.
// Neither supplies a final Engine replay, score, WIN nor authorised assets.
// The UI is temporary and entirely Editor-only (no player/Engine dependency).
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using UnityEditor;
using UnityEngine;
using UnityEngine.UI;

namespace Match3.VisualFactory.Editor
{
    public sealed class VufCrossFactoryContractWindow : EditorWindow
    {
        private const string Stage = "LFXV1_VALIDATED_DRAFT_NOT_ENGINE_REPLAY";
        private const string Wire = "M3P1";
        private static readonly UTF8Encoding StrictUtf8 = new UTF8Encoding(false, true);
        [Serializable] internal sealed class Cell
        {
            public int row, column, layer, obstacleDurability, lockDurability;
            public bool active, locked;
            public string contentId, obstacleId, specialId;
        }
        [Serializable] internal sealed class Goal
        {
            public string goalId, targetId;
            public int targetCount;
        }
        [Serializable] internal sealed class Level
        {
            public int schemaVersion, width, height, layers, moveBudget;
            public string stage, gameProfileId, levelId;
            public string sourceDraftSha256, sourceLevelFactoryGitSha;
            public long seed;
            public Cell[] cells;
            public Goal[] goals;
            public bool actualSdkWinVerified, engineM24ReleaseAccepted;
            public bool realPlayableLevel, assetRightsApproved, releaseAllowed;
        }
        internal sealed class Cue
        {
            public int Sequence, Kind, Intensity;
            public string EventId, PresentationKey, VufEvent;
            public readonly List<Vector3Int> Cells = new List<Vector3Int>();
        }

        private string draftPath, levelPath, eventsPath, status =
            "Load actual LFXV1 pair + optional genuine M3P1 Engine event receipt.";
        private Level current;
        private List<Cue> cues;
        private int currentStep = -1;
        private GameObject canvas;
        private Vector2 scroll;

        [MenuItem("Tools/MATCH3/Three Factory Real Data and Visual Events")]
        public static void Open()
        {
            var w = GetWindow<VufCrossFactoryContractWindow>("Three Factory Bridge");
            w.minSize = new Vector2(650, 720);
            w.Show();
        }
        private void OnDisable() { ClearPreview(); }
        private void ClearPreview()
        {
            if (canvas != null) DestroyImmediate(canvas);
            canvas = null; gridImages = null;
        }

        private static string Sha(byte[] bytes)
        {
            using (var sha = SHA256.Create())
                return BitConverter.ToString(sha.ComputeHash(bytes))
                    .Replace("-", "").ToLowerInvariant();
        }
        private static bool Hex(string s, int size)
        {
            return s != null && s.Length == size &&
                s.All(x => x >= '0' && x <= '9' || x >= 'a' && x <= 'f');
        }
        internal static Level ParseLevel(string envelopeJson, byte[] canonicalDraft)
        {
            if (String.IsNullOrEmpty(envelopeJson) ||
                envelopeJson.Length > 1024 * 1024 || canonicalDraft == null ||
                canonicalDraft.Length == 0 || canonicalDraft.Length > 2_000_000)
                throw new ArgumentException("missing/oversized original LFX data");
            var l = JsonUtility.FromJson<Level>(envelopeJson);
            if (l == null || l.schemaVersion != 1 || l.stage != Stage ||
                !VufVisualEventCatalog.Profiles.Contains(l.gameProfileId) ||
                l.sourceLevelFactoryGitSha != "UNPINNED" ||
                l.width < 1 || l.width > 32 || l.height < 1 || l.height > 32 ||
                l.layers < 1 || l.layers > 4 || l.moveBudget < 1 ||
                l.moveBudget > 999 || l.seed < 0 ||
                l.actualSdkWinVerified || l.engineM24ReleaseAccepted ||
                l.realPlayableLevel || l.assetRightsApproved || l.releaseAllowed ||
                !Hex(l.sourceDraftSha256, 64) ||
                Sha(canonicalDraft) != l.sourceDraftSha256 ||
                l.cells == null || l.cells.Length != l.width*l.height*l.layers ||
                l.goals == null || l.goals.Length < 1 || l.goals.Length > 32)
                throw new ArgumentException("LFXV1 source SHA, stage or grid mismatch");
            var positions = new HashSet<string>();
            foreach (var c in l.cells)
            {
                if (c == null || c.row < 0 || c.row >= l.height ||
                    c.column < 0 || c.column >= l.width ||
                    c.layer < 0 || c.layer >= l.layers ||
                    c.obstacleDurability < 0 || c.obstacleDurability > 99 ||
                    c.lockDurability < 0 || c.lockDurability > 99 ||
                    (!c.active && (c.locked || c.obstacleDurability != 0 ||
                        c.lockDurability != 0 ||
                        !String.IsNullOrEmpty(c.contentId) ||
                        !String.IsNullOrEmpty(c.obstacleId) ||
                        !String.IsNullOrEmpty(c.specialId))) ||
                    (c.active && String.IsNullOrWhiteSpace(c.contentId) &&
                        String.IsNullOrWhiteSpace(c.obstacleId)) ||
                    !positions.Add(c.layer + ":" + c.row + ":" + c.column))
                    throw new ArgumentException("Duplicate/inconsistent LFX cell");
            }
            var ids = new HashSet<string>(StringComparer.Ordinal);
            foreach (var goal in l.goals)
                if (goal == null || String.IsNullOrWhiteSpace(goal.goalId) ||
                    !ids.Add(goal.goalId) ||
                    String.IsNullOrWhiteSpace(goal.targetId) ||
                    goal.targetCount < 1 || goal.targetCount > 99999)
                    throw new ArgumentException("Invalid LFX goal");
            return l;
        }

        private static string Decode64(string input)
        {
            byte[] raw = Convert.FromBase64String(input);
            if (Convert.ToBase64String(raw) != input)
                throw new FormatException("Engine base64 noncanonical");
            string s = StrictUtf8.GetString(raw);
            if (String.IsNullOrWhiteSpace(s) || s.Length > 256)
                throw new FormatException("Invalid Engine visual ID");
            return s;
        }

        internal static List<Cue> ParseEvents(byte[] wire, Level level)
        {
            if (level == null || wire == null || wire.Length == 0 ||
                wire.Length > 1024*1024)
                throw new FormatException("Missing verified LFX + bounded Engine wire");
            string data = StrictUtf8.GetString(wire);
            var lines = data.Split('\n');
            if (lines.Length < 4 || lines[0] != Wire ||
                lines[1] != level.gameProfileId ||
                !int.TryParse(lines[2], out int count) ||
                count < 0 || count > 2048 || lines.Length != count + 4)
                throw new FormatException("Engine event profile/schema mismatch");
            string prefix = String.Join("\n", lines, 0, lines.Length - 1) + "\n";
            if (Sha(StrictUtf8.GetBytes(prefix)) != lines[lines.Length - 1])
                throw new FormatException("Engine receipt checksum mismatch");
            string[] eventNames = { null, "tile_match", "special_trigger",
                "special_trigger", "special_trigger", "combo_chain", "tile_spawn" };
            var result = new List<Cue>();
            for (int i = 0; i < count; i++)
            {
                var f = lines[3+i].Split('|');
                if (f.Length != 6 || f[0] != (i+1).ToString() ||
                    !int.TryParse(f[2], out int kind) ||
                    kind < 0 || kind >= eventNames.Length ||
                    !int.TryParse(f[4], out int intensity) ||
                    intensity < 0 || intensity > 2)
                    throw new FormatException("noncontiguous/unrecognized actual event");
                var cue = new Cue {
                    Sequence = i+1, Kind = kind, Intensity = intensity,
                    EventId = Decode64(f[1]),
                    PresentationKey = Decode64(f[3]),
                    VufEvent = eventNames[kind]
                };
                var positions = new HashSet<string>();
                foreach (var raw in f[5].Split(','))
                {
                    var coords = raw.Split(':');
                    if (coords.Length != 3 ||
                        !int.TryParse(coords[0], out int layer) ||
                        !int.TryParse(coords[1], out int row) ||
                        !int.TryParse(coords[2], out int column) ||
                        layer < 0 || layer >= level.layers ||
                        row < 0 || row >= level.height ||
                        column < 0 || column >= level.width ||
                        !positions.Add(raw))
                        throw new FormatException("Engine event outside actual LFX board");
                    cue.Cells.Add(new Vector3Int(column, row, layer));
                }
                if (cue.Cells.Count < 1 || cue.Cells.Count > 1024)
                    throw new FormatException("Event must address at least one cell");
                if (cue.VufEvent != null)
                    VufVisualEventCatalog.EventKey(level.gameProfileId, cue.VufEvent);
                // Engine Swap is kept N/A (no corresponding approved M07 cue).
                result.Add(cue);
            }
            return result;
        }

        internal static GameObject BuildRealDraftBoard(Level level)
        {
            if (level == null) throw new ArgumentNullException(nameof(level));
            GameObject host = null;
            try
            {
                host = new GameObject("VUF_THREE_FACTORY_REAL_DRAFT_TEMP",
                    typeof(RectTransform), typeof(Canvas), typeof(CanvasScaler),
                    typeof(GraphicRaycaster));
                host.hideFlags =
                    HideFlags.DontSaveInEditor | HideFlags.DontSaveInBuild;
                var panel = host.GetComponent<RectTransform>();
                panel.sizeDelta = new Vector2(620, 720);
                host.GetComponent<Canvas>().renderMode =
                    RenderMode.ScreenSpaceOverlay;
                var grid = new GameObject("Real_LFXV1_Source_Grid",
                    typeof(RectTransform),typeof(GridLayoutGroup));
                grid.transform.SetParent(host.transform, false);
                grid.hideFlags = host.hideFlags;
                var rect = grid.GetComponent<RectTransform>();
                rect.anchorMin = rect.anchorMax = new Vector2(.5f, .5f);
                rect.sizeDelta = new Vector2(520, 520);
                var layout = grid.GetComponent<GridLayoutGroup>();
                layout.constraint = GridLayoutGroup.Constraint.FixedColumnCount;
                layout.constraintCount = level.width;
                layout.spacing = new Vector2(2,2);
                layout.cellSize = new Vector2(520f / level.width - 2,
                    520f / level.height - 2);
                var firstLayer = level.cells.Where(c => c.layer == 0)
                    .OrderBy(c=>c.row).ThenBy(c=>c.column).ToArray();
                foreach (var c in firstLayer)
                {
                    var game = new GameObject("LFX_cell_"+c.row+"_"+c.column,
                        typeof(RectTransform),typeof(Image));
                    game.transform.SetParent(grid.transform,false);
                    game.hideFlags = host.hideFlags;
                    var img=game.GetComponent<Image>();
                    img.raycastTarget=false;
                    img.color = c.active ? (c.obstacleId != null ?
                        new Color(.45f,.28f,.19f,1f) :
                        new Color(.16f,.42f,.66f,1f)) :
                        new Color(.10f,.11f,.12f,.3f);
                    var label = new GameObject("SourceIDs_notArt",
                        typeof(RectTransform),typeof(Text));
                    label.transform.SetParent(game.transform,false);
                    label.hideFlags = host.hideFlags;
                    var box=label.GetComponent<RectTransform>();
                    box.anchorMin=Vector2.zero; box.anchorMax=Vector2.one;
                    box.offsetMin=Vector2.zero; box.offsetMax=Vector2.zero;
                    var text=label.GetComponent<Text>();
                    text.font=Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
                    text.fontSize=12;
                    text.alignment=TextAnchor.MiddleCenter;
                    text.horizontalOverflow=HorizontalWrapMode.Wrap;
                    text.verticalOverflow=VerticalWrapMode.Truncate;
                    text.raycastTarget=false;
                    text.color=Color.white;
                    text.text=c.active ? (c.contentId ?? c.obstacleId) :
                        "HOLE";
                }
                return host;
            }
            catch
            {
                if (host != null) UnityEngine.Object.DestroyImmediate(host);
                throw;
            }
        }

        private void Load()
        {
            ClearPreview();
            current=null; cues=null; currentStep=-1;
            try
            {
                if (String.IsNullOrEmpty(draftPath) ||
                    String.IsNullOrEmpty(levelPath) ||
                    !File.Exists(draftPath) || !File.Exists(levelPath))
                    throw new IOException("Select canonical LFX source + envelope");
                byte[] canonical=File.ReadAllBytes(draftPath);
                current=ParseLevel(File.ReadAllText(levelPath),canonical);
                cues=String.IsNullOrEmpty(eventsPath) ? new List<Cue>() :
                    ParseEvents(File.ReadAllBytes(eventsPath),current);
                canvas=BuildRealDraftBoard(current);
                Selection.activeGameObject=canvas;
                status="ACTUAL LFX validated geometry loaded ("+
                    current.width+"x"+current.height+"x"+current.layers+
                    "). Actual Engine typed event receipts "+cues.Count+
                    ". NOT settled replay/score/owner art. Swap cue N/A.";
            }
            catch(Exception ex)
            {
                ClearPreview(); current=null; cues=null;
                status="FAIL CLOSED: "+ex.Message;
            }
        }

        private void HighlightCurrentEvent()
        {
            if (canvas == null || current == null) return;
            var grid = canvas.transform.Find("Real_LFXV1_Source_Grid");
            if (grid == null) return;
            var map = current.cells.Where(c => c.layer == 0)
                .OrderBy(c => c.row).ThenBy(c => c.column).ToArray();
            for (int i=0;i<map.Length && i<grid.childCount;i++)
            {
                var c=map[i];
                var image=grid.GetChild(i).GetComponent<Image>();
                if (image == null) continue;
                bool selected = currentStep>=0 && cues!=null &&
                    cues[currentStep].Cells.Any(p =>
                        p.z==0 && p.y==c.row && p.x==c.column);
                image.color = selected ? new Color(.94f,.69f,.16f,1f) :
                    !c.active ? new Color(.10f,.11f,.12f,.3f) :
                    !String.IsNullOrEmpty(c.obstacleId) ?
                        new Color(.45f,.28f,.19f,1f) :
                        new Color(.16f,.42f,.66f,1f);
            }
        }

        private void OnGUI()
        {
            EditorGUILayout.LabelField("THREE FACTORIES | Real data, no fake WIN",
                EditorStyles.boldLabel);
            EditorGUILayout.HelpBox(
                "LFXV1 is derived from actual validated LevelDraft cells/goals. " +
                "M3P1 is typed ENGINE PresentationEvent receipt, not replay " +
                "settlement. This real uGUI grid displays SOURCE content IDs, " +
                "not licensed sprite art or completed Engine gameplay.",
                MessageType.Warning);
            if(GUILayout.Button("Select LFX canonical LevelDraft JSON"))
                draftPath=EditorUtility.OpenFilePanel("LFX validated source","", "json");
            if(GUILayout.Button("Select matching LFXV1 visual handoff JSON"))
                levelPath=EditorUtility.OpenFilePanel("LFXV1 real envelope","", "json");
            if(GUILayout.Button("Select Engine M3P1 receipt (optional)"))
                eventsPath=EditorUtility.OpenFilePanel("M3P1 typed Engine events","", "txt");
            EditorGUILayout.SelectableLabel(draftPath ?? "(no LevelDraft)");
            EditorGUILayout.SelectableLabel(levelPath ?? "(no LFXV1)");
            EditorGUILayout.SelectableLabel(eventsPath ?? "(no M3P1)");
            if(GUILayout.Button("Verify actual source SHA, render TEMP grid"))
                Load();
            if(GUILayout.Button("Destroy only this temporary grid"))
            {
                ClearPreview(); current=null; cues=null; currentStep=-1;
            }
            EditorGUILayout.HelpBox(status, MessageType.Info);
            if(current == null) return;
            scroll=EditorGUILayout.BeginScrollView(scroll);
            EditorGUILayout.LabelField("LFX actual profile",current.gameProfileId);
            EditorGUILayout.LabelField("LFX actual draft level",current.levelId);
            EditorGUILayout.LabelField("Source SHA256",current.sourceDraftSha256);
            EditorGUILayout.LabelField("Board geometry",current.width+"×"+
                current.height+"×"+current.layers);
            EditorGUILayout.LabelField("Goals","DRAFT target definitions, NOT achievements");
            foreach(var goal in current.goals)
                EditorGUILayout.LabelField(goal.goalId+": "+goal.targetId+
                    " × "+goal.targetCount);
            if(cues != null && cues.Count>0)
            {
                if(GUILayout.Button("STEP actual typed Engine presentation event"))
                {
                    currentStep=(currentStep+1)%cues.Count;
                    HighlightCurrentEvent();
                    Repaint();
                }
                if(currentStep>=0)
                {
                    var cue=cues[currentStep];
                    EditorGUILayout.LabelField("Actual Engine event",cue.EventId);
                    EditorGUILayout.LabelField("Presentation key",cue.PresentationKey);
                    EditorGUILayout.LabelField("VUF view-only cue",
                        cue.VufEvent ?? "N/A: ENGINE SWAP not bound");
                    EditorGUILayout.LabelField("Actual event coordinates",
                        String.Join(",",cue.Cells.Select(c=>c.z+":"+c.y+":"+c.x)
                            .ToArray()));
                }
            }
            if(GUILayout.Button("Open existing M07 Sprite/VFX assets inspector"))
                VufUnifiedVisualStudioWindow.Open();
            if(GUILayout.Button("Open existing M08 candidate source A/B"))
                VufExternalPackSandboxWindow.Open();
            EditorGUILayout.HelpBox(
                "ENGINE receipts only attest source format/integrity. No " +
                "SDK VerifySdkSettledSnapshots, no actual runtime gameplay, " +
                "no asset rights/owner/device/production authorization.",
                MessageType.Warning);
            EditorGUILayout.EndScrollView();
        }
    }
}
