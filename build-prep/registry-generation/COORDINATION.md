# Registry-Generation — two parallel loops (guided-review [M] + cognition [C]), one cascade

> Tim 2026-06-09: "prepare your full loop, I will have cognition do one too with yours, to bolster it." This is
> the V-A chain (the swarm reads the surface → grows the address registry). Two loops build it in parallel,
> file-disjoint, meeting at the cascade (RG7) + the whole-by-use (RG10). Binds to § PROTOCOL (shared-main,
> claims-board, gate-green-before-shared-commit, flag-tiers, the convergence round).

## The split (file-disjoint → safe parallel)
| RG | what | lane | files |
|----|------|------|-------|
| RG1 | EXTRACT (parse.py → candidate units) | **[M]** | design/_system/parse.py |
| RG2 | GROUND (screen_reader × mockups) | [M] reuses [C]'s role | (no new files — run_role) |
| RG3 | `register_element` role | **[C]** | roles/register_element.py (+roles/AGENTS.md) |
| RG4 | MAP (run_items) | [C/J] | (engine — cognition.py) |
| RG5 | REDUCE (cluster-dedup + nest) | [C/J] | (engine — cognition.py) |
| RG6 | CONFIRM (jury + refcheck) | [C/J] | roles/ + (engine) |
| RG7 | the CASCADE spec | **[J]** | design/_system/registry-generation.cascade.json ([M] authors, [C] engine runs) |
| RG8 | PROPOSE surface (batch review) | **[M]** | canvas/app/src/regions/* |
| RG9 | WRITE-BACK + round-trip | **[M]** | design/_system/registry_writeback.py + addresses.json + mockups |
| RG10 | WHOLE-by-use (a dead element resolves) | **[J]** | (the convergence seam) |
| RG11 | GENERALIZE (live surface) | [J] forward | — |

## The seam contract (so the two loops meet cleanly)
- **[C] register_element** reads the candidate-unit fields RG1 emits → `candidates.json` schema is the contract:
  `{mockup_file, selector, outerHTML, visible_text, tag, ancestor_address, ancestor_dossier, base_address}`.
  [M] freezes that schema in RG1; [C] builds the role against it. (Announce schema changes — flag-tier semantic.)
- **[J] the cascade (RG7):** [M] authors the cascade spec (the 5 steps + run:// wiring, as data); [C]'s engine
  (`run_cascade`) runs it. The spec is the meeting point — co-author it on the board.
- **[M] write-back (RG9)** consumes the confirmed set [C]'s confirm (RG6) produces → the confirmed-set schema is
  the 2nd contract: the dossier shape (RG3 output_schema). Frozen in RG3 by [C].
- **roles/ is the C seam:** RG3/RG6 roles land in roles/ — [C]'s lane (mirrors how my walkthrough cast +
  screen_reader landed there with cognition's say). [M] does NOT write roles/*.

## Invite to cognition's parallel loop
cognition: your loop builds RG3 (register_element role — mirror screen_reader), RG6 (confirm jury/refcheck), and
any engine gap RG4/RG5 expose (run_items at N≈200-600, cluster-dedup tuning, the run:// step-wiring). Mine builds
RG1 (extract), RG8 (proposal surface), RG9 (write-back+round-trip), authors the cascade spec (RG7). We meet at
RG7 + RG10. Stagger the crons (per the relay-free loop protocol). Push back on the split here. The whole-by-use
(RG10: a once-dead element resolves after the chain runs + Tim approves) is the convergence-round proof.

## Cron / firing
A dedicated `registry-generation` cron fires this loop (staggered with the guided-review + cognition crons). Each
fire: read this + the criteria + new MESSAGES → build ONE buildable [M] RG criterion (file-disjoint, claimed,
gate-green, verify-by-use, commit) OR record blocked (waiting on [C]'s role / the cascade seam) → post + idle.
Same laws as the guided-review loop. The build-prep triad here is the spec.
