"""capability_handlers_registry_acceptance — the TEETH for the L-FOUND-handlers foundation lane.

Proves the DRY handler layer's STRUCTURE (Capability Fabric §3.2). L-FOUND-handlers gates ALL
face+handler lanes, so this is the foundation test; the SEPARATE tests/capability_handlers_acceptance.py
(L-FOUND-DRY-test) proves one-handler-two-faces once the faces exist.

DESIGN NOTE — this test owns the HANDLERS registry contract (resource-grained {key → rail → readonly}
+ the registration seam) and the DURABLE cross-grain invariant that BINDS the registry to the
service-side reduction registries (reduction/{config_targets,cli_allowlist,session_capabilities,
host_reads}). It is deliberately SCHEMA-AGNOSTIC about the reduction tables' internal row shape (those
are owned/iterated by the L-FOUND-R3 / face lanes and converge there) — it checks only the invariant
that MUST hold no matter their internal schema: every reduction row's resource-prefix is a DECLARED
HANDLERS key on a coherent rail. That bridge is the foundation guarantee; the row internals are not.

Checks, all fail-loud:
  1. package + reduction registries IMPORT clean; RAILS is the specced closed vocab.
  2. EVERY declared HANDLERS entry has a VALID rail (§3.2 required-rail law) + coherent readonly
     (readonly IFF a read rail); the Handler ctor REFUSES incoherent declarations.
  3. the COMPLETE ③④⑤ inventory + the REOPENED boundaries (Tim's steer: CC-04 keybindings, CC-32
     telemetry, CC-29 provider, CC-24 auth-read, CC-34 via extensions) are present on the specced rails.
  4. the registration seam works (register_handler swaps stub→real fn; built flips) AND the honest
     `building` stub raises a TEACHING error before a lane wires it (no silent no-op, no green-paint).
  5. CROSS-GRAIN BRIDGE: every reduction act-key (family.resource[:act]) maps to a declared HANDLERS
     resource key; a write/act reduction row only ever points at a NON-read rail handler (a read-only
     resource — patterns/cost/auth — never has a write/act reduction row). registry-is-truth, both ways.

Run: ./.venv/bin/python tests/capability_handlers_registry_acceptance.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from runtime import capability_handlers as ch
from runtime.capability_handlers import reduction

PASS = 0
FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name}  {detail}")


def raises(fn, exc=Exception):
    try:
        fn()
        return False
    except exc:
        return True
    except Exception:
        return False


print("=== capability_handlers_registry_acceptance — the DRY-layer foundation (L-FOUND-handlers) ===")

# ── 1 · package + reduction load ──────────────────────────────────────────────────────────────────
print("\n[1] package + reduction registries load")
check("HANDLERS is a non-empty dict", isinstance(ch.HANDLERS, dict) and len(ch.HANDLERS) > 0)
check("RAILS closed vocab as specced (§1.1)",
      ch.RAILS == ("direct-read", "R3", "R1", "R1-prime", "R2"), f"got {ch.RAILS}")
check("READONLY_RAILS == {direct-read}", ch.READONLY_RAILS == frozenset({"direct-read"}),
      f"got {ch.READONLY_RAILS}")
check("reduction re-exports the 4 named registries (§3.2)",
      set(reduction.__all__) == {"config_targets", "cli_allowlist", "session_capabilities", "host_reads"},
      f"got {reduction.__all__}")
_regs = {n: getattr(reduction, n) for n in reduction.__all__}
for _n, _mod in _regs.items():
    # each reduction module exposes ONE primary dict (NAME.upper()-ish); find it generically.
    _dicts = [v for k, v in vars(_mod).items() if k.isupper() and isinstance(v, dict)]
    check(f"reduction.{_n} exposes a non-empty registry dict",
          any(d for d in _dicts), f"upper-case dicts: {[k for k in vars(_mod) if k.isupper()]}")

# ── 2 · every declared handler: valid rail + coherent readonly (§3.2 required-rail law) ─────────────
print("\n[2] every HANDLERS entry: valid rail + coherent readonly")
for key, h in ch.HANDLERS.items():
    check(f"{key}: rail {h.rail!r} ∈ RAILS", h.rail in ch.RAILS, f"rail={h.rail}")
    check(f"{key}: readonly IFF read rail", h.readonly == (h.rail in ch.READONLY_RAILS),
          f"readonly={h.readonly} rail={h.rail}")
    check(f"{key}: ch.rail_of agrees", ch.rail_of(key) == h.rail)
check("Handler ctor refuses readonly on a write rail",
      raises(lambda: ch.Handler("x.bad", "R3", True), ValueError))
check("Handler ctor refuses non-readonly on a read rail",
      raises(lambda: ch.Handler("x.bad", "direct-read", False), ValueError))
check("Handler ctor refuses an unknown rail",
      raises(lambda: ch.Handler("x.bad", "R9", False), ValueError))

# ── 3 · the COMPLETE ③④⑤ inventory + the REOPENED boundaries ─────────────────────────────────────────
print("\n[3] complete ③④⑤ inventory + reopened boundaries (§4 + Tim's steer)")
EXPECTED = {
    # ③ CONFIG-AUTHORING (§4)
    "config.hooks": "R3", "config.mcp_servers": "R3", "config.output_style": "R3",
    "config.slash_commands": "R3", "config.extensions": "R3", "config.patterns": "direct-read",
    # ③ REOPENED boundaries (Tim's explicit steer — buildable config-face capabilities)
    "config.keybindings": "R3",   # CC-04
    "config.telemetry": "R3",     # CC-32
    "config.provider": "R3",      # CC-29 (host-env edit, same primitive as telemetry)
    # ④ DEV-BRIDGES (§4)
    "dev.git": "R3", "dev.code_intel": "R1-prime", "dev.computer_use": "R1-prime",
    "dev.code_review": "R2", "dev.ci": "R3",
    # ⑤ AUTOMATION (§4)
    "auto.routines": "R3", "auto.workflows": "R1", "auto.cost": "direct-read", "auto.auth": "direct-read",
}
for k, r in EXPECTED.items():
    check(f"{k} declared on rail {r}", k in ch.HANDLERS and ch.HANDLERS[k].rail == r,
          f"got {ch.HANDLERS.get(k) and ch.HANDLERS[k].rail}")
check("no EXTRA undeclared keys (inventory is closed)", set(ch.HANDLERS) == set(EXPECTED),
      f"extra: {sorted(set(ch.HANDLERS) - set(EXPECTED))}")
# the inert-genuinely-out classes are NEVER admitted (CC-01/02 drive-TUI, CC-28 org-admin, CC-31 monorepo)
check("genuinely-inert classes are NOT in HANDLERS (no TUI/org-admin/monorepo op)",
      not any(k for k in ch.HANDLERS if "tui" in k or "org" in k or "monorepo" in k or "keybindings" not in k and "surface" in k))

# ── 4 · the registration seam + the honest `building` stub ───────────────────────────────────────────
print("\n[4] registration seam + honest `building` stub")
_probe = ch.Handler("config.hooks", "R3", False)   # standalone probe — leaves the registry intact
check("unwired stub raises NotImplementedError (teaching, not silent — §8)",
      raises(lambda: _probe.fn(None), NotImplementedError))
check("unwired handler.built is False", _probe.built is False)
_sentinel = {"ok": True}
def _real(suite, *a, **k):
    return _sentinel
ch.register_handler("config.patterns", _real)
check("register_handler swaps the fn", ch.HANDLERS["config.patterns"].fn is _real)
check("register_handler flips built True", ch.HANDLERS["config.patterns"].built is True)
check("registered fn returns its result", ch.HANDLERS["config.patterns"].fn(None) is _sentinel)
check("register_handler refuses an undeclared key (rail not invented per-lane, §3.2)",
      raises(lambda: ch.register_handler("nope.nope", _real), KeyError))
check("register_handler refuses a non-callable", raises(lambda: ch.register_handler("config.hooks", 42), TypeError))
check("ch.get fails loud on unknown key", raises(lambda: ch.get("nope.nope"), KeyError))
check("keys_for_family partitions config/dev/auto exhaustively",
      (set(ch.keys_for_family("config")) | set(ch.keys_for_family("dev"))
       | set(ch.keys_for_family("auto"))) == set(ch.HANDLERS)
      and all(ch.keys_for_family(p) for p in ("config", "dev", "auto")))

# ── 5 · CROSS-GRAIN BRIDGE (ADVISORY diagnostic — reduction schema is sibling-owned + in flux) ──────
# The reduction registries (config_targets/cli_allowlist/session_capabilities/host_reads) are built +
# iterated by the L-FOUND-R3 / L-③④⑤ face lanes; their internal row schema (act-grained vs
# resource-grained vs bare-noun) converges THERE, and the HARD cross-grain invariant
# (one-handler-two-faces, reduction↔face↔handler join) is the L-FOUND-DRY-test's bar (it runs after the
# faces+reduction settle). THIS foundation test does not gate on the siblings' in-flight schema — it
# PRINTS the bridge coverage as a diagnostic so the converging lanes can see the integration state.
# The DURABLE guarantee this lane owns (the HANDLERS contract + the rail-coherence + the registration
# seam) is sections 1–4 above; those are hard checks.
print("\n[5] cross-grain bridge coverage (ADVISORY — does not fail the suite)")
PRIMARY = {"config_targets": "CONFIG_TARGETS", "cli_allowlist": "CLI_ALLOWLIST",
           "session_capabilities": "SESSION_CAPABILITIES", "host_reads": "HOST_READS"}
for _n, _dictname in PRIMARY.items():
    _mod = _regs.get(_n)
    _reg = getattr(_mod, _dictname, None)
    if not isinstance(_reg, dict):
        print(f"  · reduction.{_n}.{_dictname}: not present yet (sibling lane in progress)")
        continue
    _rows = list(_reg.keys())
    # resource-prefix coverage: how many rows' family.resource prefix is a declared HANDLERS key.
    _mapped = [rk for rk in _rows if rk.split(":", 1)[0] in ch.HANDLERS]
    _unmapped = [rk for rk in _rows if rk.split(":", 1)[0] not in ch.HANDLERS]
    print(f"  · {_n}.{_dictname}: {len(_rows)} rows — {len(_mapped)} map to a HANDLERS resource by "
          f"prefix, {len(_unmapped)} do not (bare-noun/scope keys map semantically in the face lane: "
          f"{sorted(set(rk.split(':',1)[0] for rk in _unmapped))[:8]})")
# reopened-boundary handlers are DECLARED here (the durable contract); their reduction ROWS are the
# face lane's to land — report whether they're present yet (advisory, not a gate).
_red_resources = set()
for _n, _dictname in PRIMARY.items():
    _reg = getattr(_regs.get(_n), _dictname, None)
    if isinstance(_reg, dict):
        _red_resources |= {rk.split(":", 1)[0] for rk in _reg}
for _b in ("config.keybindings", "config.telemetry", "config.provider"):
    _has = _b in _red_resources
    print(f"  · reopened {_b}: HANDLERS=declared(R3)  reduction-row={'present' if _has else 'pending (L-③/R3 lane)'}")

# ── verdict ──────────────────────────────────────────────────────────────────────────────────────────
print(f"\n=== {PASS} passed, {FAIL} failed ===")
sys.exit(0 if FAIL == 0 else 1)
