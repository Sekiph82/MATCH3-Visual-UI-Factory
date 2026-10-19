// Source-constrained, nonpersistent screenshot of the actual LFXV1
// uGUI board preview. Based on existing M09 RenderTexture approach but
// WITHOUT weakening the M09 Coral-screen CandidateMarker gate.
// Not player GPU evidence, not screenshot of a real Engine game.
using System;
using UnityEngine;

namespace Match3.VisualFactory.Editor
{
    internal static class VufThreeFactoryGridCapture
    {
        internal static byte[] CaptureSourcePreview(GameObject board,
            int width, int height)
        {
            if (board==null ||
                board.name!="VUF_THREE_FACTORY_REAL_DRAFT_TEMP" ||
                width<160 || width>1024 || height<160 || height>2048 ||
                (long)width*height>2_097_152 ||
                (board.hideFlags & HideFlags.DontSaveInEditor)==0 ||
                (board.hideFlags & HideFlags.DontSaveInBuild)==0 ||
                board.transform.Find("Real_LFXV1_Source_Grid")==null)
                throw new ArgumentException(
                    "Only disposable exact LFXV1 source board may be captured");
            foreach (Transform t in board.GetComponentsInChildren<Transform>(true))
                if ((t.gameObject.hideFlags & HideFlags.DontSaveInEditor)==0 ||
                    (t.gameObject.hideFlags & HideFlags.DontSaveInBuild)==0)
                    throw new ArgumentException("non-disposable child in source canvas");
            var canvas=board.GetComponent<Canvas>();
            if (canvas==null)
                throw new ArgumentException("only actual temporary Unity uGUI Canvas");
            GameObject cameraObject=null;
            RenderTexture target=null;
            Texture2D png=null;
            RenderTexture oldActive=RenderTexture.active;
            RenderMode oldMode=canvas.renderMode;
            Camera oldCamera=canvas.worldCamera;
            float oldDistance=canvas.planeDistance;
            try
            {
                cameraObject=new GameObject("VUF_THREE_FACTORY_TEMP_CAMERA",
                    typeof(Camera));
                cameraObject.hideFlags=
                    HideFlags.DontSaveInEditor | HideFlags.DontSaveInBuild;
                cameraObject.transform.position=new Vector3(0,0,-10);
                var camera=cameraObject.GetComponent<Camera>();
                camera.orthographic=true;
                camera.clearFlags=CameraClearFlags.SolidColor;
                camera.backgroundColor=new Color(.08f,.1f,.13f,1f);
                camera.nearClipPlane=.1f;
                camera.farClipPlane=200f;
                target=new RenderTexture(width,height,24,
                    RenderTextureFormat.ARGB32);
                target.Create();
                camera.targetTexture=target;
                canvas.renderMode=RenderMode.ScreenSpaceCamera;
                canvas.worldCamera=camera;
                canvas.planeDistance=20f;
                Canvas.ForceUpdateCanvases();
                camera.Render();
                RenderTexture.active=target;
                png=new Texture2D(width,height,TextureFormat.RGBA32,false,false);
                png.ReadPixels(new Rect(0,0,width,height),0,0,false);
                png.Apply(false,false);
                return png.EncodeToPNG();
            }
            finally
            {
                canvas.renderMode=oldMode;
                canvas.worldCamera=oldCamera;
                canvas.planeDistance=oldDistance;
                RenderTexture.active=oldActive;
                if (png!=null) UnityEngine.Object.DestroyImmediate(png);
                if (target!=null)
                {
                    target.Release();
                    UnityEngine.Object.DestroyImmediate(target);
                }
                if (cameraObject!=null)
                    UnityEngine.Object.DestroyImmediate(cameraObject);
            }
        }
    }
}
