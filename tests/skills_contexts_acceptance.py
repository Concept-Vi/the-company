"""tests/skills_contexts_acceptance.py — skills + contexts as addressable registries (C 3b).

Tim's scope expansion (2026-06-08): "skills/contexts are registries like anything else
(registry-is-truth)." This is the FIRST real extension of the C 3/4 `resolve_address` seam — the
`skill://`/`context://` schemes that USED to fail loud there now have resolvers. This suite proves,
BY MECHANISM (no live model needed for the structural parts; the role-reads-a-skill end-to-end is
LIVE-or-MOCKED, mirroring run_items_acceptance), that:

  1. SCHEMES additive — `skill` + `context` are in `contracts/address.py:SCHEMES` (mirrors the
     ui://code:// precedent; no record-shape / schema_ver change).
  2. Both registries DISCOVER like roles — `SkillRegistry`/`ContextRegistry` mirror `RoleRegistry`:
     file-discovered from `skills/`+`contexts/`, dict-like, fail-loud on a malformed entry, a
     non-entry/`_`-file skipped; dropping a 2nd file registers it (the dynamic proof); removing it
     un-registers on rediscover.
  3. resolve_address resolves `skill://`+`context://` — the seed skill/context resolve to their REAL
     declared content; an UNKNOWN id RAISES fail-loud (registry-is-truth, never fabricate); the still-
     unbuilt schemes (blob/vec/ui/code) STILL RAISE (the seam holds for them).
  4. END-TO-END (the intent): a fireable role fanned over a `skill://<id>` unit reads the skill's REAL
     instructions as its primary input — "a role's input can be any skill … set by address," realised.

LAWS proven: no-hardcoding (the ids live in their dirs — discovered, never a literal list) ·
reuse-don't-parallel (the registries mirror RoleRegistry; resolve_address dispatches to them, one seam) ·
fail-loud (unknown id / malformed entry RAISES) · the floor (a skill/context read is a READ — the
registry method is `read`, not `resolve`; the C9.2 source-invariant stays intact) · drift (the seeds are
reflected in skills/contexts AGENTS.md).
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from contracts.address import SCHEMES, scheme                               # noqa: E402
from store.fs_store import FsStore                                          # noqa: E402
from runtime import cognition                                              # noqa: E402
from runtime.cognition import resolve_address, run_items, ItemsResult       # noqa: E402
from runtime.skills import SkillRegistry, ContextRegistry, Entry            # noqa: E402
from runtime.roles import RoleRegistry                                      # noqa: E402

SKILLS = os.path.join(ROOT, "skills")
CONTEXTS = os.path.join(ROOT, "contexts")
ROLES = os.path.join(ROOT, "roles")
SEED_SKILL = "summarize"
SEED_CONTEXT = "company_overview"
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


# =================================================================================================
# 1 · SCHEMES additive — skill + context are registered schemes (mirrors ui://code:// — additive)
# =================================================================================================
check("contracts.address.SCHEMES contains 'skill' (additive — the C 3b scheme)", "skill" in SCHEMES)
check("contracts.address.SCHEMES contains 'context' (additive)", "context" in SCHEMES)
check("the additive precedent holds — run/cas/blob/vec/ui/code are STILL in SCHEMES (nothing removed)",
      all(s in SCHEMES for s in ("run", "cas", "blob", "vec", "ui", "code")))
check("scheme('skill://summarize') == 'skill' (a registered scheme, not a bare name)",
      scheme(f"skill://{SEED_SKILL}") == "skill")
check("scheme('context://company_overview') == 'context'",
      scheme(f"context://{SEED_CONTEXT}") == "context")


# =================================================================================================
# 2 · the two registries DISCOVER like roles (mirror RoleRegistry — file-discovered, fail-loud)
# =================================================================================================
sk = SkillRegistry().discover([SKILLS])
cx = ContextRegistry().discover([CONTEXTS])
check("SkillRegistry().discover(['skills']) finds the seed skill (file-discovered, no literal list)",
      SEED_SKILL in sk)
check("ContextRegistry().discover(['contexts']) finds the seed context",
      SEED_CONTEXT in cx)
# the registries mirror RoleRegistry's shape (reuse-don't-parallel — the ONE registry pattern)
check("the registries mirror RoleRegistry (discover/rediscover/register/read present)",
      all(hasattr(sk, m) for m in ("discover", "rediscover", "register", "read")))
check("the registries are dict-like (reg[id] -> Entry, id in reg, .get) — drops in like RoleRegistry",
      isinstance(sk[SEED_SKILL], Entry) and sk.get("nope") is None and "nope" not in sk)
check("a discovered entry carries id + content + its kind (the registry row)",
      sk[SEED_SKILL].id == SEED_SKILL and sk[SEED_SKILL].kind == "skill"
      and cx[SEED_CONTEXT].kind == "context")

# the DYNAMIC proof — dropping a 2nd file registers it WITHOUT a code change (registry-is-truth).
probe = os.path.join(SKILLS, "sc_probe.py")
try:
    open(probe, "w").write('SKILL = {"id": "sc_probe", "content": "probe instructions — added by drop-in"}\n')
    sk2 = SkillRegistry().discover([SKILLS])
    check("dropping a 2nd skills/<id>.py FILE → it is discovered (no code change — the dynamic proof)",
          "sc_probe" in sk2 and SEED_SKILL in sk2)
    check("the dropped skill RESOLVES to its declared content (read())",
          sk2.read("sc_probe") == "probe instructions — added by drop-in")
finally:
    os.remove(probe)
skr = SkillRegistry().rediscover([SKILLS])
check("removing the file → it un-registers on rediscover (mirrors RoleRegistry.rediscover)",
      "sc_probe" not in skr and SEED_SKILL in skr)

# fail-loud adversarial — a malformed entry RAISES at discovery (not silently skipped).
for fname, body, why in [
    ("sc_bad_id.py", 'SKILL = {"id": "NOTMYNAME", "content": "x"}\n', "id != filename"),
    ("sc_bad_empty.py", 'SKILL = {"id": "sc_bad_empty", "content": ""}\n', "empty content"),
    ("sc_bad_field.py", 'SKILL = {"id": "sc_bad_field", "content": "x", "bogus": 1}\n', "unknown field"),
]:
    p = os.path.join(SKILLS, fname)
    try:
        open(p, "w").write(body)
        raised = False
        try:
            SkillRegistry().discover([SKILLS])
        except (ValueError, TypeError):
            raised = True
        check(f"a MALFORMED skill ({why}) FAILS LOUD at discovery (never a silent skip)", raised)
    finally:
        os.remove(p)
# a non-entry / _-prefixed file is SKIPPED (not raised) — mirrors RoleRegistry's non-role skip.
nr = os.path.join(SKILLS, "_sc_notentry.py")
try:
    open(nr, "w").write("X = 1\n")
    sknr = SkillRegistry().discover([SKILLS])
    check("a non-entry / _-prefixed file is SKIPPED (not registered, not raised)",
          "sc_notentry" not in sknr and "_sc_notentry" not in sknr and SEED_SKILL in sknr)
finally:
    os.remove(nr)


# =================================================================================================
# 3 · resolve_address resolves skill:// + context:// — the seam's FIRST real extension
# =================================================================================================
store = FsStore(os.path.join(tempfile.mkdtemp(prefix="sc-resolve-"), "store"))

# the seed skill/context resolve to their REAL declared content (no longer the fail-loud RAISE).
skill_content = resolve_address(store, f"skill://{SEED_SKILL}")
ctx_content = resolve_address(store, f"context://{SEED_CONTEXT}")
check("resolve_address('skill://summarize') resolves to the seed skill's REAL content (no longer raises)",
      isinstance(skill_content, str) and "summarizing" in skill_content.lower())
check("resolve_address('context://company_overview') resolves to the seed context's REAL content",
      isinstance(ctx_content, str) and "company" in ctx_content.lower())
# reuse proof: resolve_address dispatches to the SAME registry read (one seam, not a parallel resolver).
check("the skill:// path dispatches to SkillRegistry.read (identical value — one seam, no parallel resolver)",
      skill_content == SkillRegistry().discover([SKILLS]).read(SEED_SKILL))
check("the context:// path dispatches to ContextRegistry.read (identical value)",
      ctx_content == ContextRegistry().discover([CONTEXTS]).read(SEED_CONTEXT))

# an UNKNOWN skill/context id RAISES fail-loud (registry-is-truth — NEVER fabricate a missing entry).
unknown_skill = False
try:
    resolve_address(store, "skill://no-such-skill")
except ValueError as e:
    unknown_skill = "unknown skill" in str(e).lower() and "registry-is-truth" in str(e).lower()
check("resolve_address('skill://no-such-skill') RAISES fail-loud (registry-is-truth, never fabricate)",
      unknown_skill)
unknown_ctx = False
try:
    resolve_address(store, "context://no-such-context")
except ValueError as e:
    unknown_ctx = "unknown context" in str(e).lower() and "registry-is-truth" in str(e).lower()
check("resolve_address('context://no-such-context') RAISES fail-loud (registry-is-truth)",
      unknown_ctx)

# the still-UNBUILT schemes STILL RAISE (the seam holds for them — only skill+context graduated in C 3b).
for sch in ("blob://b2:abc", "vec://run://x#emb=m", "ui://panel/p", "code://suite/foo"):
    raised = False
    try:
        resolve_address(store, sch)
    except ValueError as e:
        raised = "not content-resolvable yet" in str(e)
    check(f"resolve_address({sch.split('://')[0]}://…) STILL RAISES (registered scheme, no resolver — seam holds)",
          raised)


# =================================================================================================
# 4 · END-TO-END (the intent): a role fanned over a skill:// unit reads the skill's instructions
# =================================================================================================
reg = RoleRegistry().discover([ROLES])
focus = reg["focus"]                          # a fireable "utterance"-only role (the default input path)
check("the fanned role (focus) is fireable (run_items maps a fireable role over the addressed units)",
      focus.can_fire)

store_e2e = FsStore(os.path.join(tempfile.mkdtemp(prefix="sc-e2e-"), "store"))
E2E_TURN = "t-skill-e2e"
# the UNIT is a skill:// ADDRESS — run_items' unit classifier ("://" in unit) routes it through
# resolve_address → the skill's content becomes the role's PRIMARY input. The intent, end-to-end.
UNITS = [f"skill://{SEED_SKILL}"]


def _try_live():
    from fabric import transport, client
    t = transport.openai_transport(base_url=cognition.RESIDENT_BASE_URL, timeout=8)
    client.complete(t, [{"role": "user", "content": "ok"}], model=cognition.RESIDENT_MODEL,
                    json=False, max_tokens=1, temperature=0.0)


live = True
try:
    _try_live()
except Exception as e:
    live = False
    print(f"  ..  resident 4B not up ({type(e).__name__}) — proving the end-to-end on a MOCKED transport "
          f"(the resolve→compose path is REAL; only the model call is stubbed)")

if live:
    res = run_items(focus, UNITS, store_e2e, turn_id=E2E_TURN)
    # the seed skill's content was resolved + reached the role; the live output landed at the per-unit addr.
    skilled = resolve_address(store_e2e, f"run://{E2E_TURN}/{focus.id}/0", turn_id=E2E_TURN)
    check("LIVE: run_items over a skill:// unit fired the role + wrote its output (the skill reached the model)",
          isinstance(skilled, dict))
else:
    from fabric import client as _client
    seen_users = []
    orig = _client.complete

    class _Validated:
        def __init__(self, d): self._d = d
        def model_dump(self): return dict(self._d)

    def _mock(t, msgs, *, model, schema=None, json=False, temperature=0.0, max_tokens=256, **kw):
        seen_users.append(msgs[-1]["content"])         # capture the role's input (the skill's content)
        return _Validated({"intent": "summarize the content", "which_roles": []})

    cognition.client.complete = _mock
    try:
        res = run_items(focus, UNITS, store_e2e, turn_id=E2E_TURN)
    finally:
        cognition.client.complete = orig
    # THE INTENT, PROVEN: the skill's REAL instructions reached the role as its primary input.
    check("MOCK: exactly 1 unit (the skill:// address) fired the role", len(seen_users) == 1)
    check("MOCK: the SEED SKILL's REAL instructions reached the role as its input ('summarizing' text)",
          "summarizing" in seen_users[0].lower() and "load-bearing" in seen_users[0].lower())

check("run_items over a skill:// unit returns an ItemsResult (1 role × 1 addressed unit)",
      isinstance(res, ItemsResult) and res.role_id == focus.id and len(res.runs) == 1)
check("the role's output for the skill:// unit landed at run://<turn>/<role>/0 (the addressed round-trip)",
      res.addresses[0] == f"run://{E2E_TURN}/{focus.id}/0"
      and isinstance(res.resolved.get(0), dict))


# =================================================================================================
# 5 · drift — the seeds are reflected in their AGENTS.md drift homes (mirrors roles_acceptance)
# =================================================================================================
skills_md = open(os.path.join(SKILLS, "AGENTS.md")).read()
contexts_md = open(os.path.join(CONTEXTS, "AGENTS.md")).read()
missing_sk = [sid for sid in sk if sid not in skills_md]
missing_cx = [cid for cid in cx if cid not in contexts_md]
check(f"every discovered skill is reflected in skills/AGENTS.md drift home (drift: {missing_sk})", not missing_sk)
check(f"every discovered context is reflected in contexts/AGENTS.md drift home (drift: {missing_cx})", not missing_cx)
check("the skill registry is NAMED in its drift home", "SkillRegistry" in skills_md)
check("the context registry is NAMED in its drift home", "ContextRegistry" in contexts_md)


print(f"\nALL {PASS} CHECKS PASS — SCHEMES additive (skill+context) · both registries discover like roles "
      f"(file-discovered, fail-loud, dynamic drop-in) · resolve_address resolves skill://+context:// + "
      f"unknown-id fail-loud + blob/vec/ui/code still-raise · role-reads-a-skill end-to-end · drift homes")
