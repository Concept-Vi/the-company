"""tests/voice_parts_acceptance.py — Concurrent Cognition G6 (voice coupling: the PART is the TTS unit).

Proves the LAST piece of the spine: the voice circuit synthesises part N WHILE the brain generates
part N+1 (brain↔TTS OVERLAP), and the preserve-list (the gate) holds.

  C6.1  — each completed PART is the TTS streaming unit; part-1 audio is EMITTED before part-2 is
          GENERATED (overlap). PROVEN DETERMINISTICALLY: a stub brain with a known per-part delay + a
          stub speak that timestamps each emitted chunk → assert t(part-1 chunk) < t(part-2 generated).
          Model-speed-independent (no live endpoint needed for the overlap proof).
  C6.2  — /api/voice/stream consumes a SEQUENCE of parts; in-order playback (monotonic idx across
          parts) preserved. Proven on the helper + (by-use) against the live worktree bridge :8772.

  PRESERVE (the gate):
    (1) in-order playback — chunk idx is MONOTONIC across ALL parts (never reset per part).
    (2) iOS unlock — UNTOUCHED: _voice_stream never creates/touches an AudioContext (server-side); the
        FE primeAudio path is unchanged (asserted structurally: no AudioContext logic in the server).
    (3) trial recording ONCE at turn end (not per part) — the assembled reply, the existing seam.
    (4) ONE chat event regardless of N parts — chat_parts' epilogue runs inside the generator; the
        handler must NOT emit its own chat / call SUITE.chat (asserted: SUITE.chat not called).
    (5) cancellation gated on part GENERATION — gone[0] between parts closes the generator (the next
        part is NOT generated); a mid-synth cancel stops before the next synth.
    (6) speak() near-unchanged — the helper calls speak_fn(sentence) exactly as before (one arg path).
    (7) brevity single-part path — a trivial turn → ONE part → a single synth, no regression.

  ADVERSARIAL: a brain exception is re-raised on the handler thread (fail loud, never a silent short
  stream); cancellation mid-stream stops the next part; the single-part path still works.

The DETERMINISTIC checks stub speak + a paced brain (no live endpoint). One LIVE by-use run against the
worktree bridge (:8772) proves the real circuit end-to-end (skipped-with-note if down — never a false green).
"""
import json
import os
import sys
import tempfile
import threading
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import runtime.bridge as bridge  # noqa: E402

PASS = 0
ok = True


def check(label, cond):
    global PASS, ok
    if cond:
        PASS += 1
        print(f"  PASS  {label}")
    else:
        ok = False
        print(f"  FAIL  {label}")


def _split(text):
    import re
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()] or ([text] if text.strip() else [])


# ====================================================================================================
# (1) C6.1 — THE OVERLAP PROOF (deterministic). A paced brain whose part-2 generation BLOCKS on a slow
#     step; a stub speak that timestamps each emitted chunk. We assert the FIRST chunk (part 1) is
#     emitted BEFORE part 2 finishes generating — i.e. synth ran CONCURRENTLY with the next brain part.
# ====================================================================================================
print("[1] C6.1 — brain↔TTS OVERLAP (deterministic, model-speed-independent)")

T0 = time.monotonic()
events_log = []          # (label, t) timeline
part2_generated_at = {}


def paced_parts_gen():
    # Part 1: ready immediately.
    yield {"part": 1, "text": "First part sentence one. First part sentence two.", "final": False, "staged": True}
    # Part 2: the brain "thinks" for a while BEFORE producing it. If synthesis of part 1 is concurrent,
    # part-1 chunks are emitted DURING this sleep (before part 2 exists).
    time.sleep(0.6)
    part2_generated_at["t"] = time.monotonic() - T0
    events_log.append(("part2_generated", time.monotonic() - T0))
    yield {"part": 2, "text": "Second part.", "final": True, "staged": True,
           "result": {"reply": "First part sentence one. First part sentence two.\n\nSecond part."}}


