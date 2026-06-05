"""voice/lifecycle.py — load / unload / status for ALL loadable VOICE SERVICES (G4.7 + boot-on-demand).

The UI-driven, voice-scoped slice of the VRAM resource-manager — generalised past the STT ears to the
TTS engines too (Tim: "if voice is down you can boot it up, to make it all live"). A loadable voice
service = any `group:"voice"` entry in ops/services.json carrying a `load` block (the 3 GPU ears +
the 5 trial TTS engines). whisper.cpp (CPU) + Kokoro + assemblyai have no `load` block → nothing to load.

ONE SOURCE OF TRUTH: ops/services.json (the service registry the `company` console already owns). We do
NOT keep a second port/venv/vram map here — `_loadable()` reads it. Adding a loadable voice service =
adding its services.json entry; no edit here.

  • load(id)   = launch the service in its own venv subprocess (model loads at warm()/first use; NeMo
                 ears are MINUTES, TTS engines ~25s, orpheus ~17min/swap-hostile). Returns IMMEDIATELY
                 'warming' (poll status() for 'up'). FAIL LOUD if it won't fit the card (names free vs
                 needed + which to unload) — NEVER a silent OOM.
  • unload(id) = SIGTERM the service's process(es) → VRAM freed. Idempotent.
  • status()   = per service: up / warming / down + the card VRAM.

Stdlib-only → runs IN the 3.14 bridge; the service runs as a subprocess in its own venv (NeMo /
transformers / vLLM never touch the bridge interpreter). Teardown is by pgrep on the script path, so
unload works across a bridge restart (no in-memory pid table to lose).
"""
from __future__ import annotations
import json
import os
import shutil
import subprocess
import urllib.error
import urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVICES_JSON = os.path.join(REPO, "ops", "services.json")
ENV_FILE = os.path.join(REPO, "voice", "ops", "voice.env")

# WSL ships nvidia-smi at a non-PATH location; env-overridable, fall back to PATH.
_WSL_SMI = "/usr/lib/wsl/lib/nvidia-smi"
SMI = os.environ.get("COMPANY_NVIDIA_SMI") or (_WSL_SMI if os.path.exists(_WSL_SMI)
                                               else (shutil.which("nvidia-smi") or _WSL_SMI))


def _loadable() -> dict:
    """id → its `load` block (+ health path), for every group:voice service in services.json that
    declares one. The SINGLE source — no hardcoded map here (registry-is-truth)."""
    with open(SERVICES_JSON, encoding="utf-8") as f:
        services = json.load(f).get("services", {})
    out = {}
    for sid, spec in services.items():
        if spec.get("group") == "voice" and isinstance(spec.get("load"), dict):
            out[sid] = {**spec["load"], "health": spec.get("health", "/"), "title": spec.get("title", sid)}
    return out


def _url(load: dict) -> str:
    return f"http://127.0.0.1:{load['port']}"


