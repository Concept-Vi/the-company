# R1 — Consistency & Laws Review (READ-ONLY)

*Plan-review pass 1. Checks the Concurrent Cognition triad (Completion Criteria · Implementation Guide · Research Synthesis) + DECISIONS.md against the repo's governing docs (`AGENTS.md` rules 1–10, `MAP.md`, `STATE.md`, module constitutions, `contracts/*.py`) and standing constraints in MEMORY. Findings lead with CONTRADICTIONS and GAPS; confirmations are compressed into a table at the end. Source: `/home/tim/company-cognition`, branch `concurrent-cognition`, 2026-06-07.*

---

## CONTRADICTIONS (resolve before building)

### X1 — `swarm://` vs `run://`: the plan contradicts its own recorded decision and the address contract
The triad uses **two different address schemes for the same thing** (a role's per-turn output).

- **Implementation Guide principle 3 + C4.2** (Criteria) treat `swarm://<turn>/<role>` as a *resolvable* address, resolved through the existing `_chat_context → _resolve_context_at` path.
- **G7** (Criteria C7.2 + Guide G7) uses `run://<turn>/<role>` for the same role instances ("reuse `run://`, don't mint `cog://`").
- **DECISIONS.md** (Carried dev-calls) explicitly says: *"default **reuse `run://<turn>/<role>`**, don't mint `cog://` unless a contract reason emerges (rule-8: never invent a contract lightly)."*

**Contract evidence:** `contracts/address.py:32` — `SCHEMES = ("run", "cas", "blob", "vec", "ui", "code")`. **`swarm` is NOT a registered scheme.** `scheme(addr)` (line 51) returns `None` for any `swarm://` string, and `_resolve_context_at` resolves only store-backed schemes (`run`/`cas`/`blob`/`vec`). A literal `swarm://` address would not resolve through the path the Guide names.

**Law consequences:**
- If `swarm://` is meant literally → it is a NEW scheme → a `contracts/address.py` edit = **rule 7 CONFIRM** (a contract widens the system) AND collides with **rule 8 (author from the registry; never invent)** and the carried `run://` decision. It would be additive (the `ui://`/`code://` precedent at `address.py:12-31` shows label-only schemes can be added additively), but it is still a deliberate CONFIRM-level contract act, not a build-call.
- If `swarm://` is just shorthand for `run://` → the triad needs reconciling so both faces (G4 injection and G7 render) name the same scheme.

**The plan currently does both.** This is the single cleanest inconsistency: pick one. Recommended (aligns with DECISIONS + rule 8): use `run://<turn>/<role>` throughout, drop `swarm://` to prose-only, and state that no new scheme is minted.

### X2 — Edge `kind` is a contract edit; the plan does not flag it CONFIRM
C1.3 (Criteria) + Guide G1.3 add a declared `kind` to the `Edge` shape and say "register edge-kinds in the registry." 

**Contract evidence:** `contracts/node_record.py:35` — `class Edge` today has only `from_node/from_port/to_node/to_port`; **no `kind` field and no `schema_ver`.** 

**Law consequences:**
- Adding an optional `kind` (with a default) is legal under **rule 2 (schema-additive)** — but editing `contracts/node_record.py` is the **widest-blast-radius act = rule 7 CONFIRM** ("change a contract → CONFIRM"; `contracts/AGENTS.md`: *"change a contract without CONFIRM · the widest-blast-radius act"*). The plan treats it as an in-scope MODIFY and **does not flag the CONFIRM gate.** Gap to close.
- Edge carries **no `schema_ver`** today, so the rule-2 "add optional field + bump `schema_ver`" mechanic does not cleanly apply to Edge specifically (the version markers live on `Provenance`/`NodeType`/bridge msgs, not `Edge`). The plan should say HOW old edges (no `kind`) stay valid — i.e. `kind` defaults to `data-wire` so existing graphs keep working (rule 2's intent), and note Edge has no version marker to bump.
- Contracts constitution also requires: *"Update the vault spec (`build-prep/contracts/`) to match — the vault is source of truth."* (`contracts/AGENTS.md:16`). The plan does not mention updating the C3 vault spec. Gap.

---

## GAPS (omitted obligations the laws require)

### G-A — Self-description / drift updates are unstated for every net-new registry
**Rule (AGENTS.md after the table):** *"Every change updates the self-description (AGENTS.md · MAP.md · STATE.md · the module's AGENTS.md) — it is part of the change, not optional… `tests/drift_acceptance.py` fails loud if a registered capability or an acceptance suite isn't reflected."* The triad names `drift_acceptance.py` in its tool list (Criteria C1 FORM, "drift_acceptance passes") but **does not enumerate which self-description surfaces each new registry must update.** Concretely:
- **Roles registry (G2)** — `MAP.md`'s `<!--REGISTRY:START-->` block lists node-types/RHM-verbs/modes/panels/models. A file-discovered **roles** registry is a NEW capability class; it must either appear in that live block (via `Suite.refresh_self_description()` / `capabilities()`) or `drift_acceptance` won't cover it. The plan should say roles join `capabilities()` + the MAP registry.
- **MODEL_CAPABILITIES (G8)** — `capabilities()` (`suite.py:471`) is *"one snapshot of WHAT EXISTS, fed into every authoring prompt + every registered select."* The plan does NOT state that `MODEL_CAPABILITIES` wires into `capabilities()` / the MAP registry. Under **rule 8** (registry is the source of truth, the path-of-least-resistance law that binds the self-coding brain), a capability registry that authoring prompts can't see invites confabulation. Gap: declare the `capabilities()` wiring + a drift assertion.
- **Edge-kinds, rule-engine, thought-shapes, activation-contexts** — each is registry data per L1; each needs a stated self-description/drift home. The plan asserts L1 but doesn't map the drift surface for each.

### G-B — `cognition.*` events need NO contract change but DO need self-description (the plan implies the opposite)
The Guide (G7) calls `cognition.*` an "emit-contract." **Evidence that it is NOT a pinned contract:** event kinds live as string literals in `runtime/*.py` (`suite.py:4321` `_emit("decision.intent")`; `implement.py:406` `_TERMINAL_KINDS = ("decision.implemented","decision.verify")`), emitted via `_emit`/`_emit_durable` — **there is no event-kind shape in `contracts/*.py`.** So `cognition.*` is **not** a `Cn` contract act (no rule-7 CONFIRM for the event names themselves) — it is runtime + bridge + the canvas SSE branch (the `decision.*` precedent at `useAppController.ts:384`). What it DOES require: the new SSE surface is operator-facing → **rule 9 FORM** (design-system + design-critic, already in C7/CF.1) and a STATE/MAP note. The plan should reclassify `cognition.*` from "contract" to "runtime emit + drift/self-description" so the build doesn't over-gate it or under-document it.

### G-C — `output_destination` "typed-lane/channel" (C3.2) may touch a contract or be net-new infra
Four of the five rule destinations reuse existing seams (inject→address-resolve, chain→role, address→store, surface→`surface_review`/inbox). The fifth — **typed-lane/channel** — has no cited existing seam in the triad. If a "channel" is a new addressed lane it may need a store/contract touch (CONFIRM) or is genuinely net-new infra. The plan should name the seam or flag it as a sub-decision, not leave it as a bare destination kind.

### G-D — Voice synth-unit change is consistent but the constitution's VRAM + venv constraints are unstated
G6 redefines the TTS streaming unit from per-sentence (today) to per-part. **This aligns** with `voice/AGENTS.md`: TTS voice/engine is config-driven, the synth unit is a caller decision, and the bridge proxies `/api/tts`. No contradiction. **But** the voice constitution adds two hard constraints the plan never echoes: (1) *"Load STT/TTS onto the GPU without checking VRAM headroom"* is a **Never** — and the swarm's resident-4B + co-resident voice budget is already tight (`ops/AGENTS.md`: "Orpheus + 64K brain over by ~0.6GB"). The 32-concurrency swarm KV pool (C1.2) competes for the SAME card; the plan's slot budget (G1.2) and G8 VRAM-authority reuse cover the brain, but the **swarm-KV-pool ⨯ resident-voice co-residence** is not VRAM-accounted in the triad. (2) The TTS service runs in `.voice-venv` (3.12), proxied — the plan's "near-zero change to `speak()`" should respect that proxy boundary. Both are gaps, not contradictions.

### G-E — Group G9 governance: aligned, but "roles can act" needs the deterministic-router proof stated
C9.1 says roles act through the existing posture (`guard()`/POLICY), AUTO/reversible classes only. **This is well-grounded:** `runtime/governance.py` exports `guard, posture, AUTO` (`suite.py:15`); the router is explicitly **deterministic** (`suite.py:1053,2059-2060`: *"The routing is deterministic (the action's posture decides), not a judgement call"*). This matches the **no-confidence / deterministic-gates** rule (the wire never writes a confidence value; posture decides). The gap is only that the Criteria should cite that a role's action class is resolved by the SAME deterministic posture router (no model judges escalation) — making C9.1's adversarial check concrete.

---

## CONFIRMATIONS (laws the plan honors — compressed)

| Law / constraint | Where it lives | Plan alignment |
|---|---|---|
| **1 · build-against-contracts** | AGENTS.md r1 | Reuses C1/C2/C5/C6 seams (resolve/inject, node-type, compile); doesn't work around them. ✔ |
| **2 · schema-additive** | AGENTS.md r2 | `output_schema` enforce, edge `kind`, `chat_parts` beside `chat` — all additive. ✔ *(Edge has no `schema_ver` — see X2.)* |
| **3 · one-source** | AGENTS.md r3 | "One shared substrate + two thin drivers"; no parallel system (Guide principle 5, C1 FORM). ✔ Strongly central. |
| **4 · fail-loud / no silent fallback** | AGENTS.md r4 | C0.4, C4.3 bypass, C8.4 residency fail-loud + offer-to-load, C9.3, DECISIONS B2-Q2. ✔ Matches MEMORY [[feedback-no-silent-failures]]. |
| **5 · ext4 storage** | AGENTS.md r5 | Worktree is `~/company-cognition` (ext4); no `/mnt/c` writes proposed. ✔ |
| **6 · NO Gemini** | AGENTS.md r6 | Swarm = resident 4B; no Gemini. ✔ *(Note: `gemma4`/`gemma4-26b` in the model registry are Gemma not Gemini — no violation.)* |
| **7 · stage-gated / CONFIRM contract changes** | AGENTS.md r7 | Spike-gate G0 honors stage discipline. ✗ **Misses CONFIRM on Edge-`kind` (X2) and `swarm://` if minted (X1).** |
| **8 · author-from-registry, never invent** | AGENTS.md r8 | L1 registry-driven throughout; suitability is a query not prose (C2.5/G8). ✗ **`swarm://` invention risk (X1); MODEL_CAPABILITIES→`capabilities()` wiring unstated (G-A).** |
| **deterministic gates / no-confidence** | governance.py; suite.py:1053,2059 | C0.2 replay-identical routing; L2 rules deterministic, no model in a rule; posture router deterministic. ✔ Core alignment. |
| **reflects-never-owns** | AGENTS.md r9; ui_info.py:19 | C7.1 canvas driven by `cognition.*`, backend truth; G7 "registry data → render rules → canvas." ✔ |
| **autonomous-spawn lead-only** | MEMORY [[feedback-autonomous-spawn-lead-only]]; AGENTS.md r9 wire | C9.2 structural floor, adversarially verified; `_run_swarm` off the MCP face. ✔ Explicit + correct (B3-R2). |
| **no branches in ~/company** | AGENTS.md r10; MEMORY [[feedback-no-branches-company]] | ⚠ **L3 + Criteria build on branch `concurrent-cognition`.** AGENTS.md r10 permits a `git worktree` for isolation ("merge back the same session"); `~/company-cognition` IS a worktree. Consistent IF treated as a worktree merged back, NOT a stranded feature branch. Flag: the triad says "branch," the law says "worktree, not branch" — name it a worktree to stay clean. |
| **no-versioning / update-in-place** | MEMORY [[feedback-no-versioning]] | `chat_parts` is an additive sibling, not `chat_v2`; roles/rules are new files not versioned copies. ✔ |
| **FORM is half of done** | AGENTS.md r9 | C7 FORM, CF.1, design-critic separate from implementer, `needs-tim` for feel. ✔ |
| **introspective-data-building** | MEMORY [[project-introspective-data-building]] | C5.4 rollups consolidate the swarm's own run-records; `swarm://` persist-per-turn (DECISIONS dev-call). ✔ |

---

## MINOR

- **Citation drift:** the triad cites `ROLE_REGISTRY` at `suite.py:929`; it is actually at **line 943**. Other file:line cites (`scheduler.py:60-153`, `bridge.py:357-468`, etc.) were not all re-verified. Recommendation: a build agent must re-confirm file:line before editing — citations drift as `suite.py` grows. One-line caution, not a blocker.

## Net read
The plan is deeply law-aligned on the load-bearing principles (one-source, fail-loud, deterministic routing, reflects-never-owns, lead-only spawn, registry-driven). The real work before the build is **(1) reconcile the `swarm://`/`run://` split to one scheme (X1)**, **(2) flag Edge-`kind` as a rule-7 CONFIRM with a default for old edges + a vault-spec update (X2)**, and **(3) attach explicit self-description/drift homes to every net-new registry, and reclassify `cognition.*` as runtime-emit not a contract (G-A, G-B)**. The voice VRAM co-residence accounting (G-D) and the typed-lane seam (G-C) are open sub-decisions to name, not contradictions.
