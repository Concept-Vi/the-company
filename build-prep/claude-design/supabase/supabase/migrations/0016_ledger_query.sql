-- 0016_ledger_query.sql — L11: ledger.query(spec jsonb) v1 — THE multi-axis coordinate query.
-- (ledger session's block 0014/0015/0016 — this closes the block.) Idempotent (create or replace).
--
-- ONE function, one definition, two faces: PostgREST exposes it to the UI as rpc/query; the MCP face calls
-- it via psql/psycopg — same body (the-one-system law: capabilities projected to both faces from ONE fn).
-- It is the WINDOW'S FEED (④ L8) — results shaped for the projection contract; the graph leg reads raw
-- edge kinds now and adopts ④ L4's edge_kinds validation when it lands (declared seam).
--
-- SPEC (jsonb; unknown top-level keys RAISE — fail-loud, teaching):
-- {
--   "project":  "company",                     -- default company; resolves the latest run once
--   "filter":   {"path_under": "runtime/", "node_type": ["file"], "ext": [".py"],
--                "changed_after": "2026-07-01"},          -- changed_after reads the DURABLE file_meta
--   "graph":    {"anchor": "code://company/runtime/suite.py", "kinds": ["calls"],
--                "direction": "out", "depth": 2},         -- RESTRICT candidates to the reachable set
--   "semantic": {"vector": [..], "space": "desc", "emb": "pplx", "k": 40},   -- caller embeds the query
--   "lexical":  {"text": "supersession stranded"},        -- FTS over durable interpretation
--   "limit":    20
-- }
-- RETURNS jsonb: {results:[{address, score, legs:{...}, what_it_does, path, node_type}],
--                 meta:{run_id, candidates_n, legs_run, plan, dropped}}  — counts always echoed.

create or replace function ledger.query(spec jsonb) returns jsonb
language plpgsql stable as $fn$
declare
    _known      text[] := array['project','filter','graph','semantic','lexical','scale','limit'];
    _k          text;
    _project    text  := coalesce(spec->>'project', 'company');
    _run        uuid;
    _limit      int   := coalesce((spec->>'limit')::int, 20);
    _cands      text[];                    -- candidate addresses (null = unconstrained)
    _cands_n    int;
    _plan       jsonb := '{}'::jsonb;
    _sem        jsonb := spec->'semantic';
    _lex        jsonb := spec->'lexical';
    _gph        jsonb := spec->'graph';
    _flt        jsonb := spec->'filter';
    _scl        jsonb := spec->'scale';
    _dim        int;
    _vcol       text;
    _sem_rows   jsonb;
    _lex_rows   jsonb;
    _fused      jsonb;
begin
    -- fail-loud vocabulary gate (teaching: name the bad key + the valid set)
    for _k in select jsonb_object_keys(spec) loop
        if not (_k = any(_known)) then
            raise exception 'ledger.query: unknown spec key %— valid keys are %', quote_literal(_k), _known
                  using hint = 'the spec vocabulary is closed (fail-loud); see 0016_ledger_query.sql';
        end if;
    end loop;

    -- resolve the run ONCE (cross-run leakage is a correctness trap — 18+ runs in-table)
    select run_id into _run from ledger.latest_run where project = _project;
    if _run is null then
        raise exception 'ledger.query: no runs for project % — projects with runs: %', _project,
              (select string_agg(distinct project, ', ') from ledger.run);
    end if;

    -- ── CANDIDATES: structured filter axes (path / node_type / ext / time-via-durable-file_meta) ──
    if _flt is not null or _gph is not null then
        select array_agg(u.address) into _cands from (
            select e.address
            from ledger.entry e
            left join ledger.file_meta fm on fm.project = e.project and fm.path = e.path
            where e.run_id = _run
              and (_flt->>'path_under'    is null or e.path like (_flt->>'path_under') || '%')
              and (_flt->'node_type'      is null or e.node_type = any(select jsonb_array_elements_text(_flt->'node_type')))
              and (_flt->'ext'            is null or e.ext = any(select jsonb_array_elements_text(_flt->'ext')))
              and (_flt->>'changed_after' is null or fm.last_modified_at >= (_flt->>'changed_after')::timestamptz)
        ) u;
        _cands_n := coalesce(array_length(_cands, 1), 0);
        _plan := _plan || jsonb_build_object('filter_candidates', _cands_n);
    end if;

    -- ── GRAPH RESTRICT: depth-capped recursive walk from the anchor; candidates ∩= reachable ──
    if _gph is not null then
        if coalesce((_gph->>'depth')::int, 2) > 3 then
            raise exception 'ledger.query: graph.depth % exceeds the cap 3 (frontier discipline)', _gph->>'depth';
        end if;
        with recursive walk(addr, d) as (
            select (_gph->>'anchor')::text, 0
            union
            select case when coalesce(_gph->>'direction','out') = 'out'
                        then split_part(g.to_resolved, '::', 1) else split_part(g.from_ref, '::', 1) end,
                   w.d + 1
            from walk w
            join ledger.edge g on g.run_id = _run
                 and (_gph->'kinds' is null or g.kind = any(select jsonb_array_elements_text(_gph->'kinds')))
                 and case when coalesce(_gph->>'direction','out') = 'out'
                          then split_part(g.from_ref, '::', 1) = w.addr and g.to_resolved is not null
                          else split_part(g.to_resolved, '::', 1) = w.addr end
            where w.d < coalesce((_gph->>'depth')::int, 2)
        )
        select array_agg(distinct addr) into _cands
        from walk
        where _cands is null or addr = any(_cands);
        _cands_n := coalesce(array_length(_cands, 1), 0);
        _plan := _plan || jsonb_build_object('graph_reachable', _cands_n);
        if _cands_n = 0 then
            return jsonb_build_object('results', '[]'::jsonb,
                'meta', jsonb_build_object('run_id', _run, 'candidates_n', 0, 'plan', _plan,
                    'note', 'graph walk reached nothing from the anchor — check the anchor address + kinds/direction'));
        end if;
    end if;

    -- ── SCALE drill: rank the rung's centroids by the query vector (tiny space, exact), take the top
    -- clusters, restrict candidates to their MEMBERS (coarse-to-fine; the world-map's zoom semantics).
    -- Requires semantic.vector (centroids are ranked by it); rung membership from ledger.cluster_member.
    if _scl is not null then
        if _sem is null or _sem->'vector' is null then
            raise exception 'ledger.query: scale drill needs semantic.vector (centroids are ranked by the query vector)';
        end if;
        _dim := jsonb_array_length(_sem->'vector');
        _vcol := case _dim when 3584 then 'vec_3584' when 2560 then 'vec_2560' when 1024 then 'vec_1024' end;
        execute format(
            'select array_agg(member_address) from (
                select source_address from ledger.embedding
                where space = $1 and %I is not null
                order by %I <=> $2::halfvec(%s) limit $3) top
             join ledger.cluster_member cm on cm.cluster_address = top.source_address',
            _vcol, _vcol, _dim)
        into _cands
        using format('scale:%s:k%s', _scl->>'space', _scl->>'rung'),
              (select array(select jsonb_array_elements_text(_sem->'vector'))::real[])::halfvec,
              coalesce((_scl->>'top_clusters')::int, 5);
        _cands_n := coalesce(array_length(_cands, 1), 0);
        _plan := _plan || jsonb_build_object('scale', jsonb_build_object(
            'rung', format('scale:%s:k%s', _scl->>'space', _scl->>'rung'),
            'top_clusters', coalesce((_scl->>'top_clusters')::int, 5), 'member_candidates', _cands_n));
        if _cands_n = 0 then
            raise exception 'ledger.query: scale drill found no members — is rung scale:%:k% loaded in ledger.cluster_member? (0022)',
                  _scl->>'space', _scl->>'rung';
        end if;
    end if;

    -- ── SEMANTIC leg (caller supplies the query vector; dim picks the column — never cross-dim) ──
    if _sem is not null then
        _dim := jsonb_array_length(_sem->'vector');
        _vcol := case _dim when 3584 then 'vec_3584' when 2560 then 'vec_2560' when 1024 then 'vec_1024' end;
        if _vcol is null then
            raise exception 'ledger.query: semantic.vector dim % has no column (1024/2560/3584)', _dim;
        end if;
        execute format(
            'select coalesce(jsonb_agg(jsonb_build_object(''address'', a, ''score'', s) order by s desc), ''[]''::jsonb)
             from (select source_address a, 1 - (%I <=> $1::halfvec(%s)) s
                   from ledger.embedding
                   where space = $2 and %I is not null
                     and ($3::text is null or emb_layer = $3)
                     and ($4::text[] is null or source_address = any($4))
                   order by s desc limit $5) t', _vcol, _dim, _vcol)
        into _sem_rows
        using (select array(select jsonb_array_elements_text(_sem->'vector'))::real[])::halfvec,
              coalesce(_sem->>'space', 'desc'), _sem->>'emb', _cands, coalesce((_sem->>'k')::int, 40);
        _plan := _plan || jsonb_build_object('semantic', jsonb_build_object(
            'space', coalesce(_sem->>'space','desc'), 'dim', _dim, 'hits', jsonb_array_length(_sem_rows)));
    end if;

    -- ── LEXICAL leg: FTS over the DURABLE interpretation (websearch grammar — user-ish text is fine) ──
    if _lex is not null then
        select coalesce(jsonb_agg(jsonb_build_object('address', address, 'score', rank) order by rank desc), '[]'::jsonb)
        into _lex_rows
        from (select i.address, ts_rank(i.fts, websearch_to_tsquery('english', _lex->>'text')) rank
              from ledger.interpretation i
              where i.fts @@ websearch_to_tsquery('english', _lex->>'text')
                and (_cands is null or i.address = any(_cands))
              order by rank desc limit 60) t;
        _plan := _plan || jsonb_build_object('lexical_hits', jsonb_array_length(_lex_rows));
    end if;

    -- ── FUSE (RRF k=60 when both legs ran; a single leg IS the ranking; neither → filtered listing) ──
    if _sem_rows is not null and _lex_rows is not null then
        select jsonb_agg(jsonb_build_object('address', addr, 'score', rrf, 'legs', legs) order by rrf desc)
        into _fused
        from (
            select coalesce(s.addr, l.addr) addr,
                   coalesce(1.0/(60 + s.rn), 0) + coalesce(1.0/(60 + l.rn), 0) rrf,
                   jsonb_build_object('semantic_rank', s.rn, 'lexical_rank', l.rn) legs
            from (select value->>'address' addr, row_number() over () rn from jsonb_array_elements(_sem_rows)) s
            full outer join
                 (select value->>'address' addr, row_number() over () rn from jsonb_array_elements(_lex_rows)) l
            using (addr)
            order by rrf desc limit _limit
        ) f;
        _plan := _plan || jsonb_build_object('fuse', 'rrf60');
    elsif _sem_rows is not null then
        select jsonb_agg(e) into _fused from (select jsonb_array_elements(_sem_rows) e limit _limit) q;
        _plan := _plan || jsonb_build_object('fuse', 'semantic-only');
    elsif _lex_rows is not null then
        select jsonb_agg(e) into _fused from (select jsonb_array_elements(_lex_rows) e limit _limit) q;
        _plan := _plan || jsonb_build_object('fuse', 'lexical-only');
    else                                            -- pure coordinate filter: the candidate listing itself
        select jsonb_agg(jsonb_build_object('address', a)) into _fused
        from (select unnest(_cands) a limit _limit) q;
        _plan := _plan || jsonb_build_object('fuse', 'filter-listing');
    end if;

    -- ── ENRICH results from the durable read (description + structure ride along) ──
    return jsonb_build_object(
        'results', coalesce((
            select jsonb_agg(r.value || jsonb_build_object(
                       'what_it_does', left(u.what_it_does, 240), 'path', u.path, 'node_type', u.node_type)
                   order by (r.value->>'score')::numeric desc nulls last)
            from jsonb_array_elements(coalesce(_fused, '[]'::jsonb)) r
            left join ledger.unit_latest u on u.address = r.value->>'address'), '[]'::jsonb),
        'meta', jsonb_build_object('run_id', _run, 'project', _project,
                                   'candidates_n', _cands_n, 'plan', _plan));
end
$fn$;

comment on function ledger.query(jsonb) is
'L11 v1: THE multi-axis coordinate query (filter+time+graph-restrict+semantic+lexical → RRF), one definition
serving MCP + UI. meta.plan echoes what ran (under-recall is never silent). Graph leg: raw edge kinds now,
④ L4 edge_kinds validation when it lands. Scale-drill lands with cluster_member (next block).';
