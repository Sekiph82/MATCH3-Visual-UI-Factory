using System;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.UI;
using Match3.VisualFactory.Editor;

namespace Match3.VisualFactory.Tests
{
    public sealed class VufPageCompositionEditModeTests
    {
        private static readonly string[] Themes = {
            "Coral_Rescue", "Garage_Legends", "Dino_Islands",
            "The_Fractured_Realms", "Wonder_Pop"
        };
        private static readonly string[] Pages = { "home", "gameplay", "world_map" };

        [Test]
        public void AllFifteenDraftThemePageLayoutsAreDistinctAndEditable()
        {
            int count = 0;
            foreach (string theme in Themes)
            foreach (string page in Pages)
            {
                var root = new GameObject("TEST_ONLY_Composition",
                    typeof(RectTransform), typeof(VufSafeAreaFitter));
                try
                {
                    VufPageComposition.Compose(root.transform,
                        VufScreenCatalog.LoadStyle(theme), page);
                    Assert.That(root.GetComponentsInChildren<Image>().Length,
                        Is.GreaterThanOrEqualTo(7));
                    Assert.That(root.GetComponentsInChildren<Text>().Length,
                        Is.GreaterThanOrEqualTo(1));
                    Assert.That(root.GetComponentsInChildren<Button>().Length, Is.Zero);
                    foreach (Graphic graphic in root.GetComponentsInChildren<Graphic>())
                        Assert.That(graphic.raycastTarget, Is.False,
                            "component kit cannot capture game input");
                    if (page == "home")
                    {
                        Assert.That(root.transform.Find("HOME_HeroArtworkPlaceholder"),
                            Is.Not.Null);
                        Assert.That(root.transform.Find("GAMEPLAY_Grid6x7_VISUAL_ONLY"),
                            Is.Null);
                    }
                    else if (page == "gameplay")
                    {
                        Transform board = root.transform.Find("GAMEPLAY_Grid6x7_VISUAL_ONLY");
                        Assert.That(board, Is.Not.Null);
                        Assert.That(board.childCount, Is.EqualTo(42));
                    }
                    else
                    {
                        Transform map = root.transform.Find("WORLD_EditableMapCanvas");
                        Assert.That(map, Is.Not.Null);
                        Assert.That(map.childCount, Is.EqualTo(13));
                    }
                    count++;
                }
                finally { UnityEngine.Object.DestroyImmediate(root); }
            }
            Assert.That(count, Is.EqualTo(15));
        }

        [Test]
        public void DuplicateCompositionFailsInsteadOfStackingInvisibleScreens()
        {
            var root = new GameObject("TEST_ONLY_Duplicate", typeof(RectTransform),
                typeof(VufSafeAreaFitter));
            try
            {
                var style = VufScreenCatalog.LoadStyle("Wonder_Pop");
                VufPageComposition.Compose(root.transform, style, "home");
                int children = root.transform.childCount;
                Assert.Throws<InvalidOperationException>(() =>
                    VufPageComposition.Compose(root.transform, style, "world_map"));
                Assert.That(root.transform.childCount, Is.EqualTo(children));
            }
            finally { UnityEngine.Object.DestroyImmediate(root); }
        }

        [Test]
        public void MissingSafeAreaAndUnknownPageFailClosed()
        {
            var root = new GameObject("TEST_ONLY_NoSafeArea",
                typeof(RectTransform));
            try
            {
                var style = VufScreenCatalog.LoadStyle("Coral_Rescue");
                Assert.Throws<ArgumentException>(() =>
                    VufPageComposition.Compose(root.transform, style, "home"));
                root.AddComponent<VufSafeAreaFitter>();
                Assert.Throws<ArgumentException>(() =>
                    VufPageComposition.Compose(root.transform, style, "reward"));
                Assert.That(root.transform.childCount, Is.Zero);
            }
            finally { UnityEngine.Object.DestroyImmediate(root); }
        }

        [Test]
        public void WorldMapContainsSevenStaticUnboundMarkersAndSixPaths()
        {
            var root = new GameObject("TEST_ONLY_World", typeof(RectTransform),
                typeof(VufSafeAreaFitter));
            try
            {
                VufPageComposition.Compose(root.transform,
                    VufScreenCatalog.LoadStyle("Dino_Islands"), "world_map");
                Transform map = root.transform.Find("WORLD_EditableMapCanvas");
                for (int i = 1; i <= 7; i++)
                    Assert.That(map.Find("WORLD_LevelNode_UNBOUND_" + i.ToString("D2")),
                        Is.Not.Null);
                for (int i = 1; i <= 6; i++)
                    Assert.That(map.Find("WORLD_PathSegment_STATIC_" + i),
                        Is.Not.Null);
                Assert.That(root.GetComponentsInChildren<Button>().Length, Is.Zero);
            }
            finally { UnityEngine.Object.DestroyImmediate(root); }
        }
    }
}
