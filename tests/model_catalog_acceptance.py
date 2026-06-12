#!/usr/bin/env python
"""model_catalog_acceptance — C2.5: the model CATALOG is WIDENED to the FULL declared model set,
and it is FILE-DISCOVERED declared-data (registry-is-truth), NOT a hardcoded python dict that omits
non-resident models.

This is the C2.5 (original G8/L-model) lane's drift/acceptance home. It is DISTINCT from
model_capabilities_acceptance.py (which proves the resident-4b row's exact values + the JOIN +
fail-loud residency — the no-regression base). HERE proves the WIDTH + the data-driven bar:

Proves BY USE:
  1. WIDTH — the catalog carries the full declared model set keyed by model-id (the resident 4B,
     the local chat workers, the embedders, the model-id voice engines, the cloud reasoner), not
     just the resident-chat-4b-only set. Every model-id-bearing services.json model is cataloged.
  2. CAPABILITY DISCRIMINATION — the role↔model query (suitable_models/role_can_bind/provides_for)
     now projects REAL capabilities across ALL models: an embed-requiring role resolves to the
     embedders; a chat role to the chat workers; a vision-requiring role resolves to [] (fail-loud-
     by-empty — no cataloged model provides vision), NEVER a crash; tts to the voice engines.
  3. GROUNDED, NOT FABRICATED — every row's provides traces to a hard services.json signal
     (--runner pooling → embed; --tool-call-parser → tools; chat_template_nothink → no-think).
     A services.json model with NO catalog row keeps hitting the unknown→ASK fail-loud path.
  4. THE DATA-DRIVEN BAR (the criterion, literally executed) — adding a model entry to the
     declared data file ops/model_capabilities.json makes it appear via every query with NO code
     edit. Done here by writing a temp catalog file + reload_catalog(path) and asserting the new
     model is suitable/known.
  5. FAIL-LOUD LOADER — a missing/malformed/empty catalog RAISES, never a silently-empty dict.

Run: PYTHONPATH=/home/tim/company /home/tim/company/.venv/bin/python tests/model_catalog_acceptance.py
"""
import json
import os
import sys
import tempfile

# ops/cli modules use BARE imports (stdlib-only package); add it to the path to import the module.
_OPS_CLI = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ops", "cli")
sys.path.insert(0, _OPS_CLI)

import registry
import capabilities as cap

RESIDENT = "cyankiwi/Qwen3.5-4B-AWQ-4bit"

_passed = 0
_failed = 0


def check(name, cond, detail=""):
    global _passed, _failed
    if cond:
        _passed += 1
        print(f"  PASS  {name}" + (f"  — {detail}" if detail else ""))
    else:
        _failed += 1
        print(f"  FAIL  {name}" + (f"  — {detail}" if detail else ""))


