# Consolidation Draft — consent-tests

**Overlap members:**
- `/home/tim/company/tests/propose_affordance_acceptance.py` (the B1 suite — 18 checks)
- `/home/tim/company/tests/interactive_consent_acceptance.py` (the B2 suite — 30 checks)

**Drafted:** 2026-06-10, consolidation-drafter lane (cognition-self-improvement).
**Law honoured:** no source file was edited, moved, or deleted. This document is analysis only — for TESTS the deliverable is an analysis doc, never test-code changes.

---

## VERDICT: keep-separate-by-design

These are **two acceptance suites covering one mechanism from different angles** — exactly the by-design overlap category. The mechanism is the non-executing `suggest` affordance (the RHM *offers* an action as a structured `proposal`; nothing dispatches until the operator's explicit approve fires `Suite.act` = the `/api/act` path). The B1 suite proves the **substrate** (the consent gate exists at all, act-vs-offer are distinct, approve is reuse not a new path). The B2 suite proves the **widening** (multi-option `options[]`, the `interactive` marker derived from the consequential verb class, select≠approve, the CONFIRM-class second approval, per-option fail-loud). B2's own docstring declares the layering: *"This is built ON the B1 substrate."*

Merging them into one suite would **lose things**, not gain:

1. **Criteria traceability.** Each suite is the acceptance artefact for a distinct Completion-Criteria line (B1 = the unified offer affordance from the 2026-06-06 main-merge convergence; B2 = the on-screen interactive build surface, direction doc §6B.2 mode 3). The build loops mark criteria green per suite — one suite per criterion is the marking unit. A merged file would re-couple two independently-verifiable criteria.
2. **Determinism boundary.** The B1 suite is fully deterministic end-to-end (every model turn is synthesized via the `complete_with_tools` monkeypatch). The B2 suite is *deliberately not*: its §3 approves a `panel` option whose `propose_panel` invokes a **real, unmocked model** (the lane is real-nodes-no-model for the plumbing, but the approve-side payload is live-model territory — the suite explicitly accepts the `panel | ask` nondeterminism and asserts only the model-independent invariant). Merging would infect the deterministic substrate suite with an environment-dependent step (needs a model up), degrading B1 from always-runnable to sometimes-runnable.
3. **Failure isolation.** Separate temp stores and separate graphs (`i3-graph` vs `b2-graph`); a B2 widening regression fails B2 without obscuring whether the B1 substrate still holds — that diagnostic split is the point of layered acceptance.
4. **Institutional memory lives in the headers.** The B1 docstring + its §NOTE are the *record of the unification* (the parser-era `AFFORD:` text directive retired in favour of the native `suggest` tool; `_parse_rhm_proposal` left as dead code on the Suite — still present, observed at `runtime/suite.py` ~4364–4367). The B2 docstring is the *record of the B2-vs-wider-B1 discriminator*. These are different stories; one merged header would compress them lossily — against expansion-over-reduction.
5. **The repeated checks are load-bearing contract re-proofs, not copy-paste drift.** The `options[]`/`direction` shape that both suites assert is consumed by at least three parties: the FE card mapper, the B2 interactive surface, and B3's configurable interactive-inbox (which persists exactly `{verb, address, args, options[], interactive, direction}` to revive an offer — observed at `runtime/suite.py` ~6685–6726). Re-asserting the shape in each layer's suite is regression armour for a multi-consumer contract.

What **is** genuine duplication is scaffolding, not truth — catalogued below with a proposed (never executed) remedy for the owning session.

---

## RATIONALE — what is duplicated, what each source uniquely holds

### A. The duplicated proofs (overlap matrix)

| Invariant | B1 suite (propose_affordance) | B2 suite (interactive_consent) | Nature of the overlap |
|---|---|---|---|
| `suggest` tool is offered to the RHM | §0 (offered; alongside real verbs) | §0 (offered; + advertises `options[]` schema) | Layered: B2 re-proves presence then proves the *widened schema*. The presence check repeats; the schema check is B2-only. |
| Consent gate: an offer dispatches NOTHING (`dispatched == []`, `action is None`, prose reply survives) | §1+2 — 3 checks, on a single `show` offer | §1 — 3 checks, on a 3-option `panel` offer; re-proven again in §2 (re-offer), §4 (build offer), §5 (dropped/all-bad offers), §6 (B1-shape offer) | Same invariant, **different payload classes**. B1 proves it for the substrate trigger; B2 proves it survives every widened shape. The B1-payload instance is duplicated (B1 §1+2 ≈ B2 §6); the other five instances are B2-unique surface area. |
| Whitelist gating (registry-is-truth; `Suite.RHM_VERBS`) | §5 — a single non-whitelisted verb → NO card at all | §5 — mixed offer: bad option *dropped*, good option survives; ALL-bad → no card | Different granularity of the same truth. B2's all-bad case generalises B1's single-bad case; B2's per-option drop is net-new mechanism (the filter at `runtime/suite.py` ~5760s normalises options against the whitelist). |
| `options[]` + `direction` ride on the proposal | §1+2 (shape exists even for the single offer — "rich-layer-ready") | §1 (multi-option content), §6 (single offer still carries the shape) | B1 proves the *forward-compat shape*; B2 proves the *content* that fills it. B2 §6 duplicates B1's shape check on purpose (preservation regression). |
| Approve → `Suite.act` (the `/api/act` path) | §4 — approve outcome `==` direct `act()` outcome for `show` (the reuse-equality proof) | §3 (panel → CONFIRM-class surfacing) + §4 (build → composes, node count rises) | Same entry point, **disjoint invariants**: B1 proves *path identity*; B2 proves *verb-class behaviour* (second approval vs AUTO). No real duplication beyond both calling `act()`. |
| B1 single-offer behaviour preserved | the whole suite | §6 — 3 checks (`interactive is False`, one option, shape + no dispatch) | **Deliberate regression smoke inside B2**, guarding that the widening didn't break the substrate. This is the canonical by-design overlap: an anchor re-asserting what another suite owns. It must NOT be removed from B2 (it is B2's non-regression contract), and it does NOT substitute for the B1 suite (3 checks vs 18). |

