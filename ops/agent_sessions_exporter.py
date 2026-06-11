#!/usr/bin/env python3
"""agent_sessions_exporter — Claude Code session jsonl → searchable markdown corpus.

The Session Fabric's transcript-memory exporter (F1.4, guide §E). Streams every quiesced
main-session transcript under ``~/.claude/projects/<project>/<session-uuid>.jsonl`` into
one markdown file per session at ``~/corpora/claude-sessions/<project>/<session-uuid>.md``
— a derived, regenerable projection (the jsonl stays the source of truth; this md is a
render, never a versioned copy). The substrate indexes the output dir as a normal
markdown vault (the ``claude-platform-docs`` generated-corpus precedent); vault
registration is the LEAD's step, not this exporter's.

THE FILTER LAW (binding — Session Fabric Implementation Guide §E, synthesis Round 1b):
  KEEP   user + assistant text blocks (and plain-string content), the ai-title,
         one-line tool TRACES (tool name + key arg, never bodies).
  STRIP  tool_result blocks AND the duplicated top-level toolUseResult field (where
         secrets land), tool_use input bodies, attachment lines, bookkeeping line types
         (queue-operation, file-history-snapshot, bridge-session, permission-mode, mode,
         agent-setting, agent-name, system, …), noise-prefix user texts
         (<system-reminder, Caveat:, <command-*, [Request interrupted, <task-notification,
         the summarizer synthetic prompt) and isMeta lines, thinking blocks (config flag,
         default OFF).
  PLUS   a secret-regex redaction pass over everything kept (belt-and-braces).

FRESHNESS LAW: only sessions whose jsonl mtime is older than the quiesce window
(default >15 min) are exported — a live session's every-append would otherwise re-embed
its whole md each cycle. Re-export is idempotent: write-only-if-different.

READ-ONLY on the catalog: this process never writes under ~/.claude.

Title fallback chain (criteria F1.2, verified against the real corpus 2026-06-11):
ai-title (last occurrence wins) → custom-title (verified-real line type, last wins) →
last-prompt (the old ``lastPrompt`` text shape; the new ``leafUuid`` shape is resolved
against the session's own user lines) → first real user turn truncated → untitled+envelope.

Stdlib-only (the ops convention). Fail loud: per-file errors are collected and printed,
unknown line/block types are counted and reported (residue-as-data, never swallowed),
exit code 1 if any file failed.

Run:  python3 ops/agent_sessions_exporter.py [--limit N] [--project P] [--session ID] ...
Timer: company-agent-sessions-exporter.timer (ops/systemd/), registered in ops/services.json.
"""

import argparse
import json
import os
import re
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------- constants

DEFAULT_SOURCE = Path.home() / ".claude" / "projects"
DEFAULT_DEST = Path.home() / "corpora" / "claude-sessions"
STATE_BASENAME = ".exporter_state.json"
QUIESCE_MIN_DEFAULT = 15
SUBAGENT_MIN_BYTES = 2048      # sidechain stubs below this are warmup noise — skipped
TITLE_TRUNC = 80
TRACE_ARG_TRUNC = 100
SUBAGENT_FINAL_TRUNC = 8000    # final-text rollup cap per subagent (chars, post-filter)

# user-text prefixes that are machinery, not conversation (synthesis Round 1b rule 5
# + the summarizer-call synthetic prompt, rule 7)
NOISE_PREFIXES = (
    "<system-reminder",
    "Caveat:",
    "<command-name",
    "<command-message",
    "<local-command-stdout",
    "[Request interrupted",
    "<task-notification",
    "Context: This summary will be shown",
)

# line types we consume for METADATA only (never body)
META_TYPES = {"ai-title", "custom-title", "last-prompt"}
# line types that are body candidates
BODY_TYPES = {"user", "assistant"}
# everything else (system, attachment, queue-operation, file-history-snapshot,
# bridge-session, permission-mode, mode, agent-setting, agent-name, …) is stripped
# and COUNTED by type — residue is reported, never silently swallowed.

# tool_use input keys that make a meaningful one-line trace, in preference order
TRACE_KEYS = (
    "command", "file_path", "path", "pattern", "query", "url",
    "prompt", "description", "skill", "name", "subject",
)

