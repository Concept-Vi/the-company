# Annotated example — building view `C1` (Inbox) from the blueprint alone

> **Purpose.** Show the deterministic build-TO-schema path for ONE view, so a fresh builder sees exactly how
> the blueprint's parts compose into a component. This is an *annotated walkthrough* (the B1 proof is
> COMPLETENESS + CONSISTENCY, not a full FE rebuild) — every fact below is traced to a registered source.

---

## Step 1 — read the surface-spec

`design/blueprint/surfaces/J3/C1.json` (GENERATED). The fields that drive the build:

```jsonc
{
  "id": "C1",
  "title": "Inbox — three lanes, clean",
  "platforms": ["desktop", "mobile"],     // build BOTH (responsive @1440/768/390)
  "represents": ["INB-lanes", "EVT-now"], // the features this view shows (register.json features[])
  "home_journey": "J3",                   // its tree home (lives under surfaces/J3/)
  "journeys": ["J3", "J5", "J7"],         // ALSO reachable from J5 and J7 (the web — see navgraph)
  "cross_journeys": ["J5", "J7"],         // the cross-edges the tree dropped, restored by address-refs
  "addresses": ["ui://activity", "ui://inbox"]   // the REGISTERED addresses this view carries
}
```

The spec tells you: this is the Inbox, it surfaces the 3-lane inbox + the now-view, it carries two addresses,
and it sits on three journeys (so links INTO it must exist from J3, J5, J7).

## Step 2 — find the component (component-inventory.json)

```jsonc
// region "inbox":
{ "region": "inbox", "component": "canvas/app/src/regions/Inbox.tsx", "status": "built",
  "addresses": ["ui://inbox", "ui://inbox/build-review", "ui://inbox/build-intent", "ui://inbox/coa"] }
// region "activity":
{ "region": "activity", "component": "canvas/app/src/regions/Activity.tsx", "status": "built",
  "addresses": ["ui://activity", "ui://activity/replay"] }
```

So `C1` is rendered by **`Inbox.tsx`** (+ the now-view from `Activity.tsx`). Both are `built` — real files.

## Step 3 — find the FORM target (the mockup)

`design/mockups/C1-inbox-desktop.html` is the markup the React component reproduces. It already carries the
exact addresses and rides the design-system:

```html
<link rel="stylesheet" href="../design-system.css">          <!-- the GENERATED tokens -->
<section data-ui-ref="ui://inbox">                            <!-- full-string carrier, from addresses.json -->
   <article data-ui-ref="ui://inbox/build-review"> … </article>
   <article data-ui-ref="ui://inbox/coa"> … </article>
</section>
```

## Step 4 — the addresses you carry (addresses.json — never invent)

(Values below copied verbatim from `addresses.json` — do not paraphrase; the corpus's "no fiction" law binds
this doc too.)

| address                   | region  | represents  | capabilities (corpus)         | code (powering)                  |
|---------------------------|---------|-------------|-------------------------------|----------------------------------|
| `ui://inbox`              | inbox   | INB-lanes   | openable·presentable          | runtime/suite.py:inbox_lanes     |
| `ui://inbox/build-review` | inbox   | WIRE-review | pointable·presentable·spotlit | runtime/suite.py:review_verdicts |
| `ui://inbox/coa`          | inbox   | INB-coa     | pointable·presentable         | runtime/suite.py:coa             |
| `ui://activity`           | activity| EVT-now     | presentable·driven            | runtime/suite.py:now             |

Carry these as `data-ui-ref` exactly. Anything not in `addresses.json` is an orphan — register it first.
(Note: the corpus `driven` capability maps to the live model's `drivenReadOnly` — see CONNECTION-CONTRACT §1.)

## Step 5 — the connection (CONNECTION-CONTRACT.md)

- **State (IS):** read `GET /api/capabilities → node_states`; paint each item's `@state` from
  `node_states[state].render` (token + icon). E.g. a `build-review` item that `failed` shows the fail token +
  its error string.
- **Command (SHOULD-BE — I2/I4):** a click on `ui://inbox/coa` ships `{verb, address:"ui://inbox/coa", args}`
  to the address-keyed seam. Click INDICATES + CONSENTS — the RHM proposes; a consequential resolve goes
  through governance + see-and-approve. Wire to the existing `/api/resolve` (operator-only) until `/api/act`
  lands.
- **Context (SHOULD-BE — R2):** when the operator is at `ui://inbox`, `GET /api/context?address=ui://inbox`
  loads the events/decisions/chat joined to it (decay-bounded).

## Step 6 — gate the FORM

```
python3 design/_system/check.py --target canvas/app/src --fail-on   # must exit 0
```

No off-token hex/px, no bespoke element. Then verify by use: drive the inbox in the browser, resolve an item,
see the lane update. Done = both faces verified, never a code-read.

---

## What this example proves (CONSISTENCY)

- The surface-spec's `addresses[]` ⊆ `addresses.json` (registered, not invented). ✓
- The inventory component for region `inbox`/`activity` is a **real file** under `canvas/app/src`. ✓
- The mockup carries the same full-string `data-ui-ref` addresses. ✓
- The view's journey membership (`J3·J5·J7`) is recoverable by `navgraph.py` (C1 is one of the cross-edge
  proofs). ✓

Every fact traces to a registered source — the build is deterministic, not interpretive.
