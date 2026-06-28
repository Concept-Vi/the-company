"""tests/page_face_acceptance.py — page-as-a-face (the strong artifact) + its security posture.

Proves, BY MECHANISM (pure render_page — no socket; a temp store + temp bindings overlay — no repo
writes), that:
  1. ADDITIVE CONTRACT — UnionAddressRecord carries an OPTIONAL `page` field (None default; an address
     with no page still validates); SCHEMA_VER bumped to 3; from_corpus reads `page`.
  2. ATTACH→RENDER round-trip — attach_page stores the HTML (cas://) + binds it; render_page serves it.
  3. NO-SCRIPT CSP — every served page carries the no-script / connect-src 'none' CSP (the escalation +
     XSS mitigation by construction) + nosniff.
  4. SCHEME ALLOW-LIST — a page source outside cas://|blob:// is REFUSED 403 fail-loud.
  5. FAIL-LOUD — an address with no page → 404 (never a silent empty).
  6. SEPARATE ORIGIN — the page port is NOT the bridge control plane (8770) / supervisor (8771).
  7. ADDRESS VALIDATION + empty-html — attach_page refuses a bad address / empty html.

LAWS proven: additive (optional page field) · no silent failures (404/403 loud) · the floor (served
read-only under a no-script CSP — no execution) · content-addressed sources only · separate-origin.
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from contracts.ui_info import UnionAddressRecord, SCHEMA_VER                # noqa: E402
from store.fs_store import FsStore                                         # noqa: E402
from runtime.registry import NodeRegistry                                  # noqa: E402
from runtime.suite import Suite                                            # noqa: E402
from runtime import page_face as pf                                        # noqa: E402

PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


def raises(label, exc, fn):
    try:
        fn()
    except exc:
        check(label, True)
        return
    check(label, False)


ADDR = "ui://inbox/build-review"
HTML = "<!doctype html><html><head><title>T</title></head><body><h1>Hello</h1><p>A page.</p></body></html>"

suite = Suite(FsStore(tempfile.mkdtemp(prefix="pf-store-")),
              NodeRegistry().discover([os.path.join(ROOT, "nodes")]), nodes_dir=os.path.join(ROOT, "nodes"))
binds = os.path.join(tempfile.mkdtemp(prefix="pf-binds-"), "page_bindings.json")

# 1 · ADDITIVE CONTRACT
check("SCHEMA_VER bumped to 3 (page-as-a-face)", SCHEMA_VER == 3)
r_nopage = UnionAddressRecord(address=ADDR, kind="chrome", region="inbox")
check("UnionAddressRecord validates with NO page (optional, None default)", r_nopage.page is None)
r_page = UnionAddressRecord.from_corpus(ADDR, {"region": "inbox", "page": {"source": "cas://b2:x"}})
check("from_corpus reads an optional `page` field", r_page.page == {"source": "cas://b2:x"})

# 2 · ATTACH→RENDER round-trip
binding = pf.attach_page(suite, ADDR, HTML, title="Build review", bindings_path=binds)
check("attach_page stores the html at a cas:// source + binds it", binding["source"].startswith("cas://"))
check("page_for returns the binding for the address", pf.page_for(suite, ADDR, bindings_path=binds)["source"] == binding["source"])
status, headers, body = pf.render_page(suite, ADDR, bindings_path=binds)
check("render_page serves the bound page (200) with the exact stored HTML", status == 200 and body == HTML)
check("served Content-Type is text/html", headers["Content-Type"].startswith("text/html"))

# 3 · NO-SCRIPT CSP (the escalation/XSS mitigation by construction)
csp = headers["Content-Security-Policy"]
check("CSP has NO script-src (no JS executes on a served page)", "script-src" not in csp)
check("CSP forbids any network call FROM a page (connect via default-src 'none')", "default-src 'none'" in csp)
check("served page carries X-Content-Type-Options: nosniff", headers.get("X-Content-Type-Options") == "nosniff")

# 4 · SCHEME ALLOW-LIST (a non content-addressed source is refused)
import json as _json                                                       # noqa: E402
bad = os.path.join(tempfile.mkdtemp(prefix="pf-bad-"), "page_bindings.json")
with open(bad, "w") as f:
    _json.dump({ADDR: {"source": "run://x/y/z#run=1", "content_type": "text/html"}}, f)
bstatus, bheaders, bbody = pf.render_page(suite, ADDR, bindings_path=bad)
check("a non-cas/blob page source is REFUSED 403 fail-loud", bstatus == 403 and "not allowed" in bbody)
check("even the 403 carries the no-script CSP (defense in depth)", "default-src 'none'" in bheaders["Content-Security-Policy"])

# 5 · FAIL-LOUD (no binding → 404)
nstatus, _nh, nbody = pf.render_page(suite, "ui://inbox/no-such", bindings_path=binds)
check("an address with no page → 404 (never a silent empty)", nstatus == 404 and "no page bound" in nbody)

# 6 · SEPARATE ORIGIN (page port is not the control plane / supervisor)
check("the page port is a SEPARATE origin (not bridge 8770 / supervisor 8771)",
      pf.PAGE_PORT not in (8770, 8771))

# 7 · ADDRESS VALIDATION + empty-html
raises("attach_page REFUSES a string with no scheme (not an address)", pf.PageFaceError,
       lambda: pf.attach_page(suite, "not-an-address", HTML, bindings_path=binds))
raises("attach_page REFUSES an unknown scheme (registry-is-truth)", pf.PageFaceError,
       lambda: pf.attach_page(suite, "bogus://x", HTML, bindings_path=binds))
raises("attach_page REFUSES empty html (never bind an empty page)", pf.PageFaceError,
       lambda: pf.attach_page(suite, ADDR, "   ", bindings_path=binds))

# 8 · A PAGE IS THE FACE OF *ANY* ADDRESSED THING (not just UI) — the generalization
SKILL_ADDR = "skill://summarize"
b2 = os.path.join(tempfile.mkdtemp(prefix="pf-any-"), "page_bindings.json")
pf.attach_page(suite, SKILL_ADDR, "<!doctype html><h1>Summarize — the skill</h1>", title="Summarize", bindings_path=b2)
st8, _h8, body8 = pf.render_page(suite, SKILL_ADDR, bindings_path=b2)
check("a page attaches to a NON-ui address (skill://) — a page is the face of ANY addressed thing",
      st8 == 200 and "Summarize — the skill" in body8)
check("list_pages reports the bound address(es)",
      any(r["address"] == SKILL_ADDR for r in pf.list_pages(suite, bindings_path=b2)))

print(f"\nPASS — {PASS} checks")
