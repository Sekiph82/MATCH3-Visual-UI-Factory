# Three-factory visual source integration | owner review guide

This is documentation, NOT a task tracker or a completed game release.
Only original VUF root TASKS.md records acceptance.

## Exact existing donor contracts

**Level Factory:** LevelDraftJson.Parse/Serialize provides real versioned
draft cells, layer/row/column, goals, seed and content/obstacle durability.
The new LevelDraftVisualHandoff exports a NEW external folder with both
canonical original LevelDraft bytes and a SHA-bound LFXV1 JSON projection.
Unity menu: Tools > MATCH3 Factory > Export Real LFXV1 Visual Review Pair.
A genuine LFX source record is not proof of accepted Engine M24 WIN/replay.

**MATCH3 Engine:** Existing PresentationEvent has seven distinct kinds,
monotonic sequence, source key, intensity and sorted positions. New M3P1
codec/collector exports actual caller-supplied PresentationEvent records
with UTF-8/Base64 IDs and a checksum. The host must explicitly call
NeutralVisualReceiptEditorExport.Begin(actualProfile) and
NeutralVisualReceiptEditorExport.Observe(actualEngineEvent) during a REAL
Engine game session, then use Tools > MATCH3 Engine >
Export REAL M3P1 Events for VUF Review. It is not auto-subscribed
to every Engine run. The checksum is integrity, not origin authentication,
final deterministic replay or a signed production source.

**VUF:** factory/integration/cross_factory_contract.py validates both
source wire formats, exact five-title profile, original LFX source SHA,
Engine event coordinates within original LFX board geometry, seven
kind ordinals, stage/license booleans and fails closed on altered data.
Engine Swap is N/A as M07 has no approved corresponding animation cue.
No match solver, user score or reward authority is invented.

## Actual interactive Unity Editor studio

Open Tools > MATCH3 > Three Factory Real Data and Visual Events.
Select canonical LFX LevelDraft JSON and its matching LFXV1 handoff JSON,
plus optionally REAL M3P1 typed Engine presentation events. Source hashes
are checked before the Studio creates a real temporary Unity uGUI
grid of source content IDs/obstacles and holes. Choose an original layer,
inspect original goals and seed, step actual typed presentation events
and highlight precise source board coordinates. Manual event controls
offer previous/next/reset and M07-derived view pacing 0.25x, 0.5x, 1x,
2x with reduced-motion manual-only mode. This is NOT actual Engine event
timing, gameplay, score/WIN, device GPU or certified accessibility.

The selected Engine view-only event can open the existing real M07
Sprite/VFX Studio on its matching source-pinned cue; previously imported
Sprite/FX objects are explicitly cleared to avoid cross-theme art
leaking between game profiles.

## Exact SHA-bound owner-selected prototype sprites

M08 Import External TEST_ONLY Pack Copies now retains its original
candidate_pack_receipt.json in NEW copies under
Assets/Editor/VUF_ReviewImports. Existing older imports lack that
receipt and intentionally need a fresh explicit user import.

In the Three Factory Studio select the imported M08 manifest. Click
Verify imported full M08 TEST_ONLY source SHA. This checks the original
receipt, every listed raw source SHA, imported VisualAssetManifest,
namespace, and prototype art REVIEW_PENDING status. Choose an original
LFX contentId, obstacleId or specialId in the source dropdown and
choose an exact verified M08 asset ID under sprites/. Click Bind EXACT
selected ID to disposable PNG. Art is applied only to in-memory source
grid Images in the selected LFX layer. No automatic guessed asset
mapping, no scene/prefab writes, no legal licence or runtime player
asset import. Temporary sprites are destroyed on reload/close.

## Python source visual plan and CLI

factory/integration/three_factory_visual_plan.py retains source
layer/row/column, goals, obstacles, original content IDs and an
ordered, view-only cue sequence. Every event has changesBoard=false,
awardsCoins=false and settledGameSnapshotProven=false. Optional external
M08 visual pack must be independently SHA-verified, TEST_ONLY and
same game profile. Explicit art mapping is optional and must refer to
existing source content IDs and exact SHA-listed source art asset IDs.

Use Tools.verify_three_factory_handoff as the read-only validator:
python -B -m Tools.verify_three_factory_handoff --lfx-canonical <real_leveldraft_v1_canonical.json> --lfx-view <matching_LFXV1_visual_handoff.json> --engine-events <REAL_engine_M3P1.txt>

For a NEW external review plan, add optional arguments
--vuf-test-pack <real_TEST_ONLY_pack_directory>
--explicit-test-art-map <existing_owner_ID_map.json>
--new-view-plan <NEW_absolute_external_review_plan.json>

Nothing overwrites original sources or grants production authority.

## Testing and acceptance

Three new repo feature sets have been COMMITTED to GitHub but NOT YET
TESTED in local Unity 6000.6.5f1 or complete Python regression.
New VUF code adds 10 existing Python source-contract checks, 6
visual-plan and 4 source parity checks, plus 9 Editor NUnit tests.
Engine/LFX have additional source NUnit tests, also not yet rerun.
Previous VUF Python 478 PASS/9 Windows symlink SKIP and Unity EditMode
162/162 apply ONLY to the earlier M11 tested source, NOT these changes.

Still OPEN: explicit real Engine host event forwarding, Engine settled
replay/score/WIN and LFX ENG-M24 accepted ABI, five game playable levels,
independent Game Center/Play Games, licensed owner original art/fonts,
runtime Sprite/FX, actual player build/phone GPU, physical device and
owner legal/art/GUI signoff. Review-only images and source checks do not
complete those milestones or change game saves or difficulty.

## Latest owner-visible source-grid Editor screenshot

VufThreeFactoryGridCapture.cs adds a STRICTLY NONPERSISTENT Unity
Camera/RenderTexture/PNG capture gate for exactly the original temporary
LFXV1 grid object, preserving canvas render settings and destroying
temporary GPU objects. It deliberately does NOT bypass the older M09
Coral-screen CandidateMarker capture gate.

In Three Factory Real Data and Visual Events, click RENDER actual
disposable Unity Editor PNG after loading a source board and optional
verified art/event. An in-memory actual Editor image appears. The owner
can click Export NEW Editor PNG and SHA review receipt to create a
**new external PNG + JSON only**; it records original LevelDraft source
SHA, optional typed Engine M3P1 receipt SHA, inspected M08 imported
manifest SHA, source layer and selected event index, with explicit
REAL Unity Editor pixels TRUE but production art/owner/gameplay/WIN/
physical GPU/device/shipping flags FALSE. Rebuilding a level, switching
layers, stepping events or changing art invalidates the captured image.
No tests may claim a screenshot was captured in -nographics batchmode.

Related new test counts: 10 + 6 + 5 = 21 authored Python contract/
plan/source-parity checks; 10 Unity Editor source NUnit methods.
Full owner-local Python/Unity regression and actual GUI capture on
latest SHA remain NOT RUN. Existing 137 task IDs remain frozen.
