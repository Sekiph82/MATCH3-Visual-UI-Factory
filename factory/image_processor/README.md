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

## R21 | Original-layer RGBA scene compositor (VF-04)

`python -B factory/image_processor/layer_compositor.py --manifest "D:\\ORIGINAL_ART\\reef_layers.json" --source-root "D:\\ORIGINAL_ART" --output-dir "D:\\VUF_CANDIDATES\\reef_scene_001"`

New `layer_compositor.py` builds a **real RGBA scene PNG** from 1..16
explicitly ordered source layers with exact SHA-256 pins. Pixel origins are
**top-left**; coordinates can be negative for intentional clipping. RGB
background or fully transparent canvas, integer opacity 0..255, and bounded
straight-alpha blending are supported. The external input JSON must have:
`schema_version=1`, `stage=CANDIDATE_NOT_OWNER_APPROVED`, a five-game
`profile_id`, canvas `width`, `height`, `background` (e.g. `"#062E43"`
or `null`), and `layers`. Example layer:
`{"id":"reef.front","file":"reef/front.png","sha256":"<64 lowercase hex>","x":0,"y":-20,"opacity":255}`.
`--output-dir` omitted produces only a JSON receipt on stdout with no
disk output. Explicit output makes a NEW never-overwritten candidate folder
containing `scene.png` and `scene_receipt.json`. Existing originals and
approved art are never edited; no source rights are inferred. Max canvas
2048 x 2048 (4.19M px), total input 64MiB, 16 layers. This is an RGBA
compositor, not a layered PSD painter, parallax rig or visually approved scene.

`tests/test_layer_compositor.py` adds 12 regression methods; R21 output
must be tested at its eventual exact final SHA before claiming PASS.

## R31 | Transparent RGB edge bleed for PNG filtering halos

`python -B factory/image_processor/transparent_rgb_extrusion.py --source "D:\\VUF_CANDIDATES\\tile_circle.png" --radius 2`

This asset-tool-only operation **fills RGB of fully transparent pixels**
outward from nearby nontransparent source pixels while keeping every
alpha byte and all nontransparent RGBA pixels **bit-identical**. Such
extrusion helps reduce black/colored fringes when Unity bilinear
sprite sampling reads transparent texels near sprite edges. The
propagation is bounded to 1..8 pixels and uses deterministic four-way
neighbors with fixed tie order. A radius of 2 is the default.

The source PNG must be existing and external to Git. Without
`--output-file`, results are computed in memory and only a JSON hash
receipt is printed. An explicit output destination must be a **NEW**
external PNG file with no overwrite. Original art stays unchanged.
No actual TextureImporter, mipmap or mobile GPU sampling behavior is
verified here, and it is not permission to modify owner-approved art.

11 new Python regression case definitions cover alpha invariance,
partial alpha, radius cutoff, reproducibility, invalid inputs, default
no-output and never-overwrite. New R31 tests have NOT been executed
locally on the owner's Windows checkout.
