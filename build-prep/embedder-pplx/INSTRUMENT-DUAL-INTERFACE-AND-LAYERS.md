# The Instrument as a Dual-Interface Control Surface · the Multi-Layer Re-Embeddable Model

*Stretched out from Tim's 2026-06-15 think-aloud. Living doc. Part of the embedder-pplx set
(see VISION-OVERVIEW.md). This is the conceptual heart: what the instrument IS becoming.*

---

## 1. The instrument is something we USE — not a viewer

Tim: *"an instrument is something that I and you use… I can see myself using it heaps of different ways,
whatever ways I want."*

The shift: the surface has been a **projection viewer** (pure-read lenses over fixed data). Tim is naming it as
an **instrument** in the full sense — a thing an operator *plays*: loads data into it, reads the same data many
ways, reconfigures, keeps or discards readings, layers them. The lenses (nucleation, strain, separator,
connections, scale) are the *readings*; the instrument is the *hands* that choose what to read, how, in what
frame, at what resolution — and what to keep.

This is a genuine widening of scope, and it surfaces a tension worth naming (§5): the projection ENGINE stays a
pure read; the INSTRUMENT around it gains authoring (embed / layer / load / configure). Both are true at once.

## 2. The dual interface — one capability set, two faces (Tim + agents)

Tim: *"the interface is a dual interface, both for me and for the agents through the MCP tools."*

Every capability the instrument exposes has **two faces over ONE engine**:
- **The visual face** (Tim) — a paper-aesthetic affordance: a dial, a picker, a gesture on the wheel.
- **The MCP face** (agents) — the same capability as a tool an agent calls.

This is already the Company's pattern (the bridge serves the surface AND the MCP face; `capture` exists as an
MCP tool and a bridge route over the SAME `capture_corpus` seam). The rule going forward: **a new capability is
not done until it exists on BOTH faces, driven by the same registry, so they cannot drift.** The visual face and
the tool face are projections of one underlying verb — exactly the seed's "same object, two coordinate systems."

Why it matters: Tim drives by sight; agents drive by protocol. The instrument is the shared body both inhabit —
a [[collective-cognition]] surface. An agent embeds a layer via MCP; Tim sees that layer appear on the wheel and
overrides it with a gesture; the agent reads the override. One circuit, two hands.

## 3. The multi-layer, re-embeddable model — the big one

Tim: *"I might read the same data heaps of times, sometimes I would override the previous, other times I would
store them, there's no limit to how many different layers can be run and added."*

This breaks a hidden assumption in the current store: **one item → one vector**. Tim wants **one item → many
LAYERS**, where a layer is *one reading of the thing under a chosen frame*. The data isn't a fixed embedding;
it's an accumulation of readings.

**A LAYER = (item) read under a chosen (embedder · context-frame · resolution · params) → vector(s) + provenance.**
- the **embedder** (pplx-dense, pplx-context, a future code/visual embedder — the [[mode-loadout-registry]])
- the **context-frame** (read alone, or in the context of parent P — §2a of the leverage spec: selective)
- the **resolution** (MRL truncation — 2560 / 1024 / 512; quantization — fp/int8/binary)
- the **params** (the dial, the rung, anything that shaped the read)
- **provenance** (who/when/why — agent or Tim, which run, which intent) → feeds [[project-introspective-data-building]]

**The operations on layers** (each a dual-face verb):
- **read / re-read** — embed the item under a frame → a new layer. The same data, read again, differently.
- **override** — replace the current layer in a slot (the provisional read; the working copy).
- **store** — keep a layer alongside others (no replace) — accumulate.
- **stack / compare / overlay** — multiple layers coexist; the instrument can show one, diff two, or blend.
- **promote** — a provisional layer → a ratified one (the GATE; §5 + the keystone). Sample → ratified discrete.

