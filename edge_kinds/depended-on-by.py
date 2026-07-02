"""edge_kinds/depended-on-by.py — edge kind 'depended-on-by' · face=knowledge.

Seen in: ledger.edge. Inverse 'depends-on' is COMPOSED AT READ (never stored — law 4). [needs_review: face auto-assigned; confirm the JOB] 

NOTE: a STORED-REVERSE extractor artifact (the inverse of 'depends-on' emitted as its own row — a law-4 defect in the live ledger). Registered so the live table validates; composed-at-read covers queries. Ore: the extractor should stop emitting it."""
EDGE_KIND = {
    "id": 'depended-on-by',
    "directed": True,
    "inverse": 'depends-on',
    "face": 'knowledge',
    "needs_review": True,
}
