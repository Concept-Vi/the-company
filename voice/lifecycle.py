"""voice/lifecycle.py — load / unload / status for ALL loadable VOICE SERVICES (G4.7 + boot-on-demand).

The UI-driven, voice-scoped slice of the VRAM resource-manager — generalised past the STT ears to the
TTS engines too (Tim: "if voice is down you can boot it up, to make it all live"). A loadable voice
service = any `group:"voice"` entry in ops/services.json carrying a `load` block (the 3 GPU ears +
the 5 trial TTS engines). whisper.cpp (CPU) + Kokoro + assemblyai have no `load` block → nothing to load.

ONE SOURCE OF TRUTH — TWO senses, both now honoured:
  • The SERVICE registry: ops/services.json (the `company` console already owns it). We keep no second
    port/venv/vram map here — `_loadable()` reads it. Adding a loadable voice service = adding its
    services.json entry; no edit here.
  • The VRAM authority: ops/cli/gpu.py (the shared resource-manager CORE). voice IMPORTS it now instead
    of keeping a second budget/teardown — closing the dual-authority disconnect (see CONVERGENCE below).

CONVERGENCE (2026-06-06, the keeper pass that follows the company-CLI VRAM manager):
  Before this, load() launched the service via subprocess.Popen and unload() killed it by pgrep+killpg —
  a SECOND launch/teardown/budget mechanism, parallel to the `company` console (which drives the SAME
  services via their systemd user-units). The disconnect was REAL and active: a UI-launched (Popen)
  voice service left its systemd unit `inactive`, so `company`/gpu.py — which reads is-active for unit
  services — saw it as DOWN, did NOT count its VRAM in the budget, and could green-light a second load
  on top of it → OOM. Two authorities, one card, no shared truth.
  The fix: lifecycle now drives the SAME systemd units the console does (systemctl --user start) and
  budgets/tears-down through the shared core (gpu.check_fit / gpu.teardown). So:
    - a UI load is is-active=active → `company` SEES it, counts its VRAM, and won't over-commit;
    - the budget gate counts EVERY GPU service (brain + models + voice), not just resident voices;
    - teardown is the cgroup stop (systemctl stop) — which reaps vLLM's EngineCore (orpheus) that a
      plain SIGTERM/SIGKILL on the launcher does NOT (no OS death-link; upstream #19849). The unit IS
      the orphan-safe path; lifecycle no longer needs its own pgrep teardown.
  Env-parity holds for free: every voice unit carries `EnvironmentFile=voice.env`, and NO voice service
  declares a per-service `load.env` override (verified) — so the unit launch loses zero config the old
  Popen+voice.env path carried. The systemd path is also the one already PROVEN reliable (the 5-voice
  sweep ran through `company up`, i.e. the units), so converging onto it inherits that reliability.

Stdlib-only → runs IN the bridge interpreter (.venv); the service runs as a systemd-managed subprocess
in its own venv (NeMo / transformers / vLLM never touch the bridge interpreter). Teardown is by the
unit's cgroup, so unload works across a bridge restart (no in-memory pid table to lose).
"""
from __future__ import annotations
import json
import os
import sys
import time
import urllib.error
import urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVICES_JSON = os.path.join(REPO, "ops", "services.json")

# --- the SHARED VRAM resource-manager core (ops/cli) — the single budget/teardown authority ----------
# gpu.py + its siblings (registry/systemd/telemetry) use bare imports and are stdlib-only, so we put
# ops/cli on the path and import them by name. SAFE in the bridge context: `runtime.registry`
# (NodeRegistry) is a NAMESPACED submodule, so the bare `registry` here resolves to ops/cli/registry.py,
# not runtime's (verified 2026-06-06). Imported once at module load; fail loud if the core is missing
# (no silent fallback to a private second authority — that's the very thing this convergence removes).
_OPS_CLI = os.path.join(REPO, "ops", "cli")
if _OPS_CLI not in sys.path:
    sys.path.insert(0, _OPS_CLI)
