---
type: synthesis
title: Architecture
---

# Architecture

The Company is a **typed compositional dataflow system** — a graph of deterministic-code and AI nodes wired by structured-output contracts, running over a heterogeneous local compute fabric, reflectively aware of its own code AND its own context, operated and grown through one interface fronted by an aware right-hand-man. The *same machinery* builds external products and the Company itself. The disk-reclaim job that produced the founding pipeline (scan → extract → judge) was the smallest possible instance of the same shape.

## The compositional substrate

**The topology is the program.** No single model "does anything"; the wiring computes — the way no neuron is intelligent but the network is. The Company is an *invariant compositional system*: a small fixed set of node types and a typing discipline, composed infinitely. Invariant primitives, variant compositions.

**Node taxonomy** (*examples; more will surface*):
- **Survey nodes** — deterministic, exhaustive, materialise structure from reality (filesystem walks, parsers, crawlers, queries). Cheap, exact, trivially parallel.
- **Interpret nodes** — AI, observation only, no verdicts. Turn raw or structured input into richer typed observations.
- **Reduce / shape / route nodes** — code or AI; group, join, rank, dedup, diff, filter, dispatch. Often best done in code, sitting between AI stages to shape work.
- **Synthesise / judge nodes** — AI, subjective and relational. Where judgement happens.
- **Gate nodes** — human or verification sign-off. Tim is a gate node at the top of the stack; irreversible actions are gates lower down.

**Composition patterns** (*examples; more exist*): chain, fan-out/fan-in (map-reduce), router, critic-loop, ensemble, tournament/debate, branch-and-merge. Graphs nest as nodes — unbounded depth without unbounded complexity at any one altitude.

**Design law:** *every step that can be deterministic, is*. Survey and reduce nodes are exact and reliable; AI nodes are subjective and fallible. Spend AI only on irreducibly-subjective steps. The AI output of one stage is just structured data the next code stage operates on.

## Structured outputs are the type system

Each edge between nodes has a type, schemas nest, and types are registered. The result is **type-directed composition**: node A can feed node B if and only if A's output type satisfies B's input type. This is the discipline that makes "set up any chain through the interface" tractable — the right-hand-man can only propose pipelines that type-check.

Schemas have three origins (*examples; more will surface*): shipped primitives, composed at design time by Tim with the right-hand-man, synthesised at runtime from the task. A schema is itself a buildable artefact — *context to build* — not a fixed piece of infrastructure.

The Company does not invent its type registry from scratch: the existing Vi Chat universal type registry and the typed-fence substrate are the starting layer to lift in.

## Addresses and variable resolution

**Address is the universal primitive.** An address is simultaneously: where data persists, where downstream context loads from, where the coherent record lives, and what provenance points at. One addressing scheme does all four jobs.

**Variable resolution** is the trigger: a phase becomes runnable the instant its input variables can resolve — the moment the data it depends on exists at its known address. No scheduler decides this; *presence of data* decides it. This is **declarative dataflow** (a phase is a promise that resolves when its inputs do), and the runtime form is a **blackboard architecture**: a shared structured space every participant reads and writes, with activation by pattern-match on the space.

A consequence: **the orchestration is emergent from the data dependencies, not hand-scripted.** Defining a workflow means *declaring* what each phase reads and where its result goes; execution is automatic from presence-of-data. Composing a pipeline is declaring intent, not coding.

**Stigmergy** is the coordination model that falls out of this: agents do not message each other — they read and write traces in the shared addressed space, and presence-of-data activates the next phase. This is leaderless coordination, which is what *thousands of equal agents, no boss* requires.

**Idempotency and memoization** are built in: resolved addresses are cached; re-running a phase yields the same result; the system is crash-proof and resumable for free. Interrupt anywhere, it picks up wherever the addresses left off.

The session-with-Tim is a phase in this graph — specifically a **durable human-task await**: the pipeline parks itself when it hits something only Tim can supply, costs nothing while parked, and resumes the instant his input lands at its address. A hundred workflows can be parked waiting on him, each resuming independently when serviced.

**Branch-and-merge of decisions is first-class.** Because everything is addressed and event-sourced, forking a decision-session and exploring an alternative is a cheap replay — "what if we'd decided differently" becomes an operation, not a regret.

## The twin substrates

