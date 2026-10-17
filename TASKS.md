# MATCH3 Visual & UI Factory | TASKS.md

## OWNER RULE | SINGLE CODEX HANDOFF AFTER FULL VUF MILESTONE | 2026-10-17
**Owner's latest workflow decision:** ChatGPT first completes ALL feasible source implementation, compatible upstream donor adaptation, internal source checks and authored regression/test cases for the ACTIVE milestone before assigning ANY Codex test task. Do not pause after one or two small tasks/repairs to create another Codex prompt. Send ONE comprehensive local Unity/integration/visual (as applicable) test and evidence request at milestone code-complete, then independently audit real results. Existing unfinished per-step Codex requests are nonmandatory and must not interrupt ongoing development. An environmental blocker or a missing real device/provider is recorded honestly, never replaced with a fabricated PASS. Keep source-first licensing, this single root TASKS.md as the tracker, no unauthorized CI/paid runners, no destructive cleanup or interference with owner files. This changes testing cadence only; existing milestone criteria, task IDs, sequencing and evidence thresholds remain unchanged.



## OWNER RULE | PRE-CODE DONOR-FIRST GATE | 2026-10-16
**Owner requirement for EVERY future VUF code task:** Read this existing root `TASKS.md` task, then inspect existing working VUF modules and the actual files of previously discussed pinned GitHub donors BEFORE writing new code. Prefer direct legally permitted source adoption with minimal namespace/Unity 6.6/asset-schema changes and baseline+integration tests over rewriting equivalent functionality. The existing `docs/VUF_DONOR_SOURCE_LEDGER.md` is source provenance evidence, NOT another task tracker. Reuse already adopted BSD-3-Clause Unity-UI-Extensions `NonDrawingGraphic` and other now-adopted inspected UGUI effects plus VUF's existing `VufUiTween` before adding redundant UI/animation libraries. UltraGem and Unity Game Simulation level-edit code belong to LFX, LibraStack match logic to Engine; CC BY-NC-ND Rimaethon/unlicensed assets or code are not import candidates under current rights. For EACH coding step, record exact donor repo/commit/file/blob SHA, licence and dependency review, selected functions, `DIRECT_REUSE`/`MINIMAL_ADAPTER`/`INTERNAL_REUSE`/`REJECTED_REASON`, necessary changes, actual test status and original notices in the existing Drive workflow. Update this same `TASKS.md` after real source changes/audits; no unapproved ad hoc task renumbering, no false PASS for unrun Unity, device, visuals or licensing, no GitHub Actions/paid CI or destructive cleanup. This is a **process-only instruction**, not an import or task closure.


**Status (2026-10-17):** Tek formatli milestone checklist: **78 isaretli, 63 acik, toplam 141 gorev.** Owner-local VUF-M05-015 teknik regresyonu GitHub main `cd9f9bfd6750ffeee850e700ac1c3691358b1f2b` uzerinde Python 361 PASS / 9 Windows symlink SKIP (370 discovered), Unity 6000.6.5f1 EditMode 85/85 PASS olarak raporlandi. Kaynak kodu testleri gecmis olsa da Unity GUI, sanat/hak onayi, final Engine/LFX IDs, mobil/GPU/cihaz ve tum M05 milestone cikis kabulleri acik.

**Repository:** Sekiph82/MATCH3-Visual-UI-Factory
**Local folder (owner-reported, never modified by this planning file):** C:\Users\sekip\Desktop\GAMES\MATCH3 GAMES\MATCH3-Visual-UI-Factory
**Authority:** This root TASKS.md is the only lifecycle tracker in this repository; ChatGPT alone writes auditable task statuses. Keep full prompts, Codex logs, independent audits, and evidence in designated Google Drive project folders, not in GitHub coordination files.

## KAYIT VE IZLEME KURALI
- Yalniz bu dosyadaki `VUF-MXX-NNN` satirlari gorevdir. Numaralar milestone icinde 001'den baslayip hic bosluk birakmadan siralanir; test ve Codex islemleri de ayni listededir, ayri alt-kategori veya kodu yoktur.
- Onceden atanmis 64 gorevin numaralari degistirilmedi. 50 adet eski S/T kaydi, her birinin bulunduğu milestone'a yeni VUF-MXX-NNN numarasi ile **tek seviyeli** gorev olarak eklendi; 11 tarihsel Codex oturumu ve gelecekteki tek-milestone Codex kabul oturumlari da ayni numara dizisindedir.
- Rxx etiketleri sadece GitHub geliştirici revizyon gecmisinde, Cxxx etiketleri sadece Drive Codex oturum arsivinde yer alir; R/C bagimsiz gorev ID'si degildir. Eski aciklama metinleri: `docs/VUF_DEVELOPMENT_AND_CODEX_HISTORY_20261017.md`. Bu dosya **gorev takip listesi degildir**.
- Kaynak kodu ilerlemesi ile Unity GUI, Engine/LFX nihai pinleri, orijinal sanat haklari, sahibi manuel kabulü ve fiziksel cihaz PASS birbirinden ayridir. Yeni/kodlanmamis gorevler sadece gercek kanit oldugunda `[x]` olur. Biten her işte dogrudan bu numarali satiri guncelle.
- Codex testleri son kaynak koduna uygun tek kapsamli milestone test görevi olarak planlanir; asagidaki gecmis Codex PASS sonuçları test edildikleri *eski* SHA'da gecerlidir. Son kaynak degisikligi için Python/Unity PASS uydurulmaz.

