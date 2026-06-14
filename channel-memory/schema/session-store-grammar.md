# Session Store — Grammar & Schema

```
trust: fabric-derived          # the fork's own structural work — grounded in the .jsonl + code, cite the fields; not a Tim intent
author: ch-8djrpmsl / 11e7d395 (fork)
date: 2026-06-14
verified: by-execution (jq extraction + build_timeline/resolve_cut run on the live lead+fork sources) + read-only (code read of session_pointintime.py)
```
> Per [[COMMIT-GRAMMAR]] §2. A correction was applied 2026-06-14 (the §4 `forkedFrom` claim) after re-verifying against truncated output — logged inline, not silently overwritten.

**Owner lane:** FORK (ch-8djrpmsl / 11e7d395) — session-store schema is the fork's locked lane.
**Status:** Findings VERIFIED by first-hand extraction (2026-06-14). **Document FORMAT is provisional** — pending the co-designed `../COMMIT-GRAMMAR.md` (the lead leads that; no single member locks it). Content stands; conventions may be re-shaped to the agreed grammar.
**Serves:** vision §1.6 (schema → programmatic tooling → source-registry entry), §1.3 (the scan), §1.4 (distances/map), §1.9 (projectable DATA). See `../vision/2026-06-14-session-splicing-and-channel-memory.md`.