**Code drives the deterministic nodes; context drives the AI nodes.** Prompts, schemas, examples, retrieved knowledge, personas, the principles in this folder — all of it is *context-code* that programs AI the way C programs the CPU. The Company has two co-managed, version-controlled instruction substrates.

The vault (Obsidian — non-locking, extensible, links-native) is the **context-codebase**. This folder, the exchanges archive, the memory entries, are all source files for the AI side.

The system is **homoiconic**: its description and its executable substrate are the same markdown. It can read and write its own source, both substrates. This is what makes *recursive construction* possible — the Company can rebuild itself because it can see itself. The "whole map of all code and context, known by the Company" is a unified graph over both substrates; the candidate physical substrate is the Vi Memory graph / graph-editor.

## Event-sourcing and the synthesis/source split

**The Company's record uses CQRS / event-sourcing**: an append-only immutable log of *what actually happened* (Tim's verbatim messages, decisions, session trajectories, observed outcomes) underneath a derived, always-current synthesis on top. The log carries time; the synthesis is timeless. The exchanges archive is the start of that event log.

**Persist the trajectory, not the endpoint.** Tim's input across a session is a path, not a value — what he rejected, the order he moved, the redirections, the reasoning. Capturing the trajectory matters for two reasons: the endpoint without its *why* is brittle and cannot be re-applied when context shifts; and the trajectory is the richest possible training signal for the model of Tim. Decisions become *views* derived from the log, replayable and forkable.

## The interface — the Tim-node's API

The interface is **the most expensive node's API**: every other piece of the system exists to make calls to it rare, small, and high-value. The right-hand-man is the conversational face of the one entity — front, brain, translator:

- **Voice** — the coherent front of the one entity. Talking to it is talking to the Company.
- **Brain** — the model of Tim (the twin). Built from the corpus + the context files. Its most important output is *knowing when it cannot predict Tim* — that abstention signal is what triggers escalation and protects Tim's time. The architectural pattern is **selective prediction with a reject option**.
- **Translator (decision-compiler)** — bidirectional. Compiles ground-level technical forks *up* into Commander-altitude value-choices in Tim's terms (never "commit A or B?"; always "the fast-but-fragile path or the slower-durable one — here's what each costs your goal and here's the recommendation"). Compiles Tim's high-level answers back down into technical action.

**Co-presence and symmetric agency.** The right-hand-man sees Tim's screen, selection, current run state, what he clicked — its context is grounded in the live situation, not a cold chat. And it can do anything Tim can do in the UI, narrating while doing it. *Setup for me and with me.* The GUI plane and the conversational plane are two synchronised projections of one source of truth: a click updates the conversational context; a spoken instruction drives a GUI action.

**Natural-language → graph.** Tim describes intent; the right-hand-man proposes a typed pipeline, shows it in the GUI, Tim refines by voice or click, then runs.

## The escalation ladder

Subsidiarity made operational. From cheapest to most expensive:

