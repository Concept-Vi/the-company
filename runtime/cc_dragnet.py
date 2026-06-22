"""runtime/cc_dragnet.py — a DRAGNET as a channel-attached, TRACKED operation.

Tim 2026-06-22: "a dragnet can be issued attached to a channel, for an input directory, and the outputs go to
store attached to the channel/project, to the right addresses, so a lot of it is a variable resolution from
initial input … be good to track them too — times, resources, fails/retries, all that — we don't have that
data yet."

THE SHAPE: issue a dragnet FOR a channel, pointed at an input dir. From that initial input everything RESOLVES
— the output addresses (<scheme>://<channel>/<rel_path>), the store. And the RUN is TRACKED: a run-record
capturing started/ended/duration · files_total/processed/skipped/failed/retries · throughput · coverage ·
errors — the introspective operational data the system didn't capture before. The run-record is ingested into
the corpus (queryable) AND attached to the channel (dragnet_runs) — the channel accumulates its run history.

Reuse-don't-parallel: the per-file INGEST plugs in (kind='image' → cc_images.save_image; a custom `ingest_one`
callable for code/docs → fork's extraction engine). This module is the TRACKED-RUN + ADDRESS-RESOLUTION +
CHANNEL-ATTACH wrapper around whatever extractor runs — NOT a second extraction engine.
"""
from __future__ import annotations

import os
import time
from datetime import datetime, timezone

from runtime import corpus as _corpus
from runtime import cc_attachments as _att

_IMG_EXT = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
           ".webp": "image/webp", ".gif": "image/gif", ".svg": "image/svg+xml"}


class DragnetError(RuntimeError):
    """A dragnet run could not be issued — raised TEACHING-loud."""


def _enumerate(input_dir: str, extensions=None) -> list[str]:
    """The DENOMINATOR — every file under input_dir (optionally filtered to extensions). The coverage base."""
    out = []
    for root, _dirs, files in os.walk(input_dir):
        for fn in files:
            if extensions and os.path.splitext(fn)[1].lower() not in extensions:
                continue
            out.append(os.path.join(root, fn))
    return sorted(out)


def run_dragnet(store, *, channel: str, input_dir: str, author_session: str, kind: str = "image",
                ingest_one=None, extensions=None, retries: int = 2, project: str = "company") -> dict:
    """Issue a TRACKED dragnet FOR `channel` over `input_dir`. Outputs RESOLVE to <scheme>://<channel>/<rel>
    (variable resolution from the input). Each file is ingested (with up to `retries` retries) and the RUN is
    tracked (times/processed/failed/retries/throughput/coverage). Writes a run-record into the corpus +
    attaches it to the channel. Returns the run telemetry. `kind='image'` uses cc_images; pass `ingest_one`
    (a callable (store, file_path, channel, rel_path)->address) for code/docs (fork's engine plugs in here)."""
    if not channel or not input_dir or not author_session:
        raise DragnetError("run_dragnet needs `channel`, `input_dir`, and `author_session`.")
    if not os.path.isdir(input_dir):
        raise DragnetError(f"input_dir {input_dir!r} is not a directory — fail loud (never a silent empty run).")

    exts = extensions or (set(_IMG_EXT) if kind == "image" else None)
    files = _enumerate(input_dir, exts)
    started = time.time()
    started_iso = datetime.now(timezone.utc).isoformat()

    def _ingest_image(fp, rel):
        with open(fp, "rb") as f:
            data = f.read()
        mime = _IMG_EXT.get(os.path.splitext(fp)[1].lower(), "")
        stem = os.path.splitext(rel)[0]
        rec = __import__("runtime.cc_images", fromlist=["save_image"]).save_image(
            store, data, channel=channel, path=stem, mime=mime, author_session=author_session,
            source="dragnet")
        _att.attach(channel, "images", rec["address"])
        return rec["address"]

    ingest = ingest_one or (_ingest_image if kind == "image" else None)
    if ingest is None:
        raise DragnetError(f"kind={kind!r} has no built-in ingester — pass `ingest_one` (the extractor "
                           f"callable) for non-image dragnets (fork's engine plugs in here).")

    processed, failed, retried, errors, slowest = 0, 0, 0, [], 0.0
    addresses = []
    for fp in files:
        rel = os.path.relpath(fp, input_dir)
        t0 = time.time()
        ok = False
        for attempt in range(retries + 1):
            try:
                addr = ingest(fp, rel) if ingest is _ingest_image else ingest(store, fp, channel, rel)
                addresses.append(addr)
                processed += 1
                ok = True
                break
            except Exception as e:                      # noqa: BLE001 — track every fail/retry, never swallow
                if attempt < retries:
                    retried += 1
                    continue
                failed += 1
                errors.append({"file": rel, "error": str(e)[:160]})
        dt = time.time() - t0
        slowest = max(slowest, dt)

    ended = time.time()
    dur = ended - started
    total = len(files)
    telemetry = {
        "channel": channel, "input_dir": input_dir, "kind": kind,
        "output_prefix": f"image://{channel}" if kind == "image" else f"{kind}://{channel}",
        "started": started_iso, "duration_s": round(dur, 2),
        "files_total": total, "processed": processed, "failed": failed, "retries": retried,
        "errors": errors[:50],
        "throughput_per_s": round(processed / dur, 2) if dur > 0 else 0,
        "slowest_file_s": round(slowest, 2),
        "coverage_pct": round(100 * processed / total, 1) if total else 0,
        "status": "complete" if (processed == total and total) else ("partial" if processed else "empty"),
        "by": author_session,
    }
    # the RUN RECORD — into the corpus (queryable telemetry) + attached to the channel (run history)
    src = f"dragnet/{channel}/{int(started)}"
    ev = _corpus.write_record(store, source_address=src, output=telemetry, kind="dragnet-run",
                              lineage={"session": author_session, "round": "dragnet", "project": project})
    try:
        _att.attach(channel, "dragnet_runs", ev["address"])
    except Exception as e:                              # attach failure must not lose the telemetry
        telemetry["_attach_warning"] = str(e)[:120]
    telemetry["run_record"] = ev["address"]
    return telemetry
