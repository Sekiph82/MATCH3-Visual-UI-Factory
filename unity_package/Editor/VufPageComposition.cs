// VF-07 / R35: editable, profile-aware, noninteractive uGUI layout components.
// These are art-direction candidate widgets, NEVER actual gameplay or rewards.
using System;
using UnityEngine;
using UnityEngine.UI;
using Match3.VisualFactory.Editor.ThirdParty;

namespace Match3.VisualFactory.Editor
{
    internal static class VufPageComposition
    {
        private static readonly string[] Pages = { "home", "gameplay", "world_map" };

        private static RectTransform Node(Transform parent, string name,
            Vector2 min, Vector2 max)
        {
            GameObject go = new GameObject(name, typeof(RectTransform));
            RectTransform rect = go.GetComponent<RectTransform>();
            rect.SetParent(parent, false);
            rect.anchorMin = min;
            rect.anchorMax = max;
            rect.offsetMin = Vector2.zero;
            rect.offsetMax = Vector2.zero;
            rect.localScale = Vector3.one;
            return rect;
        }

        private static RectTransform Panel(Transform parent, string name,
            Vector2 min, Vector2 max, Color color)
        {
            RectTransform rect = Node(parent, name, min, max);
            Image image = rect.gameObject.AddComponent<Image>();
            image.color = color;
            image.raycastTarget = false;
            // Reuse BSD-3-Clause upstream Gradient.cs for selected
            // large authoring panels, not a new proprietary mesh shader.
            if (name == "HOME_HeroArtworkPlaceholder" ||
                name == "HOME_DailyMissionCard" ||
                name == "GAMEPLAY_ReadOnlyHUD" ||
                name == "WORLD_EditableMapCanvas")
            {
                var gradient = rect.gameObject.AddComponent<
                    Match3.VisualFactory.Editor.ThirdParty.Gradient>();
                gradient.GradientMode =
                    Match3.VisualFactory.Editor.ThirdParty.GradientMode.Global;
                gradient.GradientDir = GradientDir.Vertical;
                gradient.OverwriteAllColor = true;
                gradient.Vertex1 = Color.white;
                gradient.Vertex2 = new Color(.58f, .68f, .86f, 1f);
            }
            return rect;
        }

        private static Text Label(Transform parent, string name, string message,
            Vector2 min, Vector2 max, int size, Color color)
        {
            RectTransform rect = Node(parent, name, min, max);
            Text text = rect.gameObject.AddComponent<Text>();
            text.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            text.text = message;
            text.fontSize = size;
            text.alignment = TextAnchor.MiddleCenter;
            text.horizontalOverflow = HorizontalWrapMode.Wrap;
            text.verticalOverflow = VerticalWrapMode.Truncate;
            text.raycastTarget = false;
            text.color = color;
            return text;
        }

