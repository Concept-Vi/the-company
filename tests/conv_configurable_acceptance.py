"""tests/conv_configurable_acceptance.py — X17 · the composition is configurable (Convergence, D2).

WHAT X17 IS (Tim's refinement: configurable, NOT predefined single values):
the R2 composition's knobs — the ranking WEIGHTS (recency λ · proximity · pin · semantic), the
window BUDGET cap, and the run-versions bound — were hardcoded class constants in suite.py. X17 makes
them CONFIG-RESOLVED (env, with the OLD constants preserved as the defaults), so retuning the context
composition needs NO code change. Registry-is-truth; defaults are the floor, not the ceiling. The knobs
are exposed via `capabilities()` so the future fleet/config surface can READ them.

THE KNOBS + their env vars (the old constant becomes the default — byte-for-behaviour when unset):
  COMPANY_R2_LAMBDA            → R2_LAMBDA            (float, default 1/(3·24·3600))
  COMPANY_R2_PROXIMITY_WEIGHT  → R2_PROXIMITY_WEIGHT  (float, default 1.0)
  COMPANY_R2_PIN_WEIGHT        → R2_PIN_WEIGHT        (float, default 1.0)
  COMPANY_R2_SEMANTIC_WEIGHT   → R2_SEMANTIC_WEIGHT   (float, default 1.0)
  COMPANY_R2_BUDGET            → R2_BUDGET            (int,   default 4000)
  COMPANY_R2_RUN_VERSIONS      → R2_RUN_VERSIONS      (int,   default 3)

DESIGN (proven here): the env is read in __init__ INTO INSTANCE attributes (the class-level constants
remain as the DEFAULT FLOOR). So a FRESH Suite() with the env set picks up the new value (a config change
alters behaviour, no code change), while Suite.R2_BUDGET (class access, used by sibling suites) and
`su.R2_BUDGET = …` (instance override, used by conv_semantic_rank) both still work. Reads at construction
satisfy the criterion "a fresh Suite/process picking up the env is sufficient" (a restart re-reads).

WHAT THIS PROVES:
  1. DEFAULTS — with NO env set, every knob == its documented default (behaviour unchanged when unset).
  2. CONFIG ALTERS BEHAVIOUR (no code change) — set COMPANY_R2_BUDGET tiny → a fresh Suite drops MORE
     items at the cap; set COMPANY_R2_SEMANTIC_WEIGHT → _r2_score's semantic term scales by it.
  3. capabilities() EXPOSES the current knob values (registry-is-truth; the surface can read them).
  4. A MALFORMED env value (non-float / non-int) → FAILS LOUD with a clear, knob-named error — never a
     silent wrong/zero value (rule 4).
  5. PRESERVE — the R2 score FORMULA is unchanged: with defaults, _r2_score is byte-for-byte the old
     recency·proximity·pin(+semantic) score; the cap still bounds.

These run WITHOUT a live model — _r2_score / _r2_score_and_cap / __init__ are deterministic; we never
call chat()/consult()/the embedder. COMPANY_TEST_RUN is set for inbox-hygiene parity with the siblings.
"""
import os, sys, tempfile, shutil, math
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ["COMPANY_TEST_RUN"] = "1"

# Ensure a CLEAN slate: none of the X17 env vars set at import (the DEFAULTS case must be honest).
for _k in ("COMPANY_R2_LAMBDA", "COMPANY_R2_PROXIMITY_WEIGHT", "COMPANY_R2_PIN_WEIGHT",
           "COMPANY_R2_SEMANTIC_WEIGHT", "COMPANY_R2_BUDGET", "COMPANY_R2_RUN_VERSIONS"):
    os.environ.pop(_k, None)

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite

NODES = os.path.join(ROOT, "nodes")
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


def expect_raises(label, fn):
    global PASS
    try:
        fn()
    except Exception:
        PASS += 1
        print(f"  ok  {label}")
        return
    assert False, f"FAIL (did not raise): {label}"


LOCUS = "ui://chrome/inbox"

# Documented defaults (the old constants — what behaviour must be when no env is set).
DEFAULT_LAMBDA = 1.0 / (3 * 24 * 3600)
DEFAULT_PROXIMITY = 1.0
DEFAULT_PIN = 1.0
DEFAULT_SEMANTIC = 1.0
DEFAULT_BUDGET = 4000
DEFAULT_RUN_VERSIONS = 3