**Durum (17.10.2026):** **78 isaretli, 63 acik, toplam 141 tek formatli gorev.** VUF-M05-015 Codex teknik test/duzeltme/kanit oturumu tamamlandi; M05 milestone'unun owner/GUI/gercek Engine kimlikleri/mobil kabulleri acik. Bitenlerden bir bolumu sadece kaynak uygulama veya belirli SHA'da testtir, milestone onayi degildir.


## MILESTONES | TEK GOREV ID FORMATI

> Her yapılacak iş, geliştirme, test ve Codex oturumu **aynı düzeyde** `VUF-MXX-NNN` kodudur. Başka görev türü / alt görev ID'si yoktur. Önceden yayımlanan 64 ana kod korunmuştur; eski iç içe `-Snn` / `-Tnn` kayıtları aynı milestone altında yeni sıradaki numaralara dönüştürülmüştür. Geçmiş R/C oturum adları yalnız kanıt ve sürüm açıklamasıdır, görev kodu değildir.
> **[x]** dosyada uygulanmış kaynak veya raporlanmış Codex işini belirtir. **[ ]** eksik veya henüz doğrulanmamış işi gösterir. Tekil `[x]` hiçbir milestone'u otomatik PASS yapmaz. VUF-M05-015 son owner-local toplu teknik test: SHA `cd9f9bfd6750ffeee850e700ac1c3691358b1f2b`, Python 361 PASS / 9 SKIP, gercek Unity EditMode 85/85 PASS. Headless Unity testi GUI/cihaz/hak kabulunun yerine gecmez.

### VUF-M00 | Source audit, scope, secure baseline

- [ ] VUF-M00-001 Freeze existing Engine M09 and LFX M08 APIs by exact SHA; extract screen/state/asset key inventory and legal restrictions.
- [x] VUF-M00-002 Record upstream Engine/LevelFactory PASS prerequisites and no-cross-repo implementation policy.
- [x] VUF-M00-003 Establish one-tracker + Drive-only prompts/logs/independent audit/evidence workflow and no-cost execution budget.
- [x] VUF-M00-004 Establish original/licensed art and font ingestion policy; no unlicensed reference extraction.
- [x] VUF-M00-005 Initialize minimal reproducible toolchain and targeted negative tests with no large caches, paid APIs or unauthorized local file operations.
- [x] VUF-M00-006 R04/R10/R13: Unity UPM, PowerShell yerel test ve Edition-only NUnit kaynak altyapisi (`unity_package/`, `scripts/`).
- [x] VUF-M00-007 Codex: ilk yerel Windows checkout ön kontrolünü yürüt, klasörün boş olduğunu ve testlerin çalıştırılamadığını kanıtla. Ön kontrol tamamlandı; testler o oturumda NOT RUN (önceki oturum kaydı 01_PROMPTS/C001).
- [x] VUF-M00-008 Codex: mevcut checkout'u güvenle hazırla; Python 125 PASS/7 SKIP ve Unity EditMode 8/8 PASS doğrulamasını yap (SHA 796a84b; Drive 02_CODEX_LOGS/C002).
- [x] VUF-M00-009 Codex: güvenli main senkronizasyonu ve Unity Studio GUI erişim kontrolünü kaydet. Kod/test aktarımı tamamlandı; gerçek GUI kontrolleri NOT RUN (Drive 02_CODEX_LOGS/C003).
- [x] VUF-M00-010 Codex: Unity ilk-import proje metalarını koruyarak gerçek headless Unity EditMode 13/13 PASS ve yerel Python source kontrollerini doğrula (SHA a4493cd; Drive 02_CODEX_LOGS/C004).
- [x] VUF-M00-011 GitHub kodu ve proje Google Drive belgeleri üzerinden bütün milestone/geliştirme işlerini denetle ve kaynak uygulama durumlarını kanıt temelli uzlaştır (2026-10-17 R53 denetim kaydı).
- [ ] VUF-M00-012 Codex: M00 kapanışında son Engine/LFX API pinleri, lisans, Windows/Unity taşınabilirlik ve bağımsız test kanıtlarını tek kapsamlı milestone doğrulamasından geçir; gerçek PASS olmadan kapatma.

**Exit:** Reproducible tracked source and audited gates without art or engine rules duplication.

### VUF-M01 | Versioned asset, UI and animation contracts

- [x] VUF-M01-001 Implement typed five-profile visual manifest with stable game/theme IDs and upstream SHA pins.
- [ ] VUF-M01-002 Implement 5-profile x 17 Engine UiSurfaceKind x 8-state SYMBOLIC contract mapping to all 26 owner Coral Rescue screens plus Home and Gameplay/HUD (28 total), including route/overlay IDs, applicable state and required dynamic text/icon/action bindings; no imported game pixels in Engine.
- [ ] VUF-M01-003 Map UI action IDs, dynamic text, localization, visible/disabled accessibility reason and fallback keys.
- [ ] VUF-M01-004 Map piece/special/combo/goal/obstacle events to versioned view-only skin, VFX and animation keys; expose time, interrupt, replay and accessibility bindings to the external Studio visual consumer. No gameplay logic forks.
- [x] VUF-M01-005 Negative validation: duplicate/missing/unbound asset IDs, unknown state, cross-theme leak, invalid version and unsafe paths.
- [x] VUF-M01-006 R04: bes profil + Engine/LFX SHA view-only manifest/parser (`Tools/validate_manifest.py`, `VisualAssetManifest.cs`).
- [x] VUF-M01-007 R08/R17: 28 Coral ID × 5 tema, 8 draft UI state; **17 UiSurfaceKind route/action eslesmesi HENUZ YOK** (`VufScreenCatalog.cs`).
- [ ] VUF-M01-008 5×17×8 goldens ve route/dynamic-action fallback contract baglantisi; ana gorev acik.
- [x] VUF-M01-009 R17/R19: EN/TR/stress locale draft + placeholder QA; tum action/fallback semantics acik (`locale_audit.py`).
- [x] VUF-M01-010 R50/R51: gerçek Engine special/combo ve obstacle damage sembolik visual key map; olay/timing/replay baglantisi acik (`special_skin_map.py`, `obstacle_skin_states.py`).
- [x] VUF-M01-011 R04/R07: Negatif manifest/provenans/PNG/path source guards (`Tools/validate_manifest.py`, `verify_candidates.py`).
- [ ] VUF-M01-012 Codex: tam beş-tema × 17 Engine UI surface × 8-state ekran/eylem/event sözleşmesi için golden fixture ve gerçek dış Unity tüketici testlerini toplu yürüt; eksik final Engine/LFX pinlerini açık raporla.

