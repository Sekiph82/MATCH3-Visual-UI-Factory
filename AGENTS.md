# Repository automation authority: Claude Code (2026-11-10)

This is the active role assignment. The historical Codex automation guidance
in prior commits/logs remains historical evidence only. Root `TASKS.md` has
137 frozen VUF-MXX-NNN IDs and 53 open items at handoff; **no shadow tracker**.

## Single executor and scope
- **Claude Code** selects, implements, fixes, tests, documents, and reviews ALL
  open tasks in this repository. Consult `CLAUDE.md` for standing instructions,
  `docs/CLAUDE_FULL_BACKLOG_HANDOFF.md` for the owner grant and gates, and
  `.claude/skills/finish-vuf-backlog/SKILL.md` for the repeated execution loop.
- A task whose original label says `Codex:` is assigned to Claude now without
  renaming the original immutable title/ID. Do not wait for a second Codex.
- Work through technically feasible tasks autonomously. A legitimate external
  dependency blocks **only its affected task**, not the entire backlog.
  Record `BLOCKED_EXTERNAL:<reason and required evidence>` in that row, keep
  its [ ] checkbox, and move to the next feasible task. Never invent approval.

## Task lifecycle
- Before source edits inspect live git status/remote, task text, prior exact-SHA
  evidence, canonical Engine/LFX upstream API, existing donor and license.
- Add forward criteria before new feature changes, code/tests, native manual
  QA, and honest real command outputs. Document SHA+test counts for each
  milestone. No fake source-only proof used as device or PlayMode proof.
- Update only existing root TASKS item lines: technical evidence [x] only when
  the entire *original* task scope is verifiably satisfied. Otherwise keep [ ].
  Do not renumber or invent 138th item.
- A separate read-only Claude reviewer is a useful adversarial **peer check**;
  it cannot replace an independent owner, legal, physical device, artist
  rights, or authoritative Engine/LFX acceptance.
- A clean `main` with verified `origin` and exact SHA permits ordinary
  additive commits and `git push origin main` using the user's authenticated
  GitHub identity. Never force-push, hard reset, git clean, erase owner files,
  override a dirty local checkout, alter non-VUF repositories or manufacture
  release tags.

## Local and external tests
- Existing Windows checkout:
  `C:\Users\sekip\Desktop\GAMES\MATCH3 GAMES\MATCH3-Visual-UI-Factory`.
  Unity **6000.6.5f1**, Python **3.12.x**; local tests only.
- Full Python: `python -B -m unittest discover -s tests -p "test_*.py" -v`.
  Structure: `python -B Tools/validate_repo_structure.py`.
  Existing PowerShell scripts: `scripts/run_source_checks.ps1`,
  `scripts/run_unity_editmode.ps1`, `scripts/prepare_visual_factory.ps1`.
- No GitHub Actions/workflow dispatch, paid provider, emulator installation,
  unauthorized local disk cleaning, owner original/artwork deletion, or source
  copied into Engine/LFX. Network/Drive integrations require genuine access.
- Existing Google Drive six-folder VUF workflow stays the preferred source of
  prompts/criteria/results/evidence. If authenticated Drive is unavailable,
  keep truthful staged local evidence outside Git and a redacted in-repo
  technical summary, disclose inability to upload, and continue.

**Stopping:** After each session, state real progress, exact HEAD/working-tree
status, tests actually run, unrun gates and next eligible task. Do not pretend
an unattended background agent will run when no Claude session exists.
