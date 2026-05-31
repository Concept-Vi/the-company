"""ACTUAL USE of the MCP agent face — a real MCP client connects to the running server and
COMPOSES + RUNS a graph that uses the self-grown 'wordcount' node. Proves the agent face is
operable in use (not just that tools are registered), end to end, over the shared substrate.
Run: .venv/bin/python tests/mcp_use.py
"""
import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from fabric import config as fcfg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GID = "mcp-use-demo"


def _text(res):
    t = res.content[0].text
    try:
        return json.loads(t)
    except Exception:
        return t


async def main():
    gp = os.path.join(fcfg.STORE_DIR, "graphs", GID + ".json")
    if os.path.exists(gp):
        os.remove(gp)
    params = StdioServerParameters(command=os.path.join(ROOT, ".venv/bin/python"),
                                   args=[os.path.join(ROOT, "mcp_face/server.py")])
    ok = True
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            types = [c.text for c in (await s.call_tool("list_types", {})).content]  # list -> multi-block
            print("  agent sees node-types:", types)
            ok &= "wordcount" in types          # the self-grown node is visible to the agent

            c = _text(await s.call_tool("create_node",
                      {"graph": GID, "type": "constant", "config": {"value": "the quick brown fox jumps"}}))
            wc = _text(await s.call_tool("create_node", {"graph": GID, "type": "wordcount"}))
            await s.call_tool("connect",
                              {"graph": GID, "from_node": c, "from_port": "value",
                               "to_node": wc, "to_port": "text"})
            ran = _text(await s.call_tool("run_graph", {"graph": GID}))
            res = _text(await s.call_tool("get_results", {"graph": GID}))
            print(f"  agent composed: {c} -> {wc}; ran: {ran}")
            print(f"  results: {res}")
            ok &= (res.get(wc) == "5")          # 'the quick brown fox jumps' = 5 words

    print("\n" + ("✅ MCP FACE PROVEN IN USE — agent composed + ran a graph using the SELF-GROWN node (5 words)"
                  if ok else "❌ MCP-use FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
