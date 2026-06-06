"""RED→GREEN for symbols.py — the code-symbol REVERSE index (the code:// branch of the
universal coordinate; Block 17-18). Run:
    python3 test_symbols.py
Real behaviour on small inline fixtures (no ~/company access, no mocks): given code: refs
in several FORMS — path:line, path:symbol, file-only, Suite.verb, /api route, glob/dir —
the indexer resolves each (reusing refcheck's resolution seam), classifies its KIND
(def|class|route|const|file-only), records whether it currently resolves, and — the NEW
information beyond refcheck — collapses every ref that lands on the SAME symbol into ONE
entry whose `referenced_by` lists EVERY corpus owner pointing at it (the reverse index).
A symbol named in a path:symbol ref that is ABSENT from the file resolves:false — that is
the drift signal. Fails LOUD on a malformed registry (reuses refcheck.collect_refs)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import symbols  # RED until symbols.py exists

# --- a fake python source: line N (1-based) = PY[N-1] ---
PY = [
    "class Suite:",                       # 1   <- a class
    "    def chat(self, msg):",            # 2   <- def, referenced by two owners (reverse merge)
    "        return self._reply(msg)",     # 3
    "    def resolve_surfaced(self):",     # 4   <- def, id stem from resolved file
    "        return 'ok'",                 # 5
    "    def run(self):",                  # 6   <- def, referenced by many engine owners
    "        return self._tick()",         # 7
]
TSX = [
    "export function Toolbar() {",        # 1
    "  const DRAG_CONN = 7;",              # 2   <- a const (tsx) — kind=const
    "  return <div/>;",                    # 3
    "}",                                   # 4
    "export default function App() {",     # 5   <- the form _all_defs MISSES (export default)
    "  return <Toolbar/>;",                # 6
]
BRIDGE = ['if path == "/api/run":', 'def do_POST(self): pass']


def fake_resolver(path):
    """Stand-in for the on-disk resolver: returns (repo-relative-path, lines) or None.
    Both 'suite.py' and 'runtime/suite.py' resolve to the SAME repo file — so refs in
    either form must collapse to ONE symbol id (the unification the reverse index needs)."""
    if path.endswith("suite.py"):
        return ("runtime/suite.py", PY)
    if path.endswith("App.tsx"):
        return ("canvas/app/src/App.tsx", TSX)
    if path.endswith("bridge.py"):
        return ("runtime/bridge.py", BRIDGE)
    return None


def run():
    # ---- 1) index_ref: each FORM → (file, symbol, kind, resolves) -------------------
    # path:symbol — names a def present in the file → resolves, kind=def.
    r = symbols.index_ref("runtime/suite.py:run", resolve=fake_resolver)
    assert r["symbol"] == "run" and r["kind"] == "def" and r["resolves"] is True, r
    assert r["file"] == "runtime/suite.py", f"keys off the RESOLVED file: {r}"

    # path:symbol naming a CLASS present in the file → kind=class.
    rc = symbols.index_ref("suite.py:Suite", resolve=fake_resolver)
    assert rc["symbol"] == "Suite" and rc["kind"] == "class" and rc["resolves"] is True, rc

    # path:symbol naming a symbol ABSENT from the file → resolves:false (the DRIFT signal).
    rd = symbols.index_ref("runtime/suite.py:ghost_method", resolve=fake_resolver)
    assert rd["symbol"] == "ghost_method" and rd["resolves"] is False, f"absent symbol -> drift: {rd}"

    # path:line — symbol = the ENCLOSING def (nearest preceding), kind from that def line.
    rl = symbols.index_ref("suite.py:3", resolve=fake_resolver)
    assert rl["symbol"] == "chat" and rl["kind"] == "def" and rl["resolves"] is True, f"line 3 in chat: {rl}"

    # path:line past EOF → does NOT resolve.
    re = symbols.index_ref("suite.py:999", resolve=fake_resolver)
    assert re["resolves"] is False, f"past-EOF -> resolves:false: {re}"

    # tsx const — kind=const (DRAG_CONN-style).
    rk = symbols.index_ref("canvas/app/src/App.tsx:DRAG_CONN", resolve=fake_resolver)
    assert rk["symbol"] == "DRAG_CONN" and rk["kind"] == "const", f"tsx const: {rk}"

    # tsx 'export default function App()' — the form refcheck's _all_defs misses; symbols.py's
    # precise per-symbol lookup MUST still resolve it (else a real symbol reads as false drift).
    rdef = symbols.index_ref("canvas/app/src/App.tsx:App", resolve=fake_resolver)
    assert rdef["symbol"] == "App" and rdef["kind"] == "def" and rdef["resolves"] is True, \
        f"export default function App() must resolve: {rdef}"

    # a NON-code-extension file that the resolver can't place (a .css selector ref) is NOT a code
    # symbol → index_ref returns None (→ caller lists it under not_indexable, never as drift).
    assert symbols.index_ref("design-system.css .tabbar", resolve=fake_resolver) is None, \
        "non-code-ext unresolvable ref -> not a symbol entry"
    # a CODE-extension file that doesn't resolve IS genuine drift (file churned away).
    rmiss = symbols.index_ref("runtime/gone.py:vanished", resolve=fake_resolver)
    assert rmiss is not None and rmiss["resolves"] is False, f"missing code file -> drift: {rmiss}"

    # file-only — no symbol, kind=file-only, resolves iff file found.
    rf = symbols.index_ref("nodes/embed.py", resolve=fake_resolver)
    assert rf["kind"] == "file-only" and rf["symbol"] is None, rf
    rf2 = symbols.index_ref("nodes/missing.py", resolve=fake_resolver)
    assert rf2["resolves"] is False, f"missing file-only -> resolves:false: {rf2}"

    # /api route — kind=route, resolves iff literal in bridge.
    ra = symbols.index_ref("/api/run", resolve=fake_resolver)
    assert ra["kind"] == "route" and ra["resolves"] is True, ra
    ra2 = symbols.index_ref("/api/ghost", resolve=fake_resolver)
    assert ra2["resolves"] is False, f"absent route -> drift: {ra2}"

    # Suite.verb — grep bridge for the verb; kind=route (api-face symbol).
    rs = symbols.index_ref("Suite.do_POST", resolve=fake_resolver)
    assert rs["resolves"] is True and rs["symbol"] == "do_POST", rs

    # glob / dir — NOT indexable as a symbol → returns None (reported, never silently dropped).
    assert symbols.index_ref("nodes/*.py", resolve=fake_resolver) is None, "glob -> not a symbol entry"
    assert symbols.index_ref("voice/", resolve=fake_resolver) is None, "dir -> not a symbol entry"

    # ---- 2) symbol_id: stable, keyed off the resolved file stem + symbol --------------
    assert symbols.symbol_id("runtime/suite.py", "resolve_surfaced") == "code://suite/resolve_surfaced", \
        symbols.symbol_id("runtime/suite.py", "resolve_surfaced")
    # file-only id has no symbol segment.
    assert symbols.symbol_id("nodes/embed.py", None) == "code://embed", \
        symbols.symbol_id("nodes/embed.py", None)

    # ---- 3) THE REVERSE INDEX: many owners on one symbol collapse to ONE entry --------
    # Two register features reference suite.py:chat (RHM-chat + RHM-decide both → 'chat'),
    # bare 'suite.py' and qualified 'runtime/suite.py' unify to the SAME file. The reverse
    # index must produce ONE entry for code://suite/chat with BOTH owners in referenced_by.
    items = [
        {"raw": "runtime/suite.py:chat", "source": "register", "owner": "RHM-chat", "label": ""},
        {"raw": "suite.py:chat",         "source": "register", "owner": "RHM-decide", "label": ""},
        {"raw": "runtime/suite.py:run",  "source": "register", "owner": "ENG-resolve", "label": ""},
        {"raw": "scheduler.py:run / runtime/suite.py:run", "source": "register",
         "owner": "ENG-force", "label": ""},  # compound: second sub-ref → suite/run
        {"raw": "canvas/app/src/App.tsx (toolbar)", "source": "addresses",
         "owner": "ui://toolbar", "label": "F1"},
    ]
    reg = symbols.build_index(items, resolve=fake_resolver)
    chat = reg["code://suite/chat"]
    assert sorted(chat["referenced_by"]) == ["RHM-chat", "RHM-decide"], \
        f"two owners collapse to one entry: {chat}"
    assert chat["file"] == "runtime/suite.py" and chat["symbol"] == "chat" and chat["kind"] == "def"
    run_ent = reg["code://suite/run"]
    assert sorted(run_ent["referenced_by"]) == ["ENG-force", "ENG-resolve"], \
        f"compound sub-ref + plain ref both land on run: {run_ent}"
    # the addresses owner (ui://) is preserved verbatim as a reference source. 'App.tsx (toolbar)'
    # is a file-only ref with a parenthetical annotation (NOT a :symbol) → file-only id code://App.
    tb = reg["code://App"]
    assert "ui://toolbar" in tb["referenced_by"] and tb["kind"] == "file-only", f"ui:// owner recorded: {tb}"

    # shared = referenced by 2+ owners.
    shared = symbols.shared_symbols(reg)
    assert "code://suite/chat" in shared and "code://suite/run" in shared, shared

    # ---- 4) malformed registry fails LOUD (reuses refcheck.collect_refs) --------------
    import refcheck
    try:
        refcheck.collect_refs({"features": "nope"}, {})
        assert False, "malformed register must raise"
    except ValueError:
        pass

    # ---- 5) build_registry assembles the emitted doc shape ----------------------------
    doc = symbols.build_registry({"features": [{"id": "RHM-chat", "code": "runtime/suite.py:chat"}]},
                                 {"ui://x": {"code": "runtime/suite.py:chat", "represents": "F1"}},
                                 resolve=fake_resolver)
    assert "_what" in doc and "code://" in doc["_what"], "carries the code:// branch note"
    assert doc["symbols"]["code://suite/chat"]["referenced_by"] and "summary" in doc, doc

    # ---- 6) X11: the SEMANTIC edge `semantically_nearest[]` beside `referenced_by[]` ---------
    # A deterministic, hermetic stand-in for the BGE-M3 embedder (no :8001 access, like the
    # resolver seam). representative_text(sid, entry, labels) carries the symbol's MEANING (name +
    # kind + file stem + the owners' represents/label text); the fake maps a text to a vector by
    # the CONCEPT WORDS it contains, so conceptually-similar texts get near-parallel vectors and
    # unrelated ones get near-orthogonal vectors — exactly the semantic ordering the live BGE-M3
    # gives (the embeddings_acceptance proof: cat≈feline > cat/stocks), without any network.
    CONCEPTS = ["chat", "voice", "vector", "embedding", "schedule", "tick", "finance", "money"]

    def fake_embed(text):
        t = text.lower()
        # one axis per concept word present; a tiny constant so no vector is all-zero (cosine-safe).
        return [1.0 if c in t else 0.0 for c in CONCEPTS] + [0.01]

    # Two conceptually-CLOSE entries (both about chat/voice) + one UNRELATED (finance/money).
    sem_items = [
        {"raw": "runtime/suite.py:chat", "source": "register", "owner": "RHM-chat",
         "label": "the conversational voice chat reply"},
        {"raw": "runtime/suite.py:run", "source": "register", "owner": "RHM-decide",
         "label": "the conversational voice chat turn"},   # close to chat: shares 'chat'/'voice'
        {"raw": "scheduler.py:run", "source": "register", "owner": "BILLING",
         "label": "finance money billing total"},          # unrelated concept
    ]
    sem_labels = {}
    sem_reg = symbols.build_index(sem_items, resolve=fake_resolver, labels_out=sem_labels)
    # representative_text pulls the owners' label/represents text (the human meaning).
    rt_chat = symbols.representative_text("code://suite/chat", sem_reg["code://suite/chat"],
                                          sem_labels.get("code://suite/chat"))
    assert "chat" in rt_chat and "voice" in rt_chat, f"representative text carries meaning: {rt_chat}"

    # structural SNAPSHOT before attaching — to prove byte-for-byte preservation after.
    import copy
    structural_before = copy.deepcopy(sem_reg)

    # --- embedder UP: each entry gains semantically_nearest[] of code:// ids -----------------
    symbols.attach_semantic_edges(sem_reg, labels=sem_labels, embed_fn=fake_embed, k=2)
    for sid, e in sem_reg.items():
        assert "semantically_nearest" in e, f"{sid} gained semantically_nearest[]: {e}"
        for n in e["semantically_nearest"]:
            assert n["id"].startswith("code://") and n["id"] != sid, f"nearest is an OTHER code:// id: {n}"
        # the structural fields are UNCHANGED (preserve — byte-for-byte).
        for k in ("file", "symbol", "kind", "resolves", "referenced_by"):
            assert e[k] == structural_before[sid][k], f"structural field {k} changed on {sid}!"

    # SEMANTIC ORDERING (the heart of X11, like embeddings_acceptance's cat≈feline>cat/stocks):
    # for the chat entry, the OTHER chat/voice symbol must rank ABOVE the unrelated finance one.
    chat_near = sem_reg["code://suite/chat"]["semantically_nearest"]
    chat_run = sem_reg["code://suite/run"]      # the conceptually-close sibling (chat/voice)
    ordering = {n["id"]: n["score"] for n in chat_near}
    assert ordering["code://suite/run"] > ordering["code://scheduler/run"], \
        f"conceptually-similar (chat↔chat) nearer than unrelated (chat↔finance): {ordering}"

    # --- embedder DOWN: degrade-with-warning, field ABSENT, structural index INTACT, NO crash --
    class _Down(Exception):
        pass

    def down_embed(text):
        raise _Down("connection refused :8001 (embedder down)")

    down_reg = symbols.build_index(sem_items, resolve=fake_resolver, labels_out={})
    warnings = []
    out = symbols.attach_semantic_edges(down_reg, labels=sem_labels, embed_fn=down_embed, k=2,
                                        warn=warnings.append)
    assert out is down_reg, "degrade returns the (structural) reg, does not crash"
    assert all("semantically_nearest" not in e for e in down_reg.values()), \
        "embedder-down: the semantic field is SKIPPED ENTIRELY (no fabricated nearest)"
    for sid, e in down_reg.items():  # structural part still fully built + valid
        assert e["resolves"] in (True, False) and isinstance(e["referenced_by"], list), e
    assert warnings and any("embedder unreachable" in w.lower() or "embed failed" in w.lower()
                            for w in warnings), f"a LOUD warning was emitted on degrade: {warnings}"

    # build_registry end-to-end with the embedder down → valid doc, semantic_edges == 0 in summary.
    doc_down = symbols.build_registry(
        {"features": [{"id": "RHM-chat", "code": "runtime/suite.py:chat"}]},
        {"ui://x": {"code": "runtime/suite.py:run", "represents": "F1"}},
        resolve=fake_resolver, embed_fn=down_embed, warn=lambda m: None)
    symbols._validate(doc_down)  # still VALID with the semantic field absent
    assert doc_down["summary"]["semantic_edges"] == 0, "down → 0 semantic edges, structural doc valid"

    # build_registry end-to-end with the embedder UP → semantic_edges populated.
    doc_up = symbols.build_registry(
        {"features": [{"id": "RHM-chat", "code": "runtime/suite.py:chat"},
                      {"id": "RHM-decide", "code": "runtime/suite.py:run"}]},
        {"ui://x": {"code": "scheduler.py:run", "represents": "finance money billing"}},
        resolve=fake_resolver, embed_fn=fake_embed, k=2, warn=lambda m: None)
    symbols._validate(doc_up)
    assert doc_up["summary"]["semantic_edges"] == len(doc_up["symbols"]) > 0, \
        f"up → every entry has a semantic edge: {doc_up['summary']}"

    print("PASS test_symbols (form→symbol/kind/resolves + id stability + REVERSE merge "
          "[many owners→one entry, bare/qualified unify, compound split] + shared + "
          "absent-symbol drift + glob/dir not-indexed + malformed raises + X11 semantic edges "
          "[up: nearest code:// ids + semantic ordering + structural unchanged; "
          "down: degrade-with-warning, field absent, structural intact, no crash])")


run()
