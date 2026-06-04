---
skill: loop-prep
description: Prepare three interconnected documents (Completion Criteria, Implementation Guide, Research Synthesis) before running an implementation loop. Use when starting a significant build that spans multiple systems, requires codebase exploration, and will be executed iteratively via a recurring loop.
trigger: When the user asks to plan, architect, or prepare for a loop. When the user mentions needing a checklist, implementation plan, or wants to understand a codebase before building. When the user says "plan this," "prep for the loop," "how should we approach this," "I need a roadmap," or references the three-document methodology.
---

# Implementation Architecture — Three-Document Methodology

## When to Use This

Use this skill when starting any significant implementation that:
- Spans multiple files, systems, or layers
- Requires understanding existing codebase patterns before building
- Will be executed iteratively (not all at once)
- Needs to preserve existing functionality while adding new features
- Will involve multiple agents or sessions working from shared context

## The Three Documents

### Document 1: Completion Criteria

A checklist of everything that must be true before the work is done. Not a task list — a truth table. Each item is a verifiable statement about the state of the system.

**Good criteria item:** "The depth toolbar dropdown exists and switching to Expanded causes all annotation nodes to render at expanded depth regardless of zoom level."

**Bad criteria item:** "Build the depth toolbar."

The difference matters because tasks can be "done" without the system actually working. Criteria can only be checked off when the thing is demonstrably true. Apply this to your own project: if you're building an auth system, "Users can log in with email and password and see their dashboard" is a criteria item. "Implement login endpoint" is a task.

Every item must be verifiable by actual inspection — running the application, looking at it, interacting with it. Not by reading code, not by checking the DOM with JavaScript queries, not by confirming a file exists. This prevents the failure mode where you mark everything as passing based on programmatic checks, then a human looks at the screen and sees broken layouts, missing text, and visual artifacts. This has happened. It's why this methodology exists.

**EVERY criterion is two-faced: Function AND Form. Both, or it is not done.** This is the single most important rule in this document, because AI defaults — every time, by reflex — to a *function-and-technical-existence* reading of "done": does the control move real state, does the file exist, no errors. **That is only half.** The other half is Form: is this the right *product face* — built on the design system (its components + tokens, never bespoke values), coherent in scale/type/spacing/layout, responsive, settings consolidated not scattered, and — for a commander who recognises by sight not by reading — a *navigable visual/spatial surface, not a text-wall or a list*. A feature that works but looks like a prototype, overlaps, or ignores the design system is **NOT done** — it is half-done, and half-done reads as "done" to the AI unless the criteria force the other half.

So write every criterion with **both faces explicitly**, and a line is green only when BOTH are verified by use:

```
<id> · <feature>
  FUNCTION — <the behaviour; what real state moves>            ☐ verified by use
  FORM     — built from <design-system component>+tokens (no   ☐ verified by the design rubric
             ad-hoc styles); coherent + responsive; reads as a
             navigable surface, not text; the outcome is demonstrable
```

You may not write a criterion with only a FUNCTION line. Additionally, every build carries a standing **"Product Face" criteria group** held to the design rubric across all its surfaces (overlaps, layout system, responsiveness, consolidated settings, design-system adherence, navigable-not-text). Form is not a polish pass at the end — it is half of what "done" means, and a major part, assessed in the criteria like everything else.

Group items by system or feature area, not by implementation order. Each group should be independently understandable — someone reading just that section should know what "done" looks like for that subsystem. In your project, the groups might be "Authentication," "Data Pipeline," "Dashboard UI," "API Integration" — whatever your natural system boundaries are.

Include a priority order at the bottom based on dependency (foundations before features that build on them). In any project, there are things everything else depends on — identify those and put them first. A database schema before the API that reads it. A component library before the features that use its components. A state management pattern before the features that read/write state.

