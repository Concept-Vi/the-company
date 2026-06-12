"""runtime/render_declaration.py — the RENDER-DECLARATION layer (Session Fabric R1.2).

THE GENUINELY-NEW MECHANISM: a session's output DECLARES how a UI should render it. Every
event a Claude Code session emits (stream-json stdout, the transcript surface, and the
supervisor's own wire events) is mapped to a TYPED declaration from the registry
`runtime/render_declarations.json` — placement · component · update-target · stream-accumulator
· blocks-execution · a field_map extracting exactly what a UI needs to draw it. A UI (or any
consumer — the voice seam, the R6 corpus-driving agent) renders from the DECLARATION, never
from bespoke per-event-type logic.

REGISTRY-SHAPED (the R11/heart frame): the registry is typed content validated against closed
vocabularies at load (fail loud on an unknown placement/component/etc. — never ad-hoc JSON).
The lookup is a declared law, implemented once here:

    exact "type/subtype"  →  family "type/*"  →  bare "type"  →  UNDECLARED
    assistant/user content blocks  →  "<type>.content.<block.type>"
                                       (tool_use refines by tool name first)
    stream_event  →  inner dispatch ("stream_event/<inner>" with content_block_start/_delta
                                      refined by block/delta type)
    attachment    →  "attachment/<attachment.type>"

NO SILENT DROPS (the R1.2 bar + the no-silent-failures law): an event that matches nothing
still RENDERS — it gets the loud UnknownEvent declaration, `undeclared: true`, and a DROP is
recorded through the registered hooks (gap-pressure law: constrained operation is a sensor
for its registry; the supervisor turns drops into `agent_sessions.render_drop` events). A
family-fallback hit ("system/*", "attachment/*", …) renders as declared but ALSO records a
soft drop (`family_fallback: true`) — the registry wants an exact entry.

Honest field extraction: a field_map path that resolves to nothing is ABSENT from `fields`
(honest-absent, never a fabricated null). Long string fields are capped at FIELD_CAP with an
explicit `<field>__truncated: true` marker beside them — truncation is visible, never silent.

Proven by: tests/render_declaration_acceptance.py (registry validity · dispatch matrix over
the documented shapes · 100% declaration coverage over the REAL T2 stream captures
(~/xsession-tests) and a real-transcript sample · the loud undeclared path · the consumer
renderer in ops/render_declared_stream.py rendering every declared event).
"""
from __future__ import annotations

import json
import os
import threading
from typing import Any, Callable

_REGISTRY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "render_declarations.json")

FIELD_CAP = 65536          # per-string-field cap on extraction — capped LOUDLY (a *_truncated marker)

# the declaration keys a registry entry may carry beyond the required ones
_REQUIRED = ("surface", "placement", "component", "is_terminal", "blocks_execution", "evidence",
             "field_map", "summary")
_OPTIONAL = ("update_target", "stream_accumulator", "blocks_from")

_LOCK = threading.Lock()
_REGISTRY: dict | None = None

# drop hooks: callables fired on every undeclared/family-fallback hit — fn(record: dict).
# The supervisor registers one that emits agent_sessions.render_drop; tests register collectors.
_DROP_HOOKS: list[Callable[[dict], None]] = []


class RegistryInvalid(Exception):
    """The render-declaration registry failed validation — fail loud at load, never serve a
    half-valid registry (registry-is-truth)."""


def on_drop(fn: Callable[[dict], None]) -> None:
    """Register a drop hook (gap-pressure consumer). Duplicate registrations are ignored."""
    if fn not in _DROP_HOOKS:
        _DROP_HOOKS.append(fn)


def _fire_drop(record: dict) -> None:
    for fn in list(_DROP_HOOKS):
        try:
            fn(record)
        except Exception:
            # a drop hook must never break declaration; the hook's owner observes its own failure
            pass


