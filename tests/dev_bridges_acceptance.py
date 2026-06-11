"""dev_bridges_acceptance — the TEETH for lane L-④-dev (Capability Fabric ④ DEV-BRIDGES).

Proves the ④ handlers (runtime/capability_handlers/dev_bridges.py) + the MCP face
(mcp_face/tools/dev_bridges.py) BY USE against STUBS — the lead-only law: NO real claude -p, NO real
bridge-session spawn, NO model load, NO real git commit. The cmd-builders/argv + the intent/job shapes
are asserted; anything needing a REAL bridge round-trip is marked live-verify-pending (lead), never live.

What this proves, all fail-loud:
  1. each handler validates op ∈ {list,get,act} + its acts, fails LOUD (teaching) on unknown — no silent no-op.
  2. dev.git → R3: reads route to the config_writer /git read; writes route to /git with consent passed
     through; the structured argv (run=False preview) is built right; injection-resistance (metachars stay
     one argv element); a write WITHOUT consent surfaces the actor's pending-proposal (consent-not-lockdown).
  3. dev.code_intel / dev.computer_use → R1-prime: an act builds a durable bridge-session INTENT (prose
     result, return_shape=None, a watch cursor); the host/rail BOUNDARY (browser/computer not-WSL) is
     REFUSED LOUD, never green-painted; the spawn-consent is passed through (the supervisor gate).
  4. dev.code_review → R2: an act writes a WIRE-JOB intent (a code_review.job event) + a job-id + watch
     cursor; the handler NEVER spawns claude -p; get folds its own surfaced jobs.
  5. dev.ci → R3: scaffold builds a .github/workflows/<name>.yml write request; traversal in `name`
     refused LOUD; get reads an existing file with honest absence.
  6. DRY (one-handler-two-faces, §3.3): the MCP face tool returns the BYTE-IDENTICAL dict the handler
     returns for the same params — proven on a read op (no side effects) for each resource.
  7. the floor: nothing here spawns/shells; the R3 calls go through a STUB config_writer HTTP server
     (so the argv/consent contract is proven without a real git/claude); fail-loud when the actor is down.

Run: ./.venv/bin/python tests/dev_bridges_acceptance.py
"""
import json
import os
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from runtime import capability_handlers as ch
from runtime.capability_handlers import dev_bridges as db

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


def raises(fn, exc=Exception, want_substr=None):
    try:
        fn()
        return False
    except exc as e:
        return (want_substr in str(e)) if want_substr else True
    except Exception:
        return False


# ─────────────────────────── stubs (lead-only: no real claude/git/spawn) ───────────────────
class StubStore:
    """A minimal store: cas put/get + an append-only event log with monotonic seq (the FsStore contract
    the handlers use). No fsync/locks needed for a single-threaded unit test."""

    def __init__(self):
        self._cas = {}
        self._events = []
        self._n = 0

    def put_content(self, data):
        key = "cas-%d" % len(self._cas)
        self._cas[key] = data
        return key

    def get_content(self, cas):
        return self._cas[cas]

    def append_event(self, event):
        rec = {"seq": self._n, **event}
        self._n += 1
        self._events.append(rec)
        return rec

    def events_since(self, seq):
        return [e for e in self._events if e["seq"] > seq]


class StubSuite:
    def __init__(self):
        self.store = StubStore()


