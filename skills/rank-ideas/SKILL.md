---
name: rank-ideas
description: |
  Score, rank, and stress-test the research ideas produced by the brain-storm skill so
  the user knows which one to actually start. Use this skill whenever the user asks to
  rank, prioritize, compare, or pick between research ideas — "which idea should I
  pursue", "rank these", "score the ideas", "what's most promising", "help me decide
  what to work on next" — even if they don't say "rank". Requires prior output from the
  brain-storm skill (`auto-research/deep-dive/<slug>/ideas.md`); if none exists, this
  skill aborts and directs the user through the pipeline (literature-survey → deep-dive
  → brain-storm → rank-ideas). Do NOT use for generating new ideas (brain-storm), for
  surveying literature (literature-survey), or for expanding a survey direction
  (deep-dive).
---

# Rank Ideas

Given an ideas document produced by the **brain-storm** skill, score every idea on two
axes, rank by the product, and subject the top 3 to validity checks rigorous enough to
bet months of work on. This is the fourth stage of the pipeline — the survey mapped the
field, the deep dive exhausted one thread, brain-storm proposed, and this skill decides.
Its value over gut feeling is calibration: brain-storm's internal ordering is a first
pass made while proposing; this stage re-scores with anchored rubrics, weighs the user's
unfair advantages, and verifies that the winners survive contact with the literature
and a named kill condition.

Pipeline: **Verify prerequisites → Confirm the envelope → Score & rank → Validity-check top 3 → Compose**

The deliverable is **`auto-research/deep-dive/<slug>/ranking.md`**, next to the ideas
document it judges. Fresh search results go in the same `raw/` directory with a
`rank_` prefix so the user can audit them.

## Portability rules (Claude / Codex / any agent)

This skill must work identically in any coding agent. Therefore:

- Use only **plain-text questions in the chat** to interact with the user — never
  agent-specific UI tools (option pickers, forms, plan modes).
