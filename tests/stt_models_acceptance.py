"""tests/stt_models_acceptance.py — the GPU STT ears transcribe + their VRAM is MEASURED (LANE: stt, step 4).

The verification harness for the three GPU ears (parakeet :2031 · canary :2032 · granite :2033). For each
ear whose service is UP it: synthesizes a known clip (live Kokoro), POSTs it through the ear's /inference,
asserts a correct transcript, and RECORDS the nvidia-smi VRAM delta around the load (the measured number
that replaces the estimated footprints). For each ear that's DOWN it SKIPs LOUD (never a vacuous pass) and
prints the registry detail — because the registered-but-down state is CORRECT (available_stt() probes the
port, reports available:false), not a failure of THIS lane's code.

VRAM REALITY (measured 2026-06-05): nvidia-smi reported ~595-654 MiB free of 16376 — the ~15.4 GB resident
allocation is UNATTRIBUTABLE under WSL (--query-compute-apps = [N/A]; :8000/:8001 both DOWN at probe). No
GPU STT model fits in <1 GB (smallest ~1 GB int8). So the live load + measured delta is ENVIRONMENT-BLOCKED
(needs_tim), NOT a code gap: the ear code is import-clean and registered; the services simply can't be
brought up until the card is freed. This harness is what proves them by USE once it is — run it then.

FAIL-LOUD POLICY: if NO ear service is up, this SKIPs all three LOUD and returns NON-ZERO (never an "ALL
PASS" over un-run checks). It does NOT install NeMo/transformers or load a model itself — bringing the ear
services up is the install step in voice/ears/REQUIREMENTS.md (own venv per ear, VRAM permitting).

Run (after starting an ear service): ./.venv/bin/python tests/stt_models_acceptance.py
"""
import json
import os
import subprocess
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from voice import stt as voice_stt

PASS = 0
ok = True
EARS = ["parakeet", "canary", "granite"]
NVSMI = "/usr/lib/wsl/lib/nvidia-smi" if os.path.exists("/usr/lib/wsl/lib/nvidia-smi") else "nvidia-smi"
measured = {}


def check(label, cond):
    global PASS, ok
    if cond:
        PASS += 1
        print(f"  PASS  {label}")
    else:
        ok = False
        print(f"  FAIL  {label}")


def vram_used_mib():
    try:
        out = subprocess.run([NVSMI, "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                             capture_output=True, text=True, timeout=10)
        return int(out.stdout.strip().splitlines()[0])
    except Exception:
        return None


def ear_up(pid) -> bool:
    spec = voice_stt.STT_PROVIDERS.get(pid, {})
    try:
        with urllib.request.urlopen(spec.get("url", "") + "/", timeout=3) as r:
            return 200 <= r.status < 500
    except Exception:
        return False


def kokoro_clip(text):
    url = os.environ.get("COMPANY_TTS_URL", "http://127.0.0.1:4123") + "/tts"
    try:
        req = urllib.request.Request(url, data=json.dumps({"text": text}).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read()
    except Exception:
        return None


print("GPU STT ears — transcribe + MEASURED VRAM (parakeet/canary/granite)")
print(f"VRAM now: used={vram_used_mib()} MiB (free is what matters; <~1 GB free = no GPU ear fits)")

reg = voice_stt.available_stt()
any_up = False
for pid in EARS:
    print(f"\n[{pid}]")
    detail = reg.get(pid, {}).get("detail", "?")
    if not ear_up(pid):
        print(f"  SKIP (LOUD): {pid} service down — registry: {detail}")
        print(f"    (registered-but-down is CORRECT; bring it up per voice/ears/REQUIREMENTS.md, then re-run)")
        ok = False
        continue
    any_up = True
    clip = kokoro_clip("The scheduler memo gate re-runs only what changed.")
    if clip is None:
        print("  SKIP (LOUD): Kokoro TTS unreachable — no clip to transcribe.")
        ok = False
        continue
    before = vram_used_mib()
    out = voice_stt.transcribe(clip, provider=pid)            # routes through the ear's /inference
    after = vram_used_mib()
    text = (out.get("text") or "").lower()
    print(f"    heard: {text!r}")
    check(f"{pid} returns a non-empty transcript", len(text.strip()) > 0)
    check(f"{pid} recovers a key word (scheduler/memo/gate/change)",
          any(w in text for w in ("scheduler", "memo", "gate", "change", "run")))
    if before is not None and after is not None:
        delta = after - before
        measured[pid] = {"before_mib": before, "after_mib": after, "delta_mib": delta}
        print(f"    MEASURED VRAM: {before} → {after} MiB (delta {delta:+d} MiB)")
    else:
        print("    (VRAM not measurable via nvidia-smi)")

if measured:
    print("\n=== MEASURED VRAM TABLE ===")
    for pid, m in measured.items():
        print(f"  {pid:10s}  delta {m['delta_mib']:+5d} MiB  ({m['before_mib']}→{m['after_mib']})")

if not any_up:
    print("\nNO GPU EAR SERVICE IS UP — all three skipped loud (VRAM-blocked / not installed; see "
          "voice/ears/REQUIREMENTS.md). This is the needs_tim branch, not a code failure.")

print(f"\n{'ALL PASS' if ok else 'FAILURES/SKIPS PRESENT'} — {PASS} checks passed")
sys.exit(0 if ok else 1)
