using System;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.UI;
using Match3.VisualFactory.Editor;
using Match3.VisualFactory.Editor.ThirdParty;

namespace Match3.VisualFactory.Tests
{
    public sealed class VufDonorFlowLayoutEditModeTests
    {
        [Test]
        public void FourCollectionCardsUseActualUpstreamWrappingLayoutGroup()
        {
            var root = new GameObject("TEST_ONLY_Flow", typeof(RectTransform),
                typeof(VufSafeAreaFitter));
            try
            {
                VufPageComposition.Compose(root.transform,
                    VufScreenCatalog.LoadStyle("Coral_Rescue"), "home");
                Transform collection = root.transform.Find("HOME_CollectionSlots");
                Assert.That(collection, Is.Not.Null);
                FlowLayoutGroup donor = collection.GetComponent<FlowLayoutGroup>();
                Assert.That(donor, Is.Not.Null);
                Assert.That(collection.childCount, Is.EqualTo(4));
                Assert.That(donor.SpacingX, Is.EqualTo(9f));
                Assert.That(donor.SpacingY, Is.EqualTo(5f));
                foreach (Transform item in collection)
                {
                    LayoutElement el = item.GetComponent<LayoutElement>();
                    Assert.That(el, Is.Not.Null);
                    Assert.That(el.preferredWidth, Is.EqualTo(104f));
                    Assert.That(el.preferredHeight, Is.EqualTo(68f));
                    Assert.That(item.GetComponent<Graphic>().raycastTarget, Is.False);
                }
                Assert.That(root.GetComponentsInChildren<Button>().Length, Is.Zero);
            }
            finally { UnityEngine.Object.DestroyImmediate(root); }
        }

        [Test]
        public void ActualDonorReflowsOnNarrowAndWideAuthoringPanels()
        {
            var root = new GameObject("TEST_ONLY_Reflow", typeof(RectTransform),
                typeof(VufSafeAreaFitter));
            try
            {
                VufPageComposition.Compose(root.transform,
                    VufScreenCatalog.LoadStyle("Garage_Legends"), "home");
                var panel = root.transform.Find("HOME_CollectionSlots")
                    .GetComponent<RectTransform>();
                var donor = panel.GetComponent<FlowLayoutGroup>();
                foreach (float width in new [] { 210f, 580f })
                {
                    panel.anchorMin = new Vector2(.5f, .5f);
                    panel.anchorMax = new Vector2(.5f, .5f);
                    panel.sizeDelta = new Vector2(width, 190f);
                    Assert.DoesNotThrow(() => {
                        donor.CalculateLayoutInputHorizontal();
                        donor.CalculateLayoutInputVertical();
                        donor.SetLayoutHorizontal();
                        donor.SetLayoutVertical();
                    });
                    foreach (Transform child in panel)
                    {
                        Vector2 p = ((RectTransform)child).anchoredPosition;
                        Assert.That(float.IsNaN(p.x), Is.False);
                        Assert.That(float.IsNaN(p.y), Is.False);
                    }
                }
            }
            finally { UnityEngine.Object.DestroyImmediate(root); }
        }
    }
}
