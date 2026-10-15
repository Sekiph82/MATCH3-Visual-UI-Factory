# VF-03 | Offline batch intake for original/licensed PNGs (R14)

The Visual Factory batch path can now ingest **up to 64 source images** per
manifest, with a maximum of **64 MiB total source bytes**, without cloud
providers, subscriptions, network activity or Unity gameplay dependencies.

## Design and rights boundaries

* **DRY RUN is the default.** No revisions, blobs, approvals or files are
  created in the catalog during planning.
* The source directory and pre-initialized catalog store must be **outside
  the Git source checkout**. No source file is overwritten, edited or moved.
* Every source is an explicitly named, contained nonlinked PNG with a pinned
  lowercase SHA-256, semantic asset key, one of the five official game profile
  IDs, an original/licensed rights declaration and its source receipt. The
  receipt is documentary metadata **not proof of ownership or permission**.
* Full PNG CRC/decompression validation is provided by the existing
  `VF-04` decoder. Unsupported formats fail rather than being changed.
* A deterministic plan SHA-256 binds the validated source bytes, semantic
  keys, rights/receipts, dimensions and *current catalog revision count*.
* Explicit `--commit` must repeat the exact `--expected-plan-sha256`.
  The catalog rechecks all originals and its current revision baseline.
* **One SQLite transaction** appends ALL candidate revision records or NONE.
  Previous versions and approved/active masters remain untouched. As with
  every content-addressed store, unused newly written blobs can remain after
  a failed transaction and must **not** be automatically deleted.
* No asset is auto-approved, published to Unity or copied to another game.
  Provider adapters remain **disabled** until a distinct, owner-approved
  provider contract, pricing and licensing workflow exists.

## Use from an existing checkout

First initialize a separate external store *once* (not in Git):

```powershell
python -B factory/asset_catalog/catalog.py --store "D:\VUF_ORIGINAL_STORE" init
```

Create an external JSON document with exact fields. Replace the example
relative PNG path and SHA with your **real** source. Use
`(Get-FileHash -Algorithm SHA256 "D:\ORIGINALS\coral\star.png").Hash.ToLower()`
to compute the pin. The source root is a separate directory:

```json
{
  "schema_version": 1,
  "stage": "CANDIDATE_ONLY",
  "items": [
    {
      "file": "coral/star.png",
      "profile_id": "Coral_Rescue",
      "asset_key": "tile.star",
      "rights": "original",
      "source_receipt": "EXPLICIT_SOURCE_PROVENANCE",
      "sha256": "REPLACE_WITH_THE_REAL_LOWERCASE_64_CHARACTER_SHA256"
    }
  ]
}
```

Preview without any catalog change:

```powershell
python -B factory/asset_generator/offline_batch.py --manifest "D:\VUF_BATCH\intake.json" --source-root "D:\ORIGINALS" --store "D:\VUF_ORIGINAL_STORE"
```

The JSON output includes the `plan_sha256`. Only after checking the plan,
apply deliberately:

```powershell
python -B factory/asset_generator/offline_batch.py --manifest "D:\VUF_BATCH\intake.json" --source-root "D:\ORIGINALS" --store "D:\VUF_ORIGINAL_STORE" --commit --expected-plan-sha256 "COPY_EXACT_HASH_FROM_DRY_RUN"
```

A changed PNG, receipt, catalog baseline or any unexpected source causes a
rejection. Replaying a submitted plan does not silently add another revision.
The plan receipt protects against *accidental stale execution*, not against
an attacker who can rewrite all sources and the local database.

## Verification

`tests/test_offline_batch.py` contains standard-library tests for
preflight-only behavior, authorization, five-game isolation, source hash and
schema rejection, traversal/reparse simulation, input mutation, baseline
replay, two-item atomic candidate commit and failed-blob DB rollback.

**Stage at R14 source commit:** new tests are authored, **not yet executed
against the current Git SHA**. Last confirmed Windows results at earlier C004
SHA `a4493cd8192b7c7744cc1e8c18034aae28492d9d` were 125 Python
PASS, 7 Windows symlink SKIP, 13 Unity EditMode PASS. New batch code and
19 tests must be run locally before anyone claims this functionality passed.
