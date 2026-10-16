"""R42 donor-first proof for upstream radial authoring layout (source-only)."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class DonorRadialLayoutContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.donor = (
            ROOT / "unity_package/Runtime/ThirdParty/RadialLayout.cs"
        ).read_text(encoding="utf-8")
        cls.layout = (
            ROOT / "unity_package/Editor/VufPageComposition.cs"
        ).read_text(encoding="utf-8")
        cls.nunit = (
            ROOT / "unity_package/Tests/Editor/VufDonorRadialLayoutEditModeTests.cs"
        ).read_text(encoding="utf-8")
        cls.ledger = (
            ROOT / "docs/VUF_DONOR_SOURCE_LEDGER.md"
        ).read_text(encoding="utf-8")

    def test_original_provenance_embedded_mit_notice_and_bsd_disclaimer_preserved(self):
        self.assertIn("Credit Danny Goodayle", self.donor)
        self.assertIn("Copyright (c) 2015", self.donor)
        self.assertIn("Permission is hereby granted", self.donor)
        self.assertIn("fc07fac023536cd54f350e8aa3d06c2015c1782c", self.donor)
        self.assertIn("BSD-3-Clause", self.donor)
        self.assertIn("RadialLayout.cs", self.ledger)

    def test_source_is_an_adaptation_not_a_reinvented_positioning_algorithm(self):
        self.assertIn("class RadialLayout : LayoutGroup", self.donor)
        self.assertIn("child.localPosition = vPos * fDistance", self.donor)
        self.assertIn("if (ChildrenToFormat == 0) return;", self.donor)
        self.assertIn("AddComponent<RadialLayout>()", self.layout)
        self.assertIn("HOME_OrbitLayout_AUTHORING_ONLY", self.layout)
        self.assertIn("HOME_OrbitBadge_STATIC_", self.layout)
        self.assertIn("radial.CalculateLayoutInputHorizontal()", self.layout)

    def test_no_gameplay_input_or_existing_art_modified(self):
        self.assertNotIn("UnityWebRequest", self.donor)
        self.assertNotIn("AssetDatabase", self.donor)
        self.assertNotIn("OnClick", self.donor)
        self.assertIn("image.raycastTarget = false;", self.layout)
        self.assertEqual(self.nunit.count("[Test]"), 3)


if __name__ == "__main__":
    unittest.main()
