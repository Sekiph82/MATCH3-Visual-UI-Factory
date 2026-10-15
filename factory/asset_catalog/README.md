# VF-02 | Offline content-addressed Asset Catalog

**Production authority remains with the human owner.** This software stores
receipts, but neither receipt strings nor SQLite file permissions can prove
the real identity of the owner. Do not treat them as an electronic signature.

## Candidate, approval and explicit rollback

The `catalog.py` SQLite catalog uses an append-only `revisions` table
and separate `approvals` history, an `active` pointer per game/semantic key,
and append-only `restorations` rollback events. Source PNGs are stored as
external SHA-256 immutable-origin blobs outside the Git repository.

```powershell
# One-time creation OR non-destructive schema upgrade, in an EXTERNAL folder
python -B factory/asset_catalog/catalog.py --store "D:\MATCH3_VISUAL_ASSETS" init

# Store the original PNG as a non-approved revision, obtain revision_id
python -B factory/asset_catalog/catalog.py --store "D:\MATCH3_VISUAL_ASSETS" ingest --file "D:\OriginalArt\tile.png" --profile Coral_Rescue --key tile.star --rights original --source-receipt "OWNER_SOURCE_REFERENCE"

# Only after human owner review. First-ever approval needs no --replaces-revision-id
python -B factory/asset_catalog/catalog.py --store "D:\MATCH3_VISUAL_ASSETS" approve --revision-id 1 --owner-receipt "EXPLICIT_OWNER_REVIEW_REFERENCE"

# A different existing approved revision must be intentionally replaced
# by declaring the EXACT current active ID.
python -B factory/asset_catalog/catalog.py --store "D:\MATCH3_VISUAL_ASSETS" approve --revision-id 2 --replaces-revision-id 1 --owner-receipt "EXPLICIT_OWNER_REVIEW_REFERENCE"

# Restore an EARLIER, genuinely approved revision, again requiring exact
# current active ID. This inserts an immutable restoration event.
python -B factory/asset_catalog/catalog.py --store "D:\MATCH3_VISUAL_ASSETS" rollback --target-revision-id 1 --expected-active-revision-id 2 --owner-receipt "OWNER_ROLLBACK_REFERENCE"

python -B factory/asset_catalog/catalog.py --store "D:\MATCH3_VISUAL_ASSETS" history --profile Coral_Rescue --key tile.star
python -B factory/asset_catalog/catalog.py --store "D:\MATCH3_VISUAL_ASSETS" verify
```

IDs are **examples**. Real IDs come from the tool response. Never assume a
revision number or reuse a stale `--expected-active-revision-id`.

Rollback never erases/replaces original bytes; it moves the active pointer
only after verifying the prior revision was indeed approved, its SHA-256 blob
is still intact, and the exact active pointer matches the owner's explicit
expectation. SQLite triggers reject UPDATE/DELETE of original revision,
approval and rollback-event rows after `init` creates the schema; this is
a local audit safeguard, **not tamper-resistant storage** against a user
with full filesystem/database administration authority.

**Safety:** `export-preview` returns `TEST_ONLY`, with unpinned Engine and
LFX dependencies. None of ingest/approve/rollback/history/verify publishes
a Unity production pack, downloads artwork or modifies a game repository.
True production approval and independent audit require additional real
owner authority, rights and final dependency checks. R09 code/test results
are currently NOT independently verified at the new exact commit.

## Five-game Visual Production Queue | R11 source prototype

For a **read-only, integrity-checked five-game portfolio snapshot**, choose a
fresh output name in the external content folder. The CLI refuses to overwrite
an existing JSON file or write into the Git checkout:

```powershell
python -B factory/asset_catalog/catalog.py --store "D:\MATCH3_VISUAL_ASSETS" portfolio-report --output-file "D:\MATCH3_VISUAL_ASSETS\portfolio_001.json"
```

The report contains all five profiles, total revision counts, pending-review
candidates (up to 100 IDs/keys/SHAs per game), counts of recorded approvals,
current active assets and recorded rollback events. Every blob is checked
against its source SHA before preparing the report. Raw PNG source pixels,
owner credentials and unrestricted filesystem paths are NOT copied into
the report. `READ_ONLY_NOT_OWNER_APPROVAL` is the only supported stage.

Import a **COPY** of this JSON into the existing Unity authoring project.
Open **Tools > MATCH3 > Visual Production Queue** to inspect the counts
and backlog; this is a read-only snapshot, not a live database connection.
The Unity window never approves an asset or changes files/games. Existing
report files are never overwritten. No GUI preview counts should be treated
as evidence that a real human owner approved copyright, originality or art.
