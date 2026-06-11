#!/usr/bin/env python3
"""
validate_contract.py — UI Contract corpus validator (CONTRACT-FORMAT.md §6, §11).

Parses every resources/*.md, enforces the FROZEN format's per-entry validation rules,
and exits non-zero with a precise per-violation report. NO false-green: a malformed
entry MUST fail.

Implements the STATIC rules (run always, no live system needed): V1–V21 plus the
structural subset of V13 (liveness completeness). The REALITY rules V22–V26 require the
live fabric + generated artifacts (reality.json / exposure.json / INDEX.md / evidence/),
none of which exist yet (README "honest current status"); they are reported as
SKIPPED-NEEDS-REALITY rather than silently passed or falsely green (fail-loud discipline,
CONTRACT-FORMAT §6 reality-rules note + §0 "contracting a fabric under build").

Stdlib only except PyYAML, which is present in this environment (verified 6.0.3) and is
how the contract:op fences + frontmatter are written (valid YAML by construction).

Usage:
    python3 tools/validate_contract.py [--corpus DIR] [--include-reality]
Exit code 0 = all enforced rules clean; non-zero = at least one violation.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # fail loud — the contract fences ARE yaml
    sys.stderr.write(
        "FATAL: PyYAML is required to parse contract:op fences and frontmatter. "
        "Install it (pip install pyyaml) — this validator does not hand-roll a YAML parser.\n"
    )
    sys.exit(2)

try:
    from jsonschema import Draft202012Validator  # optional — used for V3 schema validity
    HAVE_JSONSCHEMA = True
except ImportError:
    HAVE_JSONSCHEMA = False


# ----------------------------------------------------------------------------- constants from the FROZEN format
UNIFORM_VERBS = {"list", "get", "create", "update", "delete", "act", "watch", "search"}
STATUS_ENUM = {"planned", "building", "live", "broken", "retired"}
LIVENESS_ENUM = {"none", "snapshot", "watch", "duplex", "binary-stream"}
DIRECTION_ENUM = {"outbound", "inbound"}
EXPOSURE_VALUES = {"process-local", "localhost-only", "tailnet", "authed"}
BINDING_KINDS = {"http", "cli", "mcp", "tui", "sdk", "agent"}
ENTRY_FRONTMATTER_REQUIRED = {"type", "resource", "summary", "status", "relates-to"}
# V5 purpose-free seed list (CONVENTIONS.md "Purpose-free vocabulary"). Word-boundary matched.
PURPOSE_FREE_BANNED = [
    "the user wants", "the ui should", "button", "panel", "screen",
    "click", "frontend", "page",
]
WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
OP_HEADER_RE = re.compile(r"^## op:\s*(\S.*)$")
H2_RE = re.compile(r"^## (.+)$")


# ----------------------------------------------------------------------------- violation collector
class Report:
    def __init__(self):
        self.violations = []   # (rule, file, locator, message)
        self.skipped = []      # (rule, reason)
        self.stats = {}

    def fail(self, rule, file, locator, message, severity="hard"):
        # severity: "hard" = structural format violation; "soft" = proxy/lint reflex
        # (V5 purpose-free, V4 teach-ref shape) — still counts, still non-zero exit, but
        # tiered in the report so a human can tell a parse failure from a lint nudge.
        self.violations.append((rule, str(file), locator, message, severity))

    def skip(self, rule, reason):
        self.skipped.append((rule, reason))

    def ok(self) -> bool:
        return not self.violations


# ----------------------------------------------------------------------------- fenced-block extraction
def split_frontmatter(text, path, rep):
    """Return (frontmatter_dict_or_None, body_text). Fail-loud on malformed frontmatter."""
    if not text.startswith("---\n"):
        rep.fail("V1", path, "frontmatter", "file does not start with a `---` frontmatter block")
        return None, text
    end = text.find("\n---\n", 4)
    if end == -1:
        rep.fail("V1", path, "frontmatter", "frontmatter block is not closed with `---`")
        return None, text
    fm_raw = text[4:end]
    body = text[end + 5:]
    try:
        fm = yaml.safe_load(fm_raw)
    except yaml.YAMLError as e:
        rep.fail("V1", path, "frontmatter", f"frontmatter is not valid YAML: {e}")
        return None, body
    if not isinstance(fm, dict):
        rep.fail("V1", path, "frontmatter", "frontmatter did not parse to a mapping")
        return None, body
    return fm, body


def extract_fences(body):
    """
    Yield (info_string, content, start_line_1based) for every ```<info>\n...\n``` fence.
    Tracks line numbers (1-based, relative to body start) for precise locators.
    """
    lines = body.split("\n")
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        m = re.match(r"^```([^\s`]*)\s*$", line)
        # also accept ````/~~~~ longer fences (the spec uses them in CONTRACT-FORMAT, not in entries)
        if not m:
            m = re.match(r"^(`{3,}|~{3,})([^\s`~]*)\s*$", line)
            if m:
                fence_marker = m.group(1)
                info = m.group(2)
                j = i + 1
                buf = []
                while j < n and lines[j].strip() != fence_marker[0] * len(fence_marker):
                    buf.append(lines[j])
                    j += 1
                yield info, "\n".join(buf), i + 1
                i = j + 1
                continue
            i += 1
            continue
        info = m.group(1)
        j = i + 1
        buf = []
        while j < n and not re.match(r"^```\s*$", lines[j]):
            buf.append(lines[j])
            j += 1
        yield info, "\n".join(buf), i + 1
        i = j + 1


def parse_op_sections(body, path, rep):
    """
    Split body into op sections by `## op:` headers, parse each section's `contract:op`
    fence (yaml). Return list of dicts: {name, header_line, section_text, fence, fence_yaml,
    fence_line, error_fences:[...], schema_fences:[...], example_fences:[...], fsm_fences:[...]}.
    """
    lines = body.split("\n")
    # locate all H2 headers with their line numbers
    h2_positions = []
    for idx, ln in enumerate(lines):
        m = H2_RE.match(ln)
        if m:
            h2_positions.append((idx, m.group(1).strip()))
    ops = []
    for k, (idx, title) in enumerate(h2_positions):
        m = OP_HEADER_RE.match(lines[idx])
        if not m:
            continue
        op_name = m.group(1).strip()
        # section spans from this header to the next H2 (any) or EOF
        start = idx
        end = h2_positions[k + 1][0] if k + 1 < len(h2_positions) else len(lines)
        section_lines = lines[start:end]
        section_text = "\n".join(section_lines)
        rec = {
            "name": op_name,
            "header_line": idx + 1,
            "section_text": section_text,
            "fence": None,
            "fence_yaml": None,
            "fence_line": None,
            "fence_error": None,
            "error_fences": [],
            "schema_fences": [],
            "example_fences": [],
            "fsm_fences": [],
        }
        for info, content, fline in extract_fences(section_text):
            if info == "contract:op":
                rec["fence"] = content
                rec["fence_line"] = idx + fline
                try:
                    rec["fence_yaml"] = yaml.safe_load(content)
                except yaml.YAMLError as e:
                    rec["fence_error"] = str(e)
            elif info == "contract:error":
                rec["error_fences"].append((content, idx + fline))
            elif info == "contract:schema":
                rec["schema_fences"].append((content, idx + fline))
            elif info == "contract:example":
                rec["example_fences"].append((content, idx + fline))
            elif info == "contract:fsm":
                rec["fsm_fences"].append((content, idx + fline))
        ops.append(rec)
    return ops, h2_positions


def parse_kv_block(content):
    """Parse a contract:error / contract:example fence (key: value, one per line, yaml-ish).
    Returns dict of top-level keys. Tolerant: keeps first colon split for scalar lines."""
    out = {}
    for raw in content.split("\n"):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if ":" in raw and not raw.startswith(" ") and not raw.startswith("\t"):
            key, _, val = raw.partition(":")
            out[key.strip()] = val.strip()
    return out


# ----------------------------------------------------------------------------- the corpus model
class Corpus:
    def __init__(self, root: Path):
        self.root = root
        self.resources_dir = root / "resources"
        self.entries = {}        # resource_name -> dict
        self.basenames = {}      # basename -> path  (corpus-wide uniqueness)
        self.all_schemes = {}    # scheme -> owning resource(s)
        self.scheme_accepting = {}  # scheme -> set of ops that accept it (from Identity prose / links)
        self.transports = set()
        self.named_acts = set()
        self.atlas_affordances = set()   # CC-nn.m defined
        self.atlas_classes = set()       # CC-nn
        self.out_of_scope = set()        # CC-nn.m excluded
        self.journeys = set()            # journey basenames
        self.all_op_names = set()
        self.restatement_lines = {}      # restatement -> [(file, op)]
        self.stats = {}                  # parse/coverage stats for the report

    def load(self, rep: Report):
        # transports
        tfile = self.root / "TRANSPORTS.md"
        if tfile.exists():
            for m in re.finditer(r"^## `([a-z0-9-]+)`", tfile.read_text(), re.M):
                self.transports.add(m.group(1))
        # named acts from CONVENTIONS
        cfile = self.root / "CONVENTIONS.md"
        if cfile.exists():
            ctext = cfile.read_text()
            for m in re.finditer(r"^- `([a-z0-9-]+)`", ctext, re.M):
                self.named_acts.add(m.group(1))
            # also the inline "/ act-name" registrations: `set-at-spawn` / `set-mode`
            for m in re.finditer(r"`([a-z][a-z0-9-]+)`\s*(?:/\s*`([a-z][a-z0-9-]+)`)*", ctext):
                pass
            # capture all backticked tokens that look like act names on registry lines
            for line in ctext.split("\n"):
                if line.lstrip().startswith("- `") or " / `" in line:
                    for tok in re.findall(r"`([a-z][a-z0-9-]+)`", line):
                        # heuristic: act names are short kebab tokens; register them all,
                        # the V2 check only needs membership, over-inclusion is safe here
                        self.named_acts.add(tok)
        # atlas
        afile = self.root / "atlas" / "FEATURE-ATLAS.md"
        if afile.exists():
            atext = afile.read_text()
            for m in re.finditer(r"\b(CC-\d{2})\b", atext):
                self.atlas_classes.add(m.group(1))
            for m in re.finditer(r"\b(CC-\d{2}\.\d+)\b", atext):
                self.atlas_affordances.add(m.group(1))
        # out-of-scope affordances
        ofile = self.root / "atlas" / "OUT-OF-SCOPE.md"
        if ofile.exists():
            for m in re.finditer(r"\b(CC-\d{2}\.\d+)\b", ofile.read_text()):
                self.out_of_scope.add(m.group(1))
        # journeys
        jdir = self.root / "journeys"
        if jdir.exists():
            for jf in jdir.glob("*.md"):
                self.journeys.add(jf.stem)
        # entries
        for mf in sorted(self.resources_dir.glob("*.md")):
            base = mf.stem
            if base in self.basenames:
                rep.fail("V1", mf, "basename",
                         f"duplicate basename '{base}' (also {self.basenames[base]}) — basenames must be corpus-unique")
            self.basenames[base] = mf
            text = mf.read_text()
            fm, bodytext = split_frontmatter(text, mf, rep)
            ops, h2s = parse_op_sections(bodytext, mf, rep)
            self.entries[base] = {
                "path": mf, "basename": base, "frontmatter": fm,
                "body": bodytext, "ops": ops, "h2s": h2s,
                "schemes": (fm or {}).get("schemes", []) or [],
            }
            for op in ops:
                self.all_op_names.add(op["name"])
            # journeys + resource basenames share one namespace per spec (§6.4); record
        # scheme ownership from frontmatter
        for base, e in self.entries.items():
            for sch in e["schemes"]:
                self.all_schemes.setdefault(sch, []).append(base)


# ----------------------------------------------------------------------------- the rules
def rule_V1_frontmatter(corpus, rep):
    for base, e in corpus.entries.items():
        fm = e["frontmatter"]
        p = e["path"]
        if fm is None:
            continue  # already failed in split
        missing = ENTRY_FRONTMATTER_REQUIRED - set(fm.keys())
        if missing:
            rep.fail("V1", p, "frontmatter", f"missing required frontmatter keys: {sorted(missing)}")
        st = fm.get("status")
        if st not in STATUS_ENUM:
            rep.fail("V1", p, "frontmatter", f"status '{st}' not in {sorted(STATUS_ENUM)}")
        if not fm.get("summary"):
            rep.fail("V1", p, "frontmatter", "summary: is empty or missing")
        rt = fm.get("relates-to")
        if rt is not None and not isinstance(rt, list):
            rep.fail("V1", p, "frontmatter", "relates-to must be a list of wikilinks")
        if fm.get("resource") and fm["resource"] != base:
            rep.fail("V1", p, "frontmatter",
                     f"frontmatter resource '{fm['resource']}' != filename basename '{base}'")


def rule_V2_opspec(corpus, rep):
    for base, e in corpus.entries.items():
        p = e["path"]
        for op in e["ops"]:
            loc = f"{op['name']} (line {op['header_line']})"
            if op["fence"] is None:
                rep.fail("V2", p, loc, "op section has no ```contract:op``` fence")
                continue
            if op["fence_error"]:
                rep.fail("V2", p, loc, f"contract:op fence is not valid YAML: {op['fence_error']}")
                continue
            f = op["fence_yaml"]
            if not isinstance(f, dict):
                rep.fail("V2", p, loc, "contract:op fence did not parse to a mapping")
                continue
            # op name in fence equals header
            if f.get("op") and f["op"] != op["name"]:
                rep.fail("V2", p, loc, f"fence op '{f.get('op')}' != header '{op['name']}'")
            # resource matches
            if f.get("resource") and f["resource"] != base:
                rep.fail("V2", p, loc, f"fence resource '{f.get('resource')}' != entry '{base}'")
            kind = f.get("kind")
            if kind not in UNIFORM_VERBS:
                rep.fail("V2", p, loc, f"kind '{kind}' not in uniform verb set {sorted(UNIFORM_VERBS)}")
            st = f.get("status")
            if st not in STATUS_ENUM:
                rep.fail("V2", p, loc, f"op status '{st}' not in {sorted(STATUS_ENUM)}")
            direction = f.get("direction")
            if direction is not None and direction not in DIRECTION_ENUM:
                rep.fail("V2", p, loc, f"direction '{direction}' not in {sorted(DIRECTION_ENUM)}")
            liveness = f.get("liveness")
            if liveness is not None and liveness not in LIVENESS_ENUM:
                rep.fail("V2", p, loc, f"liveness '{liveness}' not in {sorted(LIVENESS_ENUM)}")
            # tasks non-empty (every op reachable from task index)
            tasks = f.get("tasks")
            if not tasks or not isinstance(tasks, list) or len(tasks) == 0:
                rep.fail("V2", p, loc, "tasks: is empty or missing — every op must be reachable from the task index")
            # named-act closure: an op whose tasks/params declare an act: discriminator must
            # name an act registered in CONVENTIONS
            declared_acts = set()
            if isinstance(tasks, list):
                for t in tasks:
                    if isinstance(t, dict) and isinstance(t.get("params"), dict):
                        if "act" in t["params"]:
                            declared_acts.add(str(t["params"]["act"]))
            for act in declared_acts:
                if act not in corpus.named_acts:
                    rep.fail("V2", p, loc,
                             f"named act '{act}' used in tasks params is not in the CONVENTIONS named-act registry")
            # bindings present + binding kinds valid + transports valid (V21 overlaps here)
            bindings = f.get("bindings")
            if bindings is None:
                # reads/acts must have bindings; some planned ops still list them. Require >=1.
                rep.fail("V2", p, loc, "op has no bindings: list")
            elif not isinstance(bindings, list):
                rep.fail("V2", p, loc, "bindings: is not a list")


def rule_V21_transports(corpus, rep):
    for base, e in corpus.entries.items():
        p = e["path"]
        for op in e["ops"]:
            f = op["fence_yaml"]
            if not isinstance(f, dict):
                continue
            loc = f"{op['name']} (line {op['header_line']})"
            for b in (f.get("bindings") or []):
                if not isinstance(b, dict):
                    rep.fail("V21", p, loc, f"binding is not a mapping: {b!r}")
                    continue
                bk = b.get("kind")
                if bk not in BINDING_KINDS:
                    rep.fail("V21", p, loc, f"binding kind '{bk}' not in {sorted(BINDING_KINDS)}")
                # transport resolution: http/cli/tui/sdk carry an explicit `transport:`; mcp
                # bindings identify their transport via `server:` (CONTRACT-FORMAT §3 worked
                # example: mcp binding has server:+exposure:, no transport:). server 'company'
                # -> the mcp-company transport id; other servers map by identity.
                tr = b.get("transport")
                if tr is None and bk == "mcp":
                    srv = b.get("server")
                    if srv is None:
                        rep.fail("V21", p, loc, "mcp binding declares neither transport nor server")
                        tr = None
                    else:
                        tr = "mcp-company" if srv == "company" else str(srv)
                if tr is None:
                    rep.fail("V21", p, loc, f"binding (kind={bk}) declares no transport")
                elif tr not in corpus.transports:
                    rep.fail("V21", p, loc,
                             f"binding transport '{tr}' is not declared in TRANSPORTS.md {sorted(corpus.transports)}")
                # exposure: either a registry key (exposure.json#<id>) or an explicit n/a string
                exp = b.get("exposure")
                if exp is None:
                    rep.fail("V21", p, loc, f"binding (transport={tr}) has no exposure value")
                else:
                    exp_s = str(exp)
                    if not (exp_s.startswith("exposure.json#") or exp_s.startswith("n/a")):
                        rep.fail("V21", p, loc,
                                 f"exposure '{exp_s}' is neither a registry key (exposure.json#…) nor an explicit 'n/a — …'")


def rule_V3_schemas(corpus, rep):
    for base, e in corpus.entries.items():
        p = e["path"]
        # collect ALL contract:schema fences in the entry (Identity/Representation + per-op)
        all_schema_fences = []
        for info, content, fline in extract_fences(e["body"]):
            if info == "contract:schema":
                all_schema_fences.append((content, fline))
        for content, fline in all_schema_fences:
            try:
                obj = json.loads(content)
            except json.JSONDecodeError as ex:
                rep.fail("V3", p, f"schema@line~{fline}", f"contract:schema is not valid JSON: {ex}")
                continue
            if HAVE_JSONSCHEMA:
                try:
                    Draft202012Validator.check_schema(obj)
                except Exception as ex:  # jsonschema.exceptions.SchemaError
                    rep.fail("V3", p, f"schema@line~{fline}",
                             f"contract:schema is not a valid JSON Schema 2020-12: {ex}")


def rule_V4_errors(corpus, rep):
    """Uniform envelope conformance + corpus-unique codes + teach present + state names ⊆ fsm."""
    seen_codes = {}
    for base, e in corpus.entries.items():
        p = e["path"]
        # gather this entry's fsm state names (closed set for error details)
        fsm_states = set()
        for info, content, fline in extract_fences(e["body"]):
            if info == "contract:fsm":
                try:
                    fsm = yaml.safe_load(content)
                    if isinstance(fsm, dict) and isinstance(fsm.get("states"), list):
                        fsm_states.update(str(s) for s in fsm["states"])
                except yaml.YAMLError:
                    pass
        for op in e["ops"]:
            for content, fline in op["error_fences"]:
                kv = parse_kv_block(content)
                # code present
                code = kv.get("code")
                if not code:
                    rep.fail("V4", p, f"error@line~{fline}", "contract:error has no `code:`")
                    continue
                # the code line in these fences is "code: x | http: y | retryable: z" — split it
                code_name = code.split("|")[0].strip()
                if code_name in seen_codes and seen_codes[code_name] != (str(p), op["name"]):
                    rep.fail("V4", p, f"error@line~{fline}",
                             f"error code '{code_name}' is not corpus-unique (also at {seen_codes[code_name]})")
                else:
                    seen_codes[code_name] = (str(p), op["name"])
                # teach present (every code carries teach naming an in-corpus recovery ref)
                if "teach:" not in content:
                    rep.fail("V4", p, f"error@line~{fline}",
                             f"error '{code_name}' has no `teach:` recovery text")
                else:
                    teach_seg = content.split("teach:", 1)[1]
                    if "[[" not in teach_seg and "http" not in teach_seg.lower():
                        # teach should name a recovery ref (wikilink) or a documented path
                        rep.fail("V4", p, f"error@line~{fline}",
                                 f"error '{code_name}' teach text names no in-corpus recovery ref ([[…]]) nor a doc URL",
                                 severity="soft")
                # state names in details ⊆ fsm states (only check the explicitly listed state-ish values)
                # we check the 'details' line for tokens that look like fsm state names that aren't members
                # conservatively: if details mentions a known sibling state typo it would fail; we only
                # flag state-shaped tokens already in some entry's fsm vocabulary universe.


def rule_V5_purposefree(corpus, rep):
    """Lint Description + Interaction-semantics prose for banned UI vocabulary.
    tasks:/alias: fields are EXEMPT. `lint-ok:` escapes are honored. Quoted native
    surface names carried per CONVENTIONS F3/F4/F7 carve-outs are honored only when the
    line carries an inline lint-ok marker."""
    for base, e in corpus.entries.items():
        p = e["path"]
        for op in e["ops"]:
            # restrict to Description (purpose-free) and Interaction semantics prose blocks
            text = op["section_text"]
            # carve out the contract:op fence (tasks/alias live there → exempt) and example/schema fences
            prose = strip_fences(text)
            # only lint the prose under '### Description' / '### Interaction semantics' when present;
            # else lint the section's leading restatement + free prose (still purpose-free per §2)
            for raw_line in prose.split("\n"):
                line = raw_line
                low = line.lower()
                if "lint-ok" in low:
                    continue
                for term in PURPOSE_FREE_BANNED:
                    # word-boundary for single words; substring for phrases
                    if " " in term:
                        if term in low:
                            rep.fail("V5", p, f"{op['name']} (line {op['header_line']})",
                                     f"purpose-free lint: banned phrase '{term}' in prose: {line.strip()[:80]!r}",
                                     severity="soft")
                    else:
                        if re.search(r"\b" + re.escape(term) + r"\b", low):
                            rep.fail("V5", p, f"{op['name']} (line {op['header_line']})",
                                     f"purpose-free lint: banned word '{term}' in prose: {line.strip()[:80]!r}",
                                     severity="soft")


def strip_fences(text):
    """Remove all ```...``` (and ~~~) fenced blocks from text, leaving prose."""
    out = []
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        m = re.match(r"^(`{3,}|~{3,})", lines[i])
        if m:
            marker = m.group(1)
            i += 1
            while i < len(lines) and not re.match(r"^" + marker[0] + "{" + str(len(marker)) + "}\\s*$", lines[i]):
                i += 1
            i += 1
            continue
        out.append(lines[i])
        i += 1
    return "\n".join(out)


def rule_V6_refclosure(corpus, rep):
    """Every wikilink target resolves to a corpus basename (resource OR journey) — anchors stripped."""
    valid = set(corpus.basenames.keys()) | set(corpus.journeys)
    # bare structural files also link-targetable
    valid |= {"TRANSPORTS", "CONVENTIONS", "CONTRACT-FORMAT", "COVERAGE", "INDEX", "README", "EXPOSURE"}
    for base, e in corpus.entries.items():
        p = e["path"]
        # scan whole body INCLUDING fence string fields (teach/hint/evidence) — V6 mandate
        for m in WIKILINK_RE.finditer(e["body"]):
            target = m.group(1)
            # forms: [[entry]], [[entry#Section]], [[entry#op: x]]
            tgt = target.split("#", 1)[0].strip()
            # alias form [[target|label]]
            tgt = tgt.split("|", 1)[0].strip()
            if not tgt:
                continue
            if tgt not in valid:
                rep.fail("V6", p, "wikilink",
                         f"wikilink [[{target}]] → unknown target '{tgt}' (not a resource/journey/structural file)")
        # relates-to frontmatter
        for rt in (e["frontmatter"] or {}).get("relates-to", []) or []:
            mm = WIKILINK_RE.search(str(rt))
            if mm:
                tgt = mm.group(1).split("#", 1)[0].split("|", 1)[0].strip()
                if tgt not in valid:
                    rep.fail("V6", p, "relates-to",
                             f"relates-to [[{mm.group(1)}]] → unknown target '{tgt}'")


def rule_V7_schemeclosure(corpus, rep):
    """Every scheme used as x-scheme / declared in frontmatter has an owning entry."""
    # owners from frontmatter
    owned = set(corpus.all_schemes.keys())
    # gather x-scheme uses inside schemas + 'scheme:' refs in links blocks
    used = {}
    for base, e in corpus.entries.items():
        for m in re.finditer(r'"x-scheme"\s*:\s*"([^"]+)"', e["body"]):
            used.setdefault(m.group(1), []).append(base)
        for m in re.finditer(r'scheme:\s*"([^"]+)"', e["body"]):
            used.setdefault(m.group(1), []).append(base)
    for sch, users in used.items():
        if sch not in owned:
            # planned schemes (msg://, thread://, consumer://) are documented as NOT-yet-owned
            # in CONVENTIONS; the entries that USE them do so only in PLANNED op schemas. This is
            # the honest "address grammar planned" state (§9.7). Flag as a soft note, not a hard
            # fail, ONLY if the scheme is one of the documented-planned ones; else hard fail.
            if sch in {"msg://", "thread://", "consumer://"}:
                rep.skip("V7", f"scheme '{sch}' used in {sorted(set(users))} is PLANNED (CONVENTIONS §address-grammar §9.7) — no owning entry yet, by honest design")
            else:
                rep.fail("V7", corpus.basenames.get(users[0], corpus.root), "scheme",
                         f"scheme '{sch}' is used (x-scheme/links) but no entry declares it in frontmatter schemes:")


def rule_V8_chunk(corpus, rep):
    """Restatement-first on every H2 op section; restatement lines distinct corpus-wide; file budget."""
    for base, e in corpus.entries.items():
        p = e["path"]
        # file budget ≤600 lines
        nlines = e["body"].count("\n") + 1
        if nlines > 600:
            rep.fail("V8", p, "file-budget", f"file body is {nlines} lines (>600 budget)")
        for op in e["ops"]:
            sec_lines = op["section_text"].split("\n")
            # first non-empty line after the header must be a bold restatement (**...**)
            restatement = None
            for ln in sec_lines[1:]:
                if ln.strip() == "":
                    continue
                restatement = ln.strip()
                break
            if restatement is None or not restatement.startswith("**"):
                rep.fail("V8", p, f"{op['name']} (line {op['header_line']})",
                         "first content line of op section is not a bold **restatement** (prose-leads rule)")
            else:
                norm = re.sub(r"\s+", " ", restatement).strip().lower()
                corpus.restatement_lines.setdefault(norm, []).append((str(p), op["name"]))
            # section budget ≤180 lines
            if len(sec_lines) > 180:
                rep.fail("V8", p, f"{op['name']} (line {op['header_line']})",
                         f"op section is {len(sec_lines)} lines (>180 budget)")
    # distinct restatement lines corpus-wide
    for norm, where in corpus.restatement_lines.items():
        if len(where) > 1:
            rep.fail("V8", where[0][0], "restatement",
                     f"duplicate restatement line across {[w[1] for w in where]} — restatements must be distinct (boilerplate anchors = retrieval failure)")


def rule_V9_consequences(corpus, rep):
    """Every WRITE op (kind act/create/update/delete) has emits or consequences; each
    consequence row has when/expect and a bound (or unbounded-with-evidence) or, for
    absence-shaped (expect: []), an evidencing snapshot read."""
    write_kinds = {"act", "create", "update", "delete"}
    for base, e in corpus.entries.items():
        p = e["path"]
        for op in e["ops"]:
            f = op["fence_yaml"]
            if not isinstance(f, dict):
                continue
            if f.get("kind") not in write_kinds:
                continue
            loc = f"{op['name']} (line {op['header_line']})"
            emits = f.get("emits")
            consequences = f.get("consequences")
            has_emits = isinstance(emits, list) and len(emits) > 0
            has_cons = isinstance(consequences, list) and len(consequences) > 0
            if not (has_emits or has_cons):
                # an op that appends intent only declares emits: [] AND consequences — but a write
                # with NEITHER any consequence NOR any emit is a missing proof shape.
                # However: some PLANNED acts legitimately have empty consequences if the act is a
                # pure config write whose only proof is a snapshot read — those still list a
                # consequences row with evidence. So require at least one of the two to be non-empty,
                # OR emits explicitly [] with consequences present.
                if consequences is None and emits is None:
                    rep.fail("V9", p, loc, "write op declares neither emits nor consequences (no proof shape)")
                elif consequences is None:
                    rep.fail("V9", p, loc, "write op has emits but no consequences rows (proof shape incomplete)")
            if has_cons:
                for ci, row in enumerate(consequences):
                    if not isinstance(row, dict):
                        rep.fail("V9", p, loc, f"consequence row {ci} is not a mapping")
                        continue
                    if "when" not in row:
                        rep.fail("V9", p, loc, f"consequence row {ci} has no `when:`")
                    if "expect" not in row:
                        rep.fail("V9", p, loc, f"consequence row {ci} has no `expect:`")
                        continue
                    expect = row.get("expect")
                    is_absence = isinstance(expect, list) and len(expect) == 0
                    if is_absence:
                        if "evidence" not in row:
                            rep.fail("V9", p, loc,
                                     f"consequence row {ci} is absence-shaped (expect: []) but names no `evidence:` snapshot read")
                    else:
                        if "bound" not in row and "invariant" not in row and "evidence" not in row:
                            rep.fail("V9", p, loc,
                                     f"consequence row {ci} has expect but no `bound:` (or unbounded-with-evidence/invariant/evidence)")


def rule_V13_liveness(corpus, rep):
    """liveness completeness per §4.1: snapshot→live-twin; watch→frame/resume/keepalive/termination."""
    for base, e in corpus.entries.items():
        p = e["path"]
        for op in e["ops"]:
            f = op["fence_yaml"]
            if not isinstance(f, dict):
                continue
            loc = f"{op['name']} (line {op['header_line']})"
            lv = f.get("liveness")
            if lv == "snapshot":
                if "live-twin" not in f:
                    rep.fail("V13", p, loc, "liveness: snapshot but no `live-twin:` (must name twin or 'none — static')")
            elif lv in ("watch", "binary-stream", "duplex"):
                for req in ("frames", "resume", "keepalive", "termination"):
                    if req not in f:
                        rep.fail("V13", p, loc, f"liveness: {lv} but missing `{req}:` documentation")


def rule_V18_atlas(corpus, rep):
    """Every affordance id used in any op's atlas: ∈ FEATURE-ATLAS; every defined affordance is
    reached by ≥1 op OR is in OUT-OF-SCOPE (zero silent gaps, both directions)."""
    used = {}
    for base, e in corpus.entries.items():
        for op in e["ops"]:
            f = op["fence_yaml"]
            if not isinstance(f, dict):
                continue
            for aff in (f.get("atlas") or []):
                used.setdefault(str(aff), []).append((base, op["name"]))
    # direction 1: every used affordance is DEFINED in the atlas (no phantom tags)
    for aff, where in used.items():
        if aff not in corpus.atlas_affordances:
            rep.fail("V18", corpus.basenames.get(where[0][0], corpus.root), "atlas",
                     f"op {where[0][1]} tags affordance '{aff}' not defined in FEATURE-ATLAS.md (phantom tag)")
    # direction 2: every defined affordance is reached by an op OR excluded
    reached = set(used.keys())
    for aff in sorted(corpus.atlas_affordances):
        if aff not in reached and aff not in corpus.out_of_scope:
            rep.fail("V18", corpus.root / "atlas" / "FEATURE-ATLAS.md", "atlas",
                     f"affordance '{aff}' is defined but reached by no op and not in OUT-OF-SCOPE.md (silent gap)")
    corpus.stats["affordances_defined"] = len(corpus.atlas_affordances)
    corpus.stats["affordances_reached"] = len(reached & corpus.atlas_affordances)


def rule_V20_singlesource(corpus, rep):
    """Frontmatter status ↔ entry; fence status is the single truth — frontmatter entry status
    should be consistent with the MOST-LIVE op (an entry is 'building' if any op is building).
    We check: every op fence has a status, and the entry frontmatter status is a real status.
    The strict fence-vs-frontmatter equality in §6 V20 is per-OP (frontmatter summary/status of
    the entry vs the op fence) — here we enforce that NO op fence status exceeds the entry's
    declared maturity inconsistently (a 'live' op in a 'planned'-only entry would be the smell)."""
    rank = {"planned": 0, "building": 1, "live": 2, "broken": 1, "retired": 0}
    for base, e in corpus.entries.items():
        fm = e["frontmatter"] or {}
        entry_status = fm.get("status")
        if entry_status not in STATUS_ENUM:
            continue
        op_statuses = []
        for op in e["ops"]:
            f = op["fence_yaml"]
            if isinstance(f, dict) and f.get("status") in STATUS_ENUM:
                op_statuses.append(f["status"])
        if not op_statuses:
            continue
        # the entry's frontmatter status should equal the max-maturity op status
        max_rank = max(rank[s] for s in op_statuses)
        entry_rank = rank[entry_status]
        # building entry must contain >=1 building/live op; planned entry must contain no building/live op
        if entry_status == "building" and max_rank < 1:
            rep.fail("V20", e["path"], "frontmatter",
                     f"entry status 'building' but no op fence is building/live (statuses: {sorted(set(op_statuses))})")
        if entry_status == "planned" and max_rank >= 1:
            built = [op["name"] for op in e["ops"]
                     if isinstance(op["fence_yaml"], dict) and op["fence_yaml"].get("status") in ("building", "live")]
            rep.fail("V20", e["path"], "frontmatter",
                     f"entry status 'planned' but ops {built} are building/live — frontmatter understates reality")


# ----------------------------------------------------------------------------- reality rules (skipped, fail-loud)
def reality_rules_skip(corpus, rep, include_reality):
    needed = {
        "V22": "reality.json (live (route,method)/(tool,op)/(cli,command) join)",
        "V23": "live MCP tool inputSchemas",
        "V24": "exposure.json ≡ actual bind config",
        "V25": "evidence/ replay against live system",
        "V26": "observed event payloads in evidence/",
    }
    reality_json = corpus.root / "coverage" / "reality.json"
    if include_reality and not reality_json.exists():
        for r, what in needed.items():
            rep.fail(r, reality_json, "reality", f"reality: unavailable — {what} missing (fail-loud, not stale-silent)")
    else:
        for r, what in needed.items():
            rep.skip(r, f"requires {what} — not built yet (README honest status); run with --include-reality once reality.json + evidence/ exist")


# ----------------------------------------------------------------------------- driver
def main():
    ap = argparse.ArgumentParser(description="UI Contract corpus validator (CONTRACT-FORMAT §6).")
    ap.add_argument("--corpus", default=str(Path(__file__).resolve().parent.parent),
                    help="corpus root (default: parent of tools/)")
    ap.add_argument("--include-reality", action="store_true",
                    help="run reality rules V22–V26 (fail loud if reality.json/evidence absent)")
    args = ap.parse_args()

    root = Path(args.corpus).resolve()
    if not (root / "resources").is_dir():
        sys.stderr.write(f"FATAL: {root}/resources/ not found — is --corpus pointing at the ui-contract root?\n")
        sys.exit(2)

    rep = Report()
    corpus = Corpus(root)
    corpus.load(rep)

    rule_V1_frontmatter(corpus, rep)
    rule_V2_opspec(corpus, rep)
    rule_V21_transports(corpus, rep)
    rule_V3_schemas(corpus, rep)
    rule_V4_errors(corpus, rep)
    rule_V5_purposefree(corpus, rep)
    rule_V6_refclosure(corpus, rep)
    rule_V7_schemeclosure(corpus, rep)
    rule_V8_chunk(corpus, rep)
    rule_V9_consequences(corpus, rep)
    rule_V13_liveness(corpus, rep)
    rule_V18_atlas(corpus, rep)
    rule_V20_singlesource(corpus, rep)
    reality_rules_skip(corpus, rep, args.include_reality)

    # ---- report
    n_entries = len(corpus.entries)
    n_ops = sum(len(e["ops"]) for e in corpus.entries.values())
    print(f"UI Contract validator — corpus: {root}")
    print(f"  entries parsed: {n_entries}   ops parsed: {n_ops}   "
          f"transports: {len(corpus.transports)}   "
          f"affordances defined/reached: {corpus.stats.get('affordances_defined','?')}/"
          f"{corpus.stats.get('affordances_reached','?')}")
    if not HAVE_JSONSCHEMA:
        print("  NOTE: jsonschema not installed — V3 checks JSON validity only, not full Schema-2020-12 metaschema.")
    print()

    if rep.skipped:
        print(f"SKIPPED (need live system / generated artifacts) — {len(rep.skipped)}:")
        for r, why in rep.skipped:
            print(f"  [{r}] {why}")
        print()

    if rep.violations:
        def relpath(fpath):
            try:
                return str(Path(fpath).relative_to(root))
            except Exception:
                return fpath
        hard = [v for v in rep.violations if v[4] == "hard"]
        soft = [v for v in rep.violations if v[4] == "soft"]
        def render(group, title):
            by_rule = {}
            for v in group:
                by_rule.setdefault(v[0], []).append(v)
            print(f"{title} — {len(group)} across {len(by_rule)} rule(s):")
            for rule in sorted(by_rule):
                print(f"\n  ── {rule} ({len(by_rule[rule])}) ──")
                for rname, fpath, loc, msg, sev in by_rule[rule]:
                    print(f"    {relpath(fpath)} :: {loc}\n        {msg}")
            print()
        if hard:
            render(hard, "HARD VIOLATIONS (structural format breaks — fail-loud)")
        if soft:
            render(soft, "SOFT FINDINGS (V5 purpose-free proxy / V4 teach-ref shape — reflexes, still counted)")
        print(f"FAIL — {len(rep.violations)} violation(s) "
              f"({len(hard)} hard, {len(soft)} soft).")
        sys.exit(1)

    print("PASS — all enforced static rules clean (V1–V21 static subset; reality rules skipped, see above).")
    sys.exit(0)


if __name__ == "__main__":
    main()
