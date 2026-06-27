---
type: terrain-entry
name: config-company
register: descriptive
aliases: ["config-company"]
path: /home/tim/.config/company
relation: external
kind: config
status: unconfirmed
created: 2026-06-22
last_active: 2026-06-22
size: 20K
coverage: { files_read: 2, files_total: 2, last_read: 2026-06-26 }
git_remote: none
purpose: Company config — TLS cert + key for the Tailscale serving host
secrets: true
serving_host: workstation001.tail777bc2.ts.net
data-store-for: ["[[company-systemd]]"]
relates-to: ["[[company]]"]
move_intent: none
tags: [control]
---

# config-company

## What it is
The Company's config directory. Currently it holds the TLS certificate + private key for serving the Company over Tailscale on the host `workstation001.tail777bc2.ts.net`.

Evidence (Observed): contents = `certs/workstation001.tail777bc2.ts.net.crt` + `certs/workstation001.tail777bc2.ts.net.key`. `openssl x509` → `subject=CN=workstation001.tail777bc2.ts.net`, valid `Jun 4 2026 → Sep 2 2026 GMT`. Total 20K.

## How it works
Static credential material — read by whatever Company service terminates TLS for remote/Tailscale serving (e.g. `company-remote.service`; the bridge serves the UI face on :8770). The cert CN matches Tim's Tailscale serving host, so this is the trust material for mobile/remote access (the established iPhone-via-Tailscale path).

## What it connects to
- `[[company]]` — config for the Company's serving layer.
- `[[company-systemd]]` — the units (`company-remote.service`, bridge) that present the Company over the network use this cert/key.

## When / where
Path `/home/tim/.config/company`, 20K, 2 files (under `certs/`). Both files mtime 2026-06-22 09:32 → created/last_active 2026-06-22. Cert validity window Jun 4 → Sep 2 2026.

## Notes / evidence
Read: cert subject + validity dates via `openssl x509`. NOT opened: the private key (secret). `secrets: true` — this holds a TLS private key; do not commit or expose. Caveat: the cert expires 2026-09-02; renewal is a future operational concern.
