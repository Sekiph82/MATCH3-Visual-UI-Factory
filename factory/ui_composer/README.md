# VF-07 | Real, layered Unity UI Composer (prototype)

Unity menu: **Tools > MATCH3 > Interactive UI Composer**.
The prototype creates NEW, non-overwritten uGUI `.prefab` candidates containing
an actual `Canvas`, `CanvasScaler`, `GraphicRaycaster`, `Image` layers,
`Text` and a `Button`. The Button is deliberately `interactable=false`
because **no Engine gameplay action or reward authority is connected**.
`VufSafeAreaFitter` is attached to the content RectTransform for phone insets.
Profiles: all five games. Available source-level *layout archetypes*: Home,
Gameplay HUD, World Map, Shop, Events, Collection, Settings.

**Not implemented:** full 28 Coral experiences as interactive prefabs, real
screen artwork, callbacks, data bindings, font approvals, localization,
button actions, actual animations, device testing or playmode verification.
Editor must compile Unity 6000.6.5f1 and produce a prefab before saying this
works outside source code. The first build needs `com.unity.ugui@2.6.0`
which the UPM package declares. Approved asset masters are never replaced.

## R08 | Data-driven 28-screen candidate skeletons

**Tools > MATCH3 > 28-Screen Shell Builder** reads **28 stable Coral IDs**
directly from the packaged copy of `schemas/coral-experiences.v1.json` and
loads authentic **DRAFT** per-title color tokens from
`factory/visual_director/style_profiles.v1.json`. The copies under
`unity_package/Editor/Resources/` must remain byte-for-byte identical to
their canonical originals; `Tools/validate_repo_structure.py` enforces parity.

Every supported 28-ID experience creates a **new non-overwriting candidate**
Canvas/uGUI prefab. Template kinds select separate page, modal, ceremony,
overlay, playable-board or mode *layout skeletons*. The exported root has
`VufCandidateScreenMarker` recording selected title, exact contract ID,
surface type, policy gate and `CANDIDATE_NOT_APPROVED`. Pages with explicit
policy gates stay disabled. Real Buttons exist but are
`interactable=false`; all visual placeholders visibly say that branded
source artwork and Engine/game binding remain missing. `VufSafeAreaFitter`
is placed on the candidate's safe-area content node.

**28 named candidate shells are not 28 polished screens.** No product artwork,
animation, fully working layout, game source, rewards, purchases, localization,
real screen actions, original rights or owner aesthetic approvals are implied.
The Unity Editor has not actually compiled these R08 changes yet. Test on
Unity 6000.6.5f1 before claiming runtime readiness. 


## R17: review-only state and locale copy stress
`VufReviewStateCatalog.cs` is deliberately an **Editor-only mock copy
utility**, NOT a runtime game state machine or complete translation table.
All eight possible review state labels can be inspected across all 28 Coral
draft screens using one of: `en`, `tr`, `stress`. Only Home and Gameplay
have explicit Turkish **draft** titles; other screens are visibly marked
`TR TASLAK` pending localization. Expanded stress copy is a synthetic
layout hazard probe, not shipping text. Every mock label also states
`NOT GAME STATE`.
The 28-Screen Shell Builder keeps actual gameplay action Buttons disabled,
feature-policy banners unchanged and candidate approval stage unmodified.
It allows manually saving only **new** named candidate prefabs (no overwrite).
`VufReviewStateEditModeTests.cs` defines three NEW EditMode tests covering
672 state/locale/Coral combinations, invalid state/locale rejection,
unchanged policy gates and five-profile palette preservation. These tests
and two source checks have not been run at R17 exact SHA. No source art,
copyright acceptance or real device UI is involved.


## R19 | Real draft heading intake coverage, without automatic translation

A reviewed source package is **not** generated automatically. Provide an
EXTERNAL UTF-8 JSON draft using the following small example:

```json
{
  "schema_version": 1,
  "stage": "LOCALIZATION_DRAFT_NOT_APPROVED",
  "profile_id": "Coral_Rescue",
  "locales": {
    "en": {"home": "Home", "gameplay_hud": "Gameplay"},
    "tr": {"home": "Ana Sayfa", "gameplay_hud": "Oyun Ekranı"}
  }
}
```

Run the **read-only** coverage and placeholder checker:

```powershell
python -B factory/ui_composer/locale_audit.py --draft "D:\\VUF_LOCALIZATION\\coral-draft.json"
```

Optional `--output-file "D:\\VUF_LOCALIZATION\\coverage-report-001.json"`
writes a new (never overwritten) external JSON QA report. Import a COPY
as TextAsset for `Tools > MATCH3 > Localization Coverage Studio`, which
displays missing headings, long-label risks and coverage but cannot push
translations into scenes or auto-enable policy-restricted pages.

