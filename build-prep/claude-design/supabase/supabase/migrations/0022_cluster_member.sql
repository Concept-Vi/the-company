-- 0022_cluster_member.sql — SCALE membership into SQL (ledger session; number per ④'s map).
-- Idempotent, additive-only. B·R1's axis-4 gap: rung CENTROIDS are already embedding rows
-- (space='scale:<space>:k<K>'), but the MEMBERSHIP/NESTING structure lives only in JSON sidecars
-- (.data/store/scale/<space>#emb=<emb>.json) — unqueryable in SQL, so the coordinate query's scale
-- axis (coarse-to-fine drill: rung centroids → members) couldn't compose. This lands it as rows.

create table if not exists ledger.cluster_member (
    cluster_address text not null,       -- cluster://<space>/k<K>/<label>
    member_address  text not null,       -- the unit's source address (code://…, exchange://…)
    space           text not null,       -- the UNIT space (e.g. 'topics', 'extractions')
    k               integer not null,    -- the rung
    emb             text not null default 'pplx',
    is_exemplar     boolean not null default false,
    parent_cluster  text,                -- the finer child rung links inverted: this cluster's coarser parent
    primary key (cluster_address, member_address)
);
create index if not exists cluster_member_cluster_idx on ledger.cluster_member (cluster_address);
create index if not exists cluster_member_member_idx  on ledger.cluster_member (member_address);
create index if not exists cluster_member_space_k_idx on ledger.cluster_member (space, k, emb);

comment on table ledger.cluster_member is
'Scale-axis membership: which units belong to which cluster at which rung (loaded from the scale sidecars;
build_scale_pyramid emits rows going forward). Centroid vectors stay in ledger.embedding (scale:* spaces);
this is the JOIN that makes coarse-to-fine drill one SQL hop. Nesting: parent_cluster (coarser); the
children_finer relation is its inverse, composed at read.';
