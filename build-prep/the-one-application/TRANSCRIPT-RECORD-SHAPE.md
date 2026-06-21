# transcriptRecord — the data-shape for transcript-viz (constellation archetype)

*recollection's supply to DNA's breadth-factory (lead g-1782025013/250). The transcript-viz surface =
constellation/graph archetype + `/api/transcript-search` (live, raw+determine) → recollection DATA · projection
HOST · DNA RENDER. This is the SOURCE shape (what the route returns) + the recommended faceRecord normalization.
DNA owns the final archetype binding; this is the contract to meet.*

## THE ROUTE (live now, direct-import — pre-bounce)
`GET /api/transcript-search?q=<query>` — TWO modes, by the presence of `?asset`:

- **RAW** (no `?asset`, optional `?k=` `?mode=`) → `session_search.search_sessions` — semantic→lexical
  degrade (honest, never fabricated). ONE result per SESSION (chunk hits grouped, best chunk leads). The
  "which sessions matched this meaning" constellation.
- **GROUNDED** (`?asset=full|visual-dna|theorem`) → `recall_determine.determine` — the no-fiction extraction
  layer. Themes of REAL, chunk-traced claims (the model groups BY INDEX, invents nothing). The "what the
  corpus actually says about this" constellation.

## SOURCE SHAPE A — RAW (search_sessions)
```jsonc
{
  "ok": true,
  "q": "…", "mode_requested": "auto", "mode_used": "semantic",   // or "lexical" (embedder-down degrade)
  "semantic": { "available": true, "why": "…" },
  "index": { "files": N, "chunks": N, "chunks_embedded": N },     // coverage (honest-empty signal)
  "chunks_matched": N, "sessions_found": N,
  "results": [                                                    // ← the constellation NODES (one per session)
    {
      "session_id": "…", "session_address": "session://…",
      "name": "…", "title": "…",            // HUMAN labels (operator-law: render these, NOT session_id)
      "summarizer": false,                  // CC internal one-shots (~77% of catalog — likely filter/dim)
      "state": "supervised-live|closed|…",  // LIVE registry state, joined at query time (node color/status)
      "cwd": "…", "last_activity": "…",
      "routable": true,
      "score": 0.42, "score_why": "cosine~0.420", "mode": "semantic",  // relevance → position/brightness
      "hits_in_session": N,                 // match DENSITY → node size/weight
      "point": {                            // the matched COORDINATE (drill-in target)
        "chunk_address": "…", "anchor": "turn-N-speaker-…",
        "heading_path": "…", "turn": N, "speaker": "user|assistant", "ts": "…"
      },
      "snippet": "…",                       // the matched excerpt = the node's MEANING (hover/expand)
      "primary_verb": "deliver|wake|queue|null",  // the LIVE action the node affords RIGHT NOW
      "commands": { "describe": "…", "consult": "…", "gather": "…", … }  // launch-ready tool calls
    }
  ],
  "note": "…"
}
```

## SOURCE SHAPE B — GROUNDED (determine)
```jsonc
{
  "ok": true,
  "topic": "…", "asset": "full|visual-dna|theorem",
  "filter": "semantic|keyword",            // semantic = the embedded extractions hit (precise)
  "n_candidates": N, "n_claims": N, "claims_grouped": N,
  "themes": [                               // ← the constellation CLUSTERS (theme stars)
    { "theme": "label",
      "claims": [ { "claim": "verbatim text", "chunk_id": 12345, "kind": "spec|discussion|decision|…" } ] }
  ],
  "no_fiction": true,                       // STRUCTURAL: every claim is a real extraction (provenance-true)
  "note": "GROUNDED (semantic-filtered): every claim is a verbatim extraction, chunk-traced…"
}
```

