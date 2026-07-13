---
name: brain-storm
description: |
  Turn an external literature survey named survey.md into a focused set of concrete,
  evidence-grounded research ideas. Use when the user wants project ideas, thesis
  directions, experiments, or ways to address gaps documented in an existing survey.
  Read survey.md from the path the user provides or from the current working directory,
  clarify the user's constraints, check candidate novelty when search is available, and
  write ideas.md beside the survey. Do not run a new literature survey or invent ideas
  without grounding them in the supplied document.
---

# Brain Storm

Generate at most 10 actionable research ideas from an external `survey.md`.

Pipeline: **Load survey → Clarify constraints → Generate → Check novelty → Write ideas**

## 1. Load the survey

Use a survey path explicitly named by the user; otherwise look for `survey.md` in the
current working directory. If it is missing, ask the user to provide the file or its
path and stop. If several plausible files exist, ask which one to use.

Read the entire survey. Extract its scope, taxonomy, established results, citations,
datasets, evaluation practices, disagreements, limitations, and open questions. Treat
the survey as the grounding source: do not replace missing evidence with prior knowledge.

Assess whether it contains enough detail to support ideation. If it lacks identifiable
gaps or supporting literature, explain what is missing and ask for a more detailed
survey. Do not generate generic ideas from the topic alone.

## 2. Clarify the constraint envelope

Reuse constraints already stated by the user or recorded in the survey. Ask one concise
plain-text message with only the missing questions, usually 2–4:

- What outcome and ambition level they want: learning project, thesis, publishable
  incremental work, or high-risk research.
- Their timeframe, team size, compute, equipment, data access, and monetary budget.
- Their existing code, expertise, preliminary results, or other assets.
- Any methods, applications, or target venues to prefer or exclude.

Stop and wait for the answer. If the user explicitly has no constraints, accept that
and label resource requirements for each idea.

## 3. Generate candidates

Work through the survey's documented gaps and contradictions. For each candidate, name
the evidence that motivates it and define a result that would resolve or narrow the gap.
Strong candidates usually do one of the following:

- Measure an unevaluated condition with explicit baselines and metrics.
- Resolve conflicting findings through a controlled comparison.
- Remove a shared assumption whose limitation the survey documents.
- Transfer a method between disconnected approach families.
- Build a missing dataset, benchmark, or evaluation protocol.
- Extend a method where the survey identifies a precise capability boundary.

Generate more candidates than needed, then retain at most 10 based on expected impact,
feasibility under the user's constraints, and strength of grounding. Do not pad the list.

## 4. Check novelty

Do not run another broad survey. For each surviving candidate, use current web or
literature search if the host agent provides it to look specifically for work that may
already implement the proposed contribution. Search using the candidate's core method,
setting, and claimed delta.

Classify each candidate as:

- **Clear**: no close implementation found.
- **Near miss**: related work exists, but the proposed delta remains specific.
- **Sharpened**: the initial idea collided and was narrowed to an unresolved delta.
- **Collision**: the contribution already exists; remove the candidate.
- **Unchecked**: search was unavailable; retain only with this label.

Verify every newly introduced citation and include a persistent identifier or direct
source link. Never claim novelty solely from the survey or from memory.

## 5. Write ideas.md

Write `ideas.md` in the same directory as `survey.md`, following
`references/ideas_template.md`. Preserve the survey; never modify it.

Requirements:

- Use a confident, professional tone without imagined reviewer criticism.
- Rank the retained ideas by impact and feasibility for this user.
- Trace every idea to a named survey gap, limitation, or disagreement and cite the
  survey's supporting sources.
- Specify the claim, approach, validation data, baselines, metrics, success condition,
  resource needs, and cheapest early failure test.
- Distinguish citations already present in the survey from sources added by the novelty
  check.
- Deliver at most 10 ideas, using 150–300 words per idea plus a summary table.

Finish by reporting the output path, candidate and retained counts, collisions found,
and how many ideas remain novelty-unchecked.

## Failure handling

- If the survey cannot be read, stop and identify the path problem.
- If the survey supports fewer than three strong ideas, deliver only those it supports.
- If search is unavailable, mark every novelty result `Unchecked`; do not imply that
  novelty was verified.
- If novelty checks eliminate every candidate, report the collisions and explain that
  the supplied survey currently supports no defensible new idea.
