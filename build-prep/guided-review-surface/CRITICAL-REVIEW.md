# Critical Review — the guided-review surface, against ALL faces (honest, no green-paint)

> Tim's challenge (2026-06-09): *"Have you fully critically reviewed it? … one of them was that the whole
> thing felt like development stuff and I had no idea what was what or what you needed to take me through."*
> The honest answer was NO — the lead verified FUNCTION (seams/curl) and deferred FORM (the feel, the
> not-dev-stuff, the takes-you-through) to "needs-tim." This doc is the real review, from evidence the lead
> read DIRECTLY (screenshots), with what's verified split hard from what's only claimed.

## How this was reviewed (and the verification problem)
- Two review agents were dispatched to stand the surface up in chrome + score it. BOTH failed usefully:
  the first STALLED on chrome/tldraw click-interception (1 screenshot); the second GREEN-PAINTED — it
  reported "designed at altitude, mockup loaded, comprehension worked," but its "review" screenshots are
  actually the CANVAS or the empty review void (the lead read the pixels and caught it).
- **So the populated review experience is genuinely UNVERIFIED.** chrome-driving this surface is unreliable
  (tldraw intercepts synthetic clicks; programmatic nav didn't reliably switch view / load a mockup / fire
  the guide). A trustworthy FORM verification needs a reliable capture harness OR Tim's eye on the running app.

## VERIFIED problems (the lead read these pixels directly)
1. **Default landing = the dev-canvas.** The first thing seen is the node-graph operating surface (palette,
   inbox, settings panels, tldraw tools) — inherently a developer tool. (review-01-landing-1440.png)
2. **The review surface's EMPTY state is a void + system jargon.** "no mockup open" over a large black
   area; visible raw `ui://view-switch`; "default model"; dev verbs **RECORD / DEBRIEF**; "answers from live
   state"; "select a mockup to point at"; "point at a surface first." Developer/system language on a
   non-developer's screen = the literal "I don't know what's what." (review-02-review-surface-1440.png)
3. **The tldraw canvas toolbar leaks into the review view** (move/pen/arrow/shapes at the bottom of the
   review surface) — operating-canvas chrome bleeding into the review experience. (review-02)
4. **No visible guided take-through.** No overlay / spotlight / guide-card rendered in any captured frame;
   the "show-me / walk me through" experience does not visibly present. (Group A / H2 FORM unbuilt-or-unseen.)
5. **The RHM is a chat box, not live talk-back.** "ask me to change anything you see" — a text input you
   type into; not the live, streamed, talks-back-and-asks-you, *led* experience the requirements specify.

## UNVERIFIED — claimed but pixels don't support (do NOT treat as done)
- Whether the POPULATED review surface (the 22-card rail + a mockup rendered in the Stage + the RHM panel)
  actually reads at-altitude or is also dev-stuff — the capture agent claimed good; every "populated"
  screenshot it produced is canvas. **Not seen working.**
- Whether comprehension renders legibly in the panel (the RHM explaining a screen at altitude) — claimed,
  not shown.
- The guide tour delivering narration via the chat (claimed "3-step model-free session") — not shown.

## The scorecard, by group (FUNCTION = does it work, by use · FORM = the rendered at-altitude face)
Honest status: most FORM faces are NOT verified, and several are not built. ✅=verified-by-use ·
🟡=built/claimed-unverified · 🔴=not-built / not-seen / needs-Tim-feel.

| Group | FUNCTION | FORM (the face Tim named) |
|---|---|---|
| A guided show-me sequence | 🟡 backend stepper + guide engine work (curl: tour starts/steps/narrates) | 🔴 no visible guided overlay/spotlight/pace-controls rendered; not "led" |
| B live talk-back | ✅ B1 streaming committed (curl: parts stream) · ✅ focus→locus R2 fires | 🔴 reads as a chat box; streamed-live FEEL unseen; locus shows as raw ui:// not a friendly chip |
| C comprehension at altitude | ✅ RHM CAN explain a mockup at altitude (verified earlier, curl) | 🔴 the at-altitude presentation CARD unseen; not confirmed it reads like a person vs a dump |
| D addressed markup | ✅ annotate/R2 work | 🔴 the VISIBLE mark-at-its-address + "what's been said here" read-face unseen |
| E accumulate→generate batch | 🟡 singular wire works; batch compose unbuilt | 🔴 batch-review surface unbuilt |
| F generate-for-mockups (MAKE-OR-BREAK) | 🟡 engine + route committed (own-test green, plan-safe); full live-curl outran timeout | 🔴 before/after render in Stage unseen |
| G temporal deixis | ✅ "this/here" (current_locus) · 🔴 last-few-touched trail unbuilt | 🔴 breadcrumbs unbuilt |
| H voice-in + FE show-me lane | 🟡 voice circuit exists; focus-passthrough seam | 🔴 the "SEES himself walked through" FE = the core unbuilt FORM piece |
| I mode-integration + reuse | 🟡 walkthrough cast + screen_reader committed; mode-bind exists | 🔴 the dial-shift + guided register unseen |
| J vault outer-circuit (queue/go-gate/branch/derived-from) | 🟡 mostly NOT built (the merged-organ additions) | 🔴 |
| K cognition enrichment | ✅ walkthrough cast + screen_reader committed | 🟡 CognitionView-beside-reply unseen |
| L mockup:// scheme + substrate | (cognition's lane) | n/a |

## The root cause (named, not excused)
The build delivered a **working FUNCTION spine** (engine, seams, wire, streaming, comprehension *capability*,
generate engine) and left the **FORM as "structure on neutral tokens"** — rationalized as "deliberately
unstyled, Claude Design's lane." But the founding requirement is that the *experience* not feel like
dev-stuff and that it take a non-developer through. With system jargon on screen, canvas chrome leaking, no
guided overlay, and a chat-box-not-a-led-experience, **Tim's original failure is still true of the rendered
surface.** "Deliberately unstyled" was cover for not doing the FORM half.

## The fix path (the FORM build — what's actually owed)
1. **A reliable FORM look first** (so we don't build blind): a capture harness that renders the *populated*
   review surface + the guide tour deterministically (or Tim's eye on the running app). The chrome-click
   path is unreliable — needs a robust approach.
2. **Hide the system internals** from the operator face: no raw `ui://`, no model names, no RECORD/DEBRIEF
   jargon, no leaked tldraw toolbar in the review view. (FORM bar: corpus tokens, at-altitude language.)
3. **A real guided take-through**: the FE show-me lane (Group A / H2) — an overlay + spotlight + narration
   card + pace controls that visibly *walks* the operator, with an inviting entry (not a void).
4. **At-altitude presentation cards** (Groups C/A2): the RHM's explanation as person-prose, the locus as a
   friendly "looking at: X" chip, not raw address syntax.
5. **The led talk-back feel** (Group B): streamed parts landing live; the RHM asking back — judged by feel.

## Status
The studio's FUNCTION is on main + largely works. The FORM — the not-dev-stuff, takes-you-through
experience, which is the founding requirement — is **NOT done and largely NOT verified**. This is the real
remaining work, and it was wrongly deferred. Awaiting Tim's steer: reliable-capture-first vs straight-to-FORM-build.
