// Direct reuse: Unity-UI-Extensions/com.unity.uiextensions BSD-3-Clause release commit d47f838ba918bbb9b26f242bd944940a711f525f
// Exact upstream blob fc07fac023536cd54f350e8aa3d06c2015c1782c; credit/copyright/MIT notice below retained.
// BSD-3-Clause redistributed in unity_package/NOTICE-UnityUIExtensions.md
using UnityEngine;
using UnityEngine.UI;

/// Credit Danny Goodayle 
/// Sourced from - http://www.justapixel.co.uk/radial-layouts-nice-and-simple-in-unity3ds-ui-system/
/// Updated by SimonDarksideJ - removed dependency on a custom ScrollRect script. Now implements drag interfaces and standard Scroll Rect.
/// Child Layout fix by John Hattan - enables an options 

/*
Radial Layout Group by Just a Pixel (Danny Goodayle) - http://www.justapixel.co.uk
Copyright (c) 2015
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
*/

namespace Match3.VisualFactory.Editor.ThirdParty
{
    [AddComponentMenu("Layout/Extensions/Radial Layout")]
    public class RadialLayout : LayoutGroup
    {
        public float fDistance;
        [Range(0f, 360f)]
        public float MinAngle, MaxAngle, StartAngle;
        public bool OnlyLayoutVisible = false;
        protected override void OnEnable() { base.OnEnable(); CalculateRadial(); }
        public override void SetLayoutHorizontal()
        {
        }
        public override void SetLayoutVertical()
        {
        }
        public override void CalculateLayoutInputVertical()
        {
            CalculateRadial();
        }
        public override void CalculateLayoutInputHorizontal()
        {
            CalculateRadial();
        }
#if UNITY_EDITOR
        protected override void OnValidate()
        {
            base.OnValidate();
            CalculateRadial();
        }
#endif

        protected override void OnDisable()
        {
            m_Tracker.Clear();
            LayoutRebuilder.MarkLayoutForRebuild(rectTransform);
            base.OnDisable();
        }

        void CalculateRadial()
        {
            m_Tracker.Clear();
            if (transform.childCount == 0)
                return;

            int ChildrenToFormat = 0;
            if (OnlyLayoutVisible)
            {
                for (int i = 0; i < transform.childCount; i++)
                {
                    RectTransform child = (RectTransform)transform.GetChild(i);
                    if ((child != null) && child.gameObject.activeSelf)
                        ++ChildrenToFormat;
                }
            }
            else
            {
                ChildrenToFormat = transform.childCount;
            }

            // Adaptation: enabled-only mode can yield zero visible children.
            // Guard against divide-by-zero without changing normal layout.
            if (ChildrenToFormat == 0) return;
            float fOffsetAngle = (MaxAngle - MinAngle) / ChildrenToFormat;

            float fAngle = StartAngle;
            for (int i = 0; i < transform.childCount; i++)
            {
                RectTransform child = (RectTransform)transform.GetChild(i);
                if ((child != null) && (!OnlyLayoutVisible || child.gameObject.activeSelf))
                {
                    //Adding the elements to the tracker stops the user from modifying their positions via the editor.
                    m_Tracker.Add(this, child,
                    DrivenTransformProperties.Anchors |
                    DrivenTransformProperties.AnchoredPosition |
                    DrivenTransformProperties.Pivot);
                    Vector3 vPos = new Vector3(Mathf.Cos(fAngle * Mathf.Deg2Rad), Mathf.Sin(fAngle * Mathf.Deg2Rad), 0);
                    child.localPosition = vPos * fDistance;
                    //Force objects to be center aligned, this can be changed however I'd suggest you keep all of the objects with the same anchor points.
                    child.anchorMin = child.anchorMax = child.pivot = new Vector2(0.5f, 0.5f);
                    fAngle += fOffsetAngle;
                }
            }
        }
    }
}
