# VUF M03–M04 standalone source continuation | 2026-10-21

This is **technical source documentation**, not a second task tracker or
an independent human quality/legal audit. Root `TASKS.md` remains the only
authority for the 137 frozen task IDs.

## M03 semantic uGUI candidate kit

**Menu:** `Tools > MATCH3 > M03 Five-Game Semantic Component Kit`.

- Native Editor `VufM03ComponentKitWindow` reuses the existing, checked M02
  five-game identity catalog, inherited `VufScreenCatalog` palettes,
  `VufResponsiveGeometry` through `BuildSourceGridGuide` and
  `VufReviewStateCatalog` eight mock states.
- A disposable Unity Canvas actually contains **10** semantic prototypes
  with separate uGUI Images/Text: primary/secondary CTA, card, modal, badge,
  counter, tab, progress, disabled reason and pending state. Three roles
  have real `Button` components, all disabled and without event listeners.
- Four portrait source design sizes (320 / 393 / 430 / 768 dp) use minimum
  44dp draft hit targets and 2 or 4 semantic control columns. This
  is design geometry **not measured device touch size or responsive approval**.
- The Editor shows a source-only schematic; the actual disposable Canvas is
  never saved or inserted into a production game. Owner original art, font
  rights, real in-game consent, reward, purchase and navigation are missing.
- The existing `VufDashboardWindow` now links directly to the existing
  M02 Style Bible inspector and new M03 Semantic Component Kit; no new
  navigation path for production publishing is enabled.
- The original 28 Coral contract screens, 140 prior theme-shell variants and
  their single disabled primary action are intentionally **unchanged**.
  New kit is **not** 28 finished/connected game screens and not M03 exit PASS.
- Authoring code: `unity_package/Editor/VufM03ComponentKitWindow.cs`;
  test source: `VufM03ComponentKitEditModeTests.cs` (4 NUnit methods) and
  `tests/test_m03_component_kit.py` (6 Python cases). Stable `.meta`
  registered under `Tools/validate_repo_structure.py`.

## M04 immutable source pin + change review

Module: `factory/visual_director/m04_original_comparison.py`.

Call `inspect_original_candidate(original_png_bytes,
candidate_png_bytes, manifest_json_bytes)` with one *human-supplied*
source PNG and one candidate PNG of exactly the same dimensions. The
review contract requires `schema_version=1`,
`stage=M04_SOURCE_REVIEW_UNAPPROVED`, one canonical five-title ID,
a profile-prefixed semantic `asset_id`, exact SHA-256 pins for both
byte streams, the existing M09 strict creator/usage-scope/consent
reference **receipt shape**, and **four false owner/rights flags**.

The module deliberately **reuses** `m09_pixel_diff.compare` and
`verify_receipt_source` rather than creating another PNG engine, approval
database, or artistic judgement algorithm. The returned report exposes
verified source identity hashes, pixel/alpha mismatch counts and a
deterministic lineage digest, while all human/legal/GUI/device/release
authority stays `false`. Even `pixel_identical_to_reference=true`
does **not** mean that the candidate is licensed, original or accepted.

The function makes no file writes or network/provider calls. It refuses
unknown/reordered field schema, duplicate JSON keys, cross-title IDs,
forged owner approvals, mismatched source digests and invalid or differently
sized PNGs. Tests authored at `tests/test_m04_original_comparison.py`
(6 positive/negative tests). Real commissioned originals, licence papers
and owner sign-off are not supplied and remain OPEN.

Example JSON contract shape (hashes are illustrative; never reuse them as
actual asset evidence):

```json
{
  "schema_version": 1,
  "stage": "M04_SOURCE_REVIEW_UNAPPROVED",
  "profile_id": "Coral_Rescue",
  "asset_id": "Coral_Rescue.mascot.pose_idle",
  "reference_sha256": "<actual lowercase sha256>",
  "candidate_sha256": "<actual lowercase sha256>",
  "provenance": {
    "profile_id": "Coral_Rescue",
    "asset_id": "Coral_Rescue.mascot.pose_idle",
    "source_filename": "creator_original.png",
    "creator": "<owner supplied creator>",
    "licence_text_location": "<owner supplied evidence path/reference>",
    "consent_reference": null,
    "usage_scope": "<pending explicit creator usage scope>",
    "source_sha256": "<actual lowercase sha256>",
    "stage": "OWNER_ART_SOURCE_REVIEW_PENDING"
  },
  "owner_originality_approved": false,
  "owner_legal_rights_approved": false,
  "creator_verified": false,
  "source_release_allowed": false
}
```

## What has NOT been run or accepted

All M03/M04 test cases are **authored but NOT run** in the owner
Windows Python 3.12 and Unity 6000.6.5f1 environment at the new source SHA.
No current GUI screenshot, iPhone physical touch/camera/colour accessibility
PASS, GameView interactive bindings, owner original artwork, creator/rights
approval, Engine/LFX final contract, release or Codex milestone QA is claimed.
Pre-code forward acceptance criteria live in Drive's existing
`03_AUDIT_CRITERIA`; developer logs in `02_CODEX_LOGS`.

GitHub push/update is not local checkout synchronization. Safe owner-local
fast-forward-only verification remains pending real Codex execution.
