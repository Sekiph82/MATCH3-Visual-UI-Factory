# VF-08 | Responsive Geometry and Simulated Device Wireframe

Runtime `VufSafeAreaFitter.cs` remains the source of actual device safe-area
anchor updates; the original owner/device QA gates stay open.

## R15 source: Tools > MATCH3 > Responsive Layout Wireframe

The **read-only** Unity Editor window `VufResponsivePreviewWindow.cs` accepts
an existing candidate GameObject/prefab, models its RectTransform anchor
and offset bounds, and draws an **approximate wireframe** with text/button
rectangles. It never invokes renderers, PreviewRenderUtility or owner art
services, never edits the prefab and never writes screenshots or project
assets. A button in the five-game Dashboard opens this window.

The geometry engine `VufResponsiveGeometry.cs` offers **five synthetic
screen ratio/inset presets** (tall phone, Android, compact phone, tablet,
landscape phone). It models the runtime SafeAreaFitter as a simulated safe
rectangle, checks candidate-only status, alerts on off-policy pages, warns
about anchored regions outside a synthetic safe-area, invalid/non-finite
anchors, active Buttons without serialized callbacks, and unusually small
touch targets (44 **design units**, explicitly NOT actual platform points/dp).

`VufCatalogEditModeTests.cs` has three new, not-yet-executed NUnit tests:
- every Coral Rescue screen against the five synthetic devices (140 layout
  checks) for the candidate-only marker, one disabled Button and safe bounds;
- a deliberately tiny unbound interactive Button must trigger warnings;
- the Home screen must keep its original distinct candidate profile across
  the five game themes.

## Accuracy limits

* Only RectTransform anchoring/offset geometry is modeled. `HorizontalLayoutGroup`,
  `ContentSizeFitter`, imported fonts, dynamic content, native UI layouts,
  rendering, sprite atlases and runtime graphics are NOT evaluated.
* Device preset insets are synthetic examples, not certified Apple/Samsung
  hardware dimensions. Landscape dimensions are a stress test, not a design
  guarantee; potential underflow/overflow are findings, not runtime screenshots.
* Button warning is a static inspection, not a live tap-through or game
  binding test. Animated canvases, live safe-area updates, actual accessibility
  pt/dp measurement, EN/TR localization, RTL and multi-language truncation
  remain separate work.
* **Nothing here is a GUI, real iPhone/Android, owner creative/art, or product
  release PASS.** Current R15 Editor source/tests require real Unity
  6000.6.5f1 import and exact-SHA regression evidence.

## R18 | Typography and Contrast Lab (Editor-only)

**Tools > MATCH3 > Typography and Contrast Lab** analyses original unapproved
uGUI candidate hierarchies without saving, approving, editing or rendering
the prefab. It combines existing five synthetic device anchor/bounds models
with Unity `TextGenerator.GetPreferredHeight` for the actual `Text.font`
when installed. Each text node gets measured bounds, approximate preferred
line-block height, **possible overflow** flag and an advisory foreground vs
closest opaque Image/fallback canvas background contrast ratio.

Conservative risks include `TEXT_OVERFLOW_RISK`, `LOW_CONTRAST_REVIEW`,
`BACKGROUND_UNKNOWN` and `TYPOGRAPHY_UNMEASURED`. Null/missing fonts
and transparent backgrounds remain **UNKNOWN**, never silently pass.
`4.5:1` is an indicative static threshold, not a WCAG/device certification.

The Inspector is a read-only visual *data report*, **not an actual Unity
textured frame**, physical safe-area simulation, fully shaped Unicode
text, RTL, dynamic ContentSizeFitter, Game View screenshot or native
iPhone/Android test. The Turkish mode remains synthetic draft copy.

Five new Unity EditMode test methods and three Python source contract
checks are authored for R18. Real Windows Unity 6000.6.5f1 verification
at the final R18 SHA remains open until explicitly executed.
