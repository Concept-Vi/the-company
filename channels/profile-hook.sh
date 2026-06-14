#!/usr/bin/env bash
# SessionStart hook — reminds a session to write its OWN fabric profile.
#
# Design (Tim-direct 2026-06-14): the AGENT writes its own profile. This hook only INJECTS A REMINDER;
# the agent calls the company-channel `profile` tool, which merges its self-described fields (model,
# role, focus, expertise) into its own registry entry — it knows its own handle, so whatever handle was
# assigned is fine. Self-gating: phrased "if you have a profile tool", so it is harmless for any
# non-fabric session (no such tool → the agent simply ignores it).
#
# BOUNDARY: this is a startup-loaded hook — Tim wires it into ~/.claude/settings.json himself (an agent
# does not self-edit startup config). Wiring snippet:
#   "hooks": { "SessionStart": [ { "hooks": [
#       { "type": "command", "command": "/home/tim/company/channels/profile-hook.sh" } ] } ] }
cat <<'JSON'
{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"If you are a Company cross-session channel fabric member (you have a `profile` tool), call it near the start to write WHO YOU ARE — your model (e.g. claude-fable-5), your role, and your focus (what you are working on) — so other sessions can see who they are talking to. The profile merges into your own registry entry; you know your own handle."}}
JSON
