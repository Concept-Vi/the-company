"""edge_kinds/launched-by.py — edge kind 'launched-by' · face=lineage.

Seen in: ledger.edge. Inverse 'launches' is COMPOSED AT READ (never stored — law 4). [needs_review: face auto-assigned; confirm the JOB] 

NOTE: a STORED-REVERSE extractor artifact (the inverse of 'launches' emitted as its own row — a law-4 defect in the live ledger). Registered so the live table validates; composed-at-read covers queries. Ore: the extractor should stop emitting it."""
EDGE_KIND = {
    "id": 'launched-by',
    "directed": True,
    "inverse": 'launches',
    "face": 'lineage',
    "needs_review": True,
}
