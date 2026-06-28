"""runtime/page_render.py — render an addressed thing into a REAL designed DNA page (not flat text).

A page-face is only as real as what it serves. Dumping a guide's markdown with <br> tags is flat text,
not a page. This renderer turns an addressed thing's content into an actual designed HTML page using the
ConceptV DNA tokens (inlined so the page is self-contained under the no-script CSP) — with:
  - a HEADER BAND (the page indicator): what this page is the face OF, in human terms, + a face mark.
  - the content rendered as REAL structure: headings, paragraphs, lists, code — never <br> soup.
  - DNA typography + paper ground + bronze headings + gold accents + a readable measure.

`page = f(content, surface)` done properly: the same content recomputes into a designed page.

NOTE on fonts: the served page runs under the page-face no-script CSP (`font-src data:`), so the real
webfonts (Sora / DM Sans) can't load over the network — the stack falls back to a tuned system serif/
sans. Everything else (scale, weight, spacing, colour, layout) is the real DNA. Allowing the font CDN is
a one-line CSP relax if the exact faces are wanted (it does not weaken the no-script protection).
"""
from __future__ import annotations

import html as _html
import re

# ---- DNA tokens (the real values from colors_and_type.css), inlined so the page is self-contained ----
_DNA_CSS = """
:root{
  --paper:#FCFAF2; --paper-2:#F8F3E1; --paper-3:#F2EAD0; --white:#FFFFFF;
  --ink:#1F1A12; --ink-2:#3A3026; --ink-3:#6B5F47; --ink-4:#9C8C6E;
  --gold:#E0C010; --gold-deep:#9F772C; --gold-soft:#F4E89A; --gold-50:#FBF4C8; --gold-dashed:#D8C040;
  --bronze:#988058; --bronze-deep:#7B7055; --bronze-warm:#C09D5D;
  --border:#E8DFC5; --border-faint:#F0E9D2;
  --r-md:8px; --r-lg:12px;
  --font-display:"Sora",ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;
  --font-body:"DM Sans",ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;
  --font-mono:"JetBrains Mono",ui-monospace,"SFMono-Regular",monospace;
}
*{box-sizing:border-box;}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--font-body);
     font-size:17px;line-height:1.62;-webkit-font-smoothing:antialiased;}

/* the page indicator — a header band stating what this page is the FACE OF */
.pf-head{background:var(--white);border-bottom:1px solid var(--border);
         padding:18px clamp(20px,5vw,40px);position:sticky;top:0;z-index:2;
         box-shadow:0 1px 2px rgba(31,26,18,.03);}
.pf-head .inner{max-width:64ch;margin:0 auto;display:flex;align-items:center;gap:12px;}
.pf-mark{flex:none;width:30px;height:30px;border-radius:7px;background:var(--gold-50);
         border:1px solid var(--gold-dashed);display:grid;place-items:center;color:var(--gold-deep);font-size:14px;}
.pf-head .meta{min-width:0;}
.pf-eyebrow{font-family:var(--font-body);font-weight:600;font-size:11px;letter-spacing:.09em;
            text-transform:uppercase;color:var(--bronze);margin:0 0 1px;}
.pf-faceof{font-family:var(--font-body);font-weight:500;font-size:13px;color:var(--ink-3);margin:0;}
.pf-faceof b{color:var(--bronze-deep);font-weight:600;}

/* the page body */
.pf-doc{max-width:64ch;margin:0 auto;padding:clamp(28px,6vw,56px) clamp(20px,5vw,40px) 96px;}
.pf-title{font-family:var(--font-display);font-weight:700;font-size:clamp(30px,5vw,42px);line-height:1.06;
          letter-spacing:-.02em;color:var(--ink);margin:0 0 28px;text-wrap:balance;}
.pf-doc h2{font-family:var(--font-display);font-weight:600;font-size:21px;line-height:1.2;
           letter-spacing:-.01em;color:var(--bronze);margin:34px 0 10px;}
.pf-doc h3{font-family:var(--font-display);font-weight:600;font-size:17px;color:var(--ink);margin:24px 0 8px;}
.pf-doc p{margin:0 0 16px;text-wrap:pretty;}
.pf-doc ul,.pf-doc ol{margin:0 0 18px;padding-left:1.3em;}
.pf-doc li{margin:0 0 7px;}
.pf-doc li::marker{color:var(--gold-deep);}
.pf-doc code{font-family:var(--font-mono);font-size:.86em;background:var(--paper-2);
             border:1px solid var(--border-faint);border-radius:5px;padding:1px 5px;color:var(--bronze-deep);}
.pf-doc strong{font-weight:600;color:var(--ink);}
.pf-doc a{color:var(--bronze-deep);text-decoration:none;border-bottom:1px solid var(--gold-soft);}
.pf-foot{max-width:64ch;margin:0 auto;padding:0 clamp(20px,5vw,40px) 60px;
         font-family:var(--font-mono);font-size:11px;color:var(--ink-4);}
@media (prefers-reduced-motion:reduce){*{scroll-behavior:auto;}}
"""

