# CONNECTION-CONTRACT — the FE ⇄ backend ⇄ corpus agreement (per address)

> **What this is.** The importable spec the [blueprint builder session](blueprint/README.md) reads to know
> *how a surface talks to the running system*. It is the S0 contract written as a build-spec: the canonical
> address grammar, the one union per-address record, what the FE **sends** on a command, what it **reads** for
> state and context, and how an element **declares** its address.
>
> **Honesty (IS vs SHOULD-BE).** This contract is a **proposal both halves adopt** — it is not all live today.
> Each clause below is tagged **IS** (built + reachable now) or **SHOULD-BE** (the target the builder builds
> to; net-new). Never write a built FE as if a SHOULD-BE clause already holds. Source of the IS/SHOULD-BE
> split: `.build/interactive/spec/loop-research/design-substrate.md` PART 2 + the Completion-Criteria S0/S1/S2/
> S3/S5/I1–I7/R1–R2 lines. The grammar + element-level registry + served state are **IS** (S0/S1/S5 closed);
> the address-keyed command (`/api/act`), the annotation/chat attach, and the address-keyed context resolve are
> **SHOULD-BE** (I2/I6/I7/R1/R2 — Phase-2, not yet built).

---

## 0 · The canonical address grammar (IS — S0 closed)

One grammar, full-string carrier, one union registry record.

```
ui://<region>/<element>[/<sub>][/@state]
```

- `region` — a coarse grouping (one of the 10 live regions: `toolbar · rail · canvas · inspector · inbox ·
  chat · activity · walkthrough · workshop · tabbar · models`). See `_system/addresses.json`.
- `element` / `sub` — the addressable thing inside the region (`build-review`, `model-field`, …).
- `@state` — OPTIONAL state selector for state-applicable addresses (the 7 `NODE_STATES`; see §3).
- **Carrier:** the **FULL** `ui://…` string, verbatim, in `data-ui-ref` on the DOM element (see §4) and as
  the key in `addresses.json`. NOT a bare ref. (The live app historically carried bare refs like
  `data-ui-ref="inbox"`; the migration to full strings is the F4 lane — corpus is already full-string.)

A second scheme exists for **live graph-node instances**:

```
run://<graph>/<node>
```

`ui://` addresses a **UI element** (a designed surface region); `run://` addresses a **running graph-node
instance**. The annotate-vs-operate safety seam does **not** rest on the scheme alone (see §2, governance).

---

## 1 · The union per-address RECORD (IS for the read fields · SHOULD-BE for `tier`)

What every address carries so the FE, the backend, and the corpus agree. This is the union of the corpus
record (`addresses.json`) and the live `UI_REGISTRY` (`runtime/suite.py`). Today the corpus stores the
compact form; the projected union (S0 `UnionAddressRecord.from_corpus`) normalises it to:

```jsonc
"ui://inbox/build-review": {
  "kind": "chrome",                              // {chrome|field|canvas|panel|ext} — the live resolver
                                                 // dispatches on this. SHOULD-BE on corpus rows (added by
                                                 // the S0 projection; corpus compact rows omit it today).
  "region": "inbox",                             // IS — coarse grouping (corpus)
  "title": "Build review card",                  // IS (live) — human label
  "represents": "WIRE-review",                   // IS — feature-id → register.json features[] inventory
  "code": "runtime/suite.py:review_verdicts",    // IS — powering code (refcheck-validated)
  "capabilities": {                              // IS — OBJECT of bools (live shape; opt-in, absent=false)
    "pointable": true, "spotlit": true, "presentable": true,
    "openable": false, "drivenReadOnly": false
  },
  "resolve": { "domHandle": "ui://inbox/build-review" },  // chrome/field/panel/ext → querySelector key
  // OR for kind=canvas:  "resolve": { "cameraRef": "<node-id>|*" }
  "states": ["idle","ran","cached","stuck","failed"],     // applicable NODE_STATES (for @state addressing)
  "tier": "SURFACE"                              // SHOULD-BE — governance posture for COMMANDS at this
                                                 // address (AUTO|SURFACE|CONFIRM|LOCKED). I4 is address-keyed.
}
```

**Encoding reconciliations the builder must respect (Verified specifics):**
- **Capabilities:** corpus stores a string-LIST; the canonical FE-facing shape is the bool-OBJECT (matches the
  live `Capabilities` Pydantic model the FE already reads). The S0 projection converts.
- **Vocabulary:** the corpus uses `driven` / `driven-read-only`; the live model has only **`drivenReadOnly`**.
  Map `driven`/`driven-read-only` → `drivenReadOnly`.
- **`kind`** is absent from the compact corpus rows — it is the exact field the live resolver dispatches on, so
  the S0 projection adds it. A built FE element with no resolvable `kind` is an orphan.

Capabilities glossary (from `contracts/ui_info.py`): `pointable` (can be clicked/indicated) · `spotlit` (can
be spotlit by `show`/attention) · `presentable` (can be presented in a walkthrough) · `openable` (opens a
panel/detail) · `drivenReadOnly` (the live app can drive/scroll/spotlight it read-only — it is NOT a mutate).

---

## 2 · What the FE SENDS on a command (SHOULD-BE — I2/I4, the `/api/act` seam)

> **NET-NEW.** The live bridge today exposes a per-verb route table (`POST /api/{run,set,move,node,connect,
> delete-node,chat,build-intent,resolve,propose,react,revert,…}`) and these routes are **not address-keyed**.
> The contract below (verb + address + args, behind a future `/api/act`) is the I2 target the builder builds
> to — DO NOT call a built FE as if `/api/act` exists; wire to the existing per-verb routes until I2 lands.

A command issued from the surface is the triple **verb + address + args**:

