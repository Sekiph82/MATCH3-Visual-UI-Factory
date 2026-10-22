# VUF-M01 | Five-title, 17-surface, 8-state, 28-screen Source Matrix

Status: **DRAFT SOURCE ONLY, NOT OWNER APPROVED, NOT ENGINE RUNTIME BOUND**.

## Real upstream provenance

Read-only public Engine source evidence, pinned Git blobs on the
observed MATCH3_ENGINE `main`:

- `PresentationUiContracts.cs`:
  `b7c3c05d0c073e40f8dc1c4799a8bc1d869100f6`, containing the
  canonical 17 `UiSurfaceKind` values and 4 `UiActionKind` values.
- `PresentationSurfaceContracts.cs`:
  `7598366d6eca3401ac461cb557ebd576fd09be72`, containing
  8 `PlayerSurfaceStateKind` values.
- Existing owner Coral 28-screen catalog:
  `schemas/coral-experiences.v1.json`, exact Git blob
  `7e1459c0262500be54b6bbaa658638338baf704a`.

These source pins **are not** proof of the Engine SDK UI objects,
runtime route registry, owner artwork, localization quality, legal
rights, policy activation or release.

## Independent VUF implementation

`factory/ui_composer/m01_surface_contract_matrix.py` reuses existing
M02 five-title draft profiles and the canonical 28-screen file.
It constructs one reproducible read-only packet containing:

- **680 surface-state rows** (5 draft titles × 17 Engine surface
  categories × 8 exact player-state enum values).
- **1,120 screen-state rows** (5 draft titles × 28 original Coral
  screen reference IDs × 8 states). Five non-Coral titles inherit
  *reference slots*, not imported live Coral game screens or art.
- Source-only candidate screen-to-surface taxonomy, including explicit
  missing-screen reasons where no canonical Coral experience exists.
- Candidate dynamic title/icon key, English-independent fallback marker,
  visible disabled reason, policy-off handling, action preview key.
  Every action and route is **disabled and unbound**.
- Canonical JSON SHA256 receipt for deterministic rebuild and strict
  reject-on-change `verify_m01_matrix` validation.
- Explicit false flags for engine action callbacks, reward grants,
  purchase/consent, owner art, device QA, player state and shipping.

This candidate DOES NOT enable buttons or define a new
`UiActionDefinition` on a live board. It cannot be used to grant a
purchase, reward or consent. Consent, Store, Booster and Settings
have explicit absent Canonical Coral direct screen slots, and may
need genuine game-sourced contract decisions.

To inspect the in-repository source candidate (prints summary JSON
only, does not write to disk):

```powershell
python -B -m factory.ui_composer.m01_surface_contract_matrix
```

## Test definitions and remaining gates

`tests/test_m01_surface_contract_matrix.py` adds **10** Python unit
tests for 28 immutable screen IDs, 680+1,120 unique tuples, theme
invariance, 5 off-policy screens, disabled/fallback route fields,
source hash, reproducibility, missing enum/screen and forged
owner action/approval flags.

The new M01 source and 10 tests are **AUTHORED, NOT OWNER-LOCAL TESTED**.
The most recent actual Windows Python suite passing 547 total,
538 PASS, 9 SKIP, and source-only Engine CRLF intake refers to
the **earlier `d7b80dd42ec92320f6b8654147f0a3f041080c75`** SHA,
not to these new M01 commits. Unity 187/187 EditMode refers to an
even earlier `11d7e6d` SHA; no new Unity assertion is claimed.

Original M01-001 and M01-002/003/004/008/012 remain OPEN pending:
fully real Engine UiSurfaceState/action/schema authority, localization
and icon/reward/consent bindings, genuine game-specific source assets,
Engine/LFX end-to-end accepted test receipt, Unity native consumer
screens and all owner signoffs. Do not check their root TASKS.md boxes
based on deterministic synthetic matrix alone.
