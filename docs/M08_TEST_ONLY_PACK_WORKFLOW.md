# M08 | TEST_ONLY Offline Visual Pack and UI Preview Workflow

**Scope:** existing VUF-M08-001/002/003/006/010 in root TASKS.md. This is an
operator guide and source inventory, **not** a separate task tracker, new task ID
or a source of authorization to approve or ship original art.

## M08 source code delivered

- `factory/asset_packaging/candidate_pack.py`: assembles a *single selected*
  game theme's original mathematical R52 38 prototype sprites, 3 independent
  world/chapter/gameplay environment layers (plus 4 Coral specialized scene
  identifiers), 5 VF06 VFX animated PNG sheets and 5 reduced-motion stills,
  draft English/Turkish review copy, and precise `TEST_ONLY` source manifests
  completely offline. Its export calls the **existing VF04 real pixel atlas
  packer**, writes **only to a NEW external folder**, and emits
  `candidate_pack_receipt.json` SHA-256 coverage for all emitted files. It
  does NOT invent owner artwork, create a Unity SpriteAtlas V2, configure
  production imports or certify Engine/LFX interoperability.
- `factory/asset_packaging/verify_offline_bundle.py`: independently reads
  exported files and validates each SHA, VF04 atlas geometry and candidate
  status without creating or modifying any source file.
- `unity_package/Editor/VufCandidatePackImporterWindow.cs`: explicit
  new-folder, full-file-hash-verified import into
  `Assets/Editor/VUF_ReviewImports/` ONLY. This is auto-excluded by Unity
  from normal player builds and ignored by Git. Existing assets are never
  overwritten, and input symlinks/traversal/approved rights claims are refused.
- `unity_package/Editor/VufExternalPackSandboxWindow.cs`: checks EVERY
  imported PNG source SHA, has safe A/B pack comparison, selectable draft
  locale with inert offline fallback, 5 game namespaces, a temporary real
  Unity SpriteRenderer stage and a link to the existing M07 Unified Visual
  Studio. Stage labels use M07's five-profile/14-event view-only keys, NOT
  final Engine events.
- `unity_package/Editor/VufInteractiveUiReviewWindow.cs`: reuses original
  VUF 28-screen builder and exact Coral screen IDs, five draft visual styles,
  synthetic phone/tablet safe-area bounds, existing review state/language
  text, CanvasGroup/VufUiTween, real uGUI Button test-only local click logs,
  z-order/anchors/touch rectangles. This does NOT create real business action
  bindings or final designs for all five games. Game/policy-locked actions
  never get enabled; all generated GameObjects carry DontSave flags.
- `VufExternalPackViewStage.cs`: actual Unity SpriteRenderer-only preview of
  a previously verified copied Texture2D, with immutable source and temp
  cleanup, **not** a live external ENG-M12 runtime consumer.

## Safe operator workflow on Windows (only when ready to test)

Export a new mathematical candidate example outside the Git workspace:

```powershell
python -B -m factory.asset_packaging.candidate_pack --profile Coral_Rescue --new-external-dir "C:\VUF_TestCandidates\Coral_Review_New"
python -B -m factory.asset_packaging.verify_offline_bundle --pack-dir "C:\VUF_TestCandidates\Coral_Review_New"
```

Choose a genuinely new folder; neither command is run by this documentation.
The verifier must report TEST_ONLY, correct file counts and `release_allowed:
false`. Candidate generated output is NOT an endorsed production art pack.

In a local Unity 6000.6.5f1 Editor project with this package installed, open
**Tools > MATCH3 > Import External TEST_ONLY Pack Copies**. Select that external
folder's `candidate_pack_receipt.json`, then press **Validate ALL source hashes
and import NEW copies**. The importer copies into an Editor-only Assets subtree
and opens the sandbox to browse `visual_manifest.json`.

For real disposable UI layout and local test action logs, open **Tools > MATCH3 >
Interactive UI Layout & State Review**. For FX/sprite frame scrubbing with
existing imported sprite copies, use **Tools > MATCH3 > Unified Sprite and VFX
Review Studio**.

## Acceptance limitations

All output remains `TEST_ONLY` or `CANDIDATE_NOT_OWNER_APPROVED`. Every screen
other than the original 28 Coral schema IDs is still without a separately
owner-approved screen/content taxonomy. Current state/locales are synthetic,
not shipped localization or game state. No Addressables cloud service is
necessary for the **offline candidate fallback**, but the final game bundling
and optional Addressables path need independent owner/real Unity acceptance.
M08-006 cannot be fully signed off until exact Engine and Level Factory
source SHAs, neutral replay API and cross-repo feature gates are independently
closed. Neither a 126/126 M07 EditMode pass nor source-authored M08 tests
proves M08 Unity GUI/device/player performance.

The next Codex M08 single-milestone test must cover the **entire M08** source
state, full Python+Unity suites at exact FINAL SHA, new candidate export/
offline importer/actual pixel/locale/interactive uGUI negative tests, and
real GUI/file/pack import evidence when interactive Unity is available. Preserve
the four M07 manual/device/Engine/owner gates without inventing an acceptance.
