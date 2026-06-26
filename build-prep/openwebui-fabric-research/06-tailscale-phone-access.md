# Tailscale Phone Access — Current State + How to Expose OpenWebUI

**Research date:** 2026-06-23
**Machine:** Workstation001 (WSL2, Linux 5.15 microsoft-standard-WSL2)
**Tailscale version:** 1.98.4
**Goal:** Let Tim reach OpenWebUI (and other local services) from his phone, privately, over HTTPS.

Evidence classification used throughout: **Verified** = confirmed by running a command, **Observed** = read directly from output, **Inferred** = pattern-matched, not proven.

---

## 1. Current State (all Verified unless noted)

### Tailnet & devices
- **Tailnet name:** `tail777bc2.ts.net` (MagicDNS suffix) — *Observed* from `tailscale status --json`.
- **This machine's MagicDNS hostname:** `workstation001.tail777bc2.ts.net` (Tailscale IP `100.81.137.106`). — *Verified* (`tailscale ip -4`, status).
- **Phone IS on the tailnet:** `iphone171` at `100.80.200.93`, owner `t.geldard@`, OS iOS, currently shown in `tailscale status`. — *Verified*. The phone and this machine are already peers on the same tailnet, so no new device pairing is needed.

```
100.81.137.106  workstation001  t.geldard@  linux  -
100.80.200.93   iphone171       t.geldard@  iOS    -
```

### Where Tailscale runs (the WSL2 question — answered)
- **Tailscale runs NATIVELY INSIDE this WSL2 instance**, NOT on the Windows host. — *Verified*: `tailscaled` is running as a native Linux daemon, pid 4169:
  ```
  /usr/sbin/tailscaled --state=/var/lib/tailscale/tailscaled.state --socket=/run/tailscale/tailscaled.sock --port=41641
  ```
  It is a systemd service, **enabled** (auto-starts), active since the WSL instance came up.
- **Consequence (load-bearing):** because the daemon lives in WSL, anything it proxies to `127.0.0.1:<port>` must be a service **running inside this same WSL2 instance**. Services on the Windows host are NOT reachable at this `127.0.0.1`. (This is exactly how `ollama` works today: it listens on `127.0.0.1:11434` inside WSL.) — *Verified* (ollama listener + tailscaled both in WSL).

### Serve / Funnel already configured (this is how mobile access works today)
`tailscale serve status` shows TWO existing mappings — *Verified*:

```
https://workstation001.tail777bc2.ts.net          (Funnel ON, public)   -> proxy http://127.0.0.1:8772
https://workstation001.tail777bc2.ts.net:8443     (tailnet only)        -> proxy http://127.0.0.1:5174
```