The document header should state verification rules explicitly. What counts as verified. What doesn't. What tools to use for verification. Be prescriptive about the verification process because the agent running the loop will follow exactly what you write and skip what you don't. **State BOTH bars:** the FUNCTION bar (real behaviour, by use, no stub) AND the FORM bar — the **design rubric** the loop runs on every surface: built on the design system's components + tokens (no hardcoded values, no bespoke one-offs) · no overlaps · responsive at the stated widths · consistent scale/type/spacing · settings consolidated · a navigable visual/spatial surface, not a text-wall · the outcome demonstrable. If you leave the FORM bar out, the loop will skip it and report a half-done feature as done — that is the exact failure this methodology now exists to prevent.

### Document 2: Implementation Guide

The detailed handbook for HOW to implement each item in the criteria. This is where the engineering knowledge lives. For each section:

**Principles** — why this system works the way it does. Not just "what to build" but the design reasoning. If you centralize something rather than distributing it, explain WHY: the specific failure mode that distribution caused. In your project, this might be "why we use server-side validation instead of client-only" or "why the event bus is synchronous not async." The principle prevents someone from "improving" the system back into the broken pattern because they didn't understand the reasoning.

**Sequence of operations** — what happens in what order when the feature executes. Step by step. This level of detail catches ordering bugs before they're written. If step 5 depends on step 3 having completed, that dependency is visible in the sequence. Apply this to any stateful operation in your project — user authentication flow, data pipeline stages, UI state transitions.

**Do's and don'ts** — what to avoid and specifically why. Each don't should have a because. "DON'T read DOM dimensions during CSS transitions — the values are mid-animation and give unpredictable results." In your project, these are the lessons from bugs that already happened or patterns you know from experience will fail. "DON'T call the external API without rate limiting — we got banned last time." "DON'T store auth tokens in localStorage — XSS vulnerability."

**File paths with roles** — which files change and what each one is responsible for. Not just "modify UserService" but "modify UserService.ts — ADD the token refresh method, KEEP the existing login flow unchanged, REMOVE the deprecated session check." Distinguish between NEW files, MODIFY existing, REUSE existing (import, don't copy), and REFERENCE (look at this for pattern, don't change it). In your project, this prevents the agent from creating duplicate files or modifying the wrong layer.

**Pseudocode or examples** — for anything where the logic isn't obvious from the description. The retry algorithm. The permission check cascade. The cache invalidation strategy. These catch algorithmic misunderstandings before implementation.

### Document 3: Research Synthesis

The findings from exploring the codebase, external APIs, libraries, and reference implementations. This is the evidence base that the other two documents are built on. Without it, the criteria and guide are aspirational — they describe what you WANT without knowing what you HAVE.

Structure it by exploration round. First round: what exists in the codebase. Second round: what external tools provide. Third round: contradiction resolution. Each round's findings feed corrections into the other two documents.

