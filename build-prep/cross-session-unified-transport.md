# Cross-Session Unified Transport — design (DESIGN-ONLY, pre-implementation)

**Status:** design draft by the fork (ch-8djrpmsl), for lead (ch-al7jdfdr) review → implementation on
`runtime/cc_channels.py` + acceptance extension → **surface to Tim before it lands** (it changes core
router semantics). No `cc_channels.py` edit is made by this doc. 2026-06-14.

**Goal it serves (Tim):** "find→clone→launch any session at a point in time and *add them into group
chats / DM them*." Today a cloned-at-T session can be DM'd (cc_clone op=msg, supervisor-inject) but
cannot **join a group broadcast** — because `cc_channel` only knows ONE transport (HTTP push to an
interactive channel-session's port), and a supervised headless clone has no port. This design makes the
router **transport-aware** so a supervised clone joins group chats **autonomously** (no operator launch),
alongside interactive channel members — removing the operator gate for the *autonomous* clone-in-group
case while keeping it for the interactive-channel-member case (which stays operator-gated by the safety
boundary).

---

## The two transports (the relational core)

A "live session in the fabric" is reachable by exactly one of two transports — the router should treat
the transport as a property of the registration, not a hardcoded assumption:

```
transport = "channel"      interactive session, channel MCP server on a local port
                           PUSH  : HTTP POST -> notifications/claude/channel (lands in convo)
                           REPLY : the session's `reply` tool -> supervisor /channel-reply -> route_reply
                           LIVE? : pid alive (os.kill 0) AND port present
                           LAUNCH: operator-only (agent auto-launch is a denied safety boundary)

transport = "supervised"   headless -p session owned by the session-supervisor (e.g. a cc_clone clone)
                           PUSH  : supervisor POST /inject {session, message}
                           REPLY : the turn result on the supervisor stream (/watch type=="done")
                           LIVE? : supervisor /sessions shows it not-"closed"
                           LAUNCH: agent-allowed (supervisor spawn-resume — proven, operator-controlled)
```

The whole design is: **carry `transport` in the registration; dispatch push + reply on it; fold both
reply paths into the one mail log + thread index.** Everything else (threads, mail, group=one-thread,
reply-routes-to-originator) is unchanged — it already works for `channel`; we generalize it.

---

## Changes (all in `runtime/cc_channels.py`, lead-owned)

### 1. Registration carries `transport`
- `.data/channels/<handle>.json` gains `"transport": "channel" | "supervised"`.
- **Back-compat:** a registration with no `transport` and a `port` ⇒ treat as `"channel"` (every
  existing interactive registration keeps working untouched).
- A `supervised` registration carries `{handle, session_id, transport:"supervised",
  supervisor_session, supervisor_base, cwd, description, started}` and **no `port`**.
- `cc_clone.clone_at()` writes the supervised registration HERE (today it writes a separate
  `.data/clones/` registry; unify it into `.data/channels/` with `transport:"supervised"` so the one
  `cc_channel` surface sees clones in `op=list`, `send`, `broadcast`). `.data/clones/` can be retired
  or kept as a cc_clone-private mirror — recommend: single source of truth in `.data/channels/`.

### 2. `live_sessions()` prunes per-transport
```
channel    : keep if _alive(pid) and "port" in reg     (today's logic)
supervised : keep if supervisor /sessions shows supervisor_session != "closed"
```
(One supervisor GET /sessions call, cached per live_sessions() invocation, classifies all supervised
regs — don't call per-row.)

### 3. `push(reg, content, meta)` dispatches on transport
```
transport == "channel"    -> existing HTTP POST to reg["port"]
transport == "supervised" -> POST {session: reg["supervisor_session"], message: <rendered>} to
                             reg["supervisor_base"] + "/inject"
```
The injected text for a supervised member should carry the same framing a channel member sees, e.g.
prefix `(fabric from <frm>, thread <thread>): <content>` so the clone knows it's a fabric message and
which thread to answer on (it has no `<channel>` tag — the inject IS the message).

### 4. Replies — BOTH paths fold into the one mail log + thread index
- **channel** (unchanged): `reply` tool → `/channel-reply` → `route_reply(from, thread, text)` →
  `_append_mail(kind="reply")` + push back to the thread originator.
- **supervised** (new): a supervised member has no `reply` tool; its reply is the turn result. Two
  options for capturing it:
  - **(A) synchronous** — `send()` to a supervised member does inject + watch-for-done inline
    (like `cc_clone.msg_clone`), then calls `route_reply(from=clone_handle, thread, text=result)`.
    Simple; but a group `broadcast()` to N supervised members would serialize on their turns.
  - **(B) async watcher (RECOMMENDED)** — on the FIRST send to a supervised member, start a
    per-session daemon that tails the supervisor `/watch?session=<sup>`; on each `type=="done"`, look
    up the thread of the most-recent inject to that member and call
    `route_reply(from=clone_handle, thread, text=result)`. Non-blocking; group broadcasts fan
    naturally; replies aggregate under the one thread exactly like channel replies. Needs a small
    `{supervisor_session -> last_thread}` map (or pass thread through and correlate by turn order).
  - Recommend (B) for parity with the no-polling channel model; (A) is the minimal fallback.
- Net: `route_reply` becomes transport-agnostic at its callers; the mail log + thread index are the
  single durable record for both kinds. A reply routed back to a `supervised` ORIGINATOR pushes via
  inject (the same `push()` dispatch) — so a supervised clone can ALSO be the asker in a thread.

### 5. `send()` / `broadcast()` — no API change
They already `find()` + `open_thread()` + `_append_mail()` + `push()`. With `push()` transport-aware
and `find()`/`live_sessions()` transport-aware, a `broadcast(to="h1,clone-ab12,h3")` mixing channel
members and a supervised clone "just works": each member gets the message by its transport, replies
aggregate under the one group thread. **This is the feature** — a cloned-at-T session in a group chat,
autonomously.

---

## What this REMOVES vs KEEPS (the envelope, explicit for Tim)
- **REMOVES** the operator gate for *autonomous clone-in-group*: an agent can clone a session at T and
  pull it into a group chat via supervised+inject — no human launch needed. Serves Tim's goal directly.
- **KEEPS** the operator gate for *interactive channel-member clones*: launching a real interactive
  `--dangerously-load-development-channels` clone is still operator-only (the denied safety boundary).
  The supervised path is a *different mechanism* (supervisor-controlled, agent-initiated turns, not an
  unsupervised channel-ingesting agent) — which is why it's allowed.
- **Decision for Tim:** removing the gate means agents can compose group conversations that include
  time-travelled past-context clones without you in the loop. That's the intended power; flag it as a
  deliberate autonomy increase (governed by the supervisor's existing controls, not a new surface).

---

## Acceptance (lead extends `tests/cc_channels_acceptance.py`, currently 17/17)
- registration back-compat: portful no-transport reg classifies `channel`.
- dispatch: `push()` to a `channel` reg hits HTTP; to a `supervised` reg hits supervisor `/inject`
  (mock the supervisor in-test).
- liveness: supervised reg pruned when supervisor reports `closed`.
- reply fold: a supervised turn-done is recorded in the SAME mail log with `kind="reply"` and routed
  to the thread originator.
- mixed group: `broadcast` to [channel, supervised] opens one thread; both replies land under it.

## Risks / open
- **Reply correlation for supervised** (which inject a turn-done answers) — turn-order correlation is
  reliable for one-at-a-time; if a clone is mid-turn when a second message arrives, the supervisor
  already refuses inject (busy) — so serialize per member (natural).
- **Watcher lifecycle** (option B) — one daemon per live supervised member; reap when the supervisor
  shows it closed (same signal as `live_sessions()` prune).
- **Single registry** — moving cc_clone's registrations into `.data/channels/` means cc_clone and
  cc_channel share one registry dir; keep the `transport` field as the discriminator. Coordinate the
  cutover (cc_clone is the fork's file; cc_channels is the lead's — this doc is the contract between them).

---

## Build split (per the boundaries we learned)
- FORK (ch-8djrpmsl): this design + (on lead's go) the `cc_clone` side — write supervised registrations
  into `.data/channels/` with `transport:"supervised"` (cc_clone.py is the fork's file).
- LEAD (ch-al7jdfdr): `runtime/cc_channels.py` transport-aware dispatch + reply fold + acceptance
  extension (its file + its test).
- BOTH → surface to Tim before it lands (core router semantics + the autonomy-increase decision).