The input must contain exactly the 28 stable Coral contract keys when
complete, but **incomplete drafts are deliberately accepted and reported
as incomplete**, not as a finished localization. `en` and `tr` draft
maps accept only known keys and nonempty Unicode values of <=240 characters.
Invisible/bidi control characters, duplicated JSON keys and broken or
mismatched `{named_placeholder}` tokens are rejected. Entry paths must
be outside Git; reports are never allowed to replace an existing file.
This is not a certified Turkish translation or right-to-left locale
engine, language QA, fallback-string generator or Unity text clipping test.

`tests/test_locale_audit.py` adds 18 offline Python cases; three separate
Unity EditMode tests cover the read-only coverage viewer and forged
approval/feature gates. They are SOURCE-DEFINED, NOT YET RUN at R19 SHA.

## R28 | Five-game noninteractive mobile concept PNG showcase

`python -B factory/ui_composer/concept_showcase.py --scale 1 --seed 0`

Generates **15 actual RGBA concept PNGs in memory**: each of five
distinct Style Bible draft palettes/mathematical motif languages gets
`home`, `gameplay` and `world_map` conceptual screens at 360×640.
Use `--scale 2` for 720×1280. To intentionally save, provide a NEW
external folder using `--output-dir "D:\\VUF_CANDIDATES\\concept_001"`.
A default call never writes files. Only new external folder writes are
allowed; no overwrites or original PNG edits.

Images combine six real mathematically rasterized and SHA-pinned tile
silhouettes, separate theme motifs (coral bubbles, metal rivets,
prehistoric foliage, magical circles, toy confetti), simulated scene
tiles/level nodes, and visual-only placeholder bars. Nothing is interactive,
licensed original game art, live score, a functioning button, WCAG-certified
text or a completed premium UI. The generator NEVER flattens or replaces
actual Unity interactive UI; it makes separate named concept previews
to visually evaluate composition and direction.

Files: `preview_<Profile>_<page>.png` (15) and
`showcase_manifest.json` with exact profile and page order,
360×640 or 720×1280 dimensions, PNG/source/style/tiles SHA-256 receipts
and explicit `VISUAL_CONCEPT_NOT_INTERACTIVE` flags.

`tests/test_concept_showcase.py` has 10 authored Python source tests.
Their actual execution on Windows is still OPEN at R28 code SHA.

## R32 | Editable concept reference stage builder for five games

After R28 creates the 15 concept PNG reference images and R30 verifies
the external original candidate folder, import COPIES of the PNGs and
`showcase_manifest.json` under an Assets subfolder. Open Unity Editor
`Tools > MATCH3 > Editable Concept UI Stage Builder` or the Factory
Dashboard. Pick one of five profiles and Home / Gameplay / World Map.
The window checks actual imported PNG SHA256 against the source manifest
receipt, rejects linked/outside-Assets originals, and constructs a **NEW**
Unity `.prefab` containing real, independently editable uGUI elements:

- `Canvas`, `CanvasScaler` and `VufSafeAreaFitter`.
- Theme-draft `BackgroundColor`, editable `Text` heading/banner,
  separate `Button` with `interactable=false`, no game callbacks.
- Optional `RawImage` showing the reference PNG under those real uGUI
  elements; `raycastTarget=false`, replace/remove before final artwork.
- Explicit `CANDIDATE_NOT_APPROVED` / `REQUIRES_ENGINE_OR_GAME_BINDING`
  marker, owner/rights/device QA not completed, NO production publishing.

Only user-selected brand-new `.prefab` paths are written, never replaced.
The reference image alone is NOT accepted artwork or an interactive UI.
This is a manual creation tool, not automatic 15-prefab bulk publishing.
Its C# SHA check certifies image/receipt *consistency*, not the ownership
or human legitimacy of the manifest.

Four new Unity EditMode tests cover 5x3 in-memory stages, disabled actions,
misaligned profiles/PNG dimensions, no-reference stage, and forged
approval. Three Python structural guards are also authored. They await
the next consolidated local Windows/Unity test, not per-feature Codex.

## R34 | One-image five-game comparison sheet (no Unity required)

After saving the R28 15-PNG concept bundle and validating actual bytes
with `verify_generated_kits.py showcase`, generate one bounded composite
**contact sheet PNG** for rapid owner art-direction comparisons:

`python -B factory/ui_composer/contact_sheet.py --candidate "D:\\VUF_CANDIDATES\\concept_001" --output-file "D:\\VUF_REVIEWS\\five-game-review-001.png"`

