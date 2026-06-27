---
type: terrain-entry
name: channel-test
register: descriptive
aliases: ["channel-test"]
path: /home/tim/channel-test
relation: external
kind: config
status: unconfirmed
created: 2026-06-14
last_active: 2026-06-14
size: 8K
coverage: { files_read: 1, files_total: 1, last_read: 2026-06-26 }
git_remote: none
relates-to: ["[[company]]"]
secrets: false
move_intent: none
launches: node /home/tim/company/channels/company_channel.mjs
handle: tim-live-1
port: 8795
company_root: /home/tim/company
tags: [fabric]
---

# channel-test

## What it is
A **single-file launch config** (`.mcp.json`, 303 bytes) whose only purpose is to join a Claude Code session to the **Company cross-session channel fabric**. It registers one MCP server, `company-channel`, that runs the Company's channel transport as a live mesh member.

Evidence — the entire file:
```json
{
  "mcpServers": {
    "company-channel": {
      "command": "node",
      "args": ["/home/tim/company/channels/company_channel.mjs"],
      "env": {
        "COMPANY_CHANNEL_PORT": "8795",
        "COMPANY_CHANNEL_HANDLE": "tim-live-1",
        "COMPANY_ROOT": "/home/tim/company"
      }
    }
  }
}
```

## How it works
When a Claude Code session is started with this folder as its working directory (so it picks up the local `.mcp.json`), it spawns `node ~/company/channels/company_channel.mjs` as an MCP server, configured via env vars: port **8795**, handle **`tim-live-1`**, and `COMPANY_ROOT` pointed at `~/company`. That gives the session the fabric tools (announce / profile / reply / DM / broadcast) to talk to other live sessions. It is a **test/bootstrap harness** — the smallest possible config to bring one named member onto the mesh.

## What it connects to
- **[[company]]** — directly: it launches `~/company/channels/company_channel.mjs` and roots itself at `~/company`. It is a thin external launcher for an engine that lives *inside* the Company folder; the real implementation is the channel transport in `~/company/channels/`.
- The cross-session fabric / channels system (the "company-channel" MCP, the same mechanism described in the fabric tooling and the `cross-session-fabric` skill).

## When / where
Created and last active 2026-06-14 16:04. Path `/home/tim/channel-test`, 8K, 1 file. No git. Read 1 of 1 (the whole `.mcp.json`).

## Notes / evidence
- State **dormant**: a standing config, not itself a running process — it only does anything when a session is launched against it.
- `secrets: false` — no credentials; just port/handle/root env.
- The handle `tim-live-1` and port `8795` are the identifying coordinates if this member appears on the mesh.
- Coverage caveat: I read the config in full but did not trace `company_channel.mjs` itself (that lives in `~/company` and belongs to the company-folder pass).
