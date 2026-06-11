---
type: contract-journey
journey: message-and-read-reply
summary: Ask another session a question and actually obtain its answer — the canonical cross-resource flow, carrying the history-vs-live-vs-messages disambiguation.
status: building
relates-to: ["[[session]]", "[[session-message]]", "[[events]]", "[[transcript]]"]
---

# Journey: message and read the reply

**The one flow that touches every F1 resource: find the target, post the question, prove the
consequence on the event stream, read the answer from the mailbox thread.**

## The disambiguation this journey owns (V19's ambiguity class)
Three things look like "what a session said", and they are NOT interchangeable:
- **[[transcript]] is HISTORY** — the filtered past of a session, for recall/search.
- **[[session#op: session.watch]] / [[events#op: events.watch]] are LIVE** — what is
  happening right now (one session's frames / the fabric's facts).
- **[[session-message]] is ADDRESSED COMMUNICATION** — messages and replies are durable mail,
  not turns and not transcripts; a reply exists only because something was posted.

## Ordered ops
1. **[[session#op: session.list]]** — find the target. Match on id; titles are honest but
   76.7% are envelope-fallbacks, and 72.5% of catalog rows are `summarizer` machine sessions
   (filter them for any real-conversation view).
2. **[[fabric-config#op: fabric-config.get]]** — only if fanning: read the cap, never assume 3.
3. **[[session#op: session.post]]** — post with `verb=auto` unless you have a reason;
   `from_session=session://<YOUR id>`. Keep the response's `thread` and `seq`.
4. **[[events#op: events.list]]** — prove the route happened: events after your post whose
   `intent_id` equals your `posted` id (deliver/wake/consult branches declare their expected
   kinds on the op). `verb: queue` resolutions expect NO events — their evidence is the
   waiting intent on [[session-message#op: session-message.list]] (`verb=queue`).
5. **[[session-message#op: session-message.list]]** — read the answer:
   `session=<your from_session>, thread=<thread>, since=<seq>`. Replies carry `verb: reply`
   (or `verb: error` — the supervisor's teaching refusal, equally an answer). A consult fan
   yields one reply per fork, all on the one thread.

## Pass shape
The journey PASSES when step 5 returns ≥1 thread-joined reply whose body answers the posted
message (or a teaching error naming a legal recovery you then took — pass-via-refusal).
Steps 4 and 5 together are the proof; step 3's response alone never is.
