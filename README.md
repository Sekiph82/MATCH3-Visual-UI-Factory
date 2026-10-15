# MATCH3 Visual & UI Factory

A shared Unity 6.6 visual-authoring tool for Coral Rescue, Garage Legends, Dino Islands, The Fractured Realms, and Wonder Pop.

## Current state

**M00 bootstrap/prototype, NOT a production-ready factory.** The first editor window can inspect an explicitly selected source Texture2D, preview horizontal sprite-sheet frames, adjust playback rate, and inspect aspect/safe-area guides. It is not an art generator or proof of full UI/VFX/animation/game integration. Unsupported inspector features are explicitly labeled.

**Upstream integration remains blocked** until the Engine and Level Factory have independently closed their required milestones. This repository must never ship artwork to the Engine, implement match rules, or silently award rewards.

## Unity setup (non-destructive)

1. Fetch this repository into the already existing local `MATCH3-Visual-UI-Factory` checkout, only after checking local modifications. Do not overwrite uncommitted work.
2. In Unity Hub, **Add project from disk** and select that existing folder. Use Editor **6000.6.5f1**.
3. Open **Tools > MATCH3 > Visual & UI Factory Studio**. The M00 manual texture/sprite-preview window will appear.
4. To test the preview, select a licensed/original Texture2D already imported into this VUF project. Set horizontal frame count and playback.
5. Run `python -m unittest discover -s tests -v` for manifest negative tests. No paid API, credentials or auto asset downloads are required.

## Roadmap

One factory, five themed design systems; 28 Coral Rescue experience IDs (26 requested plus Home and Gameplay), layered responsive runtime UI, editable sprites/atlases, animation and VFX, QA with human review, and versioned Unity export packages. Full VUF-M00..M11 acceptance criteria and dependency gates are tracked only in root `TASKS.md`.

## Release safety

No output here is an approved creative master. Owner-reviewed art must carry rights and source receipts. The studio's prototype overlay is **not** a real iOS/Android device test, a physical haptics test, or a production asset pack. Never put Editor scripts, references or test code inside players.
