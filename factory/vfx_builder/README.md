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
