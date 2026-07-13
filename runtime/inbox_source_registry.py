"""runtime/inbox_source_registry.py — the file-discovered INBOX-SOURCE registry for the NEEDS-ME INBOX (I1).

NAMED DELIBERATELY NOT `inbox_sources.py` (a real trap, found by use): a module named identically to the
top-level `inbox_sources/` DATA DIRECTORY would shadow it — Python's import rule is "a regular module
ALWAYS beats a namespace package, regardless of sys.path order" (PEP 420), and `runtime/` is ALWAYS on
sys.path when `bridge.py` runs (its own script directory) — so `import inbox_sources` from anywhere in
this process would resolve to a same-named loader module before it ever reached the real `inbox_sources/`
package, and every `inbox_sources.<id>:fetch` dotted reference (`resolve_fetch`, below) would 404 with
"'inbox_sources' is not a package". This module owns the REGISTRY MECHANISM; the data directory owns the
name `inbox_sources` alone.

An INBOX-SOURCE is a declared feed the operator's "needs-me" inbox folds into one card list — Tim's
"what needs my hand" surface (decisions awaiting a call, surfaced intents awaiting approve/reject, typed
messages he owes a reply, open requests). Mirrors the ONE registry mechanism `runtime/item_types.py`
mirrors in turn (ProjectionRegistry / RoleRegistry / RelationTypeRegistry / ItemTypeRegistry):
os.listdir -> importlib, fail-loud, id == filename, dict-like, rediscover. A STANDALONE copy (the row
shape is its own — a fetch + a card-shape + a verb list, not a lifecycle), so the validator is its own
(`_build_inbox_source`), same as item_types keeping its own `_build_item_type` beside the mirrored
mechanism.

## Why a FILE-DISCOVERED registry, not a hardcoded fold (the same decision item_types made 2026-06-15)
Adding a new "needs me" feed (SMS replies owed, a new decision class, a new board item-type queue) is
dropping an `inbox_sources/<id>.py` — zero code change to `runtime/needs_me.py`'s fold. The fold is
GENERIC over the registry; only the row (+ its own `fetch`) knows its source's shape.

## The inbox-source schema — each `inbox_sources/<id>.py` declares a module-level `INBOX_SOURCE` dict:
  - id          — required; MUST equal the module name (addressable by file — fail-loud otherwise).
  - label       — required; human label for the source (shown as the card's source badge).
  - fetch       — required; a DOTTED callable reference "pkg.mod:attr" (module-and-colon form) resolving
                  to a ZERO-ARG callable that returns a list[dict] of RAW items for this source. The
                  callable may live anywhere in `runtime` — commonly in the SAME module (the row + its
                  adapter travel together, so adding a source is genuinely one file).
  - card_shape  — required; a dict of FIELD-NAME hints the generic fold uses to lift a raw item into the
                  uniform card shape: {id_field, address_field, title_field, why_field, created_field}.
                  Every hinted field name must be a non-empty string. The raw items THIS source's `fetch`
                  returns must actually carry these fields (that shaping is the fetch's job, not the
                  fold's — see each source module's docstring for its own field derivation).
  - verbs       — required; a non-empty list of {id, label, door} dicts — the action buttons a card of
                  this source offers. `door` may carry `{id}` / `{address}` tokens, substituted per-card
                  by the fold (`runtime/needs_me.py:_substitute_verb`) with THIS card's id/address, so one
                  declared verb list serves every card of the source.
A malformed entry (bad id / id != filename / unknown field / missing required field / malformed
card_shape / malformed verb) FAILS LOUD at discovery — never a silent skip (mirrors item_types).
"""
from __future__ import annotations

import importlib
import importlib.util
import os
from dataclasses import dataclass


INBOX_SOURCE_FIELDS = ("id", "label", "fetch", "card_shape", "verbs")
REQUIRED_FIELDS = ("id", "label", "fetch", "card_shape", "verbs")
CARD_SHAPE_FIELDS = ("id_field", "address_field", "title_field", "why_field", "created_field")
VERB_FIELDS = ("id", "label", "door")


@dataclass
class InboxSource:
    """A discovered inbox-source row — the declared dict (`spec`) verbatim + typed accessors."""
    id: str
    label: str
    fetch: str
    card_shape: dict
    verbs: list
    spec: dict


