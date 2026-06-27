---
type: constitution
register: prescriptive
module: contexts
aliases: ["contexts — constitution"]
tags: [company, constitution, contexts, registry, addresses, cognition]
governs: [C 3b]
relates-to: ["[[Company Map]]", "[[runtime — constitution]]", "[[roles — constitution]]", "[[contracts — constitution]]"]
status: living
---

# contexts/ — module constitution

**Is:** the **file-discovered CONTEXT registry** (Concurrent Cognition C 3b). A **context** is a
declared, reusable unit of **context** — a context blob a role reads as its INPUT (distinct from a
skill, which is reusable *instructions*). Contexts are a registry like anything else (Tim, 2026-06-08:
"skills/contexts are registries like anything else — registry-is-truth"): a `contexts/` dir, one
self-registering `contexts/<id>.py` per context — **exactly mirroring how skills + roles + node-types
self-register**. Adding a context = adding a file; it self-registers, is queryable, and is
**addressable as `context://<id>`**; a removed file un-registers on `rediscover`.

**Guarantees:** a context is **one self-contained declaration** — a module-level `CONTEXT` dict over
the same minimal registry-row schema as a skill `{id · content · label · description}`. `id` (MUST
equal the file stem) and `content` (the resolvable value — the context blob a role reads) are required;
`label`/`description` are optional. On drop-in it self-registers (`ContextRegistry.discover` reads
`contexts/*.py`) and `context://<id>` resolves to its `content` — **with no change to the resolver, the
cognition driver, or the UI.**

**The contexts (the live set — the drift home; `tests/skills_contexts_acceptance.py` asserts each is reflected here):**
- **`company_overview`** — the seed context: a reusable one-paragraph frame of what the Company is
  (identity-coupled, Commander-directed, recursive, registry-driven, layered cognition). The
  demonstrative first member — real + usable, so `context://company_overview` resolves to actual
  content a role can take as its input.

**How it resolves (the address seam — C 3b is its FIRST real extension):** `context://<id>` is resolved
by `runtime/cognition.py:resolve_address` (the C 3/4 scheme-dispatching seam). It dispatches `context://`
to `runtime/skills.py:ContextRegistry.read(id)`, which returns the context's `content`. An UNKNOWN id
RAISES fail-loud (registry-is-truth — never fabricate). A role with
`input_addresses=[context://company_overview]` reads the context blob as its input (via
`run_items`/`resolve_address`) — the input-address intent, fully realised.

**Where new things go:** a new context = a new file `contexts/<id>.py` declaring its `CONTEXT` dict
(its `id` MUST equal the file name). **Update THIS file** (the drift home) when you add a context —
`tests/skills_contexts_acceptance.py` fails loud if a discovered context isn't reflected here.

**Seam:** discovered by `runtime/skills.py:ContextRegistry` (mirrors `runtime/roles.py:RoleRegistry` —
reuse-don't-parallel, the ONE registry pattern; SkillRegistry + ContextRegistry share one base, two
vocabularies); resolved via `runtime/cognition.py:resolve_address` (the `context://` dispatch branch);
the scheme is declared additively in `contracts/address.py:SCHEMES`.

**Never:** hardcode a context in a literal list/dict (this module IS the no-hardcoding rule — the
registry path, never the literal) · fork a second registry pattern (mirror `RoleRegistry`) · resolve an
unknown id to anything but a fail-loud RAISE (registry-is-truth) · ship a context without reflecting it
in this drift home.

## Relates to
- **Discovered by** [[runtime — constitution]] (`runtime/skills.py:ContextRegistry`).
- **Mirrors** [[roles — constitution]] + `skills/AGENTS.md` — the same self-registering, file-discovered,
  addressable shape (the skill registry's sibling: same machinery, the `context://` vocabulary).
- **Resolved through** the C 3/4 address seam; the scheme is declared in [[contracts — constitution]].

## Read next
[[Company Map]] · `skills/AGENTS.md` (the sibling registry — same shape, the `skill://` scheme) ·
[[roles — constitution]] (the registry pattern both mirror).