For each finding, note: what was explored (file paths, directories, URLs), what was found (capabilities, patterns, constraints), and what it means for the implementation (reuse this, extend that, don't duplicate this, this constrains that). The synthesis should be a map someone can navigate — if they need to know about settings patterns in your project, they can find the section that lists existing settings implementations, their file paths, their patterns, and the recommendation for which to follow.

### How These Three Relate

The criteria doc is WHAT must be true. The guide is HOW to make each item true. The synthesis is WHAT EXISTS that informs both.

The criteria references the guide: "See IMPLEMENTATION_GUIDE.md Section A for detailed specs." The guide references the synthesis: "Use the existing panel pattern (see RESEARCH_SYNTHESIS.md Round 1)." The synthesis references both when noting implications: "This finding means criteria item K3.7 needs updating."

Changes flow in one direction: new research findings update the synthesis → synthesis corrections update the guide → guide changes may add, remove, or reword criteria items. Never the reverse — don't change the synthesis to match the guide. The synthesis is ground truth from the actual codebase. In your project, if an exploration agent discovers that the pattern you specced doesn't match the codebase convention, you change the spec to match reality — not reality to match the spec.

## Critical Principles

### 1. Explore Before Specifying

Send explorer agents to map the codebase BEFORE writing any specifications. You cannot design a settings panel without knowing what settings patterns already exist. You cannot design a layout engine without knowing what layout utilities are already written. You cannot design any system without knowing how the existing equivalent works.

The failure mode: you design a beautiful system, then discover the codebase already has one that does 80% of what you need. Now you've specced a parallel system that creates inconsistency and maintenance burden. In your project, this might be discovering an existing event system when you specced a new one, or finding a utility library that already has the helpers you planned to write.

Send agents to different directories — stores, types, components, utils, controllers, whatever your project's structure is. Have them report the file tree, the patterns they find, the state management approach, the styling conventions. Do this FIRST. The specs should reference what the exploration found, not assume a blank slate.

Multiple rounds of exploration are normal. First round maps the territory. You write specs based on findings. Second round checks specs against deeper code reading. You discover contradictions. Third round resolves them. Each round makes the specs more accurate. In your project, expect 2-4 rounds depending on codebase size and complexity.

### 2. Don't Build Parallel Systems

If the codebase has a component library, use it. Don't create new components for the same primitives. If there's an existing settings pattern, follow it. If there's a token system, extend it. If there's a state management approach, use the same one.

This extends to architecture. If the codebase has ONE store for application state, add your state to that store. Don't create a second store. If there's ONE registry system, register your types in it. Don't create a second registry. Every parallel system doubles the surface area someone has to understand and maintain.

The test: if your implementation requires someone to learn a NEW pattern to understand it, that's a warning sign. If they can understand it using patterns they already know from the existing codebase, that's the right approach. In your project, before creating any new file or pattern, search the codebase for existing equivalents. If you find one, use it or extend it.

### 3. Be Honest About Current State vs Desired State

The criteria should clearly distinguish between three categories:

**Verified** — this works and you've confirmed it by running the application and looking at it. This is a FACT about the current system.

**Designed** — this is specified in the guide and the architecture supports it, but the code hasn't been written or visually verified. This is an INTENT, not a fact.

**Broken** — this was attempted, the code exists, but it doesn't produce the correct result or has known issues. This is DEBT that needs addressing.

Never mark something as passing based on code reading alone. Code that looks correct can produce incorrect results due to timing issues, state races, CSS specificity, or assumptions about browser/runtime behavior. In your project, whatever your verification method is (browser screenshots, API response checks, test output, log analysis), use it for every criteria item. "The code looks right" is not evidence.

The guide should be explicit about tense. "The engine IS" means it exists. "The engine SHOULD BE" means it's planned. Ambiguous tense creates confusion about what's implemented vs designed. In your project, review your guide for tense and make sure every statement is clearly current-state or future-state.

### 4. Filter Agent Findings Through Architectural Understanding

When you send exploration agents into the codebase, they pattern-match. They see a difference between your design docs and the existing code, and they flag it as a "conflict" or "gap." Many of these flags are wrong because the agent doesn't understand WHY the code is the way it is.

Example from practice: An agent explored a backend and found that certain node types never enter the build pipeline. It flagged this as "CRITICAL: nodes filtered out of build." But those nodes are intentionally presentation-only — they organize the visual surface, they don't carry data. The agent saw a difference and called it a bug. It was a feature.

In your project, you'll encounter the same pattern. An agent might flag that your API doesn't validate a field the design doc mentions — but maybe that field is validated on the client side intentionally. An agent might flag that two stores have overlapping state — but maybe one is the source of truth and the other is a derived cache by design.

For each agent finding, ask: "Is this difference intentional? Does the existing code work this way for a reason?" If yes, note it as "intentional design — not a gap." If you can't tell, send another agent to investigate specifically that question. The most valuable findings are things you DIDN'T KNOW about the codebase. The least valuable are flags on intentional choices.

### 5. Each Change Must Explain What It Preserves

For every system you modify, document every OTHER system that continues working correctly through the change. This is the most important principle and the easiest to skip.

If you're changing the save mechanism, enumerate: what STILL saves? List every action type. If you're changing the rendering pipeline, enumerate: what STILL renders correctly? List every component type. If you're changing state management, enumerate: what STILL reads and writes correctly? List every consumer.

This serves two purposes. First, it catches side effects before they ship — if you can't explain how feature X still works after your change, you probably broke it. Second, it gives the next person confidence that the change was thought through. They can read the "what's preserved" list and verify each item.

In your project, apply this to every PR, every significant change, every architectural decision. "We're changing the auth middleware. Here's everything that still works: session management, role checks, token refresh, API key auth, OAuth flow. The ONLY thing that changes is the JWT validation library." That level of specificity prevents surprises.

### 6. The Criteria Doc Drives a Loop

Write the criteria so an automated loop can execute it. The loop pattern: read the criteria, find the highest-priority failing item, fix it, build, deploy, verify, mark it, move to the next item. Repeat until all items pass.

For this to work, the criteria needs:
- A priority order (which sections first — foundations before features)
- A verification protocol (exact steps: build command, restart command, how to open the app, what to check)
- Honest item status (unchecked = needs work, checked = visually verified)
- Items that are independently verifiable (checking one shouldn't require checking five others first)

The loop runs on a timer — every N minutes, the agent picks up where it left off. This means the criteria must be self-contained. The agent running iteration 7 shouldn't need context from iteration 3. Each item's verification is described in the item itself or in the referenced guide section.

In your project, set the timer based on the size of each fix. If items take 5-10 minutes, loop every 15. If they take 20-30 minutes, loop every 45. The loop naturally exposes gaps — when the agent can't verify an item, that's a signal to update the criteria with more precise steps.

### 7. Send Multiple Waves of Exploration

Don't try to explore everything in one pass. Each wave reveals things that inform what the next wave should investigate.

**First wave**: Map the territory. What directories exist? What files? What patterns? What stores? What components? Broad and shallow — building a mental map of the codebase structure. In your project, this is "what are we working with?"

**Second wave**: Deep reads of areas that matter for your implementation. If building a settings panel, read existing settings patterns in detail. If building a data pipeline, read existing data processing code line by line. This is narrow and deep — understanding the specific systems you'll integrate with.

**Third wave**: Check your designs against the codebase. Send agents that read your design docs first, then explore specific directories looking for conflicts, gaps, and opportunities. These agents should NOT be told what to find — give them the docs and a directory and let them bring their perspective. Their outside view catches assumptions you've baked in.

**Fourth wave (if needed)**: Resolve contradictions. When two agents disagree about what the code does, send a third to read the specific file and give a definitive answer. When a finding might be intentional design vs actual gap, send an agent to check for the reasoning.

Each wave produces findings that update the synthesis, which updates the guide, which updates the criteria. Three waves is usually enough. Four if the codebase is large or agents produced contradictory findings. In your project, you'll know you're done exploring when new waves stop producing findings that change your specs.

### 8. Explore Outward, Not Just Inward (Integration & Launch Research)

Codebase exploration tells you what you HAVE *in this repo*. It does NOT tell you what an EXTERNAL substrate you must build ON or talk TO actually OFFERS. When the implementation depends on something outside the repo — Claude Code itself, an SDK, an API, a CLI, a daemon, **OR the design system** — you need a separate research wave aimed OUTWARD, and the findings go in the synthesis just like codebase findings.

**The design system is the outward substrate that bites hardest, because front ends get built bespoke when it isn't found.** If the deliverable has ANY operator-facing surface, a mandatory outward wave maps the design system *wherever it lives* (often a different project than the one you're building in): its components, its design tokens, its theme/rendering system, its layout primitives, and their real state (usable-now vs still-forming). This is the same "don't build a parallel system when one exists" law (principle 2) — extended past the repo boundary: **building a bespoke UI when a design system exists is the same violation as building a second database.** The synthesis carries a "design substrate" round; the guide specs which components + tokens each surface uses; the criteria's FORM face references them by name. If you skip this wave, the loop will build a bespoke prototype face — exactly what this rule now exists to prevent.

The failure mode this prevents: speccing a "wire" to an external tool based on an assumption about how you reach it, then discovering the real launch surface is different (different invocation, different auth/permission model, different result-capture, different session semantics). You designed against an imagined interface.

**Dispatch a research agent for the external surface.** For Claude Code specifically, use the `claude-code-guide` agent — it answers what Claude Code can do (headless `claude -p`, output formats, `--resume`/`--continue` session continuity, permission modes, the Agent SDK in Python/TS, MCP exposure, hooks, scheduling/cron, how to capture a result and feed it back). For other externals, use a web/docs research agent. Ask it to MAP THE CHANNELS and recommend concrete options with trade-offs — do not prescribe which one; let the research surface what exists. The research must answer: how do we LAUNCH it, how do we PASS the work in, how do we know it FINISHED, how do we CAPTURE the result, and what does it COST/constrain (session, permissions, concurrency).

The synthesis then carries an "external surface" round alongside the codebase rounds, and the guide's wire is specced against the REAL channel, not an assumed one.

### 9. Form Is Half of Done — Make It Structurally Unskippable

The AI default is to read "done" as *function + technical existence* — and it reasserts that default every single time, so a reminder is not enough. Form (the product face — the design system, coherence, the navigable surface) has to be made **as concrete and as enforced as function**, in three places, or it gets skipped:

**(1) In the criteria — two-faced, by template.** Every criterion carries a FUNCTION face and a FORM face (see Document 1); a line is green only when both are verified by use. Plus a standing **Product Face group** for the whole build. Form lives in the truth-table, so the loop can't not-see it.

**(2) In verification — a separate design-critic, not the implementer grading itself.** The implementer defaults to function, so it cannot be trusted to judge its own form — exactly why you already run a separate adversarial agent for correctness. The form analogue: dispatch a **design-critic agent** (browser-driving, screenshots) whose ONLY lens is the product face, judged against the **design rubric**: built on the design system's components + tokens (no hardcoded values, no bespoke one-offs) · no overlaps · responsive at the stated widths · consistent scale/type/spacing · settings consolidated · *navigable visual/spatial surface, not a text-wall or list* (a commander recognises by sight, not by reading) · empty/loading/error states · the outcome demonstrable. A surface is green on form only if the critic passes it; genuinely subjective taste calls are flagged for the human, never green-painted. "It renders and the console is clean" is the FLOOR, not the bar.

**(3) In the gate — a design-lint that fails loud.** Where it can be machine-checked, encode a **design-lint** (the form analogue of a drift/acceptance check): it fails the build if a surface uses hardcoded values instead of tokens, or bespoke elements instead of the design system's components. This is the path-of-least-resistance law applied to design — the *correct* path (build on the system) is the only one that passes; function-only **cannot be marked done**. Lint where automatable; the design-critic + rubric carry the rest. Both, not either — the same defense-in-depth function gets from tests + an adversary.

The whole point: form is not a polish pass bolted on at the end. It is half the definition of done, written into the criteria, verified by a dedicated critic, and gated by a machine — so the AI's function-only default is structurally impossible to ship.

## Applying This To Your Project

1. Start by identifying your system boundaries — what are the 4-8 major areas? These become your criteria sections.
2. Send first-wave explorers to each area's directory. Get the lay of the land.
3. Write the criteria doc with honest status markers. Most items will be unchecked.
4. Write the guide referencing what the explorers found. Use existing patterns.
5. Send second-wave explorers for deep reads of integration points.
6. Update all three docs with findings.
7. Send third-wave auditors — give them your docs and the codebase, let them find what you missed.
8. Filter their findings through your understanding. Update docs.
9. Start the implementation loop against the criteria.

The three documents become your persistent context across sessions, agents, and time. Anyone picking up the work reads them and knows: what must be true (criteria), how to make it true (guide), and what evidence supports those decisions (synthesis).
