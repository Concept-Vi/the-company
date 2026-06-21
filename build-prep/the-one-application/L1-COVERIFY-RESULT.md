# L1 (grounded walk-through) — JOINT CO-VERIFY RESULT (fork, 2026-06-21)

The lead's L1 test: open a theorem-fork card through the LIVE `/api/decision/explain` route and confirm,
by use — (fork) policy + coordinate fire · (recollection) the explanation attributes ideas to Tim,
flags the AI-reading, AND **stays on-topic** · (projection) it renders/streams.

## Verdict: WIRE ✓ · CONTENT ✗ (theorem-fork) — a GATE, not a footnote

### fork half — PROVEN ✓
The composing route works. Verified by use, real model call (not engine-direct mock):
- **authorize** (`build-consent-posture`) → 2.7s on the LIVE rhm brain `cyankiwi/Qwen3.5-4B-AWQ-4bit`.
  Operator-legible (zero machine names/addresses), grounded in Tim's corpus (approval≠authorization,
  one-entity), **on-topic**, risk-framing applied, `policy.risk-grounding` fired, caveat correctly ABSENT.
- **theorem-fork** (`cube-3d`) → `policy.theorem-grounding` + `coordinate={subtype:'theorem-fork'}` fire;
  the never-assert `caveat` RIDES as a second input; the `grounding_note` correctly FLAGS projection
  ("specific calculation of axis values … flagged as AI-projection/inference"). The wire composes all
  three halves (block + policy + framing-coordinate + caveat) faithfully.

### recollection/corpus half — DEFECTIVE ✗ (theorem-fork only)
The `cube-3d` explanation is **OFF-TOPIC**. The card asks "how should the cube become 3-D — flat
projection from each viewpoint (projection IS the math) / orbit the wheel / true 3-D?" The generated
explanation instead discusses generic substrate "multi-orientation", "App-A-to-E", "C-UI surface is the
locus of reshaping", "round-D2 / substrate-companion" — Vi software-architecture, NOT his cube/projection
mathematics. Fluent, never-assert-compliant, cites REAL framework claims — and answers the wrong question.

**The never-assert caveat does NOT catch this** — nothing false is asserted; it faithfully explains the
wrong (real) claims. To Tim opening that card it is a confident, well-formed explanation about substrate
multi-orientation that has nothing to do with his cube — and he has no signal it is off-topic. That is
arguably WORSE than the cube-error (a wrong number is detectable; a coherent off-topic explanation is not).

### ROOT CAUSE (evidenced) — the queried asset lacks his math
`explanation_grounding` (theorem-fork) → `recall_determine.determine(text, asset="theorem", max_claims=40)`
→ queries `space="extractions"` filtered to the `theorem` asset:
`.data/store/extractions/extractions-theorem.jsonl` (14,592 chunks). Raw keyword scan of that asset:
- **cube: 0 · perpendicular: 0**
- projection: 121 — but ALL software-sense ("skins are read-projections of the event stream",
  "parameter-projection", "substrate-projections over the same event-log").
- dimension: 66 · recursion: 91 · unity: 57 · self-division: 3 — present, substrate-architecture sense.

So the `theorem` extraction asset is baked from Vi software/substrate notes, **not** Tim's Structural
Completion mathematics (seed `2π/n=(1/n)^k`, self-division of unity, anamorphic projection, perpendicular
dimension-raising, the cube). `determine` retrieves substrate-multi-orientation claims because that is
what is THERE to retrieve. This is the **absent-in-the-queried-asset** case (matches the known pass-2 seam:
"substrate semantic defaults to wrong vault"). NOT a retrieval/rerank bug.

### OWNER + FIX
- **Upstream corpus/ingestion (primary):** `asset="theorem"` must be (re)baked from the universal-mechanics
  MATH vault (math-verification + universal-substrate-system = his Structural Completion theorem), not the
  software-substrate notes. Until `asset="theorem"` actually contains his cube/projection/self-division
  math, no retrieval or row-targeting can ground a theorem-fork explanation correctly.
- **Decision-registry (co-owned, secondary):** theorem-fork rows (`cube-3d`, `dimension-meaning`) carry
  `address`/`grounding_source` = null → determine queries by meaning-text. A targeted `grounding_source`
  pointing determine at his actual cube/projection chunks helps ONLY once those are indexed.
- **fork (me):** the wire is correct and verified. Nothing to fix in `/api/decision/explain` or
  `cog_run_role`. I do NOT patch recollection's determine or the corpus.

### GATE
The theorem-fork explain path is **NOT safe to surface to Tim** (his highest-stakes, most-personal
decision class) until `asset="theorem"` carries his math. The authorize/trade-off paths ARE safe
(their `recall_for_decision` bundle is on-topic, verified). L1 "closes" (per the lead) on this co-verify
+ Tim's actual walk-through — so L1 is NOT closed: the wire is proven, the theorem-fork content is gated.
