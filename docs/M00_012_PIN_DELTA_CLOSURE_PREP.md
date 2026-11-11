# VUF-M00-012 | M00 closure prep: Engine/LFX pin delta, licence, portability

**Status: CLOSURE PREP ONLY — builder evidence, not independent PASS.** Row
VUF-M00-012 stays `[ ]` until a separate read-only QA reviews this note and
the owner-reserved gates below. Pins in `factory/integration/m00_api_freeze.py`
were **not changed** (no TASKS line authorizes a re-pin).

- VUF tested source: `e590b0449ef31c54642281dc46cbd64be2d76a06` (origin/main at prep time)
- Date: 2026-11-12; Windows 11, Python 3.12.10; **no Unity run** (machine busy, not required for this read-only diff)
- Upstream read-only (no fetch/write into upstream checkouts; `git ls-remote` confirmed local refs equal live GitHub `main`):
  - Engine `Sekiph82/MATCH3_ENGINE` origin/main `743c3454e9b8e0c6a8ebf366a2dfa81db08dc45e` (2026-11-12, 568 commits after pin)
  - LFX `Sekiph82/Match3-Level-Factory` origin/main `7bb65041a30039684c2ae5beda3601786e44978c` (2026-11-11, 111 commits after pin)

## 1. Frozen M00-001 pins vs current upstream

| Pin | Frozen (M00-001) | At upstream head | Result |
|---|---|---|---|
| Engine commit | `9af6e16e…` | ancestor of `743c345` | linear, no rewrite |
| `Runtime/PresentationUiContracts.cs` | blob `b7c3c05d…` | blob `b7c3c05d…` | **UNCHANGED** (17 UiSurfaceKind, 4 UiActionKind) |
| `Runtime/PresentationSurfaceContracts.cs` | blob `7598366d…` | blob `7598366d…` | **UNCHANGED** (8 PlayerSurfaceStateKind) |
| `Runtime/PresentationVisualContracts.cs` (M3P1 `PresentationEventKind` 0..6 used by `cross_factory_contract.EVENT_CUES`) | blob `400b3cd3…` | blob `400b3cd3…` | **UNCHANGED** |
| LFX commit | `d8d0b37c…` | ancestor of `7bb6504` | linear |
| `Assets/Match3Factory/Editor/LevelDraftJson.cs` | blob `ae9acff7…` | blob `ae9acff7…` | **UNCHANGED** (31 root / 10 cell / 3 goal keys) |

Engine `Packages/com.match3.engine` diff `9af6e16..743c345`: **516 files added, 0 modified, 0 deleted** — strictly additive; `package.json` still `version 0.1.0`, `unity 6000.6`. LFX diff `d8d0b37..7bb6504`: 55 added / 13 modified files, none in the frozen `LevelDraftJson.cs`.

Commands (reproducible, read-only):
```
git -C <engine> ls-tree -r <sha> | grep -E "PresentationUiContracts.cs$|PresentationSurfaceContracts.cs$"
git -C <engine> diff --name-status 9af6e16 743c345 -- Packages/com.match3.engine | cut -f1 | sort | uniq -c
git -C <lfx>    ls-tree -r <sha> | grep LevelDraftJson.cs$
git -C <repo>   merge-base --is-ancestor <pin> <head>
```

**Conclusion:** every surface VUF froze in M00-001 is byte-identical at current upstream heads. No VUF code change is forced by upstream drift.

## 2. New upstream surfaces relevant to VUF (not consumed yet, not pinned)

