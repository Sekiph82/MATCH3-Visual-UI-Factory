// VF-05 | Small runtime UI transition primitive, no paid tween dependency.
// This component never changes Engine game state, score, purchases or rewards.
using UnityEngine;

namespace Match3.VisualFactory
{
    [DisallowMultipleComponent]
    [RequireComponent(typeof(CanvasGroup))]
    public sealed class VufUiTween : MonoBehaviour
    {
        [SerializeField, Range(0.01f, 2f)]
        private float duration = 0.20f;
        [SerializeField]
        private bool useUnscaledTime = true;
        [SerializeField]
        private bool reducedMotion;

        private CanvasGroup canvasGroup;
        private float elapsed;
        private float fromAlpha;
        private float toAlpha;
        private bool animating;

        public bool IsAnimating => animating;
        public bool ReducedMotion => reducedMotion;
        public float Duration => duration;

        private CanvasGroup Group
        {
            get
            {
                if (canvasGroup == null)
                    canvasGroup = GetComponent<CanvasGroup>();
                return canvasGroup;
            }
        }

        private void Update()
        {
            if (!animating) return;
            float delta = useUnscaledTime ? Time.unscaledDeltaTime : Time.deltaTime;
            Advance(Mathf.Max(0f, delta));
        }

        // Deterministic, inspector/test-accessible driver. No event callbacks.
        public void Advance(float seconds)
        {
            if (!animating || seconds < 0f || float.IsNaN(seconds) ||
                float.IsInfinity(seconds))
                return;
            elapsed = Mathf.Min(duration, elapsed + seconds);
            float time = Mathf.Clamp01(elapsed / duration);
            float smoothed = time * time * (3f - 2f * time);
            Group.alpha = Mathf.Lerp(fromAlpha, toAlpha, smoothed);
            if (elapsed >= duration)
            {
                animating = false;
                ApplyInteractable(toAlpha >= 0.999f);
            }
        }

        public void SetReducedMotion(bool enabled)
        {
            reducedMotion = enabled;
            if (reducedMotion && animating)
            {
                animating = false;
                Group.alpha = toAlpha;
                ApplyInteractable(toAlpha >= 0.999f);
            }
        }

        public void Show()
        {
            StartTransition(1f);
        }

        public void Hide()
        {
            StartTransition(0f);
        }

        private void StartTransition(float target)
        {
            toAlpha = target;
            if (reducedMotion || duration <= 0f || !isActiveAndEnabled)
            {
                Group.alpha = target;
                animating = false;
                ApplyInteractable(target >= 0.999f);
                return;
            }
            fromAlpha = Mathf.Clamp01(Group.alpha);
            elapsed = 0f;
            animating = true;
            // Prevent touch-through or premature interaction during animation.
            ApplyInteractable(false);
            if (Mathf.Approximately(fromAlpha, target))
            {
                animating = false;
                ApplyInteractable(target >= 0.999f);
            }
        }

        private void ApplyInteractable(bool state)
        {
            Group.interactable = state;
            Group.blocksRaycasts = state;
        }
    }
}
