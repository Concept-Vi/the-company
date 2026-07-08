"""roles/mine_design_intent.py — authored cognition role (Concurrent Cognition C7.4/C7.5 · #58 direct-create).
Authored through the cognition surface — DIRECTLY via create_role (the agent authors live, #58)
OR via propose_role→operator-approve→apply_role (surfacing, kept available). Either way validated
by import-in-a-temp-dir (the correctness gate) before it reached the live roles/ tree. A declared
role: the output_schema is a real BaseModel subclass (fail-loud requirement); rules are declared ASTs."""
from typing import Literal
from pydantic import BaseModel, Field

# OPEN VOCABULARY (Tim 2026-07-08 — the nucleation law, correcting my own enum+coercion): `kind` was a
# closed Literal, then a coercion map onto MY seven words — predetermination twice over, and with
# schema-constrained decoding it CENSORED the decoder (the model could not say what it saw; the whole
# retry-burn class was the enum failing, not the model). The design we built: schema constrains SHAPE,
# never MEANING. Novel kind-words are the NUCLEATION SIGNAL — they pile up, the cluster layer
# (pattern_cluster / run_reduce(mode='cluster')) groups them, a kimi seat names/canonicalizes, outliers
# escalate (proposed→clustered→canonical|escalated). Canonical kinds live as counts at the CANONICAL
# layer (G16), never as a decode constraint. A closed set stays legitimate ONLY where CODE branches
# deterministically on the value (design_weight below — an ordinal routing dial, kept + noted).


class MineDesignIntentOutIntents(BaseModel):
    subject: str = Field(default='', description='the thing being designed/decided/named — short name')
    kind: str = Field(default='', description="what sort of intent this is — ONE lowercase word/phrase, the model's own; common so far: decision · aspiration · principle · mechanism · correction · naming · constraint — use one where it truly fits, COIN a new one where it doesn't (novel kinds are wanted signal, they nucleate the taxonomy)")
    statement: str = Field(default='', description='what was decided/asserted/designed — concrete and specific')
    reaching_for: str = Field(default='', description='the why behind it — the problem it solves, the future it assumes')
    special: str = Field(default='', description='a non-obvious property, gotcha, or deliberate choice a future agent would not guess (empty string if none stated)')


class MineDesignIntentOut(BaseModel):
    gist: str = Field(default='', description='one plain sentence — what this exchange was actually about')
    intents: list[MineDesignIntentOutIntents] = Field(default_factory=list, description='one entry per distinct design intent found in the exchange (empty list when there is none — never padded)')
    connects_to: list[str] = Field(default_factory=list, description='file paths / addresses / ports / service names explicitly mentioned (verbatim; empty list if none)')
    design_weight: Literal['none', 'light', 'substantial'] = Field(default='none', description='how much genuine design content this exchange carries')


