SOURCE_TYPE = {
    "id": "claude_code",
    "label": "Claude Code transcripts",
    "join_keys": ["author", "path", "time"],
    "desc": "Claude Code session transcripts — the default origin of board items. Correlates with other "
            "sources (e.g. a future `github` row) by a JOIN on shared author + file path + time, so GitHub "
            "history folds in WITHOUT a migration (Tim 2026-06-15: 'same author so they correlate').",
}
