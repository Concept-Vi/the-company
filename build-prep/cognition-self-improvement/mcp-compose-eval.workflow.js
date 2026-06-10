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
])

const ok = evals.filter(Boolean)
log(`Eval: ${ok.length}/5 · outcomes: ${ok.map(e=>e.task+'='+e.outcome).join(' · ')}`)
return { evals: ok }
