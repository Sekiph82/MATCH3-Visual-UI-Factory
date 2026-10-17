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
