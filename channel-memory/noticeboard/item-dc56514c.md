---
id: item-dc56514c
address: board://item-dc56514c
type: note
source: claude_code
state: posted
title: Tim · point
author_session: tim
channel: dragnet-development
thread: ''
links:
- kind: commented_on
  target: board://item-5c2d936d
created: '2026-06-24T08:08:31.685224+00:00'
updated: '2026-06-24T08:08:31.685224+00:00'
history:
- from: null
  to: posted
  by: tim
  ts: '2026-06-24T08:08:31.685224+00:00'
  note: filed
---

[point] re: «PWA full-screen is non-negotiable for the gesture to even work. In a normal Safari tab, the bottom toolbar and the pull-to-refresh / swipe-back edge gestures will eat his thumb gestures near the edges. Installed-to-home-screen standalone PWA (his MSG2 ask) removes the bottom bar AND disables Safari's edge-swipe-back — which is required, not cosmetic, because his V and gesture live exactly where Safari's edge gestures are. The theme-color + display: standalone + apple-mobile-web-app-* meta tags he half-described are the mechanism. Edge-swipe-back conflict is a real, device-only verification item.»

Very good point, it would still have to work in Safari, and I don’t know if there is a way to detect if it is being run in Safari or if it’s saved to Home screen, but if there is then having some message or some notification or something to alert the user That tells them it works better save to home screen and maybe shows them how to do that, I’m happy to provide screenshots, so that it can be very visual and very easy to do. I am the only user right now, but eventually this will likely go to other people so I’m trying to Think of everything together.
