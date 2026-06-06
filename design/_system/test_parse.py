"""RED→GREEN test for the address parser. Run: python3 test_parse.py
Real behaviour: extract every data-ui-ref from the mockups, tie each to its
feature+code via the address registry, and flag orphans BOTH ways —
used-but-unregistered (fiction/cruft) and registered-but-unused (a gap). No mocks."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import parse  # RED until parse.py exists

def run():
    screens = {
        "A.html": '<div data-ui-ref="ui://inbox/build-review">x</div>'
                  '<div data-ui-ref="ui://ghost/thing">y</div>',
        "B.html": '<button data-ui-ref="ui://toolbar/run">r</button>',
    }
    addresses = {
        "ui://inbox/build-review": {"region": "inbox", "represents": "WIRE-review", "code": "App.tsx:252"},
        "ui://toolbar/run":        {"region": "toolbar", "represents": "RUN-run", "code": "suite.py:406"},
        "ui://inspector/model-field": {"region": "inspector", "represents": "NODE-config", "code": "node_type.py"},
    }
    m = parse.build_map(screens, addresses)
    seen = {(e["screen"], e["address"]) for e in m["elements"]}
    assert ("A.html", "ui://inbox/build-review") in seen, "extraction missed a real element"
    assert ("B.html", "ui://toolbar/run") in seen, "extraction missed a real element"
    # feature + code resolved from the registry (the join)
    e = next(e for e in m["elements"] if e["address"] == "ui://inbox/build-review")
    assert e["feature"] == "WIRE-review" and e["code"] == "App.tsx:252", "feature/code not joined"
    # used but NOT registered -> unregistered orphan (fiction/cruft)
    assert "ui://ghost/thing" in m["orphans"]["unregistered"], "used-but-unregistered not flagged"
    # registered but used in NO screen -> unused orphan (a gap)
    assert "ui://inspector/model-field" in m["orphans"]["unused"], "registered-but-unused not flagged"
    print("PASS test_parse (extract + feature/code join + bidirectional orphans)")

run()
