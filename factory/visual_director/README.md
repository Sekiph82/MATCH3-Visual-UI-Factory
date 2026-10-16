# VF-01 / R25 | Five-Game Six-Silhouette Mathematical Tile Kit

This is an offline, zero-provider **candidate prototype**, not bespoke
premium game artwork. The six silhouettes have distinguishable shape cues
independent of palette: circle, triangle, diamond, star, crescent, shield.

`python -B factory/visual_director/silhouette_kit.py --profile Coral_Rescue --side 64`

Without `--output-dir`, no files are written; the manifest prints on stdout.
For intentional export use a NEW outside-Git directory, for example:
`--output-dir "D:\\VUF_CANDIDATES\\coral_tiles_001"`.

Outputs: six `tile_<shape>.png` 8-bit RGBA anti-aliased tiles,
`tile_atlas.png` arranged 3x2, and `tile_manifest.json`. The
manifest pins Style Bible SHA-256, each encoded PNG digest and exact
raw RGBA atlas subsection hash. Supports all five draft style profiles
with original mathematical geometry and palette colors, 24..128px tile
size. It never overwrites or alters original/licensed art, modifies
gameplay or grants owner rights/approval.

`tests/test_silhouette_kit.py` includes ten authored Python tests.
These remain unexecuted on R25 source until a later local batch.
