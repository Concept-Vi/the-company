"""tests/use_side_gates_acceptance.py — WF2 LIVE half, USE-SIDE gates (deliverables b/c/d/e).

Unit-level acceptance for the use-side capability gates finished in this build. NO live endpoint
needed (the gates are pure logic over the catalog + the transport seam) — the LIVE end-to-end proof
(reasoning populates through the real bridge) is a SEPARATE step (a real /api/chat turn vs the FP8
brain at :8001), recorded in the build-log, never asserted by this offline test.

What this proves (offline, deterministic):
  (b) the REASONING use-gate sends `think` ONLY IFF the effective model DECLARES thinking=true.
  (c) the forced-choice tool probe is RETIRED: transport.model_supports_tools(endpoint='vllm') RAISES
      (declaration is truth; an undeclared vLLM model fails loud — never a forced tool_choice).
  (c) suite._model_supports_tools reads the DECLARATION first (declared-true → True without any probe).
  (routing) cognition.run_role routes think by the STACK (base_url), not a model-name heuristic.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_fail = {"n": 0}
def check(label, cond):
    print(("  ok  " if cond else "  XX  ") + label)
    if not cond:
        _fail["n"] += 1

# ---------------------------------------------------------------------------------------------------
# (c) the forced-choice probe is RETIRED — transport.model_supports_tools(vllm) RAISES, never probes.
# ---------------------------------------------------------------------------------------------------
from fabric import transport as ftrans

# CRUCIAL: the port below is CLOSED. If a forced probe still ran it would try to connect and raise a
# URLError/ConnectionError. A ValueError proves the probe is gone — it fails loud on the DECLARATION gap
# BEFORE any network attempt.
raised_kind = None
msg = ""
try:
    ftrans.model_supports_tools("some-undeclared-vllm-model",
                                base_url="http://127.0.0.1:65530/v1", endpoint="vllm", timeout=2)
except ValueError as e:
    raised_kind = "ValueError"
    msg = str(e)
except Exception as e:                          # a URLError/ConnectionError here would mean a probe DID run
    raised_kind = type(e).__name__
    msg = str(e)
check("(c) model_supports_tools(endpoint='vllm') RAISES ValueError (forced probe retired)",
      raised_kind == "ValueError")
check("(c) the raise is a ValueError (declaration gap), NOT a connection error (NO probe was attempted)",
      raised_kind == "ValueError")
check("(c) the raise NAMES the fix (declare the model) — loud-fail, legible",
      raised_kind == "ValueError" and "declar" in msg.lower())

# The retired-probe source has NO forced tool_choice left in it.
import inspect
src = inspect.getsource(ftrans.model_supports_tools)
check("(c) the vllm branch contains NO forced tool_choice dict (probe code physically gone)",
      '"tool_choice": {"type": "function"' not in src and "RETIRED" in src)

# ---------------------------------------------------------------------------------------------------
# (b) the REASONING use-gate sends `think` ONLY IFF the model DECLARES thinking=true.
#     We drive the exact gate predicate the chat path uses (suite._declared_cap + the _send_think rule)
#     against the live catalog, for a declared-thinking model and a non-declaring one.
# ---------------------------------------------------------------------------------------------------
from runtime import suite as _suite_mod
# build a bare Suite without running heavy init: reuse the instance-method on a lightweight shim.
class _Probe:
    _repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_Probe._declared_cap = _suite_mod.Suite._declared_cap

p = _Probe()

def send_think(model, think_value):
    """Replicate suite._chat_part_core's gate (lines ~6707-6711): the EXACT predicate."""
    _decl = p._declared_cap(model, "thinking")
    _model_thinks = isinstance(_decl, dict) and _decl.get("value") is True
    return (think_value is not None) and _model_thinks

FP8 = "RedHatAI/Qwen3.5-4B-FP8-dynamic"     # declares thinking=true
check("(b) declared-thinking model + think=True  → SENDS think", send_think(FP8, True) is True)
check("(b) declared-thinking model + think=False → SENDS think (the off-switch still rides)",
      send_think(FP8, False) is True)
check("(b) declared-thinking model + think=None  → does NOT send (no key → model default)",
      send_think(FP8, None) is False)
check("(b) UNDECLARED model + think=True → does NOT send (no thinking declaration → no enable_thinking)",
      send_think("cyankiwi/Qwen3.5-4B-AWQ-4bit-not-declared-thinking", True) is False)

# confirm the catalog actually backs this (FP8 declares thinking True; a bare service-id is undeclared).
sys.path.insert(0, os.path.join(_Probe._repo_root, "ops", "cli"))
import capabilities as _caps
_fp8_think = _caps.capabilities_for(FP8).get("thinking")
check("(b) catalog: FP8 served-name declares thinking.value=True",
      isinstance(_fp8_think, dict) and _fp8_think.get("value") is True)

# ---------------------------------------------------------------------------------------------------
# (c) suite._model_supports_tools reads the DECLARATION FIRST (declared-true → True, no probe).
# ---------------------------------------------------------------------------------------------------
_Probe._model_supports_tools = _suite_mod.Suite._model_supports_tools
_Probe._tools_cap_cache = {}
_Probe.TOOLS_CAP_TTL = 60.0
# FP8 declares tools=true → must return True from a CLOSED endpoint (proves declaration short-circuits
# before any probe; a probe would hit the closed port and return False).
got = _Probe._model_supports_tools(p, FP8, base_url="http://127.0.0.1:65530/v1")
check("(c) declared-tools model → True from a CLOSED endpoint (declaration short-circuits the probe)",
      got is True)

# ---------------------------------------------------------------------------------------------------
# (routing) cognition.run_role routes think by the STACK (base_url), not the model name.
# ---------------------------------------------------------------------------------------------------
import inspect as _ins
from runtime import cognition as _cog
rr_src = _ins.getsource(_cog.run_role)
# the LIVE routing CONDITION must be base_url-based (_is_ollama), never the model-name heuristic. The old
# `"/" not in model` may survive only inside an explanatory COMMENT; assert it is gone from the actual
# `if ... :` routing line.
_routing_lines = [ln for ln in rr_src.splitlines()
                  if "ollama_native_transport" in ln or (ln.strip().startswith("if ") and "eff_think" in ln)]
_routing_if = next((ln for ln in rr_src.splitlines() if ln.strip().startswith("if eff_think is not None")), "")
check("(routing) the think-routing CONDITION is base_url-based (_is_ollama), not '/' in model",
      "_is_ollama" in _routing_if and '"/" not in model' not in _routing_if)
check("(routing) run_role derives the endpoint kind from base_url (11434 = ollama)",
      "_is_ollama" in rr_src and "11434" in rr_src)

print()
if _fail["n"]:
    print(f"FAILED: {_fail['n']} check(s)")
    sys.exit(1)
print("ALL USE-SIDE GATE CHECKS PASSED")
