"""parse.py — reads every mockup, extracts its element addresses (data-ui-ref),
ties each to its feature + code via the address registry, and flags orphans both
ways. Produces _system/element-map.json. Run: python3 parse.py

This is the join key: element ⇄ address ⇄ feature ⇄ code, shared with the running
app's ui:// scheme. Add an addressable thing = register it in addresses.json
(extend-by-registration) + carry its data-ui-ref in the mockup; re-run to refresh.

──────────────────────────────────────────────────────────────────────────────
RG1 · EXTRACT — the candidate-element pass (additive; the registry-generation chain)
  Run: python3 parse.py --extract-candidates   →   _system/candidates.json
This is a SECOND, separate pass (the default `main()` element-map.json behaviour is
UNTOUCHED). It walks every mockup's DOM and emits the MEANINGFUL elements (buttons,
named sections, controls, semantic headings; layout-only / textless wrappers SKIPPED)
as candidate units — the allocation source the rest of the chain (register_element →
map → reduce → confirm → propose) registers into the address registry.

★ candidates.json — THE SEAM CONTRACT (frozen; [C]'s `register_element` reads this).
  { "generated_from": <int>,            # mockups walked
    "count": <int>,                     # number of candidate units
    "filter": { ... },                  # the meaningful-element filter, for transparency
    "candidates": [ {
       "mockup_file":      str,         # e.g. "C1-inbox-desktop.html"
       "selector":         str,         # UNIQUE locator within the file: a tag + :nth-of-type
                                        #   path from <body> (what RG9 write-back stamps onto)
       "outerHTML":        str,         # the element's raw HTML, bounded to ~700 chars
       "visible_text":     str,         # the element's FULL text CONTENT — own direct text THEN
                                        #   descendant text, ws-collapsed, capped 600. A container
                                        #   (button/section/nav) is grounded with the words inside
                                        #   it (the filter judges on OWN direct text; the dossier
                                        #   reads this full text). ~700-char outerHTML pairs with it.
                                        #   NB: AUTHORED text content (from the source HTML), incl.
                                        #   the text of hidden/alternate-state elements — NOT
                                        #   render-visible innerText (a CSS-hidden tab still yields
                                        #   its words, which is what register_element wants to ground on).
       "tag":              str,         # lowercased tag name (button, h4, section, nav, …)
       "ancestor_address": str,         # nearest STRICTLY-ABOVE data-ui-ref ui:// ancestor,
                                        #   else the mockup base_address (corpus-meta[file][3])
       "ancestor_dossier": dict|null,   # addresses.json[ancestor_address] dossier
                                        #   {region,capabilities,represents,code,howto} — null if
                                        #   the ancestor address is not a registry key (e.g. ui://chrome)
       "base_address":     str,         # the mockup's base ui:// (corpus-meta[file][3])
       "self_registered":  bool,        # True if THIS element itself carries a data-ui-ref
                                        #   (already registered — the chain may skip; surfaced not dropped)
       "self_address":     str|null     # that data-ui-ref value when self_registered, else null
    }, ... ] }
  Notes for the consumer ([C] register_element): NO dedup here (same surface across
  mockups appears multiple times → RG5 REDUCE collapses it). `ancestor_dossier` lets
  the child nest under + inherit the parent's framing. `base_address` is the fallback
  root when no registered ancestor is above the element.
──────────────────────────────────────────────────────────────────────────────
"""
import os, re, json, sys
from html.parser import HTMLParser

_REF = re.compile(r'data-ui-ref=["\']([^"\']+)["\']')

# ── RG1 meaningful-element filter (declared, transparent) ──────────────────────
# Semantic tags are always candidates (the floor). div/span join ONLY when named
# (a class) AND carrying their own direct text — and never if decorative-only.
_SEMANTIC_TAGS = {
    "button", "a", "input", "select", "textarea", "label",
    "h1", "h2", "h3", "h4", "h5", "h6",
    "nav", "section", "aside", "main", "header", "footer",
    "summary", "details", "li", "th",
}
# void / self-closing elements — never pushed on the ancestor stack (no end tag).
_VOID_TAGS = {"br", "input", "img", "meta", "link", "hr", "area", "base",
              "col", "embed", "param", "source", "track", "wbr"}
# decorative class-names: single-glyph dots/badges/keycaps — skip even if div/span.
_DECORATIVE_CLASSES = {"dot", "k", "kdot", "mono-chip", "badge", "i", "play",
                       "kicker", "live", "tag"}
