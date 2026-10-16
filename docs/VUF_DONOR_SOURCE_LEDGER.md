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
