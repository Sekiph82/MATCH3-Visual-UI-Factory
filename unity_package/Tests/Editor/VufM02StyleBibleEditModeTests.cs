using System;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;
using Match3.VisualFactory.Editor;

namespace Match3.VisualFactory.Tests
{
    public sealed class VufM02StyleBibleEditModeTests
    {
        private const string Path =
            "Packages/com.match3.visual-factory/Editor/Resources/m02_identity_catalog.v1.json";

        private static string Original()
        {
            var source=AssetDatabase.LoadAssetAtPath<TextAsset>(Path);
            if (source==null) throw new InvalidOperationException(
                "Unity package M02 Style Bible is missing");
            return source.text;
        }

        [Test]
        public void ActualFiveThemeOriginalCreativeBriefsRemainUnapproved()
        {
            var a=VufM02StyleBibleStudioWindow.ValidateAndParse(Original());
            Assert.That(a.common.stage,
                Is.EqualTo("DRAFT_IDENTITY_CONTRACT_OWNER_ART_NOT_PROVIDED"));
            Assert.That(a.profiles.Length,Is.EqualTo(5));
            Assert.That(a.profiles[0].id,Is.EqualTo("Coral_Rescue"));
            Assert.That(a.profiles[4].id,Is.EqualTo("Wonder_Pop"));
            foreach(var p in a.profiles)
            {
                Assert.That(p.right_to_use,
                    Is.EqualTo("NO_OWNER_ORIGINAL_ASSET_OR_FONT_LICENCE_EVIDENCE"));
                Assert.That(p.symbol_silhouettes.Length,Is.EqualTo(5));
                Assert.That(p.required_character_poses.Length,Is.EqualTo(5));
                Assert.That(p.master_sheet_slots.Length,Is.GreaterThanOrEqualTo(5));
            }
            Assert.That(a.common.owner_auth.all_approved, Is.False);
            Assert.That(a.common.owner_auth.original_art_received,Is.False);
            Assert.That(a.common.owner_auth.font_rights_verified,Is.False);
        }

        [Test]
        public void ExactFiveInheritedPaletteTextPairsActuallyPassContrast()
        {
            foreach (var theme in new [] {
                "Coral_Rescue","Garage_Legends","Dino_Islands",
                "The_Fractured_Realms","Wonder_Pop"})
                Assert.DoesNotThrow(() =>
                    VufM02StyleBibleStudioWindow.ValidateOriginalPalette(theme),
                    theme);
        }

        [Test]
        public void PrototypeIdentityCannotForgeOriginalOwnerOrRightsFlags()
        {
            string source=Original();
            Assert.Throws<ArgumentException>(() =>
                VufM02StyleBibleStudioWindow.ValidateAndParse(
                    source.Replace("\"all_approved\": false",
                        "\"all_approved\": true")));
            Assert.Throws<ArgumentException>(() =>
                VufM02StyleBibleStudioWindow.ValidateAndParse(
                    source.Replace("NO_OWNER_ORIGINAL_ASSET_OR_FONT_LICENCE_EVIDENCE",
                        "OWNER_APPROVED")));
        }

        [Test]
        public void MissingOrCrossTitleProfilesFailBeforePreview()
        {
            string source=Original();
            Assert.Throws<ArgumentException>(() =>
                VufM02StyleBibleStudioWindow.ValidateAndParse(
                    source.Replace("\"Coral_Rescue\"",
                        "\"Unapproved_Game\"")));
            Assert.Throws<ArgumentException>(() =>
                VufM02StyleBibleStudioWindow.ValidateAndParse(
                    source.Replace("\"Dino_Islands\"",
                        "\"Coral_Rescue\"")));
        }

        [Test]
        public void SafeAreaAndTypographyMustRetainHumanReadableMinimum()
        {
            string source=Original();
            Assert.Throws<ArgumentException>(() =>
                VufM02StyleBibleStudioWindow.ValidateAndParse(
                    source.Replace("\"min_touch_dp\": 44",
                        "\"min_touch_dp\": 18")));
            Assert.Throws<ArgumentException>(() =>
                VufM02StyleBibleStudioWindow.ValidateAndParse(
                    source.Replace("\"body\": 17",
                        "\"body\": 11")));
        }

