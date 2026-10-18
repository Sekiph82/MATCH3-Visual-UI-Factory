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
