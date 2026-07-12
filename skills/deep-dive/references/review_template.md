# review.md template

Output path: `auto-research/deep-dive/<slug>/review.md`. Target: 2000–4000 words of
prose + tables. Every paper-specific claim cited as
`[FirstAuthor et al., YEAR, arXiv:ID or DOI]` copied verbatim from raw results.

Tone: write like a research paper — assertive, declarative sentences. No hedging
("arguably", "it may be the case"), no anticipating hypothetical objections, no
restating the scope beyond Section 1. Disagreement appears only where the literature
itself disagrees, stated directly.

```markdown
# <Direction>: Deep-Dive Review
*Generated <date> · extends `auto-research/survey.md` · <N> papers reviewed
(<M> candidates retrieved, saturation <reached/not reached>) · raw results in ./raw/*

## 1. Scope
The scope contract from Phase 1: what this direction is, its boundaries (which
neighboring threads are deliberately excluded), and its relation to the parent
survey (which taxonomy family / open problem it expands).

## 2. Origin and development of the thread
The intellectual history: the problem or observation that opened the thread, the
papers that redirected it, and the state it has arrived at. Chronological narrative
is appropriate here — this is the one place it beats taxonomy. 2–4 paragraphs.

## 3. Technical account
The body of the review, organized by sub-approach within the thread:

### 3.x <Sub-approach>
Per important paper: what the method actually does (mechanism, not just label),
what it was evaluated on, what it reported, and what it acknowledged it cannot do.
Group minor/application papers into summarizing sentences with citation lists
rather than individual treatment.

## 4. Head-to-head evidence
| Method | Paper | Benchmark/setup | Metric | Reported result |
|--------|-------|-----------------|--------|-----------------|
One table per shared benchmark/dataset where 2+ papers report comparable numbers.
If no two papers in the thread evaluate on the same data, replace the table with a
paragraph stating that directly — non-comparability is a finding. Copy numbers
verbatim from abstracts/papers; never reconstruct them from memory.

## 5. Datasets, benchmarks & evaluation practice in this thread
What this specific thread evaluates on, its dominant metrics, and problems with
its evaluation culture. Be critical and specific.

## 6. Complete bibliography
| Paper | Year | Venue | One-line contribution | Role | Code |
|-------|------|-------|------------------------|------|------|
Every relevant paper found — this is the comprehensiveness deliverable, typically
40–100 rows for an active thread. "Role" = core / extension / application / adjacent.
"Venue" = arXiv if unpublished; Code = ✓/✗/unknown.

## 7. Open questions within this direction
The parent survey's gap, refined by full coverage of the thread. Numbered. Each entry:
- is grounded in the reviewed papers (an acknowledged limitation, an unevaluated
  condition, or a conflict between reported results), with supporting citations;
- names the specific missing condition, setting, baseline, or measurement.
State these as findings about the thread — do not turn them into research proposals
or suggestions for the user.

## 8. Relation to existing surveys and reviews
If any survey/review covers this thread (you searched for them in Phase 2), state
what it covers and what this document adds beyond it.
```
