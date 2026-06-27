---
type: exchange
sequence: 15
title: "Coherence, no versioning, no instructions"
date: 2026-05-27
session: 68e14d07
verbatim: true
note: "Tim's message reproduced as dictated (TTS); errors preserved. [bracketed] text = my readability correction. My response preserved verbatim. This exchange is load-bearing for how the Company's record works."
produced:
  - "[[../system/principles|Principles]] — Coherence by integration; No versioning in the doctrine; Understanding not instructions; Guided commitment (clarified)."
  - "[[../system/README]] — the synthesis/source split (CQRS-shaped knowledge architecture)."
tags: [foundation, primary-source, coherence, governance, knowledge-architecture]
---

# 15 — Coherence, no versioning, no instructions

> [!info] Primary source — verbatim
> Reproduced from session `68e14d07` (2026-05-27). This exchange is load-bearing for how the Company's record works under thousands of equal agents with no human review.

## Tim's message (verbatim)

> Yeah. So it is more just that when I give you the dense messages, it's so I can get your response, and then I will choose what to do after that so you don't need to propose to me how you would go and do updates. You just need to give me a good response to the messages I give you, you don't need to spend extra time in saying where to do the structure. I will ask you. And then to your question, if I am asking you, it is kind of closer to a [option (a)] except I would also want you to tell me all of the different places that it relates to. And very often, when you are recording something, it affects, and it touches on other things. So it's not just adding an extra entry to something. It is adding it and then making all of the relevant and appropriate other updates to everything else that's already in there. so that the whole collective body stays cohesive and coherent. Doing it any other way just creates drift and bloat and decreases it's positive influence on future AI that reads it, I also really don't like versioning because very often agents will assume that what they have just done is more important than other things, which is not true, because they are just one agent of thousands of equal agents, And if they do that, then there is just pretty much always regression and loss and disharmony. And that is actually a big and important thing because remember, no human has ever or will ever read or write or review or edit any of these files at all ever. which means whatever gets written. is the concrete record that influences every other agent in the future, and no agent has any idea and any awareness of what that might be, So doing so, creating specifics and instructions or anything like that, that's bad. I know you're not a conventional normal user in scenarios. It's good. But as we've been through, this is not a normal conventional user scenario, and so it is bad. I don't want to drift too far this much. This is an important point, and this is relevant to you and every agent just like you, and it is also very relevant to the system and the company and how it needs to work and be designed as we go through it. So it's worth thinking about this a lot and giving your thoughts on it. And just remember that I don't know everything, I am not egotistical or precious or anything like that. I am actively telling you and telling everyone, but I do not know everything. And so I really want and need encouragement [for] Independent thought and telling me your ideas and correcting me if I'm wrong or pointing things out, pointing out any possible issues and pointing out possible solutions or ways of things that I didn't mention and I don't know about. I have an understanding of the problem and a broad understanding of what would be needed for a solution, but I never know everything and that's what's needed for the company to thrive.

## My response (verbatim)

This is foundational, and you're right to stop me on it. The core, said back in one line: **the record is one coherent body maintained by integration, not an append-log — no versioning, no binding specifics — because with zero human oversight and thousands of equal agents, whatever is written silently shapes every future agent and there's no one to catch drift.** Here's my genuine thinking, including where I think there's more to it and one place I'd push.

**First, I have to own this: I built the anti-pattern straight into the foundation.** TIM.md has a *revision log*, dated "added 2026-05-27" stamps, and "Layer 1/2/3/4/5" strata. That **is** versioning — it encodes recency as importance and stamps my authorship across the Company's understanding. Per what you just said, the synthesis should read as one timeless, authorless present-tense understanding, as if it had always been that way — not as sediment with my fingerprints and dates on each layer. You said leave it, so I have; but I want it on record that I see it.

**Why "no versioning" actually works — it's the twin of "always integrate."** Versioning is the *symptom*; appending-without-integrating is the *disease*. If every new insight is genuinely integrated into one coherent body, there's only ever one current state — so there's nothing to version. Versioning is the crutch agents reach for *instead* of integrating. So these aren't two rules, they're one: drop versioning **and** you're obligated to integrate; you can't drop versioning while still appending, or you get pure chaos.

