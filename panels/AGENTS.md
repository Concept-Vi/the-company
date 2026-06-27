---
type: constitution
register: prescriptive
module: panels
aliases: ["panels — constitution"]
tags: [company, constitution, panels, self-mod]
governs: []
relates-to: ["[[Company Map]]", "[[runtime — constitution]]", "[[canvas — constitution]]"]
status: living
---

# panels/ — module constitution

**Is:** brain-authored **declarative UI panels** — JSON field-definitions whose fields edit real config. The "others" tier of self-modification (between writing a node-type and writing arbitrary code).
**Guarantees:** a panel is **pure declarative data** (no code) — fields bind to real config values; the registry overrides any guessed select-options with real registered values (path-of-least-resistance); applying a panel is **git-reversible**.
**Where new things go:** a new panel = ask the brain (`propose_panel` → operator approves → `apply_panel` writes JSON here, git-committed).
**To extend:** describe the panel to the RHM; it proposes the JSON; the operator approves.
**Seam:** authored via [[runtime — constitution]] (`propose_panel`/`apply_panel`), rendered by [[canvas — constitution]].
**Never:** put code in a panel (that's an extension — [[extensions — constitution]]) · hand-author select-options that should come from the registry · apply without operator approval.

## What's in here

The declarative panel definitions — JSON field-specs the brain authors, each binding its
fields to real config values. The **live set is owned by the single source** — see
[[Company Map]] for what's currently registered (do not enumerate it here; that's the rule
in [[Vault Conventions]]). Each panel is data, not behaviour: it describes *which config to
edit and how*, and the registry fills in the real option-values so a proposed panel can't
drift from what the system actually knows.

## Relates to

- **Authored by** [[runtime — constitution]] — the brain proposes a panel and writes it
  here through `propose_panel`/`apply_panel`, git-committed on operator approval.
- **Rendered by** [[canvas — constitution]] — the canvas reads the JSON and draws the fields
  generically, the same way it renders any object from its declaration.
- **Sibling tiers of self-modification** — between writing a node-type (nodes) and writing
  arbitrary code: nodes / [[panels — constitution]] / [[extensions — constitution]].

## Read next
[[Company Map]] (the live picture + what's registered) · [[canvas — constitution]] (what draws these) · [[Concepts and Principles]] (why the tiers of self-modification are shaped this way).
