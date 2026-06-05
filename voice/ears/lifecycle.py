"""voice/ears/lifecycle.py — load / unload / status for the GPU STT ears (G4.7).

The UI-driven, ear-scoped slice of the VRAM resource-manager. The GPU ears (Parakeet / Canary /
Granite) are HTTP services in their OWN venvs; whisper.cpp (CPU) is always-on and assemblyai (cloud)
have nothing to load. So:
  • load(ear)   = launch the ear's process in its venv (the model loads at warm() — MINUTES for NeMo).
                  Returns IMMEDIATELY as 'warming' (poll status() for 'up'); fail-loud if it won't fit
                  the card (names free vs needed + which ears to unload) — NEVER a silent OOM.
  • unload(ear) = kill the ear's process(es) → VRAM freed. Idempotent.
  • status()    = per-ear up / warming / down + the card's VRAM.

Stdlib-only → this runs IN the 3.14 bridge; the ear itself runs as a subprocess in its own venv (so
NeMo/transformers never touch the bridge interpreter). Reuse-don't-parallel: the ears + ports come
from voice.stt.STT_PROVIDERS (the registry-is-truth source); this adds only launch/kill/VRAM control,
not a second registry. Process discovery is by `pgrep` on the ear's script, so unload works even
across a bridge restart (no in-memory pid table to lose).
"""
from __future__ import annotations
import os
import shutil
import subprocess
import urllib.error
import urllib.request

from voice import stt as voice_stt

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# WSL ships nvidia-smi at a non-PATH location; env-overridable, fall back to PATH.
_WSL_SMI = "/usr/lib/wsl/lib/nvidia-smi"
SMI = os.environ.get("COMPANY_NVIDIA_SMI") or (_WSL_SMI if os.path.exists(_WSL_SMI)
                                               else (shutil.which("nvidia-smi") or _WSL_SMI))

# The LOADABLE GPU ears: id → venv name · port · resident VRAM headroom (MB) used by the load() budget
# gate. parakeet is MEASURED BY USE (2026-06-05: ~5.1 GB resident on this card — notably above the
# VRAM-brief's ~3.05 GB estimate, so the gate uses the measured figure to avoid an OOM). canary/granite
# remain brief-estimates (~10.06 / ~4.66 GB) bumped with margin until measured the same way — a refuse
# is safer than an OOM (fail loud, never silently overcommit). whisper.cpp (CPU) + assemblyai (cloud)
# are NOT here — they need no load.
GPU_EARS = {
    "parakeet": {"venv": "parakeet", "port": 2031, "vram_mb": 5500},   # MEASURED ~5.1 GB resident
    "canary":   {"venv": "canary",   "port": 2032, "vram_mb": 12000},  # estimate (brief ~10 GB) + margin
    "granite":  {"venv": "granite",  "port": 2033, "vram_mb": 6500},   # estimate (brief ~4.66 GB) + margin
}


def _ear_url(ear: str) -> str:
    spec = voice_stt.STT_PROVIDERS.get(ear, {})
    return spec.get("url") or f"http://127.0.0.1:{GPU_EARS[ear]['port']}"


def vram() -> dict:
    """Card memory in MB via nvidia-smi (the WSL path). FAIL LOUD if nvidia-smi is unavailable — we do
    NOT 'assume it fits' and risk an OOM (that would violate the no-silent-failure law)."""
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


def is_up(ear: str) -> bool:
    """Liveness probe (GET / → answers). Never raises — a down/unreachable ear is just False."""
    try:
        with urllib.request.urlopen(_ear_url(ear) + "/", timeout=3) as r:
            return 200 <= r.status < 500
    except urllib.error.HTTPError as he:
        return he.code < 500
    except Exception:
        return False


def _pids(ear: str) -> list:
    """PIDs running this ear's script — by pgrep, so unload is stateless across bridge restarts."""
    try:
        out = subprocess.run(["pgrep", "-f", f"ears/{ear}.py"], capture_output=True, text=True, timeout=5)
        return [int(p) for p in out.stdout.split()]
    except Exception:
        return []


def status() -> dict:
    """Per GPU ear: up (port answers) / warming (process running, port not yet up) / down — plus the
    card VRAM. Fail-SOFT on the VRAM read here (so the picker still renders if nvidia-smi hiccups);
    load() is the fail-LOUD gate."""
    try:
        v = vram()
    except RuntimeError as e:
        v = {"error": str(e)}
    ears = {}
    for ear, spec in GPU_EARS.items():
        up = is_up(ear)
        state = "up" if up else ("warming" if _pids(ear) else "down")
        ears[ear] = {"ear": ear, "port": spec["port"], "state": state, "vram_mb_est": spec["vram_mb"]}
    return {"vram": v, "ears": ears}


def load(ear: str) -> dict:
    """Bring a GPU ear resident: launch its process in its own venv (model loads at warm() — MINUTES
    for NeMo). Returns IMMEDIATELY as 'warming' (poll status() for 'up'). FAIL LOUD on: unknown ear,
    missing venv, OR a load that won't fit the card (names free vs needed + the resident GPU ears to
    unload). Idempotent: an already-up ear returns 'up' without relaunching."""
    if ear not in GPU_EARS:
        raise ValueError(f"unknown GPU ear {ear!r} — one of {sorted(GPU_EARS)} "
                         f"(whisper.cpp is CPU/always-on, assemblyai is cloud — neither loads)")
    if is_up(ear):
        return {"ear": ear, "state": "up", "note": "already resident"}
    spec = GPU_EARS[ear]
    py = os.path.expanduser(f"~/.voice-venvs/{spec['venv']}/bin/python")
    if not os.path.exists(py):
        raise RuntimeError(f"ear {ear!r} venv missing at {py} — install it (voice/ears/REQUIREMENTS.md)")
    free = vram()["free_mb"]                                    # fail-loud if nvidia-smi is unavailable
    if free < spec["vram_mb"]:
        resident = [e for e in GPU_EARS if e != ear and is_up(e)]
        raise RuntimeError(
            f"cannot load {ear!r}: needs ~{spec['vram_mb']} MB, only {free} MB free on the card. "
            f"Unload to make room"
            + (f" (resident GPU ears: {', '.join(resident)})" if resident else "")
            + " — refusing to OOM (fail loud).")
    script = os.path.join(REPO, "voice", "ears", f"{ear}.py")
    logp = f"/tmp/company-ear-{ear}.log"
    log = open(logp, "ab")                                     # noqa: SIM115 (handed to the child)
    subprocess.Popen([py, script, str(spec["port"])], cwd=REPO,
                     stdout=log, stderr=log, start_new_session=True)
    return {"ear": ear, "state": "warming", "port": spec["port"], "log": logp,
            "note": "launched — model loading (NeMo cold-start is minutes); poll status() for 'up'"}


def unload(ear: str) -> dict:
    """Free a GPU ear: SIGTERM its process(es) → VRAM released. Idempotent (not-running = already
    freed). Fail loud on an unknown ear."""
    if ear not in GPU_EARS:
        raise ValueError(f"unknown GPU ear {ear!r} — one of {sorted(GPU_EARS)}")
    pids = _pids(ear)
    for pid in pids:
        try:
            os.kill(pid, 15)                                   # SIGTERM — graceful
        except ProcessLookupError:
            pass
    return {"ear": ear, "state": "down", "killed_pids": pids,
            "note": "freed" if pids else "was not running"}
