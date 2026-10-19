# VUF R37-R38 | Verified Donor Source and Reuse Ledger (not a task tracker)

Date: 2026-10-16. This document is an audited software source/provenance register for Visual & UI Factory. The *only lifecycle/task tracker remains root TASKS.md*.

## Adopted exact upstream code donor | BSD-3-Clause

Repository: https://github.com/Unity-UI-Extensions/com.unity.uiextensions
Pinned upstream release commit: d47f838ba918bbb9b26f242bd944940a711f525f
Exact upstream file: Runtime/Scripts/Utilities/NonDrawingGraphic.cs
Git blob SHA (upstream): abd42d8920aedfc7c4f887a0c6ea02496a57849c
Verified license: https://github.com/Unity-UI-Extensions/com.unity.uiextensions/blob/release/LICENSE.md
Local license copy: third_party/UnityUIExtensions/LICENSE.md (BSD-3-Clause including copyright, disclaimer and mandatory redistribution notices).

Source was copied from that actual GitHub blob, with only a namespace isolation change to Match3.VisualFactory.Editor.ThirdParty and explicit using UnityEngine/UnityEngine.UI for that isolation. Original individual author credit is preserved in the source. File: unity_package/Runtime/ThirdParty/NonDrawingGraphic.cs. This component is battle-tested upstream as a non-drawing Graphic that still participates in uGUI raycast hit tests. It is used as the final fully transparent input shield over editable candidate prefabs. Original source code is not written from scratch. The namespace isolation prevents accidental type collision with a future installation of the full UI Extensions package. No package installation, network download at runtime, paid provider or Unity package dependency required.

## Reused existing in-repo code: no new dependency

VufUiTween from unity_package/Runtime/VufUiTween.cs already implements deterministic CanvasGroup alpha transitions and reduced-motion snapping. R38 VufCandidateMotionKit simply attaches the existing component to a draft Home hero, Gameplay HUD or World Map canvas. It does not rewrite interpolation, introduce DOTween or animate actual gameplay. Reduced motion is ON by default. Factory candidate primary Buttons remain explicitly disabled; the R37 input shield stays on top.

## Other previously discussed external donors: examined, not indiscriminately copied

- DhafinFawwaz/Unity-AnimationUI: https://github.com/DhafinFawwaz/Unity-AnimationUI (MIT). Supports Inspector animation sequences and editor preview; its AnimationUI.cs alone is around 80kB and depends on TMPro/extra sequence infrastructure, with input/scene/audio side effects. No direct import into authoring-only package; current existing VufUiTween reuse is leaner and avoids a second engine.
- Unity-UI-Extensions/com.unity.uiextensions (BSD-3-Clause): many mature Unity 6 uGUI controls. UILineRenderer needs its custom control mesh/primitive dependencies and has not been imported; Gradient.cs includes assumptions about nonzero geometry and has not been imported. Full package may be evaluated separately rather than manually reimplementing controls.
- LibraStack/Match3-SDK: https://github.com/LibraStack/Match3-SDK (MIT). Core swap/match/fill belongs to separate MATCH3 Engine, not Visual Factory. Do not add a competing match engine here.
- JohannesBuchner/ultragem: https://github.com/JohannesBuchner/ultragem (Simplified BSD-derived code; underlying Al Sweigart credit). Bot/auto-level/difficulty logic belongs to separate Match3 Level Factory, not UI Factory.
- Unity-Technologies/Game-Simulation-Match-3-Sample: https://github.com/Unity-Technologies/Game-Simulation-Match-3-Sample (Unity Companion License). Editor/LevelSO/bot examples belong to Level Factory evaluation; Unity license conditions and old service package matter. No automatic cloud Game Simulation or source copied into UI Factory.
- AlperenGarip/Match3: https://github.com/AlperenGarip/Match3 (MIT as previously documented for level-builder pieces), Level Factory rather than UI Factory.
- Rimaethon/Gem-Match3: https://github.com/Rimaethon/Gem-Match3 (CC BY-NC-ND 4.0). Do NOT copy derivative game/UI code for our potentially monetized games; reference architecture only.
- User-approved Godot effect plugins GameFeelFlow and Saltmire Spark do not run in Unity. No copied incompatible Godot plugin source.
- Source art, sprites, textures, fonts and demo scene assets are NOT licensed automatically by the source code license. No third-party visuals/assets have been imported.

## Standing donor-first rule for subsequent VUF work

Before implementing a substantial new visual feature, first inspect the existing VUF implementation and relevant external maintained Unity 6/uGUI or Python tooling. Prefer verified compatible existing methods. If externally vendoring actual source, pin repository, exact upstream commit/path/blob hash, retain required copyright and license notices, isolate types, add stable Unity .meta GUIDs, constrain permissions, and author local source/real Unity tests. If upstream code has incompatible dependencies, licensing uncertainty, hidden paid APIs or gameplay side effects, record rejection instead of importing or claiming prior testing. Keep owner originals and approved assets untouched, no paid/hosted CI, no automatic gameplay binding or owner PASS.
## R39–R40 | ACTUAL second/third BSD3 vendor components

Before designing the next UI effects, checked these exact external Github donors:
- Unity UI Extensions `Runtime/Scripts/Effects/Gradient.cs`, upstream commit `d47f838ba918bbb9b26f242bd944940a711f525f`, exact Git blob `d3387fd4c917196209079970e436cf0f8ffaddfc`, original Breyer credit.
- Unity UI Extensions `Runtime/Scripts/Effects/UIFlippable.cs`, exact Git blob `d06dbb032940ec8938b3841351f3ff7b7190dac1`, original ChoMPHi credit.
Both are BSD-3-Clause under the already vendored `third_party/UnityUIExtensions/LICENSE.md`, and source credits are retained. Actual original source copied to `unity_package/Runtime/ThirdParty/Gradient.cs` and `UIFlippable.cs`; namespace adapted to `Match3.VisualFactory.Editor.ThirdParty` and explicit Unity imports added. Gradient has TWO bounded defect protections: initialize its Graphic lazily and compute real vertex-list min/max instead of unsafe first/last (including zero-height guard) for Unity closed quads. No new gradients/flip vertex algorithms or heavy dependency rewritten.

R39 uses the donor `Gradient` as a `BaseMeshEffect` on the existing editable Home hero/mission, Gameplay HUD and WorldMap canvas. R40 uses actual donor `UIFlippable` horizontally on alternating Dino leaf graphics, allowing authored mirrored leaf sprites without custom UV/mesh rewrite. Four new real Unity NUnit tests (mesh vertex colors, collapsed zero-height safe return, actual flip positions, integrated five-theme UI) and five Python contract/source tests are written, not yet run. No Unity AssetDatabase importer mutation, gameplay binding, shader/device validation or production artwork acceptance. Existing R35–R38 tests also remain unverified.

