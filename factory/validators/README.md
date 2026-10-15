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
