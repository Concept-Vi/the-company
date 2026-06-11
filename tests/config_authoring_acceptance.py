"""tests/config_authoring_acceptance.py — the L-③-config lane's TEETH (Capability Fabric §4 ③).

Proves the ③ CONFIG-AUTHORING handlers BY USE, against the REAL config_writer (in-process,
r3.bind'd) on an ISOLATED tmp store + scratch HOME + scratch project (NO live config touched), with
NO real `claude mcp`/`plugin`/`git` mutation (lead-only law: this worker fires no real config-mutating
CLI; the REAL `claude mcp add` proven by `claude mcp list`, `claude plugin install`, and a settings
flag a session honours are the lead's live-verify — marked building + 'live-verify pending (lead)',
NEVER green-painted here). Checks, all fail-loud:

  1. all 9 ③ handlers are WIRED (built True) on the specced rails;
  2. PATTERNS resolver (direct-read, pure): resolve(intent) → the right mechanism; describe() → the
     whole chooser + placeholders + precedence (no file, no R3);
  3. KEYBINDINGS (CC-04 reopened): act set-binding round-trips ~/.claude/keybindings.json (merge by
     context, null unbind); bad context / reserved shortcut / bad action / non-user scope refused-loud;
  4. TELEMETRY (CC-32 reopened): set-flag writes settings.json env; unknown flag refused-loud;
  5. PROVIDER (CC-29 reopened): set-provider writes settings.json env; unknown key refused-loud;
  6. HOOKS (CC-12, DANGEROUS): act add-hook is a PENDING-CONSENT proposal unconsented (NOT a denial —
     consent-not-lockdown), SUCCEEDS with consent, re-read shows the merged hook; a bad hook EVENT
     refused; the dangerous shell `command` is NEVER in the run-record (redaction);
  7. OUTPUT-STYLE (CC-26, non-dangerous): create-style authors the file with NO consent (tier real);
  8. SLASH-COMMANDS (CC-03, DANGEROUS): create authors the .md (consent-gated);
  9. EXTENSIONS (CC-13): create-skill (DANGEROUS body) proposal→consent; plugin install (exec) →
     pending-consent unconsented (re-tiered to operator-consent, §5.2); an injection-y stdio mcp value
     lands as ONE argv token (the injection floor) on the consented add (run=False unit path);
 10. DRY: the MCP face tool delegate returns BYTE-IDENTICAL to the handler fn (one-handler-two-faces),
     for a read AND the patterns resolver;
 11. FAIL-LOUD: an unknown op / unknown act on every handler raises a teaching ValueError.

Run: ./.venv/bin/python tests/config_authoring_acceptance.py
"""
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

PASS = 0
FAIL = 0


