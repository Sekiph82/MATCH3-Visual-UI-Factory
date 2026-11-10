# Codex Task Automation

This file configures sequential, cost-aware Codex work for this repository. It adds no task ledger and does not authorize product work by itself.

## Owner delegation | 2026-10-22

- The owner explicitly delegates autonomous implementation, validation, and the canonical `TASKS.md` / `AGENTS.md` transitions for this repository to the Codex agent running this task. This supersedes historical lines that assign lifecycle writes to ChatGPT.
- The root `TASKS.md` remains the only task ledger. Use its explicit `Current Task`, `Required Actor`, `Current Milestone`, `Next Task`, and `Authorized Queue Batch`; never infer the initial task from checkbox order.
- Continue through only the exact ordered batch recorded in `TASKS.md`. When a task is blocked by a genuine human gate, record its question, mark only that task blocked, and continue to the next independent ready item in the authorized batch.
- Queue claims, task transitions, dashboard metadata, and owner answer application are local-only. Never push or merge unless the currently selected canonical task explicitly authorizes publication.
- The local heartbeat resumes this same repository queue independently of dashboard visibility or project selection. The dashboard is read-only for task state; it may append only the owner's submitted answer to the target project's dedicated JSONL inbox.
- Never fabricate human approval, device/GUI evidence, legal sign-off, or test results. A task can be technically complete while separate owner acceptance tasks remain open.

## Authority and task start

- Follow all existing repository instructions, the repository-declared canonical task source (normally root `TASKS.md`), and any active task prompt or handoff. More specific owner decisions and project gates take precedence.
- Before implementation, read the exact current task, its acceptance criteria, required prior audits/contracts, and any mandatory project-control files. If a required prompt, audit rubric, or authority file is unavailable or contradictory, stop and report the specific blocker.
- Start only the explicitly named current task when its state, required actor, prerequisites, and owner authorization permit Codex work. Never infer work from the first unchecked row, invent task scope, or cross a milestone gate.
- Continue through multiple tasks only when an existing owner-approved master prompt or canonical task state authorizes the exact ordered batch. Stop at the batch boundary, independent-audit handoff, owner decision, or blocker.
- Do not edit task status, audit results, or handoff state when this repository assigns those duties to an owner or independent auditor. When Codex is authorized to update state, update only the declared canonical files and required control-plane mirrors; never create a competing ledger.

## Sequential and cost-aware execution

- Use one implementation worker at a time. Add a read-only reviewer only when the repository workflow allows it and it does not replace the named independent auditor; do not spawn a large agent team for routine tasks.
- Run only task-required focused checks during implementation. Run the complete milestone acceptance suite once at its explicit closure, unless the active project criteria require a stricter check.
- Prefer the existing checkout when it is safe. If project rules allow a task-owned worktree, keep it isolated and remove only that exact worktree and branch after authorized publication. Preserve owner changes, caches, evidence, and unrelated temporary files.
- Avoid unnecessary dependency installs, repeated full suites, duplicate clones, workflow dispatches, paid services, and storage-heavy artifacts. Honor all project-specific CI, network, licensing, native-device, and release constraints.

## Completion and stop conditions

- Report exact files, commands, results, skipped checks, commits, and remaining owner/audit gates. Builder evidence is not independent acceptance.
- Publish only through the branch, review, or mainline procedure authorized by this repository's task source and owner instructions.
- Stop for required human approval, protected owner data, unavailable native/device access, unapproved external costs, or unresolved policy conflicts.