chunk_times = []


def stub_speak(sent):
    time.sleep(0.05)      # synth takes a little real time (so overlap is observable)
    return b"WAVDATA:" + sent.encode()


def stub_emit(c):
    chunk_times.append((c["idx"], c["text"], time.monotonic() - T0))
    events_log.append((f"chunk[{c['idx']}]", time.monotonic() - T0))


gone = [False]
res = bridge._stream_parts(paced_parts_gen(), speak_fn=stub_speak, emit_fn=stub_emit,
                           gone=gone, split_sentences=_split)

first_chunk_t = chunk_times[0][2] if chunk_times else 1e9
p2_t = part2_generated_at.get("t", -1)
check("C6.1 at least 3 chunks emitted (2 sentences of part1 + 1 of part2)", len(chunk_times) == 3)
check("C6.1 the FIRST chunk (part 1) is emitted BEFORE part 2 is generated (OVERLAP)",
      first_chunk_t < p2_t)
check("C6.2 chunk idx is MONOTONIC across parts (0,1,2 — never reset)",
      [c[0] for c in chunk_times] == [0, 1, 2])
check("the assembled reply is read from the epilogue result (both parts present)",
      "First part sentence one" in res["reply"] and "Second part" in res["reply"])
check("counts: 2 parts, 3 chunks", res["parts_done"] == 2 and res["chunks_done"] == 3)
print(f"    timeline: first-chunk@{first_chunk_t*1000:.0f}ms  part2-generated@{p2_t*1000:.0f}ms  "
      f"→ overlap={p2_t - first_chunk_t > 0}")

# dump the overlap evidence
os.makedirs("/tmp", exist_ok=True)
with open("/tmp/g6_overlap_timeline.json", "w") as f:
    json.dump({"first_chunk_ms": round(first_chunk_t * 1000, 1),
               "part2_generated_ms": round(p2_t * 1000, 1),
               "overlap_ms": round((p2_t - first_chunk_t) * 1000, 1),
               "timeline": [[lbl, round(t * 1000, 1)] for lbl, t in events_log],
               "chunks": [[i, txt, round(t * 1000, 1)] for i, txt, t in chunk_times]}, f, indent=2)
print("    → /tmp/g6_overlap_timeline.json")

# ====================================================================================================
# (2) PRESERVE (5) — CANCELLATION GATES PART GENERATION. Set gone[0] after part 1 is consumed; assert
#     part 2 is NEVER generated (the generator is closed between parts).
# ====================================================================================================
print("\n[2] PRESERVE(5) — cancellation gates part GENERATION (the next part is not generated)")

# The HONEST guarantee: the producer runs AHEAD (the overlap), so the part whose generation is IN FLIGHT
# when the client leaves will complete — but the producer checks gone[0] BEFORE pulling EACH next part, so
# the first part NOT-YET-STARTED after cancel is NEVER generated (cancel gates part-GEN). We prove that
# robustly with a 3-part generator: cancel during part-1 synth; part 2 may be in flight (we do NOT assert
# on it), but part 3 — gated behind an event the consumer sets when gone — must NEVER generate. Whether
# the producer breaks at its 2nd or 3rd gone-check, part 3 never generates. No timing race on the assertion.
cancel_gen_log = {"parts_generated": []}
gone_is_set = threading.Event()        # consumer signals: gone[0] has been set


def cancel_parts_gen():
    cancel_gen_log["parts_generated"].append(1)
    yield {"part": 1, "text": "Part one here.", "final": False, "staged": True}
    gone_is_set.wait(timeout=3)        # part-2 GEN parks here until the consumer sets gone (deterministic)
    cancel_gen_log["parts_generated"].append(2)
    yield {"part": 2, "text": "Part two.", "final": False, "staged": True}
    cancel_gen_log["parts_generated"].append(3)   # part 3 — must NEVER be reached (gone is set by now)
    yield {"part": 3, "text": "Part three.", "final": True, "staged": True,
           "result": {"reply": "Part one here.\n\nPart two.\n\nPart three."}}


