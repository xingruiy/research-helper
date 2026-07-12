---
name: deep-dive
description: |
  Turn one direction or open problem from an existing literature survey into a
  comprehensive, near-exhaustive review of that specific thread. Use this skill whenever
  the user wants to "go deeper" on something a prior survey surfaced — phrases like
  "deep dive into X", "expand on open problem 3", "give me a full review of the
  neural-field thread", "cover everything published on X", or "explore that gap in more
  detail" all qualify, even if they don't say "deep dive". Requires prior output from the
  literature-survey skill (`auto-research/survey.md`); if none exists, this skill aborts
  and directs the user to run literature-survey first. Do NOT use for the initial
  broad survey of a field (that is literature-survey), for a single paper summary, or
  for proposing/ranking research ideas.
---

# Deep Dive

Given an existing survey produced by the **literature-survey** skill, take one direction
or open problem from it and produce a comprehensive review of that thread — covering as
much of the published record on it as the search tools can reach. Where the survey is a
map of the whole field, the deep dive is a complete account of one road.

Pipeline: **Verify prerequisites → Lock the direction → Exhaustive search → Compose the review**

The deliverable is **`auto-research/deep-dive/<slug>/review.md`** (relative to the current
working directory), where `<slug>` is a short kebab-case name for the chosen direction
(e.g. `neural-field-bost`, `uq-for-tomography`). Raw search results go in
`auto-research/deep-dive/<slug>/raw/` so the user can audit sources.

**Scope guard**: this skill reviews existing literature only. Do not append research-idea
proposals, project suggestions, or rankings — even when the refined gaps invite them. The
open-questions section describes what the literature has not resolved; it does not
prescribe what the user should do about it.

## Portability rules (Claude / Codex / any agent)

This skill must work identically in any coding agent. Therefore:

- Use only **plain-text questions in the chat** to interact with the user — never
  agent-specific UI tools (option pickers, forms, plan modes).
