# M02 | Five independent SOURCE Style Bibles (not licensed final game art)

Owner-priority 2026-10-20: develop standalone Visual Factory source and
visual QA before attempting full Match3 Engine ↔ Level Factory integration.
No new milestone/task ID: all progress belongs to existing `VUF-M02-001..013`
in the root `TASKS.md`.

## Original source hierarchy and working files

- `factory/visual_director/style_profiles.v1.json`: existing M02 draft
  theme palettes and silhouettes. Kept unchanged to avoid breaking older
  VUF code or historical source-hash evidence.
- `factory/visual_director/m02_identity_catalog.v1.json`: new distinct
  creative identity plans, six+ original artist reference families per
  title, five mandatory character/mascot poses, responsive/typographic
  tokens and explicit all-owner-approval-false status.
- `factory/visual_director/m02_style_bible.py`: independent schema,
  inherited source digest, contrast/typography/44dp target, four device
  grids, never-licensed-or-approved validation. Compiles all five
  deterministic view-only source bibles.
- `docs/style_bibles/<GameID>_STYLE_BIBLE_SOURCE_DRAFT.md`: five human
  review sheets that detail draft palette, color contrasts, characters,
  original art-family inventory, accessible device layout and creative
  restrictions. These are art direction, **not finished original artwork**.
- `unity_package/Editor/Resources/m02_identity_catalog.v1.json`: exact
  byte copy for the Unity Editor reviewer; Python test enforces parity.
- `unity_package/Editor/VufM02StyleBibleStudioWindow.cs`: menu
  **Tools > MATCH3 > M02 Five-Game Style Bible and Art Identity Studio**.
  Real Unity Editor source swatches, WCAG palette math, four source
  device grid tokens, five art-family lists and a clear rights warning.
  No runtime callbacks, scene/prefab writes or owner self-approval.

## Usage

From the VUF repository on a machine with Python 3.12:

```powershell
python -B -m factory.visual_director.m02_style_bible
```

This only prints canonical reviewed data to stdout; no file is written.
To intentionally produce five JSON review drafts plus one SHA receipt,
choose a **nonexistent** folder under an existing owner-controlled external
directory. For example:

```powershell
python -B -m factory.visual_director.m02_style_bible --new-external-folder "D:\VUF_CANDIDATES\M02_STYLE_BIBLES_REVIEW_NEW"
```

No source art, font file, licensed identity, approval, game-level event or
phone screenshot is generated or replaced. The exporter cannot overwrite
an existing destination or write within the Git repository.

## Review and missing owner originals

For EACH title, actual original creator-supplied character/reference masters
plus original art rights, font embedding licence, animation/visual quality and
owner acceptance remain **MISSING / OPEN**. `character_pose_review.py`
can inspect actual owner-supplied reference/5-pose PNGs but cannot
legally or artistically approve originality. No producer, user or AI can
turn a mathematical concept placeholder into licensed production art by
changing a JSON boolean.

Source QA authored but **not run on the new M02 SHA**: Python
`tests/test_m02_style_bible.py` (12) and
`tests/test_m02_unity_source_parity.py` (3), Unity Editor
`VufM02StyleBibleEditModeTests.cs` (6). Prior VUF Python 490 PASS
and Unity 172/172 belong to older SHA `3383fe9`, not these changes.

A prospective pre-code M02 acceptance rubric was saved before source
implementation to the existing Drive `03_AUDIT_CRITERIA`:
https://docs.google.com/document/d/1nCrHF5gfk6rVgreEWA6D4TqTERR5wQOBgTt9Ij0LL_c/edit .
Retrospective M02 audit/Dev-log reconstruction are separate, labelled
historical records, not new approval. ONE full local Codex M02 QA prompt
is created only when feasible M02 source coding finishes; the result goes
to `02_CODEX_LOGS`, indexed bytes evidence to `05_EVIDENCE` and independent
audit to `04_AUDIT_RESULTS`. ChatGPT alone updates original `TASKS.md`.

The approved owner safe Git sync task must verify the local Windows
`HEAD` versus live `origin/main` after GitHub writes; no automatic
reset/clean/rebase/force or owner file cleanup. Until Codex performs and
reports this, local synchronization remains **NOT VERIFIED**.
