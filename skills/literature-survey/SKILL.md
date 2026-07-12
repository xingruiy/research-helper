---
name: literature-survey
description: |
  Turn a rough research topic or direction into a grounded mini-survey of the literature.
  Use this skill whenever the user describes a research area, asks "what's out there on X",
  wants a literature landscape / related-work scan, wants the field mapped out, or asks how a
  sub-area has evolved. Trigger even if they don't say "survey" — phrases like "I'm thinking
  about working on...", "map out the field of...", or "what's the state of the art in X?" all
  qualify. Do NOT use for implementing code from a known paper, for a single paper summary,
  or for brainstorming/ranking research ideas — this skill surveys what exists; it does not
  propose new ideas.
---

# Literature Survey

Given a rough description of a research topic/direction, run this pipeline:

**Orient → Clarify → Search → Survey**

The single deliverable is **`auto-research/survey.md`** (relative to the current working
directory; create the folder if needed). Keep raw search results in `auto-research/raw/`
so the user can audit sources.

**Scope guard**: this skill produces a survey of existing literature only. Do not append
research-idea proposals, project suggestions, or rankings — even if gaps in the field
suggest them. The "Open problems & gaps" section describes what the literature is missing;
it does not prescribe what the user should do about it.

## Portability rules (Claude / Codex / any agent)

This skill must work identically in any coding agent. Therefore:

- Use only **plain-text questions in the chat** to interact with the user — never
  agent-specific UI tools (option pickers, forms, plan modes).
- Use only **bash + `python3` (stdlib)** for tooling. `scripts/lit_search.py` has zero
  dependencies. Resolve script paths relative to this SKILL.md file's directory.
- If the agent has a built-in web search/browse capability, use it where Phase 2 says so;
  if not, skip those sub-steps and note the reduced coverage in the survey — the API
  script alone is sufficient to complete the pipeline.

---

## Phase 1 — Orient, then clarify (mandatory stop — no defaults)

Send **one message** containing two parts, then STOP and wait for the user's reply.

**Part A — Orientation paragraph.** Before asking anything, write a brief paragraph
(4–7 sentences) sketching the area as you currently understand it: what the problem is,
the 2–4 main camps or sub-directions, and where the live tensions or trade-offs are.
Label it as orientation from prior knowledge, not as cited literature — its purpose is to
give the user enough of a mental map to understand *why* the following questions matter
and to ponder their answers, not to be the survey itself.

**Part B — Clarifying questions.** Ask **3–5 questions**, picking the ones that are
actually ambiguous for this topic:

1. **Scope**: Which sub-area / setting matters most? (offer 2–4 concrete interpretations
   of their topic as *options to choose between*, not as suggestions you'd pick for them)
2. **Purpose**: What is the survey for — related-work section for a paper, thesis
   orientation, engineering/product decision, general understanding? This changes depth
   and emphasis.
3. **Time horizon**: Full history of the area, or focused on the recent frontier
   (e.g. last 2–3 years)?
4. **Coverage vs. depth**: Broad map with many families briefly, or deep on one or two
   families?
5. **Prior position**: What have they already read/tried/built, so the survey doesn't
   re-explain what they know?

**Hard rules for this phase:**

- **Do not offer defaults or recommendations.** No "my default would be...", no
  "(recommended)" markers, no "reply 'go ahead' to use my assumptions". The user must
  make these calls themselves.
- **Do not proceed without answers.** If the user replies with "you decide", "use
  defaults", "just go", or otherwise declines to answer, do not start searching. Explain
  that this skill requires their input to scope the survey correctly, restate the
  unanswered questions, and stop. If they still decline, **abort the skill** — state
  plainly that the survey was not run and why.
- Even if the user's initial message seems to answer everything, still present the
  orientation paragraph and confirm your reading of their scope with at least one
  question before proceeding. Never skip straight to Phase 2.

## Phase 2 — Search (APIs first, web search second)

**Do not rely on your training knowledge of the literature — it is stale and you will
hallucinate citations.** Every paper named in the survey must come from a search result.
(The Phase 1 orientation paragraph is the only place prior knowledge is allowed, and it
names no citations.)

Use the bundled script (stdlib-only Python, no installs needed; `scripts/` is relative to
this skill's directory):

```bash
python3 scripts/lit_search.py search "your query" --sources arxiv,s2,openalex --limit 25 --out auto-research/raw/q1.jsonl
python3 scripts/lit_search.py citations <S2_PAPER_ID or arXiv:2403.xxxxx> --direction both --limit 30 --out auto-research/raw/cites_key1.jsonl
python3 scripts/lit_search.py merge auto-research/raw/*.jsonl --out auto-research/raw/merged.md
```

See `references/api_cheatsheet.md` for the underlying APIs, query syntax, and rate-limit
rules (read it if the script fails or you need a query type it doesn't cover). Google
Scholar has no API — OpenAlex is the stand-in for coverage beyond arXiv.

Search strategy (aim for 4–8 keyword searches + 2–4 citation expansions, ~60–120
candidate papers before filtering):

1. **Seed queries**: 3–5 phrasings of the topic, including synonyms and adjacent
   terminology (e.g. "feedforward 3D reconstruction" AND "pointmap regression" AND
   "multi-view stereo transformer").
2. **Snowball**: identify the 2–4 most central papers from seed results; pull their
   references (backward) and citations (forward) via the `citations` command. Forward
   citations sorted by recency reveal the frontier.
3. **Recency pass**: one query restricted to the last ~12 months to catch what surveys miss.
4. **Web search pass** (only if the agent has web search): workshop pages, benchmark
   leaderboards, well-known blog posts, GitHub repos. Also fetch abstracts of the ~10
   most central papers if snippets are insufficient.
5. **Existing surveys**: explicitly query `"survey" OR "benchmark" <topic>` — if a recent
   survey exists, say so prominently; it is the fastest map of the taxonomy and changes
   what this survey needs to add.
6. **Open-questions mining**: read the abstracts (and, via web search, the
   limitations/future-work discussions) of the most central papers and of any existing
   surveys specifically for acknowledged limitations, unevaluated conditions, and
   conflicting results. This evidence feeds the survey's open-problems section — it must
   come from the searched papers, not from your intuition about the field.

Deduplicate, then select ~20–35 papers that actually matter. Prefer: highly cited
anchors, recent frontier work, and papers that define datasets/benchmarks/metrics.

## Phase 3 — Compose the survey

Write `auto-research/survey.md` following `references/survey_template.md`. Non-negotiables:

- **Tone: research-paper prose — assertive and authoritative.** State findings as facts
  ("Transformer-based methods dominate since 2023", not "it seems that..." or "one could
  argue..."). Do not hedge, do not defend against hypothetical objections ("a critic
  might say...", "of course, this depends on..."), and do not repeatedly re-clarify the
  scope — the framing section states the scope once, and the rest of the document simply
  operates within it. Uncertainty is expressed only where the *literature itself* is
  unsettled, and then as a direct statement of the disagreement.
- **Taxonomy over chronology**: organize by approach/axis, not by year.
- Every claim about a specific paper carries an inline citation like
  `[Wang et al., 2024, arXiv:2403.xxxxx]` with the identifier taken verbatim from search
  output. Never cite from memory.
- Include a **key-papers table** (paper, year, venue if known, one-line contribution,
  code available?).
- Include **Datasets & evaluation** and **Open problems / gaps** sections. The gaps
  section is the payload of the survey: its purpose is to let the user design further
  experiments directly from it, so it must cover the field's open questions **accurately
  and completely**, not as an afterthought. Each open question must be (a) grounded in
  evidence from the search — a limitation the papers themselves acknowledge, a condition
  no paper in the set evaluates, a conflict between reported results — with the
  supporting papers cited; and (b) stated precisely enough to be experimentally
  actionable: name the missing condition, setting, baseline comparison, or measurement
  ("no method reports X on benchmark Y under condition Z" beats "more work is needed").
  Still findings, not proposals — describe what is untested or unresolved; do not
  prescribe projects for the user to pursue.
- Flag disagreements or unresolved questions in the literature explicitly.
- 800–1500 words of prose plus tables. This is an internal report, not a journal survey.
- Reflect the user's Phase 1 answers: scope exclusions, time horizon, and depth choices
  should be visible in the framing section.

Finish by telling the user the output path (`auto-research/survey.md`), how many papers
were reviewed, and where the raw results live. Do not suggest research ideas as a next step.

---

## Failure handling

- Semantic Scholar rate-limits aggressively (HTTP 429): the script auto-retries with
  backoff; if it keeps failing, drop `s2` from `--sources` and rely on arXiv + OpenAlex,
  and note the reduced citation-count fidelity.
- If all APIs are unreachable (offline sandbox), say so plainly, produce the survey from
  web-search results only (if available), and mark every citation that couldn't be
  verified against an API record with `[unverified]`. Never silently fabricate. If
  neither APIs nor web search are available, abort and tell the user the environment
  cannot support a grounded survey.
- If the topic is too broad after clarification (a survey would need 200+ papers),
  present 2–3 narrower cuts and stop for the user to pick — do not pick one yourself.