import gpu as _gpu            # noqa: E402  read_gpu / budget_of / check_fit / plan_eviction / teardown / format_state
import systemd as _sd         # noqa: E402  is_active / port_open / control (systemctl --user)
import registry as _reg       # noqa: E402  load() / vram_of / ceiling_mb  (ops/cli/registry.py, NOT runtime's)


def _loadable() -> dict:
    """id → its `load` block (+ health path + the full svc spec), for every group:voice service in
    services.json that declares a `load` block. The SINGLE source — no hardcoded map (registry-is-truth).
    Carries the whole `svc` (incl. its `manage` unit) so the shared core can budget/control/teardown it."""
    with open(SERVICES_JSON, encoding="utf-8") as f:
        services = json.load(f).get("services", {})
    out = {}
    for sid, spec in services.items():
        if spec.get("group") == "voice" and isinstance(spec.get("load"), dict):
            out[sid] = {**spec["load"], "health": spec.get("health", "/"),
                        "title": spec.get("title", sid), "svc": spec}
    return out


def _url(load: dict) -> str:
    return f"http://127.0.0.1:{load['port']}"


def vram() -> dict:
    """Card memory in MB via the shared core (gpu.read_gpu → nvidia-smi). FAIL LOUD if it is unreadable —
    we do NOT 'assume it fits' and risk an OOM (no-silent-failure). Keeps the {used_mb,free_mb,total_mb}
    shape lifecycle's callers (status, poll_wake) expect; adds util_pct from the shared read."""
    g = _gpu.read_gpu()
    if g is None:
        raise RuntimeError("nvidia-smi unreadable via the shared resource-manager core (gpu.read_gpu) — "
                           "cannot VRAM-budget a load (fail loud)")
    return {"used_mb": g["used"], "free_mb": g["free"], "total_mb": g["total"], "util_pct": g["util"]}


def is_up(load: dict) -> bool:
    """Liveness probe (GET the service's health path → answers). Never raises — down/unreachable = False.
    Ears answer GET / ; engines answer GET /voices (the per-service `health` from services.json). This is
    the WARMING→UP discriminator: a systemd unit is is-active the instant ExecStart launches, but the
    model is still loading (orpheus ~42s) until the health endpoint answers — only then is it truly 'up'."""
    try:
        with urllib.request.urlopen(_url(load) + load.get("health", "/"), timeout=3) as r:
            return 200 <= r.status < 500
    except urllib.error.HTTPError as he:
        return he.code < 500
    except Exception:
        return False


def status() -> dict:
    """Per loadable voice service: up (health answers) / warming (unit active, model still loading) /
    down — plus the card VRAM. The unit's is-active is the AUTHORITATIVE 'has it started' signal (so this
    matches what `company` sees — one authority); the health probe refines active→up vs active→warming.
    Fail-SOFT on the VRAM read here (the picker still renders if nvidia-smi hiccups); load() is the
    fail-LOUD budget gate."""
    try:
        v = vram()
    except RuntimeError as e:
        v = {"error": str(e)}
    services = {}
    for sid, load_spec in _loadable().items():
        svc = load_spec["svc"]
        if is_up(load_spec):
            state = "up"
        elif _sd.is_active(svc) == "active":
            state = "warming"
        else:
            state = "down"
        services[sid] = {"id": sid, "title": load_spec["title"], "kind": load_spec.get("kind"),
                         "port": load_spec["port"], "state": state, "vram_mb_est": load_spec.get("vram_mb")}
    return {"vram": v, "services": services}