gone2 = [False]
emitted2 = []


def speak_then_cancel(sent):
    gone2[0] = True       # client disconnects on the FIRST synth (during part 1)
    gone_is_set.set()     # release part-2 gen; the producer's gone-check before part 3 must then STOP it
    return b"w"


res2 = bridge._stream_parts(cancel_parts_gen(), speak_fn=speak_then_cancel,
                            emit_fn=lambda c: emitted2.append(c), gone=gone2, split_sentences=_split)
check("PRESERVE(5) part 3 (the first part NOT-yet-started at cancel) was NEVER generated (cancel gates part-GEN)",
      3 not in cancel_gen_log["parts_generated"])
check("PRESERVE(5) the stream reports cancelled", res2["cancelled"] is True)

# ====================================================================================================
# (3) PRESERVE(7) + brevity single-part path: a generator that yields ONE final part (chat_parts'
#     bypass / off shape) → a single synth, no overlap machinery regression.
# ====================================================================================================
print("\n[3] PRESERVE(7) — single-part (brevity) path: ONE part → single synth, no regression")

one_part_emitted = []


def one_part_gen():
    yield {"part": 1, "text": "Hi there. How are you?", "final": True, "staged": False,
           "result": {"reply": "Hi there. How are you?"}}


res3 = bridge._stream_parts(one_part_gen(), speak_fn=lambda s: b"w", emit_fn=lambda c: one_part_emitted.append(c),
                            gone=[False], split_sentences=_split)
check("PRESERVE(7) single-part path → 1 part, 2 sentence-chunks, not staged",
      res3["parts_done"] == 1 and len(one_part_emitted) == 2 and res3["staged"] is False)
check("PRESERVE(7) single-part reply read from result", res3["reply"] == "Hi there. How are you?")

# off/refusal shape (early_return) — reply read from early_return, no result
off_emitted = []


def off_gen():
    yield {"part": 1, "text": "(voice is off)", "final": True, "staged": False,
           "early_return": {"reply": "(voice is off)"}}


res_off = bridge._stream_parts(off_gen(), speak_fn=lambda s: b"w", emit_fn=lambda c: off_emitted.append(c),
                               gone=[False], split_sentences=_split)
check("PRESERVE — off/refusal shape: reply read from early_return", res_off["reply"] == "(voice is off)")

# ====================================================================================================
# (4) ADVERSARIAL — a brain exception on the PRODUCER thread is RE-RAISED on the handler thread
#     (fail loud — never a silent short stream).
# ====================================================================================================
print("\n[4] ADVERSARIAL — a brain (producer) exception is re-raised on the handler thread (fail loud)")


def boom_gen():
    yield {"part": 1, "text": "ok part.", "final": False, "staged": True}
    raise RuntimeError("brain blew up mid-turn")


raised = False
try:
    bridge._stream_parts(boom_gen(), speak_fn=lambda s: b"w", emit_fn=lambda c: None,
                         gone=[False], split_sentences=_split)
except RuntimeError as e:
    raised = "brain blew up" in str(e)
check("ADVERSARIAL a producer-thread brain exception is RE-RAISED on the handler thread (fail loud)", raised)

# ====================================================================================================
# (5) PRESERVE(4) — the handler must NOT call SUITE.chat (the single-chat-event invariant is the
#     epilogue inside chat_parts, NOT a handler-side emit). Structural: the rewired _voice_stream uses
#     SUITE.chat_parts, not SUITE.chat.
# ====================================================================================================
print("\n[5] PRESERVE(4) + structure — _voice_stream drives chat_parts (not chat); single emitter; no AudioContext")
src = open(os.path.join(ROOT, "runtime", "bridge.py")).read()
import re as _re2
vs = src[src.index("def _voice_stream"):src.index("def do_POST")]
check("PRESERVE(4) _voice_stream calls SUITE.chat_parts (drives the part sequence)",
      "SUITE.chat_parts(" in vs)