## RECOMMENDED faceRecord — transcriptRecord(apiResponse) → constellation
Normalize BOTH modes into one node/edge model the constellation archetype renders. (DNA: adapt to the
archetype's exact node schema — this is the semantic mapping, not the field names.)

```jsonc
{
  "kind": "transcript-constellation",
  "query": "<q | topic>",
  "mode": "raw" | "grounded",

  // RAW → SESSION NODES (each a star; matched sessions clustered around the query)
  "nodes": [{
    "id": "session://<id>",
    "label": title || name || "session",   // HUMAN meaning — NEVER the raw session_id hash (operator-law)
    "weight": hits_in_session,              // node size = match density
    "brightness": score,                    // relevance (0–1) = position/glow
    "status": state,                        // color (supervised-live / closed / …)
    "meaning": snippet,                     // the matched excerpt
    "coordinate": point,                    // {anchor, turn, speaker, ts, heading_path} → drill-in
    "action": primary_verb,                 // the live verb (deliver/wake/queue) → the node's affordance
    "commands": commands                    // launch-ready (projection wires the click)
  }],

  // GROUNDED → THEME/CLAIM CONSTELLATION (2-level: theme star → claim satellites)
  "clusters": [{
    "id": "theme:<i>", "label": theme,
    "claims": [{
      "id": "extraction://<asset>/<chunk_id>",  // ← directly corpus(op='read')-able (the round-trip)
      "label": claim, "kind": kind, "chunk_id": chunk_id
    }]
  }],

  "provenance": { "no_fiction": true, "filter": "semantic", "n_claims": N, "asset": "…" },
  "degraded": (mode_used === "lexical") || (semantic.available === false),  // honest dim-state, never hide
  "note": "…"
}
```

## SEMANTIC NOTES (the meaning behind the fields)
- **Node weight = `hits_in_session`** (how densely a session matched), **brightness/position = `score`**
  (how relevant). Two different signals — a session can match MANY times weakly or ONCE strongly.
- **Labels are HUMAN** (operator-law, [[translate-everything-human-meaning]]): render `title`/`name`/`theme`/
  `claim`, NEVER `session_id` / `chunk_address` / raw addresses. The constellation translates machine→meaning.
- **Every grounded claim id is `extraction://<asset>/<chunk_id>`** → `corpus(op='read', address=…)`-able
  (the drill-in round-trip: click a satellite → read the full extraction record). RAW node `point.chunk_address`
  + `commands` are the session drill-in.
- **`primary_verb` is the LIVE affordance** — the node isn't just shown, it's ACTABLE (deliver to a live
  session, wake a closed one, queue). The constellation is operable, not a static map.
- **Degrade is HONEST, never hidden** ([[no-silent-failures]]): `mode_used==="lexical"` or
  `semantic.available===false` → render a dimmed/flagged state, never a fabricated-confident constellation.
- The two modes are COMPLEMENTARY, not either/or: RAW = "which conversations" (sessions), GROUNDED = "what
  was said" (claims). The transcript-viz surface can offer both lenses over the same query (a toggle / two
  layers of the same constellation).

## EDGES — for a TRUE constellation (relational, not just a positioned node-set)
A constellation archetype is inherently relational; `/api/transcript-search` gives the NODES, but the EDGES
(which sessions/claims relate to which) come from a second recall call DNA can layer in:
- `corpus(op='neighbours', address=<id>, space='extractions', k=N)` → the node-field AROUND any unit, ranked by
  meaning: `{neighbours: [{source, score}, …]}`. Each `source` is itself drillable. So per node, neighbours =
  its edges. `address` = a grounded claim's `extraction://<asset>/<chunk_id>` (grounded mode) or a session
  chunk's `point.chunk_address` (raw mode). `rerank=true`+`text` adds the precision pass.
- This is OPTIONAL — a flat positioned node-field (stars by score) renders without edges. Add neighbours only
  when DNA wants the relational web (the constellation's lines). Flag me and I'll confirm the exact call-shape
  for whichever node type you wire.

## STATUS
- Route LIVE + verified by-use (raw + grounded, the >60s determine timeout gone, ~13s warm). recollection's
  data half of transcript-viz is GO — DNA writes `DNA.faceRecord.transcriptRecord` + the constellation
  archetype → projection clones the SessionDrill host → the surface lights.
- Open to DNA: the exact constellation node schema (I'll adapt the faceRecord to it) + whether to render
  both modes as one toggled constellation or two.