# secret-redaction patterns (synthesis rule 6 + conservative distinctive-prefix
# extensions). Order matters: private-key blocks first (they contain everything).
REDACTIONS = [
    ("private-key",
     re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"
                r"(?:[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----|[\s\S]*\Z)")),
    ("api-key", re.compile(r"\bsk-[A-Za-z0-9_\-]{16,}")),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_\-=]{20,}(?:\.[A-Za-z0-9_\-=]+)*")),
    ("slack-token", re.compile(r"\bxox[abprsoe]-[A-Za-z0-9\-]{8,}")),
    ("aws-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("github-token",
     re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})")),
    ("hf-token", re.compile(r"\bhf_[A-Za-z0-9]{20,}\b")),
    ("google-key", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
]
# key = value / key: value assignments with long opaque values — redact the VALUE only
ASSIGNMENT_RE = re.compile(
    r"(?i)\b(api[_\-]?key|secret[_\-]?key|access[_\-]?token|auth[_\-]?token"
    r"|password|passwd|client[_\-]?secret)\b(\s*[:=]\s*)(['\"]?)([A-Za-z0-9_\-./+]{16,})\3"
)


# ---------------------------------------------------------------- redaction

def redact(text, counter):
    """Secret-pattern redaction pass. Returns redacted text; counts hits by kind."""
    if not text:
        return text
    for kind, rx in REDACTIONS:
        text, n = rx.subn(f"[redacted:{kind}]", text)
        if n:
            counter[kind] += n

    def _assign_sub(m):
        counter["assignment"] += 1
        return f"{m.group(1)}{m.group(2)}[redacted:assignment]"

    text = ASSIGNMENT_RE.sub(_assign_sub, text)
    return text


# ---------------------------------------------------------------- filters

def is_noise_user_text(text):
    t = text.lstrip()
    return any(t.startswith(p) for p in NOISE_PREFIXES) or not t.strip()


def tool_trace(name, tool_input):
    """One-line trace: Name(key arg). Bodies never survive — only a truncated key arg."""
    arg = ""
    if isinstance(tool_input, dict):
        for k in TRACE_KEYS:
            v = tool_input.get(k)
            if isinstance(v, (str, int, float)) and str(v).strip():
                arg = str(v)
                break
        else:
            for v in tool_input.values():
                if isinstance(v, (str, int, float)) and str(v).strip():
                    arg = str(v)
                    break
    elif isinstance(tool_input, (str, int, float)):
        arg = str(tool_input)
    arg = " ".join(str(arg).split())          # collapse to one line
    if len(arg) > TRACE_ARG_TRUNC:
        arg = arg[:TRACE_ARG_TRUNC] + "…"
    return f"{name}({arg})" if arg else f"{name}()"


