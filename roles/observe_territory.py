"""roles/observe_territory.py — authored cognition role (Concurrent Cognition C7.4/C7.5 · #58 direct-create).
Authored through the cognition surface — DIRECTLY via create_role (the agent authors live, #58)
OR via propose_role→operator-approve→apply_role (surfacing, kept available). Either way validated
by import-in-a-temp-dir (the correctness gate) before it reached the live roles/ tree. A declared
role: the output_schema is a real BaseModel subclass (fail-loud requirement); rules are declared ASTs."""
from typing import Literal
from pydantic import BaseModel, Field


class ObserveTerritoryOutSeen(BaseModel):
    what: str = Field(default='', description='short name of the thing')
    where: str = Field(default='', description='the path/address/row it lives at — verbatim from the material')
    state: Literal['living', 'dormant', 'half-built', 'unknown'] = Field(default='living', description='life-state judged only from evidence; unknown is honest')
    connects: list[str] = Field(default_factory=list, description='other things/addresses it references, verbatim')
    note: str = Field(default='', description='one line — the non-obvious bit')


class ObserveTerritoryOut(BaseModel):
    seen: list[ObserveTerritoryOutSeen] = Field(default_factory=list, description='one entry per distinct thing observed in the material')
    surprises: list[str] = Field(default_factory=list, description='things a maintainer would not expect (empty if none)')
    dormant_candidates: list[str] = Field(default_factory=list, description='built-but-unused or part-built-then-forgotten things, each with its where')
    next_territories: list[str] = Field(default_factory=list, description='territories this material points at that the swarm should observe next')


ROLE = {'id': 'observe_territory',
 'label': 'Observe territory (mesh open lens)',
 'description': 'One OPEN LENS of the mesh triangulation swarm (2026-07-07): reads a TERRITORY of '
                'the Company estate (a bundle of real material — file contents, registry rows, '
                'corpus records, service state — gathered deterministically by the driver) and '
                'reports WHAT IS ACTUALLY THERE: the things, their addresses, their life-state '
                '(living/dormant/half-built/unknown), their connections, the surprises. NOT a '
                'task-executor: it is not told what to find. The inverse of plan-and-dispatch — '
                'observations accumulate in the mesh space and the triangulator chooses the next '
                'territories from them. Cheap-model work (bulk looking); the judgment pass is '
                'triangulate_mesh.',
 'prompt_template': 'You are ONE OPEN LENS of a triangulating swarm mapping a system built '
                    'entirely by AI agents — the swarm is helping the system see itself for the '
                    'first time. You receive a TERRITORY: its name, why it was chosen, and a '
                    'bundle of REAL MATERIAL from it (file excerpts, registry rows, records, '
                    'listings).\n'
                    '\n'
                    'Report what is ACTUALLY THERE — you are not told what to find, and you must '
                    'not invent. Ground every observation in the material (name the '
                    'path/address/row you saw it in). The gold is: things that exist but look '
                    'DORMANT or HALF-BUILT (built once, never wired, never used), connections '
                    'between things, and SURPRISES — what a maintainer would not expect.\n'
                    '\n'
                    'Your input unit carries:\n'
                    "  - territory: the territory's name\n"
                    '  - why: why the triangulator chose it\n'
                    '  - material: the gathered real material (excerpts — may be truncated; '
                    'observe what IS there, never extrapolate past it)\n'
                    '\n'
                    'Fields:\n'
                    '  - seen: a LIST — one entry per distinct thing observed. Each: {what (short '
                    'name), where (the path/address/row it lives at, verbatim from the material), '
                    'state (living | dormant | half-built | unknown — judge ONLY from evidence in '
                    'the material; unknown is honest), connects (list of other things/addresses it '
                    'references, verbatim), note (one line — the non-obvious bit)}.\n'
                    '  - surprises: a LIST of strings — things a maintainer would not expect '
                    '(empty if none; never padded).\n'
                    '  - dormant_candidates: a LIST of strings — the things that look '
                    'built-but-unused or part-built-then-forgotten, each with its where (empty if '
                    'none).\n'
                    '  - next_territories: a LIST of strings — territories THIS material points at '
                    'that the swarm should look at next (names/paths/addresses seen here but not '
                    'included in the material).',
 'input_addresses': ['utterance'],
 'mode_scope': ['mesh'],
 'trigger': 'fanned over N territory-units by run_items from the mesh triangulation driver '
            '(build-prep/mesh/) — each unit {territory, why, material}; captures land in '
            "space='mesh' keyed mesh://territory/<slug>; the triangulate_mesh reduce reads ALL "
            "observations + the prior synthesis and chooses the next round's territories "
            '(triangulation-not-planning).',
 'render_hint': {'shape': 'observation', 'lane': 'observe_territory'},
 'default_model': 'kimi-k2.6:cloud',
 'default_base_url': 'http://localhost:11434/v1',
    'output_schema': ObserveTerritoryOut,
}
