// MCP-COMPOSE-EVAL — the intuitiveness bar (Anthropic eval-driven; Tim 2026-06-09: composition through
// the MCP must be intuitive — make/check/use/run/discover). FRESH agents, MCP-ONLY, real compositional
// flows; the FRICTION they hit IS the deliverable → the prioritised MCP gap list that drives the sweep.
// Run: Workflow({scriptPath: "build-prep/cognition-self-improvement/mcp-compose-eval.workflow.js"})

export const meta = {
  name: 'mcp-compose-eval',
  description: 'Eval the company MCP for INTUITIVE COMPOSITION — fresh agents (MCP-only) run make/check/use/run/discover flows + report every friction point. The friction = the prioritised gap list. No code build, no commit.',
  phases: [{ title: 'Eval', detail: 'fresh agents drive real compositional flows through the MCP alone; report friction' }],
}

const FRESH = `
YOU ARE A FRESH AGENT evaluating whether the "company" MCP is INTUITIVE for COMPOSITION. Rules:
- Use ONLY the mcp__company__* tools. Discover them via ToolSearch ("select:<name>" or a keyword). You know NOTHING about this system beyond what the tools + their descriptions tell you.
- DO NOT read the repo / AGENTS.md / any docs / the source — that defeats the test. Drive PURELY through the MCP, as a real agent would when handed this server cold. (cognition_info / cognition_inputs / field_types are MCP discovery tools — using THOSE is fair game; reading files is not.)
- THE FRICTION IS THE DELIVERABLE. Log EVERY point where you: had to GUESS · hit a confusing/opaque error · picked the wrong tool then backtracked · couldn't tell which tool/param to use · got an overwhelming/unreadable response · couldn't chain one step's output into the next. For each: the tool, what was confusing, and what would have made it obvious (a clearer name/param/enum/description/error).
- FLOOR: you may create DECLARATIVE things (roles, cascades) but NEVER resolve/approve/dispatch/claude-p. Name any throwaway you create with an 'eval_' prefix.
- Report HONESTLY — a smooth run is a real result (say so); don't manufacture friction, don't hide it.
`

const SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['task', 'outcome', 'friction'],
  properties: {
    task: { type: 'string' },
    outcome: { type: 'string', enum: ['smooth', 'completed-with-friction', 'blocked'] },
    steps: { type: 'string', description: 'the tool-call sequence actually taken' },
    friction: { type: 'array', items: { type: 'object', additionalProperties: true,
      properties: { tool: { type: 'string' }, confusion: { type: 'string' }, fix: { type: 'string' } } } },
    top_gap: { type: 'string', description: 'the single biggest thing that would make composition more intuitive' },
  },
}

