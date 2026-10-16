// VF-01/VF-07 / R36: five visibly different editable motif grammars.
// Geometry is original mathematical draft decoration; NEVER imported art,
// game logic, player state, interactive controls or an owner-approved skin.
using System;
using UnityEngine;
using UnityEngine.UI;
using Match3.VisualFactory.Editor.ThirdParty;

namespace Match3.VisualFactory.Editor
{
    internal static class VufThemeMotifDecor
    {
        private static readonly string[] Profiles = {
            "Coral_Rescue", "Garage_Legends", "Dino_Islands",
            "The_Fractured_Realms", "Wonder_Pop"
        };

        private static RectTransform Shape(Transform parent, string name,
            Vector2 center, Vector2 dimensions, Color color, float z = 0f)
        {
            GameObject item = new GameObject(name, typeof(RectTransform), typeof(Image));
            RectTransform rect = item.GetComponent<RectTransform>();
            rect.SetParent(parent, false);
            rect.anchorMin = center;
            rect.anchorMax = center;
            rect.pivot = new Vector2(.5f, .5f);
            rect.sizeDelta = dimensions;
            rect.anchoredPosition = Vector2.zero;
            rect.localRotation = Quaternion.Euler(0f, 0f, z);
            Image image = item.GetComponent<Image>();
            image.color = color;
            image.raycastTarget = false;
            return rect;
        }

        private static Color Transparent(Color c, float alpha)
        {
            return new Color(c.r, c.g, c.b, alpha);
        }

        private static void Coral(Transform parent, Color accent)
        {
            // Nested squares visually represent concentric circles only as a
            // preliminary "bubbles" art-direction schematic, NOT true masks.
            for (int i = 0; i < 12; i++)
            {
                float x = .04f + ((i * 29) % 87) / 100f;
                float y = .07f + ((i * 41) % 83) / 100f;
                float side = 18f + (i % 5) * 9f;
                RectTransform bubble = Shape(parent,
                    "CORAL_BubbleOutline_" + i.ToString("D2"),
                    new Vector2(x, y), new Vector2(side, side),
                    Transparent(accent, .22f));
                Shape(bubble, "CORAL_InnerWaterGlint",
                    new Vector2(.50f, .50f),
                    new Vector2(side * .35f, side * .35f),
                    Transparent(Color.white, .45f));
            }
        }

        private static void Garage(Transform parent, Color accent)
        {
            for (int i = 0; i < 12; i++)
            {
                float x = .08f + ((i * 17) % 81) / 100f;
                float y = .10f + ((i * 31) % 77) / 100f;
                RectTransform plate = Shape(parent,
                    "GARAGE_RivetPlate_" + i.ToString("D2"),
                    new Vector2(x, y), new Vector2(30, 21),
                    Transparent(accent, .25f), i % 2 == 0 ? 0 : 30);
                Shape(plate, "GARAGE_MetalFastener",
                    new Vector2(.5f, .5f), new Vector2(8, 8),
                    Transparent(Color.black, .45f));
            }
        }

        private static void Dino(Transform parent, Color accent)
        {
            for (int i = 0; i < 10; i++)
            {
                float x = .06f + ((i * 37) % 86) / 100f;
                float y = .09f + ((i * 23) % 80) / 100f;
                RectTransform frond = Shape(parent,
                    "DINO_FrondStem_" + i.ToString("D2"),
                    new Vector2(x, y), new Vector2(8, 47),
                    Transparent(accent, .28f),
                    i % 2 == 0 ? -25 : 25);
                RectTransform leafLeft = Shape(frond, "DINO_LeafLeft",
                    new Vector2(.12f, .72f),
                    new Vector2(22, 12), Transparent(accent, .5f), -40);
                RectTransform leafRight = Shape(frond, "DINO_LeafRight",
                    new Vector2(.88f, .48f),
                    new Vector2(25, 11), Transparent(accent, .5f), 35);
                // Reuse original upstream UIFlippable mesh effect, no custom
                // UV/vertex mirroring code in Visual Factory.
                var mirror = leafRight.gameObject.AddComponent<UIFlippable>();
                mirror.horizontal = true;
            }
        }

        private static void Fractured(Transform parent, Color accent)
        {
            for (int i = 0; i < 9; i++)
            {
                float x = .10f + ((i * 31) % 80) / 100f;
                float y = .12f + ((i * 19) % 73) / 100f;
                float size = 26 + (i % 4) * 15;
                RectTransform outer = Shape(parent,
                    "REALMS_PortalDiamond_" + i.ToString("D2"),
                    new Vector2(x, y), new Vector2(size, size),
                    Transparent(accent, .24f), 45);
                Shape(outer, "REALMS_InnerPortal",
                    new Vector2(.5f, .5f), new Vector2(size * .55f, size * .55f),
                    Transparent(Color.white, .25f), 0);
            }
        }

        private static void Wonder(Transform parent, Color accent)
        {
            for (int i = 0; i < 18; i++)
            {
                float x = .03f + ((i * 41) % 94) / 100f;
                float y = .04f + ((i * 29) % 90) / 100f;
                Shape(parent, "WONDER_Confetti_" + i.ToString("D2"),
                    new Vector2(x, y),
                    new Vector2(9 + (i % 4) * 5, 8 + (i % 3) * 5),
                    Transparent(i % 2 == 0 ? accent : Color.white, .25f),
                    i * 23 % 160);
            }
        }

        // Must be called on an in-memory draft safe-area. These motifs are
        // decorative editable uGUI children, never clickable or auto-shipping.
        internal static RectTransform Apply(Transform safeArea,
            VufScreenCatalog.StyleInfo style)
        {
            if (safeArea == null || style == null || style.palettes == null ||
                Array.IndexOf(Profiles, style.id) < 0 ||
                safeArea.GetComponent<VufSafeAreaFitter>() == null)
                throw new ArgumentException("unsupported profile or draft safe-area");
            if (safeArea.Find("ThemeMotifs_" + style.id) != null)
                throw new InvalidOperationException("theme motifs already authored");
            Color accent = VufScreenCatalog.ParseColor(style.palettes.accent, "accent");
            GameObject go = new GameObject("ThemeMotifs_" + style.id,
                typeof(RectTransform));
            RectTransform root = go.GetComponent<RectTransform>();
            root.SetParent(safeArea, false);
            root.anchorMin = Vector2.zero;
            root.anchorMax = Vector2.one;
            root.offsetMin = Vector2.zero;
            root.offsetMax = Vector2.zero;
            switch (style.id)
            {
                case "Coral_Rescue": Coral(root, accent); break;
                case "Garage_Legends": Garage(root, accent); break;
                case "Dino_Islands": Dino(root, accent); break;
                case "The_Fractured_Realms": Fractured(root, accent); break;
                case "Wonder_Pop": Wonder(root, accent); break;
                default: throw new ArgumentException("unknown style profile");
            }
            return root;
        }
    }
}
