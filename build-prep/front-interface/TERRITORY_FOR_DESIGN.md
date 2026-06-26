# territory_for(address) — DESIGN (build HELD by host directive 2026-06-16)

```
trust: fabric-derived — fork-authored DESIGN for a fork-owned module. BUILD HELD (host: "DESIGN
territory_for, do NOT build it yet" — finding-phase, no build on assumptions).
author: ch-8djrpmsl (fork)
status: BUILT + VERIFIED-BY-USE (2026-06-16, LANE-B greenlit) — runtime/territory.py; degrade matrix + happy path 10/10 (board://item-0af8d61e composed a real territory; case-3 nonexistent-record guard + never-raise prose proven). The bridge handoff diff is PROPOSED for the owner: channel-memory/design/claude-stream-territory-composer.patch.md. (This doc is the design it was built to.)
```

## What it is
The address→territory composer: the **16-scheme + H1.2-graph generalization** of the ui://-only context
composer that `bridge._claude_stream` uses today (inline, ui://-only, `address_help`-only — bridge.py:1670–1681).
**Brain-agnostic** (host D2 resolution): it composes the TERRITORY at an address; the SCALE/rung decides
FOCUS (RHM) vs PANEL (Claude Code) at *handoff*, NOT in this composer. Fork-owned, file-disjoint, GPU-free
(every leg is a registry / structural / decay read — none embeds; no :8007). Reuse-don't-parallel: it
COMPOSES existing resolvers, never forks one.

## The resolver map it composes (verified by reading the code)
- **9 resolvable schemes** via `cognition.resolve_address(store, addr)` → a record: run·cas·skill·context·session(+/step)·cap·board·clone·mind (cognition.py:842–1029).
- **ui://** → its own richer composer: `suite.address_help` (3 legs: what_this_is / how_to_change / how_to_use, suite.py:3271) + `suite.context_at` (scored R2 items, suite.py:4267) + `suite.chats_at` (suite.py:5698).
- **6 non-resolvable schemes** (blob·vec·code·exchange·file·project) → `resolve_address` RAISES → degrade to a legible "no content-resolver yet" note.
- **H1.2 typed-edge graph, ANY scheme** → `cc_board.relations(addr, direction="both")` (cc_board.py:380) — structural by default (no live store needed); `edges_in` via `reverse_traverse` scans all board items for links→addr (works for any scheme); `edges_out` only for board:// (else empty + stated).

## API
- `territory_for(address, *, suite=None, store=None) -> dict` — three legs, brain-agnostic.
  Returns `{address, scheme, identity, identity_kind, context_items, chats, relations, notes, legs_present}`.
- `territory_prose(territory_or_address, *, suite=None, store=None) -> str` — renders the
  `[Operator context — what Tim is pointing at]` block; the drop-in replacement for `_claude_stream`'s
  inline ui://-only composer.

## ★ THE DEGRADE CONTRACT (advisor-hardened — the part that makes it behave like the wire it replaces)
The existing wire's contract (bridge.py:1670–1681): **context-gathering never kills the turn** (address_help
is try/except → degrades to a note). There are THREE failure cases, not two:
1. **Malformed / not-an-address** (a bare name, no `://`) → `territory_for` RAISES (fail-loud-legible; good for the library + tests).
2. **Non-resolvable scheme** (vec://, code://) → identity leg = noted-absent ("no content-resolver yet"); relations leg still runs; clean partial.
3. **★ Well-formed, resolvable-scheme address → NONEXISTENT record** (`session://bogus`, stale `board://item-…`, unknown `clone://`) → `resolve_address` RAISES (`if rec is None: raise`, BoardError, CloneError, MindError). This is the case that would REGRESS the wire if unguarded.
- **Therefore:** every leg is independently guarded inside `territory_for` (mirroring address_help's per-leg guard, suite.py:3285) → a dead leg becomes a noted-absent leg, not a void territory. `territory_for` raises ONLY on case 1.
- **`territory_prose` (the bridge-facing path) NEVER raises** — an outer guard degrades even the case-1 raise to a note, preserving the wire's contract exactly.

## Verification plan (when build resumes) — the DEGRADE MATRIX, not just happy-path
Happy: a real board:// item (with edges), a real ui:// address, a real session://. **Degrade (where the bugs live):**
(1) malformed/non-address → territory_for raises, territory_prose returns a note (never raises);
(2) nonexistent record (session://bogus, board://item-missing) → identity noted-absent, partial territory returned;
(3) non-resolvable scheme (vec://…) → identity = "no resolver" note, relations still tried;
(4) store-requiring scheme with store=None → leg notes "no store to resolve", never crashes.

## The proposed bridge handoff (the meet-at-the-address diff — for the bridge owner, when build resumes)
Replace `_claude_stream`'s inline ui://-only composer (bridge.py:1670–1681) with `ctx = territory_prose(address, suite=SUITE)`.
fork does NOT edit bridge.py — proposes the one-line diff; the bridge owner applies (met-at-the-address, file-disjoint).
The FOCUS handoff (scale-rule → `chat_parts`' `focus` dict) adapts the same `territory_for` dict; not built here.

## REFINEMENTS (finding-phase — surfaced as the slice contract firmed; design only)
- **★ code:// drill targets need a SCOPE/BLAST-RADIUS leg, not just degrade (surfaced by projection's seam-3 contract, 2026-06-16).** projection's `projection:select` event hands `detail.address` = a real contracts.address, and its drill targets are mostly `code://`·`run://` corpus points (kind='corpus.record'; example `code://contracts/resolver.py`). `code://` is NOT `resolve_address`-resolvable → my default degrade-path would give a THIN territory (address + H1.2 edges + a "no content-resolver" note). But `code://` is RICH — it has `resolve_scope` + `blast_radius` (the SAME legs `address_help` pulls for ui://, suite.py:3309-3310). So `territory_for` needs a `code://` leg that reaches scope/blast-radius. Generalize: the identity-leg strategy is per-scheme — ui://→address_help · code://→resolve_scope+blast_radius · the 9 resolvable→resolve_address · the rest→degrade. (The composer is still ONE function; the per-scheme leg is a dispatch inside it, mirroring resolve_address's own scheme-dispatch — reuse-don't-parallel.)
- **The drill-handoff transport is projection's `projection:select` window CustomEvent** — `detail={address, source, record, seq, kind, space}`. The fork consumer = `addEventListener('projection:select', e => bind brain to e.detail.address)`. The brain-binding WIRE already exists (`_claude_stream`/POST /api/claude/turn takes an address); the BUILD-HELD pieces are the FE listener + this `territory_for` cross-scheme generalization. (Meet-at-the-address, file-disjoint: projection emits the address, fork consumes it.)
- **★ PRECISE EMIT SPEC (projection, confirmed 2026-06-16) — build territory_for to THIS:** `detail.address = detail.source ?? detail.record` (best handle). The DOMINANT case = CORPUS points (kind='corpus.record'): `detail.source = code://<path>` (the unit) AND `detail.record = run://corpus/company/code://…/<space>` (the run:// WRAPPER for the SAME unit — and run:// IS `resolve_address`-resolvable). Other lenses → board://·vec://·… as source (scheme-agnostic). Address-less points (raw routine/session events, no source) → `detail = null` → they DON'T drill (territory_for never sees them). ⇒ **two handles for a corpus unit:** the `code://` (needs the scope/blast-radius leg) OR the `run://` record (resolves through the ONE resolver today). DESIGN CHOICE: build the `run://` record path FIRST (it's resolvable now, zero new leg) as the resolvable fallback, then add the `code://` scope/blast-radius leg for the richer code-unit territory. Either way `territory_for(detail.address)` and `territory_for(detail.record)` both must work.
- **GATING (projection reconcile, confirmed):** the consumer (FE listener + territory_for wiring) stays held until fork's gate clears = **KIMI-CLONE-PROVEN** (lead's consumer-gating, not the broad interface-hold). NOTE for the lead: the loadable-brain PANEL path runs the CC turn on the DEFAULT model (Anthropic) — it does NOT require kimi/ollama — so a default-model drill→talk slice is not strictly kimi-blocked; whether to open the consumer on the default brain now vs hold for cheap-brains is the lead's call.
- **★ CORRECTION — the code:// resolution mechanism, VERIFIED AGAINST THE LIVE STORE (2026-06-16), supersedes the scope/blast-radius GUESS above.** The drill units are NOT code-scope — they are CORPUS RECORDS. Verified live: a corpus record is keyed by its `address` = `run://corpus/<project>/code://…/common_knowledge`, with the code:// as a SEPARATE `source_address` field. So `read_corpus_record(code://…)` → None (the code:// is the source, not the key); `read_corpus_record(run://…)` resolves; `find_corpus(source_address=code://…)` resolves it too. The record is METADATA + a `cas://` content pointer (no inline text). **BUILT FIX (territory.py corpus leg, verify-by-use on `code://recollection/skills/remembering-conversations/SKILL.md` → identity_kind=corpus.content, real digest):** read_corpus_record(address) → if None, find_corpus(source_address=address)[0] → then dereference the record's `cas://` via resolve_address → the actual comprehended content. So `territory_for(detail.source=code://)` resolves the REAL unit content. The earlier "scope/blast-radius leg" guess was wrong — corrected by verifying against the actual store (no green paint). READ half now verified-by-use against real gallery data, not just board:// + mocks.
