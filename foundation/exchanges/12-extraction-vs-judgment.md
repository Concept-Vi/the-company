---
type: exchange
sequence: 12
title: "The extraction-vs-judgment correction (the trigger)"
date: 2026-05-27
session: 68e14d07
verbatim: true
note: "Tim's message reproduced as dictated (TTS); errors preserved. [bracketed] text = my readability correction. My response preserved verbatim. This is the architectural correction that triggered the entire post-AppData arc — every later exchange in this archive proceeds from here."
produced:
  - "[[../system/architecture|Architecture]] — the node taxonomy (survey / interpret / reduce / judge / gate); the determinism preference design law; the membrane / structured-output schema; the reduction tree."
  - "[[../system/principles|Principles]] — Determinism preference."
  - "Re-built AppData pipeline: pure-extraction stage 1 ([[../../../appdata-cleanup/extract.py|extract.py]]) + telemetry + the batch-process view ([[../../../appdata-cleanup/batch_view.html|batch_view.html]])."
tags: [foundation, primary-source, architecture, extraction-vs-judgment, hybrid, trigger]
---

# 12 — The extraction-vs-judgment correction (the trigger)

> [!info] Primary source — verbatim
> Reproduced from session `68e14d07` (2026-05-27). Tim's message corrected the AppData pipeline architecture: small concurrent models must produce *structured observations*, not determinations; judgement happens after, in a central smart stage that reads the distilled output. This is the architectural seam every later exchange in the archive builds on.

## Tim's message (verbatim)

> Sounded like a decent first crack, I'd want to have a view to see the batch process, like how many and times and that kind of stuff - this is a good use case run to get a bit of an understanding. The other thing that I will mention, is that one of the failures is that you never should've asked them to determine what was safe to delete or not. They should not be making decisions or determinations about the context, that's not the benefit and purpose of concurrent processes, That would come after. All of their outputs would probably go into some other process with smarter and better models to make the determination of stuff, in this case that could be you or it could be a smarter model that you Setup, or something like that. The small models, and concurrent runs that go, they shouldn't be tasked with producing an answer or solving a problem making determinations, their output would be used to do that. It's not possible for smart models to read go through all of the content because it is too big, and it is not possible for the small models to make the reasoning because it is too subjective and contextual. I would've thought that that was how they would go together and it would be a matter of the structure output and what the smarter models need to be able to do that, do you know what I mean and can you explain that to me better?

## My response (verbatim)

You've put your finger on the actual architecture, and I got it backwards. Let me explain it properly — because you asked me to, and because it's a principle the whole Company runs on, not just this task.

### The core: two opposite limitations that cancel each other

You named the two walls precisely:

- **The volume wall** — a smart model *cannot* read 996 GB / 2.6M files. It can't even comfortably hold the 363k-directory list. The raw material is too big for judgment to ever touch it directly.
- **The judgment wall** — a small model *cannot* make the determination, because "should Tim delete this" is subjective, contextual, and **relational**. It depends on what you use, what's precious, and how folders relate to each other.

These aren't both-bad. They're **complementary** — each model is strong exactly where the other is weak:

| | Volume | Judgment |
|---|---|---|
| **Small models (concurrent)** | ✅ can chew through it | ❌ can't |
| **Smart model (central)** | ❌ can't fit it | ✅ can |

So the labour splits along that seam:

- **Small concurrent models = EXTRACTION.** Each one looks at a sliver and produces **structured facts** — *observations*, not verdicts. "What is here," never "what to do." Cheap, parallel, breadth.
- **Smart model = JUDGMENT.** It never touches the raw volume. It reads the **distilled structured output** — now small enough to fit — and makes the contextual determinations. Expensive, singular, depth.
- **The structured output is the membrane between them.** Its design is the whole game: it must carry *everything the smart layer needs to judge*, while requiring *no judgment to produce*.

My pipeline collapsed the two — I made the 4B model both extract *and* rule (`safe_to_delete`, `recommendation`). That's asking the retina to decide what you should throw away.

### Why judgment *must* be central, not at the edge

This is the part that connects to how you think. Determinations are **relational**. "Is `ov\cache` safe to delete?" only has an answer once you know `ov` is Omniverse and `ov\pkg` is the *install* sitting right beside the cache. A per-folder worker sees one node and **no relationships** — and for you, *the relationships are the content*. Fan-out **destroys** relationships by isolating each item. Judgment therefore has to live at the **fan-in**, where the whole picture is reassembled and the relationships exist again. The crew scatter to observe; the entity reasons over what they bring back.

### The proof that you're right: my "fix" was the accidental version of this

When the 4B mislabelled `Local\Packages` as "deletable" (it's the WSL disk) and misread `ov` as `uv`, I bolted on the **authoritative override table** to correct it. That override layer *was a crude, hardcoded smart-judgment stage* — I stumbled into the exact two-stage shape, but as a **patch instead of an architecture**, and with me hand-writing the rules instead of a model reasoning over the facts. You're saying: that wasn't a patch to add, it was the design I should have started from. The small models should never have emitted "safe to delete" at all.

### The cognition parallel (your field)

The brain already does this. Massively **parallel, pre-attentive feature extraction** in sensory cortex — breadth, no decisions — feeding **serial, deliberative reasoning** in prefrontal cortex that holds the integrated picture and decides. Perception extracts; cognition determines. They're separated for the same reason: the perceptual layer can't be made to reason, and the reasoning layer can't be made to process raw bandwidth. The architecture you're describing is the same split, and it's why it feels obviously right to you.

### What the membrane should carry (the design question you raised)

For this task, stage-1 extraction should emit **only observations**:
- apparent app/vendor (from name + structure)
- what it appears to contain (descriptive: "downloaded package archives", "shader binaries", "a single large .vhdx")
- content signals (telltale names: *cache/temp/logs/backup*; dominant file extensions)
- structural facts (size, file count, depth, biggest children) — most of which don't even need a model

Then stage 2 (me, or a bigger model I run) reads **all 161 at once**, sees them *relationally*, and produces the determinations — plus group-level rules, plus a flag for the genuinely ambiguous ones that should come to you. **It scales by becoming a tree**: if there were 100,000 records, you'd reduce in layers (reductions of reductions) until it fits. Map-reduce generalises to a reduction tree; only the number of judgment layers changes.

---

That's the principle. Now I'll demonstrate it the right way and build the batch-process view you asked for. Capturing the principle first (it's a durable Company architecture rule), then rebuilding stage 1 as pure extraction *with telemetry*, running it so you have real numbers, and building the observability view.

## What this produced

- The node taxonomy in `../system/architecture.md` (survey / interpret / reduce / synthesise-judge / gate) is the generalisation of this exchange's split.
- The **Determinism preference** principle in `../system/principles.md`.
- The rebuilt AppData pipeline (`~/appdata-cleanup/extract.py`) — observations-only stage 1 — and the batch-process view (`~/appdata-cleanup/batch_view.html`) — telemetry visualisation. Both serve as the working template for the compositional pattern.

## Open at this exchange

- The smart-stage / judgement-layer for the AppData pipeline was filled by the *override table* (hardcoded rules) and by me in the conversation — not by a model. The natural next step, surfaced but not built, is the dedicated standing judgement node (local big model on the fabric, or the session model, or a calibrated twin) reading the extracted records and producing the determinations natively.
- "What the structured output should carry" is partially demonstrated by the observation schema in `extract.py`; the general design question for arbitrary tasks remains open ([[13-compositional-architecture]] picks it up).