Rejected upstream `UILineRenderer.cs` for current small world-map use because its dependencies on `UIPrimitiveBase`, `BezierPath`, `CableCurve` and nontrivial mesh stack exceed simple editor line placeholders; do not copy until mature world-map curve editing needs the complete vetted dependency slice. Existing simplified R35 lines remain independent.

## R41 | Fourth real BSD3 donor: responsive wrap layout

Inspected **Unity UI Extensions** `Runtime/Scripts/Layout/FlowLayoutGroup.cs`,
pinned release commit `d47f838ba918bbb9b26f242bd944940a711f525f`,
original Git blob `a949d0c23d27124c3347405972cca7bb7a7a3489`.
Retains original credits to Simie, Martin Sharkbomb, Vicente Russo and
Ramon Molossi, plus upstream `third_party/UnityUIExtensions/LICENSE.md`
BSD-3-Clause terms. The real upstream `LayoutGroup` source was copied to
`unity_package/Runtime/ThirdParty/FlowLayoutGroup.cs`, changing ONLY its
namespace to isolated `Match3.VisualFactory.Editor.ThirdParty` and
adding explicit UnityEngine/UnityEngine.UI imports. It has no other
package dependencies and does not create gameplay events.

Home `HOME_CollectionSlots` now uses the ready-made donor wrapping layout
instead of implementing custom rows: four editable collection cards have
`LayoutElement` preferred size, simple spacing and can wrap when their
parent RectTransform narrows. This is a true uGUI LayoutGroup, not an
image mockup. Two Unity NUnit and three Python source tests authored, NOT
run locally on current new SHA. Must confirm actual rendered responsive
geometry in real Unity GUI before owner/phone PASS.

## R41 release-packaging license hardening

The exact upstream BSD-3-Clause text is also duplicated verbatim to
`unity_package/NOTICE-UnityUIExtensions.md`, including its copyright,
disclaimer and redistribution conditions, so an extracted standalone
`unity_package` copy retains the required terms. Root-side authoritative
copy is `third_party/UnityUIExtensions/LICENSE.md`. A stable .meta GUID
for the notice is committed. Neither notice implies a warranty or
license to original third-party sprites, textures, fonts or demo art.

## R42 | Fifth direct donor: responsive radial Home badge orbit

PRE-CODE DONOR CHECK: inspected actual GitHub upstream source
`Unity-UI-Extensions/com.unity.uiextensions` at pinned release commit
`d47f838ba918bbb9b26f242bd944940a711f525f`:
`Runtime/Scripts/Layout/RadialLayout.cs`, Git blob
`fc07fac023536cd54f350e8aa3d06c2015c1782c`.
Original contributor Danny Goodayle and the embedded 2015 MIT
copyright/permission/disclaimer are retained, along with BSD-3-Clause
package notices already in `unity_package/NOTICE-UnityUIExtensions.md`.
Source copied directly as `unity_package/Runtime/ThirdParty/RadialLayout.cs`.
MINIMAL_ADAPTER: added namespace isolation and explicit Unity using
directives; added ONE guard for zero active visible children when
`OnlyLayoutVisible` is true, preventing divide by zero.
No new radial placement algorithm was developed.

R42 reuses this `LayoutGroup` on
`HOME_HeroArtworkPlaceholder/HOME_OrbitLayout_AUTHORING_ONLY`:
five separately editable, input-disabled geometric prototype badges,
with initial 135px radius, 0–360° and user-configurable StartAngle in
Unity Inspector. Orbit badges are mathematical placeholders, not
commercial icons, mascot art or live rewards. At source time three
Unity EditMode tests (five badge positions, all-inactive safe branch,
rotation after angle edit) and three Python donor/provenance contracts
are AUTHORED, NOT owner-local tested.
Donor disposition: DIRECT_REUSE + MINIMAL_ADAPTER (one null-visible guard);
license MIT embedded + BSD3 package notice, no package install or service.

## C010 Unity 6.6 runtime-component import correction

The first real Unity 6000.6.5f1 run found that scripts under an `Editor/`
directory cannot be attached with `GameObject.AddComponent`, even while the
Editor is constructing candidate UI. The five direct donor sources were
moved unchanged (retaining their original code and stable `.meta` GUIDs) to
`unity_package/Runtime/ThirdParty/`, which compiles them into the package's
runtime assembly so Unity can serialize and attach them to candidate objects.
The authoring code remains editor-only; this does not bind gameplay. The
Unity 6 `SetLayoutInputForAxis` API adds a `totalMax` parameter, so the three
FlowLayoutGroup calls now explicitly preserve the upstream min/preferred/
flexible semantics. Gradient enum references are fully qualified to avoid
the collision with `UnityEngine.GradientMode`. Full Python and Unity results
for this correction are recorded in the C010 evidence report.

## R43 | Direct integration through INTERNAL_REUSE instead of another imported dependency

Mandatory pre-code donor comparison completed:
- Existing VUF `VufScreenShellBuilderWindow`, R35 `VufPageComposition`, R36
  `VufThemeMotifDecor`, R38 `VufCandidateMotionKit`, and pinned BSD3 UI
  Extensions `NonDrawingGraphic` donor were inspected for direct reuse.
- Also checked maintained upstream Unity UI Extensions `TableLayoutGroup.cs`
  at release commit `d47f838ba918bbb9b26f242bd944940a711f525f`,
  blob `663857f6abd05a54159a1c0cc112371c9cb26b92`.
  **REJECTED_REASON:** adding another dynamic nonuniform layout component to
  already working Home/Game/Map shells would duplicate R35's existing
  donor-backed FlowLayoutGroup and require unnecessary extra dependency.
- **INTERNAL_REUSE selected**: small glue module
  `unity_package/Editor/VufScreenShellLayoutBridge.cs` uses the existing
  28 exact Coral screen contracts with the five Style Bible profiles.
  It decorates all 140 candidate screens with the five profile-specific
  existing motif grammars and the real original BSD3
  `NonDrawingGraphic` last-child raycast shield. Only the five clearly
  matching screen contracts Home, World Map, Gameplay/HUD, Endless and
  Time Attack receive the already implemented appropriate
  `VufPageComposition` and existing reduced-motion `VufUiTween`.
  No gameplay logic, new vendor copies, original art, file writes or
  callback activation. Original five disabled/policy-locked social pages
  remain locked. This is glue code, not a new layout or tween algorithm.

