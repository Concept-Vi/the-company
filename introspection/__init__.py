"""introspection/ — the Mirror-Registry System engine (Level 1) + instance-#1 adapters.

The platform-agnostic engine that operates the four-verb circuit
(DISCOVER → CLASSIFY → PROJECT → REFRESH) over the Platform Registry and the
Capability Registry. NO platform names live in this package's engine/rules/adapters
code — Claude Code is ONE data row in platforms/claude_code.py (the lift, PG2 / F-FIX-10).

This __init__ keeps the package import side-effect-free (no live spawn, no model load):
sub-modules (rules, discover, engine, adapters/*) are imported explicitly by callers.

See AGENTS.md (this folder's constitution) for the rules, the NEW-pattern singleton
rationale (F-FIX-1), the transport-derivation contract (F-FIX-2), the store write
convention (F-FIX-15), and the leak invariant (F-FIX-10).
"""
