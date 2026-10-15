# VF-04 | Offline, non-destructive visual processing | R07 source prototype

**Status: source implemented; latest Unity/Python checks NOT yet rerun after R07 changes.**

The tools read original PNG assets and write NEW `CANDIDATE_NOT_APPROVED`
exports, outside the tracked GitHub working tree and outside every source folder.
No source is overwritten. Outputs include exact source SHA-256 provenance.

## 1. Pixel-exact trim / 1x, 2x, 3x

```powershell
python -B factory/image_processor/png_pipeline.py --source "D:\OriginalArt\tile.png" --output-dir "D:\MATCH3_VISUAL_ASSETS\candidates\tile-001" --padding 2 --alpha-cutoff 0 --scales 1 2 3
```

Supports 8-bit non-interlaced RGB/RGBA, PNG filters 0..4, complete chunk CRC,
bounded decompression and pixel RGBA. RGB `tRNS`, palette, grayscale,
interlaced, PNG gamma/ICC profile reproduction, PSD and layered source files are
**not yet supported**; unsupported alpha fails closed instead of silently
turning transparent pixels opaque. Retains source RGBA values in trimmed rect.

## 2. Separate transparent alpha masks

Create an original/license-reviewed, same-size RGBA PNG mask in any image
editor. Its **alpha** channel, not color, selects the preserved pixels.

```powershell
python -B factory/image_processor/alpha_mask.py --source "D:\OriginalArt\character.png" --mask "D:\OriginalArt\selection.png" --output-dir "D:\MATCH3_VISUAL_ASSETS\candidates\mask-001" --mode keep
```

`--mode remove` uses inverted mask alpha. RGB is copied unmodified, output
alpha uses deterministic integer multiplication/rounding. Original and mask
SHA-256 hashes are recorded in `mask_receipt.json`. Still needs a live
in-application brush/selection/matte editor before VF-04 full acceptance.

## 3. Deterministic alpha-preserving sprite atlas

Create a JSON file in an external, owner-controlled folder:

```json
{
  "tile.diamond": "tile_diamond.png",
  "tile.star": "tile_star.png"
}
```

Paths are resolved relative to the JSON file, or can be absolute PNG paths.
Generate a **write-once, non-rotated** sprite sheet:

```powershell
python -B factory/image_processor/atlas_pipeline.py --input-manifest "D:\OriginalArt\atlas_sources.json" --output-dir "D:\MATCH3_VISUAL_ASSETS\candidates\atlas-001" --padding 2 --extrude 1 --max-width 2048 --max-height 2048
```

A deterministic shelf packer produces `atlas.png` and
`atlas_manifest.json`, with source hashes, exact sprite pixel rectangles,
bottom-left-origin Unity UVs, no pixel scaling and edge extrusion.
Current limits: 128 sprites, max dimension 4096 and 16.8 million atlas pixels.
This is not Unity SpriteAtlas import, GPU texture compression, optimal packing,
or approved game art.

In Unity open **Tools > MATCH3 > Sprite Atlas Inspector**, manually import
the candidate PNG + JSON and inspect geometry, sprite outlines, UVs and
overlaps. The window does **not** verify cryptographic hashes.

## 4. Independent offline pixel & source verification

```powershell
python -B factory/validators/verify_candidates.py atlas --candidate "D:\MATCH3_VISUAL_ASSETS\candidates\atlas-001" --sources-json "D:\OriginalArt\atlas_sources.json"

python -B factory/validators/verify_candidates.py mask --candidate "D:\MATCH3_VISUAL_ASSETS\candidates\mask-001" --source "D:\OriginalArt\character.png" --mask "D:\OriginalArt\selection.png"
```

The verifier re-decodes actual output PNG pixels and checks source hashes,
no sprite overlap, bounding rectangles, UV geometry and mask arithmetic.
A successful offline check returns `REVIEW_REQUIRED`, **not owner approval**.

No producer/editor/verifier has permission to modify approved masters,
license receipts, MATCH3_ENGINE, Level Factory, or five consumer game repos.
Real Unity Edit/PlayMode, profiler, visual quality, original/licensed asset
provenance and physical-device tests remain separate mandatory gates.