Four new Unity EditMode NUnit definitions exercise five profiles × 28 screens
(140 in-memory structures), five actual page layouts, all five social
policy-locked screens, strict identity and duplicate enhancement rejection.
Four new source-only Python contract definitions. **NEW R43 tests NOT YET RUN.**
Previous C010 Python 294 PASS/7 OS SKIP and Unity 72/72 PASS apply only to
the earlier final commit `1ea8ac06dd13485d6c5c42a30c6d98154259c959`.
No new source rights, GPU performance, phone UI or owner artistic approval.

## R44 | VF-10 / M08-005 player content scanner donor-first decision

BEFORE source coding: inspected the existing VUF `Tools/validate_manifest.py`,
`Tools/validate_repo_structure.py`, `factory/validators/verify_candidates.py`
and export pipeline README; also reviewed the pinned Unity UI Extensions
`package.json` at exact upstream commit
`d47f838ba918bbb9b26f242bd944940a711f525f`,
Git blob `6bb5e0dbfa6878c24df2e8d1b5e42e4c970c1b15`,
and `Unity-Technologies/Addressables-Sample` repository metadata.
**REJECTED_REASON**: full Unity UI Extensions and Addressables samples are
editor/package demos, not a standalone, fail-closed, read-only player file
allowlist/security checker. Importing those would add unnecessary
dependencies and falsely conflate dev packages and player shipping.
**INTERNAL_REUSE / STDLIB MINIMAL ADAPTER**: preserve existing VUF
candidate-approval and SHA/path philosophy with Python `pathlib`,
`os.walk`, `hashlib`, `re`, `stat`, `json` (standard library)
in a new bounded read-only `factory/export_pipeline/player_pack_preflight.py`.
No downloaded code/vendor source, no need for external copyright terms.
It is an independent inspect-only fail-closed preflight, not a release
exporter or rights authority.

Twelve source-defined Python unit cases; at R44 SHA no actual Windows
execution claimed. Real consumer package, licensed art, owner sign-off,
device QA and Engine/LFX compatibility remain OPEN.

## R45 | M08-004 compatibility and rollback-diff donor-first analysis

BEFORE source implementation: inspected existing
`Tools/validate_manifest.py` exact `validate_manifest(doc)` and
`_safe_relative_path` contract, existing `factory/asset_catalog/catalog.py`
content-addressed/revision history, and `unity_package/Runtime/VisualAssetManifest.cs`
preview-only Unity manifest consumer. These provide reusable hardened
validation and hash semantics without introducing a third-party parser.
Reviewed Unity UI Extensions pinned `package.json` at blob
`6bb5e0dbfa6878c24df2e8d1b5e42e4c970c1b15` for a production
release-contract donor; REJECTED_REASON it describes a Unity UI package,
not interoperable Engine/LFX visual pack history or owner approvals.
**INTERNAL_REUSE** `Tools.validate_manifest.validate_manifest` directly
with Python stdlib `json`, `hashlib`, `re`, `pathlib` for only missing
read-only version/pin comparison and symbolic rollback-diff inspection.
No vendor source/import needed; no new asset-manifest standard fork.

Actual packaging, independently verified upstream contracts, source art
byte validation and full owner/device signoff remain NOT RUN / OPEN.

## R46 | Unity preview GUI is INTERNAL_REUSE of runtime manifest

PRE-CODE DONOR check: read the already vetted
`unity_package/Runtime/VisualAssetManifest.cs` concrete
`TryParsePreview` API and existing `VufProductionQueueWindow` read-only
TextAsset patterns. Compared pinned external Unity UI Extensions
`package.json` upstream commit
`d47f838ba918bbb9b26f242bd944940a711f525f`, blob
`6bb5e0dbfa6878c24df2e8d1b5e42e4c970c1b15`.
REJECTED_REASON: that UI package has no compatible 5-title Engine/LFX
asset-manifest reader and would add redundant UI code.
INTERNAL_REUSE: use exact existing `VisualAssetManifest.TryParsePreview`
with a small isolated Unity Editor diff/pin display component. No
external source/vendor or licensing change, no duplicate manifest
authority and no gameplay transaction code. Four Unity NUnit and
three Python contract tests authored, NOT actually executed at new SHA.

## R47 | M05-004/M08-003 actual Unity built-in SpriteAtlas V2 API adoption

MANDATORY PRE-CODE DONOR SEARCH: read local
`VufAtlasPreviewWindow`, Python `atlas_pipeline.py` and
`verify_candidates.py` to avoid rewriting existing image packers.
Inspected actual `Unity-Technologies/UnityCsReference` upstream
`Editor/Mono/2D/SpriteAtlas/SpriteAtlasAsset.bindings.cs` (blob
`9ebbbce17756251d89549df92dd55b2b0f1ed6fc`), and
`SpriteAtlasImporter.bindings.cs` (blob
`4f6d6a7c3b92a05d73e4b6874b197c08582dabbf`). Native
`SpriteAtlasAsset.Add/Save` and
`SpriteAtlasImporter.includeInBuild` signatures were confirmed
against Unity 6000.6 scripting docs
`https://docs.unity.com/en-us/engine/6000.6/script-reference/unityeditor/u2d/spriteatlasasset`.

**REJECTED_SOURCE_COPY**: UnityCsReference files explicitly carry
Unity Reference Only License, not redistribution permission to copy
their native bindings. No Unity proprietary source was copied.
**SDK_REUSE / MINIMAL ADAPTER**: call the real installed public Unity
Editor API directly from new EditorWindow
`VufSpriteAtlasV2Window.cs`; reuse existing Atlas Preview and
Sprite importer source discipline, no new atlas packing algorithm.
Create only NEW authoring candidate .spriteatlasv2 and explicitly
set `includeInBuild=false` to prevent accidental player inclusion.
Preserve original texture importers/assets untouched. Four real
EditMode and three Python source-only regression methods authored;
actual Unity Editor execution and mobile atlas QA still OPEN.

## 2026-10-18 | VUF-M06-003 responsive candidate preview pipeline

**Canonical task:** existing `VUF-M06-003` in root `TASKS.md`. This is
source provenance, NOT a task or milestone tracker. Baseline inspection:
VUF `main` SHA `da0413e0cf546317ee6ead2504095add0299c5aa`.
Existing local modules were inspected before authoring, and their declared
candidate-only policy was preserved.

**INTERNAL_REUSE** (VUF in-repository source, not third-party copied assets):