### B. What ONLY the B1 suite holds (would be lost if it were retired)

- **Act-vs-offer distinctness (§3):** an ordinary verb tool_call STILL dispatches (`execute-then-render` preserved, `dispatched[0].verb == "run"`, `action.did == "run"`), and a dispatched turn carries **NO proposal**. The B2 suite never exercises the ordinary-verb path at all.
- **Grammar validity of the offered address:** `parse_ui_address(prop["address"])` from `contracts.ui_info` must accept it. B2 never validates address grammar (its options carry `args`, mostly no address).
- **The reuse-EQUALITY proof (§4):** approving the proposal and calling `act("show", …)` directly produce the *same* outcome (`did` equal, target present) — the "approve is the act path, not a new path" theorem in its strongest form. B2 only proves approve *reaches* act-class outcomes.
- **The unification record:** the docstring's history (convergence shipped `AFFORD:` text directive via `_parse_rhm_proposal`; main retired it for native tool-calling; capability preserved + unified) and the §NOTE flagging `_parse_rhm_proposal` as **dead code remaining on the Suite** (corroborated by reading: still defined at `runtime/suite.py` ~4364–4367). This dead-code flag is an open item the owning session may want to route (see "decisions" below).
- **Single non-whitelisted verb → no card** as the *primary* (not generalised) fail-loud case.
- Distinct fixture: a 2-node connected graph (`constant → uppercase`) — B2 uses a 1-node graph.

### C. What ONLY the B2 suite holds (would be lost if it were retired)