def _ts_human(iso):
    if not iso:
        return ""
    try:
        return datetime.fromisoformat(iso.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return iso[:16]


# ---------------------------------------------------------------- per-session export

class SessionExport:
    """Streams ONE main-session jsonl (never json.load — the 238MB outlier exists)
    and accumulates filtered turns + metadata."""

    def __init__(self, include_thinking=False):
        self.include_thinking = include_thinking
        self.turns = []                  # list of {"who": "tim"|"claude", "ts": str, "parts": [str]}
        self.counters = Counter()        # strip/keep accounting
        self.redactions = Counter()
        self.unknown_line_types = Counter()
        self.unknown_block_types = Counter()
        # metadata
        self.session_id = None
        self.cwd = None
        self.git_branch = None
        self.version = None
        self.first_ts = None
        self.last_ts = None
        self.ai_title = None             # last occurrence wins (tail-heavy in reality)
        self.custom_title = None
        self.last_prompt_text = None
        self.last_prompt_leaf = None
        self.first_user_text = None
        self._user_heads = {}            # uuid -> head of user text (for leafUuid resolution)
        self._open_claude = None

    # -- line dispatch ------------------------------------------------------

    def feed_line(self, raw):
        try:
            obj = json.loads(raw)
        except (json.JSONDecodeError, UnicodeDecodeError):
            self.counters["unparseable_lines"] += 1
            return
        if not isinstance(obj, dict):
            self.counters["unparseable_lines"] += 1
            return
        ltype = obj.get("type")
        if ltype in BODY_TYPES:
            self._feed_conversation(obj, ltype)
        elif ltype == "ai-title":
            t = obj.get("aiTitle")
            if isinstance(t, str) and t.strip():
                self.ai_title = t.strip()
        elif ltype == "custom-title":
            t = obj.get("customTitle")
            if isinstance(t, str) and t.strip():
                self.custom_title = t.strip()
        elif ltype == "last-prompt":
            t = obj.get("lastPrompt")
            if isinstance(t, str) and t.strip():
                self.last_prompt_text = t.strip()
            leaf = obj.get("leafUuid")
            if isinstance(leaf, str):
                self.last_prompt_leaf = leaf
        else:
            # bookkeeping/attachment/system/unknown — stripped, counted by type
            self.counters["stripped_lines"] += 1
            self.unknown_line_types[str(ltype)] += 1

    def _envelope(self, obj):
        if self.session_id is None:
            self.session_id = obj.get("sessionId")
        if self.cwd is None and obj.get("cwd"):
            self.cwd = obj["cwd"]
        if obj.get("gitBranch"):
            self.git_branch = obj["gitBranch"]
        if obj.get("version"):
            self.version = obj["version"]
        ts = obj.get("timestamp")
        if ts:
            if self.first_ts is None:
                self.first_ts = ts
            self.last_ts = ts

    def _feed_conversation(self, obj, ltype):
        self._envelope(obj)
        msg = obj.get("message")
        content = msg.get("content") if isinstance(msg, dict) else None

        if "toolUseResult" in obj:
            self.counters["toolUseResult_stripped"] += 1   # the duplicated secret carrier

        if ltype == "user":
            if obj.get("isMeta"):
                self.counters["meta_user_stripped"] += 1
                return
            texts = []
            if isinstance(content, str):
                texts = [content]
            elif isinstance(content, list):
                for block in content:
                    if not isinstance(block, dict):
                        continue
                    btype = block.get("type")
                    if btype == "text":
                        texts.append(block.get("text", ""))
                    elif btype in ("tool_result", "advisor_tool_result"):
                        self.counters["tool_result_stripped"] += 1
                    else:
                        self.unknown_block_types[str(btype)] += 1
            kept = [t for t in texts if t and not is_noise_user_text(t)]
            for t in texts:
                if t and t not in kept:
                    self.counters["noise_user_text_stripped"] += 1
            if not kept:
                return
            text = "\n\n".join(kept).strip()
            uuid = obj.get("uuid")
            if uuid:
                self._user_heads[uuid] = " ".join(text.split())[:TITLE_TRUNC * 2]
            if self.first_user_text is None:
                self.first_user_text = " ".join(text.split())
            text = redact(text, self.redactions)
            self._open_claude = None
            self.turns.append({"who": "tim", "ts": obj.get("timestamp"), "parts": [text]})
            self.counters["user_turns_kept"] += 1

        else:  # assistant
            if not isinstance(content, list):
                if isinstance(content, str) and content.strip():
                    self._claude_part(redact(content.strip(), self.redactions))
                return
            texts, traces = [], []
            for block in content:
                if not isinstance(block, dict):
                    continue
                btype = block.get("type")
                if btype == "text":
                    t = block.get("text", "")
                    if t.strip():
                        texts.append(t.strip())
                elif btype == "thinking":
                    if self.include_thinking:
                        t = block.get("thinking", "")
                        if t.strip():
                            texts.append("*[thinking]* " + t.strip())
                    else:
                        self.counters["thinking_stripped"] += 1
                elif btype in ("tool_use", "server_tool_use"):
                    traces.append(tool_trace(block.get("name", "?"), block.get("input")))
                    self.counters["tool_use_traced"] += 1
                elif btype in ("tool_result", "advisor_tool_result"):
                    self.counters["tool_result_stripped"] += 1
                else:
                    self.unknown_block_types[str(btype)] += 1
            for t in texts:
                self._claude_part(redact(t, self.redactions))
            if traces:
                line = "> tools: " + ", ".join(
                    redact(tr, self.redactions) for tr in traces)
                self._claude_part(line)

    def _claude_part(self, part):
        if self._open_claude is None:
            self._open_claude = {"who": "claude", "ts": None, "parts": []}
            self.turns.append(self._open_claude)
            self.counters["claude_turns_kept"] += 1
        self._open_claude["parts"].append(part)

    # -- title chain ---------------------------------------------------------

    def resolve_title(self):
        """ai-title → custom-title → last-prompt → first user turn → untitled+envelope."""
        if self.ai_title:
            return self.ai_title[:200], "ai-title"
        if self.custom_title:
            return self.custom_title[:200], "custom-title"
        if self.last_prompt_text:
            return self.last_prompt_text[:TITLE_TRUNC], "last-prompt"
        if self.last_prompt_leaf and self.last_prompt_leaf in self._user_heads:
            return self._user_heads[self.last_prompt_leaf][:TITLE_TRUNC], "last-prompt"
        if self.first_user_text:
            return self.first_user_text[:TITLE_TRUNC], "first-user-turn"
        sid = (self.session_id or "unknown")[:8]
        return f"Untitled session {sid}", "untitled"


def collect_subagents(project_dir, session_id, agent_index, counters, redactions):
    """Sidechain rollup (synthesis 2.2): final assistant text only, stubs <2KB skipped.
    Sources: top-level agent-*.jsonl whose first-line sessionId matches, and
    <session-uuid>/subagents/agent-*.jsonl."""
    paths = list(agent_index.get(session_id, []))
    nested = project_dir / session_id / "subagents"
    if nested.is_dir():
        paths.extend(sorted(nested.glob("agent-*.jsonl")))
    sections = []
    for p in paths:
        try:
            if p.stat().st_size < SUBAGENT_MIN_BYTES:
                counters["subagent_stubs_skipped"] += 1
                continue
            first_prompt, final_text = None, None
            with open(p, encoding="utf-8", errors="replace") as fh:
                for raw in fh:
                    try:
                        obj = json.loads(raw)
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        continue
                    if not isinstance(obj, dict):
                        continue
                    msg = obj.get("message")
                    content = msg.get("content") if isinstance(msg, dict) else None
                    if obj.get("type") == "user" and first_prompt is None:
                        if isinstance(content, str) and not is_noise_user_text(content):
                            first_prompt = " ".join(content.split())[:TITLE_TRUNC]
                        elif isinstance(content, list):
                            for b in content:
                                if isinstance(b, dict) and b.get("type") == "text":
                                    t = b.get("text", "")
                                    if t and not is_noise_user_text(t):
                                        first_prompt = " ".join(t.split())[:TITLE_TRUNC]
                                        break
                    elif obj.get("type") == "assistant" and isinstance(content, list):
                        texts = [b.get("text", "").strip() for b in content
                                 if isinstance(b, dict) and b.get("type") == "text"
                                 and b.get("text", "").strip()]
                        if texts:
                            final_text = "\n\n".join(texts)
            if final_text:
                final_text = redact(final_text, redactions)
                if len(final_text) > SUBAGENT_FINAL_TRUNC:
                    final_text = final_text[:SUBAGENT_FINAL_TRUNC] + "\n\n*[truncated]*"
                # the heading is user text too — same redaction pass as every kept string
                heading = redact(first_prompt or p.stem, redactions)
                sections.append((heading, final_text))
                counters["subagents_rolled_up"] += 1
        except OSError as e:
            counters["subagent_errors"] += 1
            print(f"  ! subagent read failed {p}: {e}", file=sys.stderr)
    return sections


def render_markdown(sx, project_slug, source_bytes, subagent_sections):
    title, title_source = sx.resolve_title()
    title = redact(title, sx.redactions)
    fm = [
        "---",
        "type: session-transcript",
        f"session_id: {sx.session_id or 'unknown'}",
        f"project: {json.dumps(project_slug)}",
        f"cwd: {json.dumps(sx.cwd or '')}",
        f"git_branch: {json.dumps(sx.git_branch or '')}",
        f"title: {json.dumps(title)}",
        f"title_source: {title_source}",
        f"started: {sx.first_ts or ''}",
        f"last_event: {sx.last_ts or ''}",
        f"cc_version: {sx.version or ''}",
        f"turns: {sx.counters['user_turns_kept'] + sx.counters['claude_turns_kept']}",
        f"subagents: {len(subagent_sections)}",
        f"source_bytes: {source_bytes}",
        f"exported_at: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        "---",
        "",
        f"# {title}",
        "",
    ]
    body = []
    n = 0
    for turn in sx.turns:
        n += 1
        if turn["who"] == "tim":
            ts = _ts_human(turn["ts"])
            body.append(f"## Turn {n} — Tim" + (f" ({ts})" if ts else ""))
        else:
            body.append(f"## Turn {n} — Claude")
        body.append("")
        body.append("\n\n".join(turn["parts"]))
        body.append("")
    for first_prompt, final_text in subagent_sections:
        body.append(f"## Subagent: {first_prompt}")
        body.append("")
        body.append(final_text)
        body.append("")
    return "\n".join(fm + body)


def export_one(jsonl_path, project_dir, dest_root, agent_index, include_thinking):
    """Export one main session. Returns (md_path, stats_dict). Raises on hard failure."""
    sx = SessionExport(include_thinking=include_thinking)
    size = jsonl_path.stat().st_size
    with open(jsonl_path, encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            sx.feed_line(raw)
    if sx.session_id is None:
        sx.session_id = jsonl_path.stem
    subagent_sections = collect_subagents(
        project_dir, jsonl_path.stem, agent_index, sx.counters, sx.redactions)
    md = render_markdown(sx, project_dir.name, size, subagent_sections)

    out_dir = dest_root / project_dir.name
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{jsonl_path.stem}.md"

    # write-only-if-different — but the exported_at line changes every run, so compare
    # everything EXCEPT that line (idempotence law: same jsonl → same md → substrate skips)
    def _stable(text):
        return "\n".join(l for l in text.splitlines() if not l.startswith("exported_at:"))
    if out_path.exists():
        try:
            if _stable(out_path.read_text(encoding="utf-8")) == _stable(md):
                return out_path, {"in": size, "out": out_path.stat().st_size,
                                  "written": False, "sx": sx}
        except (OSError, UnicodeDecodeError):
            pass  # unreadable existing output → rewrite it
    tmp = out_path.with_suffix(".md.tmp")
    tmp.write_text(md, encoding="utf-8")
    os.replace(tmp, out_path)
    return out_path, {"in": size, "out": len(md.encode("utf-8")), "written": True, "sx": sx}


# ---------------------------------------------------------------- catalog walk

def build_agent_index(project_dir):
    """Map parent sessionId -> [top-level agent-*.jsonl] by reading ONE line each."""
    index = {}
    for p in sorted(project_dir.glob("agent-*.jsonl")):
        try:
            with open(p, encoding="utf-8", errors="replace") as fh:
                first = fh.readline()
            sid = json.loads(first).get("sessionId") if first.strip() else None
            if sid:
                index.setdefault(sid, []).append(p)
        except (OSError, json.JSONDecodeError, UnicodeDecodeError, AttributeError):
            continue  # unlinkable sidechain — main export is unaffected
    return index


def find_candidates(source, projects_filter, sessions_filter):
    out = []
    for project_dir in sorted(source.iterdir()):
        if not project_dir.is_dir():
            continue
        if projects_filter and project_dir.name not in projects_filter:
            continue
        for p in sorted(project_dir.glob("*.jsonl")):
            if p.name.startswith("agent-"):
                continue
            if sessions_filter and p.stem not in sessions_filter:
                continue
            out.append((project_dir, p))
    return out


def load_state(path):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            print(f"  ! state file unreadable ({e}) — full re-scan", file=sys.stderr)
    return {}


def save_state(path, state):
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(state, indent=1), encoding="utf-8")
    os.replace(tmp, path)


# ---------------------------------------------------------------- main

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    ap.add_argument("--dest", type=Path, default=DEFAULT_DEST)
    ap.add_argument("--quiesce-min", type=float, default=QUIESCE_MIN_DEFAULT,
                    help="only export sessions idle longer than this (mtime), default 15")
    ap.add_argument("--no-quiesce", action="store_true",
                    help="ignore the quiesce window (tests only)")
    ap.add_argument("--limit", type=int, default=0,
                    help="export at most N sessions (most recently modified first)")
    ap.add_argument("--project", action="append", default=[],
                    help="only these project dirs (repeatable)")
    ap.add_argument("--session", action="append", default=[],
                    help="only these session ids (repeatable)")
    ap.add_argument("--force", action="store_true",
                    help="re-export even if (size,mtime) unchanged in state")
    ap.add_argument("--include-thinking", action="store_true",
                    help="keep thinking blocks (default OFF per the filter law)")
    args = ap.parse_args(argv)

    source = args.source.expanduser()
    dest = args.dest.expanduser()
    if not source.is_dir():
        print(f"FATAL: source catalog not found: {source}", file=sys.stderr)
        return 2
    dest.mkdir(parents=True, exist_ok=True)
    state_path = dest / STATE_BASENAME
    state = load_state(state_path)

    now = time.time()
    quiesce_s = 0 if args.no_quiesce else args.quiesce_min * 60

    candidates = find_candidates(source, set(args.project), set(args.session))
    totals = Counter()
    totals["mains_seen"] = len(candidates)

    work = []
    for project_dir, p in candidates:
        try:
            st = p.stat()
        except OSError:
            totals["stat_failed"] += 1
            continue
        if st.st_size == 0:
            totals["empty_skipped"] += 1
            continue
        if quiesce_s and (now - st.st_mtime) < quiesce_s:
            totals["quiesce_skipped"] += 1
            continue
        key = str(p)
        rec = state.get(key)
        out_md = dest / project_dir.name / f"{p.stem}.md"
        if (not args.force and rec and rec.get("size") == st.st_size
                and rec.get("mtime") == st.st_mtime and out_md.exists()):
            totals["unchanged_skipped"] += 1
            continue
        work.append((st.st_mtime, project_dir, p, st))
    work.sort(key=lambda w: w[0], reverse=True)
    if args.limit:
        work = work[:args.limit]

    agent_indexes = {}
    errors = []
    run_counters = Counter()
    run_redactions = Counter()
    unknown_lines = Counter()
    unknown_blocks = Counter()
    in_bytes = out_bytes = 0

    for _, project_dir, p, st in work:
        if project_dir not in agent_indexes:
            agent_indexes[project_dir] = build_agent_index(project_dir)
        try:
            md_path, r = export_one(p, project_dir, dest,
                                    agent_indexes[project_dir], args.include_thinking)
            sx = r["sx"]
            in_bytes += r["in"]
            out_bytes += r["out"]
            run_counters.update(sx.counters)
            run_redactions.update(sx.redactions)
            unknown_lines.update(sx.unknown_line_types)
            unknown_blocks.update(sx.unknown_block_types)
            totals["exported" if r["written"] else "rewrites_avoided"] += 1
            state[str(p)] = {"size": st.st_size, "mtime": st.st_mtime,
                             "md": str(md_path),
                             "exported_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
        except Exception as e:  # noqa: BLE001 — collect, report loudly, keep the batch
            errors.append((str(p), repr(e)))
            totals["errors"] += 1

    save_state(state_path, state)

    pct = (out_bytes / in_bytes * 100) if in_bytes else 0.0
    print("agent_sessions_exporter — run summary")
    print(f"  mains seen: {totals['mains_seen']}   quiesce-skipped: {totals['quiesce_skipped']}"
          f"   unchanged: {totals['unchanged_skipped']}   empty: {totals['empty_skipped']}"
          f"   exported: {totals['exported']}   rewrites-avoided: {totals['rewrites_avoided']}"
          f"   errors: {totals['errors']}")
    print(f"  bytes: {in_bytes:,} in → {out_bytes:,} out  ({pct:.1f}% of source)")
    print(f"  kept: user turns {run_counters['user_turns_kept']:,} · claude turns "
          f"{run_counters['claude_turns_kept']:,} · tool traces {run_counters['tool_use_traced']:,}")
    print(f"  stripped: tool_result blocks {run_counters['tool_result_stripped']:,} · "
          f"toolUseResult fields {run_counters['toolUseResult_stripped']:,} · "
          f"thinking {run_counters['thinking_stripped']:,} · "
          f"noise user-texts {run_counters['noise_user_text_stripped']:,} · "
          f"meta lines {run_counters['meta_user_stripped']:,} · "
          f"other lines {run_counters['stripped_lines']:,}")
    print(f"  subagents: rolled up {run_counters['subagents_rolled_up']:,} · "
          f"stubs skipped {run_counters['subagent_stubs_skipped']:,}")
    if run_redactions:
        print("  redactions: " + " · ".join(f"{k} {v}" for k, v in run_redactions.most_common()))
    if unknown_blocks:
        print(f"  UNKNOWN content-block types (residue — check the filter law): {dict(unknown_blocks)}")
    if run_counters["unparseable_lines"]:
        print(f"  unparseable lines: {run_counters['unparseable_lines']}")
    stripped_types = {k: v for k, v in unknown_lines.items()}
    if stripped_types:
        print(f"  stripped line types: {stripped_types}")
    if errors:
        print("\n  FAILURES (loud, batch continued):", file=sys.stderr)
        for path, err in errors:
            print(f"    ✗ {path}: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