```jsonc
POST /api/act                       // SHOULD-BE (I2) — the unifying address-keyed seam
{
  "verb": "build-intent",           // an EXISTING bridge capability (the 7-verb whitelist; see below)
  "address": "ui://inbox/coa",      // WHERE the command was issued (the clicked element's full ui:// string)
  "args": { "spec": "make this lane calmer", "scope": "ui://inbox/coa", "why": "too loud" }
}
```

- **The address is the locus; the verb is an existing backend capability; args are that verb's existing body.**
- **Whitelist (IS — enforced backend-side, E6):** the dispatcher honours `run · propose · build · consult ·
  show · panel · extend`. `apply` / `delete` / file-write are **unreachable** from the agent face; approval is
  **operator-only** (the agent cannot self-approve). A built FE never assumes a verb outside this set.
- **Click INDICATES + CONSENTS — it does NOT execute (Tim, 2026-06-04 · IS as governance principle):** a click
  ships the address as the locus; the RHM **proposes** in chat; a consequential action goes through governance
  + see-and-approve. Click ≠ execute. The bare canvas RUN stays AUTO (immediate) — it must not regress.
- **Governance rides the ADDRESS, not the verb (SHOULD-BE — I4):** a command's tier is resolved by
  `address → tier` (the record's `tier` field, §1), NOT by verb. AUTO → acts immediately; CONFIRM/LOCKED →
  PROPOSES → see-and-approve → then acts. The annotate-vs-operate seam is enforced by **capability + tier**
  (a `drivenReadOnly` cap + a CONFIRM/LOCKED tier gate a mutating command), with the `ui://`/`run://` scheme
  as a routing **hint**, not the gate. The seam must be **visible** before commit (the I5 visible-signal is a
  reserved Tim design call — build a reasonable default, flag for Tim).

---

## 3 · What the FE READS for state (IS — S5 served) and context (SHOULD-BE — R2)

**State (IS — `capabilities().node_states` is served, S5 closed):**
- `GET /api/capabilities` → `node_states` — the served registry of the 7 states, **each carrying a `render`**
  (token + icon + shape). The FE paints an element's `@state` by looking up `node_states[<state>].render` →
  the corpus token. Status is shown **by sight**, from the served registry — never a hardcoded enum, never a
  client-side `isPortal` ternary.
- The 7 states: executing nodes carry `idle · ran · cached · stuck · failed`; reference-resolved nodes
  (portals) carry `live · empty`. A `failed` node carries its error string.
- For a live node's *current* state, `GET /api/graph` + the SSE stream (`GET /api/stream`) carry the node's
  derived state; SSE events are stamped with the `ui://` address in `meta` (S2 — `events_since`/`/api/stream`
  carry `address`), so an "…at this address" event view is a filter, not new plumbing.

**Context (SHOULD-BE — R1/R2, the address-keyed auto-resolve):**
- `GET /api/context?address=ui://inbox/coa` (NET-NEW) → the addressed slice: the events / decisions / chat /
  annotations / feature / code joined to that address, so the RHM's context loads for **where the operator is**,
  not everything. A relevance/recency **decay** bounds it (no flood). This is the keystone the corpus enables
  but the backend must add (R2 replaces keyword-keyed context-stuffing).
- The backend holds the operator's **current locus** (R1 — none today): set on indicate (a click ships the
  address as the locus), readable by the RHM.

---

## 4 · How an element DECLARES its `ui://` address (IS — both sides carry `data-ui-ref`)

- **Carrier:** `data-ui-ref="<full-ui://-address>"` on the DOM element. Corpus mockups already do this with
  full strings (e.g. `C1-inbox` carries `data-ui-ref="ui://inbox/build-review"`); the live app migrates its
  bare refs to full strings (the F4 lane).
- **Canvas nodes:** declare `data-ui-ref="run://<graph>/<node>"` (the instance), modelled by the registry as
  an instance of its `ui://canvas/node` kind. Canvas targets resolve via `cameraRef` (node-id → editor
  camera), NOT `querySelector` — the `kind` field (§1) carries this dispatch difference.
- **Registration (IS — extend-by-registration):** the address MUST exist in the unified registry
  (`/api/ui_info` ∪ `addresses.json`) or it is an **orphan** (`parse.py` / `check.py` catch it). The builder
  **never invents an address** — it carries only addresses that are registered. The design-lint (`check.py
  --target … --fail-on`) is the builder's FORM gate.

---

## Reconciliation summary — the three halves meeting in the middle

| Concern              | Corpus (`addresses.json`, mockups)        | Live app (`UI_REGISTRY` + FE `data-ui-ref`)        | Canonical (build to this) |
|----------------------|-------------------------------------------|----------------------------------------------------|---------------------------|
| grammar              | `ui://region/element` (full string)       | bare refs (`inbox`, `toolbar`) → migrating         | full `ui://…` string      |
| capabilities         | string-list, `driven`/`driven-read-only`  | bool-object, `drivenReadOnly` only                 | bool-object, `drivenReadOnly` |
| `kind`               | absent on compact rows                     | present (resolver dispatches on it)                | present (S0 projection adds) |
| command              | (static — no command)                      | per-verb routes, NOT address-keyed                 | verb+address+args via `/api/act` (SHOULD-BE) |
| state read           | render bindings in tokens                  | `capabilities().node_states[*].render` served      | read served `node_states` |
| context read         | (none)                                     | keyword-keyed today                                | `GET /api/context?address=` (SHOULD-BE) |
| governance           | (none)                                     | posture per route (operator-only resolve)          | `address → tier` (SHOULD-BE) |

The convergence is **two halves built to ONE contract meeting in the middle**: the corpus is the spec, the
builder produces the FE against it, and it connects because both speak this one address grammar.
