# THE MESH — triangulation anchor (a seed, not a plan)

**How to read this:** you are one lens in a triangulating swarm. This anchor is the shared *partial*
picture — held loosely, expected to be corrected. Do NOT confirm it; bring what is actually there.
Nothing here is a task list. Every round of observation is captured back into the substrate this
document describes, so later rounds read earlier rounds — the mesh assembles its own map over time.
Mark evidence: Observed (path/address) / Inferred / Idea. Expansion ratio > 1.

## The problem (Tim, 2026-07-07, verbatim spirit)
"All the equipment and no mesh." Local models, cloud kimis, Claude, OpenAI agents, embeddings,
loadouts, a local supabase ledger, flows, chains, roles, cascades, laws of the object underneath —
but no common memory binding them, no common coordinate space. Things get part-built in one
conversation, then lie dormant forever: **the knowledge had no address, so no future agent could
trip over it.** There is no developer behind the scenes; if the system doesn't remember itself,
nothing does. "There's pockets like that everywhere in the transcripts... I *want* all of it mesh."

## The what-if
What if the mesh is not a new system but THREE RELATIONS laid over what exists —
1. **Common coordinates** — one address per thing, any scheme (code:// exchange:// ui:// run://
   skill:// guide:// decision:// project:// board:// cap:// ...). contracts/address.py is the spine.
2. **Common memory** — every agent (any model, any provider) reads/writes the SAME substrate:
   the corpus spaces, converging into the local supabase ledger (precedent: recollection's 6983
   exchange embeddings already landed there as space='exchange' — "the merge-intention spine").
3. **Self-reference** — the mesh's own description (laws, guides, registries, THIS document, every
   observation the swarm makes) lives IN the mesh as addressed records. "What exists?" becomes a
   query, never a lost transcript pocket.

And what if it is GENERATIVE: kimi-class coders operating in address space can fan out and build
the mesh's own missing pieces, because a common coordinate space means the swarm composes instead
of colliding. The loop that mined "why does recall exist" (design_intent space, 2026-07-07) is the
same loop that finds dormant pockets — and a found pocket with an address is a build candidate.

## The method (the inversion — Tim's correction, 2026-07-07)
NOT plan-and-dispatch. **Triangulation over time:** seed → open lenses over territories → capture →
a triangulation pass reads ALL observations + the prior synthesis → convergences, contradictions,
dormant finds, and the NEXT territories → repeat. The territories are chosen by the previous round,
not by a planner. Local models observe (free), kimi triangulates (cheap), Claude tends the loop.
Deterministic work to code (material-gathering, address-verification); judgment to models.

## What is already real (verified pieces the mesh binds — Observed)
- Address schemes: contracts/address.py (scheme()). Corpus records keyed by source_address.
- Substrate: .data/store corpus + spaces (repo 1292 · history 2928 · design_intent, growing ·
  extractions · exchange in the postgres ledger :15432). Embedder pplx :8007 + reranker :8008 (@recall).
- Cognition: roles/ registry (file-discovered, self-authoring via create) · run_role/run_items/
  run_reduce/run_cascade · flows (transcript_mine, repo_ingest, drift_radar, floor_walk...) ·
  models_for_role (22 models: local vLLM + ollama-cloud kimis + more).
- The archaeology instrument: mine_design_intent (kimi-bound) + archaeology_mine.py driver +
  design_intent projection — the first strand, running.
- Laws circuit: operator(op='rules') propose→confirm registry — where mined laws become standing.
- Loadouts: services.json combos (@recall, @interaction-fp8...) — the resource half of the mesh.
- Guides: author_guide (grounded-only) — the self-description half, barely used.

## The honest hard parts (where a lens should press)
- Are there actually THREE address notions that don't unify (contracts/address.py vs corpus
  source_address free-strings vs ui:// registry)? Where does an address break?
- Supersession semantics: same source_address + projection — when do rounds DEEPEN vs CLOBBER?
- The supabase ledger vs .data/store: which is the mesh substrate of record, what migrates, what dies?
- connects_to are candidate-mentions, not verified addresses (measured 2026-07-07) — the cross-link
  needs a deterministic verify floor.
- Dormant ≠ dead: some pockets were deliberately parked (condition-addressed deferral law). The
  dormancy dragnet must distinguish, not flatten.

## Open what-ifs
- What if every registry (roles, flows, services, marks, skills) auto-captures into the corpus, so
  the mesh's map is a side-effect of existing, not a maintained document?
- What if the triangulation ROUNDS themselves are addressed (mesh://round/N) and the synthesis is
  the mesh's growing self-model — readable by any agent at session start?
- What if "loadout" generalizes: a mesh-loadout = models + spaces + roles for a kind of work?

**Spirit note to every lens:** bring back what is THERE — the half-built, the dormant, the
surprising, the contradicting. The "yes, but actually..." is the gold. You are not confirming a
design; you are helping a system see itself for the first time.
