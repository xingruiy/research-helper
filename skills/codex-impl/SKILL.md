---
name: codex-impl
description: |
  Delegate the implementation of an approved plan to the Codex CLI, executed as small,
  resumable work packages — one Codex thread per coherent piece, never the whole plan
  in a single call. Use this skill whenever the user wants Codex to implement, build,
  or execute the current plan — "implement the plan with codex", "hand this plan to
  codex", "let codex build it", "use codex as the implementer", "codex-impl" — even if
  they don't name the skill. Requires an implementation plan produced and approved in
  the current session; if none exists, this skill aborts and directs the user to
  produce a plan first. Do NOT use for writing the plan itself (plan first, then this
  skill), for the research pipeline stages (literature-survey / deep-dive /
  brain-storm / rank-ideas), or for implementing changes directly without Codex.
---

# Codex Impl

Given an implementation plan approved in the current session, drive the **Codex CLI** to
implement it the way a real person would: headless `codex exec` runs that record
genuine, resumable sessions in the user's own `~/.codex` history — one thread per
coherent work package. The failure mode this skill exists to prevent is monolithic
delegation: a single call carrying an entire large-project plan overloads one Codex
context window, stalls, and leaves nothing behind to resume. The discipline here is the
opposite: decompose first, keep every thread small, resume *within* a package, reset
*between* packages.

Pipeline: **Verify prerequisites → Materialize & decompose → Execute per package → Verify per package → Integrate & report**

The deliverable is the implemented working tree plus a **`.codex-impl/`** audit trail in
the project root: the materialized plan, a state file tracking every package and its
Codex session id, and per-package prompts and event logs. Because every session is
recorded locally, the user can reopen any thread interactively later with
`codex resume <SESSION_ID>`.

## Portability rules (Claude / Codex / any agent)

This skill must work identically in any coding agent. Therefore:

- Use only **plain-text questions in the chat** to interact with the user — never
  agent-specific UI tools (option pickers, forms, plan modes).
- Use only **bash + `python3` (stdlib)** for tooling. The one hard dependency is the
  **Codex CLI** (`codex` on PATH), checked in Phase 0.
- Drive Codex exclusively through plain `codex exec` shell commands — **never through an
  MCP server or any orchestrator-specific integration**. CLI runs behave identically
  from any agent, don't hit integration timeouts, and land in the user's own
  `~/.codex/sessions` history where they can be resumed from the terminal.

---

## Phase 0 — Verify prerequisites (hard abort if missing)

1. **A plan exists in the current session.** Qualifying plans: a plan approved through
   the agent's planning flow this session, or an explicit implementation plan written
   out in this conversation that the user signed off on. It must enumerate concrete
   changes — components to build, files to touch, steps in order. A general discussion
   of goals is not a plan. If no qualifying plan exists, **abort immediately**: state
   plainly that codex-impl executes an approved plan and does not write one, and direct
   the user to produce and approve a plan first. Do not synthesize a plan from the
   conversation and proceed. Stop.
2. **The Codex CLI is available**: `codex --version` succeeds. If not, abort and point
   the user at the install (`npm install -g @openai/codex`, or Homebrew) and
   `codex login` for authentication.

**Model policy**: every Codex call in this skill — initial and resume alike — passes
`-m gpt-5.6-sol`, unless the user explicitly names a different model.

## Phase 1 — Materialize & decompose

Create `.codex-impl/` in the project root and write the approved session plan
**verbatim** to `.codex-impl/plan.md`. This is the handoff artifact: every Codex thread
can be pointed at its section of it, and it survives orchestrator context compaction.
Mention once that the user may add `.codex-impl/` to `.gitignore` if they don't want
the audit trail committed.

Then split the plan into **work packages**. A package is one coherent piece — a module,
a feature, one refactor step — sized so a single Codex thread completes it with room to
spare in its context window. Working rules of thumb:

- One subsystem per package; roughly **≤5 files touched**.
- The package must be describable in a **self-contained prompt of a page or less**. If
  writing the prompt requires pasting half the plan, the package is too big — split it.
- Oversized packages are precisely what stalls Codex on large projects: the thread
  drowns in its own exploration and edit history. Small packages keep each thread's
  context short and its work verifiable.

