"""RED→GREEN for check.py — the structural coherence + token-candidate finder.
Run: python3 test_check.py. Real behaviour: find hardcoded literals in mockups,
aggregate with counts, and match each to an existing token value (→ should-use-var)
or flag it as a candidate new token. No mocks, no models — pure structural floor."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check  # RED until check.py exists

def run():
    screens = {
        "f.html": '<div style="color:#54d6b0;padding:8px"><span style="color:#54d6b0"></span></div>',
        "g.html": '<b style="color:#abcdef"></b>',
    }
    lits = check.find_literals(screens["f.html"])
    assert "#54d6b0" in lits and "8px" in lits, f"literal extraction missed: {lits}"
    token_values = {"acc": "#54d6b0", "sp": "8px"}  # final resolved token values
    cand = check.candidate_tokens(screens, token_values)
    by = {c["literal"]: c for c in cand}
    assert by["#54d6b0"]["count"] == 2, "should count both occurrences across the corpus"
    assert by["#54d6b0"]["matches_token"] == "acc", "should match an existing token -> use var(--acc)"
    assert by["8px"]["matches_token"] == "sp", "px literal should match token 'sp'"
    assert by["#abcdef"]["matches_token"] is None, "#abcdef matches no token -> candidate NEW token"
    print("PASS test_check (literal find + count + token-match / new-candidate)")

run()
