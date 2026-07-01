---
type: constitution
register: prescriptive
module: extensions
aliases: ["extensions — constitution"]
tags: [company, constitution, extensions, self-mod, generated]
governs: []
relates-to: ["[[Company Map]]", "[[canvas — constitution]]", "[[runtime — constitution]]"]
status: living
---

# extensions/ — module constitution

**Is:** the brain-authored **arbitrary UI components** (`.tsx`) — the most powerful, **operator-only** tier of self-modification. A GENERATED tree, grown by the system, not hand-edited.
**Guarantees:** every component is **build-GATED** before it goes live — `canvas/app/syntax-gate.cjs`, an **AST checker** that rejects non-`react` import/export specifiers, dynamic `import()`, `require()`, and external-URL literals (it is NOT a regex allowlist). A passing component is **lazy-loaded inside an error boundary**, so a bad one degrades to a single dead panel, never a white screen. Each apply is git-committed → **revert recovers**. Operator-approval is governance, not a safety guarantee — the floors are the gate + error boundary + git-revert + single-user machine.
**Where new things go:** a new component = ask the RHM (`propose_extension` → operator approves → `apply_extension` gates + writes here). Never create one by hand.
**To extend:** describe the component to the RHM; it writes the `.tsx`; the gate guards; the operator approves.
**Seam:** authored + gated via [[runtime — constitution]] (`propose_extension`/`apply_extension`/`_gate_extension`); loaded by [[canvas — constitution]].
**Never:** hand-edit this tree (it is generated) · relax the gate · import anything but `react` · let an extension hold authoritative state.

## What's in here

The generated `.tsx` components the system has authored for itself — the operator-only,
arbitrary-code tier of the live UI. This tree is **written by the brain, not by hand**, so
there is no curated list to maintain here: what exists at any moment is whatever the RHM has
proposed, the operator has approved, and the gate has admitted. Read the tree itself, or ask
the RHM, for the current set — do not enumerate it in prose that will rot.

## Relates to

- **Authored/gated by** [[runtime — constitution]] — the RHM proposes a component
  (`propose_extension`), the operator approves, and `apply_extension` runs the
  `_gate_extension` AST check before writing the `.tsx` here. The gate, not this folder, is
  the line a component must cross.
- **Loaded by** [[canvas — constitution]] — admitted components are lazy-loaded inside an
  error boundary, so a failed one collapses to a single dead panel rather than the whole
  surface.
- **The arbitrary-code tier** beside nodes / [[panels — constitution]]: where a node is a
  governed C2 type and a panel a constrained presentation, an extension is *unconstrained
  `.tsx`* — the most powerful and therefore the most gated rung of self-modification.

## Read next
[[canvas — constitution]] (what loads these) · [[Company Map]] (the whole picture) · [[Concepts and Principles]] (why self-modification is tiered and gated).
