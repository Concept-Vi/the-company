// channels/profile_test.mjs — real end-to-end test of the company-channel `profile` self-write tool.
// Spawns the actual server with a controlled env, does the MCP stdio handshake, calls tools/call
// profile, and asserts the on-disk entry got the agent's self-described fields WHILE the transport
// fields (pid/port/handle) are preserved. Run: node channels/profile_test.mjs
import { spawn } from 'node:child_process'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const SERVER = path.join(path.dirname(fileURLToPath(import.meta.url)), 'company_channel.mjs')
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'chprof-'))
const env = { ...process.env, COMPANY_ROOT: tmp, COMPANY_CHANNEL_HANDLE: 'test-prof',
  COMPANY_CHANNEL_PORT: '0', COMPANY_CHANNEL_MODEL: 'claude-fable-5', COMPANY_SESSION_ID: 'sess-test' }
const srv = spawn('node', [SERVER], { env, stdio: ['pipe', 'pipe', 'pipe'] })

let buf = ''
const pending = []
srv.stdout.on('data', d => {
  buf += d.toString()
  let i
  while ((i = buf.indexOf('\n')) >= 0) {
    const line = buf.slice(0, i); buf = buf.slice(i + 1)
    if (line.trim()) { try { pending.push(JSON.parse(line)) } catch {} }
  }
})
srv.stderr.on('data', () => {})
const send = (o) => srv.stdin.write(JSON.stringify(o) + '\n')
const sleep = (ms) => new Promise(r => setTimeout(r, ms))
const waitFor = (id, ms = 3000) => new Promise((res, rej) => {
  const t0 = Date.now()
  const iv = setInterval(() => {
    const m = pending.find(p => p.id === id)
    if (m) { clearInterval(iv); res(m) }
    else if (Date.now() - t0 > ms) { clearInterval(iv); rej(new Error('timeout id ' + id)) }
  }, 20)
})

try {
  await sleep(500)
  send({ jsonrpc: '2.0', id: 1, method: 'initialize', params: { protocolVersion: '2024-11-05', capabilities: {}, clientInfo: { name: 't', version: '1' } } })
  await waitFor(1)
  send({ jsonrpc: '2.0', method: 'notifications/initialized' })
  send({ jsonrpc: '2.0', id: 2, method: 'tools/call', params: { name: 'profile', arguments: { role: 'tester', focus: 'verifying the profile tool', description: 'test profile line' } } })
  const r = await waitFor(2)
  const reg = JSON.parse(fs.readFileSync(path.join(tmp, '.data', 'channels', 'test-prof.json'), 'utf8'))
  const checks = [
    ['profile.role == tester', reg.profile?.role === 'tester'],
    ['profile.focus written', reg.profile?.focus === 'verifying the profile tool'],
    ['description updated', reg.description === 'test profile line'],
    ['model (env) preserved', reg.model === 'claude-fable-5'],
    ['pid preserved (transport intact)', typeof reg.pid === 'number'],
    ['port preserved (transport intact)', typeof reg.port === 'number' && reg.port > 0],
    ['handle intact', reg.handle === 'test-prof'],
    ['tool returned ok', JSON.stringify(r).includes('profile written')],
  ]
  let ok = true
  for (const [name, pass] of checks) { console.log((pass ? 'PASS' : 'FAIL') + '  ' + name); if (!pass) ok = false }
  console.log('\n' + (ok ? 'ALL PROFILE CHECKS PASS' : 'PROFILE TEST FAILED'))
  srv.kill('SIGTERM'); fs.rmSync(tmp, { recursive: true, force: true })
  process.exit(ok ? 0 : 1)
} catch (e) {
  console.error('TEST ERROR:', e.message); srv.kill('SIGTERM'); process.exit(1)
}
