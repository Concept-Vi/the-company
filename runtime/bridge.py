"""runtime/bridge.py — the UI face (C8, skeleton form). Thin HTTP over the shared Suite.

Serves the operator console + state/action. Same brain (runtime.suite.Suite) and same
substrate (the store at fcfg.STORE_DIR) as the MCP face — so the agent and the UI operate
ONE system. Stdlib http only. See contracts/C8.

Run: python3 runtime/bridge.py [port]   then open http://localhost:8770
"""
from __future__ import annotations
import json
import os
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from contracts.node_record import NodeInstance, Edge, Graph
from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite
from runtime import generate_mockup            # the committed generate-for-mockups ENGINE (own-test green)
from runtime import activation_driver          # Group H/I — the always-on activation CALLER (dormant-by-default)
from runtime import cognition as _cog          # the ONE cognition engine (run_role/run_items/run_reduce/
#                                                resolve_address) — the SAME functions mcp_face/server.py calls
from fabric import config as fcfg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANVAS = os.path.join(ROOT, "canvas", "index.html")

# BRIDGE_ROUTES — the SINGLE SOURCE of the bridge route table (registry-is-truth, AGENTS.md rules 3+8).
# Every path the do_GET/do_POST dispatcher handles via a `path == "…"` / `self.path == "…"` literal is
# listed here ONCE. `Suite.capabilities()['api_verbs']` PROJECTS the /api/* subset from this (a projection by
# the INTRINSIC path-prefix, NOT a hand-maintained classification) — so adding an /api/ route here makes it
# appear in capabilities() with no second list to keep in sync (this de-hardcodes the old literal api_verbs
# list suite.py carried, which suite.py couldn't derive because it can't import bridge.py at module load —
# capabilities() lazy-imports BRIDGE_ROUTES at call time, when both modules are loaded). The TEETH that make
# this the single source rather than a relabeled third copy: tests/bridge_routes_acceptance.py greps the
# dispatcher's `path ==` / `self.path ==` literals and fail-louds if this set drifts from them (both
# directions) — so a route can't be dispatched-but-unlisted or listed-but-undispatched. Add/remove a route
# in do_GET/do_POST ⇒ add/remove it HERE (or the drift test fails loud). Non-/api paths (the served pages
# `/studio`, `/design-system.css`, the `/mockups/` prefix) are part of the table but excluded from api_verbs
# by the /api/ projection.
BRIDGE_ROUTES = (
    # served pages / static (non-/api — in the table, excluded from api_verbs by the prefix projection)
    "/studio", "/design-system.css", "/mockups/",
    # --- GET routes ---
    "/api/stream", "/api/mockup-feedback", "/api/mockup-feedback/status", "/api/corpus", "/api/graph",
    "/api/graphs", "/api/object_info", "/api/cognition_info", "/api/types", "/api/layers", "/api/models",
    "/api/chat-models", "/api/fit", "/api/surfaced", "/api/events", "/api/now", "/api/chat",
    "/api/conversations", "/api/conversation", "/api/rhm-config", "/api/inbox", "/api/last-change",
    "/api/self-change-log", "/api/panels", "/api/capabilities", "/api/capabilities/introspection",
    "/api/ui_info", "/api/scope",
    "/api/address-help", "/api/context", "/api/up-translate", "/api/self-changes-at", "/api/annotations",
    "/api/presentation-pref", "/api/chats", "/api/address-history", "/api/stale-at", "/api/ref-versions",
    "/api/review/current", "/api/review/status", "/api/journey/replay", "/api/journeys", "/api/voice",
    "/api/personas", "/api/trial/sessions", "/api/trial/transcript", "/api/cognition/models_for_role",
    "/api/cognition/inputs", "/api/cognition/field_types", "/api/cognition/list_runs",
    "/api/cognition/find_runs", "/api/cognition/find_relations", "/api/cognition/corpus", "/api/roles",
    "/api/run-stats", "/api/knobs", "/api/voice/engine-knobs", "/api/voice/paths",
    # --- POST routes ---
    "/api/stt", "/api/voice/stt-partial", "/api/tts", "/api/voice/finished-thought", "/api/voice/switch",
    "/api/voice/log", "/api/run", "/api/set", "/api/move", "/api/node", "/api/connect", "/api/delete-node",
    "/api/conversation/new", "/api/model/load", "/api/model/config", "/api/mode", "/api/coa",
    "/api/surface-output", "/api/surface-review", "/api/capture-idea", "/api/defer-offer",
    "/api/revive-offer", "/api/build-intent", "/api/cognition/create_role", "/api/cognition/create_skill",
    "/api/cognition/create_context", "/api/act", "/api/annotate", "/api/apply",
    "/api/propose", "/api/decision", "/api/resolve", "/api/revert", "/api/checkpoint", "/api/pin",
    "/api/react", "/api/attach-chat", "/api/approve-reach", "/api/intent-at",
    "/api/review/start", "/api/review/next", "/api/guide/start", "/api/walkthrough/start",
    "/api/journey/start", "/api/journey/step", "/api/journey/stop", "/api/debrief/start",
    "/api/mockup-generate", "/api/cognition/embed", "/api/cognition/preview_turn",
    "/api/cognition/run_role", "/api/cognition/run_items", "/api/cognition/run_reduce",
    "/api/cognition/role/propose", "/api/cognition/role/edit", "/api/cognition/role/delete",
    "/api/cognition/role/dry_run", "/api/cognition/rule/attach", "/api/cognition/rule/detach",
    "/api/cognition/rule/validate", "/api/cognition/rule/dry_run", "/api/trial/turn",
    "/api/trial/feedback", "/api/trial/reflection",
    # Group H/I — the always-on CALLER seam (manual/external drive of one activation tick). The autonomous
    # background loop behind this caller is OFF by default (COMPANY_ACTIVATION_LOOP, needs-tim); this POST
    # is the LIVE manual-drive door (firing it fires roles = computation, floor-clean by construction).
    "/api/activation/tick",
    # S1 (overnight) — the BUILDER side-panel: one streaming turn of the embedded Claude Code session.
    # OPERATOR FACE ONLY (never on mcp_face); plan-mode by default (COMPANY_PANEL_PERMISSION).
    "/api/claude/turn",
    # S2 (overnight) — the GREETING (caught-up-in-one-glance: the night/away-time at Tim's altitude).
    "/api/greeting",
    # S7 (overnight) — the FORAGER's search door: semantic corpus query (+ record heads) for the canvas.
    "/api/corpus-query",
    # THE UNIVERSAL PROJECTION (Tim Geldard's equation, 2026-06-13) — the stores rendered for free:
    # θ=kind (the sector registry), r=time-from-NOW, depth=nesting, phases=the ts cycles. Pure read.
    "/api/projection",
    # Group 11 — the SCALE pyramid build trigger (POST): (re)cluster a lens space's unit vectors into the
    # nested rung centroids the meaning-field's ?rung= resolves over. The discoverable rebuild path (the
    # pyramid is derived .data — this is how it's regenerated, not a manual script). GET = the built rungs.
    "/api/scale/build",
    # Proposal lifecycle (RG8/RG9) — dispatched since the register build but MISSING here until the
    # F1.5 contract lane's drift-gate run caught it (the gate working as designed, both directions).
    "/api/registry/proposals",
    "/api/registry/approve",
    # Voice/chat streaming doors — dispatched via the split("?")[0] form; invisible to the registry
    # until the extractor learned that form (same F1.5 drift-gate catch).
    "/api/chat/stream",
    "/api/voice/stream",
    "/api/voice/turn",
    # The ③④⑤ command-wrapper routes (/api/config/* /api/dev/* /api/auto/*) were REMOVED 2026-06-13
    # (Session Fabric R1.4): they hand-wrapped what a real Claude Code session does natively
    # (settings/hooks/mcp/git/scheduling via its own CLI). The fabric drives REAL sessions instead —
    # surface, don't rebuild. See build-prep "Session Fabric — Operational Requirements.md" §R1.4.
)

MOCKUPS_DIR = os.path.join(ROOT, "design", "mockups")           # the design-review portal + corpus
FEEDBACK_DIR = os.path.join(MOCKUPS_DIR, ".feedback")           # one JSONL per mockup (filename-keyed)
DESIGN_CSS = os.path.join(ROOT, "design", "design-system.css")  # the generated corpus stylesheet


def _safe_mockup_path(name):
    """Resolve a mockup FILENAME (e.g. 'IA-mobile.html') to its absolute path under MOCKUPS_DIR,
    path-safe. A bare basename only — `..`, slashes, backslashes are refused BEFORE realpath; then a
    realpath-contains check is the second wall (defence in depth, never one gate). Returns the abs path
    or raises ValueError (→ 400, fail loud). The caller still checks os.path.isfile for a 404."""
    import re as _re
    if not isinstance(name, str) or not _re.fullmatch(r"[A-Za-z0-9._-]+\.html", name):
        raise ValueError(f"refused mockup name {name!r}: must be a bare <file>.html basename (no path)")
    p = os.path.realpath(os.path.join(MOCKUPS_DIR, name))
    if os.path.commonpath([p, os.path.realpath(MOCKUPS_DIR)]) != os.path.realpath(MOCKUPS_DIR):
        raise ValueError(f"refused mockup name {name!r}: resolves outside the mockups dir (traversal)")
    return p


def _feedback_path(mockup):
    """The JSONL path for a mockup's feedback thread — design/mockups/.feedback/<mockup>.jsonl, where
    <mockup> is the FULL filename incl. .html (contract §21). Validates the mockup name the same way as
    static serving (one gate, reused) so a junk `?mockup=` can never escape FEEDBACK_DIR. Raises ValueError
    (→ 400) on a bad name. Does NOT require the mockup file to exist (feedback can predate a render)."""
    import re as _re
    if not isinstance(mockup, str) or not _re.fullmatch(r"[A-Za-z0-9._-]+\.html", mockup):
        raise ValueError(f"refused mockup name {mockup!r}: must be a bare <file>.html basename (no path)")
    p = os.path.realpath(os.path.join(FEEDBACK_DIR, mockup + ".jsonl"))
    if os.path.commonpath([p, os.path.realpath(FEEDBACK_DIR)]) != os.path.realpath(FEEDBACK_DIR):
        raise ValueError(f"refused mockup name {mockup!r}: resolves outside the feedback dir (traversal)")
    return p


