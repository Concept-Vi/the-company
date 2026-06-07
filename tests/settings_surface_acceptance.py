"""tests/settings_surface_acceptance.py — A3 (settings consolidated) + E2-FE/GC3 (the mode surface).

WHAT THE A3 LANE IS (the consolidated Settings surface):
ONE designed FE surface (canvas/app/src/regions/Settings.tsx, a full-viewport modal opened from the toolbar
gear) where every config slot lives together — modes, models, personas, RHM config, voice — instead of the
scattered RhmChat gear + Toolbar dial. It is BUILT REUSE-ONLY over the EXISTING config machinery: it reads
the registries off existing endpoints and writes through the EXISTING set_rhm_config / set_mode paths. NO new
config endpoint, NO parallel config state.

This is therefore a CONTRACT test: it proves the BACKEND DATA the consolidated surface assembles from + writes
to is exactly the shape + behaviour the surface relies on. (The FORM/render + the live "a change takes" was
verified by USE in the browser at both viewports — see the lane report; this guards the data contract so a
future backend change that would silently break the surface fails loud here.)

WHAT THIS PROVES (by USE — real Suite, real corpus/registries, NO live model):
  A. capabilities() carries the E1 MODE TYPE-REGISTRY the mode surface renders: ≤8 top-level modes, each with
     label + directive (behaviour) + a per-mode context-RESOLUTION declaration (strata/howto_detail/budget) +
     sub-types (the hierarchy) + a consent style — JSON-safe (strata serialised to a sorted list | None).
  B. capabilities().composition_config carries the E2 MODE_AUTODETECT toggle: a live value ∈ its options
     (off/suggest/auto). The surface renders it as a LIVE-SETTABLE control (see C — GC6 closed the read-only gap).
  C. MODE_AUTODETECT IS a writable rhm-config slot (GC6/E2-live): set_rhm_config('MODE_AUTODETECT', v) validates
     against the options (fail-loud on an off-options value), persists, and RE-RESOLVES the live toggle so the
     next capabilities() reflects it. The surface writes through the EXISTING config path — no parallel setter.
  D. rhm_config() exposes the slots the surface reads (model/base_url/persona/timeout/voice_enabled/stt/
     tts_engine/voice_path/roles); set_rhm_config ROUND-TRIPS the writable ones the surface edits — model,
     persona, voice_enabled, voice_path — and the value TAKES (the next rhm_config reflects it).
  E. the ROLES slot DEEP-MERGES (binding one role never wipes a sibling) — the surface binds per-role.
  F. roles() + voice_paths() are shaped as the surface expects (roles: {id:{label,description,binding}};
     voice_paths: {paths:{id:{label,available,...}}, active}) AND the s2s path is UNAVAILABLE (rendered so,
     never as working — the G-19 fail-loud-no-fiction contract).
  G. set_rhm_config FAILS LOUD on a bad value (unknown mode / unknown voice_path) — never a silent set.
"""

import os, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ["COMPANY_TEST_RUN"] = "1"

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite

NODES = os.path.join(ROOT, "nodes")
PASS = 0


def check(label, cond):
    global PASS
    if cond:
        PASS += 1
        print(f"  PASS  {label}")
    else:
        print(f"  FAIL  {label}")
        raise SystemExit(1)


def fresh_suite():
    reg = NodeRegistry()
    reg.discover([NODES])
    return Suite(FsStore(tempfile.mkdtemp(prefix="settings-")), reg)


print("A3 + E2-FE/GC3 · the consolidated Settings surface — backend data contract")

su = fresh_suite()
caps = su.capabilities()

# ── A · the MODE TYPE-REGISTRY the mode surface renders (the hierarchy) ──────────────────────────────
mr = caps.get("mode_registry")
check("A1 · capabilities carries mode_registry (a dict)", isinstance(mr, dict) and len(mr) > 0)
check("A2 · ≤8 top-level modes (the spec'd cap)", 0 < len(mr) <= 8)
for mid, spec in mr.items():
    check(f"A3 · mode {mid!r} carries label+directive+consent",
          isinstance(spec, dict) and "label" in spec and "directive" in spec and "consent" in spec)
    res = spec.get("resolution")
    # resolution is None (admit-all) OR a dict with the three declaration fields
    check(f"A4 · mode {mid!r} resolution is None|declaration(strata/howto_detail/budget)",
          res is None or (isinstance(res, dict) and "howto_detail" in res
                          and (res.get("strata") is None or isinstance(res.get("strata"), list))))
    check(f"A5 · mode {mid!r} subtypes is a JSON-safe dict (the hierarchy)", isinstance(spec.get("subtypes"), dict))
# at least one mode declares a context-resolution override (the modes-and-context-are-ONE-system claim is real)
check("A6 · at least one mode declares a resolution override (modes carry context-resolution)",
      any(s.get("resolution") for s in mr.values()))
# at least one mode declares sub-types (the hierarchy is real)
check("A7 · at least one mode declares sub-types (the hierarchy is non-trivial)",
      any(s.get("subtypes") for s in mr.values()))

