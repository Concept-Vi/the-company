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
dependency; mirrors implement.py's subprocess discipline."""
import json
import os
import subprocess

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PANEL_PERMISSION = os.environ.get("COMPANY_PANEL_PERMISSION", "plan")
CLAUDE_BIN = os.environ.get("COMPANY_CLAUDE_BIN", "claude")
TURN_TIMEOUT_S = int(os.environ.get("COMPANY_PANEL_TIMEOUT_S", "600"))

PANEL_BRIEFING = (
    "You are Claude Code embedded as the BUILDER side-panel inside the Company's own interface. "
    "The operator is Tim — he is not a developer and never reads code; explain everything in plain "
    "language at his altitude (what it does, what it means for him — never file-dumps). He points at "
    "interface elements; their address context arrives with his messages. You may investigate freely "
    "(read, search, run read-only commands). You are in a restricted permission mode: when a change "
    "is wanted, DESCRIBE the change crisply and tell him to press 'build this' — the change then "
    "flows through the system's approval gate. Never claim something works without having checked."
)


def _turn_cmd(prompt: str, *, resume: str | None, system_append: str | None) -> list:
    cmd = [CLAUDE_BIN, "-p", prompt, "--output-format", "stream-json", "--verbose",
           "--permission-mode", PANEL_PERMISSION]
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
                            stderr=subprocess.PIPE, text=True, bufsize=1)
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
