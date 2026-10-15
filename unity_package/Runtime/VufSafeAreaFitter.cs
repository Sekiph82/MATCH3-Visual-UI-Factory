using UnityEngine;

namespace Match3.VisualFactory
{
    // VF-08: normalized Screen.safeArea mapping, no gameplay dependency.
    // Place on a fullscreen RectTransform with stretch anchors and zero offsets.
    [DisallowMultipleComponent]
    [RequireComponent(typeof(RectTransform))]
    public sealed class VufSafeAreaFitter : MonoBehaviour
    {
        [SerializeField] private bool applyInEditor = false;
        private RectTransform target;
        private Rect lastArea;
        private Vector2Int lastScreen;

        private void Awake()
        {
            target = GetComponent<RectTransform>();
            Refresh();
        }

        private void OnEnable()
        {
            target = GetComponent<RectTransform>();
            Refresh();
        }

        private void Update()
        {
            if (!Application.isPlaying && !applyInEditor) return;
            Rect area = Screen.safeArea;
            var screen = new Vector2Int(Screen.width, Screen.height);
            if (lastArea != area || lastScreen != screen)
                Refresh();
        }

        public void Refresh()
        {
            if (target == null) target = GetComponent<RectTransform>();
            int width = Screen.width;
            int height = Screen.height;
            if (width <= 0 || height <= 0) return;
            Rect area = Screen.safeArea;
            if (area.width <= 0 || area.height <= 0) return;
            lastArea = area;
            lastScreen = new Vector2Int(width, height);
            target.anchorMin = new Vector2(area.xMin / width, area.yMin / height);
            target.anchorMax = new Vector2(area.xMax / width, area.yMax / height);
            target.offsetMin = Vector2.zero;
            target.offsetMax = Vector2.zero;
        }
    }
}
