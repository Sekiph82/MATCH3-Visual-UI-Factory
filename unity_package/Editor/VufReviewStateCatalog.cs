// VF-07 draft review-copy and state variants. NOT a game localization service.
// No Engine state, subscriptions, rewards, asset writes or approval authority.
using System;
using UnityEngine;
using UnityEngine.UI;

namespace Match3.VisualFactory.Editor
{
    internal static class VufReviewStateCatalog
    {
        internal static readonly string[] States = {
            "Ready", "Loading", "Offline", "Error",
            "Owned", "Claimed", "Disabled", "Pending"
        };

        internal static readonly string[] Locales = { "en", "tr", "stress" };

        private static bool Contains(string[] choices, string value)
        {
            foreach (string choice in choices)
                if (String.Equals(choice, value, StringComparison.Ordinal))
                    return true;
            return false;
        }

        internal static void Apply(GameObject candidate,
            VufScreenCatalog.ScreenInfo contract,
            string state, string locale)
        {
            if (candidate == null || contract == null)
                throw new ArgumentNullException("candidate/contract");
            if (!Contains(States, state) || !Contains(Locales, locale))
                throw new ArgumentException("unknown review state or locale");
            var marker = candidate.GetComponent<VufCandidateScreenMarker>();
            if (marker == null || marker.CandidateStatus != "CANDIDATE_NOT_APPROVED" ||
                marker.ScreenId != contract.id || marker.ScreenKey != contract.key ||
                marker.FeatureGate != contract.feature_gate)
                throw new InvalidOperationException("review requires exact unapproved screen contract");

            // Fail before any text mutation. Preview cannot re-enable disabled
            // test buttons or operate on already interactive production UI.
            foreach (Button button in candidate.GetComponentsInChildren<Button>(true))
                if (button.interactable || button.onClick.GetPersistentEventCount() != 0)
                    throw new InvalidOperationException("candidate button unexpectedly bound");

            Text heading = null;
            Text primary = null;
            Text stateLabel = null;
            foreach (Text element in candidate.GetComponentsInChildren<Text>(true))
            {
                if (element.name == "Heading") heading = element;
                if (element.name == "ActionLabel") primary = element;
                if (element.name == "ReviewState_AlwaysVisible") stateLabel = element;
            }
            if (heading == null || primary == null || stateLabel == null)
                throw new InvalidOperationException("missing mandatory draft review text slots");

            string title = VufScreenCatalog.DisplayName(contract);
            if (locale == "tr")
            {
                title = contract.key == "home" ? "Ana Sayfa" :
                    contract.key == "gameplay_hud" ? "Oyun Arayuzu" :
                    "TR TASLAK: " + title;
                primary.text = "BAGLI DEGIL";
            }
            else if (locale == "stress")
            {
                title = "[EXPANDED TEXT QA] " + title +
                    " / VERY LONG DRAFT LABEL / TRANSLATION PENDING";
                primary.text = "[LONG TEXT QA / NO ACTION]";
            }
            else
                primary.text = "NOT CONNECTED";

            // These texts are synthetic. 'Owned', 'Claimed', 'Error', etc. do
            // not reveal actual Engine values and never trigger UI actions.
            heading.text = title;
            stateLabel.text = "MOCK " + state.ToUpperInvariant() + " / " +
                locale.ToUpperInvariant() + " / NOT GAME STATE";
        }
    }
}
