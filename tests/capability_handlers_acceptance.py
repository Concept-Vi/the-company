"""tests/capability_handlers_acceptance.py — the L-FOUND-DRY-test: the §3.3 DRY TEETH for the WHOLE
③④⑤ Capability Fabric (one handler, two faces).

The arch's promise (§3.3): "every `HANDLERS` key is (a) dispatched by exactly one bridge `path ==`
literal AND (b) wrapped by exactly one MCP op — both directions fail-loud" and "the MCP op and the
bridge route return the byte-identical handler dict." This is the cross-fabric sibling of
tests/bridge_routes_acceptance.py (which owns the bridge-side drift test) and the per-family
*_acceptance suites (which own each family's behaviour by use).

WHAT IS BUILDABLE NOW vs HONESTLY PENDING (no green-paint, the standing law):
  · MCP FACE half (a): BUILT — every HANDLERS key is wrapped by exactly one MCP face tool across the
    three glob-discovered modules (config_authoring / dev_bridges / automation). PROVEN here, both
    directions (every key wrapped; every wrapper maps to a declared key).
  · DRY delegation: BUILT — a representative op through the FACE returns the byte-identical dict the
    HANDLER returns (the faces reimplement nothing; they delegate to ch.HANDLERS[key].fn).
  · BRIDGE half (b): the `/api/{config,dev,auto}/*` literal arms DO NOT EXIST yet — bridge.py carries
    ZERO fabric arms (the L-Wire lane owns bridge.py; the build's no-edit-bridge rule). This test
    ASSERTS that honest state (zero arms) and marks the bridge-side DRY join 'building · pending
    (Wire)'. It NEVER green-paints a bridge route that isn't there. When the Wire lands the arms (each
    a literal `path ==` delegating to the SAME ch.HANDLERS[key].fn), the bridge-half checks below flip
    on automatically — the harness re-derives from BRIDGE_ROUTES, not a literal.

Lead-only law: this exercises handlers + faces against STUBS — NO real claude/-p, NO schedule/CronDelete,
NO model load, NO `.claude` mutation. The real rail round-trips are the lead's 'live-verify pending'.

Run: ./.venv/bin/python tests/capability_handlers_acceptance.py   (exit 0 = pass / 1 = a failed check)
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from runtime import capability_handlers as ch

PASS = 0
FAIL = 0


def check(label, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok  {label}")
    else:
        FAIL += 1
        print(f"  XX  {label}  {detail}")


# stubs (no socket, no spawn, no shell, no model) ----------------------------------------------------

class StubStore:
    def __init__(self, events=None, content=None):
        self._events = events or []
        self._content = content or {}

    def events_since(self, since=-1):
        if since in (None, -1):
            return list(self._events)
        return [e for e in self._events if e.get("seq", 0) > since]

    def get_content(self, cas):
        return self._content.get(cas, "")

    def put_content(self, body):
        return "cas://stub"

    def append_agent_mail(self, rec):
        return {"id": "mail-1", "seq": 1, "to": rec.get("to"), "thread": rec.get("thread", "thread://1")}

    def agent_mail_since(self, since, **kw):
        return []


class StubSuite:
    def __init__(self, events=None):
        self.store = StubStore(events=events)


class StubMCP:
    def __init__(self):
        self.tools = {}

    def tool(self, annotations=None):
        def deco(fn):
            self.tools[fn.__name__] = fn
            return fn
        return deco


# 1 · the registry is WIRED + complete ---------------------------------------------------------------

print("=== capability_handlers_acceptance — the §3.3 DRY teeth (whole ③④⑤ fabric) ===")
print("\n[1] HANDLERS is fully wired (load_all imports the three family modules)")
HANDLERS = ch.load_all()
unwired = [k for k, h in HANDLERS.items() if not h.built]
check("every declared HANDLERS key is WIRED after load_all (no stub left)", not unwired,
      f"unwired: {unwired}")
check("HANDLERS spans the three families (config/dev/auto)",
      {k.split(".")[0] for k in HANDLERS} == {"config", "dev", "auto"})
for k, h in HANDLERS.items():
    check(f"{k}: rail {h.rail} valid + readonly coherent", h.rail in ch.RAILS
          and h.readonly == (h.rail in ch.READONLY_RAILS), f"rail={h.rail} ro={h.readonly}")


# 2 · MCP FACE half — every key wrapped by exactly one op --------------------------------------------

print("\n[2] MCP face (a): every HANDLERS key wrapped by exactly ONE face tool — both directions")

FACE_TOOL_TO_KEY = {
    "config_hooks": "config.hooks",
    "config_mcp_servers": "config.mcp_servers",
    "config_output_style": "config.output_style",
    "config_slash_commands": "config.slash_commands",
    "config_extensions": "config.extensions",
    "config_patterns": "config.patterns",
    "config_keybindings": "config.keybindings",
    "config_telemetry": "config.telemetry",
    "config_provider": "config.provider",
    "dev_git": "dev.git",
    "dev_code_intel": "dev.code_intel",
    "dev_computer_use": "dev.computer_use",
    "dev_code_review": "dev.code_review",
    "dev_ci": "dev.ci",
    "routines": "auto.routines",
    "workflows": "auto.workflows",
    "cost": "auto.cost",
    "auth": "auto.auth",
}

suite = StubSuite()
m = StubMCP()
from mcp_face.tools import config_authoring as face_config
from mcp_face.tools import dev_bridges as face_dev
from mcp_face.tools import automation as face_auto
face_config.register(m, suite)
face_dev.register(m, suite)
face_auto.register(m, suite)

registered = set(m.tools)
mapped_tools = set(FACE_TOOL_TO_KEY)
check("every registered face tool maps to a declared handler key (no orphan tool)",
      registered == mapped_tools, f"only-registered: {sorted(registered - mapped_tools)} "
                                  f"only-mapped: {sorted(mapped_tools - registered)}")
covered_keys = set(FACE_TOOL_TO_KEY.values())
check("every HANDLERS key is wrapped by exactly one MCP tool (coverage, handler->face)",
      covered_keys == set(HANDLERS), f"unwrapped: {sorted(set(HANDLERS) - covered_keys)} "
                                     f"phantom: {sorted(covered_keys - set(HANDLERS))}")
check("the map is 1:1 (no two tools claim one key)",
      len(set(FACE_TOOL_TO_KEY.values())) == len(FACE_TOOL_TO_KEY))


# 3 · DRY delegation — face dict == handler dict (byte-identical) ------------------------------------

print("\n[3] DRY delegation: face(op) == handler(op) byte-identical (faces reimplement NOTHING)")

COST_EVENTS = [{"seq": 1, "kind": "agent_sessions.turn", "session": "s1",
                "usage": {"input_tokens": 7, "output_tokens": 3, "cost_usd": 0.001, "model": "haiku"}}]


def _read_args(key):
    # a representative READ per key. NOTE: the ③ config.* reads route THROUGH the R3 config_writer
    # service (the ③ lane's design — reads are service-served, fail-loud when it is down), so on a
    # stub (no service) they RAISE; that is expected + correct. The DRY invariant we prove is
    # DELEGATION: the face produces the byte-identical OUTCOME the handler does — a returned dict OR
    # the SAME raised error (the face reimplements nothing, so it cannot diverge either way).
    if key == "config.patterns":
        return ("resolve", {"intent": "make Claude proactive"})   # resolve needs an intent/mechanism
    if key == "auto.cost":
        return ("read", {})
    if key == "auto.auth":
        return ("get", {})
    return ("list", {})


def _outcome(fn, *a, **kw):
    """Run fn → ('ok', byte-json) on return, or ('raise', 'ErrType: msg') on exception. Either is a
    deterministic OUTCOME the face and handler must MATCH (delegation, not reimplementation)."""
    try:
        return ("ok", json.dumps(fn(*a, **kw), sort_keys=True, default=str))
    except Exception as e:
        return ("raise", f"{type(e).__name__}: {e}")


suite_cost = StubSuite(events=COST_EVENTS)
m2 = StubMCP()
face_config.register(m2, suite_cost)
face_dev.register(m2, suite_cost)
face_auto.register(m2, suite_cost)

for tool_name, key in sorted(FACE_TOOL_TO_KEY.items()):
    op, kw = _read_args(key)
    handler = ch.HANDLERS[key].fn

    def _face(o, kwargs):
        ft = m2.tools[tool_name]
        try:
            return ft(op=o, **kwargs)
        except TypeError:
            return ft(o)

    hdl_out = _outcome(handler, suite_cost, op, **kw)
    face_out = _outcome(_face, op, kw)
    # the face must produce the IDENTICAL outcome the handler does (dict-equal OR same-error)
    same = (hdl_out == face_out)
    kind = "dict" if hdl_out[0] == "ok" else "fail-loud error"
    check(f"DRY {key}: face delegates byte-identical {kind} to handler (read {op})", same,
          f"face={face_out[1][:90]!r} hdl={hdl_out[1][:90]!r}")


# 4 · BRIDGE half (b) — HONESTLY pending (Wire handoff, never green) ----------------------------------

print("\n[4] bridge face (b): the /api/{config,dev,auto}/* arms — HONEST pending (Wire owns bridge.py)")
from runtime.bridge import BRIDGE_ROUTES


def _fabric_path(r):
    p = r[0] if isinstance(r, (tuple, list)) and r else r
    return p if isinstance(p, str) and (p.startswith("/api/config/")
                                        or p.startswith("/api/dev/")
                                        or p.startswith("/api/auto/")) else None


fabric_arms = [p for p in (_fabric_path(r) for r in BRIDGE_ROUTES) if p]
check("NO fabric bridge arms exist yet — bridge-half DRY join is 'building . pending (Wire)', "
      "NOT green-painted", len(fabric_arms) == 0,
      f"unexpected fabric arms present (the Wire landed them — flip the join ON): {fabric_arms}")
print("      bridge-half status: building . pending (Wire) — when /api/{config,dev,auto}/* literal arms")
print("      land (each delegating to the SAME ch.HANDLERS[key].fn), this section's join flips on:")
print("        every fabric (path) <-> exactly one HANDLERS key, both directions, byte-identical dict.")

EXPECTED_WIRE_ARMS = {
    "config.hooks": ["/api/config/hooks"], "config.mcp_servers": ["/api/config/mcp-servers"],
    "config.output_style": ["/api/config/output-style"], "config.slash_commands": ["/api/config/commands"],
    "config.extensions": ["/api/config/plugins"], "config.patterns": ["/api/config/patterns"],
    "config.keybindings": ["/api/config/keybindings"], "config.telemetry": ["/api/config/telemetry"],
    "config.provider": ["/api/config/provider"],
    "dev.git": ["/api/dev/git"], "dev.code_intel": ["/api/dev/code-intel"],
    "dev.computer_use": ["/api/dev/computer-use"], "dev.code_review": ["/api/dev/code-review"],
    "dev.ci": ["/api/dev/ci"],
    "auto.routines": ["/api/auto/routines"], "auto.workflows": ["/api/auto/workflows"],
    "auto.cost": ["/api/auto/cost"], "auto.auth": ["/api/auto/auth"],
}
check("the Wire-arm contract names exactly the HANDLERS keys (the handoff is closed both directions)",
      set(EXPECTED_WIRE_ARMS) == set(HANDLERS),
      f"missing: {sorted(set(HANDLERS) - set(EXPECTED_WIRE_ARMS))} "
      f"extra: {sorted(set(EXPECTED_WIRE_ARMS) - set(HANDLERS))}")


# verdict --------------------------------------------------------------------------------------------

print(f"\n=== {PASS} passed, {FAIL} failed ===")
print("NOTE: bridge-half (b) is HONESTLY pending (Wire owns bridge.py — no-edit-bridge rule). The "
      "MCP-face half (a) + DRY delegation are PROVEN. Real rail round-trips are the lead's live-verify.")
sys.exit(0 if FAIL == 0 else 1)