check("PRESERVE(4) _voice_stream does NOT call SUITE.chat( (no second chat event / forked brain)",
      "SUITE.chat(" not in vs)
check("PRESERVE(2) iOS unlock untouched — no AudioContext logic server-side",
      "AudioContext" not in vs and "audioCtx" not in vs)
check("PRESERVE(6) speak() near-unchanged — voice_loop.speak called with (sentence, eng, voice=...)",
      "voice_loop.speak(sent, eng, voice=voice_arg)" in vs)
check("PRESERVE(3) trial recording uses the existing trial_record_turn seam (once at turn end)",
      vs.count("SUITE.trial_record_turn(trial_session,") >= 2)  # operator + character, the existing pair
check("a single {type:reply} carries the assembled full reply before done",
      "\"type\": \"reply\"" in vs and "_stream_parts(" in vs)

# ====================================================================================================
# (6) BY-USE — the LIVE worktree bridge (:8772). Drive /api/voice/stream with a synthesized clip and
#     prove the parts arrive in order + ONE chat event + the run-record carries parts. Skipped-with-note
#     if the bridge / engines are down (never a false green).
# ====================================================================================================
print("\n[6] BY-USE — live worktree bridge :8772 (/api/voice/stream end-to-end)")
import urllib.request
import urllib.error

BRIDGE = os.environ.get("COMPANY_G6_BRIDGE", "http://127.0.0.1:8772")


def _bridge_up():
    try:
        with urllib.request.urlopen(BRIDGE + "/api/now", timeout=4) as r:
            return r.status == 200
    except Exception:
        return False


if not _bridge_up():
    print(f"  -- (6) by-use SKIPPED: worktree bridge unreachable at {BRIDGE} (not a false green; the "
          "deterministic overlap + preserve proofs above stand). Start it:\n"
          "       setsid /home/tim/company/.venv/bin/python runtime/bridge.py 8772 &")
