# MATCH3 Visual & UI Factory | TASKS.md

**Status:** VUF R20 CONSOLIDATED FEATURE BATCH SOURCE / VF-08 TYPOGRAPHY, VF-07 LOCALE COVERAGE, VF-09 EVIDENCE BOARD. NEW R18-R20 TESTS AWAIT ONE BATCH LOCAL RUN. LAST ACTUAL R17 C007: 172 PYTHON (165 PASS/7 WIN SYMLINK SKIP), UNITY 21/21 PASS AT f6984497. GUI/DEVICE/ART OPEN.
**Repository:** Sekiph82/MATCH3-Visual-UI-Factory
**Local folder (owner-reported, never modified by this planning file):** C:\Users\sekip\Desktop\GAMES\MATCH3 GAMES\MATCH3-Visual-UI-Factory
**Authority:** This root TASKS.md is the only lifecycle tracker in this repository; ChatGPT alone writes auditable task statuses. Keep full prompts, Codex logs, independent audits, and evidence in designated Google Drive project folders, not in GitHub coordination files.

## VUF-R13-C001 | CODEX LOCAL TEST VERIFICATION | BLOCKED / EMPTY LOCAL CHECKOUT / TESTS NOT RUN

**Prompt:** https://docs.google.com/document/d/1mnfSEvkx7j65gOkOBT5elYWEn80btPA8n5gZbzfe17M/edit
**Owner delegation:** Codex is authorized to test the existing Visual Factory checkout using local Python 3.11+ and actual Unity 6000.6.5f1 without running GitHub Actions or other billed CI. Necessary small VUF-only error fixes and tests are permitted with non-destructive Git discipline; no local cleanup, reset, duplicate clone/worktree, paid API, original artwork modification, Engine/LFX/game writes, or broad feature work.
**Actual evidence required:** clean source SHA, Python suite and guards, real Unity Editor import/compilation, eight authored EditMode test cases, explicit failures/skips, cautious manual window/prefab/VFX/atlas checks and external small logs/XML. The status remains OPEN until Codex returns logs for independent review. ChatGPT alone updates this TASKS.md status. The only previously verified hosted baseline is R05 66/66 at SHA `10a1b3bc09bef1238ced23fc54b9646e65369343`; this does not verify R08..R12.
**Prompt/storage policy:** full prompt and future Codex log reside in the project's Google Drive folders, not as separate Github coordination trackers.
**Actual 2026-10-15 Codex preflight:** Expected local folder exists but is EMPTY (no .git, TASKS.md or scripts). Python 3.12.10 and Unity 6000.6.5f1 are present; Python 0 and Unity 0 tests ran; both NOT RUN. Remote main was ec29c6e1fdede5fe5038fc71cd3ae653469a1cd0 when checked. Owner evidence: C:\\Users\\sekip\\Documents\\MATCH3_TEST_EVIDENCE\\VUF-R13-C001\\VUF-R13-C001-preflight-blocker.txt, SHA256 41C0CA3DF173D533B78AF4DC500E8D2540C3F52BD7C29C03BD3987755F25358C. No modifications or cloned checkout. Do not claim PASS from this preflight.

## VUF-R13-C002 | EMPTY CHECKOUT BOOTSTRAP AND SOURCE TESTS | COMPLETED / 7 OS SKIP / GUI OPEN

**Codex prompt:** https://docs.google.com/document/d/10OZOIedi5uA7Y4VvDCP93sUXb6647rm1e8u4tCdV-uY/edit
**Scope:** Verify the exact existing owner folder is empty including hidden entries, not a symlink or junction, and then permit ONE non-destructive git clone of `Sekiph82/MATCH3-Visual-UI-Factory` main directly into that same folder. This authorization overrides C001's 'no clone' rule ONLY for this verified truly empty destination. No cleanup, deletion, reset, force, duplicate clone/worktree, downloads/installs, paid GitHub Actions or unrelated project modifications.
**Next:** immediately run all previously requested C001 local Python, Unity Editor + EditMode and selected actual GUI/prefab smoke tests; fix minimal verified errors and rerun at exact final SHA. Keep evidence outside Git and report exact counts. C002 is OPEN pending real Codex results, independent review and owner acceptance. ChatGPT manages this sole TASKS.md lifecycle tracker.

## VUF-R13-C003 | LOCAL VERIFIED SOURCE PUSH | COMPLETE; GRAPHICAL QA BLOCKED

**Codex evidence:** https://drive.google.com/file/d/1ySBukG50NnjYQ7rlQ2YpUqMYu3ZiHB1v/view
**Published tested source:** `796a84b38e2325910b45898e0bd55ddbcb911236` on GitHub `main`, matching user-reported local main after normal non-force push; zero ahead/behind. ChatGPT confirmed GitHub HEAD at this exact SHA. Three scoped repair commits published. GitHub Actions remains workflow_dispatch only; last seen hosted runs are old R05.
**C002 real local test evidence (reused by C003 without code change):** Python 3.12.10 reported **132 executed, 125 PASS, 7 Windows symlink SKIP, 0 fail/error**. Real Unity 6000.6.5f1 import and **8/8 EditMode NUnit PASS**, no reported compiler error/markered warning. The uploaded C002/C003 Codex logs are evidence. Raw Windows log/XML SHA hashes were supplied by Codex but not recomputed independently by ChatGPT.
**C003 unresolved:** Codex session had no native Windows GUI; Visual Factory Dashboard, 28 screens, UI Composer, Production Queue, Sprite Clip, Atlas Inspector, Particle Lab, manual QA, responsive PlayMode and real iPhone/Android device/art review all **NOT RUN**. First-import 24 untracked files were preserved with 24/24 SHA-match evidence: 21 ProjectSettings YAML, two stable Unity .meta GUID files and packages-lock.json. Two untracked metas threaten portable import GUID stability until selectively versioned. No files were deleted, no paid CI.
**Milestone authority:** Source test success is NOT independent production VUF-M00..M11 PASS. Engine/LFX final dependencies and owner art/device approval remain open.

## VUF-R13-C004 | OFFLINE HEADLESS UNITY INTEGRATION AND SAFE PROJECT METADATA | SOURCE TEST COMPLETE; VISUAL QA OPEN

**Codex task:** https://docs.google.com/document/d/1KgA5R4QmBUR4AHNSCZhEdUk1XQT3P6NehMze_h4MHC8/edit
**Purpose:** No need to repeat inaccessible native GUI attempts. Safely fast-forward existing local checkout to current `main` (including this TASKS.md status update) only if no local tracked/untracked conflicts; classify existing 24 first-import files, preserve stable GUID sidecars and selected portable settings without blanket git adds. Add *actual Unity batchmode EditMode integration tests* for in-memory uGUI screen hierarchies, candidate markers and disabled Buttons, modal/mode/page layouts, five profiles, reduced-motion tween, atlas geometry, and genuine ParticleSystem source setup where testable. The interactive visual/device/owner gates remain NOT RUN until a real graphical session is available. Test real Python and Unity at final code SHA before normal non-force push.
**Safety:** No GitHub Actions/paid API, deleting caches, files or 24 untracked files, force/reset/clone/worktree, or changes to Engine/LFX/game repos. ChatGPT maintains TASKS.md status and later reviews Codex evidence.

## VUF-R13-C004 | CODEx ACTUAL LOCAL RESULTS AT PINNED SHA a4493cd8

**Owner-provided full Codex report (fetched):** https://drive.google.com/file/d/1bkHT5J3VvnYA6x5GEsIpCAaN4C9gL0XO/view
**Actual published SHA:** `a4493cd8192b7c7744cc1e8c18034aae28492d9d`; independent GitHub connector confirmed this remote main.
**Reported real Windows local tests:** Python 3.12.10 **132 executed, 125 PASS, 7 OS symlink SKIP, 0 FAIL/ERROR**; five VFX presets and structure/manifest validators PASS. Unity 6000.6.5f1 real EditMode **13 PASS, 0 FAIL/SKIP/INCONCLUSIVE**; 140 in-memory Coral ID × theme constructions, ParticleSystem presets, Atlas geometry, sprite animation, production queue and tween checks. C004 tracked 24 previously generated project settings/metas/package lock files individually, documented by matching SHA and no deletion. This does not prove GUI visual quality.
**Remaining open:** Native Unity GUI windows, rendered candidate assets, responsive real phone/tablet behavior, physical device tests, complete premium artwork and owner legal/visual acceptance NOT RUN. This is not independent VUF milestone closure.

## VUF-R16-C006 | LOCAL PYTHON + UNITY QA VERIFIED; CREATIVE GATES OPEN

**Full Codex evidence:** https://docs.google.com/document/d/1OkmMx9cn_ik0z7b4LdZlM9PKQrqjFFZVh8DzqrtQ1hg/edit
**Tested and published final SHA:** `05566214e6bae0561885f46655f0caf9492c344f`. Python 3.12.10 **170 total, 163 PASS, 7 Windows symlink SKIP, 0 fail/error**; Unity 6000.6.5f1 EditMode **18/18 PASS**, no reported compiler CS errors or warnings. C006 fixed candidate sprite bbox test expectation and hardened Unity pixel-health report against malformed alpha/bbox/contrast metrics and forged rights/approval status; optional palette exporter shape covered. Five VFX presets, design contracts, TEST_ONLY manifest and 33 GUIDs checked. This applies ONLY to SHA 05566214 and is not R17 evidence.
**Remaining gates:** real native Unity GUI, rendered typography/materials, physical devices, legal source-rights and creative/owner approval NOT RUN; no independent production milestone PASS. No GitHub Actions or paid CI.

