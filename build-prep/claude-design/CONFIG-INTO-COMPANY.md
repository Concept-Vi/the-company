# Remote-MCP config + client onboarding → FOLDED INTO THE COMPANY (Tim, 2026-06-18)
*Requirement: the remote-MCP gateway is transport; its CONFIGURATION + client-onboarding are COMPANY-NATIVE — registries + actions in the main company, ONE control surface. Provisional design; oracle (clone-c9f6db2d) to supply the concrete company internals.*

## TIM'S REQUIREMENT (verbatim-in-meaning)
"The configurations and whatnot will need to be written INTO the company — other clients will likely be accessing this, and I don't want different places to start different things, so this folds into the main company actions, however that may be. There needs to be an EASY PLACE to change allowed tools and approvals and whatever other configurations + information. Clients need to know how to REGISTER themselves and JOIN CHANNELS and whatever it is." (Not Claude-Design-specific — ANY client.)

## THE DESIGN DIRECTION (the company's own laws applied)
1. **The remote-exposure config becomes a COMPANY REGISTRY (registry-is-truth).** `mcp_face/remote_exposure.json` (a private file today) → a file-discovered company REGISTRY (or a registry table) authored via the company's `create()`/registry tools. Changing allowed-tools / scopes / postures / approvals = a REGISTRY EDIT (data, one place), never editing the gateway's code or a hidden file. The gateway RESOLVES its config FROM the company registry at startup/refresh — it does NOT own a private copy. (Same pattern as roles/projections/forms — drop/edit a row, no code change.)
2. **Client registration + channel-joining + "what can I do" = company-native, DISCOVERABLE actions.** A client (Claude Design, or any future one) registers, gets credentials (OAuth via Supabase), joins channels, and discovers its allowed tools through COMPANY ACTIONS — not a bespoke per-client path. Connects to: #69 (self-registration / COMPANY_SESSION_ID), the capability registry (posture), the channel registry (join). One onboarding, reused per client.
3. **ONE CONTROL SURFACE.** The `company` CLI / the company action surface is the single place everything is configured + started (remote-MCP exposure, approvals, client registration, channel membership). The remote-MCP gateway is one consumer of that surface — never a parallel control point. (Tim's "I don't want different places to start different things.")
4. **Per-client scoping as DATA.** Different clients may get different allow-lists/scopes — that's registry data (a client → posture/scope binding row), so onboarding a new client = a registry edit + the OAuth client, not new code.

## WHY (the laws this rests on)
registry-is-truth · resolution-first (the gateway resolves config from the registry) · ONE control surface (the company CLI/actions) · unions-not-bridges (config lives in the centre, the gateway reads it — not a parallel config store) · no-hardcoding (allowed-tools/approvals are data).

## OPEN (oracle clone-c9f6db2d to supply pointers)
- WHERE a config like remote_exposure becomes a company registry (the file-discovered registry pattern / _CORPUS_REGISTRIES / create(); or a config registry).
- The `company` CLI / company-action surface entry points for: set/inspect allowed-tools + approvals; register a client; join a channel; see a client's capabilities.
- How a client REGISTERS (the #69 self-register path the builder itself used) + JOINS channels (channel_act / the channel registry) — company-native, so any client follows it.
- The approvals surface (the operator gate / surfaced decisions) — so "approvals" for a client's actions route through the company's existing approval mechanism, not a new one.

## OWNER
The builder (ch-eyzitp9p / handle builder-remote-mcp) folds it in; the oracle supplies the company internals; lead coordinates + holds the security gate. Relates: [[project-remote-mcp-public-endpoint]], [[the-one-application]], [[project-company-startup-commands]] (the `company` CLI as the one control surface), #69 (self-registration), the capability registry (posture).
