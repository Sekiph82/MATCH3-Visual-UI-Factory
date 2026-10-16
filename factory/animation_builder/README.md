# VF-05 | Multi-method animation authoring (first Unity implementation)

**Already implemented at source level:** the portable Unity package adds
**Tools > MATCH3 > Sprite Animation Builder**. It discovers unrotated Sprite
sub-assets of a selected original/licensed Unity Texture2D imported in
Sprite (Multiple) mode. It supports frame scrub/play/pause, FPS 1 to 60,
loop/ping-pong selection, reduced-motion preview, natural numeric sprite
name ordering, and writes **new, never-overwritten** `.anim` candidates
bound to `SpriteRenderer.m_Sprite`.

Unity Editor must compile and run this tool before the feature is claimed
tested. Save destinations are chosen inside the Unity project as original
candidate clips and must receive real owner creative review before export.
No animation callback can grant rewards or change match board states.

**Still required:** sprite atlas clip diffs and crop tests, per-frame pivot
policies, clip interruption/replay, Unity Animator state graphs, UI tweens,
2D bone/skeletal rigs, optional 3D rigs, and actual VFX/audio/haptic
preview with reduced-motion alternatives. Animation Factory does NOT force all
three methods into sprite sheets.

## R12 | Real presentation-only CanvasGroup UI transitions (source)

`unity_package/Runtime/VufUiTween.cs` now implements a deterministic,
interruptible `CanvasGroup.alpha` ease-in/out transition using scaled or
unscaled delta time. It exposes `Show()`, `Hide()`, `Advance(seconds)` and
`SetReducedMotion(bool)`. During fading it suppresses UI raycasts/interactions
until fully visible. Reduced motion immediately snaps to the requested
visibility state.

`unity_package/Editor/VufUiTweenInspector.cs` adds manual PlayMode buttons
for Show/Hide and reduced-motion ON/OFF. The 28-screen candidate authoring
tool attaches CanvasGroup + VufUiTween to modal, ceremony and overlay
shells. Other screen types do not receive unwanted animation automatically.

Two additional authored Unity EditMode tests cover reduced-motion snap and
interruptible deterministic final state, bringing the current UPM authored
EditMode suite to eight tests. The actual Unity Editor PlayMode visual result
is still unverified. This is not a generalized skeletal-rig, 3D animation,
Animator state graph or timeline authoring feature. No callbacks touch
Engine board state, purchases or rewards.

## R23 | Unity procedural FX sprite-sheet player

`Tools > MATCH3 > Procedural FX Sheet Player` reads imported COPIES of
`fx_sheet.png`, `reduced_motion.png`, `fx_manifest.json` and provides a
frame-by-frame static/scrub/loop preview. Its manifest parser confirms
candidate status, the five allowed effect families, exact frame atlas
geometry and the mandatory static reduced-motion alternative. It refuses
approved/rights-forged/game-event states, malformed frame rects and bad
hash-format receipts. It does **not** independently recompute PNG hashes.

This is a separate simple read-only preview from the existing
`Sprite Animation Builder`. Importing/slicing the sheet into genuine
Unity Sprite sub-assets and creating an editable .anim remains an explicit
manual Editor step, not a background modification of owner TextureImporters.
Three new Unity EditMode test methods are authored but have NOT been
executed by Unity 6000.6.5f1 at R23 SHA. The UI itself needs GUI inspection.
