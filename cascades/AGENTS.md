---
type: constitution
register: prescriptive
module: cascades
aliases: ["cascades — constitution"]
tags: [company, container, registry, cascades, L3]
status: living
---

# cascades/ — the fan-out registered (④ · L3 · organ-studies/REGISTRY.md)

**What it is.** A's `cascade_registry` re-homed as a **file-per-row** registry beside the engine's other
file-discovered registries (roles/ · mark_types/ · relation_types/ …). Each `cascades/<id>.py` declares a
module-level `CASCADE = {...}` (DATA) **and** a `handle(type_row, ctx)` callable (CODE). `generate_all(type)`
iterates the discovered cascades **by priority** with **per-cascade exception isolation** → honest
`{ok | error | skipped:reason}`. This is "the fan-out itself registered": enable/disable/priority/add-a-row.

**What it must guarantee.**
- Every row's `id` **equals its file stem** (addressable by file); a malformed row FAILS LOUD at discovery.
- A cascade is **pure derivation**: `handle` reads the type row + ctx and returns a DERIVED payload; the
  artifact it produces is recorded as a projection row (`type://<type>/face/<cascade>`), never source.
- **Honesty, not silence**: a cascade whose `requires` face is absent → `skipped:reason`; a `cloud_only`
  cascade whose target isn't present in ④ → `skipped:reason`; a real handler exception → `error` (isolated,
  the loop continues). No cascade silently swallows a hole (the 30-vs-4 count disease REGISTRY.md diagnosed).

**The CASCADE row (schema — `runtime/type_registry.py:CASCADE_FIELDS`).**
- `id` (req) — == file stem.
- `target` (req) — the system this cascade projects into (mcp_tool_registry / notice_board_types / …).
- `priority` (req int) — the run order (A's discipline preserved; low first).
- `requires` (opt list[str]) — the FACE keys the type must declare (presence of a face = `generates[]`
  membership); absent → `skipped`.
- `cloud_only` (opt bool) — the target exists only on the cloud/read side; ④ declines it honestly (skipped).
- `desc` (opt) — operator-facing one-liner.
- plus a module-level `handle(type_row: dict, ctx: dict) -> dict` (the derivation; required for non-cloud rows).

**Where new things go.** A genuinely NEW face = one new `cascades/<name>.py` (a row + a handler) — still
not a new system. **Cascades are CODE-authored (dropping a file), NOT create()-authorable** — the row
carries a callable, which the declarative-direct data-create path cannot serialize (the same line suite.py
draws for lifter/form). A new type is `create(kind='type', spec)`; a new cascade is a file drop + commit.

**Its seam.** `runtime/type_registry.py` (CascadeRegistry + generate_all + completeness) reads this dir;
`Suite.generate_all` / `Suite.type_info` serve the fan-out state to both faces.

**What would violate it.** A hardcoded `CASCADES={...}` literal (must be file-discovered) · a cascade that
mutates source (it derives, one-way) · a cascade that swallows its own failure (must surface error/skip) ·
forking a parallel type/cascade store beside this one (rule 3).

## Agent-authored entries (auto-reflected)
<!-- created live by the create face; one line per entry — keeps the drift-home acceptance green. -->
