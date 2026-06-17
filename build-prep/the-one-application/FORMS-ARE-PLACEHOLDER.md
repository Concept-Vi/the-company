# Forms taxonomy = PLACEHOLDER, not canonical (Tim, 2026-06-17)
*Standing correction. Do NOT treat the current forms as the right application.*

Tim: "I don't actually agree that decision or hand[off] or [changelog] questions or whatever else is currently in there [is] the right application of this. Those got put in there by the AI that used to build this, and at the time it wasn't worth me correcting them... those things I've just placeholdered and were to be better in my principles and Architecture. I just wanted to get the base down."

**What this means:**
- The current `forms/` rows — `decision` (deep), `log` (legibility), `registry` (legibility), `prose` (deep fallthrough) — and `repo_digest`'s `kind` enum (code|doc|config|test|data) are **PRIOR-AI SCAFFOLDING**, not Tim's canonical taxonomy. The base mechanism (file-discovered form registry, effort-routing-by-form, forms-define-behaviour, lifters for free structure) may be sound; the SPECIFIC taxonomy is provisional and to be redesigned to Tim's principles/architecture.
- **Do NOT lock or build on the current form taxonomy as if it's correct.** ([[feedback-scaffolding-not-spec]] — pre-built things are scaffolding, never specs.)
- **Forms should come FROM the coverage, not be imposed on it.** Per Tim's coverage law (can't know in advance what's in everything → plan for the future point where you'll know based on the outputs): the open-ended coverage pass reveals the real kinds of things in the codebase → THAT evidence informs Tim's real form taxonomy. The forms get authored (to his principles) AFTER we see what's actually there — not before.

**How to apply:** when running coverage, the first pass is OPEN-ENDED (describe what's actually here), NOT a forced classification into the placeholder forms. The natural kinds that emerge → proposed to Tim → his form taxonomy. Relates: [[the-one-application]], the coverage runbook.