| Upstream item | File @ `743c345` (blob) | What it is | VUF impact |
|---|---|---|---|
| ENG-M20-010 content metadata envelope (`IMPLEMENTED_PARTIAL`, QA PASS @1b606cf) | `Runtime/LiveOps/ContentMetadataReceiver.cs` (`6c0ad6dd`) | Producer-neutral JSON envelope `schemaVersion "1.x"`, `producerId`, `gameId`, `items[] {contentKind World/Level/Event, contentId, contentVersion, payload, payloadSha256}`; fail-closed on unknown and monetization/credential/PII keys | VUF does not produce/consume it. Any future VUF metadata (theme/skin per level) must NOT ride in this envelope's payload (unknown keys reject unless `x-` prefixed). LFX does not yet emit it (no `producerId`/`payloadSha256` in LFX `7bb6504`; Engine row lists LFX-M12..M14 parity NOT_IMPLEMENTED). |
| ENG-M20-014 journey preview (`IMPLEMENTED_PARTIAL`, re-review PASS @1b606cf) | `Runtime/LiveOps/JourneyPreview.cs` (`3daf6be9`) | `JourneyStripView` schema `journey-preview/1.0`: 10-node strip (`Completed/Current/Locked`, checkpoints), `NextLevelTeaser` (moves, objectives, obstacleIds, `NewObstacleIds`), status `Active/EndOfContent/ContentGap/NoContent`; explicitly no scores/prices/offers | Natural data source for VUF WorldMap/Home surfaces (`UiSurfaceKind.WorldMap` unchanged). Engine row: "UI NOT_IMPLEMENTED". A VUF view-only binding would be a NEW consumer surface needing its own pin; recommend deferring until ENG-M20-014 closes. |
| ENG-M20-006 feature flags (`IMPLEMENTED_PARTIAL`) | `Runtime/LiveOps/FeatureFlagGate.cs` (`9b558931`) | `LiveOpsFeature {TimedMode, EndlessMode, WeeklyPersonalBest, SeasonalEvent, CatchUpReward, TournamentMode}`; Wonder_Pop: tournaments prohibited, consent non-relaxable | VUF screens for these features must render a disabled/fallback state when the gate is off; existing M01 explicit-disabled fallback rows already model this (`Disabled` state). No VUF change needed now. |
| ENG-M20-015 alternative modes (Engine TASKS still `PLANNED`, but source exists) | `Runtime/LiveOps/AlternativeModes.cs` (`97938a7f`) | `GameModeKind {Classic, TimeAttack, Endless}`, template schema `alt-mode/1`; `AlternativeModeGate` routes TimeAttack/Endless through FeatureFlagGate | No VUF surface exists for mode select/timer HUD. Not in the 17 `UiSurfaceKind` values — a future Engine UI-surface change would be a real pin break (re-freeze + M01 matrix rebuild). Watch item. |
| Family-safe / Wonder_Pop policies | `GameBusinessProfiles.cs` (`903571b7`), `Privacy/ChildProfileRestrictionsGate.cs` (`d8b73b6f`), `Analytics/PresentationAnalyticsGate.cs` (`e78659d5`), `Commerce/KidProfileGate.cs` (`d4f5e891`) | All 5 titles `GeneralAudience`/OwnerApproved (owner 2026-11-10); Wonder_Pop ads/telemetry/monetization OFF, remote-config override prohibited, presentation analytics prohibited | VUF `docs/style_bibles/Wonder_Pop_STYLE_BIBLE_SOURCE_DRAFT.md` and `validate_design.py` (`no_child_public_social`) are **stricter** than, and consistent with, the Engine policy. No "ages 5–12" assumption found in VUF source (`git grep -niE "5[-–]12"` outside history docs: none). No change required. |
| Engine name collision | `Runtime/Analytics/PresentationAnalyticsGate.cs` | Second `enum PresentationEventKind` (10 analytics values) in namespace `Match3.Engine.Runtime.Analytics`, distinct from visual `Match3.Engine.Runtime.PresentationEventKind` (7 values, M3P1) | Any future VUF C# `using Match3.Engine.Runtime.Analytics;` would make the name ambiguous. VUF Python pins ordinals by value only — unaffected. Note for future Unity consumer code. |
| M3P1 codec | `Runtime/NeutralVisualReceiptCodec.cs` (`8e1be85c`, added `4d67cd1` 2026-10-19, after pin) | Wire VUF already reads (`factory/integration/cross_factory_contract.py`) | **Consumed but unpinned by M00-001.** Recommend recording this blob in a re-pin. |
| LFXV1 visual handoff | LFX `Assets/Match3Factory/Editor/LevelDraftVisualHandoff.cs` (`d341b147`, added `dcdfc70`/`2684a0b`, after pin) | Wire VUF already reads; DTO field set (13 + 5 auth-false flags) matches `cross_factory_contract.read_lfxv1` key set exactly at `7bb6504` | **Consumed but unpinned by M00-001** (freeze file already notes "added AFTER d8d0b37"). Recommend recording this blob in a re-pin. |

## 3. Licence checks

- VUF third-party code: only `third_party/UnityUIExtensions/` with `LICENSE.md` (BSD-3-Clause) present.
- Rimaethon (CC BY-NC-ND): appears only in deny-policy code/tests (`m00_api_freeze.py`, `tests/test_m00_api_freeze.py`, `tests/test_donor_first_visual_contracts.py`); no imported Rimaethon source/assets.
- Engine and LFX: no LICENSE/NOTICE at repo root at either head (internal proprietary, read-only reference — as recorded in M00-001). Unchanged.
- Original/licensed art, fonts, creator receipts: **owner gate, NOT verified here.**

## 4. Windows / Unity portability checks (mechanical)

- `ProjectSettings/ProjectVersion.txt`: `6000.6.5f1 (3ff58d469c8a)`; Engine and LFX heads also `6000.6.5f1`; Engine package `unity: 6000.6`.
- `Packages/manifest.json`: only `com.unity.test-framework 1.8.0` + `file:../unity_package` (relative; no absolute or cross-repo path dependency).
- Tracked files: 0 symlinks, 0 case-insensitive path collisions, longest tracked path 72 chars.
- No hard-coded `C:\Users`, `C:/Users` or `/home/` paths in tracked `.py/.cs/.ps1/.json`.
- Python suite and `scripts/run_source_checks.ps1` results: see `docs/M01_012_M04_009_EXECUTION_EVIDENCE.md`.
- **NOT RUN:** Unity EditMode/PlayMode on this SHA, macOS/Linux, physical device.

## 5. Recommendations (not applied)

1. Keep M00-001 Engine/LFX pins: frozen contracts are byte-identical at upstream heads.
2. Optional re-pin (owner/master decision): add blobs `NeutralVisualReceiptCodec.cs 8e1be85c…` (Engine) and `LevelDraftVisualHandoff.cs d341b147…` (LFX) because VUF already consumes those wires.
3. Do not bind VUF to ENG-M20-010/014/015 until those rows close; then add explicit pins.
4. M00-012 cannot honestly be `[x]` yet: requires independent QA of this note, ENG-M24 (0/12 checked at `743c345`) and LFX-M14 (all open at `7bb6504`) are still open, so "final Engine/LFX API pins" do not exist yet.

## Owner-reserved / blocked

Final Engine 1.0 / LFX 1.0 pins (ENG-M24, LFX-M14), owner licence/art rights, Unity GUI and device portability, Drive 05_EVIDENCE upload (Drive not connected in this session — local/GitHub note only).
