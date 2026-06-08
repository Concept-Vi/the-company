"""tests/reduce_acceptance.py — Concurrent Cognition C 2/4 (the cross-unit REDUCE).

Proves run_reduce — the net-new cross-unit JOIN engine (`run_swarm` is map-only; the cross-unit join had
no mechanism). It wires the declared-but-dead `reduce-tree` THOUGHT_SHAPE (join="reduce") live. The bar:

  READ-BACK    — run_reduce reads the N map-output run:// addresses BACK via the canonical resolver
                 (resolve_run_ref — the run_jury read-back pattern, factored into _read_back), in a
                 STABLE order (deterministic, not finish-order dependent).
  ROLE  variant — the synthesize join: the N read-back outputs composed into ONE input fired through the
                 reduce-role (roles/reduce_synth.py) → ONE merged {summary}. Exercises the C 1/4 input-axis
                 compose path (ctx={"notes": composed}). LIVE against the resident 4B if up; else a mocked
                 transport captures the REAL compose+merge round-trip (never a false green).
  RULE  variant — the deterministic L2 join: a pure vote/merge rule over the 3 read-back values → the
                 correct result, IDENTICAL on replay (mirrors run_jury's verdict determinism). No model.
  CLUSTER variant — the embed-cluster discovery join: 3 units (2 near-duplicates + 1 distinct) → the 2
                 group, the 1 separate. SEEDED vectors (the embedder :8001 is not resident — DON'T evict
                 the live stack); the cosine-grouping is deterministic given vectors. The live-embed run is
                 pending the launch-capability (its first consumer). Order-independence asserted (replay).
  FAIL LOUD    — a missing/unresolvable map address RAISES (the run_swarm barrier discipline); a DECLARED
                 on_missing="skip" omits it (recorded in .skipped) — never a silent drop.
  REUSE        — the read-back is resolve_run_ref (shared with jury); the cosine is nodes/retrieve._cosine
                 (dim-mismatch fail-loud by reuse); the embed path is complete_embeddings; the input-axis
                 is run_role's compose. No parallel machinery.
"""
import json
import math
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from store.fs_store import FsStore                                  # noqa: E402
from runtime import cognition                                       # noqa: E402
from runtime.cognition import run_reduce, _read_back, _cluster_units, ReduceResult  # noqa: E402
from runtime.roles import RoleRegistry                              # noqa: E402

ROLES = os.path.join(ROOT, "roles")
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


def _seed(store, turn_id, units: dict) -> dict:
    """Seed N map outputs as run:// addresses (the WaveResult.addresses shape), exactly as run_swarm
    would have written them (put_content → set_ref). Returns {unit_id: run://addr}."""
    addresses = {}
    for uid, value in units.items():
        addr = f"run://{turn_id}/{uid}"
        cas = store.put_content(value)
        store.set_ref(addr, cas)
        addresses[uid] = addr
    return addresses


# =================================================================================================
# 0 · the reduce-role is discovered + fireable (the template lands in the registry)
# =================================================================================================
reg = RoleRegistry().discover([ROLES])
check("reduce_synth is discovered in the file-based role registry", "reduce_synth" in reg)
rsynth = reg["reduce_synth"]
check("reduce_synth can_fire (a generate role: prompt_template + output_schema)", rsynth.can_fire)
check("reduce_synth is op=generate (the default)", rsynth.op == "generate")
check("reduce_synth is in NO cast (fired explicitly via run_reduce, not listening)",
      not rsynth.mode_scope)
check("reduce_synth declares input_addresses=('notes',) (the composed N-outputs input)",
      tuple(rsynth.spec.get("input_addresses") or ()) == ("notes",))
check("reduce_synth emits NO resolve/approve/dispatch verb (operator-only floor)",
      all(k not in rsynth.spec for k in ("resolve", "approve", "dispatch", "verb")))


# =================================================================================================
# 1 · the SHARED read-back: stable order + fail-loud-on-missing (the run_jury pattern, factored)
# =================================================================================================
store = FsStore(os.path.join(tempfile.mkdtemp(prefix="reduce-"), "store"))
addrs = _seed(store, "t1", {
    "u_c": {"note": "third"}, "u_a": {"note": "first"}, "u_b": {"note": "second"},
})
read = _read_back(store, addrs)
check("read-back returns one (unit_id, addr, value) per seeded unit", len(read) == 3)
check("read-back is in STABLE unit_id order (sorted: u_a, u_b, u_c — NOT seed/finish order)",
      [t[0] for t in read] == ["u_a", "u_b", "u_c"])
