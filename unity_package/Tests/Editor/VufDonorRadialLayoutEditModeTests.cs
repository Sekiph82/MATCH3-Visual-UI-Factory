using System;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.UI;
using Match3.VisualFactory.Editor;
using Match3.VisualFactory.Editor.ThirdParty;

namespace Match3.VisualFactory.Tests
{
    public sealed class VufDonorRadialLayoutEditModeTests
    {
        [Test]
        public void ExistingHomeCompositionUsesActualFiveBadgeRadialDonor()
        {
            var root = new GameObject("TEST_ONLY_HomeRadial",
                typeof(RectTransform), typeof(VufSafeAreaFitter));
            try
            {
                VufPageComposition.Compose(root.transform,
                    VufScreenCatalog.LoadStyle("Coral_Rescue"), "home");
                Transform hero = root.transform.Find("HOME_HeroArtworkPlaceholder");
                Assert.That(hero, Is.Not.Null);
                Transform orbit = hero.Find("HOME_OrbitLayout_AUTHORING_ONLY");
                Assert.That(orbit, Is.Not.Null);
                RadialLayout donor = orbit.GetComponent<RadialLayout>();
                Assert.That(donor, Is.Not.Null);
                Assert.That(donor.fDistance, Is.EqualTo(135f));
                Assert.That(orbit.childCount, Is.EqualTo(5));
                donor.CalculateLayoutInputHorizontal();
                Vector3 previous = Vector3.positiveInfinity;
                for (int index = 0; index < 5; index++)
                {
                    Transform badge = orbit.Find("HOME_OrbitBadge_STATIC_" +
                        (index + 1).ToString("D2"));
                    Assert.That(badge, Is.Not.Null);
                    Assert.That(badge.localPosition.magnitude, Is.EqualTo(135f)
                        .Within(.5f));
                    Assert.That(Vector3.Distance(previous, badge.localPosition),
                        Is.GreaterThan(5f));
                    previous = badge.localPosition;
                    Assert.That(badge.GetComponent<Graphic>().raycastTarget, Is.False);
                }
                Assert.That(root.GetComponentsInChildren<Button>().Length, Is.Zero);
            }
            finally { UnityEngine.Object.DestroyImmediate(root); }
        }

        [Test]
        public void UpstreamEmptyAndAllInactiveLayoutsRemainSafe()
        {
            var groupRoot = new GameObject("TEST_ONLY_EmptyRadial",
                typeof(RectTransform), typeof(RadialLayout));
            try
            {
                RadialLayout donor = groupRoot.GetComponent<RadialLayout>();
                donor.OnlyLayoutVisible = true;
                Assert.DoesNotThrow(() => donor.CalculateLayoutInputHorizontal());
                var child = new GameObject("TEST_ONLY_InactiveBadge",
                    typeof(RectTransform));
                child.transform.SetParent(groupRoot.transform, false);
                child.SetActive(false);
                Assert.DoesNotThrow(() => donor.CalculateLayoutInputHorizontal());
                Assert.That(((RectTransform)child.transform).anchoredPosition,
                    Is.EqualTo(Vector2.zero));
            }
            finally { UnityEngine.Object.DestroyImmediate(groupRoot); }
        }

        [Test]
        public void DonorRepositionsAfterStartAngleChangesWithoutEnablingInput()
        {
            var root = new GameObject("TEST_ONLY_Rotation", typeof(RectTransform),
                typeof(VufSafeAreaFitter));
            try
            {
                VufPageComposition.Compose(root.transform,
                    VufScreenCatalog.LoadStyle("Wonder_Pop"), "home");
                var orbit = root.transform.Find(
                    "HOME_HeroArtworkPlaceholder/HOME_OrbitLayout_AUTHORING_ONLY");
                RadialLayout donor = orbit.GetComponent<RadialLayout>();
                Transform first = orbit.GetChild(0);
                donor.CalculateLayoutInputHorizontal();
                Vector3 before = first.localPosition;
                donor.StartAngle = 64f;
                donor.CalculateLayoutInputHorizontal();
                Assert.That(Vector3.Distance(first.localPosition, before),
                    Is.GreaterThan(15f));
                foreach (Graphic graphic in orbit.GetComponentsInChildren<Graphic>())
                    Assert.That(graphic.raycastTarget, Is.False);
            }
            finally { UnityEngine.Object.DestroyImmediate(root); }
        }
    }
}
