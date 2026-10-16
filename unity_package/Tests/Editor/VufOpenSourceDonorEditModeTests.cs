using System;
using System.Reflection;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.UI;
using Match3.VisualFactory.Editor.ThirdParty;

namespace Match3.VisualFactory.Tests
{
    public sealed class VufOpenSourceDonorEditModeTests
    {
        [Test]
        public void BSD3DonorIsAnInvisibleEditorUiRaycastTarget()
        {
            var root = new GameObject("TEST_ONLY_Donor",
                typeof(RectTransform), typeof(NonDrawingGraphic));
            try
            {
                NonDrawingGraphic target = root.GetComponent<NonDrawingGraphic>();
                Assert.That(target, Is.InstanceOf<MaskableGraphic>());
                Assert.That(target.raycastTarget, Is.True);
                Assert.That(root.GetComponent<Image>(), Is.Null);
                // This directly exercises the donor's empty-mesh effect.
                MethodInfo render = typeof(NonDrawingGraphic).GetMethod(
                    "OnPopulateMesh", BindingFlags.NonPublic | BindingFlags.Instance,
                    null, new[] { typeof(VertexHelper) }, null);
                Assert.That(render, Is.Not.Null);
                using (var vh = new VertexHelper())
                {
                    var v = UIVertex.simpleVert;
                    vh.AddVert(v);
                    Assert.That(vh.currentVertCount, Is.EqualTo(1));
                    render.Invoke(target, new object[] {vh});
                    Assert.That(vh.currentVertCount, Is.Zero);
                }
            }
            finally { UnityEngine.Object.DestroyImmediate(root); }
        }

        [Test]
        public void DonorCanBePlacedAboveCandidateButtonsWithoutActivatingThem()
        {
            var root = new GameObject("TEST_ONLY_Safe", typeof(RectTransform));
            try
            {
                var buttonNode = new GameObject("CandidateAction",
                    typeof(RectTransform), typeof(Image), typeof(Button));
                buttonNode.transform.SetParent(root.transform, false);
                buttonNode.GetComponent<Button>().interactable = false;
                var shield = new GameObject("InputShield",
                    typeof(RectTransform), typeof(NonDrawingGraphic));
                shield.transform.SetParent(root.transform, false);
                Assert.That(shield.transform.GetSiblingIndex(),
                    Is.EqualTo(root.transform.childCount - 1));
                Assert.That(shield.GetComponent<NonDrawingGraphic>().raycastTarget,
                    Is.True);
                Assert.That(root.GetComponentInChildren<Button>().interactable,
                    Is.False);
                Assert.That(root.GetComponentInChildren<Button>().onClick
                    .GetPersistentEventCount(), Is.Zero);
            }
            finally { UnityEngine.Object.DestroyImmediate(root); }
        }
    }
}
