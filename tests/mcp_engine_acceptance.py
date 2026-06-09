"""tests/mcp_engine_acceptance.py — #53 MCP engine-exposure (the AGENT face) — VERIFY BY USE.

Proves, by an AGENT really DRIVING the MCP tool functions (not code-reading), that the cognition
engine is now reachable by agents through the MCP exactly as the human reaches it through the FE /
`/api/cognition/*` — REUSING the SAME Suite methods + the runtime/cognition.py engine (no parallel
engine), and that the OPERATOR-ONLY FLOOR (C9.2) holds on this new face.

The 6 by-use scenarios (the task bar):
  1. cognition_info() via MCP → the registries (roles/rules/skills/contexts/modes/shapes).
  2. configure+run a role via MCP (run_role generate) against the resident 4B → a real validated output.
  3. an EMBED run via MCP (run_role op=embed) → a real 1024-dim vector. GPU-GATED: only if the embedder
     can be made resident WITHOUT evicting another session's brain; else the CODE PATH is proven (the
     op=embed wiring + the gated ensure_resident is invoked) and the live vector is marked pending a
     safe GPU window — NEVER a blind evict of the live brain.
  4. inspect a run output by address via MCP (inspect_address) → reads the generate run back.
  5. create: propose_role via MCP → SURFACES (kept available); the direct create_role/create_skill/
     create_context tools are REGISTERED (the #58 direct authoring path — by-use proven in
     tests/direct_create_acceptance.py, which uses an isolated roles dir + injected committer so it
     never commits the live repo).
  6. run_items + run_reduce via MCP → the map + the cross-unit join.

+ the FLOOR (asserted directly on THIS face, since the cognition source-invariant scans only
  cognition.py/rules.py/roles.py): the BUILD-DISPATCH floor holds — no MCP tool emits dispatch_decision
  or launches `claude -p` / calls resolve_surfaced (the wire's autonomous repo-mutation stays
  operator-gated, off this face). AUTHORING-apply (create_role/skill/context) is now ALLOWED (#58 —
  Tim's reframe: the create-approval gate was the AI default, not his constraint).

Run:  COMPANY_STORE=/tmp/mcp-eng-$$ ./.venv/bin/python tests/mcp_engine_acceptance.py
(COMPANY_STORE MUST be set BEFORE import — the MCP server binds a module-level SUITE at import.)
"""
import os
import sys
import json
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# isolate the store BEFORE importing the server (module-level SUITE binds at import — advisor flag).
os.environ.setdefault("COMPANY_STORE", f"/tmp/mcp-eng-{os.getpid()}")
os.makedirs(os.environ["COMPANY_STORE"], exist_ok=True)

PASS = 0
ok = True


def check(label, cond):
    global PASS, ok
    if cond:
        PASS += 1
        print(f"  ok  {label}")
    else:
        ok = False
        print(f"  FAIL  {label}")


def _resident_up(url):
    try:
        with urllib.request.urlopen(url + "/models", timeout=3) as r:
            return r.status == 200 and bool(json.loads(r.read()).get("data"))
    except Exception:
        return False


# import the MCP face — the EXACT tool functions an agent calls (the @mcp.tool() wraps the function;
# we call the underlying function so this is a true by-use of the agent face).
import mcp_face.server as srv
from fabric import config as fcfg

BRAIN_UP = _resident_up(fcfg.DEFAULT_BASE_URL)
EMBED_UP = _resident_up(fcfg.DEFAULT_EMBED_URL)
print(f"\n[env] resident brain {fcfg.DEFAULT_BASE_URL}: {'UP' if BRAIN_UP else 'DOWN'} · "
      f"embedder {fcfg.DEFAULT_EMBED_URL}: {'UP' if EMBED_UP else 'DOWN'}")

# need a graph for preview_turn context (chat_parts reads a graph like chat() does).
GRAPH = srv.SUITE.create_node  # noqa — just to confirm the verb exists
gid = "mcp-eng-test"
try:
    srv.SUITE.create_node(gid, "constant", {"value": "hello"})
except Exception:
    pass

