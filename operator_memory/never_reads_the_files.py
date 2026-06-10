"""operator_memory/never_reads_the_files.py — the standing context every agent needs FIRST (GC15 row)."""
MEMORY = {
    "id": "never_reads_the_files",
    "rule": "Tim has never read, reviewed, or written the code or files in this system and never will — explain everything at his altitude (plain language, relationships, visuals), assume zero file-context, and never treat 'it's in the docs' as him knowing it.",
    "why": "The system is 100% AI-driven by design; he holds the vision and decides on outcomes. Communication that assumes file-knowledge silently excludes him from his own system.",
    "evidence": [
        {"quote": "remember I am not a developer and I don't read or write or review any of the code or files that you do", "source": "2026-06-10 (restated; standing since the project frame)"},
        {"quote": "this is 100% AI driven and there are no humans ever reading or reviewing or writing any of this", "source": "2026-06-10, the common-memory directive"}],
    "scope": {"when": "any communication with Tim"},
    "status": "confirmed",
    "confirmed": "standing across the whole record; restated verbatim 2026-06-10",
}
