# Methodology — the build-loop recipes (durable copy)

These are the autonomous build-loop **recipes** the Company is built and repaired with — copied into the repo so the methodology travels with the project (it otherwise lives only in `~/.claude/skills/`, which is not version-controlled). This closes the durability gap: saved ≠ in the system.

Each is a cron-driven, parallel, crash-safe loop: read a plan → build the buildable file-disjoint lanes in parallel → verify **by use** (+ adversarial re-check) → commit per criterion on a branch → flag what needs the operator. They descend from one another (`company-build` is the canonical recipe; the rest are adaptations).

| Recipe | What it builds |
|---|---|
| `company-build.md` | the operable composition surface (configure/run/embed/act on the canvas) |
| `rhm-build.md` | the RHM walkthrough & review organ |
| `wire-build.md` | the decision→implementation wire + product surface |
| `remediation-build.md` | the unification/completion/connection loop (fixes cross-layer defects; **verifies the seam, not the cell**) |
| `loop-prep.md` | the three-document prep (Completion Criteria · Implementation Guide · Research Synthesis) a loop consumes |
| `plan-review.md` | iterative multi-agent plan review before a loop runs |

> The live, runnable versions remain in `~/.claude/skills/`. These copies are the durable record + reference. When a recipe changes, update both (or treat the live skill as source and re-copy here as part of the change).
