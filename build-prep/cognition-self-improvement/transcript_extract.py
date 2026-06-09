#!/usr/bin/env python3
"""transcript_extract.py — ③ the transcript-miner's deterministic EXTRACT (G23, promoted from the proven
mine-lane logic — no model, no network). Parses Claude-Code session transcripts (*.jsonl) into EXCHANGE
units: one Tim-message + the assistant's response (text parts joined, INCLUDING post-tool conclusions —
the lane's reply-boundary fix: a tool_result record is itself type 'user' and must NOT start a new
exchange or truncate the reply).

Units feed capture(role='mine_exchange', projection='history') — the mined extracts persist + embed into
space='history' (the ⑨ durable-memory substrate; corpus, NOT episodic-memory — Tim's standing rule).

Bounded by design: caps per-exchange text, exchanges per file, and files per call — batches compose
toward the full 465 (the same incremental shape as exocortex_ingest). The floor: pure extraction.
"""
import json
import os

MAX_TIM = 1200          # per-exchange cap on Tim's message (the head carries the intent)
MAX_REPLY = 2000        # per-exchange cap on the assistant reply (head + tail carry the substance)
MIN_TIM = 25            # a Tim message shorter than this is a non-exchange (ack/handle)


def _text_of(content) -> str:
    """A transcript record's content → plain text (string or content-block list; tool blocks skipped)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(b.get("text", "") for b in content
                         if isinstance(b, dict) and b.get("type") == "text")
    return ""


def _is_tool_result_record(rec: dict) -> bool:
    """The reply-boundary fix: a tool_result rides as type='user' — it is NOT a new Tim message."""
    msg = rec.get("message") or {}
    content = msg.get("content")
    if isinstance(content, list):
        return any(isinstance(b, dict) and b.get("type") == "tool_result" for b in content)
    return False


def extract_exchanges(path: str, *, max_exchanges: int = 40) -> list[dict]:
    """One transcript → [{session, ts, tim, reply}] exchange units, capped. Resilient to bad lines."""
    session = os.path.basename(path).split(".")[0]
    out, tim_msg, tim_ts, reply_parts = [], None, None, []
    try:
        fh = open(path, encoding="utf-8")
    except OSError:
        return []
    with fh:
        for line in fh:
            try:
                rec = json.loads(line)
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            rtype = rec.get("type")
            msg = rec.get("message") or {}
            if rtype == "user" and not _is_tool_result_record(rec):
                # a REAL Tim message → close the previous exchange first
                if tim_msg is not None and reply_parts:
                    out.append({"session": session, "ts": tim_ts, "tim": tim_msg,
                                "reply": "\n".join(reply_parts)[:MAX_REPLY]})
                    if len(out) >= max_exchanges:
                        return out
                t = _text_of(msg.get("content")).strip()
                tim_msg = t[:MAX_TIM] if len(t) >= MIN_TIM else None
                tim_ts = rec.get("timestamp")
                reply_parts = []
            elif rtype == "assistant" and tim_msg is not None:
                t = _text_of(msg.get("content")).strip()
                if t:
                    reply_parts.append(t)
    if tim_msg is not None and reply_parts and len(out) < max_exchanges:
        out.append({"session": session, "ts": tim_ts, "tim": tim_msg,
                    "reply": "\n".join(reply_parts)[:MAX_REPLY]})
    return out


def transcripts_by_size(tdir: str, *, min_kb: int = 30, max_mb: int = 20) -> list[str]:
    """The transcript files worth mining, mid-size first (tiny = no dialogue; huge = mostly tool noise —
    they still get mined via the per-file exchange cap, just later)."""
    rows = []
    for fn in os.listdir(tdir):
        if not fn.endswith(".jsonl"):
            continue
        p = os.path.join(tdir, fn)
        sz = os.path.getsize(p)
        if sz < min_kb * 1024:
            continue
        rows.append((sz if sz <= max_mb * 1024 * 1024 else max_mb * 1024 * 1024 * 2 + sz, p))
    rows.sort()
    return [p for (_s, p) in rows]
