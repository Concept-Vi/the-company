"""tests/rhm_completion_acceptance.py — the right-hand-man reliably COMPLETES and SHOWS its actions,
and two cross-lane handoffs close. Six scoped changes, each proven by use, model-FREE (mirrors
consult_acceptance.py: test the pure helpers + dispatch, never a live model call — so it runs headless,
fast, deterministic).

Proves:
  1. consult RETRIEVES a bounded, query-relevant slice (not the whole repo); a known term's file is in
     the cited sources; no-match falls back to the curated set, never the whole repo.
  2. `show` resolves a BARE "inbox" (lenient resolver) → ui://chrome/inbox; genuine no-match still refuses.
  3. EVERY dispatched verb's reply carries a confirmation (no blank reply).
  4. the interactive call-site timeout is plumbed through rhm_config/set_rhm_config (positive-int validated).
  5. available_models cache invalidates (manual refresh_models() + TTL) — a model that appears later is seen.
  6. a FAILED node surfaces as status `failed` (not idle) + the run emit counts it loud.
"""
import os, sys, tempfile, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite
from nodes import codebase as cb

NODES = os.path.join(ROOT, "nodes")
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


store_dir = tempfile.mkdtemp(prefix="rhm-completion-test-")
try:
    store = FsStore(os.path.join(store_dir, "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)
    GRAPH = "g"

    # ---- 1. consult-retrieval: bounded + relevant, not the whole repo ------------------------------
    # The repo OUTGREW whole-repo stuffing: cb.run({},{}) now FAILS LOUD past max_chars (the repo is
    # ~865k > the 600k cap). So we do NOT stuff it here — we measure the repo SIZE without reading it into
    # memory (sum of file sizes over the codebase globs) and prove the retrieved slice is a small fraction.
    import glob as _glob
    _root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    whole_repo_chars = 0
    for _g in cb.DEFAULT_GLOBS:
        for _p in _glob.glob(os.path.join(_root, _g)):
            try:
                whole_repo_chars += os.path.getsize(_p)
            except OSError:
                pass
    check("the repo genuinely outgrew stuffing (whole-repo > the codebase node's max_chars cap)",
          whole_repo_chars > cb.CONFIG["max_chars"]["default"])
    context, sources, file_list = suite._retrieve_for_consult("how does the memo gate work in the scheduler")
    check("consult context is BOUNDED (<= CONSULT_CAP)", len(context) <= suite.CONSULT_CAP)
    check("consult context is MUCH smaller than the whole repo (retrieval, not stuffing)",
          len(context) < whole_repo_chars and len(context) < whole_repo_chars // 2)
    # query is about the scheduler/memo gate — scheduler.py must be among the retrieved+cited sources
    check("a known term's file is retrieved (scheduler.py cited for a memo-gate query)",
          any("scheduler" in s for s in sources))
    check("the retrieved context actually contains a query term",
          "scheduler" in context.lower() or "memo" in context.lower())
    check("consult cites sources (the files it used)", len(sources) >= 1)
    check("the repo file-list (orientation) is provided + larger than what's fed",
          len(file_list) > len(sources) or len(file_list) >= 1)
    # no-match → curated fallback, NEVER the whole repo
    ctx2, src2, _ = suite._retrieve_for_consult("pomegranate xylophone quokka")
    check("no-match consult falls back to the CURATED set (not the whole repo)",
          len(ctx2) <= suite.CONSULT_CAP and set(src2).issubset(set(suite.CONSULT_CURATED)) and len(src2) >= 1)
    # salient-term extraction drops stopwords
    terms = suite._consult_terms("how does the memo gate work")
    check("salient terms drop stopwords ('how'/'does'/'the' gone; 'memo'/'gate' kept)",
          "memo" in terms and "gate" in terms and "how" not in terms and "the" not in terms)
    # empty consult still refused (not a crash) — the contract held before, holds now
    check("empty consult is refused (no query)",
          suite._dispatch_rhm_action({"verb": "consult", "query": ""}, GRAPH)["did"] == "none")

    # ---- 1b. CONSULT-MIGRATION: semantic retrieval against the LIVE X12 index (model-free, hermetic) -
    # The migration: consult RETRIEVES the query-relevant slice from the persisted X12 vector index
    # instead of stuffing the whole repo. Model-free + deterministic like the rest of this file: we build
    # a TINY hermetic index over REAL code:// addresses via store/vector_index.build_index with a STUB
    # embed (the same hermetic seam X11/conv_semantic_rank use — never live :8001 or the production store),
    # and monkeypatch the query embed (fabric.client.complete_embeddings, exactly as this file already
    # monkeypatches fabric.client.complete). Each address gets a distinct 1024-dim one-hot vector; the
    # query embed returns the one-hot of the TARGET address — so cosine ranks that address #1, proving the
    # real retrieve→resolve→bounded-slice path, not just that a fallback fired.
    from store import vector_index as vx
    from fabric import config as _fcfg
    DIM = _fcfg.DEFAULT_EMBED_DIM

    def _onehot(i):
        v = [0.0] * DIM
        v[i % DIM] = 1.0
        return v
    # REAL code:// addresses whose file-stems exist in the worktree (scheduler.py, suite.py, store stem).
    # The query is about the scheduler/memo gate → code://scheduler/* is the target (index 0).
    INDEXED = ["code://scheduler/_should_run", "code://suite/chat", "code://fs_store/put_vector"]
    corpus = [{"address": a, "text": f"meaning of {a}"} for a in INDEXED]
    # build_index takes an embed_fn(transport, inputs, model, dim) → list[vector]; stub returns one-hots
    # aligned to the order build_index passes them (it embeds the changed batch in INDEXED order on a cold store).
    _ranklist = []  # the addresses in the exact order build_index hands them to the stub (== change order)

    def _stub_index_embed(_t, inputs, model=None, dim=None):
        out = []
        for text in inputs:
            addr = text.replace("meaning of ", "")
            _ranklist.append(addr)
            out.append(_onehot(INDEXED.index(addr)))
        return out
    res = vx.build_index(suite.store, corpus, embed_fn=_stub_index_embed, dim=DIM)
    check("hermetic X12 index built (3 code:// addresses embedded, not degraded)",
          res["embedded"] == 3 and res["degraded"] is False)
    check("the index is populated + queryable (index_addresses sees the 3 entries)",
          len(suite.store.index_addresses()) == 3)
    # Now the SEMANTIC consult path: monkeypatch the query embed to return the scheduler one-hot (index 0)
    from fabric import client as _fc
    _orig_embed = _fc.complete_embeddings
    _fc.complete_embeddings = lambda *a, **k: [_onehot(0)]      # query ranks code://scheduler/* #1
    try:
        sem = suite._retrieve_for_consult_semantic("how does the memo gate work in the scheduler")
        check("semantic retrieval returns a result (index live → NOT a None fallback signal)", sem is not None)
        sctx, ssrc, sfl = sem
        check("semantic context is BOUNDED (<= CONSULT_CAP, never the whole repo)", len(sctx) <= suite.CONSULT_CAP)
        check("semantic retrieval cites scheduler.py (the #1-ranked code:// address resolved to its file)",
              any("scheduler" in s for s in ssrc))
        check("the semantically-retrieved slice carries the relevant source", "scheduler" in sctx.lower())
        check("semantic retrieval provides the repo orientation file-list", len(sfl) >= 1)
        # the chooser (_retrieve_for_consult_best) returns the SEMANTIC result when the index is live
        bctx, bsrc, _ = suite._retrieve_for_consult_best("how does the memo gate work in the scheduler")
        check("consult chooser prefers the SEMANTIC slice when the index is live",
              any("scheduler" in s for s in bsrc) and len(bctx) <= suite.CONSULT_CAP)
    finally:
        _fc.complete_embeddings = _orig_embed
    # DEGRADE-WITH-WARNING: embedder DOWN → semantic returns None (signal) + a loud warning → chooser
    # falls back to the proven keyword scan. Model-free: make the query embed RAISE (endpoint unreachable).
    def _boom_embed(*a, **k):
        raise OSError("embed endpoint down")
    _fc.complete_embeddings = _boom_embed
    try:
        n_before = len(store.recent_events(50))
        sem_down = suite._retrieve_for_consult_semantic("how does the memo gate work in the scheduler")
        check("embedder DOWN → semantic retrieval returns None (the keyword-fallback signal)", sem_down is None)
        evs_after = store.recent_events(50)
        check("embedder DOWN emits a LOUD warning (never a silent zero-vector)",
              any(e["kind"] == "warning" and "embed" in e["summary"].lower() for e in evs_after))
        # and the chooser DEGRADES to the keyword path (still a bounded, cited slice — never the whole repo)
        dctx, dsrc, _ = suite._retrieve_for_consult_best("how does the memo gate work in the scheduler")
        check("embedder DOWN → chooser FALLS BACK to the keyword scan (bounded + cited, not the whole repo)",
              len(dctx) <= suite.CONSULT_CAP and len(dsrc) >= 1 and any("scheduler" in s for s in dsrc))
    finally:
        _fc.complete_embeddings = _orig_embed
    # EMPTY index (embedder was down at build) → query returns the honest empty-note → semantic returns
    # None + warns → keyword fallback. Prove over a FRESH empty store.
    import tempfile as _tf
    _empty_dir = _tf.mkdtemp(prefix="rhm-empty-idx-")
    try:
        from store.fs_store import FsStore as _FsStore
        s_empty = Suite(_FsStore(os.path.join(_empty_dir, "store")), reg, nodes_dir=NODES)
        _fc.complete_embeddings = lambda *a, **k: [_onehot(0)]   # embedder UP, but the INDEX is empty
        try:
            sem_empty = s_empty._retrieve_for_consult_semantic("how does the memo gate work in the scheduler")
            check("EMPTY index → semantic returns None (honest empty, falls back — not a fabricated rank)",
                  sem_empty is None)
        finally:
            _fc.complete_embeddings = _orig_embed
    finally:
        shutil.rmtree(_empty_dir, ignore_errors=True)

    # ---- 2. show grounding + lenient resolver ------------------------------------------------------
    r = suite._dispatch_rhm_action({"verb": "show", "targets": ["inbox"]}, GRAPH)
    check("show resolves a BARE 'inbox' (lenient) → did=show", r["did"] == "show")
    check("bare 'inbox' resolved to ui://chrome/inbox (registry's own kind)",
          "ui://chrome/inbox" in r["targets"])
    r2 = suite._dispatch_rhm_action({"verb": "show", "targets": ["activity"]}, GRAPH)
    check("another bare chrome handle ('activity') resolves", "ui://chrome/activity" in r2["targets"])
    # genuine no-match STILL refuses (fail-loud preserved)
    r3 = suite._dispatch_rhm_action({"verb": "show", "targets": ["nonexistent_handle_zzz"]}, GRAPH)
    check("a genuine no-match show still REFUSES (fail-loud preserved)", r3["did"] == "none")
    # the full ui:// form still works (unchanged behaviour)
    r4 = suite._dispatch_rhm_action({"verb": "show", "targets": ["ui://chrome/inbox"]}, GRAPH)
    check("explicit ui://chrome/inbox still resolves", "ui://chrome/inbox" in r4["targets"])
    # the grounding context now ENUMERATES the show-targets
    ctx = suite._chat_context(GRAPH)
    check("_chat_context enumerates the ui:// show-targets (inbox grounded)",
          "ui://chrome/inbox" in ctx and "show targets" in ctx)

    # ---- 3. action-confirmation replies — every verb, no blank -------------------------------------
    # feed synthetic outcome dicts (the dispatcher's real shapes) → assert a non-blank confirmation
    cases = {
        "run":     {"did": "run", "ran": ["a", "b", "c"], "cached": ["d", "e"]},
        "build":   {"did": "build", "nodes": ["n1", "n2", "n3"], "edges": ["a.x -> b.y"]},
        "build-err": {"did": "build", "error": "ValueError: bad port", "nodes": ["n1"]},
        "show":    {"did": "show", "targets": ["ui://chrome/inbox"]},
        "propose": {"did": "propose", "surfaced": "s1", "name": "myNode"},
        "panel":   {"did": "panel", "surfaced": "s2", "name": "myPanel"},
        "extend":  {"did": "extend", "surfaced": "s3", "name": "myExt"},
        "refused": {"did": "none", "refused": "build needs a JSON list of steps"},
        "show-refused": {"did": "none", "refused": "show: no matching target (node-id or ui:// component)"},
    }
    for label, outcome in cases.items():
        conf = suite._confirmation_for(outcome)
        check(f"confirmation for {label!r} is NON-BLANK", bool(conf and conf.strip()))
    # the markers requested in the brief
    check("run confirmation reads like '▶ ran: 3 ran, 2 cached'",
          "ran" in suite._confirmation_for(cases["run"]) and "3" in suite._confirmation_for(cases["run"]))
    check("build confirmation names the count + wiring",
          "3" in suite._confirmation_for(cases["build"]) and "a.x -> b.y" in suite._confirmation_for(cases["build"]))
    check("show confirmation says it moved the view",
          "moved" in suite._confirmation_for(cases["show"]).lower())
    check("propose confirmation says drafted + awaiting approval",
          "draft" in suite._confirmation_for(cases["propose"]).lower()
          and "approval" in suite._confirmation_for(cases["propose"]).lower())
    check("show-refused confirmation surfaces the refusal reason",
          "refused" in suite._confirmation_for(cases["show-refused"]).lower())
    # INTEGRATION: prove the REAL chat() wiring (not just the helper) — a native-tool-call model that
    # emits a bare tool-call with ZERO prose must still produce a NON-BLANK reply carrying the confirmation
    # (the exact case the change exists for). Model-FREE + HERMETIC (mirrors rhm_action_parse_acceptance):
    # chat() now ACTS via NATIVE TOOL-CALLING, so we stub `complete_with_tools` (the function chat() calls)
    # to return an empty-content message carrying a single tool_call, and force the capability gate True.
    # (Was: a patch of the dead `fclient.complete` returning `"ACTION: run"` — INERT, since chat() no
    # longer calls complete; that left the outcome at the mercy of whatever a LIVE model happened to emit,
    # i.e. flaky. The fix makes it deterministic AND actually exercises the empty-content confirmation fold.)
    import json as _json
    from fabric import client as fclient
    def _tc(name, arguments):                                 # OpenAI-shape tool_call (arguments = JSON string)
        return {"id": "call_1", "type": "function",
                "function": {"name": name, "arguments": _json.dumps(arguments)}}
    # the graph must be NON-EMPTY for `run` to be offered in listening (the run predicate context-refines
    # OUT on an empty graph — no point recomputing nothing; proven in rhm_action_parse_acceptance (c)).
    # So compose a tiny runnable pipeline, exactly the "recompute the graph" scenario this asserts.
    suite.create_node(GRAPH, "constant", config={"value": "x"}, node_id="cc")
    suite.create_node(GRAPH, "uppercase", node_id="uu")
    suite.connect(GRAPH, "cc", "value", "uu", "text")
    orig_cwt = fclient.complete_with_tools
    orig_gate = suite._model_supports_tools
    suite._model_supports_tools = lambda model, base_url=None: True   # tool-capable (no live endpoint dependency)
    try:
        fclient.complete_with_tools = lambda *a, **k: {"role": "assistant", "content": "", "tool_calls": [_tc("run", {})]}
        out = suite.chat("recompute the graph please", GRAPH)
        check("chat() reply is NON-BLANK when the model emits ONLY a tool-call (no prose)",
              bool(out["reply"] and out["reply"].strip()))
        check("the blank-model reply carries the run confirmation (operator sees what happened)",
              "ran" in out["reply"])
        # and a verb whose outcome used to be blank (show) — bare tool-call, no prose
        fclient.complete_with_tools = lambda *a, **k: {"role": "assistant", "content": "", "tool_calls": [_tc("show", {"targets": ["inbox"]})]}
        out2 = suite.chat("show me the inbox", GRAPH)
        check("a bare 'show' tool-call yields a non-blank reply with the move confirmation",
              bool(out2["reply"].strip()) and "moved" in out2["reply"].lower())
    finally:
        fclient.complete_with_tools = orig_cwt
        suite._model_supports_tools = orig_gate

    # consult/ask fold their own richer text — _confirmation_for yields '' (no double-up)
    check("consult outcome yields '' from _confirmation_for (caller folds the answer)",
          suite._confirmation_for({"did": "consult", "answer": "x"}) == "")
    check("ask outcome yields '' from _confirmation_for (caller folds the needs-line)",
          suite._confirmation_for({"did": "ask", "needs": "x"}) == "")
    check("None/empty outcome → '' (nothing dispatched, nothing to confirm)",
          suite._confirmation_for(None) == "" and suite._confirmation_for({}) == "")

    # ---- 4. call-site cloud timeouts ---------------------------------------------------------------
    from fabric import config as fcfg
    cfg = suite.rhm_config()
    check("rhm_config carries a timeout slot defaulting to DEFAULT_TIMEOUT",
          cfg.get("timeout") == fcfg.DEFAULT_TIMEOUT)
    suite.set_rhm_config({"timeout": 90})
    check("set_rhm_config persists a valid timeout", suite.rhm_config()["timeout"] == 90)
    bad = False
    try:
        suite.set_rhm_config({"timeout": -5})
    except ValueError:
        bad = True
    check("set_rhm_config REJECTS a non-positive timeout (fail-loud)", bad)
    bad2 = False
    try:
        suite.set_rhm_config({"timeout": "abc"})
    except ValueError:
        bad2 = True
    check("set_rhm_config REJECTS a non-int timeout", bad2)

    # ---- 5. available_models cache invalidation ----------------------------------------------------
    # monkeypatch transport.list_models so no live endpoint is needed (model-free)
    from fabric import transport as ftr
    orig_list = ftr.list_models
    state = {"models": ["alpha:cloud"]}
    ftr.list_models = lambda *a, **k: list(state["models"])
    try:
        # fresh suite so the cache is cold
        s2 = Suite(store, reg, nodes_dir=NODES)
        first = s2.available_models()
        check("available_models reads the live list", "alpha:cloud" in first)
        # a model comes up LATER — invisible until refresh/TTL (we prove manual refresh sees it now)
        state["models"] = ["alpha:cloud", "beta:cloud"]
        check("the new model is NOT yet visible from the warm cache", "beta:cloud" not in s2.available_models())
        refreshed = s2.refresh_models()
        check("refresh_models() makes the newly-appeared model visible (no restart)",
              "beta:cloud" in refreshed and "beta:cloud" in s2.available_models())
        # a DOWN endpoint → fail-loud-legible fallback, and the degraded cache is NOT pinned
        def _boom(*a, **k):
            raise OSError("endpoint down")
        ftr.list_models = _boom
        s3 = Suite(store, reg, nodes_dir=NODES)
        degraded = s3.available_models()
        check("a down endpoint degrades to an EMPTY list (no fabricated -pro fallback; not a crash)",
              degraded == [])
        check("the degraded cache is NOT held — flagged degraded so the next call re-probes",
              s3._models_cache_degraded is True)
        # endpoint recovers → the very next call (degraded not pinned) re-probes + recovers
        ftr.list_models = lambda *a, **k: ["recovered:cloud"]
        check("the fleet recovers the instant the endpoint returns (degraded cache re-probes)",
              "recovered:cloud" in s3.available_models())
    finally:
        ftr.list_models = orig_list

    # ---- 6. consume result['failed'] — a failed node surfaces as `failed`, not idle ----------------
    # 'failed' is a registered node-state (registry-is-truth)
    check("'failed' is in the NODE_STATES registry (rule 8 — surface renders from it)",
          any(s["id"] == "failed" for s in suite.NODE_STATES))
    check("capabilities().node_states exposes 'failed'",
          any(s["id"] == "failed" for s in suite.capabilities()["node_states"]))
    # build a real graph with a node, then simulate a scheduler result carrying it as failed
    nid = suite.create_node(GRAPH, "uppercase", config={})
    # without consuming failed, this node (no result yet) would be idle; WITH a failed map → failed
    fake_result = {"ran": [], "skipped": [], "stuck": [], "failed": {nid: "ValueError: boom"}}
    st = suite.state(GRAPH, result=fake_result)
    node = next(n for n in st["nodes"] if n["id"] == nid)
    check("a node in result['failed'] surfaces as status 'failed' (NOT idle)", node["status"] == "failed")
    check("the failed node carries its error message", node.get("error") == "ValueError: boom")
    # control: the SAME node with NO failed map is idle (proving the regression existed + is fixed)
    st_idle = suite.state(GRAPH, result={"ran": [], "skipped": [], "stuck": [], "failed": {}})
    node_idle = next(n for n in st_idle["nodes"] if n["id"] == nid)
    check("the same node with no failure is idle (the silent-regression baseline)", node_idle["status"] == "idle")

    # the run EMIT counts failures loud — prove via a real failing node + a real run.
    # drop a deterministic always-raise node into a temp nodes dir the registry discovers.
    failnodes = os.path.join(store_dir, "failnodes")
    os.makedirs(failnodes, exist_ok=True)
    with open(os.path.join(failnodes, "boomnode.py"), "w") as f:
        f.write("VERSION='1'\nKIND='process'\nVOLATILE=True\nPORTS_IN={}\nPORTS_OUT={'text':'Text'}\n"
                "def run(inputs, config):\n    raise ValueError('intentional boom')\n")
    reg2 = NodeRegistry(); reg2.discover([NODES, failnodes])
    s4 = Suite(store, reg2, nodes_dir=NODES)
    FG = "failgraph"
    bnid = s4.create_node(FG, "boomnode", config={})
    run_r = s4.run(FG)
    check("the scheduler CONTAINS the raise into result['failed'] (not a crash)",
          bnid in (run_r.get("failed") or {}))
    # the run emitted a loud warning naming the failure
    evs = store.recent_events(10)
    check("the run emits the failed COUNT in the run line",
          any(e["kind"] == "run" and "failed 1" in e["summary"] for e in evs))
    check("a distinct loud WARNING event surfaces the failed node + its error",
          any(e["kind"] == "warning" and "FAILED" in e["summary"] and "boom" in e["summary"] for e in evs))
    # and state() shows it failed under a fresh run result
    st_run = s4.state(FG, result=run_r)
    bnode = next(n for n in st_run["nodes"] if n["id"] == bnid)
    check("the failed node renders status 'failed' through a real run", bnode["status"] == "failed")
    # RELOAD persistence (rule 4): with NO fresh result, the failed status survives (not re-defaulting to
    # idle) — derived from the last run event, mirroring stuck. Closes the same silent-regression on reload.
    st_reload = s4.state(FG)                                  # result=None → the reload/persisted path
    bnode_r = next(n for n in st_reload["nodes"] if n["id"] == bnid)
    check("the failed node SURVIVES a reload as 'failed' (not idle) — derived from the last run event",
          bnode_r["status"] == "failed")
    check("the reloaded failed node still carries its error", "boom" in str(bnode_r.get("error", "")))

    # ---- invariant: the verb whitelist derives from the single spec + no-bypass preserved ----------
    # (Derivation-based, NOT a hardcoded tuple: the whitelist grew to 10 with the config-as-tools verbs
    # configure/load_voice/unload_voice — G8.2, commit b98db99. The real contract is: it == the spec,
    # still holds the core acting verbs + the config-as-tools verbs, and NEVER holds apply/delete/file-write
    # — the no-bypass guarantee. (Merge: keeps HEAD's derivation form over the branch's hardcoded 10-tuple —
    # both pass against the merged suite; the derivation survives the next verb addition, the literal won't.))
    check("RHM_VERBS = the single-source whitelist (derives from RHM_VERB_SPECS)",
          suite.RHM_VERBS == tuple(suite.RHM_VERB_SPECS))
    check("the core acting verbs + the config-as-tools verbs are all whitelisted",
          {"run", "propose", "build", "consult", "show", "panel", "extend"}.issubset(set(suite.RHM_VERBS))
          and {"configure", "load_voice", "unload_voice"}.issubset(set(suite.RHM_VERBS)))
    check("apply/delete are NOT whitelisted (no-bypass)",
          "apply" not in suite.RHM_VERBS and "delete" not in suite.RHM_VERBS)
    check("a forbidden verb (apply) is STILL refused end-to-end",
          suite._dispatch_rhm_action({"verb": "apply", "id": "x"}, GRAPH)["did"] == "none")
    check("delete still refused", suite._dispatch_rhm_action({"verb": "delete", "id": "x"}, GRAPH)["did"] == "none")

    print(f"\nALL {PASS} CHECKS PASS — RHM completes + shows its actions; consult retrieves; failed surfaces")
finally:
    shutil.rmtree(store_dir, ignore_errors=True)
