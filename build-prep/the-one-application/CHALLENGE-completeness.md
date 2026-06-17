The exit-2 was just the last grep's missing file. I have everything I need. Critical final facts confirmed:

- **agent_sessions = 1,068 files** (map claims 13 — off by ~82x). The map read a sub-slice or stale count.
- **space_address is FLAT string concatenation**: `vec://cluster://<space>/k<K>/<label>#space=scale:...` is the literal stored key — a `vec://` whose body is itself `cluster://...`, plus a `scale:` namespace inside the `#space=` fragment. This is the live key, not prose. A flat scheme-table parser breaks on it.
- Storage objects/refs/events/graphs/vectors/backup all verified exact.
- Rendering shared-engine claim verified (`bridge.py:866`).
- `channels/` is a Node.js fabric dir (not a registry); `channel-memory/` is docs (not a registry) — those two are correctly not in the table.

I have decisive ground truth across all four domains. Writing the critique.

---

# COMPLETENESS CRITIC — what the UNION MAP missed or under-read

I verified the map's load-bearing anchors against the live repo (`/home/tim/company`). Two were exact; **three were wrong, and one whole sub-system was under-read to a single dismissive line.** The map's own authority claim — *"I have my ground truth, the other reports were stale"* — is itself partly false. Structured as the task's seam: **(A) map errors / under-reads, (B) hidden patchwork the map never names, (C) unverified claims, (D) what a further pass must capture before union is safe.**

---

## A. MAP ERRORS — the map's own "ground truth" has verified-wrong numbers

**A1 — `agent_sessions` = 1,068 files, NOT 13 (off by ~82×).** Section 3 Shape-A: *"13 agent-sessions."* Live: `find .data/store/agent_sessions -maxdepth 1 -type f` = **1,066 json + 2 subdirs**. The map did the same thing it accuses the 6/8/14 reports of — read a sub-slice and reported it as the whole. This is the *largest* relative error in the document and it sits inside the section the map presents as its most concrete. If the storage census is this wrong on one noun, the storage section is not a verified inventory; it is a partial read wearing a verified costume.

**A2 — FsStore = 77 methods, NOT 70.** `grep -cE "^    def " store/fs_store.py` = **77**. The map repeats "70" three times and builds the swap-seam argument on it (10/70 = 14%). The real ratio is 10/77 = **13%** — the seam gap is *worse* than stated, so this error happens to strengthen the map's thesis, which is exactly why it's dangerous: a number repeated 3× and never re-counted.

**A3 — registry class names are wrong, and class≠instance≠dir is conflated.** The map's table cites **`VerdictPanelRegistry`** — that class does not exist. The real class is `PanelRegistry` (`runtime/verdict_panels.py:31`). The "~25 copies" count conflates three different units: there are **28 `*Registry` class definitions**, but several are reuse-not-copy (`ContextRegistry(_BaseEntryRegistry)`, `SkillRegistry(_BaseEntryRegistry)` already share a base; `board_edges` already reuses the `relation_types` class). So the map's headline refactor ("collapse ~25 copies into one base") is partly *already done* and the map didn't notice — undercutting its own Spine-2 novelty.

**A4 — vector count "wobble" dismissed the wrong way.** Map: *"5,852/5,862 wobble is noise."* Live: exactly **5,862 active + 2,793 backup**. The "wobble" wasn't noise to be waved off — one of the two cited numbers was simply correct and the map guessed. Minor, but it shows the reconciliation method was "pick a number," not "count."

---

## B. HIDDEN PATCHWORK — systems the map under-read or never named

**B1 — THE BIG MISS: the multi-resolution scale/cluster addressing layer is a whole sub-system, not "one gap line."** The map gives `cluster://` a single row ("USED, NOT IN SCHEMES") and never mentions `scale:` at all. Ground truth (`runtime/scale.py`, `store/fs_store.py:920 space_address`):
- There is a **scheme-inside-a-scheme** live storage key: `vec://cluster://<space>/k<K>/<label>#space=scale:<space>:k<K>`. I confirmed `space_address()` is **flat string concatenation** (`addr = f"vec://{source}"; addr += f"#space={space}"`) — so when `source="cluster://..."`, the literal stored key really is a `vec://` whose body is another full `cluster://` address.
- There is a **`scale:<space>:k<K>` namespace** that lives *inside* the `#space=` fragment — a scheme-like vocabulary the map's 16-scheme table cannot represent because it isn't a scheme, it's a fragment-grammar.

**Why this breaks the union, concretely:** Spine 1 proposes promoting SCHEMES to a flat table with one `parse_fn` per row and table-dispatched `resolve_address`. A flat parser keyed on the leading `scheme://` **cannot parse a nested `vec://cluster://...` address** (it would split on the first `://` and mis-key), and it has **no slot for the `scale:` fragment-namespace.** The map's "granularity is just a field on the row" claim is false here: scale/cluster is a *recursive composition of addresses plus a fragment sub-grammar*, not a granularity. This is the single most important thing a further pass must capture before declaring "one flat address grammar."

**B2 — The entire Shape-B tier is UNADDRESSABLE — the "one address space subsumes everything" claim is false.** events, marks, pins, dispositions, annotations, findings, chat, mail (8 JSONL leaves) are stored but **have no scheme.** The map itself, in §6, says findings ride the event log "address-stamped, no `coherence://` scheme" — i.e. they *reference* addresses but are not *in* the address space. The one-sentence thesis ("one addressed graph of self-describing registry rows") silently excludes the highest-volume, most operationally live tier (events.jsonl = 6,449 lines, mail, dispositions). A union design that can't address its own event/disposition substrate is not one address space — it's an address space plus an unaddressed log tier, exactly the patchwork it claims to dissolve.

