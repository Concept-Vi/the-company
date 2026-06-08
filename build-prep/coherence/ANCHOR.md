# The Coherence Substrate — an anchor exploration (working name, Tim's to rename)

> **How to read this.** This is NOT a plan, NOT a spec, NOT a decision. It is the *shape of an idea*
> caught early, in the "what if…?" tone it was born in — Tim's and the interface session's thinking,
> mid-thought, deliberately open. It exists to be the **shared anchor** for a wave of research agents:
> everyone reads THIS first so we all hold the same partial mental picture, then each agent explores one
> allocated area across everything available and writes a companion file back beside this one. We are
> NOT looking to confirm what's written here — we want it stress-tested, extended, contradicted, grounded
> in what actually exists. The expansion ratio should be greater than one: leave the idea bigger and more
> real than you found it. If a section makes you think "yes, but actually…", that *but actually* is the
> gold — write it.
>
> The no-humans rule still holds: there is no developer to fill gaps, no reviewer to hold the picture
> together. That constraint is not incidental — it is the entire reason this idea matters. Keep it in mind
> as you read and research: everything here has to work with AI agents as the only builders.

---

## 1 · The problem that started it (the thing we keep tripping on)

We are building a large system entirely with AI agents, across many separate sessions, with no human
developers and no human code review. Each session is competent. Each session, in isolation, does good work.
And yet the system keeps **drifting apart at the seams** — not because any session is wrong, but because
*nobody holds the whole*.

In ordinary human software development, system integrity is held by *people*. A developer remembers that
this function feeds that endpoint, which a screen calls. Code review catches the half-wired thing. The team's
shared memory keeps a thousand invisible threads connected. None of that exists here. When session A builds a
capability and session B is supposed to wire a surface to it, and session C migrates the storage underneath —
there is no single mind that notices when B never happened, or when C left half the old path behind.

We have hit this concretely, repeatedly, in just the last day of work:
- A backend capability (`/api/knobs`, `/api/run-stats`, and ~30 other routes) built in one session with **no
  front-end caller** — it *works*, so no test fails, so it is *invisible*; it just sits there, unused.
- Twelve cognition "authoring" endpoints, fully built on the backend, with **no UI** — a whole screen's worth
  of capability waiting for a surface nobody built yet.
- A feedback system **half-migrated** from one storage mechanism (a per-file JSONL) to a shared one (the
  address-keyed annotation store) — where the *status lifecycle* (pending → applied → dismissed, the way a
  note gets marked acted-on) was silently dropped in the move. An agent (me) then looked at the orphaned
  leftover route, assumed it was dead, and *deleted* it — routing around the unfinished migration instead of
  finishing it. Tim caught it. That single mistake is the whole problem in miniature: **an incomplete
  migration, invisible to the next session, made worse by a reasonable-looking "cleanup."**