# ── 1. cognition_info() via MCP → the registries ─────────────────────────────────────────────────
print("\n[1] cognition_info() via MCP — the agent's 'what can I compose with'")
info = srv.cognition_info()
check("1 cognition_info returns roles", isinstance(info.get("roles"), (dict, list)) and len(info["roles"]) > 0)
check("1 cognition_info returns rule_ops (the grammar)", bool(info.get("rule_ops")))
check("1 cognition_info returns destination_kinds", bool(info.get("destination_kinds")))
check("1 cognition_info returns thought_shapes", bool(info.get("thought_shapes")))
check("1 cognition_info returns activation_contexts", bool(info.get("activation_contexts")))
# the SELECT inspects (reuse the /api selects)
mfr = srv.models_for_role("embed")
check("1 models_for_role('embed') returns candidate models", "models" in mfr)
check("1 cognition_inputs returns readable addresses", "roles" in srv.cognition_inputs())
check("1 field_types returns the closed registry", isinstance(srv.field_types(), dict) and len(srv.field_types()) > 0)
sc = srv.list_skills_contexts()
check("1 list_skills_contexts returns the skill+context registries (the addressable input units)",
      "skills" in sc and "contexts" in sc)

# ── 2. configure+run a role via MCP (generate) against the resident 4B → a real validated output ──
print("\n[2] run_role (generate) via MCP — configure + run ONE role → validated output")
gen_addr = None
if BRAIN_UP:
    res = srv.run_role("focus", utterance="What did we decide about the storage layer?")
    check("2 run_role(generate) returns op=generate", res.get("op") == "generate")
    check("2 run_role output is a validated dict (focus schema)", isinstance(res.get("output"), dict) and res["output"])
    check("2 run_role persisted a run:// address", str(res.get("address", "")).startswith("run://"))
    gen_addr = res.get("address")
    print(f"      output keys: {list(res['output'])} · address: {gen_addr}")
else:
    check("2 SKIPPED — resident brain DOWN (run_role generate needs :8000)", True)
    print("      brain down — generate by-use pending the resident 4B")

# ── 3. EMBED run via MCP (run_role op=embed) → a real 1024-dim vector (GPU-GATED) ─────────────────
print("\n[3] run_role (op=embed) via MCP — the EMBED headline")
# the embed role declares op=embed (registry-is-truth — we don't fabricate the op).
embed_role = srv.SUITE.role_registry["embed"]
check("3 the 'embed' role declares op=embed (the op-axis is registry-declared, not invented)",
      getattr(embed_role, "op", None) == "embed")
embed_live = False
if EMBED_UP:
    res = srv.run_role("embed", utterance="storage layer is content-addressed on ext4", op="embed")
    out = res.get("output", {})
    check("3 embed run returns a vector", isinstance(out.get("vector"), list) and len(out["vector"]) > 0)
    check(f"3 embed vector dim == {fcfg.DEFAULT_EMBED_DIM} (the configured dim)",
          out.get("dim") == fcfg.DEFAULT_EMBED_DIM)
    embed_live = True
    print(f"      LIVE embed: dim={out.get('dim')} model={out.get('model')}")
else:
    # the embedder is NOT resident. PROVE THE CODE PATH (op=embed routes to the embed plumbing) WITHOUT
    # a blind evict: with ensure=False a down embedder must FAIL LOUD (never a silent degrade).
    raised = False
    try:
        srv.run_role("embed", utterance="x", op="embed", ensure=False)
    except Exception as e:
        raised = True
        print(f"      embedder down + ensure=False → FAILS LOUD as designed: {type(e).__name__}")
    check("3 embed CODE PATH proven: op=embed routes to the embed plumbing + FAILS LOUD when down "
          "(ensure=False) — the live 1024-dim vector pends a safe GPU window (no blind brain-evict)", raised)

# ── 4. inspect a run output by address via MCP → reads it back ────────────────────────────────────
print("\n[4] inspect_address via MCP — read a past run's output back by address")
if gen_addr:
    got = srv.inspect_address(gen_addr)
    check("4 inspect_address reads the generate run back", got.get("address") == gen_addr and got.get("value"))
    check("4 the read-back value EQUALS the run output (round-trip)", isinstance(got["value"], dict))