Order packages by dependency (interfaces and data models before their consumers), then
record the package table in **`.codex-impl/state.md`** following
`references/state_template.md` (in this skill's directory). Show the user the package
breakdown in one compact list before executing — a misdrawn boundary is cheapest to fix
now.

## Phase 2 — Execute: one Codex thread per package

Work through the packages in dependency order. For each package `NN`:

**1. Write the prompt file** `.codex-impl/pkg-NN-prompt.md` (skeleton in
`references/state_template.md`): the goal, the package's plan excerpt, the concrete
files and entry points involved, constraints and conventions to respect, a definition
of done, and the boundary rule — *do not modify anything outside this package's scope*.
The prompt must stand alone; Codex sees none of the orchestrator's conversation. If a
prior package established something this one builds on, state it in 2–3 sentences —
never paste prior transcripts, which defeats the context budget.

**2. Start the thread** — exactly as a person running Codex headlessly would:

```bash
codex exec -m gpt-5.6-sol -s workspace-write --json \
  -o .codex-impl/pkg-NN-last.md \
  "$(cat .codex-impl/pkg-NN-prompt.md)" \
  < /dev/null > .codex-impl/pkg-NN-events.jsonl 2>&1
```

The `< /dev/null` is load-bearing: with an open stdin pipe, `codex exec` waits for
additional input — a classic source of "Codex hangs". Implementation runs are long
(minutes to tens of minutes); if the agent harness offers background execution, use it
and check the event log periodically, otherwise run in the foreground with a generous
timeout. Never block on an integration call with a short timeout.

**3. Capture the session id** from the first `thread.started` event and record it in
`state.md` immediately (guard against non-JSON banner lines in the log):

```bash
SESSION_ID=$(python3 -c "
import json
for line in open('.codex-impl/pkg-NN-events.jsonl'):
    line = line.strip()
    if not line.startswith('{'): continue
    e = json.loads(line)
    if e.get('type') == 'thread.started':
        print(e['thread_id']); break
")
```

Fallback if the event schema ever shifts: `codex exec resume --last` immediately after
the run targets the most recent recorded session.

**4. Follow up in the same thread.** Every within-package follow-up — a test failure, a
review finding, a missed edge case — goes through resume, so Codex keeps its full
working context and nothing is restated:

```bash
codex exec resume "$SESSION_ID" -m gpt-5.6-sol -s workspace-write --json \
  "<specific follow-up: the failing command and its output, or the concrete defect>" \
  < /dev/null >> .codex-impl/pkg-NN-events.jsonl 2>&1
```

Cap resume rounds at **3 per package** (track the count in `state.md`). If the package
still isn't done after 3 rounds, stop looping: fix trivial residue directly, or surface
the impasse to the user with the session id so they can take over the thread with
`codex resume <SESSION_ID>`.

## Phase 3 — Verify each package before starting the next

A package is not done because Codex says so. Before moving on:

1. **Review the diff** (`git diff`) for scope adherence — edits outside the package
   boundary get reverted or handed back to the owning thread.
2. **Run the checks that cover the package**: the build, the relevant tests, a quick
   import/smoke run. Failures go back to the *same* thread via resume, carrying the
   exact failing command and output.
3. Only then mark the package `done` in `state.md`, and start the next package on a
   **fresh thread** — a new context window, primed with a 2–3 sentence summary of what
   prior packages established.

After the first package completes, ask the user once (plain text) whether they want a
checkpoint commit per completed package; follow their answer for the rest of the run.

## Phase 4 — Integrate & report

When all packages are done, run the full build and test suite across the combined
change and fix integration fallout (route each fix to the package thread that owns the
code, or handle trivial glue directly). Then report:

- The package table from `state.md`: status, session id, files touched per package.
- Overall verification results (build/tests), stated plainly.
- Where the audit trail lives (`.codex-impl/`).
- The `codex resume <SESSION_ID>` command per package, so the user can continue any
  thread interactively in the Codex TUI — the local history is theirs.

---

## Failure handling

- **Auth errors** on the first call: have the user run `codex login`, then retry the
  same command — nothing is lost.
- **A thread stalls** (event log stops growing for an extended stretch): kill the
  process. The session survives the kill — that is the point of CLI-recorded history —
  so resume it with a narrower instruction ("continue from where you stopped; do only X
  next") rather than starting over.
- **A package proves too big mid-flight** (the thread thrashes, output truncates, work
  degrades): mark it `split` in `state.md`, subdivide it into smaller packages, and run
  those on fresh threads. Do not keep resuming a drowning thread.
- **Cross-package conflicts** (two packages touched the same code): resolve via git,
  then route the reconciliation to the thread that owns the surviving design.
- **`--json` event schema drift** across Codex versions: fall back to
  `codex exec resume --last` for session-id capture and note the version in `state.md`.
- **The user interrupts mid-run**: `state.md` plus the recorded sessions make the run
  resumable — on the next invocation, read `state.md`, skip `done` packages, and resume
  or restart the in-flight one.
