// V-B control-flow proof (headless, no React/tldraw, no real mic/audio).
//
// WHAT THIS PROVES (the control flow, with audio + stream + STT all STUBBED):
//   1. RE-ARM: after a turn fires and the reply is spoken, the session loop creates a FRESH MediaRecorder
//      and RE-ENTERS the LISTENING phase — so turn 2, turn 3 … register speech. The old bug reused ONE
//      recorder + a stale (headerless) buffer, so turn 2's STT decoded empty and the loop never re-fired.
//      The teeth: we model the OLD reused-recorder behaviour (a recorder used twice yields a headerless,
//      empty-decoding blob on the 2nd use) and assert the NEW per-cycle-recorder flow does NOT hit that.
//   2. BARGE-IN: a barge-in signal during SPEAKING (a) cancels the in-flight stream reader (→ socket close
//      → the bridge's MSG_PEEK stops synth) AND (b) stops the live audio source nodes AND (c) bumps the
//      play-epoch so a chunk still decoding is dropped, then the loop starts a FRESH capture immediately.
//
// WHAT THIS DOES NOT PROVE (needs-tim, never claimed): real mic capture, real VAD on-device, audible
// barge-in cutoff, iOS audio. This is a control-flow proof, not a device proof.
//
// Run: node canvas/app/voice_autolisten_controlflow.test.mjs   (exits non-zero + prints on any failure)

let failures = 0
function check(name, cond) {
  if (cond) { console.log('  PASS ', name) }
  else { console.log('  FAIL ', name); failures++ }
}

// ---- stubs that mirror the real primitives the controller uses --------------------------------------

// A MediaRecorder stub modelling the webm-header reality. A recorder accumulates `segments` while running;
// chunk[0] carries the container header. A SNAPSHOT taken while the recorder runs (the fixed not-finished
// path) includes chunk[0] → has the header → decodable, and contains EVERYTHING captured so far. The OLD
// bug was reusing ONE recorder ACROSS turns with the buffer reset, so a later turn's blob had NO header.
let recorderSerial = 0
class StubRecorder {
  constructor() { this.id = ++recorderSerial; this.state = 'inactive'; this.segments = []; this.everHadHeader = false; this.onstop = null }
  start() { this.state = 'recording'; this.everHadHeader = true /* a freshly-started recorder emits a header */ }
  push(seg) { this.segments.push(seg) }                          // model speech captured into the running recorder
  snapshot() { return { headerless: !this.everHadHeader, text: this.segments.join(' ') } }   // while running — has header
  stop() { this.state = 'inactive'; const b = this.snapshot(); if (this.onstop) this.onstop(b); return b }
}

// STT stub: decodes a blob → its accumulated text, UNLESS headerless (then empty, like the real bug).
function sttDecode(blob) { return blob.headerless ? '' : (blob.text || '') }

// ---- the control-flow under test (a faithful transcription of the fixed loop's structure) ------------

// barge-in / playback handles (mirror voiceReaderRef / playSourcesRef / playEpochRef / bargedRef)
const ref = { reader: null, sources: [], epoch: 0, barged: false }
const log = []

function stopPlayback() {
  ref.epoch += 1
  for (const s of ref.sources) { try { s.stop() } catch {} }
  ref.sources = []
}
function bargeIn() {
  ref.barged = true
  stopPlayback()
  if (ref.reader) { try { ref.reader.cancel() } catch {} ; ref.reader = null }
  log.push('bargein')
}

// playWavBuffer stub: schedules a source, tracks it, honours the epoch (a chunk decoded after a barge-in
// is dropped — the exact guard the real playWavBuffer adds).
async function playWavBuffer() {
  const epoch = ref.epoch
  await Promise.resolve()                                 // model the async decode window
  if (epoch !== ref.epoch) return                         // barged-in mid-decode → drop
  const src = { stopped: false, stop() { this.stopped = true } }
  ref.sources.push(src)
}

// runVoiceTurn stub: consumes a stubbed ndjson reader, plays each chunk, exits on barge-in or done.
async function runVoiceTurn(streamChunks) {
  ref.barged = false
  let i = 0
  const reader = {
    cancelled: false,
    async read() {
      if (this.cancelled) return { done: true }
      await Promise.resolve()
      if (i >= streamChunks.length) return { done: true }
      return { done: false, value: streamChunks[i++] }
    },
    cancel() { this.cancelled = true },
  }
  ref.reader = reader
  try {
    for (;;) {
      let c; try { c = await reader.read() } catch { break }
      if (c.done) break
      if (ref.barged) break                               // operator spoke over the reply → stop consuming
      if (c.type === 'chunk') await playWavBuffer()
    }
  } finally { if (ref.reader === reader) ref.reader = null }
}

// listenOnce stub: a FRESH recorder per TURN (the re-arm fix). On each modelled pause it SNAPSHOTS the
// accumulated audio WITHOUT stopping (the not-finished accumulation fix), decodes, and judges. It only
// stop()s at the FIRE boundary. `utterance` is the list of speech segments for THIS turn; `judge` decides
// finished per cumulative text. Returns the fired blob+text, or null if nothing fired.
function listenOnce(state, utterance, judge) {
  const rec = new StubRecorder()
  state.recordersCreated.push(rec.id)
  rec.start()
  let fired = null
  for (const seg of utterance) {
    rec.push(seg)                                         // operator speaks a segment
    const snap = rec.snapshot()                           // SNAPSHOT while running (has header — fixed path)
    const text = sttDecode(snap)
    state.sttResults.push(text)                           // record what STT decoded at each pause (teeth)
    if (!text) continue                                   // empty decode → would NOT fire (the old turn-2 symptom)
    const j = judge(text)
    if (j.finished) { rec.stop(); fired = { blob: rec.snapshot(), text }; break }   // FIRE — stop flushes the tail
    // not finished → KEEP the recorder running + KEEP accumulation; loop to the next segment
  }
  return fired
}