# human label for an address scheme — what KIND of thing this is the face of (translate, never machine)
_SCHEME_NOUN = {
    "skill": "skill", "guide": "guide", "context": "context", "run": "a run output",
    "ui": "screen", "cas": "a content blob", "code": "a code symbol", "project": "project",
}


def _inline(text: str) -> str:
    """Inline markdown → HTML on an already-escaped string: **bold**, `code`. (Order matters: code first
    so a `**` inside code isn't bolded.)"""
    # `code`
    text = re.sub(r"`([^`]+)`", lambda m: f"<code>{m.group(1)}</code>", text)
    # **bold**
    text = re.sub(r"\*\*([^*]+)\*\*", lambda m: f"<strong>{m.group(1)}</strong>", text)
    return text


def render_markdown(md: str) -> str:
    """A small, dependency-free markdown→HTML renderer for the structures guides use: ## / ### headings,
    paragraphs, `*`/`-` bullet lists, `1.` numbered lists, **bold**, `code`. Everything is HTML-escaped
    first (the content is DATA — never trust it as markup), then the known structures are re-applied."""
    lines = md.replace("\r\n", "\n").split("\n")
    out, i, n = [], 0, len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            i += 1
            continue
        # headings
        m = re.match(r"^(#{2,4})\s+(.*)$", stripped)
        if m:
            level = min(len(m.group(1)), 3)            # ## or ### → h2 (top body heading is h2/h3)
            tag = "h2" if level == 2 else "h3"
            out.append(f"<{tag}>{_inline(_html.escape(m.group(2)))}</{tag}>")
            i += 1
            continue
        # unordered list
        if re.match(r"^[*\-]\s+", stripped):
            items = []
            while i < n and re.match(r"^[*\-]\s+", lines[i].strip()):
                items.append(re.sub(r"^[*\-]\s+", "", lines[i].strip()))
                i += 1
            out.append("<ul>" + "".join(f"<li>{_inline(_html.escape(it))}</li>" for it in items) + "</ul>")
            continue
        # ordered list
        if re.match(r"^\d+\.\s+", stripped):
            items = []
            while i < n and re.match(r"^\d+\.\s+", lines[i].strip()):
                items.append(re.sub(r"^\d+\.\s+", "", lines[i].strip()))
                i += 1
            out.append("<ol>" + "".join(f"<li>{_inline(_html.escape(it))}</li>" for it in items) + "</ol>")
            continue
        # paragraph (gather consecutive non-blank, non-structural lines)
        para = [stripped]
        i += 1
        while i < n and lines[i].strip() and not re.match(r"^(#{2,4}\s|[*\-]\s|\d+\.\s)", lines[i].strip()):
            para.append(lines[i].strip())
            i += 1
        out.append(f"<p>{_inline(_html.escape(' '.join(para)))}</p>")
    return "\n".join(out)


def render_address_page(*, title: str, target: str, kind_noun: str, body_md: str,
                        face_of: str | None = None) -> str:
    """Render a full designed DNA page for an addressed thing. `title` = the page title, `target` = the
    address it documents, `kind_noun` = human word for the target (e.g. 'skill'), `body_md` = the
    markdown content, `face_of` = the human 'what it's the face of' line (defaults from kind_noun)."""
    target_h = _html.escape(target)
    face = face_of or f"the how-to for the <b>{_html.escape(target.split('://',1)[-1].replace('_',' '))}</b> {kind_noun}"
    body_html = render_markdown(body_md)
    return (
        "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        f"<title>{_html.escape(title)}</title><style>{_DNA_CSS}</style></head><body>"
        "<header class=\"pf-head\"><div class=\"inner\">"
        "<div class=\"pf-mark\">▦</div><div class=\"meta\">"
        "<p class=\"pf-eyebrow\">Page · the visible face of an address</p>"
        f"<p class=\"pf-faceof\">{face}</p></div></div></header>"
        f"<main class=\"pf-doc\"><h1 class=\"pf-title\">{_html.escape(title)}</h1>{body_html}</main>"
        f"<footer class=\"pf-foot\">face of {target_h} · served by the page-face service · no-script</footer>"
        "</body></html>"
    )


def render_guide_page(guide) -> str:
    """Render a GUIDE registry entry into its designed page (the common case)."""
    scheme = guide.target.split("://", 1)[0] if "://" in guide.target else ""
    kind_noun = _SCHEME_NOUN.get(scheme, "thing")
    return render_address_page(
        title=guide.label or guide.id, target=guide.target, kind_noun=kind_noun, body_md=guide.content)
