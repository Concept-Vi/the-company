"""roles/repo_digest.py — agent-authored cognition role (Concurrent Cognition C7.4/C7.5 · #58 direct-create).
Authored DIRECTLY via create_role (the agent authors live, NO operator approval — the #58 reframe);
validated by import-in-a-temp-dir (the correctness gate) before it reached the live roles/ tree. A declared
role: the output_schema is a real BaseModel subclass (fail-loud requirement), rules are declared ASTs."""
from pydantic import BaseModel, Field


class RepoDigestOut(BaseModel):
    digest: str = Field(default='', description='the 1-sentence digest')
    kind: str = Field(default='', description='the kind of file')


ROLE = {'id': 'repo_digest',
 'label': 'Repo digest',
 'description': 'One-sentence digest of a supplied file: what it is + its role in the system.',
 'prompt_template': 'Read the supplied file content and return JSON with EXACTLY these fields:\n'
                    '  "digest" — a 1-2 sentence summary of what this file IS and its role in the system '
                    '(the prose goes HERE, never in kind);\n'
                    '  "kind" — ONE WORD ONLY: code | doc | config | test | data.\n'
                    'File content:\n{utterance}',
 'op': 'generate',
 'input_addresses': ['utterance'],
 'mode_scope': [],
    'output_schema': RepoDigestOut,
}
