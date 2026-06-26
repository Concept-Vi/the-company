"""systemd — drive systemd/journald for the registry's services. stdlib-only.

The console drives systemd; it never replaces it (ops/AGENTS.md). user-units use
`--user`; system-units use `sudo -n` (fail fast if no passwordless sudo); `manual`
services have no unit (the console only reports/points at them); `hosted` services
run off-box (e.g. a Supabase edge fn) — no local unit/port, liveness is a remote URL."""
import socket, subprocess, urllib.request


def _ping_url(url, timeout=4):
    """GET a remote health URL -> True on 2xx. For 'hosted' services with no local port —
    their liveness is a remote URL, not a 127.0.0.1 socket."""
    if not url:
        return False
    try:
        with urllib.request.urlopen(urllib.request.Request(url, method="GET"), timeout=timeout) as r:
            code = getattr(r, "status", None) or r.getcode()
            return 200 <= code < 300
    except Exception:
        return False


def _scope(svc):
    return ["--user"] if svc["manage"]["type"] == "user-unit" else []


def port_open(port, timeout=0.4):
    if not port:
        return None
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect(("127.0.0.1", int(port)))
        return True
    except OSError:
        return False
    finally:
        s.close()


def is_active(svc):
    """active | inactive | failed | not-managed | unknown."""
    m = svc["manage"]
    if m["type"] == "manual":
        return "not-managed"
    if m["type"] == "hosted":
        return "active" if _ping_url(m.get("health_url", "")) else "inactive"
    r = subprocess.run(["systemctl"] + _scope(svc) + ["is-active", m["unit"]],
                       capture_output=True, text=True)
    return r.stdout.strip() or "unknown"


def verdict(svc, shared_ports=frozenset()):
    """One honest read → (label, symbol). The per-unit is-active is AUTHORITATIVE for
    'is THIS service running' — NOT the port, because model services share ports
    (a sibling on the same port would otherwise read as this one running). The port
    only distinguishes RUNNING from active-but-not-listening-yet. Genuine drift
    (up by hand, outside its unit) is only inferred when the port is UNIQUE to it."""
    if svc["manage"]["type"] == "hosted":   # off-box (e.g. Supabase edge fn): liveness = its health URL
        return ("RUNNING", "▶") if _ping_url(svc["manage"].get("health_url", "")) else ("stopped", "·")
    state = is_active(svc)
    up = port_open(svc.get("port"))
    if svc["manage"]["type"] == "manual":
        return ("RUNNING", "▶") if up else ("stopped", "·")
    if state == "active":
        return ("RUNNING", "▶") if up else ("active (no port yet)", "◐")
    if state == "failed":
        return "FAILED", "✖"
    if up and svc.get("port") not in shared_ports:   # inactive unit but its own port is live = drift
        return "RUNNING (unmanaged)", "▶"
    return "stopped", "·"


def control(svc, action):
    """action ∈ {start,stop,restart}. Returns (ok, message)."""
    m = svc["manage"]
    if m["type"] == "manual":
        return False, f"manual — start with: {m.get('run', '(see registry)')}"
    if m["type"] == "hosted":
        if action == "stop":   # off-box — the console can't take it down (it's not ours to kill)
            return False, "hosted off-box (e.g. Supabase edge fn) — not stoppable from here; manage at the host"
        deploy = m.get("deploy")   # start/restart = (re)deploy the hosted function
        if not deploy:
            return False, "hosted — no deploy command in registry"
        r = subprocess.run(deploy, shell=True, capture_output=True, text=True)
        return r.returncode == 0, (r.stderr.strip()[:200] if r.returncode else "deployed")
    cmd = ["systemctl"] + _scope(svc) + [action, m["unit"]]
    if m["type"] == "system-unit":
        cmd = ["sudo", "-n"] + cmd
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode == 0, (r.stderr.strip()[:100] if r.returncode else m["unit"])


def journal(svc, follow):
    m = svc["manage"]
    if m["type"] == "manual":
        raise ValueError("manual service — no journal")
    if m["type"] == "hosted":   # off-box — logs come from the host's own log command
        logs = m.get("logs")
        if not logs:
            raise ValueError("hosted service — no logs command in registry")
        subprocess.run(logs, shell=True)
        return
    cmd = ["journalctl"] + _scope(svc) + ["-u", m["unit"], "-n", "60"]
    if follow:
        cmd.append("-f")
    subprocess.run(cmd)