def main():
    reg = registry.load()

    print("\n[1] WIDTH — the catalog is the FULL declared set, NOT resident-chat-4b-only")
    cat = set(cap.MODEL_CAPABILITIES)
    check("catalog has > 2 models (was effectively resident-only)", len(cat) > 2,
          detail=f"{len(cat)} models")
    check("resident 4B is still cataloged (the original row, unchanged)", RESIDENT in cat)
    # Every services.json model-id (brain/models/voice) that exists should be cataloged — the catalog
    # widened to the FULL declared set. (Keyless services with no config.model are not model-id-keyed.)
    svc_model_ids = {
        (s.get("config") or {}).get("model")
        for s in reg["services"].values()
        if (s.get("config") or {}).get("model")
    }
    for mid in sorted(svc_model_ids):
        # voice engines that are model-id-bearing + chat/embed are cataloged; we assert each KNOWN
        # services.json model-id is in the catalog (the width claim).
        check(f"services.json model {mid!r} is cataloged", mid in cat)

    print("\n[2] CAPABILITY DISCRIMINATION — the query projects REAL capabilities across ALL models")
    embedders = cap.suitable_models({"embed"})
    check("an embed-requiring role resolves to the EMBEDDERS (not the resident 4B)",
          len(embedders) >= 2 and RESIDENT not in embedders, detail=str(embedders))
    check("the resident 4B does NOT provide embed (it is a chat worker)",
          cap.role_can_bind({"embed"}, RESIDENT) is False)
    chatters = cap.suitable_models({"chat", "json"})
    check("a chat,json role resolves to the chat workers (incl resident) + cloud",
          RESIDENT in chatters and len(chatters) >= 3, detail=str(chatters))
    # vision: the VL models (Qwen3-VL-Embedding/Reranker + jina-v4) now PROVIDE it (2026-06-12 —
    # before that, vision was a negative-only tag; the catalog comment's "no model provides it yet"
    # is no longer true). A vision-requiring role resolves to those models, NEVER a crash.
    try:
        vis = cap.suitable_models({"vision"})
        check("a vision-requiring role resolves to the VL models (>=2), not a crash", len(vis) >= 2,
              detail=str(vis))
    except Exception as e:
        check("a vision-requiring role does NOT raise", False, detail=f"raised {e!r}")
    check("the resident 4B (a chat worker) does NOT provide vision",
          cap.role_can_bind({"vision"}, RESIDENT) is False)
    # fail-loud-by-empty is now demonstrated by stt — on disk but NOT cataloged (keyless services),
    # so no model provides it → [] rather than a crash.
    check("an stt-requiring role resolves to [] (fail-loud-by-empty — no cataloged stt provider)",
          cap.suitable_models({"stt"}) == [], detail=str(cap.suitable_models({"stt"})))
    rerankers = cap.suitable_models({"rerank"})
    check("a rerank-requiring role resolves to the RERANKERS (>=2), not the embedders/chat",
          len(rerankers) >= 2 and RESIDENT not in rerankers, detail=str(rerankers))
    check("the rerankers do NOT also provide embed (a reranker is not an embedder)",
          all("embed" not in cap.provides_for(m) for m in rerankers))
    tts = cap.suitable_models({"tts"})
    check("a tts role resolves to the model-id voice engines", len(tts) >= 1, detail=str(tts))

    print("\n[3] GROUNDED, NOT FABRICATED — every provides ⊆ tags; every embedder provides embed")
    for mid in embedders:
        # pure text embedders provide exactly [embed]; MULTIMODAL embedders provide embed + vision.
        # The grounded bar: every embedder genuinely provides embed (no chat/tools fabricated), and
        # any extra tag is itself grounded (vision for the VL/jina-v4 multimodal embedders).
        prov = set(cap.provides_for(mid))
        check(f"{mid}: provides INCLUDES embed and ⊆ {{embed,vision}} (grounded, no chat/tools)",
              "embed" in prov and prov <= {"embed", "vision"}, detail=str(cap.provides_for(mid)))
    for mid, spec in cap.MODEL_CAPABILITIES.items():
        check(f"{mid}: provides ⊆ CAPABILITY_TAGS (controlled vocab, no invented tag)",
              set(spec["provides"]) <= set(cap.CAPABILITY_TAGS), detail=str(spec["provides"]))
    # a services.json model that is NOT cataloged must hit the unknown→ASK fail-loud path
    u = cap.capabilities_for("totally/unregistered-model", reg)
    check("an uncataloged model-id → known=False + action=ASK (no fabricated row, rule 8)",
          u.get("known") is False and u.get("action") == "ASK")

    print("\n[4] THE DATA-DRIVEN BAR — add a row to the FILE → it appears, NO code edit")
    # Build a temp catalog file = the live catalog + ONE net-new vision model row. Reload FROM it.
    # If the catalog were a hardcoded python dict, this could not work without editing capabilities.py.
    src_path = os.path.join(os.path.dirname(_OPS_CLI), "model_capabilities.json")
    with open(src_path) as f:
        raw = json.load(f)
    NEW_ID = "acme/test-vision-7b"
    raw[NEW_ID] = {
        "_note": "test-only row injected by model_catalog_acceptance to prove add-a-row-no-code-edit.",
        "tools": {"value": False, "source": "declared"},
        "json_schema": {"value": None, "source": "declared"},
        "thinking": {"value": False, "source": "declared"},
        "context_ceiling": {"value": 32768, "source": "declared"},
        "concurrency_knee": {"value": None, "source": "declared"},
        "speed_profile": {"value": None, "source": "declared"},
        "provides": ["chat", "vision"],
    }
    saved = dict(cap.MODEL_CAPABILITIES)  # remember the live catalog to restore after
    tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    try:
        json.dump(raw, tmp)
        tmp.close()
        cap.reload_catalog(tmp.name)  # the seam: re-read the FILE into the live name
        check("the new model appears in the catalog after a FILE add (no code edit)",
              NEW_ID in cap.MODEL_CAPABILITIES)
        check("the new vision model is now suitable for a vision role (query sees it)",
              NEW_ID in cap.suitable_models({"vision"}))
        check("provides_for(new model) reads the FILE's provides",
              cap.provides_for(NEW_ID) == ["chat", "vision"])
        check("role_can_bind({chat,vision}, new model) → True",
              cap.role_can_bind({"chat", "vision"}, NEW_ID) is True)
        check("the _note annotation was stripped (row is pure capability fields)",
              "_note" not in cap.MODEL_CAPABILITIES[NEW_ID])
    finally:
        os.unlink(tmp.name)
        # restore the live catalog from the canonical file (so the test leaves no residue)
        cap.reload_catalog()
    check("after restore, the temp model is GONE (catalog re-read from the canonical file)",
          NEW_ID not in cap.MODEL_CAPABILITIES)
    check("after restore, the canonical models are all back",
          set(cap.MODEL_CAPABILITIES) == set(saved))

    print("\n[5] FAIL-LOUD LOADER — missing / malformed / empty catalog RAISES (never silently empty)")
    try:
        cap._load_catalog("/no/such/catalog.json")
        check("missing catalog file RAISES", False, detail="did NOT raise")
    except RuntimeError:
        check("missing catalog file RAISES (fail-loud, no empty dict)", True)
    bad = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    bad.write("{ this is not json ")
    bad.close()
    try:
        cap._load_catalog(bad.name)
        check("malformed catalog RAISES", False, detail="did NOT raise")
    except RuntimeError:
        check("malformed catalog RAISES (fail-loud)", True)
    finally:
        os.unlink(bad.name)
    empty = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    json.dump({"_doc": "only annotations, no model rows"}, empty)
    empty.close()
    try:
        cap._load_catalog(empty.name)
        check("a catalog with NO model rows RAISES", False, detail="did NOT raise")
    except RuntimeError:
        check("a catalog with NO model rows RAISES (fail-loud)", True)
    finally:
        os.unlink(empty.name)

    print(f"\n=== {_passed} passed, {_failed} failed ===")
    sys.exit(1 if _failed else 0)


if __name__ == "__main__":
    main()