> **Evidence legend (Tim's mandate):** **[O]bserved** = seen directly in the `.jsonl` without execution · **[I]nferred** = pattern-match, NOT verified · **[V]erified** = confirmed by running an extraction. Every claim below is tagged.

---

## 1. Store location & encoding  [O]
- Transcripts live at `~/.claude/projects/<encoded-cwd>/<session-id>.jsonl`.
- **encoded-cwd** = the session's cwd with `/` and `.` → `-`. (e.g. cwd `/home/tim` → dir `-home-tim`.)
- One `.jsonl` per session; one JSON event per line. Append-only during a session's life.
- Side files in the same project dir: `tool-results/` (large tool outputs spilled to `<id>.txt` via `<persisted-output>`), `subagents/`, `workflows/`, `tool-results/`, plus `<session-id>/` subdirs for per-session spill.
- **Concrete sample (this program):**
  - Lead origin: `-home-tim/bda8ce28-6dfb-4a76-b13a-bc016b8574ca.jsonl` — 20.4 MB, **12561 lines**, 2026-06-10 → 2026-06-14.
  - Fork (me): `-home-tim/11e7d395-8bb9-463f-bcb3-06616da49ebb.jsonl` — 6.6 MB.

## 2. Event taxonomy — `.type` distribution (lead session)  [V]
`jq -r '.type' <file> | sort | uniq -c`:

| count | type | what it is |
|------:|------|------------|
| 4102 | `attachment` | file/compact_file_reference attachments pulled into context |
| 2798 | `assistant` | model turns — **carry `.message.usage` (tokens) + `.message.model`** |
| 1390 | `user` | user turns AND tool-result carriers (see §3 trap) |
| 492 | `system` | system events — **incl. `subtype:"compact_boundary"`** (§3) |
| 459 | `permission-mode` / `mode` / `agent-setting` | per-turn UI/permission state |
| 452 | `last-prompt` | 451 | `ai-title` | 451 | `agent-name` | per-prompt metadata (~1 per user prompt) |
| 366 | `queue-operation` | enqueue/dequeue of injected messages (incl. `<channel>` pushes) |
| 351 | `worktree-state` · 204 `file-history-snapshot` · 127 `bridge-session` | env/tooling state |

## 3. ★ The compaction-boundary grammar — the headline reconciliation  [V]
**A compaction boundary is a PAIR of consecutive events:**
1. `type=="system"` **AND** `subtype=="compact_boundary"` — content `"Conversation compacted"`, carries `logicalParentUuid`. The structural marker.
2. immediately followed by `type=="user"` **AND** `isCompactSummary==true` — `message.content` is a plain **string** (the summary prose, opens *"This session is being continued from a previous conversation that ran out of context."*), and carries distinctive keys `isVisibleInTranscriptOnly`, `slug` (an auto-label, e.g. `declarative-inventing-codd`), and **no `toolUseResult`**.

**Two structural discriminators, distinct roles (refined by reading + executing the existing `runtime/session_pointintime.build_timeline`):**
- **COUNTING a boundary** keys on the `system`/`compact_boundary` event — **deduped against payload copies** (a re-appended preserved window can contain a byte-copy of an earlier `compact_boundary` with the same uuid; that copy is payload, not a new boundary).
- **`isCompactSummary==true`** marks the summary HEAD that follows the boundary (its `parentUuid` = the boundary's uuid); it extends the resume-cut, it does NOT count as a separate boundary.
- Both are STRUCTURAL. Neither is text. (My earlier "single discriminator = isCompactSummary" was imprecise — corrected here.)

**Verified by execution on the lead source [V]:** `build_timeline(bda8ce28.jsonl)` → **boundaries: 1** — compact:1, line **8401**, uuid `38f1ef23-…`, ts `2026-06-13T14:21:07.199Z`, **trigger=`auto`** (1M-window auto-compaction, not manual `/compact`), resume_cut_line 8402. The summary HEAD (`isCompactSummary:true`, uuid `64fc8fd7-…`) sits at line 8403. `compact_boundary` system events in the file = **exactly 1** (`jq` subtype count confirms).

**Reconciliation of the open discriminator (vision §1.6):**
- `build_timeline` reported **1 boundary** → **CORRECT** (it keys on `isCompactSummary`). Not a bug.
- The earlier "3 markers" (lines 8403/11328/11342) = **1 real + 2 FALSE POSITIVES.** Lines 11328 & 11342 are `type:user` **tool-result** carriers (`sourceToolAssistantUUID` + `toolUseResult`; 11328 is a `<persisted-output>` blob about embeddings). Their *content* merely quoted continuation-like phrases. `isCompactSummary` on both = `null`.
- `compactMetadata` near line 5190 = top-level field present but **`null`**; the string only appeared *inside* a research-doc tool result ("LANE 1: Point-in-Time Mechanics"). It's a real schema field, unpopulated for **auto**-compaction (likely populated by manual `/compact`).

**ROOT CAUSE of "only one compaction in a 4-day / 12.5k-line session":** the session runs on **`claude-opus-4-8[1m]` — the 1M-token context window.** A 1M window runs enormously far before filling once. [I: the 1M-window→single-compaction causal link is inferred from the model id + the single boundary; consistent, not independently executed.]

**THE TRAP (for the programmatic tool):** never detect compactions by text-grepping for "continued from" / "compaction" / "compactMetadata" — those strings appear inside `toolUseResult` and `attachment` content. **Detect structurally only:** `subtype=="compact_boundary"` or `isCompactSummary==true`.

## 4. Fork / branch provenance mechanism  [V] — CORRECTED
> ⚠️ Correction (2026-06-14): an earlier draft claimed "no forkedFrom field exists." **That was WRONG** — a misread of 200-char-truncated grep output (the field sits past the truncation). It is itself an instance of this vault's core law: don't text-trust, verify on structure. Corrected facts below, re-verified by execution.

- **`forkedFrom` DOES exist and IS the explicit provenance link.** Shape: `{"sessionId": "<parent>", "messageUuid": "<event's original uuid>"}`. In the fork (11e7d395): **1718 events carry it**, all with `sessionId == bda8ce28` (uniform — the single parent); **630 events do NOT** carry it.
- **The discriminator partitions the file:** `forkedFrom` present ⇒ an event INHERITED from the parent (the compaction summary head + the re-appended preserved window); `forkedFrom` absent ⇒ the fork's OWN new turn. The inherited block is contiguous (fork lines 0..1717), the fork's own life begins ~line 1718 — and grows (live).
- **The fork keeps the parent's ORIGINAL uuids** (fork L1 `uuid==38f1ef23`, L2 `uuid==64fc8fd7` — identical to the parent's branch pair, NOT remapped). ∴ this fork was made by the **native Claude Code fork**, not the Company's `materialize_at_point`.
- **Branch detection rule (verified on this pair):** `forkedFrom.sessionId` names the parent; the inherited block = parent's compacted state at the branch; the fork's own life = the no-`forkedFrom` tail. [I: that this exact partition holds for every CC-era fork is inferred from one fork — verify on a 2nd before coding as law; but the field's presence is [V].]
- **The root has none:** bda8ce28 (the origin) carries no `forkedFrom` on its own events (L100 = ABSENT). Absence-of-forkedFrom-on-all-events ⇒ a root session.

### 4b. `materialize_at_point` vs the native fork — a fidelity gap to flag  [O, code-read]
`runtime/session_pointintime.materialize_at_point` (R3.4, the Company's clone tool) emulates the native fork but differs in TWO ways:
1. It **remaps** every prefix uuid (`uuid5(REMAP_NS, "{nsid}:{uuid}")`) — the native fork keeps originals.
2. Its `forkedFrom` uses a **constant** `messageUuid` = the cut uuid for ALL events (`fork_stamp` built once from `cut["cut_uuid"]`, line 345/366) — the native fork uses **each event's own** original uuid (verified: fork L1→38f1ef23, L2→64fc8fd7, L100→8fa86f9f, all distinct).
→ Functionally resume-able either way, but NOT a byte-faithful native shape. Flag for the verified-spine lane: if downstream tooling reads `forkedFrom.messageUuid` per-event, the materialize emulation will mislead. (Raised to the lead.)

## 5. Attribution & token fields  [V]
- **Every assistant event** (2798/2798) has `.message.usage` (object, 100% present): `input_tokens`, `output_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens`, `service_tier`, `speed`, plus a per-`iterations` breakdown. → **Real per-turn tokens; no estimation needed.**
- `.message.model` per assistant turn — lead distribution: **1984 `claude-opus-4-8`**, **793 `claude-fable-5`**, **21 `<synthetic>`**. Per-turn model attribution is real and projectable. [I: why 793 fable-5 turns sit inline in the main file — sub-agent inlining vs a fable mode — is not yet determined; an "interesting" scan dimension, not blocking.]
- Sender attribution: `.type` (`user` vs `assistant`) + `.message.role`; tool turns = `user` events bearing `toolUseResult`.
- Timestamps: top-level `.timestamp` (ISO-8601, ms). Time-gaps between consecutive turns = the walk/sleep signal (vision §1.3 "other things of interest").

## 6. ★ The projectable SCAN ROW schema (vision §1.3 + §1.9)
The scan must emit **DATA rows, not prose**, so the Company UI projects them for free (§1.9). One row per event (or per turn):

```
{ line, uuid, parentUuid, ts,
  type,                      # assistant|user|system|attachment|...
  role,                      # message.role
  attribution,              # "tim" | "assistant" | "tool" | "system" | "synthetic"
  model,                     # message.model (assistant only)
  in_tokens, out_tokens, cache_read_tokens, cache_creation_tokens,   # message.usage
  content_bytes,            # size of the rendered content
  is_tool_result,           # has toolUseResult
  is_boundary,              # subtype==compact_boundary OR isCompactSummary==true
  boundary_slug,            # slug, when a boundary
  gap_sec }                 # ts - prev.ts
```
This row IS the registry shape for §1.6 (session store as a SOURCE) → the projection keys off it directly.

## 7. Status & open items (this lane)
> **Scope correction (2026-06-14, both advisors):** read-only/reversible analytics (scan, map, the scanner tool) are NOT gated — they're advisor-cleared by reversibility + are the fork's verified tim-direct + locked lane. Only AUTHORITY, the source-REGISTRY commitment, the clone-fleet LAUNCH + perms, config edits, and the materialize-fidelity fix stay [TIM-GATED]. (An earlier draft over-gated the scan; corrected.)

**DONE / verified (reversible, built):**
- [V] Compaction-boundary grammar reconciled (§3) — `compact_boundary` (deduped) counts; `isCompactSummary` marks the head; 1 real boundary in the lead, `trigger=auto`, 1M-window root cause.
- [V] **Spine cut-path is STRUCTURAL for N>1 — verified by EXECUTION:** `build_timeline` run on the fork (11e7d395) returns **3** boundaries (`compact:1/2/3`); `resolve_cut`→`build_timeline` returns the Nth `compact_boundary`'s `resume_cut` (session_pointintime.py L246/248/258); NO text-match anywhere. ⇒ `cc_clone(at="compact:N")` cuts at real boundaries for any N, never a "continued from…" false positive. (The fork doubled as the multi-boundary test case I couldn't find elsewhere — see the no-multi-boundary-in-store note below.)
- [V] `forkedFrom` provenance mechanism (§4, corrected) + the `materialize_at_point` fidelity gap (§4b — documented, HELD per scope).
- [V] **Programmatic SCANNER built + run** — `runtime/session_scan.py` → `channel-memory/scans/<sid>.{summary.json,rows.ndjson}` for both sessions (§6 rows; attribution splits human/tool/channel/compaction; real per-turn tokens; system-subtype taxonomy incl. `turn_duration`/`away_summary`/`model_refusal_fallback`; dense-message profile; largest time-gaps = away signal).
- [V] **Lineage/DISTANCE map built + run** — `runtime/session_lineage.py` → `channel-memory/map/lineage.{json,md}`: root start, the branch, shared-trunk vs parallel-divergence distances, oriented (§1.4).

**Open, this lane (autonomous):**
- [ ] Verify the §4 fork-detection partition on a SECOND fork (only one fork exists in-store; generalisation-proof pending a 2nd).
- [ ] Determine the **793 `claude-fable-5`** lead turns vs the fork's **0** (sub-agent inlining vs a fable mode) — quantified, cause open.
- [ ] **No multi-boundary session exists elsewhere in `~/.claude/projects`** (swept: none with >1 `compact_boundary` except the fork) — the docstring's "41-boundary" session isn't present; the fork (N=3) is the live N>1 witness.
- [ ] Confirm `compactMetadata` semantics on a **manual `/compact`** session (vs `auto`).

**[TIM-GATED] (await his direct word; PLANs may be committed, execution waits — [[COMMIT-GRAMMAR]] §5):**
- Register the session store as a SOURCE in the source registry (vision §1.6) — the projection-feeding commitment; coordinate shape with the lead.
- Align `materialize_at_point`'s `forkedFrom` to native fidelity (§4b) — registry-grade, ahead of need.
- Mass clone-fleet launch + perms; program authority.

---
*Foundational schema entry of the common channel-memory vault. Cross-link: [[2026-06-14-session-splicing-and-channel-memory]]. Format provisional pending [[COMMIT-GRAMMAR]].*
