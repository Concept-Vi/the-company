# Reference — tools, endpoints, launch, loadout

## Launch a session into the fabric
```
claude --mcp-config /home/tim/company/channels/channel.mcp.json \
       --dangerously-load-development-channels server:company-channel
```
- Works from any directory; loads the channel ON TOP of the session's normal MCP servers.
- Approve the one-time "Use this MCP server?" consent if prompted.
- Look for the dim line: *Channels (experimental) messages from server:company-channel inject
  directly in this session* — that confirms registration.
- Optional env (set in `channel.mcp.json` or the launch env): `COMPANY_CHANNEL_HANDLE`,
  `COMPANY_CHANNEL_PORT` (default: auto), `COMPANY_SESSION_ID`, `COMPANY_CHANNEL_DESC`.

## The MCP tool: `mcp__company__cc_channel`
| op | args | does |
|---|---|---|
| `list` | — | every live channel-session: handle · cwd · description · started (auto-prunes dead) |
| `send` | `to`, `message`, [`thread`], [`topic`], [`frm`] | inject into one live session; returns `thread`; reply pushes back to you |
| `broadcast` | `to` (comma-sep), `message`, [`topic`], [`frm`] | group chat: fan to many, one shared `thread` |
| `mail` | [`thread`], [`limit`] | the durable record (messages + replies) |

`to` resolves a handle, an exact cwd, or a unique substring of cwd/description (fail-loud on
ambiguous). A **closed** session is not reachable by channel — use `session_post` wake/consult.

## Per-session channel tools (inside a channel-enabled session)
- `mcp__company-channel__announce {description}` — set this session's one-line description (identity).
- `mcp__company-channel__reply {text, thread}` — reply to an inbound `<channel>` message; pass the
  `thread` from the tag. Routes to the asker's conversation.

## Supervisor HTTP endpoints (the routing layer, 127.0.0.1:8771)
- `POST /channel-reply {from, thread, text}` — record a reply + push it to the thread originator.
- `POST /channel-send {to, message, from?, thread?, topic?}` — HTTP twin of `cc_channels.send`.
(Plus the existing fabric routes: `/spawn`, `/inject`, `/interrupt`, `/teardown`, `/sessions`,
`/watch`, `/bridge-session`.)

## The `@xsession` loadout (`ops/services.json` combos)
```
company up @xsession      # embed-pplx + tts-qwen3tts + stt-whisper
```
| service | port | ~VRAM | role |
|---|---|---|---|
| embed-pplx | 8007 | ~8.2G | pplx-embed-context-4b — semantic session/transcript search. `POST /v1/embeddings {input:[...]}` → 2560-dim int8 (compare by cosine) |
| tts-qwen3tts | 4128 | ~4.4G | Qwen3-TTS VoiceDesign — voice out, no voice clip needed. `POST / {text}` → 24kHz mono WAV |
| stt-whisper | 2022 | CPU/0 | whisper.cpp ear. `POST /v1/audio/transcriptions` → `{text}` |
~12.6G co-resident on the 16G card. Swap voice engine later via the registry (the combo is editable).
Free the card first if a brain/embedder is resident: `company down chat-4b embed-bge`.

## Files
- `channels/company_channel.mjs` — channel MCP server · `channels/channel.mcp.json` — launch config
- `runtime/cc_channels.py` — registry/router/threads/mail · `runtime/session_supervisor.py` — routes
- `mcp_face/tools/cc_channel.py` — the MCP tool
- runtime state: `.data/channels/<handle>.json` (registrations), `_mail.jsonl` (record),
  `_threads.json` (thread→originator)

## Verify it (quick checks)
- Loadout: `company gpu` (embed-pplx + tts-qwen3tts resident); embed `curl -s :8007/v1/embeddings -d
  '{"input":["x"],"model":"perplexity-ai/pplx-embed-context-v1-4b"}'` → dim 2560; voice `curl :4128/
  -d '{"text":"hi"}' -o t.wav` → RIFF WAVE.
- Channel loop: `cc_channel op=list` shows live sessions; `op=send` to one → it sees the tag; its
  `reply` → arrives in your conversation; `op=mail thread=<t>` shows both.
