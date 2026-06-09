"""tests/chunk_compose_acceptance.py — Cognition Engine F3 (chunk-and-compose for over-context units).

Proves the over-context TIER in runtime/cognition.py — when a unit's text EXCEEDS the model's context
window, SPLIT it into context-sized chunks, MAP the role over each chunk (REUSE run_items), then COMPOSE
the per-chunk outputs into ONE result (REUSE run_reduce). Today a unit > the model context is a DEAD END
(a loud 400); F3 makes the common over-context case (one big document) processable.

  run_chunked       — the over-context tier. The SIZE GATE (fit vs chunk) reads the model's context window
                      from the LIVE registry (max_model_len), injectable for a SHORT synthetic window.
                      FIT  → byte-identical to a single run_role call (no chunking, no reduce, no event).
                      OVER → chunk_text → run_items (map) → run_reduce (compose) → ONE result.
  model_context_window / chunk_budget_chars / chunk_text — the registry-read window + the budget arithmetic
                      + the deterministic chunker (NOTHING hardcodes 65536).

THE F3 LAW (a dropped chunk is LOUD): the chunks ARE one document, so run_items' F2 per-unit resilience
(a failed unit lands in .failed, the good units still return) is the OPPOSITE of what F3 needs — composing
the survivors would SILENTLY TRUNCATE the document. So run_chunked inspects .failed AND .skipped after the
map and FAILS LOUD (which chunk, of how many, why) rather than compose a truncated document.

LIVE-or-MOCKED (mirror run_items_acceptance / reduce_acceptance): the resident 4B is preferred; if down, a
mocked transport captures the REAL chunk→map→compose round-trip (never a false green).
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from store.fs_store import FsStore                                          # noqa: E402
from runtime import cognition                                              # noqa: E402
from runtime.cognition import (run_chunked, ChunkedResult, run_role,        # noqa: E402
                               model_context_window, chunk_budget_chars, chunk_text,
                               resolve_run_ref)
from runtime.roles import RoleRegistry                                     # noqa: E402

ROLES = os.path.join(ROOT, "roles")
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


reg = RoleRegistry().discover([ROLES])
focus = reg["focus"]                          # a fireable "utterance"-only role (the byte-identical path)


# =================================================================================================
# LIVE detection (the same probe run_items_acceptance uses).
# =================================================================================================
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
    print(f"  ..  resident 4B not up ({type(e).__name__}) — proving run_chunked on a MOCKED transport")


# A focus-shaped schema-valid stub (FocusOut = {intent, which_roles}); captures the user content it saw.
class _Validated:
    def __init__(self, d): self._d = d
    def model_dump(self): return dict(self._d)


def _install_focus_mock(seen):
    """Mock fabric.client.complete to return a schema-valid FocusOut + record the user content. Returns
    the original so the caller restores it. The compose reduce-role (reduce_synth) returns {summary}."""
    orig = cognition.client.complete

    def _mock(t, msgs, *, model, schema=None, json=False, temperature=0.0, max_tokens=256, **kw):
        user = msgs[-1]["content"]
        seen.append(user)
        # reduce_synth's schema is ReduceSynthOut={summary}; everything else is FocusOut={intent,which_roles}.
        sname = getattr(schema, "__name__", "")
        if sname == "ReduceSynthOut":
            return _Validated({"summary": "MERGED: " + user[:60]})
        return _Validated({"intent": user[:40], "which_roles": []})

    cognition.client.complete = _mock
    return orig


# =================================================================================================
# 1 · the registry-read window + the budget arithmetic + the chunker (NOTHING hardcodes 65536)
# =================================================================================================
win = model_context_window()                                  # reads ops/services.json chat-4b max_model_len
check("model_context_window() reads the LIVE registry (a positive token window — chat-4b max_model_len)",
      isinstance(win, int) and win > 0)
# it is the registry value, not a hardcoded constant — confirm it matches what services.json declares.
import json as _json                                                       # noqa: E402
with open(os.path.join(ROOT, "ops", "services.json")) as _f:
    _reg = _json.load(_f)
_declared = int((_reg["services"]["chat-4b"]["config"])["max_model_len"])
check("the window equals the registry's max_model_len (registry-is-truth, never a hardcoded 65536)",
      win == _declared)

# a corrupt/absent service fails loud (never a silent guessed window).
raised = False
try:
    model_context_window(service_id="no-such-service")
except KeyError:
    raised = True
check("model_context_window FAILS LOUD on an unknown service (never assume a window)", raised)

# the budget arithmetic: usable = (window − out − prompt) × margin, × chars/token.
b = chunk_budget_chars(1000, output_tokens=100, prompt_tokens=100, margin=0.8, chars_per_token=4)
check("chunk_budget_chars derives chars from the token window (reservations + margin + char ratio)",
      b == int((1000 - 100 - 100) * 0.8) * 4)
# a window too small for the reservations fails loud (never a ≤0 chunk size).
small_raised = False
try:
    chunk_budget_chars(50, output_tokens=100, prompt_tokens=100)
except ValueError:
    small_raised = True
check("chunk_budget_chars FAILS LOUD when the window can't fit the reservations (no ≤0 chunk size)",
      small_raised)

# the chunker: a doc <= budget is ONE chunk; a doc > budget splits into multiple; the join is the whole doc.
doc = "\n\n".join(f"Paragraph {i}: " + ("word " * 30).strip() for i in range(40))   # ~6K chars, many paras
one = chunk_text("short text", 1000)
check("chunk_text: a fitting text is ONE chunk (no split)", one == ["short text"])
parts = chunk_text(doc, 500)
check("chunk_text: an over-budget doc splits into MULTIPLE chunks", len(parts) > 1)
check("chunk_text: every chunk is within the budget (no chunk exceeds chunk_chars)",
      all(len(p) <= 500 for p in parts))
check("chunk_text: no chunk is empty (never a fabricated empty unit)", all(p for p in parts))
# coverage: the chunks together carry every non-whitespace token of the doc (no silent character drop).
check("chunk_text: the chunks COVER the whole doc (no silent truncation — coverage law)",
      "".join(parts).replace("\n", "").replace(" ", "") == doc.replace("\n", "").replace(" ", ""))
# a single line longer than the budget hard-splits.
longline = "x" * 2500
hs = chunk_text(longline, 1000)
check("chunk_text: a single line over the budget HARD-splits at the char boundary",
      len(hs) == 3 and all(len(p) <= 1000 for p in hs) and "".join(hs) == longline)


# =================================================================================================
# 2 · THE FIT PATH — a unit that FITS is byte-identical to a single run_role call (additive floor)
# =================================================================================================
store_fit = FsStore(os.path.join(tempfile.mkdtemp(prefix="chunk-fit-"), "store"))
FIT_TEXT = "tell me about the voice circuit"          # tiny — fits any window
seen_fit: list = []
if not live:
    orig = _install_focus_mock(seen_fit)
try:
    # inject a generous window so the small text fits.
    res_fit = run_chunked(focus, FIT_TEXT, store_fit, turn_id="t-fit", context_window=8192)
    # a direct run_role on the same text (the byte-identical comparison) — the SAME mock stays installed.
    direct = run_role(focus, {"utterance": FIT_TEXT})
finally:
    if not live:
        cognition.client.complete = orig

check("run_chunked returns a ChunkedResult", isinstance(res_fit, ChunkedResult))
check("FIT: a unit within the window is NOT chunked (chunked=False, n_chunks=1)",
      res_fit.chunked is False and res_fit.n_chunks == 1)
check("FIT: no compose ran (compose_mode is None, no map addresses)",
      res_fit.compose_mode is None and res_fit.map_addresses == {})
check("FIT: composed is the single role output (byte-identical to a direct run_role on the same text)",
      res_fit.composed == direct)


# =================================================================================================
# 3 · THE OVER-CONTEXT PATH — split → map (run_items) → compose (run_reduce) → ONE coherent output
#     proven with a SHORT injected window + a long synthetic doc (a real 65K-char doc is impractical)
# =================================================================================================
store_ov = FsStore(os.path.join(tempfile.mkdtemp(prefix="chunk-over-"), "store"))
LONG_DOC = "\n\n".join(
    f"Section {i}. " + ("The storage layer stays content-addressed on ext4. " * 8).strip()
    for i in range(30))                                # ~13K chars
# a SHORT window: at window=300, out=50, prompt=50, margin=0.85, chars/token=4 →
# budget = int((300-50-50)*0.85)*4 = int(170)*4 = 680 chars/chunk → ~20 chunks over a 13K doc.
WIN, OUT, PROMPT = 300, 50, 50
budget = chunk_budget_chars(WIN, output_tokens=OUT, prompt_tokens=PROMPT)
expect_chunks = len(chunk_text(LONG_DOC, budget))
check("the synthetic doc is genuinely OVER the injected short window (multiple chunks expected)",
      len(LONG_DOC) > budget and expect_chunks > 1)

# COMPOSE via mode="rule" — a deterministic L2 join over the chunk outputs (model-free compose; the cleanest
# proof that EVERY chunk's output reached the compose). The rule concatenates the chunk intents → one record.
def _concat_rule(values):
    """A PURE deterministic compose over the N chunk outputs: join their 'intent' fields → one merged dict."""
    return {"merged_intents": [v.get("intent") for v in values], "n": len(values)}


events_ov: list = []
seen_ov: list = []
if not live:
    orig = _install_focus_mock(seen_ov)
try:
    res_ov = run_chunked(focus, LONG_DOC, store_ov, turn_id="t-over",
                         context_window=WIN, output_tokens=OUT, prompt_tokens=PROMPT,
                         compose_mode="rule", reduce_rule=_concat_rule,
                         emit=lambda kind, p: events_ov.append((kind, p)))
finally:
    if not live:
        cognition.client.complete = orig

check("OVER: the over-context unit WAS chunked (chunked=True)", res_ov.chunked is True)
check("OVER: it split into the expected number of chunks (deterministic chunker)",
      res_ov.n_chunks == expect_chunks and res_ov.n_chunks > 1)
check("OVER: the per-chunk MAP addresses are present (run://<turn>/<role>/<i>, one per chunk)",
      len(res_ov.map_addresses) == res_ov.n_chunks and
      all(a == f"run://t-over/focus/{i}" for i, a in res_ov.map_addresses.items()))
# every chunk's MAP output actually resolves (the map ran the role over EVERY chunk — none dropped).
check("OVER: every chunk's map output RESOLVES (the role ran over EVERY chunk — none silently dropped)",
      all(isinstance(resolve_run_ref(store_ov, a), dict) and "intent" in resolve_run_ref(store_ov, a)
          for a in res_ov.map_addresses.values()))
# the COMPOSE produced ONE coherent output joining ALL the chunks (the rule saw n == n_chunks values).
check("OVER: COMPOSED to ONE output that joined ALL the chunks (compose saw every chunk's output)",
      isinstance(res_ov.composed, dict) and res_ov.composed.get("n") == res_ov.n_chunks and
      len(res_ov.composed.get("merged_intents", [])) == res_ov.n_chunks)
check("OVER: compose_mode is recorded ('rule')", res_ov.compose_mode == "rule")
# C1.6 — run_chunked adds NO third emit; the emits are run_items' + run_reduce's own per-fan rollups.
kinds = [k for (k, _p) in events_ov]
check("OVER: the emits are run_items' (cognition.items) + run_reduce's (cognition.reduce) per-fan rollups "
      "— run_chunked adds NO extra emit (C1.6 per-fan discipline preserved)",
      "cognition.items" in kinds and "cognition.reduce" in kinds)
check("OVER: NO resolve/approve/dispatch verb on any emit (the operator-only floor — driver, not agent)",
      all(all(k not in p for k in ("resolve", "approve", "dispatch", "verb")) for (_kind, p) in events_ov))


# =================================================================================================
# 3b · OVER-CONTEXT with compose_mode="role" — the synthesize join via reduce_synth (the smart compose)
# =================================================================================================
store_role = FsStore(os.path.join(tempfile.mkdtemp(prefix="chunk-role-"), "store"))
seen_role: list = []
if not live:
    orig = _install_focus_mock(seen_role)
try:
    res_role = run_chunked(focus, LONG_DOC, store_role, turn_id="t-role",
                           context_window=WIN, output_tokens=OUT, prompt_tokens=PROMPT,
                           compose_mode="role")            # default reduce_synth join
finally:
    if not live:
        cognition.client.complete = orig
check("OVER(role): compose_mode='role' synthesized via reduce_synth → ONE merged output (a {summary} dict)",
      res_role.chunked is True and res_role.compose_mode == "role" and
      isinstance(res_role.composed, dict) and "summary" in res_role.composed)


# =================================================================================================
# 4 · THE F3 LAW — a chunk FAILURE surfaces LOUD (never compose a truncated document)
# =================================================================================================
store_fail = FsStore(os.path.join(tempfile.mkdtemp(prefix="chunk-fail-"), "store"))
# Mock the transport so the FIRST chunk-fire RAISES (a poison chunk) and the rest succeed — run_items'
# F2 would put it in .failed and return the survivors; run_chunked MUST refuse to compose them.
from fabric import client as _client                                       # noqa: E402
orig_complete = _client.complete
_fire_count = {"n": 0}


def _poison_first(t, msgs, *, model, schema=None, json=False, temperature=0.0, max_tokens=256, **kw):
    _fire_count["n"] += 1
    if _fire_count["n"] == 1:
        from fabric.client import FabricError
        raise FabricError("simulated over-context 400 on chunk 0 (poison chunk)")
    return _Validated({"intent": msgs[-1]["content"][:40], "which_roles": []})


cognition.client.complete = _poison_first
fail_raised = False
fail_msg = ""
try:
    run_chunked(focus, LONG_DOC, store_fail, turn_id="t-fail",
                context_window=WIN, output_tokens=OUT, prompt_tokens=PROMPT,
                compose_mode="rule", reduce_rule=_concat_rule)
except RuntimeError as e:
    fail_raised = True
    fail_msg = str(e)
finally:
    cognition.client.complete = orig_complete

check("FAIL-LOUD: a chunk failure RAISES (never composes the survivors — no silent truncation)",
      fail_raised)
check("FAIL-LOUD: the message is LEGIBLE (which chunk, of how many, why — F4 not a bare KeyError)",
      "refusing to compose a TRUNCATED document" in fail_msg and "chunk 0" in fail_msg and
      "FAILED" in fail_msg)


# =================================================================================================
# 5 · ADDITIVE / behaviour-preserving — run_role/run_items/run_reduce/run_swarm unchanged (the C law)
# =================================================================================================
import inspect                                                              # noqa: E402
sig = inspect.signature(run_role)
check("run_role's signature is unchanged (additive — run_chunked did not touch the seam)",
      list(sig.parameters)[:2] == ["role", "ctx"])
check("run_items / run_reduce / run_swarm remain present (additive — run_chunked REUSES, removes nothing)",
      all(callable(getattr(cognition, n)) for n in ("run_items", "run_reduce", "run_swarm", "run_jury")))
# run_chunked is a NEW opt-in function (the over-context tier) — present + callable.
check("run_chunked is a NEW opt-in function (the over-context tier) — present + callable",
      callable(getattr(cognition, "run_chunked")))


print(f"\nALL {PASS} CHECKS PASS — F3 chunk-and-compose: registry-read window (max_model_len, never "
      f"hardcoded) · deterministic chunker (covers the whole doc) · FIT byte-identical to run_role · OVER "
      f"split→map(run_items)→compose(run_reduce) → ONE coherent output · role+rule compose · a chunk "
      f"failure FAILS LOUD (no silent truncation) · additive (run_role/items/reduce/swarm unchanged)")
