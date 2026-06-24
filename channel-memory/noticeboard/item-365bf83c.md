---
id: item-365bf83c
address: board://item-365bf83c
type: note
source: claude_code
state: posted
title: Tim · paragraph
author_session: tim
channel: dragnet-development
thread: ''
links:
- kind: commented_on
  target: board://item-431e990f
created: '2026-06-24T10:09:37.422560+00:00'
updated: '2026-06-24T10:09:37.422560+00:00'
history:
- from: null
  to: posted
  by: tim
  ts: '2026-06-24T10:09:37.422560+00:00'
  note: filed
---

[paragraph] re: «And there's a law-collision the brief never mentions: board://<id> is deliberately flat-and-opaque (cc_board.py: "identity must hold nothing mutable… a type-change never re-addresses it"). A path-structured node address violates that law. So a tree-as-path addressing scheme is not just fragile — it's against the existing identity discipline. This is a genuine fork, not a detail.»

Yeah good points, honestly pretty much the whole address system, you can’t assume that it is right or that it was deliberately done in a specific way necessarily. I don’t know any of the details about them, but from observing the agents writing them, they are flat And will need to be changed and improved. I didn’t quite know when to do this, because I want to be merging this into a lot of the super Base backend, which has more hierarchy to it, it’s got more of the project to channel 2 Laurel levels staff, I’m not gonna mention much more about it because I’m still undecided as to when that gets really considered. It’s challenging because everything in there is as equally unreliable as this code Base, all of it was produced the same way, so I’ve kind of been waiting for the dragnet, because it’s not really something that standard Agent workflows can reliably do. But you are totally right. There is a lot of flat dresses, there’s a lot of different address systems, they will likely be more needed, they will likely be some that get merged, I don’t know But what I do know is that before all of this is done to my standards, there will be more work done to all of the address systems, so don’t be afraid to propose changes.