class _StubCWHandler(BaseHTTPRequestHandler):
    """A stub config_writer: echoes the request so the handler's argv/consent contract is provable WITHOUT
    a real git/claude. /git returns a fake-success shape (incl. a sha for commit) when consent is present;
    a pending-proposal when a write lacks consent (the consent-not-lockdown beat the real service emits)."""

    def log_message(self, *a):
        pass

    def _send(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        body = json.loads(self.rfile.read(length) or b"{}") if length else {}
        act = body.get("act", "")
        consent = bool(body.get("consent"))
        run = body.get("run", True)
        # a WRITE without consent → the real service's pending-proposal receipt (consent-not-lockdown)
        is_write = act in ("dev.git:commit", "dev.git:open-pr", "dev.git:worktree-add",
                           "dev.git:worktree-remove", "dev.ci:scaffold")
        if is_write and not consent:
            self._send(200, {"ok": False, "status": "pending-consent", "consent_class": "git-write",
                             "act": act, "echo_run": run})
            return
        if not run:
            # the preview path the real service honours — echo a plausible argv
            self._send(200, {"ok": True, "act": act, "argv": ["git"] + (body.get("args") or []),
                             "would_run": True, "consented": consent})
            return
        out = {"ok": True, "act": act, "exit": 0, "stdout": "stub", "consented": consent}
        if act == "dev.git:commit":
            out["sha"] = "deadbeef"
        self._send(200, out)


def _start_stub_cw():
    srv = ThreadingHTTPServer(("127.0.0.1", 0), _StubCWHandler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    port = srv.server_address[1]
    os.environ["COMPANY_CONFIG_WRITER_PORT"] = str(port)
    return srv, port


print("=== dev_bridges_acceptance — ④ DEV-BRIDGES handlers + face, by USE against stubs (L-④-dev) ===")

# ── 1 · op/act validation + fail-loud ───────────────────────────────────────────────────────────────
print("\n[1] op/act validation fails LOUD (no silent no-op)")
su = StubSuite()
check("dev.git unknown op → ValueError", raises(lambda: db.git(su, "frobnicate"), ValueError, "unknown op"))
check("dev.git get with a WRITE act → teaching ValueError",
      raises(lambda: db.git(su, "get", act="commit"), ValueError, "not a git READ"))
check("dev.git act with a READ act → teaching ValueError",
      raises(lambda: db.git(su, "act", act="status"), ValueError, "not a git WRITE"))
check("dev.code_intel unknown act → ValueError",
      raises(lambda: db.code_intel(su, "act", act="nope", target="x"), ValueError, "unknown"))
check("dev.code_intel act without target → ValueError",
      raises(lambda: db.code_intel(su, "act", act="definition", target=""), ValueError, "required"))
check("dev.code_review unknown act → ValueError",
      raises(lambda: db.code_review(su, "act", act="nope"), ValueError, "unknown"))
check("dev.ci unknown act → ValueError",
      raises(lambda: db.ci(su, "act", act="nope", name="x", body="y"), ValueError, "unknown"))

# ── 2 · dev.git → R3 (stub config_writer) ─────────────────────────────────────────────────────────────
print("\n[2] dev.git → R3 structured git/gh via the (stub) config_writer")
srv, port = _start_stub_cw()
try:
    su = StubSuite()
    lst = db.git(su, "list")
    check("dev.git list names rail R3 + read/write acts",
          lst["rail"] == "R3" and "status" in lst["reads"] and "commit" in lst["writes"])
    rd = db.git(su, "get", act="status", cwd=".")
    check("dev.git get(status) routes to the R3 service (ok echo)", rd.get("ok") and rd["act"] == "status")
    # WRITE without consent → the actor's pending-proposal (consent-not-lockdown, NOT a denial)
    nc = db.git(su, "act", act="commit", cwd=".", args=["-m", "x"])
    check("dev.git commit WITHOUT consent → pending-proposal (consent-not-lockdown, not denial)",
          nc.get("status") == "pending-consent" and nc.get("ok") is False)
    # WRITE with consent + run=False → the preview argv (injection-resistance: metachars stay one element)
    prev = db.git(su, "act", act="commit", cwd=".", args=["-m", "hi; rm -rf /"], consent=True, run=False)
    check("dev.git commit consent+preview returns argv (no exec)", prev.get("would_run") is True)
    check("injection metachars stay ONE argv element (argv-array floor)",
          "-m" in prev["argv"] and "hi; rm -rf /" in prev["argv"])
    # WRITE with consent + run=True → structured sha (the structured-sha path, NOT prose)
    com = db.git(su, "act", act="commit", cwd=".", args=["-m", "real"], consent=True, run=True)
    check("dev.git commit consent+run → structured sha (R3 path, not prose)", com.get("sha") == "deadbeef")
    check("dev.git rail is R3 on the act result", com["rail"] == "R3")
finally:
    srv.shutdown()

# fail-loud when the R3 actor is DOWN (point at a dead port)
os.environ["COMPANY_CONFIG_WRITER_PORT"] = "1"   # nothing listening
check("dev.git read fails LOUD when config_writer is down (no silent empty)",
      raises(lambda: db.git(StubSuite(), "get", act="status", cwd="."), ValueError, "not reachable"))

# ── 3 · dev.code_intel / dev.computer_use → R1-prime ───────────────────────────────────────────────────
print("\n[3] R1-prime in-session (code_intel/computer_use): intent (prose, no return_shape) + boundary refusal")
su = StubSuite()
ci_list = db.code_intel(su, "list")
check("code_intel list: rail R1-prime, liveness stream, return_shape None",
      ci_list["rail"] == "R1-prime" and ci_list["liveness"] == "stream" and ci_list["return_shape"] is None)
intent = db.code_intel(su, "act", act="definition", target="resolve_address", consent=True)
check("code_intel act builds a bridge-session INTENT (R1-prime)", intent["rail"] == "R1-prime")
check("code_intel intent is prose: return_shape None + liveness stream",
      intent["return_shape"] is None and intent["liveness"] == "stream")
check("code_intel intent carries a watch cursor (events stream)",
      intent["watch"]["stream"] == "events" and isinstance(intent["watch"]["since"], int))
check("code_intel intent persisted a dev_bridge.intent event (the store append — handler never spawns)",
      any(e["kind"] == "dev_bridge.intent" and e["capability"] == "dev.code_intel"
          for e in su.store.events_since(-1)))
check("code_intel intent records operator_consent (the spawn gate, passed through)",
      intent["operator_consent"] is True)
check("code_intel requires_tool_grant names the wider tools (LSP family)",
      "LSP" in intent["requires_tool_grant"])
# computer-use: web-fetch grantable; browser/computer host/rail boundary refused LOUD
su = StubSuite()
wf = db.computer_use(su, "act", act="web-fetch", target="https://example.com", consent=True)
check("computer_use web-fetch builds an R1-prime intent (grantable on this rail)",
      wf["rail"] == "R1-prime" and wf["return_shape"] is None)
check("computer_use browser REFUSED LOUD (beta + not-WSL host boundary, never green-painted)",
      raises(lambda: db.computer_use(su, "act", act="browser", target="x", consent=True),
             ValueError, "BOUNDARY"))
check("computer_use computer REFUSED LOUD (macOS+interactive host boundary)",
      raises(lambda: db.computer_use(su, "act", act="computer", target="x", consent=True),
             ValueError, "BOUNDARY"))
cu_list = db.computer_use(su, "list")
check("computer_use list surfaces per-act caveats (boundary visible BEFORE trying)",
      cu_list["caveats"]["browser"]["not_wsl"] is True and cu_list["caveats"]["web-fetch"]["not_wsl"] is False)

# ── 4 · dev.code_review → R2 wire job (no spawn) ───────────────────────────────────────────────────────
print("\n[4] dev.code_review → R2 wire-job intent + watch cursor (handler NEVER spawns claude -p)")
su = StubSuite()
cr_list = db.code_review(su, "list")
check("code_review list: rail R2 + the three review acts",
      cr_list["rail"] == "R2" and set(cr_list["acts"]) == {"review-local", "security-review-local", "review-pr"})
job = db.code_review(su, "act", act="review-local", target="HEAD~1..HEAD")
check("code_review act returns a job-id + watch cursor (R2)",
      job["rail"] == "R2" and job["job"].startswith("crev-") and job["watch"]["stream"] == "events")
check("code_review wrote a code_review.job event (the wire-job intent — no spawn)",
      any(e["kind"] == "code_review.job" for e in su.store.events_since(-1)))
got = db.code_review(su, "get")
check("code_review get folds its own surfaced jobs", got["total"] == 1 and got["jobs"][0]["act"] == "review-local")

# ── 5 · dev.ci → R3 scaffold + traversal refusal ───────────────────────────────────────────────────────
print("\n[5] dev.ci → R3 scaffold request shape + traversal refusal + honest read")
srv, port = _start_stub_cw()
try:
    su = StubSuite()
    ci_l = db.ci(su, "list")
    check("dev.ci list: scaffold write + inbound boundary (mention/event have NO op)",
          ci_l["writes"] == ["scaffold"] and ci_l["inbound_boundary"] == ["mention", "event"])
    check("dev.ci scaffold traversal in name REFUSED LOUD",
          raises(lambda: db.ci(su, "act", act="scaffold", name="../evil", body="x"), ValueError, "BARE id"))
    check("dev.ci scaffold empty body REFUSED LOUD",
          raises(lambda: db.ci(su, "act", act="scaffold", name="ci", body=""), ValueError, "non-empty"))
    # consent path: a scaffold WITHOUT consent → pending-proposal from the stub actor (consent-not-lockdown)
    sc = db.ci(su, "act", act="scaffold", name="claude", body="on: [push]\njobs: {}\n")
    check("dev.ci scaffold WITHOUT consent → pending-proposal (consent-not-lockdown)",
          sc.get("status") == "pending-consent")
    check("dev.ci scaffold targets .github/workflows/<name>.yml", sc.get("rel_path", "").endswith("/claude.yml")
          or sc.get("rel_path", "").endswith("\\claude.yml"))
finally:
    srv.shutdown()
# honest read of a real on-disk workflow
with tempfile.TemporaryDirectory() as td:
    wfdir = os.path.join(td, ".github", "workflows")
    os.makedirs(wfdir)
    open(os.path.join(wfdir, "claude.yml"), "w").write("on: [push]\n")
    su = StubSuite()
    got = db.ci(su, "get", name="claude", cwd=td)
    check("dev.ci get reads an existing workflow file", got["exists"] and "on: [push]" in got["content"])
    missing = db.ci(su, "get", name="nope", cwd=td)
    check("dev.ci get honest absence (exists False, content None — not a default)",
          missing["exists"] is False and missing["content"] is None)

# ── 6 · DRY: one handler, two faces (§3.3) — the MCP face returns the handler's BYTE-IDENTICAL dict ──────
print("\n[6] DRY — MCP face delegates to the SAME handler (byte-identical dict on a read)")
from mcp.server.fastmcp import FastMCP
su = StubSuite()
mcp = FastMCP("test")
faces = db_face_tools = None
from mcp_face.tools import dev_bridges as face
dev_git_t, dev_code_intel_t, dev_computer_use_t, dev_code_review_t, dev_ci_t = face.register(mcp, su)
check("MCP face exports OPS = (list,get,act)", face.OPS == ("list", "get", "act"))
# read ops (no side effects) — compare the face tool result to the handler result, identical
pairs = [
    ("dev.git", dev_git_t, lambda: db.git(StubSuite(), "list"), lambda: dev_git_t("list")),
    ("dev.code_intel", dev_code_intel_t, lambda: db.code_intel(StubSuite(), "list"), lambda: dev_code_intel_t("list")),
    ("dev.computer_use", dev_computer_use_t, lambda: db.computer_use(StubSuite(), "list"), lambda: dev_computer_use_t("list")),
    ("dev.code_review", dev_code_review_t, lambda: db.code_review(StubSuite(), "list"), lambda: dev_code_review_t("list")),
    ("dev.ci", dev_ci_t, lambda: db.ci(StubSuite(), "list"), lambda: dev_ci_t("list")),
]
for key, _t, h_call, f_call in pairs:
    h = h_call()
    f = f_call()
    check(f"{key}: MCP face dict == handler dict (DRY, one handler two faces)", h == f,
          f"\n    handler={h}\n    face={f}")

# annotations: every ④ tool is a WRITE rail → readonly False (registry-is-truth)
for key in ch.keys_for_family("dev"):
    check(f"{key}: HANDLERS readonly=False (write rail) drives the face annotation",
          ch.get(key).readonly is False)

# ── verdict ──────────────────────────────────────────────────────────────────────────────────────────
print(f"\n=== {PASS} passed, {FAIL} failed ===")
sys.exit(0 if FAIL == 0 else 1)
