# MATCH3 Visual & UI Factory | TASKS.md

**Status:** PROPOSED / OWNER DESIGN REVIEW / NOT STARTED.
**Repository:** Sekiph82/MATCH3-Visual-UI-Factory
**Local folder (owner-reported, never modified by this planning file):** C:\Users\sekip\Desktop\GAMES\MATCH3 GAMES\MATCH3-Visual-UI-Factory
**Authority:** This root TASKS.md is the only lifecycle tracker in this repository; ChatGPT alone writes auditable task statuses. Keep full prompts, Codex logs, independent audits, and evidence in designated Google Drive project folders, not in GitHub coordination files.

## PROPOSED execution sequence and release boundaries

**Do not implement Factory code, generate production asset packs, modify the owner's local checkout or launch paid image APIs before the owner adopts this design and both upstream phases independently close.**

1. MATCH3_ENGINE: ENG-M00..ENG-M24 independent PASS/CLOSED. Engine defines five neutral GameProfiles, player-facing surface/state interfaces, immutable presentation events, responsive layout and stable asset keys. No finished branded game assets or Game-repo implementation are required for engine acceptance.
2. Match3-Level-Factory: LFX-M00..LFX-M14 independent PASS/CLOSED. LFX-M08 preview uses original neutral placeholders and five mock themes until Visual Factory begins, and exports accepted sample level packs/fixtures.
3. MATCH3-Visual-UI-Factory: VUF-M00..VUF-M11 independent acceptance for the reusable production pipeline, complete five-theme sample vertical slice, Unity runtime bindings, asset provenance, and deterministic export. **VUF v1 is a tested production tool, not a false claim that every future game's final art is approved.**
4. Five branded game repositories, each G00..G12: all title-specific production assets are made through versioned VUF contracts and independently reviewed at G01; scenes/prefabs/animations are integrated at G02; game-specific device and owner visual acceptance stays at G09–G11. Subsequent VUF patches are individually versioned, backward-compatible, independently audited, and pinned by consuming game repos, never silent changes to a completed prior phase.

**Dependency conflict requiring an explicit decision:** ENG-M09-014 currently requires owner approval of actual five-game visual masters and real iOS/Android signoffs before the Engine itself can close. This contradicts the existing Engine -> LFX -> VUF -> Games sequence. Do NOT silently weaken or self-approve the frozen R01 audit: issue explicit owner-approved ENG-M09-014 R02 scope/criteria preserving engine-owned neutral UI/device evidence now and deferring final branded master/device signoffs to each game's G01/G09/G11 plus ENG-M23/24 device gates. Until owner authorizes that versioned change, ENG-M09-014 stays blocked and the full sequential execution cannot progress.

## System boundaries

- Engine OWNS rules, immutable event/state semantics, profile IDs, screen/action routes, signed content contracts and fallback/permission policy. It never calls generative AI or imports title artwork into deterministic rule assemblies.
- Level Factory OWNS levels, seeds, playability, goals, verified sample level packs and themed preview data via neutral asset IDs; never produces or verifies premium artwork.
- Visual Factory OWNS brand-specific design tokens, component templates, approved original/licensed image generation, background layers, icon/tile/booster/obstacle sheets, animation and VFX bindings, 1x/2x/3x exports, runtime asset manifests, Unity art import scripts and independent visual QA. It does NOT implement match rules or mint rewards.
- Title repos OWN gameplay scenes, title story/content, imported frozen VUF asset pack versions and owner approval of final screens on actual devices.
- Visual factory uses ChatGPT for design direction, concept/master review and image creation where an actual supported image tool is available; Codex for code, automation, Unity export/adapters, test suites, and repeatable transforms. A ChatGPT subscription is NOT treated as a programmable image-generation API. All automated generation requires an explicitly available, cost-approved provider; manual artwork intake remains a first-class path.
- No new paid API, surprise subscriptions, desktop worktrees/TEMP growth, cache cleanup, or unapproved local changes. No generated artwork is accepted solely because an AI marked it PASS. Track licence, generation source/model if known, prompt/version, references, dimensions, alpha, SHA-256, rights/review and source-to-output mapping.

## Contract baseline

Each VUF output package carries: schema version, engine API version, level pack compatibility, game/profile ID, theme version, surface/component ID, state variant (Ready, Loading, Offline, Error, Owned, Claimed, Disabled, Pending where relevant), localization text binding, icon/action key, aspect/safe-area policy, accessibility shape/contrast/focus, animation/reduced-motion binding, asset source/licence/SHA-256, dependency hashes, generated artifact manifest and fallback keys. It must not embed runtime secrets or executable remote code. A screen is constructed from independently themed layers, buttons and actual localized text; a single flattened AI PNG must never pretend to implement tappable runtime UI.

## Factory milestones (all PLANNED/GATED; no claimed execution)