**Layers ARE the seed made literal.** The seed: *one object, many coordinate systems sharing an origin.* A
layer is one coordinate system over the item. "Centre here," "set poles," "read in the context of P," "at
resolution R" are all **frame-choices** — and a frame-choice, persisted, IS a layer. Origin-selection (seed §8)
generalizes: every framing operation is the same primitive — *choose the frame, optionally keep it.*

**Layers accumulate on the address** — directly [[project-address-accumulation]] (registry addresses as
accumulation points; conversations write new fields onto the address). A layer is a field written onto the
item's address. The address grows readings over time; the instrument is where you write and read them.

**No limit (Tim's "no limit to how many layers"):** the layer set per item is itself a registry — fractal with
everything else ([[the-heart]]). Add a layer = add a row. The instrument's job is to keep this legible, not to
cap it.

## 4. Framing is the unifying primitive

Pulling §3 together: **centre · poles · context-parent · resolution · embedder · time** are not separate
features — they are all *the operator choosing a FRAME to read the data in.* The instrument is a frame-chooser;
a kept frame is a layer; a lens is how a framed reading is drawn. This is the clean mental model to build toward:

> choose a frame → read the data in it → see it (a lens) → keep it (a layer) → compare/override/promote.

Every capability below (MODEL-CAPABILITIES-AS-AFFORDANCES.md) slots into "choose a frame." Every storage
concern (DATA-SUBSTRATE-POSTGRES-SUPABASE.md) is "persist the framed readings as layers."

## 5. The tension to name: pure-read engine vs authoring instrument

The standing law: *"the instrument is a PURE READ — no resolve/approve/dispatch."* Tim now describes the
instrument **loading data, re-embedding, overriding, storing layers, reconfiguring** — those are WRITES.

The resolution (not a contradiction — a layering):
- **The PROJECTION engine stays pure-read.** Drawing a lens never mutates data. Reading a frame computes; it
  does not commit. This protects the "instrument never lies / never acts behind your back" property.
- **The instrument GAINS explicit, operator-driven authoring** — embed a layer, override, store, load data,
  configure a space. These are *deliberate verbs the operator (Tim or an agent) invokes*, never side-effects of
  viewing. They are safe by the Company's existing model: simple-consent + git-revert + the GATE (provisional
  layers are revertible; promotion is the ratifying act).
- So the law sharpens to: **reading is pure; writing is explicit and gated.** The wheel you look at is a pure
  projection; the wheel you *play* writes layers when you tell it to.

This is the single most important decision in Tim's message to get right, because it changes what the
instrument is allowed to be. Recommend confirming this framing with Tim before building authoring verbs.

## 6. The FORM standard holds for all of it

Tim: *"minimal text, intuitive, not written for a developer… the interface is half of the whole thing."*

Every affordance added here is held to the FORM bar already in force on this surface ([[feedback-render-for-cognition]],
[[feedback-whole-screen-verification]], the loop's design rubric): built on the paper design system (tokens, no
bespoke values), minimal text, a navigable visual/spatial surface (not a control panel of labelled sliders), and
verified by use at both viewports + a design-critic. A "layer manager" must not become a developer's table of
rows — it must be a *spatial, legible stratigraphy* the eye reads. The interface is half of done; a capability
exposed as developer-UI is NOT done.

## 7. Open questions for Tim (the forks I can't decide alone)
- **The pure-read→authoring evolution (§5)** — confirm the instrument may write (gated) layers, or keep it
  strictly read with authoring living elsewhere?
- **Layer identity / slots** — is "override" per (item × embedder × frame) slot, or a free stack with a
  "current" pointer? (Affects the schema — DATA-SUBSTRATE doc.)
- **How visible are layers by default** — show the "current" reading only, with layers on demand (text-minimal),
  or always hint the stratigraphy?
- **Scope of "everything can be rewritten"** — the whole store is provisional (Tim: "the database hasn't had any
  attention"); how far to redesign now vs incrementally (DATA-SUBSTRATE doc).
