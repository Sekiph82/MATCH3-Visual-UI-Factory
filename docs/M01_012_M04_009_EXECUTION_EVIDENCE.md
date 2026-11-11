# VUF-M01-012 / VUF-M04-009 execution evidence (for independent QA)

**Builder receipts only — not PASS, rows stay `[ ]`.** A separate read-only
QA reviewer must re-run or inspect; owner art/rights/Unity/device gates are
untouched.

- Source under test: `e590b0449ef31c54642281dc46cbd64be2d76a06` (VUF origin/main), clean detached worktree
- Date 2026-11-12, Windows 11, `python` = CPython 3.12.10 (per-user Windows install), pytest 9.1.1
- **No Unity Editor run** (machine occupied by other Unity jobs; also not needed for these Python suites)

## VUF-M04-009 — six authored M04 tests (first execution)

`tests/test_m04_original_comparison.py` (added in `7ab5974`, never run before) against
`factory/visual_director/m04_original_comparison.py`.

```
python -B -m unittest tests.test_m04_original_comparison -v
Ran 6 tests in 0.003s
OK            (exit 0)
```

1. `test_m02_five_game_id_and_source_lineage_are_mechanical_not_approval` ok
2. `test_even_identical_reference_and_candidate_are_not_license_approval` ok
3. `test_mismatched_source_or_candidate_sha_fails_before_pixel_diff` ok
4. `test_all_forged_owner_creator_release_flags_rejected` ok
5. `test_cross_title_and_extra_duplicate_fields_rejected` ok
6. `test_creator_receipt_must_match_image_and_candidate_dimensions` ok

**Defects in code under test:** none found; no source change.

**Mutation probe (out-of-repo script, module text mutated in memory only):**

| Mutant | Result |
|---|---|
| forged owner/creator/release flag check disabled | KILLED (4 failures) |
| reference/candidate SHA intake check disabled | KILLED (3 failures) |
| asset-id profile prefix check disabled | KILLED (1 failure) |
| duplicate-JSON-key check disabled | **SURVIVED** |
| provenance cross-family (asset/profile) check disabled | **SURVIVED** |

Test-gap findings (tests NOT edited — reported for QA/owner decision):
- The duplicate-key case duplicates `creator_verified` as `false, true`; with
  the duplicate guard removed, last-wins yields `true` and the forged-flag guard
  still rejects it, so the test does not isolate duplicate detection. A
  same-value duplicate (`false, false`) would.
- No test puts a different `asset_id`/`profile_id` inside `provenance` only.
  Manual probe: the guard does work (`provenance.asset_id = "Coral_Rescue.tile.other"`
  → `OriginalReviewError: creator receipt belongs to another art family`).

Owner part of M04-009 (complete original/licensed art, approval flow, immutable
master, human originality/rights decision) **untouched and OPEN**.

## VUF-M01-012 — re-run at this SHA

```
python -B -m pytest -p no:cacheprovider tests/test_m01_surface_contract_matrix.py tests/test_m01_view_event_bindings.py tests/test_m01_golden_fixtures.py -v
collected 27 items
================== 27 passed, 1835 subtests passed in 1.27s ===================   (exit 0)
```

Per file: surface contract matrix 10/10, view event bindings 8/8, golden fixtures 9/9.

```
python -B -m factory.ui_composer.m01_surface_contract_matrix
{"matrix_rows": 680, "matrix_sha256": "a709ee437e6e57d6e2f93377d6f6efb2a75f0f8d90543726f7a7c59eb77f6cef",
 "original_screens": 28, "profiles": 5, "real_engine_ui_bound": false, "release_allowed": false,
 "screen_state_rows": 1120, "stage": "M01_UI_SYMBOLIC_SOURCE_CANDIDATE_NOT_ENGINE_BINDING",
 "states": 8, "surfaces": 17}
```

Missing final Engine/LFX pins, reported explicitly as the row requires: all
**1120/1120** screen-state rows have `actual_engine_action_id`,
`actual_engine_route` and `actual_game_binding` = `None` (needs ENG-M24; 0/12
ENG-M24 rows checked at Engine `743c345`). Engine 17/4/8 enum source blobs are
unchanged since the M00-001 pin (see `docs/M00_012_PIN_DELTA_CLOSURE_PREP.md`).

**Remaining for M01-012 closure:** "real external Unity consumer tests" — **NOT
RUN** (Unity-blocked in this session); independent QA; owner acceptance.

## Full Python suite + source checks at this SHA

```
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\run_source_checks.ps1
Unit tests: Ran 595 tests in 293.488s — OK (skipped=9)   [9 = Windows symlink-privilege skips]
Visual director contracts: {'profile_count': 5, 'silhouette_count': 6} {'coral_experience_count': 28}
Unity source/package structure: {'package': 'com.match3.visual-factory', 'unique_guids': 106}
TEST_ONLY sample manifest: VUF_MANIFEST_VALID
All local structural checks PASSED.   (exit 0)
```

Not run: Unity EditMode/PlayMode, GUI, device/GPU. Drive 05_EVIDENCE upload not
performed (Drive not connected in this session).
