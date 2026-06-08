"""skills/extract_decisions.py — agent-authored skill (Concurrent Cognition C 3b · #56/#58 write-half).
Authored DIRECTLY through the agent surface (create_skill); validated by import-in-a-temp-dir
before it ever reached the live skills/ tree. A registry ROW: skill://extract_decisions resolves to its
declared `content` (the reusable instructions a role reads)."""
SKILL = {
    "id": "extract_decisions",
    "content": "Read the document and list every DECISION it records, one per line, formatted as: <decision> - <rationale if stated>. Ignore non-decisions, questions, and open items.",
    "label": "Extract decisions",
    "description": "Instructions to extract DECISIONS from a document."
}