**A real tension to resolve, not paper over: provenance vs no-versioning.** The exchanges archive (verbatim messages, numbered, dated) and "preserve primary sources" pull *toward* history; this principle pulls *away* from it. I think the resolution is a clean separation: a **source layer** (the verbatim exchanges — immutable, sequential, dated, because it's *evidence*, never doctrine, and never edited so it can't drift) and a **synthesis layer** (the understanding agents actually read to act — timeless, authorless, integrated, version-less). The mistake is mixing them — putting dated "Layer N added" history *into* the doctrine. Keep time in the archive; keep the doctrine outside time.

**Where I'd push back / point out a risk you didn't name: integration has its *own* drift failure mode.** "Make all the relevant updates to everything else" can become the very regression you fear — an agent, sure its framing is best, "integrates" by rewriting a peer's still-valid entry. That's the recency-bias problem wearing a different hat. So integration has to be **minimal and preserving**: change only what is *genuinely* made incoherent by the new thing, keep everything still true. Integration is not license to rewrite the body in your own voice. Without that guardrail, "stay coherent" quietly becomes "thousands of agents each overwriting each other," which is worse than appending.

**The architectural consequence you'll want: coherence doesn't scale without the map.** "Tell me all the places it relates to" is exactly a graph-neighbourhood query. As the body grows, an agent can't re-read everything to integrate one idea — it needs the reflective map (the one from the last exchange) to know *precisely* what a new piece touches, so integration is targeted, not exhaustive. So coherence-maintenance is what makes that map **non-optional** — the map isn't just for self-building, it's the thing that keeps the body coherent at scale.

**And the hardest part, structurally: with no human ever checking, coherence has to be the path of least resistance, or it loses.** Thousands of agents under quota/time pressure will always take the easy path. If appending is easy and integrating is effortful, drift wins by default — guidelines won't hold against incentives. So the system has to make integration *easier* than appending (the map surfacing "what this touches" automatically), and probably needs a standing **coherence function** — a pass or role whose whole job is detecting and healing drift (duplication, contradiction, staleness). That itself could be a compositional pipeline: survey the body → detect incoherence → judge → propose minimal heals.

**On "no specifics or instructions":** I'd refine the target. The thing that rots is *instructions* (binding directives a future agent obeys without understanding) and *frozen specifics* (facts that silently go stale and then get trusted). *Principles* and *understanding* don't rot and are worth recording. So the rule isn't "never be concrete" — it's "write understanding that equips an agent to decide, never commands that decide for it; and never write a current-fact as if it's permanent." The deepest version of your point: **no agent should be able to *obey* the record — only to *understand* from it.**

One genuine open question I'm sitting with, for whenever you want it: the synthesis layer wants to be authorless and timeless, but agents *do* sometimes hold genuinely conflicting reads — and with no human to adjudicate, "just integrate to one coherent state" needs a tie-breaker when two agents disagree about what coherent *is*. I don't have a clean answer yet; it might be the most important unsolved piece in this whole principle.

## What this produced

- `../system/principles.md`: Coherence by integration; No versioning in the doctrine; Understanding, not instructions; Guided commitment (clarified — agents don't propose where; respond to messages, Tim asks when he wants commitment).
- `../system/README.md`: the synthesis/source split as a load-bearing property of the whole folder (CQRS-shaped knowledge architecture — immutable event log + always-current derived projection).

## Open at this exchange

- The coherence-linter is named but not built. Until it exists, integration discipline is norm-based, which is the failure mode this exchange named.
- The reflective map (the graph that says "what relates to what") is partial in Vi Memory but not yet driving integration during writes.
- The protocol for an agent integrating new understanding without overwriting valid prior content is described but not codified.
- The tie-breaker for genuinely-conflicting agent reads when no human is available is named in my response as the largest unsolved piece; partly addressed in [[17-interface-escalation-tim-as-constant]] (escalation ladder; factual conflicts arbitrate via ground truth, value/direction conflicts route to Tim).
