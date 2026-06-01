"""voice/stt.py — speech-to-text, a SWAPPABLE provider (see voice/AGENTS.md).

Default: AssemblyAI (cloud, top accuracy + low latency, key from ~/company/.secrets). Audio leaves
the machine — that trades the fully-local path; it's a config flag so you can flip to local Whisper.
Stdlib only (HTTP), so it runs in the 3.14 runtime venv — no heavy install for the cloud provider.
"""
from __future__ import annotations
import json
import os
import time
import urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_PROVIDER = os.environ.get("COMPANY_STT", "assemblyai")
AAI_BASE = "https://api.assemblyai.com/v2"


def secret(key: str, default: str = "") -> str:
    """env first, then ~/company/.secrets (KEY=VALUE, gitignored) — so a key never lives in code or git."""
    if os.environ.get(key):
        return os.environ[key]
    p = os.path.join(REPO, ".secrets")
    if os.path.exists(p):
        for line in open(p, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                if k.strip() == key:
                    return v.strip().strip('"').strip("'")
    return default


def available() -> dict:
    """Which providers are usable right now (the registry the RHM/UI should read — never guess)."""
    return {"assemblyai": bool(secret("ASSEMBLYAI_API_KEY")), "whisper_local": False}


def transcribe(audio: bytes, provider: str | None = None) -> dict:
    provider = provider or DEFAULT_PROVIDER
    if provider == "assemblyai":
        return _assemblyai(audio)
    if provider in ("whisper", "local"):
        return _whisper_local(audio)
    raise ValueError(f"unknown STT provider {provider!r}")


def _post(url: str, data: bytes, headers: dict, timeout: int = 90) -> dict:
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def _assemblyai(audio: bytes) -> dict:
    key = secret("ASSEMBLYAI_API_KEY")
    if not key:
        raise RuntimeError("ASSEMBLYAI_API_KEY not set — add it to ~/company/.secrets (gitignored) or the env")
    upload = _post(AAI_BASE + "/upload", audio,
                   {"authorization": key, "content-type": "application/octet-stream"})
    tid = _post(AAI_BASE + "/transcript", json.dumps({"audio_url": upload["upload_url"]}).encode(),
                {"authorization": key, "content-type": "application/json"})["id"]
    for _ in range(90):                                   # poll until done (fail loud on error/timeout)
        req = urllib.request.Request(AAI_BASE + f"/transcript/{tid}", headers={"authorization": key})
        with urllib.request.urlopen(req, timeout=60) as r:
            d = json.loads(r.read())
        if d["status"] == "completed":
            return {"text": d.get("text") or "", "provider": "assemblyai"}
        if d["status"] == "error":
            raise RuntimeError("AssemblyAI error: " + str(d.get("error")))
        time.sleep(1)
    raise RuntimeError("AssemblyAI transcription timed out")


def _whisper_local(audio: bytes) -> dict:
    raise NotImplementedError(
        "local faster-whisper STT not installed — set COMPANY_STT=assemblyai, or install the local "
        "provider in .voice-venv (faster-whisper) when you want fully-on-machine STT.")
