---
id: item-1f68e3fa
address: board://item-1f68e3fa
type: note
source: claude_code
state: posted
title: Tim · point
author_session: tim
channel: dragnet-development
thread: ''
links:
- kind: commented_on
  target: board://item-d5691851
created: '2026-06-24T07:57:29.552308+00:00'
updated: '2026-06-24T07:57:29.552308+00:00'
history:
- from: null
  to: posted
  by: tim
  ts: '2026-06-24T07:57:29.552308+00:00'
  note: filed
---

[point] re: «MSG2: "hamburger in the top-left, document switcher on the title." Top-left is the worst thumb target on the phone — the literal hardest pixel to reach one-handed (for a right-handed grip). His own "save to home screen, one-handed, non-obtrusive" goals fight his "hamburger top-left" instinct. I'd flag this honestly: either move document-switching into the V/bottom zone, or accept that the top bar is a "two-handed / deliberate" action (which is fine for switching documents — a rare, deliberate act — but would be wrong for anything frequent). The principle: frequency determines altitude. Frequent → bottom/thumb. Rare/deliberate → top is acceptable. Document-switch is rare, so top-left is tolerable there specifically — but the comment/submit/mode actions must never live up top.»

Okay? I really liked this, very good point. Well reason And better than my suggestion. I think they are right, the hamburger maybe Bettar in the thumb zone maybe something like Settings or other infrequently used things could go on the top corners, or nothing goes to top coins. That’s actually a really good point, maybe nothing should go in the top other than informational stuff, like titles or whatever stuff helps to frame or contextualise the experience you’re about to have. I’m sure eventually I’ll think of things that could go out of the thumb zone, but those would be things like links or switches to Sibling applications, not something that you would use in any extended session. I am also realising that I don’t want to have a bottom bar either, because stuff all the way on the left is a pain to get to and a lot of the stuff on the right is just wasted space. I see so many applications that just have a bar at the bottom of the top, but that doesn’t feel easy or intuitive in use, so I think maybe something unconventional here, I’m an inventor and we’re building all of this for me so why not? So maybe the V is in the bottom right or something and maybe it has something Above it and to its left, making like a back to front L shape or something. But the thing is stacked, they would probably be small than the V, And. I feel like aiming for not more than two on either side. As to what those are, I don’t expressly know, but probably two of them would be frequent actions and the other two would be menus or something. And that component, the thing that goes in the bottom right that holds the V and the other four, Which would all be the same component and use the iconography that I was describing earlier, that would be a reusable component or template too. So changing what goes in those slots should be something really should just be able to drop something else in. If all of the other four slots Are the same component as the V then they’re already self-contained anyway. I don’t know how much you remember about all the work from the last few days but the composition stream, that’s where a lot of the Architecture for that was discussed, which also has its backend  in supabase. Honestly, if it is built right, and by right I mean to my principles, we could do anything and be able to experiment, like two of the slots could be dynamic ones, that change depending on whatever the context is. We don’t need to do that upfront because I can’t currently think of things for That but The client application which is blocks, versus a different application which might be a gruff view or a grass builder or something I don’t know. Actually, we are building in modes, which should be a registry by the way, and we’ve identified two modes for this, so potentially, only if there is a use for it, two slots could be dynamic in switch depending on that you’re in. Again we don’t necessarily need to build that right away but like I am with pretty much all these comments and planting seeds, and you told me that these are assisted onto the boards in the channel, And I am assuming that they are typed to me, and so would be available in filterable and whatever in the future. If this is not the case, if it doesn’t get persisted if it’s not attached or whatever, that’s gotta be fixed because that’s why I’m putting in so much effort.
