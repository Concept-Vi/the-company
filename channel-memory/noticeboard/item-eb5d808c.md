---
id: item-eb5d808c
address: board://item-eb5d808c
type: note
source: claude_code
state: posted
scope: channel://dragnet-development
author: operator://tim
title: Tim · section
author_session: tim
channel: dragnet-development
thread: ''
links:
- kind: commented_on
  target: board://item-79c533e9
created: '2026-06-24T08:54:30.415986+00:00'
updated: '2026-06-24T08:54:30.415986+00:00'
history:
- from: null
  to: posted
  by: tim
  ts: '2026-06-24T08:54:30.415986+00:00'
  note: filed
---

[section]

This was a good breakdown, I understood like 80%. I’ve got some ideas, but I started by saying I understood 80% to indicate that it is quite likely I’m wrong or Off, like I don’t know these are just thoughts. And I want pushback and alternative ideas and stuff. I’m not sure if I love that specific redundancy Setup, it’s just a feeling. In the vi visual project I’ve mentioned, blocks had versions. The block system that we’ve talked about, it’s hierarchical, it’s a containment graph that just keeps going up. Everything can be traced back to the same root, which I guess is the user? That part doesn’t matter too much, but the point being every possible block, is contained by its next one up. In that project, it was as you say, the whole point of the application is things change. So they were versions, and those versions I think went to the nearest parent, and if a parent above it then changed, then that would be a nested version, which is still addressable. I have thought of versions as another orthogonal axis, so one block that gets changed then has two versions, and they’re not really two versions of the same block, they are two blocks that relate to each other through a directional edge, supersedes/succeeds and precedes maybe. So a comment that is made on one is attached to that one, and what replace is it might be derivable through those typed edges, and the containment graph or something. so if a parent or something else in the document changes, it should still be derivable because everything is connected. And, elements or blocks or whatever, they aren’t just the positions on the page, they are a node, that node, which has data, so if that changes, that specific data then that is a recognisable event, but if other data changes and not that data then it is the same node, and the node and the position are not the same thing, the address is that node at That position. Again I have no experience in any of these domains so I could be barking mad and using the wrong words and explaining things badly, but in my mind, I’m thinking now of a Directory, a file path is four things. It is the address to that location, it is that specific file name, it is that specific file extension, it is that specific meta data describing the files content. It’s not just one thing, the file path is all of them. If another file in the same Directory changes, that doesn’t change that path, it only changes the order that that file appears in the Directory if that Directory is sorted in a particular order. Again totally discrediting myself, I have no experience so push back an ideas and everything is totally welcome. I could be just totally wrong, I could be saying the same thing, I don’t know.
