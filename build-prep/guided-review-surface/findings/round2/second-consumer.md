# Second-Consumer Analysis: How Other Inbox Lanes Ride the Guided-Review Organ

**Thread:** Generalization — mapping every inbox lane to the one organ, identifying what's shared vs instance-1-only.

---

## 1. The Inbox — Full Lane Inventory (Observed, suite.py)

`inbox_lanes()` at line 5685 returns three buckets from ONE store: `live_escalations`, `resolved_for_you`, and `batched` (grouped by `action`). Every surfacing call writes to the SAME inbox.list(). The action types that appear in the live store, with their surfacing points:

| Action type | Surfaced by | Nature |
|---|---|---|
| `"question"` | `_ask_operator()` line 800 | Brain hit unregistered ground; needs yes/no |
| `"result"` | `surface_output()` line 5964 | Node output routed for operator decision |
| `"review"` | `surface_review()` / `surface_build_intent()` lines 5993, 6807 | Build-loop criterion OR idea; `intent="build"` is the discriminator |
| `"deferred_offer"` | `defer_offer()` line 6057 | Live RHM proposal the operator queued; revivable |
| `"code_build"` | line 8145 | Brain-authored node type awaiting apply |
| `"role_build"` / `"role_delete"` | lines 8238, 8328, 8346 | Role authoring / deletion awaiting apply |
| `"ui_panel"` | line 9067 | Brain-authored UI panel awaiting apply |
| `"ui_extension"` | line 9158 | Brain-authored React component awaiting build-gate + apply |
| addr-tier class (I4) | line 4180 | Governance-tier escalation for an addressed action |

All nine are `resolved=None` live escalations until the operator acts. `inbox_lanes()` batches them by `action` when > 1 of the same type is pending.

---

## 2. The Walkthrough Organ — What It Is (Observed)

The organ is four methods riding the scheduler:

- `start_session(item_ids, mode, teach, indicate)` — compiles a Graph of go-gate → step-carrier pairs, one per item; persists session; calls `present_current(0)`.
- `present_current(session_id)` — reads cursor; if item is a `ui://` string → guide branch (corpus how-to, model-free); else → `coa(item_id)` (COA framing, model-dependent). Stamps `ui_target` on raw for view-drive.
- `next(session_id)` — opens the current step's go-gate by writing its address; advances cursor; calls `present_current`.
- `start_walkthrough(item_ids=None)` — the operator-triggered entry point: sets the presence dial to `"walkthrough"` + calls `start_session` over pending inbox items.

There are TWO entry points that compose this organ:
- **`start_walkthrough`** (line 6287) — walks PENDING INBOX items (review decisions); operator/dial-triggered.
- **`start_guide`** (line 6442) — walks `ui://` ELEMENT ADDRESSES (interface orientation); system-initiated, model-free.

The session record is `{id, graph, mode, items, cursor, opened, done}` with optional `teach[]` and `indicate[]` side-channels.

---

## 3. Lane-by-Lane: Guided Walkthrough Sketch

### Lane A — Build Review (action=`"review"`, `intent="build"`)
**Current instance-1 consumer.** Operator is led through pending build-intents; each item gets COA framing (meaning + options + recommendation); operator resolves (approve/reject); wire dispatches on approve.

- **Queue:** same `resolved=None` inbox items, gathered by `start_walkthrough`.
- **Sequencer:** `start_session` → `next` → `present_current`.
- **Addressed markup:** `ui_target` stamped into `raw` for view-drive to the thing being reviewed (`ui://canvas/<node>` or `ui://inbox/build-review`).
- **Generate:** COA framing calls the model to up-translate; `coa()` is the per-item model call.
- **Resolve:** operator calls `/api/resolve` → `resolve_surfaced`; on approve, `dispatch_decision` fires.

### Lane B — Deferred Offers (action=`"deferred_offer"`)
**Inferred walkthrough shape:** Operator led through their queued live RHM proposals. Each step presents the offer's `name` + `note` + stored proposal shape (verb/address/args/options). At the step, operator can: **revive** (re-open the ProposeAffordance card for live steering + approve), **dismiss** (resolve=reject), or **defer again** (skip for now).

- **Shared with review:** same inbox queue; same `start_session`/`next`/`present_current` organ; `ui_target` drives view to the locus the offer pointed at (already carried in payload.ui_target via L8).
- **Per-consumer delta:** COA framing is wrong here — the item IS already a commander-altitude value choice (it came from a live RHM offer). `present_current` should branch on `action=="deferred_offer"` and return the offer's `name`/`note`/options directly as `framing`, bypassing `coa()`. This is a small branch in `present_current`, not a new organ.
- **Resolve:** `revive_offer(sid)` returns the proposal state; the FE re-opens the ProposeAffordance card; approve path is the existing B1/B2 consent machinery.
- **Mode/sub-mode:** same `"walkthrough"` mode. A sub-mode `"offer-review"` is possible but NOT required — the organ handles it with a `present_current` branch.