1. **Ground truth** — the verbatim exchanges, the actual code, observed reality. Most factual conflicts arbitrate here; re-derive from what was actually said or what the code actually does.
2. **The model of Tim** — explicit (the context files + the laws here) plus implicit (the twin, trained from Tim's corpus). The two can check each other: when the twin's call contradicts a principle in the context files, the disagreement *is* the escalation signal.
3. **Real Tim** — last resort, never the default. The genuinely-irreducible direction calls, the value/taste judgements only he can make.

Provenance grades the signal everywhere: *Tim actually said/chose this* is gold-grade and the only thing that trains the twin; *the twin inferred this* is working-grade and never masquerades as ground truth — this prevents model-collapse (the twin learning from its own echoes).

## The inbox: chief-of-staff triage

Tim has an inbox; he does not work it. The right-hand-man (with the twin) runs it as **three lanes**:

- **Resolved-for-you** — the twin was confident; logged for audit; Tim can spot-check but needn't.
- **Batched walkthroughs** — related decisions grouped so Tim handles a theme in one sitting rather than scattered pings.
- **Live escalations** — the genuinely irreducible, brought in **COA-style packages**: 2-3 fully-worked options with trade-offs *and a recommendation attached*, so Tim ratifies-or-overrides in seconds rather than evaluating from cold.

The right-hand-man's job is keeping lane 3 tiny and lane 1 large. **Every item is drillable** — the briefing is the top layer, but Tim can always pull the thread down to ground level on demand (progressive disclosure). The interface itself has *modes* — brief-me-fast, teach-me-deeply, decide-for-me — switched by the live context, since *context is a consequence of what Tim is doing at the time*.

**Attention-budgeting and forecasting.** Because Tim is the bottleneck, his time is *scheduled*, not interrupted. The system forecasts upcoming demand on him and batches it: *this week roughly N minutes across these themes; nothing urgent until Thursday.* Predictable, batched, never surprise-interrupting.

## The autonomy ratchet

Tim's involvement is high while uncertainty is high and tapers as the model of him sharpens — but never reaches zero, and *spikes* whenever the Company moves into new territory where it has no pattern of him yet. **The Company estimates and requests Tim, rather than running on a fixed schedule** — the involvement curve is a measured output, not a setting. The system *earns* its autonomy by demonstrating it can predict Tim, and the dial is visible so he can set the confidence threshold himself.

## Tensions held, not simplified away

- **Dynamic context vs reproducibility.** If context is a consequence of what Tim is doing, two runs are not identical by default. Resolution: **run snapshots** — capture the *resolved* context and the exact graph of each run, so any run is replayable, auditable, forkable.
- **Power vs safety.** The right-hand-man with screen, control, code, and context access is exactly the thing that, mis-composed, could do real damage. Resolution: **irreversible nodes carry mandatory confirmation gates** — safety as a structural graph property, not a bolt-on.
- **Infinite composition vs legibility.** Unbounded graph depth fights "Tim must see and guide it." Resolution: **altitude views** — the same graph viewable at Commander altitude (collapsed, intent-level) down to ground level (every node).

## The genetic kernel

Not MVP-prioritisation. The minimal capability set such that everything else is buildable *from within*. Success test: *after the kernel exists, can Tim grow every further capability without leaving the bridge?* If yes, growth is internal and recursive. If any growth still requires dropping back to the CLI or to me, that's the friction the Company is meant to kill.

Taking the "it is all the same operation" principle seriously, the irreducible seed is small:

- **Resolution engine** — the addressing + variable-resolution + reactive-dataflow substrate that turns presence-of-data into execution.
- **Constitution** — this folder, made machine-enforceable so the principles become checked invariants, not just prose.
- **Interface** — the right-hand-man (voice + twin + decision-compiler) plus the Commander's bridge surface it lives on.

Everything else — workflows, pipelines, the knowledge body, products — is *declared content* on top of the kernel.

**What exists today, fragmentally:**
- *Compute fabric* (a node-runtime layer): the local vLLM/Ollama/embedders stack. The batch-runner pattern from the AppData job (`~/appdata-cleanup/extract.py`) is a working concurrent-node template.
- *Context store*: the vault, this foundation folder, the memory entries.
- *Reflective map* (partial): the Vi Memory graph / graph-editor substrate.
- *Type registry* (partial): Vi Chat's universal type registry + typed-fence substrate to lift in.

**What is gestured but not built:** the resolution engine itself, the constitution-as-machine-enforceable layer, the right-hand-man, the bridge interface, the build loop. Roughly a third assembled.

## Synthesis: Tim's existing projects are organs of one Company

The Vi Chat type registry → the contract system. The vault / Obsidian Builder → the context-codebase. Vi Memory / graph-editor → the reflective self-model. The local AI stack → the compute fabric. The AppData job → the first real pipeline + the observability pattern. **Universal Composition applied to Tim's own portfolio**: the organs were built under different project names; this is the body that unifies them. Nothing here requires building from scratch — only naming the body and wiring the organs.

## Open

- The composition engine itself (declarative pipeline runtime over the addressing substrate) is the missing core piece.
- The type registry as live infrastructure (not just an idea in another project) needs to be lifted in and made the runtime.
- The right-hand-man's three organs (voice, twin, decision-compiler) are each gestured at; the twin's training pipeline from the corpus is the highest-leverage missing piece.
- The bridge interface — the actual UI Tim operates in — is at the seed stage (the viewer patterns from the AppData job).
- *What the structured outputs are, where they come from, when they get set up, what connects to what* remains the explicit open design question Tim named.
- Whether the standing judgement layer (the smart model sitting above the wide extraction workers) defaults to a local big model running on the fabric, or to the conversation model, or to the twin, is open.
- The boundary between this folder and TIM.md will need to settle as both evolve. They overlap in subject; the right factoring will emerge.
