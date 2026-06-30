"""roles/extraction_audit.py — authored cognition role (Concurrent Cognition C7.4/C7.5 · #58 direct-create).
Authored through the cognition surface — DIRECTLY via create_role (the agent authors live, #58)
OR via propose_role→operator-approve→apply_role (surfacing, kept available). Either way validated
by import-in-a-temp-dir (the correctness gate) before it reached the live roles/ tree. A declared
role: the output_schema is a real BaseModel subclass (fail-loud requirement); rules are declared ASTs."""
from typing import Literal
from pydantic import BaseModel, Field


class ExtractionAuditOutFindings(BaseModel):
    discrepancy_type: Literal['in_contract_not_extracted', 'in_file_not_in_contract', 'wrong_in_extraction', 'other'] = Field(default='in_contract_not_extracted', description='which kind of discrepancy this is')
    name: str = Field(default='', description='the symbol / anchor name')
    symbol_kind: str = Field(default='', description='function, class, component, hook, constant, registry-dict, import, export, or another kind you identify')
    location: str = Field(default='', description='line number or where in the file')
    detail: str = Field(default='', description='what is missing, extra, or wrong')


class ExtractionAuditOut(BaseModel):
    findings: list[ExtractionAuditOutFindings] = Field(default_factory=list, description='every discrepancy between the file, the contract, and the extraction; empty when the extraction is complete and correct')
    complete: bool = Field(default=False, description="true = PASS: the extraction fully and correctly captures the file's symbols")
    kind_seen: str = Field(default='', description="the model's own read of the file kind, as a sanity check against the declared kind")


ROLE = {'id': 'extraction_audit',
 'thinking': False,   # extraction-audit is a CLEAR MEASUREMENT, not reasoning — run no-think so the BATCH
                      # path (run_items, which has no `think` arg) inherits it (cognition.py eff_think reads
                      # role.thinking when the call passes none). Thinking-on times out the batch.
 'prompt_template': 'You verify a code extractor against the ACTUAL file. Its INTENT is to capture '
                    'every SYMBOL — every named, identifiable definition the rest of the system '
                    'could reference, link to, or navigate to (its anchors). Below you are given: '
                    'the CONTRACT (what the extractor was supposed to capture for this file kind), '
                    'the EXTRACTION (what it actually persisted, including its own element '
                    'COUNTS), and the FILE itself. Report every discrepancy, each classified by '
                    'discrepancy_type: a symbol in the contract AND the file but NOT extracted '
                    '(extraction failed its contract); a symbol in the file of a kind the contract '
                    'does NOT cover (the contract itself is too narrow — a blind spot); a symbol '
                    'extracted but misrepresented; or any other mismatch. Be literal — only report '
                    'what is genuinely in the file.\n'
                    '\n'
                    '{utterance}\n'
                    '\n'
                    "If the extraction fully and correctly captures the file's symbols, return "
                    'findings=[] and complete=true.',
    'output_schema': ExtractionAuditOut,
    # ROOT-CAUSE FIX (Tim 2026-06-30, fully traced): greedy (temp 0) + schema-CONSTRAINED (guided JSON)
    # decoding makes the 4-bit AWQ fall into a REPETITION LOOP on files with enumerable/repetitive
    # structure (many similar functions, acceptance-test cases) — it re-emits the same findings until
    # max_tokens (finish_reason=length) → invalid → retries → recorded "unresolved". NOT thinking, NOT
    # context, NOT concurrency (all ruled out by isolation tests). A light repetition_penalty breaks the
    # loop: VERIFIED on types-adapter.js — runaway 117s → 5s, finish=stop, 11 DISTINCT findings. 1.1 is the
    # sweet spot (1.3 over-suppressed to 3 findings; temperature alone did not break the loop). The 1276
    # files that passed simply lacked loop-triggering structure.
    # SAMPLING — this role OVERRIDES the system-wide guard. The greedy+guided-JSON loop is broken system-wide
    # in run_role (schema fire → presence_penalty at temp 0, deterministic — ensures NO structured role loops
    # into unusable output). But presence_penalty penalises REPEATED phrasing, and an extraction audit's
    # findings legitimately share phrasing ("function X not captured") → it over-suppresses real findings
    # (verified: the bare guard gave 2 findings where this gives ~10). So for COMPLETENESS this role uses a
    # small temperature instead (escapes the loop via sampling diversity, not penalty) + a gentle pp.
    # VERIFIED: temp 0.3 + min_p 0.2 + presence 1.5 → finish=stop, distinct + thorough findings.
    'knobs': {'temperature': 0.3, 'min_p': 0.2, 'presence_penalty': 1.5, 'repetition_penalty': 1.0},
}
