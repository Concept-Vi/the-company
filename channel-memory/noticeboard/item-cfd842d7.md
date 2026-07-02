---
id: item-cfd842d7
address: board://item-cfd842d7
type: note
source: claude_code
state: posted
scope: channel://dragnet-development
author: operator://tim
title: Tim · point
author_session: tim
channel: dragnet-development
thread: ''
links:
- kind: commented_on
  target: board://item-bd30758f
created: '2026-06-24T05:21:29.316913+00:00'
updated: '2026-06-24T05:21:29.316913+00:00'
history:
- from: null
  to: posted
  by: tim
  ts: '2026-06-24T05:21:29.316913+00:00'
  note: filed
---

[point] re: «Typed edge = "relation." There's a registry of relationship-types, each with a direction and an inverse (this→that, and the reverse). The board already links things across all those address-types with typed edges (authored_by, references, commented_on, reply_to, …), and there's a function that follows a thing's typed links outward and resolves whatever they point at — that's traversal, and it already exists in a first form.»

Yes - there’s kinda two forms of typed edges though which I haven’t really worked out or specifically defined. There’s the directional ones for each level of the type registry system (the bidirectional ones, with their equal and opposite), then there’s normal relations, for graph uses that have actual relations. They’re seperate, similar of course but they have different rules. The typed edges (the directional ones), those are agnostic, they’re about the structures and registries and stuff. The typed relations (which I’ll use so there’s a distinct handle for edges and relations), that’s more domain or situation specific. I have a lot of different experiments on graph structures, and they all have the same cascade properties as everything else, the four part Cascade of global to project to user to instance, which aren’t necessarily the only names, but that’s what I’ve generally used for terminology. And that cascade works with the registries that govern any particular graph, there is the global and the project And the user and the specific graph, not all of them necessarily need to be populated but they have relations, and those registries combine and cascade together, and may be in different places. Sometimes embedded into the graph itself so that it is portable, and the global may be at the application level, Project may be a projector channel or something, these aren’t hard rules. I’m just trying to explain. So they can be in multiple places and then Cascade together, I don’t have a clear link of this description to the difference between typed edges and type to relations, these are my broad ideas. The same kind of thing applies to the nodes as well, with the cascading registries. And the typed edges in relations, they declare and connect to the node registries that they are in, even if the rules for some of them are that they can apply to every node. It is all rules. Again I don’t have a pre-existing specific structured thing, I’ve done dozens different experiments that are spread throughout heaps of different projects and the dragnet will likely be instrumental in capturing them at some point.