- `factory/image_processor/png_pipeline.py` (Git blob
  `f31dfefca03902a19ae227055f92067e06d6b2d4`): existing
  `encode_png/decode_png` CRC-checked PNG bytes, no new codec/provider.
- `factory/image_processor/representative_scene_pack.py`: existing
  `build_representative_pack`, 19 scene identifiers, 3-layer source
  manifest SHA/stage/ownership checks. Added 3× candidate layer scale to
  existing `SCALES` with no replacement scene-renderer rewrite.
- `unity_package/Editor/VufSceneLayerReviewWindow.cs`: existing read-only
  five-theme human Editor preview; narrowly allows true 3× 540×960 PNG
  manifest dimensions. It does NOT certify an actual Unity Editor run.
- `unity_package/Runtime/VufParallaxCanvasController.cs` (blob
  `0c9ce2eebe8454d47fb49a1db49bf35803d14acd`):
  existing view-only three-RectTransform parallax factors and reset, no
  Engine callbacks, no game-state or rewards authority.

**MINIMAL_ADAPTER / ORIGINAL_VUF_CODE**:
`factory/image_processor/scene_viewport_export.py` composes independent
SHA-verified layered PNGs into visual **review-only** portrait 9:16,
tall-phone 6:13 and tablet 3:4 cropped previews; nearest-neighbor image
cover preserves proportions; optional guide border is synthetic, never a
verified OS safe area or runnable UI. Output is in-memory by default or in
a NEW owner-chosen external folder; no source originals or existing files
are overwritten. Reused existing `scene_pack`/PNG codec and source/style
sha records; did not copy third-party code or visual assets.

**REJECTED_REASON:** installing another image rendering/Unity tween/atlas
framework would duplicate the existing VUF PNG and Unity view-only
components, add licensing and import complexity, and cannot furnish
human art-rights or device acceptance.

**Test status:** 9 Python source regression/negative methods authored in
`tests/test_scene_viewport_export.py`, one extra actual Unity EditMode
source test in `VufSceneLayerReviewEditModeTests.cs`, and existing Python
invalid-scale fixture corrected for newly permitted 3×. THESE NEW TESTS
HAVE NOT RUN IN THE OWNER WINDOWS/UNITY ENVIRONMENT. The previous
M05 Codex 361 Python PASS + 85 Unity EditMode PASS applies ONLY to
`cd9f9bfd6750ffeee850e700ac1c3691358b1f2b`, **not** this
source change. Test/GUI/physical-device, final art, rights and owner
approval remain separately open in VUF-M06-007 and M09.

## 2026-10-18 | VUF-M07-002 / M07-009 Sprite playback/atlas/replay consumer

**Source baseline:** `8922dc5647116c5fe58e4abdc00bb3182e9ef2ae`;
the only lifecycle tracker is root `TASKS.md`. Reviewed the existing
`VufSpriteClipBuilderWindow.cs` sprite ordering/AnimationClip implementation,
the genuine `VufFxClipExporterWindow.cs` asset-authoring path and the already
adopted `VufUiTween.cs` CanvasGroup transition primitive **before writing
new playback logic**. The five-profile `view_event_timeline.py` event/replay
schema and M07 owner review requirements were also inspected.

**INTERNAL_REUSE**, exact current blobs after implementation:
- `unity_package/Editor/VufSpriteClipBuilderWindow.cs`, blob
  `5aa133aa4b9313e80c3de30c438e6c983f7a2849`;
  existing Sprite selection, natural sprite ordering, Editor loop/ping-pong
  and real SpriteRenderer AnimationClip exporter were **retained**. Existing
  `BuildFrameSequence` now delegates to the SAME reusable view-only runtime
  sequence, preventing Editor vs Runtime playback order drift. Added human
  0.25/0.5/1/2x timeline speed controls, Sprite alpha checkerboard and
  zoom/clipping, normalized-pivot guide and PPU drift warnings. A deliberate
  owner button creates only a **DontSaveInEditor / DontSaveInBuild temporary**
  Scene SpriteRenderer preview; it is cleaned up on window close/source
  change. Optional alternative imported Sprite atlas can be swapped in the
  temporary preview only after runtime frame-geometry/normalized-pivot
  validation. No sprite importer/asset, existing scene GameObject or Engine
  code gets edited.
- `unity_package/Editor/VufFxClipExporterWindow.cs` blob
  `64b6e3ce980e672927101170a37aa29bfb1f4e1c`: existing candidate-only
  SpriteRenderer AnimationClip export implementation re-used unchanged.
- `unity_package/Runtime/VufUiTween.cs` blob
  `c86d73f1eb024539a00460c5258864c046e3bd44`: existing built-in UI
  tween and reduced-motion transition primitive deliberately preserved.

**SDK_REUSE / ORIGINAL_VUF_CODE:** `unity_package/Runtime/VufSpritePlaybackPreview.cs`
current blob `d4e6e6374ea434c3505b693c99019bb286f36812`
uses only public Unity `SpriteRenderer`, `Sprite`, `MonoBehaviour` and
bounded manual `Advance` APIs. Deterministic real SpriteRenderer
sprite assignments, loop/non-loop ping-pong, pause/replay/interrupt,
full/reduced-motion, import-safe atlas Sprite replacement and same-channel
visual-only event priority competition have **no** Engine/save/reward callbacks
or gameplay dependency. Invalid sprite/frame/priority/asset inputs reject
before modifying the current preview renderer. Renderer original Sprite is
restored on Clear/disable; no Editor-only APIs enter runtime.

**REJECTED_REASON:** do not add DOTween, reinvent exporter, copy
UnityCsReference reference-license native source or bring in additional
animation frameworks when current SDK and adopted VUF tween/FX clip modules
already supply needed functionality. No vendor art/files, license-bearing
code copy or paid services were used.

**Test authored:** `VufSpritePlaybackEditModeTests.cs` has 11 NUnit
methods covering real in-memory Unity SpriteRenderer binding, sequence and
timing, pause/resume, loop/ping-pong, replay/interrupt, alpha geometry/PPU
identity, safe atlas-swap, rejected corrupted inputs/priority and restoring
the previously attached Sprite on clear/disable. New Unity source/test
`.meta` GUIDs are registered with the existing
`Tools/validate_repo_structure.py` source-layout contract.
**NEW UNITY EDITMODE/GUI TESTS NOT RUN ON OWNER WINDOWS**. Prior C011
85/85 PASS occurred on M05 SHA `cd9f9bfd6750ffeee850e700ac1c3691358b1f2b`
and cannot validate this source. The manual owner GUI, real player/device/GPU,
actual Engine view-channel event parity, stable provider art/licence,
and final M07 milestone signoff remain **OPEN** in M07-006/009/013/014 and M09.


