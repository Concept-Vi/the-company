# THE KINDS REGISTRY — human meaning for each event KIND (the sectors of the data-driven "Kinds" wheel).
# Mirrors bindings/raw.py: ONE data map (NOT 51 files), the SAME legibility-type meta shape as the bindings
# (composition ch-2mnxl9j0, 2026-06-17: "same legibility-type, OWN registry"). The instrument reads this
# DECLARED-FIRST for the tapped sector and renders it; un-seeded kinds fall back to a humanized id (split on
# . _ - / + title-case) so they're still legible. The meaning lives HERE (the data), never in the instrument.
#
# TENTATIVE draft copy — Tim/DNA ratify; the field-set is journey-gated (OPERATOR-SURFACE-LOOP.md OQ1–4). The
# operator NEVER sees the machine kind-id; only `name` + `is`. Seeded with the kinds grounded from the live
# store + runtime emit-sites (verified in runtime/suite.py, runtime/session_supervisor.py, runtime/cognition.py).
# composition's validate/backfill set-diff finds any kind present in the data but missing here.
KIND_META = {
    "corpus.record":        {"name": "A note saved",       "is": "The system wrote something into its memory."},
    "corpus.content":       {"name": "Content saved",      "is": "A piece of content was stored in the memory."},
    "op.run":               {"name": "A job finished",     "is": "An operation ran to completion (and how long it took)."},
    "run":                  {"name": "A run",              "is": "Something ran."},
    "cognition.role.fire":  {"name": "An AI step started", "is": "One of the AI minds began a step."},
    "cognition.role.ran":   {"name": "An AI step finished","is": "One of the AI minds completed a step."},
    "cognition.items":      {"name": "AI made results",    "is": "An AI step produced its results."},
    "agent_sessions.turn":  {"name": "A session turn",     "is": "A working session finished one back-and-forth."},
    "agent_sessions.idle":  {"name": "A session went quiet","is": "A working session paused — no activity for a while."},
    "agent_sessions.spawned":{"name": "A session started","is": "A new working session was started."},
    "agent_sessions.closed": {"name": "A session ended",  "is": "A working session finished and closed."},
    "agent_sessions.registered":{"name": "A session joined","is": "A working session joined the fabric."},
    "annotation":           {"name": "A note",            "is": "A comment or note attached to something."},
    "apply":                {"name": "A change applied",  "is": "A change was applied to the system."},
    "chat":                 {"name": "A message",          "is": "A message in a conversation."},
    "voice":                {"name": "A spoken message",   "is": "Something said aloud in a voice conversation."},
    "connect":              {"name": "Two things linked",  "is": "Two parts were wired together."},
    "create":               {"name": "Something new",      "is": "Something new was made."},
    "move":                 {"name": "Something moved",    "is": "Something was moved."},
    "delete":               {"name": "Something removed",  "is": "Something was deleted."},
    "warning":              {"name": "A warning",          "is": "The system flagged a problem worth noticing."},
    "error":                {"name": "An error",           "is": "Something went wrong."},
    "config":               {"name": "A setting changed",  "is": "A setting was changed."},
    "mode":                 {"name": "A mode change",      "is": "The system switched modes."},
    "decision":             {"name": "A decision",         "is": "A choice the system recorded."},
    "approve":              {"name": "An approval",        "is": "Something was approved."},
    "resolve":              {"name": "A resolution",       "is": "Something was resolved."},
}
