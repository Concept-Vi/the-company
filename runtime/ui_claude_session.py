"""runtime/ui_claude_session.py — the CLAUDE CODE SIDE-PANEL session (overnight S1; Track-1 slice 1).

The BUILDER in the surface: Tim points at an element and talks; a real Claude Code session runs in
the repo with the pointed-at address's context riding in, and its activity streams back to the panel.

OPERATOR-FACE ONLY (the floor): these sessions launch ONLY from the bridge's HTTP routes — the face
Tim drives. This module is NEVER imported by mcp_face (no agent can reach it), and the loop never
self-dispatches through it. Safe-by-default: permission mode comes from COMPANY_PANEL_PERMISSION
(default 'plan' — read/investigate only; edits require the deliberate env opt-in), the exact
pattern of implement.py's COMPANY_WIRE_PERMISSION. Consequential building stays on the WIRE's gated
path (intent-at → operator approve → dispatch_decision) — the panel HANDS OFF to it, never replaces it.

Transport: the claude CLI's stream-json (one subprocess per turn; --resume <session_id> carries the
conversation across turns — Claude Code owns the session state, we hold only the id). No SDK
dependency; mirrors implement.py's subprocess discipline.

FLOOR NOTE UPDATE (Session Fabric F1, 2026-06-11): runtime/session_supervisor.py — an
operator-sanctioned SERVICE, not the MCP face — imports _find_claude + _MCP_CONFIG from here
(one source of the binary resolution + the strict company-MCP config). That import keeps this
floor honest: mcp_face still NEVER imports this module (or the supervisor); process-launching
stays off the face. NOTE: TURN_TIMEOUT_S below is a DEAD CONSTANT (defined, enforced nowhere —
audit C3); the supervisor enforces its own wall-clock watchdog instead of inheriting this."""
import json
import os
import subprocess

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PANEL_PERMISSION = os.environ.get("COMPANY_PANEL_PERMISSION", "plan")
def _find_claude() -> str:
    """Resolve the claude binary ABSOLUTELY (the wire's lived failure: a service-started bridge has
    no ~/.local/bin on PATH → 'claude not found' dispatch litter in the inbox). Env wins; then
    PATH; then the known install home. Fail-loud at call time if none exist."""
    import shutil
    cand = os.environ.get("COMPANY_CLAUDE_BIN") or shutil.which("claude") \
        or os.path.expanduser("~/.local/bin/claude")
    return cand


CLAUDE_BIN = _find_claude()
TURN_TIMEOUT_S = int(os.environ.get("COMPANY_PANEL_TIMEOUT_S", "600"))

PANEL_BRIEFING = (
    "You are Claude Code, the right-hand-man embedded inside the Company's own interface, talking DIRECTLY "
    "TO the operator. Address them as 'you' — SECOND PERSON. NEVER narrate ABOUT them in the third person and "
    "NEVER use their name in your reply (no 'the operator is…', no narrating their actions in the third "
    "person) — speak TO them, not about them. They are not a developer and never read code: explain in plain "
    "language at their altitude "
    "(what this is, what it means for you) — never file-dumps. Write as SPOKEN PROSE — a voice talking TO "
    "them, NOT a document: NO markdown — no **bold**, no '-'/'*' bullet lists, no # headers, no `backticks` — "
    "just plain sentences (the reply renders as plain text, so any markdown shows as literal asterisks). "
    "NEVER show raw addresses, identifiers, file "
    "paths, URLs, or scheme:// strings (e.g. ui://… / run://… / code://…) — ALWAYS translate to plain human "
    "meaning. ★ ANSWER FROM THE CONTEXT YOU ARE GIVEN, IMMEDIATELY — for an orientation question ('what am I "
    "looking at?') answer DIRECTLY and BRIEFLY (a sentence or two), to them, from your context block. ★★ DO NOT "
    "INVESTIGATE to answer an orientation question — NOT even if the context seems thin. If your context is "
    "sparse, that is FINE: say briefly + honestly what you CAN from it ('You're looking at part of your "
    "instrument surface — I don't have finer detail on this exact spot') and OFFER to look closer ('want me to "
    "dig in?'), then STOP and let them choose. NEVER launch tools / read the codebase / spawn agents to ground "
    "an orientation answer — that hangs the turn and never reaches them. Investigate ONLY when they EXPLICITLY "
    "ask you to dig into a specific thing. You are in a restricted permission mode: when a change is wanted, DESCRIBE it "
    "crisply and tell them to press 'build this' — the change flows through the system's approval gate. "
    "Never claim something works without having checked."
)


# The panel session gets the COMPANY'S OWN MCP (the Atlas's #1 ranked upgrade): the embedded builder
# holds every company tool — registries, cognition, the operator memory — not just the filesystem.
# Same stdio launch the session-level registration uses (one source of the server identity); strict
# config so the panel session loads ONLY this server (deterministic toolset, no surprise plugins).
_MCP_CONFIG = json.dumps({"mcpServers": {"company": {
    "type": "stdio",
    "command": os.path.join(REPO_ROOT, ".venv", "bin", "python"),
    "args": [os.path.join(REPO_ROOT, "mcp_face", "server.py")],
}}})