## 2026-10-18 | VUF-M07-005/006/009/013 | unified Editor Sprite/VFX manual review Studio

**Canonical work authority:** existing root TASKS.md VUF-M07-001..014. **No new lifecycle task** was opened. These notes preserve source provenance only.

**PRE-CODE donor-first review:** inspected actual in-repo implementations and blob SHA: 
- VufSpritePlaybackPreview.cs (Runtime view-only SpriteRenderer; original blob d4e6e6374ea434c3505b693c99019bb286f36812);
- VufVfxLabWindow.cs (five Unity ParticleSystem presets; blob 4a78a8d131cd310dde34b80145e095e229eda4d9);
- VufFxSheetPreviewWindow.cs (bounded geometry/manifest parser, procedural sheet manual frames; blob 698aba2ee6d6e81958561b7316b9716a009b6542);
- VufSpriteClipBuilderWindow.cs (existing imported-sprite parsing and genuine AnimationClip export; blob 5aa133aa4b9313e80c3de30c438e6c983f7a2849);
- VufUiTween.cs (VUF reduced-motion CanvasGroup primitive; blob c86d73f1eb024539a00460c5258864c046e3bd44);
- Python view_event_timeline.py (actual 5 theme x 14 source-pinned symbolic view event/priority/FX receipt ontology), special_skin_map.py (Engine SpecialActivationKind 5 names + 15 pair keys, only verified to pinned inspected Engine source).
- Already adopted Unity UI Extensions BSD-3-Clause donor components and all existing licence notices remain intact; no external vendor code or new art copied.

**INTERNAL_REUSE/SDK_REUSE:** New Editor-side files VufVisualEventCatalog.cs and VufUnifiedVisualStudioWindow.cs reuse Unity public EditorWindow/AssetDatabase read operations, Unity SpriteRenderer/ParticleSystem/Profiler, the existing VF-05/06 FX sheet parser, five particle presets, and the existing M07 runtime playback. They provide a coherent *manual candidate-only owner review* workspace with theme/event/special/FX selection, temporary nonpersistent Scene SpriteRenderer and particle preview, parallel Sprite/FX frame scrub, 0.25/0.5/1/2x, reduced-motion/muted LOG-ONLY cues, source-validated Sprite/FX PNG metadata/SHA, atlas geometry-preserving A/B comparison, viewport aspect/synthetic safe border and approximate editor-only resource diagnostics. A review receipt can be copied or exported only as a NEW JSON file outside the Unity checkout; it has hardcoded FALSE for actual device/GPU owner/right/final Engine release approval, score/save/rewards/monetization authority. Source and importer GUIDs are left untouched; existing source/prefab/scene files are not created by the studio. Added 3 immutable Unity .meta GUID and required them in Tools/validate_repo_structure.py.

**REJECTED_REASON:** adding DOTween, a fresh separate VFX framework, copying Unity reference-only internals or donor art would duplicate existing installed/locally licensed VUF rendering code and would not supply real Engine/game/owner/device acceptance. No external redistribution or paid CI dependency was created.

**SOURCE TESTS AUTHORED, NOT ACTUALLY EXECUTED**: six Unity EditMode methods in VufUnifiedVisualStudioEditModeTests.cs validate 5x14 semantics, 5 upstream special/15 unordered combo visual keys, strict negative spoof checks, cue log-only/mute and three synthetic phone/tablet framing constraints. Five additional Python source consistency tests in tests/test_m07_unified_visual_catalog.py compare the new Unity declarative source catalog with Python view_event_timeline.py event/channel/priority/duration/FX preset data and fail on source drift, unapproved source rights or forbidden game mutations. The previously authored 11 real SpriteRenderer Unity tests are retained. Source braces, GitHub file/metadata presence and fixed TASKS IDs were inspected but **REAL WIN UNITY TESTS/GUI OWNER ACCEPTANCE NOT RUN**. The prior M05 Python 361/9 SKIP + Unity 85/85 results are from SHA cd9f9bfd6750ffeee850e700ac1c3691358b1f2b and cannot validate M07 changes.

**Single M07 Codex source+Unity test gate**: Existing TASKS.md task VUF-M07-014; the unique full-milestone executable prompt is at https://docs.google.com/document/d/1WyQbMfpP696GvSZ2B1PeSatvLuc2xnENN8_0hGhSypk/edit. No new task IDs, no separate lifecycle tracker.

## 2026-10-18 | VUF-M08-001/003/006 | external TEST_ONLY imported pack preview

**Canonical tasks:** existing root TASKS.md `VUF-M08-001`, `VUF-M08-003`, `VUF-M08-006` (left OPEN for actual Engine/LFX, Unity GUI/device and packaging acceptance). No new task IDs. **Avoid carrying an untested M07 source change as production QA**: M07 remains queued for ONE owner-local Codex full-milestone suite under existing `VUF-M07-014`.

**PRE-CODE existing-module reuse:** inspected `unity_package/Runtime/VisualAssetManifest.cs` (actual preview schema v1; `stage=TEST_ONLY`, five profile namespaces, immutable `asset_id/path/sha256` fields), `unity_package/Editor/VufQaStudioWindow.cs` (existing read-only candidate QA), `VufScreenShellBuilderWindow.cs` and current uGUI + Unity local UPM manifest and source GUID validator. There is no justification yet to choose UI Toolkit or ship mobile Addressables ahead of Unity safe-area and original-art acceptance.

**MINIMAL_ADAPTER / UNITY_SDK_REUSE:** `unity_package/Editor/VufExternalPackSandboxWindow.cs` adds one read-only Editor tool for manually imported `Assets/` copies: apply existing VisualAssetManifest.TryParsePreview, verify allowed TEST_ONLY profile and image name/path, reject duplicate namespace/asset/path and art-rights shipping spoof, hash every actual imported PNG byte with SHA256, render side-by-side visually inspected profile/theme asset images. Switching a preview never writes source TextureImporters, asset GUIds, original VUF or Engine files, game score/save state or runtime game content. Add stable Unity `.meta` GUIDs and `Tools/validate_repo_structure.py` source gate. Tests authored: `unity_package/Tests/Editor/VufExternalPackSandboxEditModeTests.cs` seven NUnit cases for 5 profiles, 2 image digests, duplicate/invalid IDs and paths, traversal, forged rights and changed source. These tests have NOT been run in owner's Unity Editor.

