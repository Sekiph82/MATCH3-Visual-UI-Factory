// VF-08 / VF-09: review-only typography fit and text/color-contrast diagnostics.
// Uses Unity's Font/TextGenerator metrics, but does not render, localize,
// certify accessibility or modify candidate prefabs.
using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace Match3.VisualFactory.Editor
{
    internal static class VufTypographyAudit
    {
        internal sealed class Finding
        {
            internal string Path;
            internal string Copy;
            internal float BoundsWidth;
            internal float BoundsHeight;
            internal float PreferredHeight;
            internal float ContrastRatio;
            internal bool OverflowRisk;
            internal bool ContrastRisk;
            internal bool MeasurementAvailable;
            internal bool BackgroundKnown;
        }

        internal sealed class Report
        {
            internal string DeviceName;
            internal readonly List<Finding> Items = new List<Finding>();
            internal readonly List<string> Warnings = new List<string>();
            internal int OverflowCount;
            internal int LowContrastCount;
            internal int UnmeasuredCount;
        }

        private static float Linear(float c)
        {
            return c <= .04045f ? c / 12.92f :
                Mathf.Pow((c + .055f) / 1.055f, 2.4f);
        }

        private static float Luminance(Color c)
        {
            return .2126f * Linear(c.r) + .7152f * Linear(c.g) +
                .0722f * Linear(c.b);
        }

        internal static float Contrast(Color fg, Color bg)
        {
            if (fg.a < .999f || bg.a < .999f)
                return 0f; // Uncomposited colors must never be marked PASS.
            float a = Luminance(fg);
            float b = Luminance(bg);
            return (Mathf.Max(a, b) + .05f) / (Mathf.Min(a, b) + .05f);
        }

        private static bool TryBackground(Transform node, GameObject root, out Color color)
        {
            Transform current = node.parent;
            while (current != null)
            {
                Image image = current.GetComponent<Image>();
                if (image != null && image.enabled && image.gameObject.activeInHierarchy)
                {
                    color = image.color;
                    return image.color.a >= .999f;
                }
                if (current == root.transform) break;
                current = current.parent;
            }
            Transform background = root.transform.Find("BackgroundColor");
            if (background != null)
            {
                Image image = background.GetComponent<Image>();
                if (image != null && image.enabled)
                {
                    color = image.color;
                    return image.color.a >= .999f;
                }
            }
            color = Color.clear;
            return false;
        }

        internal static Report Analyze(GameObject candidate,
            VufResponsiveGeometry.Device device)
        {
            if (candidate == null) throw new ArgumentNullException(nameof(candidate));
            var geometry = VufResponsiveGeometry.Analyze(candidate, device);
            var report = new Report { DeviceName = device.Name };
            if (!geometry.CandidateOnly)
                report.Warnings.Add("BLOCKED: candidate-only marker missing/modified");
            foreach (string warning in geometry.Warnings)
                if (warning.StartsWith("BLOCKED:", StringComparison.Ordinal))
                    report.Warnings.Add(warning);

            CanvasScaler scaler = candidate.GetComponent<CanvasScaler>();
            float referenceW = scaler != null && scaler.referenceResolution.x > 0f
                ? scaler.referenceResolution.x : 720f;
            float referenceH = scaler != null && scaler.referenceResolution.y > 0f
                ? scaler.referenceResolution.y : 1280f;
            float factor = Mathf.Lerp(device.Width / referenceW,
                device.Height / referenceH, scaler != null
                    ? Mathf.Clamp01(scaler.matchWidthOrHeight) : .5f);

            foreach (VufResponsiveGeometry.Node node in geometry.Nodes)
            {
                if (!node.IsText) continue;
                if (!node.Path.StartsWith(candidate.name + "/", StringComparison.Ordinal))
                    throw new InvalidOperationException("unexpected geometry text path");
                string childPath = node.Path.Substring(candidate.name.Length + 1);
                Transform child = candidate.transform.Find(childPath);
                if (child == null)
                {
                    report.Warnings.Add("BLOCKED: missing text node " + childPath);
                    continue;
                }
                Text component = child.GetComponent<Text>();
                if (component == null)
                    throw new InvalidOperationException("geometry text component changed");
                var finding = new Finding {
                    Path = childPath,
                    Copy = component.text ?? "",
                    BoundsWidth = node.Bounds.width,
                    BoundsHeight = node.Bounds.height
                };
                report.Items.Add(finding);
                if (!TryBackground(child, candidate, out Color background) ||
                    component.color.a < .999f)
                {
                    report.Warnings.Add("BACKGROUND_UNKNOWN: " + childPath);
                }
                else
                {
                    finding.BackgroundKnown = true;
                    finding.ContrastRatio = Contrast(component.color, background);
                    // 4.5:1 is a conservative static guidance threshold, NOT
                    // certification for a particular pt/dp size or WCAG claim.
                    finding.ContrastRisk = finding.ContrastRatio < 4.5f;
                    if (finding.ContrastRisk)
                    {
                        report.LowContrastCount++;
                        report.Warnings.Add("LOW_CONTRAST_REVIEW: " + childPath);
                    }
                }

                if (component.font == null || node.Bounds.width < 1f ||
                    node.Bounds.height < 1f || component.text == null)
                {
                    report.UnmeasuredCount++;
                    report.Warnings.Add("TYPOGRAPHY_UNMEASURED: " + childPath);
                    continue;
                }

                try
                {
                    var settings = component.GetGenerationSettings(new Vector2(
                        Mathf.Max(1f, node.Bounds.width),
                        Mathf.Max(1f, node.Bounds.height)));
                    settings.scaleFactor = 1f;
                    settings.fontSize = Mathf.Clamp(
                        Mathf.RoundToInt(component.fontSize * factor), 1, 512);
                    settings.resizeTextForBestFit = false;
                    settings.horizontalOverflow = HorizontalWrapMode.Wrap;
                    settings.verticalOverflow = VerticalWrapMode.Overflow;
                    TextGenerator generator = new TextGenerator();
                    float preferred = generator.GetPreferredHeight(component.text, settings);
                    if (float.IsNaN(preferred) || float.IsInfinity(preferred) ||
                        preferred < 0f)
                        throw new InvalidOperationException("non-finite text measurement");
                    finding.PreferredHeight = preferred;
                    finding.MeasurementAvailable = true;
                    finding.OverflowRisk = preferred >
                        node.Bounds.height + Mathf.Max(1f, node.Bounds.height * .015f);
                    if (finding.OverflowRisk)
                    {
                        report.OverflowCount++;
                        report.Warnings.Add("TEXT_OVERFLOW_RISK: " + childPath);
                    }
                }
                catch (Exception)
                {
                    report.UnmeasuredCount++;
                    report.Warnings.Add("TYPOGRAPHY_UNMEASURED: " + childPath);
                }
            }
            return report;
        }
    }
}