**B3 — A SECOND `CapabilityRegistry` class exists, undeduplicated.** `introspection/registry.py:55` defines `class CapabilityRegistry` importing `CapabilityEntry` — distinct from the map's named singleton. The map's "triple capability inventory" (Cluster C) counted *call sites* but missed that there are **two registry classes** for the same noun. The dedup target is bigger than the map states.

**B4 — `model_routing.resolve_model` is NOT unwired — the map's Cluster-D claim is stale.** Map: *"nothing calls it."* Live callers: `roles/focus.py:36`, `roles/reduce_synth.py:48`, `runtime/cc_clone.py:195`. It is referenced as the routing resolver in at least three role/clone paths. Whether it *fires today* vs is *referenced-pending* needs reading (the comments say "does NOT change today's firing"), but the flat "nothing calls it" is falsified. Same suspicion applies to the other Cluster-D "unwired" claims (lifters/forms) — I confirmed `LifterRegistry.extract()` has **no caller** (map correct there) and `forms` are referenced in `bridge.py:908` (map's "no ingest path" needs re-checking against that wiring). The map mixed verified-unwired with assumed-unwired and presented both as fact.

**B5 — `_RESOLVABLE` drift is real and worse than implied.** `runtime/territory.py:32`: `_RESOLVABLE = ("run","cas","skill","context","session","cap","board","clone","mind")` = **9 schemes**, a hand-maintained parallel tuple to the 16-tuple SCHEMES. The map mentions this as a derive-it fix but doesn't note it's already **7 schemes out of sync** (missing blob/vec/ui/code/exchange/file/project) — the drift the union must kill is live now, not hypothetical.

---

## C. UNVERIFIED CLAIMS the map states as fact (a further pass must test)

- **"Lifters/Forms built-but-unwired, complete, tested."** I confirmed lifters have no `extract()` caller, but "tested" is unverified — no test run cited. Forms ARE referenced (`bridge.py:908`). Claim is half-checked.
- **"FsStore as concrete type, Suite never goes through the Protocol."** Plausible (Protocol=10, FsStore=77) but the map never showed a single `Suite` call site typed to `FsStore`. The 13% number is real; the "Suite bypasses the Protocol" *mechanism* is asserted, not traced.
- **"DNA substrate: 621 addresses, 1,050 edges, 14 ghost nodes."** Entirely uncited to a live file in my checks — these come from `counterpart/design/substrate/` which I did not census. The map imports DNA's self-reported numbers without re-verifying, the exact failure mode it diagnoses in others.
- **"structured_output dropped at session_supervisor._turn_done:1086, 3-line fix."** Specific and falsifiable; I did not open that line. If the union's keystone loop depends on it, it must be verified before being called a "3-line fix."
- **Rendering shared-engine claim is the one I CAN confirm GOOD:** `runtime/bridge.py:866` explicitly states `/api/projection` AND the MCP `project` door both route through the same engine via `Suite.project`. Verified true. (Credit where due — the rendering section held up.)

---

## D. WHAT A FURTHER PASS MUST CAPTURE before the union design is safe

1. **Re-census ALL of Shape-A, not a slice.** The 13-vs-1,068 agent-sessions error means every storage count in §3 is suspect. A migration plan sized on wrong counts (e.g. "events.jsonl at 6,449 is the I/O argument" — but agent_sessions at 1,068 files is a far bigger dir-scan problem the map never flagged) will mis-prioritize the Supabase move.

2. **Model the scale/cluster/scale: layer as a first-class part of the address grammar BEFORE flattening SCHEMES to a table.** The flat `parse_fn`-per-row design must be proven against the live nested key `vec://cluster://...#space=scale:...`. Either the grammar is recursive (scheme bodies can be addresses) or the table design is wrong. This is the load-bearing unverified assumption of Spine 1.

3. **Decide the status of the Shape-B unaddressed tier.** Either (a) give events/marks/pins/dispositions/annotations a scheme and admit they enter the address space, or (b) state explicitly that the union is "one address space for content + one unaddressed event tier" — but do not let the one-sentence thesis claim subsumption it doesn't have.

4. **Re-verify every Cluster-D "unwired" claim with a caller-grep** (resolve_model is already falsified). The keystone loop's "only the binding is missing" rests on these being accurately classified.

5. **Recount registries by the right unit** — class defs (28, incl. 2 CapabilityRegistry, PanelRegistry not VerdictPanelRegistry) vs file-discovered *instances* vs dirs — and note which dedup is **already done** (`_BaseEntryRegistry`, board_edges-reuses-relation_types) so Spine-2 doesn't propose work that exists.

**The one-sentence verdict:** The map is a strong viewpoint-synthesis whose two safest-looking sections (storage counts, scheme grammar) contain its worst error (agent_sessions 13→1,068) and its biggest blind spot (the recursive `vec://cluster://...#space=scale:...` grammar + the unaddressed Shape-B tier) — so its central claim, *"one flat address space subsumes all granularities,"* is **not yet earned**: it is contradicted by a live nested scheme-in-scheme key and by an entire event/disposition tier that has no scheme at all.

**Key anchors (verified live):** `store/fs_store.py:920` (`space_address` = flat concat → nested key is real), `runtime/scale.py:34,283` (`vec://cluster://...#space=scale:` live key), `runtime/territory.py:32` (`_RESOLVABLE` = 9, 7-out-of-sync), `runtime/verdict_panels.py:31` (`PanelRegistry`, not VerdictPanelRegistry), `introspection/registry.py:55` (2nd CapabilityRegistry class), `roles/focus.py:36`+`runtime/cc_clone.py:195` (resolve_model IS called), `.data/store/agent_sessions/` (1,066 files, not 13), `runtime/bridge.py:866` (rendering shared-engine — the one verified-good claim).