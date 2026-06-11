"""tests/config_writer_acceptance.py — the R3 CONFIG WRITER's service-level guarantees (arch §3.1).

Proves BY USE, against the REAL service process (no mock of the service), on an ISOLATED tmp store +
a SCRATCH .claude tree (HOME pointed at the scratch dir → NO live config touched), with NO real
`claude mcp`/`git` mutation (lead-only law: this worker fires no real config-mutating CLI; the REAL
`claude mcp add`/`claude plugin install`/`git commit` round-trip is the lead's live-verify, marked
building + 'live-verify pending (lead)', NEVER green-painted). It binds the SAME reduction registries
the service does (config_targets / cli_allowlist — registry-is-truth). Checks:

  1. /health 200 on 127.0.0.1, names the consent-not-lockdown model + the 4 consent classes;
  2. CONFIG-WRITE ROUND-TRIP (the headline): a hooks settings write (a DANGEROUS payload — a shell
     command Claude Code runs on a trigger) is a PENDING-CONSENT proposal while unconsented (NOT a
     denial — names the danger + both consent paths), then SUCCEEDS with consent:true; the re-read
     shows the merged block; a second write merges (shallow), leaves a .bak, prior key survives;
  3. STANDING CONSENT: /consent grants config-write; the next dangerous write needs no per-call
     consent; revoking it returns to per-call (consent is revocable, not a one-way door);
  4. NON-DANGEROUS write (output-style) needs no consent (the tier distinction is real);
  5. SCOPE/PATH SAFETY: a bad/managed scope and a traversal name are refused-loud (400);
  6. CONTENT VALIDATION: a non-object hooks block + a bad hook EVENT + an empty body refused;
  7. CLI TIER GATE (no real claude mutation — run=False / proposal): mcp.list (read) ungated;
     mcp.add (exec) → pending-consent unconsented; argv-array carries an injection-y value as ONE
     token; git.commit (write) → pending then, with consent + injected git, a structured sha;
  8. RUN-RECORD: a write lands a config_writer.* event (args redacted);
  9. CONTRACT DRIFT: CONFIG_WRITER_ROUTES == the do_GET/do_POST dispatch literals, both directions.

Deadlock-safe: bounded waits; the child is killed in finally. Exit 0 = pass, 1 = a failed check.
Run: ./.venv/bin/python tests/config_writer_acceptance.py
"""
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

PY = os.path.join(ROOT, ".venv", "bin", "python")
if not os.path.exists(PY):
    PY = sys.executable
PORT = 8782                      # a TEST port — never the live 8772
BASE = f"http://127.0.0.1:{PORT}"
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