store_dir = tempfile.mkdtemp(prefix="conv-configurable-test-")
try:
    root = os.path.join(store_dir, "store")
    reg = NodeRegistry(); reg.discover([NODES])

    def new_suite(sub):
        return Suite(FsStore(os.path.join(root, sub)), reg, nodes_dir=NODES)

    print("\n── 1. DEFAULTS: no env → every knob == its documented default (behaviour unchanged) ──")
    s0 = new_suite("defaults")
    check("default R2_LAMBDA == 1/(3·24·3600)", abs(s0.R2_LAMBDA - DEFAULT_LAMBDA) < 1e-15)
    check("default R2_PROXIMITY_WEIGHT == 1.0", abs(s0.R2_PROXIMITY_WEIGHT - DEFAULT_PROXIMITY) < 1e-12)
    check("default R2_PIN_WEIGHT == 1.0", abs(s0.R2_PIN_WEIGHT - DEFAULT_PIN) < 1e-12)
    check("default R2_SEMANTIC_WEIGHT == 1.0", abs(s0.R2_SEMANTIC_WEIGHT - DEFAULT_SEMANTIC) < 1e-12)
    check("default R2_BUDGET == 4000", s0.R2_BUDGET == DEFAULT_BUDGET)
    check("default R2_RUN_VERSIONS == 3", s0.R2_RUN_VERSIONS == DEFAULT_RUN_VERSIONS)
    check("defaults are the right NUMERIC TYPES (int budget/versions, float weights)",
          isinstance(s0.R2_BUDGET, int) and isinstance(s0.R2_RUN_VERSIONS, int)
          and isinstance(s0.R2_LAMBDA, float) and isinstance(s0.R2_SEMANTIC_WEIGHT, float))
    # Class-level access still resolves to the default floor (sibling suites use Suite.R2_BUDGET).
    check("PRESERVE: Suite.R2_BUDGET (class access) still resolves to the default 4000",
          Suite.R2_BUDGET == DEFAULT_BUDGET)

    print("\n── 2a. CONFIG ALTERS BEHAVIOUR: COMPANY_R2_BUDGET tiny → a fresh Suite drops MORE at the cap ──")
    now = datetime.now(timezone.utc)
    def iso(dt): return dt.isoformat()
    # Three same-address, equal-recency items so ordering is stable; each ~20 chars of text.
    items = [
        {"text": "AAAAAAAAAAAAAAAAAAAA", "address": LOCUS, "ts": iso(now), "kind": "annotation"},
        {"text": "BBBBBBBBBBBBBBBBBBBB", "address": LOCUS, "ts": iso(now - timedelta(seconds=1)), "kind": "annotation"},
        {"text": "CCCCCCCCCCCCCCCCCCCC", "address": LOCUS, "ts": iso(now - timedelta(seconds=2)), "kind": "annotation"},
    ]
    # default budget keeps all three (60 chars << 4000)
    kept_default = s0._r2_score_and_cap([dict(it) for it in items], LOCUS, now)
    check("default budget (4000) keeps all 3 small items (60 chars << 4000)", len(kept_default) == 3)
    # set a tiny budget via env → a FRESH Suite picks it up, no code change → drops more
    os.environ["COMPANY_R2_BUDGET"] = "25"
    try:
        s_tiny = new_suite("tiny_budget")
        check("config: a fresh Suite reads COMPANY_R2_BUDGET=25 (no code change)", s_tiny.R2_BUDGET == 25)
        kept_tiny = s_tiny._r2_score_and_cap([dict(it) for it in items], LOCUS, now)
        check("config ALTERS BEHAVIOUR: the tiny budget drops MORE items than the default",
              len(kept_tiny) < len(kept_default))
        check("config ALTERS BEHAVIOUR: a 25-char budget keeps exactly ONE 20-char item",
              len(kept_tiny) == 1)
    finally:
        os.environ.pop("COMPANY_R2_BUDGET", None)

    print("\n── 2b. CONFIG ALTERS BEHAVIOUR: COMPANY_R2_SEMANTIC_WEIGHT scales the semantic term ──")
    one = {"text": "x", "address": LOCUS, "ts": iso(now), "kind": "annotation"}
    base_no_sem = s0._r2_score(one, LOCUS, now, semantic=0.0)
    # default weight 1.0: a 0.5 cosine adds 1.0·0.5
    score_default = s0._r2_score(one, LOCUS, now, semantic=0.5)
    check("default semantic weight 1.0: score(sem=0.5) == base + 1.0·0.5",
          abs(score_default - (base_no_sem + DEFAULT_SEMANTIC * 0.5)) < 1e-9)
    os.environ["COMPANY_R2_SEMANTIC_WEIGHT"] = "4.0"
    try:
        s_sem = new_suite("sem_weight")
        check("config: a fresh Suite reads COMPANY_R2_SEMANTIC_WEIGHT=4.0", abs(s_sem.R2_SEMANTIC_WEIGHT - 4.0) < 1e-12)
        score_bumped = s_sem._r2_score(one, LOCUS, now, semantic=0.5)
        check("config ALTERS BEHAVIOUR: the semantic term scales by the configured weight (4.0·0.5)",
              abs(score_bumped - (base_no_sem + 4.0 * 0.5)) < 1e-9)
        check("config ALTERS BEHAVIOUR: a higher semantic weight raises the score (relevance matters more)",
              score_bumped > score_default)
    finally:
        os.environ.pop("COMPANY_R2_SEMANTIC_WEIGHT", None)
    # zero semantic weight removes the semantic term entirely
    os.environ["COMPANY_R2_SEMANTIC_WEIGHT"] = "0"
    try:
        s_zero = new_suite("sem_zero")
        check("config: COMPANY_R2_SEMANTIC_WEIGHT=0 → the semantic term is removed (score == base, any cosine)",
              abs(s_zero._r2_score(one, LOCUS, now, semantic=0.9) - base_no_sem) < 1e-9)
    finally:
        os.environ.pop("COMPANY_R2_SEMANTIC_WEIGHT", None)

    print("\n── 3. capabilities() EXPOSES the current knob values (registry-is-truth) ──")
    cap = s0.capabilities()
    check("capabilities() carries a composition_config map", "composition_config" in cap)
    cc = cap["composition_config"]
    check("composition_config exposes R2_LAMBDA", abs(cc["R2_LAMBDA"] - DEFAULT_LAMBDA) < 1e-15)
    check("composition_config exposes R2_PROXIMITY_WEIGHT", abs(cc["R2_PROXIMITY_WEIGHT"] - DEFAULT_PROXIMITY) < 1e-12)
    check("composition_config exposes R2_PIN_WEIGHT", abs(cc["R2_PIN_WEIGHT"] - DEFAULT_PIN) < 1e-12)
    check("composition_config exposes R2_SEMANTIC_WEIGHT", abs(cc["R2_SEMANTIC_WEIGHT"] - DEFAULT_SEMANTIC) < 1e-12)
    check("composition_config exposes R2_BUDGET", cc["R2_BUDGET"] == DEFAULT_BUDGET)
    check("composition_config exposes R2_RUN_VERSIONS", cc["R2_RUN_VERSIONS"] == DEFAULT_RUN_VERSIONS)
    # the exposed values track a configured instance (registry-is-truth, not a hardcoded echo)
    os.environ["COMPANY_R2_BUDGET"] = "1234"
    try:
        s_cfg = new_suite("cap_cfg")
        check("composition_config reflects the LIVE configured value (not a hardcoded default echo)",
              s_cfg.capabilities()["composition_config"]["R2_BUDGET"] == 1234)
    finally:
        os.environ.pop("COMPANY_R2_BUDGET", None)

    print("\n── 4. MALFORMED env → FAILS LOUD (clear, knob-named error), never a silent wrong value ──")
    os.environ["COMPANY_R2_BUDGET"] = "not-a-number"
    try:
        expect_raises("a non-int COMPANY_R2_BUDGET fails loud at construction", lambda: new_suite("bad_budget"))
    finally:
        os.environ.pop("COMPANY_R2_BUDGET", None)
    os.environ["COMPANY_R2_SEMANTIC_WEIGHT"] = "abc"
    try:
        expect_raises("a non-float COMPANY_R2_SEMANTIC_WEIGHT fails loud at construction",
                      lambda: new_suite("bad_sem"))
    finally:
        os.environ.pop("COMPANY_R2_SEMANTIC_WEIGHT", None)
    # the error must NAME the knob (a clear error, not a bare ValueError from float())
    os.environ["COMPANY_R2_LAMBDA"] = "xyz"
    try:
        try:
            new_suite("bad_lambda")
            assert False, "FAIL: bad COMPANY_R2_LAMBDA did not raise"
        except Exception as e:
            check("the fail-loud error NAMES the offending knob (clear, not a bare float() message)",
                  "COMPANY_R2_LAMBDA" in str(e))
    finally:
        os.environ.pop("COMPANY_R2_LAMBDA", None)

    print("\n── 5. PRESERVE: the _r2_score FORMULA is unchanged with defaults (byte-for-byte) ──")
    # recompute the documented formula by hand and compare to _r2_score on a synthetic item.
    it = {"text": "Z", "address": "ui://chrome", "ts": iso(now - timedelta(seconds=10)), "kind": "annotation", "pinned": True}
    delta = 10.0
    recency = math.exp(-DEFAULT_LAMBDA * delta)
    proximity = Suite.address_tree_distance(LOCUS, "ui://chrome")  # parent → 1
    expected = recency * (1.0 / (1.0 + DEFAULT_PROXIMITY * proximity)) + DEFAULT_PIN + DEFAULT_SEMANTIC * 0.3
    got = s0._r2_score(it, LOCUS, now, semantic=0.3)
    check("PRESERVE: _r2_score with defaults == the hand-computed recency·proximity·pin+semantic formula",
          abs(got - expected) < 1e-9)
    check("PRESERVE: the budget cap still bounds (≤ R2_BUDGET) with defaults",
          sum(len(x.get("text", "") or "") for x in kept_default) <= s0.R2_BUDGET)

    print(f"\nALL {PASS} CHECKS PASSED — X17 · the composition is configurable")
finally:
    shutil.rmtree(store_dir, ignore_errors=True)