        [Test]
        public void SourceStyleBibleUiIsEditorOnlyAndNoGameplayBindingOccurs()
        {
            var source=Original();
            var result=VufM02StyleBibleStudioWindow.ValidateAndParse(source);
            Assert.That(result.profiles[4].forbidden_visual_patterns.Length,
                Is.EqualTo(2));
            Assert.That(result.common.grid.columns_phone,Is.EqualTo(4));
            Assert.That(result.common.grid.columns_tablet,Is.EqualTo(8));
            Assert.That(result.common.screen_modes.Length,Is.EqualTo(4));
        }

        [Test]
        public void SourceGridGuidesFitFourPortraitDesignTokens()
        {
            var data=VufM02StyleBibleStudioWindow.ValidateAndParse(Original());
            foreach(var mode in data.common.screen_modes)
            {
                var guide=VufM02StyleBibleStudioWindow.BuildSourceGridGuide(
                    data.common,mode);
                int expected=mode.id=="portrait_tablet" ? 8 : 4;
                Assert.That(guide.Columns.Length,Is.EqualTo(expected),mode.id);
                Assert.That(guide.MinimumTap.width,
                    Is.GreaterThanOrEqualTo(44f),mode.id);
                Assert.That(guide.MinimumTap.height,
                    Is.GreaterThanOrEqualTo(44f),mode.id);
                Assert.That(guide.Safe.Contains(guide.MinimumTap.min),
                    Is.True,mode.id);
                Assert.That(guide.Safe.Contains(guide.MinimumTap.max),
                    Is.True,mode.id);
                for(int i=0;i<guide.Columns.Length;i++)
                {
                    var cell=guide.Columns[i];
                    Assert.That(cell.width,
                        Is.GreaterThanOrEqualTo(44f),mode.id);
                    Assert.That(cell.xMin,Is.GreaterThanOrEqualTo(
                        guide.Safe.xMin),mode.id);
                    Assert.That(cell.xMax,Is.LessThanOrEqualTo(
                        guide.Safe.xMax+0.001f),mode.id);
                    if (i>0)
                        Assert.That(cell.xMin,Is.GreaterThan(
                            guide.Columns[i-1].xMax),mode.id);
                }
            }
        }

        [Test]
        public void AccessibleSymbolInkMeetsNonTextContrastInAllFiveThemes()
        {
            foreach(var theme in new [] {
                "Coral_Rescue","Garage_Legends","Dino_Islands",
                "The_Fractured_Realms","Wonder_Pop"})
            {
                var palette=VufScreenCatalog.LoadStyle(theme).palettes;
                var surface=VufScreenCatalog.ParseColor(palette.surface,"surface");
                var ink=VufM02StyleBibleStudioWindow.GetAccessibleSymbolInk(theme);
                Assert.That(
                    VufM02StyleBibleStudioWindow.Contrast(ink,surface),
                    Is.GreaterThanOrEqualTo(3f),theme);
                var expected=VufScreenCatalog.ParseColor(
                    theme=="Wonder_Pop" ? palette.text : palette.accent,
                    "accessible_symbol_ink");
                Assert.That(ink,Is.EqualTo(expected),theme);
            }
        }

        [Test]
        public void SourceGridGuideRejectsImpossibleTouchGeometry()
        {
            var data=VufM02StyleBibleStudioWindow.ValidateAndParse(Original());
            var invalid=new VufM02StyleBibleStudioWindow.Device {
                id="compact_phone",width_dp=320,height_dp=568,
                min_safe_top_dp=270,min_safe_bottom_dp=270
            };
            Assert.Throws<ArgumentException>(() =>
                VufM02StyleBibleStudioWindow.BuildSourceGridGuide(
                    data.common,invalid));
            var narrower=new VufM02StyleBibleStudioWindow.Device {
                id="compact_phone",width_dp=320,height_dp=568,
                min_safe_top_dp=0,min_safe_bottom_dp=0
            };
            data.common.min_touch_dp=72;
            Assert.Throws<ArgumentException>(() =>
                VufM02StyleBibleStudioWindow.BuildSourceGridGuide(
                    data.common,narrower));
        }

    }
}