def _load_module(path: str):
    name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(f"_inboxsrc_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return name, mod


def _build_inbox_source(name: str, decl: dict) -> InboxSource:
    """Validate + build an InboxSource. FAIL LOUD on a malformed entry (mirrors _build_item_type)."""
    if not isinstance(decl, dict):
        raise TypeError(
            f"inbox-source module {name!r}: INBOX_SOURCE must be a dict, got {type(decl).__name__} — fail loud.")
    rid = decl.get("id")
    if not rid or not isinstance(rid, str):
        raise ValueError(f"inbox-source module {name!r}: declares no string `id` — fail loud (never unnamed).")
    if rid != name:
        raise ValueError(
            f"inbox-source module {name!r}: id {rid!r} != module name {name!r} — the id must equal the file "
            f"name (addressable by file). Fail loud.")
    unknown = [k for k in decl if k not in INBOX_SOURCE_FIELDS]
    if unknown:
        raise ValueError(
            f"inbox-source {rid!r}: unknown field(s) {unknown} — the schema is {list(INBOX_SOURCE_FIELDS)}. "
            f"Fail loud.")
    missing = [k for k in REQUIRED_FIELDS if k not in decl]
    if missing:
        raise ValueError(
            f"inbox-source {rid!r}: missing required field(s) {missing} — a source MUST declare "
            f"{list(REQUIRED_FIELDS)}. Fail loud.")
    label = decl["label"]
    if not isinstance(label, str) or not label.strip():
        raise ValueError(f"inbox-source {rid!r}: `label` must be a non-empty string. Got {label!r} — fail loud.")
    fetch = decl["fetch"]
    if not isinstance(fetch, str) or ":" not in fetch or not fetch.strip():
        raise ValueError(
            f"inbox-source {rid!r}: `fetch` must be a dotted 'pkg.mod:attr' string (module path + colon + "
            f"callable name). Got {fetch!r} — fail loud.")
    card_shape = decl["card_shape"]
    if not isinstance(card_shape, dict):
        raise ValueError(f"inbox-source {rid!r}: `card_shape` must be a dict. Got {type(card_shape).__name__} — fail loud.")
    cs_missing = [k for k in CARD_SHAPE_FIELDS if k not in card_shape]
    if cs_missing:
        raise ValueError(
            f"inbox-source {rid!r}: `card_shape` missing {cs_missing} — must declare {list(CARD_SHAPE_FIELDS)}. "
            f"Fail loud.")
    for k in CARD_SHAPE_FIELDS:
        v = card_shape[k]
        if not isinstance(v, str) or not v.strip():
            raise ValueError(f"inbox-source {rid!r}: card_shape[{k!r}] must be a non-empty string. Got {v!r} — fail loud.")
    verbs = decl["verbs"]
    if not isinstance(verbs, list) or not verbs:
        raise ValueError(f"inbox-source {rid!r}: `verbs` must be a non-empty list. Got {verbs!r} — fail loud.")
    for i, v in enumerate(verbs):
        if not isinstance(v, dict):
            raise ValueError(f"inbox-source {rid!r}: verbs[{i}] must be a dict. Got {type(v).__name__} — fail loud.")
        v_missing = [k for k in VERB_FIELDS if k not in v]
        if v_missing:
            raise ValueError(f"inbox-source {rid!r}: verbs[{i}] missing {v_missing} — must declare {list(VERB_FIELDS)}. Fail loud.")
        for k in VERB_FIELDS:
            if not isinstance(v[k], str) or not v[k].strip():
                raise ValueError(f"inbox-source {rid!r}: verbs[{i}][{k!r}] must be a non-empty string. Got {v[k]!r} — fail loud.")
    return InboxSource(id=rid, label=label, fetch=fetch, card_shape=dict(card_shape),
                        verbs=[dict(v) for v in verbs], spec=dict(decl))


def resolve_fetch(fetch: str):
    """Resolve a `fetch` dotted reference ("pkg.mod:attr") to a real, callable object. FAIL LOUD on a
    bad reference, an unimportable module, a missing attribute, or a non-callable attribute — a broken
    `fetch` string must never resolve to a silent no-op."""
    if ":" not in fetch:
        raise ValueError(f"fetch {fetch!r} is not 'pkg.mod:attr' form (no colon) — fail loud.")
    modpath, attr = fetch.split(":", 1)
    try:
        mod = importlib.import_module(modpath)
    except Exception as e:
        raise ImportError(f"fetch {fetch!r}: module {modpath!r} did not import — {type(e).__name__}: {e}") from e
    if not hasattr(mod, attr):
        raise AttributeError(f"fetch {fetch!r}: module {modpath!r} has no attribute {attr!r} — fail loud.")
    fn = getattr(mod, attr)
    if not callable(fn):
        raise TypeError(f"fetch {fetch!r}: {modpath}.{attr} is not callable ({type(fn).__name__}) — fail loud.")
    return fn


class InboxSourceRegistry:
    """The file-discovered INBOX-SOURCE registry — mirrors ItemTypeRegistry (the ONE registry
    mechanism). Dict-like. Adding a needs-me feed = dropping an `inbox_sources/<id>.py` declaring
    `INBOX_SOURCE = {...}` (+ its own `fetch` adapter, in the same file)."""

    def __init__(self):
        self.sources: dict[str, InboxSource] = {}

    def discover(self, dirs: list[str]) -> "InboxSourceRegistry":
        for d in dirs:
            if not os.path.isdir(d):
                continue
            for fn in sorted(os.listdir(d)):
                if not fn.endswith(".py") or fn.startswith("_"):
                    continue
                name, mod = _load_module(os.path.join(d, fn))
                decl = getattr(mod, "INBOX_SOURCE", None)
                if decl is None:
                    continue
                self.register(name, decl)
        return self

    def rediscover(self, dirs: list[str]) -> "InboxSourceRegistry":
        self.sources.clear()
        return self.discover(dirs)

    def register(self, name: str, decl: dict) -> None:
        self.sources[name] = _build_inbox_source(name, decl)

    def as_records(self) -> list[dict]:
        return [dict(self.sources[k].spec) for k in sorted(self.sources)]

    # --- dict-like ---
    def __getitem__(self, rid: str) -> InboxSource:
        return self.sources[rid]

    def __contains__(self, rid: str) -> bool:
        return rid in self.sources

    def __iter__(self):
        return iter(self.sources)

    def __len__(self) -> int:
        return len(self.sources)

    def get(self, rid: str, default=None):
        return self.sources.get(rid, default)
