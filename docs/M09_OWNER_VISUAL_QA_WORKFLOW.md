# VUF-M09 | Owner Manual Visual QA and Responsive Regression

**Canonical task tracker:** root `TASKS.md`, existing M09-001..017 only.
This guide is NOT a second tracker. Code here is non-shipping source authoring,
not the creative/artistic or iOS/Android device acceptance of five games.

## M09 source design, assembled from pre-existing VUF modules

The new Unity Editor menu **Tools > MATCH3 > M09 Owner Visual QA Studio**
opens `VufM09OwnerVisualQaWindow.cs`. It reuses actual:
- `VufScreenCatalog.LoadScreens`: **28 Coral Rescue only** original contract IDs.
- `VufScreenCatalog.LoadStyle`: five independent DRAFT palettes and skins.
  Other four games do **not** obtain their own finished 28-screen contracts
  by borrowing Coral markup. Clearly mark N/A when shown in a foreign skin.
- `VufScreenShellBuilderWindow.BuildCandidateHierarchy`: real disposable uGUI
  Canvas/Text/Button/Images, intentionally blocked gameplay callbacks.
- `VufReviewStateCatalog.Apply`: 8 MOCK states, en/tr/stress artificial copy.
- `VufResponsiveGeometry.Analyze`: five **synthetic** notched-phone/tablet/
  landscape safe-area presets, approximate touch/anchor checks.
- `VufTypographyAudit.Analyze`: dynamic Unity TextGenerator text-fit and
  conservative 4.5:1 contrast risk flags. These are source heuristics,
  not WCAG or physical touch DP claims.
- `VufUiTween`: reduced-motion CanvasGroup show/hide with explicit single-step.
- M07 Unified Sprite & VFX Review Studio: 14 view-only event selectors,
  real imported SpriteRenderer and ParticleSystem, FX still/mute/cue logs,
  manual frame scrub, .25/.5/1/2x, pivot and atlas swapping. The M09
  Studio links to this existing tool rather than cloning its renderer.
- M06 Environment Layer & Parallax Review: real existing layered BG inspector.
- M08 External Visual Pack Sandbox and M09 readiness/rights evidence board.
  No remote Engine, LFX, cloud service, money, save or match rule API imported.

**Owner interactions in the M09 window:** choose draft theme, Coral screen,
8-state + 3-language mock, synthetic phone/tablet, symbolic level and seed,
visual cue, speed, reduced-motion and guides. Build a temporary REAL Unity
uGUI component hierarchy and inspect geometry/text/contrast/touch-target
warnings. A single candidate-only button click writes a text trace; blocked
social/events/game business functions remain OFF. Click Render to produce a
true **Unity Editor RenderTexture PNG** of the current disposable candidate,
not a hand-drawn fake image; pin A for side-by-side B comparison. The render
uses a temporary camera and restores the candidate Canvas settings. Owner
may export PNG + an immutable **UNAPPROVED** JSON SHA receipt to new files
outside repo only, with 0 automatic rights/device/game/creative signoff.
Owner can also export **8 Editor-only frame-by-frame CanvasGroup tween PNGs**
with SHA receipts into a newly created external folder. No actual MP4, camera
recording, live hardware GPU/FPS or sound/haptic playback is claimed.
GUI screenshot and actual frame export remain **NOT RUN** until used by owner.

`VufM09MatrixAudit.InspectBatch` audits 1..32 **actual Unity component**
combinations per click in deterministic order. Across 5 draft style skins,
28 Coral IDs, 8 mock states, 3 review locales and 5 synthetic devices the
source matrix contains **16,800 candidates**. Only the selected batch
has been inspected; unvisited cells must never be treated as rendered or
automatically accepted. 4/5 game profiles only display reused Coral draft IDs
and are explicitly `N_A_FOREIGN_GAME_USING_CORAL_DRAFT_CONTRACT`.
For repeatable source indexing without graphical Unity:
`python -B -m factory.qa.m09_review_inventory`.

## Windows SOURCE viewer

The new optional Windows 11/Python 3.12 stdlib Tk tool
`Tools/vuf_m09_windows_viewer.py` opens M08 TEST_ONLY export directories
(one required, second optional) and validates their full source receipts and
VF04 atlas hashes before displaying candidate original PNG pixels.
Owner can compare A/B, select mock state/locale/synthetic device/event,
level+seed, source FX frame 0..7, pause/step and 0.25/0.5/1/2x. The
optional review JSON is create-only outside the Git workspace. Real Unity
Canvas, gameplay event playback, safe area and video are deliberately N/A
in this Tk source viewer, explicitly marked in the GUI.

```powershell
python -B -m Tools.vuf_m09_windows_viewer --pack-a "C:\VUF_TestCandidates\Coral_Review_New"
python -B -m Tools.vuf_m09_windows_viewer --pack-a "C:\VUF_TestCandidates\Coral_A" --pack-b "C:\VUF_TestCandidates\Coral_B"
```

Neither command is run by this guide. A pack can be generated from the
existing M08 Python candidate packer; choose external NEW destination.

## RGBA and accessibility/donor-first diagnostics

- `factory/qa/m09_pixel_diff.py`: real source bytes and decoder,
  per-pixel RGBA/alpha/fringing candidate comparison and visual diff PNG,
  1x vs 2x/3x nearest-source comparison, bounded animation per-frame
  diff with SHA receipts. NO production high-DPI sharpness/GPU claim.
- `factory/qa/m09_accessibility_candidates.py`: reuses original VF04
  six silhouette alpha channel masks and five style palettes, computes
  geometry-distinct alpha cue and preliminary 4.5 contrast warnings.
  Physical accessibility, final font, colour vision usability and touch DP
  remain UNVERIFIED.
- `factory/qa/m09_review_inventory.py`: exact 5x28x8x3x5 source-indexed
  ledger, per-cell candidate stage, policy-off, foreign N/A and pinned
  source catalogue digests. This is derived evidence, NOT a new task tracker.
- `factory/qa/m09_pixel_diff.verify_receipt_source` validates an owner-supplied
  provenance/creator/licence-text field receipt and exact original PNG SHA.
  It does NOT verify legal authenticity, copyright ownership or approve
  any lookalike. Owner and qualified rights reviewer must verify that evidence
  externally and sign off.

## Test and delivery gates

Tests are SOURCE-AUTHORED in `tests/test_m09_*.py` and Unity
`VufM09VisualQaEditModeTests.cs`; M09's actual new Python/full suite,
Unity 6000.6.5f1 EditMode compilation and interactive GUI have **NOT RUN**
on these new revisions yet. The M08 Codex 416 PASS/9 Windows symlink SKIP
and Unity 140/140 PASS applies exclusively to source
`de5b8cc1b0938294d8c4aa1f5405240d29817d74`, not the new M09 code.

Before considering closure, run the one existing M09-017 milestone-wide
Codex task on the final SHA, inspect real imported original art/Fonts/rights
and layout in Unity Editor GUI, capture independently verifiable rendered
screenshots and real iPhone/Android safe area/GPU/device traces, manually
compare final 1x/2x/3x animation atlas scales and reduced motion, inspect
all owner screens/state/locale profiles; verify final Engine/LFX neutral replay
and actual licensed art. **No owner signoff is implicit from a synthetic
candidate screenshot, symbolic 16,800 row count or an automated test.**