def _read_feedback(mockup):
    """Read a mockup's feedback thread → list of entries (oldest-first), [] if no file. Each line is one
    JSON entry {id,mockup,element,text,ts,status}. A malformed line is SKIPPED with a stderr warn (never a
    silent total loss — one bad line shouldn't blank the thread; the warn surfaces it for repair)."""
    path = _feedback_path(mockup)
    if not os.path.isfile(path):
        return []
    out = []
    with open(path, "r", encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            try:
                out.append(json.loads(ln))
            except json.JSONDecodeError as e:
                print(f"[bridge] WARN skipping malformed feedback line in {path}: {e}", file=sys.stderr, flush=True)
    return out


# STUDIO CORPUS (G4 fix) — the gallery binds the REAL corpus, never a hardcoded FE list. The corpus IS
# the set of mockup files ACTUALLY on disk under design/mockups/ (so it can never drift from reality — a
# new mockup file appears the moment it lands; a removed one disappears). `_CORPUS_META` is the curated
# join layer: per file, its human title, its platform tag (desktop|mobile|tool), its group label (for the
# rail's sections), and the REVIEWED-SURFACE `ui://` address the mockup depicts (so a gallery Card carries
# that address as its data-ui-ref → the document-level capture listener indicates it → chat/address-help/
# annotate all bind to that locus for free). A file with NO meta entry STILL appears (honest, never
# dropped) with a derived title + an UNGROUPED bucket — the corpus is truth, the meta is only enrichment.
# STUDIO.html itself is excluded (it is the legacy standalone tool, not a reviewable surface).
# _CORPUS_META — a DECLARED registry (design/_system/corpus-meta.json), NOT a hardcoded code dict
# (no-hardcoding / registry-is-truth law, Tim 2026-06-09 — this WAS an inline dict, a flagged violation).
# Shape {file: [title, platform, group, address]}; a JSON list unpacks exactly like the old 4-tuple, so the
# `_corpus_index` consumer is byte-unchanged. WHY it's now data: the generate engine (runtime/generate_mockup)
# can read the SAME file to map a mockup → its ui:// address WITHOUT importing bridge.py — the prerequisite
# for the comment→generate loop (F2/Q1: gather a mockup's annotations at its address). Editing the corpus =
# editing the JSON, no code change.
_CORPUS_META_PATH = os.path.join(ROOT, "design", "_system", "corpus-meta.json")
with open(_CORPUS_META_PATH, encoding="utf-8") as _cf:
    _CORPUS_META = json.load(_cf)


def _corpus_index():
    """The studio gallery's corpus (G4): every reviewable mockup file actually present under
    design/mockups/, joined to its curated meta. Registry-is-truth — the disk listing is the source, the
    FE never carries a hardcoded list. Returns a list of {file, title, platform, group, address}, sorted
    by (group, file) so the rail's sections are stable. A file with no meta still appears (group
    'ungrouped', a title derived from the filename, address None) — fail-loud-friendly: a new mockup is
    visible immediately, never silently absent. STUDIO.html is excluded (the legacy tool, not a surface)."""
    out = []
    try:
        names = sorted(n for n in os.listdir(MOCKUPS_DIR)
                       if n.endswith(".html") and n != "STUDIO.html")
    except FileNotFoundError:
        names = []
    for n in names:
        meta = _CORPUS_META.get(n)
        if meta:
            title, platform, group, address = meta
        else:
            title = n[:-5].replace("-", " ")   # derived, honest title for an un-curated file
            platform, group, address = "desktop", "ungrouped", None
        out.append({"file": n, "title": title, "platform": platform, "group": group, "address": address})
    out.sort(key=lambda r: (r["group"], r["file"]))
    return out


TTS_URL = os.environ.get("COMPANY_TTS_URL", "http://127.0.0.1:4123")   # local Kokoro service (default engine)

# voice-trial lane B — multi-engine TTS routing. The voice-module builder writes each engine as an
# HTTP service mirroring tts_service.py's contract (POST /tts {text,voice?,speed?}->wav · GET
# /voices · GET /health) on its OWN port. This map is the ONE source of truth for the port routing
# (used by BOTH /api/tts routing AND /api/voice status). The DEFAULT engine "kokoro" routes to
# TTS_URL (so COMPANY_TTS_URL still overrides the default — we do NOT hardcode kokoro to 4123 here,
# which would silently break that override). An absent `engine` field → kokoro (unchanged
# behaviour). An UNKNOWN engine → fail loud (no silent fallback to kokoro).
ENGINE_PORTS = {"chatterbox": 4124, "orpheus": 4125, "cosyvoice": 4126,
                "xtts": 4127, "qwen3tts": 4128}


def _apply_model_ctx(key, ctx, *, restart=True):
    """Set a config-model's context window, auto-sizing gpu_util from its measured `_profile` so vLLM
    gets the KV pool that ctx needs, then (optionally) restart it — budget-gated (fail loud, never OOM).
    SHARED (one source) by /api/model/config AND /api/voice/switch's co-residence shrink. Returns a dict."""
    import sys as _sys
    _ops = os.path.join(ROOT, "ops", "cli")
    if _ops not in _sys.path:
        _sys.path.insert(0, _ops)
    import gpu as _gpu, systemd as _sd, registry as _reg
    reg = _reg.load()
    if key not in reg["services"]:
        raise ValueError(f"unknown service {key!r}")
    _reg.set_config(reg, key, "max_model_len", int(ctx))
    reg = _reg.load(); c = reg["services"][key].get("config", {}); auto_util = None
    prof = c.get("_profile")
    if prof and prof.get("fixed_mb") and prof.get("kv_kb_per_token"):
        need = prof["fixed_mb"] + int(ctx) * prof["kv_kb_per_token"] / 1024.0 + 500
        auto_util = min(0.92, round(need / _reg.ceiling_mb(reg) + 0.005, 2))
        _reg.set_config(reg, key, "gpu_util", auto_util)
    reg = _reg.load(); svc = reg["services"][key]
    if not restart or _sd.is_active(svc) != "active":
        return {"service": key, "max_model_len": int(ctx), "auto_util": auto_util, "restarted": False,
                "note": "saved — applies when the service next starts"}
    new_budget = _gpu.budget_vram(reg, key)
    others = sum(mb for k, mb in _gpu.running_gpu_services(reg) if k != key)
    if new_budget + others > _reg.ceiling_mb(reg):
        return {"service": key, "max_model_len": int(ctx), "auto_util": auto_util, "restarted": False,
                "error": f"{key} at {ctx} needs ~{new_budget} MB; {others} MB held by other GPU services → "
                         f"{new_budget+others} MB > {_reg.ceiling_mb(reg)} MB card. Not restarting (would OOM).\n"
                         + _gpu.format_state(reg)}
    started, msg = _sd.control(svc, "restart")
    return {"service": key, "max_model_len": int(ctx), "auto_util": auto_util, "restarted": started,
            "note": (msg if started else "restart failed: " + str(msg))}


def _local_brain_key(reg, rc):
    """The registry service key of the ACTIVE brain IF it's a local GPU model (config.model == the
    rhm_config model, group 'brain'); else None (a cloud/ollama brain has no VRAM to size). So the
    co-residence shrink only ever touches the local brain it's actually running."""
    model = (rc.get("model") or "").strip()
    if not model:
        return None
    return next((k for k, s in reg["services"].items()
                 if s.get("group") == "brain" and (s.get("config") or {}).get("model") == model), None)


def _tts_base_url(engine: str | None) -> str:
    """The base URL for a TTS engine. kokoro / None → TTS_URL (env-overridable default). A mapped
    engine → its 127.0.0.1:<port>. An unknown engine → ValueError (fail loud, names the known set —
    NEVER a silent fallback to kokoro, which would mask a typo and ship the wrong voice)."""
    if not engine or engine == "kokoro":
        return TTS_URL
    if engine not in ENGINE_PORTS:
        raise ValueError(
            f"unknown TTS engine {engine!r} — known: {['kokoro'] + sorted(ENGINE_PORTS)}. "
            f"Refusing to fall back to kokoro silently (fail loud).")
    return f"http://127.0.0.1:{ENGINE_PORTS[engine]}"


# --- Concurrent Cognition G6: voice coupling — the PART is the TTS streaming unit ----------------
# The streaming core, FACTORED OUT of the HTTP handler so it is testable WITHOUT a socket (same path,
# not a parallel one — reuse-don't-parallel). It drives a `chat_parts()` GENERATOR through a
# brain-producer THREAD into a thread-safe queue while the CALLING thread (the one that owns the
# socket) synthesises + emits each completed part's sentences. THAT is the brain↔TTS OVERLAP (C6.1):
# a naive `for part in gen: synth(part)` gives ZERO overlap — yielding suspends the generator, so
# part N+1 isn't generated until part N's synth returns (sequential). The producer thread keeps the
# brain running AHEAD of synthesis.
#
# Contract with chat_parts() (G4, already built — we CONSUME it, never re-implement staging):
#   • each yield is {"part": N, "text": <complete sub-generation>, "final": bool, "staged": bool, ...}
#   • the epilogue (the SINGLE chat-history append + the SINGLE _emit("chat") for the WHOLE turn) runs
#     INSIDE the generator, right before its FINAL yield. So draining to the final yield gives us the
#     "ONE chat event regardless of N parts" preserve-item FOR FREE — we must NOT emit our own chat
#     event and must NOT call SUITE.chat. A cancelled turn that stops draining never reaches the
#     epilogue → records no chat turn (a speculative turn the operator interrupted — stated, not silent).
#   • the assembled FULL reply lives in: final["result"]["reply"] (staged + bypass paths) OR
#     final["early_return"]["reply"] (off/refusal prologue short-circuit). We read it from THERE (what
#     the epilogue actually wrote to history), never a manual re-join of part texts.
def _stream_parts(parts_gen, *, speak_fn, emit_fn, gone, split_sentences, on_part=None, should_stop=None,
                  clean_fn=None):
    """Drive a chat_parts() generator with brain↔TTS overlap. Pure of HTTP — the caller passes:
      • parts_gen      — an iterator of part dicts (SUITE.chat_parts(...) or a test stub)
      • speak_fn(text) — synth ONE sentence → wav bytes (voice_loop.speak bound to engine+voice)
      • emit_fn(obj)   — emit ONE ndjson event (the SINGLE emitter — owns ordering; the producer never emits)
      • gone           — a 1-element mutable [bool]: True ⇒ client disconnected, STOP (cancellation)
      • split_sentences(text) -> [str]  — the per-part sentence split (the existing re.split)
      • on_part(text)  — optional callback per completed part (e.g. a {type:part} event)
      • clean_fn(text) -> str  — V-C/V-D the SPEAKABLE LAYER (optional; None = identity). Applied to a
                         WHOLE PART's text BEFORE the sentence split (cleaning per-CHUNK would split markdown
                         — code fences/lists span sentences; a PART is a coherent reply segment, so per-part
                         is the correct granularity). Strips markdown/code/urls/emoji + maps expression tags
                         to the bound engine's syntax. The RAW part text still flows to `on_part` (the
                         {type:part} display event) + the assembled reply (the {type:reply} event + trial
                         recording, owned by the caller); ONLY what hits TTS (speak_fn) is cleaned. Fail-loud
                         (rule 4): a part that cleans to EMPTY raises ValueError on this thread → the caller's
                         try/except surfaces {type:error} + the durable log (never silent synth of silence).
      • should_stop()  — optional PROACTIVE disconnect probe (the handler's client_gone — select+MSG_PEEK).
                         The consumer polls it before each synth and folds its verdict into gone[0], so a
                         disconnect during a long part-GENERATION (no emits in flight) is noticed promptly
                         — preserving the original synth-loop's proactive cancel, not just reactive
                         emit-failure detection. Both the consumer (before synth) and the producer (before
                         the next part) read gone[0].
    Returns {"reply": <assembled full reply>, "parts_done": int, "parts_total": int,
             "chunks_done": int, "chunks_total": int, "cancelled": bool, "staged": bool}.
    FAIL LOUD: a brain exception on the producer thread is re-raised on THIS thread (so the handler's
    try/except surfaces {type:error} + the durable log) — never swallowed into a silent short stream."""
    import queue as _q
    import threading as _thr
    SENTINEL = object()
    q: "_q.Queue" = _q.Queue()
    prod_err: dict = {}
    final_holder: dict = {}

    def _produce():
        # Pull parts AHEAD of synthesis. Between parts, honour cancellation: BEFORE pulling the next part
        # (which is where the brain spends its compute — generating part N+1), check gone[0]; if the
        # client went away, close the generator (unwinding chat_parts' own daemon wave thread) and STOP
        # — the next part is NEVER generated (C6.1 cancel gates part-GEN). The brain keeps generating
        # part N+1 while the consumer synths part N — the overlap.
        try:
            while True:
                if gone[0]:                                  # client gone → do NOT generate the next part
                    break
                try:
                    part = next(parts_gen)                   # pull (generate) the next part — the brain compute
                except StopIteration:
                    break
                if part.get("final"):
                    final_holder["final"] = part            # carries result/early_return → the full reply
                q.put(part)
        except BaseException as e:                           # a brain failure → re-raise on the consumer (fail loud)
            prod_err["err"] = e
        finally:
            try:
                parts_gen.close()                            # idempotent; unwinds a suspended generator
            except Exception:
                pass
            q.put(SENTINEL)

    producer = _thr.Thread(target=_produce, name="voice-brain-producer", daemon=True)
    producer.start()

    import queue as _q2
    idx = 0                                                  # MONOTONIC chunk index ACROSS ALL parts (playCursorRef ordering)
    parts_done = 0
    cancelled = False
    staged = False
    while True:
        # Poll for the next part; while WAITING (a long part-GENERATION with no sentences flowing) keep
        # the PROACTIVE disconnect probe live so a mid-generation disconnect is noticed promptly (it folds
        # into gone[0] → the producer stops generating the next part). select+MSG_PEEK is read-only — the
        # consumer is the only thread that probes the socket (no cross-thread socket race).
        while True:
            try:
                item = q.get(timeout=0.4)
                break
            except _q2.Empty:
                if should_stop is not None and should_stop():
                    gone[0] = True
                continue
        if item is SENTINEL:
            break
        part = item
        parts_done += 1
        if part.get("staged"):
            staged = True
        text = (part.get("text") or "").strip()
        if on_part is not None and text:
            on_part(text)                                    # the RAW part text (display/{type:part}) — never cleaned
        if text:
            # V-C/V-D: clean the WHOLE part to speakable prose BEFORE the sentence split (only the TTS-bound
            # text is cleaned; the raw `text` already went to on_part + rides into the assembled reply). A
            # clean-to-empty raises here (fail-loud) → re-raised on the handler thread below as the producer
            # err path does, surfacing {type:error}; we never hand the engine silence.
            spoken = clean_fn(text) if clean_fn is not None else text
            for sent in split_sentences(spoken):
                if should_stop is not None and should_stop():  # PROACTIVE probe (select+MSG_PEEK) → folds into gone[0]
                    gone[0] = True
                if gone[0]:                                  # client gone → STOP before the next synth (existing tier-2)
                    cancelled = True
                    break
                wav = speak_fn(sent)
                emit_fn({"idx": idx, "text": sent, "wav": wav})
                idx += 1
        if gone[0]:
            cancelled = True
            # client gone → DRAIN the rest of the queue to the SENTINEL (so the producer never blocks on
            # put()) then STOP the consumer (the producer closes the generator → the next part is never
            # generated; cancellation gates part-GEN, C6.1). Break the OUTER loop too — the sentinel is
            # consumed HERE, so returning to the outer q.get() would block forever (the deadlock).
            while q.get() is not SENTINEL:
                pass
            break

    producer.join(timeout=5)
    if prod_err.get("err") is not None:
        raise prod_err["err"]                                # FAIL LOUD on the handler thread

    final = final_holder.get("final") or {}
    if "result" in final and isinstance(final["result"], dict):
        reply = (final["result"].get("reply") or "")
    elif "early_return" in final and isinstance(final["early_return"], dict):
        reply = (final["early_return"].get("reply") or "")
    else:
        reply = ""
    return {"reply": reply, "parts_done": parts_done, "parts_total": parts_done,
            "chunks_done": idx, "chunks_total": idx, "cancelled": cancelled, "staged": staged}


SUITE = Suite(FsStore(fcfg.STORE_DIR),
              NodeRegistry().discover([os.path.join(ROOT, "nodes")]))
DEMO = "codebase"


def _semantic_projection(q, binding, reg, evs, center, now, lim):
    """THE CIRCLE (Group 6) + THE SCALE AXIS (Group 11) for the /api/projection semantic binding. Returns
    (status, body). The store/registry I/O lives HERE; project() stays PURE (vectors ride in keyed by the
    SAME _addr_of the projector uses).

    SCALE (Group 11): a binding whose `space` has a built pyramid gains a RUNG axis. `?rung=` selects it:
      · absent / 'unit' → the UNIT meaning-field (Group 6, unchanged) — every embedded item a point.
      · a coarse k present in the pyramid (e.g. 8, 32) → the THEME meaning-field: the points are the rung's
        cluster CENTROIDS (scale.rung_points), projected by the SAME instrument (same semantic radius, same
        angle, same centre) — "zoom changes which rung RESOLVES", not which renderer runs. Each coarse point
        carries its theme metadata (size / exemplar / member-count / finer children) so the surface can size
        + label it and zoom INTO it. EVERY response (unit or coarse) carries `scale` (space, current rung,
        the available rungs, n_units) so the FE can render the zoom ladder; absent when no pyramid is built.
    Fail-loud: a requested coarse rung with no built pyramid is simply ignored (falls to the unit field — the
    ladder is absent, never a faked coarse field); a malformed centre at a coarse rung → 400 (same as unit).
    """
    from datetime import datetime, timedelta, timezone
    from runtime.projection import project as _uproject, _addr_of as _proj_addr
    from runtime import scale as _scale

    space = binding.get("space")
    emb = q.get("emb") or binding.get("emb") or None   # embedder LAYER (None=BGE default); applies to UNIT reads
    # MRL semantic-zoom (the RESOLUTION axis): ?dim=N truncates every read vector to its first N dims before
    # the cosine — a Matryoshka coarse↔fine MEANING zoom, orthogonal to the rung pyramid (the 2-D scale:
    # rung × dim). ALL vectors (centre + items/themes) are truncated CONSISTENTLY so _cosine's dim-mismatch
    # guard never trips; None = full dim (byte-identical to pre-MRL). Same contract as nucleation's _mrl.
    _md = (q.get("dim") or "").strip()
    mdim = int(_md) if _md.isdigit() and int(_md) > 0 else None
    def _mrl(v):
        return v[:mdim] if (mdim and mdim < len(v)) else v
    rung = (q.get("rung") or "").strip()
    pyr = _scale.load_pyramid(SUITE.store, space, emb) if space else None
    rungs = [r["k"] for r in pyr["rungs"]] if pyr else []
    coarse_k = int(rung) if (rung.isdigit() and int(rung) in rungs) else None

    def attach_scale(body, current):
        if pyr:
            body["scale"] = {"space": space, "rung": current, "rungs": rungs,
                             "n_units": pyr.get("n_units")}
        body["binding"]["res"] = mdim     # the active MRL resolution (None = full dim) — every return path
        body["binding"]["emb"] = emb      # the active embedder LAYER (None = default/BGE) — echoed everywhere
        return body

    def centre_vector(c):
        """Resolve a centre's vector PORTABLY across rungs (so stepping the ladder while centred never 400s):
        a UNIT centre lives in the unit `space`; a THEME centre (`cluster://<space>/k<K>/<label>`) lives in
        its OWN rung's scale space — fetched from there regardless of which rung is being VIEWED (a k8 theme
        stays a valid centre at the k32 or unit rung — its centroid ranks the finer points by distance from
        it). Falls back to the viewing coarse rung's space for a same-rung theme centre. None if truly absent."""
        if not c:
            return None
        r = SUITE.store.get_vector(SUITE.store.space_address(c, space, emb))       # a UNIT centre (at the layer)
        if r and r.get("vector"):
            return r["vector"]
        if c.startswith("cluster://"):                                            # a THEME centre — its NATIVE rung
            seg = c.split("cluster://", 1)[1].split("/")                          # [space, 'k<K>', label]
            if len(seg) >= 2 and seg[1].startswith("k"):
                r = SUITE.store.get_vector(SUITE.store.space_address(c, f"scale:{space}:{seg[1]}", emb))
                if r and r.get("vector"):
                    return r["vector"]
        if coarse_k is not None:                                                  # same-rung theme centre
            r = SUITE.store.get_vector(SUITE.store.space_address(c, f"scale:{space}:k{coarse_k}", emb))
            if r and r.get("vector"):
                return r["vector"]
        return None

    # ── COARSE RUNG: the meaning-field over THEMES (cluster centroids), not units ──────────────────────
    if coarse_k is not None:
        pts = _scale.rung_points(SUITE.store, space, coarse_k, emb)     # raises only on a corrupt pyramid (at the layer)
        meta = {p["source"]: p for p in pts}
        # EVERY pseudo-event needs a parseable ts ≤ now — project() filters by the time scrubber (t <= now)
        # before the semantic radius runs, so a ts-less event is silently dropped. Stamp by SIZE rank (bigger
        # theme = more recent) so the no-centre TIME layout orders by size; the with-centre SEMANTIC radius
        # ignores ts (only needs it parseable). `base` is concrete (now, or real-now when no ?at= was given).
        base = now or datetime.now(timezone.utc)
        size_rank = {p["source"]: i for i, p in enumerate(sorted(pts, key=lambda p: -p["size"]))}
        # pseudo-events shaped like corpus.record so the semantic projector + _addr_of resolve them; the
        # cluster address is BOTH address and source_address (so the surface can re-centre / zoom on a theme).
        cevs = [{"kind": "corpus.record", "projection": space, "seq": i,
                 "address": p["source"], "source_address": p["source"],
                 "ts": (base - timedelta(seconds=size_rank[p["source"]])).isoformat(),
                 "summary": f'{(p["exemplar"] or "").split("/")[-1]}  ·{p["size"]}'}
                for i, p in enumerate(pts)]

        def enrich(body):
            for pt in body.get("points", []):
                m = meta.get(pt.get("source"))
                if m:
                    pt["scale_size"] = m["size"]
                    pt["scale_exemplar"] = m["exemplar"]
                    pt["scale_members"] = len(m["members"])
                    if "children_finer" in m:
                        pt["scale_children"] = m["children_finer"]
            return body

        if not center:
            # NO centre — lay the themes out by size (the growth-front proxy via the size-ranked ts above),
            # flagged needs_center (never a faked meaning-distance), so the surface prompts 'pick a centre'.
            # Mirrors the unit no-centre case.
            pend = _uproject(cevs, binding={**binding, "radius_from": "time"}, registry=reg, now=now, limit=lim)
            pend["binding"]["radius_from"] = "semantic"
            pend["binding"]["needs_center"] = True
            pend["binding"]["space"] = space
            return 200, attach_scale(enrich(pend), coarse_k)
        # centre given: its vector is a UNIT (unit space) OR a THEME (this rung's centroids) — themes ranked
        # by meaning-distance from it. The centre need not itself be one of the points (it can be off-stage).
        vectors = {p["source"]: _mrl(p["vector"]) for p in pts}   # MRL: theme centroids at the chosen resolution
        cv = centre_vector(center)                       # portable across rungs (unit OR a theme's native rung)
        if cv:
            vectors[center] = _mrl(cv)
        try:
            out = _uproject(cevs, binding=binding, registry=reg, now=now, center=center, limit=lim, vectors=vectors)
        except ValueError as ve:
            return 400, {"error": str(ve), "binding": binding.get("id"),
                         "hint": "this centre has no vector in the lens's space or this rung — pick an "
                                 "embedded item or a theme as the centre"}
        return 200, attach_scale(enrich(out), coarse_k)

    # ── UNIT RUNG: the meaning-field over the embedded items (Group 6, unchanged) ─────────────────────
    uevs = [e for e in evs if e.get("kind") == "corpus.record" and e.get("projection") == space]
    if not center:
        pend = _uproject(uevs, binding={**binding, "radius_from": "time"}, registry=reg, now=now, limit=lim)
        pend["binding"]["radius_from"] = "semantic"
        pend["binding"]["needs_center"] = True
        pend["binding"]["space"] = space
        return 200, attach_scale(pend, "unit")
    vectors = {}
    for e in uevs:
        rec = SUITE.store.get_vector(SUITE.store.space_address(e.get("source_address") or "", space, emb))
        if rec and rec.get("vector"):
            vectors[_proj_addr(e)] = _mrl(rec["vector"])    # MRL: items at the chosen resolution
    cv = centre_vector(center)                           # unit centre, OR a theme centre (zoom-out-from-a-theme)
    if cv:
        vectors[center] = _mrl(cv)
    try:
        out = _uproject(uevs, binding=binding, registry=reg, now=now, center=center, limit=lim, vectors=vectors)
    except ValueError as ve:
        return 400, {"error": str(ve), "binding": binding.get("id"),
                     "hint": "this centre has no vector in the lens's space — pick an embedded item as the centre"}
    return 200, attach_scale(out, "unit")


def _separator_projection(q, binding, reg, evs, center, now, lim):
    """THE TWO-GRAVITY SEPARATOR (Group 9) for /api/projection. Returns (status, body). A GENERAL
    variable-two-pole field: every embedded item's radius = its signed lean toward pole A vs pole B (both
    pulls + the raw lean carried per point). The store I/O lives HERE; project() stays PURE (poles + vectors
    ride in). The poles are VARIABLES, registry-true: declared by the binding (pole_a/pole_b) AND overridable
    per request (?pole_a=&pole_b=) so the operator DRIVES which two gravities (interactive — a separator with
    poles welded into the engine would be the very hardcode Tim deleted). A pole ref is any address carrying a
    vector in the binding's lens: a corpus ITEM, a THEME centroid (cluster://<space>/k<K>/<label> — a real,
    clustering-separated corpus region), or an anchor:// the AI itself planted (the pollution instance sets
    pole_b=anchor://ai-corner). The FIFTH GATE (separation_report) rides in the response — the witness that
    the field actually SEPARATES, so a normalized-gradient-over-noise can never read as done."""
    from runtime.projection import project as _uproject, _addr_of as _proj_addr
    space = binding.get("space")
    emb = q.get("emb") or binding.get("emb") or None   # embedder LAYER (None=BGE default); applies to UNIT reads
    # MRL resolution axis (?dim=N): truncate every read vector — BOTH poles + all items — to its first N dims
    # before the lean/separation cosines. Consistent truncation (poles + items together) keeps _cosine's
    # dim-guard happy; the fifth gate (separation_report) then runs AT the chosen resolution. None = full dim.
    _md = (q.get("dim") or "").strip()
    mdim = int(_md) if _md.isdigit() and int(_md) > 0 else None
    def _mrl(v):
        return v[:mdim] if (mdim and mdim < len(v)) else v
    if not space:
        return 400, {"error": "separator binding needs a `space` (the lens the items + poles live in)",
                     "binding": binding.get("id")}

    def _pole_vector(ref):
        """Resolve a pole's vector from the store: a UNIT item / anchor in the lens's space, OR a THEME
        centroid (cluster://) from its own rung's scale space. None if truly absent (→ fail loud above)."""
        if not ref:
            return None
        r = SUITE.store.get_vector(SUITE.store.space_address(ref, space, emb))  # unit item / planted anchor (layer)
        if r and r.get("vector"):
            return r["vector"]
        if ref.startswith("cluster://"):                                     # a theme centroid (real region)
            seg = ref.split("cluster://", 1)[1].split("/")                   # [space, 'k<K>', label]
            if len(seg) >= 2 and seg[1].startswith("k"):
                r = SUITE.store.get_vector(SUITE.store.space_address(ref, f"scale:{seg[0]}:{seg[1]}", emb))
                if r and r.get("vector"):
                    return r["vector"]
        return None

    pole_a_ref = q.get("pole_a") or binding.get("pole_a")
    pole_b_ref = q.get("pole_b") or binding.get("pole_b")
    # the binding's friendly label names its OWN default pole; an operator-OVERRIDDEN pole (?pole_a=) is named
    # by its ref (so the readout never shows the stale default label for a pole the operator just drove to).
    pole_a_label = None if q.get("pole_a") else binding.get("pole_a_label")
    pole_b_label = None if q.get("pole_b") else binding.get("pole_b_label")
    if not pole_a_ref or not pole_b_ref:
        return 400, {"error": "separator needs TWO poles (?pole_a=&pole_b= or the binding's pole_a/pole_b) — "
                              "fail loud, never a one-gravity field", "binding": binding.get("id")}
    va, vb = _pole_vector(pole_a_ref), _pole_vector(pole_b_ref)
    missing = [ref for ref, v in ((pole_a_ref, va), (pole_b_ref, vb)) if v is None]
    if missing:
        return 400, {"error": f"pole(s) with no vector in lens {space!r}: {missing} — pick poles embedded in "
                              f"this lens (a corpus item, a cluster:// theme, or a planted anchor). Fail loud, "
                              f"never a silent fallback.", "binding": binding.get("id")}
    va, vb = _mrl(va), _mrl(vb)   # MRL: poles at the chosen resolution (consistent with the items below)

    uevs = [e for e in evs if e.get("kind") == "corpus.record" and e.get("projection") == space]
    vectors = {}
    for e in uevs:
        rec = SUITE.store.get_vector(SUITE.store.space_address(e.get("source_address") or "", space, emb))
        if rec and rec.get("vector"):
            vectors[_proj_addr(e)] = _mrl(rec["vector"])    # MRL: items at the chosen resolution
    poles = {"a": {"vector": va, "label": pole_a_label or pole_a_ref, "ref": pole_a_ref},
             "b": {"vector": vb, "label": pole_b_label or pole_b_ref, "ref": pole_b_ref}}
    try:
        out = _uproject(uevs, binding=binding, registry=reg, now=now, center=center, limit=lim,
                        vectors=vectors, poles=poles)
    except ValueError as ve:
        return 400, {"error": str(ve), "binding": binding.get("id")}
    out["binding"]["space"] = space
    out["binding"]["res"] = mdim     # the active MRL resolution (None = full dim)
    out["binding"]["emb"] = emb      # the active embedder LAYER (None = default/BGE)
    return 200, out


def _nucleation_projection(q, binding, reg, evs, center, now, lim):
    """TYPE-NUCLEATION — the 20/80 water-law (Tim Geldard's growth law) — for /api/projection. Returns
    (status, body). Types the items of one data store against a REGISTRY OF TYPES (the scale-pyramid centroids
    of a `types_space` at a `rung`) and reads where the registry under-covers its content: what FITS sits inside
    the square, what does NOT piles up OUTSIDE, and a DISTINCT coherent pile past the birth threshold is a
    CANDIDATE NEW TYPE. All store I/O lives HERE; project()+nucleation_report stay pure (the resolved report
    rides in). Every axis is a VARIABLE, registry-true AND drivable, so the law works on ANY registry/store —
    as the Company grows new types/stores they appear with NO code edit (the universal law, not a fixed wiring):
      ?types_space= (which registry of types)   ?rung= (how fine that registry)   ?space= (which content store)
      ?dial= (the 20/80 BIRTH threshold — moves the born/forming line, NOT the membership split).
    The default is a CROSS-INSTANCE pair (types from one store, items from ANOTHER) so the misfit is genuine and
    non-circular, and >1 data store is visibly exercised. Cosines are within ONE BGE-M3 1024-dim lens — a dim
    mismatch fails loud in _cosine (never a wrong-but-plausible fit). HONEST BOUNDARY: this is SEMANTIC
    nucleation over the EMBEDDED data stores; the symbolic pile-outside for a code-declared type-registry
    (events naming no registered row) is Group 10's '—' remainder — distinct-type CLUSTERING is scoped to where
    vectors exist (a growth front otherwise)."""
    from runtime.projection import (project as _uproject, nucleation_report as _nuc)
    from runtime import scale
    import math as _math
    types_space = q.get("types_space") or binding.get("types_space")
    item_space = q.get("space") or binding.get("space")
    rung = int(q.get("rung") or binding.get("rung") or 8)
    try:
        dial = float(q.get("dial") or binding.get("dial") or 0.2)
    except (TypeError, ValueError):
        dial = 0.2
    # EMBEDDER LAYER (Tim's multi-layer model, 2026-06-15): read the content ITEMS at a chosen embedder layer
    # (the C1 `#emb=` key) so the SAME items can be typed against an embedder-matched registry. emb=None = the
    # default (BGE) layer — every existing nucleation call is byte-identical. emb='pplx' reads the pplx layer
    # (e.g. types_space=operators which is pplx-native × space=repo@pplx). The dim guard below (len==dim) keeps
    # it honest: a layer-mismatched pair (e.g. pplx 2560 types × BGE 1024 items) yields no items → fails loud.
    emb = q.get("emb") or binding.get("emb") or None
    # MRL SEMANTIC-ZOOM (Tim's capability §C; verified graceful 2026-06-15): the pplx 2560-d vector is
    # Matryoshka-trained, so its first-N dims are a valid COARSER embedding. ?dim=<N> truncates the read vectors
    # (types AND items, consistently) to N before the cosine → a continuous semantic-RESOLUTION zoom, orthogonal
    # to the rung pyramid (the 2-D scale: rung × dim). dim=None = full resolution (byte-identical). FREE (no
    # re-embed). Applied at every vector boundary so all cosines + the dim guard stay consistent.
    _md = (q.get("dim") or "").strip()
    mdim = int(_md) if _md.isdigit() and int(_md) > 0 else None
    def _mrl(v):
        return v[:mdim] if (mdim and mdim < len(v)) else v
    if not types_space or not item_space:
        return 400, {"error": "nucleation needs a `types_space` (the registry of types) AND a `space` (the "
                              "content store typed against it) — fail loud", "binding": binding.get("id")}
    try:
        tpts = scale.rung_points(SUITE.store, types_space, rung, emb)   # the TYPE registry at the embedder LAYER
    except Exception as ex:
        return 400, {"error": f"no scale pyramid / rung {rung} for types_space {types_space!r}: {ex} — build a "
                              f"pyramid first (POST /api/scale/build {{space: {types_space!r}}})",
                     "binding": binding.get("id")}
    if not tpts:
        return 400, {"error": f"types_space {types_space!r} rung {rung} resolved NO type centroids — a registry "
                              f"of nothing cannot be under-covered", "binding": binding.get("id")}
    type_vecs = [_mrl(t["vector"]) for t in tpts]   # MRL: truncate the type centroids to the chosen resolution
    type_sizes = [t.get("size") or len(t.get("members") or []) for t in tpts]
    # readable, UNIQUE type labels from the cluster exemplars (the sector keys the placement maps to)
    type_labels, _seen = [], {}
    for i, t in enumerate(tpts):
        base = str(t.get("exemplar") or f"type{i}")
        lbl = base if base not in _seen else f"{base}#{i}"
        _seen[base] = 1
        type_labels.append(lbl)

    def _cos(a, b):
        d = sum(x * y for x, y in zip(a, b))
        na = _math.sqrt(sum(x * x for x in a)); nb = _math.sqrt(sum(x * x for x in b))
        return d / (na * nb) if na and nb else 0.0
    # admission radii = each type's OWN empirical extent (10th-pct member cosine to its centroid) — truthful
    # membership, not a tuned global floor (cross-store → mostly outside; same-store → populated + outliers).
    type_radii = []
    for t in tpts:
        mc = []
        for m in (t.get("members") or []):
            rec = SUITE.store.get_vector(SUITE.store.space_address(m, types_space, emb))
            if rec and rec.get("vector"):
                mc.append(_cos(_mrl(rec["vector"]), _mrl(t["vector"])))   # MRL: radii at the chosen resolution
        mc.sort()
        type_radii.append(mc[max(0, len(mc) // 10)] if mc else 0.0)

    # resolve the ITEM vectors of the content store (keyed by source_address — what project() looks up per item)
    uevs = [e for e in evs if e.get("kind") == "corpus.record" and e.get("projection") == item_space]
    item_vecs, item_refs = [], []
    dim = len(type_vecs[0])
    for e in uevs:
        sa = e.get("source_address") or ""
        rec = SUITE.store.get_vector(SUITE.store.space_address(sa, item_space, emb))
        if rec and rec.get("vector"):
            v = _mrl(rec["vector"])                      # MRL: items at the chosen resolution
            if len(v) == dim:                            # dim = len(type_vecs[0]) = the (possibly truncated) resolution
                item_vecs.append(v); item_refs.append(sa)
    if not item_vecs:
        return 400, {"error": f"no embedded items in space {item_space!r} at dim {dim} (the lens the types live "
                              f"in) — capture+embed that store first, or pick an embedded space",
                     "binding": binding.get("id")}
    try:
        rep = _nuc(item_vecs, item_refs, type_vecs, type_labels, type_radii, type_sizes, dial=dial)
    except ValueError as ve:
        return 400, {"error": str(ve), "binding": binding.get("id")}
    rep["types_space"] = types_space
    typed = set(item_refs)
    pevs = [e for e in uevs if (e.get("source_address") or "") in typed]
    try:
        out = _uproject(pevs, binding=binding, registry=reg, now=now, center=center, limit=lim, nucleation=rep)
    except ValueError as ve:
        return 400, {"error": str(ve), "binding": binding.get("id")}
    out["binding"]["types_space"] = types_space
    out["binding"]["space"] = item_space
    out["binding"]["rung"] = rung
    out["binding"]["dial"] = dial
    out["binding"]["emb"] = emb                          # the active embedder LAYER (None = default/BGE)
    out["binding"]["res"] = mdim                          # the active MRL resolution (None = full dim)
    # registry-true PICKERS for the FORM (no FE hardcode — as the Company embeds new stores / builds new
    # pyramids they appear here automatically): item_spaces = every embedded store (>2 units); types_spaces =
    # those that ALSO have a scale pyramid (so they can be a registry of types); rungs = the chosen registry's.
    from collections import Counter as _Counter
    _counts = _Counter(e.get("projection") for e in evs
                       if e.get("kind") == "corpus.record" and e.get("projection"))
    _embedded = sorted(sp for sp, c in _counts.items() if sp and c > 2)
    _typ = []
    for sp in _embedded:
        try:
            if scale.load_pyramid(SUITE.store, sp, emb):   # a registry-of-types AT THE ACTIVE LAYER
                _typ.append(sp)
        except Exception:
            pass
    _rungs = []
    try:
        _pyr = scale.load_pyramid(SUITE.store, types_space, emb)
        _rungs = sorted([(r.get("k") if isinstance(r, dict) else r) for r in (_pyr or {}).get("rungs", [])])
    except Exception:
        pass
    if "nucleation" in out:
        out["nucleation"]["available"] = {"item_spaces": _embedded, "types_spaces": _typ, "rungs": _rungs}
    return 200, out


# ── Group H/I — the always-on activation CALLER (DORMANT by default) ─────────────────────────────
# ONE long-lived ActivationCaller holds the rollup driver's held cursor (the H3 discipline — a fresh
# driver per tick would re-consolidate every wave). BOTH the manual POST /api/activation/tick AND the
# autonomous loop drive THIS instance, so the cursor is held across manual + loop ticks alike.
# maybe_start_activation_loop SPAWNS NOTHING unless COMPANY_ACTIVATION_LOOP is deliberately set (the
# wire_armed()-analog dormancy gate, default OFF) — so importing this module / constructing SUITE stands
# up NO thread + NO autonomous tick. Arming the live cadence is a behavior change the operator greenlights
# → needs-tim; this build NEVER auto-starts the loop. The manual endpoint stays the live external-drive
# seam regardless (firing it fires roles = computation, the G9/C9.2 floor holds by construction).
ACTIVATION_CALLER = activation_driver.ActivationCaller(suite=SUITE)
_ACTIVATION_LOOP_THREAD = activation_driver.maybe_start_activation_loop(ACTIVATION_CALLER)


# =================================================================================================
# THE COGNITION-ENGINE GLUE (LANE-BRIDGE) — the thin per-face wrapper around the SHARED engine fns.
#
# REUSE-DON'T-PARALLEL: the ENGINE is `runtime.cognition` (`_cog.run_role`/`run_items`/`run_reduce`/
# `resolve_address`) — the SAME functions the swarm, `dry_run_role`, and `mcp_face/server.py` call. There
# is NO second engine here. What these helpers do is the small, NON-engine glue the engine deliberately
# leaves to the caller: assign a `turn_id`, resolve address-valued declared inputs, PERSIST the output to
# its `run://` address, and emit the ONE `op.run` RUN-INDEX record (#54 storage-discovery) so an
# FE-initiated run is DISCOVERABLE by `list_runs`/`find_runs` exactly like an MCP-initiated one.
#
# SEAM (BAR2 — surfaced honestly): this glue is byte-for-byte the same shape as `mcp_face/server.py`'s
# run_role/run_items/run_reduce (same `ENGINE_RUN_OPS` strings, same `addresses=[address]`, same
# `run_op`). It is mirrored, NOT shared, because extracting it into a shared helper (or onto the Suite)
# would touch `suite.py`/`mcp_face` — OUT of the BRIDGE lane this pass. The long-term home is one shared
# `Suite.run_role/run_items/run_reduce` (or a `runtime/cognition_face.py`) both faces call; until then
# the two copies MUST stay identical (drift on the op-string/addresses silently breaks #54 discovery).
# THE FLOOR (C9.2) HOLDS: every helper produces a `run://` output + an `op.run` telemetry record — NONE
# emits resolve/approve/dispatch (the operator-only floor; the `claude -p` wire stays off this seam).
# =================================================================================================

# the closed, NAMED reduce-rule registry (registry-is-truth) — IDENTICAL to mcp_face/server.py's
# `_REDUCE_RULES`: a deterministic L2 join selected BY NAME over the JSON boundary (a Python callable
# can't cross HTTP). An unknown name FAILS LOUD (never a fabricated rule). Same seam-note as above.
_COG_REDUCE_RULES = {
    "count":  lambda values: {"count": len(values)},
    "concat": lambda values: {"concat": [v for v in values]},
    "first":  lambda values: {"first": (values[0] if values else None)},
}


def build_projection(q):
    """THE UNIVERSAL PROJECTION ENGINE — the ONE resolver behind BOTH faces: the bridge HTTP
    /api/projection AND the MCP `project` door (via Suite.project, which lazy-imports this — the same
    call-time-import idiom capabilities() uses for BRIDGE_ROUTES, since bridge can't be imported at the
    suite/mcp module load). Takes the parsed query dict, resolves the binding, dispatches by `radius_from` to
    the lens helpers (semantic/separator/nucleation — all store I/O there) or the pure project() for the
    Group-10 angle-by-registry/graph case. Returns (status, body). ONE implementation, reused — never a
    parallel projector per face (Tim: one entity, reuse-don't-parallel). Provisional home: it sits beside the
    helpers it dispatches; a future neutral module can thread the Suite in (today it reads via the bridge's
    Suite over the shared store — byte-identical data either way)."""
    from runtime.projection import (project as _uproject, BindingRegistry as _BR,
                                    parse_now as _parse_now, _addr_of as _proj_addr)
    # ABSOLUTE bindings path (ROOT-based, like NodeRegistry below) — NOT the cwd-relative default: this engine
    # is called from BOTH faces, and the MCP server's cwd is not the repo root, so a relative "bindings" there
    # discovers ZERO lenses → every binding silently falls back to raw. Absolute = cwd-independent, both faces.
    reg = _BR().discover([os.path.join(ROOT, "bindings")])
    binding = reg.get(q.get("binding"))
    evs = SUITE.store.events_since(int(q.get("since") or 0))
    center = q.get("center")
    now = _parse_now(q.get("at"))          # ?at= moves the temporal centre into the past (the scrubber)
    lim = int(q.get("limit") or 0)
    rf = binding.get("radius_from")        # radius_from='time'(age) | 'address'(tree) | 'semantic' | 'separator' | 'nucleation'
    if rf == "semantic":
        # THE CIRCLE (Group 6) + THE SCALE AXIS (Group 11) — the meaning-field, at the unit or a coarse THEME
        # rung (?rung=). All store/registry I/O + the rung resolution live in the helper; project() stays pure.
        return _semantic_projection(q, binding, reg, evs, center, now, lim)
    if rf == "separator":
        # THE TWO-GRAVITY SEPARATOR (Group 9) — the store I/O (the two pole vectors + the item vectors) lives
        # in the helper; project() stays pure. Poles are drivable (?pole_a=&pole_b=).
        return _separator_projection(q, binding, reg, evs, center, now, lim)
    if rf == "nucleation":
        # TYPE-NUCLEATION (the 20/80 water-law) — the store I/O (the registry-of-types' centroids + admission
        # radii, and the content store's item vectors) lives in the helper. Drivable: ?types_space=&rung=&space=&dial=.
        return _nucleation_projection(q, binding, reg, evs, center, now, lim)
    # Group 10 — angle_from=<registry/graph>: resolve the entity-set's rows (+ directed edges) HERE (the
    # store/registry I/O), pass to the pure project(). A REGISTRY's rows come from the live discovered registry
    # (registry-is-truth) with NO inter-row edges yet (→ order_by falls back to count honestly). A GRAPH's
    # nodes + connect wires ARE real directed edges → order_by=edge topological-sorts them.
    af = binding.get("angle_from", "kind")
    skw = {}
    if af not in ("kind", "kind-group"):
        _REG = {"projections": SUITE.projection_registry, "roles": SUITE.role_registry,
                "mark_types": SUITE.mark_type_registry, "relation_types": SUITE.relation_type_registry,
                "generation_policies": SUITE.generation_policy_registry,
                "ai_tics": SUITE.ai_tic_registry, "forms": SUITE.form_registry,
                "lifters": SUITE.lifter_registry}
        if af in ("node-types", "node_types"):
            # THE CONNECTIONS in the node registry (Group 10): rows = node types; edges = the DIRECTIONAL typed
            # type-flow — A's output type feeds B's input type, ASYMMETRIC only (the both-ways pairs are NOT
            # typed → excluded). Cycles among the directional edges are KEPT. Registry-true: the LIVE node registry.
            _nt = NodeRegistry().discover([os.path.join(ROOT, "nodes")]).types
            _names = sorted(_nt)
            _outs = {n: set(_nt[n].ports.outputs.values()) for n in _names}
            _ins = {n: set(_nt[n].ports.inputs.values()) for n in _names}
            _feeds = lambda a, b: bool(_outs[a] & _ins[b])
            _dir = [(a, b) for a in _names for b in _names
                    if a != b and _feeds(a, b) and not _feeds(b, a)]
            skw = {"sector_ids": _names, "sector_edges": _dir}
        elif af in _REG:
            skw = {"sector_ids": sorted(_REG[af]), "sector_edges": []}
        elif af == "graph" or af.startswith("graph:"):
            gid = af.split(":", 1)[1] if ":" in af else (q.get("graph") or "")
            G = SUITE.store.load_graph(gid) if gid else None
            if G:
                evs = [e for e in evs if e.get("graph") == gid]   # scope to that graph's events
                skw = {"sector_ids": [n.id for n in G.nodes],
                       "sector_edges": [(e.from_node, e.to_node) for e in G.edges]}
    return 200, _uproject(evs, binding=binding, registry=reg, now=now, center=center, limit=lim, **skw)


def _cog_emit(kind, payload):
    """The (kind, payload-dict) emit sink the engine fns expect, onto the Suite's lenient telemetry
    `_emit` (the ONE event log — reflects-never-owns narration; never a safety claim). Mirrors
    mcp_face/server.py:_cog_emit so run_items/run_reduce telemetry is identical across both faces."""
    summary = payload.get("summary") or f"{kind} ({payload.get('turn_id', '')})"
    SUITE._emit(kind, summary, **{k: v for k, v in payload.items() if k != "summary"})


def _cog_resolve_role(role_id_or_fields):
    """Resolve a role from an id (str — looked up in the LIVE registry, registry-is-truth) OR a draft
    field-set (dict — rendered + loaded via the authoring path). Mirrors mcp_face/server.py:_resolve_role
    (reuse-don't-parallel: no second role notion). Fail loud on an unknown id (rule 8 — never invent)."""
    from runtime import authoring as _auth
    if isinstance(role_id_or_fields, str):
        rid = _auth._safe_role_id(role_id_or_fields)
        if rid not in SUITE.role_registry:
            raise ValueError(f"unknown role {rid!r} — registered roles: {sorted(SUITE.role_registry)} "
                             f"(see /api/cognition_info — author from the registry, never invent).")
        return SUITE.role_registry[rid]
    if isinstance(role_id_or_fields, dict):
        rid = _auth._safe_role_id(role_id_or_fields.get("id"))
        source = _auth.render_role_source(role_id_or_fields)
        return _auth.load_role_from_source(rid, source)          # the SAME RoleRegistry discovery (no fork)
    raise TypeError("role must be a registered role id (str) or a draft field-set (dict)")


def _cog_turn_id(prefix):
    """A face-tagged turn id (the FE face uses 'fe-' so a run's origin is legible in the run index)."""
    return prefix + time.strftime("%Y%m%d-%H%M%S") + f"-{int(time.monotonic()*1000) % 100000}"


def cog_run_role(role, *, utterance="", model="", inputs=None,
                 max_tokens=256, temperature=0.0, ensure=False, ensure_evict=False):
    """Fire ONE role and persist+index its output. Mirror of mcp_face/server.py:run_role (same engine
    `_cog.run_role`, same persist to run://<turn>/<role>, same `cognition.run_role` op.run emit). The
    OPERATION is the ROLE's own `op` (NOT a caller kwarg — the engine dispatches on `role.op`, exactly as
    the MCP face does): a generate-role → validated structured output; an embed-role (op='embed', e.g. the
    'embed' role) → a {vector,dim,model} via the local embedder (down embedder FAILS LOUD unless
    ensure=True requests the gated #50 load). Returns {role, op, output, address, turn_id}."""
    r = _cog_resolve_role(role)
    op = getattr(r, "op", "generate")                            # the op rides the ROLE (mcp_face parity)
    turn_id = _cog_turn_id("fe-")
    ctx = {"utterance": utterance}
    for name, val in dict(inputs or {}).items():
        # an address-VALUED input is RESOLVED via the engine resolver (input-address intent); else literal.
        # Mirrors mcp_face/server.py:run_role exactly (the "://" probe → resolve_address, which itself
        # fail-louds on an unresolvable/unknown scheme — the engine owns the scheme contract, not the glue).
        if isinstance(val, str) and "://" in val:
            ctx[name] = _cog.resolve_address(SUITE.store, val, turn_id=turn_id)
        else:
            ctx[name] = val
    kw = {"max_tokens": max_tokens, "temperature": temperature, "store": SUITE.store,
          "ensure": ensure, "ensure_evict": ensure_evict}
    if model:
        kw["model"] = model
    _t0 = time.monotonic()
    out = _cog.run_role(r, ctx, **kw)
    _ms = int((time.monotonic() - _t0) * 1000)
    address = f"run://{turn_id}/{r.id}"
    cas = SUITE.store.put_content(out)
    SUITE.store.set_ref(address, cas)
    # #54 RUN INDEX — colocated with the persist (engine run_role has no emit + does not persist).
    SUITE.emit_run_record("cognition.run_role", _ms,
                          run_op=op, turn_id=turn_id, role=r.id, addresses=[address])
    return {"role": r.id, "op": op, "output": out, "address": address, "turn_id": turn_id}


def cog_run_items(role, items, *, max_tokens=256, temperature=0.0):
    """Fan ONE role over N units (the MAP axis). Mirror of mcp_face/server.py:run_items (same engine
    `_cog.run_items`, same per-unit run://<turn>/<role>/<i> outputs + cognition.items rollup; the engine
    emits its OWN op.run index via the `emit` sink). Returns {role, turn_id, n_units, addresses, resolved,
    finish_order, skipped, wall_s}."""
    r = _cog_resolve_role(role)
    turn_id = _cog_turn_id("fe-items-")
    res = _cog.run_items(r, list(items), SUITE.store, turn_id=turn_id, emit=_cog_emit,
                         max_tokens=max_tokens, temperature=temperature)
    return {"role": r.id, "turn_id": turn_id, "n_units": len(items),
            "addresses": res.addresses, "resolved": res.resolved,
            "finish_order": res.finish_order, "skipped": res.skipped, "wall_s": res.wall_s}


def cog_run_reduce(addresses, mode, *, role="", reduce_rule="", cluster_threshold=0.85, max_tokens=512):
    """Reduce N map-output run:// addresses into ONE output (the JOIN axis). Mirror of
    mcp_face/server.py:run_reduce (same engine `_cog.run_reduce`). mode='role' → synthesize join (pass a
    reduce-role id); mode='rule' → a NAMED deterministic L2 join (count·concat·first); mode='cluster' →
    embed-cluster (needs the local embedder). Returns {turn_id, mode, joined, inputs, skipped, wall_s,
    detail}."""
    turn_id = _cog_turn_id("fe-reduce-")
    kw = {"turn_id": turn_id, "mode": mode, "emit": _cog_emit, "max_tokens": max_tokens,
          "cluster_threshold": cluster_threshold}
    if mode == "role":
        if not role:
            raise ValueError("run_reduce(mode='role'): pass a reduce-role id (e.g. 'reduce_synth').")
        kw["role"] = _cog_resolve_role(role)
    elif mode == "rule":
        if reduce_rule not in _COG_REDUCE_RULES:
            raise ValueError(f"run_reduce(mode='rule'): unknown reduce_rule {reduce_rule!r} — named "
                             f"built-ins are {sorted(_COG_REDUCE_RULES)} (fail loud, never a fabricated rule).")
        kw["reduce_rule"] = _COG_REDUCE_RULES[reduce_rule]
    res = _cog.run_reduce(list(addresses), SUITE.store, **kw)
    return {"turn_id": turn_id, "mode": mode, "joined": res.joined, "inputs": res.inputs,
            "skipped": res.skipped, "wall_s": res.wall_s, "detail": res.detail}


def seed_demo():
    """First-run graph = the FIRST PURPOSE: the system answering about its own codebase."""
    if DEMO not in SUITE.list_graphs():
        SUITE.save_graph(Graph(id=DEMO, nodes=[
            NodeInstance(id="question", type="constant",
                         config={"value": "What does the scheduler's memo gate do, and which file is it in?"}),
            NodeInstance(id="code", type="codebase", config={}),
            NodeInstance(id="answer", type="ask", config={"model": "deepseek-v4-pro:cloud"}),
        ], edges=[
            Edge(from_node="question", from_port="value", to_node="answer", to_port="question"),
            Edge(from_node="code", from_port="context", to_node="answer", to_port="context"),
        ]))


class H(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"   # keep-alive so /api/stream (SSE) can hold the socket open

    def _send(self, code, body, ctype="application/json"):
        b = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def _body(self):
        ln = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(ln) or "{}")

    def _qs(self, parsed):
        """A flat {key: value} from the query string (first value per key)."""
        return {k: v[0] for k, v in parse_qs(parsed.query).items()}

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path                                 # path WITHOUT the query (exact matches hold)
        q = self._qs(parsed)
        gid = q.get("graph_id", DEMO)                      # graph-scoped reads default to DEMO (C4)
        if path == "/api/stream":                          # SSE — own handler, NEVER _send (G)
            self._stream(q)
            return
        try:
            if path in ("/", "/index.html"):
                with open(CANVAS, "rb") as f:
                    self._send(200, f.read(), "text/html; charset=utf-8")
            elif path == "/studio":                        # MOCKUP STUDIO — clean URL → the portal.
                # A 302 (NOT a byte-alias): the studio's iframe srcs are BARE filenames (src="IA-mobile.html"),
                # so they resolve against the DOCUMENT url. Served at /studio they'd resolve to /IA-mobile.html
                # (unserved → dead stage); redirecting to /mockups/STUDIO.html makes the document live IN
                # /mockups/, so both the iframe (→ /mockups/<file>.html) and ../design-system.css (→
                # /design-system.css) resolve correctly. Keeps the clean URL, touches nothing in the studio.
                self.send_response(302)
                self.send_header("Location", "/mockups/STUDIO.html")
                self.send_header("Content-Length", "0")
                self.end_headers()
            elif path == "/design-system.css":             # the generated corpus stylesheet (../design-system.css from a mockup)
                if not os.path.isfile(DESIGN_CSS):
                    self._send(404, "{}")
                else:
                    with open(DESIGN_CSS, "rb") as f:
                        self._send(200, f.read(), "text/css; charset=utf-8")
            elif path.startswith("/mockups/") and path.endswith(".html"):
                # STATIC, READ-ONLY mockup serving (the studio + every mockup it stages, same-origin). The
                # name after /mockups/ is path-safe-resolved (bare basename only; realpath-contained). A
                # bad name → ValueError → 400 (the wrapper); a well-formed but missing file → explicit 404
                # HERE (the generic except→400 would otherwise mask a missing mockup as a malformed-request).
                fp = _safe_mockup_path(path[len("/mockups/"):])
                if not os.path.isfile(fp):
                    self._send(404, "{}")
                else:
                    with open(fp, "rb") as f:
                        body = f.read()
                    # IN-FRAME ELEMENT DEIXIS (studio only): when the studio Stage stages a mockup it
                    # requests it with `?studio=1`. ONLY on that path we inject a tiny sandboxed click-
                    # capture script before </body>. On a click inside the mockup it finds the nearest
                    # element carrying a `data-ui-ref` that is a full ui:// address and postMessages that
                    # address up to the parent window (the studio FE), which sets the review locus to the
                    # clicked ELEMENT (not just the whole mockup). FAIL-SOFT: a click on an element with no
                    # ui:// data-ui-ref posts nothing → the locus stays at the whole-mockup address (today's
                    # behaviour). The flag is read from the QUERY (q), while the file is resolved from the
                    # query-STRIPPED path (line 402) — so `?studio=1` never reaches `_safe_mockup_path`, and a
                    # standalone mockup view (no flag) is served byte-for-byte un-injected. The sandbox is
                    # `allow-scripts allow-same-origin` (set on the iframe FE-side) so this script runs AND
                    # can postMessage to the parent. STRUCTURE only — no styling (the feel is a later pass).
                    if q.get("studio"):
                        inject = (
                            b"<script>(function(){try{"
                            b"document.addEventListener('click',function(e){try{"
                            b"var t=e.target&&e.target.closest?e.target.closest('[data-ui-ref]'):null;"
                            b"if(!t)return;"                                   # no ref ancestor → fail-soft (whole-mockup locus)
                            b"var a=t.getAttribute('data-ui-ref')||'';"
                            b"if(a.indexOf('ui://')!==0)return;"              # only full ui:// addresses are loci
                            b"parent.postMessage({type:'studio-deixis',address:a},location.origin);"
                            b"}catch(_){}}, true);"                            # capture phase, like the FE onDocClick
                            b"}catch(_){}})();</script>"
                        )
                        if b"</body>" in body:
                            body = body.replace(b"</body>", inject + b"</body>", 1)
                        else:
                            body = body + inject                              # no </body> → append (still runs)
                    self._send(200, body, "text/html; charset=utf-8")
            elif path == "/api/mockup-feedback":           # MOCKUP STUDIO: read a mockup's feedback thread
                # GET ?mockup=<filename> → {entries:[{id,mockup,element,text,ts,status}]}, [] if none.
                # Missing `mockup` → KeyError → 400 (fail loud, mirrors the address-keyed reads). A junk
                # name → ValueError from _read_feedback's gate → 400. status ∈ pending|applied|dismissed.
                self._send(200, json.dumps({"entries": _read_feedback(q["mockup"])}))
            elif path == "/api/corpus":                     # STUDIO (G4): the gallery's corpus, registry-is-truth
                # The reviewable mockup files actually on disk + their curated meta (title/platform/group/
                # reviewed-surface ui:// address). The studio gallery binds THIS, never a hardcoded FE list,
                # so a new mockup appears the moment its file lands. {items:[{file,title,platform,group,address}]}.
                self._send(200, json.dumps({"items": _corpus_index()}))
            elif path == "/api/graph":
                self._send(200, json.dumps(SUITE.state(gid)))
            elif path == "/api/graphs":                    # C4: list every graph in the substrate
                self._send(200, json.dumps(SUITE.list_graphs()))
            elif path == "/api/object_info":
                self._send(200, json.dumps(SUITE.object_info()))
            elif path == "/api/cognition_info":            # L-fe-be: the COGNITION registry (sibling of object_info)
                self._send(200, json.dumps(SUITE.cognition_info()))
            elif path == "/api/types":
                self._send(200, json.dumps(sorted(SUITE.list_types())))
            elif path == "/api/layers":                    # the multi-layer model's self-description: {space:[embedder layer,…]}
                self._send(200, json.dumps(SUITE.store.layers_by_space()))
            elif path == "/api/models":                    # B: per-kind/per-endpoint live model list
                self._send(200, json.dumps(SUITE.models_at(
                    kind=q.get("kind", "chat"), base_url=q.get("base_url"))))
            elif path == "/api/chat-models":                # S1: the picker list — ollama/cloud + local vLLM (model·base_url·service·up)
                self._send(200, json.dumps(SUITE.chat_models_detailed()))
            elif path == "/api/fit":                        # S6 (Tim 2026-06-07): "tell me if my selection won't fit"
                # ?services=chat-4b,tts-orpheus → the VRAM picture for that SELECTION (each budget, the sum
                # vs the 16GB card ceiling, measured free, fit/no-fit + what to unload). Config-derived, so
                # it tracks a resize (brain @256K vs @64K). Reuses gpu.fit_report — no parallel predictor.
                import sys as _sys
                _ops = os.path.join(ROOT, "ops", "cli")
                if _ops not in _sys.path:
                    _sys.path.insert(0, _ops)
                import gpu as _gpu, registry as _reg
                sel = [s for s in (q.get("services", "").split(",")) if s.strip()]
                if not sel:
                    raise ValueError("/api/fit needs ?services=<key>[,<key>] (fail loud: nothing selected)")
                self._send(200, json.dumps(_gpu.fit_report(_reg.load(), sel)))
            elif path == "/api/surfaced":
                self._send(200, json.dumps(SUITE.list_surfaced()))
            elif path == "/api/events":
                self._send(200, json.dumps(SUITE.events(60)))
            elif path == "/api/now":
                self._send(200, json.dumps(SUITE.now(gid)))
            elif path == "/api/greeting":                  # S2: caught-up-in-one-glance (Tim's arrival face)
                q = parse_qs(urlparse(self.path).query)
                self._send(200, json.dumps(SUITE.greeting(since=(q.get("since") or [None])[0])))
            elif path == "/api/projection":                # THE UNIVERSAL PROJECTION: resolved from a binding, no hardcode
                q = self._qs(urlparse(self.path))
                # ONE engine — the SAME resolver the MCP `project` door calls via Suite.project (the dual
                # interface: every UI affordance behind an MCP door). All the lens dispatch + store I/O lives
                # in build_projection (a sibling of the lens helpers); this face just serializes the result.
                _st, _body = build_projection(q)
                self._send(_st, json.dumps(_body))
            elif path == "/api/corpus-query":              # S7: the forager's search door (semantic + heads)
                q = self._qs(urlparse(self.path))
                text, space = q.get("text"), q.get("space") or None
                if not text:
                    self._send(400, json.dumps({"error": "/api/corpus-query needs ?text= (fail loud)"}))
                else:
                    res = SUITE.query_corpus(text, space=space, k=int(q.get("k") or 16))
                    # enrich each hit with its index row + a content head (the circle's River detail)
                    hits = []
                    for h in res.get("ranked", []):
                        rid = h["id"]
                        sa = rid.split("#", 1)[0].removeprefix("vec://") if rid.startswith("vec://") else rid
                        rows = SUITE.find_corpus(source_address=sa)
                        row = rows[-1] if rows else {}
                        content = {}
                        if row.get("cas"):
                            content = (SUITE.store.get_content(row["cas"]) or {}).get("output") or {}
                        head = json.dumps(content, ensure_ascii=False, default=str)[:400] if content else ""
                        hits.append({"address": sa, "score": h.get("score"),
                                     "kind": row.get("record_kind"), "projection": row.get("projection"),
                                     "session": (row.get("lineage") or {}).get("session"),
                                     "ts_source": content.get("ts_source"), "head": head})
                    self._send(200, json.dumps({"query": text, "space": res.get("space"),
                                                "note": res.get("note"), "hits": hits}))
            elif path == "/api/chat":
                self._send(200, json.dumps(SUITE.chat_history(40)))
            elif path == "/api/conversations":               # S2: the previous threads (reopen list)
                self._send(200, json.dumps(SUITE.list_conversations(int(q.get("limit", 30)))))
            elif path == "/api/conversation":                 # S2: reopen one → make current + its history
                self._send(200, json.dumps(SUITE.load_conversation(q["thread_id"])))
            elif path == "/api/rhm-config":
                self._send(200, json.dumps(SUITE.rhm_config()))
            elif path == "/api/inbox":
                self._send(200, json.dumps(SUITE.inbox_lanes()))
            elif path == "/api/last-change":
                self._send(200, json.dumps(SUITE.last_self_change() or {}))
            elif path == "/api/self-change-log":           # the self-modification AUDIT LEDGER (Finding #1)
                self._send(200, json.dumps(SUITE.self_change_log(int(q.get("limit", 50)))))
            elif path == "/api/panels":
                self._send(200, json.dumps(SUITE.list_panels()))
            elif path == "/api/capabilities":
                self._send(200, json.dumps(SUITE.capabilities()))
            elif path == "/api/capabilities/introspection":  # Mirror-Registry LANE-PROJECTION: the capability registry projection
                # Projects the CapabilityRegistry snapshot (counts + postures + entries) — the same
                # source as the MCP `capability` tool and the cap:// resolver. registry-is-truth:
                # the snapshot is the engine.project() view of the in-memory CapabilityRegistry.
                # 🟡 lead-verify-queued: live when Suite.capability_registry is populated by
                # LANE-CAP-WIRE (Suite.__init__ calls set_capability_registry after discovery).
                # A missing registry raises a teaching error (fail loud, never silent empty).
                try:
                    from introspection.registry import capability_registry as _cap_reg
                    cap_reg = _cap_reg()
                    self._send(200, json.dumps({"ok": True, **cap_reg.snapshot()}))
                except RuntimeError as _e:
                    self._send(200, json.dumps({
                        "ok": False,
                        "error": str(_e),
                        "note": ("Mirror-Registry LANE-CAP-WIRE not yet active in this Suite — "
                                 "Suite.__init__ must call set_capability_registry() once after "
                                 "CapabilityRegistry().discover() returns. This route is built; "
                                 "the live registry snapshot is queued for the lead to verify.")
                    }))
            elif path == "/api/ui_info":                   # C1: the UI-component registry (sibling of object_info)
                self._send(200, json.dumps(SUITE.ui_info()))
            elif path == "/api/registry/proposals":        # RG8: the pending registry-proposal batch (read)
                self._send(200, json.dumps(SUITE.registry_proposals()))
            elif path == "/api/scope":                     # S3: ui://→code://→scope[] (the address→code join)
                self._send(200, json.dumps(SUITE.resolve_scope(q["address"])))
            elif path == "/api/address-help":              # D2: the COMPOSED affordance bundle for one ui:// address
                # The address-keyed READ that EXPOSES the existing D1 composer (Suite.address_help — committed
                # 89f60d9, NOT rebuilt here): the JOIN of the THREE legs — what_this_is (_describe_ui_address /
                # represents), how_to_change (resolve_scope → blast_radius/X16 reach), how_to_use (the corpus
                # 'howto' stratum) — plus a `legs_present` flag the D2 surface reads to DEGRADE cleanly when a
                # leg is thin (G-53: many elements author no howto yet). Mirrors /api/scope + /api/self-changes-at
                # exactly: missing `address` → KeyError → 400 (fail loud); a MALFORMED address → ValueError from
                # address_help's S0 grammar gate → 400 (fail loud); a well-formed-but-unregistered address returns
                # a clean partial bundle (what_this_is tagged '(unregistered)', legs honestly false), never a crash.
                self._send(200, json.dumps(SUITE.address_help(q["address"])))
            elif path == "/api/context":                   # R2: the addressed-context inspector (the R2 read-face)
                # The standalone read that EXPOSES the EXISTING R2 engine (Suite.context_at — composes
                # `_r2_gather` + `_r2_score_and_cap`, the SAME scoring the chat runs at the live locus,
                # NOT a reimplementation). Returns the context bundle resolved AT a given ui:// address:
                # {address, items:[{kind,address,ts,text,pinned}], count, budget} — annotations + chats +
                # addressed events at the locus AND its ancestors, scored + budget-capped. Mirrors
                # /api/scope + /api/address-help exactly: missing `address` → KeyError → 400 (fail loud);
                # a MALFORMED address → ValueError from the S0 grammar gate inside context_at → 400 (fail
                # loud); a well-formed-but-UNREGISTERED address returns an HONEST EMPTY bundle (items=[],
                # DENY-ALL — never fabricated), not a crash.
                self._send(200, json.dumps(SUITE.context_at(q["address"])))
            elif path == "/api/up-translate":              # F1: the GENERALIZED up-translate move (reach face)
                # The reusable "present-this-at-Tim's-altitude" resolver (Suite.up_translate — composes the
                # EXISTING organs, NOT rebuilt): ANY artifact → its altitude envelope {lead, mechanism,
                # legs_present, grounded, degraded}. `kind` ∈ address|decision|finding|event. For the read-face
                # we expose the two FIRST-CLASS reachable kinds keyed by a string `ref`: 'address' (ref = a
                # ui:// address → composes address_help) and 'decision' (ref = a surfaced_id → composes coa).
                # finding/event take a dict the caller holds (the G2/FE-surface lane will POST those) — not on
                # this GET read. Mirrors /api/address-help exactly: missing `kind`/`ref` → KeyError → 400; an
                # unknown kind / malformed address → ValueError → 400 (fail loud); a missing surfaced_id →
                # KeyError → 400. The grounding guard means the body is honestly grounded/degraded, never faked.
                self._send(200, json.dumps(SUITE.up_translate(q["kind"], q["ref"])))
            elif path == "/api/self-changes-at":           # L5: "what did the system change HERE?" (§21.7#5)
                # The address-keyed READ over the self-change audit log: filters self_change_log by the
                # S3 address→code scope join. Missing `address` → KeyError → 400 (fail loud, mirrors
                # /api/scope). Revert from here stays on the EXISTING operator-only /api/revert (no new
                # revert route, gate untouched). Carries stale/note straight through so the surface
                # distinguishes "corpus stale — regenerate" from "no changes here" (never a silent lie).
                self._send(200, json.dumps(SUITE.self_changes_at(q["address"])))
            elif path == "/api/annotations":               # I6: the comment THREAD attached to a ui:// address
                # The address-keyed READ side of /api/annotate (POST). Missing `address` → KeyError →
                # 400 (fail loud, mirrors /api/scope). Suite.annotations_at validates the address (S0)
                # and returns the thread oldest-first. This is what R2 will gather at the operator's locus.
                self._send(200, json.dumps(SUITE.annotations_at(q["address"])))
            elif path == "/api/presentation-pref":         # F1: the ACTIVE learned presentation pref at a ui:// address
                # The address-keyed READ side of the POST capture seam (latest-wins). Missing `address` →
                # KeyError → 400 (fail loud, mirrors /api/annotations). Suite.presentation_pref_at validates
                # the address (S0) + re-validates a stored junk pref (raises → 400). Returns the structured
                # pref {kind, arg} or null (a clean absence — the adapt step degrades to the default).
                self._send(200, json.dumps(SUITE.presentation_pref_at(q["address"])))
            elif path == "/api/chats":                     # I7: the chat THREAD attached to a ui:// address
                # The address-keyed READ side of /api/attach-chat (POST). Missing `address` → KeyError →
                # 400 (fail loud, mirrors /api/scope + /api/annotations). Suite.chats_at validates the
                # address (S0) and returns the thread oldest-first. DISTINCT from /api/chat (GET = the
                # whole RHM history; POST = the RHM conversation) — this reads ONLY the turns attached to
                # `address`. This is what R2 will gather at the operator's locus (address-keyed context).
                self._send(200, json.dumps(SUITE.chats_at(q["address"])))
            elif path == "/api/address-history":            # L3: everything that happened AT a ui:// address
                # §21.7#1: clicking an element shows its addressed history. The address-keyed READ over
                # the event tail. Missing `address` → KeyError → 400 (fail loud, mirrors /api/scope +
                # /api/annotations + /api/chats). Suite.address_view validates the address (S0 grammar
                # gate) and returns the trajectory chronological — the addressed analogue of decision_view
                # (it WIDENS the audit-view machinery to an address key; the sid path is untouched).
                self._send(200, json.dumps(SUITE.address_view(q["address"])))
            elif path == "/api/stale-at":                  # L10: "is the cached result at this node's address
                # stale vs its CURRENT inputs?" (§21.7#10). A COSTED DERIVATION, not a served field — the FE
                # CALLS it only for a cached node (it recompiles + resolves input-hashes + recomputes the
                # _memo_sig + memo_get-compares; seams-engine Seam 8a). The key is a run://<graph>/<node>
                # node-instance address (NOT ui:// — `cached` is served per run:// node). Missing `address`
                # → KeyError → 400 (fail loud, mirrors /api/scope + /api/address-history). A malformed /
                # non-run:// address RAISES in stale_at_address → 400 too — a junk query never reads as a
                # silent 'fresh'. The verdict carries stale/unknown/reason/volatile (rule 4: an unevaluable
                # node is 'unknown' with a reason, never a silent false). READ-ONLY: the memo gate is unmutated.
                self._send(200, json.dumps(SUITE.stale_at_address(q["address"])))
            elif path == "/api/ref-versions":               # L6: the PRIOR VERSIONS of an addressed output
                # §21.7#6: a portal shows the CURRENT ref live; this is the trail of values the address has
                # HELD over time (Suite.ref_versions → store.ref_history index, appended on each set_ref).
                # The key is a run://<graph>/<node> OUTPUT address (NOT ui:// — versions accrue where set_ref
                # wrote; a PORTAL never writes, so the FE queries the address its config.ref POINTS AT). The
                # cas bytes survive (put_content write-once), so each prior version is fetchable by its cas.
                # Missing `address` → KeyError → 400 (fail loud, mirrors /api/stale-at + /api/address-history);
                # a malformed / non-run:// address RAISES in ref_versions → 400 too (a junk query never reads
                # as a silent 'no versions'). An address with no history returns versions:[] (honest empty).
                self._send(200, json.dumps(SUITE.ref_versions(q["address"])))
            elif path == "/api/review/current":            # B: the node at the cursor + its framing + ui:// target
                self._send(200, json.dumps(SUITE.present_current(q["session"])))
            elif path == "/api/review/status":             # B: the session's live status
                self._send(200, json.dumps(SUITE.session_status(q["session"])))
            elif path == "/api/journey/replay":             # L9: the ordered ui:// addresses of a recorded
                # journey — the FE steps the view through them via the PRESERVED forward resolveUiTarget (the
                # reverse of present_current's drive; no second navigation mechanism). Missing `journey` →
                # KeyError → 400 (fail loud, mirrors /api/review/current).
                self._send(200, json.dumps(SUITE.replay_journey(q["journey"])))
            elif path == "/api/journeys":                   # L9: the recorded journeys (id · step-count · done),
                # newest-first — the picker the FE replays from.
                self._send(200, json.dumps(SUITE.list_journeys_meta()))
            elif path == "/api/voice":                     # voice status: STT providers + per-engine TTS
                from voice import stt as voice_stt
                import urllib.request as _u

                def _probe(name, base):
                    """STATUS probe (lane B): is this engine's service up, and what voices does it
                    report? A status read NEVER raises on a down engine (unlike /api/tts which fails
                    loud) — it reports up:false so the picker can grey it out. Liveness is checked via
                    `GET /voices` (which is IN the shared engine contract — POST /tts + GET /voices)
                    rather than /health (NOT in the contract — the five new engines need not implement
                    it; only Kokoro happens to). One call → up AND the voice list together; Kokoro has
                    /voices too, so this is uniform across every engine."""
                    info = {"engine": name, "url": base, "up": False, "voices": []}
                    try:
                        with _u.urlopen(base + "/voices", timeout=3) as r:
                            v = json.loads(r.read() or b"{}")
                        info["up"] = True
                        info["voices"] = v.get("voices", [])
                        if v.get("default"):
                            info["default"] = v["default"]
                    except Exception:
                        pass                                # unreachable / not-yet-serving → up:false
                    return info

                engines = [_probe("kokoro", TTS_URL)] + [
                    _probe(name, f"http://127.0.0.1:{port}")
                    for name, port in sorted(ENGINE_PORTS.items())]
                self._send(200, json.dumps({
                    "stt": voice_stt.available(),          # back-compat: id → bool (the old shape)
                    "stt_default": voice_stt.stt_default(),  # back-compat: the default ear id
                    "stt_registry": voice_stt.available_stt(),  # the RICH ear registry (label/kind/detail)
                    "stt_active": SUITE.rhm_config().get("stt") or voice_stt.active_ear(),  # selected ear
                    "tts_up": engines[0]["up"],            # back-compat: the default (kokoro) up?
                    "engines": engines,                    # lane B: per-engine availability + voices
                    "voice_enabled": SUITE.voice_enabled()}))  # lane H: the per-mode voice toggle state
            elif path == "/api/personas":                  # G2.4/G3: the 5-cast registry the picker reads
                from voice import personas as voice_personas   # stdlib-only data module (3.14-importable)
                self._send(200, json.dumps(voice_personas.list_personas()))
            elif path == "/api/trial/sessions":            # G4.6: the recorded trial sessions (the debrief's set)
                self._send(200, json.dumps(SUITE.trial_sessions()))
            elif path == "/api/trial/transcript":          # G4.6: a trial session's CAS transcript (fail loud if unrecorded)
                self._send(200, json.dumps(SUITE.trial_transcript(q["session"])))
            elif path in ("/api/voice/services", "/api/voice/ears"):  # G4.7: voice-service lifecycle (ears+engines: up/warming/down + VRAM)
                from voice import lifecycle as voice_lc       # /api/voice/ears kept as a back-compat alias
                for w in voice_lc.poll_wake():                # G7-loadcost: a service just became up → record its WAKE-TIME
                    SUITE.emit_run_record("voice.load", w["wake_ms"], service=w["service"], vram_used_mb=w.get("vram_used_mb"))
                self._send(200, json.dumps(voice_lc.status()))
            elif path == "/api/cognition/models_for_role":   # AUTHORING SELECT: models whose provides ⊇ requires
                q = parse_qs(urlparse(self.path).query)       # module-level import (bridge.py:15) — no local shadow
                requires = q.get("requires", [""])[0]
                self._send(200, json.dumps(SUITE.models_for_role(requires)))
            elif path == "/api/cognition/inputs":          # AUTHORING SELECT: the addresses a role/rule can read
                self._send(200, json.dumps(SUITE.available_inputs()))
            elif path == "/api/cognition/field_types":     # AUTHORING SELECT: the closed output-schema field types
                self._send(200, json.dumps(SUITE.field_types()))
            # --- LANE-BRIDGE: the cognition-engine HUMAN-face reads (G2; reflects-never-owns; reuse the
            #     SAME Suite methods the MCP tools call — list_runs/find_runs/find_relations/corpus). ---
            elif path == "/api/cognition/list_runs":       # #54 RUN INDEX: discover past engine runs (read)
                # → {runs:[{address,op,run_op,turn_id,role,duration_ms,seq,ts}], total_records}. Delegates to
                # Suite.list_runs (the SAME read-time op.run projection the MCP list_runs tool serves). op
                # filters to one ENGINE_RUN_OP (fail-loud on a fabricated op); run_op by operation; since=seq.
                self._send(200, json.dumps(SUITE.list_runs(
                    op=q.get("op"), run_op=q.get("run_op"),
                    since=int(q.get("since", -1)), limit=int(q.get("limit", 50)))))
            elif path == "/api/cognition/find_runs":       # #54: the FILTERED run index (by role/op/run_op)
                self._send(200, json.dumps(SUITE.find_runs(
                    role=q.get("role"), op=q.get("op"), run_op=q.get("run_op"),
                    since=int(q.get("since", -1)), limit=int(q.get("limit", 50)))))
            elif path == "/api/cognition/find_relations":  # GROUP L2: the inversion-finder (near∩¬far)
                # ?item=&near_space=&far_space=[&k=&min_score=] → items NEAR the item in near_space but NOT
                # near it in far_space ("same principle, different subject"). Delegates to Suite.find_relations
                # (anchored on the item's persisted per-space vector — NO live-embedder dependency; the
                # SAME method the MCP find_relations tool serves). A missing axis → KeyError → 400 (fail loud).
                self._send(200, json.dumps(SUITE.find_relations(
                    q["item"], near_space=q["near_space"], far_space=q["far_space"],
                    k=int(q.get("k", 10)), min_score=float(q.get("min_score", 0.5)),
                    emb=q.get("emb") or None)))   # ?emb= → inversion within an embedder LAYER (None=BGE default)
            elif path == "/api/cognition/corpus":          # GROUP D5: the discovered corpus records (LIST/READ)
                # Two read shapes on ONE route (NOT /api/corpus — that is the mockup-gallery index, a
                # name-collision; verified). ?address=… → read ONE record back (read_corpus_record, honest
                # None if never written). Else → the discovered corpus PROJECTION, filtered by any of
                # project/kind/projection/source_address (find_corpus; list_corpus when no filter). Both
                # delegate to the SAME Suite methods the MCP face uses (the corpus.record event-log
                # projection — no parallel DB). Writes are a POST to the same path.
                if q.get("address"):
                    self._send(200, json.dumps({"record": SUITE.read_corpus_record(q["address"])}))
                elif any(q.get(k) for k in ("project", "kind", "projection", "source_address")):
                    self._send(200, json.dumps({"records": SUITE.find_corpus(
                        project=q.get("project"), kind=q.get("kind"),
                        projection=q.get("projection"), source_address=q.get("source_address"))}))
                else:
                    self._send(200, json.dumps({"records": SUITE.list_corpus(project=q.get("project"))}))
            elif path == "/api/roles":                     # G4.2: the model-ROLE registry (judge + future) the config lab binds
                self._send(200, json.dumps(SUITE.roles()))
            elif path == "/api/run-stats":                 # G7 rollup: op.run run-records → distributions (learning by use)
                self._send(200, json.dumps(SUITE.run_stats(op=q.get("op"))))
            elif path == "/api/knobs":                     # G8.1: the dynamic configurable-knob surface for a (loaded) model
                self._send(200, json.dumps(SUITE.knobs_for(model=q.get("model"), base_url=q.get("base_url"))))
            elif path == "/api/voice/engine-knobs":        # S5: per-TTS-engine knob catalog (all, or ?engine=)
                self._send(200, json.dumps(SUITE.voice_engine_knobs(q.get("engine"))))
            elif path == "/api/voice/paths":               # Tier-4: the swappable voice-path registry (pipeline vs s2s)
                self._send(200, json.dumps(SUITE.voice_paths()))
            else:
                self._send(404, "{}")
        except Exception as e:                             # fail loud to the UI (parity with do_POST)
            self._send(400, json.dumps({"error": f"{type(e).__name__}: {e}"}))

    def _stream(self, q):
        """GET /api/stream — Server-Sent Events (G). Tails the SHARED events.jsonl (so it captures
        BOTH faces, not an in-memory queue), pushing each new event as `id: <seq>\\ndata: <json>\\n\\n`.
        Cursor = ?since= or the Last-Event-ID reconnect header (default -1 = from the start). Heartbeat
        every ~15s so idle proxies don't drop the socket. NOT routed through _send (which sets
        Content-Length + closes). Fail loud: only client-disconnect is swallowed, never a real error."""
        since = q.get("since")
        if since is None:
            since = self.headers.get("Last-Event-ID", "-1")   # gapless reconnect
        try:
            cursor = int(since)
        except (TypeError, ValueError):
            cursor = -1
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        last_beat = time.monotonic()
        try:
            while True:
                for ev in SUITE.events_since(cursor):
                    self.wfile.write(
                        f"id: {ev['seq']}\ndata: {json.dumps(ev)}\n\n".encode())
                    self.wfile.flush()
                    cursor = ev["seq"]
                if time.monotonic() - last_beat >= 15:
                    self.wfile.write(b": keepalive\n\n")
                    self.wfile.flush()
                    last_beat = time.monotonic()
                time.sleep(0.4)
        except (BrokenPipeError, ConnectionResetError):
            return                                          # client closed — done, not an error

    def _chat_stream(self):
        """B1 TEXT-streaming turn: the TEXT-ONLY sibling of _voice_stream — drive SUITE.chat_parts() and
        stream each completed part as an NDJSON line so the reply appears INCREMENTALLY in the RHM chat
        (instead of the whole-reply wait of /api/chat). ADDITIVE: /api/chat (non-stream) is UNTOUCHED.

        Reuses the PURE driver _stream_parts (no copy of the producer/consumer overlap) with a TEXT-ONLY
        wiring: speak_fn is a NOOP (lambda s: b"" — same shape voice uses for voice-off at bridge.py:852)
        and emit_fn is a NOOP (lambda c: None — we don't stream per-sentence audio chunks here, only the
        per-PART text via on_part). The brain↔TTS overlap structure still runs (the producer pulls parts
        ahead) but nothing synthesises — _stream_parts still DRAINS the generator so chat_parts' epilogue
        (the SINGLE chat append + SINGLE _emit('chat')) runs exactly once, giving us the persisted history.

        SUPERSET-not-degrade (no-silent-failures): the non-stream /api/chat path consumes r.proposal (the
        I3 consent card), r.action (post-dispatch reactions), r.thread_id/r.history. _stream_parts returns
        only `reply`, so we TEE the generator to capture the FINAL part dict (which carries the epilogue's
        full 7-key return at final['result'], or the prologue's at final['early_return']) and fold
        proposal/action/thread_id/history/reply into the {type:done} event. The FE's onDone then reuses the
        SAME handlers (setProposal/applyActionReactions/setThreadId) → streaming loses NOTHING.

        Response = newline-delimited JSON:
          {type:part,idx,text,final}  (per completed part — the incremental display) ·
          {type:done,reply,proposal,action,thread_id,history,parts}  (terminal — the FE's authoritative state) ·
          {type:error,error,step}  (fail-loud)
        The reply on `done` is the CANONICAL joined reply the epilogue wrote to history (never a manual
        re-join of part texts — the parts are display-incremental; the done text is the source of truth)."""
        import re as _re
        b = self._body()                                      # read the request body BEFORE send_response (mirrors voice@764)
        message = b.get("message")
        gid = b.get("graph_id", DEMO)
        focus = b.get("focus")
        self.send_response(200)
        self.send_header("Content-Type", "application/x-ndjson")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "close")
        self.end_headers()

        import select as _sel, socket as _sock
        gone = [False]                                        # client-disconnect flag (cancel a speculative turn)

        def emit(obj):
            try:
                self.wfile.write((json.dumps(obj) + "\n").encode()); self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError, OSError):
                gone[0] = True                                # client hung up — stop, don't raise

        def client_gone():
            if gone[0]:
                return True
            try:
                r, _, _ = _sel.select([self.connection], [], [], 0)
                if r and self.connection.recv(1, _sock.MSG_PEEK) == b"":
                    gone[0] = True
            except Exception:
                pass
            return gone[0]

        step = "init"
        try:
            if not message:
                raise ValueError("/api/chat/stream needs {message} (fail loud)")

            def _split(text):                                 # same per-part sentence split shape as voice (unused-result but keeps the contract)
                return [s.strip() for s in _re.split(r'(?<=[.!?])\s+', text) if s.strip()] or ([text] if text.strip() else [])

            box: dict = {}                                    # captures the FINAL part dict (carries result/early_return)
            idx_box = [0]                                     # the per-part display index (on_part gives only text — track idx in a closure)

            def _tee(gen):
                # pass each part THROUGH while capturing the FINAL one (its result/early_return carries the
                # epilogue's 7-key return — proposal/action/thread_id/history — that _stream_parts discards).
                for p in gen:
                    if p.get("final"):
                        box["final"] = p
                    yield p

            def _emit_part(text):                             # the incremental display event (per completed part)
                emit({"type": "part", "idx": idx_box[0], "text": text, "final": False})
                idx_box[0] += 1

            step = "think"
            parts_gen = SUITE.chat_parts(message, gid, focus)
            # TEXT-ONLY wiring: NOOP speak_fn/emit_fn (no audio); on_part streams each part's text. The driver
            # still DRAINS the generator so the epilogue runs (the persisted chat turn) — voice-off does the
            # same at bridge.py:851-853.
            res = _stream_parts(_tee(parts_gen), speak_fn=lambda s: b"", emit_fn=lambda c: None, gone=gone,
                                split_sentences=_split, on_part=_emit_part, should_stop=client_gone)
            if res["cancelled"] or gone[0]:
                return                                        # client disconnected mid-stream — socket's dead, nothing to send
            # the CANONICAL turn-end state from the captured final part: result (normal/bypass) OR early_return
            # (off/refusal prologue). reply prefers the epilogue's joined reply (res['reply']) — the source of truth.
            final = box.get("final") or {}
            ret = final.get("result") if isinstance(final.get("result"), dict) else (
                  final.get("early_return") if isinstance(final.get("early_return"), dict) else {})
            done = {"type": "done", "parts": res["parts_done"],
                    "reply": (res["reply"] or ret.get("reply") or "").strip(),
                    "proposal": ret.get("proposal"), "action": ret.get("action"),
                    "thread_id": ret.get("thread_id"), "history": ret.get("history")}
            emit(done)
        except Exception as e:                                # fail loud — to the client (the socket is the only channel here)
            try:
                emit({"type": "error", "error": f"{type(e).__name__}: {e}", "step": step})
            except Exception:
                pass

    def _claude_stream(self):
        """S1 (overnight) — the BUILDER side-panel turn: stream one Claude Code session turn as NDJSON.
        Body: {prompt, session_id?, address?}. The pointed-at ui:// address's help bundle rides in as
        the turn's context block (the indicated-chip semantics of the RHM chat, aimed at the builder).
        OPERATOR FACE ONLY + plan-mode default (see runtime/ui_claude_session.py — the floor note).
        Events: {type:init,session_id} · {type:text,text} · {type:tool,name,detail} ·
        {type:done,result,session_id,num_turns,is_error} · {type:error,error}. Client-disconnect
        terminates the subprocess (no stranded claude processes)."""
        from runtime.ui_claude_session import run_turn
        b = self._body()
        prompt = b.get("prompt")
        sid = b.get("session_id") or None
        address = b.get("address") or None
        # FORAGER D1 (additive) — the operator's SELECTED CONTEXT SET from the canvas (multi-selected
        # forager circles → "give to builder"). An opaque pre-composed block; absent = today's body.
        set_block = b.get("context_block") or None
        self.send_response(200)
        self.send_header("Content-Type", "application/x-ndjson")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "close")
        self.end_headers()

        import select as _sel, socket as _sock
        gone = [False]

        def emit(obj):
            try:
                self.wfile.write((json.dumps(obj) + "\n").encode()); self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError, OSError):
                gone[0] = True

        def client_gone():
            if gone[0]:
                return True
            try:
                r, _, _ = _sel.select([self.connection], [], [], 0)
                if r and self.connection.recv(1, _sock.MSG_PEEK) == b"":
                    gone[0] = True
            except Exception:
                pass
            return gone[0]

        try:
            if not prompt:
                raise ValueError("/api/claude/turn needs {prompt} (fail loud)")
            ctx = None
            if address:
                try:                                          # the pointed-at element's bundle — degrade-clean
                    h = SUITE.address_help(address)
                    bits = [f"Address: {address}"]
                    for leg in ("what_this_is", "how_to_use"):
                        v = (h.get(leg) or {}) if isinstance(h.get(leg), dict) else h.get(leg)
                        if v:
                            bits.append(f"{leg}: {json.dumps(v, default=str)[:600]}")
                    ctx = "\n".join(bits)
                except Exception as e:
                    ctx = f"Address: {address} (help bundle unavailable: {type(e).__name__})"
            # FORAGER D1 (additive) — compose the selection-set block WITH the pointed-address bundle
            # when both ride the turn (the locus first, then the sculpted set). FAIL-SAFE: a non-string
            # degrades through json (never raises out), a hard 8KB cap bounds a misbehaving client, and
            # any error here NEVER kills the turn — the prompt still runs (degrade-clean, like the
            # address bundle above). The block is opaque to run_turn (context_block was already so).
            if set_block:
                try:
                    cb = set_block if isinstance(set_block, str) else json.dumps(set_block, default=str)
                    cb = cb[:8192]
                    ctx = f"{ctx}\n\n{cb}" if ctx else cb
                except Exception:
                    pass
            for ev in run_turn(prompt, session_id=sid, context_block=ctx, should_stop=client_gone):
                emit(ev)
                if gone[0]:
                    return
        except Exception as e:                                # fail loud — to the client
            try:
                emit({"type": "error", "error": f"{type(e).__name__}: {e}"})
            except Exception:
                pass

    def _voice_stream(self):
        """Tier-1 STREAMING voice turn: hear → think-IN-PARTS → SPEAK part-by-part. The win over
        /api/voice/turn: instead of synthesising the WHOLE reply before any audio (the ~28s-on-a-long-
        reply wall), we drive the brain as a SEQUENCE OF PARTS (SUITE.chat_parts, G4) and stream each
        completed part's sentences AS THE NEXT PART IS STILL GENERATING — so first audio plays at
        ~(silence+STT+PART_1-gen+TTS-of-one-short-sentence), and the brain runs CONCURRENTLY with synth.

        CONCURRENT COGNITION G6 — the PART is the TTS streaming unit (C6.1): the multi-part design IS
        the voice-streams-as-it-thinks mechanism. Two overlaps now COMPOSE: parts overlap brain↔TTS
        (this), sentences overlap synth↔playback (the FE's playCursorRef). A brain-PRODUCER thread runs
        chat_parts() ahead of the SYNTH-CONSUMER (the handler thread, the single emitter) — see
        _stream_parts. A trivial one-liner → ONE part (chat_parts' brevity bypass) → a single synth,
        no regression.

        Response = newline-delimited JSON events the FE reads + plays incrementally (SUPERSET of the old
        contract — additive, no FE change required):
          {type:transcript,text} · {type:part,idx,text} (NEW, per completed part) ·
          {type:chunk,idx,text,wav_b64,ms} (per sentence, MONOTONIC idx ACROSS parts — UNCHANGED shape) ·
          {type:reply,text} (the ASSEMBLED full reply, emitted ONCE before done — the FE's single append) ·
          {type:done,total_ms,reply,parts,chunks}
        Engine-agnostic. Fail-loud surfaces as a {type:error} event then closes."""
        import base64 as _b64, re as _re, time as _t
        from urllib.parse import urlparse as _up, parse_qs as _pq
        from voice import loop as voice_loop, stt as voice_stt, lifecycle as voice_lc, personas as voice_personas
        from voice import speakable as voice_speakable
        self.close_connection = True
        vq = {k: v[0] for k, v in _pq(_up(self.path).query).items()}
        persona = (vq.get("persona") or "").strip()
        gid = vq.get("graph_id", DEMO)
        trial_session = (vq.get("trial_session") or "").strip()   # V3.1: when present, RECORD the turn
        audio = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        self.send_response(200)
        self.send_header("Content-Type", "application/x-ndjson")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "close")
        self.end_headers()

        import select as _sel, socket as _sock
        gone = [False]                                        # Tier-2: client-disconnect flag (cancel a speculative turn)

        def emit(obj):
            try:
                self.wfile.write((json.dumps(obj) + "\n").encode()); self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError, OSError):
                gone[0] = True                                # client hung up (e.g. resumed talking) — stop, don't raise

        def client_gone():
            """Tier-2: PROACTIVELY detect a client disconnect (a speculative turn cancelled on resume) so
            we stop BEFORE the next expensive synth — more reliable + prompt than waiting for a write to
            fail (TCP buffers the first post-close write). select+MSG_PEEK: socket readable AND 0 bytes
            peeked = EOF (closed). Readable-with-data is unexpected here (body's read) → treat as alive."""
            if gone[0]:
                return True
            try:
                r, _, _ = _sel.select([self.connection], [], [], 0)
                if r and self.connection.recv(1, _sock.MSG_PEEK) == b"":
                    gone[0] = True
            except Exception:
                pass
            return gone[0]
        import uuid as _uuid
        turn_id = _uuid.uuid4().hex[:12]      # correlates every record + client event for THIS turn
        transcript = ""; reply = ""; eng = ""; step = "init"; t0 = _t.monotonic()
        try:
            if not persona:
                raise ValueError("/api/voice/stream needs ?persona=<id> (fail loud)")
            if SUITE.rhm_config().get("voice_path") == "s2s":
                emit({"type": "error", "error": "voice_path is 's2s' but no S2S runner/model exists yet — "
                      "this is the pipeline route. Set voice_path=pipeline or download an S2S model."}); return
            p = voice_personas.get_persona(persona)               # fail loud on unknown persona
            _rc = SUITE.rhm_config()
            eng_override = (_rc.get("tts_engine") or "").strip() or None   # G4.2 engine/voice override slots
            voice_override = (_rc.get("tts_voice") or "").strip() or None
            eng = eng_override or p["engine"]                     # override wins; else the persona's engine
            speak_reply = SUITE.voice_enabled()
            # boot-on-demand (only if we'll speak)
            if speak_reply:
                svc = voice_lc.engine_service_for(eng)
                if svc and not voice_lc.is_up(voice_lc._loadable()[svc]):
                    emit({"type": "error", "error": f"engine {eng} ({svc}) is down — load it "
                          f"(POST /api/voice/load) or use ?boot=1 on /api/voice/turn first"}); return
            ear = SUITE.rhm_config().get("stt") or voice_stt.active_ear()
            step = "stt"
            heard = voice_stt.transcribe(audio, provider=ear)
            transcript = (heard.get("text") or "").strip()
            stt_ms = int((_t.monotonic() - t0) * 1000)
            emit({"type": "transcript", "text": transcript, "ms": stt_ms})
            if not transcript:
                raise RuntimeError("empty transcript — STT heard nothing (fail loud)")
            step = "think"
            think_t0 = _t.monotonic()
            voice_arg = voice_override or voice_loop._voice_arg_for(p, eng)   # G4.2: voice for the SELECTED engine (any persona × any engine)

            def _split(text):                                 # the existing per-part sentence split (unchanged shape)
                return [s.strip() for s in _re.split(r'(?<=[.!?])\s+', text) if s.strip()] or ([text] if text.strip() else [])

            def _speak(sent):
                cs = _t.monotonic()
                wav = voice_loop.speak(sent, eng, voice=voice_arg)   # `eng` honours the override; short sentence → fast synth
                _speak.last_ms = int((_t.monotonic() - cs) * 1000)
                return wav
            _speak.last_ms = 0

            def _emit_chunk(c):                               # the SINGLE emitter — ndjson line ordering is safe (one thread)
                emit({"type": "chunk", "idx": c["idx"], "text": c["text"],
                      "wav_b64": _b64.b64encode(c["wav"]).decode(), "ms": _speak.last_ms})

            def _emit_part(text):                             # NEW additive event: a completed part (the current FE ignores it)
                emit({"type": "part", "idx": -1, "text": text})

            # G6: drive chat_parts() with the brain↔TTS overlap. The brain produces parts AHEAD while
            # the synth-consumer (this thread) speaks+emits each part's sentences (C6.1). chat_parts'
            # epilogue (the SINGLE chat append + SINGLE _emit('chat')) runs inside the generator → we get
            # "one chat event regardless of N parts" for free; we never emit our own chat event.
            parts_gen = SUITE.chat_parts(transcript, gid, turn_id=turn_id)
            if not speak_reply:
                step = "think"                                # voice off → still DRAIN the generator (the epilogue MUST run
                res = _stream_parts(                          # to record the turn) but synth NOTHING.
                    parts_gen, speak_fn=lambda s: b"", emit_fn=lambda c: None, gone=gone,
                    split_sentences=_split, should_stop=client_gone)
                reply = (res["reply"] or "").strip()
                think_ms = int((_t.monotonic() - think_t0) * 1000)
                if trial_session:
                    try:
                        SUITE.trial_record_turn(trial_session, "operator", transcript, character=persona)
                        SUITE.trial_record_turn(trial_session, "character", reply, character=persona)
                    except Exception as _e:
                        emit({"type": "note", "text": f"(recording skipped: {type(_e).__name__})"})
                emit({"type": "reply", "text": reply, "ms": think_ms})
                emit({"type": "done", "total_ms": int((_t.monotonic() - t0) * 1000), "spoke": False,
                      "reply": reply, "parts": res["parts_done"], "turn_id": turn_id})
                return

            step = "tts"
            # V-C/V-D the SPEAKABLE LAYER bound to THIS engine — folded into the parts overlap: each part's
            # text is cleaned (markdown/code/urls/emoji stripped; canonical expression tags mapped to `eng`'s
            # syntax or dropped) BEFORE its sentence split. The {type:reply} event + trial recording stay RAW
            # (only the TTS-bound text is cleaned). A non-fatal warn (unknown engine) → {type:note}.
            res = _stream_parts(parts_gen, speak_fn=_speak, emit_fn=_emit_chunk, gone=gone,
                                split_sentences=_split, on_part=_emit_part, should_stop=client_gone,
                                clean_fn=lambda txt: voice_speakable.speakable(
                                    txt, eng, warn=lambda w: emit({"type": "note", "text": w})))
            reply = (res["reply"] or "").strip()
            think_ms = int((_t.monotonic() - think_t0) * 1000)
            total = int((_t.monotonic() - t0) * 1000)
            step = "done"
            if res["cancelled"] or gone[0]:                   # cancelled mid-stream — record it (server-side; the socket's dead)
                SUITE.emit_run_record("voice.stream.cancelled", total, turn_id=turn_id, ok=False, step="cancelled",
                                      stt_ms=stt_ms, think_ms=think_ms, chunks_done=res["chunks_done"],
                                      chunks_total=res["chunks_total"], parts_done=res["parts_done"],
                                      persona=persona, engine=eng, transcript=transcript[:2000], reply=reply[:4000])
                return
            # trial recording ONCE at turn end, with the ASSEMBLED reply the epilogue wrote to history
            if trial_session:                                 # V3.1: RECORD the turn into the trial session
                try:                                          # (the EXISTING trial_record_turn; reuse, don't reinvent)
                    SUITE.trial_record_turn(trial_session, "operator", transcript, character=persona)
                    SUITE.trial_record_turn(trial_session, "character", reply, character=persona)
                except Exception as _e:
                    emit({"type": "note", "text": f"(recording skipped: {type(_e).__name__})"})  # never break the turn
            # NOTE (additive merge — main↔cognition): main's OLD per-sentence synth loop here is SUPERSEDED by
            # the G6 _stream_parts overlap above (parts-as-TTS-units, brain↔TTS overlap). main's V-C/V-D
            # SPEAKABLE LAYER was NOT dropped — it is folded INTO _stream_parts via the `clean_fn` arg
            # (per-part speakable() cleaning before the sentence split). Both survive: the overlap structure
            # AND the speakable cleaning. The reply/{type:reply} + trial recording stay RAW (above); only the
            # TTS-bound text is cleaned (inside _stream_parts).
            # the DETAILED, durable per-turn log line (Tim 2026-06-07): the texts + per-step timings + config,
            # so a whole turn is investigable from the event log (op=voice.stream, keyed by turn_id).
            SUITE.emit_run_record("voice.stream", total, turn_id=turn_id, ok=True, stt_ms=stt_ms, think_ms=think_ms,
                                  chunks=res["chunks_done"], parts=res["parts_done"], staged=res["staged"],
                                  persona=persona, engine=eng, ear=ear,
                                  input_mode=SUITE.rhm_config().get("voice_input_mode"),
                                  transcript=transcript[:2000], reply=reply[:4000])
            emit({"type": "reply", "text": reply, "ms": think_ms})   # the FE's single assistant-append (moved to end)
            emit({"type": "done", "total_ms": total, "spoke": True, "chunks": res["chunks_done"],
                  "parts": res["parts_done"], "reply": reply, "turn_id": turn_id})
        except Exception as e:                                     # fail loud — to the client AND DURABLY to the log
            # the error used to vanish with the socket. Now a durable record: WHICH step failed, the error,
            # the texts so far, the config — everything needed to investigate a failed turn from the log.
            try:
                SUITE.emit_run_record("voice.stream", int((_t.monotonic() - t0) * 1000), turn_id=turn_id, ok=False,
                                      step=step, error=f"{type(e).__name__}: {e}", persona=persona, engine=eng,
                                      ear=SUITE.rhm_config().get("stt"), transcript=transcript[:2000], reply=reply[:4000])
            except Exception:
                pass
            try:
                emit({"type": "error", "error": f"{type(e).__name__}: {e}", "step": step, "turn_id": turn_id})
            except Exception:
                pass

    def do_POST(self):
        # HTTP/1.1 keeps sockets alive (needed for the GET /api/stream SSE). But a POST handler that
        # doesn't drain its request body (e.g. /api/react, the 404 branch) would leave bytes that the
        # next request on a reused connection mis-parses → garbled 400s in a browser (which pools
        # connections; curl uses a fresh socket per call, so it's invisible there). Force-close POST
        # sockets — GET (incl. the stream) still keeps alive.
        self.close_connection = True
        try:
            if self.path == "/api/stt":                   # raw audio bytes in → transcript out
                # The ear is chosen by the SELECTED provider (rhm_config().stt — the config slot the
                # suite lane added, mirroring the brain-model slot), NOT a literal default. This closes
                # the bug where the bridge defaulted assemblyai while the loop defaulted local — ONE
                # source of selection now. A selected-but-down ear → transcribe() raises LOUD (fail
                # loud, no fallback); _send's except surfaces it to the UI.
                from voice import stt as voice_stt
                ln = int(self.headers.get("Content-Length", 0))
                audio = self.rfile.read(ln)
                ear = SUITE.rhm_config().get("stt") or voice_stt.active_ear()
                self._send(200, json.dumps(voice_stt.transcribe(audio, provider=ear)))
                return
            if self.path == "/api/voice/stt-partial":     # Tier-2: PARTIAL transcript of the audio-so-far (FE drives the window)
                from voice import stt as voice_stt
                import time as _t
                ln = int(self.headers.get("Content-Length", 0)); audio = self.rfile.read(ln)
                ear = SUITE.rhm_config().get("stt") or voice_stt.active_ear()
                t0 = _t.monotonic()
                r = voice_stt.transcribe_partial(audio, provider=ear)
                r["ms"] = int((_t.monotonic() - t0) * 1000)
                self._send(200, json.dumps(r))
                return
            if self.path == "/api/tts":                   # text in → wav out (routed by engine)
                # lane B: parse the body to read the optional `engine` field, route to that engine's
                # service (kokoro/absent → TTS_URL; others → ENGINE_PORTS), and forward ONLY the
                # downstream contract {text,voice?,speed?} (engine stripped — the engine's /tts must
                # not need to know its own name). Fail loud naming the engine+port if it's down (no
                # silent failure — AGENTS.md rule 4). DEFAULT (no engine) is byte-identical to before.
                import urllib.error as _ue
                import urllib.request as _u
                raw = self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}"
                payload = json.loads(raw or b"{}")
                engine = payload.get("engine")            # explicit engine wins; unknown → fail loud
                if not engine:
                    # No explicit engine → speak in the CONFIGURED voice (the tts_engine override, else the
                    # active persona's engine) — NOT a generic kokoro default. So EVERY voice-out (a text
                    # reply via speakReply, a voice reply, walkthrough narration) uses the chosen Company
                    # voice. Resolved the SAME way /api/voice/stream resolves it (one source — eng_override
                    # → persona.engine). Falls back to kokoro (TTS_URL) only when nothing is configured
                    # (no override AND no persona, or the persona declares no engine).
                    _rc = SUITE.rhm_config()
                    engine = (_rc.get("tts_engine") or "").strip() or None
                    if not engine and (_rc.get("persona") or "").strip():
                        from voice import personas as _vp
                        try:
                            engine = (_vp.get_persona(_rc["persona"].strip()) or {}).get("engine") or None
                        except Exception:
                            engine = None                 # unknown persona → kokoro fallback (never crash a reply)
                base = _tts_base_url(engine)              # raises ValueError on an unknown engine
                fwd = {k: v for k, v in payload.items() if k != "engine"}
                # V-C/V-D the SPEAKABLE LAYER on the GENERIC text→wav path too (speakReply text-replies,
                # walkthrough narration — also "reply text → TTS"). One universal transform everywhere
                # reply text becomes speech: clean markdown/code/urls/emoji + map canonical expression
                # tags to THIS engine's syntax (kokoro/absent → no tags → stripped). Cleaning already-
                # clean text is idempotent, so this is safe + complete. Empty `text` is left as-is for
                # the downstream engine to handle; only non-empty text is run through (speakable raises
                # on a non-empty-but-cleans-to-nothing string — that fail-loud is desirable here too).
                if isinstance(fwd.get("text"), str) and fwd["text"].strip():
                    from voice import speakable as _vsp
                    fwd["text"] = _vsp.speakable(fwd["text"], engine)
                req = _u.Request(base + "/tts", data=json.dumps(fwd).encode(),
                                 headers={"Content-Type": "application/json"})
                try:
                    with _u.urlopen(req, timeout=60) as r:
                        self._send(200, r.read(), "audio/wav")
                except (_ue.URLError, ConnectionError, OSError) as e:
                    port = base.rsplit(":", 1)[-1]
                    raise RuntimeError(
                        f"{engine or 'kokoro'} TTS service at {base} (port {port}) unreachable: "
                        f"{type(e).__name__}: {e} — start the engine's service (fail loud).")
                return
            if self.path.split("?")[0] == "/api/voice/turn":   # G1.1: ONE live turn — hear→think→speak
                # The core circuit, reusing voice.loop.loop_turn (NOT a parallel hear/think/speak). We
                # inject the IN-PROCESS Suite.chat as the brain step (loop.py's designed injection point)
                # AND pass the selected ear explicitly → loop_turn makes NO HTTP call back to this bridge
                # (one in-process brain, one event log). Input: raw audio body + ?persona=<id>. Output:
                # JSON with the wav base64'd (a turn is hear→think→speak; the reply text + the spoken wav
                # travel together, so the UI shows the transcript/reply AND plays the audio from one call).
                # Fail loud: empty transcript, unknown persona, a down engine/ear all raise → 400.
                import base64 as _b64
                from urllib.parse import urlparse as _up, parse_qs as _pq
                from voice import loop as voice_loop, stt as voice_stt
                vq = {k: v[0] for k, v in _pq(_up(self.path).query).items()}
                persona = (vq.get("persona") or "").strip()
                if not persona:
                    raise ValueError("/api/voice/turn needs ?persona=<id> (fail loud)")
                gid = vq.get("graph_id", DEMO)
                audio = self.rfile.read(int(self.headers.get("Content-Length", 0)))
                if not audio:
                    raise ValueError("/api/voice/turn got empty audio (fail loud)")
                if SUITE.rhm_config().get("voice_path") == "s2s":     # Tier-4: s2s path has no runner yet
                    raise RuntimeError("voice_path is 's2s' but no S2S runner/model exists yet — this is "
                                       "the PIPELINE route. Set voice_path=pipeline, or download an S2S "
                                       "model + build the s2s runner. Refusing to silently use the pipeline.")
                # G4.4 voice gate: the per-mode voice_enabled toggle. When voice is OFF (a text-only
                # presence), the turn is hear→think only — no speak, and NO engine boot for nothing.
                speak_reply = SUITE.voice_enabled()
                # BOOT-ON-DEMAND ("make it all live"): the persona needs its TTS engine up. Check BEFORE
                # the turn so we don't burn a brain call then fail at speak. Only when we WILL speak. If
                # down: ?boot=1 launches it (returns 'booting' — the UI shows warming + retries when up;
                # we do NOT block the request ~25s); else a legible refusal naming the load endpoint.
                from voice import lifecycle as voice_lc, personas as voice_personas
                _rc = SUITE.rhm_config()
                eng_override = (_rc.get("tts_engine") or "").strip() or None   # G4.2 engine override slot
                voice_override = (_rc.get("tts_voice") or "").strip() or None
                eng = eng_override or voice_personas.get_persona(persona)["engine"]   # override wins; else persona
                if speak_reply:
                    svc = voice_lc.engine_service_for(eng)
                    if svc and not voice_lc.is_up(voice_lc._loadable()[svc]):
                        if vq.get("boot") == "1":
                            booted = voice_lc.load(svc)           # warming; fail-loud if it won't fit
                            self._send(200, json.dumps({"booting": booted, "persona": persona, "engine": eng,
                                "note": f"engine {eng} is loading — retry the turn when status() shows it up"}))
                            return
                        raise RuntimeError(
                            f"persona {persona!r} needs TTS engine {eng!r} ({svc}) which is DOWN — load it "
                            f"first (POST /api/voice/load {{\"service\":\"{svc}\"}}) or call this with ?boot=1. "
                            f"Refusing a silent stall (fail loud).")
                ear = SUITE.rhm_config().get("stt") or voice_stt.active_ear()
                # G7 timing: split the turn into stt/think/tts using loop_turn's EXISTING callbacks as
                # markers (on_transcript fires after STT, on_reply after THINK) — no new plumbing.
                import time as _t
                marks = {}
                t0 = _t.monotonic()
                r = voice_loop.loop_turn(
                    audio, persona, graph_id=gid, stt_provider=ear, speak_reply=speak_reply,
                    engine_override=eng_override, voice_override=voice_override,   # any persona × any engine
                    think_fn=lambda txt: SUITE.chat(txt, gid),    # the ONE in-process brain
                    on_transcript=lambda _t_, _m=marks: _m.__setitem__("stt", int((_t.monotonic()-t0)*1000)),
                    on_reply=lambda _r_, _m=marks: _m.__setitem__("think_done", int((_t.monotonic()-t0)*1000)))
                total = int((_t.monotonic() - t0) * 1000)
                stt_ms = marks.get("stt")
                think_ms = (marks["think_done"] - stt_ms) if ("think_done" in marks and stt_ms is not None) else None
                tts_ms = (total - marks["think_done"]) if "think_done" in marks else None
                SUITE.emit_run_record("voice.turn", total, ok=True, stt_ms=stt_ms, think_ms=think_ms,
                                      tts_ms=tts_ms, persona=persona, engine=r.get("engine"),
                                      ear=ear, spoke=r.get("spoke", True),
                                      input_mode=SUITE.rhm_config().get("voice_input_mode"),
                                      transcript=(r.get("transcript") or "")[:2000], reply=(r.get("reply") or "")[:4000])
                wav = r.pop("wav", b"")
                r["wav_b64"] = _b64.b64encode(wav).decode()       # the spoken reply, travels with the text
                r["timing"] = {"total_ms": total, "stt_ms": stt_ms, "think_ms": think_ms, "tts_ms": tts_ms}
                self._send(200, json.dumps(r))
                return
            if self.path.split("?")[0] == "/api/voice/stream":   # G7/Tier-1: STREAMING turn — speak sentence-by-sentence
                self._voice_stream()
                return
            if self.path.split("?")[0] == "/api/chat/stream":    # B1: TEXT-streaming turn — parts appear incrementally
                self._chat_stream()
                return
            if self.path.split("?")[0] == "/api/claude/turn":    # S1: the BUILDER side-panel (Claude Code session turn)
                self._claude_stream()
                return
            if self.path == "/api/run":
                b = self._body()
                gid = b.get("graph_id", DEMO)
                result = SUITE.run(gid, force=b.get("force"))   # D4: force re-run bypasses the memo gate
                self._send(200, json.dumps(SUITE.state(gid, result)))
            elif self.path == "/api/set":
                b = self._body()
                gid = b.get("graph_id", DEMO)
                SUITE.set_config(gid, b.get("node"), b.get("config", {}))
                self._send(200, json.dumps(SUITE.state(gid)))
            elif self.path == "/api/move":              # C5: drag-end → write the sibling position/size
                b = self._body()
                gid = b.get("graph_id", DEMO)
                SUITE.set_position(gid, b["node"], b["x"], b["y"], b.get("w"), b.get("h"))
                self._send(200, json.dumps(SUITE.state(gid)))
            # --- on-canvas composition ---
            elif self.path == "/api/node":              # add a node from the palette
                b = self._body()
                gid = b.get("graph_id", DEMO)
                nid = SUITE.create_node(gid, b["type"], b.get("config", {}),
                                        position=b.get("position"))
                self._send(200, json.dumps({"id": nid, "state": SUITE.state(gid)}))
            elif self.path == "/api/connect":           # wire two nodes (type-checked)
                b = self._body()
                gid = b.get("graph_id", DEMO)
                SUITE.connect(gid, b["from_node"], b["from_port"], b["to_node"], b["to_port"])
                self._send(200, json.dumps(SUITE.state(gid)))
            elif self.path == "/api/delete-node":
                b = self._body()
                gid = b.get("graph_id", DEMO)
                SUITE.delete_node(gid, b["node"])
                self._send(200, json.dumps(SUITE.state(gid)))
            elif self.path == "/api/scale/build":         # Group 11 — (re)build a lens space's SCALE pyramid
                # The DISCOVERABLE rebuild path (registry-is-truth / no-silent-failure): the rung centroids the
                # meaning-field's ?rung= resolves over are derived .data; this regenerates them from the space's
                # unit vectors. {space (required), rungs?, force?}. Fail loud (empty/thin space → 400, not a
                # silent empty pyramid). Pure read of the embedder — centroids are means of on-disk vectors.
                b = self._body()
                from runtime import scale as _scale
                space = b.get("space")
                if not space:
                    self._send(400, json.dumps({"error": "scale/build needs a `space` (a built lens, e.g. topics)"}))
                else:
                    try:
                        res = _scale.build_scale_pyramid(SUITE.store, space=space,
                                                         rungs=b.get("rungs"), force=bool(b.get("force")))
                        self._send(200, json.dumps(res))
                    except ValueError as _ve:             # empty/thin space → fail loud, legible
                        self._send(400, json.dumps({"error": str(_ve), "space": space}))
            elif self.path == "/api/chat":                # right-hand-man — grounded conversation
                b = self._body()
                gid = b.get("graph_id", DEMO)
                self._send(200, json.dumps(SUITE.chat(b["message"], gid, focus=b.get("focus"))))
            elif self.path == "/api/conversation/new":    # S2: start a fresh conversation (becomes current)
                b = self._body()
                self._send(200, json.dumps(SUITE.new_conversation(b.get("title", ""))))
            elif self.path == "/api/model/load":          # S1: load a registered model service on demand (budget-gated)
                import sys as _sys
                _ops = os.path.join(ROOT, "ops", "cli")
                if _ops not in _sys.path:
                    _sys.path.insert(0, _ops)
                import gpu as _gpu, systemd as _sd, registry as _reg
                b = self._body()
                key = (b.get("service") or "").strip()
                reg = _reg.load()
                if key not in reg["services"]:
                    raise ValueError(f"unknown service {key!r}")
                svc = reg["services"][key]
                ok, need, free, _m = _gpu.check_fit(reg, [key])
                if not ok:                                 # fail loud: name what to unload (no silent OOM)
                    evict, proj = _gpu.plan_eviction(reg, [key], need, free)
                    raise RuntimeError(f"cannot load {key!r}: needs ~{need} MB, {free} MB free on the card. "
                                       + (f"Unload to make room — e.g. {', '.join(evict)} (→ ~{proj} MB). " if evict
                                          else "Nothing evictable frees enough. ") + "Refusing to OOM.\n" + _gpu.format_state(reg))
                started, msg = _sd.control(svc, "start")
                if not started:
                    raise RuntimeError(f"failed to start {key!r}: {msg} (journalctl --user -u {svc.get('manage',{}).get('unit')})")
                self._send(200, json.dumps({"service": key, "state": "warming", "note": "started — model loading; poll its endpoint"}))
            elif self.path == "/api/model/config":        # S5: set a serve-time config (e.g. context window) + restart
                import sys as _sys
                _ops = os.path.join(ROOT, "ops", "cli")
                if _ops not in _sys.path:
                    _sys.path.insert(0, _ops)
                import systemd as _sd, registry as _reg
                b = self._body()
                key, field, value = (b.get("service") or "").strip(), (b.get("key") or "").strip(), b.get("value")
                reg = _reg.load()
                if key not in reg["services"]:
                    raise ValueError(f"unknown service {key!r}")
                if field == "max_model_len":
                    # the context window → the SHARED helper (auto-util from _profile + budget-gated restart,
                    # one source with the co-residence shrink). "the registry knows the resource need" (Tim).
                    self._send(200, json.dumps({"key": field, "value": value, **_apply_model_ctx(key, int(value))}))
                else:                                      # any other serve-time field → set + restart if running
                    _reg.set_config(reg, key, field, value)
                    reg = _reg.load(); svc = reg["services"][key]
                    if _sd.is_active(svc) == "active":
                        started, msg = _sd.control(svc, "restart")
                        self._send(200, json.dumps({"service": key, "key": field, "value": value,
                                                    "restarted": started, "note": msg if started else "restart failed"}))
                    else:
                        self._send(200, json.dumps({"service": key, "key": field, "value": value, "restarted": False,
                                                    "note": "saved — applies when the service next starts"}))
            elif self.path == "/api/mode":                # the presence dial — set the RHM mode
                b = self._body()
                SUITE.set_mode(b["mode"])
                self._send(200, json.dumps(SUITE.now(DEMO)))
            elif self.path == "/api/activation/tick":     # Group H/I — manual/external drive of ONE activation tick.
                # The LIVE external-drive seam for the always-on caller (the autonomous loop is OFF by default,
                # needs-tim). Fires the DUE clock-driven drivers (background idle-gate + the held-cursor rollup +
                # the mode auto-detector→toggle) on the ONE module-level ActivationCaller (cursor held across
                # manual + loop ticks), and fires SENSE only if a real `sense_event` is supplied in the body
                # (a clock tick fabricates none). Floor-clean by construction: every effect routes through the
                # reused H/I drivers over the non-consequential DESTINATION_KINDS — no resolve/approve/dispatch.
                b = self._body()
                res = ACTIVATION_CALLER.activation_tick(sense_event=b.get("sense_event"),
                                                        mode=b.get("mode"))
                self._send(200, json.dumps(res.as_dict()))
            elif self.path == "/api/rhm-config":          # configure model/provider + persona
                b = self._body()
                self._send(200, json.dumps(SUITE.set_rhm_config(b)))
            elif self.path == "/api/coa":                 # decision-compiler UP — value-framing
                b = self._body()
                self._send(200, json.dumps(SUITE.coa(b["id"])))
            elif self.path == "/api/surface-output":      # F2: route a node's result to the inbox/COA
                b = self._body()
                gid = b.get("graph_id", DEMO)
                self._send(200, json.dumps(SUITE.surface_output(gid, b["node"])))
            elif self.path == "/api/surface-review":       # A: surface a review item into the one queue
                b = self._body()
                self._send(200, json.dumps(SUITE.surface_review(
                    b["item"], origin=b.get("origin", "responsive"))))
            elif self.path == "/api/capture-idea":         # A4: capture a fleeting idea (generative review item)
                b = self._body()
                self._send(200, json.dumps(SUITE.idea_capture(b["text"])))
            elif self.path == "/api/defer-offer":           # B3: defer a live RHM offer into the inbox as a
                # REAL queued, revivable item (§6B QUEUE mode). The operator face mints it; resolved=None, so
                # it stays a live escalation until they revive+approve or dismiss it. NOTHING dispatches here
                # (the offer's verb runs only on a later approve through /api/act — the B1/B2 consent invariant).
                # Fail loud on a missing proposal (no silent no-op).
                b = self._body()
                prop = b.get("proposal")
                if not isinstance(prop, dict):
                    raise ValueError("/api/defer-offer needs a 'proposal' object (fail loud)")
                self._send(200, json.dumps(SUITE.defer_offer(prop, note=b.get("note", ""))))
            elif self.path == "/api/revive-offer":          # B3: read a deferred offer back out to RE-OPEN the
                # live interactive conversation (the ProposeAffordance card with its options+steer+approve).
                b = self._body()
                self._send(200, json.dumps(SUITE.revive_offer(b["id"])))
            elif self.path == "/api/build-intent":          # T0-WIRE: the REAL production entry seam for the
                # decision→implementation wire. The operator (this is the OPERATOR face, not the agent
                # face) mints a build-intent — a declared-scope decision that, once they APPROVE it via
                # /api/resolve (operator-only), the WIRE-LOOP dispatches to `claude -p`. This route only
                # SURFACES the intent (resolved=None); it does NOT dispatch (dispatch is dispatch_decision,
                # off this face). So the wire's "off the agent face / operator-only approve" gates hold:
                # this is the missing FRONT DOOR (the closure + UI already existed but nothing in
                # production could populate the builds lane). Fail loud on a missing spec (no silent no-op).
                b = self._body()
                spec = b.get("spec")
                if not spec or not str(spec).strip():
                    raise ValueError("/api/build-intent needs a non-empty 'spec' (fail loud)")
                self._send(200, json.dumps(SUITE.surface_build_intent(
                    str(spec).strip(), scope=b.get("scope"),
                    consequence_class=b.get("consequence_class", "decision_build"),
                    why=b.get("why", ""))))
            elif self.path == "/api/intent-at":              # L1 (§21.4#2): a COMMENT-AT-AN-ADDRESS becomes a
                # build-intent that surfaces for approval AT that address. The addressed-feedback → wire
                # entry seam — mirrors /api/build-intent (OPERATOR face), but the scope is DERIVED from the
                # ui:// address via S3 (resolve_scope) instead of declared by the caller, and the comment is
                # RECORDED at the address via I6 (ingest_comment). It only SURFACES the intent (resolved=None);
                # approval stays on the EXISTING operator-only /api/resolve, and dispatch-on-approve is L2 (a
                # separate switch — this route NEVER dispatches). An orphan/stale address → EMPTY scope =
                # DENY-ALL (never fabricated). Fail loud on a missing address/text (S0 + I6 gates → 400).
                b = self._body()
                addr = b.get("address")
                if not addr or not str(addr).strip():
                    raise ValueError("/api/intent-at needs a non-empty 'address' (fail loud)")
                text = b.get("text") or b.get("comment")
                if not text or not str(text).strip():
                    raise ValueError("/api/intent-at needs a non-empty 'text' comment (fail loud)")
                self._send(200, json.dumps(SUITE.surface_intent_at(
                    str(addr).strip(), str(text).strip(), source=b.get("source", "operator"),
                    consequence_class=b.get("consequence_class", "decision_build"),
                    why=b.get("why", ""))))
            elif self.path == "/api/review/start":         # B: start a review session (NOT graph-scoped — makes its own)
                b = self._body()
                self._send(200, json.dumps(SUITE.start_session(
                    b["item_ids"], mode=b.get("mode", "walkthrough"))))
            elif self.path == "/api/walkthrough/start":     # C4: the mode-selection → ORGAN-start seam.
                # SELECTING the guided/walkthrough experience: this binds the cosmetic presence-dial
                # 'walkthrough' MODE to the real walkthrough ORGAN (start_walkthrough sets the dial AND
                # starts the organ over the pending items) — closing the naming trap (a dial mode that
                # only narrated vs. the screen-driving engine). Optional `item_ids` to pre-select a set;
                # absent → it walks every pending unresolved inbox item. FAIL LOUD (no silent no-op):
                # nothing pending → {organ_started:False, reason} (the dial is set, the surface is told).
                # The FE that CALLS this on dial-select + drives the per-step view is the FE show-me lane.
                b = self._body()
                self._send(200, json.dumps(SUITE.start_walkthrough(b.get("item_ids"))))
            elif self.path == "/api/guide/start":           # C1: the SYSTEM-INITIATED guided sequence ("show
                # me how" tour). start_guide composes the SAME walkthrough organ over ui:// ELEMENT addresses
                # (not inbox items): it sets the dial to 'walkthrough' AND starts a session whose steps each
                # narrate the element's corpus how-to (address_help) + spotlight the real element (G-43).
                # MODEL-FREE by construction (present_current's guide branch reads the corpus, never a model).
                # Optional `topic` to pick a sequence; absent → the default orientation tour. FAIL LOUD: no
                # registered addresses → {organ_started:False, reason} (the dial is set, the surface is told).
                b = self._body()
                self._send(200, json.dumps(SUITE.start_guide(b.get("topic"))))
            elif self.path == "/api/debrief/start":         # voice-trial lane F: walk Tim back through the
                # recorded trial sessions. start_debrief SURFACES each recorded session as a review item
                # (carrying its real CAS transcript) then drives the SAME walkthrough organ — so the
                # debrief is read/advanced via the EXISTING /api/review/{current,next,status} routes;
                # only this START is net-new. Verdicts are captured via /api/resolve (operator-only),
                # exactly like a review session. Fail loud on missing session_ids (no silent no-op).
                b = self._body()
                sids = b.get("session_ids")
                if not sids:
                    raise ValueError("/api/debrief/start needs a non-empty 'session_ids' list (fail loud)")
                self._send(200, json.dumps(SUITE.start_debrief(
                    sids, host_persona=b.get("host_persona"), mode=b.get("mode", "walkthrough"))))
            elif self.path == "/api/trial/turn":            # G4.6: record one spoken trial turn (durable event + CAS)
                b = self._body()
                self._send(200, json.dumps(SUITE.trial_record_turn(
                    b["session_id"], b.get("role", "operator"), b["text"], b.get("character"))))
            elif self.path == "/api/trial/feedback":        # G4.6: record Tim's spoken feedback during a trial
                b = self._body()
                self._send(200, json.dumps(SUITE.trial_record_feedback(
                    b["session_id"], b["text"], b.get("character"))))
            elif self.path == "/api/trial/reflection":      # G4.6: record the character's own reflection-note
                b = self._body()
                self._send(200, json.dumps(SUITE.trial_record_reflection(
                    b["session_id"], b["text"], b.get("character"))))
            elif self.path in ("/api/voice/load", "/api/voice/ear/load"):    # G4.7: load a voice service (ear OR engine; 'warming'; fail-loud if it won't fit)
                from voice import lifecycle as voice_lc
                b = self._body()
                self._send(200, json.dumps(voice_lc.load(b.get("service") or b["ear"])))
            elif self.path in ("/api/voice/unload", "/api/voice/ear/unload"):  # G4.7: unload a voice service → frees its VRAM
                from voice import lifecycle as voice_lc
                b = self._body()
                self._send(200, json.dumps(voice_lc.unload(b.get("service") or b["ear"])))
            elif self.path == "/api/voice/switch":  # Option A: pick a persona → set it AS active + auto-load its voice
                # "switch between them all" without manual VRAM juggling: set the active persona (brain
                # character + voice), then EVICT the previous voice engine and cold-load this persona's
                # engine (the card can't hold them all — accepted). Returns 'warming' → poll
                # /api/voice/services for 'up'. Fail loud on unknown persona, and (via the budget gate)
                # if the voice won't fit even after eviction (e.g. orpheus + a big brain).
                from voice import lifecycle as voice_lc, personas as voice_personas
                b = self._body()
                persona_id = (b.get("persona") or "").strip()
                if not persona_id:
                    raise ValueError("/api/voice/switch needs {persona} (fail loud)")
                p = voice_personas.get_persona(persona_id)        # fail loud on an unknown persona
                rc = SUITE.rhm_config()
                eng = (rc.get("tts_engine") or "").strip() or p["engine"]   # override wins, else persona's engine
                SUITE.set_rhm_config({"persona": persona_id})
                svc = voice_lc.engine_service_for(eng)
                # CO-RESIDENCE (Tim 2026-06-07, non-negotiable): the finished-thought judge + the brain run
                # alongside the voice — so the brain must stay RESIDENT with it, not be evicted. Size the
                # brain's context to what the registry records as co-resident-safe for THIS voice
                # (the voice service's config.coresident_brain_ctx — a STORED max, not auto-computed), and
                # shrink+restart the brain BEFORE loading the voice. A voice that records nothing leaves the
                # brain at its default context (light voices co-reside at full 64K already).
                import sys as _sys2
                _ops2 = os.path.join(ROOT, "ops", "cli")
                if _ops2 not in _sys2.path:
                    _sys2.path.insert(0, _ops2)
                import registry as _reg2
                _r = _reg2.load()
                co_ctx = ((_r["services"].get(svc) or {}).get("config") or {}).get("coresident_brain_ctx") if svc else None
                brain_recfg = None
                if co_ctx:
                    bkey = _local_brain_key(_r, rc)
                    if bkey and int((_r["services"][bkey].get("config") or {}).get("max_model_len", 0)) != int(co_ctx):
                        brain_recfg = _apply_model_ctx(bkey, int(co_ctx))      # shrink+restart the brain FIRST
                if not svc:                                       # always-on engine (kokoro) — nothing to load
                    out = {"persona": persona_id, "engine": eng, "service": None, "state": "up",
                           "note": "always-on engine — no load step"}
                else:
                    out = {"persona": persona_id, "engine": eng, "service": svc, **voice_lc.switch_to(svc)}
                if brain_recfg is not None:
                    out["brain_coresident_ctx"] = co_ctx
                    out["brain_reconfig"] = brain_recfg
                self._send(200, json.dumps(out))
            elif self.path == "/api/voice/finished-thought":  # G1.3: the semantic endpoint judge (brain-side)
                b = self._body()
                self._send(200, json.dumps(SUITE.is_finished_thought(b.get("text", ""))))
            elif self.path == "/api/voice/log":            # client-side voice trace (Tim 2026-06-07): the
                # browser reports its half of the live loop (VAD pause, recording start/stop, judge-call,
                # turn-fire, chunk playback ok/fail, errors) into the ONE event log so the WHOLE process is
                # investigable. {event, turn_id?, ms?, ...} → op=voice.client. Lenient (never breaks a turn).
                b = self._body()
                ev = (b.pop("event", "") or "").strip()
                if ev:
                    SUITE.voice_log(ev, **{k: v for k, v in b.items() if k != "event"})
                self._send(200, json.dumps({"logged": bool(ev)}))
            elif self.path == "/api/review/next":          # B: Next — open the gate, fire the step, advance
                b = self._body()
                self._send(200, json.dumps(SUITE.next(b["session"])))
            elif self.path == "/api/journey/start":         # L9: open a journey-record (the REVERSE capture).
                # DISTINCT from /api/review/start (the review-session organ): a journey records NAVIGATION
                # (an ordered ui:// click-path), a session records a REVIEW (item-ids with a cursor). No body.
                self._send(200, json.dumps(SUITE.start_journey()))
            elif self.path == "/api/journey/step":          # L9: append one addressed step to an OPEN journey.
                # The address is S0-validated in the Suite (parse_ui_address raises → 400 here, fail loud,
                # mirrors /api/annotate). Appending to a finalized/absent journey raises → 400 (no silent no-op).
                b = self._body()
                self._send(200, json.dumps(SUITE.append_journey_step(b["journey"], b["address"])))
            elif self.path == "/api/journey/stop":          # L9: finalize a journey → it becomes replayable.
                b = self._body()
                self._send(200, json.dumps(SUITE.stop_journey(b["journey"])))
            elif self.path == "/api/react":               # watch-and-react ambient comment
                self._send(200, json.dumps(SUITE.react(DEMO)))
            elif self.path == "/api/revert":              # OPERATOR-only rollback of a self-change
                b = self._body()
                self._send(200, json.dumps(SUITE.revert_self_change(b["sha"])))
            elif self.path == "/api/checkpoint":          # OPERATOR-only: mint a reversible restore point
                # The operator stamps a `[checkpoint]` of NAMED paths (path-scoped — rule 10, parallel
                # sessions on main) — the third reversible stream beside [self-apply]/[self-build]. It
                # shows in the SAME audit ledger (GET /api/self-change-log) and undoes via the SAME
                # /api/revert. Operator face only (beside /api/revert), off the MCP/agent face. Fail-loud
                # guards (empty/escaping path-set, empty delta) surface through _send's except.
                b = self._body()
                self._send(200, json.dumps(SUITE.checkpoint(b["paths"], b.get("label", ""))))
            # --- build-dispatch (self-growth), operable from the operator's UI ---
            elif self.path == "/api/propose":          # agent/operator dispatches a build
                b = self._body()
                self._send(200, json.dumps(SUITE.propose_node(b["name"], b["spec"])))
            # === AUTHORING BACKEND (Concurrent Cognition C7.4/C7.5) — OPERATOR face ===
            # The write/validate/test endpoints the authoring FE lives on. Mirror the node propose/apply
            # endpoints exactly (propose-not-apply): propose/edit/delete SURFACE for approval; apply is the
            # EXISTING operator-only /api/apply (routes by action class to apply_role/apply_role_delete);
            # approval is /api/resolve (operator-only). validate/dry_run/preview are pure/read-only.
            elif self.path == "/api/cognition/role/propose":   # author a NEW role → surfaces for approval
                b = self._body()
                self._send(200, json.dumps(SUITE.propose_role(b.get("spec") or b, model=b.get("model"))))
            elif self.path == "/api/cognition/role/edit":      # re-propose an existing role → surfaces
                b = self._body()
                self._send(200, json.dumps(SUITE.edit_role(b["role_id"], b.get("spec") or {},
                                                            model=b.get("model"))))
            elif self.path == "/api/cognition/role/delete":    # request removal → surfaces for approval
                b = self._body()
                self._send(200, json.dumps(SUITE.delete_role(b["role_id"])))
            elif self.path == "/api/cognition/role/dry_run":   # TEST a role (or a draft field-set) in isolation
                b = self._body()
                self._send(200, json.dumps(SUITE.dry_run_role(
                    b.get("role_id") or b.get("fields"), b["utterance"],
                    model=b.get("model"), base_url=b.get("base_url"))))
            elif self.path == "/api/cognition/rule/validate":  # live AST validation for the rule-builder
                b = self._body()
                self._send(200, json.dumps(SUITE.validate_rule(b["ast"], destination=b.get("destination"))))
            elif self.path == "/api/cognition/rule/dry_run":   # routing decision over sample resolved values
                b = self._body()
                self._send(200, json.dumps(SUITE.dry_run_rule(
                    b["ast"], b.get("sample_resolved") or {}, destination=b.get("destination", "inject"),
                    params=b.get("params"), on_missing=b.get("on_missing", "raise"))))
            elif self.path == "/api/cognition/rule/attach":    # attach a rule onto a role → surfaces (edit)
                b = self._body()
                self._send(200, json.dumps(SUITE.attach_rule(b["role_id"], b["rule"])))
            elif self.path == "/api/cognition/rule/detach":    # detach a rule from a role → surfaces (edit)
                b = self._body()
                self._send(200, json.dumps(SUITE.detach_rule(b["role_id"], b["rule_id"])))
            elif self.path == "/api/cognition/preview_turn":   # PREVIEW a full staged turn (read-only)
                b = self._body()
                self._send(200, json.dumps(SUITE.preview_turn(
                    b["utterance"], b.get("mode"), graph_id=b.get("graph_id"))))
            # --- LANE-BRIDGE: the cognition-engine HUMAN-face RUNS + DIRECT creates (G2). The engine
            #     functions (run_role/run_items/run_reduce/embed) are COMPUTATION — they produce run://
            #     outputs + op.run telemetry, NEVER a resolve/approve/dispatch (the floor; reuse the SAME
            #     `_cog` engine the swarm + MCP face use, via the cog_* glue above). The DIRECT creates
            #     (#58: declarative-direct, no approval) reuse the SAME Suite.create_* methods the MCP
            #     create tools call; node-type/arbitrary-code create stays GATED (operator-only, off this
            #     run-route — propose_* + /api/apply). ---
            elif self.path == "/api/cognition/run_role":   # fire ONE role (op rides the role) → run:// output
                b = self._body()
                self._send(200, json.dumps(cog_run_role(
                    b["role"], utterance=b.get("utterance", ""),
                    model=b.get("model", ""), inputs=b.get("inputs"),
                    max_tokens=int(b.get("max_tokens", 256)), temperature=float(b.get("temperature", 0.0)),
                    ensure=bool(b.get("ensure", False)), ensure_evict=bool(b.get("ensure_evict", False)))))
            elif self.path == "/api/cognition/run_items":  # the MAP: fan ONE role over N units (per-unit run://)
                b = self._body()
                self._send(200, json.dumps(cog_run_items(
                    b["role"], b["items"], max_tokens=int(b.get("max_tokens", 256)),
                    temperature=float(b.get("temperature", 0.0)))))
            elif self.path == "/api/cognition/run_reduce": # the JOIN: reduce N run:// addresses → one output
                b = self._body()
                self._send(200, json.dumps(cog_run_reduce(
                    b["addresses"], b["mode"], role=b.get("role", ""),
                    reduce_rule=b.get("reduce_rule", ""),
                    cluster_threshold=float(b.get("cluster_threshold", 0.85)),
                    max_tokens=int(b.get("max_tokens", 512)))))
            elif self.path == "/api/cognition/embed":      # EMBED: fire an embed-op role → {vector,dim,model}
                # The embed op via the SAME run_role engine path — exactly how the MCP face exposes embed
                # (there is no standalone Suite.embed; embed IS run_role over an op='embed' role, e.g. the
                # registered 'embed' role; the engine dispatches on role.op). `role` defaults to 'embed'.
                # A down local embedder FAILS LOUD unless ensure=True requests the gated #50 load.
                b = self._body()
                self._send(200, json.dumps(cog_run_role(
                    b.get("role", "embed"), utterance=b.get("utterance", b.get("text", "")),
                    model=b.get("model", ""), inputs=b.get("inputs"),
                    ensure=bool(b.get("ensure", False)), ensure_evict=bool(b.get("ensure_evict", False)))))
            elif self.path == "/api/cognition/corpus":     # GROUP D1: CAPTURE — persist + EMBED-on-write
                # The WRITE half of /api/cognition/corpus (the GET is the list/read). CAPTURE-EMBED
                # ONE-SOURCE: delegates to Suite.capture_corpus — the SHARED capture+embed-on-write seam the
                # MCP `capture` tool ALSO calls (one source, NOT a duplicated bridge embed path). This closes
                # the SUITE-3 silent no-op: the route USED to call ONLY write_corpus_record and never embed,
                # so an FE/bridge capture wrote a record but NEVER populated the space → find_relations
                # silently returned nothing over it (brushed the no-silent-failure law). Now BOTH faces
                # populate identically. The LINEAGE GATE still bites (session/round/project REQUIRED — a
                # record without lineage raises CorpusError → 400, fail loud); a projection naming a
                # NON-embeddable space RAISES (→ 400) rather than silently capturing-only (the WHOLE POINT).
                # Back-compat: accepts the SINGLE-record body shape {source_address, output, kind?, lineage,
                # projection?, model?, **extra} (lineage carries session/round/project) OR a {records:[…],
                # project, session, round} batch shape. Returns {captured, embedded, n_records}; the
                # single-record top-level address/cas are surfaced for callers that read the old shape.
                b = self._body()
                if "records" in b:                          # batch shape (project/session/round at top level)
                    out = SUITE.capture_corpus(
                        list(b["records"]), project=b["project"], session=b["session"],
                        round=b.get("round", "1"))
                else:                                        # single-record shape (lineage holds the axes)
                    lin = b["lineage"]
                    rec = {"source_address": b["source_address"], "output": b["output"],
                           "kind": b.get("kind", "capture"), "projection": b.get("projection"),
                           "model": b.get("model"),
                           **{k: v for k, v in b.items() if k not in (
                               "source_address", "output", "kind", "lineage", "model", "projection")}}
                    out = SUITE.capture_corpus(
                        [rec], project=lin["project"], session=lin["session"], round=lin.get("round", "1"))
                resp = dict(out)
                if out["captured"]:                          # surface the first record's address/cas at top
                    resp["address"] = out["captured"][0]["address"]   # level (back-compat with the old shape)
                    resp["cas"] = out["captured"][0]["cas"]
                    resp["seq"] = out["captured"][0].get("seq")
                self._send(200, json.dumps(resp))
            elif self.path == "/api/cognition/create_role":    # DIRECT create (#58 — declarative, no approval)
                # Reuses Suite.create_role (the SAME render+gate+write+commit+rediscover path the MCP
                # create_role tool calls). The CORRECTNESS gate bites (a malformed spec is refused fail-loud,
                # never written). The build-dispatch floor is UNTOUCHED — this writes a roles/ file, it never
                # launches claude -p. (Surfacing stays available via /api/cognition/role/propose.)
                b = self._body()
                spec = b.get("spec") or b
                self._send(200, json.dumps(SUITE.create_role(spec, model=spec.get("model"))))
            elif self.path == "/api/cognition/create_skill":   # DIRECT create (#56 write-half / #58 direct)
                b = self._body()
                self._send(200, json.dumps(SUITE.create_skill(b.get("spec") or b)))
            elif self.path == "/api/cognition/create_context": # DIRECT create (#56 write-half / #58 direct)
                b = self._body()
                self._send(200, json.dumps(SUITE.create_context(b.get("spec") or b)))
            elif self.path == "/api/act":               # I2: the click-emission seam — a DETERMINISTIC
                # human click ships a STRUCTURED {verb, address, args} that drives _dispatch_rhm_action
                # DIRECTLY (bypassing the unreliable model-prose parse) — the emission RELOCATION
                # (§21.4#1). OPERATOR face only (beside /api/resolve, NOT the MCP/agent face): a human
                # click is an operator act, where the no-self-approve gates already live (seams-rhm
                # headline). The 7-verb whitelist + no-self-apply ride along INSIDE the dispatcher; the
                # verb-class governance posture + the "did X" confirmation are re-folded by Suite.act.
                # Fail loud on a missing verb (no silent no-op).
                b = self._body()
                gid = b.get("graph_id", DEMO)
                verb = b.get("verb")
                if not verb or not str(verb).strip():
                    raise ValueError("/api/act needs a non-empty 'verb' (fail loud)")
                self._send(200, json.dumps(SUITE.act(
                    str(verb).strip(), gid, address=b.get("address"), args=b.get("args"))))
            elif self.path == "/api/annotate":          # I6: attach a comment/annotation to a ui:// ADDRESS
                # NET-NEW and SEPARATE from /api/resolve's comment choice (which annotates a surfaced
                # item by id, suite.py:3045) and from /api/act (I2): nothing else attaches BY ADDRESS.
                # OPERATOR face (beside the others). Suite.annotate validates the address against the S0
                # grammar (raises → 400 here) and persists keyed by address; retrieve via GET
                # /api/annotations?address=…. Feeds R2 (address-keyed context resolution). Fail loud on a
                # missing address (no silent no-op — AGENTS.md rule 4).
                b = self._body()
                addr = b.get("address")
                if not addr or not str(addr).strip():
                    raise ValueError("/api/annotate needs a non-empty 'address' (fail loud)")
                # L4: route through `ingest_comment` (NOT the pure `annotate` leaf) — a clicked comment
                # IS the twin's LOCATED gold label: it records the I6 annotation AND emits one additive
                # located-gold chat turn (operator=gold, address-stamped) that rides the existing
                # `append_chat → training_signal` pipe. This is the WIRED production entry the FE's
                # annotate-click hits; the same entry the I5 router composes (single-source). Returns the
                # annotation rec (unchanged response shape — retrieve the comment via GET /api/annotations).
                self._send(200, json.dumps(SUITE.ingest_comment(
                    str(addr).strip(), b.get("text", ""), source=b.get("source", "operator"))))
            elif self.path == "/api/presentation-pref":  # F1 LEARNING LOOP: record "how Tim wants <this>
                # presented" at a ui:// ADDRESS — the CAPTURE seam. It IS the annotate-branch of the
                # addressed-feedback channel (a comment at an address WITH a presentation intent), so it
                # rides the SAME annotations.jsonl store leaf, but with a STRUCTURED pref so the adapt step
                # (up_translate/coa/address_help consult it) is MODEL-FREE. OPERATOR face. The VOICE/TYPING
                # input that PRODUCES "show me this differently" rides the existing chat path (/api/chat);
                # this is the recorder a parsed presentation intent calls. Suite.set_presentation_pref
                # S0-validates the address (raises → 400) AND validates the pref kind/arg (raises → 400 on a
                # malformed pref — fail loud, no silent ignore). Persists keyed by address; consulted via
                # the up-translate organs; survives reload (the leaf reads disk every call). Fail loud on a
                # missing address or pref (no silent no-op — AGENTS.md rule 4).
                b = self._body()
                addr = b.get("address")
                pref = b.get("pref")
                if not addr or not str(addr).strip():
                    raise ValueError("/api/presentation-pref needs a non-empty 'address' (fail loud)")
                if not isinstance(pref, dict):
                    raise ValueError("/api/presentation-pref needs a structured 'pref' object "
                                     "{kind, arg?} (fail loud — no silent ignore)")
                self._send(200, json.dumps(SUITE.set_presentation_pref(
                    str(addr).strip(), pref, text=b.get("text"), source=b.get("source", "operator"))))
            elif self.path == "/api/pin":                # X7: pin/unpin an attached item at a ui:// ADDRESS
                # OPERATOR face (beside /api/annotate, /api/attach-chat) — the SET path for the dead pin
                # term: `pinned` is read in `_r2_score` but nothing set it. This records a pin/unpin of the
                # attached item at (address, target_ts) so the gather's existing read picks up the real flag
                # → a pinned item holds in the bounded R2 window. OPERATOR-ONLY, OFF the MCP face (not in
                # RHM_VERBS — no-bypass preserved). Suite.pin S0-validates the address (raises → 400) AND
                # fails loud if (address, target_ts) names no real attached item. Default pinned=True.
                b = self._body()
                addr = b.get("address")
                target_ts = b.get("target_ts")
                if not addr or not str(addr).strip():
                    raise ValueError("/api/pin needs a non-empty 'address' (fail loud)")
                if not target_ts or not str(target_ts).strip():
                    raise ValueError("/api/pin needs a non-empty 'target_ts' (the item's handle) (fail loud)")
                self._send(200, json.dumps(SUITE.pin(
                    str(addr).strip(), str(target_ts).strip(), pinned=bool(b.get("pinned", True)))))
            elif self.path == "/api/attach-chat":        # I7: attach a chat turn to a ui:// ADDRESS (the
                # dropped 4th attach-type, §21.1's chat:// branch). RIDES the open append_chat record with
                # one additive `address` field — NO separate chat store (one-source). DISTINCT from
                # /api/chat (the RHM conversation): this attaches a turn AT an address, retrieve via GET
                # /api/chats?address=…. Suite.attach_chat validates the address against the S0 grammar
                # (raises → 400 here) + tags source/grade (echo-guard) + flows through training_signal
                # unchanged. Feeds R2 (address-keyed context resolution). Fail loud on a missing address.
                b = self._body()
                addr = b.get("address")
                if not addr or not str(addr).strip():
                    raise ValueError("/api/attach-chat needs a non-empty 'address' (fail loud)")
                self._send(200, json.dumps(SUITE.attach_chat(
                    str(addr).strip(), b.get("text", ""),
                    role=b.get("role", "user"), source=b.get("source"))))
            elif self.path == "/api/approve-reach":      # X16: the operator authorizes HOW FAR a build's
                # edit propagates — the reach-approval. OPERATOR face (beside /api/resolve, /api/pin — NOT
                # the MCP/agent face). DEFAULT is the pointed address only (the build's declared scope is
                # unchanged); this widens it to include the files the APPROVED blast-radius members live in.
                # approve_reach validates each member against the PERSISTED blast_radius the operator saw
                # (consent-time) — a member NOT in that radius RAISES (→ 400), so this is never a
                # scope-injection path that defeats empty-scope=DENY-ALL. Operator-only, off the MCP face
                # (not in RHM_VERBS — no-bypass + the 7-verb whitelist + no-self-apply preserved). Fail loud
                # on a missing id / members (no silent no-op — AGENTS.md rule 4).
                b = self._body()
                if not b.get("id") or not str(b["id"]).strip():
                    raise ValueError("/api/approve-reach needs a non-empty 'id' (the build-intent) (fail loud)")
                members = b.get("members")
                if not members or not isinstance(members, list):
                    raise ValueError("/api/approve-reach needs a non-empty 'members' list (the approved "
                                     "blast-radius members) (fail loud)")
                self._send(200, json.dumps(SUITE.approve_reach(
                    str(b["id"]).strip(), [str(m) for m in members], reason=b.get("reason", ""))))
            elif self.path == "/api/resolve":           # OPERATOR approves/rejects/comments/skips (UI channel)
                b = self._body()
                # D: additive session tagging + the comment/skip/decide vocabulary; existing callers
                # (id+choice+reason) are unchanged. Operator-only — never on the MCP face (no-bypass).
                v = SUITE.resolve_surfaced(b["id"], b["choice"], b.get("reason", ""),
                                           session_id=b.get("session"), position=b.get("position"))
                self._send(200, json.dumps({"ok": True, "verdict": v, "surfaced": SUITE.list_surfaced()}))
            elif self.path == "/api/registry/approve":   # RG9: the OPERATOR's batch approve (UI channel —
                # operator-consent by construction, like /api/resolve; never on the MCP face). The kept
                # pending dossiers are written via the existing all-or-nothing registry_writeback.
                b = self._body()
                self._send(200, json.dumps(SUITE.registry_apply_batch(skip=b.get("skip") or [])))
            elif self.path == "/api/decision":           # a decision as a view over the log (audit)
                b = self._body()
                self._send(200, json.dumps(SUITE.decision_view(b["id"])))
            elif self.path == "/api/apply":             # apply (only succeeds if operator approved)
                b = self._body()
                r = SUITE.apply_surfaced(b["id"])       # dispatches by class; build-gate may reject
                self._send(200, json.dumps({"ok": not r.get("rejected"), "path": r.get("applied"),
                                            "kind": r["kind"], "error": r.get("error"),
                                            "types": sorted(SUITE.list_types())}))
            elif self.path == "/api/mockup-feedback":   # MOCKUP STUDIO: capture one feedback note (durable)
                # body {mockup,element,text,ts} → appends ONE JSONL line to .feedback/<mockup>.jsonl and
                # returns {ok:true, entry:{id,mockup,element,text,ts,status:"pending"}}. The id is a
                # file-scoped sequence (len of the existing thread + 1, zero-padded) PLUS a uuid4 stub so
                # it's unique even across an out-of-band edit — no Date.now/random in app code, but the
                # bridge is infra (a uuid here is fine). Fail loud: a non-string/empty `text` → 400; a
                # junk `mockup` name → 400 (the path gate); a write failure → propagates → 400/500 (never
                # a silent success). status starts "pending" (the lead's edit-loop flips it).
                import uuid as _uuid
                b = self._body()
                mockup = b.get("mockup")
                text = b.get("text")
                if not isinstance(mockup, str) or not mockup.strip():
                    raise ValueError("/api/mockup-feedback needs a 'mockup' filename (fail loud)")
                if not isinstance(text, str) or not text.strip():
                    raise ValueError("/api/mockup-feedback needs non-empty 'text' (fail loud)")
                path = _feedback_path(mockup)            # validates the name (→ 400 on junk) + path-safe
                element = b.get("element")
                if element is not None and not isinstance(element, str):
                    raise ValueError("/api/mockup-feedback 'element' must be a string or null (fail loud)")
                ts = b.get("ts")
                if not isinstance(ts, str) or not ts.strip():
                    ts = SUITE.now_iso() if hasattr(SUITE, "now_iso") else time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                seq = len(_read_feedback(mockup)) + 1    # file-scoped sequence (human-legible ordering)
                entry = {"id": f"{seq:04d}-{_uuid.uuid4().hex[:8]}", "mockup": mockup,
                         "element": (element.strip() if isinstance(element, str) and element.strip() else None),
                         "text": text, "ts": ts, "status": "pending"}
                os.makedirs(FEEDBACK_DIR, exist_ok=True)
                with open(path, "a", encoding="utf-8") as f:   # append ONE line — write failure raises → fail loud
                    f.write(json.dumps(entry) + "\n")
                self._send(200, json.dumps({"ok": True, "entry": entry}))
            elif self.path == "/api/mockup-feedback/status":  # MOCKUP STUDIO: the lead's edit-loop flips an entry
                # body {mockup,id,status} → rewrites the JSONL flipping that entry's status. status ∈
                # pending|applied|dismissed (anything else → 400). A missing mockup/id/unknown id → 400
                # (fail loud, no silent no-op). The rewrite is whole-file (the thread is small); a failure
                # propagates. This is how the lead marks a note done after editing the mockup.
                b = self._body()
                mockup = b.get("mockup"); fid = b.get("id"); status = b.get("status")
                if not isinstance(mockup, str) or not mockup.strip():
                    raise ValueError("/api/mockup-feedback/status needs a 'mockup' filename (fail loud)")
                if not isinstance(fid, str) or not fid.strip():
                    raise ValueError("/api/mockup-feedback/status needs an entry 'id' (fail loud)")
                if status not in ("pending", "applied", "dismissed"):
                    raise ValueError("/api/mockup-feedback/status 'status' must be pending|applied|dismissed (fail loud)")
                path = _feedback_path(mockup)            # validates the name
                entries = _read_feedback(mockup)
                hit = next((e for e in entries if e.get("id") == fid), None)
                if hit is None:
                    raise ValueError(f"no feedback entry {fid!r} for mockup {mockup!r} (fail loud — no silent no-op)")
                hit["status"] = status
                with open(path, "w", encoding="utf-8") as f:   # whole-file rewrite (thread is small)
                    for e in entries:
                        f.write(json.dumps(e) + "\n")
                self._send(200, json.dumps({"ok": True, "entry": hit}))
            elif self.path == "/api/mockup-generate":   # MOCKUP STUDIO: the GENERATE FOLLOW-ON.
                # body {mockup, mode?} → calls the COMMITTED generate_for_mockup ENGINE (own-test green) to
                # refine ONE reviewed mockup from its captured feedback. mode defaults to 'plan' (SAFE/read-
                # only: the engine's claude -p run changes NOTHING, commits NOTHING — changed_files == []).
                # We import the module FUNCTION and call it directly — NOT through suite.py/surface_intent_at:
                # the engine calls implement.launch itself (the scope-enforced dispatch wire). We return the
                # PROPOSED result (the RHM showing what it WOULD change). Fail loud (no silent no-op): a
                # missing/junk mockup, no actionable feedback, or any engine raise propagates → the outer
                # try/except turns it into a 400 {error} — never a fabricated success.
                b = self._body()
                mockup = b.get("mockup")
                if not isinstance(mockup, str) or not mockup.strip():
                    raise ValueError("/api/mockup-generate needs a 'mockup' filename (fail loud)")
                mode = b.get("mode")
                if mode is not None and mode not in ("plan", "apply"):
                    raise ValueError("/api/mockup-generate 'mode' must be 'plan' or 'apply' (fail loud)")
                result = generate_mockup.generate_for_mockup(mockup.strip(), mode=mode)
                self._send(200, json.dumps(result))
            else:
                self._send(404, "{}")
        except Exception as e:                          # fail loud to the UI
            self._send(400, json.dumps({"error": f"{type(e).__name__}: {e}"}))

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    seed_demo()
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8770
    print(f"[bridge] UI face over the shared Suite at http://localhost:{port}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
