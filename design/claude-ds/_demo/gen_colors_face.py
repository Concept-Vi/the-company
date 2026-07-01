# Author the FACE OF the real Colors canvas FROM its real token data (model-authored, adds guidance,
# not a hardcoded mirror, not a foreign guide). Grounded in the actual colors_and_type.css :root block.
import sys, os, re
sys.path.insert(0, "/home/tim/company"); os.chdir("/home/tim/company")
from runtime.suite import Suite
from runtime.registry import NodeRegistry
from store.fs_store import FsStore
from runtime import page_face as pf, page_render as pr
from fabric import client, transport

# --- the REAL token source (read from the canonical CSS, not hand-typed) ---
css = open("design/claude-ds/colors_and_type.css").read()
root = css.split(":root {",1)[1].split("/* ============",1)[0]  # the first :root token block
# keep only color-token lines (a --x: #hex; with their trailing role comment)
tok_lines = [ln.strip() for ln in root.splitlines()
             if re.search(r"--[\w-]+:\s*#", ln) or ("--accent" in ln) or ("/* " in ln and "color" in ln.lower())]
tokens_text = "\n".join(tok_lines)[:3500]

s = Suite(FsStore(".data/store"), NodeRegistry().discover(["nodes"]), nodes_dir="nodes")
r = s.resolve_role("guide_author"); cfg = s.rhm_config()
sys_p = ("You are writing the reference page for the ConceptV color system, for a designer/agent USING it. "
         "Ground ONLY in the real tokens given — every hex/role you mention must be present below. Do not just "
         "list them; explain what each VOICE is FOR and how to use it well (when to reach for gold vs bronze vs "
         "sage; the paper ground; the gold->bronze ramp; the near-white zoning idea). Add genuine using-guidance, "
         "not a restatement. Sections (## headings): The voices · The ground & ink · The ramp · Using it well. "
         "Markdown only, no preamble.")
usr = "REAL TOKENS (from colors_and_type.css):\n" + tokens_text
print(">>> authoring the Colors face on the live model...", flush=True)
md = client.complete(transport.openai_transport(base_url=r["base_url"], timeout=cfg.get("timeout",120)),
                     [{"role":"system","content":sys_p},{"role":"user","content":usr}],
                     model=r["model"], max_tokens=1400, temperature=0.3)
md = md.strip()
html = pr.render_address_page(title="The ConceptV color system", target="ui://canvas/colors",
                              kind_noun="canvas", body_md=md,
                              face_of="the how-to for the <b>Colors</b> canvas — authored from its real tokens")
pf.attach_page(s, "ui://canvas/colors", html, title="The ConceptV color system")
print("attached ui://canvas/colors | md chars:", len(md), "| html:", len(html))
print("--- first 600 chars of the model's real, token-grounded content ---")
print(md[:600])
