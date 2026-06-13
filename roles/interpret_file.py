"""roles/interpret_file.py — authored cognition role (Concurrent Cognition C7.4/C7.5 · #58 direct-create).
Authored through the cognition surface — DIRECTLY via create_role (the agent authors live, #58)
OR via propose_role→operator-approve→apply_role (surfacing, kept available). Either way validated
by import-in-a-temp-dir (the correctness gate) before it reached the live roles/ tree. A declared
role: the output_schema is a real BaseModel subclass (fail-loud requirement); rules are declared ASTs."""
from pydantic import BaseModel, Field


class InterpretFileOut(BaseModel):
    notable: list[str] = Field(default_factory=list, description='Observations requiring judgment that the structural data alone does not state. Empty list if genuinely nothing notable. NEVER restate raw structural facts.')
    uncertainties: list[str] = Field(default_factory=list, description='Explicit unknowns, ambiguities or concerns about this file. Empty list if none.')
    architectural_role: str = Field(default='', description="The file's role in the broader system in a few words (e.g. 'bridge server', 'deployment gate', 'test suite for annotations'). Empty string if undeterminable from the evidence.")


ROLE = {'id': 'interpret_file',
 'label': 'Discovery: interpret file',
 'description': "Discovery-system interpret phase: receives a file's programmatically-extracted "
                'structural observations and produces the interpretive observations only AI can '
                'make (notable, uncertainties, architectural_role). Authored from the '
                'type-observation contract in '
                'vi-visual-bridge/.discovery/taxonomies/type-observation-contract.json.',
 'prompt_template': 'You are the interpret phase of a repository discovery system. You receive '
                    'STRUCTURAL OBSERVATIONS for one file, extracted programmatically (they are '
                    'facts — do not re-extract or dispute them). Your task is JUDGMENT only: what '
                    'do these facts mean?\n'
                    '\n'
                    'Rules:\n'
                    '- notable: observations requiring judgment, NOT restatements of the '
                    "structural data. 'Has 167 functions' is a restatement; 'single file carries "
                    "an entire embedded web UI across 4 languages' is notable. Empty list if "
                    'nothing genuinely notable.\n'
                    '- uncertainties: explicit unknowns or ambiguities. If the file_type is '
                    "'unknown', explain what evidence is missing. Empty list if none.\n"
                    "- architectural_role: the file's role in the system, a few words. Empty "
                    'string if the evidence is insufficient — never guess.\n'
                    '- Base everything ONLY on the supplied evidence. Never invent file contents.\n'
                    '\n'
                    'STRUCTURAL OBSERVATIONS:\n'
                    '{utterance}',
    'output_schema': InterpretFileOut,
}
