# Dino Islands | Visual Factory Style Bible (SOURCE DRAFT)

**Game namespace:** `Dino_Islands` | **Owner approval:** NOT GIVEN | **Actual original artwork:** NOT PROVIDED | **Font licensing:** UNVERIFIED | **Release:** BLOCKED.

This is a source-level creative direction and reference checklist. It is not an image asset, an original character sheet, a visual sign-off, or a licensed master. Source of truth: `factory/visual_director/style_profiles.v1.json` plus `m02_identity_catalog.v1.json`. A separate artist must supply original works with provenance and an owner must approve them.

## Creative identity

**Art direction:** Colorful prehistoric adventure; friendly sculpted creatures and lush layered islands

**Story and mood:** Friendly discovery with living creatures, sculpted eggs and botanical habitat layers.

**Materials and finish:** Touchable clay volumes, moss/light green depth, friendly fossiled edges. Material grammar: `clay_leaf`. Mascot/guide role: `juvenile_dino_guide`. World progression identity: `island_habitat`. Particle style: `leaf`.

**Silhouette language:** Fossils, eggs, leaves and gemstones with thick readable outer shape

**Symbol families with unique non-hue contours:** `egg`, `fern`, `claw`, `fossil`, `leaf`. These are ART DIRECTIVES, not finished vector/logo/character artwork. Maintain six generic accessible source tile silhouettes separately: circle, triangle, diamond, star, crescent, shield.

## Working palette and accessible typography

| Semantic token | Draft color | Usage |
|---|---|---|
| background | `#163D31` | background behind safe-area content |
| surface | `#34715A` | card and modal surface |
| accent | `#AEDC6D` | non-essential ornament, secondary semantic cue |
| cta | `#FBE184` | principal button fill |
| cta_label | `#23402E` | primary button label |
| text | `#FFFFFF` | body label and selectable information |

Computed WCAG approximate normal-body contrasts: **text/surface 5.74:1**, **text/background 12.03:1**, **CTA label/CTA 8.79:1**. These pass the 4.5:1 source-color criterion; this does NOT prove final art/text over rendered composite backgrounds.

**Source typography scale:** hero 40dp; page heading 30dp; section 24dp; body 17dp; caption 14dp; button 17dp. Fonts remain OS/system fallback until actual font source and embedding rights are supplied; no commercial font is implicitly authorized.

**Grid:** 4 phone columns / 8 tablet columns, 16dp gutters, 16dp phone side margins, 32dp tablet margins, minimum 44dp interactive targets. Spacing scale: 4, 8, 12, 16, 24, 32, 48dp. Component radius: card 18dp, modal 24dp, CTA 16dp.

| Review device | Draft dp canvas | Safe top / bottom |
|---|---:|---:|
| compact_phone | 320 × 568 | 0 / 0dp |
| tall_phone | 393 × 852 | 24 / 24dp |
| large_phone | 430 × 932 | 24 / 24dp |
| portrait_tablet | 768 × 1024 | 24 / 16dp |

**Source UI state set:** Ready, Loading, Offline, Error, Owned, Claimed, Disabled, Pending. Genuine game state authority remains in Engine; do not hard-code gameplay actions into background art. The semantic component set shared across five titles is primary_cta, secondary_cta, card, modal, badge, counter, tab, progress, disabled_reason, pending_state. Accessibility must not rely on color alone and must preserve readable copy in English, Turkish and long-text stress conditions. Reduced motion is a full semantic fallback, not simply fewer particle frames.

## Environment depth planning

Original scene layers, rear to front: `volcano_sky` → `island_mid` → `foliage_front` → `ambient`. Source foreground elements must leave semantic UI hit targets unobstructed; backgrounds must not contain flattened buttons, score numerals, CTA copy or license-uncleared brand logos.

## Original artist master/reference sheets still required

1. **juvenile_dino_identity_reference**: Original creator deliverable with full-res master, transparent/cropped variants as applicable, SHA-256, owner/source and rights receipt. **Status: MISSING/UNAPPROVED.**
2. **dinosaur_hatchling_family**: Original creator deliverable with full-res master, transparent/cropped variants as applicable, SHA-256, owner/source and rights receipt. **Status: MISSING/UNAPPROVED.**
3. **egg_and_fossil_icons**: Original creator deliverable with full-res master, transparent/cropped variants as applicable, SHA-256, owner/source and rights receipt. **Status: MISSING/UNAPPROVED.**
4. **prehistoric_habitat_layers**: Original creator deliverable with full-res master, transparent/cropped variants as applicable, SHA-256, owner/source and rights receipt. **Status: MISSING/UNAPPROVED.**
5. **island_map_landmarks**: Original creator deliverable with full-res master, transparent/cropped variants as applicable, SHA-256, owner/source and rights receipt. **Status: MISSING/UNAPPROVED.**
6. **dino_tile_symbols**: Original creator deliverable with full-res master, transparent/cropped variants as applicable, SHA-256, owner/source and rights receipt. **Status: MISSING/UNAPPROVED.**

Mandatory identity reference-sheet slots: original_character_turnaround, original_silhouette_swatch, component_palette_board, world_depth_map, icon_geometry_board. Any mascot/character family requires five consistent original poses: **idle, greet, celebrate, concerned, action**. Use `character_pose_review.py` to inspect hash/alpha/alignment from owner-provided originals, never to self-certify identity, originality or license.

## Visual hazards and prohibited patterns

- Avoid species identity drift across poses and giant scary creature faces in family-facing UI.
- Never use color as the only egg differentiation or cover the tap hitbox with foliage.


## Implementation and acceptance gates

Original environment and character artworks, UI graphics, editable layers and font files must be supplied under an explicit rights agreement; no stock/brand/game-lookalike images can be silently copied. Use existing VUF Editor systems for swatch/style review, layered uGUI generation and sprite/atlas preview. The actual original owner art and signed visual decisions must be linked by SHA.

**Next independent checks:** (1) canonical source JSON SHA and theme identity, (2) valid palette/contrast/silhouette, (3) exported source art SHA provenance and full editable layers, (4) real Unity Editor GUI checks with actual original imported PNGs, (5) physical phone/tablet tests and owner/rights signoff. TECHNICAL source review is not production approval.

**Stage:** `SOURCE_STYLE_BIBLES_REVIEW_ONLY` / `release_allowed=false`.
