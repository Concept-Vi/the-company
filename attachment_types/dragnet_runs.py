"""dragnet_runs — a tracked DRAGNET RUN attached to a channel: the operational record (times·resources·
fails·retries·coverage) of a dragnet issued FOR this channel over an input directory."""
ATTACHMENT_TYPE = {
    "id": "dragnet_runs",
    "label": "Dragnet runs",
    "target_kind": "address",       # target = run://corpus/.../dragnet/<id> (the tracked run record)
    "multi": True,
    "desc": "a tracked dragnet RUN (run-record address) bound to a channel — issued for the channel over an "
            "input dir; the run telemetry (started/ended/duration · files_total/processed/failed/retries · "
            "throughput · coverage) is captured as the introspective record of the process. The channel "
            "accumulates its dragnet-run history, queryable.",
}
