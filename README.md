# MATCH3 Visual & UI Factory

**Five Match3 games, one shared Unity visual production system.** Current state: **VUF-M00 foundation under active development, not audited or production-ready.**

Games: `Coral_Rescue`, `Garage_Legends`, `Dino_Islands`, `The_Fractured_Realms`, `Wonder_Pop`.

## What works at source level today

- Unity 6000.6.5f1 authoring shell and **local UPM** shared package at `unity_package/`, referenced by `Packages/manifest.json` as `file:../unity_package`.
- **Tools > MATCH3 > Visual Factory Dashboard** lists the ten VF modules with truthful feature support status.
- **Tools > MATCH3 > Visual & UI Factory Studio** manually previews imported original/licensed Texture2D horizontal sprite strips, frame stepping/speed, five profile and eight state selectors, simulated phone/tablet ratio overlays. Animation/VFX editing, real UI screens, integration and export are **NOT IMPLEMENTED**.
- Five original, editable **DRAFT** style profiles in `factory/visual_director/style_profiles.v1.json`; owner creative approval remains open.
- Stable **28-ID Coral Rescue** interface inventory, with a source-level **Tools > MATCH3 > 28-Screen Shell Builder** that can construct draft, visibly unbound uGUI candidate shells for each ID using five distinct draft color palettes. Neither those layouts nor their source artwork are finished/owner-approved screens.
- **VF-02 offline content-addressed PNG asset catalog** at `factory/asset_catalog/catalog.py`, with explicit review receipts, immutable approved history, owner-controlled explicit replacement and SHA-256 blob checks. Approval strings are audit metadata, **not proof of an authenticated human signature**.
- Python structural validators and adversarial tests. **Historical verification:** 66/66 tests at source SHA `10a1b3bc09be...` passed on 2026-10-15 GitHub Actions [38788803805](https://github.com/Sekiph82/MATCH3-Visual-UI-Factory/actions/runs/38788803805); NOT proof that later source changes passed, and NOT a Unity compilation test.
- **VF-06 draft particle prefab lab:** five preset families, manual controls and deterministic 2D motion sketch; Unity Scene/Game preview remains necessary.
- **VF-07 draft interactive composer:** seven base screen archetypes plus a data-driven 28-ID Coral shell builder using real Unity uGUI Canvas/Images/Text/disabled Buttons, exact screen IDs, a candidate marker and game draft palette tokens. No Game/Engine action bindings or finished polished graphics yet.
- **VF-02 explicit rollback:** previously approved asset revisions can be restored only with a matching expected active revision and review receipt; immutable history rows and original source files remain. SQLite audit metadata is not an authenticated owner signature.
- **VF-02 Five-Game Production Queue:** offline, source-integrity-checked JSON portfolio report and read-only Unity Editor dashboard showing candidate backlog, recorded approvals, active revision counts and rollback events. No game publish or automatic owner approval.
- **VF-03 offline batch importer (R14 source):** deterministic dry-run of up to 64 SHA-pinned original/licensed PNGs per manifest, explicit plan SHA to commit, single SQLite transaction for candidate-only revisions, stale-plan/replay/linked-source rejection. No AI provider/API charges or silent art approval. Newly authored tests require a separate local rerun at R14 SHA.
- **VF-08 runtime safe-area component + synthetic layout wireframe:** five approximate device presets and static actual RectTransform bounds/tap-target warnings using the new Unity Editor `Tools > MATCH3 > Responsive Layout Wireframe`. It is explicitly NOT a rendered mobile preview or physical device sign-off.
- **VF-09 offline sprite pixel QA:** read-only 32-PNG batch health analysis (alpha coverage, visible bounds, edge/fringe indicators, recorded SHA-256) and draft style-palette contrast advisories, plus a Unity Editor JSON report inspector. R16 changes require exact-SHA Python and Unity tests; no creative approval.
- **VF-05 UI tween runtime:** a small, dependency-free `CanvasGroup` presentation transition with inspector PlayMode controls and reduced-motion snap; 28-shell modal/ceremony/overlay candidates attach it. Unity runtime effect acceptance remains open.
- **VF-09 manual prefab QA Inspector:** browse candidate uGUI/ParticleSystem components, suspect unbound active buttons, safe area, missing renderer materials and image/clip import metadata. Real visuals, user experience and performance acceptance are still human/device-gated.
- **VF-04 offline PNG processor**: 1×/2×/3× trim/scaling, alpha keep/remove mask, and deterministic multi-sprite PNG atlas with exact sprite/UV ledger. All output is candidate-only, outside Git. Unity `Tools > MATCH3 > Sprite Atlas Inspector` provides read-only geometric preview, not production art acceptance.
- **VF-09 independent pixel verifier** checks original SHA provenance, sprite rects, UV layout, atlas pixel-by-pixel parity and original/mask alpha composition, without writing any image data.

## Open in Unity Hub (existing folder, do not create duplicate checkout)

Use **Unity 6000.6.5f1**. In Unity Hub select **Add project from disk** and browse to the already present:

`C:\Users\sekip\Desktop\GAMES\MATCH3 GAMES\MATCH3-Visual-UI-Factory`

Before updating the existing folder, inspect uncommitted local changes and remote divergence; never reset, force-pull, overwrite untracked files or create duplicate clones. This cloud operation has NOT synced or installed files on the owner's PC.

Unity may generate `Library/`, `Temp/` and package metadata on first opening; these are local caches and must not be committed. Unity visual QA/device tests remain outstanding.

## One-command Windows preparation (optional, owner-controlled)

From PowerShell **in the existing local checkout**, after reviewing local changes:

```powershell
.\scripts\prepare_visual_factory.ps1 -FetchAndFastForward -OpenUnity
```

The script verifies the exact remote, `main`, clean local status, repository
version, and only permits **fast-forward** Git synchronization. It never
uses hard reset, force push, deletes, worktrees or duplicate clones. If local
changes or divergence are found, it stops without overwriting anything. The
actual local run and Unity import still require on-machine execution and
are NOT claimed completed by this cloud implementation.

## No-cost Unity EditMode tests (source harness, not executed here)

Eight Unity EditMode NUnit tests have been authored in the shared package to
cover all 28 Coral catalog IDs, all five draft palettes, social/policy-off
restrictions, no automatic marker approval, sprite-loop frame order,
UI reduced-motion and interruption behavior.
The host project declares the package as `testables`; the NUnit test assembly
is Editor-only and excluded from player builds.

After a clean, owner-approved synchronization of the existing Windows
checkout, local Unity 6000.6.5f1 can run the suite **without GitHub Actions**:

```powershell
.\scripts\run_unity_editmode.ps1 -EvidenceDirectory "D:\MATCH3_TEST_EVIDENCE\VUF_R10"
```

This command is available **but has not been executed** in this cloud coding
session. It writes logs/XML only to the supplied external evidence location,
retains results even when tests fail and does not delete or install anything.
Unity first import may still generate its ordinary `Library/` and `Temp/`
cache in the local checkout. It is not a device/art acceptance test.

## Offline asset catalog, no paid APIs

Choose a separate, owner-controlled **store outside the repository**; the catalog explicitly rejects blob storage inside the tracked GitHub source tree.

```powershell
python factory/asset_catalog/catalog.py --store "D:\MATCH3_VISUAL_ASSETS" init

python factory/asset_catalog/catalog.py --store "D:\MATCH3_VISUAL_ASSETS" ingest --file "D:\source\my-original.png" --profile Coral_Rescue --key "tile.star" --rights original --source-receipt "LOCAL_SOURCE_REFERENCE"

python factory/asset_catalog/catalog.py --store "D:\MATCH3_VISUAL_ASSETS" verify

python factory/asset_catalog/catalog.py --store "D:\MATCH3_VISUAL_ASSETS" export-preview --profile Coral_Rescue
```

`ingest` returns a candidate `revision_id`. Only after real owner review can the owner explicitly authorize an `approve --revision-id ... --owner-receipt ...` command. Replacing an active approved asset also **requires** `--replaces-revision-id <current_id>`. Neither `approve` nor `export-preview` publishes to a game. `export-preview` always reports `TEST_ONLY`, with upstream Engine/LFX SHAs unpinned.

## Structural checks

```powershell
python -m unittest discover -s tests -v
python factory/validators/validate_design.py
python Tools/validate_manifest.py Samples~/sample_manifest.json
```

**Cost control:** GitHub Actions source workflow is now opt-in **manual dispatch only**. Each automatic push/PR run has been disabled to avoid spending on a CI run per source commit. Run free/local source checks on the owner's existing checkout with `.\\scripts\\run_source_checks.ps1`. The script makes no source modifications or paid calls. Actual Unity Editor compilation, manual art/VFX lab operation, source rights, real devices and integration require separate evidence before PASS.

## Design and ownership

See [architecture](docs/ARCHITECTURE.md) and root [TASKS.md](TASKS.md) for the VF-01..VF-10 module map, VUF-M00..M11 milestones, development sequence and protected upstream integration gates. Google Drive carries prompts and audit evidence, not GitHub. No production game asset pixels are imported into MATCH3_ENGINE.


## R17 | Draft UI state and bilingual/stress copy review
The **28-Screen Shell Builder** now offers **8 review-only UI state labels**
(Ready/Loading/Offline/Error/Owned/Claimed/Disabled/Pending) and three
non-shipping mock copy modes: English, Turkish draft, and deliberately
expanded stress text. Selected mock values are written only onto **NEW**
candidate-only prefabs at manual save. Preview code cannot enable Buttons,
attach Engine callbacks, publish art or approve a product. English/Turkish
copy is not finalized localization. Source-defined R17 validation covers
28 × 8 × 3 combinations and five Style Bible profiles; real Unity import,
rendering, typography, overflow and devices still require separate tests.


### R18 | Text-fit and color-contrast authoring
Added a read-only **Typography and Contrast Lab** under
`Tools > MATCH3`, accessible through the Factory dashboard.
It uses actual Unity `TextGenerator` with candidate Text components and
five synthetic viewport bounds, reporting approximate text overflow and
contrast risks without modifying a prefab. Missing font/background is
reported as unknown. This is **not** a rendered UI/device or language
acceptance test. Five new NUnit methods and three Python source guards
are written but have not run at R18 exact code SHA.


### R19 | External English/Turkish draft localization audit
`factory/ui_composer/locale_audit.py` reads a human-supplied offline,
external JSON draft for **all 28 canonical Coral screen heading keys**.
It validates current screen IDs and policy gates, UTF-8 source integrity,
invisible/bidirectional control characters, EN/TR brace-placeholder
parity, duplicate JSON keys, missing copy, excessive length, and tracks
coverage without importing any game-ready translations.
New `Tools > MATCH3 > Localization Coverage Studio` is a **read-only**
Unity report viewer. No translation is approved, no runtime UI or game
state is changed, no cloud translation/payment is invoked. R19 source,
new Python/Unity tests need a later batched local regression.
