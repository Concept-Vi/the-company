"""roles/authtest_role.py — operator-authored cognition role (Concurrent Cognition C7.4/C7.5).
Authored through the surface (propose_role → operator approve → apply_role); validated by
import-in-a-temp-dir before it ever reached the live roles/ tree. A declared role: the
output_schema is a real BaseModel subclass (fail-loud requirement), rules are declared ASTs."""
from pydantic import BaseModel, Field


class AuthtestRoleOut(BaseModel):
    intent: str = ''


ROLE = {
    "id": "authtest_role",
    "label": "AuthTest",
    "prompt_template": "Echo the utterance intent.",
    "mode_scope": [
        "listening"
    ],
    "model_binding": {
        "requires": [
            "chat",
            "json"
        ]
    },
    "output_schema": AuthtestRoleOut,
}
