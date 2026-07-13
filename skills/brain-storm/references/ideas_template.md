# ideas.md template

Output path: `auto-research/deep-dive/<slug>/ideas.md`. At most 10 ideas, ranked,
150–300 words each plus the summary table. Every citation
`[FirstAuthor et al., YEAR, arXiv:ID or DOI]` copied verbatim from the review, its raw
files, or the novelty-check results.

Tone: confident, professional proposals — each idea is a plan someone could start
executing, not a musing. State risks as concrete technical failure modes with early
detection signals, never as hedging or imagined reviewer pushback.

```markdown
# Research Ideas: <Direction>
*Generated <date> · derived from `review.md` (deep-dive) and `../../survey.md` ·
<N> ideas from <M> candidates; <K> killed or sharpened by novelty check ·
novelty-check results in ./raw/novelty_*.jsonl*

## Constraint envelope
2–4 sentences: the user's resources, ambition level, and prior position from Phase 1
(or the statement that they chose no constraints). This is the lens the ranking uses.

## Summary
| # | Idea (short title) | Gap addressed | Resources | Risk | Novelty check |
|---|--------------------|---------------|-----------|------|---------------|
"Gap addressed" = review open-question number(s). "Resources" = low/medium/high against
the envelope. "Risk" = low/medium/high. "Novelty check" = clear / near miss / sharpened.

## Idea 1: <Title>
**Gap.** Which open question(s) of the review this closes and the evidence behind the
gap, citations included.

**Claim.** The single sentence the resulting paper would defend.

**Approach.** The method sketch: what gets built or measured, and the key technical
move that makes it work.

**Validation.** Data/benchmark, baselines, metrics, and the concrete result that counts
as success ("beats X on Y by more than its reported variance", not "shows improvement").

**Closest prior work.** The nearest papers from the novelty check and the one-sentence
delta between them and this idea. If the idea was sharpened after a collision, say what
was already done and what remains.

**Risks & resources.** Main technical failure mode, the cheapest early experiment that
detects it, and the resource demand against the envelope.

## Idea 2: ...
(same structure)

## Killed in novelty check
One line per killed candidate: the idea, and the paper that already did it (cited).
Omit the section if nothing was killed.
```
