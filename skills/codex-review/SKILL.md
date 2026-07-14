---
name: codex-review
description: |
  Send the current session plan to Codex for an external review, reflect on the
  feedback, and revise the plan where the feedback is accepted. Use when the user
  asks to codex-review a plan, wants a second opinion on the current plan, or wants
  the plan stress-tested before implementation. A session plan must already exist
  on disk; abort immediately if it does not. Run one review round per invocation
  and decide autonomously which feedback points to apply, reporting every decision
  with its reasoning.
---

# Codex Review

Use Codex as an external reviewer of the current session plan, then incorporate the
feedback that survives scrutiny.

Pipeline: **Locate plan → Send to Codex → Reflect on feedback → Revise plan → Report**

## 1. Locate the session plan

The plan under review is, in order of precedence:

1. A plan file path explicitly provided by the user.
2. The plan file created in the current session (for Claude Code plan mode, the
   session plan file under `~/.claude/plans/`).
3. A plan document written to disk earlier in this session.

Read the plan file completely before doing anything else.

If no session plan exists on disk, abort with one sentence explaining that a plan
must be created first (for example via plan mode), and take no further action. Do
not reconstruct a plan from conversation memory and do not review an unwritten plan.

## 2. Send the plan to Codex

Confirm the CLI is available with `command -v codex`; if it is missing, abort and
tell the user to install Codex or add it to `PATH`.

Copy the plan to a temporary file inside the current working directory so Codex can
read it regardless of where the original lives. `codex exec` refuses to run outside
a trusted directory: invoke it from the project's git repository, or append
`--skip-git-repo-check` when the working directory is not one. Redirect stdin from
`/dev/null` — when stdin is not a terminal, `codex exec` waits to read it and the
command hangs. Then request a read-only, non-interactive review:

```bash
codex exec --sandbox read-only "Review the implementation plan in <temp-file>.
You are an external reviewer; critique the plan but do not rewrite it or modify
any files. Return a numbered list of concrete findings. For each finding give a
severity (high/medium/low) and cover, where applicable: correctness risks, missing
steps or files, wrong assumptions about the codebase, simpler alternatives, and
gaps in the verification strategy. Reference specific plan sections or repository
files in every finding. If the plan is sound, say so explicitly instead of
inventing objections." < /dev/null
```

Capture the complete output and delete the temporary file afterward.

## 3. Reflect on each feedback point

Evaluate every numbered finding independently. Verify each claim against the actual
plan and repository — read the referenced files rather than taking the finding on
faith. Then mark the finding:

- **Accepted** — the finding is correct and in scope; state in one sentence what
  will change in the plan.
- **Rejected** — the finding is factually wrong, already handled by the plan, or
  out of scope; state in one sentence the evidence that disqualifies it.

Every verdict requires reasoning tied to the plan text or repository contents.
Acceptance is decided here, autonomously; do not pause to ask the user which
findings to apply.

## 4. Revise the plan

If at least one finding is accepted, edit the session plan file in place to
incorporate all accepted findings. Preserve the plan's existing structure and leave
unrelated sections untouched. If every finding is rejected, leave the plan exactly
as it was.

All edits are made by the hosting agent. Codex runs read-only and never modifies
the plan or any other file.

## 5. Report

Finish with a summary containing:

- The plan file reviewed and the total number of findings returned.
- A table of findings with severity, verdict (Accepted/Rejected), and the
  one-sentence reasoning for each.
- What changed in the plan, or a statement that the plan stands unchanged.

This skill runs a single review round. For another round, revise further and invoke
the skill again.

## Failure handling

- No session plan on disk: abort at step 1 with the one-sentence explanation.
- `codex` CLI unavailable or the `codex exec` command errors: abort and report the
  error output verbatim.
- Codex returns empty or unusable feedback: report that the review produced no
  actionable findings and leave the plan unchanged.
- Codex output includes an attempted rewrite of the plan: extract only the
  critique; never paste a Codex-authored plan over the session plan.
