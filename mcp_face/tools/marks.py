"""mcp_face/tools/marks.py — the MARKS READ tool (consolidated; MCP-DESIGN-PRINCIPLE).

CQRS: the WRITE (`mark(target, mark_type, …)` in server.py) STAYS as its own tool (a consequential
append — kept split from reads, per the law). This module consolidates the three flat READS into ONE
resource tool with a `by` selector:

    marks(by='target')   → every mark on a claim/span target      (Suite.marks_for)
    marks(by='type')     → every mark of a mark_type, cross-target (Suite.marks_by_type — REGISTRY-GATED)
    marks(by='findings')→ the legacy coherence findings at an address (store.findings_for)

Replaces the flat marks_for / marks_by_type / findings_for. Read-only — no resolve/approve/dispatch
(the floor). Reuse-don't-parallel: wraps the existing Suite/store methods, no new engine, no 2nd path.

THE STORE DISTINCTION (load-bearing — the cold agent picks `by` from the docstring alone):
  • by='target' / by='type' read the MARKS store (marks.jsonl): records keyed by a claim/span `target`
    + a REGISTERED `mark_type` (the marks-generalization's two retrieval keys). `by='type'` carries the
    mark_type registry GATE (fail-loud on a typo'd type — registry-is-truth; we wrap Suite.marks_by_type,
    NOT store.marks_by_type, so the gate bites).
  • by='findings' reads the DISTINCT legacy coherence findings store (findings.jsonl), keyed by a corpus
    `address`. There is no Suite method for it — only store.findings_for (mirrors the old flat tool's
    SUITE.store.findings_for reach). SEAM (flagged, not built — out of this lane's file): the symmetric
    long-term home would be a Suite.findings_for wrapper mirroring marks_for; until that lands we mirror
    the existing flat tool's direct store reach (the create_projection in-lane precedent, server.py:910).
"""
from typing import Literal



def register(mcp, suite):
    @mcp.tool()
    def marks(by: Literal["target", "type", "findings"], target: str = "", mark_type: str = "", address: str = "",
              detail: str = "concise", limit: int = 100) -> dict:
        """READ marks / findings (the detection layer — what a mark-pass left). Read-only. Pick `by`:

          by="target"   — every MARK on a claim/span `target`, oldest-first (the mark THREAD there; the
                           gold-likelihood PROFILE is this composed with its evidence — a READ, never a
                           stored score; Tim sees-WHY and overrules, positive-only). `target` (required)
                           is the marked thing (a corpus address, a claim id, a span ref). An unmarked
                           target → an HONEST empty list (never a fabricated mark).
          by="type"     — every MARK of `mark_type` across targets, oldest-first (the cross-target view of
                           one mark kind — e.g. every ai_fingerprint mark, the denoising surface).
                           `mark_type` (required) is GATED fail-loud against the live mark_types registry
                           (a typo'd type would silently look like 'no marks' — registry-is-truth; see
                           cognition_info for the registered types, or create one via create(kind=mark_type)).
          by="findings" — the legacy COHERENCE findings at a corpus `address`, oldest-first (the detection
                           thread the coherence pass left). `address` (required). DISTINCT from marks: this
                           reads the coherence findings store (findings.jsonl) keyed by address, NOT the
                           marks store (keyed by claim/span target + registered mark_type). An address with
                           no findings → an HONEST empty list.

        `detail`: "concise" (default) returns high-signal fields per branch; "detailed" returns the full
        records. `limit` (default 100) caps the rows. WRITING a mark is the separate `mark` tool (CQRS).
        Read-only — a mark/finding is telemetry-class, never a resolve/approve/dispatch (the floor)."""
        BY = ("target", "type", "findings")
        if by not in BY:
            return {"error": f"marks: unknown by={by!r}. Valid: {list(BY)} — "
                    "target=marks on a claim/span (needs `target`) · type=marks of a kind across targets "
                    "(needs `mark_type`, registry-gated) · findings=legacy coherence findings at a corpus "
                    "address (needs `address`). To WRITE a mark use the `mark` tool (CQRS — reads vs writes)."}
        if detail not in ("concise", "detailed"):
            return {"error": f"marks: detail must be 'concise' or 'detailed', got {detail!r}."}

        def _cap(rows):
            return list(rows)[:limit]

        if by == "target":
            if not target:
                return {"error": "marks(by='target') needs `target` — the claim/span the marks sit on "
                        "(a corpus address, a claim id, or a span ref)."}
            rows = _cap(suite.marks_for(target))
            if detail == "concise":
                rows = [{"mark_type": r.get("mark_type"), "value": r.get("value"),
                         "confidence": r.get("confidence"), "source_pass": r.get("source_pass"),
                         "evidence": r.get("evidence"), "ts": r.get("ts")} for r in rows]
            return {"by": by, "target": target, "total": len(rows), "detail": detail, "marks": rows}

        if by == "type":
            if not mark_type:
                return {"error": "marks(by='type') needs `mark_type` — a registered mark-type. See the "
                        "live registry via cognition_info; author one via create(kind=mark_type). "
                        "Registry-gated fail-loud (a typo'd type would falsely look like 'no marks')."}
            # Wrap the SUITE method (NOT store.marks_by_type) so the mark_types registry GATE bites — an
            # unknown type RAISES a teaching ValueError here, never a silent empty list.
            rows = _cap(suite.marks_by_type(mark_type))
            if detail == "concise":
                rows = [{"target": r.get("target"), "value": r.get("value"),
                         "confidence": r.get("confidence"), "source_pass": r.get("source_pass"),
                         "evidence": r.get("evidence"), "ts": r.get("ts")} for r in rows]
            return {"by": by, "mark_type": mark_type, "total": len(rows), "detail": detail, "marks": rows}

        if by == "findings":
            if not address:
                return {"error": "marks(by='findings') needs `address` — a corpus address (a run://). "
                        "This reads the legacy coherence findings store (DISTINCT from marks): findings "
                        "are keyed by address, marks by claim/span target + registered mark_type."}
            rows = _cap(suite.store.findings_for(address))
            if detail == "concise":
                rows = [{"kind": r.get("kind"), "address": r.get("address"), "state": r.get("state"),
                         "source": r.get("source"), "evidence": r.get("evidence"), "ts": r.get("ts")}
                        for r in rows]
            return {"by": by, "address": address, "total": len(rows), "detail": detail, "findings": rows}
    return marks
