# The Overnight Mandate — 2026-06-10 (Tim, going to bed)

## The goal function (Tim's words, made better — as he asked)

Tim's literal words: "your goal is to just do good things for me specifically, on loop... I don't
know how to tell you to just do everything you can to make things good for me without giving you
instructions... the real goal is to blow my fricking mind."

The best version of that intent, which this night runs on:

**Compose everything that exists — the engine, the memory, the resolver, the wire, the mining, the
transcripts, today's entire riff — into the system Tim described today, so that when he arrives
tomorrow the difference is FELT, not reported.** Not a list of completed tasks: a changed morning.
He should arrive and the system should MEET him — know him, know the night, know what's waiting,
put the builder at his fingertips — at his altitude, by his rules (operator_memory op='rules' is
the rulebook), with everything reversible (git) and everything honest (no green-paint, ever).

The bar, concretely — the MORNING EXPERIENCE this night aims at:
1. **He is greeted.** Arriving at the surface (or asking Viv "what happened?"), he gets
   caught-up-in-one-glance: what was built, what's in flight, what waits on his gate — rendered at
   his altitude, not a log. (The greeting resolution from Track-1, made real enough to feel.)
2. **The builder is in the surface.** The Claude Code side panel works end-to-end: point at
   anything, talk, watch it investigate with full context, and the build-this handoff reaches his
   existing gate. Command-through-the-surface, first contact.
3. **A memory returns BY ITSELF.** The deferred-27's condition references FE-work-becoming-now;
   tonight FE work becomes now. The first condition-fired memory injection — his time-axis idea,
   alive. (Honestly scoped: the condition partially fires — the panel exists, the full UI doesn't.)
4. **The night presents ITSELF.** The morning walkthrough is not a markdown file he must read —
   it's the system's own organs: inbox cards he can walk, the walkthrough organ pointing at what
   was built, Viv able to narrate it. (.build/overnight/MORNING.md exists as the agent-facing
   record; TIM's copy is the surface itself.)
5. **The night's ideas enter the lifecycle.** New feature-rows proposed (status='proposed', at
   their addresses) where the work reveals them — his accept-queue grows with real, grounded
   proposals, never fabrications.

Resources: TOTAL. All MCP tools, dynamic workflows, agent fleets, the embedder + concurrent models,
the transcripts on disk (mine tonight's riff into the corpus — today's conversation is foundational
material), the vault, the Atlas. Session compaction is expected; the loop carries; state lives in
files, never in any one context window.

## The work queue (the FLOOR — .build/overnight/state.json tracks)

- **S1 · THE CLAUDE CODE SIDE PANEL.** runtime/ui_claude_session.py (subprocess stream-json wrapper:
  `claude -p --output-format stream-json --include-partial-messages --permission-mode plan`,
  --resume multi-turn; permission env-gated COMPANY_PANEL_PERMISSION default plan, the implement.py
  pattern) + bridge routes /api/claude/start|continue|history (ndjson, the RhmChat streaming
  pattern; OPERATOR FACE ONLY — never on MCP) + FE sidebar region on kit primitives, the indicated
  ui:// address + address_help/R2 context riding in + the handoff (build-this → intent-at → the
  wire's gate). Verify BY USE end-to-end + npm build + devtools + 390px. FORM = tokens only.
- **S2 · THE NOW-ORGAN + THE GREETING.** now() upgraded: activity-states (mode · live runs ·
  in-flight builds · last contact · the night's work), a conditions seam (rules-engine reuse),
  dial-override evaluation (honest flip of overrides_evaluated), and the GREETING RESOLUTION
  composed on it (morning bar #1).
- **S3 · CONTEXT-RESOLUTION EXTRAS.** operator_memory as an R2 stratum (his rules surface when
  presenting-to-Tim is the activity) · the GC14 first fire (morning bar #3) · what the work reveals.
- **S4 · INBOX.** The ~38-item stale litter → triage lanes + age-aware presentation + a bulk-retire
  PROPOSAL for Tim (never auto-resolve) · altitude-grammar rendering (Pulse/River).
- **S5 · MODES.** What the work reveals (mode-aware default altitudes; condition vocabulary
  alignment).
- **S6 · COMPOUND.** Mine tonight's sessions (the riff is gold) · drift radar · floor walk ·
  proposed rows from the night (morning bar #5) · operator-memory proposals from fresh patterns.

## Loop laws (bind every fire)
One bounded beat per fire · lock or exit (.build/overnight/loop.lock <25min) · commit per coherent
unit to main, explicit pathspecs, "[overnight] …", NO Co-Authored-By · verify by USE (bridge:
systemctl --user restart company-bridge.service; FE: npm run build + chrome-devtools :5173 + 390px;
suites + drift before commit on engine edits) · FLOOR UNCHANGED (the panel launches claude ONLY
operator-initiated, plan-mode default; /api/claude/* never on the MCP face; nothing auto-resolves;
autonomous claude -p stays lead-only — the loop itself never self-dispatches builds) · fail-loud ·
no green-paint (feel/aesthetics → needs-tim) · GPU-aware (`company gpu` first; never stomp) ·
record to MESSAGES.md + state.json each fire · DON'T delete the cron (Tim ends it) · keep
.build/overnight/MORNING.md current as the agent-record; the surface is Tim's copy.