- Use only **bash + `python3` (stdlib)** for tooling. This skill bundles no scripts of
  its own; it reuses the literature-survey skill's `scripts/lit_search.py` (zero
  dependencies). Resolve it as `<this skill's directory>/../literature-survey/scripts/lit_search.py`.
  If that path does not exist, tell the user the rank-ideas skill requires the
  literature-survey skill to be installed alongside it (both are installed by this
  repository's `install.sh`) and abort.
- If the agent has a built-in web search/browse capability, use it where the
  validity-check phase says so; if not, rely on the API script alone and note the
  reduced coverage in the output.

---

## Phase 0 — Verify prerequisites (hard abort if missing)

Look for ideas documents at `auto-research/deep-dive/*/ideas.md` in the current working
directory. If none exists, **abort immediately**: state plainly that no brain-storm
output was found, that this skill ranks only ideas that were generated from a deep-dive's
documented gaps and novelty-checked against the literature, and point the user to the
pipeline — run brain-storm if a `review.md` exists, deep-dive before that if only
`survey.md` exists, literature-survey if nothing does. Do not rank ideas the user pastes
into the chat or ideas from prior knowledge — an unranked idea with no gap anchor and no
novelty check cannot be scored honestly against ideas that have both. Stop.

If exactly one ideas document exists, use it. If several exist and the prompt doesn't
make the target obvious, list them (slug + direction title) and ask the user to pick —
one plain-text question, then wait.

Then read in full:

1. The chosen `ideas.md` — every idea, its constraint envelope, and its
   closest-prior-work fields.
2. The sibling `review.md` — the open questions the ideas anchor to; needed to judge
   impact honestly.
3. Skim the `raw/novelty_*.jsonl` files — they are the starting point for the nearest-
   neighbor checks in Phase 3.

## Phase 1 — Confirm the envelope and the unfair advantages

Plausibility is meaningless in the abstract — it is the probability of a real result
given *this user's* compute, timeframe, data access, and existing assets. The ideas
document already records a constraint envelope from brain-storm; restate it in 2–3
sentences so the user can correct drift.

Then establish the **unfair advantages**, which brain-storm did not ask about: an
existing codebase, a private or hard-to-get dataset, domain expertise, lab equipment,
or collaborator access that most groups attacking the same gap would lack. If the
envelope or the advantages are not already clear from the documents or the prompt, ask
as **one** plain-text message (2–3 questions max) and wait. An unfair advantage raises
plausibility and speed simultaneously, so it moves scores — do not skip this step.

If the user says "no particular advantages", record that and score accordingly.

## Phase 2 — Score every idea and rank by the product

Score **every** idea in the document — not just the promising-looking ones — on two
axes, integers 1–5, and rank by **Impact × Plausibility**.

**Impact — if it works, who actually cares?**

- **5** — changes how the subfield evaluates or builds things; others must respond to it.
- **4** — a result many groups outside the immediate niche would build on.
- **3** — a solid paper the immediate niche would cite and use.
- **2** — an incremental footnote; the delta matters mostly to its own authors.
- **1** — nobody outside the project would notice.

**Plausibility — probability of a real result under the Phase 1 envelope.**

- **5** — near-certain: assets in hand, the effect is known to exist, the remaining work
  is execution.
- **4** — likely: one uncertain step; everything else is within demonstrated capability.
- **3** — a coin flip: the core technical bet is unproven but testable with available
  resources.
- **2** — requires resources, data, or scale the user does not have, or a method with no
  working precedent.
- **1** — depends on something outside the user's control materializing.

Scoring discipline:

- **Use the whole scale.** A column of 3s and 4s is a refusal to decide, not caution.
  The rubric anchors exist so that scores are defensible; commit to them.
- **Unfair advantages move plausibility up.** An idea that is a 3 for the field but sits
  on the user's existing codebase or dataset is a 4 for the user — say so explicitly in
  the justification.
- **One sentence of justification per score**, citing the rubric anchor it matches and
  the evidence (from the review, the ideas document, or the envelope) behind it.
- Ties in the product are broken by plausibility — a likelier result beats a grander
  maybe.

The ranking may disagree with brain-storm's internal ordering; when it does, that is the
point of this stage, not an error. Note the disagreement in one line.

## Phase 3 — Validity-check the top 3

The top 3 by product get checks the scores alone cannot provide. Run all three checks
per idea; each produces a written verdict in the output.

**1. Nearest neighbors and the delta.** Find the 1–3 closest existing papers. Start
from the idea's closest-prior-work field and the brain-storm `novelty_*.jsonl` results,
then run fresh searches — the collision risk is highest in the months since brain-storm
ran, so also use web search here if available (recent preprints are the likeliest
neighbors):

```bash
LITSEARCH=<this skill's directory>/../literature-survey/scripts/lit_search.py
python3 "$LITSEARCH" search "core terms of the idea" --sources arxiv,s2,openalex --limit 20 --out auto-research/deep-dive/<slug>/raw/rank_idea1.jsonl
```

Name the neighbors with identifiers copied verbatim from search output, and articulate
the delta in **full, specific sentences**: what the neighbor did, what this idea does
that it did not, and why that difference is a contribution. Two hard rules: if you
cannot name the nearest neighbors, you do not yet know whether the idea is novel — say
so and score the check as failed rather than bluffing; and if the delta reduces to one
sentence of hand-waving ("ours is more general"), the idea is weaker than it feels —
demote it.

**2. "Why now?"** Good ideas have an answer to what recent development makes them newly
feasible or newly interesting — a new model class, a new dataset, new hardware, a new
theoretical result, a shift in what the community measures. Write that answer down with
the enabling development named and dated. If the idea could have been done five years
ago and wasn't, either there is a hidden blocker or nobody cares — investigate briefly
(the review and the neighbor search usually reveal which) and state the finding either
way. "No answer to why-now" is a legitimate verdict and a mark against the idea.

**3. Name the kill condition.** Write down the **single most likely way the idea dies**:
the dataset doesn't exist, the effect size is too small to measure, the baseline is
already near-ceiling, the labeling cost is prohibitive. Vague risks ("might not work")
are not kill conditions; a kill condition is specific enough to test. Then design the
**cheapest experiment that tests that failure mode first** and estimate its cost in
days. This estimate feeds back into the ranking: an idea whose biggest risk can be
de-risked in a day of experiments ranks above an idea where the answer only arrives
after three months — cheap falsifiability is worth more than a slightly higher product
score, because it converts a maybe into a decision quickly.

**Verdict and re-ranking.** Each check ends in a verdict: *pass*, *weakened* (survives
but with a named deficiency), or *fail*. An idea that fails a check is demoted out of
the top 3; when that happens, promote the next idea by product score and run the full
validity checks on it too, so the final top 3 are all validated. Adjust the final
order for kill-test cost as described above, and record every adjustment with its
reason — the user must be able to see why the final order differs from the raw
product ranking.

## Phase 4 — Compose the ranking document

Write `auto-research/deep-dive/<slug>/ranking.md` following
`references/ranking_template.md` (in this skill's directory). Non-negotiables:

- **Tone: confident and professional.** The document renders decisions, not
  possibilities. Scores are stated with their rubric justification, verdicts are
  stated plainly, and the recommendation names one idea to start and the first
  experiment to run. No hedging, no imagined reviewer objections — kill conditions are
  engineering, not anxiety.
- **The scoreboard covers every idea**, with both scores, the product, the unfair-
  advantage flag, and a one-line justification each.
- **The top 3 get full validity-check sections** with neighbors cited verbatim from
  search output, the why-now answer, the kill condition, and the cost of the de-risking
  experiment. Never cite from memory.
- **The final ranking is explicit about its deltas** from the raw product order —
  every promotion or demotion carries its one-line reason.
- End with a **recommendation**: the single idea to start, the de-risking experiment to
  run first, and what result would green-light the full project.

Finish by telling the user the output path, the final top 3, any idea that was demoted
by a validity check and why, and where the fresh search results live.

---

## Failure handling

- Semantic Scholar rate-limits aggressively (HTTP 429): the script auto-retries with
  backoff; if it keeps failing, drop `s2` from `--sources` and rely on arXiv + OpenAlex.
- If all APIs and web search are unavailable, still deliver the scored ranking (scoring
  needs no network) but mark every validity check's nearest-neighbor section
  `[neighbors unchecked]` and state prominently that the top-3 checks could not run —
  never imply an idea was verified when it wasn't.
- If the ideas document has fewer than 3 ideas, validity-check all of them.
- If a validity check reveals a full collision (the idea is now published), treat it as
  a *fail*, cite the paper, and say plainly that the idea is dead — a documented death
  is valuable output, not a failure of this skill.
- If the ideas document lacks a constraint envelope (degraded brain-storm run), ask the
  user for the envelope in Phase 1 rather than scoring plausibility in a vacuum.
