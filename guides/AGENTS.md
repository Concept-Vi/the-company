---
type: constitution
register: prescriptive
module: guides
aliases: ["guides — constitution"]
tags: [company, constitution, guides, registry, addresses, cognition, self-documentation]
governs: [C 3b]
relates-to: ["[[Company Map]]", "[[runtime — constitution]]", "[[skills — constitution]]", "[[contracts — constitution]]"]
status: living
---

# guides/ — module constitution

**Is:** the **file-discovered GUIDE registry** — the **narrative-guide face** of "one entry, two
faces" (Tim, 2026-06-28). A **guide** is a declared, reusable unit of **narrative how-to**: the prose
a human/agent reads to LEARN a part of the system. It is the SECOND face beside the SKILL
(`[[skills — constitution]]`): a skill is the dense INSTRUCTION-unit a role reads mid-task
(`skill://<id>`); a guide is the how-to a learner reads (`guide://<id>`). Both are projections OF a
target — NOT two bodies in one file (the 3-review verdict, 2026-06-27: co-locating them would be two
homes sharing a filename → drift). A guide holds only REFERENCES to its sources (`grounded_from`),
never a copy — one-home satisfied.

**Guarantees:** a guide is **one self-contained declaration** — a module-level `GUIDE` dict over the
schema `{id · content · target · grounded_from · source_hash? · label? · description?}`.
`id` (MUST equal the file stem), `content` (the narrative the address resolves TO), `target` (the
address the guide documents — a guide is ABOUT something), and `grounded_from` (a NON-EMPTY list of
source addresses — the **mandatory-grounding gate**: a guide is authored FROM real sources or it does
not exist) are required; `source_hash` (freshness), `label`, `description` are optional. On drop-in it
self-registers (`GuideRegistry.discover` reads `guides/*.py`) and `guide://<id>` resolves to its
`content` — **with no change to the resolver beyond its dispatch branch**.

**The carrier rule (review [A4]):** a guide attaches to a **non-obvious-use system / capability /
domain**, NOT to an operational role-input. `summarize` does not need a how-to; the *skills system*
does. Pick targets that a newcomer would otherwise have to reverse-engineer.

**Freshness (the practice):** `source_hash` is a content hash of `grounded_from` at authoring time.
When the sources change, the hash differs → the guide is STALE and due a re-author. (Reuses the
hash-diff IDEA, deliberately NOT the embedding-reconcile function in `runtime/freshness.py` — which is
the open no-auto-reindex concern.) A future `guide`-author re-authors on a source-hash delta, never on
run-churn, and PROPOSES a diff over human-edited guides rather than clobbering them.

**The guides (the live set — the drift home; `tests/guides_acceptance.py` asserts each is reflected here):**
- **`using_skills`** — the SEED guide (the demonstrative first member). Documents the SKILL registry
  (`target: skill://summarize`): what a skill is, when to add one, the only steps to add one, the
  worked example, and the schema gotchas. Grounded in `skill://summarize` + `skills/AGENTS.md` +
  `runtime/skills.py` (all real). `guide://using_skills` resolves to that how-to. Proof the registry
  is real + usable, like `skill://summarize` was for skills.

**How it resolves (the address seam):** `guide://<id>` is resolved by
`runtime/cognition.py:resolve_address` (the C 3/4 scheme-dispatching seam), which dispatches `guide://`
to `runtime/guides.py:GuideRegistry.read(id)`, returning the guide's `content`. An UNKNOWN id RAISES
fail-loud (registry-is-truth, never fabricate).

**Where new things go:** a new guide = a new file `guides/<id>.py` declaring its `GUIDE` dict (its `id`
MUST equal the file name). **Update THIS file** (the drift home) when you add a guide —
`tests/guides_acceptance.py` fails loud if a discovered guide isn't reflected here (mirrors
`skills_contexts_acceptance.py`).

**Seam:** discovered by `runtime/guides.py:GuideRegistry` (mirrors `runtime/skills.py:SkillRegistry`,
reusing its `_load_module` importlib helper — reuse-don't-parallel, the ONE registry mechanism, own
schema like roles/nodes); resolved via `runtime/cognition.py:resolve_address` (the `guide://` dispatch
branch); the scheme is declared additively in `contracts/address.py:SCHEMES`.

**Never:** hardcode a guide in a literal list/dict (this module IS the no-hardcoding rule — the
registry path, never the literal) · fork a second registry mechanism (mirror `SkillRegistry`) · resolve
an unknown id to anything but a fail-loud RAISE · author an UNGROUNDED guide (empty `grounded_from`
RAISES — a guide is true-by-construction or it does not exist) · stuff narrative into a skill's
`content` (that is this registry's job) · ship a guide without reflecting it in this drift home.

## Relates to
- **Discovered by** [[runtime — constitution]] (`runtime/guides.py`, mirroring `runtime/skills.py`).
- **The other face of** [[skills — constitution]] — skill:// (instruction-unit) + guide:// (narrative) are
  two projections of a target.
- **Resolved through** the C 3/4 address seam (`runtime/cognition.py:resolve_address`); the scheme is
  declared in [[contracts — constitution]] (`SCHEMES`).

## Read next
[[Company Map]] · [[skills — constitution]] (the sibling registry this is the second face of) ·
`contexts/AGENTS.md` (the context registry — same shape, the `context://` scheme).

## Agent-authored entries (auto-reflected)
- **`using_patterned_visibility`** — agent-authored guide (created via the declarative-direct face). 
<!-- created live by the create face; one line per entry — keeps the
     drift-home acceptance green; refine the prose by integration. -->
- **`using_corpus_pipeline`** — agent-authored guide (created via the declarative-direct face). 