phase('Eval')
const evals = await parallel([
  () => agent(`${FRESH}
TASK A — MAKE → CHECK → USE → RUN → SAVE (the full compose loop). Through the MCP only:
1) MAKE a new role 'eval_classify' that labels a short text as exactly one of {question, statement, command}.
2) CHECK it's registered and works (fire it once on "what time is it?").
3) USE it over these 5 texts: ["close the door", "the sky is blue", "are we there yet", "run the build", "it works"].
4) REDUCE the results to a count per label.
5) SAVE the make→use→reduce flow as a reusable cascade 'eval-classify-flow' and RUN it once.
Report the friction at every hop — especially: was making a role obvious? could you tell how to run it over many inputs? how to reduce? how to save+run a cascade? did outputs chain into inputs cleanly?`,
    { label: 'A-make-use-save', phase: 'Eval', schema: SCHEMA }),

  () => agent(`${FRESH}
TASK B — ASK THE SYSTEM (retrieval/use flow). Through the MCP only:
1) Ask the system (its corpus) two questions and get real answers: "where is the embedding model configured?" and "what does the reduce step do?".
2) Read ONE returned record's full content.
Report the friction: was it obvious HOW to ask (which tool, which params)? could you tell what 'spaces' exist + which to search? were the responses readable + high-signal, or noisy/overwhelming? could you follow a result to its full content?`,
    { label: 'B-ask', phase: 'Eval', schema: SCHEMA }),

  () => agent(`${FRESH}
TASK C — DISCOVER WHAT YOU CAN COMPOSE (the discovery flow). Through the MCP only, with NO prior knowledge, figure out:
1) what ROLES exist and what each does; 2) what OPERATIONS/MODES are available (generate? embed? reduce modes?); 3) what SPACES/registries exist; 4) HOW you would chain one role's output into a reduce (the run:// addressing).
Report the friction: how discoverable is "what can I compose with"? Is there ONE obvious place to learn the composition vocabulary, or is it scattered? What did you have to guess about how things connect?`,
    { label: 'C-discover', phase: 'Eval', schema: SCHEMA }),

  () => agent(`${FRESH}
TASK D — RUN AN EXISTING COMPOSITION (the use-existing flow). Through the MCP only:
1) Find an existing reusable composition (a saved cascade — list them).
2) Run ONE of them end-to-end with a reasonable input, and read the result.
Report the friction: could you tell what cascades exist + what each needs as input? Was running one obvious? Did the result come back legible? If none ran cleanly, exactly why (the gap).`,
    { label: 'D-run-existing', phase: 'Eval', schema: SCHEMA }),

  () => agent(`${FRESH}
TASK E — THE FULL KNOWLEDGE LOOP (feed → ask → tally — the newest capabilities, cold). Through the MCP only:
1) FEED: get the file build-prep/cognition-self-improvement/MCP-DESIGN-PRINCIPLE.md into the system's queryable memory (find the tool for ingesting; use it on that one explicit path).
2) ASK: query the system's memory: "what are the rules for designing MCP tools here?" — get real ranked results and read one back.
3) TALLY: run any registered classification role over 4-5 short texts of your choosing, then reduce the outputs to a COUNT PER LABEL (a histogram) using a deterministic rule — no model in the reduce.
Report the friction at each hop: was the ingest tool discoverable + did its response teach you anything? was asking obvious? was the per-label tally achievable with a NAMED rule this time (it required building a custom role in an earlier eval)?`,
    { label: 'E-knowledge-loop', phase: 'Eval', schema: SCHEMA }),

  () => agent(`${FRESH}
TASK F — THE PRODUCTION LINES (the newest face — proven chains, cold). Through the MCP only:
1) DISCOVER whether this system has any pre-built multi-step chains/production-lines you can run as one call (find the tool; list what exists).
2) Pick the one that looks SAFEST + CHEAPEST to actually run, read its description/params, and RUN it with conservative params (prefer a tiny/zero-cost invocation).
3) Read the result back and say what the chain actually did.
Report the friction: could you FIND the chains tool without being told its name? did list/describe teach you enough to choose safely? did the params validate helpfully when unsure? would you have known these chains existed if you hadn't been told to look?`,
    { label: 'F-flows-cold', phase: 'Eval', schema: SCHEMA }),

  () => agent(`${FRESH}
TASK G — THE GOVERNED GROWTH LOOP (the newest face, cold). Through the MCP only:
1) OPERATOR MEMORY: you are about to prepare something the system's human operator will review. BEFORE doing so, discover what the system knows about working with him (find the tool yourself). Name the TWO rules that would most change how you present to him, and say why.
2) PROPOSE A PRODUCTION LINE: propose (NOT create) a trivial new flow — spec {id:'eval_g_probe', label, description, params:{}, body:'return {"ok": true}'}. Report what happened: did it land immediately or surface for approval? Was the boundary (what YOU can do vs what only the operator can) clear from the tool's teaching?
3) RUN A DECLARED CHAIN WITH GATES: run the saved cascade 'registration-gauntlet' with inputs = a small dossier JSON of your own construction (use cognition_info/capabilities to find REAL feature ids — invented ids should be CAUGHT). Report the verdict and whether the gate behavior taught you anything.
Report friction at each hop; honesty rules apply (a smooth run is a real result).`,
    { label: 'G-governed-growth', phase: 'Eval', schema: SCHEMA }),
])

const ok = evals.filter(Boolean)
log(`Eval: ${ok.length}/7 · outcomes: ${ok.map(e=>e.task+'='+e.outcome).join(' · ')}`)
return { evals: ok }