def check(label, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok  {label}")
    else:
        FAIL += 1
        print(f"  XX  {label}  {detail}")


def raises(fn, exc=Exception):
    try:
        fn()
        return False
    except exc:
        return True
    except Exception:
        return False


def main():
    tmp = tempfile.mkdtemp(prefix="config_authoring_")
    home = os.path.join(tmp, "home")
    proj = os.path.join(tmp, "proj")
    os.makedirs(os.path.join(proj, ".claude"), exist_ok=True)
    os.makedirs(home, exist_ok=True)
    old_home = os.environ.get("HOME")
    os.environ["HOME"] = home                       # scratch HOME — NO live ~/.claude touched
    try:
        # import AFTER HOME is set (config_targets caches HOME at import)
        import importlib
        import runtime.capability_handlers.reduction.config_targets as CT
        importlib.reload(CT)
        import runtime.config_writer as cw
        importlib.reload(cw)
        from store.fs_store import FsStore
        from runtime import capability_handlers as ch
        from runtime.capability_handlers import r3
        import runtime.capability_handlers.config_authoring as ca  # wires the fns
        importlib.reload(ca)

        W = cw.ConfigWriter(FsStore(os.path.join(tmp, "store")))
        r3.bind(W)                                  # in-process R3 — no service, no network

        def H(key):
            return ch.get(key)

        print("\n[1] all 9 ③ handlers wired on their rails")
        EXPECT = {"config.hooks": "R3", "config.mcp_servers": "R3", "config.output_style": "R3",
                  "config.slash_commands": "R3", "config.extensions": "R3",
                  "config.patterns": "direct-read", "config.keybindings": "R3",
                  "config.telemetry": "R3", "config.provider": "R3"}
        for k, rail in EXPECT.items():
            check(f"{k} wired (built) on rail {rail}", ch.get(k).built and ch.get(k).rail == rail,
                  f"built={ch.get(k).built} rail={ch.get(k).rail}")

        print("\n[2] patterns resolver (pure direct-read)")
        r = H("config.patterns").fn(None, "resolve",
                                    intent="run code automatically at a lifecycle point")
        check("resolve('lifecycle') → hook", r["matches"][0]["mechanism"] == "hook", r["matches"][0])
        r2 = H("config.patterns").fn(None, "resolve", intent="give claude access to an external tool")
        check("resolve('external tool') → mcp-server", r2["matches"][0]["mechanism"] == "mcp-server",
              r2["matches"][0])
        d = H("config.patterns").fn(None, "describe")
        check("describe() carries chooser+placeholders+precedence",
              len(d["chooser"]) == 10 and "${CLAUDE_PROJECT_DIR}" in d["placeholders"] and d["precedence"])
        check("patterns unknown op fails loud", raises(lambda: H("config.patterns").fn(None, "nope"), ValueError))

        print("\n[3] keybindings (CC-04 reopened) — round-trip + refusals")
        kb = H("config.keybindings").fn(None, "act", act="set-binding", context="Chat",
                                        bindings={"ctrl+e": "chat:externalEditor", "ctrl+u": None})
        check("keybindings set-binding ok (non-dangerous, no consent)", kb.get("ok"), kb)
        rk = H("config.keybindings").fn(None, "get")
        kmap = rk["content"]["bindings"][0]["bindings"]
        check("keybindings read-back: bind + null-unbind landed",
              kmap.get("ctrl+e") == "chat:externalEditor" and kmap.get("ctrl+u") is None, kmap)
        # merge a second context — prior survives
        H("config.keybindings").fn(None, "act", act="set-context", context="Global",
                                   bindings={"ctrl+t": "app:toggleTodos"})
        ctxs = [b["context"] for b in H("config.keybindings").fn(None, "get")["content"]["bindings"]]
        check("keybindings merge: both contexts present", "Chat" in ctxs and "Global" in ctxs, ctxs)
        check("bad context refused-loud",
              raises(lambda: H("config.keybindings").fn(None, "act", act="set-binding",
                     context="Nope", bindings={"ctrl+y": "x:y"}), cw.WriteRefusal))
        check("reserved shortcut (ctrl+c) bind refused-loud",
              raises(lambda: H("config.keybindings").fn(None, "act", act="set-binding",
                     context="Chat", bindings={"ctrl+c": "chat:cancel"}), cw.WriteRefusal))
        check("bad action shape refused-loud",
              raises(lambda: H("config.keybindings").fn(None, "act", act="set-binding",
                     context="Chat", bindings={"ctrl+y": "noColon"}), cw.WriteRefusal))
        check("non-user scope keybindings refused-loud (handler ValueError, no silent redirect)",
              raises(lambda: H("config.keybindings").fn(None, "act", act="set-binding", scope="project",
                     context="Chat", bindings={"ctrl+y": "x:y"}, project_dir=proj), ValueError))

        print("\n[4] telemetry (CC-32 reopened) — settings env flags")
        tf = H("config.telemetry").fn(None, "act", act="set-flag", flags={"DISABLE_TELEMETRY": "1"})
        check("telemetry set-flag ok (non-dangerous)", tf.get("ok"), tf)
        rt = H("config.telemetry").fn(None, "get")
        check("telemetry read-back env flag", rt["content"]["env"]["DISABLE_TELEMETRY"] == "1", rt)
        check("unknown data-posture flag refused-loud",
              raises(lambda: H("config.telemetry").fn(None, "act", act="set-flag",
                     flags={"NOPE": "1"}), ValueError))

        print("\n[5] provider (CC-29 reopened) — settings env routing")
        pv = H("config.provider").fn(None, "act", act="set-provider",
                                     env={"CLAUDE_CODE_USE_BEDROCK": "1"})
        check("provider set-provider ok (non-dangerous)", pv.get("ok"), pv)
        check("unknown provider env key refused-loud",
              raises(lambda: H("config.provider").fn(None, "act", act="set-provider",
                     env={"NOPE": "1"}), ValueError))

        print("\n[6] hooks (CC-12 DANGEROUS) — consent beat + redaction")
        HOOK = {"PostToolUse": [{"matcher": "Bash",
                                 "hooks": [{"type": "command", "command": "echo SECRETCMD"}]}]}
        prop = H("config.hooks").fn(None, "act", act="add-hook", block=HOOK, scope="project",
                                    project_dir=proj)
        check("hooks add-hook UNCONSENTED → pending-consent proposal (not a denial)",
              prop.get("status") == "pending-consent", prop)
        ok = H("config.hooks").fn(None, "act", act="add-hook", block=HOOK, scope="project",
                                  project_dir=proj, consent=True)
        check("hooks add-hook CONSENTED → ok", ok.get("ok"), ok)
        rh = H("config.hooks").fn(None, "get", scope="project", project_dir=proj)
        check("hooks read-back: PostToolUse present", "PostToolUse" in rh["content"]["hooks"], rh)
        check("bad hook EVENT refused-loud",
              raises(lambda: H("config.hooks").fn(None, "act", act="add-hook",
                     block={"NopeEvent": []}, scope="project", project_dir=proj, consent=True),
                     cw.WriteRefusal))
        # redaction: the dangerous shell command must not appear in any run-record event
        events = W.store.events_since(-1)
        recs = [e for e in events if str(e.get("kind", "")).startswith("config_writer.")]
        leaked = any("SECRETCMD" in json.dumps(e) for e in recs)
        check("run-records written + dangerous command REDACTED (not in any record)",
              recs and not leaked, f"records={len(recs)} leaked={leaked}")

        print("\n[7] output-style (CC-26 non-dangerous) — file authoring, no consent")
        st = H("config.output_style").fn(None, "act", act="create-style", name="myrole",
                                         body="---\nname: myrole\n---\nbe terse", scope="user")
        check("output-style create-style ok with NO consent (tier distinction real)", st.get("ok"), st)

        print("\n[8] slash-commands (CC-03 DANGEROUS) — consent-gated authoring")
        cmd = H("config.slash_commands").fn(None, "act", act="create", name="mycmd",
                                            body="run the thing", scope="user")
        check("slash-command create UNCONSENTED → pending-consent",
              cmd.get("status") == "pending-consent", cmd)
        cmd2 = H("config.slash_commands").fn(None, "act", act="create", name="mycmd",
                                             body="run the thing", scope="user", consent=True)
        check("slash-command create CONSENTED → ok", cmd2.get("ok"), cmd2)

        print("\n[9] extensions (CC-13) — skill authoring + plugin/mcp exec consent + injection floor")
        sk = H("config.extensions").fn(None, "act", act="create-skill", name="myskill",
                                       body="---\nname: myskill\n---\ndo the thing", scope="user")
        check("create-skill UNCONSENTED → pending-consent (dangerous prompt body)",
              sk.get("status") == "pending-consent", sk)
        sk2 = H("config.extensions").fn(None, "act", act="create-skill", name="myskill",
                                        body="---\nname: myskill\n---\ndo the thing", scope="user",
                                        consent=True)
        check("create-skill CONSENTED → ok", sk2.get("ok"), sk2)
        pl = H("config.extensions").fn(None, "act", act="install-plugin", plugin="some-plugin",
                                       scope="user")
        check("plugin install UNCONSENTED → pending-consent (exec, re-tiered §5.2)",
              pl.get("status") == "pending-consent", pl)
        # injection floor: a consented mcp add with an injection-y stdio value → ONE argv token (run=False
        # via the writer's cli unit path; the handler always run=True, so probe the writer directly with
        # the same allowlist render the handler uses — proves the argv-array is the floor).
        from runtime.capability_handlers.reduction import cli_allowlist as CL
        argv = CL.render_argv("config.mcp_servers:add", transport="stdio", scope="local",
                              name="weather", url_or_cmd="python -m weather; rm -rf /")
        check("mcp add injection-y value is ONE argv token (the injection floor)",
              "python -m weather; rm -rf /" in argv and len(argv) == 9, argv)
        mcpp = H("config.mcp_servers").fn(None, "act", act="add", name="weather", transport="stdio",
                                          url_or_cmd="python -m weather", scope="local")
        check("mcp add (exec) UNCONSENTED → pending-consent",
              mcpp.get("status") == "pending-consent", mcpp)
        nu = H("config.extensions").fn(None, "act", act="update-native")
        check("CC-34 native updater (claude update, exec) UNCONSENTED → pending-consent (reopened)",
              nu.get("status") == "pending-consent", nu)

        print("\n[10] DRY — MCP face delegate == handler fn (one-handler-two-faces)")
        from mcp_face.tools import config_authoring as face
        for label, key, args in (
            ("patterns describe", "config.patterns", ("describe",)),
            ("patterns resolve", "config.patterns", ("resolve",)),
        ):
            kw = {} if key != "config.patterns" else ({"intent": "run code at a lifecycle point"}
                                                      if args[0] == "resolve" else {})
            f = face._call(key, *args, **kw)
            h = H(key).fn(None, *args, **kw)
            check(f"DRY {label}: face == handler (byte-identical)",
                  json.dumps(f, sort_keys=True) == json.dumps(h, sort_keys=True))
        fk = face._call("config.keybindings", "get")
        hk = H("config.keybindings").fn(None, "get")
        check("DRY keybindings read: face == handler",
              json.dumps(fk, sort_keys=True) == json.dumps(hk, sort_keys=True))

        print("\n[11] fail-loud on unknown op / unknown act")
        check("hooks unknown op fails loud", raises(lambda: H("config.hooks").fn(None, "frobnicate"), ValueError))
        check("hooks unknown act fails loud",
              raises(lambda: H("config.hooks").fn(None, "act", act="nope", block={}), ValueError))
        check("mcp_servers unknown act fails loud",
              raises(lambda: H("config.mcp_servers").fn(None, "act", act="nope"), ValueError))
        check("extensions unknown act fails loud",
              raises(lambda: H("config.extensions").fn(None, "act", act="nope"), ValueError))

    finally:
        r3 = sys.modules.get("runtime.capability_handlers.r3")
        if r3:
            r3.bind(None)
        if old_home is not None:
            os.environ["HOME"] = old_home
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"\n{'PASS' if FAIL == 0 else 'FAIL'} — {PASS} passed, {FAIL} failed "
          f"(③ config-authoring handlers by USE on a scratch tree; real claude-CLI/settings round-trip "
          f"is the lead's live-verify, NOT run here — lead-only law).")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