Three small gates we built this session each caught one *class* of this:
- **drift** — does the system's written self-description (its MAP/STATE files) still match what actually exists?
- **all-green (suite_health)** — does *every* acceptance test actually pass, run standalone? (Not "is it
  listed," not "did the build that touched it pass" — *every* one, *now*.)
- **reachability** — does every `/api` route reach a caller (a front-end use or a test), or is it a built-but-
  unwired orphan?

Each gate is a *point detector*. Each returns its own ad-hoc shape. Each is forgotten the moment it finishes.
And the moment we ran them seriously, they lit up — drift, dead routes, half-migrations — confirming the
suspicion that **this disconnection is not rare; it is everywhere, structurally, by the nature of the build
method.**

## 2 · The insight (what if coherence were a first-class thing the system *holds*?)

What if the gates are the wrong altitude? They *catch* drift, one symptom at a time, and forget. What if the
thing we actually need is the layer *above* them: a **live, central, continuously-maintained model of the
system's own connectedness** — every element of the system and the state of every connection between them —
that both the human (Tim) and the agents read from and write to?

Not a test. Not a report. A **substrate**: the system's standing self-knowledge of its own integrity. The
detectors stop being standalone tests that pass or fail; they become *contributors* to one shared model. A
"finding" stops being a log line that scrolls away; it becomes a *typed, addressed, living record* with a
state and a disposition, that persists until it is resolved or deliberately accepted.

The shift is from **catching drift** to **holding integrity**. From "this run found 3 problems" to "the system
knows, at all times, exactly where it is whole and where it is not, and what to do about each gap."

And — the part that makes it more than hygiene — what if that model is what an **autonomous build loop reads
to know what to do next**? If the system can *see its own incompleteness*, then a loop can keep finishing the
incomplete things until the model is empty, and refuse to call itself "done" while it is not. That is the thing
a human team normally provides — the holding-together — turned into a substrate the machine maintains itself.

> **The big what-if:** *Could this be the keystone that makes fully-autonomous, large-scale building actually
> converge — builds that always complete and always stay together — because coherence is a thing the system
> continuously knows about itself, rather than something a human has to keep watch over?*

## 3 · What it might BE (the shape, held loosely)

If you made it concrete, it looks like a graph the system keeps *of itself*:

- **Nodes** — the system's elements: backend routes, public methods/capabilities, front-end surfaces and
  components, acceptance suites, registered `ui://` addresses, node-types, migrations, design mockups, voice
  engines… every *thing* the system is made of.
- **Edges** — the relations between them: «route R is called-by surface S», «method M is exposed-at route R»,
  «element E is registered-at address A», «mechanism X migrated-to mechanism Y», «suite T covers capability C».
- **States** — on each node and edge: `wired` · `unwired` · `half-migrated` · `orphan` · `stale` ·
  `by-design` · `covered` · `uncovered`…

A **finding**, then, is not free text — it is a typed node with an address and a state and a *disposition*:
```
{ kind: unwired-route,
  at:   code://api/knobs   (and the ui:// surface that should consume it, if known),
  state: built-no-caller,
  owner: interface-stream,
  disposition: to-wire,          // finish | defer-with-reason | by-design
  since: <when first detected>,
  evidence: <how the detector knows> }
```

The **disposition** is the thing that turns a nag into a tool. Not every orphan is a defect — the voice routes
aren't "broken," they're owned by another session and pending; some backend entry points legitimately have no
UI. So every finding carries a judgment: *finish it*, *defer it with a reason*, or *it's by-design* (and the
by-design ones, accumulated, quietly become the documented architecture). A model without dispositions cries
wolf; a model with them *guides*.

What if the findings are **typed in the same way the rest of the app is typed** — so an "unwired-route" finding
is as much a first-class object as a node-type or a verb or a mode? And what if they are **addressed** — every
finding anchored to a `ui://` / `code://` / `run://` coordinate — so the integrity model is just *another lens
over the same addressed substrate* the rest of the system already speaks, not a parallel universe?

## 4 · Why it belongs in *this* system (the substrate is already here)

This is the part that makes the idea feel less like a megaproject and more like *naming and unifying something
half-built already*. This system has, by Tim's design over a long time, an unusual amount of the needed
machinery in place. An agent who has never seen this codebase needs to understand these pieces, because the
whole bet is that the Coherence Substrate is built **on** them, not beside them (building it as a separate
parallel system would violate the project's own deepest law — *one substrate, more types not more tools* — and
would rot):

- **The address system** (`ui://…`, `run://…`, `code://…`). A universal coordinate space. Every element of the
  UI, every node instance, every code symbol has an address. Clicking a thing, commenting on a thing, asking
  about a thing — all resolve through addresses. *This is the coordinate space the Coherence model would live
  in: every finding anchors to an address. The same address that names a button names the finding about that
  button.*
- **The registry** (node-types, verbs, modes, panels, models — the system's declared truth, the source of what
  *should* exist). *This is half of integrity already: the registry says what should be; the live system shows
  what is; coherence is the comparison.*
- **A typed structured-record substrate** (the system stores structured data as typed records, not loose text;
  there's prior art in the project for "typed fences" — `<format>:<kind>` structured blocks — and registry-
  driven dispatch). *This is the storage format for findings.*
- **The self-description that maintains itself** (`AGENTS.md` / `MAP.md` / `STATE.md`, regenerated from the live
  registry by a method called `refresh_self_description`, with a `drift` check that fails loud if the written
  description falls behind reality). *This already proves the system can hold a factual self-model and keep it
  current. Coherence extends that self-model from "what exists" to "what's connected."*
- **An event log + live SSE stream** (everything that happens emits an addressed event; surfaces reflect live
  state via a stream and never own it — "reflects-never-owns"). *This is how a Coherence interface would stay
  live without owning state.*
- **`capabilities()`** — the system already projects its own registry as a machine-readable self-model.
- **The three gates** we just built — already emit typed-ish findings; they're just not unified, not persisted,
  not addressed, not dispositioned. *They are the first three detectors of the model, today, in embryo.*
- **The autonomous build loop + the reviewer gate** — there is already a "wire" that turns an approved intent
  into a real `claude -p` build, commits it git-safely, and runs a reviewer pass that keeps or reverts. *This
  is the loop that would consume the Coherence model as its worklist.*
