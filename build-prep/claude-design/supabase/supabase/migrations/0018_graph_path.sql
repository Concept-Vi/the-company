-- 0018_graph_path.sql — ④ THE CONTAINER · L4 GRAPH + PATH (organ-studies/GRAPH-PATH.md §3)
--
-- The rebuilt GRAPH+PATH organ, schema-additive on the live ledger (0011) + container (0013):
--   1. ledger.edge_kind      — the ONE edge-kind registry (files author edge_kinds/<id>.py; this table
--                              is the DERIVED read side, populated by runtime/edge_kinds.py:assemble —
--                              law 3: vocabulary=files, data=DB). Declared inverses (law 4), a `face`
--                              naming the job (containment|knowledge|lineage), endpoints, behavior.
--   2. ledger.validate_edge_kind / ledger.edge_kind_exists — the fail-loud validation SEAM. Callable
--                              from the loader (fail-loud on write) AND from the ledger session's
--                              edge_unified view (NON-BLOCKING retro-validation of authored assertions).
--                              ABSORB-never-reject: no hard FK on ledger.edge / ledger.assertion — a new
--                              kind is added as a ROW (author a file, re-assemble), never a rejection gate.
--   3. ledger.path / ledger.path_step — the PATH as a first-class record (adopts A3's designed-but-empty
--                              sequences/sequence_steps shape). path://<project>/<id>, steps addressable
--                              path://<project>/<id>/<ordinal>. Reverses composed-at-read, never stored.
--   4. spelling normalization — part-of → part_of in ledger.edge (count-verified in the acceptance test;
--                              idempotent: re-run touches 0 rows).
--
-- Idempotent (IF NOT EXISTS / CREATE OR REPLACE / guarded UPDATE) — applies clean twice, and clean on a
-- scratch DB carrying only 0011_ledger.sql. schema-additive; no destructive DDL. Reversal per object noted.

BEGIN;

