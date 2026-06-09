# Registry-Generation Chain — Research Synthesis (what EXISTS to build ON)

> The evidence base for the V-A loop (the swarm reads the surface → grows the address registry). Grounded on
> `main` 2026-06-09 (guided-review session, "full charge" loop-prep; cognition runs a parallel loop to bolster).
> Provenance marks: **Observed(file)** = verified on main this session · **Verified-by-use** = ran it ·
> **Inferred** = pattern, not yet run. The chain is almost ALL reuse — the net-new is one role + the extract +
> the proposal write-back. Read this first; the Completion-Criteria carries the bar, the Guide the how.

## 0 · The problem this closes (the gap, measured)
- **Observed:** 23 mockups · `addresses.json` = **82** registered `ui://` addresses · only **102** `data-ui-ref`
  attributes across ALL mockups. A single mockup (C1-inbox) has **131 elements, 3 addressed**. So ~3000 mockup
  elements exist; ~100 are addressable. Clicking an un-registered element → the RHM has no dossier (V-B made it
  describe-from-HTML as the floor; V-A fills the registry so it resolves richly).
- **The registry entry IS the junction** (Observed `addresses.json`): `{represents, code, howto{what/can-do/
  how-to-change}, capabilities}`. That dossier is what makes a clicked element explain itself at altitude.

## 1 · The engine primitives the chain REUSES (all Observed on main — net-new is tiny)
- **`run_items`** (Observed `runtime/cognition.py`) — ONE role × N input-units, concurrent on the swarm. THE map.
  The N units = the candidate elements. This is the axis-inversion the engine added FOR corpus-chains.
- **`run_reduce`** (Observed cognition.py; **cluster mode** present — 8 refs) — the cross-unit join. Three modes:
  `role` (a join role merges), `rule` (pure L2 verdict), **`cluster`** (embed-dedup: "which of these are the
  same?" via `nodes/retrieve._cosine`). The dedup-across-mockups job IS cluster mode.
- **`run_role`** (Observed) — fire one role over one input (the per-mockup screen_reader ground pass).
- **`save_cascade`/`run_cascade`/`list_cascades`** (Observed `runtime/suite.py`; cognition `91dbee8` "saved chains
  become re-runnable") — ★ **the whole chain can BE a declared, re-runnable cascade** (registry-is-truth: the
  pipeline is data in the ActionRegistry, not hardcoded orchestration; re-run when mockups change). Reuses
  `build_action` validator — no 2nd registry. The `run://` resolver wires step output → next step input.
- **`screen_reader` role** (Observed `roles/screen_reader.py`, built this session) — mockup HTML → at-altitude
  `{what_this_is, what_you_can_do}`. The step-1 GROUND pass (per mockup).
- **`design/_system/parse.py`** (Observed) — already parses mockups for `data-ui-ref`/element structure → the
  EXTRACT source (extend it to emit the candidate-element units; do NOT write a parallel parser).
- **`design/_system/addresses.json`** (Observed, 82) + **`corpus-meta.json`** (Observed, my Q2 — mockup→ui://
  base map) — the registry to grow + the base-address each mockup's elements nest under.
- **governance inbox / surface** (Observed `runtime/governance.py`, 21 surface refs) — the PROPOSE→operator floor:
  proposed entries surface as a review decision; Tim approves once (simple-consent); only then written.
- **`design/_system/refcheck.py`** (Observed) — code-ref ground-truth: the CONFIRM step checks a proposed entry's
  `code` ref actually resolves (no fiction).
- **Feature & Function Inventory** (the no-fiction ground truth — the register role's context so it never invents
  a capability; un-built element → marked `proposed`, the live-vs-proposed distinction Tim set).

## 2 · The net-new (small, and split clean across the two parallel loops)
- **NEW role `register_element`** (`roles/register_element.py`) — element snippet + context → a proposed dossier.
  COGNITION's lane (roles/ is the C seam; mirrors screen_reader). Op:generate. *Net-new: one role file.*
- **EXTRACT** — extend `parse.py` to emit candidate-element units (text/html/path/tag/ancestor/base). MINE
  (design/_system). *Net-new: a parser pass + a filter for "meaningful".*
- **The cascade definition** — declare extract→ground→map→reduce→confirm as a saved cascade. JOINT (uses the
  engine; the definition is data). *Net-new: a cascade spec (data).*
- **The PROPOSAL write-back** — proposed entries → governance surface → on approve, merge into addresses.json +
  stamp `data-ui-ref` into the mockups + re-run parse.py. MINE (the surface + the write-back + the round-trip).
  *Net-new: the merge/stamp + the batch-review surface.*
- **The CONFIRM jury** — a stronger-model/refcheck pass over the reconciled set. JOINT (engine `run_jury` +
  refcheck). *Net-new: the confirm role/rule + threshold.*

## 3 · The reuse-not-parallel guards (the laws this chain must not break)
- NO parallel registry — grow `addresses.json` (the one truth); NO parallel parser — extend `parse.py`; NO
  parallel chain-runner — use `run_cascade`; NO hand-orchestration — declare the cascade as data.
- **Operator-only floor:** nothing auto-writes the registry — every entry is PROPOSED, Tim approves (governance).
- **No-fiction:** the register role's context MUST include the feature inventory + the parent dossier + the
  mockup summary; un-built → `proposed`, never invented capability.
- **Introspective-data:** each proposed entry carries provenance (which `run://`, model, confidence).

## 4 · The cross-lane split (why a parallel cognition loop bolsters this)
- **MINE (guided-review):** EXTRACT (parse.py pass), the cascade spec (data), the PROPOSAL surface + write-back +
  parse.py round-trip, the end-to-end verify, the FE that shows proposals + the approve gate.
- **COGNITION's (parallel loop):** the `register_element` role (+ the confirm role/jury), any engine-primitive
  gap the chain exposes (run_items over an element corpus at this N, cluster-dedup tuning, the run:// wiring),
  the cognition-side of the cascade.
- **JOINT:** the cascade composition + the whole-chain by-use (a real run: mockups → proposed entries → approve →
  registry grows → a previously-dead element now resolves). The convergence-round verifies the seam.
- This is exactly the corpus-chain the engine was generalized for — cognition owns the engine/role depth, I own
  the surface + the registry round-trip; the two loops meet at the cascade.