## VUF-R20 | FIVE-GATE REVIEW EVIDENCE BOARD | SOURCE / COMBINED TEST GATE OPEN

**New tool:** `VufReadinessBoardWindow.cs` adds read-only Factory Dashboard access to optional original/unapproved candidate, VF-09 pixel QA report and VF-07 locale coverage report. It validates input formats through existing typed parsers and audits five synthetic viewport geometry/font/contrast cases. Produces counts/warnings and permanently **OPEN** human source-art rights, owner visual quality, actual Unity GUI, physical iPhone/Android, and independent Engine/LFX integration gates. Never writes, signs off or ships anything.

**R18-R20 combined source changes:** R18 TextGenerator typography/contrast lab (5 new Unity NUnit + 3 Python source methods); R19 external EN/TR draft translation auditor and read-only Unity coverage window (18 Python + 3 NUnit); R20 cross-module Review Evidence Board (3 Python + 3 NUnit). In aggregate **24 new Python + 11 new Unity test definitions**, so at R20 sources expect **196 Python unit methods and 32 Unity EditMode methods**, **NOT verified runs**. No per-small-feature Codex dispatch was made; schedule ONE bulk local Windows Python+Unity run at the end of this batch. Historical R17 C007 at SHA `f6984497`: Python 165 PASS + 7 OS symlink SKIP, real Unity 21/21 PASS. All current new code remains UNVERIFIED until exact-SHA local logs.

**Owner product goals still open:** full original premium visual asset creation, editable art and animation pipeline, per-game finished screens, 3D/skeletal motion, shader/material fidelity, multilingual language design, live GUI/device performance and rights evidence. These review tools are infrastructure, not the final art factory.

## VUF-R19 | OFFLINE DRAFT EN/TR COVERAGE AND UNITY READ-ONLY REVIEW | SOURCE / BATCH TEST OPEN

`factory/ui_composer/locale_audit.py` inspects owner-supplied external EN/TR draft heading JSON for exactly 28 canonical Coral screen keys, validates schema/stage, UTF-8, hidden/BiDi controls, duplicate JSON keys, matching named placeholders, short/long copy length heuristics and feature-policy-off metadata. Incomplete translations generate coverage/missing/long-copy warnings rather than false complete status; no translations generated, sent to any provider, approved or applied to runtime UI. Records SHA-256 of canonical contract and external source. Writes only optional new non-overwritten JSON outside Git.

`unity_package/Editor/VufLocaleCoverageWindow.cs` is a read-only Unity TextAsset report viewer; validates two locale coverage maps, 28 stable canonical keys, five OFF-policy screens, draft stage and no enabled game bindings. Three Unity EditMode methods and 18 Python unit methods authored, with stable Editor .meta files, dashboard entry and source structure guard. **R18 + R19 combined source definitions:** 193 Python methods, 29 Unity EditMode methods. Neither new R18 nor R19 source has been executed by owner-local Unity yet. Old R17 evidence at SHA `f6984497` was Python 172 discovered/165 PASS/7 OS SKIP and real Unity 21/21 PASS.

**Execution policy:** Continue coding the next related Visual Factory component before ONE combined Codex batch regression, not a new test prompt for every small change. No GitHub Actions, paid CI, local deletes/cache clearing, cross-repo modifications, original-art rights or owner visual acceptance claims. ENG-M24/LFX-M14 upstream production bindings still blocked.

## VUF-R18 | TYPOGRAPHY & CONTRAST LAB | SOURCE IMPLEMENTED, LOCAL UNITY TEST OPEN

**Real previous Codex C007 evidence:** https://drive.google.com/file/d/1ZQ3Gh87ISLbdRgcXmpXmFemjbp1Ff8bp/view. Previous exact SHA `f6984497196d374fbfc0b0d0c50b10cc7a417444` reported clean main 0/0, Python 172 total / 165 PASS / 7 Windows OS symlink SKIP and actual Unity 6000.6.5f1 EditMode 21/21 PASS. Five VFX presets, Style Bible five profiles, 28 IDs and 35 GUIDs also passed. Unity GUI/render/phone/owner visual and commercial rights not checked.

**New VF-08 source:** `VufTypographyAudit.cs` uses Unity TextGenerator preferred-height metrics and approximate anchors for five synthetic screens. Offers possible text clipping and 4.5:1 approximate color-contrast flags; missing fonts/translucent or absent backgrounds are UNKNOWN, not automatically acceptable. `VufTypographyLabWindow.cs` adds a read-only Unity Editor screen, linked in the dashboard. Never mutates prefab, Engine state, files, approvals, source art or game binaries. Five new EditMode methods in `VufTypographyEditModeTests.cs` and three Python source contract checks in `tests/test_typography_contracts.py` authored. **Expected source counts: 175 Python methods + 26 Unity NUnit methods; NOT executed at current R18 SHA**. No fake visual acceptance.
**Work model:** Continue source development in batches; do not ask Codex to run every small change. Group R18 with subsequent functional scope for ONE future full Windows/Unity integration test gate. Github Actions manual only, zero paid CI, no local cache deletion or original art replacement.

## VUF-R17-C007 | LOCAL CODEX PYTHON/UNITY REGRESSION | ASSIGNED / NOT RUN

**Codex prompt:** https://docs.google.com/document/d/1elh_L9qGItsScntDno1ib_Ri8bC4UBED7aE1RL2pHBI/edit
**R17 source baseline:** `312caeeb0bddc18d26507c632b3e0682a37236c6`. Safely fast-forward existing clean local checkout, run full Python test source suite (172 method definitions) and genuine Unity 6000.6.5f1 EditMode (21 NUnit method definitions) at exact source SHA, preserve 7 Windows symlink SKIPs if environment unchanged. Fix only observed VUF defects, rerun both suites after final commit, ordinary fast-forward Git push if appropriate; no hosted GitHub Actions/paid CI, no deletes or cross-repo changes. No GUI/device/owner translation or artistic approval claimed. ChatGPT alone edits lifecycle statuses.

## VUF-R17 | VF-07 STATE/COPY VARIATIONS | SOURCE BUILD / UNITY TEST OPEN

**Builder:** `unity_package/Editor/VufReviewStateCatalog.cs` defines eight review-only states and three non-shipping text modes (en, Turkish draft and expanded layout stress). The 28-Screen Shell Builder applies the selected preview-only copy to new, non-overwritten candidate uGUI prefabs, explicitly labels the mock state `NOT GAME STATE`, preserves policy-off feature gates and will not operate if any candidate Button is already interactable or has serialized event bindings. Turkish Home/Gameplay are visibly draft; all other titles remain clearly marked draft pending localization. This is NOT a production translation layer, Engine state, actual reward, game state or new artwork.
**Tests authored:** `VufReviewStateEditModeTests.cs` adds 3 Unity EditMode NUnit methods (current new source **21 authored**, not verified), covering all 28 IDs × 8 states × 3 preview locales = 672 in-memory variant applies, unknown mode rejection and five title palette invariance. `tests/test_screen_shells.py` adds two source-level checks (Python **172 authored** total). Stable .meta GUIDs, Unity package structure guard, README and module documentation updated.
**Execution gate:** Safely fast-forward existing owner-local checkout and run free local Python + real Unity 6000.6.5f1 EditMode suites at the exact final R17 SHA, fix real errors and rerun; hosted GitHub Actions remain dispatch-only. No silent status acceptance, local deletion/cache cleanup or paid creative APIs. GUI, rendered layout under localization, true translation, iPhone/Android and owner aesthetic/rights remain OPEN.

## VUF-R15-C005 | CODEX LOCAL PYTHON/UNITY REGRESSION | VERIFIED AT 9dcca802; GUI OPEN

**Codex test/remediation prompt:** https://docs.google.com/document/d/1Kf36IB9qHSlbpfj_XCcgjwdub8a2Mpgu5tRorsgDbJk/edit
**Source baseline:** R15 published code SHA `61184a6e4c9d1b70764cde17d378d81b9e763ef6`. Safely fast-forward existing owner checkout only when clean; run REAL local `scripts/run_source_checks.ps1` (151 Python source-defined methods, 7 Windows OS symlink SKIPs possible) and `scripts/run_unity_editmode.ps1` (16 Unity NUnit source-defined methods) at exact final SHA, including R14 offline batch and R15 responsive wireframe. Repair only observed VUF problems, retest after final commit, normal non-force Git push if needed. No paid GitHub Actions, deletes, cache clearance, other repo modifications or owner art/device approval claims. ChatGPT retains sole lifecycle status control.

## VUF-R15 | VF-08 STATIC RESPONSIVE WIREFRAME AUTHORING | CURRENT UNITY TESTS OPEN