**REJECTED_REASON:** Avoid copying more UI/asset framework code, installing paid or external Unity plugins and inventing final ENG-M12-010 consumer/runtime contracts before independently pinning Engine and LevelFactory final releases. This is an *offline source candidate browser only*, NOT asset-pack shipping, actual animated consumer, phone GPU acceptance, or visual owner signoff. Previous Codex M05 tests on `cd9f9bfd` do not verify this new M08 code.

## 2026-10-18 | VUF-M08 comprehensive source delivery and no-self-approval

**Only task authority** is original root TASKS.md M08-001..010. No new
lifecycle, test-subtask or R/C task IDs were introduced. This is an internal
licence/reuse ledger, not project progress tracker.

**PRE-CODE inspected actual in-repo existing candidates/donors:**
- Unity `VisualAssetManifest.TryParsePreview` (strict TEST_ONLY schema),
  `VufExternalPackSandboxWindow` (existing SHA-verifying imported copies),
  `VufScreenShellBuilderWindow.BuildCandidateHierarchy` (28 Coral contract
  IDs; 5 draft visual styles; uGUI Canvas/disabled Button),
  `VufReviewStateCatalog` (8 synthetic states and en/tr/stress copy),
  `VufResponsiveGeometry` (synthetic safe area/anchors),
  `VufSafeAreaFitter`, `VufUiTween` and existing M07
  `VufVisualEventCatalog` (view-only 14-event namespace). No source consumer
  game or ENGINE/LFX repo changed or even imported here.
- Python `representative_scene_pack.build_representative_pack` (existing
  mathematical 3-layer scenes); `sample_sprite_pack.build_sample_pack` (M05
  R52 38 geometrical sprite candidates/real source receipt);
  `procedural_fx_sheet.build_candidate` (five known VFX frame sheets and
  reduced-motion stills); `atlas_pipeline.create_atlas_candidate` (actual
  VF04 original pixel shelf packing and UV/extrusion); the existing
  `atlas_candidate_audit.audit_candidate` and `png_pipeline.decode_png`.
  No Pillow/Photoshop, new vendor FX library, donor artwork or paid tooling
  added.

**MINIMAL_ADAPTER / ORIGINAL_VUF_CODE:**
- `factory/asset_packaging/candidate_pack.py` bundles only one of 5
  source-pinned theme namespaces, with separate 1x independent RGBA scene
  layers, 38 R52 mathematical sprite prototypes, five local VF06 FX
  animation/still pairs and their receipts, en/tr DRAFT locales, actual VF04
  SOURCE atlas, and immutable full SHA256/file receipt. All writes are
  explicitly requested to a NEW folder **outside** checkout. Unity
  JsonUtility supports its typed `file_entries` receipt array alongside
  Python `file_sha256` dictionary. Emitted manifest is `TEST_ONLY` with
  unknown/unpinned final ENG/LFX release, and no original source rights or
  actual game transactions. Release impossible by design.
- `factory/asset_packaging/verify_offline_bundle.py` independent read-only
  receipt/SHA/PNG/VF04 atlas revalidator. No writing to original artwork or
  Git source. `tests/test_m08_candidate_pack.py` contains eight new
  deterministic/negative test methods, including actual one-folder export and
  corrupted copy rejection; `tests/test_m08_unity_source_parity.py` adds four
  static Python↔Unity source parity/authority checks.
- `unity_package/Editor/VufCandidatePackImporterWindow.cs` explicitly
  imports verified TEST_ONLY source **copies**, not originals, solely into
  Unity's Editor-only Assets subtree, with exact file whitelist, symlink,
  traversal, digest, no-overwrite and 128MiB safety bounds. The .gitignore
  excludes `Assets/Editor/VUF_ReviewImports/` to avoid source pollution.
- `VufInteractiveUiReviewWindow.cs` reuses existing REAL uGUI input components,
  policy-locked original candidate prefabs and existing native layout/
  safe-area/tween modules as nonpersistent, owner-invoked GUI **review** only.
  One explicitly enabled temporary test action writes ONLY a local inspector
  text log; no Engine business action. Does not falsify five separate games'
  approved layout contracts.
- `VufExternalPackViewStage.cs` and enhancements to
  `VufExternalPackSandboxWindow.cs` stage a SHA rechecked imported PNG in
  an actual TEMP Scene SpriteRenderer, with candidate 14-event view label,
  5-theme A/B browse, validated synthetic en/tr locale and inert absent-
  locale fallback. The existing M07 Unified FX Studio is reusable separately;
  no saved original Scenes or runtime gameplay update performed.
- Unity `.meta` GUIDs and existing `Tools/validate_repo_structure.py`
  source/module .meta coverage were extended, not replaced.

**REJECTED_REASON:** no unjustified new UGUI/UIToolkit fork, game-rule SDK,
cloud Addressables/mobile billing or reference-licence UnityCsReference code
copy: the installed uGUI, existing original candidate builder, original
mathematical VUF assets and existing VF04/VF06 Python source cover **current
offline Editor candidate needs**. Optional production Addressables/cloud
streaming cannot be approved before final Engine/LFX runtime and actual
device/network tests. No source assumes owner art-rights or final marketing
approval.

**VALIDATION STATUS AT PUBLICATION:** all newly added Python unittest,
C# EditMode test, importer/editor UI and pack verification **SOURCE AUTHORED
ONLY; NOT EXECUTED on the owner's actual Windows Unity 6000.6.5f1 yet**.
The previously confirmed Codex M07 Python 404 PASS/9 OS symlink SKIP,
Unity 126/126 EditMode PASS is tied ONLY to tested SHA
`469233cccb1ad533c6b32cd946e915e98bc22543`. New M08 source is a
different SHA and requires a fresh SINGLE owner-local
VUF-M08-010 final-SHA whole-milestone test. Manual uGUI, original art
licensing, real ENG-M12/LFX neutral consumer parity, mobile GPU/device and
production player build acceptance remain OPEN. The unique whole-M08 Codex
prompt is a native Google Doc:
https://docs.google.com/document/d/19mAHGyJM3978LW9S5YBYCw_BnLTv8-kUu7w0M92tXEA/edit

## 2026-10-18 | Existing M09-001/002/003/004/006/012 milestone source batch

**Only canonical tracker:** root TASKS.md existing VUF-M09-001..017.
These provenance notes are never task IDs or milestone approvals.