check("read-back resolves the run:// addresses to their content",
      [t[2]["note"] for t in read] == ["first", "second", "third"])

# fail loud: a missing/unresolvable address RAISES (the run_swarm barrier discipline)
missing_addrs = dict(addrs)
missing_addrs["u_x"] = "run://t1/u_x"        # never written → head() is None
raised = False
try:
    _read_back(store, missing_addrs)
except RuntimeError:
    raised = True
check("a missing map address RAISES on read-back (fail loud, never a silent drop)", raised)

# a DECLARED skip omits it (never silent) — and run_reduce records it in .skipped
skipped = _read_back(store, missing_addrs, on_missing="skip")
check("a DECLARED on_missing='skip' omits the missing unit (4 declared → 3 read)", len(skipped) == 3)


# =================================================================================================
# 2 · RULE variant — the deterministic L2 join (no model), mirrors run_jury's verdict determinism
# =================================================================================================
store2 = FsStore(os.path.join(tempfile.mkdtemp(prefix="reduce-rule-"), "store"))
# 3 map outputs each a {label} classification — the rule is a MAJORITY VOTE over them (a real join job).
vote_addrs = _seed(store2, "t2", {
    "u1": {"label": "wired"}, "u2": {"label": "wired"}, "u3": {"label": "orphan"},
})


def majority_label(values: list) -> dict:
    """A PURE deterministic reduce rule — majority vote over the N units' labels (vote/merge/select).
    Mirrors run_jury's verdict_rule shape: a callable over the list, deterministic, no model call."""
    from collections import Counter
    counts = Counter(v["label"] for v in values)
    # deterministic tiebreak: highest count, then alphabetical (never arrival-order dependent)
    winner = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[0]
    return {"winner": winner[0], "counts": dict(counts), "n": len(values)}


r_rule = run_reduce(vote_addrs, store2, turn_id="t2", mode="rule", reduce_rule=majority_label)
check("rule variant returns a ReduceResult", isinstance(r_rule, ReduceResult))
check("rule variant computes the correct majority winner (wired: 2, orphan: 1)",
      r_rule.joined["winner"] == "wired" and r_rule.joined["counts"] == {"wired": 2, "orphan": 1})
# REPLAY: identical inputs → identical result (the jury determinism — counts, not finish order)
r_rule2 = run_reduce(vote_addrs, store2, turn_id="t2", mode="rule", reduce_rule=majority_label)
check("rule variant is REPLAY-IDENTICAL (deterministic, like the jury verdict)",
      r_rule2.joined == r_rule.joined)
# order-independence: the SAME 3 units passed as a different mapping iteration → SAME verdict
reordered = {"u3": vote_addrs["u3"], "u1": vote_addrs["u1"], "u2": vote_addrs["u2"]}
r_rule3 = run_reduce(reordered, store2, turn_id="t2", mode="rule", reduce_rule=majority_label)
check("rule variant does NOT depend on input order (reordered units → same verdict)",
      r_rule3.joined == r_rule.joined)


# =================================================================================================
# 3 · CLUSTER variant — the embed-cluster discovery join (SEEDED vectors; embedder :8001 not resident)
# =================================================================================================
store3 = FsStore(os.path.join(tempfile.mkdtemp(prefix="reduce-cluster-"), "store"))
# 3 units: u_dup1 + u_dup2 are near-duplicates ("the same"); u_distinct is separate.
clu_addrs = _seed(store3, "t3", {
    "u_dup1":     {"text": "the storage layer is content-addressed on ext4"},
    "u_dup2":     {"text": "storage stays content-addressed, ext4 substrate"},
    "u_distinct": {"text": "the voice circuit streams sentence-by-sentence"},
})

# SEEDED vectors: the embedder is NOT resident (do NOT evict the live stack). The cosine-grouping is
# deterministic given vectors, so the cluster LOGIC is proven on precomputed vectors. The live-embed
# run is pending the launch-capability (its first consumer). Vectors chosen so u_dup1·u_dup2 cosine is
# high (near-1) and either-vs-u_distinct is low (near-0). Order matches sorted unit_id: u_distinct,
# u_dup1, u_dup2 (the _cluster_units sort) — but we provide a text->vector map so order can't fool it.
# NOTE the cluster embeds each unit's _reduce_embed_text — which for a dict is the stable JSON string
# (json.dumps(value, sort_keys=True)), NOT the bare inner text. So the seeded map is keyed on that exact
# rendered form (the contract the live embedder would also receive).
def _rendered(value):
    return json.dumps(value, sort_keys=True)


