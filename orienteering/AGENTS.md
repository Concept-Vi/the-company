---
type: constitution
module: orienteering
register: prescriptive
aliases: ["orienteering — constitution", "Orienteering"]
tags: [company, constitution, orienteering, knowledge-space]
governs: []
status: unconfirmed
coverage: { files_read: all, files_total: all, last_read: 2026-06-26 }
relates-to: ["[[Company Map]]", "[[Vault Conventions]]", "[[Orienteering Index]]"]
governed-by: ["[[Vault Conventions]]"]
---

# orienteering/ — module constitution

**Is:** the **terrain ledger** — a descriptive map of *what the Company is and where it physically
lives.* The Company is not just this folder: its engines, recall index, certs, service units, and a
tail of scattered work/data live **outside** `~/company`. One `terrain-entry` note per thing
(`entries/`), indexed by [[Orienteering Index]]. It is **descriptive, not prescriptive** — a map, never
a blueprint; its own layout must never be copied as "how the Company should be structured."

**Guarantees:** every thing in the Company's orbit has exactly one entry · each entry states what it
is, where it is (absolute `path`), what it connects to (typed links), and **how much of it was actually
read** (`coverage`, with `last_read`) · `status` is only ever a **Tim-confirmed** lifecycle (default
`unconfirmed`) — the ledger never asserts live/dead/dormant by inference · membership (`relation`) and
graph edges (typed link keys) are kept distinct.

**Where new things go:** a new thing appears in the Company's orbit → add `entries/<slug>.md` from
`templates/entry.md` + a line in [[Orienteering Index]]. A path moves or dies → update that entry's
`path`/`move_intent`/links (the `foundation` move-in is the worked example).

**To extend:** add a `terrain-entry` (the schema lives in [[Vault Conventions]]); add a new typed
relation kind simply by using a new frontmatter key (the relation vocabulary is open); never assign a
lifecycle `status` you cannot confirm.

**Seam:** governed by [[Vault Conventions]] (one schema, one vault, one home). [[Orienteering Index]]
is a **region sub-map linked from [[Company Map]]** — not a competing home. Entries describe things
that mostly live *outside* this repo, so their links often resolve cross-location by name.

**The drift detector (BUILT):** `runtime/orienteering_drift.py` — declared INTO the coherence substrate (same finding model as `coherence_detect`). EXACT gate `entry-path-missing` (a ledger path vanished → fails `company suites` via `tests/orienteering_drift_acceptance.py`); positive-only `orbit-uncatalogued` (home-dir things absent from both the entries and `_orbit-dispositions.json` → surfaces, never auto-fails, never auto-classifies). Both render in `company coherence`. `_orbit-dispositions.json` is the declared out-of-orbit registry (the orphan-routes pattern).

**Never:** assign `status` by inference (only `unconfirmed` unless Tim confirms) · claim coverage you
didn't do (`files_read` is honest) · nest an `.obsidian/` here (one vault: `~/company`) · let an entry
become a prescriptive design (this region only ever *describes*) · treat membership `relation` and the
typed link keys as the same thing.

## The schema (quick reference; canonical in [[Vault Conventions]])
`type: terrain-entry` · `register: descriptive` · `relation` (company/external/connected/candidate/
resource) · `kind` (external: work/data/config/engine) · `status: unconfirmed` (Tim-confirmed only) ·
`coverage: {files_read, files_total, last_read}` · `path` (absolute) · `created` · `last_active` ·
`size` · `git_remote` · `secrets` · `move_intent` · typed relations as needed (`indexed-by`,
`launched-by`, `depends-on`, `data-of`, `derived-from`, `aimed-at`, `prospected-for`, `relates-to`).
Cross-cutting tags only: `#voice #model #memory #embedding #fabric #mcp #control #image`.