        private static void Home(Transform parent, Color surface, Color accent,
            Color ink)
        {
            RectTransform hero = Panel(parent, "HOME_HeroArtworkPlaceholder",
                new Vector2(.095f, .49f), new Vector2(.905f, .78f),
                Color.Lerp(surface, accent, .26f));
            Panel(hero, "HOME_CharacterSilhouettePlaceholder",
                new Vector2(.29f, .14f), new Vector2(.71f, .84f),
                Color.Lerp(surface, accent, .68f));
            Label(hero, "HOME_HeroCaption", "HERO / MASCOT ART SLOT",
                new Vector2(.07f, .03f), new Vector2(.93f, .18f), 20, ink);
            // R42 donor-first: reuse upstream MIT/BSD3 RadialLayout
            // instead of implementing our own orbital positioning.
            RectTransform orbit = Node(hero, "HOME_OrbitLayout_AUTHORING_ONLY",
                Vector2.zero, Vector2.one);
            var radial = orbit.gameObject.AddComponent<RadialLayout>();
            radial.OnlyLayoutVisible = false;
            radial.fDistance = 135f;
            radial.MinAngle = 0f;
            radial.MaxAngle = 360f;
            radial.StartAngle = 18f;
            for (int i = 0; i < 5; i++)
            {
                RectTransform badge = Panel(orbit,
                    "HOME_OrbitBadge_STATIC_" + (i + 1).ToString("D2"),
                    new Vector2(.5f, .5f), new Vector2(.5f, .5f),
                    Color.Lerp(surface, accent, (i + 2f) / 8f));
                badge.sizeDelta = new Vector2(28f, 28f);
            }
            radial.CalculateLayoutInputHorizontal();
            RectTransform quest = Panel(parent, "HOME_DailyMissionCard",
                new Vector2(.095f, .34f), new Vector2(.905f, .45f), surface);
            Label(quest, "HOME_MissionTitle", "DAILY QUEST | MOCK",
                new Vector2(.04f, .56f), new Vector2(.96f, .94f), 24, ink);
            Panel(quest, "HOME_ProgressTrack", new Vector2(.08f, .20f),
                new Vector2(.92f, .33f), Color.Lerp(surface, accent, .35f));
            Panel(quest, "HOME_ProgressFill_STATIC",
                new Vector2(.08f, .20f), new Vector2(.46f, .33f), accent);
            RectTransform collection = Panel(parent, "HOME_CollectionSlots",
                new Vector2(.095f, .205f), new Vector2(.905f, .32f), surface);
            // Reuse actual Simie/Martin Sharkbomb/Vicente Russo BSD3 flow
            // LayoutGroup implementation instead of another wrap algorithm.
            var flow = collection.gameObject.AddComponent<FlowLayoutGroup>();
            flow.padding = new RectOffset(12, 12, 7, 7);
            flow.SpacingX = 9f;
            flow.SpacingY = 5f;
            flow.ChildForceExpandWidth = false;
            flow.ChildForceExpandHeight = false;
            for (int i = 0; i < 4; i++)
            {
                float left = .04f + i * .24f;
                RectTransform tile = Panel(collection,
                    "HOME_CollectiblePlaceholder_" + (i + 1).ToString("D2"),
                    new Vector2(left, .14f), new Vector2(left + .19f, .87f),
                    Color.Lerp(surface, accent, (i % 3 + 1) * .17f));
                var element = tile.gameObject.AddComponent<LayoutElement>();
                element.preferredWidth = 104f;
                element.preferredHeight = 68f;
            }
        }

        private static void Gameplay(Transform parent, Color surface,
            Color accent, Color ink)
        {
            RectTransform hud = Panel(parent, "GAMEPLAY_ReadOnlyHUD",
                new Vector2(.065f, .77f), new Vector2(.935f, .86f), surface);
            Label(hud, "GAMEPLAY_LevelLabel", "LEVEL PREVIEW",
                new Vector2(.03f, .5f), new Vector2(.45f, .94f), 22, ink);
            Label(hud, "GAMEPLAY_MovesLabel", "MOVES --",
                new Vector2(.55f, .5f), new Vector2(.97f, .94f), 22, ink);
            Label(hud, "GAMEPLAY_ScorePlaceholder", "SCORE / OBJECTIVE UNBOUND",
                new Vector2(.03f, .06f), new Vector2(.97f, .47f), 18, ink);

            RectTransform board = Panel(parent, "GAMEPLAY_Grid6x7_VISUAL_ONLY",
                new Vector2(.055f, .265f), new Vector2(.945f, .745f),
                Color.Lerp(surface, accent, .2f));
            for (int row = 0; row < 7; row++)
            for (int col = 0; col < 6; col++)
            {
                float x0 = (col + .06f) / 6f;
                float x1 = (col + .94f) / 6f;
                float y0 = (row + .06f) / 7f;
                float y1 = (row + .94f) / 7f;
                Panel(board, "GAMEPLAY_StaticTile_" + row.ToString("D2") + "_" +
                    col.ToString("D2"), new Vector2(x0, y0),
                    new Vector2(x1, y1),
                    Color.Lerp(surface, accent,
                        ((row * 3 + col * 5) % 7 + 2f) / 10f));
            }
            RectTransform inventory = Panel(parent, "GAMEPLAY_BoosterPreview",
                new Vector2(.065f, .175f), new Vector2(.935f, .245f), surface);
            for (int i = 0; i < 3; i++)
            {
                float left = .07f + .315f * i;
                Panel(inventory, "GAMEPLAY_BoosterIcon_STATIC_" + (i + 1),
                    new Vector2(left, .1f), new Vector2(left + .235f, .9f),
                    Color.Lerp(surface, accent, .35f + .17f * i));
            }
        }

