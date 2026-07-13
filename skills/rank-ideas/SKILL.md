---
name: rank-ideas
description: |
  Score, compare, and prioritize research ideas using an external survey.md and the
  ideas.md produced from it. Use when the user asks which research idea to pursue,
  wants ideas ranked or stress-tested, or needs a concrete first experiment. Read both
  files from a user-provided directory or the current working directory, evaluate each
  idea against the survey evidence and the user's resource constraints, validate the
  leading candidates when search is available, and write ranking.md beside them.
---

# Rank Ideas

Rank every proposal in `ideas.md` against the evidence in its source `survey.md` and
recommend one project to start.

Pipeline: **Load files → Confirm constraints → Score → Validate leaders → Write ranking**

## 1. Load survey.md and ideas.md

Use paths explicitly provided by the user; otherwise look for `survey.md` and `ideas.md`
in the current working directory. If either is missing, ask the user to provide it or
its path and stop. When the files are in different directories or several candidates
exist, ask the user to identify the matching pair.

Read both files completely. Verify that each idea is grounded in the survey. Flag any
idea whose cited gap, prior work, or evaluation claim cannot be found in `survey.md`;
unsupported claims reduce evidence strength and cannot be silently repaired from memory.

## 2. Confirm the decision context

Restate the constraint envelope from `ideas.md`. Ask one concise plain-text message only
when necessary to confirm missing or changed information:

- Available time, team, compute, equipment, data, and budget.
- Desired ambition and target outcome.
- Existing code, datasets, expertise, collaborators, or other unfair advantages.
- Hard exclusions or dependencies.

Stop and wait if the answers could materially change the ranking.

## 3. Score every idea

Assign integer scores from 1–5 on four axes:

- **Impact**: importance of the survey gap and value if resolved.
- **Feasibility**: likelihood of a meaningful result within the user's constraints.
- **Evidence**: strength and specificity of the survey evidence supporting the gap.
- **Novelty**: separation from the closest work documented in `survey.md` and
  `ideas.md`; score an unchecked idea conservatively.

Calculate the base score as `Impact × Feasibility`. Use Evidence and Novelty as gates:
an idea scoring below 3 on either cannot enter the top three until validated. Break ties
by Feasibility, then Evidence. Justify every score with a concise reference to the files
or the user's constraints. Use the whole scale and make real distinctions.

## 4. Validate the leading candidates

For enough high-scoring candidates to produce a defensible top three, perform these
checks:

1. **Grounding:** confirm that the gap and claimed contribution follow from the survey.
2. **Nearest work:** use current web or literature search when available to find recent
   collisions missed by the survey. Verify citations and include persistent identifiers
   or direct links. If search is unavailable, mark the check `Unchecked`.
3. **Why now:** name the development that makes the project newly feasible or valuable.
4. **Kill condition:** identify the most likely concrete failure and the cheapest
   experiment that tests it, including an estimated cost in time and resources.

Give each check a `Pass`, `Weakened`, `Fail`, or `Unchecked` verdict. Demote an idea that
fails grounding or collides with existing work, promote the next candidate, and validate
the replacement. Do not invent missing evidence.

## 5. Write ranking.md

Write `ranking.md` beside `survey.md` and `ideas.md`, following
`references/ranking_template.md`. Do not modify either input file.

Requirements:

- Score every idea and show the complete ordering.
- Explain every promotion or demotion from the base-score order.
- Give full validation sections for the final top three, or all ideas if fewer exist.
- Recommend exactly one idea and specify its first de-risking experiment, expected cost,
  kill result, and green-light result.
- Use a confident, professional tone grounded in evidence rather than hypothetical
  reviewer reactions.

Finish by reporting the output path, final top three, and any ideas rejected because of
weak survey grounding or literature collisions.

## Failure handling

- If either input file cannot be read, stop and identify the path problem.
- If `ideas.md` does not derive from the supplied survey, stop and ask for the matching
  pair rather than ranking incompatible artifacts.
- If search is unavailable, complete the ranking but mark nearest-work checks
  `Unchecked` and score Novelty conservatively.
- If every idea fails grounding or novelty validation, write the findings but make no
  project recommendation.
