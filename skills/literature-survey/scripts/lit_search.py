#!/usr/bin/env python3
"""lit_search.py — dependency-free literature search across arXiv, Semantic Scholar, OpenAlex.

Commands:
  search "query" [--sources arxiv,s2,openalex] [--limit N] [--year-from YYYY] [--out FILE.jsonl]
  citations PAPER_ID [--direction refs|cites|both] [--limit N] [--out FILE.jsonl]
      PAPER_ID: Semantic Scholar paperId, "arXiv:2403.12345", or "DOI:10.xxxx/..."
  merge FILE1.jsonl [FILE2.jsonl ...] [--out FILE.md]
      Dedupes by title/arXiv id/DOI, sorts by citation count, emits a markdown table.

All records are normalized JSON lines:
  {title, year, venue, authors, abstract, citations, arxiv_id, doi, s2_id, url, source}

No external dependencies. Python 3.8+.
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

UA = {"User-Agent": "literature-survey-skill/1.0 (literature survey tool)"}

# Optional credentials (never required; APIs work keyless):
#   S2_API_KEY      — Semantic Scholar API key, lifts the shared unauthenticated rate limit
#   OPENALEX_MAILTO — contact email for OpenAlex's polite pool (better rate limits)
S2_API_KEY = os.environ.get("S2_API_KEY", "").strip()
OPENALEX_MAILTO = os.environ.get("OPENALEX_MAILTO", "").strip()


def http_get(url, retries=4, backoff=3.0):
    headers = dict(UA)
    if S2_API_KEY and "semanticscholar.org" in url:
        headers["x-api-key"] = S2_API_KEY
    if OPENALEX_MAILTO and "openalex.org" in url:
        url += ("&" if "?" in url else "?") + "mailto=" + urllib.parse.quote(OPENALEX_MAILTO)
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            last = e
            if e.code == 429 or e.code >= 500:
                wait = backoff * (attempt + 1)
                print(f"  HTTP {e.code}, retrying in {wait:.0f}s...", file=sys.stderr)
                time.sleep(wait)
                continue
            raise
        except Exception as e:  # timeouts, DNS
            last = e
            time.sleep(backoff)
    raise RuntimeError(f"GET failed after {retries} attempts: {url}\n{last}")


def rec(title=None, year=None, venue=None, authors=None, abstract=None,
        citations=None, arxiv_id=None, doi=None, s2_id=None, url=None, source=None):
    return {
        "title": (title or "").strip(),
        "year": year,
        "venue": venue or "",
        "authors": authors or [],
        "abstract": re.sub(r"\s+", " ", abstract or "").strip()[:1200],
        "citations": citations,
        "arxiv_id": arxiv_id,
        "doi": doi,
        "s2_id": s2_id,
        "url": url,
        "source": source,
    }


# ---------------- arXiv ----------------
def search_arxiv(query, limit, year_from):
    q = urllib.parse.quote(f'all:"{query}"' if " " in query else f"all:{query}")
    url = (f"http://export.arxiv.org/api/query?search_query={q}"
           f"&start=0&max_results={limit}&sortBy=relevance")
    xml_text = http_get(url)
    ns = {"a": "http://www.w3.org/2005/Atom"}
    out = []
    for e in ET.fromstring(xml_text).findall("a:entry", ns):
        aid = (e.findtext("a:id", "", ns) or "").rsplit("/", 1)[-1]
        aid = re.sub(r"v\d+$", "", aid)
        year = int((e.findtext("a:published", "0000", ns) or "0000")[:4]) or None
        if year_from and year and year < year_from:
            continue
        out.append(rec(
            title=e.findtext("a:title", "", ns),
            year=year,
            venue="arXiv",
            authors=[a.findtext("a:name", "", ns) for a in e.findall("a:author", ns)][:6],
            abstract=e.findtext("a:summary", "", ns),
            arxiv_id=aid,
            url=f"https://arxiv.org/abs/{aid}",
            source="arxiv",
        ))
    return out


# ---------------- Semantic Scholar ----------------
S2_FIELDS = "title,year,venue,authors,abstract,citationCount,externalIds,url"


def s2_to_rec(p):
    ext = p.get("externalIds") or {}
    return rec(
        title=p.get("title"),
        year=p.get("year"),
        venue=p.get("venue") or "",
        authors=[a.get("name", "") for a in (p.get("authors") or [])][:6],
        abstract=p.get("abstract"),
        citations=p.get("citationCount"),
        arxiv_id=ext.get("ArXiv"),
        doi=ext.get("DOI"),
        s2_id=p.get("paperId"),
        url=p.get("url"),
        source="s2",
    )


def search_s2(query, limit, year_from):
    url = ("https://api.semanticscholar.org/graph/v1/paper/search?"
           f"query={urllib.parse.quote(query)}&limit={min(limit, 100)}&fields={S2_FIELDS}")
    if year_from:
        url += f"&year={year_from}-"
    data = json.loads(http_get(url))
    time.sleep(1.2)  # unauthenticated rate limit courtesy
    return [s2_to_rec(p) for p in data.get("data", [])]


def s2_citations(paper_id, direction, limit):
    """paper_id: S2 id, arXiv:xxxx.xxxxx, or DOI:..."""
    out = []
    dirs = ["references", "citations"] if direction == "both" else \
           (["references"] if direction == "refs" else ["citations"])
    key = {"references": "citedPaper", "citations": "citingPaper"}
    for d in dirs:
        url = (f"https://api.semanticscholar.org/graph/v1/paper/"
               f"{urllib.parse.quote(paper_id)}/{d}?limit={min(limit, 100)}&fields={S2_FIELDS}")
        data = json.loads(http_get(url))
        for item in data.get("data", []):
            p = item.get(key[d]) or {}
            if p.get("title"):
                r = s2_to_rec(p)
                r["source"] = f"s2:{d}"
                out.append(r)
        time.sleep(1.2)
    return out


# ---------------- OpenAlex ----------------
def search_openalex(query, limit, year_from):
    url = ("https://api.openalex.org/works?search="
           f"{urllib.parse.quote(query)}&per-page={min(limit, 50)}"
           "&select=title,publication_year,primary_location,authorships,"
           "cited_by_count,ids,abstract_inverted_index")
    if year_from:
        url += f"&filter=from_publication_date:{year_from}-01-01"
    data = json.loads(http_get(url))
    out = []
    for w in data.get("results", []):
        inv = w.get("abstract_inverted_index")
        abstract = ""
        if inv:
            pos = {}
            for word, idxs in inv.items():
                for i in idxs:
                    pos[i] = word
            abstract = " ".join(pos[i] for i in sorted(pos))
        ids = w.get("ids") or {}
        doi = (ids.get("doi") or "").replace("https://doi.org/", "") or None
        loc = (w.get("primary_location") or {}).get("source") or {}
        arxiv_id = None
        pdf = (w.get("primary_location") or {}).get("landing_page_url") or ""
        m = re.search(r"arxiv\.org/abs/(\d{4}\.\d{4,5})", pdf)
        if m:
            arxiv_id = m.group(1)
        out.append(rec(
            title=w.get("title"),
            year=w.get("publication_year"),
            venue=loc.get("display_name") or "",
            authors=[a.get("author", {}).get("display_name", "")
                     for a in (w.get("authorships") or [])][:6],
            abstract=abstract,
            citations=w.get("cited_by_count"),
            arxiv_id=arxiv_id,
            doi=doi,
            url=pdf or (ids.get("openalex")),
            source="openalex",
        ))
    return out


# ---------------- merge ----------------
def norm_title(t):
    return re.sub(r"[^a-z0-9]", "", (t or "").lower())


def merge(files, out_md):
    seen = {}
    for f in files:
        with open(f, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                r = json.loads(line)
                key = r.get("arxiv_id") or r.get("doi") or norm_title(r.get("title"))
                if not key:
                    continue
                if key in seen:
                    old = seen[key]
                    # keep max citation count, fill missing fields
                    if (r.get("citations") or 0) > (old.get("citations") or 0):
                        old["citations"] = r["citations"]
                    for k in ("abstract", "venue", "doi", "arxiv_id", "s2_id", "url", "year"):
                        if not old.get(k) and r.get(k):
                            old[k] = r[k]
                else:
                    seen[key] = r
    papers = sorted(seen.values(),
                    key=lambda r: (r.get("citations") or 0, r.get("year") or 0),
                    reverse=True)
    lines = [f"# Merged results — {len(papers)} unique papers\n",
             "| # | Title | Year | Venue | Cites | ID |",
             "|---|-------|------|-------|-------|----|"]
    for i, p in enumerate(papers, 1):
        pid = p.get("arxiv_id") and f"arXiv:{p['arxiv_id']}" or p.get("doi") or (p.get("s2_id") or "")[:12]
        title = (p.get("title") or "").replace("|", "/")[:90]
        lines.append(f"| {i} | {title} | {p.get('year') or ''} | "
                     f"{(p.get('venue') or '')[:30]} | {p.get('citations') if p.get('citations') is not None else ''} | {pid} |")
    lines.append("\n## Abstracts (top 40 by citations)\n")
    for p in papers[:40]:
        first = (p.get("authors") or [""])[0]
        lines.append(f"### {p.get('title')}")
        lines.append(f"*{first} et al., {p.get('year')}* — {p.get('url') or ''}")
        lines.append((p.get("abstract") or "(no abstract)") + "\n")
    text = "\n".join(lines)
    if out_md:
        ensure_parent(out_md)
        with open(out_md, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"Wrote {out_md} ({len(papers)} papers)")
    else:
        print(text)


def ensure_parent(path):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)


def write_jsonl(records, out):
    if out:
        ensure_parent(out)
        with open(out, "a", encoding="utf-8") as fh:
            for r in records:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"Appended {len(records)} records -> {out}")
    else:
        for r in records:
            print(json.dumps(r, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search")
    s.add_argument("query")
    s.add_argument("--sources", default="arxiv,s2,openalex")
    s.add_argument("--limit", type=int, default=20)
    s.add_argument("--year-from", type=int, default=None)
    s.add_argument("--out", default=None)

    c = sub.add_parser("citations")
    c.add_argument("paper_id")
    c.add_argument("--direction", choices=["refs", "cites", "both"], default="both")
    c.add_argument("--limit", type=int, default=30)
    c.add_argument("--out", default=None)

    m = sub.add_parser("merge")
    m.add_argument("files", nargs="+")
    m.add_argument("--out", default=None)

    args = ap.parse_args()

    if args.cmd == "search":
        records, errors = [], []
        for src in [x.strip() for x in args.sources.split(",") if x.strip()]:
            fn = {"arxiv": search_arxiv, "s2": search_s2, "openalex": search_openalex}.get(src)
            if not fn:
                errors.append(f"unknown source: {src}")
                continue
            try:
                got = fn(args.query, args.limit, args.year_from)
                print(f"  {src}: {len(got)} results", file=sys.stderr)
                records += got
            except Exception as e:
                errors.append(f"{src}: {e}")
        write_jsonl(records, args.out)
        for e in errors:
            print(f"WARNING: {e}", file=sys.stderr)
        if not records:
            sys.exit(1)
    elif args.cmd == "citations":
        write_jsonl(s2_citations(args.paper_id, args.direction, args.limit), args.out)
    elif args.cmd == "merge":
        merge(args.files, args.out)


if __name__ == "__main__":
    main()
