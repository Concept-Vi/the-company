"""judge — a role-mind: the judging leg, consumes the extractor's output (the +1 in N+1).
Binds the existing roles/judge_mining (judges mined/extracted facts) — the JUDGE half of
extraction-vs-judgment (small models extract; the judge decides). Takes the extractor's run:// output."""
MIND = {
    "id": "judge",
    "kind": "role",
    "role": "judge_mining",
    "desc": "the judge (binds roles/judge_mining) — weighs the extractor's structured facts + decides.",
}
