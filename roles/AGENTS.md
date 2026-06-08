---
type: constitution
module: roles
aliases: ["roles — constitution"]
tags: [company, constitution, roles, cognition, role-registry]
governs: [C2.1, C2.2, C2.3, C2.4, C2.5]
relates-to: ["[[Company Map]]", "[[runtime — constitution]]", "[[nodes — constitution]]", "[[fabric — constitution]]"]
status: living
---

# roles/ — module constitution

**Is:** the **file-discovered role registry** of the collective cognition (Concurrent Cognition G2). A
**role** is a named model-FUNCTION — a specific job done by a model that is not (necessarily) the
conversational brain. Roles were two hardcoded things before G2 (`suite.py`'s one-entry `ROLE_REGISTRY`
class dict + `cognition.py`'s inline `SPIKE_ROLES`); G2 promotes both into ONE registry: a `roles/` dir,
one self-registering `roles/<id>.py` per role — **exactly mirroring how node-types self-register**
(`nodes/` + `runtime/registry.py`). Adding a role = adding a file; it self-registers + is queryable; a
removed file un-registers on `rediscover`.

**Guarantees:** a role is **one self-contained declaration** — a module-level `ROLE` dict over the C2.1
superset schema `{id · label · description · prompt_template · output_schema · input_addresses · op · trigger
· model_binding · mode_scope · rules · render_hint · draws · verdict_rule · knobs · …}`. Every field
except `id` is OPTIONAL, and a role's **facet follows which fields are populated**:
`prompt_template`+`output_schema` ⇒ a **generate** role can **fire** (`run_role`/`run_swarm`); `op:embed`
⇒ an **embed** role fires the vector path (no prompt/schema needed — `complete_embeddings`, local
embedder only); `mode_scope` ⇒ it is in that mode's **cast**; `draws` ⇒ it is a **jury** (N varied draws
+ a pure verdict_rule). The **op-axis** (`op: generate|embed`, default `generate`) declares the role's
OPERATION as data — today's every role is `generate` (byte-identical). On drop-in it
self-registers (`RoleRegistry.discover` reads `roles/*.py`) and is queryable
(`cast_for_mode`/`fireable`/`juries`) — **with no change to the cognition driver, suite, or UI.**
Roles fire model calls through `fabric/` guards (a model runs only INSIDE a role — L2).

**The registry is the single source (C2.1):** `runtime/roles.py` `RoleRegistry` mirrors
`runtime/registry.py` `NodeRegistry` (`discover`/`rediscover`/`register`); `suite.py` builds
`ROLE_REGISTRY = {id: role.spec}` from it (so `resolve_role`/`roles()` read the SAME dict-view), and
`cognition.py` sources `SPIKE_ROLES` from it. No second role notion, no fork.

**The roles (the live set — the drift home; `tests/roles_acceptance.py` asserts each is reflected here):**
- **`judge`** — role #0, the finished-thought judge (the voice circuit's semantic endpoint). Config-only:
  declares NO `prompt_template`/`mode_scope`/`draws` → fires via `is_finished_thought`, not the swarm; in
  no cast; not a jury. Moved here from suite.py UNCHANGED IN BEHAVIOUR (C2.2 — byte-identical binding).
- The **`listening` cast (C2.3 — DECISIONS Batch 3 Q1, the first locked cast):**
  - **`focus`** — the selector: utterance → intent + which auxiliary roles to fire (gates the cast).
  - **`recall`** — memory: utterance (+memory) → a past-context snippet + whether it is relevant to inject.
  - **`ground`** — citable facts: live state → whether in scope + a grounding note (gates recall's inject).
  - **`connect`** — a link: topic+thread → a related thread/decision worth surfacing.
  - **`check`** — contradiction: a forming answer vs ground → does it contradict? (CHAINS after a part
    starts — its dependency is declared as DATA; the chaining executor is G3/G4).
  - **`voice`** — tone: persona+answer → the toned phrasing (the cognition role, not the TTS module).
- **`verify_jury`** — the canonical **jury** (C2.4): `draws:3` + a pure majority-vote `verdict_rule`. In no
  cast (fired explicitly via `run_jury`). **⚠ E4 caveat:** N draws on ONE model are correlated (variance,
  not independent error) — a correctness-jury that matters needs model diversity; the verdict_rule shape
  accepts a future 2nd-model/cloud tiebreak. v1 single-model, limit documented.
- **`reduce_synth`** — the demonstrative **reduce-role** (C 2/4): the `reduce-tree` THOUGHT_SHAPE's declared
  `join` role made real — `op:generate`, takes the N map-output notes (composed by `run_reduce` into one
  `"notes"` input via the C 1/4 input-axis) → ONE merged `{summary}`. In no cast (fired explicitly via
  `run_reduce(mode="role")`, the cross-unit synthesize join — `runtime/cognition.py:run_reduce`). The
  reduce DRIVER also offers `mode="rule"` (a pure L2 verdict over the N values, mirroring `run_jury`) and
  `mode="cluster"` (the embed-cluster "which of these are the same" discovery join, reusing
  `nodes/retrieve._cosine`).

**Where new things go:** a new role = a new file `roles/<id>.py` declaring its `ROLE` dict (its `id`
MUST equal the file name). Put it in a mode's cast by adding that mode to its `mode_scope`. Make it a
jury by declaring `draws:N` + a `verdict_rule`.

**To extend:** declare the `ROLE` dict, drop it in. That's the whole self-extending path. **Update THIS
file** (the drift home) when you add a role — `tests/roles_acceptance.py` fails loud if a discovered
role isn't reflected here (mirrors how `edge_kinds_acceptance` guards `EDGE_KINDS` against
`contracts/AGENTS.md`).

**Seam:** discovered by `runtime/roles.py:RoleRegistry`; consumed by `runtime/suite.py` (`resolve_role`/
`roles()`/`cast_for_mode`/`resolve_role_binding`) and the cognition driver `runtime/cognition.py`
(`run_role`/`run_swarm`/`run_jury`). C2.5 binding: `role.requires ⊆ provider.provides`
(`runtime/roles.py:model_satisfies`/`resolve_binding`) against `Suite.capability_providers()` — a thin
seam G8/L-model will populate with the full capability catalog (the downstream dep).

**Never:** hardcode a role in a class dict (the thing G2 retired) · fork a second registry pattern (mirror
`NodeRegistry`, reuse-don't-parallel) · run a model inside a *rule* (a model runs only inside a *role*; a
routing/verdict rule is a pure declared function — L2) · let a role emit `resolve`/`approve`/`dispatch`
(the `claude -p`/build-dispatch floor is lead-only) · ship a role without reflecting it in this drift home.

## Relates to
- **Discovered by** [[runtime — constitution]] (`runtime/roles.py`, mirroring `runtime/registry.py`) and
  **consumed by** the cognition driver + the Suite.
- **Uses** [[fabric — constitution]] — a role's model call passes through its guards (validate/retry).
- **Mirrors** [[nodes — constitution]] — the same self-registering, file-discovered, queryable shape.

## Read next
[[Company Map]] (the whole picture) · [[runtime — constitution]] (what fires these) · the triad at
`build-prep/concurrent-cognition/` (the G2 criteria + guide).
