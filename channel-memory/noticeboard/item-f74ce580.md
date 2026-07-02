---
id: item-f74ce580
address: board://item-f74ce580
type: block
source: claude_code
state: current
scope: channel://dragnet-development
author: session://ch-3mpkjg3r
title: P7 · 6. What's missing for a voice-first operator (additions nobody else will
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-60542ab3
created: '2026-06-24T01:32:21.400452+00:00'
updated: '2026-06-24T01:32:21.400452+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T01:32:21.400452+00:00'
  note: filed
---

## 6. What's missing for a voice-first operator (additions nobody else will raise)

1. **Voice note as a first-class comment body, not just an attachment.** Sometimes he won't want even a transcript — he'll want to *leave a 20-second spoken explanation* on a block. Store the audio (blob://, exists) AND auto-transcribe it into the envelope text so the member gets both the words and the *tone/emphasis* (which transcription strips). For a founder explaining nuanced product feedback, the audio carries intent the text loses.
2. **Eyes-free review mode.** A mode where he taps the V and the system reads the document/section aloud and he says "comment here" to drop an anchor at the current read position — annotation while not looking at the screen at all. This is the deepest accessibility/ergonomics play: it removes the screen from the loop entirely for the *capture* phase.
3. **Barge-in / interruptible TTS.** When replies are read aloud, he must be able to cut in and respond mid-read. Standard VUI requirement; easy to forget.
4. **Noisy-environment graceful degradation.** Voice fails in noise. The system must *always* leave the touch path live in parallel (never a modal "now speaking" state that locks out the thumb) and degrade silently to the gesture/keyboard. **Voice and touch are co-equal, simultaneously available channels — never modes you switch between.** This is the central accessibility principle: redundancy, not replacement.
5. **Motor-ergonomic guardrails the touch brief under-weights:** long-press *duration* and thumb-walk *travel* must be tunable per-person (his thumb, his grip) — fixed timings are an accessibility failure. Large tap targets (44pt+) for every chip/icon he asked to "make into an icon button" in MSG2. Reachability: the V and submit live in the bottom thumb arc; nothing load-bearing in the top corners except the hamburger (which is navigation, used rarely).
6. **Confirmation without friction.** He said "don't auto-send." For voice that's doubly important — a mis-heard "send" must not fire a batch. So: spoken "send all" → a *glanceable* confirm (count + one-tap or one-word "confirm"), never silent fire. But a *single* immediate comment (the "send now" he added in MSG2) can be lower-ceremony.

---
