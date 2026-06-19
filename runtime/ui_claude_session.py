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
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PANEL_PERMISSION = os.environ.get("COMPANY_PANEL_PERMISSION", "plan")
# Where the DNA design standard lives (the VOICE face: design/dna/voice.json). The RHM's spoken
# register RESOLVES from DNA's standard (operator_voice.rhm_spoken) rather than hardcoding it — when
# DNA calibrates that node, the RHM inherits the change with no code edit. Env-overridable so the path
# is not baked (path-read source, the developer call; no DNA action needed to consume it).
COMPANY_DNA_DIR = os.environ.get("COMPANY_DNA_DIR", "/home/tim/repos/counterpart/design/dna")
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

# ── PANEL_BRIEFING: the RHM's spoken-voice system prompt (import-time-composed) ────────────────────
# The spoken VOICE REGISTER (how the right-hand-man sounds — second-person, brief-lead+offer-deeper,
# phone-aware, translate-not-leak, answer-from-context) RESOLVES from the DNA standard at
# COMPANY_DNA_DIR/voice.json → node operator_voice.rhm_spoken. The voice CONTENT is Tim's authority
# (DNA derives it from his real language); this module only WIRES the resolve — it composes the
# voice instruction FROM rhm_spoken's `is` + `properties`, it does NOT author voice rules. So when
# DNA calibrates rhm_spoken (refines a property, adds elevated wording), the RHM inherits it with no
# code change. The non-voice parts (decisions-grounding, point-as-you-speak cadence, the build-this
# approval-gate, the answer-from-context behavioural enforcement, never-claim) are BEHAVIOURAL WIRING,
# not the voice register — they stay hardcoded here.
#
# DEGRADE-CLEAN (no-silent-failure): if voice.json is missing / unreadable / malformed, or the
# rhm_spoken node is absent / empty, the voice register FALLS BACK to _FALLBACK_VOICE_REGISTER below
# (which equals the as-is deposited rhm_spoken properties) so the RHM NEVER loses its voice — and the
# fallback is surfaced honestly on stderr, never a silent empty briefing. The bar: PANEL_BRIEFING is
# ALWAYS a valid, non-empty voice instruction.

# The voice register exactly as DNA deposited it (rhm_spoken.is + the 5 properties, in prose). This is
# the degrade-clean floor — used verbatim when the DNA standard can't be resolved. It is NOT the live
# voice when the standard is reachable: then the register is composed from the live rhm_spoken node, so
# DNA's calibration flows through. (Source of these words: the as-is corpus DNA extracted FROM this very
# briefing — operator_voice.rhm_spoken.as_is_corpus; the fallback is that round-trip, not new authoring.)
_FALLBACK_VOICE_REGISTER = (
    "Speak as the right-hand-man's spoken prose — conversational, TO the operator. "
    "Address them as 'you' — SECOND PERSON, TO the operator, never ABOUT it. NEVER narrate ABOUT them in "
    "the third person and NEVER use their name in your reply (no 'the operator is…') — speak TO them, not "
    "about them. Keep every answer a tight 2-3 sentence lead plus an offer to go deeper, EVERY turn (the "
    "operator often asks several in a row; brevity is not just for the first question — give the one-breath "
    "essence, then OFFER to go deeper, 'want me to say more?', and expand only if they ask). Stay "
    "phone-aware — a wall of text buries what it describes: it fills the screen, HIDES the very thing "
    "you're describing, and gets cut off at the bottom so they miss there's more. Translate, never leak — "
    "never a machine-name, file path, identifier, URL, or scheme:// string (e.g. ui://… / run://… / "
    "code://…); ALWAYS give the plain human meaning. They are not a developer and never read code: explain "
    "at their altitude (what this is, what it means for you), never file-dumps. Answer from the context you "
    "are given — an orientation question is answered, not researched."
)

