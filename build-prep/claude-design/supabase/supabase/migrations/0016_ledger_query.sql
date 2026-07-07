-- 0016_ledger_query.sql — L11: ledger.query(spec jsonb) — THE multi-axis coordinate query.
-- (Canonical definition, updated in place — create-or-replace, the no-versioning law. v2 2026-07-03:
-- Tim's axis-extension directive — paths axis · count/group-by operator · address-set seeds · filter
-- combinators (any-of/not_under) · graph direction=both + hop attribution + edge expansion.)
--
-- ONE function, one definition, two faces: PostgREST rpc for the UI; psql/psycopg for MCP. The WINDOW'S
-- FEED (④ L8). Closed vocabulary — unknown keys RAISE with the valid set (teaching, never silent).
--
-- SPEC (all keys optional, all combinable):
--   project   "company" (default) — resolves the latest run ONCE (cross-run leakage guard)
--   addresses ["code://…", …]                  — explicit candidate seed (an address-set combinator)
--   filter    {path_under: "runtime/"|[…], not_under: "tests/"|[…], node_type: […], ext: […],
--              changed_after: ts}              — structured axes (time via DURABLE file_meta)
--   graph     {anchor, kinds: […], direction: out|in|both, depth ≤3, expand: bool}
--             — RESTRICT candidates to the reachable set; hop distances attributed on results;
--               expand=true attaches each result's own edges (edge_unified, both provenances)
--   paths     {id: "<path uuid>"} | {kind: "fusion"} | {through: "code://…"}
--             — restrict to addresses walked by matching ledger.path/path_step records
--   scale     {space, rung, top_clusters}      — coarse-to-fine drill via cluster_member (the zoom)
--   semantic  {vector: […], space, emb, k}     — cosine leg (dim → column, never cross-dim)
--   lexical   {text}                           — FTS over DURABLE interpretation
--   count     {by: node_type|ext|language|kind|space|path_prefix}
--             — the COUNT OPERATOR: aggregate the candidate set instead of ranking it
--   limit     20
-- RETURNS {results: […], meta: {run_id, project, candidates_n, plan}} — plan echoes every leg.

create or replace function ledger.query(spec jsonb) returns jsonb
language plpgsql stable as $fn$
declare
    _known      text[] := array['project','addresses','filter','graph','paths','semantic','lexical',
                                'scale','count','limit'];
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
    _pth        jsonb := spec->'paths';
    _cnt        jsonb := spec->'count';
    _dim        int;
    _vcol       text;
    _sem_rows   jsonb;
    _lex_rows   jsonb;
    _fused      jsonb;
    _hops       jsonb;
    _dirn       text;