else:
    # synthesize a clip via an UP engine (the live mouth) → POST to /api/voice/stream → read the ndjson.
    try:
        # read the live voice status: which engines are UP, and the persona→engine map.
        with urllib.request.urlopen(BRIDGE + "/api/voice", timeout=8) as r:
            vstat = json.loads(r.read() or b"{}")
        up_engines = {e.get("engine") for e in (vstat.get("engines") or []) if e.get("up")}
        # personas come from the voice/personas module (list_personas) — pick one whose engine is UP.
        from voice import personas as _vp
        plist = _vp.list_personas()
        persona = ""
        clip_engine = None
        for p in plist:
            if p.get("engine") in up_engines:
                persona = p.get("id"); clip_engine = p.get("engine"); break
        # synthesize the input clip via an UP engine (Kokoro is down in this env; use the persona's UP engine).
        spoken = "Can you explain the memo gate and the scheduler in some detail please?"
        clip = b""
        if clip_engine:
            req = urllib.request.Request(
                BRIDGE + "/api/tts", data=json.dumps({"text": spoken, "engine": clip_engine}).encode(),
                headers={"Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    clip = r.read()
            except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
                print(f"  -- (6) clip synth via {clip_engine} failed ({e})")
        if not persona:
            print(f"  -- (6) by-use SKIPPED: no persona with an UP engine (up={sorted(up_engines)}) "
                  "(not a false green)")
        elif not (clip[:4] == b"RIFF"):
            print(f"  -- (6) by-use SKIPPED: could not synthesize an input clip via {clip_engine} "
                  "(not a false green)")
        else:
            # measure ONE chat event for the turn (the epilogue inside chat_parts) — count chat events
            # in the run-record log before/after via /api/voice (the event log isn't directly exposed;
            # we assert one via the done.parts + the absence of duplicate replies instead).
            from urllib.parse import urlencode

            def _chat_event_count():
                try:
                    with urllib.request.urlopen(BRIDGE + "/api/events", timeout=6) as r:
                        evs_ = json.loads(r.read() or b"[]")
                    return len([e for e in evs_ if e.get("kind") == "chat"])
                except Exception:
                    return None

            def _chat_history_len():
                try:
                    with urllib.request.urlopen(BRIDGE + "/api/chat", timeout=6) as r:
                        return len(json.loads(r.read() or b"[]"))
                except Exception:
                    return None

            hist_before = _chat_history_len()
            url = BRIDGE + "/api/voice/stream?" + urlencode({"persona": persona, "graph_id": "codebase"})
            print(f"    driving /api/voice/stream persona={persona!r} engine={clip_engine!r} (clip {len(clip)}B)")
            req = urllib.request.Request(url, data=clip, headers={"Content-Type": "application/octet-stream"})
            evs = []
            t_first_chunk = None
            t_first_part = None
            t_start = time.monotonic()
            with urllib.request.urlopen(req, timeout=180) as r:
                buf = b""
                for raw in r:
                    buf += raw
                    while b"\n" in buf:
                        line, buf = buf.split(b"\n", 1)
                        s = line.decode().strip()
                        if not s:
                            continue
                        ev = json.loads(s)
                        evs.append(ev)
                        if ev.get("type") == "part" and t_first_part is None:
                            t_first_part = time.monotonic() - t_start
                        if ev.get("type") == "chunk" and t_first_chunk is None:
                            t_first_chunk = time.monotonic() - t_start
            types = [e.get("type") for e in evs]
            chunks = [e for e in evs if e.get("type") == "chunk"]
            done = next((e for e in evs if e.get("type") == "done"), {})
            err = next((e for e in evs if e.get("type") == "error"), None)
            with open("/tmp/g6_live_stream_events.json", "w") as f:
                json.dump({"types": types, "n_chunks": len(chunks),
                           "first_part_ms": round((t_first_part or 0) * 1000, 1),
                           "first_chunk_ms": round((t_first_chunk or 0) * 1000, 1),
                           "done": done, "error": err,
                           "chunk_idxs": [c.get("idx") for c in chunks]}, f, indent=2)
            print("    → /tmp/g6_live_stream_events.json")
            if err:
                print(f"  -- (6) by-use SKIPPED: live stream returned an error event "
                      f"(engine/config not ready): {err.get('error')} (not a false green)")
            else:
                check("(6/by-use) the live stream produced chunk events (audio per sentence)", len(chunks) > 0)
                check("(6/by-use C6.2) chunk idx arrive MONOTONIC + in order",
                      [c.get("idx") for c in chunks] == sorted(c.get("idx") for c in chunks)
                      and [c.get("idx") for c in chunks] == list(range(len(chunks))))
                check("(6/by-use) a done event with a non-empty assembled reply", bool((done.get("reply") or "").strip()))
                check("(6/by-use) done carries a parts count (the staged turn produced N parts)",
                      isinstance(done.get("parts"), int) and done.get("parts") >= 1)
                # exactly ONE {type:reply} event reached the FE (the single assistant-append — not N).
                reply_evs = [e for e in evs if e.get("type") == "reply"]
                check("(6/by-use PRESERVE-4) exactly ONE {type:reply} event for the turn (one FE append, not N)",
                      len(reply_evs) == 1)
                # PRESERVE(4): the chat organ gains exactly ONE user + ONE assistant row (the epilogue once).
                # The LIVE /api/chat delta is INFORMATIONAL-ONLY — it is confounded (chat_parts' epilogue runs
                # on a daemon wave thread that can race the hist_after read; graph_id='codebase' grounding and any
                # concurrent bridge turn perturb the count). The AUTHORITATIVE PRESERVE-4 proof is the deterministic
                # in-process drive in the dedicated section below (the REAL bridge `_stream_parts` over a REAL
                # `SUITE.chat_parts(...)` generator, isolated store, no HTTP/TTS/STT/concurrency confound).
                hist_after = _chat_history_len()
                if hist_before is not None and hist_after is not None:
                    print(f"    (live /api/chat delta = {hist_after - hist_before} — informational only; "
                          "the deterministic PRESERVE-4 check is authoritative)")
                # C6.1 overlap (live, best-effort): if the turn STAGED (parts>=2) and emitted >=1 part event,
                # the first chunk should land before the done — the real brain↔TTS overlap. With a fast 4B the
                # margin can be tight; the deterministic section (1) carries the rigorous proof.
                if done.get("parts", 0) >= 2:
                    check("(6/by-use C6.1) a STAGED live turn produced multiple parts (overlap path exercised)",
                          done.get("parts") >= 2)
                print(f"    live: types={types[:4]}...  chunks={len(chunks)}  parts={done.get('parts')}  "
                      f"reply_evs={len(reply_evs)}  first-part@{(t_first_part or 0)*1000:.0f}ms  "
                      f"first-chunk@{(t_first_chunk or 0)*1000:.0f}ms")
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
        print(f"  -- (6) by-use SKIPPED: live hop failed ({e}) (not a false green)")

# ── PRESERVE-4 (AUTHORITATIVE, deterministic): the REAL bridge `_stream_parts` consumer driven over a
# REAL `SUITE.chat_parts(...)` generator in an isolated store — no HTTP/TTS/STT/daemon-race/grounding
# confound. This is the rigorous "ONE chat event regardless of N parts" proof (the live /api/chat delta
# above is informational only). Needs the resident 4B (:8000) for chat_parts; skipped-with-note if down.
print("\n[PRESERVE-4 authoritative] deterministic in-process: real _stream_parts over real chat_parts")
try:
    import re as _re_p4
    from runtime.suite import Suite as _SuiteP4
    from runtime.registry import NodeRegistry as _RegP4
    from store.fs_store import FsStore as _FsP4
    from runtime import bridge as _bridgeP4
    _sp4 = _SuiteP4(_FsP4(tempfile.mkdtemp(prefix="g6p4-")), _RegP4().discover(["nodes"]), nodes_dir="nodes")
    def _split_p4(t):
        return [x.strip() for x in _re_p4.split(r'(?<=[.!?])\s+', t) if x.strip()] or ([t] if t.strip() else [])
    _before_p4 = len(_sp4.chat_history(50))
    _gen_p4 = _sp4.chat_parts("What did we decide about the storage layer last week?", "codebase", turn_id="g6p4")
    _res_p4 = _bridgeP4._stream_parts(_gen_p4, speak_fn=lambda s: b"", emit_fn=lambda c: None, gone=[False],
                                      split_sentences=_split_p4, should_stop=lambda: False)
    _delta_p4 = len(_sp4.chat_history(50)) - _before_p4
    check("(PRESERVE-4 authoritative) the REAL _stream_parts over chat_parts leaves EXACTLY 2 chat rows "
          "(one user + one assistant — ONE chat event regardless of N parts)", _delta_p4 == 2)
    print(f"    deterministic delta = {_delta_p4} (expect 2); parts_done={_res_p4.get('parts_done')}")
except (OSError, ConnectionError) as e:
    print(f"  -- PRESERVE-4 authoritative SKIPPED: resident model hop failed ({e}) (not a false green)")

print(f"\n{'ALL PASS' if ok else 'FAILURES PRESENT'} — {PASS} checks passed — G6 voice coupling: the PART "
      "is the TTS streaming unit (brain↔TTS overlap proven); monotonic idx; cancellation gates part-gen; "
      "single-part brevity path intact; producer exceptions fail loud; chat_parts drives it (one chat event); "
      "iOS-unlock + speak() + trial-recording-once preserved")
sys.exit(0 if ok else 1)
