# ideas.md template

Write beside the source `survey.md`. Every idea must trace to evidence in that survey.

```markdown
# Research Ideas: <Survey Topic>
*Generated <date> from `survey.md` · <N> retained from <M> candidates ·
<K> collisions removed · <U> novelty-unchecked*

## Constraint envelope
Summarize the user's goal, timeframe, resources, existing assets, and exclusions.

## Summary
| Rank | Idea | Survey gap | Impact | Feasibility | Novelty status |
|------|------|------------|--------|-------------|----------------|

## 1. <Idea title>

**Survey grounding.** Name the documented gap, limitation, or disagreement and cite
the survey sources that establish it.

**Claim.** State the single claim a successful project would establish.

**Approach.** Describe the method, experiment, dataset, or analysis.

**Validation.** Name the data, baselines, metrics, and concrete success condition.

**Closest work and novelty.** Give the novelty status, nearest work, and exact delta.
Mark sources introduced by the novelty check as `[additional source]`. Use `Unchecked`
when no current search was possible.

**Resources and early failure test.** State the required resources, main technical
failure mode, and cheapest experiment that detects it.

## 2. <Idea title>
Repeat the same structure.

## Removed collisions
List rejected candidates and the work that already implements them. Omit when empty.
```