**Exit:** Engine/LevelFactory-compatible manifest consumer with deterministic golden fixtures.

### VUF-M02 | Five design systems and art-direction bibles

- [ ] VUF-M02-001 Define typography, layout grid, palette, component tokens, silhouette/contrast and portrait/tablet responsive rules.
- [ ] VUF-M02-002 Coral Rescue visual bible and icon/character/background reference sheets.
- [ ] VUF-M02-003 Garage Legends visual bible and component/vehicle/tool identity sheets.
- [ ] VUF-M02-004 Dino Islands visual bible and creature/habitat/egg identity sheets.
- [ ] VUF-M02-005 The Fractured Realms visual bible and elemental/realm identity sheets.
- [ ] VUF-M02-006 Wonder Pop accessible child-safe visual bible, no adult ad/social pressure.
- [x] VUF-M02-007 R04/R16/R18: 5 taslak tema paleti/6 silhouette, contrast/text-fit source; final design-token/font rehberi acik (`style_profiles.v1.json`).
- [x] VUF-M02-008 R28/R36: Coral 3 matematiksel konsept ekran ve motifler; final karakter/reference sheets acik (`concept_showcase.py`, `VufThemeMotifDecor.cs`).
- [x] VUF-M02-009 R28/R36: Garage 3 konsept/motif; gercek vehicle/tool kimlik masterlari acik.
- [x] VUF-M02-010 R28/R36: Dino 3 konsept/motif; gercek creature/egg kimlik masterlari acik.
- [x] VUF-M02-011 R28/R36: Fractured Realms 3 konsept/motif; elemental/realm kimlik masterlari acik.
- [x] VUF-M02-012 R28/R36: Wonder Pop 3 konsept/motif; child-safe owner art/review acik.
- [ ] VUF-M02-013 Codex: beş tema Style Bible, erişilebilirlik, tipografi ve kaynak/orijinallik dosyalarını toplu incele; insanın görsel/hak onayını otomatik PASS sayma.

**Exit:** Owner-reviewed reference styles; placeholders clearly distinguished from final approved art.

### VUF-M03 | Layered screen and UI component factory

- [ ] VUF-M03-001 Component generator for CTA, cards, modals, badges, counters, tabs, progress bars and disabled/pending/claimed feedback.
- [ ] VUF-M03-002 Layered interactive templates, modal/ceremony/mode variants for all 28 Coral Rescue experiences in the inventory, with reusable consent/account/booster/surface components for all five themed games; no flattened unclickable full-screen images.
- [x] VUF-M03-003 Runtime text/icon placement stays separate from artwork and supports EN/TR plus pseudo-long localized strings.
- [ ] VUF-M03-004 Safe-area, tall phone, compact phone and tablet layout with usable touch targets and no cropped background text.
- [ ] VUF-M03-005 Five-title theme swap never changes the semantic UI route graph or player state.
- [x] VUF-M03-006 R06/R17: 7 uGUI page archetype + 8 durumlar/disabled actions (`VufUiComposerWindow.cs`, `VufReviewStateCatalog.cs`).
- [x] VUF-M03-007 R35–R42: uGUI editable components, Home flow/radial, gradient/mirror/raycast, reduced motion donor reuse (`VufPageComposition.cs`, donor ledger).
- [x] VUF-M03-008 R08/R32/R35/R36: 28 shell, editable Home/Gameplay/World concept staging ve 5 motif (`VufScreenShellBuilderWindow.cs`, `VufConceptStageBuilderWindow.cs`).
- [x] VUF-M03-009 R43: 28 Coral shell icine R35–R42 donor component bridge; VUF-M05-015 kapsamli yerel kaynak testi henuz kosulmadi (`VufScreenShellLayoutBridge.cs`).
- [ ] VUF-M03-010 28 ekranin gercek bagli runtime aksiyonlari/modal/consent/booster ve owner GUI kabulu.
- [x] VUF-M03-011 R17/R19: editable text slot + EN/TR uzun metin onizlemesi (`locale_audit.py`, `VufReviewStateCatalog.cs`).
- [x] VUF-M03-012 R06/R15/R18: SafeAreaFitter, 5 synthetic responsive wireframe + typography QA; gercek telefon/tablet testi eksik.
- [x] VUF-M03-013 Codex: offline toplu PNG alımı ve beş sentetik cihaz responsive UI kontrollerinin yerel regresyonunu çalıştır. Python 144 PASS/7 SKIP; Unity 16/16 PASS (SHA 9dcca802; Drive 02_CODEX_LOGS/C005).
- [x] VUF-M03-014 Codex: 28 Coral ekranına 8 durum × 3 taslak metin görünümü kaynak/Unity testi yap. Python 165 PASS/7 SKIP; Unity 21/21 PASS (SHA f698449; Drive 02_CODEX_LOGS/C007).
- [ ] VUF-M03-015 Codex: M03 kapsamındaki 28 ekranın gerçek buton/modal/booster/consent bağları ve beş temalı Unity GUI etkileşimleri tamamlanınca tek gerçek milestone testi yap; salt sahte UI shell testi ile kapatma.

