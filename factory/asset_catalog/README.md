# VF-02 Asset Catalog | Current standalone implementation

The SQLite catalog provides append-only, immutable review records, candidate
revisions, active-revision pointers and SHA-256 content-addressed PNG files.
Use `python factory/asset_catalog/catalog.py --help` in the project root.

Content store **MUST** be external to the tracked GitHub repository.
`init` creates the external catalog only when explicitly requested. `ingest`
never auto-approves. `approve` requires a nonempty owner receipt and exact
previous active revision when replacing. Previous approved source bytes remain.
`export-preview` emits `TEST_ONLY` metadata with no Engine/LFX pins and
never produces a runtime release or changes any game repo.

NOTE: a receipt is an audit note, not identity-verified owner approval.
Additional real human review/rights and signed release gates are mandatory.