- **Port 443** → `127.0.0.1:8772`, **Funnel ON** = exposed to the **public internet**. The service behind it returns HTTP 401 (auth-gated). — *Verified*.
- **Port 8443** → `127.0.0.1:5174`, **tailnet-only** (private). Returns HTTP 200. — *Verified*.
- **End-to-end HTTPS proven:** `curl https://workstation001.tail777bc2.ts.net:8443/` returns **200 with valid TLS** (no cert errors). — *Verified*. This is the working private-mobile pattern: a local service proxied over an auto-TLS tailnet HTTPS host. (Which service 8772/5174 are — the Company surface, a PWA bridge, etc. — is *Inferred*, not confirmed, and doesn't matter for this task. The proven, load-bearing fact is the **pattern**.)

**This answers "how does mobile access already work":** via `tailscale serve` (and one `funnel`) reverse-proxying local ports to auto-TLS HTTPS hostnames on the tailnet — option (b) below. It is NOT a `0.0.0.0` bind.

### OpenWebUI right now
- **OpenWebUI is NOT currently running.** — *Verified*: nothing answers on 8080 from any address, and no open-webui process exists. Ollama (its usual backend) IS running on `127.0.0.1:11434`. — *Verified*.
- **Stale socket warning:** there is a half-open listener on `*:8080` (`Recv-Q 3`, no owning PID visible, refuses all connections — `127.0.0.1`, `0.0.0.0`, `localhost`, and the Tailscale IP all return connection-refused/000). — *Verified*. This looks like a stale/crashed bind (possibly held cross-namespace by the Windows side). **Before binding OpenWebUI to 8080, clear or re-check this** or the bind may conflict. Easiest path: run OpenWebUI on a clean port (e.g. 8081) and serve that instead.

---

## 2. Recommended Way to Expose OpenWebUI to the Phone

**Use `tailscale serve` (tailnet-private, auto-HTTPS) on a NEW port — do NOT reuse 443 or 8443.**

### Why serve, not the alternatives
- **(a) Bind OpenWebUI to `0.0.0.0` and hit the Tailscale IP** — works for raw access, but the URL is plain **HTTP** on `http://100.81.137.106:8080`. **Rejected** because: no trusted TLS, and **PWA "Add to Home Screen" / installable PWA requires a secure HTTPS origin** — a bare HTTP IP does not qualify. It also exposes the port to the whole LAN, not just the tailnet.
- **(b) `tailscale serve` (RECOMMENDED)** — reverse-proxy with an **auto-provisioned tailnet TLS cert**, giving `https://workstation001.tail777bc2.ts.net:<port>`. Private to the tailnet (phone is already a member). The trusted HTTPS origin is exactly what makes the **PWA installable**, and it matches the pattern already proven working on this box (the 8443→5174 mapping). This is the clean answer.
- **(c) `tailscale funnel`** — same as serve but **public to the entire internet**. **Rejected** for a private phone-only UI. (The existing 443→8772 funnel is a separate, deliberately-public service; leave it alone.)

### The exact command

OpenWebUI's default port is 8080, but on THIS machine port 8080 has a stale socket and 8443 is already taken by the working surface. Run OpenWebUI on a clean local port and serve it on a clean tailnet port. Example using `8081` for OpenWebUI and `8444` for the HTTPS endpoint:

```bash
# 1. Run OpenWebUI bound to localhost INSIDE this WSL2 instance, on a free port (8081):
#    (docker example — adjust to however OpenWebUI is launched)
#    docker run -d -p 127.0.0.1:8081:8080 ... ghcr.io/open-webui/open-webui:main
#    The bind must be reachable at 127.0.0.1 from inside WSL.

# 2. Expose it to the tailnet over HTTPS, persistently, on a NEW port (8444):
tailscale serve --bg --https=8444 localhost:8081
```

Then from the phone (Safari), open:

```
https://workstation001.tail777bc2.ts.net:8444
```

Valid TLS, private to the tailnet, and **installable as a PWA** (Share -> Add to Home Screen).

If port 8080 is cleaned up and you prefer OpenWebUI on its native 8080, the serve command becomes `tailscale serve --bg --https=8444 localhost:8080` — but **keep the HTTPS port at 8444 (or any other free port), never 443 or 8443.**

### Verify after running
```bash
tailscale serve status     # confirm 443 and 8443 are UNCHANGED, and 8444 -> localhost:8081 appears
curl -s -o /dev/null -w "%{http_code}\n" https://workstation001.tail777bc2.ts.net:8444   # expect 200
```

---

## 3. Gotchas (must-read)

1. **PORT COLLISION — the #1 trap.** The official docs example is `tailscale serve --https=443 localhost:8080`. On THIS machine that would **overwrite the existing public funnel** (443→8772), and `--https=8443` would **clobber the working private surface** (8443→5174). **Always pick a fresh HTTPS port** (8444 suggested). Tailnet-only `serve` accepts arbitrary ports; only public `funnel` is restricted to 443/8443/10000. — *Verified* from the in-use config + serve help.

2. **NEVER run `tailscale serve reset` here.** `reset` clears **ALL** serve config — it would wipe both existing mappings (443 + 8443). To remove ONLY the OpenWebUI mapping later, use the targeted `off`:
   ```bash
   tailscale serve --https=8444 localhost:8081 off
   ```

3. **WSL same-namespace requirement.** `serve` proxies to `127.0.0.1`, and the daemon is inside WSL. OpenWebUI **must run inside this WSL2 instance** (like ollama does), not on the Windows host — otherwise `127.0.0.1:<port>` won't reach it. — *Verified* (daemon + ollama both in WSL).

4. **Persistence is TWO separate things.** `--bg` makes the **serve mapping** persist across Tailscale restarts/reboots. But **OpenWebUI itself still needs its own autostart** (docker `--restart unless-stopped`, a systemd unit, etc.). And the whole thing only works while **this WSL2 instance is running** — if WSL is shut down, both tailscaled and OpenWebUI stop. For always-on phone access, ensure WSL stays up (e.g. Windows Task Scheduler keeping the distro running, or `wsl --shutdown` avoidance).

5. **Stale `*:8080` socket.** Clear/re-check it before binding OpenWebUI to 8080, or run OpenWebUI on a different port (8081) to sidestep it entirely. — *Verified* it currently refuses connections.

6. **MagicDNS on the phone.** The `https://workstation001.tail777bc2.ts.net:8444` hostname resolves via Tailscale MagicDNS, which the iOS Tailscale app provides while the VPN is connected. The phone must have the **Tailscale app running/connected** for the name (and the route) to work. The phone is already a tailnet member, so no new auth is needed. — *Verified* phone is a peer; MagicDNS-on-phone is *Inferred* standard behavior.

---

## 4. One-line summary of the working pattern

`tailscale serve --bg --https=<FREE_PORT> localhost:<OPENWEBUI_PORT>` → reach `https://workstation001.tail777bc2.ts.net:<FREE_PORT>` from the phone. Private to the tailnet, auto-TLS, PWA-installable. Same mechanism already proven live on this machine at `:8443`.