### VUF-M00 | Source audit, scope, secure baseline
- [ ] VUF-M00-001 Freeze existing Engine M09 and LFX M08 APIs by exact SHA; extract screen/state/asset key inventory and legal restrictions.
- [ ] VUF-M00-002 Record upstream Engine/LevelFactory PASS prerequisites and no-cross-repo implementation policy.
- [ ] VUF-M00-003 Establish one-tracker + Drive-only prompts/logs/independent audit/evidence workflow and no-cost execution budget.
- [ ] VUF-M00-004 Establish original/licensed art and font ingestion policy; no unlicensed reference extraction.
- [ ] VUF-M00-005 Initialize minimal reproducible toolchain and targeted negative tests with no large caches, paid APIs or unauthorized local file operations.
**Exit:** Reproducible tracked source and audited gates without art or engine rules duplication.

### VUF-M01 | Versioned asset, UI and animation contracts
- [ ] VUF-M01-001 Implement typed five-profile visual manifest with stable game/theme IDs and upstream SHA pins.
- [ ] VUF-M01-002 Implement full 17-player-surface screen inventory and required interactive states; allow shared components without 680 separate flat images.
- [ ] VUF-M01-003 Map UI action IDs, dynamic text, localization, visible/disabled accessibility reason and fallback keys.
- [ ] VUF-M01-004 Map logical piece/special/combo/goal/obstacle states to view-only skin keys; no gameplay logic forks.
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
- [ ] VUF-M03-002 Master screen templates: Home, WorldMap, HUD, Results, Pause, Settings, Shop, DailyRewards, Tasks, Fail, Life, Booster, Collection, Achievements, Store, Account, Consent.
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
- [ ] VUF-M06-001 Layered world/chapter maps and gameplay backdrops, not single frozen full-UI images.
- [ ] VUF-M06-002 Character/mascot reference sheets with consistent poses and silhouette identity.
- [ ] VUF-M06-003 Parallax/background/screen scaling exports and relevant overlays.
- [ ] VUF-M06-004 Title/theme naming, provenance and version pinning through generation and export.
**Exit:** At least one representative scene package per profile, owner-reviewable.

### VUF-M07 | Animations, VFX and reduced-effects parity
- [ ] VUF-M07-001 Idle, reward, win/fail, tile, combo, character and UI transition effect contracts.
- [ ] VUF-M07-002 Sprite-sheet/Unity animation bindings, frame/pivot/timing policy and interruption safety.
- [ ] VUF-M07-003 Full/reduced-motion mode and optional middleware-absent fallback.
- [ ] VUF-M07-004 Enforce no animation/VFX callback may mutate engine board, rewards or save transactions.
- [ ] VUF-M07-005 Frame/voice/particle/texture performance budgets on genuine demo runs.
**Exit:** Real Unity-consumable effects and replay-invariant acceptance.

### VUF-M08 | Unity UI and asset packaging adapters
- [ ] VUF-M08-001 Unity 6000.6.5f1 Editor authoring interface and import automation; choose runtime uGUI/TMP versus UI Toolkit based on actual animation/safe-area tests, not assumptions.
- [ ] VUF-M08-002 Build layered, interactive prefabs/UXML where appropriate, versioned theme components and real action bindings.
- [ ] VUF-M08-003 Package sprite atlases, imports, locales, effect configs and optional Addressables with fallback.
- [ ] VUF-M08-004 Offline/missing image/incorrect manifest/version conflict and rollback negative checks.
- [ ] VUF-M08-005 Release scanner rejects test assembly, templates, raw reference art, secrets and generated evidence from game players.
**Exit:** Working external Unity consumer of one export per five neutral game profiles.

### VUF-M09 | Automated visual QA and rights acceptance
- [ ] VUF-M09-001 Render comparable named-state screenshots across five profiles and phone/tablet aspect ratios.
- [ ] VUF-M09-002 Accessibility: color-independent shapes, contrast, text fitting, focus, hit targets, reduced motion and translated long strings.
- [ ] VUF-M09-003 Visual consistency regression, missing overlays, resolution sharpness, safe area and image fidelity checks.
- [ ] VUF-M09-004 Original/licensed artwork and font receipts, approved source revisions and no forbidden lookalikes.
- [ ] VUF-M09-005 Separate mechanical automated PASS from human creative acceptance and real device signoff.
**Exit:** Fail-closed audit that produces reproducible visual proof, never forged owner approval.

### VUF-M10 | Five-profile executable vertical slice
- [ ] VUF-M10-001 Five neutral Engine profiles consume real LevelFactory representative level packs with real visual exports.
- [ ] VUF-M10-002 Home -> World -> Level -> Results -> Collection/Daily/Shop/offline state sample in each theme.
- [ ] VUF-M10-003 Actual Unity EditMode/PlayMode plus positive/negative rendering and UI-route integration tests.
- [ ] VUF-M10-004 Real build content manifest, platform texture/memory/frame budgets and mobile smoke where available.
- [ ] VUF-M10-005 Demonstrate updated art/theme cannot alter gameplay, scoring, saves or level difficulty.
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

**CURRENT_OWNER:** OWNER_REVIEW_PROPOSED_DEPENDENCY_MODEL. This planning tracker creates no Unity build, graphics, commercial licence, paid API usage, real-device approval or independently audited PASS.
