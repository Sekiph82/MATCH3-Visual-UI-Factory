// VF-05 manual Unity Play Mode inspection, no gameplay events or screenshots.
using UnityEditor;
using UnityEngine;

namespace Match3.VisualFactory.Editor
{
    [CustomEditor(typeof(VufUiTween))]
    public sealed class VufUiTweenInspector : UnityEditor.Editor
    {
        public override void OnInspectorGUI()
        {
            DrawDefaultInspector();
            EditorGUILayout.HelpBox(
                "This is a presentation-only CanvasGroup fade. Enter Unity Play Mode " +
                "to manually test Show, Hide, interruption, reduced-motion and frame " +
                "transitions. It never grants items or touches the Engine.",
                MessageType.Info);
            VufUiTween tween = (VufUiTween)target;
            if (!Application.isPlaying)
            {
                EditorGUILayout.LabelField("Preview", "Enter Play Mode first");
                return;
            }
            using (new EditorGUILayout.HorizontalScope())
            {
                if (GUILayout.Button("Show (Play Mode)"))
                    tween.Show();
                if (GUILayout.Button("Hide (Play Mode)"))
                    tween.Hide();
                if (GUILayout.Button("Reduced-motion ON"))
                    tween.SetReducedMotion(true);
                if (GUILayout.Button("Reduced-motion OFF"))
                    tween.SetReducedMotion(false);
            }
            EditorGUILayout.LabelField("IsAnimating", tween.IsAnimating.ToString());
            EditorGUILayout.LabelField("ReducedMotion", tween.ReducedMotion.ToString());
        }
    }
}