**Exit:** Source-layered template packages for every screen and state family.

### VUF-M04 | AI artwork provider and human-review pipeline

- [x] VUF-M04-001 ChatGPT-assisted concept/master intake and optional approved image-provider adapter; clean no-API/manual path.
- [ ] VUF-M04-002 Source reference/character identity lock, palette/style continuity and explicit image originality review.
- [ ] VUF-M04-003 Review loop: generate -> candidate -> compare -> owner approve/reject -> immutable approved master; no self-approval.
- [x] VUF-M04-004 Stable asset lineage, image dimension/alpha/hash metadata, deduplication and licence provenance.
- [x] VUF-M04-005 Fail-closed paid-provider approval budget; no automatic credential capture or GitHub-stored tokens.
- [x] VUF-M04-006 R14/R28: No-cost manuel/batch candidate PNG import ve 15 konsept PNG onizleme; harici AI-provider entegrasyonu iddia edilmez (`offline_batch.py`, `concept_showcase.py`).
- [x] VUF-M04-007 R09/R11/R34: SQLite immutable revision/rollback + queue + 5×3 owner karsilastirma sheet; gercek owner yaratıcı approve UI eksik (`catalog.py`, `contact_sheet.py`).
- [x] VUF-M04-008 R04/R07: hash/alpha/PNG/source receipt ve immutable lineage (`catalog.py`, `verify_candidates.py`).
- [ ] VUF-M04-009 Codex: eksiksiz orijinal/lisanslı sanat ve onay akışı tamamlanınca aday karşılaştırması, immutable master, manipüle edilmiş hak/onay fişi negatifleri ve kaynak SHA bütünlüğünü toplu doğrula; owner kararı ayrı kalır.

**Exit:** Reproducible art transformations and provenance, without pretending that generative images are bit-for-bit deterministic.

### VUF-M05 | Tile, booster, obstacle and sprite-atlas factory