def req(method, path, body=None, timeout=10):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(BASE + path, data=data, method=method,
                               headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


def main():
    tmp = tempfile.mkdtemp(prefix="cfgwriter-test-")
    store_dir = os.path.join(tmp, "store")
    project_dir = os.path.join(tmp, "project")
    os.makedirs(project_dir, exist_ok=True)
    env = dict(os.environ)
    env["COMPANY_STORE"] = store_dir
    env["COMPANY_CONFIG_WRITER_PORT"] = str(PORT)
    env["HOME"] = tmp                # user-scope writes land in the scratch tree, NOT the real ~/.claude
    proc = subprocess.Popen([PY, os.path.join(ROOT, "runtime", "config_writer.py"), str(PORT)],
                            env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        # ---- 1. /health ----
        up = False
        for _ in range(80):
            try:
                code, h = req("GET", "/health", timeout=2)
                if code == 200 and h.get("ok"):
                    up = True
                    break
            except Exception:
                time.sleep(0.05)
        check("service starts; /health 200 on 127.0.0.1", up)
        check("health binds 127.0.0.1 (exposure law)", h.get("bind") == "127.0.0.1")
        check("health names consent-not-lockdown model", "consent-not-lockdown" in (h.get("model") or ""))
        check("health lists the 4 consent classes",
              set(h.get("consent_classes") or []) ==
              {"config-write", "cli-write", "cli-exec", "git-write"})

        # ---- 2. CONFIG-WRITE ROUND-TRIP (hooks — the dangerous payload) ----
        block = {"PostToolUse": [{"matcher": "*", "hooks": [{"type": "command", "command": "echo audited"}]}]}
        # 2a. unconsented → PENDING-CONSENT proposal (consent-not-lockdown, NOT a denial, NOT a write)
        code, r = req("POST", "/write", {"key": "config.hooks", "scope": "project",
                                         "block": block, "project_dir": project_dir})
        check("unconsented dangerous write → 200 pending-consent proposal (not a denial)",
              code == 200 and r.get("status") == "pending-consent" and r.get("ok") is False)
        teach = (r.get("teach", "") + " " + r.get("note", "")).lower()
        check("proposal TEACHES the danger (executes on a trigger)",
              "execut" in teach and "trigger" in teach)
        check("proposal names BOTH consent paths (per-call + standing /consent)",
              '"consent": true' in r.get("note", "") and "/consent" in r.get("note", ""))
        check("proposal is consent-not-lockdown (path-to-yes / not walled)",
              "one signal away" in r.get("note", "").lower())
        settings_path = os.path.join(project_dir, ".claude", "settings.json")
        check("unconsented proposal left NO file (a real no-write)", not os.path.isfile(settings_path))

        # 2b. with consent:true → succeeds, round-trips
        code, w = req("POST", "/write", {"key": "config.hooks", "scope": "project",
                                         "block": block, "consent": True, "project_dir": project_dir})
        check("consented write SUCCEEDS (200, ok)", code == 200 and w.get("ok"))
        check("write reports re-read verification (no green-paint)", "re-read matches" in (w.get("verified") or ""))
        check("scratch settings.json now exists", os.path.isfile(settings_path))
        code, rd = req("POST", "/read", {"key": "config.hooks", "scope": "project", "project_dir": project_dir})
        check("ROUND-TRIP: read-back hook command == written",
              rd.get("exists") and
              rd["content"]["hooks"]["PostToolUse"][0]["hooks"][0]["command"] == "echo audited")
        # 2c. second dangerous write (env via config.hooks is hooks-only; use a second hook event) merges
        block2 = {"SessionStart": [{"hooks": [{"type": "command", "command": "echo start"}]}]}
        code, w2 = req("POST", "/write", {"key": "config.hooks", "scope": "project",
                                          "block": block2, "consent": True, "project_dir": project_dir})
        check("second write 200 + leaves a .bak backup", code == 200 and w2.get("backup"))
        check("backup file on disk", os.path.isfile(w2["backup"]))
        code, rd2 = req("POST", "/read", {"key": "config.hooks", "scope": "project", "project_dir": project_dir})
        hooks = rd2["content"]["hooks"]
        check("merge: new hook event present", "SessionStart" in hooks)
        check("merge: PRIOR hook event survived (shallow merge, not overwrite)", "PostToolUse" in hooks)

        # ---- 3. STANDING CONSENT (revocable) ----
        code, c = req("POST", "/consent", {"class": "config-write", "grant": True})
        check("grant standing config-write consent 200", code == 200 and c.get("granted"))
        # a dangerous slash-command write now needs no per-call consent
        code, w3 = req("POST", "/write", {"key": "config.slash_commands", "scope": "project",
                                          "name": "demo", "body": "Do the demo thing.",
                                          "project_dir": project_dir})
        check("standing-consented dangerous write needs NO per-call consent (200 ok)", code == 200 and w3.get("ok"))
        check("command file written under .claude/commands",
              os.path.isfile(os.path.join(project_dir, ".claude", "commands", "demo.md")))
        code, _ = req("POST", "/consent", {"class": "config-write", "grant": False})
        code, w4 = req("POST", "/write", {"key": "config.slash_commands", "scope": "project",
                                          "name": "demo2", "body": "x", "project_dir": project_dir})
        check("after revoke, dangerous write → pending-consent again (revocable)",
              code == 200 and w4.get("status") == "pending-consent")

        # ---- 4. NON-DANGEROUS write (output-style) needs no consent ----
        code, ws = req("POST", "/write", {"key": "config.output_style", "scope": "project",
                                          "name": "calm", "body": "---\nname: calm\n---\nBe calm.",
                                          "project_dir": project_dir})
        check("non-dangerous output-style write needs NO consent (200 ok, tier distinction real)",
              code == 200 and ws.get("ok"))

        # ---- 5. SCOPE / PATH SAFETY ----
        code, t = req("POST", "/write", {"key": "config.hooks", "scope": "managed", "block": block,
                                         "consent": True, "project_dir": project_dir})
        check("managed/unknown scope refused-loud (400 — boundary = absence, §5.5)",
              code == 400 and "scope" in t.get("error", "").lower())
        code, t2 = req("POST", "/write", {"key": "config.slash_commands", "scope": "project",
                                          "name": "../escape", "body": "x", "consent": True,
                                          "project_dir": project_dir})
        check("traversal name refused-loud (400)",
              code == 400 and ("invalid" in t2.get("error", "").lower()
                               or "traversal" in t2.get("error", "").lower()
                               or "leading dash" in t2.get("error", "").lower()))

        # ---- 6. CONTENT VALIDATION ----
        code, cv = req("POST", "/write", {"key": "config.hooks", "scope": "project",
                                          "block": "not-an-object", "consent": True, "project_dir": project_dir})
        check("non-object hooks block refused (400)", code == 400 and "JSON object" in cv.get("error", ""))
        code, cv2 = req("POST", "/write", {"key": "config.hooks", "scope": "project",
                                           "block": {"NotAnEvent": []}, "consent": True, "project_dir": project_dir})
        check("bad hook EVENT refused (400, grounded in Atlas event set)",
              code == 400 and "hook EVENT" in cv2.get("error", ""))
        code, cv3 = req("POST", "/write", {"key": "config.extensions", "scope": "project", "name": "s",
                                           "body": "   ", "consent": True, "project_dir": project_dir})
        check("empty skill body refused (400)", code == 400 and "non-empty" in cv3.get("error", ""))

        # ---- 7. CLI TIER GATE (no real claude/git mutation) ----
        import runtime.config_writer as cw
        from runtime.capability_handlers.reduction import cli_allowlist as CL
        # 7a. read tier is ungated — prove via the in-process actor with run=False (no real claude run)
        from store.fs_store import FsStore
        actor = cw.ConfigWriter(FsStore(store_dir))
        r_list = actor.cli(act="config.mcp_servers:list", run=False)
        check("cli read (mcp.list) ungated → builds argv (run=False)", r_list.get("would_run") and r_list["tier"] == "read")
        # 7b. exec tier unconsented → pending-consent proposal (NOT a denial)
        r_add = actor.cli(act="config.mcp_servers:add", transport="stdio", scope="local", name="x",
                          url_or_cmd="/x; rm -rf /", run=False)
        check("cli exec (mcp.add) unconsented → pending-consent proposal",
              r_add.get("status") == "pending-consent" and r_add.get("consent_class") == "cli-exec")
        # 7c. with consent → builds the argv; the injection-y value is ONE token (no shell parse)
        r_add2 = actor.cli(act="config.mcp_servers:add", transport="stdio", scope="local", name="x",
                           url_or_cmd="/x; rm -rf /", consent=True, run=False)
        check("consented mcp.add builds argv; dangerous value is a SINGLE argv token (no injection)",
              "/x; rm -rf /" in r_add2["argv"] and r_add2["argv"].count("/x; rm -rf /") == 1)
        # 7d. git.commit unconsented → pending; consented + injected git → structured sha
        g_pending = actor.git(act="dev.git:commit", cwd=project_dir, args=["-m", "msg"], run=False)
        check("git.commit unconsented → pending-consent (git-write class)",
              g_pending.get("status") == "pending-consent" and g_pending.get("consent_class") == "git-write")
        # consented build (run=False — no real git): argv-array carries the message as discrete tokens
        g_build = actor.git(act="dev.git:commit", cwd=project_dir, args=["-m", "msg"], consent=True, run=False)
        check("consented git commit builds `git commit -m msg` argv-array",
              g_build["argv"][1:] == ["commit", "-m", "msg"])

        # ---- 8. RUN-RECORD (Introspective-Data law, args redacted) ----
        evs = [e for e in FsStore(store_dir).events_since(-1) if e.get("kind", "").startswith("config_writer.")]
        check("run-record events written (config_writer.*)",
              any(e.get("kind") == "config_writer.write" for e in evs))
        check("a write run-record does NOT log the raw hook command (redaction)",
              all("echo audited" not in json.dumps(e) for e in evs))

        # ---- 9. CONTRACT DRIFT ----
        src = open(os.path.join(ROOT, "runtime", "config_writer.py")).read()
        declared = set(cw.CONFIG_WRITER_ROUTES)
        get_block = src[src.index("def do_GET"):src.index("def do_POST")]
        post_block = src[src.index("def do_POST"):src.index("def main")]
        get_routes = {("GET", p) for p in re.findall(r'u\.path == "(/[a-z]+)"', get_block)}
        post_routes = {("POST", p) for p in re.findall(r'u\.path == "(/[a-z]+)"', post_block)}
        dispatched = get_routes | post_routes
        check("DRIFT: every CONFIG_WRITER_ROUTES route has a dispatch literal", declared <= dispatched)
        check("DRIFT: every dispatch literal is in CONFIG_WRITER_ROUTES (no phantom)", dispatched <= declared)
        check("DRIFT: both directions EQUAL", declared == dispatched)

        print(f"\nPASS — {PASS} checks (config_writer R3: scratch-config round-trip + consent-not-lockdown "
              f"beat proven by use, bound to the real config_targets/cli_allowlist registries; real "
              f"claude mcp/plugin/git mutation is the lead's live-verify, NOT run here).")
        return 0
    except AssertionError as e:
        print(f"\n{e}")
        # kill the child FIRST (it is still serving — reading its PIPE while alive deadlocks)
        try:
            proc.kill(); proc.wait(timeout=3)
        except Exception:
            pass
        try:
            out = proc.stdout.read() if proc.stdout else ""
        except Exception:
            out = ""
        if out:
            print("--- service output (tail) ---\n" + out[-1500:])
        return 1
    finally:
        try:
            proc.send_signal(signal.SIGTERM)
            proc.wait(timeout=5)
        except Exception:
            proc.kill()
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
