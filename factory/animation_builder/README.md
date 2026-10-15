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