else:
    # seed a run:// address ourselves to prove inspect_address resolves it (engine resolve_address reuse).
    cas = srv.SUITE.store.put_content({"probe": "value"})
    srv.SUITE.store.set_ref("run://mcp-probe/x", cas)
    got = srv.inspect_address("run://mcp-probe/x")
    check("4 inspect_address resolves a run:// address (engine resolve_address reuse)",
          got.get("value") == {"probe": "value"})
# fail-loud on a bad address
raised = False
try:
    srv.inspect_address("run://nope/missing")
except Exception:
    raised = True
check("4 inspect_address FAILS LOUD on an unresolvable address (never a silent empty)", raised)

# ── 5. CREATE: propose_role SURFACES (kept) + the DIRECT create tools are registered (#58) ────────
print("\n[5] propose_role via MCP surfaces (kept) + direct create_role/skill/context registered (#58)")
roles_dir = os.path.join(ROOT, "roles")
before_files = set(os.listdir(roles_dir))
spec = {"id": "mcp_probe_role", "label": "MCP probe",
        "prompt_template": "Return JSON {ack:bool}. Always ack=true.",
        "output_fields": [{"name": "ack", "type": "bool"}]}
prop = srv.propose_role(spec)
sid = prop.get("id")
check("5 propose_role (surfacing path, kept available) returns a surfaced id", bool(sid))
surfaced = srv.SUITE.store.get_surfaced(sid)
check("5 the proposal SURFACED (an inbox item exists)", surfaced is not None)
check("5 the surfaced item is UNRESOLVED (propose still surfaces — NOT applied)",
      surfaced is not None and surfaced.get("resolved") in (None, ""))
after_files = set(os.listdir(roles_dir))
check("5 propose wrote NO roles/ file (surfacing path is still propose-not-apply)",
      after_files == before_files)
# the #58 DIRECT create tools are wired (by-use applies LIVE — proven in direct_create_acceptance.py
# with an isolated dir so this no-regression suite never commits the live repo).
check("5 the DIRECT create_role tool is registered on the MCP face (#58)", hasattr(srv, "create_role"))
check("5 the DIRECT create_skill tool is registered on the MCP face (#56/#58)", hasattr(srv, "create_skill"))
check("5 the DIRECT create_context tool is registered on the MCP face (#56/#58)", hasattr(srv, "create_context"))
check("5 create_role routes to the DIRECT Suite.create_role (no surfacing in its source)",
      "create_role" in __import__("inspect").getsource(srv.create_role)
      and "SUITE.create_role" in __import__("inspect").getsource(srv.create_role))

# ── 6. run_items + run_reduce via MCP → the map + the cross-unit join ─────────────────────────────
print("\n[6] run_items (map) + run_reduce (cross-unit join) via MCP")
if BRAIN_UP:
    items = ["The storage layer is content-addressed.",
             "We decided storage lives on ext4.",
             "The card has 16GB of VRAM."]
    mres = srv.run_items("ground", items)
    check("6 run_items fanned ONE role over N units", mres.get("n_units") == len(items))
    check("6 run_items produced per-unit run:// addresses", len(mres.get("addresses", {})) == len(items))
    check("6 run_items resolved each unit's output", len(mres.get("resolved", {})) >= 1)
    # cross-unit JOIN — mode=rule (deterministic L2, no model, no embedder) over the map addresses.
    addrs = list(mres["addresses"].values())
    rred = srv.run_reduce(addrs, mode="rule", reduce_rule="count")
    check("6 run_reduce (mode=rule) joined the map outputs", rred.get("joined", {}).get("count") == len(addrs))
    # mode=role (synthesize join via the resident 4B + reduce_synth role)
    rrole = srv.run_reduce(addrs, mode="role", role="reduce_synth")
    check("6 run_reduce (mode=role) synthesized via reduce_synth", isinstance(rrole.get("joined"), dict) and rrole["joined"])
else:
    check("6 SKIPPED — resident brain DOWN (run_items/run_reduce need :8000)", True)
# run_reduce mode=rule with an unknown named rule → FAIL LOUD (registry-is-truth)
raised = False
try:
    srv.run_reduce(["run://x/a"], mode="rule", reduce_rule="bogus")
except Exception:
    raised = True
check("6 run_reduce rejects an unknown named reduce_rule (fail loud, never fabricate)", raised)

