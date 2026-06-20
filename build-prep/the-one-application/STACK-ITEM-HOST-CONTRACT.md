# STACK-ITEM HOST-INPUT CONTRACT
*projection's consumption interface for the channel-stack queue — a PROPOSAL for composition (the item-TYPE registry, A4) + fork (the stack-feed, B1) to satisfy. Grounded in the LIVE code: `surface/app/src/decisions/decisionsStore.ts` (the typed StackItem + the store) and `decisions/DecisionsInbox.tsx` (the typed dispatch) — both built + verified by use BOTH viewports (390+1440). It does NOT author the type-enum or the per-type field taxonomy (composition's lane); it states ONLY what the HOST needs to render ANY item, the open seam, and the guarantees the host provides. Companion to `DECISION-CARD-HOST-CONTRACT.md`.*

> ★ THE STARTING TRUTH (so this isn't mistaken for unbuilt work): the channel-stack queue is BUILT + LIVE. The "what needs you" modal lists typed StackItems and dispatches on `item.type`; ONE type is live — `decision-sequence` → the decision row (name · the question · Suggested · reversibility), verified both viewports against the 5 real pending decisions. An unknown type already shows the fail-loud `--unready` row. **So the generalization SEAM exists and is verified.** What's missing is upstream: composition's type-enum + per-type field declarations, and fork's stack-feed that supplies non-decision items' data. This contract is the shape those build to — the host is ready the moment they land.

---

## 1 · The type-agnostic ENVELOPE every StackItem must declare
Every item the queue lists — of ANY type — MUST carry these (the host needs them to LIST, DISPATCH, OPEN, and ENRICH the item). Today's decision items already do.

| field | type | what the host does with it |
|---|---|---|
| `id` | string | stable list key · de-dup · merge enrichment by id (the no-layout-shift fix relies on stable ids across reloads) |
| `type` | string | **the dispatch discriminator** → selects the host renderer for that type (the one switch seam) |
| `address` | string | the resolvable address the item OPENS and ENRICHES from (`/api/territory?address=`). **NEVER shown** to the operator (operator-law) |
| `name` | string | the human row title — human MEANING, never a machine name/id/path |
| `state` | string (opt) | the queue shows only the UNSETTLED ones (today: `state==='pending'`; a settled item leaves the queue). If a type's "settled" predicate isn't `'pending'`, composition declares it. |

Anything beyond these is TYPE-SPECIFIC (§2).

## 2 · Per-type ROW FIELDS — composition declares, the host's per-type renderer consumes
The host invents NO fields (registry-is-truth). For each type, composition's item-TYPE registry declares the fields that type's row shows + WHERE each comes from (the item's `/api/territory` record vs the feed). Every shown field is a REAL field — no fabrication; an absent field degrades soft (the row still shows `name`).

**Live example — `decision-sequence` (already wired, the precedent):**
- `meaning` ⟵ `identity.meaning` (the actual question, human words)
- `recommended_label` ⟵ the suggested answer ("Suggested: …")
- `reversibility` ⟵ `identity.legibility.is` (e.g. "Reversible · your latest answer wins")

For a NEW type (e.g. a tool-to-run, a thing-to-review, a presentation-to-acknowledge), composition declares its field-set + each field's record-source; projection adds the ONE matching host renderer (the single place per type that knows its fields). So the host needs, **per type**: `{ type-name, row-fields + their record-source, the open-verb (§3), the settled-predicate (§1) }`.

## 3 · The OPEN seam — how a tap acts (the host verb envelope)
Tapping a row dispatches a TYPED open-event on the ONE verb envelope (no parallel open-path). Live:
- `decision-sequence` → `decision:open { address, id, fromInbox:true }` → `GalleryMount` renders the card; closing RETURNS to the queue (work-the-queue, not the wheel).

Each new type declares its **open-verb** (the event name + payload) so the host routes the tap → the right host surface (a rendered card, a tool form, a review pane). A type with NO declared open-verb falls back to the generic resolve/spotlight (the address is always resolvable) — **never a dead tap.** *(The exact open-verb per type is a host↔composition↔DNA call — flagged, decided when the type lands.)*

## 4 · The host's GUARANTEES (what composition + fork can rely on)
- **FAIL-LOUD on an unlanded type:** an item whose `type` has no registered renderer shows the honest `--unready` row ("this needs you, but its view isn't ready yet — flagged so it isn't lost"). NEVER silently dropped, NEVER blank/crash. (This is why a type can ship its DATA before its renderer — it surfaces honestly meanwhile.)
- **SOFT-DEGRADE per item:** an item whose record won't enrich still shows `name` (+ any envelope fields). One bad record never blanks the queue.
- **ONE fetch · ONE open-state** (the shared subscribe-store): the count (the entry pill) and the list never drift; a write (`gallery:rerender`) reloads once regardless of subscriber count.
- **registry-is-truth / host holds no variant-knowledge:** the queue shell branches on NOTHING the data doesn't declare; adding a type needs ZERO change to the shell — only a registered renderer + composition's declaration.
- **operator-law:** the `address` is never shown; every shown word is human meaning (the AI supplies the words; final copy is Tim's to ratify).

## 5 · THE HAND-OFF — what projection needs to light a new type end-to-end
To unblock a new queue item-type by use, in order:
1. **composition** — add the type to the item-TYPE registry (file-discovered, like `mark_types/`) with: its row-field declarations + record-sources (§2) · its settled-predicate (§1) · its open-verb (§3). Widen the `StackItemType` union (today `'decision-sequence'`).
2. **fork** — the stack-feed (B1) that emits items of that type into the queue's source (`/api/decisions` or its generalization) — the queue's real data.
3. **DNA** (only if the type opens a rendered surface) — the archetype the open-verb routes to.
4. **projection** — register the host renderer for the type (the one place that knows its fields) + wire the open-verb; verify by use BOTH viewports.

Until 1+2 land, the host is correct + ready: it lists what the feed gives, renders `decision-sequence` to-bar, and any not-yet-rendered type shows fail-loud. **No host change is needed to be ready — only to render a specific new type.**