def load_registry(path: str = _REGISTRY_PATH, *, force: bool = False) -> dict:
    """Load + VALIDATE the registry (cached). Validation is the typed-content guarantee:
    every declaration's surface/placement/component/update_target/stream_accumulator/evidence
    must come from the registry's own closed vocab; required keys must be present; field_map
    values must be non-empty strings. Any violation → RegistryInvalid naming the entry."""
    global _REGISTRY
    with _LOCK:
        if _REGISTRY is not None and not force:
            return _REGISTRY
        with open(path, "r", encoding="utf-8") as f:
            reg = json.load(f)
        vocab = reg.get("vocab") or {}
        decls = reg.get("declarations") or {}
        if not decls:
            raise RegistryInvalid(f"{path}: no declarations")
        problems: list[str] = []
        for key, d in decls.items():
            for req in _REQUIRED:
                if req not in d:
                    problems.append(f"{key}: missing required field {req!r}")
            for fld, vocab_name in (("surface", "surfaces"), ("placement", "placements"),
                                    ("component", "components"), ("evidence", "evidence")):
                v = d.get(fld)
                if v is not None and v not in (vocab.get(vocab_name) or []):
                    problems.append(f"{key}: {fld}={v!r} not in vocab.{vocab_name}")
            if d.get("update_target") is not None and d["update_target"] not in (vocab.get("update_targets") or []):
                problems.append(f"{key}: update_target={d['update_target']!r} not in vocab.update_targets")
            if d.get("stream_accumulator") is not None and d["stream_accumulator"] not in (vocab.get("stream_accumulators") or []):
                problems.append(f"{key}: stream_accumulator={d['stream_accumulator']!r} not in vocab.stream_accumulators")
            fm = d.get("field_map")
            if not isinstance(fm, dict):
                problems.append(f"{key}: field_map must be a dict")
            else:
                for out, src in fm.items():
                    if not isinstance(src, str) or not src:
                        problems.append(f"{key}: field_map[{out!r}] must be a non-empty dotted path")
            for k in d:
                if k not in _REQUIRED and k not in _OPTIONAL:
                    problems.append(f"{key}: unknown declaration field {k!r} (schema-additive means "
                                    f"declared-additive: add it to _OPTIONAL with meaning, never ad-hoc)")
        if problems:
            raise RegistryInvalid(f"{path}: {len(problems)} validation problem(s):\n  " + "\n  ".join(problems))
        _REGISTRY = reg
        return reg


def _resolve(path: str, root: Any) -> Any:
    """Dotted-path resolution into a dict tree. '.' = the root itself. Missing → None
    (honest-absent — the caller omits the field)."""
    if path == ".":
        return root
    cur = root
    for part in path.split("."):
        if isinstance(cur, dict):
            cur = cur.get(part)
        else:
            return None
        if cur is None:
            return None
    return cur


def _extract(field_map: dict, root: Any) -> dict:
    out: dict = {}
    for name, path in field_map.items():
        v = _resolve(path, root)
        if v is None:
            continue                            # honest-absent
        if isinstance(v, str) and len(v) > FIELD_CAP:
            out[name] = v[:FIELD_CAP]
            out[name + "__truncated"] = True    # truncation is VISIBLE, never silent
        else:
            out[name] = v
    return out


def _lookup(decls: dict, *candidates: str) -> "tuple[str, dict, bool] | None":
    """First candidate that exists wins. Returns (key, declaration, family_fallback)."""
    for i, key in enumerate(candidates):
        d = decls.get(key)
        if d is not None:
            return key, d, key.endswith("*")
    return None


def derive_key(ev: dict) -> "list[str]":
    """The lookup candidates for a raw event, most-specific first (the declared lookup law)."""
    t = ev.get("type")
    st = ev.get("subtype")
    if t == "stream_event":
        inner = (ev.get("event") or {})
        it = inner.get("type") or "?"
        if it == "content_block_delta":
            dt = ((inner.get("delta") or {}).get("type")) or "?"
            return [f"stream_event/content_block_delta.{dt}", "stream_event/content_block_delta.*",
                    "stream_event/*"]
        if it == "content_block_start":
            bt = ((inner.get("content_block") or {}).get("type")) or "?"
            return [f"stream_event/content_block_start.{bt}", "stream_event/content_block_start.*",
                    "stream_event/*"]
        return [f"stream_event/{it}", "stream_event/*"]
    if t == "attachment":
        at = ((ev.get("attachment") or {}).get("type")) or "?"
        return [f"attachment/{at}", "attachment/*"]
    if st:
        return [f"{t}/{st}", f"{t}/*", str(t)]
    return [str(t)]