- **The RHM (the "right-hand-man") organ** — a chat/explain/at-altitude capability: `chat`, `address_help`
  (explain what's at an address + how to change it + how to use it), `up_translate` (render technical reality
  at Tim's altitude). Surfaces reuse this *one organ* rather than each reinventing explanation.
- **The cognition stream's live model** — a parallel session built a "Concurrent Cognition" layer: a live view
  (Pulse → River → Nodes) driven by `run://` addresses and the SSE stream, reflecting how the system is
  thinking. *It is the same shape as what a Coherence view would be — a live, addressed, reflects-never-owns
  model rendered as a glanceable surface. There is real convergence to mine here.*

It's the **introspective-data-building law** the project already holds — *an operation self-instruments → emits
run-records under conditions → those accrete into a substrate → rollups become knowledge that improves the
operation* — pointed, for the first time, at *integrity itself* as the thing being instrumented.

## 5 · The loop (how it might make autonomous builds converge)

Here is the engine, if it works:
```
read the Coherence model  →  pick the highest-priority unresolved incompleteness
   →  dispatch an agent to finish exactly that connection
   →  the reviewer gate verifies the fix by use
   →  the detectors re-run; the model updates (that finding resolves, new ones may appear)
   →  repeat until the model has no open "finish" findings left
```
The build loop and the reviewer gate already exist. The Coherence model is the missing piece that makes them
*converge* instead of wander: the loop has a worklist that is *the system's own incompleteness*, and a
definition of done that is *the model is empty of open work*. A build cannot quietly leave something half-wired,
because the half-wiring is a standing finding the loop will return to.

What if "done" for the whole system stops being a human's judgment and becomes a *measurable, live property* —
the Coherence model at zero open findings, all dispositions either resolved or deliberately accepted?

There are real questions buried here. Does it actually converge, or can finishing one thing create two new
findings forever? (Probably needs a notion of *net burn-down* and a guard against thrash.) What stops it from
"finishing" something the wrong way just to clear a finding? (The reviewer gate, and the disposition needing
human assent for the consequential ones.) Where is the human still essential? (Almost certainly in the
*dispositions* — deciding what's by-design vs must-finish — and in the genuinely creative/design calls. The
machine can hold and burn down the model; the human still says what the system is *for*.)

## 6 · The interface (Tim wants a full one, RHM-capable)

A first cut is a CLI: `company coherence` — interactive, queryable (by kind, by address, by owner, by
disposition), showing the live burn-down. That's the cheapest way to *see* the model and is in keeping with the
existing single-console pattern.

But Tim's instinct is bigger: **a full interface, in the app, that adopts all the RHM capabilities.** What if the
Coherence model isn't just a list you query, but a *first-class surface* — a sibling of the cognition view —
where:
- the system's coherence is *glanceable* (a shape you read by sight: where it's whole, where it's frayed, the
  burn-down over time) — rendered for Tim's cognition, spatial/relational, not a text wall;
- every finding is *addressed*, so you can click it and drop to the element it's about (the same indicate-an-
  element flow the rest of the app uses);
- the **right-hand-man explains it** — `address_help` / `up_translate` over a finding: "what is this gap, what
  would finishing it mean, what depends on it," at Tim's altitude, because Tim is not a developer and should not
  have to read a call graph;
- you can *act* from it — disposition a finding (finish / defer / by-design), or approve dispatching an agent to
  finish it, through the same consent-gated build wire that already exists;
- it's *live* (reflects-never-owns, via the SSE stream) — findings appear and resolve in front of you as the
  autonomous loop works.

So the Coherence interface would be the operator's bridge over the *integrity* of the whole system — the place
Tim stands to watch a fully-autonomous build keep itself together, and steer it where judgment is needed. The
same RHM organ, the same address system, the same render law, one more lens.

## 7 · The hard parts (where this is fragile, told honestly)

This is the most important section to research, because the idea is only as good as its weakest assumption:

