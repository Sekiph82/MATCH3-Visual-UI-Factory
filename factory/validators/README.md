# VF-09 | Source and visual quality validation

**R07 state:** `factory/validators/verify_candidates.py` independently
checks real decoded candidate PNG output against original source file SHA-256
and pixel values. Atlas QA checks source IDs, exact rect/UV coordinates,
no overlapping placed sprite rectangles and zero rotation. Mask QA checks
original RGB/alpha and per-pixel keep/remove alpha composition. All commands
are read-only, issue `REVIEW_REQUIRED` on success and fail closed when
metadata or source bytes are altered. They do not grant owner approval.

Run locally (no GitHub-hosted CI):
```powershell
.\scripts\run_source_checks.ps1
```

Structural contract validators: `validate_design.py`,
`Tools/validate_manifest.py`, `Tools/validate_repo_structure.py`,
`factory/vfx_builder/validate_presets.py` and all `tests/` Python unit
cases. Unity Editor QA tool:
**Tools > MATCH3 > Manual Visual QA Studio**, for imported components,
basic Button/Safe Area/VFX/texture/animation metadata.

**Still required:** actual Unity 6000.6.5f1 compilation and EditMode/PlayMode,
image rendering comparison, VFX replay, transparent border/pivot/atlas
filtering, draw call/GPU budget, accessibility and device safe area, source
copyright/licensing checks, real iOS/Android performance and independent audit.
Automated or structural verification is NOT creative owner approval. The
post-R07 Python suite has not been run by GitHub Actions, which remains manual
dispatch only to prevent unexpected per-commit runner costs.

## R16 static sprite health QA

Use `python -B factory/validators/visual_qa.py --source <PNG> --profile Coral_Rescue`. Advisory metrics: alpha coverage, visible bounds, colored transparency, matte-fringe hints and draft palette contrast. Optional `--output-file` writes a NEW external JSON report. The read-only Unity `Sprite Pixel Health QA` Editor panel inspects a JSON TextAsset copy. This never approves art or tests real device rendering. The 19 new Python cases require local execution at the R16 SHA.


## R20 integrated review evidence board
Select `Tools > MATCH3 > Review Evidence Board` from Unity Editor or the
Factory Dashboard. Optionally select a candidate prefab and previously
inspected `VF09_PIXEL_HEALTH_V01` + `OFFLINE_DRAFT_COVERAGE_V01`
JSON TextAssets. The window validates report stages and summarizes data
from the pixel, language and responsive/typography inspectors across
five synthetic device presets, without modifying assets or calling APIs.
Missing input creates a visible outstanding evidence gate.

This tool **never authorizes production or shipping**, even if every
source-only metric reports no warnings. It always keeps original art
rights, human creative/aesthetic approval, live GUI interaction, physical
iOS/Android device QA, and Engine/LFX integration in OPEN state.
An external copied JSON report does not prove artwork ownership or that
any person accepted an asset. Full dependency, legal and device evidence
must be documented and reviewed independently.

## R26 | Read-only independent generated bundle verification

Use `python -B factory/validators/verify_generated_kits.py fx --candidate "D:\\VUF_CANDIDATES\\bubble_fx_001"`
or `tiles` or `scene` for the corresponding candidate bundle.

Checks actual stored PNG CRC, SHA-256 and dimensions. For FX, checks
every frame rectangle and raw RGBA digest, including the separately
hashed static reduced-motion fallback. For tile kits, compares all six
PNG sprites to actual atlas regions and tests distinct alpha outlines.
For layered scenes, verifies the scene image against its recorded digest
and validates ordered provenance receipts, but **does not** re-open original
layers or establish real licensing rights. A success is
`VERIFIED_CANDIDATE_ONLY`, never owner visual approval.
Nine new Python test definitions await R26 exact-SHA execution.
