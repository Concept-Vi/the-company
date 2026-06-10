---
type: constitution
module: flows
aliases: ["flows — constitution"]
tags: [company, constitution, flows, registry, cognition]
governs: [GC1, GC2]
relates-to: ["[[Company Map]]", "[[runtime — constitution]]", "[[roles — constitution]]"]
status: living
---

# flows/ — module constitution

**Is:** the **file-discovered FLOW registry** (GC1). A flow is a registered, multi-primitive
PRODUCTION LINE — committed code composing the engine's primitives into a proven, re-runnable chain,
invocable through the company MCP by name with declared params. Born from the GC1 evidence (2026-06-10):
agents rebuild chains UNGROUNDED when the proven chain isn't the easiest path — a flow row makes the
grounded chain ONE call.

**The law (the floor's executable-code half):** a flow is AUTHORED in the repo (reviewed, committed),
never through the MCP; it is INVOKED through the MCP (`flows` tool: op=list|describe|run); it
PROPOSES ONLY (`proposes_only: True` enforced at discovery — compute, artifacts, corpus writes,
surface_review; never resolve/approve/dispatch/claude -p; flows/*.py is scanned by the floor's
source-invariant). Declarative chains are NOT flows — they go through save_cascade.

**Row shape:** `flows/<id>.py` with a module-level `FLOW` dict ({id==stem, label, description,
params:{name:{desc,default}}, proposes_only:True}) + a module-level `run(**params)`.
Add a row = add a FILE + reflect it here (the drift home). Loader: `runtime/flows.py`.

## The rows

- **registry_generation** — the grounded mockup→dossier chain (GC2's proven instance): GROUND → MAP
  (full context package) → cluster-dedupe → floor+jury CONFIRM; resume-safe batches; proposes
  per-mockup artifacts toward the operator's APPROVE gate.
- **transcript_mine** — ③/G23: dialogue transcripts → distilled exchange extracts, embedded into
  space='history' (durable memory); exchange-granular idempotent; bounded batches.
- **pattern_cluster** — ③/G13: the self-study REDUCE — tally + embed-cluster every mined pattern_tag
  into named weighted groups; feeds G13-PATTERN-REPORT.md.
