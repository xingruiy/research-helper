# ranking.md template

Output path: `auto-research/deep-dive/<slug>/ranking.md`. Every idea scored; top 3
validity-checked in full. Every citation `[FirstAuthor et al., YEAR, arXiv:ID or DOI]`
copied verbatim from the ideas document, its raw files, or the fresh `rank_*.jsonl`
search results.

Tone: confident, professional, decisive — this document renders a verdict the user can
act on Monday morning. Scores carry rubric-anchored justifications, kill conditions are
concrete technical failure modes with a costed test, and the recommendation names one
idea and one first experiment. No hedging.

```markdown
# Idea Ranking: <Direction>
*Generated <date> · derived from `ideas.md` (brain-storm) and `review.md` (deep-dive) ·
<N> ideas scored; top <K> validity-checked ·
fresh search results in ./raw/rank_*.jsonl*

## Constraint envelope & unfair advantages
2–4 sentences: the envelope restated from ideas.md (with any corrections from the
user), followed by the unfair advantages — existing codebase, dataset, expertise,
equipment — or the statement that there are none. This is the lens plausibility uses.

## Scoreboard
| Rank | Idea (short title) | Impact | Plausibility | Score | Unfair advantage |
|------|--------------------|--------|--------------|-------|------------------|
Ranked by Score = Impact × Plausibility, ties broken by Plausibility. "Unfair
advantage" = the asset that lifted the score, or —.

One line per idea below the table: the rubric anchor each score matches and the
evidence behind it. If this order disagrees with brain-storm's internal ordering, note
where and why in one line.

## Validity check: <Title>  (rank 1)
**Nearest neighbors.** 1–3 papers, cited verbatim from search output. For each: what it
did, what this idea does that it does not, and why that delta is a contribution — full
sentences, no hand-waving. Verdict: pass / weakened / fail.

**Why now.** The recent development (named, dated) that makes this newly feasible or
newly interesting. If it could have been done five years ago, the identified blocker or
the finding that nobody cared — and what that implies. Verdict: pass / weakened / fail.

**Kill condition.** The single most likely way the idea dies, stated specifically. The
cheapest experiment that tests that failure mode first, its cost in days, and what
outcome kills vs. clears the idea. Verdict: pass / weakened / fail.

## Validity check: <Title>  (rank 2)
(same structure)

## Validity check: <Title>  (rank 3)
(same structure)

## Final ranking
| Rank | Idea | Score | Change from scoreboard | Reason |
|------|------|-------|------------------------|--------|
Every promotion or demotion carries its one-line reason (failed check, weakened delta,
cheap kill test moved it up). If an idea was demoted out of the top 3, its replacement
appears here with full validity checks above.

## Recommendation
The single idea to start, the de-risking experiment to run first (from its kill
condition), the expected cost in days, and the concrete result that green-lights the
full project.
```