- [x] VUF-M05-001 Six accessible base tile silhouettes for each title; separate shape from color.
- [x] VUF-M05-002 All horizontal/vertical/area/color/missile special combinations mapped to engine IDs.
- [ ] VUF-M05-003 Obstacle states, damage variations, collectibles, goals, equipment and boosters. **KANIT/ACIK:** SHA `cd9f9bfd` R51 view-only demo role/HP/damage testi PASS; `sample_*` kimlikler Engine production IDs DEGIL. Tam gercek Engine registry, collect/goal/booster durum ve sanat state paritesi bu gorevin kalan kapsami. Kaynak: `obstacle_skin_states.py`, Codex M05-015 raporu. Mevcut demo sample ID'leriyle production PASS yasak.
- [ ] VUF-M05-004 Trim/pivot/transparent margins, 1x/2x/3x image exports and Sprite Atlas V2 import settings. **KANIT/ACIK:** Python 1x/2x/3x trim/extrusion ve real Unity EditMode V2 *olusturma* PASS (`cd9f9bfd`), orijinal TextureImporter/GUID/hash korunuyor. 5-tema pivot/border/texture import davranisi ve Editor GUI gozle kabul/cihaz atlas-swap **NOT RUN**; M05-013 ile birlikte acik.
- [x] VUF-M05-005 Automatic alpha/dimension/duplicates/missing-state/atlas memory-budget tests.
- [x] VUF-M05-006 R25: 5 tema icin 6 alpha silhouette PNG ve 3×2 candidate atlas (`silhouette_kit.py`).
- [x] VUF-M05-007 R50: gercek Engine 5 special enum ve 15 unordered combo x 5 temali symbolic skin map (`special_skin_map.py`).
- [x] VUF-M05-008 R51: Engine layer/damage enum tabanli 5 rol ve HP visual-state taslagi; demo ID (`obstacle_skin_states.py`).
- [x] VUF-M05-009 R52: her oyun icin 38 matematiksel ornek sprite + candidate atlas (toplam 190, PREMIUM DEGIL) (`sample_sprite_pack.py`).
- [ ] VUF-M05-010 Tum gercek obstacle/goal/booster final Engine IDs ve owner art/state parity dogrulama. **KANIT/ACIK:** Engine `ObstacleLifecycleContracts.cs` declaration blob `0a882ec44e6ecfcb840971efad187515f44ef9b3` kontrol edildi, yalniz layer/damage enum biliniyor; runtime registry'nin tum ID'leri/pinleri ve owner approved asset-ID mapping dogrulanmadi. Nihai kaynak / exact SHA / owner art receipt ile sonradan yeniden dogrula; cross-repo write yok, atama/ID uydurma yok.
- [x] VUF-M05-011 R05/R07/R31: trim, 1×/2×/3×, alpha mask, edge-extrusion, deterministik atlas (`png_pipeline.py`, `atlas_pipeline.py`).
- [x] VUF-M05-012 R27/R47: Unity tile/atlas inspector ve SpriteAtlas V2 draft export authoring (`VufTileKitInspectorWindow.cs`, `VufSpriteAtlasV2Window.cs`).
- [ ] VUF-M05-013 Unity'de gercek SpriteAtlas V2 import/pivot/texture settings ve 1×/2×/3× kabul. **TEKNIK PASS / KABUL ACIK:** Codex M05-015 (`cd9f9bfd`) gerçek Unity EditMode create-new atlas, `includeInBuild=false`, texture source/hash/importer/GUID dokunulmazligi, mevcut hedef overwrite reddi 85/85 Unity tam suite icinde PASS. **NOT RUN:** Unity Editor elle acip 5 tema atlas gorunumu, 1×/2×/3× pivots/borders/bleeding/texture compression, device/GPU atlas swapping ve sahibin gorsel imzasi. Unity GUI screenshot + gercek cihaz kaniti olmadan son check yok. Sonraki gercek Unity GUI kabul oturumuna ertelenmistir.
- [x] VUF-M05-014 R07/R26/R49: Bagimsiz alpha/CRC/hash/UV/pixel/state/duplicate/memory estimate negatifs (`verify_generated_kits.py`, `atlas_candidate_audit.py`).
- [x] VUF-M05-015 Codex: TEK toplu M05 yerel teknik regresyon/duzeltme oturumu **TAMAMLANDI (2026-10-17)**; final kaynak main SHA `cd9f9bfd6750ffeee850e700ac1c3691358b1f2b`. Python 370 toplam / 361 PASS / 9 symlink SKIP / 0 FAIL/ERROR, AST 65 Python ve repository validators PASS; Unity 6000.6.5f1 gercek headless EditMode **85/85 PASS**. Bes tema 30 tile silhouette / 5 R25 atlas, 190 demo sprite / 5 R52 atlas; R49 hash/alpha/UV/butce denetimi ve Unity gercek nonshipping V2 atlas yazma + kaynak GUID/importer korunumu PASS. Hatalar dar kapsamli 6 dosya ile onarildi ve tam test final SHA'da tekrar calistirildi. Owner sanat/hak/Unity GUI/gercek cihaz/GPU ve final Engine obstacle/booster ID/parity **NOT RUN/OPEN** (M05-003/004/010/013 acik). Tek final Codex raporu: https://docs.google.com/document/d/1TvMdFJA64oN4mX_O6-X8ETV9X2QMo19jv9q7ohbtRKM/edit ; Drive kanit ZIP SHA-256 (Codex bildirdigi): `D8F4B8E5B7F5DC7F9F02557CCC26A83FEC36CA52C4EDE79722FF46E5331C2787` ; https://drive.google.com/file/d/1I4_i_3T0InYsAl5_ywehebA7mCOh_ApH/view . Kaynak log ve commit ayri okundu; ZIP ham byte hash bu ChatGPT oturumunda bagimsiz hesaplanmadi.

**Exit:** Complete five-title sample atlas packs with no unsupported runtime assumptions.

### VUF-M06 | Backgrounds, characters and maps

- [ ] VUF-M06-001 Layered World/Chapter maps, Gameplay backdrops, reef restoration, Marine Collection, My Aquarium decoration, and New Region reveal scene layers; no flattened runtime buttons or text. **SOURCE PROGRESS:** `representative_scene_pack.py` implements separate backdrop/distant/near candidate PNG layer render for all 5 themes x World/Chapter/Gameplay + Coral reef/restoration/collection/aquarium/region (19 scene IDs), owner reviewable only, no runtime buttons/text. Final owner art + real Unity scene integration STILL OPEN. New 11 authored Python tests NOT RUN.
- [ ] VUF-M06-002 Character/mascot reference sheets with consistent poses and silhouette identity. **SOURCE PROGRESS:** `character_pose_review.py` accepts an EXTERNAL artist-owned SHA-pinned reference and exactly 5 pose PNGs, creates an isolated 6-panel candidate contact sheet and alpha/anchor geometry receipt. Actual original/licensed five-game character sheets NOT PROVIDED/NOT APPROVED, no automatic visual identity assertion; 8 authored tests NOT RUN.
- [ ] VUF-M06-003 Parallax/background/screen scaling exports and relevant overlays. **SOURCE PROGRESS:** 19 scenes x 3 independent RGBA layers; deterministic 1x/2x review PNG and fixed milli-parallax metadata (0/120/340). Real Unity scene parallax runtime, safe-area/tall-device/GPU validation and artwork overlays NOT RUN/OPEN.
- [x] VUF-M06-004 Title/theme naming, provenance and version pinning through generation and export.
- [x] VUF-M06-005 R21/R28/R30: Real PNG katman compositoru ve 5×3 concept preview; eksik reef/aquarium/region final sahneleri var (`layer_compositor.py`, `concept_showcase.py`).
- [x] VUF-M06-006 R21/R52: theme source SHA, PNG provenance ve generated asset metadata (`sample_sprite_pack.py`, `layer_compositor.py`).
- [ ] VUF-M06-007 Codex: beş tema için temsilî katmanlı harita/arka plan/karakter sahnelerini, kaynak görsel SHA'larını, Unity görünüm oranlarını ve manuel owner karşılaştırmasını toplu test et. **TEK M06 GATE:** M06'nin makul tum kaynak kapsamı (M06-008..011 dahil) bitince yerel Python + gerçek Unity + kaynak hash/test/GUI raporu iste; 19 scene/57 PNG matematiksel candidate art için otomatik premium PASS verme; owner art/cihaz hâlâ ayrı.
- [x] VUF-M06-008 Beş tema için World/Chapter/Gameplay ve Coral özel dört çevre ekranında **19 temsilî sahne × 3 ayrı RGBA PNG = 57** matematiksel aday layer üreten, hash/SHA kaynak ve 0/120/340 milli-parallax metaverisi içeren offline factory kodlandı (`factory/image_processor/representative_scene_pack.py`). Etkileşimli text/button, gameplay veya yapay art-rights yok; **kaynak teslimi, test HENÜZ KOŞULMADI**.
- [x] VUF-M06-009 M06 19-sahne layer-pack için 11 negatif/deterministik test **SOURCE AUTHORING** tamamlandı (`tests/test_representative_scene_pack.py`); cross-theme, eksik/boguk PNG, SHA/depth, art-approval spoof, 1x/2x, güvenli dışa aktarım. Python/Unity test koşusu henüz NOT RUN; M06-007 Codex gate'e dahildir.
- [x] VUF-M06-010 Sahip/artist original PNG'lerini Git dışından hash ile okuyup beş gerçek poz + tek referans için 6-panel inceleme sheet'i, alpha kutusu/ankor/poz SHA receipt'i olusturan, yalnız yeni dış klasöre yazan original-art intake kodlandı (`factory/visual_director/character_pose_review.py`). Gerçek owner sanat referansları henüz yok, identite/hak onayı koşul değil; **SOURCE ONLY, untested**.
- [x] VUF-M06-011 Character pose intake için 8 negatif/güvenli test source yazıldı (`tests/test_character_pose_review.py`): kaynak hash kayması, kopya/eksik poz, path traversal, hak onayı sahteciliği, canvas ve anchor, no-overwrite. Gerçek Python/Unity test koşusu henüz NOT RUN; M06-007 kapsamına alınacak.