- Use only **bash + `python3` (stdlib)** for tooling. This skill bundles no scripts of
  its own; it reuses the literature-survey skill's `scripts/lit_search.py` (zero
  dependencies). Resolve it as `<this skill's directory>/../literature-survey/scripts/lit_search.py`.
  If that path does not exist, tell the user the deep-dive skill requires the
  literature-survey skill to be installed alongside it (both are installed by this
  repository's `install.sh`) and abort.
- If the agent has a built-in web search/browse capability, use it where Phase 2 says so;
  if not, skip those sub-steps and note the reduced coverage in the review — the API
  script alone is sufficient to complete the pipeline.

---

## Phase 0 — Verify prerequisites (hard abort if missing)

Check for `auto-research/survey.md` in the current working directory. If it does not
exist, **abort immediately**: state plainly that no literature survey was found, that the
deep-dive skill only extends an existing survey, and that the user should run the
literature-survey skill first. Do not offer to run the survey yourself as part of this
invocation, do not produce a review from scratch, and do not search. Stop.

If the survey exists:

1. Read `auto-research/survey.md` in full. It is the map you are zooming into: its
   taxonomy names the threads, its open-problems section names the gaps, and its
   citations are your seed papers.
2. Inventory `auto-research/raw/*.jsonl` (and `merged.md` if present). These are
   already-retrieved candidates — many deep-dive-relevant papers are already sitting
   there, filtered out of the survey only for breadth reasons. Reuse them; do not
   re-run queries the survey already ran.

## Phase 1 — Lock the direction

The user must end up having chosen exactly one direction. Two ways to get there:

**Infer from the prompt.** If the user's request names a direction that maps cleanly
onto the survey — a taxonomy family, a numbered open problem, or an unambiguous
paraphrase of either ("go deeper on the PINN stuff", "expand open problem 2") — restate
your reading of it in 2–4 sentences: what the direction is, what is in scope, what is
explicitly out of scope, and which survey sections/papers seed it. Then proceed. A
confident restatement the user can interrupt beats a redundant question.

**Ask when it is not clean.** If the prompt names no direction, names several, or names
one that could map onto the survey in more than one way, present a numbered list of
candidate directions extracted from the survey (its taxonomy families and its open
problems are the natural candidates — typically 4–10 items, each with a one-line
description of what a deep dive on it would cover), then STOP and wait for the user's
pick. Do not pick for them, do not mark a recommendation, and do not proceed on "you
decide" — if the user declines to choose, explain that the deep dive needs a single
direction to be worth doing, restate the list, and stop. If they still decline, abort
and say the deep dive was not run and why.

Either way, before Phase 2 you must be able to write down a **scope contract**: one
paragraph stating the direction, its boundaries (what neighboring threads are excluded),
and the seed papers from the survey. This paragraph becomes Section 1 of the review.

## Phase 2 — Exhaustive search (aim for saturation)

**Do not rely on your training knowledge of the literature — it is stale and you will
hallucinate citations.** Every paper named in the review must come from a search result
or from the survey's audited raw files.

The survey selected ~20–35 papers across the whole field; the deep dive should surface
**most of what exists on the one chosen thread** — typically 40–100 relevant papers for
an active direction, fewer for an embryonic one. The standard is *saturation*, not a
fixed count: keep searching until new queries and new citation expansions return mostly
papers you have already seen. As a working rule, when two consecutive search rounds each
yield under ~10% previously-unseen relevant papers, coverage is adequate — say so in the
review's methodology line.

Use the literature-survey script (path per the portability rules above; see the
literature-survey skill's `references/api_cheatsheet.md` if the script fails or you need
a query type it doesn't cover):

```bash
LITSEARCH=<this skill's directory>/../literature-survey/scripts/lit_search.py
python3 "$LITSEARCH" search "your query" --sources arxiv,s2,openalex --limit 25 --out auto-research/deep-dive/<slug>/raw/q1.jsonl
python3 "$LITSEARCH" citations <S2_PAPER_ID or arXiv:2403.xxxxx> --direction both --limit 30 --out auto-research/deep-dive/<slug>/raw/cites_key1.jsonl
python3 "$LITSEARCH" merge auto-research/raw/*.jsonl auto-research/deep-dive/<slug>/raw/*.jsonl --out auto-research/deep-dive/<slug>/raw/merged.md
```

Search strategy — deeper and more repetitive than the survey's, by design:

1. **Harvest the survey.** Extract every paper the survey cites for this direction and
   locate its record in the existing `auto-research/raw/` files. These are your core set.
2. **Snowball every core paper.** Pull references (backward) and citations (forward) for
   *each* core paper, not just the most central 2–4. Forward citations sorted by recency
   are the primary instrument for finding the frontier of a narrow thread.
3. **Terminology sweep.** Narrow threads hide under multiple names across communities
   (e.g. the same idea appears as "implicit neural representation", "neural field", and
   "coordinate network"). Run one query per naming variant, including the vocabulary of
   adjacent communities the survey identified.
4. **Recency pass.** One query restricted to the last ~12 months on the thread's core
   terms — the newest work is the least likely to be cited by anything yet.
5. **Second-generation snowball.** Any paper discovered in steps 2–4 that proves central
   (highly cited within the thread, or introduces the thread's benchmark/method that
   others build on) gets its own citation expansion.
6. **Web search pass** (only if the agent has web search): theses, workshop papers,
   project pages, GitHub repos, and benchmark leaderboards for the thread; fetch
   abstracts or key results tables for core papers whose API snippets are too thin to
   support the per-paper detail the review needs.
7. **Repeat 2–5 until saturated** per the criterion above.

Then filter: keep every paper that genuinely belongs to the thread (comprehensiveness is
the point — a paper that merely applies the thread's standard method to a new domain
still earns a bibliography row), but reserve detailed treatment for the papers that
advance the thread's methods, evidence, or evaluation.

## Phase 3 — Compose the review

Write `auto-research/deep-dive/<slug>/review.md` following
`references/review_template.md` (in this skill's directory). Non-negotiables:

- **Tone: research-paper prose — assertive and authoritative.** State findings as facts.
  No hedging, no defending against hypothetical objections, no re-clarifying scope after
  Section 1. Uncertainty appears only where the literature itself is unsettled, stated
  as a direct account of the disagreement.
- **Depth over breadth.** The survey gave each family a paragraph; the deep dive gives
  the important papers of this one thread individual technical treatment: what the
  method actually does, what it was evaluated on, what it reported, and what it
  acknowledged it cannot do. Where papers report comparable numbers, tabulate them.
- **Development narrative is allowed here.** Unlike the survey (taxonomy over
  chronology), a single thread has a real intellectual history: what problem opened it,
  which papers redirected it, and why. Tell it — then organize the technical body by
  sub-approach.
- Every claim about a specific paper carries an inline citation like
  `[Wang et al., 2024, arXiv:2403.xxxxx]` with the identifier taken verbatim from search
  output or the survey's raw files. Never cite from memory.
- Include a **complete bibliography table** listing *every* relevant paper found — this
  is the comprehensiveness deliverable, and it is normal for it to be several times
  longer than the survey's key-papers table.
- Include a **results-comparison table** wherever two or more papers evaluate on the
  same dataset/flow/benchmark, and say explicitly when no two papers do (that fact is
  itself a finding).
- Include **Open questions within this direction** — the survey's gap, refined: after
  reading everything on the thread, state precisely what remains unmeasured, untested,
  or contradictory, with supporting citations. Findings, not proposals.
- 2000–4000 words of prose plus tables. Longer than the survey; still an internal
  report, not a journal article.

Finish by telling the user the output path, how many papers were reviewed against how
many candidates retrieved, whether saturation was reached, and where the raw results
live. Do not suggest research ideas as a next step.

---

## Failure handling

- Semantic Scholar rate-limits aggressively (HTTP 429): the script auto-retries with
  backoff; if it keeps failing, drop `s2` from `--sources` and rely on arXiv + OpenAlex,
  and note the reduced citation-count fidelity. Deep dives issue many more citation
  calls than surveys — space them out and batch merges rather than hammering the API.
- If all APIs are unreachable (offline sandbox), the deep dive can still proceed from
  the survey's existing `auto-research/raw/` files plus web search (if available), but
  say so plainly, mark every citation that couldn't be verified against an API record
  with `[unverified]`, and state that saturation was not reachable. Never silently
  fabricate. If neither the raw files nor any search capability can support the chosen
  direction, abort and say why.
- If the chosen direction turns out to be broader than expected (saturation nowhere in
  sight past ~150 relevant papers), stop searching, present 2–3 narrower cuts of the
  direction, and wait for the user to pick — do not pick one yourself.
- If the chosen direction turns out to be nearly empty (under ~8 relevant papers after
  a full search cycle), write the review anyway at proportionate length and state
  prominently that the thread is embryonic — a thin literature is a valid and useful
  finding.
