# M11 | Reproducible REVIEW Candidate, Independent Audit & Four-Game Handoff

**SINGLE authoritative progress tracker:** root `TASKS.md` VUF-M11-001..006.
This document is a user quickstart and acceptance boundary, not a new task list.
**NO final factory/game v1 release is frozen.** The reproducible output below
is an immutable **TEST_ONLY candidate** with no original art rights, accepted
Engine ABI, authorized game action, player build or device signoff.

## 1. Existing components reused, not rewritten

- M08 `factory/asset_packaging/candidate_pack.export_pack`: deterministic
  five-theme mathematical PNG/vFX/VF04 atlas, draft en/tr locales, own
  `VisualAssetManifest` and SHA-256 receipt, NEW external destination only.
- M08 `factory/asset_packaging/verify_offline_bundle.verify_exported_pack`:
  full source hash, atlas/pivot/trim evidence, locale/test-only verification.
- M08 Unity `VufCandidatePackImporterWindow`: EDITOR-only copy importer;
  independent source checks, no overwrite of original art/prefabs.
- M08 Unity `VufExternalPackSandboxWindow`, M09 owner visual QA Studio and
  `VufReadinessBoardWindow`: candidate-only external view, A/B, source
  hash, manual rights and owner approval gates.

**Added M11 source code**:
- `factory/release/m11_candidate_release.py`: deterministic canonical
  review-only manifest v1 and content SHA-256 identity; explicit observed
  **40-character** Engine/LFX Git SHAs recorded as
  `OBSERVED_UNACCEPTED_NOT_REPLAY_VERIFIED`. Read-only full audit, external
  NEW-folder exporter, append-only NEW-folder staging importer, and rollback
  by NEW copying a prior reviewed revision. **Rollback does not change a
  running game's active version pointer.** No destructive deletion or
  automatic activation; all source hashes revalidated from actual bytes.
  Extra files, symlinks/junctions, Editor/test/source-art references, secret
  sidecars, digest mismatches, inflated number/size, forbidden owner claims
  or conflicting manifests fail closed. No use of cloud/CI billing.
- `factory/release/m11_game_handoff.py`: typed four-target handoff for
  **G01, G02, G09, G11** with the requested *exact ID strings*.
  Existing authoritative VUF sources have no independently confirmed
  mapping of these four IDs to game titles, so the handoff intentionally
  uses `UNCONFIRMED_NOT_IN_VUF_SOURCE`, and all game-specific acceptance
  flags remain FALSE. Do not invent G01=Coral or similar assignments.
- Unity `Tools > MATCH3 > M11 Release Candidate and Rights Audit`:
  `VufM11CandidateReleaseReviewWindow.cs` can inspect an owner-selected
  external M11 candidate manifest, check all referenced imported/source
  raw file SHA digests and display observed Git pins, source IDs and
  rights/release blockers. It is **read-only** and not the canonical
  Python verifier of manifest content-identity, complete M08 receipt
  or VF04 atlas. Buttons open existing safe importer and rights board.

## 2. Windows 11/Python 3.12 review-only operator commands

**Always use NEW directories outside Git checkout.** The following is a
documented sequence, NOT an action already run by the assistant. Supply
both observed full 40-char Git SHA pins from actual current owner sources,
but understand they are NOT accepted/final ABI pins.

```powershell
python -B -m factory.asset_packaging.candidate_pack --profile Coral_Rescue --new-external-dir "C:\VUF_Candidates\M11_Source_New"
python -B -m factory.asset_packaging.verify_offline_bundle --pack-dir "C:\VUF_Candidates\M11_Source_New"

python -B -m factory.release.m11_candidate_release export --source "C:\VUF_Candidates\M11_Source_New" --new-dir "C:\VUF_Candidates\M11_Review_001" --engine-sha "<OBSERVED_40_HEX_GIT_SHA>" --lfx-sha "<OBSERVED_40_HEX_GIT_SHA>"
python -B -m factory.release.m11_candidate_release audit --candidate "C:\VUF_Candidates\M11_Review_001"

python -B -m factory.release.m11_candidate_release import --candidate "C:\VUF_Candidates\M11_Review_001" --new-slot "C:\VUF_Candidates\Staged_001"
python -B -m factory.release.m11_candidate_release import --candidate "C:\VUF_Candidates\M11_Review_001" --new-slot "C:\VUF_Candidates\Rollback_New_Slot" --rollback-from "C:\VUF_Candidates\Staged_001"

python -B -m factory.release.m11_game_handoff --review-candidate "C:\VUF_Candidates\M11_Review_001" --new-handoff-json "C:\VUF_Candidates\G01_G02_G09_G11_REVIEW_ONLY.json"
```

Each destination MUST NOT exist. The script creates only a new owner-named
external directory or JSON file and rejects repository storage, duplicate
or linked sources. A failed newly created directory can be retained for
owner audit, never automatically removed. Running the rollback command
creates a **second independent candidate copy** of an older verified
candidate; neither a production installation nor a live game is rolled
back. Consumer activation would require a separately designed and
accepted game integration and production safety authority.

## 3. G01/G02/G09/G11 owner approval handoff

For **each original game ID**, the consumer must separately supply:
a verified title ↔ ID mapping (not present in this VUF repository),
an exact approved game-specific visual source package and SHA, authorized
original creator/font/logos plus license/consent documentation, approved
Engine M12 neutral replay schema and final LevelFactory/Engine M24 producer
ABI, native Unity consumer and PlayMode/capture proof, player build
content-exclusion report, physical iPhone/Android GPU metrics, manual
owner GUI/visual approval and its own game's official release gate.
No G01/G02/G09/G11 handoff currently claims these records exist.

A legal source receipt SHAPE is not evidence that the creator owns the
work or that a lookalike is lawful; real owner/legal review is essential.

## 4. What the independent v1 audit does and does NOT mean

Mechanical audit covers candidate TEST_ONLY identity, SHA-256 for all
actual source bytes, unique safe relative paths, revalidated VF04 atlas,
pre-existing M08 locale/rights fail-closed checks and immutable
content-addressed metadata. It checks that no surprise files, raw source
reference art, passwords or Editor/test packages are mixed into the
exported candidate; it never certifies all possible secrets or performs
an external legal/IP opinion. Append-only source staging ensures there
are no destructive overwrite/delete operations. No new remote service,
app/plugin billing or distribution is used.

**Still OPEN for M11-001..006:** real released/accepted Engine/LFX pins
(unaccepted observed SHA is only provenance), version incompatibility
tests with true running consumer, production Unity build or actual game
rollback, signed owner's Factory v1 design system, legitimate original
art/font and game-specific creative samples, independent audit signature,
physical GUI/device/GPU, real first-title asset approval and legal records,
the final formal v1 freeze and game handoff acceptance.

M11 new sources and test methods are AUTHORED but have **NOT yet been
executed in the owner's actual Windows/Unity environment**. The prior M10
technical PASS (Python 454 PASS + 9 symlink SKIP, Unity EditMode 157/157
at SHA `23b087d1d91cd26921994c5b19d42dadea98be6d`) is **historical only**.
VUF-M11-006 is the one whole-milestone Codex test and final technical
audit gate, with human/production decisions explicitly separate.
