# VF-10 Export/Publishing
Versioned UPM component packages, SpriteAtlas V2, Animator and VFX bindings,
layered runtime UI and optional Addressables. All production output requires
reviewed source rights, approved current active revision, exact Engine/LFX
final SHA pins, deterministic dependencies and rollback. NO release export
may run until independently audited Engine and Level Factory final gates.
Current status: local source UPM package only.

## R44 | Owner-safe player content preflight (M08-005 source)

`python -B factory/export_pipeline/player_pack_preflight.py --candidate "D:\\VUF_PLAYER_PACK_CANDIDATE\\001"`

Runs a strict **READ-ONLY** scan over ONLY one explicitly selected
existing, external nonlinked candidate folder. No packages, original
art files, APK/IPA, prefab or manifests are generated or modified.
For each supported PNG/prefab/SpriteAtlas V2/animation/asset/JSON file,
the scan records actual SHA-256 and byte size. It rejects
`Editor`, `Tests`, `Tools`, `docs`, `Library`, `ProjectSettings`,
`Packages`, logs, evidence, raw references, dotfiles, scripts, DLLs,
fonts, credentials, test/candidate/authoring-only markers and suspicious
serialized secrets. Bounds: 512 files, 16 MiB per file, 128 MiB total;
file/directory reparse points, junctions and symlinks are refused.

Even a completely clean scan is ONLY
`REVIEW_ONLY_NOT_PRODUCTION_RELEASE` with `release_allowed=false`.
The Engine/LFX pins, original/licensed artwork approval, real GUI/devices
and owner human release acceptance are separate mandatory checks.
No stage self-promotion, no hidden background upload, GitHub Actions,
paid service or cleanup. Candidate status cannot be upgraded here.

`tests/test_player_pack_preflight.py` defines twelve Python unit cases
for clean candidate hashes, forbidden directories/extensions, secret
and authoring markers, unsafe roots, empty/oversize content, file
counts/case collisions, supported symlink denial and source immutability.
These are source definitions, **not yet executed** on owner Windows.

## R45 | Non-writing manifest compatibility and rollback-diff preflight (M08-004)

`python -B factory/export_pipeline/preview_compatibility.py --candidate-manifest "D:\\VUF_CANDIDATES\\current.json" --profile Coral_Rescue --engine-sha <40hex> --level-factory-sha <40hex> --previous-manifest "D:\\VUF_CANDIDATES\\older.json"`

**INTERNAL_REUSE** of existing strict
`Tools.validate_manifest.validate_manifest`, not a new metadata parser,
gameplay API, asset downloader, approval mechanism, transaction/rollback
executor or release publisher. It reads explicit external nonlinked JSON
manifests (<=2 MiB, <=512 assets), rejects duplicate fields and unsafe
paths/versions/theme IDs, confirms declared full SHA pins against explicitly
supplied expected values, compares optional previous/next manifest asset
hash IDs to report ADDED/CHANGED/REMOVED diffs.

The output ALWAYS reports `release_allowed=false`,
`previous_release_available=false`,
`asset_file_bytes_reverified=false`; an owner receipt or an APPROVED-stage
assertion cannot be authenticated by this tool. The old pack cannot be
restored merely from JSON. Actual blobs, Engine/LFX independently closed
gates, owner art licensing, real devices and visual QA remain OPEN.

Ten regression source tests authored in
`tests/test_preview_compatibility.py` for pinned/nonpinned SHA, duplicate
fields, path traversal, cross-theme, owner receipt forgery, non-mutating
asset diff and missing manifest. **NOT YET RUN ON OWNER WINDOWS.**

## R46 | Read-only Unity manifest version/pin inspector

`Tools > MATCH3 > Preview Version Compatibility` is a Unity Editor
visual metadata comparator. It reuses existing
`VisualAssetManifest.TryParsePreview` from the Runtime package and
existing draft `VufProductionQueueWindow` patterns, rather than
rewriting a JSON parser. Select a TEST_ONLY current and optional
TEST_ONLY previous imported TextAsset manifest, choose one game and
expected exact 40-character Engine/LFX pins. The panel reports
pin drift, ADDED/REMOVED/CHANGED asset IDs and a hardcoded
`Release permitted: NO`. It NEVER writes or restores packages,
approves art, reads secret sources or claims actual Engine compatibility.
Python R45 accepts unapproved CANDIDATE in its strict schema; Unity
intentionally handles TEST_ONLY only.

Four EditMode NUnit test methods (plus three static Python test methods)
are authored, but actual Unity GUI, new-source tests and owner/phone
approval are NOT YET RUN.

## R47 | Real Unity SpriteAtlas V2 candidate authoring (M05-004/M08-003)

`Tools > MATCH3 > SpriteAtlas V2 Candidate Builder` chooses 1–32
existing imported Sprite PNG Texture2D copies, checks identical
assets/dimensions/TextureImporter Sprite type and explicit new path,
then calls **native Unity 6000.6** `UnityEditor.U2D.SpriteAtlasAsset`
APIs (`new SpriteAtlasAsset`, `Add`, `Save`).
After import, `SpriteAtlasImporter.includeInBuild=false` and
SaveAndReimport keep the output **excluded from player builds** while
owner art/GPU/memory/atlas QA remains open. It does not rewrite
source TextureImporter settings or crop/slice input assets.
Only a brand-new `.spriteatlasv2` in Assets may be saved.

The model's manual output is a Unity-side asset candidate, not an
approved/release sprite atlas; creating a SpriteAtlasAsset alone cannot
prove packed sizes, trim/pivot, platform texture compression, 1x/2x/3x
swap correctness or mobile memory/GPU budgets. Real Unity Editor tests
and owner manual inspections are required.

Four Unity EditMode tests cover nonwriting packable validation, null,
duplicate and >32 packables, original pixel invariants, and real
SpriteAtlasAsset/SpriteAtlasImporter API types; three additional
Python source guards inspect safety rules. All R47 additions are
AUTHORED, NOT owner-local tested at new source SHA.