-- ── 1. the edge-kind registry (DERIVED from edge_kinds/<id>.py by runtime/edge_kinds.py) ─────────────
-- Reversal: DROP TABLE ledger.edge_kind (a derived projection — the files are the source of truth).
CREATE TABLE IF NOT EXISTS ledger.edge_kind (
    id            text PRIMARY KEY,                       -- == the authoring filename; ONE spelling per concept
    directed      boolean     NOT NULL DEFAULT true,      -- symmetric kinds (syncs_with, parallels) declare false
    inverse       text,                                   -- the DECLARED equal-and-opposite NAME (composed at read)
    face          text        NOT NULL DEFAULT 'knowledge'
                  CHECK (face IN ('containment', 'knowledge', 'lineage')),  -- the JOB, declared per kind
    endpoints     text[],                                 -- valid endpoint schemes, e.g. {code://,exchange://}
    behavior      text,                                   -- A2's trigger as a DECLARATION (e.g. 'dispatch'), not hidden
    label         text,
    description   text,
    near          text,
    far           text,
    needs_review  boolean     NOT NULL DEFAULT false,     -- absorbed long-tail kinds flagged for a face review
    source        text,                                   -- the authoring file path (breadcrumb)
    assembled_at  timestamptz NOT NULL DEFAULT now()
);
COMMENT ON TABLE ledger.edge_kind IS
    'The ONE edge-kind grammar (GRAPH-PATH §3.1). DERIVED from edge_kinds/<id>.py via runtime/edge_kinds.py:assemble '
    '(files author, DB serves the read side — law 3). Declared inverses composed-at-read, never stored (law 4). '
    'ABSORB-never-reject: add a kind = author a file + re-assemble.';

-- ── 2. the validation seam (fail-loud on write · non-blocking for retro-validation) ─────────────────
-- Reversal: DROP FUNCTION ledger.validate_edge_kind(text), ledger.edge_kind_exists(text).
CREATE OR REPLACE FUNCTION ledger.edge_kind_exists(k text) RETURNS boolean
    LANGUAGE sql STABLE AS $$ SELECT EXISTS (SELECT 1 FROM ledger.edge_kind WHERE id = k) $$;
COMMENT ON FUNCTION ledger.edge_kind_exists(text) IS
    'NON-BLOCKING registry membership test. The ledger session''s edge_unified retro-validation joins on this '
    '(never a gate on authored assertion writes — ABSORB-never-reject).';

CREATE OR REPLACE FUNCTION ledger.validate_edge_kind(k text) RETURNS void
    LANGUAGE plpgsql AS $$
BEGIN
    IF NOT ledger.edge_kind_exists(k) THEN
        RAISE EXCEPTION 'unregistered edge kind %: not in ledger.edge_kind registry. Author a row '
            '(edge_kinds/<id>.py) then re-assemble (.venv/bin/python -m runtime.edge_kinds assemble). '
            'ABSORB-never-reject: add the kind, never drop the edge.', k
            USING ERRCODE = 'check_violation';
    END IF;
END $$;
COMMENT ON FUNCTION ledger.validate_edge_kind(text) IS
    'FAIL-LOUD write-time validation (naming edge_kinds/). Used by the ledger loader''s pre-check.';

-- ── 3. the PATH as first-class (adopts A3 sequences/sequence_steps; GRAPH-PATH §3.3) ─────────────────
-- Reversal: DROP TABLE ledger.path_step, ledger.path.
CREATE TABLE IF NOT EXISTS ledger.path (
    path_id      uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    address      text UNIQUE NOT NULL,       -- path://<project>/<id>  (identity IS the text address — law 1)
    project      text,
    kind         text NOT NULL,              -- cascade-run | fusion | navigation | session-lineage | authored-flow
    name         text,
    summary      text,
    start_addr   text,
    end_addr     text,
    state        text,
    confidence   real,
    status       text NOT NULL DEFAULT 'active',
    provenance   jsonb,                       -- {generated_by: exchange://…, produced_by_session: …}
    promoted_to  text,                        -- flows/<id> ref once a walk is promoted (natural selection)
    created_at   timestamptz NOT NULL DEFAULT now()
);
COMMENT ON TABLE ledger.path IS
    'An ordered typed walk (GRAPH-PATH §3.3): path://<project>/<id>, derived from runs/sessions/navigation, '
    'replayable, embeddable (space=paths), promotable to a flow. path.kind vocabulary is open (ABSORB new '
    'derivations by row, no CHECK) — known: cascade-run|fusion|navigation|session-lineage|authored-flow.';

CREATE TABLE IF NOT EXISTS ledger.path_step (
    path_id      uuid NOT NULL REFERENCES ledger.path(path_id) ON DELETE CASCADE,
    ordinal      int  NOT NULL,               -- unique per path; step address = path.address || '/' || ordinal
    at_addr      text,                         -- the node stood ON
    via_kind     text,                         -- edge-kind registry ref (NULL at ordinal 0 — the start node)
    via_edge_id  uuid,                          -- the ledger.edge walked, when the step rode a stored edge
    payload_addr text,                          -- run://<turn>/<member>[/<i>] · session://<sid>/step/<tid> · cas://…
    stamp        timestamptz,
    step_state   text NOT NULL DEFAULT 'observed' CHECK (step_state IN ('observed', 'inferred', 'planned')),
    label        text,
    metadata     jsonb,
    PRIMARY KEY (path_id, ordinal)
);
COMMENT ON TABLE ledger.path_step IS
    'One step of a path — alternating addresses and registry kinds (the same grammar as the graph, plus '
    'ordinals + time). via_kind references ledger.edge_kind; reverses are composed at read, never stored.';

CREATE INDEX IF NOT EXISTS path_project_idx  ON ledger.path (project);
CREATE INDEX IF NOT EXISTS path_kind_idx     ON ledger.path (kind);
CREATE INDEX IF NOT EXISTS path_step_at_idx  ON ledger.path_step (at_addr);

-- ── 4. spelling normalization — part-of → part_of (count-verified in graph_path_acceptance) ─────────
-- The one within-ledger.edge collision (part_of 239 + part-of 11). Cross-source collisions (cloud
-- depends_on vs ledger depends-on) are normalized at LANDING (ops/migrate_edges_from_cvi.py), keeping
-- the live 720k table otherwise untouched. Idempotent: a second run updates 0 rows.
UPDATE ledger.edge SET kind = 'part_of' WHERE kind = 'part-of';

COMMIT;