ROLE = {'id': 'mine_design_intent',
 'label': 'Mine design intent (memory archaeology extract)',
 'description': 'The MEMORY-ARCHAEOLOGY miner — the deep-understanding sibling of mine_exchange '
                '(which mines the SELF-IMPROVEMENT facet). Reads ONE conversation exchange (a '
                'Tim-message + assistant-response pair riding in the unit) and extracts the '
                'DESIGN-INTENT signal: what things ARE, what they were REACHING FOR (the '
                'aspiration/problem behind them), their ROLE in the larger system, their SPECIAL '
                'non-obvious properties, and the concrete files/addresses/systems the exchange '
                'touches. LIST-VALUED on purpose: a rich exchange carries several intents (the '
                'one-decision-per-exchange loss in mine_exchange was measured, 2026-07-07 A/B); a '
                'mundane exchange yields an empty list — never a padded one. Fanned over exchanges '
                'via run_items; records land in the history space addressed exchange://<sid>/<i>, '
                'connects_to carries the code://-linkable paths (the transcript-address ↔ '
                'directory-address bridge Tim named).',
 'prompt_template': 'You are the MEMORY ARCHAEOLOGIST. Everything in this company was built by AI '
                    'agents in conversation with Tim (the founder) — the transcripts are the ONLY '
                    "record of why anything exists. You read ONE exchange (Tim's message + the "
                    "assistant's reply) and extract the DESIGN-INTENT signal: the understanding a "
                    'future agent needs that the code alone cannot give.\n'
                    '\n'
                    'Your input is a unit containing the exchange:\n'
                    '  - `tim_message` — what Tim said/typed;\n'
                    '  - `my_response` — what the assistant replied;\n'
                    '  - `session_id`/`ts` — orientation only.\n'
                    '\n'
                    'Extract ONLY what is ACTUALLY IN the exchange — quote or closely paraphrase; '
                    'never invent. Many exchanges are operational noise with NO design content: '
                    'then `intents` is the EMPTY LIST and design_weight is "none". A fabricated '
                    'intent poisons the memory; an empty extract is honest.\n'
                    '\n'
                    'Read the WHOLE exchange before extracting — the substance is often mid-reply, '
                    'not in the opening lines. Do not anchor on the first salient sentence.\n'
                    '\n'
                    'Fields:\n'
                    '  - gist: one plain sentence — what this exchange was actually about.\n'
                    '  - intents: a LIST — one entry PER distinct design intent in the exchange (a '
                    'rich exchange has several; extract them ALL, not just the first). Each '
                    'entry:\n'
                    '      - subject: the thing being designed/decided/named (a system, mechanism, '
                    'principle, or component — short name).\n'
                    '      - kind: ONE lowercase word/phrase naming the sort of intent — common so '
                    'far: decision, aspiration, principle, mechanism, correction, naming, '
                    'constraint. Use one where it truly fits; COIN a new word where it does not '
                    '(a novel kind is wanted signal — the taxonomy grows from what you coin).\n'
                    '      - statement: WHAT was decided/asserted/designed about the subject — '
                    'concrete, specific.\n'
                    '      - reaching_for: the WHY BEHIND it — the problem it solves, the future '
                    'it assumes, what it was aspiring toward. This is the field the code cannot '
                    'carry; work hardest here.\n'
                    '      - special: a non-obvious property, gotcha, or deliberate choice a '
                    'future agent would not guess (or "" if none stated).\n'
                    '  - connects_to: file paths, ui://|code://|exchange:// addresses, port '
                    'numbers, service or system names EXPLICITLY mentioned in the exchange '
                    '(verbatim; empty list if none).\n'
                    '  - design_weight: none | light | substantial — how much genuine design '
                    'content this exchange carries (substantial = intents worth re-reading later; '
                    'none = pure ops/ack noise).',
 'input_addresses': ['utterance'],
 'mode_scope': ['mining'],
 'trigger': 'fired over N exchange-units by run_items (the archaeology MAP, sibling of '
            "mine_exchange's self-improvement MAP) — one unit per exchange {tim_message, "
            "my_response, session_id?, ts?}; captures land in space='history' addressed "
            'exchange://<sid>/<i>; connects_to feeds the exchange://↔code:// cross-link (the '
            'transcript-address ↔ directory-address bridge).',
 'render_hint': {'shape': 'extract', 'lane': 'mine_design_intent'},
 # KIMI-BOUND (2026-07-07, the archaeology decision): extraction of design-INTENT is judgment work —
 # the measured A/B (build-prep/memory-archaeology/KIMI-VS-4B-MINE-SAMPLE.md) showed the strong model's
 # repeatable edge is exactly the correction/intent-catching this role exists for. TOP-LEVEL binding
 # (roles/AGENTS.md binding-trap law: a default_model nested in model_binding is silently unread) —
 # explain_role.py is the canonical pattern; base_url = the ollama host where the cloud kimi runs
 # (model+endpoint must match). create(kind='role')'s model= param was silently dropped at authoring
 # time (fixed in Suite.create_role the same day); this explicit binding is the repair.
 'default_model': 'kimi-k2.7-code:cloud',
 'default_base_url': 'http://localhost:11434/v1',
 'model_binding': {'requires': ['chat', 'json'], 'default_model': 'kimi-k2.7-code:cloud',
                   'default_base_url': 'http://localhost:11434/v1'},
    'output_schema': MineDesignIntentOut,
}
