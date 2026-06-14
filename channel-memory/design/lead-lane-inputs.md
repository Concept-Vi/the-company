---
trust: fabric-derived
author: ch-al7jdfdr (lead, session bda8ce28)
date: 2026-06-14
verified: design-input — proposed answers grounded in Tim's history/preferences (the get-a-feel pass), for Tim to react to
relates: [vision/2026-06-14-session-splicing-and-channel-memory.md, COMMIT-GRAMMAR.md]
---
# Lead-lane inputs to the full design-plan (A–D)

My sections for the fork's plan. Each proposed answer cites the evidence it's drawn from (Tim's
direct words this session + standing preference-memory) so Tim reacts to grounded proposals, not
cold questions. PROPOSED — Tim's to confirm/correct.

## A. Multi-channel membership + management model (my lane: channels)
**Tim-direct (2026-06-14):** "multiple different channels … a create channel and a managed channel
… members added and removed [to] different channels." + "no wrapper — the flag just runs at launch."
+ "registering themselves … still a hook … describing themselves so … profiles."
**Proposed model (one structure for members ↔ channels ↔ transport):**
- A **channel** = a named, managed group with a member set + attached context (§C) + a coordinator.
  Maps onto the Company's existing `channels`/`channel_act` concept (named persistent groups) — REUSE
  it, don't fork (grounding: no-hardcoding / registry-is-truth; the fabric already has channels).
- **Membership is a registry**, not ad-hoc handles: `cc_channel` gains create / list / add-member /
  remove-member / archive. A session or a supervised clone can belong to several channels at once.
