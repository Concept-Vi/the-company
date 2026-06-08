# Autonomous three-session loop — the message system + staggered crons (2026-08, Tim's "go to bed" setup)

> Removes the human relay: each session runs a cron timer; the FIRE is the trigger (replaces Tim's "go read
> it"); the sessions message each other through `MESSAGES.md` in this folder. The cron + the message system =
> autonomous coordination. Each fire does ONE bounded round, then idles; the next fire continues.

## The message system (`build-prep/coordination/MESSAGES.md`)
- **Append-only, race-safe.** Post with `cat >> MESSAGES.md <<'EOF' … EOF` (NEVER read-then-Edit — two
  sessions writing concurrently). Newest at the bottom.
- **Tagged:** each message `### [YYYY-MM-DD HH:MM] from:<session> to:<all|session> re:<topic>` + body.
- **Read-marker:** each session, on each fire, reads messages BELOW its own last post (track by your last
  `from:<you>` line). Act on anything `to:you` or `to:all` that's relevant.
- **The CLAIMS board (`WORK-SPLIT.md § CLAIMS`) is still read FIRST each fire** — it's authoritative over
  memory; a claimed file is held.

## The staggered crons (so messages propagate + commits don't collide)
Every 15 min, offset by 5 — the ring order cognition → guided-review → coherence, so a message posted by one
is read by the next ~5 min later, and no two commit to main at the same instant:
| session | cron (local) | slot |
|---|---|---|
| cognition | `0,15,30,45 * * * *` | :00 |
| guided-review | `5,20,35,50 * * * *` | :05 |
| coherence | `10,25,40,55 * * * *` | :10 |
(Each session sets its OWN cron in its OWN Claude session — `durable: true` so it survives a restart. The
sessions must be left running/idle for the crons to fire.)

## The per-fire loop (each session, every fire — ONE bounded round then idle)
1. **Read:** this protocol + `WORK-SPLIT.md § CLAIMS` + the NEW messages in `MESSAGES.md` since your last post.
2. **React:** act on messages to you / claims-state changes (e.g. cognition posts "C released" → the files you
   were holding are free → do the work that was waiting). Answer questions addressed to you.
3. **Build ONE buildable, ungated, file-disjoint piece** of your lane: CLAIM the file (append to § CLAIMS) →
   build → `company suites` GREEN → verify BY USE (on a TEMP store, never the live one) → commit ONLY your
   files → release the claim. HOLD files claimed by others.
4. **If blocked/gated** (waiting on another lane, or a file is claimed): record it in your STATE + post a
   message saying what you're blocked on → **EXIT the fire. Do NOT spin or do busywork to avoid stopping.**
5. **Post** a status message (append): what you did, what's blocked, what you need. **Update your STATE doc.**
6. **PushNotification Tim ONLY if something truly needs him** (a real blocker, a destructive call) — otherwise
   record it for morning; never wait on him.

## The discipline (binds every fire — this is what makes unattended-to-one-main safe)
Registry-is-truth / no-hardcoding · additive · fail-loud · reflects-never-owns · operator-only floor ·
verify-by-USE never code-reading · **NO green-paint** (not-confirmable-headlessly → needs-tim, never "done") ·
**surface-don't-defer** · commit-to-main (no branches) · `company suites` green before any shared-file commit ·
one driver per shared file via CLAIMS · **don't-spin** (blocked → record + exit, not busywork) · bounded reads
(never whole suite.py/bridge.py). The **CONVERGENCE ROUND** (`CONVERGENCE-ROUND.md`) fires when all three post
`lane-complete` — the shared seam+whole-system+by-use pass.

## Morning
Each session leaves an up-to-date `AUTONOMOUS-STATE.md` (done / in-flight / blocked / needs-Tim) so Tim wakes
to an honest picture, not a guess. PushNotification only for real blockers overnight.
