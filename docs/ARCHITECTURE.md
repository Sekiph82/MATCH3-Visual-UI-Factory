# Visual Factory Architecture | R04, 2026-10-15

This document describes components, not audit status. The only lifecycle tracker is root TASKS.md.

## Vision
Five independent branded Match3 titles share Visual Director, Asset Catalog, AI provider adapters, image processing, animation and VFX builders, a Unity UI composer, safe-area devices, Visual QA Studio and reproducible exporter. Game rules, ledger, save mutations and genuine business logic remain exclusively with MATCH3_ENGINE and each game.

## Canonical layers
- `factory/visual_director` **VF-01**: versioned per-game style bibles, non-color tile silhouettes and editorial screen inventory.
- `factory/asset_catalog` **VF-02**: immutable, SHA-256-addressed original/licensed sources, explicit candidate review and revision-level approval.
- `factory/asset_generator` **VF-03**: pluggable manual image import and optional consented external providers. Zero required paid APIs and zero implied commercial rights.
- `factory/image_processor` **VF-04**: non-destructive masking, trim and normalized sprite extraction, source/review receipts.
- `factory/animation_builder` **VF-05**: sprite-sheet / skeletal / approved 3D authoring, no single forced representation.
- `factory/vfx_builder` **VF-06**: particles, shaders, transition playback and reduced-motion fallbacks.
- `factory/ui_composer` **VF-07**: real Unity interactive components and layer-based templates, not flat mockups.
- `factory/responsive` **VF-08**: responsive safe-area and real device validation.
- `factory/validators` **VF-09**: negative acceptance, performance, rights, contrast, transparency, device and QA receipts.
- `factory/export_pipeline` **VF-10**: view-only UPM importer, version pinning and rollback.
- `unity_package`: self-contained Unity 6000.6.5f1 UPM source; no rules/rewards mutations.
- `games/<profile>`: **only theme configs, references to versioned exports and metadata**. These are NOT the real game repos.

## Development order
1. **Phase A / isolated foundation, authorized now:** M00 source audit and pinned toolchain; VF-01 style directions; VF-02 candidate/approval catalog; manual-import VF-03 interface; runtime contract stubs; source-only automated tests. Maintain Engine and LFX integration gates.
2. **Phase B / safe creative tools:** VF-04 lossless processing, VF-05 sprite editor, VF-06 local VFX authoring and reduced-motion; all manual import friendly.
3. **Phase C / interactive authoring:** VF-07 layered real UI components for all 28 Coral screens, with component reuse for five themes; VF-08 responsive tools and manual multi-device simulator.
4. **Phase D / visual quality:** VF-09 full manual Visual QA Studio, reproducible replays, performance, accessibility/rights checks, owner candidate acceptance. Preview is not physical-device proof.
5. **Phase E / gated integration:** after independently audited full Engine and LFX milestones, VF-10 exactly pinned manifests, Unity prefab/atlas/Animator/Addressables adapters and five playable visual slices; owner and device tests and independent audit before VUF-M11 release.
6. **Phase F / five game projects:** versioned assets are consumed downstream without mutating ENGINE source, rules or earned rewards.

## Version and source policy
`CANDIDATE` images never silently supersede an `APPROVED` revision. All approved blobs are immutable and separately stored in an owner-selected, external content-addressed folder. A new revision is approved by a distinct owner decision explicitly specifying the expected previous active revision. Catalog receipt strings are record fields, NOT a cryptographic or identity-based signature; final approval still requires direct owner review. Failing provenance, missing art, signature mismatch, unavailable age policy and broken dependency contracts fail closed. No automated provider may charge by default or store tokens in GitHub.

## Prompt and evidence policy
Root TASKS.md owns lifecycle. Google Drive contains instructions/audits/test evidence; never commit production artwork source, machine caches, secrets or large reference datasets to GitHub. A technical source test cannot replace Unity Edit/PlayMode or physical iOS/Android device proof.
