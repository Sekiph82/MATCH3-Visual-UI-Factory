"""R37-R38 donor reuse and license/source contracts (source only).

These static checks are not substitutes for a true Unity Editor compile/NUnit run.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class DonorFirstVisualContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        def read(path):
            return (ROOT / path).read_text(encoding="utf-8")
        cls.donor = read("unity_package/Editor/ThirdParty/NonDrawingGraphic.cs")
        cls.license = read("third_party/UnityUIExtensions/LICENSE.md")
        cls.stage = read("unity_package/Editor/VufConceptStageBuilderWindow.cs")
        cls.motion = read("unity_package/Editor/VufCandidateMotionKit.cs")
        cls.reuse = read("unity_package/Runtime/VufUiTween.cs")
        cls.ledger = read("docs/VUF_DONOR_SOURCE_LEDGER.md")

    def test_source_was_actually_copied_with_original_credit_and_bsd_licence(self):
        self.assertIn("Credit Slipp Douglas Thompson", self.donor)
        self.assertIn("capnslipp/349c18283f2fea316369", self.donor)
        self.assertIn("class NonDrawingGraphic : MaskableGraphic", self.donor)
        self.assertIn("vh.Clear();", self.donor)
        self.assertIn("BSD-3-Clause", self.license)
        self.assertIn("Redistributions in source", self.license)
        self.assertIn("Unity-UI-Extensions/com.unity.uiextensions", self.ledger)
        self.assertIn("abd42d8920aedfc7c4f887a0c6ea02496a57849c", self.ledger)

    def test_editable_stage_has_non_drawn_shield_without_activation(self):
        self.assertIn("NonDrawingGraphic shield = blocker.gameObject.AddComponent", self.stage)
        self.assertIn("shield.raycastTarget = true;", self.stage)
        self.assertIn("AUTHORING_ONLY_InputShield", self.stage)
        self.assertIn("button.interactable = false;", self.stage)
        self.assertIn("raw.raycastTarget = false;", self.stage)
        self.assertIn("VufCandidateMotionKit.Attach", self.stage)

    def test_existing_motion_engine_reused_not_reimplemented(self):
        self.assertIn("GetComponent<VufUiTween>()", self.motion)
        self.assertIn("target.gameObject.AddComponent<VufUiTween>()", self.motion)
        self.assertIn("tween.SetReducedMotion(true)", self.motion)
        self.assertIn("group.blocksRaycasts = false", self.motion)
        self.assertIn("private void StartTransition(float target)", self.reuse)
        self.assertNotIn("LeanTween", self.motion)
        self.assertNotIn("DOTween", self.motion)

    def test_license_meta_and_actual_nunit_test_sources_are_present(self):
        paths = [
            "unity_package/Editor/ThirdParty/NonDrawingGraphic.cs.meta",
            "unity_package/Editor/VufCandidateMotionKit.cs.meta",
            "unity_package/Tests/Editor/VufOpenSourceDonorEditModeTests.cs.meta",
            "unity_package/Tests/Editor/VufCandidateMotionReuseEditModeTests.cs.meta"
        ]
        for p in paths:
            self.assertTrue((ROOT / p).is_file(), p)
        first = (ROOT / "unity_package/Tests/Editor/"
                 "VufOpenSourceDonorEditModeTests.cs").read_text()
        second = (ROOT / "unity_package/Tests/Editor/"
                  "VufCandidateMotionReuseEditModeTests.cs").read_text()
        self.assertEqual(first.count("[Test]"), 2)
        self.assertEqual(second.count("[Test]"), 3)

    def test_no_prohibited_restricted_or_engine_donors_vendored(self):
        # The negative license decision is explicit and persists in a ledger.
        self.assertIn("Rimaethon/Gem-Match3", self.ledger)
        self.assertIn("Do NOT copy", self.ledger)
        self.assertIn("Unity-Technologies/Game-Simulation-Match-3-Sample",
                      self.ledger)
        self.assertIn("LibraStack/Match3-SDK", self.ledger)


if __name__ == "__main__":
    unittest.main()