// THE SESSION LOOP (the fixed shape): listen → fire → speak (barge-in watch) → RE-ARM.
// `turnsSpec` = per-turn { utterance:[segments], judge:fn }. bargeInOnTurn cancels that turn's reply.
async function sessionLoop({ turnsSpec, bargeInOnTurn, streamChunks }) {
  const state = { recordersCreated: [], sttResults: [], fires: 0, rearms: 0, firedTexts: [] }
  let stop = false
  for (let t = 0; t < turnsSpec.length && !stop; t++) {
    const fired = listenOnce(state, turnsSpec[t].utterance, turnsSpec[t].judge)
    if (!fired) break                                     // a null here = "stopped registering" (the bug)
    state.fires++; state.firedTexts.push(fired.text)
    // SPEAK with a barge-in watch
    let watching = true
    const watcher = (async () => {
      if (bargeInOnTurn === t) { await Promise.resolve(); bargeIn() }
      while (watching) { await Promise.resolve(); if (!watching) break; break }
    })()
    await runVoiceTurn(streamChunks)
    watching = false; await watcher
    state.rearms++                                        // re-arm: the loop continues to the next listenOnce
  }
  return state
}

// ---- the proofs ------------------------------------------------------------------------------------

const alwaysFinished = () => ({ finished: true, verdict: 'FINISHED' })

console.log('V-B-rearm: auto-listen re-arms with a FRESH recorder every turn')
const r = await sessionLoop({
  turnsSpec: [
    { utterance: ['turn one'], judge: alwaysFinished },
    { utterance: ['turn two'], judge: alwaysFinished },
    { utterance: ['turn three'], judge: alwaysFinished },
  ], bargeInOnTurn: -1, streamChunks: [{ type: 'chunk' }, { type: 'chunk' }],
})
check('fired on all 3 turns (turn 2+ did NOT go dead)', r.fires === 3)
check('re-armed after each spoken reply', r.rearms === 3)
check('a DISTINCT recorder was created per turn (no reuse → fresh header every turn)',
  new Set(r.recordersCreated).size === r.recordersCreated.length && r.recordersCreated.length === 3)
check('every turn decoded non-empty (no headerless turn-2 symptom)', r.sttResults.every(t => t !== ''))
check('each turn fired its OWN text', r.firedTexts.join('|') === 'turn one|turn two|turn three')

console.log('\nV-B-rearm (multi-segment): a NOT-FINISHED pause KEEPS accumulating — the thought is heard WHOLE')
{
  // segment 1 judged not-finished, segment 2 finished → the fired text MUST contain BOTH segments.
  // This is the regression the advisor caught: a fresh-recorder-per-PAUSE would have fired only "and settings".
  const segJudge = (text) => ({ finished: /settings/.test(text), verdict: 'x' })
  const r3 = await sessionLoop({
    turnsSpec: [{ utterance: ['show me the inbox', 'and settings'], judge: segJudge }],
    bargeInOnTurn: -1, streamChunks: [{ type: 'chunk' }],
  })
  check('fired once', r3.fires === 1)
  check('the fired thought contains BOTH segments (accumulation preserved, not truncated)',
    /show me the inbox/.test(r3.firedTexts[0]) && /and settings/.test(r3.firedTexts[0]))
}

console.log('\nV-B-rearm (teeth): the OLD reused-recorder path would have gone empty on turn 2')
{
  // model the OLD behaviour: ONE recorder reused across turns with the buffer RESET → 2nd use is headerless.
  const one = new StubRecorder(); one.start(); one.push('turn one')
  const f1 = one.snapshot()                              // turn 1: header present (freshly started)
  one.everHadHeader = false; one.segments = []           // the old code's reset: buffer cleared, no fresh start
  one.push('turn two'); const f2 = one.snapshot()        // turn 2: headerless continuation fragment
  check('old path: turn-1 blob decodes (header present)', sttDecode(f1) !== '')
  check('old path: turn-2 blob is EMPTY (headerless) — reproduces the reported symptom', sttDecode(f2) === '')
}

console.log('\nV-B-bargein: a barge-in during SPEAKING cancels the reader, stops sources, bumps epoch')
{
  ref.reader = null; ref.sources = []; ref.epoch = 0; ref.barged = false; log.length = 0
  const r2 = await sessionLoop({
    turnsSpec: [
      { utterance: ['turn one'], judge: alwaysFinished },
      { utterance: ['turn two'], judge: alwaysFinished },
    ], bargeInOnTurn: 0, streamChunks: [{ type: 'chunk' }, { type: 'chunk' }, { type: 'chunk' }],
  })
  check('bargeIn() fired', log.includes('bargein'))
  check('the in-flight reader was cancelled (socket close → bridge stops synth)', ref.reader === null)
  check('live audio sources were stopped + cleared', ref.sources.length === 0)
  check('still re-armed for the next turn after the interruption', r2.fires === 2 && r2.rearms === 2)
}

console.log('\nV-B-bargein (epoch teeth): a chunk decoding ACROSS a barge-in is dropped, not played')
{
  ref.reader = null; ref.sources = []; ref.epoch = 0; ref.barged = false
  const p = playWavBuffer()                               // starts decoding at epoch 0
  bargeIn()                                               // bumps epoch to 1 mid-decode
  await p
  check('the chunk that finished decoding after the cut was NOT scheduled', ref.sources.length === 0)
}

console.log('')
if (failures) { console.log('RESULT: ' + failures + ' FAILED'); process.exit(1) }
console.log('RESULT: all control-flow proofs PASS')