**Exit:** At least one representative scene package per profile, owner-reviewable.

### VUF-M07 | Animations, VFX and reduced-effects parity

- [ ] VUF-M07-001 Idle, reward, win/fail, tile, combo, character and UI transition effect contracts. **KIRILIM:** M06 candidate layers tamamlaninca view-only event/FX timeline contract ve reduced-motion/replay timing keys yazilacak; canli Engine gameplay yazma yetkisi yok.
- [ ] VUF-M07-002 Sprite-sheet/Unity animation bindings: manual frame-by-frame scrub, frame rate/loop/ping-pong, pivots, alignment, transparency, scale, clipping, atlas swaps, transition priority and interruption/replay parity.
- [x] VUF-M07-003 Full/reduced-motion mode and optional middleware-absent fallback.
- [x] VUF-M07-004 Enforce no animation/VFX callback may mutate engine board, rewards or save transactions.
- [ ] VUF-M07-005 Frame, audio cue, haptic trigger, particle, texture/atlas, draw-call, memory and CPU/GPU budget diagnostics on genuine demo runs; distinguish simulation from real-device verification.
- [ ] VUF-M07-006 **Manual Sprite & VFX Lab (OWNER REQUIRED):** User selects a game profile, asset, animation, event and state; manually plays/pauses/scrubs frame-by-frame at 0.25x/0.5x/1x/2x, compares sprite sheets, keyframes, particle bursts/trails, masks, lighting/parallax, combo/chained VFX, success/fail and transitions. Test loop/pivot/atlas/crop/alpha, overlapping effects, interruption, replay, reduced-motion, mute and logged haptic events. No VFX callback may mutate gameplay or rewards; save reproducible test receipts. Do not claim physical haptic/audio-device PASS from desktop simulation.
- [x] VUF-M07-007 R22: 5 deterministic VFX sprite-sheet + reduced-motion still; full event/FX ontology eksik (`procedural_fx_sheet.py`).
- [x] VUF-M07-008 R05/R23/R24: Sprite clip authoring, scrub, ping-pong/loop ve procedural FX-to-Unity clip exporter (`VufSpriteClipBuilderWindow.cs`, `VufFxClipExporterWindow.cs`).
- [ ] VUF-M07-009 Olay/replay/interrupt/atlas swap/pivot/transition priority gercek Unity playback parity testi.
- [x] VUF-M07-010 R12/R38: CanvasGroup tween + reduced-motion gercek source ve yeniden kullanim (`VufUiTween.cs`).
- [x] VUF-M07-011 R06/R12/R22/R24: gameplay/save/score/reward mute eden presentation-only runtime/Editor sinirlari (`VufUiTween.cs`, `VufVfxLabWindow.cs`).
- [x] VUF-M07-012 R06/R23: Manual Unity Particle Lab ve imported sheet frame preview (`VufVfxLabWindow.cs`, `VufFxSheetPreviewWindow.cs`).
- [ ] VUF-M07-013 Owner-required 0.25×/0.5×/1×/2× tam olay/VFX/sprite editor Studio ve gercek GUI evidence.
- [ ] VUF-M07-014 Codex: tüm VFX/sprite animasyonu, frame scrub/loop/interrupt/reduced-motion/replay/ses-haptik simülasyonu ve ayrık callback güvenliği için tek milestone Unity test görevi yap; gerçek cihaz durumunu ayrı raporla.

**Exit:** Real Unity-consumable effects and replay-invariant acceptance.