**New Unity Editor source:** `unity_package/Editor/VufResponsiveGeometry.cs` models anchored RectTransform child positions inside synthetic screen presets and the estimated SafeAreaFitter inset. `VufResponsivePreviewWindow.cs` draws a read-only overlay of actual candidate prefab text/button rectangles; highlights candidate-only marker, policy-off screens, potential safe-area escape and too-small tap targets. Five synthetic phone/tablet/landscape presets are included. Dashboard links to this tool. All new scripts include stable .meta GUIDs and package structure source guard updates.
**New tests authored:** three NUnit EditMode tests (existing C004 13 plus these three => **16 defined, NOT 16 verified**) cover 28 Coral layouts × five simulated devices (140 cases), a tiny unsafe unbound Button and five draft title Home variants. No OS screenshot, actual Unity UI render, real mobile safe-area, dynamic text layout or owner visual approval is implied.
**Cumulative source test definitions:** R14 added 19 Python methods beyond the old 132; **151 Python test methods defined**, and R15 extends Unity methods to **16**. They require actual local tests at the new exact HEAD. Last verified Codex C004 evidence remains Python 125 PASS + 7 OS SKIP, real Unity 13/13 PASS at SHA `a4493cd8`, before R14/R15.
**NEXT:** safely fast-forward owner checkout to R15 HEAD and run free Python source suite and Unity 6000.6.5f1 EditMode source tests. Any new failures must be fixed and rerun at final SHA. Keep CI workflow manual-only and continue other VF-08 localization/render QA after this test gate.

## VUF-R14 | VF-03 OFFLINE BATCH CANDIDATE INTAKE SOURCE DEVELOPMENT | LOCAL TEST GATE OPEN

- `factory/asset_generator/offline_batch.py`: offline source-root constrained, link/junction/traversal rejecting manifest of 1..64 original/licensed PNGs, full CRC/dimension checks, per-item pinned SHA256, 64MiB aggregate memory ceiling, five-profile asset-key isolation and deterministic stale-baseline dry-run `plan_sha256`.
- `AssetCatalog.ingest_batch`: explicit `--commit` only, checks the unchanged original plan and catalog revision count; single SQLite transaction for all candidate revisions, write-once SHA256 content-addressed PNG masters, NEVER updates active/approved revisions. A failed transaction may leave unreferenced immutable blobs (no automatic deletion).
- `tests/test_offline_batch.py`: 19 added source-defined methods for all-or-nothing DB behavior, dry-run zero writes, stale receipt/replay, changed originals, rights/schema/path rejection, linked-source simulation, CRC and CLI. Latest reported C004 test results apply ONLY to old SHA `a4493cd8`; these new 19 tests and modified catalog **NOT YET EXECUTED**.
- R14 carries NO paid provider, cost grant, automated owner approval, Unity game integration or production release. Do not call this VF-03 or VUF milestone PASS before real local Python regression and independent source audit. Last verified Unity EditMode remains 13/13 on C004 SHA.

## PROPOSED execution sequence and release boundaries

**OWNER ADOPTED R04 (2026-10-15):** The full ten-module VF-01..VF-10 Visual/UI Factory plan is adopted, and ChatGPT is authorized to implement **stand-alone VUF repository source and isolated verification now**, beyond the earlier R03 setup-only exception. The final independently audited Engine and LFX release gates still block shared contract freeze, real Engine replay/level bindings, five-title integration, production asset package publishing and VUF-M11 release. Never write art or Factory behavior into the Engine, change LFX/game repos, claim creative approval or modify owner-local Windows files without an actual safe access/sync path. No paid image API, surprise subscription, destructive cleanup, or automatic commercial image rights assumption. **VF module progress is separate from VUF milestone audit status.**

1. MATCH3_ENGINE: ENG-M00..ENG-M24 independent PASS/CLOSED. Engine defines five neutral GameProfiles, player-facing surface/state interfaces, immutable presentation events, responsive layout and stable asset keys. No finished branded game assets or Game-repo implementation are required for engine acceptance.
2. Match3-Level-Factory: LFX-M00..LFX-M14 independent PASS/CLOSED. LFX-M08 preview uses original neutral placeholders and five mock themes until Visual Factory begins, and exports accepted sample level packs/fixtures.
3. MATCH3-Visual-UI-Factory: VUF-M00..VUF-M11 independent acceptance for the reusable production pipeline, complete five-theme sample vertical slice, Unity runtime bindings, asset provenance, and deterministic export. **VUF v1 is a tested production tool, not a false claim that every future game's final art is approved.**
4. Five branded game repositories, each G00..G12: all title-specific production assets are made through versioned VUF contracts and independently reviewed at G01; scenes/prefabs/animations are integrated at G02; game-specific device and owner visual acceptance stays at G09–G11. Subsequent VUF patches are individually versioned, backward-compatible, independently audited, and pinned by consuming game repos, never silent changes to a completed prior phase.

**Resolved contract-specific Engine dependency (R02):** ENG-M09-014 now records owner-authorized **PASS/CLOSED_R02** for symbolic five-profile x 17 surface x 8-state neutral contracts, without branded artwork. Evidence in Engine TASKS.md and independent audit https://docs.google.com/document/d/1rJKb3vfCXfyaokeT3E7cDs-roOGOfxk7S2hLraxDgn4/edit . This closes the old M09-014 circular design contradiction only. **The complete Engine ENG-M24 and Level Factory LFX-M14 final independent PASS gates are still open**, so real inter-repo integration and release must wait.

## OWNER-ADOPTED TEN MODULES | VF-01..VF-10 vs. VUF milestones | R04

Each VF number is a functional module. VUF numbers are milestone/independent audit gates; neither numbering system replaces the other. `docs/ARCHITECTURE.md` describes technical boundaries, not lifecycle status.

| Functional module | System role / required acceptance | Primary VUF phases | Current verified scope |
| --- | --- | --- | --- |
| VF-01 Visual Director / Style Bible | Five distinctive style bibles, design tokens, silhouettes, original/language/age rules, owner sample review | M00/M02/M03/M09 | Draft five-profile JSON + structural validators source, NO creative approval |
| VF-02 Asset Catalog / Versioning | Original/licensed SHA256 masters, candidate review, version records and explicit rollback | M00/M01/M04/M11 | Offline SQLite catalog, append-only approvals/restoration events, read-only five-game report and Unity Queue SOURCE; authenticated approval/Unity QA OPEN |
| VF-03 Modular AI / Batch Intake | External manual import first, optional paid API adapters default OFF, measured cost and provenance, no overwrite | M04 | Offline batch PNG candidate intake SOURCE with 64-item/64MiB budgets, SHA pinned originals, dry-run consent plan, SQLite all-or-nothing revision writes and 19 NEW UNVERIFIED unit methods; paid provider adapters OFF/not implemented |
| VF-04 Image Processing | Non-destructive alpha/crop/segmentation/masking/resolutions/atlas, preserve original SHA | M05/M06 | PNG trim/scale, external alpha keep/remove mask, deterministic no-rotation atlas candidate tools and Unity atlas inspector SOURCE; PSD layers, paint editor, GPU/Unity native SpriteAtlas NOT IMPLEMENTED; R07 tests open |
| VF-05 Animation Builder | UI tween, sprite/skeletal/3D clip methods, scrubbing/sprite sheet, frame/pivot/state/reduced motion | M07 | Sprite .anim builder, manual frame scrub/ping-pong/reduced motion Editor SOURCE; Unity compile, full skeleton/3D/tween workflows open |
| VF-06 VFX Lab | Shader/particles/audio/haptic triggers/combo chaining, interruption/replay/reduced motion | M07/M09 | Five candidate ParticleSystem preset prefab builder + 2D sketch SOURCE; shaders/audio/haptic GPU/replay/device QA open |
| VF-07 UI Composer | Layered interactive UI, 28 Coral experiences, five-theme design candidates and real state/locale binding | M03/M08/M10 | Seven standard UI archetypes, exact 28 Coral draft shells, 8 review-only state labels and synthetic EN/TR/stress copy, 5 draft profiles SOURCE. Real gameplay actions, full translations, art, GUI and real-device QA OPEN |
| VF-08 Responsive Preview | Safe areas, mobile ratios, tablet, touch accessibility and real-device evidence | M03/M08/M09 | Runtime SafeAreaFitter + NEW five-device synthetic RectTransform layout wireframe/read-only Editor audit with heuristic tap targets SOURCE; no actual Unity GUI/render/physical device/locale layout PASS |
| VF-09 Validation / Visual QA | Automated art/rights/render/perf + complete manual Sprite/VFX/UI Studio, separate owner/device PASS | M09/M10 | Independent atlas/mask original-to-output SHA/pixel verifier, manual prefab/atlas inspection SOURCE; newest tests/Unity/device performance unverified |
| VF-10 Unity Packaging / Release | Versioned UPM, SpriteAtlas, Animator, prefabs, Addressables optional, deterministic export/rollback | M08/M10/M11 | Local UPM package SOURCE and preview contract; no production export |

