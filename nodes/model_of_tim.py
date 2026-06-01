"""model_of_tim — the EXPLICIT model of Tim (the twin's grounding, context-05 escalation rung 2).

The synthesised principles/laws (foundation/system/principles.md) — Tim's own statements of how
the Company holds itself. The twin reasons from THIS (explicit) plus, later, the corpus-trained
implicit model. A content source, drillable like `codebase`. Path is configurable (env override).
"""
import os

VERSION = "1"
KIND = "content"
PORTS_IN: dict = {}
PORTS_OUT = {"principles": "Text"}

DEFAULT_PATH = os.environ.get("COMPANY_MODEL_OF_TIM",
                              os.path.expanduser("~/foundation/system/principles.md"))


def run(inputs: dict, config: dict):
    path = config.get("path") or DEFAULT_PATH
    try:
        return open(path, encoding="utf-8").read()
    except Exception as e:                              # fail loud — no fabricated model of Tim
        raise ValueError(f"model_of_tim: cannot read the explicit model at {path!r}: {e}")