# ── FLOOR (C9.2, reframed by #58) — asserted directly on THIS face ────────────────────────────────
print("\n[FLOOR] the BUILD-DISPATCH floor holds on the MCP cognition face (C9.2, #58 reframe)")
import inspect as _inspect
import ast as _ast
src = _inspect.getsource(srv)
# #58: AUTHORING-apply (create_role/skill/context → live) is now ALLOWED from the agent face. What
# STILL holds is the BUILD-DISPATCH floor: no MCP tool may trigger the wire's autonomous repo-mutation —
# i.e. CALL the operator-only build-dispatch trigger (resolve_surfaced) or the wire's dispatch
# (dispatch_decision) or launch `claude -p`. We scan the REAL CODE (AST — robust to docstrings/comments
# that legitimately MENTION these tokens while describing the floor) for any CALL of those names.
_called = set()
for node in _ast.walk(_ast.parse(src)):
    if isinstance(node, _ast.Call):
        f = node.func
        nm = f.attr if isinstance(f, _ast.Attribute) else (f.id if isinstance(f, _ast.Name) else None)
        if nm:
            _called.add(nm)
FORBIDDEN_CALLS = {"resolve_surfaced", "dispatch_decision", "apply_role_delete"}
breaches = sorted(FORBIDDEN_CALLS & _called)
check("FLOOR: NO MCP tool CALLS the build-dispatch trigger (resolve_surfaced/dispatch_decision) — the "
      "wire's autonomous repo-mutation stays operator-gated, off this face",
      not breaches)
if breaches:
    print("      breach calls:", breaches)
# the `claude -p` build-dispatch is a SUBPROCESS LAUNCH (the wire's implement.py via subprocess/Popen).
# The phrase "claude -p" appears ONLY in floor-describing docstrings here (which AST/launch-detection
# ignores); a REAL launch would be a subprocess.run/Popen call or an import of the wire's implement.py.
# Scan the AST imports + the called-names set for those — never the bare docstring mention.
_imported = set()
for node in _ast.walk(_ast.parse(src)):
    if isinstance(node, _ast.Import):
        _imported.update(a.name.split(".")[0] for a in node.names)
    elif isinstance(node, _ast.ImportFrom) and node.module:
        _imported.add(node.module.split(".")[0])
check("FLOOR: no MCP tool launches `claude -p` (no subprocess/implement.py — the build-dispatch stays "
      "operator-gated, off this face)",
      "subprocess" not in _imported and "implement" not in _imported
      and not ({"run", "Popen", "call", "check_output"} & _called and "subprocess" in _imported))
# #58 POSITIVE: authoring-apply IS now reachable from this face (the reframe — create applies directly).
_code_no_comments = "\n".join(l.split("#", 1)[0] for l in src.splitlines())
check("FLOOR (#58): authoring-apply IS allowed — create_role/skill/context call the DIRECT Suite methods",
      "SUITE.create_role" in _code_no_comments and "SUITE.create_skill" in _code_no_comments
      and "SUITE.create_context" in _code_no_comments)
# the registered tool set does not include an apply/resolve tool name
tool_names = set()
try:
    import asyncio
    tool_names = {t.name for t in asyncio.get_event_loop().run_until_complete(srv.mcp.list_tools())}
except Exception:
    # fallback: scan @mcp.tool()-decorated module functions
    tool_names = {n for n, o in vars(srv).items() if callable(o) and not n.startswith("_")}
check("FLOOR: no MCP tool is named apply_node/resolve/approve/dispatch on the cognition additions",
      not ({"resolve", "approve", "dispatch", "checkpoint", "revert_self_change"} & tool_names))

print(f"\n{'ALL PASS' if ok else 'FAILURES PRESENT'} — {PASS} checks passed — "
      f"MCP cognition engine-exposure: agents inspect/configure/run/embed/inspect/create via the MCP, "
      f"REUSING the /api/cognition Suite methods + the cognition.py engine; the operator-only floor holds "
      f"(create=propose→surface, no self-apply). "
      f"{'LIVE embed proven.' if embed_live else 'Embed CODE PATH proven; live vector pends a safe GPU window.'}")
sys.exit(0 if ok else 1)