        private static void WorldMap(Transform parent, Color surface,
            Color accent, Color ink)
        {
            RectTransform terrain = Panel(parent, "WORLD_EditableMapCanvas",
                new Vector2(.07f, .205f), new Vector2(.93f, .84f),
                Color.Lerp(surface, accent, .18f));
            Vector2[] nodes = {
                new Vector2(.25f, .12f), new Vector2(.54f, .22f),
                new Vector2(.73f, .33f), new Vector2(.41f, .46f),
                new Vector2(.23f, .6f), new Vector2(.57f, .72f),
                new Vector2(.78f, .83f)
            };
            // Explicit graphical links, not scene navigation or buttons.
            for (int i = 1; i < nodes.Length; i++)
            {
                Vector2 delta = nodes[i] - nodes[i - 1];
                RectTransform segment = Panel(terrain,
                    "WORLD_PathSegment_STATIC_" + i,
                    nodes[i - 1], nodes[i - 1], accent);
                segment.anchorMin = nodes[i - 1];
                segment.anchorMax = nodes[i - 1];
                segment.pivot = new Vector2(0f, .5f);
                segment.sizeDelta = new Vector2(delta.magnitude * 460f, 7f);
                segment.localRotation = Quaternion.Euler(0f, 0f,
                    Mathf.Atan2(delta.y, delta.x) * Mathf.Rad2Deg);
            }
            for (int i = 0; i < nodes.Length; i++)
            {
                Vector2 point = nodes[i];
                RectTransform pin = Panel(terrain,
                    "WORLD_LevelNode_UNBOUND_" + (i + 1).ToString("D2"),
                    point - new Vector2(.058f, .035f),
                    point + new Vector2(.058f, .035f),
                    i == 0 ? accent : Color.Lerp(surface, accent, .62f));
                Label(pin, "WORLD_NodeNumber", (i + 1).ToString(),
                    Vector2.zero, Vector2.one, 20, ink);
            }
            Label(parent, "WORLD_MapFooter", "WORLD MAP / STATIC AUTHORING",
                new Vector2(.15f, .175f), new Vector2(.85f, .2f), 19, ink);
        }

        // Must be called on an in-memory candidate stage with author-only
        // colors. Never creates assets, modifies source art or activates Buttons.
        internal static void Compose(Transform safeArea,
            VufScreenCatalog.StyleInfo style, string page)
        {
            if (safeArea == null || style == null || style.palettes == null ||
                Array.IndexOf(Pages, page) < 0 ||
                safeArea.GetComponent<VufSafeAreaFitter>() == null)
                throw new ArgumentException("composition requires a supported draft safe area");
            Color accent = VufScreenCatalog.ParseColor(style.palettes.accent, "accent");
            Color surface = VufScreenCatalog.ParseColor(style.palettes.surface, "surface");
            Color ink = VufScreenCatalog.ParseColor(style.palettes.text, "text");
            if (safeArea.Find("HOME_HeroArtworkPlaceholder") != null ||
                safeArea.Find("GAMEPLAY_Grid6x7_VISUAL_ONLY") != null ||
                safeArea.Find("WORLD_EditableMapCanvas") != null)
                throw new InvalidOperationException("duplicate component composition refused");
            if (page == "home") Home(safeArea, surface, accent, ink);
            else if (page == "gameplay") Gameplay(safeArea, surface, accent, ink);
            else WorldMap(safeArea, surface, accent, ink);
        }
    }
}
