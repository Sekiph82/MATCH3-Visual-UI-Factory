"""R41 direct BSD3 FlowLayoutGroup donor reuse/source contract."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]

class DonorFlowContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.donor=(ROOT/"unity_package/Editor/ThirdParty/FlowLayoutGroup.cs").read_text()
        cls.page=(ROOT/"unity_package/Editor/VufPageComposition.cs").read_text()
        cls.ledger=(ROOT/"docs/VUF_DONOR_SOURCE_LEDGER.md").read_text()
        cls.nunit=(ROOT/"unity_package/Tests/Editor/VufDonorFlowLayoutEditModeTests.cs").read_text()

    def test_upstream_credit_and_exact_pinned_source_receipt(self):
        self.assertIn("Credit Simie",self.donor)
        self.assertIn("a949d0c23d27124c3347405972cca7bb7a7a3489",self.donor)
        self.assertIn("class FlowLayoutGroup : LayoutGroup",self.donor)
        self.assertIn("FlowLayoutGroup.cs",self.ledger)

    def test_original_wrapping_algorithm_not_rewritten(self):
        self.assertIn("public float SetLayout(int axis, bool layoutInput)",self.donor)
        self.assertIn("ChildForceExpandCrossAxis",self.donor)
        self.assertIn("AddComponent<FlowLayoutGroup>()",self.page)
        self.assertIn("element.preferredWidth = 104f",self.page)
        self.assertIn("element.preferredHeight = 68f",self.page)
        self.assertIn("image.raycastTarget = false",self.page)

    def test_layout_input_calls_match_unity_6_axis_signature(self):
        self.assertIn("SetLayoutInputForAxis(minWidth, -1, -1, -1, 0)", self.donor)
        self.assertIn("SetLayoutInputForAxis(minHeight, -1, -1, -1, 1)", self.donor)
        self.assertIn("SetLayoutInputForAxis(offset, -1, offset, -1, axis)", self.donor)

    def test_stable_meta_and_genuine_nunit_definitions(self):
        self.assertTrue((ROOT/"unity_package/Editor/ThirdParty/FlowLayoutGroup.cs.meta").exists())
        self.assertTrue((ROOT/"unity_package/Tests/Editor/VufDonorFlowLayoutEditModeTests.cs.meta").exists())
        self.assertEqual(self.nunit.count("[Test]"),2)
        self.assertIn("ActualDonorReflowsOnNarrowAndWideAuthoringPanels",self.nunit)

if __name__=="__main__":unittest.main()
