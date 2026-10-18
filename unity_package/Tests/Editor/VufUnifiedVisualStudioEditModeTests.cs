// M07: Editor catalog + Studio synthetic geometry tests (NOT real GUI owner QA).
// Uses actual Unity assemblies; no Sprite/FX imports, no package writes.
using System;
using System.Collections.Generic;
using NUnit.Framework;
using UnityEngine;
using Match3.VisualFactory.Editor;

namespace Match3.VisualFactory.Tests
{
    public sealed class VufUnifiedVisualStudioEditModeTests
    {
        [Test]
        public void FiveThemesFourteenEventsStayDistinctAndNeverBecomeGameRules()
        {
            Assert.That(VufVisualEventCatalog.Profiles.Length, Is.EqualTo(5));
            Assert.That(VufVisualEventCatalog.Events.Length, Is.EqualTo(14));
            Assert.That(VufVisualEventCatalog.MayMutateGameplay, Is.False);
            Assert.That(VufVisualEventCatalog.ArtRightsOwnerApproved, Is.False);
            Assert.That(VufVisualEventCatalog.ProductionEventParityProven, Is.False);
            var ids = new HashSet<string>(StringComparer.Ordinal);
            foreach (string profile in VufVisualEventCatalog.Profiles)
                foreach (var e in VufVisualEventCatalog.Events)
                {
                    string key = VufVisualEventCatalog.EventKey(profile, e.Name);
                    Assert.That(ids.Add(key), Is.True);
                    Assert.That(key, Does.StartWith(profile.ToLowerInvariant() + ".anim."));
                    Assert.That(e.Priority, Is.InRange(0, 100));
                    Assert.That(e.DurationMs, Is.GreaterThan(0));
                }
            Assert.That(ids.Count, Is.EqualTo(70));
        }

        [Test]
        public void SymbolicSpecialAndUnorderedEngineComboKeysMatchExpectedVufR50Format()
        {
            Assert.That(VufVisualEventCatalog.EngineSpecials.Length, Is.EqualTo(5));
            string one = VufVisualEventCatalog.ViewEventKey(
                "Coral_Rescue", "special_trigger", "HorizontalLine");
            Assert.That(one, Is.EqualTo(
                "coral_rescue.anim.special_trigger.horizontal_line"));
            string first = VufVisualEventCatalog.ViewEventKey(
                "Garage_Legends", "combo_chain", "Area", "Targeted");
            string second = VufVisualEventCatalog.ViewEventKey(
                "Garage_Legends", "combo_chain", "Targeted", "Area");
            Assert.That(first, Is.EqualTo(
                "garage_legends.anim.combo_chain.area__targeted"));
            Assert.That(first, Is.EqualTo(second));
            var combos = new HashSet<string>();
            foreach (string a in VufVisualEventCatalog.EngineSpecials)
                foreach (string b in VufVisualEventCatalog.EngineSpecials)
                    combos.Add(VufVisualEventCatalog.ViewEventKey(
                        "Coral_Rescue", "combo_chain", a, b));
            Assert.That(combos.Count, Is.EqualTo(15));
        }

        [Test]
        public void UnexpectedOrUnsafeEngineStyleVariantsAreRejectedBeforeRendering()
        {
            Assert.Throws<ArgumentException>(() =>
                VufVisualEventCatalog.ViewEventKey(
                    "../private", "tile_match", null));
            Assert.Throws<ArgumentException>(() =>
                VufVisualEventCatalog.ViewEventKey(
                    "Dino_Islands", "real_money_purchase", null));
            Assert.Throws<ArgumentException>(() =>
                VufVisualEventCatalog.ViewEventKey(
                    "Dino_Islands", "combo_chain", "Area", "Unpublished"));
            Assert.Throws<ArgumentException>(() =>
                VufVisualEventCatalog.ViewEventKey(
                    "Dino_Islands", "special_trigger", "Area", "Targeted"));
            Assert.Throws<ArgumentException>(() =>
                VufVisualEventCatalog.ViewEventKey(
                    "Dino_Islands", "level_win", "Area"));
        }

        [Test]
        public void CuesAreLoggedNotActuatedAndMutedModesNeverPretendToPlay()
        {
            Assert.That(VufVisualEventCatalog.AudioCueLog(
                "Coral_Rescue", "level_win", true), Is.EqualTo("MUTED_NO_AUDIO"));
            Assert.That(VufVisualEventCatalog.HapticCueLog(
                "Coral_Rescue", "level_win", true), Is.EqualTo("MUTED_NO_HAPTIC"));
            Assert.That(VufVisualEventCatalog.AudioCueLog(
                "Coral_Rescue", "level_win", false), Does.Contain("LOG ONLY"));
            Assert.That(VufVisualEventCatalog.HapticCueLog(
                "Coral_Rescue", "level_win", false), Does.Contain("NOT PLAYED"));
        }

        [Test]
        public void SyntheticPhoneTabletAspectFramesNeverClaimOSDeviceSafeArea()
        {
            var view = new Rect(0f, 0f, 400f, 400f);
            var portrait = VufUnifiedVisualStudioWindow.SyntheticViewport(view, 0);
            var tall = VufUnifiedVisualStudioWindow.SyntheticViewport(view, 1);
            var tablet = VufUnifiedVisualStudioWindow.SyntheticViewport(view, 2);
            Assert.That(portrait.width / portrait.height,
                Is.EqualTo(9f / 16f).Within(.001f));
            Assert.That(tall.width / tall.height,
                Is.EqualTo(6f / 13f).Within(.001f));
            Assert.That(tablet.width / tablet.height,
                Is.EqualTo(3f / 4f).Within(.001f));
            Assert.That(tall.width, Is.LessThan(portrait.width));
            Assert.That(tablet.width, Is.GreaterThan(portrait.width));
        }

        [Test]
        public void InvalidSyntheticPreviewBoundsAndProfilesCannotBeSilentlyAccepted()
        {
            Assert.Throws<ArgumentOutOfRangeException>(() =>
                VufUnifiedVisualStudioWindow.SyntheticViewport(
                    new Rect(0f, 0f, 400f, 400f), -1));
            Assert.Throws<ArgumentOutOfRangeException>(() =>
                VufUnifiedVisualStudioWindow.SyntheticViewport(
                    new Rect(0f, 0f, 400f, 400f), 3));
            Assert.Throws<ArgumentOutOfRangeException>(() =>
                VufUnifiedVisualStudioWindow.SyntheticViewport(
                    new Rect(0f, 0f, 0f, 400f), 0));
        }
    }
}