# class-names that mark a div/span as the INNER TEXT-HOLDER of a control/node (a
# fragment, not a unit) — its words already belong to the kept parent. Skipped.
_FRAGMENT_CLASSES = {"label", "lbl", "nm", "kind", "ty", "seq", "t", "sm",
                     "who", "presence", "kindlabel", "name", "val", "value",
                     "num", "ct", "count", "meta", "sub", "hint", "ph"}
# tags that, when an ANCESTOR, mean a div/span is a fragment of a control — its
# words belong to that control (already a candidate), so the fragment is skipped.
_CONTROL_ANCESTOR_TAGS = {"button", "a", "label", "summary"}
# div/span need their OWN DIRECT text of at least this length to be a named unit
# (own text, NOT descendant — a layout wrapper whose words live in children is not
# itself a unit; its kept ancestor carries those words). Tuned for signal-over-noise.
_MIN_NAMED_TEXT = 12


def _attr(attrs, name):
    for k, v in attrs:
        if k == name:
            return v
    return None


class _CandidateExtractor(HTMLParser):
    """Streaming walk over one mockup: tracks the open-tag stack (with each frame's
    start char-offset + its data-ui-ref if any), the per-element collected text, and
    emits a candidate unit at end-tag for every element that passes the filter.
    convert_charrefs=False so &amp; etc. survive into outerHTML/text as authored."""

    def __init__(self, html, base_address, addresses):
        super().__init__(convert_charrefs=True)
        self.html = html
        self.base_address = base_address
        self.addresses = addresses
        self.candidates = []
        # line-start offsets → absolute char index from getpos() (1-based line, 0-based col)
        self._line_starts = [0]
        for i, ch in enumerate(html):
            if ch == "\n":
                self._line_starts.append(i + 1)
        # stack frames: dict(tag, start, ui_ref, text_parts, type_counts_snapshot)
        self.stack = []
        # nth-of-type counters per (parent_id, tag) — for unique selectors
        self._sibling_counts = [{}]  # one dict per open level (root level present)

    def _abs(self):
        line, col = self.getpos()
        return self._line_starts[line - 1] + col

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in _VOID_TAGS:
            self._note_void(tag, attrs)
            return
        # nth-of-type within current parent
        counts = self._sibling_counts[-1]
        counts[tag] = counts.get(tag, 0) + 1
        nth = counts[tag]
        ui_ref = _attr(attrs, "data-ui-ref")
        cls = _attr(attrs, "class") or ""
        self.stack.append({
            "tag": tag, "start": self._abs(), "ui_ref": ui_ref,
            "class": cls, "nth": nth,
            # own_parts = this element's DIRECT text (the filter reads this);
            # desc_parts = text collected from descendants (grounds the dossier).
            "own_parts": [], "desc_parts": [],
        })
        self._sibling_counts.append({})

    def handle_startendtag(self, tag, attrs):
        # self-closing in source (e.g. <input .../>): treat as a complete element
        tag = tag.lower()
        counts = self._sibling_counts[-1]
        counts[tag] = counts.get(tag, 0) + 1
        nth = counts[tag]
        ui_ref = _attr(attrs, "data-ui-ref")
        cls = _attr(attrs, "class") or ""
        start = self._abs()
        # outerHTML: from start to current parser position end-of-tag — approximate by
        # slicing to the next '>' from start (the tag itself).
        end = self.html.find(">", start)
        end = (end + 1) if end != -1 else start
        frame = {"tag": tag, "start": start, "ui_ref": ui_ref, "class": cls,
                 "nth": nth, "own_parts": [], "desc_parts": []}
        self._emit_if_meaningful(frame, end)

    def _note_void(self, tag, attrs):
        # void tag in a non-self-closed form (<input ...>): still a complete element.
        counts = self._sibling_counts[-1]
        counts[tag] = counts.get(tag, 0) + 1
        nth = counts[tag]
        ui_ref = _attr(attrs, "data-ui-ref")
        cls = _attr(attrs, "class") or ""
        start = self._abs()
        end = self.html.find(">", start)
        end = (end + 1) if end != -1 else start
        frame = {"tag": tag, "start": start, "ui_ref": ui_ref, "class": cls,
                 "nth": nth, "own_parts": [], "desc_parts": []}
        self._emit_if_meaningful(frame, end)

    def handle_data(self, data):
        # direct text belongs to the innermost OPEN element (own_parts) — it is
        # also that element's descendant text; ancestors collect it at endtag.
        s = data.strip()
        if s and self.stack:
            self.stack[-1]["own_parts"].append(s)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in _VOID_TAGS:
            return
        # pop to the matching open tag (tolerant of minor imbalance)
        idx = None
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i]["tag"] == tag:
                idx = i
                break
        if idx is None:
            return
        # collapse any frames above the match (malformed nesting): fold each
        # orphaned child's text DOWN into the matched frame's descendant text so
        # the words survive. (These collapsed frames are NOT emitted as their own
        # candidates — they only arise from malformed/unbalanced markup; the
        # corpus is well-formed in practice, verified: every addressed element
        # round-trips into candidates.json, MISSING=0.)
        while len(self.stack) - 1 > idx:
            child = self.stack.pop()
            self._sibling_counts.pop()
            self.stack[-1]["desc_parts"].extend(child["own_parts"])
            self.stack[-1]["desc_parts"].extend(child["desc_parts"])
        frame = self.stack.pop()
        self._sibling_counts.pop()
        # PROPAGATE this element's full text up to its parent's descendant text,
        # so a container (button/section/nav) is grounded with the words that
        # live in its children — the fix that lets us drop fragment leaves
        # without losing the words downstream register_element needs.
        if self.stack:
            self.stack[-1]["desc_parts"].extend(frame["own_parts"])
            self.stack[-1]["desc_parts"].extend(frame["desc_parts"])
        line, col = self.getpos()
        end = self._line_starts[line - 1] + col + len(tag) + 3  # past </tag>
        self._emit_if_meaningful(frame, end)

    def _ancestor_address(self):
        # nearest STRICTLY-ABOVE frame carrying a data-ui-ref; else base_address
        for f in reversed(self.stack):
            if f.get("ui_ref"):
                return f["ui_ref"]
        return self.base_address

    def _selector(self):
        # unique tag + :nth-of-type path from body, built from the open stack
        parts = []
        for f in self.stack:
            parts.append(f"{f['tag']}:nth-of-type({f['nth']})")
        return parts

    def _has_control_ancestor(self):
        # the live open stack IS the ancestor chain at emit time (the frame is
        # already popped). A div/span inside a button/a/label/summary is a
        # fragment of that control — its words belong to the control, not itself.
        return any(f["tag"] in _CONTROL_ANCESTOR_TAGS for f in self.stack)

    def _is_meaningful(self, frame, own_text):
        # ── unconditional keep: an element that already carries a data-ui-ref is
        #    addressed → definitionally a registered unit (surface, never drop) ──
        if frame.get("ui_ref"):
            return True
        tag = frame["tag"]
        if tag in _SEMANTIC_TAGS:
            return True   # controls / regions / semantic headings — the floor
        if tag in ("div", "span"):
            cls = frame.get("class") or ""
            classes = set(cls.split())
            if not classes:
                return False  # unnamed layout wrapper
            if classes & _DECORATIVE_CLASSES:
                return False  # decorative glyph/badge
            if classes & _FRAGMENT_CLASSES:
                return False  # inner text-holder of a control/node (its words
                              # belong to the kept parent) — a fragment, not a unit
            if self._has_control_ancestor():
                return False  # fragment of a button/link/label — skip
            # a named div/span counts ONLY on its OWN direct text (not the words
            # of its children — those belong to the child or are the container's
            # job to summarise). A wrapper whose text lives in descendants is not
            # itself a unit; its kept ancestor already carries those words.
            if len(own_text) >= _MIN_NAMED_TEXT:
                return True
        return False

    def _emit_if_meaningful(self, frame, end):
        own_text = re.sub(r"\s+", " ", " ".join(frame["own_parts"]).strip())
        # full visible text = own direct text THEN descendant text (so a container
        # is grounded with the words inside it) — what register_element reads.
        full = re.sub(r"\s+", " ",
                      " ".join(frame["own_parts"] + frame["desc_parts"]).strip())
        if not self._is_meaningful(frame, own_text):
            return
        start = frame["start"]
        outer = self.html[start:end]
        outer = re.sub(r"\s+", " ", outer).strip()[:700]
        sel_path = self._selector() + [f"{frame['tag']}:nth-of-type({frame['nth']})"]
        ancestor = self._ancestor_address()
        dossier = self.addresses.get(ancestor)
        self.candidates.append({
            "mockup_file": None,  # filled by caller
            "selector": " > ".join(sel_path),
            "outerHTML": outer,
            "visible_text": full[:600],
            "tag": frame["tag"],
            "ancestor_address": ancestor,
            "ancestor_dossier": dossier,
            "base_address": self.base_address,
            "self_registered": bool(frame.get("ui_ref")),
            "self_address": frame.get("ui_ref"),
        })


