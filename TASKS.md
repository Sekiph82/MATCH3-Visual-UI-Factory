# MATCH3 Visual & UI Factory | TASKS.md

## OWNER RULE | SINGLE CODEX HANDOFF AFTER FULL VUF MILESTONE | 2026-10-17
**Owner's latest workflow decision:** ChatGPT first completes ALL feasible source implementation, compatible upstream donor adaptation, internal source checks and authored regression/test cases for the ACTIVE milestone before assigning ANY Codex test task. Do not pause after one or two small tasks/repairs to create another Codex prompt. Send ONE comprehensive local Unity/integration/visual (as applicable) test and evidence request at milestone code-complete, then independently audit real results. Existing unfinished per-step Codex requests are nonmandatory and must not interrupt ongoing development. An environmental blocker or a missing real device/provider is recorded honestly, never replaced with a fabricated PASS. Keep source-first licensing, this single root TASKS.md as the tracker, no unauthorized CI/paid runners, no destructive cleanup or interference with owner files. This changes testing cadence only; existing milestone criteria, task IDs, sequencing and evidence thresholds remain unchanged.



## OWNER RULE | PRE-CODE DONOR-FIRST GATE | 2026-10-16
**Owner requirement for EVERY future VUF code task:** Read this existing root `TASKS.md` task, then inspect existing working VUF modules and the actual files of previously discussed pinned GitHub donors BEFORE writing new code. Prefer direct legally permitted source adoption with minimal namespace/Unity 6.6/asset-schema changes and baseline+integration tests over rewriting equivalent functionality. The existing `docs/VUF_DONOR_SOURCE_LEDGER.md` is source provenance evidence, NOT another task tracker. Reuse already adopted BSD-3-Clause Unity-UI-Extensions `NonDrawingGraphic` and other now-adopted inspected UGUI effects plus VUF's existing `VufUiTween` before adding redundant UI/animation libraries. UltraGem and Unity Game Simulation level-edit code belong to LFX, LibraStack match logic to Engine; CC BY-NC-ND Rimaethon/unlicensed assets or code are not import candidates under current rights. For EACH coding step, record exact donor repo/commit/file/blob SHA, licence and dependency review, selected functions, `DIRECT_REUSE`/`MINIMAL_ADAPTER`/`INTERNAL_REUSE`/`REJECTED_REASON`, necessary changes, actual test status and original notices in the existing Drive workflow. Update this same `TASKS.md` after real source changes/audits; no unapproved ad hoc task renumbering, no false PASS for unrun Unity, device, visuals or licensing, no GitHub Actions/paid CI or destructive cleanup. This is a **process-only instruction**, not an import or task closure.


**Status (2026-10-18):** Tek formatli **dondurulmus 137 gorev**: **81 tamamlanan, 56 acik gorev.** M08-010 gercek yerel Codex full Python 425 test: 416 PASS/9 Windows symlink SKIP/0 FAIL, Unity 6000.6.5f1 EditMode 140/140 PASS, kaynak SHA `de5b8cc1`. VUF-M08-003 TEST_ONLY offline kaynak paketleme testleri PASS; M08-001/002/006 ise GUI/owner/cihaz/Engine LFX son kabul sartlari icin ACIK. Son gercek owner-local M07-014 Python 404 PASS/9 SKIP, Unity EditMode 126/126 PASS kaynak `469233c`; bu PASS M08'e aktarilamaz. Final Engine/LFX, GUI, art-rights, GPU ve cihaz kabul kapilari acik. 12 sonradan eklenmis duplicate M06/M07 kaynak girişi mevcut gorevlerin notlarina tasindi; 2 asil acik kaynak gorevi (M06-001, M07-001) kanitlarina dayanilarak kapatildi. Unity GUI/gercek cihaz/sanat-hak ve Engine/LFX final kabulleri ACIK. Owner-local VUF-M05-015 teknik regresyonu GitHub main `cd9f9bfd6750ffeee850e700ac1c3691358b1f2b` uzerinde Python 361 PASS / 9 Windows symlink SKIP (370 discovered), Unity 6000.6.5f1 EditMode 85/85 PASS olarak raporlandi. Kaynak kodu testleri gecmis olsa da Unity GUI, sanat/hak onayi, final Engine/LFX IDs, mobil/GPU/cihaz ve tum M05 milestone cikis kabulleri acik.