Five game columns x Home/Gameplay/World Map rows each show their exact
individual original mathematical concept thumbnails. Tiny fixed 5x7
ASCII labels identify the theme and page. Output includes cell positions,
individually rechecked source SHA256 receipts, contact-sheet SHA256 and
explicit `CANDIDATE_NOT_OWNER_APPROVED` / noninteractive status. Without
`--output-file`, only computed JSON manifest prints to stdout, with no
disk writes. The output path must be a NEW PNG outside Git, never overwriting
an existing file. Actual concept images, original art, Unity metadata
and game repositories are never modified.

It is still a static reference sheet, not high-end art or a finished
responsive interactive UI, authentic licensing or physical device QA.
Five Python tests are authored for future bundled local execution.

## R35 | Editable page-specific uGUI composition

The existing `Tools > MATCH3 > Editable Concept UI Stage Builder`
now goes beyond a flattened source screenshot: after checking the imported
reference SHA and five-game Style Bible, it creates separate, editable
uGUI authoring objects for **three different screen page layouts**.

- Home: distinct hero artwork placeholder, editable mission panel with
  static progress bar, four collectible placeholders.
- Gameplay: 6-column × 7-row **STATIC board preview**, separate
  score/objective/moves Text components and three booster placeholders.
- World Map: seven manually editable level map markers linked by six
  decorative path segments and a map footer.

All of these are **purely visual candidates**. The test board contains
neither matches nor input; level markers have no navigation, rewards or
save-data callbacks; text/graphics are editable. The original design
reference is a separate optional `RawImage`, not a clickable flattened
background. Nothing here is a production-quality artwork or a real game
HUD. Disabled primary game action and existing policy gates remain.

`unity_package/Editor/VufPageComposition.cs` is the shared in-memory
composition helper; four Unity EditMode test methods and Python source
guards are authored. Real Editor compilation and UI visual acceptance
for R35 are still NOT RUN.

## R36 | Five original mathematical uGUI motif grammars

The same stage builder now layers profile-specific **editable,
noninteractive** geometric decoration *under* its page components:
Coral bubbles, Garage rivet plates, Dino foliage stems, Fractured Realms
portal diamonds, and Wonder Pop confetti. These are intentionally
different shapes rather than mere palette swaps. All Images have
`raycastTarget=false`. They are draft shapes, **not owner-provided art**,
real physics, sprites, skeletal animation or shaded effects.

The authoring-only source is
`unity_package/Editor/VufThemeMotifDecor.cs`. Four Unity EditMode
tests cover five distinct motif sets, input safety and duplicate
composition rejection. `tests/test_editable_composition_contracts.py`
adds three Python source checks for R35/R36. All R35/R36 tests are
authored but NOT run on owner-local Windows/Unity.

## R37 | License-compliant tested upstream uGUI primitive, not rewritten

A COPY of Unity UI Extensions `NonDrawingGraphic` is vendored under
`unity_package/Editor/ThirdParty/` from an exact upstream BSD-3-Clause
Git blob. Namespace is isolated; original contributor credits are
retained. Full BSD-3-Clause license is included at
`third_party/UnityUIExtensions/LICENSE.md`.
The component is placed last in all new editable concept stages as an
invisible raycast-only shield for candidate-only UI. This blocks input
without covering the draft visuals or activating any Button.
**No network install or second UI package dependency.**

## R38 | Reuse existing reduced-motion tween, do not rebuild it

`VufCandidateMotionKit` attaches the already existing/tested runtime
`VufUiTween` to one editable major panel per page, with a CanvasGroup
and reduced motion enabled by default. It adds NO new tween easing
algorithm. All candidate primary actions stay unbound and disabled.

Before production export, the stage still needs real Unity rendered
GUI/art owner inspection and device accessibility review. The new
C# R37–R38 NUnit and Python source tests have been written but are
NOT RUN yet on the owner-local Windows checkout.

## R39–R40 | Real open-source Gradient + UIFlippable integration

Mature `Unity UI Extensions` **BSD-3-Clause** implementations
`Gradient.cs` (upstream Breyer credit) and `UIFlippable.cs`
(upstream ChoMPHi credit) are copied from pinned Git blobs into
`unity_package/Editor/ThirdParty/`, with isolated namespaces and
attribution. Gradient fixes only the upstream min/max-bounds/zero-height
corner cases in Unity quad geometry. Gradient mesh effects are attached
to Home hero, Home mission, Gameplay HUD and World Map placeholder
panels. UIFlippable is used to mirror selected Dino Islands leaf
geometry instead of writing another mesh transformation.

These are editor-only candidate effects, not real art/rights/device
approval and not actual game input. Four Unity mesh/source contract
tests and five Python source checks are authored; local Unity execution
is still pending for this new batch. The heavy `UILineRenderer` donor
was inspected and intentionally not imported due transitive primitive,
Bezier and cable dependencies.