**Nine production output families covered:** (1) UI Screens, (2) UI Components, (3) Game Tiles incl. special/obstacle/booster, (4) Characters/mascots, (5) Environments/worlds, (6) UI/character/transition Animations, (7) gameplay VFX, (8) Rewards/collections, **(9) Marketing Assets (app icon, splash, store screenshots)**. The marketing export deliverables belong to VF-04 and VF-10 and must have separate platform aspect/dimension/rights QA and explicit owner acceptance. All families follow request -> candidate -> QA -> owner approval -> immutable versioned export -> Unity/consumer import -> device/release test. Real rewards remain Engine grant events only.

**Visual Production Dashboard:** one game selector and ten module states now exists as a truthful Unity Editor UI source; later shows candidate production queue, outstanding review, approved/active pins, exports and QA receipts. Each unavailable button/tab must display unsupported reasons, not imply functionality.

### Implementation sequence R04
1. **A | independent foundation (ACTIVE):** VUF-M00 toolchain, VF-01 initial draft style bibles, VF-02 external asset catalog/immutable approval, VF-03 offline import, portable UPM source and automated negative controls. Compile/test/audit before claiming PASS.
2. **B | independent creative tooling:** VF-04 non-destructive cleanup/alpha/atlas, VF-05 multi-format animation builder and VF-06 VFX templates with manual edit/playback and reduced-motion support; no game rules.
3. **C | interactive screen composing:** VF-07 runtime-backed layered UI, 28 Coral experience templates and five theme skins; VF-08 phone/tablet responsive/safe-area and EN/TR pseudo-long strings.
4. **D | comprehensive review:** VF-09 manual Visual QA Studio, animation/event/replay lab, deterministic diagnostics, asset licence/consistency/accessibility review, owner aesthetic approval separately from unit tests.
5. **E | downstream-gated packaging:** only AFTER full Engine + LFX independent PASS, exact pinned replay/level consumptions, VF-10 final Unity adapters, texture performance budgets, five-profile playable visual slices and real iOS/Android smoke acceptance at VUF-M10/M11.
6. **F | five branded game integration:** per-game G01 final character/screen approval and device QA; active VUF masters are immutable and require explicit reviewed supersession.

**Source layout:** `factory/{visual_director,asset_catalog,asset_generator,image_processor,animation_builder,vfx_builder,ui_composer,responsive,validators,export_pipeline}`; `games/` holds only five draft profile configs, NOT five app repositories; `unity_package/{Runtime,Editor,Samples~}`; `schemas/`, `tests/`, and sole root lifecycle `TASKS.md`. Big PNG/PSD/animation assets are external versioned content-addressed blobs, never bulk GitHub data. Individual unsupported modules remain PLANNED until genuinely developed.

## System boundaries

- Engine OWNS rules, immutable event/state semantics, profile IDs, screen/action routes, signed content contracts and fallback/permission policy. It never calls generative AI or imports title artwork into deterministic rule assemblies.
- Level Factory OWNS levels, seeds, playability, goals, verified sample level packs and themed preview data via neutral asset IDs; never produces or verifies premium artwork.
- Visual Factory OWNS brand-specific design tokens, component templates, approved original/licensed image generation, background layers, icon/tile/booster/obstacle sheets, animation and VFX bindings, 1x/2x/3x exports, runtime asset manifests, Unity art import scripts and independent visual QA. It does NOT implement match rules or mint rewards.
- Title repos OWN gameplay scenes, title story/content, imported frozen VUF asset pack versions and owner approval of final screens on actual devices.
- Visual factory uses ChatGPT for design direction, concept/master review and image creation where an actual supported image tool is available; Codex for code, automation, Unity export/adapters, test suites, and repeatable transforms. A ChatGPT subscription is NOT treated as a programmable image-generation API. All automated generation requires an explicitly available, cost-approved provider; manual artwork intake remains a first-class path.
- No new paid API, surprise subscriptions, desktop worktrees/TEMP growth, cache cleanup, or unapproved local changes. No generated artwork is accepted solely because an AI marked it PASS. Track licence, generation source/model if known, prompt/version, references, dimensions, alpha, SHA-256, rights/review and source-to-output mapping.

## Contract baseline

Each VUF output package carries: schema version, engine API version, level pack compatibility, game/profile ID, theme version, surface/component ID, state variant (Ready, Loading, Offline, Error, Owned, Claimed, Disabled, Pending where relevant), localization text binding, icon/action key, aspect/safe-area policy, accessibility shape/contrast/focus, animation/reduced-motion binding, asset source/licence/SHA-256, dependency hashes, generated artifact manifest and fallback keys. It must not embed runtime secrets or executable remote code. A screen is constructed from independently themed layers, buttons and actual localized text; a single flattened AI PNG must never pretend to implement tappable runtime UI.

## Owner-supplied Coral Rescue concept reference and screen inventory | 2026-10-15

**IMPORTANT: NO CORAL/GAME ART INSIDE MATCH3_ENGINE.** The owner shared three partial Coral Rescue concept sheets in ChatGPT (not a complete approved production pack). They may be visually reviewed as conceptual references ONLY when the gated Visual Factory or Coral Rescue G01 phase begins. Do not ingest them into Engine or Engine CI, copy them automatically from chat into GitHub, assert commercial asset licence/approval, or claim 28 finished game screens. Source image bytes have NOT been uploaded or incorporated by this TASKS change.

The owner specified **26 named Coral Rescue UI/game experiences**. Home and the core playable Gameplay/HUD are indispensable additional screens, yielding **28 total screen/experience IDs**, not 28 flat screenshots. A screen may be a page, playable scene, modal, event ceremony, overlay or mode. Reuse interactive Unity components, layers, localized runtime text and animation instead of baking controls into PNG.

| ID | Screen or experience | Reusable VUF visual work | Functional/age-policy authority |
| --- | --- | --- | --- |
| 01 | World Map / Bölüm Haritası | Scrollable layered ocean region map, level pins, paths, stars, locks | Engine level progression, Coral G04 |
| 02 | Level Start / Bölüm Başlangıcı | Objective panel, booster picks, Play CTA | Engine goal/inventory, Coral G02/G03 |
| 03 | Level Won / Zafer | 1/2/3-star results, animated reward, Continue | Engine results/reward ledger, Coral G02/G07 |
| 04 | Level Failed / Başarısızlık | Retry, heart status, conditional extra move | Engine failure/recovery, age/offer policy |
| 05 | Reef Restoration | Repair, cleaning, coral placement, ambient growth | Coral G04/G07 persistent progress |
| 06 | Marine Collection | Species cards, rarity and earned/locked tabs | Engine earned album, Coral G04/G07 |
| 07 | My Aquarium | Layered owner-customizable tank, decor and marine creatures | Coral G04/G07 new save-backed decor feature, requires game-specific implementation |
| 08 | New Region Unlocked | Ocean realm unlock reveal and ceremony | Engine unlock receipt, Coral G04 |
| 09 | Daily Rewards | 7-day rewards and Claim action | Engine claim-once ledger, Coral G07 |
| 10 | Tasks & Missions | Daily, weekly, story mission tabs and reward states | Engine task ledger, Coral G07 |
| 11 | Shop | Coin/gem only if wallet supports; boosters; offers | Engine entitlement, Coral G12; consent and real store products |
| 12 | Treasure & Rewards | Chests, reward ceremonies, transparency and collection states | Engine earned-only fairness, Coral G07 |
| 13 | Events Hub | Event cards, active/upcoming/expired and offline states | Engine LiveOps/age flags, Coral G12 |
| 14 | Season Pass | Free rewards and separately gated premium pathway | Not presumed implemented/allowed: Engine/Coral opt-in policy and verified commerce first |
| 15 | Endless Mode | Endless board entry, current and best score | ENG-M20-015, Coral G12-011 |
| 16 | Time Attack | Timed board and run result | ENG-M20-015, Coral G12-011 |
| 17 | Tournament | Optional bracket/ranking/reward view | Default OFF, no paid entry/wagering; ENG-M20/21 and age policy |
| 18 | Weekly Records | Week progress, verified best, historical badge | ENG-M08/20 personal records, Coral G12 |
| 19 | Friends | Eligible opt-in list, invites, verified heart gifts | ENG-M21 age/consent/privacy/abuse, disabled if ineligible |
| 20 | Leaderboard | Friends and event ranking, hidden/disabled states | ENG-M21 restrictions; no child public social |
| 21 | Player Profile | Achievements, stats, name/avatar and privacy | Engine achievement ledger and age/consent |
| 22 | Splash & Loading | Logo, ocean splash, loading/offline/retry | Coral G02/G08 startup flow |
| 23 | Tutorial | First three-level coachmark and swipe hint overlays | ENG-M10 and Coral G03; not standalone full-screen only |
| 24 | Pause & Settings | Pause modal plus settings view/toggles | Engine pause/resume and accessible settings |
| 25 | Out of Lives | True recovery countdown and available alternatives | Engine hearts, COR-G07 |
| 26 | Welcome Back | True capped catch-up reward state | ENG-M20-013, age limits, exactly-once grant |
| 27 | Home (required baseline) | Premium coral title Home layout and navigation | Engine neutral Home routes, Coral G02 |
| 28 | Gameplay / Level HUD (required baseline) | Real interactive match board, progress and boosters | Engine deterministic rule events, Coral G02 |

