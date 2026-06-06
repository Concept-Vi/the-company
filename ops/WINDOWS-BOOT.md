# Windows boot — start WSL so the Company comes up with no login

> **The last boot gap.** `loginctl enable-linger tim` makes the Company's user
> services (canvas · bridge · brain · voice, via `company.target`) start the moment
> **WSL** boots — no Linux login needed. But WSL itself only runs once Windows starts
> it. After a Windows reboot, if nobody launches WSL, the box is unreachable
> (phone over Tailscale included). This entry closes that: it launches WSL on Windows
> startup, the distro boots, linger starts `company.target`, everything comes up.

This is **Windows-side** setup — it cannot be done or verified from inside WSL. The
operator installs it once on the Windows host, then confirms reachability after a real
reboot. Until then this is `needs_tim` (see `ops.report.json`).

## What it does (the chain)
```
Windows starts  →  Task Scheduler runs `wsl`  →  WSL distro boots
   →  systemd user instance starts (linger is on)  →  company.target pulls up
      canvas :5173 · bridge :8770 · brain :8000 · TTS :4123 · STT :2022
   →  tailscaled (system) + `tailscale serve` expose canvas+bridge over the tailnet
   →  phone reaches https://workstation001.tail777bc2.ts.net/  — no login, no console
```

## Option A — Task Scheduler GUI (recommended; explicit + visible)
1. Press `Win`, type **Task Scheduler**, open it.
2. **Action → Create Task…** (not "Basic Task" — we need "run whether logged on or not").
3. **General** tab:
   - Name: `Start WSL (Company)`
   - Select **Run whether user is logged on or not**. *(This is what gives no-login
     reachability after a reboot. "Run only when user is logged on" would NOT start it
     at the lock screen.)*
   - Check **Run with highest privileges**.
   - Configure for: your Windows version (Windows 10/11).
4. **Triggers** tab → **New…**:
   - Begin the task: **At startup**. *(Earlier and login-independent than "At log on".
     If "At startup" proves flaky on this box, fall back to "At log on of any user".)*
   - (Optional) Delay task for: `30 seconds` — lets networking settle before WSL boots.
5. **Actions** tab → **New…**:
   - Action: **Start a program**
   - Program/script: `C:\Windows\System32\wsl.exe`
   - Add arguments: `-d Ubuntu --exec /bin/true`
     - Replace `Ubuntu` with your actual distro name — find it with `wsl -l -v` in a
       Windows terminal. `--exec /bin/true` boots the distro (which starts systemd +
       linger) then exits cleanly; the distro keeps running in the background.
     - If your distro is the default, `wsl.exe --exec /bin/true` (no `-d`) also works.
6. **Conditions** tab: **uncheck** "Start the task only if the computer is on AC power"
   (so it runs on a laptop on battery / a desktop always).
7. **Settings** tab: check **Run task as soon as possible after a scheduled start is
   missed**; leave **Stop the task if it runs longer than** unchecked (WSL is meant to
   stay up).
8. **OK.** It will prompt for the Windows account password (required for "run whether
   logged on or not"). Enter it.

## Option B — one PowerShell command (run as Administrator)
Equivalent to Option A; adjust the distro name (`-d Ubuntu`) to match `wsl -l -v`.
```powershell
$action  = New-ScheduledTaskAction  -Execute 'C:\Windows\System32\wsl.exe' -Argument '-d Ubuntu --exec /bin/true'
$trigger = New-ScheduledTaskTrigger -AtStartup
$trigger.Delay = 'PT30S'
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Password -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName 'Start WSL (Company)' -Action $action -Trigger $trigger -Principal $principal -Settings $settings
# It will prompt for the account password (needed for run-whether-logged-on-or-not).
```

## Verify (operator, after a real Windows reboot — this is the `needs_tim` step)
1. Reboot Windows. Do **not** open a WSL terminal or log in past the lock screen.
2. From the **phone** (on the tailnet) open `https://workstation001.tail777bc2.ts.net/`.
   The canvas should load — that proves the whole chain (WSL booted → linger →
   company.target → bridge/canvas → tailscale serve) with no login.
3. Or from another machine: `wsl -l --running` on the Windows host should list the
   distro as running shortly after boot, before any interactive WSL session.
4. If it didn't come up: open Task Scheduler → the task's **History** tab for the last
   run result, and check the distro name in the Action matches `wsl -l -v`.

## Notes
- **Why not `wsl.exe` with no command:** `wsl.exe` alone opens an interactive shell and
  blocks; `--exec /bin/true` boots the distro and returns, leaving systemd running.
- **systemd must be enabled in WSL** (`/etc/wsl.conf` → `[boot] systemd=true`) for the
  user services + linger to start on distro boot. On this box it already is (the
  `--user` units run today); listed here so a fresh machine isn't surprised.
- This file is the **only** record of the Windows-side step — keep it self-contained;
  the WSL-side boot story lives in `ops/STARTUP.md`.