# ── least-privilege brain env (defense-in-depth, 2026-06-17) ──────────────────────────────────────────
# The loadable-brain subprocess does NOT need the company process's DATA-STORE creds: it reaches the
# factory / company state via the company MCP tools + resolve_address (which run in the COMPANY process,
# not in this subprocess), NEVER by querying Supabase/a store itself. So strip the store/factory secret
# vars from the child env (the vi-vision integration introduces a Supabase key into the company env, and a
# bare Popen inherits the full parent env — a full-access cred would otherwise be reachable by the CC brain
# subprocess). DENYLIST by prefix, NOT an allowlist: claude -p needs a broad env (PATH/HOME/ANTHROPIC_*/
# locale/…), so we keep everything EXCEPT the named secret prefixes — this can't accidentally strip what the
# brain needs (claude uses neither prefix). Extensible: add a prefix here for any future company-process
# secret the brain must not see. The brain's behaviour is unchanged (only non-claude vars are removed).
_BRAIN_ENV_DENY_PREFIXES = ("SUPABASE_", "VI_VISION_")


def _brain_env() -> dict:
    """os.environ minus the store/factory secret vars the brain must not see (least-privilege)."""
    return {k: v for k, v in os.environ.items()
            if not any(k.startswith(p) for p in _BRAIN_ENV_DENY_PREFIXES)}


def _turn_cmd(prompt: str, *, resume: str | None, system_append: str | None) -> list:
    cmd = [CLAUDE_BIN, "-p", prompt, "--output-format", "stream-json", "--verbose",
           "--permission-mode", PANEL_PERMISSION,
           "--mcp-config", _MCP_CONFIG, "--strict-mcp-config",
           # the company face carries NO consequential verbs (the floor: no resolve/approve/dispatch
           # exists on it), so pre-allowing the whole server is consistent with plan-mode safety —
           # the builder reads/computes through company tools frictionlessly; EDITS stay gated.
           "--allowedTools", "mcp__company"]
    if resume:
        cmd += ["--resume", resume]
    if system_append:
        cmd += ["--append-system-prompt", system_append]
    return cmd


def run_turn(prompt: str, *, session_id: str | None = None, context_block: str | None = None,
             should_stop=None):
    """One panel turn → a generator of panel events (dicts, ready for ndjson):
       {type:'init', session_id} · {type:'text', text} · {type:'tool', name, detail} ·
       {type:'done', result, session_id, num_turns?} · {type:'error', error}.
    `context_block` (the pointed-at address's help bundle) is folded into the prompt — per-turn
    context, exactly the indicated-chip semantics of the RHM chat. `should_stop()` (client gone)
    terminates the subprocess — a hung panel never strands a claude process."""
    full_prompt = f"[Operator context — what Tim is pointing at]\n{context_block}\n\n{prompt}" \
        if context_block else prompt
    cmd = _turn_cmd(full_prompt, resume=session_id,
                    system_append=None if session_id else PANEL_BRIEFING)
    proc = subprocess.Popen(cmd, cwd=REPO_ROOT, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True, bufsize=1,
                            env=_brain_env())   # least-privilege: strip store/factory secrets from the child env

    sid = session_id
    try:
        for line in proc.stdout:
            if should_stop and should_stop():
                proc.terminate()
                return
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except ValueError:
                continue                                      # non-JSON chatter on stdout — skip, the result event is the contract
            et = ev.get("type")
            if et == "system" and ev.get("subtype") == "init":
                sid = ev.get("session_id") or sid
                yield {"type": "init", "session_id": sid}
            elif et == "assistant":
                for block in (ev.get("message") or {}).get("content") or []:
                    if block.get("type") == "text" and block.get("text"):
                        yield {"type": "text", "text": block["text"]}
                    elif block.get("type") == "tool_use":
                        inp = block.get("input") or {}
                        detail = (inp.get("file_path") or inp.get("path") or inp.get("pattern")
                                  or inp.get("command") or inp.get("description") or "")
                        yield {"type": "tool", "name": block.get("name", "?"),
                               "detail": str(detail)[:160]}
            elif et == "result":
                yield {"type": "done", "result": (ev.get("result") or "")[:4000],
                       "session_id": ev.get("session_id") or sid,
                       "num_turns": ev.get("num_turns"),
                       "is_error": bool(ev.get("is_error"))}
        rc = proc.wait(timeout=30)
        if rc != 0:
            err = (proc.stderr.read() or "")[:1500]
            yield {"type": "error", "error": f"claude exited {rc}: {err}"}
    finally:
        if proc.poll() is None:
            proc.terminate()