**Mandatory downstream mapping:** VUF-M01-002 maps each of these 28 experiences to the Engine's existing 17 typed `UiSurfaceKind` primitives, plus separate Coral page/overlay/mode IDs, action IDs and state applicability. Do NOT add 28 engine enum values or demand image pixels/creative master approval in Engine. The existing 5 x 17 x 8 matrix is a **symbolic interface coverage contract only**. VUF-M03 creates layered/reusable UI templates and VUF-M09 checks actual full/disabled/empty/loading/claimed/owned/offline/pending states when applicable. G01 signs off final original/licensed Coral art and G02/G09/G11 confirm functioning screens and on-device appearance. No dead buttons: disabled feature states must show an accessible reason.

## 2026-10-15 | R12 SOURCE IMPLEMENTATION / UI TWEEN + REDUCED MOTION | OPEN UNITY TEST GATE

- Added `unity_package/Runtime/VufUiTween.cs` for real presentation-only `CanvasGroup` fade, scaled/unscaled time, deterministic manual `Advance`, interruptible `Show/Hide`, and immediate reduced-motion mode. UI raycasts and CanvasGroup interaction are prevented until visible; underlying unbound Buttons remain disabled.
- Added manual `VufUiTweenInspector.cs` in Unity Editor with PlayMode Show/Hide and reduced-motion controls. The 28-Screen Shell Builder now attaches this runtime UI component to modal/ceremony/overlay candidate types only. No rule, rewards, inventory, saves or paid provider changes.
- Two Unity EditMode tests added to source, reaching eight authored test cases. The no-cost `scripts/run_unity_editmode.ps1` now requires eight passing zero-skip NUnit cases. Stable Unity .meta GUIDs and Python package structure contract amended. Source-defined Python methods increased to **132**.
- **Not executed/verified:** current R08..R12 local Python suite, actual Unity Editor/PlayMode UI tween fade and on-device behavior. Source code alone is not module acceptance. Full 2D skeletal/3D animation workflows remain open; latest independently verified Python CI was R05 66/66.
- No GitHub-hosted CI dispatch, Windows laptop changes, source cleanup, auto approval or production game integration.

## 2026-10-15 | R11 SOURCE IMPLEMENTATION / FIVE-GAME PRODUCTION QUEUE / OPEN AUDIT

- VF-02 `AssetCatalog.portfolio_report()` checks SHA integrity and reports five game profiles: pending candidate review, recorded approval counts, active masters, explicit restorations and up to 100 candidate IDs/SHAs for each title. No image pixels or raw local paths are included.
- `portfolio-report --output-file` creates a fresh UTF-8 read-only JSON report outside the Git repository and refuses to overwrite existing files.
- Unity Editor source `VufProductionQueueWindow.cs` consumes a manually imported report, validates five-profile consistency and displays each game's backlog without any approval/publish/game-mutation button. Dashboard links to it; stable Unity GUID and package source gate added.
- New Python tests: empty/candidate/approved/tampered portfolio reports, CLI UTF-8 output and no overwrite, plus read-only Unity source checks. Total is **131 test methods defined, not 131 PASS**; six Unity EditMode test cases remain unexecuted.
- R08-R11 still need real local Python/Unity 6000.6.5f1 tests at pinned commit. Last independently verified hosted tests were R05 66/66, not the new source. Automatic GitHub Actions remain disabled. No owner Windows, Engine/LFX or five-game repo changes.

## 2026-10-15 | R10 UNITY TEST HARNESS SOURCE / NO PAID CI / OPEN EXECUTION GATE

**Unity EditMode test harness authored (not executed):** the UPM package now contains `unity_package/Tests/Editor/Match3.VisualFactory.Editor.Tests.asmdef`, isolated by Editor platform and `UNITY_INCLUDE_TESTS`, plus six NUnit tests in `VufCatalogEditModeTests.cs`. Tests cover exact 28 Corona Rescue contract IDs and gate status, all five Style Bible palettes, policy-off social/events, candidate marker never auto-approved, ping-pong sprite frame sequence and invalid frame count. `unity_package/Editor/AssemblyInfo.cs` permits dedicated Editor test assembly friend access. All new Unity scripts/folders carry stable .meta GUIDs. Host `Packages/manifest.json` declares `testables: ["com.match3.visual-factory"]`. `Tools/validate_repo_structure.py` verifies Unity test assembly isolation, stable metadata and authored package parity.

**No-cost local runner prepared:** `scripts/run_unity_editmode.ps1` requires the exact existing clean local checkout, Unity 6000.6.5f1 and a separate external evidence folder. It intentionally does not run by itself; when launched it saves Unity batch log and NUnit XML, validates six or more passed/zero failed/skipped EditMode cases, and performs no cache cleanup or hosted GitHub Action. User Windows filesystem remains UNTOUCHED.

**Source verification:** the Python test definition count increased from 125 to **126**, plus six authored Unity NUnit cases. Source check and real Unity EditMode tests have **not been executed for R08/R09/R10 commits**. Last independently read hosted run remains R05 66/66 success, not evidence for these new changes. No module or milestone PASS is claimed. Do not manufacture Unity evidence, artwork approvals or free disk assumptions.

**Next:** execute the existing local source checks and Unity Editor import after safe owner-side synchronization, fix proven errors and add meaningful Unity prefab-render/device QA before any VUF milestone acceptance. GH Actions manual-only, Engine/LFX final integration gates unchanged.

## 2026-10-15 | R09 SOURCE / VF-02 REVISION ROLLBACK | UNVERIFIED

- Asset catalog now supports restoring an earlier approved revision with an explicitly provided expected active revision and an owner review receipt. Historic source blobs are retained and restoration activity is separately recorded.
- SQLite schema adds append-only controls for historic revision, approval and restoration records. These safeguard history locally but do not provide authenticated ownership or prevent manipulation by database administrators.
- An optional CLI history view and rollback command were added, with eight new unit-test methods. Current source defines 125 unit-test methods across ten files. This is not a passing test result. The last verified hosted run remains R05: 66 tests successful at 10a1b3bc09bef1238ced23fc54b9646e65369343.
- GitHub Actions automatic triggers remain disabled. R08/R09 still require free local Python checks and real Unity Editor import, followed by independent review before any milestone PASS. Do not publish assets or change game repositories.

## 2026-10-15 | R08 DIRECT DEVELOPMENT / ALL 28 CORAL EXPERIENCE CANDIDATE SHELLS | UNITY NOT TESTED

**Owner directive:** continue working without frequent progress messages, no background promises, no paid CI/API. Authoring-only changes are scoped to this repository.

**28-ID UI infrastructure at source level:** `unity_package/Editor/VufScreenCatalog.cs` loads immutable draft Coral contract data mirrored in `unity_package/Editor/Resources/coral-experiences.v1.json` from canonical `schemas/coral-experiences.v1.json`. Rejects non-28, duplicate IDs or keys, unsupported page kinds, missing Home/Gameplay, enabled demo status, fake approval stage or unknown feature-policy gates. Paired five-profile draft style mirror `style_profiles.v1.json` retains each title's distinct original draft color palette. `Tools/validate_repo_structure.py` checks byte-for-byte parity for both mirrors, plus stable C# .meta GUIDs.

**`Tools > MATCH3 > 28-Screen Shell Builder`**: `VufScreenShellBuilderWindow.cs` now offers a selector for all 28 named Coral experiences and 5 game palettes; builds one new non-overwritten uGUI `Canvas` candidate prefab with safe-area content, page/modal/ceremony/overlay/board/mode visual skeleton, placeholder art slots, `interactable=false` action button, visible Engine/policy-disabled gate, and owner-unapproved notice. Runtime `VufCandidateScreenMarker.cs` persists exact `COR-01..28` ID, profile, kind, gate and `CANDIDATE_NOT_APPROVED`. Dashboard exposes the builder. Manual QA Studio reads marker and flags policy-off screens and any doctored candidate status.

**Important scope:** 28 layout **SHELLS are NOT 28 final designed/functional screens**. No claim about original illustrated artwork, true tap actions, animation/VFX bindings, layout robustness under localization, cloud social permissions, Engine replay, device/Unity compilation or owner creative approval. Policy-off screens stay disabled until Engine policy is resolved. Non-Coral game screen inventory is still draft.

**Source QA:** nine new defined unittest cases in `tests/test_screen_shells.py` cover 28 IDs, Home/Gameplay, five policy-off social/events, source-to-package byte parity, disabled real button code, candidate-only marker and Editor contract. **This is 117 source-defined test methods across ten test files, not 117 verified passes.** Historical R05 run 38788803805 remains only exact-SHA hosted PASS 66/66. GitHub Actions remains manual-dispatch only; zero new workflow job was requested. Unity and current Python R08 source tests OPEN.

**NEXT:** run local free source/unit suite and real Unity 6000.6.5f1 Editor import at exact HEAD before any status PASS; fix observed compile, screen preview, and prefab-save issues. Then implement truly editable screen region/component layout, dynamic text/device simulator and complete physical asset review. Maintain ENG-M24/LFX-M14 final integration gates.

## 2026-10-15 | R07 SOURCE DEVELOPMENT / VF-04 ATLAS + MASK & VF-09 SOURCE PIXEL QA | OPEN TEST GATE