- **Tool-schema widening (§0):** `suggest` advertises an `options[]` parameter whose items declare `summary` (the distinguishing content); consequential verbs (`build`/`panel`/`extend`) are actually OFFERED in the mode (`available_verbs` reachable).
- **The `interactive` marker derivation:** consequential multi-option offer → `interactive is True`; single non-consequential → `False`. (Implementation: `interactive = any(o["verb"] in {"build","panel","extend"} for o in norm_opts)` — observed at `runtime/suite.py` ~5796–5797.)
- **Distinguishing content per option:** 3 options, 3 *distinct* summaries, human labels, all verbs whitelisted — the comparison surface's substance, "not just the verb".
- **SELECT ≠ APPROVE (§2):** re-offering (the operator merely looking/steering) dispatches nothing — there exists NO backend route by which *carrying* options runs one; only a deliberate `act()` on the chosen option dispatches. (The FE select-then-approve interaction itself is verified by use in chrome, per the suite's own note — not asserted here.)
- **The CONFIRM-class second approval (§3):** approving a consequential `panel` option SURFACES exactly one unresolved inbox item (`resolved is None`) for a SECOND operator approval — never self-applies; accepts `did in ("panel","ask")` because `propose_panel` invokes a deliberately-unmocked model (PoLR fail-loud `ask` is an equally valid consent-honouring outcome).
- **AUTO-class build proof (§4):** approving the chosen build composes the pipeline (`did == "build"`) and *actually adds the node* (count +1) — the model-free "the CHOSEN option, and only it, drove the dispatch" proof.
- **Per-option fail-loud (§5):** a non-whitelisted option is dropped from a mixed offer (never a bad card); an ALL-bad offer yields no card.
- **Inbox-delta accounting** (`before`/`after` id-set diff) — a technique the B1 suite doesn't use.
- The needs-tim boundary statement: multi-option **generation quality** is the live-model half — flagged, not asserted.

### D. The genuine duplication — shared scaffolding (~45 lines per file, copy-paste)

Identical in both: `check()` (assert + counter + print), `tool_call()` (the OpenAI tool_call shape with JSON-string arguments), the `FsStore`+`NodeRegistry`+`Suite` temp-dir setup, `_model_supports_tools` stub, the dispatcher-spy pattern (`spy_dispatch` appending to `dispatched`), the `complete_with_tools` monkeypatch + `finally`-restore, `COMPANY_TEST_RUN=1` (inbox hygiene, governance.py), `shutil.rmtree` teardown.

This is the only consolidation-shaped material here, and the right move (if any) is **extraction, not merging**: a `tests/_consent_harness.py` (or wider `tests/_acceptance_harness.py` — the pattern likely recurs in other acceptance suites) exposing `check`, `tool_call`, the spy, and a suite-factory context manager. Both suites would shrink by ~45 lines and stay independent. Proposed only — NOT executed in this lane (no test-code changes), and note `conv_consent_acceptance.py` (a *different* mechanism: X5 consent-time resolution, surfaced==launched — outside this overlap) likely shares the same scaffolding and would be a third beneficiary.

### E. Coverage gaps neither suite holds (found while mapping — free value, not a consolidation argument)

Observed in the implementation but asserted by neither suite:

1. **Single consequential offer → `interactive is True`.** The code comment at `runtime/suite.py` ~5792–5795 states a *single* consequential offer still presents the interactive frame (`interactive = any(...)` over even one option). B2 tests multi-consequential (True) and single-NON-consequential (False) — the single-consequential cell of the truth table is untested.
2. **Multi-option NON-consequential offer → `interactive is False`** ("a multi-`show` offer stays the lighter B1 list", same comment block). Also untested.
3. The `extend` verb is asserted as *offered* (B2 §0) but never exercised as a chosen/approved option (only `panel` and `build` are).

If the owning session adds checks, they belong in the **B2 suite** (they are derivation-of-the-marker facts, B2's lane).

### F. Verification status (honest split)

- **Observed:** everything above re: check content, scaffolding identity, and the `runtime/suite.py` anchors (suggest tool schema ~3959–3987; whitelist filter + interactive derivation ~5757–5801; `RHM_VERBS` ~3777–3833; dead `_parse_rhm_proposal` ~4364; B3 consumer ~6685–6726) — by reading, this session.
- **NOT verified here:** neither suite was *executed* in this lane (B2 §3 requires a live model for `propose_panel`; running was out of scope for an analysis deliverable). No claim is made that both currently pass — the owning session's loops own green status.

---

## WHAT THE OWNING SESSION SHOULD DECIDE

1. **Accept keep-separate-by-design** (this draft's recommendation) — the two suites stay the acceptance artefacts of their two criteria.
2. **Whether to extract the shared harness** (`tests/_consent_harness.py` or repo-wide `_acceptance_harness.py`, §D) — pure de-duplication, zero behaviour change, three+ consumers. Per no-deferral this should be *routed*, not parked: it is a small, file-disjoint lane.
3. **The `_parse_rhm_proposal` dead code** (flagged by the B1 suite's own §NOTE, still present): delete in a hygiene pass, or keep as a documented fossil. Either way the B1 docstring remains the record of the unification.
4. **Whether to add the three missing derivation checks** (§E) to the B2 suite.
5. **Cross-reference hygiene (optional):** a one-line pointer in each suite's docstring to the other ("substrate suite" ↔ "widening suite") would make the by-design layering self-describing for future agents — AI-path-of-least-resistance against a future drafter re-flagging this same overlap.

---

## DISPOSITION TABLE (proposed, never executed)

| Source file | Disposition | Reasoning |
|---|---|---|
| `tests/propose_affordance_acceptance.py` | **keep** (as-is; no fold-in, no retire) | Owns the substrate criterion: consent-gate trigger, act-vs-offer distinctness, reuse-equality, address grammar, the unification/dead-code record. Fully deterministic — the always-runnable layer. Optional: adopt shared harness; add pointer-line to the B2 suite. |
| `tests/interactive_consent_acceptance.py` | **keep** (as-is; no fold-in, no retire) | Owns the widening criterion: options[] schema, interactive derivation, select≠approve, CONFIRM-class second approval, AUTO build composition, per-option fail-loud. Its §6 B1-smoke is non-regression armour and must stay. Optional: adopt shared harness; add the §E derivation checks; add pointer-line to the B1 suite. |
| *(proposed net-new)* `tests/_consent_harness.py` | **create** (owning session's call) | Extraction target for the ~45 duplicated scaffolding lines (§D); `conv_consent_acceptance.py` is a likely third consumer. |

Nothing retires. Nothing folds. Every unique fact in both suites is inventoried above (§B/§C) and survives in place.