_SEED_VECS = {
    _rendered({"text": "the storage layer is content-addressed on ext4"}):  [1.0, 0.05, 0.0],
    _rendered({"text": "storage stays content-addressed, ext4 substrate"}): [0.98, 0.10, 0.0],  # ~dup1 dir
    _rendered({"text": "the voice circuit streams sentence-by-sentence"}):  [0.0, 0.05, 1.0],   # distinct
}


def seeded_embed(texts):
    """Inject SEEDED vectors (the embedder-down path — mirrors vector_index.build_index's embed_fn seam).
    Looks each rendered unit up in the precomputed map → deterministic. Fail loud on an un-seeded text."""
    out = []
    for t in texts:
        if t not in _SEED_VECS:
            raise KeyError(f"seeded_embed: no seeded vector for text {t!r} — fail loud (never a zero vector).")
        out.append(_SEED_VECS[t])
    return out


# sanity: the seeded cosines really do separate (the test's premise is sound)
def _cos(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)); nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb)


dup_cos = _cos(_SEED_VECS[_rendered({"text": "the storage layer is content-addressed on ext4"})],
               _SEED_VECS[_rendered({"text": "storage stays content-addressed, ext4 substrate"})])
dist_cos = _cos(_SEED_VECS[_rendered({"text": "the storage layer is content-addressed on ext4"})],
                _SEED_VECS[_rendered({"text": "the voice circuit streams sentence-by-sentence"})])
check(f"seeded vectors separate: dup cosine ({dup_cos:.3f}) >> distinct cosine ({dist_cos:.3f})",
      dup_cos > 0.9 and dist_cos < 0.5)

r_clu = run_reduce(clu_addrs, store3, turn_id="t3", mode="cluster",
                   cluster_threshold=0.85, embed_fn=seeded_embed)
clusters = r_clu.joined["clusters"]
# normalize for comparison: sort each cluster + sort the cluster list
norm = sorted([sorted(c) for c in clusters])
check("cluster variant returns a ReduceResult", isinstance(r_clu, ReduceResult))
check("cluster variant groups the 2 near-duplicates together + the 1 distinct separate (2 clusters)",
      norm == [["u_distinct"], ["u_dup1", "u_dup2"]])
check("cluster variant reports k=2 clusters", r_clu.joined["k"] == 2)

# REPLAY / order-independence: a different input order → identical clustering (deterministic grouping)
clu_reordered = {"u_distinct": clu_addrs["u_distinct"], "u_dup2": clu_addrs["u_dup2"],
                 "u_dup1": clu_addrs["u_dup1"]}
r_clu2 = run_reduce(clu_reordered, store3, turn_id="t3", mode="cluster",
                    cluster_threshold=0.85, embed_fn=seeded_embed)
norm2 = sorted([sorted(c) for c in r_clu2.joined["clusters"]])
check("cluster variant is REPLAY-IDENTICAL / order-independent (reordered units → same clusters)",
      norm2 == norm)

# dim-mismatch fail-loud BY REUSE (nodes/retrieve._cosine raises) — not a wrong-but-plausible cosine
def bad_dim_embed(texts):
    return [[1.0, 0.0, 0.0], [1.0, 0.0], [0.0, 1.0, 0.0]][:len(texts)]  # second vector is wrong dim


