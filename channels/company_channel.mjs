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
const MODEL = process.env.COMPANY_CHANNEL_MODEL || ''   // machine-set model id; the agent enriches via `profile`
let PROFILE = {}                                          // the agent's SELF-written profile (model/role/focus/…)
const SUPERVISOR = process.env.COMPANY_SUPERVISOR_BASE || 'http://127.0.0.1:8771'
const REGDIR = path.join(REPO, '.data', 'channels')
const REG = path.join(REGDIR, HANDLE + '.json')

// #69 fold-home: record this session's CLAUDE-ANCESTOR PID on the registration — the session-unique
// self-id key (resolve_own_session scans .data/channels/*.json by it). The channel server, the company
// MCP server, and the SessionStart hook are all children of the SAME claude session process, so all
// three walk to the SAME PID = the shared key. FAILURE-ISOLATED (the LEAD's caution #1): any /proc
// error → null, NEVER throw — a thrown announce = a session fails to register on the live fabric (high
// blast radius). Computed ONCE at load (the ancestor is stable for the session's life).
function claudeAncestorPid() {
  try {
    let pid = process.pid
    for (let i = 0; i < 40 && pid > 1; i++) {
      const stat = fs.readFileSync(`/proc/${pid}/stat`, 'utf8')
      // comm is parenthesised + may contain spaces/parens → slice between first '(' and last ')'
      const lp = stat.indexOf('('), rp = stat.lastIndexOf(')')
      const comm = stat.slice(lp + 1, rp)
      const after = stat.slice(rp + 2).split(' ')   // fields after comm: state ppid ...
      const ppid = parseInt(after[1], 10)
      let argv0 = ''   // the EXECUTABLE (argv0 basename), NOT a loose '/claude' substring anywhere in
      try { argv0 = fs.readFileSync(`/proc/${pid}/cmdline`, 'utf8').split('\0')[0] } catch {}   // argv
      const base = argv0.slice(argv0.lastIndexOf('/') + 1)    // (a substring match would mis-identify self)
      if (comm === 'claude' || base === 'claude' || /^\d+\.\d+\.\d+$/.test(comm)) return pid
      pid = ppid
    }
  } catch { return null }
  return null
}
const CLAUDE_PID = claudeAncestorPid()

function regEntry(port) {
  return {
    handle: HANDLE, session_id: SESSION_ID, cwd: process.cwd(), description: DESCRIPTION,
    model: MODEL, profile: PROFILE, pid: process.pid, claude_pid: CLAUDE_PID,
    port, started: new Date().toISOString(),
  }
}
function writeReg(port) {
  fs.mkdirSync(REGDIR, { recursive: true })
  fs.writeFileSync(REG, JSON.stringify(regEntry(port), null, 2))
}
// merge a patch into the EXISTING on-disk reg — the agent updating its OWN entry (it knows its handle).
// preserves the transport fields the server wrote (pid/port); only the self-described fields change.
function updateReg(patch) {
  try {
    const r = JSON.parse(fs.readFileSync(REG, 'utf8'))
    Object.assign(r, patch)
    fs.writeFileSync(REG, JSON.stringify(r, null, 2))
    return true
  } catch { return false }
}

const mcp = new Server(
  { name: 'company-channel', version: '0.2.0' },
  {
    capabilities: { experimental: { 'claude/channel': {}, 'claude/channel/permission': {} }, tools: {} },
    instructions:
      'Messages from the Company fabric arrive as <channel source="company-channel" from="..." thread="..."> tags — REAL messages from other Claude Code sessions or the operator, injected live. Read and act on them. To reply to one, call the `reply` tool with the text and the `thread` attribute from the tag (this delivers your reply back into the asking session). Once, near the start, call `profile` to write WHO YOU ARE into the fabric — your `model` (e.g. claude-fable-5), your `role`, and `focus` (what you are working on) — so other sessions see who they are talking to. (`announce` sets just a one-line description if that is all you have.)',
  },
)

mcp.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    { name: 'reply', description: 'Reply to a fabric/channel message (delivers back into the asking session)',
      inputSchema: { type: 'object', properties: { text: { type: 'string' }, thread: { type: 'string', description: 'the thread attribute from the inbound <channel> tag' } }, required: ['text'] } },
    { name: 'announce', description: 'Set this session\'s short one-line description so it is recognisable in the fabric',
      inputSchema: { type: 'object', properties: { description: { type: 'string' } }, required: ['description'] } },
    { name: 'profile', description: 'Write THIS session\'s OWN profile into its fabric registry entry (the agent describes itself — it knows its own handle). Fields merge into this session\'s entry; transport fields (pid/port) are preserved.',
      inputSchema: { type: 'object', properties: {
        description: { type: 'string', description: 'one-line summary (also updates the top-level description)' },
        model: { type: 'string', description: 'the model this session is running, e.g. claude-fable-5' },
        role: { type: 'string', description: 'this session\'s role in the fabric' },
        focus: { type: 'string', description: 'what this session is currently working on' },
        expertise: { type: 'string', description: 'what this session knows / can advise on' },
      } } },
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
    updateReg({ description: DESCRIPTION })
    return { content: [{ type: 'text', text: 'announced: ' + DESCRIPTION }] }
  }
  if (req.params.name === 'profile') {
    // the agent writes its OWN profile (it knows its handle). Merge the supplied self-described fields
    // into PROFILE; mirror description/model to the top level so `list` surfaces them without digging.
    const fields = {}
    for (const k of ['model', 'role', 'focus', 'expertise']) if (a[k] != null) fields[k] = String(a[k])
    PROFILE = { ...PROFILE, ...fields }
    const patch = { profile: PROFILE }
    if (a.description != null) { DESCRIPTION = String(a.description); patch.description = DESCRIPTION }
    if (a.model != null) patch.model = String(a.model)
    updateReg(patch)
    return { content: [{ type: 'text', text: 'profile written: ' + JSON.stringify(PROFILE) }] }
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
