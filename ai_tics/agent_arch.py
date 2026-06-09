"""ai_tics/agent_arch.py — SEED AI-tic: agent-arch.

The generic-AI tell of defaulting to agent-architecture (tools+autonomy+loop, an agent DECIDING to act)
when the work is content/dataflow (resolve→work→persist→trigger; models = slot-values). A named Tim
distinction — agentic is supported but NEVER the default/assumption. See runtime/ai_tics.py +
ai_tics/AGENTS.md.
"""

AI_TIC = {
    "id": "agent_arch",
    "label": "agent-arch",
    "markers": ["the agent decides", "autonomous agent", "agent loop", "tool-calling agent", "the agent will then", "agentic workflow"],
    "desc": "defaulting to agent-architecture where the work is content/dataflow (a named Tim distinction)",
}
