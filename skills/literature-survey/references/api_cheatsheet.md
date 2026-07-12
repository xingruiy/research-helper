# API cheatsheet

Read this if `scripts/lit_search.py` fails, or you need query types it doesn't cover
(author search, venue filters, batch lookups). All APIs below are keyless. Two optional
env vars improve rate limits and are picked up automatically by the script:
`S2_API_KEY` (Semantic Scholar `x-api-key` header) and `OPENALEX_MAILTO` (OpenAlex
polite pool). See `.env.example` at the repo root.

## arXiv API
- Endpoint: `http://export.arxiv.org/api/query`
- Params: `search_query`, `start`, `max_results` (≤2000), `sortBy=relevance|submittedDate`
- Query syntax: fielded prefixes `ti:` (title), `abs:` (abstract), `au:` (author), `cat:`
  (category, e.g. `cs.CV`, `cs.RO`), `all:`. Boolean: `AND`, `OR`, `ANDNOT`.
  Example: `search_query=cat:cs.CV+AND+abs:%22pose+regression%22`
- Returns Atom XML. Politeness: 1 request / 3 seconds.
- No citation counts — use S2/OpenAlex for those.

## Semantic Scholar Graph API
- Base: `https://api.semanticscholar.org/graph/v1`
- Paper search: `/paper/search?query=...&fields=title,year,venue,abstract,citationCount,externalIds,url&limit=100`
- Bulk search (better for >100 results, supports boolean syntax): `/paper/search/bulk?query=...`
- Paper by ID: `/paper/{id}` where id is an S2 hash, `arXiv:2403.12345`, `DOI:10.xxx/...`,
  or `CorpusId:12345`
- References / citations: `/paper/{id}/references` and `/paper/{id}/citations`
- Author search: `/author/search?query=name`
- Recommendations: `https://api.semanticscholar.org/recommendations/v1/papers/forpaper/{id}` —
  useful extra snowballing signal.
- Rate limit (no key): shared pool, roughly 1 req/sec with bursts; expect HTTP 429 —
  back off 5–30 s. Abstracts are sometimes null (publisher restrictions); fall back to
  arXiv/OpenAlex for the abstract text.

## OpenAlex (Google Scholar stand-in — GS has no API and blocks scraping)
- Base: `https://api.openalex.org`
- Works search: `/works?search=...&per-page=50`
- Filters: `&filter=from_publication_date:2024-01-01,cited_by_count:>50,concepts.id:...`
- Sort: `&sort=cited_by_count:desc` or `relevance_score:desc`
- Abstracts come as an inverted index (`abstract_inverted_index`) — the script reconstructs it.
- Citing works of W123: `/works?filter=cites:W123`
- Very generous rate limits; add `&mailto=you@example.com` for the polite pool.

## When to still use plain web search / browsing
- Workshop and challenge pages, benchmark leaderboards (paperswithcode), GitHub repos,
  blog posts, tweets/threads announcing very recent work (APIs lag arXiv by hours–days,
  and lag blogs entirely).
- Verifying venue of acceptance for an arXiv paper (search "<title> CVPR 2025" etc.).

## Verification rule
A citation may appear in `auto-research/survey.md` only if its identifier (arXiv id, DOI,
or S2 id) appears verbatim in a saved raw result under `auto-research/raw/`. Anything else
is `[unverified]`.
