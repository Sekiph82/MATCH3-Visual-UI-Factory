// Imported and minimally adapted from Unity UI Extensions under BSD-3-Clause.
// Original: https://github.com/Unity-UI-Extensions/com.unity.uiextensions
// File: Runtime/Scripts/Utilities/NonDrawingGraphic.cs
// Upstream blob SHA: abd42d8920aedfc7c4f887a0c6ea02496a57849c
// Modification: namespace isolated for VUF Editor assembly; not a new effect.
// Full upstream copyright, conditions and disclaimer in
// third_party/UnityUIExtensions/LICENSE.md (must ship with source/binary).
﻿/// Credit Slipp Douglas Thompson 
/// Sourced from - https://gist.github.com/capnslipp/349c18283f2fea316369

using UnityEngine;
using UnityEngine.UI;

namespace Match3.VisualFactory.Editor.ThirdParty
{
    /// A concrete subclass of the Unity UI `Graphic` class that just skips drawing.
    /// Useful for providing a raycast target without actually drawing anything.
    [AddComponentMenu("Layout/Extensions/NonDrawingGraphic")]
    [RequireComponent(typeof(CanvasRenderer))]
    public class NonDrawingGraphic : MaskableGraphic
    {
        public override void SetMaterialDirty() { return; }
        public override void SetVerticesDirty() { return; }

        /// Probably not necessary since the chain of calls `Rebuild()`->`UpdateGeometry()`->`DoMeshGeneration()`->`OnPopulateMesh()` won't happen; so here really just as a fail-safe.
        protected override void OnPopulateMesh(VertexHelper vh)
        {
            vh.Clear();
            return;
        }
    }
}