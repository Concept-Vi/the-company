---
type: constitution
register: prescriptive
module: verdict_panels
aliases: ["verdict-panels — constitution", "verdict_panels — constitution"]
tags: [company, constitution, verdict-panels, registry, cognition]
governs: [GC7]
relates-to: ["[[Company Map]]", "[[runtime — constitution]]", "[[roles — constitution]]"]
status: living
---

# verdict_panels/ — module constitution

**Is:** the **file-discovered VERDICT-PANEL registry** (GC7 — Tim: the jury is "like a panel, easy to
add additional roles"). A verdict-panel = declared SEATS (distinct lens roles) + a quorum — the
perspective-DIVERSE jury (run_jury = self-consistency of one role's varied draws; run_panel =
agreement across DIFFERENT judgments). The seat contract: every seat's output carries
`grounded: bool`; the combine is deterministic (grounded-seats ≥ quorum — L2, no model). A failed
seat is a recorded DISSENT, never a silent pass. Add a seat = edit the row; add a panel = add a FILE.
Loader: `runtime/verdict_panels.py`; executor: `cognition.run_panel`.

**NAMING (a LAW-0 lesson, 2026-06-10):** this dir is `verdict_panels/`, NOT `panels/` — `panels/` is
the pre-existing brain-authored declarative UI-panels module (JSON field-definitions the canvas
renders). The first draft landed here as `panels/registration_confirm.py` — a parallel-system
collision caught at build time. Two different nouns, two dirs.

**THE FLOOR:** a verdict-panel JUDGES — flags/confirms for the operator's review; never
resolve/approve/dispatch.

## The rows

- **registration_confirm** — grounding (confirm_registration) · altitude (voice_lens) · claims-fit
  (element_fit_lens); quorum 2/3. The s102 re-jury of the 222 no-quorum dossiers runs through this
  panel on the operator's yes.
