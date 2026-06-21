# POPCORN / KERNELS — the build spec (D in the D→C→A→B sequence)
*Tim's direction 2026-06-21 (a folding-in). Concept + criteria: CHANNEL-LOOP-BOARD.md §POPCORN. Memory: [[project-popcorn-kernels]]. This is the build-ready spec, grounded in the read-only scout (the kernel system is ~80% built, infrastructure-complete, wiring-incomplete).*

## The primitive (one line)
A KERNEL = an OUTSIDE perspective (curated to this instance, no stake in the consensus, no preconception to satisfy) injected to surface what the self-confirming fabric can't: GENERATE un-preconceived ideas/designs, or ADVERSARIALLY attack the fabric's done/connected claims. A new channel item-type alongside `decisions`, on the operator-cycle, with a feedback→elevate-to-Tim loop. Composable — perspective · input-spread · prompt · substrate · threshold = registry fields.

## What EXISTS (the 80% — scout-grounded, cite-checked)
- **Diverse-lens JUDGE** — `run_panel` (N-role quorum verdict) + `run_jury` (N-draw of one role) at runtime/cognition.py:1925/1844; verdict_panels/ registry file-discovered + wired. ENGINE-ONLY (no MCP tool).
- **Generate path** — `run_draft`/`run_draft_items` (inline ad-hoc role, no file) at mcp_face/server.py:632/688 + `run_items` (MAP) cognition.py:1318 + `run_reduce` (JOIN/cluster) :2112 + `run_cascade` :2358. All MCP-callable + live. run_items takes inline Role() objects (dragnet_extract.py builds roles on the fly) → no second "unregistered role" path needed.
- **Local-4B fleet / concurrency** — SlotBudget.from_registry (cognition.py:781) DERIVES the concurrent-slot count from the live chat-4b config (≈32 typical, NOT hardcoded); run_swarm uses global_vram_gate, ThreadPoolExecutor capped to budget. The "breadth ≤32" is this path, live.
- **Fresh-session spawn** — session_supervisor (:8771) + cc_clone (point-in-time) + `session_post` (MCP) — spawn/inject/watch proven. A perspective-session = session_post(to=new, message=<kernel-prompt>, verb=consult).
- **Item-type + decision pattern** — file-discovered registries (decisions/, item_types/, roles/); state composes from the mark thread (not the row); resolve_address dispatch (cognition.py:99-111) is the ONE seam.
- **The dragnet** — ops/dragnet_extract.py (coarse→gate→fine over chunks) + run_items+run_reduce; PROVEN at scale (the theorem bake: 35,904 chunks, 32-concurrent). Reads substrate.db chunks today, NOT company files.

## What to WIRE (the ~20% — the build-list, sequenced)
**D (this spec) → then:**

### C — the certain-landscape dragnet (grounds everything after)
1. **Source-redirect** the dragnet's load_chunks (dragnet_extract.py:79-117) to read the COMPANY FILES (a git-tree loader), not substrate.db chunks. Each file → one item.
2. Run: 4B `run_items` over every file with a FORMALISED prompt ("how does this relate to <build-intent>?", authored for the kernels — not Tim's words, not generic) → structured output → a table → a threshold drops the definitely-irrelevant → a NEXT LAYER (same/larger model, fewer items, against the project) → the TOTAL CERTAIN LANDSCAPE. (MAP=run_items, REDUCE=run_reduce/layered.)
3. ★ Surfaces the company-directory DRIFT (scout: primary=/home/tim/company is the ONLY live runtime; company-cognition/company-scan/the /home/tim/ session_supervisor copy are stale/explorations — merge/retire to ONE).

### the kernel item-type (mirror the decision pattern — mechanical)
4. **kernels/ dir + runtime/kernel_registry.py** (copy decision_registry.py): each kernels/<id>.py declares `KERNEL = {id, perspective, lens_roles|prompt, input_spread, substrate, threshold, valence: generative|adversarial}`. File-discovered.
5. **kernel:// branch** in resolve_address (cognition.py:~110, mirror decision://).
6. **mark_type kernel_feedback** (mirror decision_take) — threads on kernel://<id>; the feedback→better-next-attempt + elevate-to-Tim signal.
7. **stack_item_type kernel** (mirror decision-sequence) — render the verdict/takes as a card (NOT a text-wall); the operator surface stacks it like a decision.
8. **feed-builder ext** (kernel_inbox alongside decision_inbox) — surface kernel rows to the stack.

### the run-paths (the two valences)
9. **MCP wrapper** `run_panel`/`run_jury` (mcp_face/server.py) — so a kernel can fire an N-lens verdict. (The one genuine engine→face gap.)
10. **GENERATE valence:** run_draft(lens-prompt) → run_items over the units (or the landscape from C) → run_reduce → a take-card. UN-CONSTRAINED prompt (full spread + the gap + open generativity; NO specific instruction).
11. **ADVERSARIAL valence:** run_panel/jury (or a fresh session) over a CLAIM + channel-history → hunt counter-evidence → inject the refutation card. The standing confirmation-bias fix. (fork's theorem-synthesis refutation is this, done manually — formalise it.)

### orchestration (the loop)
12. A kernel RUN: craft the perspective-prompt → fire (local-4B breadth OR fresh-CC depth OR run_panel) → the take/verdict surfaces as a kernel card → the fabric GROUNDS it (recall/check vs what exists) → feedback marks → better next attempt → elevate the strong ones to Tim → his taste → crystallize.

## Sequence (knowledge-dependency, Tim's ordering)
**D (this) → C (dragnet/landscape → know what's there) → A (generative kernel, grounded by C) → B (adversarial kernel, standing).** Each floats without the prior. A is Tim's primary need (the un-give-able direction); B is the standing confirmation-bias fix (already emerging in fork's refutation).

## Folds onto the operator-cycle
The decision-surface (LIVE: the item-type registry, the card render, the feed, feedback→elevate-to-Tim) IS popcorn's substrate. A kernel card = the same machinery as a decision card. Not new infrastructure — a new item-type + the kernel run-paths on the proven cycle. Recursive: the adversarial kernel hardens the fabric building popcorn (incl. popcorn).