### VUF-M08 | Unity UI and asset packaging adapters

- [ ] VUF-M08-001 Unity 6000.6.5f1 Editor authoring interface and import automation; choose runtime uGUI/TMP versus UI Toolkit based on actual animation/safe-area tests, not assumptions.
- [ ] VUF-M08-002 Build layered interactive prefabs/UXML and real action bindings with dev-only UI inspector for z-order, touch targets, layout anchors, safe areas, tween/transition states, disabled/offline/loading and localized text.
- [ ] VUF-M08-003 Package sprite atlases, imports, locales, effect configs and optional Addressables with fallback.
- [x] VUF-M08-004 Offline/missing image/incorrect manifest/version conflict and rollback negative checks.
- [x] VUF-M08-005 Release scanner rejects test assembly, templates, raw reference art, secrets and generated evidence from game players.
- [ ] VUF-M08-006 **External Visual Test Studio adapter (OWNER REQUIRED):** After Engine and LFX are independently closed, connect versioned VUF asset packs to ENG-M12-010 neutral event/replay contracts in a separate Unity consumer or compatible Studio plugin. Preview real layered graphics, sprites, VFX, camera/UI transitions without inserting any artwork into MATCH3_ENGINE repo, tests or runtime source. Permit owner manual asset/theme hot-swap in sandbox only, with immutable hashes, schema mismatch, missing-pack fallbacks and no revenue/save authority.
- [x] VUF-M08-007 R47: Unity SDK SpriteAtlasAsset V2 candidate authoring, production asset paketi degil (`VufSpriteAtlasV2Window.cs`).
- [x] VUF-M08-008 R09/R45/R46: SQLite restore ile bagimsiz manifest version/rollback diff negative checker (`catalog.py`, `preview_compatibility.py`).
- [x] VUF-M08-009 R44: Editor/tests/ref art/secret/evidence deny rules olan read-only player preflight (`player_pack_preflight.py`).
- [ ] VUF-M08-010 Codex: son Engine/LFX pinlerinden sonra gerçek Unity dış tüketici/Studio bağlantısı, derlenmiş paket, atlas/import/locale ve temiz player build taramasını tek milestone doğrulamasında çalıştır.

**Exit:** Working external Unity consumer of one export per five neutral game profiles.

### VUF-M09 | Automated visual QA and rights acceptance

- [ ] VUF-M09-001 Test rendered five-profile screen/component state matrices and Coral 28-experience inventory across phone/tablet ratios (Ready/Loading/Offline/Error/Owned/Claimed/Disabled/Pending where applicable); record explicit N/A/disabled evidence, no fake feature availability.
- [ ] VUF-M09-002 Accessibility: color-independent shapes, contrast, text fitting, focus, hit targets, reduced motion and translated long strings.
- [ ] VUF-M09-003 Visual consistency regression, missing overlays, resolution sharpness, safe area, sprite pixel fidelity, transparency/fringing, layer ordering, 1x/2x/3x atlas swaps and frame-by-frame animation diffs.
- [ ] VUF-M09-004 Original/licensed artwork and font receipts, approved source revisions and no forbidden lookalikes.
- [x] VUF-M09-005 Separate mechanical automated PASS from human creative acceptance and real device signoff.
- [ ] VUF-M09-006 **Owner Manual Visual QA Studio acceptance (MANDATORY):** Desktop Unity Editor and development Windows viewer must expose manual, clickable inspection of every supported screen, button state, gameplay tile/obstacle/booster animation, sprite-sheet frame, particle/VFX cue, camera/parallax, layer/z-order, popup transitions, sound cue and simulated haptic event. Controls: profile/asset/screen/state/level/seed selector, pause/single-frame/event stepping, speed, before/after or A/B compare, overlay and safe-area guides, multiple phone/tablet ratios, EN/TR long strings, disabled/offline/loading, full/reduced-motion, FPS/memory/draw-call metrics where supported, screenshot/video or frame-sequence export and deterministic event trace. Separate automatic rendering PASS, human aesthetic approval, and real iOS/Android physical tests. Any unavailable feature shows explicit UNSUPPORTED/N-A reason. Owner must be able to manually reproduce animation/cropping/state errors; no mere static mockup is accepted.
- [x] VUF-M09-007 R17: 28 ID × 8 mock state × 3 locale stress source/in-memory kontrol; rendered device matrix yok (`VufReviewStateCatalog.cs`).
- [x] VUF-M09-008 R18/R19: Unity text height contrast ve offline EN/TR placeholder audit; accessibility manual focus/device yok (`VufTypographyAudit.cs`, `locale_audit.py`).
- [x] VUF-M09-009 R16/R26/R30/R33: sprite pixel-health, source re-composition ve concept bundle SHA/visual negatives (`visual_qa.py`, `verify_generated_kits.py`).
- [x] VUF-M09-010 R20: mekanik/rights/owner/device onaylarini ayiran release evidence board (`VufReadinessBoardWindow.cs`).
- [x] VUF-M09-011 R06: manual prefab QA inspector baslangic modulu; tam owner GUI/animation controls eksik (`VufQaStudioWindow.cs`).
- [ ] VUF-M09-012 Tam clickable owner Visual QA Studio, dev Windows viewer, screenshot/video, speed/scrub/event A/B ve gercek kabul.
- [x] VUF-M09-013 Codex: sprite pixel/alpha/kontrast sağlık kontrollerini gerçek Windows Python ve Unity ile sınadı. Python 163 PASS/7 SKIP; Unity 18/18 PASS (SHA 05566214; Drive 02_CODEX_LOGS/C006).
- [x] VUF-M09-014 Codex: EN/TR metin-fit, kontrast ve hazır olma raporunu toplu sınadı. Python 189 PASS/7 SKIP; Unity 32/32 PASS (SHA aa4900aa; önceden belgelenmiş 02_CODEX_LOGS/C008).
- [x] VUF-M09-015 Codex: 15 beş-temalı konsepte, layered scene, sprite/FX aday paketlerine ait Python 273 PASS/7 SKIP ve Unity 50/50 PASS regresyonunu gerçekleştirdi (SHA 6c70a6a; Google Drive 02_CODEX_LOGS/C009).
- [x] VUF-M09-016 Codex: lisanslı Unity donor bileşenleri ve 28 ekran katmanları için Python 294 PASS/7 SKIP, Unity EditMode 72/72 PASS doğrulaması yaptı (SHA 1ea8ac06; Google Drive 02_CODEX_LOGS/C010). Yeni sonraki revizyonların testleri değildir.
- [ ] VUF-M09-017 Codex: owner manual Visual QA Studio tamamlanınca gerçek 5 tema×ekran×durum×telefon/tablet render, accessibility, FPS, artefakt/rights ve cihaz kanıtlarını tek M09 test oturumunda değerlendir; manuel signoff yerine geçme.