**Repository:** Sekiph82/MATCH3-Visual-UI-Factory
**Local folder (owner-reported, never modified by this planning file):** C:\Users\sekip\Desktop\GAMES\MATCH3 GAMES\MATCH3-Visual-UI-Factory
**Authority:** This root TASKS.md is the only lifecycle tracker in this repository; ChatGPT alone writes auditable task statuses. Keep full prompts, Codex logs, independent audits, and evidence in designated Google Drive project folders, not in GitHub coordination files.

## KAYIT VE IZLEME KURALI
- Yalniz bu dosyadaki `VUF-MXX-NNN` satirlari gorevdir. Numaralar milestone icinde 001'den baslayip hic bosluk birakmadan siralanir; test ve Codex islemleri de ayni listededir, ayri alt-kategori veya kodu yoktur.
- Onceden atanmis 64 gorevin numaralari degistirilmedi. 50 adet eski S/T kaydi, her birinin bulunduğu milestone'a yeni VUF-MXX-NNN numarasi ile **tek seviyeli** gorev olarak eklendi; 11 tarihsel Codex oturumu ve gelecekteki tek-milestone Codex kabul oturumlari da ayni numara dizisindedir.
- **SAHİBİN DÜZELTMESİ (2026-10-18):** Kanonik kapsam **137 önceden tanımlı görevde donduruldu**. Yeni kaynak dosyası/test yazıldı diye ayrıca MXX-NNN görevi EKLEME; ilerlemeyi mevcut açık `VUF-MXX-NNN` satırında kaynak yolu, commit, çalıştırılmış/çalıştırılmamış test ve kalan kabul şartlarıyla kaydet. 2026-10-17'de sonradan eklenen M06-008..015 ve M07-015..018 12 mükerrer iş kaydı, içerikleri var olan M06-001/002/003/007 ve M07-001/006/009/013/014 satırlarına taşınarak silindi; ilgili kaynak dosyaları ve Git commit geçmişi korundu. **Yeni görev sadece sahibin açıkça onayladığı gerçek kapsam değişikliğinde**, var olan işi küçük parçalara bölerek ilerleme sayacı şişirmek için asla değil. Bir görevi `[x]` yapmak için satırdaki kaynak kapsamı yerine getirilmiş olmalı; kaynak tamamlanmış olsa da Unity/owner/device kabulleri başka açık görevlerde ayrı takip edilir, metin içinde açıkça NOT RUN kalır.
- Rxx etiketleri sadece GitHub geliştirici revizyon gecmisinde, Cxxx etiketleri sadece Drive Codex oturum arsivinde yer alir; R/C bagimsiz gorev ID'si degildir. Eski aciklama metinleri: `docs/VUF_DEVELOPMENT_AND_CODEX_HISTORY_20261017.md`. Bu dosya **gorev takip listesi degildir**.
- Kaynak kodu ilerlemesi ile Unity GUI, Engine/LFX nihai pinleri, orijinal sanat haklari, sahibi manuel kabulü ve fiziksel cihaz PASS birbirinden ayridir. Yeni/kodlanmamis gorevler sadece gercek kanit oldugunda `[x]` olur. Biten her işte dogrudan bu numarali satiri guncelle.
- Codex testleri son kaynak koduna uygun tek kapsamli milestone test görevi olarak planlanir; asagidaki gecmis Codex PASS sonuçları test edildikleri *eski* SHA'da gecerlidir. Son kaynak degisikligi için Python/Unity PASS uydurulmaz.

**Durum (18.10.2026):** **81 isaretli, 56 acik, toplam 137 tek formatli gorev.** M08-010 gercek yerel Codex QA `de5b8cc1` uzerinde Python 416 PASS/9 Windows SKIP ve Unity 140/140 PASS ile tamamlandi. TEST_ONLY kod/QA gecti; M08 GUI/art/rights/Engine-LFX/device kabulleri M08-001/002/006 ve daha sonraki gorevlerde ACIK, owner GUI/cihaz/Engine LFX final kabul gorevleri acik. 12 mükerrer kaynak/test satırı kaldırıldı, kapsam ilgili orijinal görevlerin notlarına taşındı. M06-001 ve M07-001 kaynak kapsamı tamamlandı; henüz çalıştırılmamış Unity/Python veya owner art/device kapılarına PASS verilmedi. VUF-M05-015 Codex teknik test/duzeltme/kanit oturumu tamamlandi; M05 milestone'unun owner/GUI/gercek Engine kimlikleri/mobil kabulleri acik. Bitenlerden bir bolumu sadece kaynak uygulama veya belirli SHA'da testtir, milestone onayi degildir.