def vram() -> dict:
    """Card memory in MB via nvidia-smi (the WSL path). FAIL LOUD if nvidia-smi is unavailable — we do
    NOT 'assume it fits' and risk an OOM (no-silent-failure)."""
    try:
        out = subprocess.run(
            [SMI, "--query-gpu=memory.used,memory.free,memory.total", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=10)
    except (FileNotFoundError, OSError, subprocess.SubprocessError) as e:
        raise RuntimeError(f"nvidia-smi unavailable at {SMI!r} ({type(e).__name__}: {e}) — "
                           f"cannot VRAM-budget a load (fail loud)")
    if out.returncode != 0:
        raise RuntimeError(f"nvidia-smi failed (rc={out.returncode}): {out.stderr.strip()}")
    used, free, total = (int(x.strip()) for x in out.stdout.strip().split(",")[:3])
    return {"used_mb": used, "free_mb": free, "total_mb": total}


def is_up(load: dict) -> bool:
    """Liveness probe (GET the service's health path → answers). Never raises — down/unreachable = False.
    Ears answer GET / ; engines answer GET /voices (the per-service `health` from services.json)."""
    try:
        with urllib.request.urlopen(_url(load) + load.get("health", "/"), timeout=3) as r:
            return 200 <= r.status < 500
    except urllib.error.HTTPError as he:
        return he.code < 500
    except Exception:
        return False


def _pids(load: dict) -> list:
    """PIDs running this service's script — by pgrep, so unload is stateless across bridge restarts."""
    try:
        out = subprocess.run(["pgrep", "-f", load["script"]], capture_output=True, text=True, timeout=5)
        return [int(p) for p in out.stdout.split()]
    except Exception:
        return []


def status() -> dict:
    """Per loadable voice service: up (health answers) / warming (process running, not yet up) / down —
    plus the card VRAM. Fail-SOFT on the VRAM read here (the picker still renders if nvidia-smi
    hiccups); load() is the fail-LOUD budget gate."""
    try:
        v = vram()
    except RuntimeError as e:
        v = {"error": str(e)}
    services = {}
    for sid, load_spec in _loadable().items():
        up = is_up(load_spec)
        state = "up" if up else ("warming" if _pids(load_spec) else "down")
        services[sid] = {"id": sid, "title": load_spec["title"], "kind": load_spec.get("kind"),
                         "port": load_spec["port"], "state": state, "vram_mb_est": load_spec.get("vram_mb")}
    return {"vram": v, "services": services}


def load(service_id: str) -> dict:
    """Bring a voice service resident: launch its process in its own venv (the model loads at warm()/
    first use). Returns IMMEDIATELY 'warming' (poll status() for 'up'). FAIL LOUD on: unknown/non-
    loadable id, missing venv, OR a load that won't fit the card (names free vs needed + the resident
    loadable voice services to unload). Idempotent: an already-up service returns 'up' without relaunch."""
    loadables = _loadable()
    if service_id not in loadables:
        raise ValueError(f"unknown or non-loadable voice service {service_id!r} — loadable: "
                         f"{sorted(loadables)} (whisper.cpp/Kokoro/cloud have no load step)")
    load_spec = loadables[service_id]
    if is_up(load_spec):
        return {"service": service_id, "state": "up", "note": "already resident"}
    py = os.path.expanduser(f"~/.voice-venvs/{load_spec['venv']}/bin/python")
    if not os.path.exists(py):
        raise RuntimeError(f"voice service {service_id!r} venv missing at {py} — install it "
                           f"(voice/ears/REQUIREMENTS.md or voice/engines/REQUIREMENTS.md)")
    need = load_spec.get("vram_mb", 0)
    free = vram()["free_mb"]                                    # fail-loud if nvidia-smi is unavailable
    if free < need:
        resident = [s for s in loadables if s != service_id and is_up(loadables[s])]
        raise RuntimeError(
            f"cannot load {service_id!r}: needs ~{need} MB, only {free} MB free on the card. Unload to "
            f"make room" + (f" (resident: {', '.join(resident)})" if resident else "")
            + " — refusing to OOM (fail loud).")
    script = os.path.join(REPO, load_spec["script"])
    logp = f"/tmp/company-voice-{service_id}.log"
    env = dict(os.environ)
    if os.path.exists(ENV_FILE):                               # the engines/ears read voice.env (CUDA_HOME, refs…)
        for line in open(ENV_FILE, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                if line.startswith("export "):                 # voice.env uses `export KEY=VAL` on some lines
                    line = line[len("export "):]
                k, _, val = line.partition("=")
                env.setdefault(k.strip(), val.strip().strip('"').strip("'"))
    log = open(logp, "ab")                                     # noqa: SIM115 (handed to the child)
    subprocess.Popen([py, script, str(load_spec["port"])], cwd=REPO, env=env,
                     stdout=log, stderr=log, start_new_session=True)
    return {"service": service_id, "state": "warming", "port": load_spec["port"], "log": logp,
            "note": "launched — model loading; poll status() for 'up'"}


def unload(service_id: str) -> dict:
    """Free a voice service: SIGTERM its process(es) → VRAM released. Idempotent (not-running = already
    freed). Fail loud on an unknown/non-loadable id."""
    loadables = _loadable()
    if service_id not in loadables:
        raise ValueError(f"unknown or non-loadable voice service {service_id!r} — loadable: {sorted(loadables)}")
    pids = _pids(loadables[service_id])
    for pid in pids:
        try:
            os.kill(pid, 15)                                   # SIGTERM — graceful
        except ProcessLookupError:
            pass
    return {"service": service_id, "state": "down", "killed_pids": pids,
            "note": "freed" if pids else "was not running"}


def engine_service_for(engine: str) -> str | None:
    """Map a TTS engine name (a persona's engine, e.g. 'qwen3tts') → its services.json id ('tts-qwen3tts'),
    so the circuit / config lab can pre-warm the engine a chosen persona needs. None if not loadable
    (e.g. 'kokoro' — always up)."""
    sid = f"tts-{engine}"
    return sid if sid in _loadable() else None