def load(service_id: str) -> dict:
    """Bring a voice service resident: START ITS SYSTEMD UNIT (the same one `company` drives), so the
    console SEES it and budgets against it. The model loads at warm()/first use; returns IMMEDIATELY
    'warming' (poll status() for 'up'). FAIL LOUD on: unknown/non-loadable id, missing venv, a unit that
    won't start, OR a load that won't fit the card — the budget gate now counts EVERY GPU service (brain +
    models + voice) via the shared core, names free-vs-need + what's holding the card + what to unload.
    Idempotent: an already-up service returns 'up' without a relaunch."""
    loadables = _loadable()
    if service_id not in loadables:
        raise ValueError(f"unknown or non-loadable voice service {service_id!r} — loadable: "
                         f"{sorted(loadables)} (whisper.cpp/Kokoro/cloud have no load step)")
    load_spec = loadables[service_id]
    if is_up(load_spec):
        return {"service": service_id, "state": "up", "note": "already resident"}
    svc = load_spec["svc"]
    manage = svc.get("manage", {})
    if manage.get("type") not in ("user-unit", "system-unit"):
        raise RuntimeError(f"voice service {service_id!r} has no systemd unit (manage.type="
                           f"{manage.get('type')!r}) — the convergence requires a unit to launch through "
                           f"so the console can see+budget it. Add one in voice/ops/systemd/ + services.json.")
    py = os.path.expanduser(f"~/.voice-venvs/{load_spec['venv']}/bin/python")
    if not os.path.exists(py):
        raise RuntimeError(f"voice service {service_id!r} venv missing at {py} — install it "
                           f"(voice/ears/REQUIREMENTS.md or voice/engines/REQUIREMENTS.md)")
    # --- the SHARED budget gate: counts ALL running GPU services, not just resident voices (the fix) ---
    reg = _reg.load()
    if service_id not in reg["services"]:
        raise RuntimeError(f"{service_id!r} not in the service registry — registry-is-truth out of sync")
    ok, need, free, _measured = _gpu.check_fit(reg, [service_id])
    if not ok:
        evict, projected = _gpu.plan_eviction(reg, [service_id], need, free)
        raise RuntimeError(
            f"cannot load {service_id!r}: needs ~{need} MB, only {free} MB free on the card. "
            + (f"Unload to make room — e.g. {', '.join(evict)} (→ ~{projected} MB free). " if evict
               else "Nothing evictable would free enough. ")
            + "Refusing to OOM (fail loud).\n" + _gpu.format_state(reg))
    # --- start the unit (the console's own mechanism — one authority); the unit carries voice.env -----
    started, msg = _sd.control(svc, "start")
    if not started:
        raise RuntimeError(f"failed to start {service_id!r} unit ({manage.get('unit')}): {msg} — "
                           f"check `journalctl --user -u {manage.get('unit')}` (fail loud)")
    # G7-loadcost: stamp the load START (wall-clock, cross-process). poll_wake() reads this when the
    # service first answers 'up' to measure the WAKE-TIME (measured, not estimated).
    try:
        with open(_loadstart_path(service_id), "w") as f:
            f.write(str(time.time()))
    except Exception:
        pass                                                   # telemetry must never break the load
    return {"service": service_id, "state": "warming", "port": load_spec["port"], "unit": manage.get("unit"),
            "note": "unit started — model loading; poll status() for 'up'"}


def _loadstart_path(service_id: str) -> str:
    return f"/tmp/company-voice-{service_id}.loadstart"


def poll_wake() -> list:
    """G7-loadcost: detect each loadable voice service that has just become 'up' AND carries a load-start
    marker → return its measured WAKE-TIME (ms) + the marker is consumed (removed) so it's recorded once.
    Stays Suite-free (returns data; the bridge emits the run-record via SUITE.emit_run_record) so the
    stdlib lifecycle stays importable in any interpreter. Returns [{service, wake_ms, vram_used_mb}]."""
    out = []
    try:
        free_used = vram().get("used_mb")
    except RuntimeError:
        free_used = None
    for sid, spec in _loadable().items():
        mp = _loadstart_path(sid)
        if not os.path.exists(mp):
            continue
        if not is_up(spec):
            continue                                           # still warming — leave the marker
        try:
            start = float(open(mp).read().strip())
            wake_ms = int((time.time() - start) * 1000)
            out.append({"service": sid, "wake_ms": wake_ms, "vram_used_mb": free_used})
        except Exception:
            pass
        try:
            os.remove(mp)                                      # record exactly once
        except OSError:
            pass
    return out


