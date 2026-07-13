---
name: brain-storm
description: |
  Turn a deep-dive review into at most 10 concrete, novelty-checked research ideas that
  address the open problems the review identified. Use this skill whenever the user asks
  for research ideas, project proposals, "what should I work on", "how could we close
  gap 4", "brainstorm from the review", or wants the open problems turned into an
  actionable research agenda — even if they don't say "brainstorm". Requires prior
  output from the deep-dive skill (`auto-research/deep-dive/<slug>/review.md`); if none
  exists, this skill aborts and directs the user through the pipeline
  (literature-survey → deep-dive → brain-storm). Do NOT use for surveying literature
  (literature-survey), for expanding a survey direction (deep-dive), or for writing up
  an idea the user already has.
---

# Brain Storm

Given a deep-dive review produced by the **deep-dive** skill, generate **at most 10**
research ideas that fill the gaps and attack the open problems the review documented.
This is the third stage of the pipeline — the survey mapped the field, the deep dive
exhausted one thread, and this skill is the only stage allowed to propose. Its value
over free-form ideation is discipline: every idea is anchored to a documented gap,
checked against the literature for novelty, and specified down to the experiment that
would validate it.

Pipeline: **Verify prerequisites → Ground & constrain → Generate candidates → Novelty-check → Compose**

The deliverable is **`auto-research/deep-dive/<slug>/ideas.md`**, next to the review it
derives from. Novelty-check search results go in the same `raw/` directory with a
`novelty_` prefix so the user can audit them.

## Portability rules (Claude / Codex / any agent)

This skill must work identically in any coding agent. Therefore:

- Use only **plain-text questions in the chat** to interact with the user — never
  agent-specific UI tools (option pickers, forms, plan modes).
