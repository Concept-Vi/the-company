# SELF-RECALL RECOVERY PROTOCOL — the one-step heal for a disoriented / post-compaction session (#64/#65/#69)

*The canonical recovery packet (recollection's lane, captured 2026-06-18 after the live incident where projection + fork hit compaction and could not auto-self-recall). PROVEN BY USE across the fleet: recollection, fork (ch-8djrpmsl), and the lead (ch-al7jdfdr, a Jun-14 pre-hook session) all self-seeded + verified. Hand this to any session that returns disoriented.*

## SYMPTOM
After a compaction (or any time a session "wakes up" not knowing who it is), `resolve_own_session(self)` raises **`AmbiguousSelfError`** — many transcripts in the project dir, no `COMPANY_SESSION_ID` env, can't safely pick SELF. This hits sessions **launched before the SessionStart marker-hook deploy** (51a0cf4): their hook config was snapshotted at launch, so they never wrote a self-marker, so there's nothing to resolve by.

## THE ONE-STEP HEAL (run from INSIDE the session — the only place its own sid is certain)
Two turns, because the nonce must be written to your transcript before you can grep for it:

```
# Turn 1 — emit a unique nonce (it lands in YOUR transcript):
echo "SEED-$(date +%s%N)"

# Turn 2 — seed yourself by that nonce (replace with the exact string Turn 1 printed):
python ops/seed_self.py --phrase "SEED-…" --fold-registration <your-handle>

# Verify:
python -c "import sys;sys.path.insert(0,'/home/tim/company');from runtime.session_scan import resolve_own_session as r;print(r(cwd='<your-cwd>'))"
# → {session_id: …, how: 'fabric-registration (#69 claude_pid)', ambiguous: False}
```

`seed_self.py` greps `~/.claude/projects/*/*.jsonl` for your nonce → the SOLE transcript containing it is you (zero inference) → writes `~/.recollection/self/<claude-ancestor-pid>.json` and folds `{claude_pid, session_id}` into your registration. **claude_pid is stable across compaction**, so `resolve_own_session` resolves you by it from then on. `--phrase` is the reliable path; `--sid <id>` works if you already know your sid.

★ **Keep the nonce PRIVATE** — don't paste it into a channel message, or it gets quoted into OTHER sessions' transcripts and the grep matches >1 (the helper will tell you and refuse — use a fresh nonce).

## WHY NOT identify from outside (the hard lesson — do NOT /proc-backfill)
A peer cannot reliably derive your CURRENT session_id from `/proc`:
- `cmdline --resume` is the **stale launch anchor**, not the current (post-compaction) sid — they diverge after the first compaction.
- **start-time correlation collides** — two pids map to one transcript; Δ runs to days.
- **content is entangled** — coordinating sessions quote each other, so hit-counts mis-identify (we nearly tagged projection's transcript as DNA's; fork nearly `--sid`'d the LEAD's transcript because its dir's recent jsonls were the lead's).
The current sid lives **inside the running process** — only the session itself knows it for certain. An outside backfill would write WRONG sids into shared registrations = the mis-id corruption #69 exists to prevent. **Inside-nonce is the only safe primitive.** (Measure-don't-infer.)

## FULL RECOVERY PACKET (once you have your sid)
```
session_recall(op=catch_up,    session=<sid>)   # what happened across your session
session_recall(op=decisions,   session=<sid>)   # your decisions
session_recall(op=open_loops,  session=<sid>)   # your unresolved threads
corpus(op=query, space='history', text='<your topic>', rerank=False)
```
★ `space='history'` — NOT the default/unspaced index (that's a near-empty trap; durable cross-session records live in SPACES). `rerank=False` — the jina rerank is off the latency path (see RERANK-CPU-PERF.md).

Then re-read your lane's build doc + your finds (`build-prep/common-knowledge/finds/<your-handle>.md`).

## GOING-FORWARD (close the gap at the root, not retroactively)
- **At launch**: inject `COMPANY_SESSION_ID=<sid>` (the resolver's first-choice unambiguous self-id) — the cleanest fix; needs the launcher to set it.
- **The marker hook**: ensure the SessionStart hook fires on `compact`/`resume` (matcher), AND remember hook config is snapshotted at launch → only sessions launched after the change get it. So self-seed (this doc) remains the bridge for any session launched before.
- Until a session relaunches with one of those, it self-seeds once (above) and is then compaction-durable.

## PROVEN BY USE
- recollection (ch-83e2cque): healed — resolves via fabric-registration (#69 claude_pid).
- fork (ch-8djrpmsl): seeded + verified → 11e7d395; nonce-grep caught the lead's-jsonl ambiguity.
- lead (ch-al7jdfdr): Jun-14 pre-hook session, self-seeded + verified → bda8ce28 — the predates-hook proof.
- Code: `ops/seed_self.py` (e2032e5) · `resolve_own_session` cwd-robust (8f4df59) · `runtime/session_scan.py`.
