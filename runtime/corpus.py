"""runtime/corpus.py — the corpus-record WITH LINEAGE (Cognition Engine D1 · the sequencing GATE).

The scale test (COMPLETION-CRITERIA Group D) digested 427 files and DISCARDED the output: the engine
produces at scale with no place for output to LIVE + be reused. The corpus-record is that place. A
capture/map run over a corpus produces, per unit (or per unit×projection), a RECORD that is durable,
addressed, embeddable, and queryable — a PROJECTION over the store, NOT a new DB.

## LINEAGE is a sequencing GATE, not a nice-to-have (PART 4.7 — the headline)
The record carries `session/round/project` lineage **FROM THE START** — and the writer REFUSES a record
that lacks it (fail-loud, NOT optional-with-default). Why a gate and not an optional field: corroboration
(M3) is CROSS-SESSION (high recurrence of a principle ACROSS sessions = a corroboration mark), and the
inversion-finder (L2) needs to know which session/round/project a record came from. A record written
WITHOUT lineage can never be corroborated cross-session — so retrofitting lineage after a capture run is
a full re-capture. An optional-with-default field would silently reproduce exactly the failure the gate
exists to prevent (a record that looks fine but is uncorroboratable). So lineage is REQUIRED at write.

## Three distinct "lineage" axes — DO NOT conflate (the advisor's correctness pivot)
1. **corpus lineage** (THIS module): `session/round/project` — the CAPTURE provenance (which run, which
   round, which project produced this record). Rides IN the cas record content. NEVER routed through
   `write_provenance`.
2. **store provenance-lineage** (`store.lineage()`): the inputs an artefact was made FROM (the C1/C4
   provenance walk). A DIFFERENT axis — untouched here.
3. **decision-lineage** (`decision_view`): the event-trajectory reconstruction of a decision. Also distinct.
Same word, three axes. The corpus-record's `lineage` is axis 1 only.

## A THIN module over the store — NO fs_store edit (STORE lane owns it)
This wraps the store's EXISTING public methods — `put_content` (write-once immutable cas://) +
`set_ref` (the mutable run:// pointer, atomic + crash-durable + version-history) + `append_event`
(the durable index) + `get_content`/`head`/`events_since` (read-back + projection). It edits NEITHER
`store/fs_store.py` NOR `store/vector_index.py` (the STORE lane owns those — the space-keyed vectors +
the marks generalization land there). Embed-on-write (D2) is a CALL the SUITE/ENGINE lane makes after
the record exists; this module just persists + indexes the record.

## The index is a `corpus.record` EVENT, NOT `op.run` (the second correctness pivot)
A corpus record is NOT an engine run — `ENGINE_RUN_OPS` (suite.py) is a CLOSED grammar
(`cognition.run_role`/`run_items`/`run_reduce`); emitting `op.run` with a non-member op would break that
closed set AND pull this module into suite.py's lane. So the corpus index rides a DISTINCT durable event
kind, `corpus.record`, on the SAME ONE event log (`store.append_event`) — the SAME "the log IS the index,
no maintained index, no new store" pattern the run-index uses (#54), but its own kind. `list_corpus` /
`find_corpus` are a READ-TIME PROJECTION over `events_since(-1)` filtered to `kind=="corpus.record"`
(the run_stats sibling) — no maintained index, no parallel DB. The Suite-level convenience methods
(list/query exposed to faces) are the SUITE lane consuming THIS module's read helpers.

## Resume-safety / single-writer (the restored discipline, PART 4.7)
A capture run is resumable: re-writing the SAME record (same source_address + same output + same lineage)
is IDEMPOTENT on the content side — `put_content` is write-once (same JSON → same cas, no duplicate
object) and the logical `run://` address is DETERMINISTIC (`corpus_address(...)`), so a re-run overwrites
the same pointer with the same cas (no-op effect). The dedup-on-READ (mirroring the findings reconcile)
folds duplicate `corpus.record` events by their corpus address (latest cas wins) so a resumed run never
double-counts. No new lock is built — `set_ref`/`append_event` already ride the store's fcntl + atomic
writes (STORE lane's guarantees, behind the resolver seam — PORTABILITY: a Supabase backend implements
the SAME methods).

LAWS honoured: fail loud (lineage REQUIRED at write — the gate) · reuse-don't-parallel (the store's
EXISTING public methods + the run-index event pattern — no fs_store edit, no new DB) · the floor
(`corpus.record` is telemetry/index — append_event, NEVER a resolve/approve/dispatch) · schema-additive
(the record is an OPEN dict — `{ts, **}` — extra fields ride free) · introspective-data-building (a
capture self-instruments via the durable record).
"""
from __future__ import annotations

from typing import Any