- **A member is reached by its transport** (the unified-transport, Tim-approved "notify"): a member
  row carries `transport: channel|supervised`; push dispatches per-member (HTTP to a live channel
  session's port, or supervisor /inject to a clone). One broadcast fans across mixed members; replies
  aggregate by channel thread (grounding: my unified-transport design 5fdd41b, now approved).
- **Join = the launch flag, full stop** (no wrapper — Tim corrected me): `claude --mcp-config
  channels/channel.mcp.json --dangerously-load-development-channels server:company-channel`. The CLI
  capability is already in the dynamic registry; nothing wraps it.
- **Profile via a SessionStart HOOK** (Tim's correction): on start, a session writes a PROFILE
  (handle, cwd, model, a self-description of what it's working on) to the registry, so listing members
  shows rich profiles, not the thin one-line announce. The hook is identity/profile; the launch flag
  is transport. (Boundary: Tim applies the global hook — an agent can't self-edit startup config.)
- **Notify-each** (Tim's "approve but notify"): when an agent pulls a clone into a channel, emit a
  Notice to Tim's inbox.

## B. Multi-project / multi-session addressing (gates indexing more sessions — Tim flagged to me)
**Tim-direct:** "heaps of different sessions … heaps of different projects … all in one source … search
across a project, across one session, across a segment … set a session to be the default recall."
**Model — UPDATED to Tim-direct D-1 (multi-space, supersedes the earlier hierarchy-keying wording):**
- **Multi-space coordinate addressing** (canonical decision #1, tim-direct): a unit has a REAL address
  in EVERY relevant space at once — provenance/structural, semantic (per-lens embedding position),
  temporal, physical (filesystem), relational (links) — as **co-equal coordinate spaces**. **Provenance
  (`exchange://<sid>/<i>`) is the re-embed-stable CANONICAL IDENTITY** (semantic coords move on an
  embedder swap; provenance doesn't), and the embedding lattice is **ONE co-equal space, not the
  master container**. "Having an address in many spaces is the value — find via one, cross to the
  others." The UI renders the space (the Heart). [[both-plus-others]] — not lattice-vs-provenance, both.
- The session store IS the source (the CLI-discovery precedent / Mirror-Registry Law); within the
  PROVENANCE space its discrete axes are **project · session · segment** (a segment = a compaction
  generation, the structural `isCompactSummary` boundary, per the schema find) — these are the
  structural sub-space of the multi-space address, NOT a competing hierarchy model.
- Address grammar: `session://<project>/<sid>` and a recall scope selector `{scope: project|session|
  segment|all, project?, sid?, segment?}`. The project key = the `~/.claude/projects/<encoded-cwd>/`
  dir (encoding verified: `/`→`-`, `.`→`-`; resolve by re-encoding, never trust a decode — from
  session_pointintime.resume_cwd_for).
- **Default-recall** = a setting (a `default_recall` row: which session/project recall targets when no
  scope is given). Grounding: registry-driven + configurable-by-default (Tim's standing pattern).
- **Indexing gate (the reason this is first):** index per-(project,session) with the scope keys
  embedded, so a query can filter scope WITHOUT re-embedding. Pick ONE embedder space per index (the
  golden rule — pplx-4b is the decision); never mix spaces. Don't index more sessions until this
  keying is locked (Tim's explicit gate).

## C. Channel-attachment (sessions + docs as loadable context for a channel's members)
**Tim-direct:** "link … recall and semantics to channels" + (the relayed §5) "attach sessions + docs
to a channel as a loadable rule/context-set for agents that join."
**Proposed model:**
- A channel row carries an **attachments manifest**: `{sessions: [session://…], docs: [path…],
  recall_scope: {…}}`. On join, a member is handed the manifest as context (the channel's
  rule/context-set) — and can run **recall scoped to the channel** ("what did we decide about X" over
  the channel's attached sessions).
- Mechanism: reuse the channel push — on add-member, inject a `<channel>` context-load message
  pointing at the manifest + the recall scope; the member loads it. Recall-as-a-channel-capability =
  a `cc_channel op=recall {channel, query}` that runs the scoped recall (§B scope = the channel's
  attached sessions) through the served embed+rerank. Grounding: the Heart (channels are projections
  of addressed state; attachments are addresses) + recall-usable-by-agents (Tim's standing requirement).

## D. The extractor PANEL — build ON the existing cognition path, NOT parallel (the fork's (c))
**Verified (this session):** `runtime/cognition.py` already has `run_role(role, ctx)` + concurrency
(ThreadPoolExecutor / `concurrency_probe` fires N concurrent role-runs) + structured output
(`json=True` → response_format). `roles/` ALREADY embodies the extraction-vs-judgment split — extract
roles (`mine_exchange`, `eval_classify`, `ground`, `interpret_file`) + judge roles (`judge`,
`judge_mining`, `judge_drift`). Small models for the panel: **chat-4b** (Qwen3.5-4B, the 32-concurrency
swarm worker, :8000), **chat-2b** (:8003), **chat-08b** (ultra-concurrency, :8006).
**Proposed:** the "panel" = concurrent `run_role(<facet-extract role>)` on chat-4b/08b (each extracts
ONE facet — chosen / alternatives / reason / constraints / owner — structured output ONLY, never
judges), chained into a single `run_role(<judge role>)` on a smarter seat (chat-nemotron-30B or a
cloud seat) that JUDGES. This IS the Company's concurrent-cognition pattern + the extraction-vs-judgment
law ([[feedback-extraction-vs-judgment]]: small models extract, central smart model judges; never let
fan-out workers decide) + dataflow-not-agents ([[feedback-not-agent-architecture-by-default]]). So the
fork builds NEW facet-extract + judge ROLES (roles/*.py) + a chain — NOT new infrastructure. Reuse
run_role/run_swarm + the roles registry.

## Cross-cutting grounding (the get-a-feel evidence)
Registry-driven + no-hardcoding everywhere; reuse don't reinvent (the fabric's own channels concept,
the cognition engine); configurable-by-default; the Heart (UI/recall/channels = projections of one
addressed state → the scan output must be DATA, §1.9); extraction-vs-judgment; verify-on-structure-
not-text (the triply-confirmed law this session). These are Tim's established patterns the proposed
answers lean on — cite them when bringing the plan so he reacts to grounded inferences.
