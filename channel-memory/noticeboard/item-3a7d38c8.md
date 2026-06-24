---
id: item-3a7d38c8
address: board://item-3a7d38c8
type: block
source: claude_code
state: current
title: P4 · 3. The voice loop, end-to-end, grounded in this system
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-60542ab3
created: '2026-06-24T01:32:21.249839+00:00'
updated: '2026-06-24T01:32:21.249839+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T01:32:21.249839+00:00'
  note: filed
---

## 3. The voice loop, end-to-end, grounded in this system

Walk the whole pipeline he described (select → comment → batch → submit → read replies → choose) as a voice circuit, and note where touch is mandatory.

| Step | Voice-first path | Touch role |
|---|---|---|
| **Enter annotation** | Wake the composer by voice ("comment on this") OR long-press anchor | Long-press = the eyes-free anchor |
| **Pick target + scale** | Anchor by tap/press, then *say the scale* ("the whole section") | Thumb-walk = fallback scale picker |
| **Author comment** | **Dictate** the comment; live transcript shows on screen | Keyboard = correction fallback |
| **Set intent** (BD-D) | Say it inline: *"change request —", "question —", "idea —"* parsed off the front | Tap an intent chip |
| **Attach** (BD-H) | *"attach a screenshot" / "record a voice note"* | Tap the paperclip |
| **Batch** (BD-F) | *"add another" / nothing — it just queues* | — |
| **Submit all** (BD-F) | *"send all" / "send this one now"* | The icon button he asked for in MSG2 |
| **Hear replies** (BD-F/G) | **Read replies aloud (TTS)**; he listens, eyes free | Open the inbox in the V-overlay |
| **Make a choice** (BD-F) | Member poses options; he *says the option* ("the second one" / says its label) | Tap the option |

Two things this surfaces that the touch brief does **not** scope:

**(a) Replies must be speakable back to him, not just readable.** He prefers voice *in*; he'll want voice *out*. A reply or a member's decision-question (BD-E "structured question / option set") should be **readable aloud on demand** — tap-and-hold the V, "read me the new replies" — so he can triage correspondence while one-handed and not staring. This is a whole output channel (TTS over the reply thread) that no other lens will raise. It's also the accessibility win: it makes the system usable while walking, eyes-occupied, or with visual fatigue.

**(b) Choices are the cleanest voice win in the system.** When a Claude-Code member surfaces an options set, *speaking the choice* ("approve", "option two", "the green one") is faster and lower-effort than any tap, and it's unambiguous because the option set is closed and known — so the recognizer can be **constrained to the option labels** (a grammar, not free dictation), which makes it near-error-free. **Constrained-vocabulary voice should be used everywhere the command set is closed** (mode switch, level words, submit, choices); free dictation reserved only for actual comment prose. This is the core VUI reliability principle: closed grammars don't mis-hear.

---
