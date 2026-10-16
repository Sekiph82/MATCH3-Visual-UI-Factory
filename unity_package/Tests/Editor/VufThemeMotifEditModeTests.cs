using System;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.UI;
using Match3.VisualFactory.Editor;

namespace Match3.VisualFactory.Tests
{
    public sealed class VufThemeMotifEditModeTests
    {
        private static readonly string[] Themes = {
            "Coral_Rescue", "Garage_Legends", "Dino_Islands",
            "The_Fractured_Realms", "Wonder_Pop"
        };
        private static readonly string[] ExpectedPrefix = {
            "CORAL_", "GARAGE_", "DINO_", "REALMS_", "WONDER_"
        };
        private static readonly int[] ExpectedCount = { 12, 12, 10, 9, 18 };

        [Test]
        public void FiveThemesProduceDistinctEditableGeometricMotifs()
        {
            for (int i = 0; i < Themes.Length; i++)
            {
                var safe = new GameObject("SafeArea_TEST_ONLY",
                    typeof(RectTransform), typeof(VufSafeAreaFitter));
                try
                {
                    RectTransform holder = VufThemeMotifDecor.Apply(
                        safe.transform, VufScreenCatalog.LoadStyle(Themes[i]));
                    Assert.That(holder.name, Is.EqualTo("ThemeMotifs_" + Themes[i]));
                    Assert.That(holder.childCount, Is.EqualTo(ExpectedCount[i]));
                    for (int j = 0; j < holder.childCount; j++)
                        Assert.That(holder.GetChild(j).name,
                            Does.StartWith(ExpectedPrefix[i]));
                    Assert.That(holder.GetComponentsInChildren<Image>().Length,
                        Is.GreaterThanOrEqualTo(ExpectedCount[i]));
                    foreach (Graphic image in holder.GetComponentsInChildren<Graphic>())
                        Assert.That(image.raycastTarget, Is.False);
                    Assert.That(holder.GetComponentsInChildren<Button>().Length, Is.Zero);
                }
                finally { UnityEngine.Object.DestroyImmediate(safe); }
            }
        }

        [Test]
        public void CallingTwiceRejectsDuplicationWithoutChangingExistingNodes()
        {
            var safe = new GameObject("SafeArea_TEST_ONLY",
                typeof(RectTransform), typeof(VufSafeAreaFitter));
            try
            {
                var style = VufScreenCatalog.LoadStyle("Garage_Legends");
                RectTransform first = VufThemeMotifDecor.Apply(safe.transform, style);
                int childCount = first.childCount;
                Assert.Throws<InvalidOperationException>(() =>
                    VufThemeMotifDecor.Apply(safe.transform, style));
                Assert.That(first.childCount, Is.EqualTo(childCount));
                Assert.That(safe.transform.childCount, Is.EqualTo(1));
            }
            finally { UnityEngine.Object.DestroyImmediate(safe); }
        }

        [Test]
        public void MissingSafeAreaAndUnknownStyleAreRejectedBeforeMutation()
        {
            var parent = new GameObject("TEST_ONLY_Unbound", typeof(RectTransform));
            try
            {
                var original = VufScreenCatalog.LoadStyle("Dino_Islands");
                Assert.Throws<ArgumentException>(() =>
                    VufThemeMotifDecor.Apply(parent.transform, original));
                parent.AddComponent<VufSafeAreaFitter>();
                var tampered = new VufScreenCatalog.StyleInfo {
                    id = "Unapproved_Game", palettes = original.palettes
                };
                Assert.Throws<ArgumentException>(() =>
                    VufThemeMotifDecor.Apply(parent.transform, tampered));
                Assert.That(parent.transform.childCount, Is.Zero);
            }
            finally { UnityEngine.Object.DestroyImmediate(parent); }
        }

        [Test]
        public void ThemeDecorationNeverAddsGameplayOrEngineDependencies()
        {
            var parent = new GameObject("TEST_ONLY_Safe", typeof(RectTransform),
                typeof(VufSafeAreaFitter));
            try
            {
                VufThemeMotifDecor.Apply(parent.transform,
                    VufScreenCatalog.LoadStyle("The_Fractured_Realms"));
                Assert.That(parent.GetComponentsInChildren<Button>().Length, Is.Zero);
                Assert.That(parent.GetComponentsInChildren<GraphicRaycaster>().Length,
                    Is.Zero);
                foreach (Graphic item in parent.GetComponentsInChildren<Graphic>())
                    Assert.That(item.raycastTarget, Is.False);
            }
            finally { UnityEngine.Object.DestroyImmediate(parent); }
        }
    }
}
