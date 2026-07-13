# ranking.md template

Write beside the matching `survey.md` and `ideas.md`.

```markdown
# Idea Ranking: <Survey Topic>
*Generated <date> from `survey.md` and `ideas.md` · <N> ideas scored ·
<K> fully validated*

## Decision context
Summarize the user's constraints, goals, and unfair advantages.

## Scoreboard
| Base rank | Idea | Impact | Feasibility | Base score | Evidence | Novelty | Gate |
|-----------|------|--------|-------------|------------|----------|---------|------|

Add one concise justification per idea. Base score is Impact × Feasibility; Evidence
and Novelty below 3 block entry into the top three until validated.

## Validation: <Idea title>

**Grounding.** Confirm the survey gap and contribution. Verdict: Pass / Weakened / Fail.

**Nearest work.** Name the closest work, explain the exact delta, and mark sources not
already in the survey as `[additional source]`. Verdict: Pass / Weakened / Fail /
Unchecked.

**Why now.** Name and date the enabling development. Verdict: Pass / Weakened / Fail.

**Kill condition.** State the likely failure, cheapest test, estimated time and resource
cost, kill result, and green-light result. Verdict: Pass / Weakened / Fail.

Repeat for every candidate needed to establish the final top three.

## Final ranking
| Final rank | Idea | Change from base rank | Reason |
|------------|------|-----------------------|--------|

## Recommendation
Name exactly one idea to start. Specify the first de-risking experiment, expected cost,
the result that kills the project, and the result that green-lights full work.

## Rejected ideas
List ideas rejected for weak grounding or a literature collision. Omit when empty.
```
