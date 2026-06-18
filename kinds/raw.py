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
    # --- 2026-06-18: completed the default-lens kinds (grounded from each kind's own _emit message in
    #     runtime/suite.py, cognition.py, activation.py, session_supervisor.py — the system's own words,
    #     paraphrased into operator language; TENTATIVE for Tim/DNA). The AI-thinking layer reads "AI turn /
    #     AI minds / AI step" (never "cognition"); a cascade reads "flow" (matches the Flow lens); a journey
    #     reads "walk-through". Two live kinds (config_writer.git, projection.verify) are intentionally LEFT
    #     to the humanized fallback — no emit-site exists to ground them (config_writer was removed), and
    #     fabricating meaning would break the evidence rule. ---
    # The copy below was tightened after a fresh-eyes copy critic (non-technical reader): insider words —
    # "turn / wave / activated / context / flow / trial / debrief / surface / minds" — were translated to
    # plain English, and the journey.* trio was corrected (the names had implied a USER tour, but these are
    # the system RECORDING a path). The MEANING stays faithful to each kind's own _emit message.
    "cognition.turn.start": {"name": "The AI started thinking", "is": "The AI began a round of thinking (one or more helpers)."},
    "cognition.turn.done":  {"name": "The AI finished thinking","is": "The AI completed a round of thinking."},
    "cognition.part":       {"name": "A step in the AI's thinking","is": "One step within a longer round of AI thinking."},
    "cognition.wave":       {"name": "Several AI steps at once","is": "A batch of AI helpers ran together at the same time."},
    "cognition.inject":     {"name": "Background added",     "is": "Extra background was fed into the AI's thinking."},
    "cognition.reduce":     {"name": "AI answers merged",    "is": "The AI merged several answers into one."},
    "activation":           {"name": "AI helpers started",   "is": "A group of AI helpers was set running."},
    "ask":                  {"name": "Needs your input",     "is": "The system surfaced something for you to answer or decide."},
    "grow":                 {"name": "The system added to itself","is": "The assistant wrote a new piece of itself — waiting for your approval."},
    "decision.intent":      {"name": "A build proposed",     "is": "Something to build was surfaced for your approval."},
    "decision.dispatch":    {"name": "A decision put into action","is": "A recorded decision was sent to be carried out."},
    "decision.verify":      {"name": "A decision checked",   "is": "A decision's outcome was verified."},
    "cascade.save":         {"name": "A sequence saved",     "is": "A reusable sequence of steps was saved."},
    "review.start":         {"name": "A review started",     "is": "A review opened over a set of items."},
    "review.advance":       {"name": "Review went to the next","is": "The review moved to its next item."},
    "review.comment":       {"name": "A review comment",     "is": "Someone left a comment during a review."},
    "guide.start":          {"name": "A guide started",      "is": "A guided, step-by-step sequence began."},
    "journey.start":        {"name": "Path recording started","is": "The system started recording a path of where it went."},
    "journey.step":         {"name": "A step in a recorded path","is": "A recorded path moved to a new place."},
    "journey.stop":         {"name": "Path recording finished","is": "The system finished recording a path."},
    "trial.turn":           {"name": "A test-run exchange",  "is": "One back-and-forth inside a test run."},
    "trial.debrief.start":  {"name": "A test-run wrap-up",   "is": "A test run started its wrap-up review."},
    "dial":                 {"name": "A dial set",           "is": "A tuning control was changed to a new value."},
    "presentation_pref":    {"name": "A display preference", "is": "A learned preference for how something should be shown."},
    "react":                {"name": "The assistant reacted","is": "The assistant noticed something in the chat and responded."},
    "revert":               {"name": "A change undone",      "is": "A change the system made to itself was rolled back."},
    "agent_sessions.render_drop": {"name": "A skipped screen update","is": "A working session had a screen update that wasn't shown."},
}