dim_raised = False
try:
    _cluster_units([("a", "x", {"text": "p"}), ("b", "y", {"text": "q"}), ("c", "z", {"text": "r"})],
                   threshold=0.85, embed_fn=lambda ts: [[1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
except ValueError:
    dim_raised = True
check("cluster variant FAILS LOUD on a vector dim mismatch (reuse of nodes/retrieve._cosine)", dim_raised)


# =================================================================================================
# 4 · ROLE variant — the synthesize join (the C 1/4 input-axis compose path)
# =================================================================================================
store4 = FsStore(os.path.join(tempfile.mkdtemp(prefix="reduce-role-"), "store"))
role_addrs = _seed(store4, "t4", {
    "u1": {"note": "storage is content-addressed on ext4"},
    "u2": {"note": "storage is durable across crashes"},
    "u3": {"note": "storage is keyed by address, one substrate"},
})

# mode error: a missing reduce-role RAISES (fail loud)
role_err = False
try:
    run_reduce(role_addrs, store4, turn_id="t4", mode="role", role=None)
except ValueError:
    role_err = True
check("role variant FAILS LOUD when no reduce-role is passed", role_err)

# unknown mode fail-loud
mode_err = False
try:
    run_reduce(role_addrs, store4, turn_id="t4", mode="bogus")
except ValueError:
    mode_err = True
check("an unknown join mode RAISES (no silent default branch)", mode_err)


# the LIVE-or-MOCKED reduce-role synthesize. Try the resident 4B; if down, mock the transport so the
# REAL compose + run_role + schema-validate round-trip is captured (never a false green).
def _try_live():
    from fabric import transport, client
    t = transport.openai_transport(base_url=cognition.RESIDENT_BASE_URL, timeout=8)
    # a cheap liveness probe via the real complete (a 1-token-ish call); raise if down.
    client.complete(t, [{"role": "user", "content": "ok"}], model=cognition.RESIDENT_MODEL,
                    json=False, max_tokens=1, temperature=0.0)


live = True
try:
    _try_live()
except Exception as e:
    live = False
    print(f"  ..  resident 4B not up ({type(e).__name__}) — proving the reduce-role on a MOCKED transport")

if live:
    r_role = run_reduce(role_addrs, store4, turn_id="t4", mode="role", role=rsynth)
    check("role variant (LIVE 4B) returns ONE merged {summary}",
          isinstance(r_role.joined, dict) and isinstance(r_role.joined.get("summary"), str)
          and len(r_role.joined["summary"]) > 0)
    check("role variant detail records the N units joined + the role id",
          r_role.detail["n_units"] == 3 and r_role.detail["role"] == "reduce_synth")
else:
    # MOCK the fabric transport so the compose + run_role + schema-validate path is exercised for real.
    # We patch client.complete to (a) ASSERT the composed N-outputs reached the user message (the C 1/4
    # compose path), and (b) return a schema-valid ReduceSynthOut. This captures the REAL merge wiring.
    from fabric import client as _client
    captured = {}

    class _Validated:
        def __init__(self, d): self._d = d
        def model_dump(self): return dict(self._d)

    orig_complete = _client.complete

    def _mock_complete(t, msgs, *, model, schema=None, json=False, temperature=0.0, max_tokens=256, **kw):
        captured["user"] = msgs[-1]["content"]
        captured["system"] = msgs[0]["content"]
        return _Validated({"summary": "merged: storage is content-addressed, durable, address-keyed."})

    cognition.client.complete = _mock_complete
    try:
        r_role = run_reduce(role_addrs, store4, turn_id="t4", mode="role", role=rsynth)
    finally:
        cognition.client.complete = orig_complete

    check("role variant (mocked) returns ONE merged {summary} (the real compose+validate path)",
          r_role.joined == {"summary": "merged: storage is content-addressed, durable, address-keyed."})
    # the C 1/4 compose path: the N read-back outputs are each labelled [unit_id] in the user message
    check("role variant composes the N map outputs into the role's input (C 1/4 input-axis compose)",
          all(f"[{u}]" in captured["user"] for u in ("u1", "u2", "u3")))
    check("role variant uses the reduce-role's prompt_template as the system message",
          "REDUCE role" in captured["system"])
    check("role variant detail records the N units joined + the role id",
          r_role.detail["n_units"] == 3 and r_role.detail["role"] == "reduce_synth")


# =================================================================================================
# 5 · run_reduce is a DRIVER, not an agent: an emit rollup carries no resolve/approve/dispatch
# =================================================================================================
events = []
run_reduce(vote_addrs, store2, turn_id="t2", mode="rule", reduce_rule=majority_label,
           emit=lambda kind, payload: events.append((kind, payload)))
check("run_reduce emits ONE cognition.reduce rollup (C1.6 batched discipline)",
      len(events) == 1 and events[0][0] == "cognition.reduce")
check("the reduce rollup carries NO resolve/approve/dispatch (operator-only floor)",
      all(k not in events[0][1] for k in ("resolve", "approve", "dispatch", "verb")))


print(f"\nALL {PASS} CHECKS PASS — run_reduce: read-back (shared with jury) · rule (deterministic) · "
      f"cluster (seeded vectors, embedder-down) · role (live-or-mocked synthesize) · fail-loud · driver-only")
