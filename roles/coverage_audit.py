"""roles/coverage_audit.py — authored cognition role (Concurrent Cognition C7.4/C7.5 · #58 direct-create).
Authored through the cognition surface — DIRECTLY via create_role (the agent authors live, #58)
OR via propose_role→operator-approve→apply_role (surfacing, kept available). Either way validated
by import-in-a-temp-dir (the correctness gate) before it reached the live roles/ tree. A declared
role: the output_schema is a real BaseModel subclass (fail-loud requirement); rules are declared ASTs."""
from pydantic import BaseModel, Field


class CoverageAuditOut(BaseModel):
    missing: list[str] = Field(default_factory=list, description="each missed definition as 'name | kind'; empty list if nothing is missing")
    notes: str = Field(default='', description="one short line; or 'complete'")


ROLE = {'id': 'coverage_audit',
 'prompt_template': 'You audit a code extractor for COMPLETENESS. Below is a FILE and the symbols '
                    '+ imports the extractor pulled from it. Report ONLY definitions genuinely '
                    'present IN the file but ABSENT from the extracted lists — functions, classes, '
                    'methods, AND module-level constant / dict / registry assignments (e.g. NAME = '
                    '{...}). Do not list anything already in the extracted lists.\n'
                    '\n'
                    '{utterance}\n'
                    '\n'
                    "If nothing is missing, return missing=[] and notes='complete'.",
    'output_schema': CoverageAuditOut,
}
