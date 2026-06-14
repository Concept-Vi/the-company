#!/usr/bin/env node
// channels/company_channel.mjs — the Company's Claude Code CHANNEL server (cross-session live
// injection). Declares `claude/channel` so a session launched with
// --dangerously-load-development-channels server:company-channel registers a listener; an external
// POST to this server's port becomes a notifications/claude/channel event that lands IN the live
// conversation. Registers {handle, session_id, cwd, description, pid, port} under .data/channels/.
// Two-way: the `reply` tool routes the session's reply to the supervisor (/channel-reply) which
// records it in the mailbox AND pushes it back into the asking session. `announce` sets the session's
// short description (identity for discovery/history). Design: Tim 2026-06-14.
import { Server } from '@modelcontextprotocol/sdk/server/index.js'
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js'
import { ListToolsRequestSchema, CallToolRequestSchema } from '@modelcontextprotocol/sdk/types.js'
import http from 'node:http'
import fs from 'node:fs'
import path from 'node:path'

const HANDLE = process.env.COMPANY_CHANNEL_HANDLE || ('ch-' + Math.random().toString(36).slice(2, 10))
const SESSION_ID = process.env.COMPANY_SESSION_ID || ''
const PORT = parseInt(process.env.COMPANY_CHANNEL_PORT || '0', 10)
const REPO = process.env.COMPANY_ROOT || process.cwd()
let DESCRIPTION = process.env.COMPANY_CHANNEL_DESC || ''
const SUPERVISOR = process.env.COMPANY_SUPERVISOR_BASE || 'http://127.0.0.1:8771'
const REGDIR = path.join(REPO, '.data', 'channels')
const REG = path.join(REGDIR, HANDLE + '.json')

function writeReg(port) {
  fs.mkdirSync(REGDIR, { recursive: true })
  fs.writeFileSync(REG, JSON.stringify({
    handle: HANDLE, session_id: SESSION_ID, cwd: process.cwd(), description: DESCRIPTION,
    pid: process.pid, port, started: new Date().toISOString(),
  }, null, 2))
}

const mcp = new Server(
  { name: 'company-channel', version: '0.2.0' },
  {
    capabilities: { experimental: { 'claude/channel': {}, 'claude/channel/permission': {} }, tools: {} },
    instructions:
      'Messages from the Company fabric arrive as <channel source="company-channel" from="..." thread="..."> tags — REAL messages from other Claude Code sessions or the operator, injected live. Read and act on them. To reply to one, call the `reply` tool with the text and the `thread` attribute from the tag (this delivers your reply back into the asking session). Once, near the start, call `announce` with a one-line description of what this session is working on, so it is recognisable in the fabric.',
  },
)

mcp.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    { name: 'reply', description: 'Reply to a fabric/channel message (delivers back into the asking session)',
      inputSchema: { type: 'object', properties: { text: { type: 'string' }, thread: { type: 'string', description: 'the thread attribute from the inbound <channel> tag' } }, required: ['text'] } },
    { name: 'announce', description: 'Set this session\'s short description so it is recognisable in the fabric',
      inputSchema: { type: 'object', properties: { description: { type: 'string' } }, required: ['description'] } },
  ],
}))

async function postSupervisor(pathname, obj) {
  const body = JSON.stringify(obj)
  await new Promise((resolve) => {
    try {
      const u = new URL(SUPERVISOR + pathname)
      const req = http.request({ hostname: u.hostname, port: u.port, path: u.pathname, method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) } },
        (res) => { res.resume(); res.on('end', resolve) })
      req.on('error', resolve)   // best-effort; the mail log is the durable backstop
      req.write(body); req.end()
    } catch { resolve() }
  })
}

mcp.setRequestHandler(CallToolRequestSchema, async (req) => {
  const a = req.params.arguments || {}
  if (req.params.name === 'reply') {
    await postSupervisor('/channel-reply', { from: HANDLE, thread: a.thread || '', text: a.text })
    return { content: [{ type: 'text', text: 'reply delivered to the fabric' }] }
  }
  if (req.params.name === 'announce') {
    DESCRIPTION = String(a.description || '')
    try { const r = JSON.parse(fs.readFileSync(REG, 'utf8')); r.description = DESCRIPTION; fs.writeFileSync(REG, JSON.stringify(r, null, 2)) } catch {}
    return { content: [{ type: 'text', text: 'announced: ' + DESCRIPTION }] }
  }
  throw new Error('unknown tool: ' + req.params.name)
})

await mcp.connect(new StdioServerTransport())

const server = http.createServer(async (rq, rs) => {
  if (rq.method === 'POST') {
    let raw = ''
    for await (const c of rq) raw += c
    let content = raw, meta = {}
    try { const j = JSON.parse(raw); if (j && typeof j === 'object' && 'content' in j) { content = String(j.content); meta = j.meta || {} } } catch {}
    try { await mcp.notification({ method: 'notifications/claude/channel', params: { content, meta } }); rs.writeHead(200); rs.end('ok') }
    catch (e) { rs.writeHead(500); rs.end('notify failed: ' + e.message) }
    return
  }
  rs.writeHead(200); rs.end('company-channel ' + HANDLE)
})
server.listen(PORT, '127.0.0.1', () => {
  const port = server.address().port
  writeReg(port)
  process.stderr.write(`[company-channel] ${HANDLE} listening 127.0.0.1:${port} cwd=${process.cwd()}\n`)
})
const cleanup = () => { try { fs.unlinkSync(REG) } catch {} }
process.on('exit', cleanup)
process.on('SIGINT', () => { cleanup(); process.exit(0) })
process.on('SIGTERM', () => { cleanup(); process.exit(0) })
