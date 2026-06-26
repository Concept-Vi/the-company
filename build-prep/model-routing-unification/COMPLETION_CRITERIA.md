# Model-Routing Unification — Completion Criteria (the truth table)
*A line is GREEN only when verified BY USE (a real run, the `run://` trail / a real spawn), not by code-reading. Priority = dependency order. Provisional; Tim is the judge of "right."*

## VERIFICATION RULES
- FUNCTION verified by USE: a real turn/spawn/resolve, evidenced by the `run://` trail, the spawned process's model, or a live resolve call — never "the code looks right."
- registry-is-truth verified: the change is a registry/role-binding edit (data), ZERO engine code.
- byte-identical verified: `git diff` shows ONLY the additive kwarg on the default path.
- fail-loud verified: the unresolvable case RAISES + surfaces (Notice/Gap), never a silent wrong model.

## PRIORITY 1 — THE RESOLVER + REGISTRY TIERS (foundation)
- **U1 · One resolver exists.** `resolve_model(intent)` resolves role/step/session/clone/service intents to {model, base_url, provider, why}.
  - FUNCTION ☐ by use: `resolve_model({kind:role, role_id:focus})` → the 4B; `resolve_model({kind:role, role_id:reduce_synth})` → a cloud brain; `resolve_model({kind:clone, context_tokens:300000})` → deepseek-v4-flash (1M), `…:100000` → kimi (256K). All evidenced live.
  - FORM ☐: it WRAPS the existing resolvers (resolve_role/capability_providers/resolve_binding) — no second router (diff shows reuse, not re-implementation).
- **U2 · Registry encodes the tiers.** `model_capabilities.json` + `capability_providers()` declare the 4B provider `[chat,json,fast,no-think]` and the cloud brain `[chat,json,reasoning,wide,code]`; extractor roles require `fast`, judge/synth roles require `wide`/`reasoning`.
  - FUNCTION ☐ by use: a capability-query for a judge role returns the cloud provider; for an extractor returns the 4B. registry-is-truth ☐: re-tiering a role (edit its `requires`) flips its resolved model with ZERO code change.
- **U3 · Fail-loud.** An intent that no provider satisfies RAISES (reuse `resolve_binding`'s raise) + surfaces a Notice/Gap. ☐ by use (force a no-match → raise, not a silent default).

## PRIORITY 2 — THE COGNITION ENGINE ROUTES THROUGH IT (the build-brain fix)
- **U4 · Per-role routing in the swarm.** A single RHM turn runs EXTRACTOR roles on the 4B and JUDGE/SYNTH roles on a wide cloud brain, simultaneously.
  - FUNCTION ☐ by use: the turn's `run://` trail shows ≥1 role on `:8000` (4B) AND ≥1 synth/judge step on the cloud brain — in the SAME turn. This is THE proof Tim asked for (the local small model no longer builds complex things; the wide brain does).
- **U5 · run_swarm byte-identical default.** With no `resolve=` passed, `run_swarm`/`run_jury`/`run_panel`/`run_reduce`/`run_composition` behave exactly as before (RESIDENT 4B).
  - FUNCTION ☐ by use + diff: existing cognition acceptance tests pass unchanged; `git diff` shows only the additive kwarg + the `if resolve:` branch.
- **U6 · reduce / jury / composition synth on the wide brain.** The synthesis/judge steps (`reduce_synth`, `triad_synth`, `judge`, composition's judge leg) resolve to cloud. ☐ by use (the `run://` step shows the cloud model).
- **U7 · cascade pin lifted.** `run_cascade` routes per-step via the resolver (the outdated RESIDENT_BASE_URL pin is gone); a cascade step can run cloud. ☐ by use.

## PRIORITY 3 — INTERACTIVE / CLONE BRAINS ROUTE THROUGH IT
- **U8 · One context-size picker.** Clones resolve their model via `resolve_model({kind:clone, context_tokens})` — the cc_clone picker is FOLDED IN (not a parallel picker). ☐ by use: a >256K clone → deepseek-v4-flash, ≤256K → kimi, via the unified resolver; `cc_clone_acceptance` green.
- **U9 · The loadable/builder brain runs on a wide brain by default.** `/api/claude/turn` (the FACE loadable brain) + `implement.py` resolve a build-tier model (kimi) via the resolver, not the account default — so the brain that "builds complex things" is wide-knowledge.
  - FUNCTION ☐ by use: a loadable-brain turn spawns on the resolved wide model (the spawn cmd / `run://` shows it); the FACE first-slice loadable brain uses it.

## PRIORITY 4 — ABSORB THE SCATTERED KNOBS (unification tail)
- **U10 · No hardcoded model ids in the build path.** `bridge.py:1064` (and any literal model id in the cognition/build path) resolves via the registry, not a hardcode. ☐ by grep + use.
- **U11 · Consts become registry defaults.** `DEFAULT_BRAIN`/`RESIDENT_MODEL` are read THROUGH `resolve_model` as registry defaults; no consumer bypasses the resolver for a model choice. ☐ by grep (no `fcfg.DEFAULT_BRAIN`/`RESIDENT_MODEL` used as a model EXCEPT inside the resolver/registry).
- **U12 · `-pro` is never an implicit default.** No path defaults to `deepseek-v4-pro:cloud` without an explicit registry tier asking for it (Tim's rule). ☐ by grep + use.

## STANDING "ONE MECHANISM" CRITERIA (held across the build)
- **M1 · Single entry.** Every model choice (chat/role/clone/session; service-models noted as the same pattern) flows through `resolve_model` OR a documented registry-driven service selector — no scattered ad-hoc picks survive in the build path. ☐ by grep audit (the catchment list in RESEARCH_SYNTHESIS.md is the checklist — each point either routes through the resolver or is explicitly logged as out-of-scope).
- **M2 · registry-is-truth.** A model/tier change is a registry edit; the engine code names no model. ☐.
- **M3 · No silent caps.** Any selection point left un-unified in this build is `log()`-ed/noted (not silently skipped) so the catchment stays honest. ☐.

## OUT OF SCOPE (this build) — note, don't silently drop
- Embedder LAYER selection (`resolve_emb_layer`) stays its own resolver (same pattern, different concern — dims must not cross). Noted as a sibling, unified in pattern only.
- Voice/TTS/STT engine selection (already persona/registry-driven) — folded conceptually, not rewritten.
- Mode-loadout (which services are RESIDENT) — the resource layer (`company up @mode`) is a separate axis from per-call model resolution; they meet at "is the resolved model's service up?" (a fit/ensure check) but are not merged here.