- Use only **bash + `python3` (stdlib)** for tooling. This skill bundles no scripts of
  its own; it reuses the literature-survey skill's `scripts/lit_search.py` (zero
  dependencies). Resolve it as `<this skill's directory>/../literature-survey/scripts/lit_search.py`.
  If that path does not exist, tell the user the brain-storm skill requires the
  literature-survey skill to be installed alongside it (both are installed by this
  repository's `install.sh`) and abort.
- If the agent has a built-in web search/browse capability, use it where the
  novelty-check phase says so; if not, rely on the API script alone and note the
  reduced novelty-check coverage in the output.

---

## Phase 0 — Verify prerequisites (hard abort if missing)

Look for deep-dive reviews at `auto-research/deep-dive/*/review.md` in the current
working directory. If none exists, **abort immediately**: state plainly that no
deep-dive review was found, that this skill generates ideas only from a deep-dive's
grounded account of open problems, and point the user to the pipeline — run
literature-survey first if `auto-research/survey.md` is also missing, or deep-dive if
the survey exists but no direction has been expanded. Do not brainstorm from the survey
alone, from the user's prompt, or from prior knowledge. Stop.

If exactly one review exists, use it. If several exist and the prompt doesn't make the
target obvious, list them (slug + first heading) and ask the user to pick — one
plain-text question, then wait.

Then read in full:

1. The chosen `review.md` — its "Open questions within this direction" section is the
   raw material; its bibliography and head-to-head evidence sections are the grounding.
2. The parent `auto-research/survey.md` — for cross-thread context the ideas may draw on.
3. Skim the review's `raw/` files as needed to recover details on specific papers.

## Phase 1 — Ground & constrain

Ideas that ignore the user's situation are trivia. Before generating, establish the
constraint envelope. If the user's prompt already answers these, restate your reading in
2–3 sentences and proceed; otherwise ask the missing ones as **one** plain-text message
(2–3 questions max) and wait:

1. **Resources**: what can the user actually run — hardware/equipment, compute, data
   access, collaborators? (An idea requiring a 20-camera rig is dead on arrival for a
   single-camera lab.)
2. **Ambition**: incremental publishable results, or high-risk/high-reward bets? A
   target venue or thesis context, if any.
3. **Position**: anything the user has already built or tried that ideas should build on.

Unlike the survey's scoping questions, "no constraints, go broad" is an acceptable
answer here — record it and generate across the full feasibility range, labeling each
idea's resource demands so the user can filter later.

## Phase 2 — Generate candidates

Work gap-by-gap through the review's open questions. For each, generate candidate ideas
by asking: what experiment, method, dataset, or analysis would *resolve* this open
question — not restate it? Strong moves, in rough order of reliability:

- **Close a measurement gap**: the review says no paper reports X under condition Y —
  design the study that measures it, with the baselines and metrics named.
- **Transfer across threads**: combine techniques the review shows belong to disjoint
  communities working on the same problem (the survey's cross-thread context helps here).
- **Break a shared assumption**: every method in the thread assumes Z; specify the
  system that drops Z and the case where dropping it matters.
- **Build the missing benchmark/dataset**: if the review found non-comparable
  evaluations, the benchmark itself is a research contribution — specify what it must
  contain to discriminate between existing methods.
- **Resolve a documented contradiction**: two papers report conflicting results; design
  the controlled comparison that explains the discrepancy.

Generate liberally at this stage (15–25 sketches is normal), then cull to the strongest
before novelty-checking. **At most 10 ideas survive to the final document** — fewer is
better than padded: if the review's gaps honestly support only 5 strong ideas, deliver 5.
Every idea must trace to a specific open question or documented gap in the review; an
idea you cannot anchor to the review's evidence does not belong in this document, no
matter how good it sounds.

## Phase 3 — Novelty-check every surviving idea

Your training knowledge of what "hasn't been done" is stale — the whole failure mode of
LLM brainstorming is proposing last year's papers. Check each surviving candidate
against the literature before it earns a place:

```bash
LITSEARCH=<this skill's directory>/../literature-survey/scripts/lit_search.py
python3 "$LITSEARCH" search "core terms of the idea" --sources arxiv,s2,openalex --limit 20 --out auto-research/deep-dive/<slug>/raw/novelty_idea1.jsonl
```

Run 1–2 targeted queries per idea (phrase them as the paper that would exist if the
idea were already done). Also use web search here if available — very recent preprints
are the likeliest collisions. Then triage:

- **Clear**: nothing close found — the idea stands, and the search is its evidence.
- **Collision**: the idea is substantially published — kill it, or sharpen it to the
  genuine remaining delta and cite the colliding paper explicitly in the idea's
  closest-prior-work field.
- **Near miss**: adjacent work exists — keep the idea, cite the neighbors, and state
  the delta in one sentence.

Never present an idea whose novelty check was skipped without labeling it
`[novelty unchecked]` and saying why (e.g. APIs unreachable).

## Phase 4 — Compose the ideas document

Write `auto-research/deep-dive/<slug>/ideas.md` following
`references/ideas_template.md` (in this skill's directory). Non-negotiables:

- **Tone: confident and professional.** Propose each idea as a defensible plan, not a
  timid suggestion. No self-doubt, no imagined reviewer objections. The risks field
  states concrete technical failure modes and how to detect them early — it is
  engineering, not anxiety.
- **Ranked order.** Present ideas ranked by expected value under the user's constraint
  envelope (impact × feasibility), with a summary table up front. State the ranking
  rationale in one line per idea; do not agonize over it.
- **Every idea is experimentally specified**: the claim it would establish, the method
  sketch, the validation plan (data, baselines, metrics, and what result counts as
  success), and its resource demands against the Phase 1 envelope.
- **Every idea is cited**: the gap it addresses (pointing at the review's open-question
  number with its supporting citations) and its closest prior work from the novelty
  check, identifiers copied verbatim from search output. Never cite from memory.
- At most 10 ideas. 150–300 words each plus the summary table.

Finish by telling the user the output path, how many ideas were delivered out of how
many candidates generated, how many were killed or sharpened by the novelty check, and
where the novelty-check raw results live. Suggest the **rank-ideas** skill as the next
pipeline stage to score the ideas and stress-test the top candidates.

---

## Failure handling

- Semantic Scholar rate-limits aggressively (HTTP 429): the script auto-retries with
  backoff; if it keeps failing, drop `s2` from `--sources` and rely on arXiv + OpenAlex.
- If all APIs and web search are unavailable, still deliver the ideas but mark every
  one `[novelty unchecked]` and state prominently that the novelty check could not run —
  never imply an idea was verified novel when it wasn't.
- If the review's open-questions section is thin or vague (deep-dive output from a
  degraded run), say so, generate only the ideas the evidence supports, and recommend
  re-running deep-dive on the direction before committing to a project.
- If the novelty check kills so many candidates that fewer than 3 survive, deliver the
  survivors and report the collisions explicitly — a list of "already done, here's the
  paper" findings is itself valuable output, not a failure.
