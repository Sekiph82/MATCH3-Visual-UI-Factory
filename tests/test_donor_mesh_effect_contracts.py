"""R39-R40 source/rights guards for direct BSD3 gradient & mirroring donors.

Real Unity EditMode execution still required for mesh-effect correctness.
"""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]

class DonorMeshEffectsContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        def read(path):
            return (ROOT/path).read_text(encoding="utf-8")
        cls.gradient=read("unity_package/Editor/ThirdParty/Gradient.cs")
        cls.flip=read("unity_package/Editor/ThirdParty/UIFlippable.cs")
        cls.page=read("unity_package/Editor/VufPageComposition.cs")
        cls.motif=read("unity_package/Editor/VufThemeMotifDecor.cs")
        cls.nunit=read("unity_package/Tests/Editor/VufDonorMeshEffectsEditModeTests.cs")
        cls.ledger=read("docs/VUF_DONOR_SOURCE_LEDGER.md")
        cls.license=read("third_party/UnityUIExtensions/LICENSE.md")

    def test_direct_vendor_original_authors_and_exact_upstream_blob_provenance(self):
        self.assertIn("Credit Breyer",self.gradient)
        self.assertIn("Credit ChoMPHi",self.flip)
        self.assertIn("d3387fd4c917196209079970e436cf0f8ffaddfc",self.gradient)
        self.assertIn("d06dbb032940ec8938b3841351f3ff7b7190dac1",self.flip)
        self.assertIn("BSD-3-Clause",self.license)
        self.assertIn("Gradient.cs",self.ledger)
        self.assertIn("UIFlippable.cs",self.ledger)

    def test_upstream_gradient_has_minimal_mesh_range_safety_guard(self):
        self.assertIn("class Gradient : BaseMeshEffect",self.gradient)
        self.assertIn("float.PositiveInfinity",self.gradient)
        self.assertIn("float.NegativeInfinity",self.gradient)
        self.assertIn("Mathf.Abs(uiElementHeight) < 0.00001f",self.gradient)
        self.assertIn("if (targetGraphic == null) targetGraphic = graphic",self.gradient)

    def test_real_gradient_and_flip_used_in_candidate_components(self):
        self.assertIn("AddComponent<\n                    Match3.VisualFactory.Editor.ThirdParty.Gradient>()",self.page)
        self.assertIn("name == \"HOME_HeroArtworkPlaceholder\"",self.page)
        self.assertIn("name == \"WORLD_EditableMapCanvas\"",self.page)
        self.assertIn("AddComponent<UIFlippable>()",self.motif)
        self.assertIn("mirror.horizontal = true",self.motif)
        self.assertIn("image.raycastTarget = false;",self.page)
        self.assertIn("image.raycastTarget = false;",self.motif)

    def test_editor_nunit_and_meta_guards_present(self):
        self.assertEqual(self.nunit.count("[Test]"),4)
        self.assertIn("UpstreamGradientCanShadeARealUiImage",self.nunit)
        self.assertIn("CopiedFlippableMirrorsActualUiVertices",self.nunit)
        for path in (
            "unity_package/Editor/ThirdParty/Gradient.cs.meta",
            "unity_package/Editor/ThirdParty/UIFlippable.cs.meta",
            "unity_package/Tests/Editor/VufDonorMeshEffectsEditModeTests.cs.meta"
        ):
            self.assertTrue((ROOT/path).is_file(),path)

    def test_no_duplicated_shader_or_external_paid_dependency(self):
        self.assertNotIn("UnityWebRequest",self.page)
        self.assertNotIn("AssetDatabase.CreateAsset",self.gradient)
        self.assertNotIn("DOTween",self.flip)


if __name__=="__main__":
    unittest.main()
