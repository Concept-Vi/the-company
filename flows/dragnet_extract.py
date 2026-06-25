"""flows/dragnet_extract.py — PROPOSE a dragnet extraction bake (unify-exercise 2026-06-26).

The dragnet joins the flows surface so it is configurable THROUGH a tool: an agent can PROPOSE a bake
(scope / grain-asset / filters) via flows(op='run', flow='dragnet_extract'), and it surfaces ONE
'dragnet_bake' inbox item for the operator. It does NOT run the bake — proposes_only:True is the floor,
and the ~4h side-effecting extract-once bake is OPERATOR-ONLY (Q5/F7): the operator fires it via the
--confirm CLI door (ops/dragnet_extract.py --all --confirm) after the gated checklist. So this flow
honors S12 (agents propose, never dispatch) AND F7 (a flow can't execute) while making the dragnet
addressable from the same surface as every other chain.

The proposed payload carries the exact CLI the operator runs, the registry roles the bake will read
(roles/dragnet_{coarse,fine}.py — +dragnet_design when design=True), and the params, so the surface
renders a real, runnable proposal (never a fabricated command).
"""
import os
import shlex

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FLOW = {
    "id": "dragnet_extract",
    "label": "Dragnet extraction bake (propose-only)",
    "description": (
        "Proposes a dragnet extract-once bake over a chosen scope into a grain-asset "
        "(extractions-<asset>.jsonl), surfacing ONE 'dragnet_bake' inbox item for the operator. "
        "DOES NOT run the bake (proposes_only): the side-effecting ~4h bake is operator-only via the "
        "--confirm CLI door. The bake reads the file-discovered registry roles dragnet_coarse/_fine "
        "(+dragnet_design when design=True) behind the schema-freeze door, so grain/scope are "
        "configurable while the locked superset (D1) and neutral coarse pass (D3) stay frozen."
    ),
    "params": {
        "out_name": {"desc": "grain-asset basename → extractions-<out_name>.jsonl (full|theorem|visual-dna|…)",
                     "default": "full"},
        "projects": {"desc": "comma-sep rel_path leading-segment filter to INCLUDE (Tim's filter)", "default": ""},
        "since": {"desc": "conversation date >= YYYY-MM-DD (from anchor, not mtime)", "default": ""},
        "until": {"desc": "conversation date <= YYYY-MM-DD", "default": ""},
        "design": {"desc": "visual-dna ONLY: also run the DESIGN stage (resolves_into + resolution)",
                   "default": False},
    },
    "proposes_only": True,
}


def _proposed_command(out_name, projects, since, until, design) -> str:
    """The EXACT operator command this flow proposes (never fabricated — maps 1:1 to ops/dragnet_extract.py
    main() flags). The operator runs it through the --confirm door after the gated checklist."""
    parts = ["python3", "ops/dragnet_extract.py", "--all", "--confirm", "--write",
             "--out-name", out_name]
    if projects:
        parts += ["--projects", projects]
    if since:
        parts += ["--since", since]
    if until:
        parts += ["--until", until]
    if design:
        parts += ["--design"]
    return " ".join(shlex.quote(p) for p in parts)


def run(out_name="full", projects="", since="", until="", design=False) -> dict:
    """Surface a dragnet bake PROPOSAL into the governance inbox. Returns {status, surfaced_id, proposed}.
    Fail-closed default ('reject'): a non-response never fires a bake."""
    import sys
    sys.path.insert(0, ROOT)
    roles = ["dragnet_coarse", "dragnet_fine"] + (["dragnet_design"] if design else [])
    payload = {
        "kind": "dragnet_bake",
        "out_name": out_name,
        "asset": f"extractions-{out_name}.jsonl",
        "projects": projects,
        "since": since,
        "until": until,
        "design": bool(design),
        "roles": roles,
        "command": _proposed_command(out_name, projects, since, until, design),
        "note": ("Operator-only run (proposes_only floor). Run --sample N first to size max_tokens, "
                 "then the command above through the --confirm door. The bake reads the PROTECTED "
                 "registry roles; schema is frozen (D1) and the coarse pass is neutral (D3)."),
    }
    from store.fs_store import FsStore
    from fabric import config as fcfg
    from runtime.governance import Inbox
    store = FsStore(fcfg.STORE_DIR)
    surfaced_id = Inbox(store).surface("dragnet_bake", payload, default="reject")
    return {"status": "surfaced", "surfaced_id": surfaced_id, "proposed": payload}