1. **Detection rigor is the whole game.** The three gates today are *grep/string-based* — and already produced
   false positives this session (methods that looked unwired but were called from a file the scan didn't read).
   For a model the *autonomous loop trusts enough to act on*, false findings are corrosive: a wrong "unwired"
   sends an agent to fix nothing, or erodes Tim's trust in the whole instrument. The engineering heart of this
   is **accurate extraction of the real connection graph** — likely AST-level for Python and the front-end, the
   registry, the real route table — not string matching. *Is that feasible on this codebase? How accurately?
   What's the gap between a cheap heuristic and a trustworthy graph? This is the make-or-break, and it is
   exactly Area C.*
2. **Dispositions, or it's a nag.** Without per-finding judgment (finish / defer / by-design) the model screams
   about things that are fine. With it, the by-design set becomes documentation. *How are dispositions decided,
   stored, kept honest, and prevented from becoming a dumping ground that hides real gaps?*
3. **Build-on-not-beside.** The instant this becomes its own store / format / interface divorced from the
   address + registry + event substrate, it violates the project's law and rots into yet another parallel
   system. *It must BE a lens over the existing substrate. How, concretely?*
4. **The convergence promise is strong.** "Always completes / stays together" is a big claim. *Does the loop
   provably burn down? What about findings that legitimately can't be auto-finished (need a human design call)?
   How does it avoid thrash, and how does it represent "blocked-on-human" without stalling?*
5. **Trust and legibility for a non-developer.** Tim drives by sight and by the RHM, not by reading code. *The
   model is only useful to him if it renders at his altitude and the RHM can explain any finding faithfully.
   Can it?*
6. **Cost and cadence.** Continuously maintaining an accurate whole-system graph isn't free. *When does it run —
   pre-merge, on a tick, on demand, incrementally on change? What's the right cadence vs cost?*

## 8 · What I can already see, concretely (the anchors in the real code)

So the research is grounded, here is what is *actually there* right now to build from (verify and extend these):
- `runtime/suite.py` holds the three detectors as methods: `doc_drift()`, `suite_health()`, `reachability()`,
  plus `refresh_self_description()` and `capabilities()`. They already produce structured findings; they are not
  unified, persisted, addressed, or dispositioned.
- `reachability()` already classifies orphan routes by a hand-kept tag (to_build_ui / to_wire / voice_owned /
  backend_only) — an *embryonic disposition system*, already there.
- The `tests/*_acceptance.py` suites are the existing "is it true" checks (116+ of them); `suite_health`
  already runs them all and classifies green / live-dep-skip / red.
- `design/_system/addresses.json` is the live address registry (~79 `ui://` entries) — the coordinate space.
- The bridge (`runtime/bridge.py`) exposes ~112 `/api` routes; ~32 currently have no caller.
- The wire/build loop + reviewer gate live in `runtime/implement.py` + `suite.py` (the decision→build→verify→
  commit→review path).
- The RHM organ is `chat` / `address_help` / `up_translate` in `suite.py`; the cognition live view is
  `canvas/app/src/regions/CognitionView.tsx` driven by `/api/cognition_info` + the `cognition.*` SSE branch.
- There is a coordination file, `MERGE-COORDINATION.md`, where this (interface) session and the cognition
  session talk; the Coherence Substrate spans both streams and would likely be co-owned.

## 9 · Open questions, freely (the what-ifs to pull on)

- What if the Coherence model and the cognition model are *the same kind of thing* — both live, addressed,
  reflects-never-owns models of the system's inner state — and should share machinery (or even be one substrate
  with two lenses: "how it thinks" and "how whole it is")?
- What if "types of finding" is itself a registry the system can grow — so a new kind of integrity check is
  *declared*, not coded as another bespoke gate? (More types, not more tools — again.)
- What if the address system grows a `coherence://` or the findings simply ride existing `code://`/`ui://`
  addresses — which is truer to the law?
- What if the burn-down history *is* the project's institutional memory — the thing that replaces "the developer
  who remembers" — and becomes queryable: "when did this connect, what migration left this, who dispositioned
  that as by-design and why"?
- What if other valuable patterns of the app (the consent gate, the typed records, the modes, the build wire)
  are themselves things the Coherence model should track the integrity *of* — i.e. it's recursive: the model
  watches the coherence of the very mechanisms that maintain coherence?
- What if this is the substrate that finally lets a build run overnight, unattended, across both streams, and be
  *trusted* in the morning — because it could not have called itself done while incomplete?

---

## For the research agents — the spirit of this

You've read the shape. Now go to your allocated area and explore it **across everything available** — the
codebase, the existing substrate, external patterns and prior art, your own reasoning. You were given an *area*,
not a list of things to find, on purpose: we don't want to bias you toward confirming this doc. Bring what's
actually there. Where the idea is naive, say so. Where it's missing something this system already has, surface
it. Where there's prior art (in this repo, or in how mature systems hold architectural integrity), bring it.
Where it's harder than this doc admits, prove it.

Write a **full** companion file (no shallow skim — your area was sized to have real content; cover it). Anchor
everything to real evidence (`file:line`, real route names, real patterns) where you can, and mark clearly what
is *observed* vs *inferred* vs *your idea*. Write it to live beside this anchor so Tim can read all the areas
together and reason over the whole, then write the real artefact — which the cognition session will then weigh
in on with him.

Leave the idea bigger and more real than you found it.
