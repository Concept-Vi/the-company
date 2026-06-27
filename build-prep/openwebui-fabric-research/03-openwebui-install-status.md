# OpenWebUI — Install & Status Report

**Date:** 2026-06-23
**Machine:** Workstation001 (Linux/WSL2, user `tim`)
**Investigated by:** Bash discovery (ports, processes, /proc, sqlite, docs)
**Premise confirmed by lead:** installed long ago, NEVER used/configured, no precious data, changes are fair game.

---

## TL;DR

There are **TWO** OpenWebUI installs on this machine, **neither currently serving**:

1. **Docker install (the documented/primary one)** — `openwebui/open-webui:latest`, host-network, was the canonical setup per the foundation docs. **The Docker daemon is DOWN** (the socket exists but `dockerd` returns HTTP 500 / `systemctl` reports docker inactive, no `docker.service` unit). So this container is not running and cannot be started until Docker itself is fixed.
2. **Python venv install** — `/home/tim/openwebui-venv/` (open-webui **0.8.12** via pip). Has a tiny throwaway dataset from a single 2026-04-04 session. Not running.

A **`*:8080` socket is LISTENING but DEAD** — it accepts a TCP connection then never responds (curl times out, HTTP 000; `Recv-Q` backlog climbing). Even under `sudo ss`/`lsof` it shows **no owning PID** — an orphaned/zombie listen socket (almost certainly a leftover from the dead Docker host-network binding). It is **not** a working OpenWebUI; it just squats the default port.

**Net state: nothing is configured, nothing is wired, nothing is serving. Effectively a clean slate.**

---

## 1. Where it's installed + method

| Install | Path | Method | Version | Status |
|---|---|---|---|---|
| **Docker (primary, documented)** | Docker volume `open-webui-data`, container `open-webui` | `docker run` host-network | `:latest` (docs reference 0.9.5 baseline) | **Cannot run — Docker daemon down** |
| **Python venv** | `/home/tim/openwebui-venv/` (binary at `bin/open-webui`, pkg at `lib/python3.11/site-packages/open_webui/`) | pip in venv | **0.8.12** | Installed, not running |