**User directive:** continue direct development without needless pauses. The changes below were actually published in this Visual Factory repository. No device/production release is claimed.

**VF-04 deterministic atlas SOURCE:** `factory/image_processor/atlas_pipeline.py` builds original-pixel-preserving unrotated PNG sprite atlas candidates from explicitly named source PNG files. Deterministic shelf packing (max 128 sprites, maximum 4096 edge/16.8M RGBA pixels), configurable transparent padding/edge extrusion, bottom-left Unity UV coordinates, per-sprite original SHA and output atlas SHA. External candidate folder only; no overwrite or source mutation. `tests/test_atlas_pipeline.py` adds 12 defined pixel/layout/symlink/overflow/invariance tests.

**VF-04 alpha masking SOURCE:** `factory/image_processor/alpha_mask.py` reads original and same-sized RGBA mask file, outputs keep/remove mask-alpha pixel composition with original RGB unchanged and original/mask/output SHA-256 receipt. Separate external, non-overwritten `CANDIDATE_NOT_APPROVED` outputs; `tests/test_alpha_mask.py` has 10 tests. This is not a painting/select-brush GUI, PSD layer authoring or automatic background removal.

**VF-04 Unity atlas Inspector SOURCE:** `unity_package/Editor/VufAtlasPreviewWindow.cs` now checks candidate JSON schema, sprite ID uniqueness, bounds, normalized bottom-left UV, overlap and draws labelled sprite rectangles over a selected imported Texture2D. Dashboard menu opens the inspector; stable Unity .meta GUID and `Tools/validate_repo_structure.py` source gate added. **This does not prove source hashes or real Unity Editor compilation**, and is not Unity SpriteAtlas packaging.

**VF-09 independently replayed pixel QA SOURCE:** `factory/validators/verify_candidates.py` re-reads original PNGs and output candidate pixels/receipts, verifies source SHA, atlas UV/geometry/overlap and sprite pixels, or mask alpha arithmetic/RGB immutability. `tests/test_verify_candidates.py` adds 10 tests with forged hashes/UVs/original mutation/altered output. Success returns `REVIEW_REQUIRED`, not owner approval.

**PNG edge hardening:** `png_pipeline.py` now fails closed on RGB `tRNS` transparency PNG that would otherwise be silently decoded opaque; regression test added. Unsupported indexed/grayscale/interlaced/ICC color-managed PNG must be normalized by a separate verified converter before original masters are approved.

