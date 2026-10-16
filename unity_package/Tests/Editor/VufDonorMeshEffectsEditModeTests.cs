using System;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.UI;
using Match3.VisualFactory.Editor;
using Match3.VisualFactory.Editor.ThirdParty;

namespace Match3.VisualFactory.Tests
{
    public sealed class VufDonorMeshEffectsEditModeTests
    {
        private static VertexHelper Quad(float lowY, float highY)
        {
            var helper = new VertexHelper();
            var first = UIVertex.simpleVert;
            first.position = new Vector3(-40f, highY, 0f);
            helper.AddVert(first);
            first.position = new Vector3(40f, highY, 0f);
            helper.AddVert(first);
            first.position = new Vector3(40f, lowY, 0f);
            helper.AddVert(first);
            first.position = new Vector3(-40f, lowY, 0f);
            helper.AddVert(first);
            helper.AddTriangle(0, 1, 2);
            helper.AddTriangle(2, 3, 0);
            return helper;
        }

        [Test]
        public void UpstreamGradientCanShadeARealUiImageWithoutChangingInputPolicy()
        {
            var obj = new GameObject("TEST_ONLY_BSD_Gradient",
                typeof(RectTransform), typeof(Image), typeof(Match3.VisualFactory.Editor.ThirdParty.Gradient));
            try
            {
                var image = obj.GetComponent<Image>();
                image.raycastTarget = false;
                var donor = obj.GetComponent<Match3.VisualFactory.Editor.ThirdParty.Gradient>();
                donor.OverwriteAllColor = true;
                donor.GradientMode =
                    Match3.VisualFactory.Editor.ThirdParty.GradientMode.Global;
                donor.GradientDir = GradientDir.Vertical;
                donor.Vertex1 = Color.white;
                donor.Vertex2 = Color.black;
                using (var vh = Quad(-40f, 40f))
                {
                    donor.ModifyMesh(vh);
                    var top = new UIVertex();
                    var bottom = new UIVertex();
                    vh.PopulateUIVertex(ref top, 0);
                    vh.PopulateUIVertex(ref bottom, 2);
                    Assert.That(top.color.r, Is.GreaterThan(bottom.color.r));
                    Assert.That(vh.currentVertCount, Is.EqualTo(4));
                }
                Assert.That(image.raycastTarget, Is.False);
            }
            finally { UnityEngine.Object.DestroyImmediate(obj); }
        }

        [Test]
        public void PatchedDonorZeroHeightGeometryDoesNotProduceInvalidColors()
        {
            var obj = new GameObject("TEST_ONLY_Collapsed",
                typeof(RectTransform), typeof(Image),
                typeof(Match3.VisualFactory.Editor.ThirdParty.Gradient));
            try
            {
                var donor = obj.GetComponent<Match3.VisualFactory.Editor.ThirdParty.Gradient>();
                donor.OverwriteAllColor = true;
                using (var vh = Quad(0f, 0f))
                {
                    Assert.DoesNotThrow(() => donor.ModifyMesh(vh));
                    UIVertex v = new UIVertex();
                    vh.PopulateUIVertex(ref v, 0);
                    Assert.That(float.IsNaN(v.position.y), Is.False);
                }
            }
            finally { UnityEngine.Object.DestroyImmediate(obj); }
        }

        [Test]
        public void CopiedFlippableMirrorsActualUiVerticesWithoutCallbacks()
        {
            var obj = new GameObject("TEST_ONLY_BSD_Flippable",
                typeof(RectTransform), typeof(Image), typeof(UIFlippable));
            try
            {
                var rect = obj.GetComponent<RectTransform>();
                rect.sizeDelta = new Vector2(100f, 80f);
                var flip = obj.GetComponent<UIFlippable>();
                flip.horizontal = true;
                flip.vertical = false;
                using (var vh = Quad(-25f, 25f))
                {
                    UIVertex before = new UIVertex(), after = new UIVertex();
                    vh.PopulateUIVertex(ref before, 0);
                    flip.ModifyMesh(vh);
                    vh.PopulateUIVertex(ref after, 0);
                    Assert.That(after.position.x, Is.EqualTo(-before.position.x)
                        .Within(.01f));
                    Assert.That(after.position.y, Is.EqualTo(before.position.y)
                        .Within(.01f));
                }
                Assert.That(obj.GetComponent<Button>(), Is.Null);
            }
            finally { UnityEngine.Object.DestroyImmediate(obj); }
        }

        [Test]
        public void AllFiveThemesRetainSpecializedArtNotGenericOnlyColor()
        {
            var style = VufScreenCatalog.LoadStyle("Dino_Islands");
            var stage = new GameObject("TEST_ONLY_DonorIntegration",
                typeof(RectTransform), typeof(VufSafeAreaFitter));
            try
            {
                VufThemeMotifDecor.Apply(stage.transform, style);
                VufPageComposition.Compose(stage.transform, style, "home");
                Transform leaf = stage.transform.Find(
                    "ThemeMotifs_Dino_Islands/DINO_FrondStem_00/DINO_LeafRight");
                Assert.That(leaf, Is.Not.Null);
                Assert.That(leaf.GetComponent<UIFlippable>().horizontal, Is.True);
                var hero = stage.transform.Find("HOME_HeroArtworkPlaceholder");
                Assert.That(hero, Is.Not.Null);
                Assert.That(hero.GetComponent<
                    Match3.VisualFactory.Editor.ThirdParty.Gradient>(), Is.Not.Null);
                foreach (Button button in stage.GetComponentsInChildren<Button>())
                    Assert.That(button.interactable, Is.False);
            }
            finally { UnityEngine.Object.DestroyImmediate(stage); }
        }
    }
}
