using UnityEngine;

namespace Match3.VisualFactory
{
    // View-only audit metadata for new, unapproved UI templates.
    // No Engine APIs, score, purchases, saves, gameplay or network calls.
    [DisallowMultipleComponent]
    public sealed class VufCandidateScreenMarker : MonoBehaviour
    {
        [SerializeField] private string profileId;
        [SerializeField] private string screenId;
        [SerializeField] private string screenKey;
        [SerializeField] private string screenKind;
        [SerializeField] private string featureGate;
        [SerializeField] private string candidateStatus = "CANDIDATE_NOT_APPROVED";

        public string ProfileId => profileId;
        public string ScreenId => screenId;
        public string ScreenKey => screenKey;
        public string ScreenKind => screenKind;
        public string FeatureGate => featureGate;
        public string CandidateStatus => candidateStatus;

#if UNITY_EDITOR
        // Editor only and never auto-approved or promoted to a consumer game.
        public void SetCandidate(string profile, string id, string key,
            string kind, string gate)
        {
            profileId = profile;
            screenId = id;
            screenKey = key;
            screenKind = kind;
            featureGate = gate;
            candidateStatus = "CANDIDATE_NOT_APPROVED";
        }
#endif
    }
}
