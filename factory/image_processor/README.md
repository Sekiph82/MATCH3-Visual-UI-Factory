# VF-04 | Offline PNG image processing (M00/M05 source prototype)

Current implementation: `png_pipeline.py` decodes and CRC-verifies the **complete**
8-bit RGB/RGBA, non-interlaced PNG pixel stream (including filters 0 to 4).
It trims outer alpha, preserves original per-pixel color and alpha, supports
configurable transparent padding and alpha cutoff, and exports deterministic
nearest-neighbor 1x, 2x, 3x PNG candidates plus a SHA-256 lineage receipt.

**This is a real pixel transform, not yet a full image editor.** PSD layers,
mask painting, curved vector paths, GPU effects, sprite packing and color-space
art review remain required future VF-04 work. Grayscale/palette/interlaced PNG
fail closed in v0.1 until dedicated original-pixel parity testing exists.

Example, from repo root with owner-provided original PNG:

```powershell
python factory/image_processor/png_pipeline.py --source "D:\SOURCE\my-original.png" --output-dir "D:\MATCH3_VISUAL_ASSETS\candidates\manual-001" --padding 2 --alpha-cutoff 0 --scales 1 2 3
```

The destination must be an isolated folder **outside the GitHub checkout** and
not the source directory. Files cannot overwrite existing outputs; rerunning
against the same destination fails closed. Source pixels and original file are
never altered. Every export is a `CANDIDATE_NOT_APPROVED` until separately
ingested, reviewed and versioned through the VF-02 catalog. This operation
never changes approved masters or any five-game consumer repository.

Tests: `python -m unittest discover -s tests -v` includes real PNG filter
round trips, alpha bounds, deterministic 1x/2x/3x output, corruption tests,
invalid dimensions/scales and overwrite protection. An actual hosted test
report and Unity preview are still separate acceptance requirements.
