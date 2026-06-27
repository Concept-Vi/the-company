---
type: exchange
sequence: 08
title: "The Modes message"
date: 2026-05-27
session: 12c59b4e
verbatim: true
note: "Tim's message reproduced as dictated (TTS); errors preserved. [bracketed] text = my correction for readability."
produced:
  - "[[TIM]] — Layer 4 (modes primitive); open-future mode locked"
  - "[[vi-modes-design-decision]]"
tags: [foundation, primary-source, modes]
---

# 08 — The Modes message

> [!info] Primary source — verbatim
> Tim's message below is reproduced **verbatim** from session `12c59b4e` (2026-05-27). It was dictated via text-to-speech, so spelling/grammar artefacts are part of the original. Any `[bracketed]` text is a correction added for readability — the signal that it was changed. The unbracketed words are exactly as Tim typed them.

## Tim's message (verbatim)

i l iked that term - open future mode, worth putting that somewhere it's a mode I'd use a bit - I like the ieda of modes too, more broadly. Wish I couldv'e done that with staff, just switched them to the mode they eneded rather than have to guide them into it

## My response (verbatim)

**"Open-future mode" — locked in as canonical vocabulary.** Removing the "provisional" tag. The other candidates I'd offered (seed-tree, tributary, iceberg, etc.) retire; this is the name from here forward.

## Modes as a Company primitive — bigger than this one instance

What you gestured at is bigger than a single mode for writing. You're pointing at **modes as a general architectural primitive** for the Company. The wish — *switch the entity to the mode it needs without guiding it there* — is the friction-elimination version of all those years of having to teach staff how to operate in each new context.

You already use modes in Vi (per the memory layer: ~19 activity-states, auto-detected, extensible to context injection). That's the **same relational primitive** working at a different layer. The Universal Composition pattern at work — identify the primitive once, reuse everywhere. Modes in Vi for activity-states; modes in the Company for how the entity operates.

## What I'd bring to the modes thinking

Sharing these as insights, not as architecture (per your "don't design this now"):

**The switching-cost asymmetry.** Switching modes is expensive for humans — cognitive overhead, identity readjustment, time to settle into a new style. For an AI entity, mode-switching is near-instant. That's an *AI-affordance* — something AI can do that humans literally cannot. The Company should lean into this hard. Your old staff needed days to genuinely shift modes; the Company can shift mid-message.

**Modes are not roles or departments.** A specialist's *who-you-are* (Finance, Strategy, Engineering) is a department. *How-you-operate* (research, build, triage, brief, open-future, dense-expansion, terse-status) is a mode. The same specialist can be in any mode. Keeping these conceptually distinct matters because confusing them produces brittle designs.

**Modes stack.** Open-future mode is a base layer for *writing*. Within it, you might have sub-modes — drafting, synthesising, archiving, briefing. The base mode persists; sub-modes overlay. This becomes important if you ever want to combine modes ("brief in open-future style" rather than "brief mode XOR open-future mode").

**Mode entry has two triggers.** Manual command from the Commander ("switch to X") and inferred from context (the entity detects the situation and shifts). Vi uses auto-detection; the Company likely wants both. Manual lets you override; auto-detection lets the entity carry the cognitive load of switching without you having to think about it.

**Mode discovery is a Company capability.** You should be able to ask "what modes exist?" or "what mode would you recommend for X?" without remembering the list. The Company should introspect its own modes and surface them on request.

**Defining new modes is itself a Company task.** When a pattern crystallises (like *open-future* did, from this exchange), it becomes a mode worth naming and locking. The Company should be able to *propose* new modes when it notices recurring distinct ways of operating that don't have names yet.

## What's worth recording now

Going to add:
- **Open-future mode** locked into vocabulary, marked canonical.
- **Modes as a Company primitive** — added as a gestured-at-not-yet-designed thread under Layer 4. Connects to Vi modes via Universal Composition.
- The friction-elimination framing: *the Company should be switchable, not guideable.*

Not designing the mode mechanism itself yet — you said "we'll figure that out at some point." This stays open.

Locked. *Open-future mode* is canonical; modes-as-primitive is recorded under Layer 4 as gestured-at-not-yet-designed; the connection to Vi modes is noted; primary source captured.

**Open at this response:** modes' actual mechanism (entry/exit, stacking, discovery, definition) is not designed; the candidate-modes list I sketched (triage, research, build, brief, dense-expansion, terse-status, exploratory, critical, archive) is *examples; more exist*; the relationship between Company modes and Vi modes is recognised but not mapped — they're the same primitive at different layers, but how they coordinate is open.

## What this produced

- [[TIM]] — Layer 4 (modes primitive); open-future mode locked
- [[vi-modes-design-decision]]

## Source
- Session transcript: `12c59b4e-fc9d-4d3e-beec-1948eedc23dd.jsonl`
- Part of the [[_exchanges-index|foundational exchanges archive]]
