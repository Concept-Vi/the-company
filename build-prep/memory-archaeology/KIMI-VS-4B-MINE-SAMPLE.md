# kimi-k2.7-code:cloud vs resident-4B on `mine_exchange` — 5-exchange A/B (2026-07-07)

**What this is:** a controlled sample — the SAME 5 real exchanges from session `104a58a7`
(`-home-tim` project) run through the `mine_exchange` role on both models. The 4B column is the
EXISTING history-space record (the real production miner output); the kimi column is a fresh
`run_role(model=kimi-k2.7-code:cloud)` on byte-faithful units. Isolates the model as the only variable.

Purpose: measure kimi's real quality lift for the memory-archaeology re-mine, with a range (mundane →
design-rich → correction → noise-trap → ops), not a single lucky point.

## Per-exchange verdict

| ex | type | 4B record | kimi record | verdict |
|----|------|-----------|-------------|---------|
| 3 | open subagent/parallax design | decision = "both modes + sub-agent strategy to find blind spots"; tag `parallax-blind-spots` | decision = "Tim settled needs both modes, identity↔instance"; tag `open-parallax-subagents` | **4B slightly better** — kimi anchored on the throwaway "banked" opener, missed the parallax substance the 4B caught. kimi's own failure mode: latch on the first salient token. |
| 15 | multi-thread: parallel-session merge + portal→type-registry | decision = long run-on of ALL threads; **tim_correction="" my_error=""**; tag `defer-document-then-build` | decision = "merge parallel-session branches into main"; **tim_correction + my_error FOUND** ("branches aren't stale/different — same work, must merge"); tag `merge-parallel-sessions` | **kimi clearly better** — surfaced the correction+error the 4B flattened to "". BUT kimi dropped the portal-state-registry decision the 4B kept. Both lose material — the exchange has ~5 decisions, the schema allows 1. |
| 49 | the leverage CORRECTION (acid test) | decision + tim_correction + my_error all present; tag `reuse-dont-parallel` | same correction; decision sharper ("re-key by address" — the mechanism); tag `fit-over-leverage` | **~tie** — kimi sharper on the decision mechanism; 4B's tag arguably more reusable. Both good. |
| 120 | compaction-summary continuation (NOISE TRAP) | decision = "verified worktree, F8 single unit"; tag `verify-before-claiming` | decision = detailed full resume sequence; tag `context-resume-orient-first` | **~tie, kimi richer** — neither fell for the trap (both mined the REAL work in the reply, not the auto-injected summary). kimi more detailed + more specific tag. |
| 300 | ops kickoff / killed-worker verify | decision + verify-by-use; tag `verify-by-use` | near-identical | **tie** — same output. |

## The findings that actually matter (bigger than "which model")

1. **kimi is NOT uniformly better.** On rich single-decision + operational exchanges the 4B is *fine* —
   the earlier "88% noise" was never mainly a model-quality problem on substantive exchanges. Both
   produced usable records on 4 of 5.

2. **kimi's ONE repeatable edge is the highest-value one:** on the multi-threaded exchange (ex15) it
   caught a **Tim-correction + my-error** the 4B missed entirely. Learning-from-corrections is exactly
   the signal worth the strong model — but the win showed on 1 of 5, not across the board.

3. **kimi has its own failure mode** (ex3): anchoring on the first salient sentence and missing the
   substance. A strong model is not automatically a careful one.

4. **The schema forces ONE decision per exchange** — but rich exchanges carry 4–5. BOTH models lose
   material to this. That's a *granularity/schema* limit, not a model limit. No model fixes it.

5. **THE DECISIVE ONE — wrong lens entirely.** `mine_exchange` extracts a SELF-IMPROVEMENT schema
   {decision, rationale, tim_correction, my_error, bug_fix, needs_tim, frustration, pattern_tag}. That
   is a *failure-pattern / how-to-work-with-Tim* lens. It does **NOT** capture what Tim asked for —
   *what a thing IS, what it was REACHING FOR, its ROLE, its SPECIAL properties*. Even a perfect model
   on this role produces the wrong kind of record for archaeology. **The engine (extract→embed→address
   onto `exchange://`/`code://`) is right; the ROLE is wrong.** The archaeology needs a NEW extraction
   role — a "design-intent miner" — not `mine_exchange` on a better model.

## Implication for the plan
- The re-mine is worth doing on kimi for the correction-catching, but the **first build is a new
  role** (`mine_design_intent` or similar) whose schema is the archaeology schema Tim named:
  `what_it_is · reaching_for · role_in_system · special_properties · connects_to (addresses) · evidence`.
- Granularity: the new role should allow N decisions/intents per exchange (list output), not 1.
- Then run it (kimi) over the design-history sessions, capture onto `exchange://` + cross-link `code://`.

---

# ROUND 2 — the new `mine_design_intent` role on the SAME 5 exchanges (kimi, 2026-07-07)

The archaeology role was authored (create(kind='role'), live at roles/mine_design_intent.py, kimi-bound
top-level) and run on the same sample. Verdict per exchange:

| ex | mine_exchange result | mine_design_intent result | assessment |
|----|---------------------|---------------------------|------------|
| 3  | kimi missed the parallax substance (anchored on the opener) | **2 intents** — the dual-mode decision AND the parallax mechanism with the why ("framing quietly decides what I can notice") + special ("value is parallax, not redundancy") | **FIXED** — the "read the whole exchange / don't anchor" instruction repaired kimi's own failure mode |
| 49 | 1 decision | **3 intents** — fit-over-leverage principle · universal-address principle ("re-key, don't build") · the append_event meta keystone mechanism | the full design stack, not one flattened line |
| 15 | 1 decision (best-of) | 6 intents (round 1 test) | the multi-decision loss is gone |
| 120 (noise trap) | forced a decision out of ops noise | **intents=[] · design_weight=none** | honest empty — the no-padding law held |
| 300 | 1 decision | **4 intents** — the loop mechanism · the worktree-isolation constraint · killed-worker recovery · the verify-by-use decision | ops exchange still yielded real architecture knowledge |

**Caveat found (for the cross-link step):** `connects_to` sometimes decorates names with address schemes
not verbatim in the text (e.g. "ui://bridge :8771", "code://ShapeHow.tsx", the session's own exchange://).
The exchange↔code cross-linker must NORMALIZE + VERIFY connects_to against the real code://
space before writing links — treat it as candidate-mentions, not resolved addresses.

**Tool issues found & fixed this session:**
1. `create(kind='role')` silently dropped its `model=` param (no binding rendered) — fixed in
   Suite.create_role (binds top-level default_model + catalog/ollama-paired default_base_url; the
   binding-trap law one layer up). The authored role was repaired with an explicit top-level binding,
   verified by-use (fresh Suite resolve_role → kimi).
2. `run_items` has NO model param — a batch fan can only run on the role's bound model. The kimi
   binding on the role is what makes the batch archaeology sweep possible.

**State: the archaeology instrument is BUILT and VALIDATED. Next: the sweep driver (g23_mine sibling
that fans mine_design_intent over design-rich transcripts, captures to space='history' on
exchange://<sid>/<i>, then the connects_to→code:// cross-link pass).**
