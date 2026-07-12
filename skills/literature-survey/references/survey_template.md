# survey.md template

Output path: `auto-research/survey.md`. Target: 800–1500 words of prose + tables.
Taxonomy over chronology. Every paper-specific claim cited as
`[FirstAuthor et al., YEAR, arXiv:ID or DOI]` copied verbatim from raw results.

Tone: write like a research paper — assertive, declarative sentences. No hedging
("arguably", "it may be the case"), no anticipating hypothetical objections, no
restating the scope beyond Section 1. Disagreement appears only where the literature
itself disagrees, stated directly.

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
Be critical.

## 5. Trends & recent frontier (last ~12 months)
What changed recently; which older assumptions are being overturned.

## 6. Open problems & gaps
The payload of the survey: an accurate, complete account of the field's open questions,
written so the reader can design experiments directly from it. Numbered. Each entry:
- is grounded in the searched papers (an acknowledged limitation, an unevaluated
  condition, or a conflict between reported results), with supporting citations;
- names the specific missing condition, setting, baseline, or measurement.
Good: "No method reports calibration of its confidence outputs under domain shift;
all evaluate in-domain only [cites]." Bad: "Robustness needs work." State these as
findings about the field — do not turn them into research proposals or suggestions
for the user.

## 7. Existing surveys & benchmarks of this space
If any exist (you searched for them in Phase 2), list them and state what they
cover — and therefore what this survey adds beyond them.
```
