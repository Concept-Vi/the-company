"""roles/atlas_linker.py — authored cognition role (Concurrent Cognition C7.4/C7.5 · #58 direct-create).
Authored through the cognition surface — DIRECTLY via create_role (the agent authors live, #58)
OR via propose_role→operator-approve→apply_role (surfacing, kept available). Either way validated
by import-in-a-temp-dir (the correctness gate) before it reached the live roles/ tree. A declared
role: the output_schema is a real BaseModel subclass (fail-loud requirement); rules are declared ASTs."""
from pydantic import BaseModel, Field


class AtlasLinkerOut(BaseModel):
    tags: list[str] = Field(default_factory=list, description='3-7 kebab-case topic tags for the page')
    atlas_notes: list[str] = Field(default_factory=list, description='0-3 Atlas domain notes this page belongs to, chosen ONLY from: Channels, Custom Apps Integration, Routines, Hooks & Extension Fabric, Feature Atlas, Memory Systems, Config & UI Data Model, Docs Inventory')
    summary: str = Field(default='', description='one sentence, max 25 words, saying what the page covers')


ROLE = {'id': 'atlas_linker',
 'label': 'Atlas: doc tagger + linker',
 'description': 'Tags a Claude Code documentation page and connects it to the Atlas domain notes. '
                'Built for the Claude Code Atlas corpus enrichment fan (run_items over doc pages).',
 'prompt_template': 'You are organizing the Claude Code Atlas, a documentation corpus about Claude '
                    "Code (Anthropic's agentic coding tool), MCP, and the Claude platform.\n"
                    '\n'
                    'Given one documentation page below (path, title, headings, excerpt), '
                    'produce:\n'
                    '- tags: 3-7 kebab-case topic tags (specific, retrieval-useful; e.g. hooks, '
                    'mcp-servers, session-resume, permission-rules)\n'
                    '- atlas_notes: which Atlas domain notes this page belongs to (0-3), chosen '
                    'ONLY from this exact list: Channels | Custom Apps Integration | Routines | '
                    'Hooks & Extension Fabric | Feature Atlas | Memory Systems | Config & UI Data '
                    'Model | Docs Inventory\n'
                    '- summary: one sentence (max 25 words) stating what the page covers.\n'
                    '\n'
                    'PAGE:\n'
                    '{utterance}',
    'output_schema': AtlasLinkerOut,
}
