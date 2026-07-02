"""contracts/scope_grammar.py — the ONE scope-grammar parser (④ L2-IDENTITY, organ-studies/TENANCY.md §3.3).

The missing unifier: three grammars ran unparsed —
  · A (cloud):   read/write/execute/admin/approve · write:leads · create:intent · deploy:langgraph
  · C (client):  company:design:write
  · B (engine):  permission='use'
This module reads the VERB registry (scope_grammar/*.py — vocabulary=files, THE-CONTAINER law 3) and
normalizes ANY scope token into {verb, domain, resource, object, raw}. The verb is the ONE segment that
is a REGISTERED verb; segments before it are domain/resource, segments after are the object qualifier.
So `read`→verb=read; `write:leads`→verb=write,object=leads; `create:intent`→verb=create,object=intent;
`company:design:write`→verb=write,domain=company,resource=design. A token whose verb is not registered
FAILS LOUD (registry-is-truth, never guess). Exactly-one-verb is required (0 or >1 → raise).

REUSE: the discovery mirrors runtime/mark_types.py (the ONE registry mechanism). No parallel loader.
"""
from __future__ import annotations

import importlib.util
import os

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCOPE_GRAMMAR_DIR = os.path.join(_REPO, "scope_grammar")

_VERBS_CACHE: dict[str, dict] | None = None


def _load_verbs(*, grammar_dir: str | None = None, force: bool = False) -> dict[str, dict]:
    """Discover the registered verbs from scope_grammar/<verb>.py (each declares SCOPE_VERB). Cached.
    FAIL LOUD on a malformed row or an id/file-stem mismatch (mirrors _build_mark_type)."""
    global _VERBS_CACHE
    d = grammar_dir or SCOPE_GRAMMAR_DIR
    if _VERBS_CACHE is not None and not force and grammar_dir is None:
        return _VERBS_CACHE
    verbs: dict[str, dict] = {}
    if not os.path.isdir(d):
        raise FileNotFoundError(
            f"scope_grammar: registry dir {d!r} missing — expected scope_grammar/ (vocabulary=files, "
            f"THE-CONTAINER law 3); previously three unparsed grammars; fix: restore scope_grammar/*.py.")
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".py") or fn.startswith("_"):
            continue
        stem = fn[:-3]
        spec = importlib.util.spec_from_file_location(f"_sg_{stem}", os.path.join(d, fn))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        decl = getattr(mod, "SCOPE_VERB", None)
        if not isinstance(decl, dict):
            raise TypeError(f"scope_grammar/{fn}: SCOPE_VERB must be a dict — fail loud, never a silent row.")
        v = decl.get("verb")
        if v != stem:
            raise ValueError(f"scope_grammar/{fn}: verb {v!r} != file stem {stem!r} — the verb must equal "
                             f"the file name (addressable by file). Fail loud.")
        verbs[v] = dict(decl)
    if not verbs:
        raise ValueError(f"scope_grammar: no verbs discovered in {d!r} — fail loud (an empty grammar "
                         f"authorizes nothing legibly).")
    if grammar_dir is None:
        _VERBS_CACHE = verbs
    return verbs


def registered_verbs(*, grammar_dir: str | None = None) -> list[str]:
    """The verb vocabulary, sorted — read from the registry (never a code literal)."""
    return sorted(_load_verbs(grammar_dir=grammar_dir))


def parse_scope(token: str, *, grammar_dir: str | None = None) -> dict:
    """Normalize a scope token into {verb, domain, resource, object, raw}. FAIL LOUD on 0 or >1
    registered verbs (an unparseable/ghost scope is never silently allowed)."""
    if not isinstance(token, str) or not token.strip():
        raise ValueError("parse_scope: empty scope token — fail loud.")
    raw = token.strip()
    verbs = _load_verbs(grammar_dir=grammar_dir)
    segs = raw.split(":")
    hits = [(i, s) for i, s in enumerate(segs) if s in verbs]
    if len(hits) != 1:
        raise ValueError(
            f"parse_scope: {raw!r} has {len(hits)} registered verb(s) (want exactly 1) — the verb "
            f"vocabulary is {sorted(verbs)} (scope_grammar/). A token with 0 verbs is a ghost; >1 is "
            f"ambiguous. Fail loud, never guess.")
    idx, verb = hits[0]
    before, after = segs[:idx], segs[idx + 1:]
    # before → domain/resource (last two positions); after → object qualifier (joined).
    domain = before[0] if len(before) >= 2 else None
    resource = before[-1] if before else None
    obj = ":".join(after) if after else None
    return {"verb": verb, "domain": domain, "resource": resource, "object": obj, "raw": raw}


def normalize(token: str, *, grammar_dir: str | None = None) -> str:
    """The canonical stored form: verb[:object] (domain/resource fold into the address, not the scope).
    `company:design:write`→'write'; `write:leads`→'write:leads'; `read`→'read'. Idempotent."""
    p = parse_scope(token, grammar_dir=grammar_dir)
    return f"{p['verb']}:{p['object']}" if p["object"] else p["verb"]