# The corpus-record fields. `source_address` · `output` · `kind` · `lineage` are REQUIRED;
# `model`/`projection` are optional (a code-lifter record has no model; a single-pass record has no
# projection). `ts` is stamped by the writer. An unknown field is allowed (open record — schema-additive),
# but the REQUIRED set is enforced fail-loud (the D1 contract).
REQUIRED_RECORD_FIELDS = ("source_address", "output", "kind", "lineage")

# The lineage axes the GATE enforces (PART 4.7). All three REQUIRED — a record missing ANY of them is
# uncorroboratable cross-session, so it is REFUSED at write (never written with a silent default).
LINEAGE_FIELDS = ("session", "round", "project")

# The distinct durable event kind that indexes corpus records (NOT op.run — see module docstring).
CORPUS_EVENT_KIND = "corpus.record"


class CorpusError(ValueError):
    """A corpus-record violated the D1 contract (missing lineage / missing required field) — fail loud,
    never a silently-defaulted record (the sequencing gate, PART 4.7)."""


def corpus_address(source_address: str, *, project: str, projection: str | None = None) -> str:
    """The DETERMINISTIC logical run:// address a corpus record is written to (resume-safe — a re-run
    writes the SAME address). Keyed by project + source + (optional) projection so:
      • the same unit captured under two PROJECTIONS gets two distinct records (per-projection capture, K2);
      • the same unit re-captured (resume) overwrites the SAME pointer (idempotent on the content side —
        put_content write-once means same output → same cas → a no-op overwrite).
    run:// is the registered scheme for a mutable pointer (contracts/address.py); the corpus record is a
    durable addressed artefact, NOT a per-turn role output, so it lives under a `corpus/` domain to keep it
    distinct from `run://<turn>/<role>` (the engine-run namespace). NEVER swarm:// (not a scheme)."""
    suffix = f"/{projection}" if projection else ""
    return f"run://corpus/{project}/{source_address}{suffix}"


def _validate_lineage(lineage: Any) -> dict:
    """FAIL LOUD if lineage is missing/malformed/incomplete — THE sequencing gate (PART 4.7). A record
    without all three axes (session/round/project) can never be corroborated cross-session, so it is
    REFUSED here, before any write. This is NOT optional-with-default on purpose: a silent default would
    reproduce exactly the uncorroboratable-record failure the gate exists to prevent."""
    if not isinstance(lineage, dict):
        raise CorpusError(
            f"corpus-record lineage must be a dict carrying {list(LINEAGE_FIELDS)} (the sequencing gate — "
            f"corroboration is cross-SESSION, so lineage is REQUIRED from the start, never defaulted). "
            f"Got {type(lineage).__name__}.")
    missing = [k for k in LINEAGE_FIELDS if not lineage.get(k)]
    if missing:
        raise CorpusError(
            f"corpus-record lineage is missing required axis/axes {missing} — a record without "
            f"session/round/project is UNCORROBORATABLE cross-session (M3) and the inversion-finder (L2) "
            f"can't place it. Lineage is the sequencing GATE: supply all of {list(LINEAGE_FIELDS)} at write "
            f"(fail loud — never a silent default that looks fine but can't be corroborated).")
    # normalize to str (a round may be passed as int) — keep only the three axes plus any extra the caller
    # carried (open/additive), but the three are guaranteed present + truthy here.
    out = dict(lineage)
    for k in LINEAGE_FIELDS:
        out[k] = str(out[k])
    return out


