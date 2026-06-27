"""runtime/guide_author.py — the GUIDE-author (Spec 3 reshaped; the practice that keeps guides true).

Tim greenlit (2026-06-28) a generator that authors the narrative-guide face (`guide://<id>`) FROM real
sources. The 3-review verdict (2026-06-27) reshaped the original "skill-author" hard:
  - it authors human-read GUIDES ONLY, never role-executed skill `content` (closes the prompt-injection
    supply-chain path by construction — a generated guide is read by a human/agent, not executed as a
    role's instructions).
  - GROUNDING IS MANDATORY (abort-on-cold): a guide is composed only from sources that actually resolve
    to content; if NOT ONE does, it raises — never an invented guide.
  - FRESHNESS by source-HASH delta, not run-churn: `source_hash` is a hash of the content-resolvable
    grounded_from sources; when they change, the hash differs → the guide is STALE and due a re-author.
    (Reuses the hash-diff IDEA deliberately, NOT the embedding-reconcile fn in runtime/freshness.py —
    that is the open no-auto-reindex concern.)
  - PROPOSE-DIFF, NEVER CLOBBER: re-authoring an existing guide DEFAULTS to proposing the new source
    (no write) — a human-edited guide is safe by construction; an overwrite is an explicit opt-in.

The model-compose step is INJECTED (`compose`) so the orchestration + every gate are testable with a
stub. `model_composer()` is the production composer (role-resolved model — cognition-is-role-resolved,
never a pinned model); composing on a real model is the LEAD-VERIFY slice (flagged, never green-painted
until run).

LAWS honoured: no silent failures (abort-on-cold + empty-narrative RAISE) · the floor (a guide is read,
never executed) · grounding-mandatory (true-by-construction or it does not exist) · reuse-don't-parallel
(rides create_guide / _write_entry_file / render_entry_source — no parallel write path).
"""
from __future__ import annotations

import hashlib


class GuideAuthorError(Exception):
    """A guide could not be authored truthfully (cold grounding, empty narrative, bad target). Loud."""


def _resolvable_sources(store, grounded_from: list) -> list:
    """Resolve each grounded_from address to its string content where possible. Returns
    [(addr, content), …] for the CONTENT-BEARING addresses (skill:// · context:// · guide:// · cas:// ·
    run:// …). Provenance-only addresses (file:// · project://) that don't resolve to a str are skipped —
    they document ORIGIN, they don't drive freshness (this is by design, not a silent failure: a guide's
    freshness tracks the content it was distilled from). ABORT-ON-COLD: if NOT ONE address resolves to
    content, RAISE — a guide must be grounded in at least one verifiable source."""
    from runtime.cognition import resolve_address
    out = []
    for a in grounded_from:
        try:
            v = resolve_address(store, a)
        except Exception:
            continue                                   # provenance-only / unresolvable — not content
        if isinstance(v, str) and v:
            out.append((a, v))
    if not out:
        raise GuideAuthorError(
            f"abort-on-cold: none of grounded_from={grounded_from} resolved to content — a guide must "
            f"be grounded in at least one verifiable source (registry-is-truth, never an invented guide).")
    return out


def compute_source_hash(store, grounded_from: list) -> str:
    """The freshness fingerprint: a sha256 prefix over the content-resolvable grounded_from sources
    (sorted by address for determinism). When any source's content changes, the hash differs → the
    guide built from it is stale. Raises (abort-on-cold) if nothing resolves to content."""
    srcs = _resolvable_sources(store, grounded_from)
    blob = "\n\x00\n".join(content for _addr, content in sorted(srcs))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def is_stale(store, guide_entry) -> bool:
    """Is a discovered guide stale vs its sources NOW? True if it has no recorded `source_hash` (can't
    prove fresh → a re-author is due) OR the recomputed hash differs from the recorded one."""
    recorded = getattr(guide_entry, "source_hash", None)
    if not recorded:
        return True
    return compute_source_hash(store, guide_entry.grounded_from) != recorded


def staleness_report(suite) -> list:
    """Scan every discovered guide and report freshness — the input to the re-author practice (a future
    cron calls author_guide(on_existing='propose') on the stale ones; it PROPOSES, never clobbers)."""
    reg = suite._entry_registry("guide")
    rows = []
    for gid in sorted(reg):
        g = reg[gid]
        try:
            stale = is_stale(suite.store, g)
            rows.append({"guide_id": gid, "target": g.target, "stale": stale,
                         "source_hash": g.source_hash})
        except GuideAuthorError as e:                  # cold grounding NOW = a loud, surfaced problem
            rows.append({"guide_id": gid, "target": g.target, "stale": True, "error": str(e)})
    return rows


def _derive_id(target: str) -> str:
    """A default guide id from a target address (e.g. skill://summarize → 'using_summarize'). Ids are
    plain lower-case IDENTIFIERS (underscores, never hyphens — the registry convention: a guide id is
    its filename AND a valid module name, like the `extract_decisions`/`corpus_pipeline` skills). The
    author may always pass an explicit guide_id; this is the convenience default."""
    tail = target.split("://", 1)[-1].strip("/")
    safe = "".join(c if (c.isalnum() or c == "_") else "_" for c in tail).strip("_").lower()
    return f"using_{safe}" if safe else "guide"