**Test status:** Nine Python test source modules now contain **108 discovered-style `test_*` methods**. This is a SOURCE COUNT, **NOT 108 PASS**. Last independently inspected hosted run remains R05 SHA `10a1b3bc09bef1238ced23fc54b9646e65369343`, 66/66 PASS on [run 38788803805](https://github.com/Sekiph82/MATCH3-Visual-UI-Factory/actions/runs/38788803805). R06/R07 source has not been run in the owner's Unity Editor or by Python. The workflow is manual-only to avoid paid automatic GH Actions. No free local user's Windows machine was accessed by the connector, no paid API or content generation enabled.

**Next bounded verification:** on a permitted Windows checkout, run `scripts/run_source_checks.ps1`, correct any unit failures; open Unity 6000.6.5f1 and check actual package compilation, Atlas Inspector VFX Animation UI prefab source, exports and real device behavior. Advance masks/atlas into editable Studio and accessible, working 28 Coral UI templates only after these hard gates. Do not mark VUF-M00/M05/M06/M09 PASS or release from source-code claims.

## 2026-10-15 | R06 DIRECT DEVELOPMENT / VERIFIED R05 CI / CONTROLLED-COST NEW TOOLS

**Verified historical source regression (at exact prior commit only):** GitHub Actions run [38788803805](https://github.com/Sekiph82/MATCH3-Visual-UI-Factory/actions/runs/38788803805), at SHA `10a1b3bc09bef1238ced23fc54b9646e65369343`, job ID `116607670939`, reports `Ran 66 tests in 0.151s` followed by `OK`; all source, package structure and Python syntax job steps SUCCESS, no reported failures or skips. Logs were read directly through GitHub tool. **This is NOT evidence for R06 commits, Unity compilation or creative owner signoff.**

**CI COST CONTAINMENT (owner bill awareness):** the existing workflow accumulated 75 push-triggered runs. R06 changes `.github/workflows/manifest-validation.yml` from automatic `push` and `pull_request` triggers to `workflow_dispatch` only, so normal incremental development does not auto-start GitHub-hosted runs. `scripts/run_source_checks.ps1` supplies free local Python source checks without installing dependencies, deleting files or cloning repositories. Avoid manually dispatching paid runners without owner approval; use local tests. The single R06 workflow-change commit could still be processed under the old workflow trigger; do not claim zero billing without GitHub billing statements.

**VF-06 first functional authoring source:** new `unity_package/Editor/VufVfxLabWindow.cs` authoring UI, five ParticleSystem presets (BubbleRise, MatchBurst, StarSparkle, SoftDrift, PortalPulse), editable count/lifetime/speed/color/size, distinct testable candidate prefab path and reduced-motion deterministic **2D SKETCH**; actual Unity ParticleSystem shader/renderer preview is NOT simulated by this sketch. `factory/vfx_builder/presets.v1.json` + `validate_presets.py` define explicit bounded, candidate-only view events and reduced-motion fallback. Shader, haptics and audio testing, automated visual QA and real Unity ParticleSystem playback remain OPEN.

**VF-07 initial real component source:** new `unity_package/Editor/VufUiComposerWindow.cs` builds non-overwriting GameObject uGUI Canvas, CanvasScaler, GraphicRaycaster, Image, Text and disabled Button candidate prefabs for seven reusable screen archetypes across five draft profiles. This is not the 28 fully working Coral experiences; callbacks are disabled until Engine view/action binding can be pinned. Unity 6000.6 uGUI package dependency is declared and editor asmdef explicitly references `UnityEngine.UI`.

**VF-08 initial runtime component source:** `unity_package/Runtime/VufSafeAreaFitter.cs` observes `Screen.safeArea` changes and maps normalized RectTransform anchors. Editor simulated device guides are NOT real iPhone/Android tests.

**VF-09 partial manual QA Studio source:** `unity_package/Editor/VufQaStudioWindow.cs` inspects imported candidate prefab uGUI components, enabled button bindings, Safe Area components, particle budget/material, texture Sprite importer and animation clip metadata, opens actual prefab in Unity for human inspection; never auto-accepts or simulates real Engine bindings. It is an Editor source prototype and not yet a real-device QA pass.

**New tests/source checks:** `tests/test_vfx_lab_contracts.py` adds contract and explicitly disabled event tests; `Tools/validate_repo_structure.py` requires new Editor/Runtime scripts, fixed .meta GUIDs and exact uGUI dependency; new `factory/vfx_builder/validate_presets.py` checks no game state changes. New R06 source remains **UNTESTED on actual Unity and not post-change CI-verified** until direct fresh evidence exists. VUF milestones not independently PASS.

**Next:** independently run free Python checks at exact R06 SHA in an allowed local environment; real Unity Editor import, authoring windows, particle prefab and uGUI/safe-area screenshot evidence; remediate all compile issues; then advance full Sprite/Shader manual QA Studio and VF-04 image masks/atlases. Continue only source-isolated development until ENG-M24 and LFX-M14 final independent PASS.

## 2026-10-15 | R05 DIRECT DEVELOPMENT / VF-04 PNG + VF-05 UNITY SPRITE CLIPS | NO AUDIT PASS

**Owner handoff:** continue direct implementation. No change to the final independent Engine ENG-M24 + LFX LFX-M14 gates, creative review or release policy.

- **VF-04 implemented source (prototype):** `factory/image_processor/png_pipeline.py` now independently decodes CRC-checked full, 8-bit non-interlaced RGB/RGBA PNG pixels (filter modes 0..4), fails closed for unsupported input, trims outer alpha while preserving pixel RGBA and transparent padding, produces nearest-neighbor 1x/2x/3x distinct candidate PNG files and SHA-256 original/output provenance receipts. Output is write-once and must remain external to the GitHub checkout, never overwrites originals or approved assets. This is not a complete PSD/masking/atlas factory. `tests/test_png_pipeline.py` covers pixel round-trip, alpha, crop/scaling, corruption, symlinks, no in-repo writes.
- **VF-02 hardened source:** `catalog.py` now checks full PNG validity (rather than only IHDR), blocks orphan write before explicit catalog initialization and rejects unsafe original/store paths. Source tests include malformed compressed input.
- **VF-05 implemented Unity Editor source (prototype):** `unity_package/Editor/VufSpriteClipBuilderWindow.cs` creates a new candidate `.anim` from unrotated multiple Sprite sub-assets. Includes FPS, looping, ping-pong, manual frame scrub, reduced-motion preview, stable natural frame order and no-overwrite guard. Dashboard opens the new Builder. No 2D rig, 3D rig, VFX, Animator graph, real Unity validation or physical device claims.
- **Unity package integrity:** eight source/folder `.meta` GUID files pinned, structural package validator `Tools/validate_repo_structure.py`, CI includes Python unittest discovery, syntax check and package meta/isolation gate. Earlier stale `Assets/Editor/VufStudioWindow.cs` CI path was repaired after migration.
- **Test status:** 66 individual Python unittest method definitions currently exist across five files. This is **not 66 PASS**. The GitHub workflow has been edited but its actual hosted run/result could not be independently inspected in this execution. Unity 6000.6.5f1 compilation, PlayMode, genuine image QA and Windows desktop sync remain **NOT VERIFIED**. Milestones/checkboxes remain OPEN; do not mark M00/M05/M07 closed.
- **Next:** independently reproduce current Python source negative controls and real Unity import; fix errors as discovered; then extend VF-04 masking/atlas, VF-05 clip correctness, VF-06 shader/particle manual Studio. All actual owner approval remains separate.

## R04 source implementation progress | 2026-10-15 | NOT INDEPENDENTLY AUDITED

**GitHub main source-only implemented/created:** `unity_package/package.json`, C# Editor Dashboard, migrated manual Sprite Preview, C# read-only preview contract, `Packages/manifest.json` local UPM reference; five draft style bibles `factory/visual_director/style_profiles.v1.json`; 28 experience IDs `schemas/coral-experiences.v1.json`; five thin game configs; VF-02 offline SQLite + external SHA-256 PNG store under `factory/asset_catalog/catalog.py`; original `Tools/validate_manifest.py`, new `factory/validators/validate_design.py`; source unit tests and workflow. Source audit evidence still required for completeness.

**UNVERIFIED:** hosted Python test job conclusion, real Unity Editor compilation/PlayMode, local Windows folder synchronization, actual image/animation/VFX editor controls, complete PNG decoding, production licences, user art selection, five-title live bindings, actual device appearance, independent review. Existing M00 checkboxes stay **open**; no M00/M01 or VF module declared PASS. Do not claim asset generation or production-ready Studio based on dashboard labels.

**Next priority:** inspect true GitHub Actions results and independently reproduce tests; harden legal/source, external store, package Editor import and Unity 6000.6.5f1 compilation; then complete M00 and advance isolated VF-04/VF-05 tasks without breaking upstream gates. Keep future builds source/test evidence in Drive only.

## 2026-10-15 | VUF-M00 early-bootstrap execution record (owner R03)

- Owner requests ChatGPT implement the entire five-game Visual/UI Factory, beginning with setup. This supersedes the earlier *setup* prohibition only, **not** upstream acceptance, owner artistic review, licence, genuine device/Unity test or final release gates.
- Google Drive project workspace established at https://drive.google.com/drive/folders/1apwUpKSDc_QJJSk8Y3TWw9X-_Wu4quj0, with the six required numbered Drive-only prompt/log/audit/evidence/release subfolders. No fabricated Codex logs or independent approvals.
- Tracked Unity 6000.6.5f1 root project manifest/EditorWindow prototype, minimal safe Git ignore, M00 manual sprite-sheet/image preview, TEST_ONLY five-profile structural manifest validator, adversarial unittest source and source-check CI workflow published to GitHub main. See README.md. This is a functional code-start, **not** 11 completed modules.
- Editor preview supports an imported source Texture2D, horizontal frame playback, 0.25/0.5/1/2x, frame scrub, symbolic state/theme selection and simulated device ratios/safe-area. Other studios are explicitly UNSUPPORTED. Source/originality rights are not independently verified and the preview never self-approves artwork.
- **Tests:** Unity compilation, actual Editor Studio run, Windows local checkout sync, physical phone tests, image-generation providers, Engine/LFX compatibility and independent audit are **NOT VERIFIED**. CI configuration is source only until an actual job result is inspected; never mark M00 PASS from writing test definitions.
- **Task ownership:** VUF-M00-003 and VUF-M00-005 are IN_PROGRESS / READY_FOR_FOCUSED_VERIFICATION. M00-001/002/004 are open, with upstream final SHA/policy decisions required. None of VUF-M00..M11 are PASS/CLOSED.

## Factory milestones (M00 EARLY BOOTSTRAP / ALL OTHER PHASES GATED; no PASS claimed)

### VUF-M00 | Source audit, scope, secure baseline
- [ ] VUF-M00-001 Freeze existing Engine M09 and LFX M08 APIs by exact SHA; extract screen/state/asset key inventory and legal restrictions.
- [ ] VUF-M00-002 Record upstream Engine/LevelFactory PASS prerequisites and no-cross-repo implementation policy.
- [ ] VUF-M00-003 Establish one-tracker + Drive-only prompts/logs/independent audit/evidence workflow and no-cost execution budget.
- [ ] VUF-M00-004 Establish original/licensed art and font ingestion policy; no unlicensed reference extraction.
- [ ] VUF-M00-005 Initialize minimal reproducible toolchain and targeted negative tests with no large caches, paid APIs or unauthorized local file operations.
**Exit:** Reproducible tracked source and audited gates without art or engine rules duplication.

### VUF-M01 | Versioned asset, UI and animation contracts
- [ ] VUF-M01-001 Implement typed five-profile visual manifest with stable game/theme IDs and upstream SHA pins.
- [ ] VUF-M01-002 Implement 5-profile x 17 Engine UiSurfaceKind x 8-state SYMBOLIC contract mapping to all 26 owner Coral Rescue screens plus Home and Gameplay/HUD (28 total), including route/overlay IDs, applicable state and required dynamic text/icon/action bindings; no imported game pixels in Engine.
- [ ] VUF-M01-003 Map UI action IDs, dynamic text, localization, visible/disabled accessibility reason and fallback keys.
- [ ] VUF-M01-004 Map piece/special/combo/goal/obstacle events to versioned view-only skin, VFX and animation keys; expose time, interrupt, replay and accessibility bindings to the external Studio visual consumer. No gameplay logic forks.
- [ ] VUF-M01-005 Negative validation: duplicate/missing/unbound asset IDs, unknown state, cross-theme leak, invalid version and unsafe paths.
**Exit:** Engine/LevelFactory-compatible manifest consumer with deterministic golden fixtures.

### VUF-M02 | Five design systems and art-direction bibles
- [ ] VUF-M02-001 Define typography, layout grid, palette, component tokens, silhouette/contrast and portrait/tablet responsive rules.
- [ ] VUF-M02-002 Coral Rescue visual bible and icon/character/background reference sheets.
- [ ] VUF-M02-003 Garage Legends visual bible and component/vehicle/tool identity sheets.
- [ ] VUF-M02-004 Dino Islands visual bible and creature/habitat/egg identity sheets.
- [ ] VUF-M02-005 The Fractured Realms visual bible and elemental/realm identity sheets.
- [ ] VUF-M02-006 Wonder Pop accessible child-safe visual bible, no adult ad/social pressure.
**Exit:** Owner-reviewed reference styles; placeholders clearly distinguished from final approved art.

### VUF-M03 | Layered screen and UI component factory
- [ ] VUF-M03-001 Component generator for CTA, cards, modals, badges, counters, tabs, progress bars and disabled/pending/claimed feedback.
- [ ] VUF-M03-002 Layered interactive templates, modal/ceremony/mode variants for all 28 Coral Rescue experiences in the inventory, with reusable consent/account/booster/surface components for all five themed games; no flattened unclickable full-screen images.
- [ ] VUF-M03-003 Runtime text/icon placement stays separate from artwork and supports EN/TR plus pseudo-long localized strings.
- [ ] VUF-M03-004 Safe-area, tall phone, compact phone and tablet layout with usable touch targets and no cropped background text.
- [ ] VUF-M03-005 Five-title theme swap never changes the semantic UI route graph or player state.
**Exit:** Source-layered template packages for every screen and state family.

### VUF-M04 | AI artwork provider and human-review pipeline
- [ ] VUF-M04-001 ChatGPT-assisted concept/master intake and optional approved image-provider adapter; clean no-API/manual path.
- [ ] VUF-M04-002 Source reference/character identity lock, palette/style continuity and explicit image originality review.
- [ ] VUF-M04-003 Review loop: generate -> candidate -> compare -> owner approve/reject -> immutable approved master; no self-approval.
- [ ] VUF-M04-004 Stable asset lineage, image dimension/alpha/hash metadata, deduplication and licence provenance.
- [ ] VUF-M04-005 Fail-closed paid-provider approval budget; no automatic credential capture or GitHub-stored tokens.
**Exit:** Reproducible art transformations and provenance, without pretending that generative images are bit-for-bit deterministic.

### VUF-M05 | Tile, booster, obstacle and sprite-atlas factory
- [ ] VUF-M05-001 Six accessible base tile silhouettes for each title; separate shape from color.
- [ ] VUF-M05-002 All horizontal/vertical/area/color/missile special combinations mapped to engine IDs.
- [ ] VUF-M05-003 Obstacle states, damage variations, collectibles, goals, equipment and boosters.
- [ ] VUF-M05-004 Trim/pivot/transparent margins, 1x/2x/3x image exports and Sprite Atlas V2 import settings.
- [ ] VUF-M05-005 Automatic alpha/dimension/duplicates/missing-state/atlas memory-budget tests.
**Exit:** Complete five-title sample atlas packs with no unsupported runtime assumptions.

### VUF-M06 | Backgrounds, characters and maps
- [ ] VUF-M06-001 Layered World/Chapter maps, Gameplay backdrops, reef restoration, Marine Collection, My Aquarium decoration, and New Region reveal scene layers; no flattened runtime buttons or text.
- [ ] VUF-M06-002 Character/mascot reference sheets with consistent poses and silhouette identity.
- [ ] VUF-M06-003 Parallax/background/screen scaling exports and relevant overlays.
- [ ] VUF-M06-004 Title/theme naming, provenance and version pinning through generation and export.
**Exit:** At least one representative scene package per profile, owner-reviewable.

### VUF-M07 | Animations, VFX and reduced-effects parity
- [ ] VUF-M07-001 Idle, reward, win/fail, tile, combo, character and UI transition effect contracts.
- [ ] VUF-M07-002 Sprite-sheet/Unity animation bindings: manual frame-by-frame scrub, frame rate/loop/ping-pong, pivots, alignment, transparency, scale, clipping, atlas swaps, transition priority and interruption/replay parity.
- [ ] VUF-M07-003 Full/reduced-motion mode and optional middleware-absent fallback.
- [ ] VUF-M07-004 Enforce no animation/VFX callback may mutate engine board, rewards or save transactions.
- [ ] VUF-M07-005 Frame, audio cue, haptic trigger, particle, texture/atlas, draw-call, memory and CPU/GPU budget diagnostics on genuine demo runs; distinguish simulation from real-device verification.
- [ ] VUF-M07-006 **Manual Sprite & VFX Lab (OWNER REQUIRED):** User selects a game profile, asset, animation, event and state; manually plays/pauses/scrubs frame-by-frame at 0.25x/0.5x/1x/2x, compares sprite sheets, keyframes, particle bursts/trails, masks, lighting/parallax, combo/chained VFX, success/fail and transitions. Test loop/pivot/atlas/crop/alpha, overlapping effects, interruption, replay, reduced-motion, mute and logged haptic events. No VFX callback may mutate gameplay or rewards; save reproducible test receipts. Do not claim physical haptic/audio-device PASS from desktop simulation.
**Exit:** Real Unity-consumable effects and replay-invariant acceptance.

### VUF-M08 | Unity UI and asset packaging adapters
- [ ] VUF-M08-001 Unity 6000.6.5f1 Editor authoring interface and import automation; choose runtime uGUI/TMP versus UI Toolkit based on actual animation/safe-area tests, not assumptions.
- [ ] VUF-M08-002 Build layered interactive prefabs/UXML and real action bindings with dev-only UI inspector for z-order, touch targets, layout anchors, safe areas, tween/transition states, disabled/offline/loading and localized text.
- [ ] VUF-M08-003 Package sprite atlases, imports, locales, effect configs and optional Addressables with fallback.
- [ ] VUF-M08-004 Offline/missing image/incorrect manifest/version conflict and rollback negative checks.
- [ ] VUF-M08-005 Release scanner rejects test assembly, templates, raw reference art, secrets and generated evidence from game players.
- [ ] VUF-M08-006 **External Visual Test Studio adapter (OWNER REQUIRED):** After Engine and LFX are independently closed, connect versioned VUF asset packs to ENG-M12-010 neutral event/replay contracts in a separate Unity consumer or compatible Studio plugin. Preview real layered graphics, sprites, VFX, camera/UI transitions without inserting any artwork into MATCH3_ENGINE repo, tests or runtime source. Permit owner manual asset/theme hot-swap in sandbox only, with immutable hashes, schema mismatch, missing-pack fallbacks and no revenue/save authority.
**Exit:** Working external Unity consumer of one export per five neutral game profiles.

### VUF-M09 | Automated visual QA and rights acceptance
- [ ] VUF-M09-001 Test rendered five-profile screen/component state matrices and Coral 28-experience inventory across phone/tablet ratios (Ready/Loading/Offline/Error/Owned/Claimed/Disabled/Pending where applicable); record explicit N/A/disabled evidence, no fake feature availability.
- [ ] VUF-M09-002 Accessibility: color-independent shapes, contrast, text fitting, focus, hit targets, reduced motion and translated long strings.
- [ ] VUF-M09-003 Visual consistency regression, missing overlays, resolution sharpness, safe area, sprite pixel fidelity, transparency/fringing, layer ordering, 1x/2x/3x atlas swaps and frame-by-frame animation diffs.
- [ ] VUF-M09-004 Original/licensed artwork and font receipts, approved source revisions and no forbidden lookalikes.
- [ ] VUF-M09-005 Separate mechanical automated PASS from human creative acceptance and real device signoff.
- [ ] VUF-M09-006 **Owner Manual Visual QA Studio acceptance (MANDATORY):** Desktop Unity Editor and development Windows viewer must expose manual, clickable inspection of every supported screen, button state, gameplay tile/obstacle/booster animation, sprite-sheet frame, particle/VFX cue, camera/parallax, layer/z-order, popup transitions, sound cue and simulated haptic event. Controls: profile/asset/screen/state/level/seed selector, pause/single-frame/event stepping, speed, before/after or A/B compare, overlay and safe-area guides, multiple phone/tablet ratios, EN/TR long strings, disabled/offline/loading, full/reduced-motion, FPS/memory/draw-call metrics where supported, screenshot/video or frame-sequence export and deterministic event trace. Separate automatic rendering PASS, human aesthetic approval, and real iOS/Android physical tests. Any unavailable feature shows explicit UNSUPPORTED/N-A reason. Owner must be able to manually reproduce animation/cropping/state errors; no mere static mockup is accepted.
**Exit:** Fail-closed audit that produces reproducible visual proof, never forged owner approval.

### VUF-M10 | Five-profile executable vertical slice
- [ ] VUF-M10-001 Five neutral Engine profiles consume real LevelFactory representative level packs with real visual exports.
- [ ] VUF-M10-002 Five-profile runnable Home -> World -> LevelStart -> Gameplay -> Results -> Collection/Daily/Shop/offline vertical slice; include one Coral reef-restoration/aquarium/region visual sample without claiming every Coral G02 runtime screen is already shipped.
- [ ] VUF-M10-003 Actual Unity EditMode/PlayMode plus positive/negative rendering, event-to-animation, obstacle/booster visuals, manual-screen interaction and UI-route integration tests.
- [ ] VUF-M10-004 Real build content manifest, platform texture/memory/frame budgets and mobile smoke where available.
- [ ] VUF-M10-005 Demonstrate updated art/theme cannot alter gameplay, scoring, saves or level difficulty.
- [ ] VUF-M10-006 **Five-theme manual end-to-end Studio run:** Owner can manually swap five versioned themes against identical replay/event fixtures and inspect Home, Gameplay, results, collection/rewards, obstacle damage, boosters, combo effects, UI transitions and accessibility with no game rule changes. Document representative vertical slices per profile plus Coral 28-screen inventory coverage/status, not falsely assert finished art for every game. Record actual artifact, host version, imported asset-pack hashes, screenshot/video/replay evidence and owner acceptance/blockers.
**Exit:** One complete technical vertical slice for each of five themes with real artifacts, not UI mockups alone.

### VUF-M11 | Versioned Factory v1 release / handoff
- [ ] VUF-M11-001 Release reproducible exporter/importer with pinned Engine/LFX compatibility matrix and rollback.
- [ ] VUF-M11-002 Owner approves the Factory design system, master samples, workflow quality and safe manual override path.
- [ ] VUF-M11-003 Independent audit reviews original tests/artifact hashes, versioned sources, legal records and no-cost boundaries.
- [ ] VUF-M11-004 Produce consumer quickstart and exact game G01/G02/G09/G11 asset-approval handoff.
- [ ] VUF-M11-005 Freeze v1 pipeline for the first title; game-specific final art approvals remain in their own task trackers.
**Exit:** VUF-M00..M11 auditable PASS/CLOSED; only then start branded game implementation.

## Required eventual existing-repo TASKS.md alignment (NOT YET MODIFIED)

- MATCH3_ENGINE: retain M01-003 and M09-001/004/005/007/016 as core UI/theming contracts; update M09-014 criteria ONLY after owner-authorized versioned resolution of the frozen visual/device contradiction; keep mobile evidence at M23-014 and M24-012.
- Match3-Level-Factory: LFX-M08-001..012 preview + provenance + owner screen inventory remain preview/contract work with placeholders; LFX-M13-005 defines view-only mapping. Add downstream VUF compatibility handoff when owner adopts new sequence.
- Five games: G01-001..011 original visual identity/production, G02 view binding/animations, G09 responsive/accessibility, G10 packaging cleanliness and G11 owner device acceptance consume specifically pinned approved VUF packs. No final-themed asset production in Engine or LFX.
- Existing frozen independent PASS results remain unchanged; revised future acceptance criteria require provenance and owner approval where specified.

**CURRENT_OWNER:** CHATGPT VUF R20 FEATURE BATCH BUILDER. NEXT: ONE consolidated Codex local test of R18-R20 at FINAL exact SHA; fix real failures and continue VF04/05/06 asset production. No per-feature CI, Github Actions charges, deletion, owner art or independent product acceptance claims.
