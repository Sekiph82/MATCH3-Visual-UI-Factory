# M05 | Native SpriteAtlas V2 source-import QA | 2026-10-21

Root `TASKS.md` is the only task tracker. This page is code usage and
unverified acceptance evidence, not an independent owner sign-off.

The existing **Tools > MATCH3 > SpriteAtlas V2 Candidate Builder** now
includes a separate **Inspect existing PNG Sprite importer settings
(READ-ONLY)** command. It accepts only distinct, already imported PNGs
under Unity `Assets/` whose `TextureImporter.textureType` is `Sprite`.
No owner PNG is resaved or imported by this inspection.

The report reads the real `AssetDatabase` GUID, source texture resolution,
`TextureImporter.spriteImportMode`, `spritePivot`, `spriteBorder`,
`spritePixelsPerUnit`, `maxTextureSize`, `mipmapEnabled`,
`alphaIsTransparency`, and read-only Android/iPhone platform override
flags. **Multiple** sprite import mode is not falsely certified as one
pivot: every slice's individual pivot/border still requires explicit
native sprite inspection. Preview labels `OriginalRightsVerified`,
`RealDeviceTextureVerified` and `ReleaseAllowed` remain false.

Implementation reuses Unity official built-in `SpriteAtlasAsset`,
`SpriteAtlasImporter`, `TextureImporter`, and existing
`VufSpriteAtlasV2Window.ValidateDraft`; it copies no UnityCsReference
source or externally licensed art. The existing explicit manual creation
of a NEW `.spriteatlasv2` (includeInBuild=false) remains separate and
unchanged. `ReadImportedSettings` has no write/reimport/importer-changing
API invocation.

New test definitions are AUTHORED, **not executed**: two actual Unity
EditMode cases for an unimported texture rejection and a test-owned
temporary imported PNG's bytes, GUID, and `EditorJsonUtility` importer
settings being unchanged after inspection; plus one Python source
contract test. The Unity test creates/deletes only its own unique
test sandbox under `Assets/` and does not use original owner PNGs.

**Open:** original creative rights, manually checked real SpriteAtlas V2
image atlas, per-Sprite multiple pivots, 1×/2×/3× pixel bounds/packing,
real iPhone/Android compression/image quality/GPU tests, owner GUI
screenshots, final live Engine IDs and production atlas acceptance.

The exact new GitHub source commit does not imply local owner PC sync.
The existing ff-only checkout verification and one full M05 milestone
Codex test are separately required.