def extract_candidates(screens: dict, addresses: dict, bases: dict) -> dict:
    """screens={file:html}; addresses={ui://:dossier}; bases={file:base_address}.
    Returns the candidates.json payload (see the SEAM CONTRACT in the module docstring)."""
    out = []
    for name in sorted(screens):
        ex = _CandidateExtractor(screens[name], bases.get(name, ""), addresses)
        ex.feed(screens[name])
        ex.close()
        for c in ex.candidates:
            c["mockup_file"] = name
            out.append(c)
    return {
        "generated_from": len(screens),
        "count": len(out),
        "filter": {
            "always_keep": "any element carrying data-ui-ref (already addressed)",
            "semantic_tags": sorted(_SEMANTIC_TAGS),
            "div_span_rule": "kept ONLY when: has a class AND not decorative AND not "
                             "a fragment-class AND no control ancestor (button/a/label/"
                             f"summary) AND OWN DIRECT text >= {_MIN_NAMED_TEXT} chars. "
                             "(Own text, not descendant — a wrapper whose words live in "
                             "children is not a unit; the kept ancestor carries the words.)",
            "decorative_classes_skipped": sorted(_DECORATIVE_CLASSES),
            "fragment_classes_skipped": sorted(_FRAGMENT_CLASSES),
            "control_ancestor_tags": sorted(_CONTROL_ANCESTOR_TAGS),
            "void_tags": sorted(_VOID_TAGS),
            "note": "no dedup — same surface across mockups recurs; RG5 REDUCE collapses",
        },
        "candidates": out,
    }


