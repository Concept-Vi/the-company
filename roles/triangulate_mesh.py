"""roles/triangulate_mesh.py — authored cognition role (Concurrent Cognition C7.4/C7.5 · #58 direct-create).
Authored through the cognition surface — DIRECTLY via create_role (the agent authors live, #58)
OR via propose_role→operator-approve→apply_role (surfacing, kept available). Either way validated
by import-in-a-temp-dir (the correctness gate) before it reached the live roles/ tree. A declared
role: the output_schema is a real BaseModel subclass (fail-loud requirement); rules are declared ASTs."""
from typing import Literal
from pydantic import BaseModel, Field


class TriangulateMeshOutConvergences(BaseModel):
    thing: str = Field(default='', description='the load-bearing fact/thing')
    addresses: list[str] = Field(default_factory=list, description='where it lives')
    seen_from: list[str] = Field(default_factory=list, description='the territories that saw it')


class TriangulateMeshOutContradictions(BaseModel):
    about: str = Field(default='', description='what the disagreement is about')
    faces: list[str] = Field(default_factory=list, description='the conflicting readings (may be legitimate multiple jobs)')


class TriangulateMeshOutDormant(BaseModel):
    what: str = Field(default='', description='the dormant thing')
    where: str = Field(default='', description='its address/path')
    verdict: Literal['forgotten', 'parked', 'unclear'] = Field(default='forgotten', description='genuinely forgotten vs deliberately condition-parked')


class TriangulateMeshOutNextTerritories(BaseModel):
    territory: str = Field(default='', description='a concrete path/address/registry the driver can gather from')
    why: str = Field(default='', description="one line, grounded in this round's evidence")


class TriangulateMeshOut(BaseModel):
    convergences: list[TriangulateMeshOutConvergences] = Field(default_factory=list, description='the same thing seen independently from different territories')
    contradictions: list[TriangulateMeshOutContradictions] = Field(default_factory=list, description='observations that disagree — each usually the next place to look')
    dormant: list[TriangulateMeshOutDormant] = Field(default_factory=list, description='the real part-built/forgotten finds')
    next_territories: list[TriangulateMeshOutNextTerritories] = Field(default_factory=list, description="the next round's territories, chosen from evidence — never invented")
    mesh_note: str = Field(default='', description='3-6 sentences — what the mesh now understands about itself that it did not before')


ROLE = {'id': 'triangulate_mesh',
 'label': 'Triangulate mesh (cross-observation synthesis)',
 'description': "The TRIANGULATION seat of the mesh swarm (2026-07-07): reads the round's N "
                "territory-observations (from observe_territory lenses) PLUS the prior round's "
                'synthesis, and triangulates — where do independent observations CONVERGE (the '
                'same thing seen from different territories), where do they CONTRADICT (the next '
                'places to look), which dormant finds matter, and which TERRITORIES the next round '
                'should observe. This role is HOW the swarm steers itself: territories are chosen '
                'here, from evidence, never pre-planned (the inversion — '
                'triangulation-not-planning, Tim 2026-07-07). Frontier-model work (judgment); the '
                'bulk looking is observe_territory.',
 'prompt_template': 'You are the TRIANGULATION seat of a swarm mapping a system built entirely by '
                    'AI agents. This round, N open lenses each observed one TERRITORY of the '
                    'estate and reported what is actually there. You receive ALL their '
                    'observations, plus the synthesis from the PREVIOUS round (empty on round 1, '
                    'beyond the anchor).\n'
                    '\n'
                    'Triangulate — reason ACROSS the observations, never within one:\n'
                    '  - CONVERGENCES: the same thing/pattern seen independently from different '
                    'territories — these are load-bearing facts of the estate. Name the thing, its '
                    'address(es), and which territories saw it.\n'
                    '  - CONTRADICTIONS: places where observations disagree with each other, with '
                    'the prior synthesis, or with the anchor — each contradiction is a signal, and '
                    'usually the next place to look. (Remember the standing law: a thing sources '
                    'disagree about may legitimately do MULTIPLE jobs — record the faces, do not '
                    'force one winner.)\n'
                    "  - DORMANT: from the lenses' dormant_candidates, the ones that look REAL "
                    '(evidence from more than one angle, or strong single evidence) — the '
                    'part-built forgotten things the mesh exists to resurface. Distinguish '
                    'deliberately-parked (condition-addressed deferral) from genuinely forgotten '
                    'where the evidence allows.\n'
                    "  - NEXT_TERRITORIES: choose the next round's territories FROM the evidence — "
                    "the lenses' next_territories suggestions, the contradictions, the thin spots. "
                    '4-8 of them, each {territory (a concrete path/address/registry the driver can '
                    "gather material from), why (one line, grounded in this round's evidence)}. "
                    'NEVER invent a territory no observation pointed at.\n'
                    '  - MESH_NOTE: 3-6 sentences — what the mesh now understands about itself '
                    "that it did not before this round. Written for the NEXT round's triangulator "
                    "and for any agent reading the mesh's self-model.\n"
                    '\n'
                    'Ground everything in the observations (cite territory names/addresses). '
                    'Honest empties beat padding.\n'
                    '\n'
                    'Your input carries:\n'
                    "  - notes: the round's N observations (JSON), each tagged with its territory\n"
                    "  - prior: the previous round's synthesis (may be empty)\n"
                    "  - anchor: the mesh anchor's core (the shared partial picture — stress-test "
                    "it, don't confirm it)",
 'input_addresses': ['notes', 'prior', 'anchor'],
 'mode_scope': ['mesh'],
 'trigger': 'fired once per round by the mesh triangulation driver (build-prep/mesh/) after the '
            "observe_territory fan — notes = the round's observations, prior = the previous "
            "synthesis, anchor = the ANCHOR core; its next_territories BECOME the next round's fan "
            "(the self-steering loop); captured to space='mesh' keyed mesh://round/<n>.",
 'render_hint': {'shape': 'synthesis', 'lane': 'triangulate_mesh'},
 'default_model': 'kimi-k2.7-code:cloud',
 'default_base_url': 'http://localhost:11434/v1',
    'output_schema': TriangulateMeshOut,
}
