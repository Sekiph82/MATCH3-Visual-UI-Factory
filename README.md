# MATCH3 Visual & UI Factory

**Five Match3 games, one shared Unity visual production system.** Current state: **VUF-M00 foundation under active development, not audited or production-ready.**

Games: `Coral_Rescue`, `Garage_Legends`, `Dino_Islands`, `The_Fractured_Realms`, `Wonder_Pop`.

## What works at source level today

- Unity 6000.6.5f1 authoring shell and **local UPM** shared package at `unity_package/`, referenced by `Packages/manifest.json` as `file:../unity_package`.
- **Tools > MATCH3 > Visual Factory Dashboard** lists the ten VF modules with truthful feature support status.
- **Tools > MATCH3 > Visual & UI Factory Studio** manually previews imported original/licensed Texture2D horizontal sprite strips, frame stepping/speed, five profile and eight state selectors, simulated phone/tablet ratio overlays. Animation/VFX editing, real UI screens, integration and export are **NOT IMPLEMENTED**.
- Five original, editable **DRAFT** style profiles in `factory/visual_director/style_profiles.v1.json`; owner creative approval remains open.
- Stable **28-ID Coral Rescue** interface inventory in `schemas/coral-experiences.v1.json`, including Home and Gameplay/HUD. These are specifications, not 28 implemented screens.
- **VF-02 offline content-addressed PNG asset catalog** at `factory/asset_catalog/catalog.py`, with explicit review receipts, immutable approved history, owner-controlled explicit replacement and SHA-256 blob checks. Approval strings are audit metadata, **not proof of an authenticated human signature**.
- Python structural validators and adversarial tests. **Historical verification:** 66/66 tests at source SHA `10a1b3bc09be...` passed on 2026-10-15 GitHub Actions [38788803805](https://github.com/Sekiph82/MATCH3-Visual-UI-Factory/actions/runs/38788803805); NOT proof that later source changes passed, and NOT a Unity compilation test.
- **VF-06 draft particle prefab lab:** five preset families, manual controls and deterministic 2D motion sketch; Unity Scene/Game preview remains necessary.
- **VF-07 draft interactive composer:** real Unity uGUI layered Canvas/Images/Text/disabled Buttons for seven base screen archetypes; no Game/Engine action bindings yet.
- **VF-08 runtime safe-area component** for RectTransforms; real device evidence still required.
- **VF-09 manual prefab QA Inspector:** browse candidate uGUI/ParticleSystem components, suspect unbound active buttons, safe area, missing renderer materials and image/clip import metadata. Real visuals, user experience and performance acceptance are still human/device-gated.
- **VF-04 full PNG pixel decoder, alpha crop, 1×/2×/3× source transform** and candidate provenance receipt (external output only).

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