### Lane C — Questions (action=`"question"`)
**Inferred walkthrough shape:** The brain surfaced a question (hit unregistered ground) and is blocked until answered. A walkthrough of pending questions leads the operator through each: here is the question + context, what is your answer? Operator replies; answer is injected back.

- **Shared with review:** same inbox queue; same organ sequencer; `ui_target` = `ui://chrome/inbox` (the question always lands there, line 801).
- **Per-consumer delta:** COA framing is inappropriate (no value-choice to frame — the question IS the content). `present_current` should return `framing = payload["question"]` and `raw = payload` for a `"question"` action, bypassing `coa()`. One more branch in `present_current`.
- **Resolve:** operator's free-text answer is the verdict (`resolve_surfaced(sid, choice="custom", reason=<answer>)`). The `_ask_operator` default is `"reject"` so unanswered questions resolve to reject.
- **Mode/sub-mode:** same `"walkthrough"` mode.

### Lane D — Node Results (action=`"result"`)
**Inferred walkthrough shape:** Operator led through surfaced node outputs, each of which represents a result that needs a decision (keep it? send it somewhere? acknowledge it?). Each step presents the output content + the node that produced it.

- **Shared with review:** same inbox queue; same organ; `ui_target` already carried in payload (L8, line 5968-5976) → drives view to `ui://canvas/<node>`.
- **Per-consumer delta:** COA framing MAY be appropriate here (a result could be a decision: what do you want to do with this output?). If the output is a plain content result, COA would over-frame it. A lightweight branch: if `payload["output"]` is short/content, present raw directly; if it's a value-choice result (e.g., a proposed plan), COA frames it. OR: let COA always run — it degrades gracefully (abstains on empty, presents raw on failure). Probably NO branch needed; COA's grounding guard handles it.
- **Resolve:** acknowledge (approve) or dismiss (reject); no dispatch wire for plain results — the resolved verdict is just a closure.
- **Mode/sub-mode:** same `"walkthrough"` mode.

### Lane E — Code / Role / UI Authoring (action=`"code_build"`, `"role_build"`, `"role_delete"`, `"ui_panel"`, `"ui_extension"`)
**Inferred walkthrough shape:** Operator led through brain-authored assets awaiting apply. Each step shows what was authored (code/panel/role) and asks: apply it? The sequencer presents one at a time; operator approves → `apply_surfaced` dispatches by class.