def write_record(store, *, source_address: str, output: Any, kind: str, lineage: dict,
                 model: str | None = None, projection: str | None = None, **extra) -> dict:
    """Persist ONE corpus record (D1) — durable (cas://), addressed (a deterministic run://), and indexed
    (a `corpus.record` durable event). REFUSES a record missing lineage (the gate). Returns the indexed
    event record `{seq, ts, cas, address, source_address, kind, model, projection, lineage, ...}`.

    Reuse-don't-parallel: uses ONLY the store's existing public methods (put_content/set_ref/append_event)
    — no fs_store edit, no new DB. The floor: the index event is telemetry, never a resolve/dispatch."""
    if not source_address or not isinstance(source_address, str):
        raise CorpusError(
            f"corpus-record needs a string `source_address` (the unit this record describes — the retrieval "
            f"key). Got {source_address!r} — fail loud.")
    # G18 (fail-loud at the boundary, not a raw OSError downstream): the source_address is a RETRIEVAL KEY
    # (a short ADDRESS — e.g. `code://suite/run_role`, a file path, a unit id), NOT the unit's content. It
    # becomes the corpus run:// address → a ref FILENAME (store.set_ref → _safe), so a content-blob passed
    # as source_address overflows the filename ([Errno 36] File name too long). Guard it here with guidance:
    # content goes in `output`; source_address names WHAT the record describes. (A path/address is well under
    # this; the bound is generous so any legitimate address passes, only content-blobs trip it.)
    if len(source_address) > 200 or "\n" in source_address:
        raise CorpusError(
            f"corpus-record `source_address` looks like CONTENT, not a retrieval key (len={len(source_address)}"
            f"{', has newlines' if chr(10) in source_address else ''}). It is the ADDRESS the record is keyed by "
            f"(it becomes the run:// corpus address → a ref filename), so it must be a SHORT key — a file path, "
            f"a `code://<file>/<symbol>`, or a unit id. Put the file/unit CONTENT in `output`, and pass its "
            f"address/path as `source_address`. (Capturing repo files: source_address=the path, output=the digest.)")
    if not kind or not isinstance(kind, str):
        raise CorpusError(
            f"corpus-record needs a string `kind` (what KIND of record — e.g. 'capture'/'reduce'/'lift'). "
            f"Got {kind!r} — fail loud.")
    if output is None:
        raise CorpusError(
            "corpus-record `output` is None — a record with no output is empty; fail loud "
            "(never persist an empty record as if a capture succeeded).")
    lin = _validate_lineage(lineage)        # THE GATE (fail-loud before any write)

    address = corpus_address(source_address, project=lin["project"], projection=projection)
    # the record content (rides IN the cas — lineage travels WITH the artefact, cross-session-readable).
    # Open/additive: extra fields ride free (schema-additive — store constitution).
    # DETERMINISTIC CONTENT for resume-safety (put_content write-once): the cas record carries ONLY the
    # content axes (source/output/kind/model/projection/lineage) — NO per-write timestamp. A re-written
    # SAME record therefore hashes to the SAME cas (a true no-op overwrite on resume). The write-TIME (`ts`)
    # is event/index metadata, stamped by append_event on the index event below (the log's own `ts`), NOT
    # in the content — provenance-of-the-write belongs on the event, not the content-addressed artefact.
    record = {
        "source_address": source_address,
        "output": output,
        "kind": kind,
        "model": model,
        "projection": projection,
        "lineage": lin,
        **extra,
    }
    cas = store.put_content(record)         # write-once immutable (resume-safe: same record → same cas)
    store.set_ref(address, cas)             # deterministic pointer (resume-safe: re-run overwrites same)
    # INDEX via a DISTINCT durable event kind (NOT op.run — that's a closed engine-run grammar). The log
    # IS the index (#54 pattern, its own kind) — no maintained index, no new store.
    ev = store.append_event({
        "kind": CORPUS_EVENT_KIND,
        "cas": cas,
        "address": address,
        "source_address": source_address,
        "record_kind": kind,
        "model": model,
        "projection": projection,
        "lineage": lin,
    })
    return {**ev, "cas": cas, "address": address}


def read_record(store, address: str) -> dict | None:
    """Read a corpus record back by its run:// address (head → get_content; REUSE the canonical resolver
    path). None if never written (an HONEST None — never a crash, never a fabricated record). The
    round-trip proof: write_record(...) then read_record(store, ev['address']) returns the record with its
    lineage INTACT."""
    cas = store.head(address)
    if not cas:
        return None
    return store.get_content(cas)


def list_corpus(store, *, project: str | None = None) -> list[dict]:
    """A READ-TIME PROJECTION over the event log → the discovered corpus records (the run-index sibling —
    `events_since(-1)` filtered to `kind=="corpus.record"`). NO maintained index, NO new store
    (reuse-don't-parallel; the log IS the index). DEDUP-ON-READ (resume-safety, mirroring the findings
    reconcile): folds duplicate records by their corpus `address`, LATEST `seq` wins (a resumed run that
    re-wrote the same address never double-counts). Optionally filtered by `project` (the lineage axis).
    Each row: `{address, cas, source_address, record_kind, model, projection, lineage, seq, ts}`,
    newest-first."""
    folded: dict[str, dict] = {}
    for ev in store.events_since(-1):
        if ev.get("kind") != CORPUS_EVENT_KIND:
            continue
        if project is not None and (ev.get("lineage") or {}).get("project") != str(project):
            continue
        addr = ev.get("address")
        prev = folded.get(addr)
        if prev is None or ev.get("seq", -1) > prev.get("seq", -1):   # latest seq wins (dedup-on-read)
            folded[addr] = ev
    rows = sorted(folded.values(), key=lambda e: e.get("seq", -1), reverse=True)
    return rows


def find_corpus(store, *, project: str | None = None, kind: str | None = None,
                projection: str | None = None, source_address: str | None = None) -> list[dict]:
    """The FILTERED corpus projection (the query face) — `list_corpus` narrowed by any of the lineage/record
    axes (project · record kind · projection lens · source_address). Thin reuse of `list_corpus` (no second
    scan path); registry-is-truth (filters the discovered set, never a hand-listed one)."""
    rows = list_corpus(store, project=project)
    if kind is not None:
        rows = [r for r in rows if r.get("record_kind") == kind]
    if projection is not None:
        rows = [r for r in rows if r.get("projection") == projection]
    if source_address is not None:
        rows = [r for r in rows if r.get("source_address") == source_address]
    return rows
