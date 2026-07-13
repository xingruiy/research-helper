# Template: `.codex-impl/state.md`

Copy this structure when creating the state file in Phase 1. Keep it current: update
the table the moment a package changes status or gains a session id — the state file is
what makes an interrupted run resumable.

```markdown
# codex-impl state — <project name>

- Plan: `.codex-impl/plan.md` (materialized <YYYY-MM-DD> from the approved session plan)
- Model: gpt-5.6-sol · Sandbox: workspace-write
- Checkpoint commits per package: <yes/no, per the user's Phase 3 answer>

## Packages

| ID | Scope (one line)                  | Depends on | Status  | Session id | Resume rounds | Files touched |
|----|-----------------------------------|------------|---------|------------|---------------|---------------|
| 01 | Data model + storage layer        | —          | done    | <uuid>     | 1             | src/models.py, src/store.py |
| 02 | API endpoints over the store      | 01         | running | <uuid>     | 0             | — |
| 03 | CLI wiring + docs                 | 02         | pending | —          | 0             | — |

## Log

- <YYYY-MM-DD HH:MM> pkg-01 started, session <uuid>
- <YYYY-MM-DD HH:MM> pkg-01 resume 1: test_store failures (output attached to thread)
- <YYYY-MM-DD HH:MM> pkg-01 verified done; checkpoint commit <sha>
```

**Status values**: `pending` → `running` → `verifying` → `done`. Use `split` when a
package was subdivided mid-flight — list the child package IDs in its scope line and
never execute the parent.

# Skeleton: `.codex-impl/pkg-NN-prompt.md`

Each package prompt must stand alone — Codex sees none of the orchestrator's
conversation. One page or less; if it won't fit, split the package.

```markdown
# Package NN: <one-line goal>

## Goal
<What exists and works when this package is done — 2–4 sentences.>

## Context
<2–3 sentences on what prior packages established, if this one builds on them.
State outcomes, never paste transcripts.>

## Plan excerpt
<The verbatim portion of the plan this package implements.>

## Files & entry points
<Concrete paths to create or modify, and the key functions/classes involved.>

## Constraints
<Project conventions, dependencies to use or avoid, style expectations.>

## Definition of done
<The commands that must pass (build, specific tests) and observable behavior.>

## Boundary
Do not modify anything outside this package's scope. If a needed change falls
outside it, stop and report instead of making the change.
```