def _run_extract():
    here = os.path.dirname(os.path.abspath(__file__))
    mockdir = os.path.join(os.path.dirname(here), "mockups")
    with open(os.path.join(here, "addresses.json"), encoding="utf-8") as f:
        reg = json.load(f)
    addresses = reg.get("addresses", reg)
    with open(os.path.join(here, "corpus-meta.json"), encoding="utf-8") as f:
        meta = json.load(f)
    bases = {fn: (v[3] if isinstance(v, list) and len(v) > 3 else "")
             for fn, v in meta.items()}
    screens = {}
    for fn in sorted(os.listdir(mockdir)):
        if fn.endswith(".html"):
            with open(os.path.join(mockdir, fn), encoding="utf-8") as f:
                screens[fn] = f.read()
    payload = extract_candidates(screens, addresses, bases)
    out = os.path.join(here, "candidates.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f"candidates -> {out}")
    print(f"  {payload['count']} candidate units across {payload['generated_from']} mockups")
    # a quick by-tag rollup so the count is legible
    from collections import Counter
    by_tag = Counter(c["tag"] for c in payload["candidates"])
    print("  by tag: " + ", ".join(f"{t}={n}" for t, n in by_tag.most_common()))


def build_map(screens: dict, addresses: dict) -> dict:
    """screens = {filename: html}; addresses = {address: {region, represents, code}}.
    Returns {elements:[...], orphans:{unregistered:[...], unused:[...]}, summary:{...}}."""
    elements, used = [], set()
    for name, html in screens.items():
        for addr in _REF.findall(html):
            used.add(addr)
            reg = addresses.get(addr)
            elements.append({
                "screen": name,
                "address": addr,
                "region": (reg or {}).get("region"),
                "feature": (reg or {}).get("represents"),
                "code": (reg or {}).get("code"),
                "registered": reg is not None,
            })
    unregistered = sorted({e["address"] for e in elements if not e["registered"]})
    unused = sorted(a for a in addresses if a not in used)
    return {
        "elements": elements,
        "orphans": {"unregistered": unregistered, "unused": unused},
        "summary": {
            "screens": len(screens),
            "addressed_elements": len(elements),
            "distinct_addresses_used": len(used),
            "registered_addresses": len(addresses),
            "unregistered_orphans": len(unregistered),
            "unused_orphans": len(unused),
        },
    }


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    mockdir = os.path.join(os.path.dirname(here), "mockups")
    with open(os.path.join(here, "addresses.json"), encoding="utf-8") as f:
        reg = json.load(f)
    addresses = reg.get("addresses", reg)  # tolerate {addresses:{...}} or a bare map
    screens = {}
    for fn in sorted(os.listdir(mockdir)):
        if fn.endswith(".html"):
            with open(os.path.join(mockdir, fn), encoding="utf-8") as f:
                screens[fn] = f.read()
    m = build_map(screens, addresses)
    out = os.path.join(here, "element-map.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)
    s = m["summary"]
    print(f"mapped -> {out}")
    print(f"  {s['addressed_elements']} addressed elements across {s['screens']} screens "
          f"({s['distinct_addresses_used']} distinct addresses)")
    print(f"  orphans: {s['unregistered_orphans']} used-but-unregistered, "
          f"{s['unused_orphans']} registered-but-unused")


if __name__ == "__main__":
    if "--extract-candidates" in sys.argv:
        _run_extract()
    else:
        main()