## MILESTONES | TEK GOREV ID FORMATI

> Her yapılacak iş, geliştirme, test ve Codex oturumu **aynı düzeyde** `VUF-MXX-NNN` kodudur. Başka görev türü / alt görev ID'si yoktur. **137 görevlik mevcut kapsam sabittir**, 64 ilk görev dahil ve geriye dönük kaynak uygulama kayıtları içinde. Yeni kod yazmak görevi artırmaz, mevcut görevi ilerletir. Eski iç içe S/T kayıtları eski sürüm tarihçesine aittir; R/C oturum adları yalnız kanıt ve sürüm açıklamasıdır, görev kodu değildir.
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

- [x] VUF-M06-001 Five-theme CANDIDATE layered World/Chapter/Gameplay maps and Coral Reef Restoration, Marine Collection, My Aquarium and New Region reveal scene layers; no flattened UI/buttons/text. **SOURCE IMPLEMENTED:** `factory/image_processor/representative_scene_pack.py` renders 19 identified scenes × 3 independent RGBA layers = 57 candidate PNGs (0/120/340 milli-parallax + deterministic SHA receipts); `tests/test_representative_scene_pack.py` contains 11 authored regression/negative tests. **NOT RUN on current SHA:** local Python/Unity; actual final art, owner acceptance, true device display and gameplay consumer stay open under M06-002/003/007 and downstream M09/M10. Closure here denotes *candidate-layer source delivery only*, not milestone acceptance.
- [ ] VUF-M06-002 Character/mascot reference sheets with consistent original poses and silhouette identity. **PARTIAL SOURCE:** `factory/visual_director/character_pose_review.py` safely accepts externally supplied reference + 5 original pose PNGs, validates SHA/alpha/canvas/anchors and emits 6-panel candidate comparison receipts; `tests/test_character_pose_review.py` adds 8 authored negative tests, **NOT RUN**. **STILL MISSING:** real licensed/original reference and pose master files for the five games, owner identity comparison and rights approval. A test-only geometric pose is not a finished mascot.
- [x] VUF-M06-003 Responsive/background **source exports and synthetic guide overlays** implemented for five themes: `factory/image_processor/representative_scene_pack.py` now accepts source layers at 1×/2×/3× (180×320 / 360×640 / 540×960), `factory/image_processor/scene_viewport_export.py` composes SHA-verified independent BG/distant/near PNGs into 9:16, 6:13 tall-phone and 3:4 tablet **aspect-preserving** preview PNGs, 0/120/340 milli-parallax camera offsets and optional synthetic safe-area line guides, writes only to NEW external output folders; no runtime buttons/text flattening, no release rights. Existing Unity `VufSceneLayerReviewWindow.cs` now accepts 3× layers; `VufParallaxCanvasController.cs` remains view-only. Authored **9 Python test cases** and **1 new Unity EditMode case**; adjusted prior Python scale negative test. **CODE/SOURCE COVERAGE ONLY; new Python/Unity NOT RUN at this SHA, real Unity GUI/manual/device/GPU/parallax/owner approval stay OPEN and are explicitly tracked by VUF-M06-007 + M09 QA.**
- [x] VUF-M06-004 Title/theme naming, provenance and version pinning through generation and export.
- [x] VUF-M06-005 R21/R28/R30: Real PNG katman compositoru ve 5×3 concept preview; eksik reef/aquarium/region final sahneleri var (`layer_compositor.py`, `concept_showcase.py`).
- [x] VUF-M06-006 R21/R52: theme source SHA, PNG provenance ve generated asset metadata (`sample_sprite_pack.py`, `layer_compositor.py`).
- [ ] VUF-M06-007 Codex: after finishing all feasible M06 source work, run ONE genuine Windows Python 3.12 + Unity 6000.6.5f1 milestone test on the FINAL exact SHA, including 19 scene/57 layer candidate PNGs, 1×/2×/3× responsive 9:16/6:13/3:4 synthetic guides and live visual camera offsets from `scene_viewport_export.py`, 9 additional Python cases and 1 additional real Unity 3× acceptance case, source/hash/provenance, 11 scene Python + 8 pose Python tests, real Unity Scene Layer Studio (+6 new EditMode tests), view-only parallax Runtime (+5 new EditMode tests), imported copied assets/safe area, adversarial paths/approvals, and single Drive 02_CODEX_LOGS report. **NOT RUN**; GUI screenshots/device/owner original art/rights marked separately, never fabricated.

