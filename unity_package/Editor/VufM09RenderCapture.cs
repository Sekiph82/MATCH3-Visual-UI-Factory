// VUF-M09-003/006/012 | Real Unity uGUI camera render into in-memory
// RenderTexture, explicitly only for nonpersistent candidate objects.
// This is NOT a screenshot of an iPhone/Android, live Engine or owner-approved
// shipped layout. Does NOT overwrite files or touch existing scene objects.
using System;
using UnityEngine;

namespace Match3.VisualFactory.Editor
{
    internal static class VufM09RenderCapture
    {
        internal static byte[] CaptureCandidate(GameObject candidate,
            int width, int height, bool reducedMotion)
        {
            if (candidate == null || width < 160 || height < 160 ||
                width > 1440 || height > 2560 ||
                (long)width * height > 2359296)
                throw new ArgumentException("bounded screenshot candidate/viewport");
            var marker = candidate.GetComponent<VufCandidateScreenMarker>();
            var canvas = candidate.GetComponent<Canvas>();
            if (marker == null || canvas == null ||
                marker.CandidateStatus != "CANDIDATE_NOT_APPROVED" ||
                (candidate.hideFlags & HideFlags.DontSaveInEditor) == 0 ||
                (candidate.hideFlags & HideFlags.DontSaveInBuild) == 0)
                throw new ArgumentException("screenshots are disposable candidates only");

            GameObject cameraGo = null;
            RenderTexture texture = null;
            Texture2D result = null;
            RenderTexture oldActive = RenderTexture.active;
            RenderMode oldMode = canvas.renderMode;
            Camera oldCamera = canvas.worldCamera;
            float oldPlane = canvas.planeDistance;
            try
            {
                cameraGo = new GameObject("VUF_TEMP_M09_CAMERA_DONT_SAVE",
                    typeof(Camera));
                cameraGo.hideFlags =
                    HideFlags.DontSaveInEditor | HideFlags.DontSaveInBuild;
                cameraGo.transform.position = new Vector3(0, 0, -10);
                Camera cam = cameraGo.GetComponent<Camera>();
                cam.orthographic = true;
                cam.clearFlags = CameraClearFlags.SolidColor;
                cam.backgroundColor = new Color(.06f, .07f, .09f, 1f);
                cam.nearClipPlane = .1f;
                cam.farClipPlane = 200f;
                cam.cullingMask = ~0;
                texture = new RenderTexture(width, height, 24,
                    RenderTextureFormat.ARGB32);
                texture.Create();
                cam.targetTexture = texture;
                canvas.renderMode = RenderMode.ScreenSpaceCamera;
                canvas.worldCamera = cam;
                canvas.planeDistance = 20f;
                // Only the constructed disposable candidate is changed.
                // The existing VufUiTween component's motion never starts.
                foreach (var group in
                    candidate.GetComponentsInChildren<CanvasGroup>(true))
                    if (reducedMotion && group.alpha < 0.001f)
                        group.alpha = 1f; // candidate-only static image
                Canvas.ForceUpdateCanvases();
                cam.Render();
                RenderTexture.active = texture;
                result = new Texture2D(width, height, TextureFormat.RGBA32,
                    false, false);
                result.ReadPixels(new Rect(0, 0, width, height), 0, 0, false);
                result.Apply(false, false);
                return result.EncodeToPNG();
            }
            finally
            {
                canvas.renderMode = oldMode;
                canvas.worldCamera = oldCamera;
                canvas.planeDistance = oldPlane;
                RenderTexture.active = oldActive;
                if (result != null) UnityEngine.Object.DestroyImmediate(result);
                if (texture != null)
                {
                    texture.Release();
                    UnityEngine.Object.DestroyImmediate(texture);
                }
                if (cameraGo != null)
                    UnityEngine.Object.DestroyImmediate(cameraGo);
            }
        }
    }
}