def unload(service_id: str) -> dict:
    """Free a voice service via the shared core's ORPHAN-SAFE teardown (gpu.teardown → systemctl stop →
    the unit's CGROUP is killed). The cgroup stop is what reaps vLLM's EngineCore (orpheus): EngineCore is
    a spawn child with NO OS death-link + finalizer-only cleanup, so a SIGTERM/SIGKILL to just the launcher
    pid orphans it (it reparents to init + squats ~10 GB — upstream #19849). The systemd cgroup kills the
    whole unit tree, EngineCore included — so the unit IS the orphan-safe path. We then VERIFY VRAM
    actually dropped and REPORT loud if it didn't (a possible orphan), never blind-killing GPU pids (other
    sessions share the card). Idempotent; fail loud on an unknown id."""
    loadables = _loadable()
    if service_id not in loadables:
        raise ValueError(f"unknown or non-loadable voice service {service_id!r} — loadable: {sorted(loadables)}")
    svc = loadables[service_id]["svc"]
    before = None
    try:
        before = vram().get("used_mb")
    except RuntimeError:
        pass
    ok, msg = _gpu.teardown(svc)                               # cgroup stop — reaps EngineCore
    time.sleep(1.5)                                            # let the card settle before the verify read
    after = None
    try:
        after = vram().get("used_mb")
    except RuntimeError:
        pass
    leftover = _sd.port_open(svc.get("port")) is True         # the unit's port still answering = not down
    note = f"freed via cgroup teardown ({msg})" if ok else f"teardown reported: {msg}"
    if leftover:                                              # fail loud — a possible orphan; don't stomp the card
        note = (f"WARNING: {service_id} still answering on port {svc.get('port')} after teardown — possible "
                f"orphan squatting VRAM (before={before}MB after={after}MB). Investigate "
                f"(journalctl --user -u {svc.get('manage', {}).get('unit')}); do NOT blind-kill GPU pids "
                f"(other sessions share the card).")
    return {"service": service_id, "state": "down" if not leftover else "leftover",
            "unit": svc.get("manage", {}).get("unit"),
            "vram_before_mb": before, "vram_after_mb": after, "note": note}


def engine_service_for(engine: str) -> str | None:
    """Map a TTS engine name (a persona's engine, e.g. 'qwen3tts') → its services.json id ('tts-qwen3tts'),
    so the circuit / config lab can pre-warm the engine a chosen persona needs. None if not loadable
    (e.g. 'kokoro' — always up)."""
    sid = f"tts-{engine}"
    return sid if sid in _loadable() else None


def resident_tts() -> list:
    """The tts-* engine services currently UP (the persona voices holding VRAM). Used by switch_to to
    evict the previous voice. STT ears are NOT included — only the persona TTS engines are juggled."""
    loadables = _loadable()
    return [sid for sid in loadables if sid.startswith("tts-") and is_up(loadables[sid])]


def switch_to(service_id: str) -> dict:
    """Make `service_id` the resident persona VOICE for a live persona switch: UNLOAD every OTHER resident
    tts-* engine first (the 16 GB card can't hold them all — a switch EVICTS the previous voice), then
    load the target. Cold-load is expected + accepted (Tim 2026-06-06: "if switching has to cold load them
    that will just have to be what happens"). The STT ear + the chat brain are untouched — only persona
    TTS engines are swapped. Returns the load result (`warming` → poll status() for `up`). Fail loud on a
    non-tts/unknown id, and — via load()'s budget gate — if the target won't fit even after eviction
    (e.g. orpheus ~10.5 GB cannot co-reside with a ~9.5 GB brain; the gate names what to unload)."""
    loadables = _loadable()
    if service_id not in loadables or not service_id.startswith("tts-"):
        raise ValueError(f"switch_to expects a loadable tts engine id (tts-*); got {service_id!r} — "
                         f"loadable engines: {sorted(s for s in loadables if s.startswith('tts-'))}")
    if is_up(loadables[service_id]):
        return {"service": service_id, "state": "up", "note": "already resident — no switch needed"}
    evicted = []
    for sid in resident_tts():
        if sid != service_id:
            unload(sid)                                        # cgroup teardown — frees the previous voice's VRAM
            evicted.append(sid)
    res = load(service_id)                                     # budget-gated; fail-loud if it still won't fit
    res["evicted"] = evicted
    return res
