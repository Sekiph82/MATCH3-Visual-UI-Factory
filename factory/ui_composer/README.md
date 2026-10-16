# VF-07 | Real, layered Unity UI Composer (prototype)

Unity menu: **Tools > MATCH3 > Interactive UI Composer**.
The prototype creates NEW, non-overwritten uGUI `.prefab` candidates containing
an actual `Canvas`, `CanvasScaler`, `GraphicRaycaster`, `Image` layers,
`Text` and a `Button`. The Button is deliberately `interactable=false`
because **no Engine gameplay action or reward authority is connected**.
`VufSafeAreaFitter` is attached to the content RectTransform for phone insets.
Profiles: all five games. Available source-level *layout archetypes*: Home,
Gameplay HUD, World Map, Shop, Events, Collection, Settings.

**Not implemented:** full 28 Coral experiences as interactive prefabs, real
screen artwork, callbacks, data bindings, font approvals, localization,
button actions, actual animations, device testing or playmode verification.
Editor must compile Unity 6000.6.5f1 and produce a prefab before saying this
works outside source code. The first build needs `com.unity.ugui@2.6.0`
which the UPM package declares. Approved asset masters are never replaced.

## R08 | Data-driven 28-screen candidate skeletons

**Tools > MATCH3 > 28-Screen Shell Builder** reads **28 stable Coral IDs**
directly from the packaged copy of `schemas/coral-experiences.v1.json` and
loads authentic **DRAFT** per-title color tokens from
`factory/visual_director/style_profiles.v1.json`. The copies under
`unity_package/Editor/Resources/` must remain byte-for-byte identical to
their canonical originals; `Tools/validate_repo_structure.py` enforces parity.

Every supported 28-ID experience creates a **new non-overwriting candidate**
Canvas/uGUI prefab. Template kinds select separate page, modal, ceremony,
overlay, playable-board or mode *layout skeletons*. The exported root has
`VufCandidateScreenMarker` recording selected title, exact contract ID,
surface type, policy gate and `CANDIDATE_NOT_APPROVED`. Pages with explicit
policy gates stay disabled. Real Buttons exist but are
`interactable=false`; all visual placeholders visibly say that branded
source artwork and Engine/game binding remain missing. `VufSafeAreaFitter`
is placed on the candidate's safe-area content node.

**28 named candidate shells are not 28 polished screens.** No product artwork,
animation, fully working layout, game source, rewards, purchases, localization,
real screen actions, original rights or owner aesthetic approvals are implied.
The Unity Editor has not actually compiled these R08 changes yet. Test on
Unity 6000.6.5f1 before claiming runtime readiness. 


## R17: review-only state and locale copy stress
`VufReviewStateCatalog.cs` is deliberately an **Editor-only mock copy
utility**, NOT a runtime game state machine or complete translation table.
All eight possible review state labels can be inspected across all 28 Coral
draft screens using one of: `en`, `tr`, `stress`. Only Home and Gameplay
have explicit Turkish **draft** titles; other screens are visibly marked
`TR TASLAK` pending localization. Expanded stress copy is a synthetic
layout hazard probe, not shipping text. Every mock label also states
`NOT GAME STATE`.
The 28-Screen Shell Builder keeps actual gameplay action Buttons disabled,
feature-policy banners unchanged and candidate approval stage unmodified.
It allows manually saving only **new** named candidate prefabs (no overwrite).
`VufReviewStateEditModeTests.cs` defines three NEW EditMode tests covering
672 state/locale/Coral combinations, invalid state/locale rejection,
unchanged policy gates and five-profile palette preservation. These tests
and two source checks have not been run at R17 exact SHA. No source art,
copyright acceptance or real device UI is involved.


## R19 | Real draft heading intake coverage, without automatic translation

A reviewed source package is **not** generated automatically. Provide an
EXTERNAL UTF-8 JSON draft using the following small example:

```json
{
  "schema_version": 1,
  "stage": "LOCALIZATION_DRAFT_NOT_APPROVED",
  "profile_id": "Coral_Rescue",
  "locales": {
    "en": {"home": "Home", "gameplay_hud": "Gameplay"},
    "tr": {"home": "Ana Sayfa", "gameplay_hud": "Oyun Ekranı"}
  }
}
```

Run the **read-only** coverage and placeholder checker:

```powershell
python -B factory/ui_composer/locale_audit.py --draft "D:\\VUF_LOCALIZATION\\coral-draft.json"
```

Optional `--output-file "D:\\VUF_LOCALIZATION\\coverage-report-001.json"`
writes a new (never overwritten) external JSON QA report. Import a COPY
as TextAsset for `Tools > MATCH3 > Localization Coverage Studio`, which
displays missing headings, long-label risks and coverage but cannot push
translations into scenes or auto-enable policy-restricted pages.

The input must contain exactly the 28 stable Coral contract keys when
complete, but **incomplete drafts are deliberately accepted and reported
as incomplete**, not as a finished localization. `en` and `tr` draft
maps accept only known keys and nonempty Unicode values of <=240 characters.
Invisible/bidi control characters, duplicated JSON keys and broken or
mismatched `{named_placeholder}` tokens are rejected. Entry paths must
be outside Git; reports are never allowed to replace an existing file.
This is not a certified Turkish translation or right-to-left locale
engine, language QA, fallback-string generator or Unity text clipping test.

`tests/test_locale_audit.py` adds 18 offline Python cases; three separate
Unity EditMode tests cover the read-only coverage viewer and forged
approval/feature gates. They are SOURCE-DEFINED, NOT YET RUN at R19 SHA.