# The non-voice behavioural wiring — kept hardcoded (these are mechanism, not the voice register): the
# spoken-form constraint (plain text, no markdown), the decisions-grounding, the answer-from-context
# ENFORCEMENT (do-not-investigate), the build-this approval gate, the point-as-you-speak cadence, and
# the never-claim line. Only the VOICE REGISTER above resolves from DNA.
_BEHAVIOURAL_WIRING = (
    "Write as SPOKEN PROSE — a voice talking TO them, NOT a document: NO markdown — no **bold**, no "
    "'-'/'*' bullet lists, no # headers, no `backticks` — just plain sentences (the reply renders as "
    "plain text, so any markdown shows as literal asterisks). "
    "★ DECISIONS WAITING: when they ask what decisions are open/waiting/pending for them, use the "
    "decisions tool — it is the SAME canonical set shown in their inbox; name them plainly by name and "
    "never show any item code; do NOT use the surfaced-items tool or memory recall for this (those are "
    "different things and will contradict what they see). "
    "★★ DO NOT INVESTIGATE to answer an orientation question — NOT even if the context seems thin. If "
    "your context is sparse, that is FINE: say briefly + honestly what you CAN from it ('You're looking "
    "at part of your instrument surface — I don't have finer detail on this exact spot') and OFFER to "
    "look closer ('want me to dig in?'), then STOP and let them choose. NEVER launch tools / read the "
    "codebase / spawn agents to ground an orientation answer — that hangs the turn and never reaches "
    "them. Investigate ONLY when they EXPLICITLY ask you to dig into a specific thing. "
    "You are in a restricted permission mode: when a change is wanted, DESCRIBE it crisply and tell them "
    "to press 'build this' — the change flows through the system's approval gate. "
    "★ POINT AS YOU SPEAK (do this OFTEN — it's how you guide their eye, the whole point of being their "
    "guide): your context may include a 'Things you can point at' list — each an opaque token + a human label "
    "describing it. WHENEVER your reply names or describes one of those things — INCLUDING a broad overview "
    "that mentions several, and ESPECIALLY when you walk them through the surface — match what you're "
    "describing to its label in the list and call the point tool with that token, right as you say it. "
    "Example: if you say 'a live map' and the list has a token labelled 'the live map…', call point with that "
    "token at that moment; then if you mention 'the controls' or 'the time scrubber', point at each as you "
    "name it. Don't point on narrow questions only — point THROUGH a broad answer too, one thing at a time, "
    "as you name each (a walkthrough that names the map, the lens, and the scrubber should fire point three "
    "times, in order). Match by the label's MEANING (your words won't be identical to the label); point ONLY "
    "at tokens in the list; never invent one; if the list is absent, just speak normally. "
    "Never claim something works without having checked."
)

# The fixed identity preamble (framing, not the resolvable voice register): WHO the brain is and WHO it
# addresses. Kept hardcoded; the resolved register supplies HOW it sounds.
_IDENTITY_PREAMBLE = (
    "You are Claude Code, the right-hand-man embedded inside the Company's own interface, talking DIRECTLY "
    "TO the operator. "
)


def _resolve_voice_register() -> str:
    """RESOLVE the RHM's spoken-voice register from the DNA standard (COMPANY_DNA_DIR/voice.json →
    operator_voice.rhm_spoken), composing the voice instruction FROM the node's `is` + `properties`.
    DEGRADE-CLEAN: any failure (missing/unreadable/malformed file, absent node, or empty/blank content)
    returns _FALLBACK_VOICE_REGISTER and surfaces the fallback on stderr — NEVER an empty string, never
    silent. Composing from the deposited properties is WIRING; this invents no voice content."""
    path = os.path.join(COMPANY_DNA_DIR, "voice.json")
    try:
        with open(path, encoding="utf-8") as fh:
            dna = json.load(fh)
        rhm = (dna.get("operator_voice") or {}).get("rhm_spoken") or {}
        is_line = str(rhm.get("is") or "").strip()
        # The PROPERTIES are the substance (the voice rules); `is` is one-line framing. Only real strings
        # count — and `properties` MUST be a list: a string-typed value (malformed deposit) would otherwise
        # iterate CHARACTERS into garbage, so guard the type before iterating.
        raw_props = rhm.get("properties")
        props = ([str(p).strip() for p in raw_props if isinstance(p, str) and str(p).strip()]
                 if isinstance(raw_props, list) else [])
        # Explicit empty-content guard: an absent / empty / mistyped properties list is NOT an exception,
        # but it leaves no voice rules — degrade-clean to the fallback rather than ship a ruleless briefing.
        if not props:
            raise ValueError("rhm_spoken has no usable `properties` (the voice rules)")
        # COMPOSE the register from the LIVE node: the `is` frames the voice, each property is a rule. Minimal
        # connective tissue only (no elaboration — elaborating would be authoring voice, forbidden). So when DNA
        # refines a property or adds elevated wording, this register inherits it verbatim with no code change.
        parts = []
        if is_line:
            parts.append("Speak as " + is_line + ".")
        for p in props:
            parts.append(p[0].upper() + p[1:] + "." if p else p)
        register = " ".join(parts).strip()
        if not register:                                          # belt: composition yielded nothing → degrade
            raise ValueError("composed voice register is empty")
        return register
    except Exception as e:
        # NO silent failure: surface the degrade honestly (operator never loses the voice; we just lost the
        # DNA-calibrated wording for this process). Matches the runtime's stderr-warn convention.
        print(f"[ui-claude-session] WARN voice-register resolve failed ({type(e).__name__}: {e}); "
              f"falling back to the deposited rhm_spoken register (path={path})",
              file=sys.stderr, flush=True)
        return _FALLBACK_VOICE_REGISTER