**Exit:** At least one representative scene package per profile, owner-reviewable.

### VUF-M07 | Animations, VFX and reduced-effects parity

- [x] VUF-M07-001 Idle, reward, win/fail, tile, special/combo, booster/obstacle, character, region and UI transition **view-only effect contracts**. **SOURCE IMPLEMENTED:** `factory/vfx_builder/view_event_timeline.py`: 5 themes × 14 event keys, actual Engine special/combo symbolic keys, reusable VF06 particle-preset pins, deterministic normalized frames/replay SHA, visual-only priorities/interrupt, mute and reduced-motion/cue-LOG-ONLY, manual 0.25/0.5/1/2× cursor. `tests/test_view_event_timeline.py`: 10 authored Python regression/negative tests **NOT RUN**. Separate M07-002/006/009/013/014 still require true Unity animation playback, UI Studio, visuals and real proof. Source contract completion is not an Engine release/gameplay PASS.
- [x] VUF-M07-002 **SOURCE IMPLEMENTATION COMPLETE (2026-10-18)**: actual Unity SpriteRenderer view-only animation binding + manual frames/FPS/loop/ping-pong, 0.25×/0.5×/1×/2× speed, original Sprite pivot/PPU geometry diagnosis, alpha checkerboard, zoom/clipped preview, alternate-atlas geometry-checked replacement, priority/channel interruption, deterministic replay and reduced-motion semantics. Existing `VufSpriteClipBuilderWindow.cs` now reuses common `VufSpritePlaybackPreview.FrameSequence` and provides TEMP **DontSave** Scene SpriteRenderer preview with auto-cleanup; existing clip exporter & VufUiTween unchanged. `unity_package/Runtime/VufSpritePlaybackPreview.cs` + GUID .meta and `VufSpritePlaybackEditModeTests.cs` (11 authored real SpriteRenderer NUnit tests) + GUID .meta are registered in `Tools/validate_repo_structure.py`. **SOURCE ONLY**: actual Windows Unity compilation/EditMode, interactive manual screen recordings, event↔Engine parity, real device/GPU/owner art remain **NOT RUN/OPEN** under existing M07-006/009/013/014 and M09 acceptance tasks. A checked source task does NOT imply acceptance.
- [x] VUF-M07-003 Full/reduced-motion mode and optional middleware-absent fallback.
- [x] VUF-M07-004 Enforce no animation/VFX callback may mutate engine board, rewards or save transactions.
- [ ] VUF-M07-005 **SOURCE IMPLEMENTED, REAL HARDWARE ACCEPTANCE OPEN:** unified Editor `VufUnifiedVisualStudioWindow.cs` displays explicit event/profile/cue logs (audio/haptics NOT actuated), frame cursors, procedural FX frame, actual temporary Unity ParticleSystem.particleCount, Editor Stopwatch CPU update duration, Unity Editor allocated-byte telemetry, estimated raw Sprite/FX RGBA memory, atlas source SHA. It labels physical phone FPS, GPU draw-call/texture budget, audio/haptic playback as NOT RUN/UNVERIFIED; no fake profiling. `VufVisualEventCatalog.cs` pins all 14 event channel/priority/cue choices. **STILL OPEN:** genuine Windows Editor interaction and device/GPU profiling, draw-call budget and source art approval; source-only metrics not considered mobile performance PASS.
- [ ] VUF-M07-006 **OWNER REQUIRED: UNIFIED MANUAL SPRITE & VFX LAB SOURCE IMPLEMENTED; OWNER GUI ACCEPTANCE OPEN.** New `Tools/MATCH3/Unified Sprite and VFX Review Studio` (`unity_package/Editor/VufUnifiedVisualStudioWindow.cs`) integrates already adopted `VufSpritePlaybackPreview` real temporary SpriteRenderer, existing `VufVfxLabWindow` five Unity particle presets, existing procedural `VufFxSheetPreviewWindow.Parse`, 5 game profiles ×14 visual events, 5 Engine special names/15 unordered combos, same-channel priority/replay/interruption, pause/scrub/reduced-motion, .25/.5/1/2× and loop/pingpong, sprite alpha/pivot/zoom guide, synthetic three device ratios, simultaneous imported atlas A/B and geometry-safe swap. FX atlas/still SHA and metadata validated from imported COPIES; FX/preset mismatch rejects before SpriteRenderer mutation. No production gameplay/score/reward/save/audio/haptic writes; source importers untouched, TEMP objects never saved. A reproducible JSON `CANDIDATE_ONLY` review receipt can be copied or exported ONLY as a NEW file OUTSIDE repo (no overwrite). **NOT RUN:** actual owner GUI, screenshot, device/GPU, visual polish/rights and final production Engine event integration. Source does NOT equal owner acceptance.
- [x] VUF-M07-007 R22: 5 deterministic VFX sprite-sheet + reduced-motion still; full event/FX ontology eksik (`procedural_fx_sheet.py`).
- [x] VUF-M07-008 R05/R23/R24: Sprite clip authoring, scrub, ping-pong/loop ve procedural FX-to-Unity clip exporter (`VufSpriteClipBuilderWindow.cs`, `VufFxClipExporterWindow.cs`).
- [ ] VUF-M07-009 **REAL UNITY/ENGINE PARITY GATE OPEN; SOURCE ADAPTER EXPANDED.** New `VufVisualEventCatalog.cs` maps 5 profiles, 14 typed Python `view_event_timeline.py` events with exact channels/priorities/durations/FX presets, R50 source-pinned HorizontalLine/VerticalLine/Area/Color/Targeted and 15 unordered special pairs. Unified Editor Stage calls actual `VufSpritePlaybackPreview.TryPresentViewEvent` with semantic key/priority, temporary Scene SpriteRenderer, live FX ParticleSystem, hash-verified imported FX sheet, replay/interrupt/motion/atlas swap. Added `VufUnifiedVisualStudioEditModeTests.cs` six NUnit contract/negative tests and `tests/test_m07_unified_visual_catalog.py` five Python source-parity tests. **TESTED:** real Unity EditMode 126/126 PASS plus Python 404 PASS/9 SKIP on `469233c`. **STILL OPEN:** manual Unity GUI, latest Engine/LFX exact production replay parity, chained combo/atlas swap device performance and physical GPU. Existing M07-014 is one full QA gate.
- [x] VUF-M07-010 R12/R38: CanvasGroup tween + reduced-motion gercek source ve yeniden kullanim (`VufUiTween.cs`).
- [x] VUF-M07-011 R06/R12/R22/R24: gameplay/save/score/reward mute eden presentation-only runtime/Editor sinirlari (`VufUiTween.cs`, `VufVfxLabWindow.cs`).
- [x] VUF-M07-012 R06/R23: Manual Unity Particle Lab ve imported sheet frame preview (`VufVfxLabWindow.cs`, `VufFxSheetPreviewWindow.cs`).
- [ ] VUF-M07-013 **UNIFIED 5-THEME OWNER MANUAL FX/SPRITE STUDIO SOURCE IMPLEMENTED, OWNER GUI EVIDENCE OPEN:** `VufUnifiedVisualStudioWindow.cs` now provides 14 selectable visual events and five Engine special variants/15 pair keys, actual TEMP Scene SpriteRenderer and ParticleSystem, real imported sprite/FX sheet/still SHA receipt validation, reduced-motion, cue logs, 0.25×–2× preview, synchronized FX frame/sprite scrub, real Sprite atlas preview swap, pivot/alpha checkerboard, synthetic 9:16/6:13/3:4 viewport guides, simultaneous A/B candidate visual comparison, Editor-only particle/CPU/texture/memory diagnostics and safe external NEW review receipts. Six Unity Studio NUnit and five cross-language Python tests PASS on `469233c`; interactive Unity GUI/owner screenshots NOT RUN and physical GPU/haptic/audio acceptance OPEN. Existing auxiliary Sprite Animation Builder and standalone FX Lab retained, no redundant animation framework.
- [x] VUF-M07-014 Codex M07 full technical verification COMPLETE on GitHub SHA `469233cccb1ad533c6b32cd946e915e98bc22543` (2026-10-18): Python 413 tests, 404 PASS, 9 Windows symlink SKIP, 0 FAIL; Unity 6000.6.5f1 EditMode 126/126 PASS, 0 FAIL; 74 Python syntax modules and manifest/layout gates PASS. Two Codex fix commits pushed normally: `b8bb46d` (outdated test assertions) and `469233c` (`ExecuteAlways` for SpriteRenderer cleanup). Evidence report: https://drive.google.com/file/d/1Cu_7uKbcHiH_xXRj_OIKiQIyyW-gt2ia/view ; NUnit/log ZIP: https://drive.google.com/file/d/1A8gLx-TMAEkmA1FP8RBgQwMIGH9l2tBt/view . GUI owner visual acceptance, device/GPU, art rights, real audio/haptic and exact Engine/LFX runtime parity NOT RUN: see open M07-005/006/009/013. This check means completed Codex technical test, NOT overall M07 signoff.