- **Shared with review:** same inbox queue; same organ. `apply_surfaced()` (line 9114) already dispatches by `action` class — the walkthrough step just presents the item and the operator resolves; apply_surfaced handles the class-routing.
- **Per-consumer delta:** COA is wrong for authoring items — there is no "value choice" to frame, the asset is binary (apply or don't). `present_current` should return the asset content (`code`/`panel`/`spec`) as `framing` directly for authoring action classes. One branch grouping all authoring actions.
- **Resolve:** `/api/apply` (line 1529 of bridge.py) calls `apply_surfaced` — already routes by class. No change needed to the resolve path.
- **Mode/sub-mode:** could be a sub-mode `"authoring-review"` but NOT required. The organ handles it with a `present_current` branch.

### Lane F — Governance Tier Escalations (I4, addr-tier class)
**Inferred walkthrough shape:** The operator clicked an address whose governance tier requires consent (CONFIRM-class action). A walkthrough presents each pending governance escalation: here is the action + the address it was triggered on + the governance tier. Operator approves or rejects.

- **Shared with review:** same inbox queue; same organ. `ui_target` = the address that triggered the escalation (already in payload, line 4180 context).
- **Per-consumer delta:** COA may frame these well (they are consequential decisions scoped to a ui:// address); or a lighter presentation suffices. Low risk either way — COA degrades on empty.
- **Mode/sub-mode:** same `"walkthrough"` mode.

---

## 4. The System-Initiated Guided Tour (start_guide)

`start_guide` is a THIRD consumer of the organ — distinct from both review and deferred-offer walkthrough:

- Items are `ui://` element addresses (not inbox item IDs).
- `present_current` branches on `isinstance(item_id, str) and item_id.startswith("ui://")` → corpus how-to, model-free.
- Used for orientation ("show me how to request a change") and self-modify bootstrap.
- Registered at bridge route `/api/guide/start` (line 1259-1268 of bridge.py).
- This is already built and working. It is a mode of the organ, not a second organ.

---

## 5. What Generalizes (the General Organ)

All consumers share:

| Shared component | What it is |
|---|---|
| **One inbox queue** | `inbox.list()` filtered by `resolved is None`; no parallel queues; batching by `action` class |
| **Sequencer** | `start_session` → `next` → `present_current`; cursor + go-gate graph; atomic advance |
| **Addressed markup** | `ui_target` stamped in `raw`; `resolveUiTarget` on FE drives view to the thing |
| **Present branch point** | `present_current` dispatches on item type: `ui://` → guide (corpus, model-free); inbox id → per-action framing |
| **Resolve path** | `resolve_surfaced(sid, choice, reason)` with the operator face; `resolved` closure |
| **Mode dial** | `set_mode("walkthrough")` sets the presence register; RHM speaks in guide register |

The organ IS general. The only per-consumer variation is in `present_current`'s framing branch:

- `ui://` prefix → guide (corpus)
- `action == "review"` with `intent == "build"` → COA (model-dependent up-translate) [**instance-1 today**]
- `action == "deferred_offer"` → offer name + options (raw, no COA)
- `action == "question"` → question text direct (raw)
- `action ∈ {"code_build","role_build","role_delete","ui_panel","ui_extension"}` → asset content direct (raw)
- `action == "result"` → COA or raw depending on payload content (COA degrades gracefully; probably COA is fine)
- governance tier class → COA or raw

---

## 6. What Is Instance-1-Only (Build Review)

These pieces are specific to the build-review consumer and should NOT be built into the general organ:

| Instance-1-only piece | Why it's specific |
|---|---|
| `dispatch_decision` wired to resolve | Only build-intents dispatch an autonomous implementation on approve; other lanes have simpler resolution effects (apply, answer, acknowledge) |
| `surface_build_intent` / scope declaration | The scope+consequence_class machinery is build-specific |
| `decision_build` consequence class | Governance class tied to the build wire; other lanes have their own classes or none |
| Build-gate + scope-diff at dispatch time | The DENY-ALL empty-scope rule is the build wire's safety property, not a general walkthrough concern |
| `surface_intent_at` (L1) as the comment→intent entry | The addressed-feedback-to-wire seam is build-specific |

---

## 7. Architecture: One Organ, N Consumers by Branch

```
start_walkthrough(item_ids) ──► start_session ──► present_current
                                                        │
                             ┌──────────────────────────┤
                             │ item is ui:// ?           │ NO
                             ▼                           ▼
                      corpus how-to             action == "review" (build-intent)?
                      (model-free)              ── COA framing (model) ← instance-1
                                                action == "deferred_offer"?
                                                ── offer raw (name/options)
                                                action == "question"?
                                                ── question text direct
                                                action ∈ authoring classes?
                                                ── asset content direct
                                                action == "result"?
                                                ── COA or raw (degrades safely)
                             │
                             └──► next(session_id) → advance cursor → present_current
                                        │
                                  resolve_surfaced(sid, choice)
                                        │
                             ┌──────────┴────────────────┐
                             │                           │
                     action="review"              other actions
                     + approved?                  (apply / answer /
                             │                    acknowledge / revive)
                     dispatch_decision            class-specific handler
                     (instance-1)
```

The build here is: widen `present_current`'s framing branch to handle the other action classes. The sequencer, go-gate graph, cursor, addressed markup, and mode dial are ALREADY general — they need no change. Each new consumer is one branch case in `present_current` + one resolve handler for its specific post-approval effect.

---

## 8. Named Consumers (Priority Order for the Build)

1. **Build Review** (`"review"`, `intent="build"`) — instance-1, already described in prior round.
2. **Deferred Offers** (`"deferred_offer"`) — closest to review in shape; revive path already exists; one `present_current` branch + FE card for offer revival.
3. **Node Results** (`"result"`) — COA degrades gracefully; `ui_target` already in payload; lowest delta.
4. **Questions** (`"question"`) — direct text framing; resolve = free-text answer injection; needed for brain-unblock flow.
5. **Authoring** (code/role/panel/extension) — present asset content; resolve = `apply_surfaced` (already class-routing); clean.
6. **Governance tier** (I4 addr-tier) — COA or raw; resolve = approve/reject governance consent; minor.
7. **System-Initiated Tour** (`start_guide`) — already built and working; no delta needed.

---

## Key Evidence Notes

- **Observed** (suite.py line numbers cited throughout): all nine action classes, the three-bucket `inbox_lanes()`, the go-gate session graph in `start_session`, the `present_current` guide/COA branch at lines 6207-6284, the `ui_target` L8 stamp.
- **Inferred** (NOT verified by execution): the per-consumer `present_current` branch strategy above; the deferred-offer and question framing paths do not yet exist in code — they are the extension points, not current code.
- **Idea** (not in code, not tested): the "one branch per action class in present_current" architecture; the "COA degrades gracefully for results" claim; the priority ordering. These are design recommendations based on structural reading.
