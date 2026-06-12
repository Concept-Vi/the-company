"""tests/session_search_acceptance.py — the SEARCH→HANDLE→ACT chain's teeth (Session Fabric
R4.2/R4.5; research lane 5 B5.1+B5.2).

What is proven HERE, against the REAL index + the REAL registry (no fixtures — the corpus index at
~/.cache/company/substrate-claude-sessions and the live agent_sessions registry ARE the test bed;
this suite is honest about being environment-backed, the same way the registry acceptance is):

  1. A real content query returns LIVE HANDLES: session_id + session_address + state joined at
     query time + point + snippet + primary_verb + runnable commands (R4.2's envelope).
  2. Grouping: one result per session (best chunk leads, hits_in_session counts the rest).
  3. The primary_verb shown is EXACTLY what session_post(verb='auto')'s router would do now
     (supervised-live→deliver · closed→wake · else→queue) — the result is act-ready.
  4. Point parsing: `turn-N-speaker…` anchors yield {turn:int, speaker}; the raw anchor +
     chunk_address always ride (R3.4's adapter input).
  5. Closed vocabularies fail TEACHING-loud: unknown mode, unknown state filter, empty q.
  6. The semantic leg is HONEST about its preconditions: embedder down ⇒ a teaching raise naming
     `company up embed-pplx` (never silent emptiness); embedder up ⇒ a real semantic search runs
     and the envelope declares mode_used='semantic'. (Branch chosen by the REAL availability —
     both paths are the law; whichever is live is what gets proven.)
  7. The MCP face routes op="search" → the join (the tool layer, registered against the real Suite
     with a recorder MCP — no protocol stub theater; the stdio protocol proof is the separate
     tests/session_search_mcp_stdio_probe.py, which speaks real JSON-RPC to the real server).

Run: ./.venv/bin/python tests/session_search_acceptance.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore                      # noqa: E402
from runtime.registry import NodeRegistry               # noqa: E402
from runtime.suite import Suite                         # noqa: E402
from fabric import config as fcfg                       # noqa: E402
from runtime import session_search                      # noqa: E402

ok = True


def check(label, cond, extra=""):
    global ok
    ok &= bool(cond)
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}" + (f"  — {extra}" if extra and not cond else ""))


def raises_teaching(fn, *needles):
    try:
        fn()
        return False, "no raise"
    except ValueError as e:
        msg = str(e)
        missing = [n for n in needles if n not in msg]
        return (not missing), (f"missing {missing} in: {msg[:160]}" if missing else "")


print("session_search acceptance — the search→handle→act chain (R4.2/R4.5)")

suite = Suite(FsStore(fcfg.STORE_DIR), NodeRegistry().discover([os.path.join(ROOT, "nodes")]))

# ── 1+2+3+4: a REAL lexical search returns act-ready live handles ────────────────────────────────
out = session_search.search_sessions(suite, q="supabase backend store documents", k=3, mode="lexical")
check("envelope declares mode_used + semantic availability + index provenance",
      out["mode_used"] == "lexical" and "available" in out["semantic"]
      and out["index"]["chunks"] > 0 and "embed_coverage" in out["index"])
check("a real query over the real index returns results", out["sessions_found"] > 0)
rs = out["results"]
check("one result per session (no duplicate session_ids)",
      len({r["session_id"] for r in rs}) == len(rs))
required = ("session_id", "session_address", "state", "cwd", "routable", "point", "snippet",
            "primary_verb", "commands", "score", "hits_in_session")
check("every result carries the full R4.2 handle envelope",
      all(all(k in r for k in required) for r in rs),
      f"missing keys in {[ [k for k in required if k not in r] for r in rs ]}")
check("session_address is the session:// form",
      all(r["session_address"] == f"session://{r['session_id']}" for r in rs))

VERB_OF = {"supervised-live": "deliver", "closed": "wake"}
for r in rs:
    if r["routable"]:
        expect = VERB_OF.get(r["state"], "queue")
        check(f"primary_verb({r['session_id'][:8]}…, state={r['state']}) == router's auto rule "
              f"({expect})", r["primary_verb"] == expect)
        check(f"commands carry describe + consult + the primary verb form",
              "describe" in r["commands"] and "consult" in r["commands"]
              and (expect in r["commands"] or expect == "deliver" and "deliver" in r["commands"]))
    else:
        check("unroutable hit is honest: primary_verb None + registry_error present",
              r["primary_verb"] is None and r.get("registry_error"))

# point parsing on a real turn anchor (find one among the pool)
deep = session_search.search_sessions(suite, q="supabase backend store documents",
                                      k=8, mode="lexical")
turned = [r for r in deep["results"] if r["point"]["turn"] is not None]
check("at least one matched point parses to {turn:int, speaker}",
      bool(turned) and isinstance(turned[0]["point"]["turn"], int)
      and turned[0]["point"]["speaker"] in ("tim", "claude"))
check("every point carries the raw anchor + chunk_address (R3.4 adapter input)",
      all(r["point"]["anchor"] and r["point"]["chunk_address"] for r in deep["results"]))

# detail=detailed widens honestly
det = session_search.search_sessions(suite, q="supabase backend", k=1, mode="lexical",
                                     detail="detailed")
check("detail='detailed' carries the full registry row + transcript path",
      det["results"] and "registry_row" in det["results"][0]
      and "transcript_rel_path" in det["results"][0])

# ── 5: closed vocabularies fail TEACHING-loud ────────────────────────────────────────────────────
good, why = raises_teaching(
    lambda: session_search.search_sessions(suite, q="x y", mode="vibes"), "unknown mode", "lexical")
check("unknown mode raises teaching (names the valid registry)", good, why)
good, why = raises_teaching(
    lambda: session_search.search_sessions(suite, q="x y", state="zombie"), "closed vocabulary")
check("unknown state filter raises teaching (closed vocabulary)", good, why)
good, why = raises_teaching(
    lambda: session_search.search_sessions(suite, q="   "), "`q` is required")
check("empty q raises teaching", good, why)
good, why = raises_teaching(
    lambda: session_search.search_sessions(suite, q="the of to", mode="lexical"),
    "no searchable terms")
check("stopword-only query raises teaching (lexical)", good, why)

# ── 6: the semantic leg is honest about its real preconditions (branch on REAL availability) ────
av = session_search.semantic_availability()
print(f"  · semantic availability NOW: {av['available']} — {av['why'][:110]}")
if av["available"]:
    sem = session_search.search_sessions(suite, q="session supervisor wake consult verbs",
                                         k=3, mode="semantic")
    check("REAL semantic search ran (mode_used=semantic, results carry cosine why)",
          sem["mode_used"] == "semantic" and sem["sessions_found"] > 0
          and all("cosine" in r["score_why"] for r in sem["results"]))
else:
    good, why = raises_teaching(
        lambda: session_search.search_sessions(suite, q="anything", mode="semantic"),
        "semantic", "lexical")
    check("semantic-down raises TEACHING (names the down leg + the lexical alternative)", good, why)
    auto = session_search.search_sessions(suite, q="supabase backend", k=1, mode="auto")
    check("auto DECLARES its choice when semantic is down (mode_used=lexical, why visible)",
          auto["mode_used"] == "lexical" and not auto["semantic"]["available"]
          and auto["semantic"]["why"])

# ── 7: the MCP face routes op='search' (tool layer over the REAL suite) ──────────────────────────
sys.path.insert(0, os.path.join(ROOT, "mcp_face"))
import importlib                                        # noqa: E402
sessions_mod = importlib.import_module("mcp_face.tools.sessions")


class _RecorderMCP:
    def __init__(self):
        self.tools = {}

    def tool(self, *a, **k):
        def deco(fn):
            self.tools[fn.__name__] = fn
            return fn
        return deco


rec = _RecorderMCP()
sessions_tool, session_post_tool = sessions_mod.register(rec, suite)
check("'search' is in the exported OPS", "search" in sessions_mod.OPS)
res = sessions_tool(op="search", q="supabase backend store documents", limit=2)
check("sessions(op='search') returns the joined envelope through the tool face",
      res["op"] == "search" and res["sessions_found"] > 0
      and all("commands" in r for r in res["results"]))
good, why = raises_teaching(lambda: sessions_tool(op="search"), "needs `q`")
check("op='search' without q raises teaching", good, why)
good, why = raises_teaching(lambda: sessions_tool(op="nope"), "search=content search")
check("unknown-op teaching now names search", good, why)

print("\n" + ("ALL PASS" if ok else "FAILURES — fix before commit (fail loud)"))
sys.exit(0 if ok else 1)
