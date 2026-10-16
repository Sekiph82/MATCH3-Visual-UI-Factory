# VF-06 | Particle/VFX authoring prototype

**Tools > MATCH3 > VFX Particle Lab** creates NEW `ParticleSystem` prefab
candidates with editable preset/tint/count/lifetime/size/speed, and optionally
a separate material when a compatible built-in/URP shader is available.
Five draft presets: BubbleRise, MatchBurst, StarSparkle, SoftDrift, PortalPulse.
Each preset is bounded to 160 particles and lifetime 2.5 s. Render pipeline
compatibility needs verification in the owner's actual Unity version.

The window's timeline/particles are **explicitly a deterministic 2D SKETCH**,
not a Unity ParticleSystem render. Inspect generated prefab in the real Unity
Scene/Game view to test the true effect before claiming VFX/animation PASS.
Reduced motion currently uses a static sketch; runtime reduced-motion effects,
shader/noise/graph preview, genuine event timelines, sound, haptics,
performance instrumentation and chain combos remain NOT IMPLEMENTED.

All effects must be presentation-only. No score, life, reward, purchase,
savegame or Match3 board actions are in this package. A local original or
owner-reviewed shader/material is necessary for production export.

## R22 | Deterministic procedural VFX sprite-sheet production

`python -B factory/vfx_builder/procedural_fx_sheet.py --preset BubbleRise --frames 12 --frame-side 64 --columns 4 --output-dir "D:\\VUF_CANDIDATES\\bubble_fx_001"`

Unlike the prior 2D *sketch*, this actually generates an original **RGBA
animated PNG sprite sheet** plus a **separate static reduced-motion PNG**.
Five mathematical AUTHORING_ONLY effect families use existing preset policy:
`BubbleRise`, `MatchBurst`, `StarSparkle`, `SoftDrift`,
`PortalPulse`. Other parameters are `--fps`, bounded integer `--seed`,
and optional RGB `--color #64E5FF`. Defaults to read-only in-memory
preview receipt if no `--output-dir` is supplied. Explicit output creates
a brand-new candidate folder containing `fx_sheet.png`,
`reduced_motion.png` and `fx_manifest.json`. The manifest includes exact
frame rectangles, per-frame raw RGBA SHA-256, sheet/still SHA-256 and preset
source SHA-256. It never grants actual copyright/owner approval or game
state and never consumes provider/API keys. Bounds: 2..32 frames, frame
side 16..128, fps 1..60, max 2.1M atlas pixels.

`tests/test_procedural_fx_sheet.py` adds 12 unverified source tests. The
output is **functional concept art**, not final premium artwork, particle
shader/material VFX, mobile GPU-certified effects or owner-approved art.
