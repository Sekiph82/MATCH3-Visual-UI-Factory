// M08 | Unity in-memory uGUI tap/layout source tests; true user touch QA OPEN.
using System;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.UI;
using Match3.VisualFactory.Editor;

namespace Match3.VisualFactory.Tests
{
    public sealed class VufInteractiveUiReviewEditModeTests
    {
        private GameObject root;
        private Button button;
        private VufCandidateScreenMarker marker;

        [SetUp]
        public void SetUp()
        {
            root = new GameObject("temporary_no_save_candidate",
                typeof(RectTransform), typeof(VufCandidateScreenMarker));
            marker = root.GetComponent<VufCandidateScreenMarker>();
            marker.SetCandidate("Coral_Rescue", "COR-27", "home", "page",
                "REQUIRES_ENGINE_OR_GAME_BINDING");
            var node = new GameObject("OwnerAction_UNBOUND",
                typeof(RectTransform), typeof(Image), typeof(Button));
            node.transform.SetParent(root.transform, false);
            button = node.GetComponent<Button>();
            button.interactable = false;
        }

        [TearDown]
        public void TearDown()
        {
            if (root != null) UnityEngine.Object.DestroyImmediate(root);
        }

        private void MakeTemporary()
        {
            root.hideFlags = HideFlags.DontSaveInEditor | HideFlags.DontSaveInBuild;
        }

        [Test]
        public void ExplicitTempEditorOnlyTapFiresOnlyLocalCounterNoGameBinding()
        {
            MakeTemporary();
            int count = 0;
            Assert.That(VufInteractiveUiReviewWindow.EnableOnlyPreviewButton(
                root, button, () => count++), Is.True);
            Assert.That(button.interactable, Is.True);
            Assert.That(button.onClick.GetPersistentEventCount(), Is.Zero);
            button.onClick.Invoke();
            button.onClick.Invoke();
            Assert.That(count, Is.EqualTo(2));
        }

        [Test]
        public void PersistentOwnerPrefabOrSceneNeverGetsEnabledAsTestAction()
        {
            int count = 0;
            Assert.Throws<InvalidOperationException>(() =>
                VufInteractiveUiReviewWindow.EnableOnlyPreviewButton(
                    root, button, () => count++));
            Assert.That(button.interactable, Is.False);
            Assert.That(count, Is.Zero);
        }

        [Test]
        public void PolicyOffNeverAllowsTapEvenInsideTemporaryPreview()
        {
            MakeTemporary();
            marker.SetCandidate("Coral_Rescue", "COR-20", "tournament", "page",
                "OFF_UNTIL_ENGINE_POLICY_CONFIRMED");
            int count = 0;
            Assert.That(VufInteractiveUiReviewWindow.EnableOnlyPreviewButton(
                root, button, () => count++), Is.False);
            Assert.That(button.interactable, Is.False);
            Assert.That(count, Is.Zero);
        }

        [Test]
        public void WrongOwnerOrNullActionIsRejectedBeforeButtonMutation()
        {
            MakeTemporary();
            var other = new GameObject("other_candidate", typeof(RectTransform));
            try
            {
                Assert.Throws<ArgumentException>(() =>
                    VufInteractiveUiReviewWindow.EnableOnlyPreviewButton(
                        other, button, () => { }));
                Assert.Throws<ArgumentException>(() =>
                    VufInteractiveUiReviewWindow.EnableOnlyPreviewButton(
                        root, button, null));
                Assert.That(button.interactable, Is.False);
            }
            finally { UnityEngine.Object.DestroyImmediate(other); }
        }

        [Test]
        public void RealShellBuilderMaintainsItsBlockedSourceButtonContract()
        {
            var spec = VufScreenCatalog.LoadScreens()[26]; // COR-27 home
            var style = VufScreenCatalog.LoadStyle("Coral_Rescue");
            var page = VufScreenShellBuilderWindow.BuildCandidateHierarchy(
                spec, style, true);
            try
            {
                var buttons = page.GetComponentsInChildren<Button>(true);
                Assert.That(buttons.Length, Is.EqualTo(1));
                Assert.That(buttons[0].interactable, Is.False);
                Assert.That(buttons[0].onClick.GetPersistentEventCount(), Is.Zero);
                Assert.That(page.GetComponent<VufCandidateScreenMarker>()
                    .CandidateStatus, Is.EqualTo("CANDIDATE_NOT_APPROVED"));
                Assert.That(page.GetComponentsInChildren<VufSafeAreaFitter>(true).Length,
                    Is.GreaterThan(0));
            }
            finally { UnityEngine.Object.DestroyImmediate(page); }
        }
    }
}