**Exit:** Real Unity-consumable effects and replay-invariant acceptance.

### VUF-M08 | Unity UI and asset packaging adapters

- [ ] VUF-M08-001 **KISMI SOURCE + GERCEK UNITY EDITMODE TEKNIK PASS (2026-10-18, `de5b8cc`):** `VufScreenShellBuilderWindow` uGUI/Candidate Canvas, `VufInteractiveUiReviewWindow` local TEST_ONLY tap, 28 Coral draft screen, 5 draft skin, sentetik phone/tablet safe-area ve `VufCandidatePackImporterWindow` EDITOR-only SHA-256 kaynak kopya import/deny kurallari mevcut. M08-010 full Python **416 PASS/9 Windows symlink SKIP**, Unity EditMode **140/140 PASS**; importer **4/4**, interactive UI review **5/5**. Gercek **interactive Unity GUI ve diskte dosya-backed import NOT RUN**, final uGUI/TMP vs UI Toolkit owner karari, telefonda safe-area/animasyon/GPU ve sanat haklari OPEN. Unity EditMode PASS, owner cihaz kabulu anlamina gelmez.
- [ ] VUF-M08-002 **KISMI SOURCE + GERCEK UNITY EDITMODE TEKNIK PASS (`de5b8cc`):** uGUI test-only screen builder ile 28 Coral screen ID, 5 taslak skin, 8 MOCK state, EN/TR/stress, z-order/anchors/touch bounds, `VufUiTween` reduced-motion ve sadece lokal log yazan disposable EDITOR_ONLY_TAP var; gameplay/save/reward/purchase baglantisi YOK. Codex M08-010: full Python 416 PASS/9 SKIP ve real Unity 140/140 PASS; uGUI review **5/5**. **OPEN/NOT RUN:** gercek Editor GUI/touch kaniti, owner locale/art kabul, bes oyuna ozel nihai ekran sozlesmeleri ve Engine/LFX olay/aksiyon entegrasyonu.
- [x] VUF-M08-003 **TEST_ONLY OFFLINE SOURCE PAKETLEME TAMAMLANDI VE TEKNIK OLARAK DOGRULANDI (`de5b8cc`):** `candidate_pack.py` ile secilen 5 temadan birinin aday matematiksel PNG katmanlari/R52 38 prototype sprite/VF06 5 FX seti+reduced-motion EN/TR DRAFT ve immutable SHA-256 receipt; gercek VF04 PNG atlas (raporlanan Coral paketi **1976×52, 38 sprite**, atlas SHA256 `265ea359773c5c803b8df28aace3dd647a99215e64ed87cca0301519d73d6a97`). Codex M08-010 Python pack **8/8** + cross-language **4/4**, tam Python **416 PASS/9 Windows SKIP**, Unity 6000.6.5f1 EditMode **140/140 PASS**; ayri kopya PNG bozulmasi hash mismatch ile beklendigi gibi reddedildi. Aday `TEST_ONLY` ve release_allowed=false. **BU SADECE ADAY SOURCE PAKETI:** lisansli final sanat, lokalizasyon, production SpriteAtlas/import, Android/iOS player dagitimi, Addressables opsiyonu, cihaz/GPU ve owner signoff HALA OPEN (M08-001/002/006 ve downstream QA).
- [x] VUF-M08-004 Offline/missing image/incorrect manifest/version conflict and rollback negative checks.
- [x] VUF-M08-005 Release scanner rejects test assembly, templates, raw reference art, secrets and generated evidence from game players.
- [ ] VUF-M08-006 **BAGIMSIZ TEST_ONLY SOURCE STUDIO + GERCEK EDITMODE PASS (`de5b8cc`):** `VufExternalPackSandboxWindow` bes taslak tema ad alani, import edilmis PNG SHA ve A/B preview, inert EN/TR offline fallback, `VufExternalPackViewStage` nonpersistent SpriteRenderer ve M07 14 view-only event whitelist; gercek oyun/save/revenue mutasyonu YOK. M08-010 total Python 416 PASS/9 SKIP, Unity 140/140 PASS; external sandbox/locale **9/9**, SpriteRenderer stage **3/3**. **ACIK:** interactive Unity GUI, file-backed imported bundle, final Engine/LFX SHA + ENG-M12 neutral replay ve gercek game runtime consumer/parity, owner art/rights, cihaz/GPU. Bunlar headless EditMode ile kabul edilmedi.
- [x] VUF-M08-007 R47: Unity SDK SpriteAtlasAsset V2 candidate authoring, production asset paketi degil (`VufSpriteAtlasV2Window.cs`).
- [x] VUF-M08-008 R09/R45/R46: SQLite restore ile bagimsiz manifest version/rollback diff negative checker (`catalog.py`, `preview_compatibility.py`).
- [x] VUF-M08-009 R44: Editor/tests/ref art/secret/evidence deny rules olan read-only player preflight (`player_pack_preflight.py`).
- [x] VUF-M08-010 **TEK TOPLU M08 CODEX TEKNIK TEST GOREVI TAMAMLANDI (2026-10-18), MILESTONE KAPANMADI.** Final TEST SOURCE & GitHub `main` SHA `de5b8cc1b0938294d8c4aa1f5405240d29817d74`; Codex yerel `HEAD`, `origin/main`, GitHub `main` ayni, clean, ek kaynak fix/commit gerekmemis. Python 3.12.10 **425 discovered / 416 PASS / 9 Windows symlink SKIP / 0 FAIL**; 78 Python modulu AST syntax PASS, sample manifest/structural control ve 90 Unity GUID PASS. Gercek Unity 6000.6.5f1 EditMode **140/140 PASS, 0 FAIL/SKIP**; importer 4/4, interactive UI 5/5, sandbox 9/9, SpriteRenderer staging 3/3; Coral TEST_ONLY bundle 81 hashlenmis payload (receipt dahil 82 dosya) ve VF04 atlas kontrolu PASS, ayrik bozuk PNG negatif fixture hash mismatch exit 2. Player preflight 9 NON_SHIPPING_MARKER bulmus, `release_allowed=false`; clean production player build YAPILMADI. **Rapor:** https://drive.google.com/file/d/1wXbzSNGdUNJ1rEpSu6Ww3Vu28FAavbgP/view ; **kanit ZIP:** https://drive.google.com/file/d/1f2FFa45a_-zPEzR6r0G93oi8QM2TQMUn/view ; Codex beyanli ZIP SHA-256 `D4BBB050C12432F09F605FEFED602E6E91CF90B6A1BC70EE200F30E803976F43` (GitHub/Drive raporu ve ZIP metadata okundu, arsiv bayt digest'i bu asistan oturumunda bagimsiz hesaplanmadi). **M08-001/002/006 ve sonraki kabul kapilari ACIK:** interactive Unity GUI/file-backed import, owner art/rights, cihaz/GPU, final Engine/LFX/ENG-M12 replay, uretim player dislama kaniti; teknik PASS milestone/art/runtime onayi degildir.

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
