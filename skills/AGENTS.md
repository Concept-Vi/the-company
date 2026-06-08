---
type: constitution
module: skills
aliases: ["skills — constitution"]
tags: [company, constitution, skills, registry, addresses, cognition]
governs: [C 3b]
relates-to: ["[[Company Map]]", "[[runtime — constitution]]", "[[roles — constitution]]", "[[contracts — constitution]]"]
status: living
---

# skills/ — module constitution

**Is:** the **file-discovered SKILL registry** (Concurrent Cognition C 3b). A **skill** is a declared,
reusable unit of **instructions** — the instructions text a role reads as its INPUT. Skills are a
registry like anything else (Tim, 2026-06-08: "skills/contexts are registries like anything else —
registry-is-truth"): a `skills/` dir, one self-registering `skills/<id>.py` per skill — **exactly
mirroring how roles + node-types self-register** (`roles/` + `runtime/roles.py`; `nodes/` +
`runtime/registry.py`). Adding a skill = adding a file; it self-registers, is queryable, and is
**addressable as `skill://<id>`**; a removed file un-registers on `rediscover`.

**Guarantees:** a skill is **one self-contained declaration** — a module-level `SKILL` dict over the
minimal registry-row schema `{id · content · label · description}`. `id` (MUST equal the file stem)
and `content` (the resolvable value — the instructions a role reads) are required; `label`/`description`
are optional operator-facing fields (like roles have). On drop-in it self-registers
(`SkillRegistry.discover` reads `skills/*.py`) and `skill://<id>` resolves to its `content` — **with no
change to the resolver, the cognition driver, or the UI.**

**The skills (the live set — the drift home; `tests/skills_contexts_acceptance.py` asserts each is reflected here):**
- **`summarize`** — the seed skill: reusable instructions to faithfully condense supplied content
  (keep load-bearing detail + relationships, add nothing, no preamble). The demonstrative first member
  (like `roles/judge.py` was the seed role) — real + usable, so `skill://summarize` resolves to actual
  instructions a role can take as its primary input.

**How it resolves (the address seam — C 3b is its FIRST real extension):** `skill://<id>` is resolved
by `runtime/cognition.py:resolve_address` (the C 3/4 scheme-dispatching seam). It dispatches `skill://`
to `runtime/skills.py:SkillRegistry.read(id)`, which returns the skill's `content`. An UNKNOWN id
RAISES fail-loud (registry-is-truth — never fabricate). A role with `input_addresses=[skill://summarize]`
reads the skill's instructions as its input (via `run_items`/`resolve_address`) — the input-address
intent, fully realised.

**Where new things go:** a new skill = a new file `skills/<id>.py` declaring its `SKILL` dict (its `id`
MUST equal the file name). **Update THIS file** (the drift home) when you add a skill —
`tests/skills_contexts_acceptance.py` fails loud if a discovered skill isn't reflected here (mirrors how
`roles_acceptance` guards roles against `roles/AGENTS.md`).

**Seam:** discovered by `runtime/skills.py:SkillRegistry` (mirrors `runtime/roles.py:RoleRegistry`,
which mirrors `runtime/registry.py:NodeRegistry` — reuse-don't-parallel, the ONE registry pattern);
resolved via `runtime/cognition.py:resolve_address` (the `skill://` dispatch branch); the scheme is
declared additively in `contracts/address.py:SCHEMES`.

**Never:** hardcode a skill in a literal list/dict (this module IS the no-hardcoding rule — the registry
path, never the literal) · fork a second registry pattern (mirror `RoleRegistry`/`NodeRegistry`) ·
resolve an unknown id to anything but a fail-loud RAISE (registry-is-truth, never fabricate) · ship a
skill without reflecting it in this drift home.

## Relates to
- **Discovered by** [[runtime — constitution]] (`runtime/skills.py`, mirroring `runtime/roles.py`).
- **Mirrors** [[roles — constitution]] — the same self-registering, file-discovered, addressable shape.
- **Resolved through** the C 3/4 address seam (`runtime/cognition.py:resolve_address`); the scheme is
  declared in [[contracts — constitution]] (`SCHEMES`).

## Read next
[[Company Map]] · [[roles — constitution]] (the sibling registry this mirrors) · `contexts/AGENTS.md`
(the context registry — same shape, the `context://` scheme).
