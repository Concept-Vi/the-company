# PRINCIPLE — No Confidence · Tags + Counts · The Temporal Axis is First-Class

> Tim, 2026-06-09: **"No confidence, tags and counts. Temporal axis play a real role in this."** A standing design law for the cognition self-improvement program + the Live Intent Resolution Surface. Externalised reference (orients the multi-agent build).

## 1. NO CONFIDENCE (the enforced invariant — resolves SYSTEM-GAPS reuse-decision b)
No confidence scores anywhere — not "78% likely a web app," not a `confidence: float` that pretends at precision. Confidence scores are shallow + subjective (Tim's standing objection; the Surface doc §8/§33 "avoid fake certainty"). They are ENFORCED OUT, not discouraged:
- Evidence is **traceable interpretive evidence**: tags · counts · structured observations · relationships · rejections · decisions — never a probability display.
- **Enforce, don't convention** (Tim's call): `mark()` / the output schemas should NOT carry a `confidence` field as the evidence representation. Where a degree-of-evidence is needed, it is a COUNT (how many times observed) + its TEMPORAL SHAPE (below), not a float. (Migration: the existing `confidence:float` fields on register_element/judge_mining/etc. are the old shape — flagged to move to count+trajectory; a schema/floor invariant is the build.)

## 2. TAGS + COUNTS (the representation)
- **Tags** — discrete labels on statements/choices/reactions/objects (prefers_visual, rejects_static_document, wants_autonomous_execution…).
- **Counts** — repeated tag occurrences. The count is what reveals a pattern, NOT a confidence guess.
- **Structured observations** — human-readable interpretations derived from tags+counts ("user repeatedly frames the system as universal → schemas should be modular").
- Rejections count as much as acceptances. Decisions carry their reason. (Surface doc §9.)

## 3. ★ THE TEMPORAL AXIS IS FIRST-CLASS (the new law)
Temporal is NOT metadata bolted on — it is a FIRST-CLASS AXIS alongside the SEMANTIC (embedding spaces) and the STRUCTURAL (graph). A count without time is shallow; the signal is in *when* + *how it moved*.

### 3a. A count is a TRAJECTORY, not a scalar
`prefers_visual: 7` → carry `{count, first_seen, last_seen, occurrence_series}`. The shape is the meaning:
- **rising** → a hardening preference (momentum) · **fading** → stale / being abandoned · **bursty** → a moment, not a pattern · **steady** → a stable trait. The system reasons over the shape, never a flat number.

### 3b. Recency-weighting in retrieval + the evolving model
A thing observed NOW and one observed weeks ago are NOT equal evidence. Corpus/space retrieval + the user/project model weight by recency + reinforcement, so the model EVOLVES (decay of the unreinforced; a rejected-then-re-embraced direction reads as a real reversal, not a contradiction). The "alive / growing over time" the Surface §14.1 reaches for IS this.

### 3c. The event store is the TEMPORAL SPINE
Every interaction is already timestamped (the event store / run-index / corpus `ts`). "How a decision emerged" (Surface §18) is a REPLAYABLE temporal trace, not a static ledger row. The Decision Ledger gains before/after: what was believed WHEN, what changed it.

### 3d. The downstream organs become temporal BY NATURE
- **② drift-radar:** drift IS "doc + code diverged OVER TIME"; built-twice is "the second appeared LATER." Time makes drift legible — add the temporal dimension to the drift query.
- **③ failure-patterns:** the question that matters is "is this failure-mode RISING or did I fix it?" — a trajectory over the transcript timeline, not a static cluster.
- **the user/project model:** preferences strengthen/decay; the model is a time-series, not a snapshot.

## 4. WHERE IT EXISTS / WHERE IT'S NET-NEW (lean — ground with ① when the corpus is online)
- ✅ EXISTS: timestamps on corpus records (`ts`) + the run-index events + `mark()` (occurrence records). The temporal RAW DATA is captured.
- 🟡 PARTIAL: counts exist as aggregates but NOT as trajectories; no recency-weighting in retrieval; no decay.
- 🔴 NET-NEW: the trajectory representation (count→series), recency/decay-weighted retrieval, the temporal drift/failure queries, the time-series user/project model, the no-confidence schema invariant.

## 5. DESIGN CHOICES THIS OPENS (surface to Tim — his axis to shape)
- **Decay function:** linear recency, exponential decay, or reinforcement-with-half-life? (How fast does an unreinforced tag fade?)
- **Trajectory granularity:** per-occurrence series (heaviest, fullest) vs windowed buckets (session/day) vs just {first_seen,last_seen,count,slope}? (Lean: start with {first,last,count,slope} — cheap, captures rising/fading/steady — richen later.)
- **A temporal SPACE?** alongside the semantic spaces (principles/topics/worldview), is "when" a queryable axis (time-sliced embeddings / time-filtered find_relations), or a weighting ON the existing spaces? (Lean: a weighting first, a time-sliced space if discovery needs it.)

## 6. STANDING
This is now a program law: **no confidence; tags+counts as evidence; the temporal axis is first-class (trajectories, recency, decay, replay).** Every new role/schema/composition obeys it. The no-confidence invariant + the trajectory-count are the first concrete builds it implies.
