"""tests/supervisor_routes_acceptance.py — the contract corpus's MACHINE INVENTORY teeth (F1.5).

CONTRACT-FORMAT.md imposes code-side obligations so the corpus's reality checks (V21/V22) have
real registries to read (§9 — adopted into the contract lane's scope, scaffolding-not-spec law):

  §9.3  the supervisor ships SUPERVISOR_ROUTES before any supervisor binding is contracted —
        a (method, path) STRUCTURED registry (the §9.1 bridge shape from birth). This test is
        the bidirectional drift teeth (the bridge_routes_acceptance pattern): a path dispatched
        in do_GET/do_POST but absent from the registry fails loud, and a registry row that
        nothing dispatches fails loud (a phantom binding advertised to the contract).
  §9.2  every consolidated MCP tool module exports a closed OPS constant —
        mcp_face/tools/sessions.py exports OPS, and the tool's own dispatch handles exactly
        that set (no phantom op, no undispatched op).

Run: ./.venv/bin/python tests/supervisor_routes_acceptance.py    (exit 0 = pass)
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

PASS = 0
FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name}  {detail}")


# ── §9.3 — SUPERVISOR_ROUTES ↔ the dispatch literals, both directions ─────────────────────────
from runtime import session_supervisor as sup

declared = set(sup.SUPERVISOR_ROUTES)
src = open(os.path.join(ROOT, "runtime", "session_supervisor.py"), encoding="utf-8").read()

check("SUPERVISOR_ROUTES is a non-empty tuple of (method, path) pairs",
      isinstance(sup.SUPERVISOR_ROUTES, tuple) and len(declared) > 0
      and all(isinstance(r, tuple) and len(r) == 2 and r[0] in ("GET", "POST")
              and r[1].startswith("/") for r in declared))
check("SUPERVISOR_ROUTES has no duplicates", len(declared) == len(sup.SUPERVISOR_ROUTES))

get_body = src[src.index("def do_GET"):src.index("def _watch")]
post_body = src[src.index("def do_POST"):src.index("def main")]
dispatched = set()
for m in re.finditer(r'u\.path\s*==\s*"(/[^"]*)"', get_body):
    dispatched.add(("GET", m.group(1)))
for m in re.finditer(r'u\.path\s*==\s*"(/[^"]*)"', post_body):
    dispatched.add(("POST", m.group(1)))
for m in re.finditer(r'u\.path\s+in\s+\(([^)]*)\)', post_body):
    for p in re.findall(r'"(/[^"]*)"', m.group(1)):
        dispatched.add(("POST", p))

check("every dispatched route is DECLARED in SUPERVISOR_ROUTES (nothing invisible to the contract)",
      dispatched <= declared, f"undeclared: {sorted(dispatched - declared)}")
check("every declared route is DISPATCHED (no phantom binding advertised)",
      declared <= dispatched, f"phantom: {sorted(declared - dispatched)}")

# ── §9.2 — the consolidated tool's exported closed OPS set ────────────────────────────────────
sys.path.insert(0, os.path.join(ROOT, "mcp_face"))
import importlib
sessions_mod = importlib.import_module("mcp_face.tools.sessions")

ops = getattr(sessions_mod, "OPS", None)
check("mcp_face/tools/sessions.py EXPORTS a closed OPS constant (§9.2 — extract_reality's read)",
      isinstance(ops, tuple) and len(ops) > 0 and all(isinstance(o, str) for o in ops))
check("OPS has no duplicates", ops is not None and len(set(ops)) == len(ops))

tool_src = open(os.path.join(ROOT, "mcp_face", "tools", "sessions.py"), encoding="utf-8").read()
handled = set(re.findall(r'if op == "([a-z]+)"', tool_src))
check("every exported op is dispatched in the tool body (no phantom op)",
      ops is not None and set(ops) == handled,
      f"OPS={sorted(ops or [])} vs dispatched={sorted(handled)}")
literal = re.search(r'op:\s*Literal\[([^\]]*)\]', tool_src)
sig_ops = set(re.findall(r'"([a-z]+)"', literal.group(1))) if literal else set()
check("the tool signature's Literal[...] equals OPS (one vocabulary, no drift)",
      ops is not None and sig_ops == set(ops),
      f"signature={sorted(sig_ops)} vs OPS={sorted(ops or [])}")

# ── L-FOUND-R1prime — the `bridge-session` spawn PROFILE (Capability Fabric ③④⑤) ────────────────
# Unit-tests the PURE cmd-builders + the consent gate WITHOUT spawning a real claude (lead-only law:
# this lane never fires a real turn — the live wider-session round-trip is the build lead's,
# 'live-verify pending'). Every flag asserted here is Atlas-grounded (see the profile block's
# docstring in session_supervisor.py), never invented.

S = sup.SessionSupervisor  # the class — _build_* are static/class methods, no instance/store needed

# (a) the wider allowlist IS present (the profile's whole purpose) — and it is NOT the floor.
_bin = "/usr/bin/claude"
cmd_default = S._build_bridge_session_cmd(claude_bin=_bin)
ai = cmd_default.index("--allowedTools")
allow = cmd_default[ai + 1]
check("bridge-session allowlist is the WIDER profile set (Bash/Edit/Read/web + mcp__company), NOT the floor",
      "Bash" in allow and "Edit" in allow and "WebFetch" in allow and "mcp__company" in allow
      and allow != "mcp__company",
      f"allow={allow!r}")
check("bridge-session allowlist is a single comma-separated --allowedTools value (Atlas shape)",
      cmd_default.count("--allowedTools") == 1 and "," in allow)

# (b) the transport head is PRESERVED byte-identically (the T2 injection contract): --input-format
#     stream-json + stream-json output + -p + strict-mcp-config all still present.
for flag in ("-p", "--input-format", "stream-json", "--strict-mcp-config", "--mcp-config"):
    check(f"bridge-session preserves transport flag {flag!r} (held-open injection contract)",
          flag in cmd_default, f"cmd={cmd_default}")
check("bridge-session permission posture defaults to acceptEdits (in-session writes — NOT plan)",
      cmd_default[cmd_default.index("--permission-mode") + 1] == sup.BRIDGE_SESSION_PERMISSION
      and sup.BRIDGE_SESSION_PERMISSION != "plan")

# (c) the floor spawn is UNCHANGED by this lane: _build_spawn_cmd with no params is still mcp__company-only.
floor = S._build_spawn_cmd(claude_bin=_bin, resume=None, fork=False)
check("the FLOOR spawn cmd is untouched — still --allowedTools mcp__company only (no leak from R1-prime)",
      floor[floor.index("--allowedTools") + 1] == "mcp__company")

# (d) capability NARROWING: asking for only `git` grants Bash (+mcp__company), not the whole set.
cmd_git = S._build_bridge_session_cmd(claude_bin=_bin, capabilities=["git"])
git_allow = cmd_git[cmd_git.index("--allowedTools") + 1]
check("capabilities=['git'] grants Bash (native Bash-tool git) + mcp__company, narrowed (no WebFetch)",
      "Bash" in git_allow and "mcp__company" in git_allow and "WebFetch" not in git_allow,
      f"git_allow={git_allow!r}")
cmd_lsp = S._build_bridge_session_cmd(claude_bin=_bin, capabilities="lsp")
lsp_allow = cmd_lsp[cmd_lsp.index("--allowedTools") + 1]
check("capabilities='lsp' grants the Read/Edit family (the LSP tool's permission family, Atlas)",
      "Read" in lsp_allow and "Edit" in lsp_allow)

# (e) HOST/RAIL BOUNDARY refusals — computer/browser can NEVER bind on a -p/Linux rail. Refused LOUD,
#     never an allowlist entry that silently never binds (§5.4 honesty). As a capability AND as a raw tool.
for boundary in ("computer", "browser"):
    raised = False
    try:
        S._build_bridge_session_cmd(claude_bin=_bin, capabilities=[boundary])
    except sup.TeachingRefusal:
        raised = True
    check(f"capabilities=['{boundary}'] is REFUSED LOUD (macOS/interactive-only host boundary, never on -p)",
          raised)
    raised2 = False
    try:
        S._build_bridge_session_cmd(claude_bin=_bin, extra_tools=[boundary])
    except sup.TeachingRefusal:
        raised2 = True
    check(f"extra_tools=['{boundary}'] is also refused (the boundary holds however it is asked for)",
          raised2)
# the resolver surfaces the WHY (requires_tool_grant honesty), not a bare denial
_tools, _refusals = S._resolve_bridge_tools("computer", None)
check("computer refusal carries the teaching reason (macOS + non-interactive -p), never opaque",
      any("macOS" in r and "-p" in r for r in _refusals), f"refusals={_refusals}")

# (f) an UNKNOWN capability is refused-loud too (no silent drop).
raised_unknown = False
try:
    S._build_bridge_session_cmd(claude_bin=_bin, capabilities=["telepathy"])
except sup.TeachingRefusal:
    raised_unknown = True
check("an unknown capability is refused-loud (no silent drop — names the grantable + boundary sets)",
      raised_unknown)

# (g) THE CONSENT GATE (sole-operator: consent-not-lockdown). spawn_bridge_session WITHOUT
#     operator_consent refuses LOUD before ANY subprocess work — proven without spawning by asserting
#     the refusal fires (no Popen reached because the consent check is the first statement).
class _FakeStore:
    pass
_sup_inst = S.__new__(S)            # no __init__ → no real store/threads; we only exercise the gate
import threading as _th
_sup_inst.lock = _th.RLock()
consent_refused = False
try:
    _sup_inst.spawn_bridge_session(operator_consent=False)
except sup.TeachingRefusal as e:
    consent_refused = "consent-gated" in str(e)
check("spawn_bridge_session WITHOUT operator_consent is REFUSED LOUD (consent beat, not a lockout)",
      consent_refused)

# (h) the consent refusal maps to HTTP 403 in the dispatcher (forbidden-until-consent), distinct from
#     cap=429 / state=409 — proven by the literal mapping in the source (no live server needed).
sup_src = open(os.path.join(ROOT, "runtime", "session_supervisor.py"), encoding="utf-8").read()
check("the consent refusal maps to HTTP 403 in do_POST (forbidden-until-consent, not 409/429)",
      '403 if "consent-gated"' in sup_src)
check("the /bridge-session arm returns liveness:stream with NO typed return_shape (arch doc correction)",
      '"liveness": "stream"' in sup_src and "no typed return_shape" in sup_src)

# (i) the spawn EVENT records the security decision (profile + consent + allowlist) — Introspective-
#     Data-Building / §5.6 (every R1-prime act writes who+consent+args for the gap-pressure signal).
check("the bridge-session spawn event stamps profile + operator_consent + allowed_tools (run-record)",
      'profile="bridge-session", operator_consent=True' in sup_src and "allowed_tools=cmd[i + 1]" in sup_src)

print(f"\n{'PASS' if FAIL == 0 else 'FAIL'} — {PASS} ok, {FAIL} failed")
sys.exit(0 if FAIL == 0 else 1)
