"""roles/repo_digest.py — operator-authored cognition role (Concurrent Cognition C7.4/C7.5).
Authored through the surface (propose_role → operator approve → apply_role); validated by
import-in-a-temp-dir before it ever reached the live roles/ tree. A declared role: the
output_schema is a real BaseModel subclass (fail-loud requirement), rules are declared ASTs."""
from pydantic import BaseModel, Field


class RepoDigestOut(BaseModel):
    digest: str = Field(default='', description='the 1-sentence digest')
    kind: str = Field(default='', description='the kind of file')


ROLE = {'id': 'repo_digest',
 'label': 'Repo digest',
 'description': 'One-sentence digest of a supplied file: what it is + its role in the system.',
 'prompt_template': 'Read the supplied file content and produce a 1-sentence digest of what it is '
                    '+ its role in the system.',
 'op': 'generate',
 'input_addresses': ['utterance'],
 'mode_scope': [],
    'output_schema': RepoDigestOut,
}
