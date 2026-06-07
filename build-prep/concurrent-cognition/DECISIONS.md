# Concurrent Cognition — Decisions Log

*Tim's answers, recorded as we go (he directs; I record). The locked items are settled; the open ones are being walked through as questions with options. This + the two landscapes converge into the loop-prep triad.*

## Locked (settled)

- **L1 — Registry-driven, not hardcoded.** Everything (roles, rules, chains, models, capabilities, outputs, destinations, render) is declared registry data by type, like the rest of the system. No hardcoded one-offs. *(Tim, 2026-06-07)*
- **L2 — The core mechanism is RULE-BASED ROUTING/RESOLUTION from registry declarations.** A role emits structured output; **declared rules** decide what happens next — route it, chain it to a dependent role, inject it into a future part, send it to a destination. It can depend on a previous output to route somewhere. It is NOT a model judging weak-vs-strong / aggregating by quality. Deterministic, declared. *"That is the main mechanism that all of this application is aimed at."* (Tim, 2026-06-07.) → Consequence: model-aggregation/fusion is just **one optional role-type**, not the spine; the "can a 4B fuse 32 outputs" risk is no longer central — routing-by-declared-rules is.
- **L3 — Branch + worktree.** Built in `~/company-cognition` on branch `concurrent-cognition`, sub-agent-driven, the loop-prep triad as the common reference. *(Tim, 2026-06-07)*

## Open — being walked through (questions + recorded answers)

*(answers recorded here as Tim responds to each batch)*

### Batch 1 (answered 2026-06-07)
- **Q1 part grain → MODE-DEPENDENT.** The grain of a "part" follows the presence-dial (terse in focus, beats in conversation, paragraphs when explaining). Composes with the mode system. → reinforces "mode = the dial."
- **Q2 first role cast → I PROPOSE a starter set, and it is MODE-SCOPED** ("choose it for one mode"). Roles are declared per-mode; I seed a cast for one representative mode (chose **listening** — the conversational default), Tim reacts (keep/cut/add/rename). → roles are mode-scoped registry data; the active cast is a function of mode.
- **Q3 build scope → FULL SUBSTRATE NOW.** Do the proper registry-driven node-mechanism rebuild up front (edge-types, port-types, file-discovered roles, enforced output_schema) — the real foundation, benefits the app surface too. (Bigger build before payoff; accepted.)
- **Q4 rule richness → FULL DECLARED LOGIC.** A routing rule may be an arbitrary declared expression. Power over simplicity. CONSTRAINT to hold (else it violates the system's laws): the logic stays **declarative-by-inspection · deterministic · renderable · no hidden model judgment** (rules route; a model only ever runs inside a role, never inside a rule). Governance/render approach for rich rules is a build concern to design.

### Batch 1 follow-through — proposed starter cast for `listening` mode (Tim to react)
*(presented; awaiting keep/cut/add/rename)*

### Batch 2 (answered 2026-06-07)
- **Q1 slot budget → RESERVE A FLOOR, MODE TUNES THE REST.** Always keep ~a few slots free for the main stream + judge (never stall a turn); the swarm uses the rest; the mode-dial tunes how many. (Floor const = config, measured by use.)
- **Q2 residency → FAIL LOUD + OFFER TO LOAD.** If the resident model isn't up when a turn needs the swarm, surface it + offer to load — never silent degrade (no-silent-fallback law).
- **Q3 cloud → DECOUPLED + OPTIONAL (richer than the options).** The swarm always runs on the RESIDENT model. The CLOUD is an optional *brain choice* — it can be the main-stream brain (a deliberate choice, swarm still runs), it can be OFF, a MODE can auto-decide to use cloud, and cloud can run roles in the BACKGROUND. So: resident swarm ⟂ separately-selectable main brain (resident or cloud) ⟂ mode-driven auto-routing. CORRECTS the earlier "cloud loses the swarm" framing — it does not.
- **Q4 second target → ALL FOUR.** After live voice, the mechanism proves out across codebase-map-reduce · altitude-translation · typed-triage · background cognition (a roadmap, not one pick). Voice = first proving target; these = the sequence after.

### Batch 3 (answered 2026-06-07)
- **Q1 the cast → DEFERRED** (viewer truncated the option descriptions; re-asking with context in the message). FEEDBACK noted: AskUserQuestion option descriptions truncate in Tim's viewer → put substance in the message text, keep options short. (Applies to all future questions.)
- **Q2 when cognition fires → ALL ACTIVATION-CONTEXTS.** Per-turn + background (between turns) + sense-triggered (screen/app changes) + scheduled rollups. "Mode" generalises to activation-contexts (R4 confirmed). Build sequences them; voice-turn first.
- **Q3 role authority → ROLES CAN ACT IN SOME MODES (governed).** Not propose-only. In permitted modes a role may trigger reversible/AUTO-class actions via the EXISTING governance (POLICY/posture, like `decide-for-me`). BOUNDARY held: autonomous build-dispatch / `claude -p` stays lead-only ([[feedback-autonomous-spawn-lead-only]]) — roles never bypass the deterministic gates. So: governed reversible reach per mode, never unbounded.
- **Q4 destinations → ALL OF THESE.** A rule may route an output to: inject-into-reply · chain/trigger another role · land-at-an-address · surface-to-inbox/decisions · a typed lane/channel. (R3 confirmed — the destination set the four applications need.)

### Batch 4 (answered 2026-06-07)
- **Q1 cast → GOOD STARTING CAST.** Keep all six for `listening`: focus · recall · ground · connect · check · voice. Mode-scoped; tuned by use. (First locked role cast.)
- **Q2 jury/ensemble → BUILD IT IN.** The per-draw-variation primitive is first-class core (B3-R1): any role can be a quorum (run N times, varied, take a verdict). Fixes the volatile-memo collapse.
- **Q3 live view → IN THE FIRST BUILD.** The live cognition thought-graph (roles firing · chains · injections) renders on the canvas from the start, not deferred. Rendering is in-scope wave 1.
- **Q4 rule gating → TREAT LIKE ANY CHANGE.** A new/changed role or rule goes through the normal review/commit path — no special approval gate. (Rules are declared data; they ride the existing change discipline.)

## Carried as developer-level calls (Tim: make dev calls myself; surface outcomes)
- Address scheme for role instances/injections: default **reuse `run://<turn>/<role>`**, don't mint `cog://` unless a contract reason emerges (rule-8: never invent a contract lightly).
- `swarm://` namespace lifecycle: persist per-turn run-records (introspective-data-building) vs reap — lean **persist** (the swarm's own telemetry), GC old turns.
- Tools-offered-across-parts: only the **final** part carries the operator-facing tools array (intermediate parts are pure generation) unless a shape declares otherwise.
- The exact per-mode part-grain mapping (focus=line, listening=beat, explaining=paragraph) — a config table, tuned by use.

## Status: READY TO CONVERGE
All foundational decisions captured. Next: this + the two landscapes → the loop-prep triad (Completion Criteria · Implementation Guide · Research Synthesis) = the common reference for the sub-agent-driven build in the worktree. (Spike-gated: prove a 2-role staged turn before fan-out; full-substrate node-mechanism rebuild + live view in scope.)
