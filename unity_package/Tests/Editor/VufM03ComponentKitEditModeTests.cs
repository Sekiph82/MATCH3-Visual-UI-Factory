using System;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;
using UnityEngine.UI;
using Match3.VisualFactory.Editor;

namespace Match3.VisualFactory.Tests
{
    public sealed class VufM03ComponentKitEditModeTests
    {
        private static VufM02StyleBibleStudioWindow.Catalog Catalog()
        {
            var asset = AssetDatabase.LoadAssetAtPath<TextAsset>(
                "Packages/com.match3.visual-factory/Editor/Resources/" +
                "m02_identity_catalog.v1.json");
            Assert.That(asset, Is.Not.Null);
            return VufM02StyleBibleStudioWindow.ValidateAndParse(asset.text);
        }

        [Test]
        public void FiveThemesAndFourDeviceGuidesProduceTenRealUnboundComponents()
        {
            var data = Catalog();
            int candidates = 0;
            foreach(var theme in VufM03ComponentKitWindow.Profiles)
            for(int device=0;device<4;device++)
            {
                var result = VufM03ComponentKitWindow.BuildCandidate(
                    data, theme, device, "Ready");
                try
                {
                    Assert.That(result.GetComponent<Canvas>(),Is.Not.Null);
                    Assert.That(result.GetComponent<CanvasScaler>(),Is.Not.Null);
                    var safe = result.transform.Find("M03_SourceSafeArea");
                    Assert.That(safe,Is.Not.Null);
                    var buttonCount = 0;
                    foreach(var semantic in VufM03ComponentKitWindow.Semantics)
                    {
                        var child = safe.Find("M03_"+semantic+"_UNBOUND");
                        Assert.That(child,Is.Not.Null,theme+"/"+semantic);
                        var box = child.GetComponent<RectTransform>();
                        var width = (box.anchorMax.x-box.anchorMin.x)*
                            data.common.screen_modes[device].width_dp;
                        var safeHeight = data.common.screen_modes[device].height_dp -
                            data.common.screen_modes[device].min_safe_top_dp -
                            data.common.screen_modes[device].min_safe_bottom_dp;
                        var height=(box.anchorMax.y-box.anchorMin.y)*safeHeight;
                        Assert.That(width,Is.GreaterThanOrEqualTo(44f),
                            theme+"/"+semantic);
                        Assert.That(height,Is.GreaterThanOrEqualTo(44f),
                            theme+"/"+semantic);
                        var native=child.GetComponent<Button>();
                        if(native!=null)
                        {
                            buttonCount++;
                            Assert.That(native.interactable,Is.False);
                            Assert.That(native.onClick.GetPersistentEventCount(),Is.Zero);
                            Assert.That(native.navigation.mode,
                                Is.EqualTo(Navigation.Mode.None));
                        }
                        Assert.That(child.Find("M03_Label_"+semantic),Is.Not.Null);
                    }
                    Assert.That(buttonCount,Is.EqualTo(3));
                    Assert.That(safe.Find("M03_AlwaysVisibleRightsAndBindingGate"),
                                Is.Not.Null);
                    candidates++;
                }
                finally { UnityEngine.Object.DestroyImmediate(result); }
            }
            Assert.That(candidates,Is.EqualTo(20));
        }

        [Test]
        public void EightStatesCannotCauseActiveButtonsOrRealProgress()
        {
            var data=Catalog();
            foreach(var state in VufReviewStateCatalog.States)
            {
                var kit=VufM03ComponentKitWindow.BuildCandidate(
                    data,"Wonder_Pop",0,state);
                try
                {
                    var pending=kit.transform.Find(
                        "M03_SourceSafeArea/M03_pending_state_UNBOUND/" +
                        "M03_Label_pending_state").GetComponent<Text>();
                    Assert.That(pending.text,Does.Contain("MOCK "+state.ToUpperInvariant()));
                    foreach(var button in kit.GetComponentsInChildren<Button>(true))
                        Assert.That(button.interactable,Is.False);
                    Assert.That(kit.transform.Find(
                        "M03_SourceSafeArea/M03_progress_UNBOUND/" +
                        "M03_ProgressTrack/M03_ProgressFill_MOCK"),Is.Not.Null);
                }
                finally { UnityEngine.Object.DestroyImmediate(kit); }
            }
        }

        [Test]
        public void NoUnknownProfileStateOrForgedOwnerApproval()
        {
            var data=Catalog();
            Assert.Throws<ArgumentException>(() =>
                VufM03ComponentKitWindow.BuildCandidate(
                    data,"Unlicensed_Title",0,"Ready"));
            Assert.Throws<ArgumentException>(() =>
                VufM03ComponentKitWindow.BuildCandidate(
                    data,"Coral_Rescue",99,"Ready"));
            Assert.Throws<ArgumentException>(() =>
                VufM03ComponentKitWindow.BuildCandidate(
                    data,"Coral_Rescue",0,"Unexpected"));
            data.common.owner_auth.production_release_allowed=true;
            Assert.Throws<ArgumentException>(() =>
                VufM03ComponentKitWindow.BuildCandidate(
                    data,"Coral_Rescue",0,"Ready"));
        }

        [Test]
        public void DuplicatedOrChangedSemanticRoleIsRejectedBeforeAuthoring()
        {
            var data=Catalog();
            data.profiles[1].ui_components[1]=
                data.profiles[1].ui_components[0];
            Assert.Throws<ArgumentException>(() =>
                VufM03ComponentKitWindow.ValidateSemantics(data.profiles[1]));
            Assert.Throws<ArgumentException>(() =>
                VufM03ComponentKitWindow.BuildCandidate(
                    data,"Coral_Rescue",0,"Ready"));
        }
    }
}