begin
    for _k in select jsonb_object_keys(spec) loop
        if not (_k = any(_known)) then
            raise exception 'ledger.query: unknown spec key %— valid keys are %', quote_literal(_k), _known
                  using hint = 'the spec vocabulary is closed (fail-loud); see 0016_ledger_query.sql';
        end if;
    end loop;

    select run_id into _run from ledger.latest_run where project = _project;
    if _run is null then
        raise exception 'ledger.query: no runs for project % — projects with runs: %', _project,
              (select string_agg(distinct project, ', ') from ledger.run);
    end if;

    -- ── ADDRESS-SET seed (combinator): an explicit list IS the starting candidate set ──
    if spec->'addresses' is not null then
        select array_agg(x) into _cands from jsonb_array_elements_text(spec->'addresses') x;
        _plan := _plan || jsonb_build_object('address_seed', coalesce(array_length(_cands,1),0));
    end if;

    -- ── FILTER axes: path any-of/not-under combinators · node_type/ext · time via durable file_meta ──
    if _flt is not null then
        select array_agg(u.address) into _cands from (
            select e.address
            from ledger.entry e
            left join ledger.file_meta fm on fm.project = e.project and fm.path = e.path
            where e.run_id = _run
              and (_flt->'path_under' is null or (
                     case when jsonb_typeof(_flt->'path_under') = 'array'
                          then exists (select 1 from jsonb_array_elements_text(_flt->'path_under') p
                                       where e.path like p || '%')
                          else e.path like (_flt->>'path_under') || '%' end))
              and (_flt->'not_under' is null or not (
                     case when jsonb_typeof(_flt->'not_under') = 'array'
                          then exists (select 1 from jsonb_array_elements_text(_flt->'not_under') p
                                       where e.path like p || '%')
                          else e.path like (_flt->>'not_under') || '%' end))
              and (_flt->'node_type'      is null or e.node_type = any(select jsonb_array_elements_text(_flt->'node_type')))
              and (_flt->'ext'            is null or e.ext = any(select jsonb_array_elements_text(_flt->'ext')))
              and (_flt->>'changed_after' is null or fm.last_modified_at >= (_flt->>'changed_after')::timestamptz)
              and (_cands is null or e.address = any(_cands))
        ) u;
        _cands_n := coalesce(array_length(_cands, 1), 0);
        _plan := _plan || jsonb_build_object('filter_candidates', _cands_n);
    end if;

    -- ── PATHS axis: restrict to addresses WALKED by matching path records (the journey lens) ──
    if _pth is not null then
        select array_agg(distinct ps.at_addr) into _cands
        from ledger.path_step ps
        join ledger.path p using (path_id)
        where (_pth->>'id'      is null or p.path_id = (_pth->>'id')::uuid)
          and (_pth->>'kind'    is null or p.kind = _pth->>'kind')
          and (_pth->>'through' is null or p.path_id in
                 (select path_id from ledger.path_step where at_addr = _pth->>'through'))
          and (_cands is null or ps.at_addr = any(_cands));
        _cands_n := coalesce(array_length(_cands, 1), 0);
        _plan := _plan || jsonb_build_object('paths_candidates', _cands_n);
        if _cands_n = 0 then
            raise exception 'ledger.query: the paths axis matched no step addresses — path kinds present: %',
                  coalesce((select string_agg(distinct kind, ', ') from ledger.path), '(none)');
        end if;
    end if;

    -- ── GRAPH: depth-capped walk (direction out|in|both) → restrict + HOP ATTRIBUTION ──
    if _gph is not null then
        if coalesce((_gph->>'depth')::int, 2) > 3 then
            raise exception 'ledger.query: graph.depth % exceeds the cap 3 (frontier discipline)', _gph->>'depth';
        end if;
        _dirn := coalesce(_gph->>'direction', 'out');
        if _dirn not in ('out','in','both') then
            raise exception 'ledger.query: graph.direction % — one of out|in|both', quote_literal(_dirn);
        end if;
        with recursive walk(addr, d) as (
            select (_gph->>'anchor')::text, 0
            union all
            select nxt.addr, w.d + 1
            from walk w
            cross join lateral (
                select split_part(g.to_resolved, '::', 1) as addr
                from ledger.edge g
                where g.run_id = _run and _dirn in ('out','both')
                  and (_gph->'kinds' is null or g.kind = any(select jsonb_array_elements_text(_gph->'kinds')))
                  and split_part(g.from_ref, '::', 1) = w.addr and g.to_resolved is not null
                union
                select split_part(g.from_ref, '::', 1)
                from ledger.edge g
                where g.run_id = _run and _dirn in ('in','both')
                  and (_gph->'kinds' is null or g.kind = any(select jsonb_array_elements_text(_gph->'kinds')))
                  and split_part(g.to_resolved, '::', 1) = w.addr
            ) nxt
            where w.d < coalesce((_gph->>'depth')::int, 2)
        ),
        reach as (select addr, min(d) as hops from walk group by addr)
        select array_agg(addr) filter (where _cands is null or addr = any(_cands)),
               jsonb_object_agg(addr, hops)
        into _cands, _hops
        from reach;
        _cands_n := coalesce(array_length(_cands, 1), 0);
        _plan := _plan || jsonb_build_object('graph_reachable', _cands_n, 'graph_direction', _dirn);
        if _cands_n = 0 then
            return jsonb_build_object('results', '[]'::jsonb,
                'meta', jsonb_build_object('run_id', _run, 'candidates_n', 0, 'plan', _plan,
                    'note', 'graph walk reached nothing from the anchor — check the anchor address + kinds/direction'));
        end if;
    end if;

    -- ── SCALE drill (the zoom): rank rung centroids, take the warm clusters, restrict to members ──
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
             join ledger.cluster_member cm on cm.cluster_address = top.source_address'
            || case when _cands is not null then ' where cm.member_address = any($4)' else '' end,
            _vcol, _vcol, _dim)
        into _cands
        using format('scale:%s:k%s', _scl->>'space', _scl->>'rung'),
              (select array(select jsonb_array_elements_text(_sem->'vector'))::real[])::halfvec,
              coalesce((_scl->>'top_clusters')::int, 5), _cands;
        _cands_n := coalesce(array_length(_cands, 1), 0);
        _plan := _plan || jsonb_build_object('scale', jsonb_build_object(
            'rung', format('scale:%s:k%s', _scl->>'space', _scl->>'rung'),
            'top_clusters', coalesce((_scl->>'top_clusters')::int, 5), 'member_candidates', _cands_n));
        if _cands_n = 0 then
            raise exception 'ledger.query: scale drill found no members — is rung scale:%:k% loaded in ledger.cluster_member? (0022)',
                  _scl->>'space', _scl->>'rung';
        end if;
    end if;

    -- ── THE COUNT OPERATOR: aggregate the candidate set instead of ranking (counts are answers too) ──
    if _cnt is not null then
        if _cnt->>'by' not in ('node_type','ext','language','kind','space','path_prefix') then
            raise exception 'ledger.query: count.by % — one of node_type|ext|language|kind|space|path_prefix',
                  quote_literal(_cnt->>'by');
        end if;
        if _cnt->>'by' = 'kind' then                 -- edge kinds touching the candidate set (or all)
            return jsonb_build_object('results', coalesce((
                select jsonb_agg(jsonb_build_object('group', kind, 'n', n) order by n desc)
                from (select kind, count(*) n from ledger.edge_unified
                      where _cands is null or split_part(from_ref,'::',1) = any(_cands)
                      group by kind order by count(*) desc limit 40) t), '[]'::jsonb),
                'meta', jsonb_build_object('run_id', _run, 'plan', _plan || '{"operator":"count-by-kind"}'::jsonb));
        elsif _cnt->>'by' = 'space' then             -- embedding spaces covering the candidate set
            return jsonb_build_object('results', coalesce((
                select jsonb_agg(jsonb_build_object('group', space, 'n', n) order by n desc)
                from (select space, count(*) n from ledger.embedding
                      where space not like '\_\_root\_%' escape '\'
                        and (_cands is null or source_address = any(_cands))
                      group by space order by count(*) desc limit 40) t), '[]'::jsonb),
                'meta', jsonb_build_object('run_id', _run, 'plan', _plan || '{"operator":"count-by-space"}'::jsonb));
        elsif _cnt->>'by' = 'path_prefix' then       -- the folder histogram (2 levels)
            return jsonb_build_object('results', coalesce((
                select jsonb_agg(jsonb_build_object('group', pfx, 'n', n) order by n desc)
                from (select split_part(path,'/',1) || case when position('/' in path) > 0
                             then '/' || split_part(path,'/',2) else '' end as pfx, count(*) n
                      from ledger.entry where run_id = _run
                        and (_cands is null or address = any(_cands))
                      group by 1 order by 2 desc limit 40) t), '[]'::jsonb),
                'meta', jsonb_build_object('run_id', _run, 'plan', _plan || '{"operator":"count-by-path"}'::jsonb));
        else
            return jsonb_build_object('results', coalesce((
                select jsonb_agg(jsonb_build_object('group', g, 'n', n) order by n desc)
                from (select case _cnt->>'by' when 'node_type' then node_type
                                              when 'ext' then ext else language end as g, count(*) n
                      from ledger.entry where run_id = _run
                        and (_cands is null or address = any(_cands))
                      group by 1 order by 2 desc limit 40) t), '[]'::jsonb),
                'meta', jsonb_build_object('run_id', _run, 'plan',
                        _plan || jsonb_build_object('operator', 'count-by-' || (_cnt->>'by'))));
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

    -- ── LEXICAL leg: FTS — over the DURABLE interpretation (default), or over the TRANSCRIPT TEXT
    -- itself when lexical.over='exchange' (0024: the conversation words joined the one store) ──
    if _lex is not null then
        if coalesce(_lex->>'over', 'interpretation') = 'exchange' then
            select coalesce(jsonb_agg(jsonb_build_object('address', address, 'score', rank) order by rank desc), '[]'::jsonb)
            into _lex_rows
            from (select x.address, ts_rank(x.fts, websearch_to_tsquery('english', _lex->>'text')) rank
                  from ledger.exchange x
                  where x.fts @@ websearch_to_tsquery('english', _lex->>'text')
                    and (_cands is null or x.address = any(_cands))
                  order by rank desc limit 60) t;
            _plan := _plan || jsonb_build_object('lexical_over', 'exchange');
        elsif coalesce(_lex->>'over', 'interpretation') <> 'interpretation' then
            raise exception 'ledger.query: lexical.over % — one of interpretation|exchange', quote_literal(_lex->>'over');
        else
            select coalesce(jsonb_agg(jsonb_build_object('address', address, 'score', rank) order by rank desc), '[]'::jsonb)
            into _lex_rows
            from (select i.address, ts_rank(i.fts, websearch_to_tsquery('english', _lex->>'text')) rank
                  from ledger.interpretation i
                  where i.fts @@ websearch_to_tsquery('english', _lex->>'text')
                    and (_cands is null or i.address = any(_cands))
                  order by rank desc limit 60) t;
        end if;
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

    -- ── ENRICH from the durable read (+ hop attribution + optional edge expansion) ──
    return jsonb_build_object(
        'results', coalesce((
            select jsonb_agg(
                r.value
                || jsonb_build_object(
                       -- a unit enriches from the durable read; an EXCHANGE from its own words (0024)
                       'what_it_does', coalesce(left(u.what_it_does, 240),
                                                left(regexp_replace(coalesce(x.user_text,''), '\s+', ' ', 'g'), 240)),
                       'path', coalesce(u.path, x.archive_path), 'node_type', coalesce(u.node_type, case when x.address is not null then 'exchange' end))
                || case when _hops is not null and _hops ? (r.value->>'address')
                        then jsonb_build_object('hops', _hops->(r.value->>'address')) else '{}'::jsonb end
                || case when coalesce((_gph->>'expand')::boolean, false)
                        then jsonb_build_object('edges', coalesce((
                             select jsonb_agg(jsonb_build_object('kind', eu.kind, 'to', eu.to_resolved,
                                                                 'provenance', eu.provenance))
                             from (select kind, to_resolved, provenance from ledger.edge_unified
                                   where split_part(from_ref,'::',1) = r.value->>'address'
                                     and to_resolved is not null limit 8) eu), '[]'::jsonb))
                        else '{}'::jsonb end
                order by (r.value->>'score')::numeric desc nulls last)
            from jsonb_array_elements(coalesce(_fused, '[]'::jsonb)) r
            left join ledger.unit_latest u on u.address = r.value->>'address'
            left join ledger.exchange x on x.address = r.value->>'address'), '[]'::jsonb),
        'meta', jsonb_build_object('run_id', _run, 'project', _project,
                                   'candidates_n', _cands_n, 'plan', _plan));
end
$fn$;

comment on function ledger.query(jsonb) is
'L11 v2: THE multi-axis coordinate query — addresses/filter(any-of,not_under)/paths/graph(out|in|both,
hop-attributed, expand=edges)/scale-drill/semantic/lexical → RRF · count operator (group-by aggregations).
One definition, both faces; closed vocabulary; meta.plan echoes every leg. The window''s feed.';