Supporting evidence found on disk:
- `/home/tim/company/foundation/operations/open-webui.md` + `open-webui-extras.md` — the canonical docs; describe the **Docker** install as the live one.
- `/home/tim/backups/open-webui-volume-20260528-*.tar.gz` — two ~988 MB backups of the **Docker volume** (named `pre-0.9.5-upgrade` and `pre-tier1`), so the Docker setup was real and once carried data.
- `/home/tim/openclaw-deploy/scripts/e2e/openwebui-docker.sh` + `openwebui-probe.mjs` — Docker-oriented deploy/probe scripts.
- Windows-side artifacts (not this machine's server): `Open WebUI.lnk` on Desktop, `open-webui-desktop-v0.0.20-x64-setup.exe` in Downloads — the desktop client, separate concern.

> Note: the venv's `data/readme.txt` literally says *"docker dir for backend files (db, documents, etc.)"* — i.e. the venv was a quick local spin-up; the intended home was always the Docker volume.

## 2. Running? On which port?

- **Not running.** No `open-webui`, `open_webui`, or `uvicorn` process exists (`pgrep` empty; `ps` clean).
- **Port 8080** (OpenWebUI default) is in `LISTEN` state on `*:8080` but is a **dead socket**: `curl http://127.0.0.1:8080/` connects then times out with 0 bytes (HTTP 000), and the `Recv-Q` backlog is non-zero and rising (6→7 across checks = connections piling up unaccepted). No PID owns it even under `sudo` — orphaned, likely a residue of the dead Docker host-network bind. **It must be cleared before a fresh OpenWebUI can bind 8080.**
- Docker daemon: socket `/var/run/docker.sock` exists (root:docker, dated Jun 20) but the daemon errors on every API call (`Internal Server Error ... v1.47`); `systemctl is-active docker` = inactive; no `docker.service` unit. **Docker is broken/half-up under WSL2.**

## 3. Config / data dir / backends pointed at

**Docker install (from docs `open-webui.md`):** the documented `docker run` wired it to:
- `OPENAI_API_BASE_URLS=http://localhost:8000/v1;http://localhost:8001/v1` (vLLM chat + vLLM embed)
- `OPENAI_API_KEYS=dummy;dummy`, `WEBUI_AUTH=false`, `ENABLE_OLLAMA_API=false`
- RAG embedding routed to `http://localhost:8001/v1` (BGE-M3)
- Data persisted in Docker volume `open-webui-data` (the 988 MB backups).
- **These backends are now STALE/DEAD** — see §4. The docs describe a substrate that no longer exists.

**Venv install:** `DATA_DIR = /home/tim/openwebui-venv/lib/python3.11/site-packages/open_webui/data/`
- `webui.db` (483 KB, SQLite, last touched 2026-04-04 12:43)
- `vector_db/chroma.sqlite3` (188 KB — default ChromaDB), `uploads/`, `cache/`
- **DB inspection: `user`=1, `chat`=0, `model`=0, `config`=1.** The single `config` row has only `version` + `ui` keys — **no `openai` block, no `ollama` block.** i.e. **zero model backends configured.** One throwaway user, no chats, no models, no connections. Genuinely unconfigured.

## 4. Connected vs empty (live backend reality)

| Backend | Port | Live now? | Evidence |
|---|---|---|---|
| **Ollama** | 11434 | ✅ **LIVE** | `/api/tags` returns models incl. cloud routes (e.g. `kimi-k2.7-code:cloud`). Listening on `127.0.0.1:11434`. |
| **LiteLLM proxy** | 4100 | ✅ **LIVE** (needs key) | `127.0.0.1:4100`; `/health` + `/v1/models` return `401 No api key passed in` → up, auth-gated. |
| vLLM chat | 8000 | ❌ dead | `/v1/models` returns empty; nothing listening. The docs' primary backend is GONE. |
| vLLM embed | 8001 | ❌ dead | empty; nothing listening. |
| OpenWebUI itself | 8080 | ⚠️ dead socket | listens but never responds; no owning process. |

**So:** every backend the docs say OpenWebUI is "connected" to (vLLM 8000/8001) is **dead**. The live model surfaces today are **Ollama (11434)** and **LiteLLM (4100)** — and neither is wired into either OpenWebUI install (venv config is empty; Docker can't run). **Everything is effectively empty.**

## 5. How to start it (per method)

**Recommended path — venv (no Docker dependency, clean slate):**
```bash
# clear the dead 8080 socket first (find/kill its owner, or just use a different port)
/home/tim/openwebui-venv/bin/open-webui serve --port 8081
# then in Admin Settings → Connections, add the LIVE backends:
#   Ollama:   http://localhost:11434   (or as OpenAI-compat: http://localhost:11434/v1, key=dummy)
#   LiteLLM:  http://localhost:4100/v1 (needs the litellm key)
```
(Env-var alternative: `OPENAI_API_BASE_URL=http://localhost:4100/v1` + `OPENAI_API_KEY=<litellm-key>`, and/or `OLLAMA_BASE_URL=http://localhost:11434` before `serve`.)

**Docker path — blocked until Docker is fixed:**
```bash
# 1. revive Docker under WSL2 first (daemon currently down):
sudo service docker start      # or restart Docker Desktop WSL integration
# 2. then per the documented launch (note: its 8000/8001 vLLM targets are dead — repoint to 11434/4100):
docker start open-webui        # if the container still exists
# or full re-run from open-webui.md §"Container management" with corrected OPENAI_API_BASE_URLS
```

> Caveat: docs reference version 0.9.5 for the Docker image but the venv is 0.8.12 — they are different installs at different versions. The 988 MB volume backups belong to the Docker line, not the venv.

---

## Open questions / flags for the lead

- **Pick a lane:** venv (0.8.12, simplest, no Docker) vs Docker (0.9.5, richer feature set per extras doc, but daemon is down). For a fabric experiment the venv is the fastest clean start; Docker needs a daemon-revive first.
- **Clear the orphaned :8080 socket** before any fresh bind, or run on :8081.
- **Backends to wire are 11434 (Ollama) + 4100 (LiteLLM)** — NOT the 8000/8001 vLLM pair the docs assume (those are dead).
- The 988 MB Docker-volume backups (2026-05-28) are the only sizeable historical data; lead said no precious data, so they're likely discardable — confirm before deleting.