def _block_key(parent: str, block: dict) -> "list[str]":
    bt = block.get("type") or "?"
    cands = []
    if bt == "tool_use" and block.get("name"):
        cands.append(f"{parent}.content.tool_use.{block['name']}")
    cands += [f"{parent}.content.{bt}", f"{parent}.content.*"]
    return cands


def _declare_block(parent: str, block: dict, decls: dict, drops: list) -> dict:
    hit = _lookup(decls, *_block_key(parent, block))
    if hit is None:
        # no family entry either — the loud undeclared block (never dropped)
        rec = {"render_key": f"undeclared/{parent}.content.{block.get('type')}",
               "undeclared": True, "placement": "conversation-thread", "component": "UnknownEvent",
               "fields": {"block_type": block.get("type")},
               "summary": "UNDECLARED content block — the registry wants an entry"}
        drops.append({"kind": "undeclared", "render_key": rec["render_key"]})
        return rec
    key, d, family = hit
    out = {"render_key": key, "placement": d["placement"], "component": d["component"],
           "fields": _extract(d["field_map"], block)}
    if d.get("update_target"):
        out["update_target"] = d["update_target"]
    if d.get("stream_accumulator"):
        out["stream_accumulator"] = d["stream_accumulator"]
    if d.get("blocks_execution"):
        out["blocks_execution"] = True
    if family:
        out["family_fallback"] = True
        drops.append({"kind": "family-fallback", "render_key": key,
                      "raw_block_type": block.get("type")})
    return out


def declare(ev: dict, *, registry: dict | None = None) -> dict:
    """Map ONE raw event to its declared wire shape:

        {render_key, surface, placement, component, is_terminal, blocks_execution,
         update_target?, stream_accumulator?, fields{…}, blocks[…]?,
         family_fallback?: true, undeclared?: true}

    NEVER returns None and NEVER raises on unknown content — unknown → the loud UnknownEvent
    declaration + a drop record through the hooks. (RegistryInvalid at load is the only
    intended exception path.)"""
    reg = registry or load_registry()
    decls = reg["declarations"]
    drops: list = []
    hit = _lookup(decls, *derive_key(ev))
    if hit is None:
        key = "/".join(str(x) for x in (ev.get("type"), ev.get("subtype")) if x)
        out = {"render_key": f"undeclared/{key or '?'}", "undeclared": True,
               "surface": "stream", "placement": "conversation-thread", "component": "UnknownEvent",
               "is_terminal": False, "blocks_execution": False,
               "fields": {"raw_type": ev.get("type"), "raw_subtype": ev.get("subtype")},
               "summary": "UNDECLARED emit — rendered loud, recorded as a registry gap"}
        _fire_drop({"kind": "undeclared", "render_key": out["render_key"],
                    "raw_type": ev.get("type"), "raw_subtype": ev.get("subtype")})
        return out
    key, d, family = hit
    out = {"render_key": key, "surface": d["surface"], "placement": d["placement"],
           "component": d["component"], "is_terminal": bool(d["is_terminal"]),
           "blocks_execution": bool(d["blocks_execution"]),
           "fields": _extract(d["field_map"], ev)}
    if d.get("update_target"):
        out["update_target"] = d["update_target"]
    if d.get("stream_accumulator"):
        out["stream_accumulator"] = d["stream_accumulator"]
    if family:
        out["family_fallback"] = True
        drops.append({"kind": "family-fallback", "render_key": key,
                      "raw_type": ev.get("type"), "raw_subtype": ev.get("subtype")})
    # content-block sub-dispatch (assistant/user envelopes declare their blocks)
    bf = d.get("blocks_from")
    if bf:
        content = _resolve(bf, ev)
        if isinstance(content, list):
            parent = str(ev.get("type"))
            out["blocks"] = [_declare_block(parent, b, decls, drops)
                             for b in content if isinstance(b, dict)]
    for rec in drops:
        _fire_drop(rec)
    return out


def declared_keys() -> list[str]:
    """Every render_key in the registry (sorted) — the catalogue surface."""
    return sorted(load_registry()["declarations"].keys())