**DONOR-FIRST source inspection performed before writing M09:**
existing Unity VufQaStudioWindow, VufReadinessBoardWindow,
VufScreenCatalog.LoadScreens (28 CORAL-ONLY contract IDs),
VufScreenCatalog.LoadStyle (five DRAFT palettes),
VufScreenShellBuilderWindow.BuildCandidateHierarchy (real local uGUI
Canvas/Text/disabled Button and zero game actions),
VufReviewStateCatalog.Apply (8 MOCK states/en-tr-stress),
VufResponsiveGeometry.Analyze (5 synthetic device safe-area/anchors),
VufTypographyAudit.Analyze (actual Unity text generation/contrast risk),
VufInteractiveUiReviewWindow (temporary test-tap),
VufUiTween (deterministic CanvasGroup reduced-motion primitive),
M07 VufUnifiedVisualStudioWindow (real imported SpriteRenderer/ParticleSystem
symbolic cue playback; existing frame stepping),
M06 VufSceneLayerReviewWindow (layer/parallax),
M08 VufExternalPackSandboxWindow (imported TEST_ONLY pack), and
VufReadinessBoardWindow (release rights vs technical QA separation).
Existing Python VF04 mathematically authored silhouette_kit, PNG CRC decoder
and M08 candidate pack/independent bundle verification were also inspected.
Existing BSD-3-Clause donor modules and preserved notices remain untouched.

**MINIMAL_ADAPTER / SDK_REUSE original VUF code:**
- VufM09MatrixAudit.cs: candidate matrix five DRAFT styles × 28 CORAL-only
  draft screens × 8 MOCK states × 3 review locales × five synthetic phone/
  tablet/landscape presets. A 16,800-row *source* inventory is not 16,800
  actual rendered/screenshots; batches are 1..32 real transient Unity
  uGUI candidate instantiations. Four nonCoral themes explicitly show
  N_A_FOREIGN_GAME_USING_CORAL_DRAFT_CONTRACT. Policy-disabled
  screens never get game business/online feature enablement.
- VufM09RenderCapture.cs: original temporary Unity
  Camera/RenderTexture/readPixels->EncodeToPNG drawing of a disposable
  candidate Canvas, guarded to reject persistent/unknown source objects.
  Capture metadata says actual EDITOR preview only, never an iOS/Android
  screenshot or owner-accepted art. Canvas camera/render mode and temporary
  render targets are restored/disposed. GUI actual capture NOT RUN.
- VufM09OwnerVisualQaWindow.cs: manual owner Studio orchestrates existing
  28-screen component builder, state, responsive geometry, font fit,
  view-only test tap, VufUiTween single-step, A/B actual Editor PNG snapshot,
  8 actual Editor-tween PNG frames (NO MP4), SHA-256 receipt and safe
  create-only EXTERNAL output. Links directly to existing M07/M06/M08
  render/FX/layer/import browsers, without new competing framework.
  Mock level/seed/cue selectors DO NOT connect to Engine rules.
  All release/device/rights/owner approval fields remain FALSE.
- factory/qa/m09_review_inventory.py: read exact existing original Coral
  schema+Style Bible bytes, enumerate immutable 16,800 SOURCE matrix,
  N/A and policy gates with SHA pins.
- factory/qa/m09_pixel_diff.py: reuse existing VUF PNG codec for original
  source SHA pin, RGBA/alpha and semitransparent edge candidates, nearest
  source 1x/2x/3x comparisons, frame-by-frame animation candidate diff and
  source rights receipt fields. No legal/ownership approval inferred.
- factory/qa/m09_accessibility_candidates.py: reuse six VF04 mathematically
  distinct alpha shapes and five DRAFT color palette contrast checks.
  No WCAG, font-fit, physical-touch or disability-use certificate.
- Tools/vuf_m09_windows_viewer.py: optional Python stdlib Tkinter viewer
  for original SHA-checked M08 TEST_ONLY pack source PNGs, A/B and 4x2 FX
  source frame crop; NOT a live Unity Game view, real game FPS or video.
  Source receipt export create-only/owner-only to outside Git.

**REJECTED_REASON:** installing duplicate Tween/FX/UI engines or unsafe GUI
capture packages would duplicate already adopted original Unity modules;
third-party art licensing and "lookalike" original ownership cannot be
determined by a candidate CRC/hash or generated schematic prototype.
Production gameplay, Addressables, monetization, final Engine/LFX replay,
physical iOS/Android/GPU and commissioned art remain separate gates.
No copied donor source or original game assets were used in this batch.

**CURRENT TEST STATUS:** Added authored (NOT RUN) eight+ new Unity
EditMode matrix/render-capture contract tests, Python source inventory,
RGBA/art provenance/scale/frame, palette/silhouette, Windows Tk viewer
pure contract and cross-language source-parity tests. C# source braces and
Unity .meta GUID path registration were checked only syntactically.
Previous owner-local M08 Codex Python 416 PASS/9 Windows symlink SKIP,
Unity 140/140 PASS applies ONLY to earlier
`de5b8cc1b0938294d8c4aa1f5405240d29817d74`, NOT this new source.
One M09 full-milestone Codex/Windows local QA source prompt is
https://docs.google.com/document/d/1J_Spo9GLxfiMdBEqRK8xjoJ_aACGSS4NlhZv-thgiGA/edit
under existing task VUF-M09-017. Owner real interactive GUI,
actual screenshot/frame exports, original/licensed art rights and source
fonts, physical device/GPU and final Engine/LFX remain OPEN.

## 2026-10-18 | M10 source batch: 5-theme manual candidate routes and guarded pack budgets

**Canonical authority:** existing root TASKS.md M10-001..007 only. No new VUF
task IDs; actual Engine/LFX cross-repo releases remain an OPEN dependency.

**DONOR-FIRST / SOURCE-READ:** before M10 source authoring, read existing
VufScreenCatalog/Coral schema 28 draft IDs, actual disabled-button
VufScreenShellBuilderWindow, VufReviewStateCatalog, VufResponsiveGeometry,
VufTypographyAudit, VufUiTween, M07 VisualEventCatalog/Sprite/VFX manual
playback, M08 External Pack Sandbox/VisualAssetManifest and M09 QA real
Editor RenderTexture/Candidate geometry. Reused M08 actual SHA-indexed VF04
offline bundle validator and existing VUF PNG codec without new art or
external code. Existing BSD-3-Clause Unity UI Extensions licence preserved.
Read-only connected GitHub Engine main observed SHA
`e84d65ab712dddc534cbdb3a30cfe2d7930cea8a` with
ENG-M11 11/14 accepted and ENG-M12 gated; LFX main observed
`dad072e519276334bd1438fadf7be58f741d5579` with M08 preview and
ENG-M24 actual replay dependency not accepted. Neither source HEAD is a
shipping ABI or independent WIN replay proof.

