# L3 — the decide→SIGNAL→resume wire (the heart of the operator loop)

Lead's principle (2026-06-21): `decide → SIGNAL [post decision.decided(id, chosen_option) + emit the
event/mark] → the work GATED on that decision RESUMES with the chosen option`. v1 = the decided-signal
posts → the lead/lanes un-pause; the fuller version = a blocked-on registry that auto-resumes.

## v1 — BUILT + verified by use (2026-06-21, fork)

The decide→SIGNAL half closes; the resume is consumer-driven (lead/lanes), within the floor.

**The chokepoint.** Every operator decide is a `decision_take` mark routed through
`runtime/territory.py:territory_write` (the card-take route-back: `{type:'decision_take', value:<chosen
option label>, element_id:<canonical decision://global/<id>>}` → `suite.mark`). That is the ONE place a
decide is written — so the signal fires there, once, for every decide.

**The SIGNAL.** `runtime/decision_registry.py:decision_decided_signal(suite, address, chosen_option, *,
by=None)` emits a first-class `decision.decided` event (`suite.emit_run_record("decision.decided", 0,
decision_id=, address=, chosen_option=, by=)`) the instant the take lands. territory_write attaches the
returned signal dict to the mark record as `decided_signal` (or `decided_signal_error` if the emit fails —
surfaced, never swallowed; the decide itself never rolls back, the mark already landed).

**The READ (consume).** `GET /api/decision/decided-signals?since=<seq>` — a thin projection over the
existing event log (`events_since` filtered to `op=decision.decided`), no parallel signal store. Returns
`{ok, signals:[{decision_id, address, chosen_option, by, seq, ts}], count}`. The lead/lanes read this to
know a decision cleared + with which option → they un-pause the gated work (v1's resume).

**THE FLOOR (why v1 stops at signal+read).** A true autonomous resume — posting into a live channel,
waking/dispatching a session — is exactly the gated path (`autonomous-spawn-lead-only`;
`session_post`/`channel_act` → 403). So the wire's AUTONOMOUS part is a RECORD emit only (floor-clean, like
every role-run); the actual resume is fired by the lead/operator (or, later, the gated activation loop when
Tim enables it). The brain records + makes-consumable; the human/lead fires. This is the same floor
brain_router + run-in-channel/propose already honour.

Verified by use: drove the exact card-take payload through `territory_write` → mark landed (decision_take)
→ `decided_signal` attached `{decision_id, address, chosen_option:'check with you before each build',
by:'tim'}`, no error → the signal is queryable via the read. (One disclosed test artifact: a
`__l3_verify__` signal in the append-only event log — inert, no matching decision row.) No regressions:
territory 33/33, decision_lineage 8/8, decisions unchanged (the pre-existing D7 render fail is not L3).

## v2 — the blocked-on registry (true auto-resume; NOT built)

For the loop to close WITHOUT a human relaying the signal, the gated work must DECLARE its dependency:
- A `gated_on: decision://global/<id>` field on the unit of work (a flow stage / a routine / a paused lane
  cursor / a session checkpoint). This is the missing declaration — today nothing records "I am blocked on
  decision X."
- A consumer that, on `decision.decided(id, option)`, finds the work `gated_on` that id and resumes it with
  `option`. WITHIN THE FLOOR this resume is still a PROPOSE for anything that posts/spawns (lead/operator
  fires) — OR a pull: a flow/activation tick re-reads the now-decided state on its next run (the gated
  activation loop, off by default).

The decision-registry side of v2 (co-owned): theorem-fork + other rows could carry a `resumes`/`origin`
pointer so a decided-signal knows WHICH lane raised it. Today decisions carry no origin (DECISION_FIELDS =
id/address/meaning/options/explanation_source/scope/legibility/subtype/owner) — adding a resume-target is
the decision-registry's v2 enrichment.

## Genuine Tim-semantics question (surfaced, not assumed)
"What resumes" in the fullest sense is a Tim-semantics call: is a decision a blocker on ONE lane that
raised it (resume that lane), or a value many downstream resolves read (pull-based, no active resume)? v1
is agnostic (emit + consume). v2's blocked-on shape should be chosen against how Tim sees a decision
relating to the work it gates — left for the lead/Tim, not guessed.
