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


# Tim's DRAGNET LAW (2026-06-23): "whenever a dragnet is called it must be assumed it's the entire thing,
# except for what's specifically stated not to be included." So the denominator = the WHOLE tree (git-ignored
# dirs INCLUDED — they're often the real foundation, e.g. counterpart/design's reference/). Exclusions are
# EXPLICIT (`exclude` arg) + always RECORDED with a reason (never a silent/curated subset). These are the
# only DEFAULT excludes (junk/secrets/binaries that would poison the corpus), each justified.
_DEFAULT_EXCLUDE_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".cache"}
_SECRET_HINTS = (".secret", ".secrets", ".key", ".crt", ".pem", "id_rsa", ".env")
_BINARY_EXT = {".onnx", ".bin", ".wav", ".pt", ".safetensors", ".pyc", ".so", ".dylib", ".zip", ".gz"}


def _enumerate(input_dir: str, extensions=None, exclude=None) -> tuple[list[str], list[dict]]:
    """The DENOMINATOR — every file under input_dir EXCEPT what's explicitly excluded (Tim's law: assume the
    entire thing). git-ignored content dirs are INCLUDED. Returns (included_files, excluded_records) — every
    exclusion carries {file, reason} so coverage is provable + nothing is silently dropped."""
    extra_dirs = set(exclude or [])
    included, excluded = [], []
    for root, dirs, files in os.walk(input_dir):
        # prune excluded dirs in-place (recorded)
        keep = []
        for d in dirs:
            if d in _DEFAULT_EXCLUDE_DIRS or d in extra_dirs:
                excluded.append({"file": os.path.relpath(os.path.join(root, d), input_dir), "reason": f"excluded-dir:{d}"})
            else:
                keep.append(d)
        dirs[:] = keep
        for fn in files:
            fp = os.path.join(root, fn)
            rel = os.path.relpath(fp, input_dir)
            ext = os.path.splitext(fn)[1].lower()
            low = fn.lower()
            if any(h in low for h in _SECRET_HINTS):
                excluded.append({"file": rel, "reason": "secret/credential — never embed into the corpus"})
            elif ext in _BINARY_EXT:
                excluded.append({"file": rel, "reason": f"binary:{ext}"})
            elif extensions and ext not in extensions:
                excluded.append({"file": rel, "reason": f"extension-filter (not in {sorted(extensions)})"})
            else:
                included.append(fp)
    return sorted(included), excluded


def run_dragnet(store, *, channel: str, input_dir: str, author_session: str, kind: str = "image",
                ingest_one=None, ingest_batch=None, extensions=None, exclude=None,
                retries: int = 2, project: str = "company") -> dict:
    """Issue a TRACKED dragnet FOR `channel` over `input_dir`. Outputs RESOLVE to <scheme>://<channel>/<rel>
    (variable resolution from the input). The RUN is tracked (times/processed/failed/retries/throughput/
    coverage) → a run-record into the corpus + attached to the channel. Tim's law: the denominator is the
    WHOLE tree (git-ignored INCLUDED) except `exclude` (always recorded with a reason).

    Two ingest seams (reuse-don't-parallel — the extractor PLUGS IN, this is the tracked-run wrapper):
      • ingest_one(store, fp, channel, rel)->address — PER-FILE (default for kind='image').
      • ingest_batch(store, files, channel)->{addresses, processed, failed, errors[, extra]} — BATCH-CONCURRENT
        (fork's 32-way code_archaeology cascade plugs in here; preserves the fan + step-gate + throughput)."""
    if not channel or not input_dir or not author_session:
        raise DragnetError("run_dragnet needs `channel`, `input_dir`, and `author_session`.")
    if not os.path.isdir(input_dir):
        raise DragnetError(f"input_dir {input_dir!r} is not a directory — fail loud (never a silent empty run).")

    exts = extensions or (set(_IMG_EXT) if kind == "image" else None)
    files, excluded = _enumerate(input_dir, exts, exclude)
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

    processed, failed, retried, errors, slowest = 0, 0, 0, [], 0.0
    addresses = []
    if ingest_batch is not None:
        # BATCH-CONCURRENT seam — fork's 32-way cascade runs the whole file list at once (preserves the fan +
        # step-gate + throughput). It returns its own processed/failed/errors; cc_dragnet wraps the TIMING +
        # coverage + telemetry-record + channel-attach around it (the ONE tracked-run shape).
        res = ingest_batch(store, files, channel) or {}
        addresses = list(res.get("addresses", []))
        processed = int(res.get("processed", len(addresses)))
        failed = int(res.get("failed", 0))
        retried = int(res.get("retries", 0))
        errors = list(res.get("errors", []))[:50]
        batch_extra = res.get("extra", {})
    else:
        ingest = ingest_one or (_ingest_image if kind == "image" else None)
        if ingest is None:
            raise DragnetError(f"kind={kind!r} has no built-in ingester — pass `ingest_one` (per-file) or "
                               f"`ingest_batch` (concurrent — fork's engine plugs in here).")
        batch_extra = {}
        for fp in files:
            rel = os.path.relpath(fp, input_dir)
            t0 = time.time()
            for attempt in range(retries + 1):
                try:
                    addr = ingest(fp, rel) if ingest is _ingest_image else ingest(store, fp, channel, rel)
                    addresses.append(addr)
                    processed += 1
                    break
                except Exception as e:                  # noqa: BLE001 — track every fail/retry, never swallow
                    if attempt < retries:
                        retried += 1
                        continue
                    failed += 1
                    errors.append({"file": rel, "error": str(e)[:160]})
            slowest = max(slowest, time.time() - t0)

    ended = time.time()
    dur = ended - started
    total = len(files)
    denominator = total + len(excluded)
    telemetry = {
        "channel": channel, "input_dir": input_dir, "kind": kind,
        "output_prefix": f"image://{channel}" if kind == "image" else f"{kind}://{channel}",
        "started": started_iso, "duration_s": round(dur, 2),
        # COVERAGE LEDGER (Tim's law): denominator = whole tree; every file is processed | failed | excluded(+reason)
        "denominator": denominator, "files_total": total,
        "processed": processed, "failed": failed, "retries": retried,
        "excluded_count": len(excluded), "excluded": excluded[:100],
        "errors": errors[:50],
        "throughput_per_s": round(processed / dur, 2) if dur > 0 else 0,
        "slowest_file_s": round(slowest, 2),
        "coverage_pct": round(100 * processed / total, 1) if total else 0,
        # fail-loud invariant: every enumerated-or-excluded file is accounted for (no silent drop)
        "fail_loud_ok": (processed + failed + len(excluded)) == denominator,
        "status": "complete" if (processed == total and total) else ("partial" if processed else "empty"),
        "by": author_session, **({"extra": batch_extra} if batch_extra else {}),
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