def author_guide(suite, target: str, grounded_from: list, *, compose,
                 guide_id: str | None = None, label: str | None = None, description: str | None = None,
                 on_existing: str = "propose", dry_run: bool = False) -> dict:
    """Author (or re-author) a guide for `target`, grounded in `grounded_from`, composing the narrative
    via the injected `compose(target, sources) -> str`.

    The gates, in order:
      1. ABORT-ON-COLD — `grounded_from` must resolve to ≥1 content source (else RAISE).
      2. compose the narrative; an empty narrative RAISES (never an empty guide).
      3. stamp `source_hash` (freshness) from the resolved sources.
      4. render+validate the guide source (the same gate create_guide uses).
      5. if the guide EXISTS → PROPOSE (default; returns the new source, writes NOTHING — human-edits
         are safe) unless on_existing='overwrite' (explicit opt-in → re-write via the proven path).
         if NEW → create it live (create_guide).
    `dry_run=True` returns the rendered source + spec WITHOUT writing (for review/testing).
    Returns a dict with `action` ∈ {dry_run, proposed, created, overwritten}."""
    if not isinstance(target, str) or "://" not in target:
        raise GuideAuthorError(f"author_guide: target must be an address (got {target!r}).")
    srcs = _resolvable_sources(suite.store, grounded_from)          # gate 1 — abort-on-cold
    src_hash = compute_source_hash(suite.store, grounded_from)      # gate 3 (fingerprint)
    gid = guide_id or _derive_id(target)
    narrative = compose(target, srcs)                              # gate 2 — the (injected/live) compose
    if not isinstance(narrative, str) or not narrative.strip():
        raise GuideAuthorError(
            f"author_guide({gid!r}): compose returned an empty narrative — fail loud (never an empty guide).")
    spec = {"id": gid, "content": narrative, "target": target,
            "grounded_from": list(grounded_from), "source_hash": src_hash}
    if label:
        spec["label"] = label
    if description:
        spec["description"] = description
    from runtime import authoring as _auth
    source = _auth.render_entry_source(spec, kind="guide")          # gate 4 — render+validate (fail-loud)
    if dry_run:
        return {"action": "dry_run", "guide_id": gid, "target": target, "source": source, "spec": spec,
                "exists": gid in suite._entry_registry("guide")}
    reg = suite._entry_registry("guide")
    if gid in reg:                                                  # gate 5 — exists: propose, don't clobber
        if on_existing == "propose":
            return {"action": "proposed", "guide_id": gid, "target": target, "would_write": source,
                    "current_content": reg[gid].content, "new_content": narrative,
                    "note": ("guide exists — PROPOSING the re-authored source, writing nothing (human "
                             "edits are safe). Pass on_existing='overwrite' to replace deliberately.")}
        if on_existing == "overwrite":
            path = suite._write_entry_file("guide", gid, source, f"re-author guide '{gid}' (overwrite)",
                                           emit_msg=f"re-authored guide '{gid}' (overwrite)")
            return {"action": "overwritten", "guide_id": gid, "path": path}
        raise GuideAuthorError(f"author_guide: unknown on_existing={on_existing!r} (expected 'propose'|'overwrite').")
    result = suite.create_guide(spec)                              # new → create live (the proven path)
    return {"action": "created", **result}


def model_composer(suite, *, role: str, model: str | None = None):
    """Build the PRODUCTION compose(target, sources) — drafts the guide narrative on a ROLE-RESOLVED
    model (cognition-is-role-resolved: the brain is a role → model via the registry, never pinned).
    The role must exist (resolve_role); `model` optionally overrides its bound model. Composing on a
    REAL model is the LEAD-VERIFY slice — never green-painted until actually run against a live model.
    The system-prompt forbids adding anything not supported by the sources (grounded-by-construction)."""
    from fabric import client, transport

    def _compose(target: str, sources: list) -> str:
        r = suite.resolve_role(role)                  # {model, base_url, knobs} — fail-loud if unknown
        cfg = suite.rhm_config()
        src_text = "\n\n".join(f"### {addr}\n{content}" for addr, content in sources)
        sys_p = (
            "You write a concise NARRATIVE how-to guide for the given target, for a human/agent learning "
            "to use it. Ground it ONLY in the provided sources — add nothing they do not support. "
            "Sections: what it is · when to reach for it · how (the steps) · a worked example · gotchas. "
            "Markdown, sentence case, no preamble.")
        msgs = [{"role": "system", "content": sys_p},
                {"role": "user", "content": f"TARGET: {target}\n\nSOURCES:\n{src_text}\n\nWrite the guide."}]
        return client.complete(
            transport.openai_transport(base_url=r["base_url"], timeout=cfg["timeout"]),
            msgs, model=model or r["model"], max_tokens=r["knobs"].get("max_tokens", 2048),
            temperature=r["knobs"].get("temperature", 0.2))

    return _compose
