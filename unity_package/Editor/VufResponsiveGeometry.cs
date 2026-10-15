// VF-08: deterministic Editor-only anchor/offset and synthetic safe-area audit.
// This intentionally does NOT render the actual prefab, compute dynamic
// Unity layout groups, simulate fonts or replace real iOS/Android device QA.
using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace Match3.VisualFactory.Editor
{
    internal static class VufResponsiveGeometry
    {
        internal readonly struct Device
        {
            internal readonly string Name;
            internal readonly int Width;
            internal readonly int Height;
            internal readonly int Left;
            internal readonly int Right;
            internal readonly int Bottom;
            internal readonly int Top;

            internal Device(string name, int width, int height,
                            int left, int right, int bottom, int top)
            {
                Name = name;
                Width = width;
                Height = height;
                Left = left;
                Right = right;
                Bottom = bottom;
                Top = top;
            }

            internal Rect SafeRect
            {
                get
                {
                    return new Rect(Left, Bottom,
                        Width - Left - Right, Height - Top - Bottom);
                }
            }
        }

        internal sealed class Node
        {
            internal string Path;
            internal Rect Bounds;
            internal bool IsButton;
            internal bool IsText;
            internal bool IsSafeArea;
        }

        internal sealed class Audit
        {
            internal readonly List<Node> Nodes = new List<Node>();
            internal readonly List<string> Warnings = new List<string>();
            internal Device Device;
            internal bool CandidateOnly;
            internal int ButtonCount;
        }

        internal static readonly Device[] Presets = {
            new Device("Tall phone (approx 19.5:9)", 1179, 2556, 0, 0, 102, 162),
            new Device("Android (approx 20:9)", 1080, 2400, 0, 0, 70, 90),
            new Device("Compact phone (16:9)", 1080, 1920, 0, 0, 0, 0),
            new Device("Tablet portrait (4:3)", 2048, 2732, 0, 0, 0, 0),
            new Device("Landscape phone (20:9)", 2400, 1080, 90, 70, 0, 0)
        };

        private static bool Finite(float value)
        {
            return !float.IsNaN(value) && !float.IsInfinity(value);
        }

        internal static Audit Analyze(GameObject candidate, Device device)
        {
            if (candidate == null)
                throw new ArgumentNullException(nameof(candidate));
            if (device.Width < 100 || device.Height < 100 ||
                device.Left < 0 || device.Right < 0 ||
                device.Top < 0 || device.Bottom < 0 ||
                device.Left + device.Right >= device.Width ||
                device.Top + device.Bottom >= device.Height)
                throw new ArgumentException("Invalid simulated device bounds");
            var root = candidate.GetComponent<RectTransform>();
            if (root == null)
                throw new ArgumentException("Expected candidate root RectTransform");

            var result = new Audit { Device = device };
            var marker = candidate.GetComponent<VufCandidateScreenMarker>();
            result.CandidateOnly = marker != null &&
                marker.CandidateStatus == "CANDIDATE_NOT_APPROVED";
            if (!result.CandidateOnly)
                result.Warnings.Add("BLOCKED: missing/unapproved candidate-only marker");
            if (marker != null &&
                marker.FeatureGate == "OFF_UNTIL_ENGINE_POLICY_CONFIRMED")
                result.Warnings.Add("POLICY-OFF: do not enable this game screen");

            // CanvasScaler is MatchWidthOrHeight=.5 on authored candidates.
            var scaler = candidate.GetComponent<CanvasScaler>();
            float referenceWidth = scaler != null &&
                scaler.referenceResolution.x > 0f ? scaler.referenceResolution.x : 720f;
            float referenceHeight = scaler != null &&
                scaler.referenceResolution.y > 0f ? scaler.referenceResolution.y : 1280f;
            float horizontal = device.Width / referenceWidth;
            float vertical = device.Height / referenceHeight;
            float factor = Mathf.Lerp(horizontal, vertical, scaler != null
                ? Mathf.Clamp01(scaler.matchWidthOrHeight) : .5f);
            Rect full = new Rect(0, 0, device.Width, device.Height);
            result.Nodes.Add(new Node {
                Path = candidate.name, Bounds = full
            });
            for (int i = 0; i < root.childCount; i++)
            {
                var child = root.GetChild(i) as RectTransform;
                if (child == null)
                    result.Warnings.Add("UNSUPPORTED: non-RectTransform root child");
                else
                    AnalyzeChild(child, full, device.SafeRect,
                        factor, root.name, result, 1, false);
            }
            return result;
        }

        private static void AnalyzeChild(RectTransform rect, Rect parent,
            Rect safe, float factor, string parentPath, Audit audit, int depth,
            bool underSafeArea)
        {
            if (depth > 48)
            {
                audit.Warnings.Add("BLOCKED: UI depth >48 at " + parentPath);
                return;
            }
            string path = parentPath + "/" + rect.name;
            bool isSafe = rect.GetComponent<VufSafeAreaFitter>() != null;
            Rect bounds;
            if (isSafe)
            {
                // Matches the normalized anchors that SafeAreaFitter would set
                // at runtime; here this is solely a geometric model.
                bounds = safe;
            }
            else
            {
                float minX = parent.xMin + parent.width * rect.anchorMin.x +
                    rect.offsetMin.x * factor;
                float minY = parent.yMin + parent.height * rect.anchorMin.y +
                    rect.offsetMin.y * factor;
                float maxX = parent.xMin + parent.width * rect.anchorMax.x +
                    rect.offsetMax.x * factor;
                float maxY = parent.yMin + parent.height * rect.anchorMax.y +
                    rect.offsetMax.y * factor;
                if (!Finite(minX) || !Finite(maxX) ||
                    !Finite(minY) || !Finite(maxY) ||
                    maxX < minX || maxY < minY)
                {
                    audit.Warnings.Add("BLOCKED: invalid/non-finite anchors " + path);
                    return;
                }
                bounds = Rect.MinMaxRect(minX, minY, maxX, maxY);
            }
            var button = rect.GetComponent<Button>();
            bool text = rect.GetComponent<Text>() != null;
            audit.Nodes.Add(new Node {
                Path = path, Bounds = bounds,
                IsButton = button != null, IsText = text, IsSafeArea = isSafe
            });
            bool inSafe = underSafeArea || isSafe;
            if (inSafe && !isSafe && (
                bounds.xMin < safe.xMin - .01f ||
                bounds.xMax > safe.xMax + .01f ||
                bounds.yMin < safe.yMin - .01f ||
                bounds.yMax > safe.yMax + .01f))
            {
                audit.Warnings.Add("SAFE-AREA: outside simulated insets " + path);
            }
            if (button != null)
            {
                audit.ButtonCount++;
                float touchMin = 44f * factor; // heuristic, NOT iOS pt or Android dp
                if (bounds.width + .01f < touchMin ||
                    bounds.height + .01f < touchMin)
                    audit.Warnings.Add("TOUCH-TARGET: below 44 design-unit heuristic " + path);
                if (button.interactable && button.onClick.GetPersistentEventCount() == 0)
                    audit.Warnings.Add("UNBOUND-ACTION: interactive button " + path);
            }
            for (int i = 0; i < rect.childCount; ++i)
            {
                var child = rect.GetChild(i) as RectTransform;
                if (child == null)
                    audit.Warnings.Add("UNSUPPORTED: non-RectTransform child " + path);
                else
                    AnalyzeChild(child, bounds, safe, factor, path, audit, depth + 1, inSafe);
            }
        }
    }
}