**INTERNAL_REUSE / ORIGINAL_VUF_ADAPTER:** added
`factory/integration/m10_neutral_slice.py` and three Python M10 test
modules, `factory/integration/m10_pack_budget.py`, and Unity Editor
`VufM10VerticalSliceStudio.cs` + 8 NUnit and GUIDs. Routes are candidate
presentations only (nine per title, Coral additional three reef/aquarium/region
draft source pages). Source has disabled Buttons and transient uGUI; level and
seed are MOCK, no board solver, game score, purchases, save/rewards or
difficulty. Other four themes use borrowed Coral source screen keys explicitly
N/A as game-approved title UI. Source-bound opaque LFX data may have SHA
verified but not falsely parsed as a final level schema or claimed WIN.
Immutable source pseudo-reference hash can demonstrate only that switching
draft visual theme revision does not mutate *that synthetic reference*.
It does NOT prove identical gameplay for real Engine sessions.
Budget analyzer hashes actual M08 exported source PNG, decodes source
dimensions and estimates theoretical RGBA32 memory. It cannot replace
real BuildPipeline/player binary or physical mobile GPU/frame budget.

**REJECTED_REASON:** do not invent a future Engine Neutral Replay API,
pick an arbitrary prototype LevelFactory level ID or game rule resolver,
fork entire external game/engine repositories, or copy donor screenshots
as original licensed game art. Need exact accepted real ENG-M12/ENG-M24
neutral consumer, genuine LFX representative level/seed events, Unity
PlayMode and owner rights before production vertical slices. Do not
claim M10 milestone complete based on Editor TEST_ONLY preview.

**VALIDATION:** new Python/C# M10 source and NUnit/Python regression tests
AUTHORED, NOT RUN on this new source SHA; read-only GitHub presence and
C# basic balanced-delimiter scan only. Previous full M09 Codex actual
Python 450 PASS/9 Windows symlink SKIP; Unity 149/149 EditMode PASS
on `1c8d99b248bd3462fce80e78ac30760c8b9d55a2` is historical.
Existing M10-007 full-milestone one-shot Codex prompt (technical tests and
explicit upstream real-gate audit):
https://docs.google.com/document/d/1zCp8w4u7OJyiyca-I4IWwKYKB4jB0T_1w-hY6iDuJa0/edit

## 2026-10-19 | M11-001..006 entire milestone candidate source batch

**SINGLE canonical tracker** remains root TASKS.md (137 contiguous IDs).
No new VUF task IDs or parallel tracker files. No final v1 shipping freeze
or human legal/owner approval is inferred by M11 source implementation.

**Pre-code inspected actual original VUF code:**
`factory/asset_packaging/candidate_pack.py` (M08 mathematical
TEST_ONLY export and VF04 real atlas, typed Unity array/source receipts);
`factory/asset_packaging/verify_offline_bundle.py` (independent actual
source PNG/locale/vFX/VF04 pack bytes audit);
`unity_package/Editor/VufCandidatePackImporterWindow.cs` (explicit
NEW Unity Editor-only source copy, all SHA, deny secret/raw assets);
`VufExternalPackSandboxWindow.cs` (view-only imported TEST_ONLY SHA/A-B),
`VufReadinessBoardWindow.cs` (legal/owner/source quality gates),
and M09/M10 mock screen/win/replay owner Studio. Existing source
package `com.match3.visual-factory` remains pre-v1 0.1.0.

**MINIMAL_ADAPTER / SOURCE-ONLY review v1**
- `factory/release/m11_candidate_release.py`: original deterministic
M08 source path export is REUSED; creates canonical SHA256 content-identity
M11 manifest with observed (NOT ACCEPTED) precise Git 40-hex
Engine/LFX provenance, 100%-source artifact raw SHA whitelist, no extra
files, symlinks/junctions/secrets/tests/Editor/reference art, MAX byte
budget. Export and consumer review import are NEW external dirs ONLY,
never overwrite previous candidate or original artwork. A rollback
creates a *NEW verified copy of old reviewed source*, never changes
running game's active revision or deletes current consumer. Full M08
receipt and VF04 source hash revalidated; independent legal/owner/Engine
ABI/player/phone statuses remain explicitly FALSE.
- `factory/release/m11_game_handoff.py`: produces a G01/G02/G09/G11
four-consumer original-ID review contract, with title/profile mapping
explicitly UNCONFIRMED in this VUF repo (no guess of which game maps
to each ID), all original creator/font/licence and Engine/LFX owner
release signoffs FALSE, create-only JSON outside source checkout.
- `unity_package/Editor/VufM11CandidateReleaseReviewWindow.cs`:
read-only Unity window showing externally supplied observed Git pins
and recalculating all original referenced file SHA. It is NOT a
Python canonical content-ID/full M08 receipt audit or a replacement
for the existing Unity M08 Editor-only importer/rights board.
- `docs/M11_RELEASE_CANDIDATE_AND_HANDOFF.md` explains operator
review-only workflow, exact four game target IDs and every gated
acceptance separately; **no game v1 release called or executed**.

**REJECTED_REASON**: do not fabricate accepted released Engine M12/
LevelFactory M24 neutral replay, owner art/font licensed originals,
signed independent legal review, game-specific title mappings or
production rollout/rollback authority. No new external paid SDK or
cloud service; donor original source license notices untouched.

**Source QA authored, NOT EXECUTED ON NEW SHA**:
11 Python source/real external candidate export, import, rollback,
path, PIN, corruption and rights negative test methods in
`tests/test_m11_candidate_release.py`; 4 handoff/Python→Unity parity
tests in `tests/test_m11_handoff_and_parity.py`; 5 real Unity EditMode
source NUnit tests in
`unity_package/Tests/Editor/VufM11CandidateReleaseEditModeTests.cs`
with stable .meta GUID/structure requirements. The only verified
owner-local M10 reference remains Python 454 PASS/9 Windows
symlink SKIP, Unity 157/157 EditMode PASS at GitHub SHA
`23b087d1d91cd26921994c5b19d42dadea98be6d`.
M11 tests, actual Unity GUI, production package scanning, owner
creative original art/rights, full Engine LFX game parity, physical
devices and signed M11 handoff are **NOT RUN / OPEN**.
One M11-006 full-milestone Codex prompt created in Drive 01_PROMPTS:
https://docs.google.com/document/d/1mTXbEaLazWHhaF-j58nFB31Z6meB3oBcNWT_ScS8e0g/edit
