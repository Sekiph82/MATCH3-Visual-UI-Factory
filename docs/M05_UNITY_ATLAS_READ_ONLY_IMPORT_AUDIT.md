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

## 2026-10-21 | Per-slice Sprite pivot readback (additional source)

The imported Sprite inspector now calls `AssetDatabase.LoadAllAssetsAtPath`
**without reimport**. For every actual `UnityEngine.Sprite` subasset it
checks rect bounds inside the source PNG, finite pivot, unique slice name,
bounded at 2,048 slices, then reports Sprite.rect, Sprite.pivot,
Sprite.border and Sprite.pixelsPerUnit. Unlike the earlier single
`TextureImporter.spritePivot` summary, **Multiple Sprite** mode is now
inspected by real per-Sprite Unity metadata. This is still **not** a
pixel-accurate GameView or phone screenshot and never edits an importer.
Native Unity EditMode test source now checks one true imported Sprite
subasset's rect and pivot against bytes/GUID/importer identity. This
test has not run on the current exact GitHub SHA.

## 2026-10-21 | 1× / 2× / 3× full-RGBA source audit

`factory/visual_director/m05_sprite_scale_receipt.py` audits
original + 3 exported PNG byte streams with their exact SHA256s,
alpha-trim bounds, padding, pivot translation from original bottom-left
pixel anchor and full 1×/2×/3× nearest RGBA identity using the existing
VF04 `decode_png`, `trim_rgba`, `scale_nearest` primitives.
Unlike centre-sample-only reviews, any malformed changed pixel at the
edge or inside a 2× block is rejected. The normalized pivot is
unchanged across scales. It is a read-only receipt, never a GIF,
GameView, Unity Sprite pivot import, GPU bleed or creator approval.

Six Python tests added, authored but NOT RUN. Source fixtures are
synthetic and not production sprites. True 1×/2×/3× imported Unity
Sprite/atlas/GUI and iPhone/Android physical-device acceptances stay OPEN.

## 2026-10-21 | Exact read-only Engine source-kind intake

`factory/visual_director/m05_engine_kind_intake.py` uses existing
Engine public source declarations pinned to **exact original Git blob
SHAs** for `ObstacleLifecycleContracts.cs`,
`GoalScoreContracts.cs`, `BoosterEconomyContracts.cs`,
and `SpecialEffectContracts.cs`. It reads the source files from an
**already-existing separate** MATCH3_ENGINE local checkout, never
clones/fetches/updates a sibling repository. It rejects changed
byte-identities, enum ordinals, source paths/symlink/junction ancestors,
missing files, oversized sources or substituted hand-edited receipt
JSON. The actual enum kinds captured are obstacle layers/damage,
four GoalKind, eight BoosterKind, five SpecialActivationKind.

To inspect explicitly, only if the sibling Engine checkout is present,
from the Visual Factory root:

```powershell
python -B -m factory.visual_director.m05_engine_kind_intake --engine-runtime "C:\\path\\to\\MATCH3_ENGINE\\Packages\\com.match3.engine\\Runtime"
```

This prints a **SOURCE_ONLY** JSON report to stdout. It does not
demonstrate that any title has a real obstacle definition registry,
goal instance IDs, booster asset IDs or an accepted ENG-M12/ENG-M24
neutral replay. Until real registry exports and authorized original
art are present, `actual_*_ids_verified`, Engine ABI, owner art,
gameplay and `release_allowed` remain **false**. No `sample_*` key
is upgraded to a real runtime definition. Eight Python regression
tests authored; no current owner-local test execution claimed.

### Current remaining M05 gates

Source work for read-only audit and deterministic drafts can be
considered implemented, **but M05-003/-004/-010/-013 are not accepted**:
real Engine registry and official LFX final IDs, original creator
art states/master SHA/legal consent, manual Editor SpriteAtlas 1×/2×/3×
pixel/bleeding review, physical device textures/GPU and owner signoff
have not occurred. The already completed historical M05-015 Codex
test was tied to its older exact SHA; it cannot certify new sources.

## 2026-10-21 | Codex successful exact-SHA full regression / Engine CRLF source root cause

Verified Codex readback [M03/M05 full QA report](https://docs.google.com/document/d/15hTwJzKMomuDmPx0I3RJhbt2weEWVOC0_RcxgMMkLpk/edit) at **`11d7e6d25664d24ea93a370ba2d0fc200e61b6a2`**:
Python 3.12.10 **543 total, 534 PASS, 9 Windows symlink SKIP, 0 FAIL/ERROR**;
actual Unity 6000.6.5f1 EditMode **187/187 PASS**, Atlas V2 **7/7 PASS**.
These are true Codex-run outcomes at that exact prior SHA and must never be
carried forward as executed tests for later source commits. Actual multi-slice
fixture, native interactive GUI, original owner art and devices still OPEN.

Local Engine checkout has `CRLF` worktree source while HEAD blobs are
canonical `LF`: all FOUR Engine HEAD enum blob hashes equal original VUF pins,
while byte hashing the checkout returns different blob digests due to EOL.
This is **transport encoding**, not proof of Engine enum contract drift.
It is not permission to modify dirty Engine checkout (reported 1 modified and
3,944 untracked owner paths). We must not lower exact Git blob pin checks.

Narrow VUF-only fix: `m05_engine_kind_intake.py` gains
`_canonical_checkout_source_eol` and
`read_pinned_engine_sources_with_receipts`. They accept exact pinned
bytes or only a *pure CRLF* worktree whose **in-memory CRLF->LF** result
has the exact pinned Git blob SHA. Mixed newline, bare CR, byte mutation,
nonmatching pin or source path identity fail closed. Receipts disclose the
raw checkout blob SHA, canonical pinned Git SHA and mode
`PURE_CRLF_NORMALIZED_IN_MEMORY`; no working file/Git operations or
cross-repo writes. Public `read_pinned_engine_sources` retains the
original dict-only API, and the CLI adds `engine_checkout_eol_receipts`.
Four more Python regression methods cover exact-LF, pure-CRLF, negative EOL
and read-only source invariants. **All these additional source changes and
tests are authored, NOT YET TESTED by owner-local Codex/Unity.**

This EOL evidence does **not** establish actual host registry definition
IDs, ENG-M12/ENG-M24 gameplay parity, multi-slice Editor behavior,
licensed artwork, physical device texture rendering or release permission.
