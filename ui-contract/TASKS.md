<!-- generated: INITIAL SKELETON, hand-derived 1:1 from the per-op `tasks:` declarations in
     resources/*.md by the F1 contract lane (2026-06-12). The generator (tools/) is NOT YET
     BUILT — when it lands it overwrites this file in place and hand-edits fail its diff.
     Until then: if a row here disagrees with an op's tasks: block, the OP'S FENCE WINS. -->

# TASKS — intent → (op, params)

Cross-resource tasks: see `journeys/` (currently: [[message-and-read-reply]]).
Statuses ride the ops (CONTRACT-FORMAT §4.2); rows whose op is `planned` say so.

## Find & inspect sessions
| intent / alias | op | params |
|---|---|---|
| list every Claude Code session on this machine | [[session#op: session.list]] | |
| find a session by title or directory | [[session#op: session.list]] | q= / cwd= |
| which sessions are alive right now | [[session#op: session.list]] | state=supervised-live |
| show the fleet · session catalog *(aliases)* | [[session#op: session.list]] | |
| inspect one session in full | [[session#op: session.get]] | |
| is this session alive, and what has it been mailed | [[session#op: session.get]] | |
| describe a session *(alias)* | [[session#op: session.get]] | |

## Spawn & control sessions
| intent / alias | op | params |
|---|---|---|
| spawn a supervised Claude Code session | [[session#op: session.create]] | |
| resume an old session under supervision | [[session#op: session.create]] | resume=<id> |
| fork a session into a sandbox copy | [[session#op: session.create]] | resume=<id>, fork=true |
| launch a session *(alias)* | [[session#op: session.create]] | |
| push a turn directly into a supervised session | [[session#op: session.inject]] | |
| type into a running session *(alias)* | [[session#op: session.inject]] | |
| stop a session's in-flight turn without killing it | [[session#op: session.interrupt]] | |
| cancel a running turn *(alias)* | [[session#op: session.interrupt]] | |
| tear down a supervised session · free a fabric slot | [[session#op: session.stop]] | |
| kill a session *(alias)* | [[session#op: session.stop]] | |

## Message sessions (the routed verbs — parameter-level rows, never buried)
| intent / alias | op | params |
|---|---|---|
| send a message to another session | [[session#op: session.post]] | verb=auto (default) |
| resume a closed session and ask it something | [[session#op: session.post]] | verb=wake |
| ask N forked copies of a session in parallel | [[session#op: session.post]] | verb=consult, copies=N |
| leave a message a running unsupervised session picks up next turn | [[session#op: session.post]] | verb=auto → queue |
| notify a session · fan out a question · consult a session without disturbing it *(aliases)* | [[session#op: session.post]] | |
| read a session's inbox · check my mail *(alias)* | [[session-message#op: session-message.list]] | |
| collect the replies to a question I fanned out · did anyone answer *(alias)* | [[session-message#op: session-message.list]] | thread=<from post> |
| check for queued messages at my turn start | [[session-message#op: session-message.list]] | verb=queue |

## Observe the fabric
| intent / alias | op | params |
|---|---|---|
| what happened in the fabric since my cursor · poll fabric events *(alias)* | [[events#op: events.list]] | since= |
| did my message cause a turn | [[events#op: events.list]] | since=, session= (join intent_id) |
| stream fabric events live · subscribe to the event stream *(alias)* | [[events#op: events.watch]] | |
| watch what a session is doing right now · tail a session *(alias)* | [[session#op: session.watch]] | |

## Memory & configuration
| intent / alias | op | params |
|---|---|---|
| refresh the session-transcript corpus now · turn the exporter on | [[transcript#op: transcript.export]] | |
| export my sessions to markdown *(alias)* | [[transcript#op: transcript.export]] | |
| what did a past session decide about X · search my session history *(alias)* | [[transcript#op: transcript.search]] | **PLANNED** — until live: session.list q= (titles) + direct file reads over ~/corpora/claude-sessions/ |
| find the session that edited a given file · recall a past conversation *(alias)* | [[transcript#op: transcript.search]] | **PLANNED** (same interim paths) |
| what is the fabric's concurrency cap · check the cap before fanning out *(alias)* | [[fabric-config#op: fabric-config.get]] | |
| is the session supervisor up · fabric health *(alias)* | [[fabric-config#op: fabric-config.get]] | |

## Not exposed locally (honest rows — reach for these and you found a recorded boundary)
| intent | status |
|---|---|
| get one mail message by id | NOT EXPOSED — read the thread/inbox ([[session-message#op: session-message.list]] thread=/since=); a by-id get lands with the planned msg:// scheme (§9.7) |
| rename/retitle a session record | NOT EXPOSED — titles are importer-derived (fallback chain); no update op exists yet |
| change the fabric's cap/timeout/permission via an API | NOT EXPOSED BY DESIGN — operator env + service restart; raising the cap is a recorded decision ([[fabric-config#Caller]]) |
| reach the supervisor from off this machine | NOT EXPOSED BY DESIGN — 127.0.0.1 only, no env to widen (exposure law B3) |