# Composed at import: identity preamble + the RESOLVED voice register + the non-voice behavioural wiring.
# Import-time-loaded by the bridge → a DNA calibration goes live on the next bridge restart (coordinated
# separately). Always a valid, non-empty instruction (the register is degrade-clean above).
PANEL_BRIEFING = _IDENTITY_PREAMBLE + _resolve_voice_register() + " " + _BEHAVIOURAL_WIRING


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


def _render_pointables(pointables) -> str:
    """The per-turn 'things you can point at' catalog → a prompt block (opaque token + human label, NEVER
    an address — addresses stay client-side, operator-law). The brain calls point(<token>) when it names
    one. The live set varies per turn (the surface sends only what's currently on screen), so this rides
    the PER-TURN prompt, not the persistent system-append. Empty/absent → no block (brain speaks normally)."""
    if not pointables:
        return ""
    lines = []
    for p in pointables:
        if not isinstance(p, dict):
            continue
        tok = str(p.get("token") or "").strip()
        lab = str(p.get("label") or "").strip()
        if tok and lab and "://" not in tok:            # operator-law belt: a token is opaque, never an address
            lines.append(f'- "{tok}" — {lab}')
    if not lines:
        return ""
    return ('[Things you can point at — call point("<token>") the moment you name one, so the surface '
            'highlights it as you speak]\n' + "\n".join(lines))


def run_turn(prompt: str, *, session_id: str | None = None, context_block: str | None = None,
             pointables: list | None = None, should_stop=None):
    """One panel turn → a generator of panel events (dicts, ready for ndjson):
       {type:'init', session_id} · {type:'text', text} · {type:'tool', name, detail} ·
       {type:'point', token} · {type:'done', result, session_id, num_turns?} · {type:'error', error}.
    `context_block` (the pointed-at address's help bundle) is folded into the prompt — per-turn
    context, exactly the indicated-chip semantics of the RHM chat. `pointables` (a per-turn [{token,label}]
    catalog the surface sources) is folded in too → the brain points at on-screen things via the point verb
    (→ a {type:'point', token} event; the client maps token→ui:// + dispatches). `should_stop()` (client
    gone) terminates the subprocess — a hung panel never strands a claude process."""
    full_prompt = f"[Operator context — what Tim is pointing at]\n{context_block}\n\n{prompt}" \
        if context_block else prompt
    pblock = _render_pointables(pointables)
    if pblock:
        full_prompt = f"{pblock}\n\n{full_prompt}"
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
                        name = block.get("name", "?")
                        inp = block.get("input") or {}
                        # the RHM's POINT verb → a dedicated {type:'point', token} event (fork-brain-core maps
                        # the opaque token → ui:// client-side + dispatches ui:point). No address rides here.
                        if name == "mcp__company__point" or name.split("__")[-1] == "point":
                            tok = str(inp.get("token") or "").strip()
                            if tok:
                                yield {"type": "point", "token": tok}
                        else:
                            detail = (inp.get("file_path") or inp.get("path") or inp.get("pattern")
                                      or inp.get("command") or inp.get("description") or "")
                            yield {"type": "tool", "name": name, "detail": str(detail)[:160]}
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
