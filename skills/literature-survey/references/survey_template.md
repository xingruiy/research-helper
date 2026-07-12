# survey.md template

Target: 800–1500 words of prose + tables. Taxonomy over chronology. Every paper-specific
claim cited as `[FirstAuthor et al., YEAR, arXiv:ID or DOI]` copied verbatim from raw results.

```markdown
# <Topic>: Landscape Survey
*Generated <date> · <N> papers reviewed · queries and raw results in ./raw/*

## 1. Problem framing
What the problem is, why it matters, and the precise scope of this survey
(including what's deliberately excluded, per the user's clarification answers).

## 2. Taxonomy of approaches
2–4 sentence intro, then one subsection per family:

### 2.x <Family name>
Core idea, representative papers (cited), strengths, known failure modes.
Note which family currently dominates and why.

## 3. Key papers
| Paper | Year | Venue | Contribution (one line) | Code |
|-------|------|-------|--------------------------|------|
(10–20 rows. "Venue" = arXiv if unpublished; Code = ✓/✗/unknown.)

## 4. Datasets, benchmarks & evaluation
What people evaluate on, dominant metrics, and any known problems with the
evaluation culture (protocol inconsistencies, saturated benchmarks, train/test leakage).
This section is disproportionately useful for gap-finding — be critical.

## 5. Trends & recent frontier (last ~12 months)
What changed recently; which older assumptions are being overturned.

## 6. Open problems & gaps
Numbered, concrete, and specific — each gap should be phrased so an idea card in
ideas.md can point at it. Good: "No method reports calibration of its confidence
outputs under domain shift; all evaluate in-domain only." Bad: "Robustness needs work."

## 7. Existing surveys & benchmarks of this space
If any exist (you searched for them in Phase 2), list them and state what they
cover — and therefore what a NEW survey/benchmark would need to add.
```