**Exit:** Fail-closed audit that produces reproducible visual proof, never forged owner approval.

### VUF-M10 | Five-profile executable vertical slice

- [ ] VUF-M10-001 Five neutral Engine profiles consume real LevelFactory representative level packs with real visual exports.
- [ ] VUF-M10-002 Five-profile runnable Home -> World -> LevelStart -> Gameplay -> Results -> Collection/Daily/Shop/offline vertical slice; include one Coral reef-restoration/aquarium/region visual sample without claiming every Coral G02 runtime screen is already shipped.
- [ ] VUF-M10-003 Actual Unity EditMode/PlayMode plus positive/negative rendering, event-to-animation, obstacle/booster visuals, manual-screen interaction and UI-route integration tests.
- [ ] VUF-M10-004 Real build content manifest, platform texture/memory/frame budgets and mobile smoke where available.
- [ ] VUF-M10-005 Demonstrate updated art/theme cannot alter gameplay, scoring, saves or level difficulty.
- [ ] VUF-M10-006 **Five-theme manual end-to-end Studio run:** Owner can manually swap five versioned themes against identical replay/event fixtures and inspect Home, Gameplay, results, collection/rewards, obstacle damage, boosters, combo effects, UI transitions and accessibility with no game rule changes. Document representative vertical slices per profile plus Coral 28-screen inventory coverage/status, not falsely assert finished art for every game. Record actual artifact, host version, imported asset-pack hashes, screenshot/video/replay evidence and owner acceptance/blockers.
- [ ] VUF-M10-007 Codex: Engine/LFX tüketicisiyle beş oyunun gerçek Home→Gameplay→Results dikey kesitleri, replay/event doğruluğu, cihaz ve performans testlerini tek milestone test oturumunda çalıştır.

**Exit:** One complete technical vertical slice for each of five themes with real artifacts, not UI mockups alone.

### VUF-M11 | Versioned Factory v1 release / handoff

- [ ] VUF-M11-001 Release reproducible exporter/importer with pinned Engine/LFX compatibility matrix and rollback.
- [ ] VUF-M11-002 Owner approves the Factory design system, master samples, workflow quality and safe manual override path.
- [ ] VUF-M11-003 Independent audit reviews original tests/artifact hashes, versioned sources, legal records and no-cost boundaries.
- [ ] VUF-M11-004 Produce consumer quickstart and exact game G01/G02/G09/G11 asset-approval handoff.
- [ ] VUF-M11-005 Freeze v1 pipeline for the first title; game-specific final art approvals remain in their own task trackers.
- [ ] VUF-M11-006 Codex: Frozen Factory v1 exporter/importer/rollback, hak/pin/QA kaydı, game handoff ve bağımsız release denetimini tamamla; owner final kabulü ayrı kanıtla.

**Exit:** VUF-M00..M11 auditable PASS/CLOSED; only then start branded game implementation.


## Required eventual existing-repo TASKS.md alignment (NOT YET MODIFIED)

- MATCH3_ENGINE: retain M01-003 and M09-001/004/005/007/016 as core UI/theming contracts; update M09-014 criteria ONLY after owner-authorized versioned resolution of the frozen visual/device contradiction; keep mobile evidence at M23-014 and M24-012.
- Match3-Level-Factory: LFX-M08-001..012 preview + provenance + owner screen inventory remain preview/contract work with placeholders; LFX-M13-005 defines view-only mapping. Add downstream VUF compatibility handoff when owner adopts new sequence.
- Five games: G01-001..011 original visual identity/production, G02 view binding/animations, G09 responsive/accessibility, G10 packaging cleanliness and G11 owner device acceptance consume specifically pinned approved VUF packs. No final-themed asset production in Engine or LFX.
- Existing frozen independent PASS results remain unchanged; revised future acceptance criteria require provenance and owner approval where specified.

**CURRENT_OWNER:** CHATGPT. Yalniz bu dosyanin VUF-MXX-NNN kodlu tek seviyeli gorevleri gecerlidir. Kod tamamlaninca ilgili satiri aninda guncelle; Codex tek milestone QA; final GUI/cihaz/rights/Engine-LFX onaylari ayri.
