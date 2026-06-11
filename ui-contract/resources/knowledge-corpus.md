---
type: contract-entry
resource: knowledge-corpus
summary: The fabric's queryable knowledge surface — semantic search over embedded markdown corpora (the Claude Code Atlas + the platform-docs mirror via the substrate face, the repo-exocortex via the company corpus tool), each hit a cited, dereferenceable source.
schemes: []
status: building
relates-to: ["[[transcript]]", "[[claude-memory]]", "[[cost-usage]]", "[[which-corpus]]"]
---

# Resource: knowledge-corpus

## Identity
**A knowledge-corpus is identified by its VAULT/SPACE name (`claude-code-atlas`,
`claude-platform-docs`, the company `repo` space, the planned `claude-sessions` space); a
search returns hits each carrying a stable source address (`filesystem://<vault>/<rel_path>`
or `code://<repo-rel-path>`) that round-trips back to the document.**
There is no single id for "the knowledge" — there is a SET of named, embedded corpora, listed
by the inventory op below; you pick the corpus by name, search it by meaning, and follow each
hit's source address to the document on disk (granted: plain markdown). The Atlas/docs vaults
are NOT company-owned files — they live behind a separate substrate MCP server the company
wires in (see [[knowledge-corpus#Caller]] and TRANSPORTS `substrate-mcp`); the company's own
embedded corpus (the repo-exocortex + capture output) is the separate company `corpus` tool.
Two backends, one capability, kept distinct on purpose ([[which-corpus]] disambiguates).

## Representation
**A corpus is a named collection of embedded markdown chunks; its catalog entry carries the
name, the on-disk path, files indexed, chunks embedded, and the embedding model — the four
numbers a consumer needs to know whether a search will be meaningful (an unindexed or
zero-chunk corpus answers nothing, and says so).**
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/knowledge-corpus.catalog-entry",
  "type": "object",
  "required": ["name"],
  "properties": {
    "name":            { "type": "string", "description": "the corpus/vault/space id you search by" },
    "backend":         { "enum": ["substrate", "company"], "description": "substrate = the obsidian-overlord substrate MCP (the knowledge vaults); company = the company corpus tool (repo-exocortex + capture output)" },
    "path":            { "type": ["string", "null"], "description": "on-disk root (substrate vaults only) — hits dereference here" },
    "files_indexed":   { "type": ["integer", "null"] },
    "chunks_embedded": { "type": ["integer", "null"] },
    "embedding_model": { "type": ["string", "null"], "description": "the vectors are only comparable WITHIN one embedding model — stated, never assumed" } } }
```
A single search HIT (what a query returns; the unit a UI renders as a result card):
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/knowledge-corpus.hit",
  "type": "object",
  "required": ["text", "source"],
  "properties": {
    "text":     { "type": "string", "description": "the matched chunk's text (full at enrichment=none, ~200 chars at lean)" },
    "source":   { "type": "string", "description": "the source address — filesystem://<vault>/<rel_path> (substrate) or code://<repo-rel> (company); ALWAYS dereferenceable (V7)" },
    "title":    { "type": ["string", "null"] },
    "heading_path": { "type": ["string", "null"], "description": "the chunk's heading lineage inside its file — the deep anchor" },
    "distance": { "type": ["number", "null"], "description": "vector distance; SMALLER = nearer in meaning (NOT a probability, NOT a 0..1 score)" } } }
```
| field | reality (measured via `substrate-mcp.get_status`, 2026-06-12) |
|---|---|
| `claude-code-atlas` | 287 files · 6,958 chunks embedded · path `/mnt/c/Users/Workstation001/Documents/Obsidian Builder/Spaces/Claude Code Atlas` — the research-note + official-docs-mirror corpus answering "how does Claude Code do X" |
| `claude-platform-docs` | 811 files · 23,274 chunks (`chroma_count` 50,781 — a known store/index count asymmetry, reported not hidden) · path `/home/tim/corpora/claude-platform-docs` — the Anthropic platform/API docs mirror |
| company `repo` space | populated by `ingest()` over the company source tree; query via the company `corpus` tool — coverage is whatever has been ingested, NOT the whole repo by default (incremental, path-keyed) |
| `claude-sessions` space | PLANNED — the transcript corpus ([[transcript]]) exists on disk (1,040 md) but its substrate vault is not yet registered; until then it is filesystem-readable, not semantically searchable |
| embedding model | `BAAI/bge-m3` (substrate, OpenAI-compatible provider; `health` reported EMPTY `{}` at status time — a known un-instrumented health field, stated honestly) |

## State model
**State model: stateless.** (A corpus search is a pure read over an embedded index; the index
GROWS — substrate rescans on its own cadence, company `ingest()` adds records — but a search
itself transitions nothing. Freshness is a property of the last scan/ingest, not a session
state.)

## Caller
**No caller identity is required to search; the backend identity is what matters — the Atlas/
docs vaults answer through the `substrate-mcp` stdio server (a SEPARATE repo,
`/home/tim/repos/obsidian-overlord`, wired into every session's MCP config), the repo-exocortex
answers through the company `corpus` tool, and BOTH are `process-local` stdio — no socket, no
network, no auth.** A bridge/HTTP consumer cannot reach these today: there is no HTTP face on
either search backend (the gap is named in the search op's bindings). This is the precise
honesty: the knowledge capability is real and proven-by-use over MCP, and unreachable from a
pure-HTTP vantage until a bridge route is built.

## Operations

## op: knowledge-corpus.list
**`knowledge-corpus.list` is the corpus catalog read: the named corpora a consumer can search,
each with its backend, indexed file/chunk counts, and embedding model — the pre-flight that
tells you whether a search will return anything before you run it.**
```contract:op
op: knowledge-corpus.list
resource: knowledge-corpus
kind: list
status: building
direction: outbound
atlas: [CC-23.2]
tasks:
  - phrase: "what knowledge corpora can I search"
  - phrase: "is the Claude Code Atlas indexed and how big is it"
  - alias: "list the vaults"
  - alias: "what's in the knowledge base"
bindings:
  - { kind: mcp, tool: list_vaults, server: substrate-mcp, exposure: "exposure.json#substrate-mcp", note: "the substrate (knowledge-vault) catalog; include_config=true adds path/ignore/extensions" }
  - { kind: mcp, tool: get_status, server: substrate-mcp, exposure: "exposure.json#substrate-mcp", note: "the FULL field-reality: per-vault files_indexed, chunks_embedded, chroma_count, embedding model + health" }
  - { kind: mcp, tool: cognition_info, server: company, exposure: "exposure.json#mcp-company", note: "the company side: cognition_info().spaces lists the embeddable spaces (e.g. 'repo') the company corpus tool can query" }
liveness: snapshot
live-twin: "none — static between scans/ingests; corpus GROWTH is observed by re-reading this op, not by a stream"
emits: []
verification:
  substrate-catalog: {state: verified-by-use, run: "list_vaults + get_status called live 2026-06-12 — 10 vaults returned incl. claude-code-atlas (287f/6958c) + claude-platform-docs (811f/23274c)", date: 2026-06-12}
  company-spaces:    {state: unverified, note: "cognition_info().spaces not exercised in this lane; the company-side space enumeration is a candidate-reuse claim until run"}
```
```contract:example
captured: synthetic
binding: mcp
request: list_vaults(include_config=false)
response: { "vaults": [ {"name": "claude-code-atlas", "active": false},
                        {"name": "claude-platform-docs", "active": false} ],
            "count": 10, "lean": true }
```
Adjacent: [[knowledge-corpus#op: knowledge-corpus.search]] (search a named corpus),
[[which-corpus]] (which corpus answers which question).

## op: knowledge-corpus.search
**`knowledge-corpus.search` is the meaning-keyed read over an embedded corpus: a natural-
language query against one or more named vaults/spaces, returning the nearest chunks each with
its dereferenceable source address — the company's actual "look it up, never invent it"
capability, and the strongest live-by-use endpoint in the F6 lane.**
```contract:op
op: knowledge-corpus.search
resource: knowledge-corpus
kind: search
status: building
direction: outbound
atlas: [CC-23.2, CC-35.1]
tasks:
  - phrase: "how does Claude Code do X"
    params: {vault: claude-code-atlas}
  - phrase: "what does the Anthropic API doc say about Y"
    params: {vault: claude-platform-docs}
  - phrase: "ask the company codebase a question"
    params: {backend: company, space: repo}
  - alias: "search the knowledge base"
  - alias: "look it up in the docs"
  - alias: "semantic search the Atlas"
  - alias: "ask the codebase"
bindings:
  - { kind: mcp, tool: search_semantic, server: substrate-mcp, exposure: "exposure.json#substrate-mcp", note: "the knowledge vaults; query + vault(name|list|'*'|null) + n_results + enrichment(lean|none|minimal|full) + context(chunk|window|section|file) + filter_type/filter_axis" }
  - { kind: mcp, tool: corpus, op-param: "op=query", server: company, exposure: "exposure.json#mcp-company", note: "the repo-exocortex / capture corpus; text + space(e.g. 'repo') + k + detail(concise|detailed). detailed inlines each hit's record content (answers in ONE call)" }
liveness: snapshot
live-twin: "none — static between scans/ingests"
emits: []
correlate: []
verification:
  substrate-search: {state: verified-by-use, run: "search_semantic over [claude-code-atlas,claude-platform-docs] for CLAUDE.md-hierarchy + cost-tracking + auto-memory queries 2026-06-12 — every cited fact in [[claude-memory]] and [[cost-usage]] traces to a returned chunk's source address", date: 2026-06-12}
  company-query:    {state: unverified, note: "company corpus(op='query') not exercised in this lane — candidate-reuse until run; the repo space's coverage depends on what ingest() has fed"}
```
Substrate request: `search_semantic(query="…", vault=["claude-code-atlas"], n_results=8,
enrichment="none", context="window")`. `enrichment` controls payload size (lean ~5KB at
n_results=10 on heavy-frontmatter vaults; `full` adds wikilinks; on Tim's vaults parent
envelopes are ~3KB each so `minimal`/`full` get large fast). `context="window"` returns the
preceding+following chunks; `"file"` returns the whole parent body (use sparingly). `distance`
is a vector distance (smaller = nearer); it is NOT a normalized 0..1 confidence.
```contract:example
captured: synthetic
binding: mcp
request: search_semantic(query="how does CLAUDE.md memory hierarchy load: enterprise, user, project, local", vault=["claude-code-atlas"], n_results=3, enrichment="none", context="chunk")
response: { "query": "how does CLAUDE.md memory hierarchy load…",
            "vaults": ["claude-code-atlas"],
            "results": [
              { "text": "CLAUDE.md files can live in several locations… in load order, from broadest scope to most specific…",
                "metadata": { "address": "filesystem://claude-code-atlas/Docs/claude-code/memory.md",
                              "rel_path": "Docs/claude-code/memory.md",
                              "heading_path": "how-claude-remembers-your-project/claudemd-files/choose-where-to-put-claudemd-files",
                              "title": "How Claude remembers your project", "vault": "claude-code-atlas" },
                "distance": 0.272 } ],
            "n_returned": 3, "duplicates_collapsed": 1 }
```
```contract:example
captured: synthetic
binding: mcp
request: corpus(op="query", space="repo", text="where does the supervisor read injected turns", detail="detailed", k=2)
response: { "op": "query",
            "ranked": [ { "id": "code://runtime/session_supervisor.py", "score": 0.81,
                          "content": "<the capture digest of that file>",
                          "record_address": "run://corpus/…" } ],
            "note": "… · every hit id is corpus(op='read', address=<id>)-able" }
```
The completeness check for a search task is a CONSISTENCY cross-check, not an event match
(reads have a pass-shape, §8 step 5): the returned hits' source addresses dereference to real
documents on disk AND at least one hit's text actually contains the answer the task sought —
a search that returns only off-topic chunks is a `fail`/drop, not a pass on "got a 200".
Adjacent: [[knowledge-corpus#op: knowledge-corpus.list]] (what's searchable),
[[which-corpus]] (which backend), [[transcript#op: transcript.search]] (the PLANNED
session-history search — a sibling capability over a different, not-yet-registered corpus).

## Errors
**The search backends fail loud at the call boundary: an unknown vault name, a missing
required `text`/`query`, or a down embedding provider each returns a teaching error — never an
empty result that masquerades as "no matches".** An empty `results` array with a healthy index
means genuinely no near chunks (a real, honest negative); an empty array because the embedder
is down is a DIFFERENT condition the backend reports as an error, not silent emptiness.
```contract:error
code: knowledge-corpus.unknown-vault | retryable: false
when: a vault/space name passed to search/list does not exist in the catalog
teach: "List searchable corpora via [[knowledge-corpus#op: knowledge-corpus.list]] — names must match exactly (claude-code-atlas, claude-platform-docs, the company 'repo' space). Vault is case- and spelling-exact."
```
```contract:error
code: knowledge-corpus.empty-query | retryable: false
when: search called with no query/text
teach: "Pass the natural-language question as `query` (substrate) or `text` (company corpus). An empty query has no meaning to embed."
```
```contract:error
code: knowledge-corpus.embedder-down | retryable: true
when: the embedding provider is unreachable (substrate bge-m3 / the company embed service)
teach: "The vectors cannot be computed without the embedder. For the company space, bring the embed model up (the resource-managed stack — see [[fabric-config]] / `company up`); for substrate, the bge-m3 provider must be reachable. Retry once it is healthy. A down embedder NEVER returns fake matches."
```

## Links
**Every hit's `source` is a dereferenceable address: `filesystem://<vault>/<rel_path>` (the
substrate vaults — read the file directly on disk at the catalog `path` + `rel_path`, or
`get_by_address` on the substrate face) and `code://<repo-rel>` (the company corpus — round-
trips through `corpus(op='read', address=<id>)`). No hit is a dead end (V7); `heading_path`
deep-anchors within the file. The corpora about Claude Code's OWN memory/cost behavior are the
authoritative SOURCE the [[claude-memory]] and [[cost-usage]] entries cite — those two entries
contract the DATA MODELS; this entry contracts how to QUERY the knowledge of them.**
