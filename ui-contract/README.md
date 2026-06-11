# ui-contract — the Company's UI Contract corpus

You are (probably) an agent given ONLY this directory. It is the complete, purpose-free contract
for driving the Company's capability fabric — you never read the repo's code or its disposable
harness UI. You have plain filesystem read over this WHOLE tree, including `coverage/*.json`
(machine artifacts; reach them by reading files, not search). Semantic search, if you have it,
is an accelerator — these flat files are sufficient on their own.

## Ontology
- `resources/<noun>.md` — one entry per resource noun. Each carries Identity, Representation
  (with field-reality honesty columns), State model (an fsm fence or `stateless.`), Caller
  (who you are, per transport), Operations (uniform verbs: list · get · create · update ·
  delete · act · watch · search), Errors, Links.
- `journeys/` — authored cross-resource flows: ordered op refs + the disambiguation prose
  that lives BETWEEN resources.
- `atlas/FEATURE-ATLAS.md` — the 35 capability classes (frozen ids CC-01…CC-35) and their
  affordances; coverage grain is the affordance. `OUT-OF-SCOPE.md`/`INVENTORY-EXCLUSIONS.md`
  hold reasoned exclusions (never silent).
- `TASKS.md` — intent phrase / alias → (op, params) rows, including "not exposed" rows.
- `TRANSPORTS.md` — transport ids → protocol, exposure, caller-identity model, inventory source.
- `CONVENTIONS.md` — uniform verbs, the error envelope + per-face carriers, cursor law,
  address grammar, the named-act registry.
- `CONTRACT-FORMAT.md` — the frozen format this corpus is written in (the full law).

## How to navigate (the protocol, in full in CONTRACT-FORMAT §8)
1. Orient here, then find your task in `TASKS.md` (intent phrases + aliases map straight to
   ops, parameter-level rows included). Cross-resource tasks: check `journeys/`.
2. Orient on the resource: Identity → Representation → State model → Caller. The fsm tells
   you what is legal BEFORE you pick; Caller tells you who you are on your transport.
3. Pick the op + binding for your vantage (bindings carry exposure registry keys).
4. Execute and PROVE: for writes, follow the op's "Consequences & proof shape" — read the
   declared event stream from your cursor, join on the correlation keys, match the declared
   rows. Done = declared events appeared, never "the response looked ok".
5. On refusal: match the error code, follow its `teach` text. A state-gated refusal after a
   passed pre-check is expected concurrency — verdict `pass-via-refusal`, not failure.
6. Every address in any response → INDEX's SCHEMES table → owning entry + accepting ops.
7. Reached-for-but-missing → append `{task, looked_for, where_searched, ts}` to
   `coverage/drops.jsonl`. A missing affordance is a recorded gap, never a dead end.

## Honest current status (F1 slice — update in place, never version)
This corpus is UNDER BUILD beside the fabric it contracts. As of 2026-06-12 it carries the
F1 Session-Fabric slice (`session`, `session-message`, `events`, `transcript`, `fabric-config`)
and the F3 Execution-&-control slice (`permission`, `model`, `agent-team`, `headless-control` —
Atlas classes 7/9/10/18). Statuses are honest per CONTRACT-FORMAT §4.2 — most F1 ops are
`building` (code exists, run-proven by acceptance suites; NOT harness-flipped `live`), some
`planned` (no code yet — bridge fabric routes, transcript search). F3 is mostly `planned`: the
supervisor spawn carries no permission/model/effort/output-format param, and there is no native
agent-team face — so those control resources contract the NATIVE Claude Code surface with the
exact spawn-param gap named per op, and route the live capability to the fabric (permission
posture READ, the consult fan, inject/interrupt, the folded watch stream are the `building`
slices F3 re-exposes through F1's endpoints). No op in this corpus is `live`:
the corpus-only driving harness that flips statuses has not run yet. Examples are
`captured: synthetic` and marked so. The generated layers (`INDEX.md`, `EXPOSURE.md`/
`exposure.json`, `coverage/`, `evidence/`, `tools/validate.py` V1–V26) are NOT YET BUILT —
`TASKS.md` is an initial hand-derived render of the per-op `tasks:` declarations and says so
in its header. Until `tools/` lands, treat the resource entries + TRANSPORTS + CONVENTIONS
as the truth surface and the absence of coverage artifacts as a known, loud gap.