# ── B · the MODE_AUTODETECT toggle (E2) — live value + options ───────────────────────────────────────
cc = caps.get("composition_config", {})
check("B1 · composition_config carries MODE_AUTODETECT", "MODE_AUTODETECT" in cc)
opts = cc.get("MODE_AUTODETECT_OPTIONS")
check("B2 · MODE_AUTODETECT_OPTIONS = (off, suggest, auto)", list(opts) == ["off", "suggest", "auto"])
check("B3 · the live MODE_AUTODETECT value ∈ its options", cc.get("MODE_AUTODETECT") in opts)

# ── C · MODE_AUTODETECT IS a runtime-settable slot (GC6/E2-live) ─────────────────────────────────────
# the set_rhm_config whitelist now accepts it (via the existing config path), validates fail-loud,
# persists, and re-resolves the live toggle — the surface writes the toggle through this path.
su.set_rhm_config({"MODE_AUTODETECT": "auto"})         # the FE-facing key, the same composition_config exposes
after_ad = su.capabilities()["composition_config"]["MODE_AUTODETECT"]
check("C1 · MODE_AUTODETECT IS a writable rhm-config slot (set takes + re-resolves live)", after_ad == "auto")
rejected = False
try:
    su.set_rhm_config({"MODE_AUTODETECT": "nonsense"})   # fail-loud on an off-options value (rule 4/8)
except ValueError:
    rejected = True
check("C2 · an off-options MODE_AUTODETECT value is REJECTED fail-loud", rejected)
check("C3 · the FE-facing key never leaks into rhm_config (persisted under the lowercase slot)",
      "MODE_AUTODETECT" not in su.rhm_config() and su._rhm_cfg().get("mode_autodetect") == "auto")
su.set_rhm_config({"MODE_AUTODETECT": "off"})           # reset so downstream D-checks see the default floor

# ── D · rhm_config exposes + round-trips the slots the surface reads/writes ──────────────────────────
rc = su.rhm_config()
for slot in ("mode", "model", "base_url", "persona", "timeout", "voice_enabled", "stt", "tts_engine", "voice_path", "roles"):
    check(f"D1 · rhm_config exposes the {slot!r} slot the surface reads", slot in rc)

# model TAKES
su.set_rhm_config({"model": "settings-test-model:vX"})
check("D2 · set model TAKES (rhm_config reflects it)", su.rhm_config()["model"] == "settings-test-model:vX")
# persona TAKES (the surface writes persona via switchPersona → set_rhm_config{persona})
su.set_rhm_config({"persona": "viv"})
check("D3 · set persona TAKES", su.rhm_config()["persona"] == "viv")
# voice_enabled TAKES (the surface's on/off control)
su.set_rhm_config({"voice_enabled": "off"})
check("D4 · set voice_enabled TAKES", su.rhm_config()["voice_enabled"] == "off")
su.set_rhm_config({"voice_enabled": "on"})
# voice_path TAKES (the surface's path picker; pipeline is always available)
su.set_rhm_config({"voice_path": "pipeline"})
check("D5 · set voice_path TAKES", su.rhm_config()["voice_path"] == "pipeline")

# ── E · the ROLES slot DEEP-MERGES (binding one role never wipes a sibling) ──────────────────────────
role_ids = list(su.roles().keys())
check("E1 · at least one model-function role is registered (the surface binds them)", len(role_ids) >= 1)
rid = role_ids[0]
su.set_rhm_config({"roles": {rid: {"model": "role-bind-A:vX"}}})
check("E2 · binding a role TAKES", su.rhm_config()["roles"].get(rid, {}).get("model") == "role-bind-A:vX")
# a SECOND partial write to the same role's a different key must NOT wipe the model (deep-merge)
su.set_rhm_config({"roles": {rid: {"base_url": "http://localhost:9/v1"}}})
merged = su.rhm_config()["roles"].get(rid, {})
check("E3 · a partial role update DEEP-MERGES (model survives a base_url-only write)",
      merged.get("model") == "role-bind-A:vX" and merged.get("base_url") == "http://localhost:9/v1")

# ── F · roles() + voice_paths() are shaped as the surface expects; s2s is UNAVAILABLE (G-19) ─────────
r0 = su.roles()[rid]
check("F1 · a role carries label+description (the surface renders them)", "label" in r0 and "description" in r0)
vp = su.voice_paths()
check("F2 · voice_paths carries {paths{...}, active}", isinstance(vp.get("paths"), dict) and "active" in vp)
check("F3 · the pipeline path is available (the default, built)", vp["paths"]["pipeline"]["available"] is True)
check("F4 · the s2s path renders UNAVAILABLE — no fiction (G-19)",
      vp["paths"]["s2s"]["available"] is False)

# ── G · set_rhm_config FAILS LOUD on a bad value — never a silent set ────────────────────────────────
def raises(fn):
    try:
        fn(); return False
    except Exception:
        return True
check("G1 · set_rhm_config rejects an unknown mode (fail loud)",
      raises(lambda: su.set_rhm_config({"mode": "no-such-mode"})))
check("G2 · set_rhm_config rejects an unknown voice_path (fail loud)",
      raises(lambda: su.set_rhm_config({"voice_path": "no-such-path"})))

print(f"\nALL {PASS} CHECKS PASS — the consolidated Settings surface's backend data contract holds "
      f"(modes hierarchy + autodetect render-only + the writable slots round-trip + roles deep-merge + "
      f"voice-paths shape + s2s unavailable + fail-loud).")
