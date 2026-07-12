---
name: literature-survey
description: |
  Turn a rough research topic or direction into a grounded mini-survey and a ranked list of
  research ideas. Use this skill whenever the user describes a research area, asks "what's out
  there on X", wants a literature landscape / related-work scan, asks for research ideas or
  paper topics, wants to find gaps in a field, or asks to evaluate whether a direction is
  promising. Trigger even if they don't say "survey" — phrases like "I'm thinking about working
  on...", "map out the field of...", "brainstorm ideas for...", or "is X a good research
  direction?" all qualify. Do NOT use for implementing code from a known paper or for a single
  paper summary.
---

# Literature Survey

Given a rough description of a research topic/direction, run this pipeline:

**Clarify → Search → Survey → Brainstorm → Rank**

Produce two deliverables in the working directory (create `./literature-survey-out/<topic-slug>/` if the user doesn't specify a location):

1. `survey.md` — a short landscape survey (~800–1500 words + tables)
2. `ideas.md` — 10 research ideas, ranked by impact × plausibility

Keep raw search results in `raw/` inside the same folder so the user can audit sources.

---

## Phase 1 — Clarify (ask, then wait)

Ask **3–5 questions maximum**, in a single message, then STOP and wait for answers. Do not start searching before the user replies. Pick the questions that are actually ambiguous from this menu:

1. **Scope**: Which sub-area / setting matters most? (offer 2–4 concrete interpretations of their topic)
2. **Goal**: Paper for a specific venue (CVPR/ICRA/3DV/...), thesis direction, product/engineering decision, or general curiosity? This changes how ideas are ranked.
3. **Constraints**: Compute budget (single GPU? cluster?), timeframe, data access, solo vs. team.
4. **Prior position**: What have they already read/tried/built? What's their unfair advantage (existing codebase, dataset, domain expertise)?
5. **Novelty appetite**: Incremental-but-safe vs. risky-but-high-upside ideas?

For each question, offer your recommended default so a lazy "use your defaults" reply is enough. If the user's initial message already answers everything, skip straight to Phase 2 and say so.

## Phase 2 — Search (APIs first, web search second)

**Do not rely on your training knowledge of the literature — it is stale and you will hallucinate citations.** Every paper named in the survey must come from a search result.

Use the bundled script (stdlib-only Python, no installs needed):

```bash
python3 scripts/lit_search.py search "your query" --sources arxiv,s2,openalex --limit 25 --out raw/q1.jsonl
python3 scripts/lit_search.py citations <S2_PAPER_ID or arXiv:2403.xxxxx> --direction both --limit 30 --out raw/cites_key1.jsonl
python3 scripts/lit_search.py merge raw/*.jsonl --out raw/merged.md
```

See `references/api_cheatsheet.md` for the underlying APIs, query syntax, and rate-limit rules (read it if the script fails or you need a query type it doesn't cover). Google Scholar has no API — OpenAlex is the stand-in for coverage beyond arXiv.

Search strategy (aim for 4–8 keyword searches + 2–4 citation expansions, ~60–120 candidate papers before filtering):

1. **Seed queries**: 3–5 phrasings of the topic, including synonyms and adjacent terminology (e.g. "feedforward 3D reconstruction" AND "pointmap regression" AND "multi-view stereo transformer").
2. **Snowball**: identify the 2–4 most central papers from seed results; pull their references (backward) and citations (forward) via the `citations` command. Forward citations sorted by recency reveal the frontier.
3. **Recency pass**: one query restricted to the last ~12 months to catch what surveys miss.
4. **Web search pass**: use the normal web search tool for things APIs miss — workshop pages, benchmark leaderboards, well-known blog posts, GitHub repos. Also fetch abstracts of the ~10 most central papers if snippets are insufficient.
5. **Existing surveys**: explicitly query `"survey" OR "benchmark" <topic>` — if a recent survey exists, say so prominently; it changes the value of writing another one and is the fastest map of the taxonomy.

Deduplicate, then select ~20–35 papers that actually matter. Prefer: highly cited anchors, recent frontier work, and papers that define datasets/benchmarks/metrics.

## Phase 3 — Compose the survey

Write `survey.md` following `references/survey_template.md`. Non-negotiables:

- **Taxonomy over chronology**: organize by approach/axis, not by year.
- Every claim about a specific paper carries an inline citation like `[Wang et al., 2024, arXiv:2403.xxxxx]` with the identifier taken verbatim from search output. Never cite from memory.
- Include a **key-papers table** (paper, year, venue if known, one-line contribution, code available?).
- Include **Datasets & evaluation** and **Open problems / gaps** sections — the gaps section is the raw material for Phase 4, so make it concrete ("nobody evaluates X under Y" beats "more work is needed").
- Flag disagreements or unresolved questions in the literature explicitly.
- 800–1500 words of prose plus tables. This is a internal report, not a journal survey.

## Phase 4 — Brainstorm 10 ideas

Generate exactly 10 ideas in `ideas.md`. Force diversity — cover at least 4 of these archetypes:

- **New method** (novel architecture/algorithm/loss)
- **Benchmark/evaluation** (new benchmark, protocol audit, reproducibility study)
- **Analysis/understanding** (why does X work/fail; probing; scaling behavior)
- **Combination/transfer** (import a technique from an adjacent field)
- **Application/system** (deploy known methods in an underserved setting)
- **Data/resource** (dataset, simulator, tooling)

Each idea gets a fixed card:

```
### Idea N: <punchy title>
- **One-liner**: what you'd do, in one sentence.
- **Gap it fills**: tie back to a specific gap from survey.md.
- **Why now**: what recent development makes this newly feasible or newly interesting.
- **Sketch**: 2–4 sentences on method/experiments; name the datasets/baselines you'd use.
- **Nearest neighbors**: 1–3 closest existing papers (cited) and the delta from each.
- **Biggest risk**: the single most likely way this dies.
```

Ideas must be grounded: if you can't name the nearest-neighbor papers from your search results, you haven't searched enough to claim novelty — go back to Phase 2.

## Phase 5 — Rank

Score each idea 1–5 on two axes and rank by the product:

- **Impact**: if it works, who cares? (5 = reshapes how the subfield evaluates/builds things; 3 = solid conference paper; 1 = incremental footnote)
- **Plausibility**: probability of a publishable result **given the user's stated constraints** from Phase 1 — compute, timeframe, data access, existing assets. An idea needing a 64-GPU pretraining run scores low for a solo researcher on one GPU regardless of its merit.

Present a ranked table (rank, idea, impact, plausibility, product, one-line justification), then write a short recommendation paragraph: your top pick, the runner-up, and one "dark horse" (high impact, lower plausibility) worth keeping warm. Be opinionated — the user asked for a ranking, not a shrug. Note explicitly where scores are sensitive to assumptions ("if you can get access to dataset X, idea 7 jumps to #2").

Finish by telling the user the output paths and offering obvious next steps (deep-dive one idea into a full proposal, expand the survey section, or re-run with different constraints).

---

## Failure handling

- Semantic Scholar rate-limits aggressively (HTTP 429): the script auto-retries with backoff; if it keeps failing, drop `s2` from `--sources` and rely on arXiv + OpenAlex, and note the reduced citation-count fidelity.
- If all APIs are unreachable (offline sandbox), say so plainly, produce the survey from web-search results only, and mark every citation that couldn't be verified against an API record with `[unverified]`. Never silently fabricate.
- If the topic is too broad after clarification (a survey would need 200+ papers), propose 2–3 narrower cuts and let the user pick rather than producing a shallow overview.
