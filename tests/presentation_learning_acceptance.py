"""tests/presentation_learning_acceptance.py — F1 · the presentation-feedback LEARNING LOOP.

WHAT THE LEARNING LOOP IS (Tim's key F1 expansion, made operable):
F1's altitude layer presents the system's reality at Tim's level. His expansion: he must be able to
SHAPE how it presents to him FROM INSIDE the system ("show me this differently / more / less / lead with
X"), by voice OR typing, and it must ADAPT + REMEMBER — "how it presents to him is LEARNED." That is THIS
loop: a presentation-preference STORE + an ADAPT step that the up-translate organs consult.

IT REUSES, NEVER REBUILDS (rule 3, one-source):
  • the addressed-feedback substrate — a pref is "a comment at an address" with a presentation intent, so
    it rides the EXISTING `annotations.jsonl` store leaf with one additive structured marker
    (`kind:"presentation_pref"`). NO parallel store. It rides the PURE annotate leaf-shape (the S0-gate +
    fail-loud guards), NOT `ingest_comment` — a pref is a control signal, not twin gold-training data.
  • R2 resolve-at-locus — gathered as its OWN distinct `presentation_pref` stratum (pin-persistent, like
    the howto leg) so a learned pref rides the SAME machinery as everything else.
  • the up-translate organs (up_translate / coa / address_help) CONSULT + APPLY it (the adapt step).
The NET-NEW is ONLY the pref store + the adapt step.

WHAT THIS PROVES (by USE — real Suite + temp FsStore + real discovered nodes + real corpus, NO live model):
  A. CAPTURE — set_presentation_pref records a structured pref at an address (the annotate-branch of the
     addressed-feedback channel) WITHOUT writing twin gold (the I6 SEPARATION spirit preserved).
  B. PERSIST + RELOAD-SURVIVAL — a FRESH Suite over the SAME store root READS the learned pref (the loop's
     "remembers" — proven across an actual reload, not just in-process).
  C. ADAPT (address, MODEL-FREE) — address_help + up_translate('address') for that address CONSULT the
     pref and the envelope REFLECTS it (presentation_pref attached; lead_with REORDERS the lead — a
     deterministic, SEE-able re-shape). The MECHANISM is proven model-free.
  D. ADAPT (decision, model-free MECHANISM) — coa threads the pref directive INTO the framing prompt (the
     `_complete` injection seam receives the directive in its prompt args). The wording the model emits
     honoring it is the model-dependent half (flagged); the mechanism is proven model-free.
  E. NO PREF = CLEAN DEFAULT — an address with no pref gives the byte-for-byte default framing (no error,
     no fabricated pref).
  F. FAIL LOUD — THREE distinct guards: a malformed ADDRESS raises; EMPTY pref/missing-arg raises; a
     MALFORMED pref kind raises; a STORED junk pref raises on the consult-read.
  G. R2 RIDE — the learned pref resolves into the locus context as its OWN distinct stratum (rides
     resolve-at-locus) and is NOT double-counted as a comment.

MODEL-DEPENDENT (flagged): the WORDING the model actually emits when honoring the pref (coa's framing
text). Everything STRUCTURAL — capture, persist, reload, consult, the pref reaching the envelope/prompt,
the lead reorder, the fail-loud guards, the R2 ride — is proven model-free.

COMPANY_TEST_RUN is set for inbox-hygiene parity with the sibling suites.
"""
import os, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ["COMPANY_TEST_RUN"] = "1"

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite, CoaFraming, CoaOption

NODES = os.path.join(ROOT, "nodes")
PASS = 0


def check(label, cond):
    global PASS
    if cond:
        PASS += 1
        print(f"  PASS  {label}")
    else:
        print(f"  FAIL  {label}")
        raise SystemExit(1)


def suite_at(root):
    reg = NodeRegistry()
    reg.discover([NODES])
    return Suite(FsStore(root), reg)


# Real corpus fixtures (READ from the corpus, never hardcoded prose).
RICH = "ui://toolbar/run"            # registered, all 3 legs authored (rich howto + real code scope)
MALFORMED = "not-a-ui-address"       # violates the S0 grammar → raises
UNSHAPED = "ui://toolbar/presence"   # registered, but NO pref recorded → the clean default

# ONE store root shared across two Suites — to PROVE reload-survival (B).
ROOT_DIR = tempfile.mkdtemp(prefix="preslearn-")

print("F1 · the presentation-feedback LEARNING LOOP (capture → persist → reload → consult → adapt)")
su = suite_at(ROOT_DIR)


def canned(sys_p, user, model, base_url):
    # The model-free injection seam: capture the prompt args so D can assert the directive REACHED them.
    canned.last_user = user
    return CoaFraming(meaning="m.", options=[CoaOption(label="A", tradeoff="t1"),
                                             CoaOption(label="B", tradeoff="t2")], recommendation="Pick A.")
canned.last_user = None


# ── A · CAPTURE — record a structured pref at an address (the annotate-branch, no twin gold) ─────────
chat_before = len(su.store.chat_history(limit=999))
rec = su.set_presentation_pref(RICH, {"kind": "terser"})
check("A1: CAPTURE — set_presentation_pref returns a record marked kind=presentation_pref",
      rec.get("kind") == "presentation_pref")
check("A2: CAPTURE — the structured pref is stored (kind=terser, normalized arg=None)",
      rec.get("pref") == {"kind": "terser", "arg": None})
check("A3: CAPTURE — it rides the SAME annotations leaf (retrievable in the address's annotation thread)",
      any(a.get("kind") == "presentation_pref" for a in su.store.annotations_for(RICH)))
check("A4: CAPTURE — it does NOT write twin gold (no chat turn emitted — the I6 SEPARATION spirit)",
      len(su.store.chat_history(limit=999)) == chat_before)
# the pure-annotate sibling is UNTOUCHED — a bare annotate still writes NO chat (annotation_acceptance holds).
ch2 = len(su.store.chat_history(limit=999))
su.annotate(RICH, "a normal comment")
check("A5: PRESERVE — annotate()'s contract is intact (a bare annotate writes no chat)",
      len(su.store.chat_history(limit=999)) == ch2)

# ── B · PERSIST + RELOAD-SURVIVAL — a FRESH Suite over the same store reads the learned pref ─────────
su2 = suite_at(ROOT_DIR)                                  # a fresh brain, same store root
active = su2.presentation_pref_at(RICH)
check("B1: RELOAD-SURVIVAL — a FRESH Suite reads Tim's learned pref (it REMEMBERS across a reload)",
      active == {"kind": "terser", "arg": None})

# latest-wins: a second shaping overrides the first (the consult takes the most-recent).
su2.set_presentation_pref(RICH, {"kind": "lead_with", "arg": "how_to_change"})
check("B2: LATEST-WINS — the consult returns the MOST-RECENT shaping (remembers the current preference)",
      su2.presentation_pref_at(RICH) == {"kind": "lead_with", "arg": "how_to_change"})
# and THAT survives another reload too.
su3 = suite_at(ROOT_DIR)
check("B3: RELOAD-SURVIVAL (2) — the re-shaping also survives a fresh Suite",
      su3.presentation_pref_at(RICH) == {"kind": "lead_with", "arg": "how_to_change"})

# ── C · ADAPT (address, MODEL-FREE) — address_help + up_translate consult + reflect the pref ─────────
b = su3.address_help(RICH)
check("C1: ADAPT/address_help — the consulted pref reaches the bundle (presentation_pref attached)",
      b.get("presentation_pref") == {"kind": "lead_with", "arg": "how_to_change"})
check("C2: ADAPT/address_help — a presentation_directive (single-source human form) is carried",
      isinstance(b.get("presentation_directive"), str) and "Lead with" in b["presentation_directive"])
env = su3.up_translate("address", RICH)
check("C3: ADAPT/up_translate — the F1 envelope reflects the pref (presentation_pref surfaced)",
      env.get("presentation_pref") == {"kind": "lead_with", "arg": "how_to_change"})
check("C4: ADAPT/up_translate — lead_with:how_to_change REORDERS the lead (a SEE-able model-free re-shape)",
      env.get("led_with") == "how_to_change" and env.get("lead", "").startswith("[changes:"))
# the UN-adapted ground is preserved: the mechanism (how-to-change) still carries the real scope.
check("C5: PRESERVE — the drillable MECHANISM (how-to-change scope) is intact under the adapt",
      isinstance(env.get("mechanism"), dict) and bool(env["mechanism"].get("scope")))

# ── D · ADAPT (decision) — coa threads the pref directive INTO the framing prompt (mechanism model-free) ─
# a surfaced decision minted AT the shaped address carries it in its payload → coa consults the pref there.
sid = su3.inbox.surface("register_type",
                        {"name": "wc", "code": "def run(): ...", "address": RICH}, default="reject")
c = su3.coa(sid, _complete=canned)
check("D1: ADAPT/coa — the pref directive REACHED the framing prompt (model-free: in the injected args)",
      canned.last_user is not None and "PRESENTATION PREFERENCE" in canned.last_user
      and "Lead with" in canned.last_user)
check("D2: ADAPT/coa — the consulted pref is surfaced on the coa return", c.get("presentation_pref") ==
      {"kind": "lead_with", "arg": "how_to_change"})
check("D3: PRESERVE — coa still frames (grounded) + keeps the raw drillable under the adapt",
      c.get("grounded") is True and isinstance(c.get("raw"), dict))

# ── E · NO PREF = CLEAN DEFAULT (no error, no fabrication) ───────────────────────────────────────────
check("E1: DEFAULT — an address with NO pref consults to None (a clean absence, not an error)",
      su3.presentation_pref_at(UNSHAPED) is None)
b0 = su3.address_help(UNSHAPED)
check("E2: DEFAULT — address_help with no pref carries NO presentation_pref/directive (the default framing)",
      "presentation_pref" not in b0 and "presentation_directive" not in b0)
env0 = su3.up_translate("address", UNSHAPED)
check("E3: DEFAULT — up_translate with no pref is the un-adapted envelope (no fabricated pref)",
      "presentation_pref" not in env0 and "led_with" not in env0 and isinstance(env0.get("lead"), str))
# a decision whose address has no pref → the coa prompt is the default (no directive threaded).
sid0 = su3.inbox.surface("register_type", {"name": "x", "code": "...", "address": UNSHAPED}, default="reject")
canned.last_user = None
c0 = su3.coa(sid0, _complete=canned)
check("E4: DEFAULT — coa with no pref threads NO directive (byte-for-byte the default prompt)",
      "PRESENTATION PREFERENCE" not in (canned.last_user or "") and "presentation_pref" not in c0)
# a decision with NO address at all → no consult attempted, clean default.
sid_na = su3.inbox.surface("register_type", {"name": "y", "code": "..."}, default="reject")
canned.last_user = None
su3.coa(sid_na, _complete=canned)
check("E5: DEFAULT — a decision with no address skips the consult entirely (no directive, no error)",
      "PRESENTATION PREFERENCE" not in (canned.last_user or ""))

# ── F · FAIL LOUD — three DISTINCT guards (address / pref-shape / stored junk) ───────────────────────
def raises(fn, exc=Exception):
    try:
        fn(); return False
    except exc:
        return True

check("F1: FAIL-LOUD — a MALFORMED address raises (S0 grammar gate) on capture",
      raises(lambda: su3.set_presentation_pref(MALFORMED, {"kind": "terser"}), (ValueError, TypeError)))
check("F2: FAIL-LOUD — a MALFORMED address raises on the consult-read too",
      raises(lambda: su3.presentation_pref_at(MALFORMED), (ValueError, TypeError)))
check("F3: FAIL-LOUD — an UNKNOWN pref kind raises (rule 8 — never silently accept/ignore)",
      raises(lambda: su3.set_presentation_pref(RICH, {"kind": "make-it-pretty"}), ValueError))
check("F4: FAIL-LOUD — an arg-taking pref with NO arg raises (lead_with needs a target)",
      raises(lambda: su3.set_presentation_pref(RICH, {"kind": "lead_with"}), ValueError))
check("F5: FAIL-LOUD — a non-dict pref raises", raises(lambda: su3.set_presentation_pref(RICH, "terser"), ValueError))
# a STORED junk pref (corruption / a record written outside the guard) must RAISE on read, never degrade
# silently to 'no pref' (which the operator would misread as 'it forgot').
su3.store.append_annotation({"kind": "presentation_pref", "address": UNSHAPED,
                             "pref": {"kind": "bogus-kind"}, "text": "junk", "source": "operator"})
check("F6: FAIL-LOUD — a STORED junk pref RAISES on the consult-read (no silent degrade-to-default)",
      raises(lambda: su3.presentation_pref_at(UNSHAPED), ValueError))

# ── G · R2 RIDE — the learned pref resolves into the locus context as its OWN distinct stratum ───────
# a fresh store so the R2 gather is clean; set a pref + a normal comment at the SAME locus.
g_root = tempfile.mkdtemp(prefix="preslearn-r2-")
g = suite_at(g_root)
g.set_presentation_pref(RICH, {"kind": "more"})
g.annotate(RICH, "a normal operator comment here")
gathered = g._r2_gather(RICH)
pref_items = [it for it in gathered if it.get("kind") == "presentation_pref"]
comment_items = [it for it in gathered if it.get("kind") == "annotation"]
check("G1: R2 — the learned pref rides resolve-at-locus as its OWN distinct stratum",
      len(pref_items) == 1 and "presentation pref" in pref_items[0]["text"].lower())
check("G2: R2 — the pref is pin-persistent (rides the R2_PIN_WEIGHT bonus, doesn't decay out)",
      pref_items[0].get("pinned") is True)
check("G3: R2 — the normal comment is STILL gathered (the pref skip didn't drop real comments)",
      len(comment_items) == 1 and "normal operator comment" in comment_items[0]["text"])
check("G4: R2 — the pref is NOT double-counted as a comment (distinct kind, no comment row for it)",
      not any("presentation pref" in (it.get("text", "").lower()) for it in comment_items))
# G5 — the AMBIENT/EXPLICIT split (the defect-class the consult-raise created): a STORED junk pref at the
# locus must NOT collapse the per-turn gather. The explicit consult RAISES (F6), but the ambient _r2_gather
# (every chat turn) must catch+warn+skip the pref leg and STILL return the other strata. Inject a junk pref
# at the SAME locus as a real comment, gather, and assert: no raise, the real comment survives, no pref row.
gj_root = tempfile.mkdtemp(prefix="preslearn-r2junk-")
gj = suite_at(gj_root)
gj.annotate(RICH, "a real comment that must survive a junk pref")
gj.store.append_annotation({"kind": "presentation_pref", "address": RICH,
                            "pref": {"kind": "not-a-real-kind"}, "text": "junk", "source": "operator"})
gj_raised = False
try:
    gj_gathered = gj._r2_gather(RICH)
except Exception:
    gj_raised = True
check("G5a: R2-AMBIENT — a stored JUNK pref does NOT crash the per-turn gather (ambient catch+skip)",
      not gj_raised)
check("G5b: R2-AMBIENT — the junk pref is SKIPPED (no presentation_pref stratum emitted from junk)",
      not any(it.get("kind") == "presentation_pref" for it in gj_gathered))
check("G5c: R2-AMBIENT — the OTHER strata survive (the real comment is still gathered — not nuked to [])",
      any(it.get("kind") == "annotation" and "must survive" in it.get("text", "") for it in gj_gathered))
# and the EXPLICIT consult on that SAME junk-pref address still RAISES (the posture split is real).
check("G5d: SPLIT — the EXPLICIT consult on the junk-pref address STILL raises (ambient skips, consult fails loud)",
      raises(lambda: gj.presentation_pref_at(RICH), ValueError))

print(f"\n{PASS} checks PASSED — the F1 presentation-feedback LEARNING LOOP proven by use: capture → "
      "persist → RELOAD-SURVIVAL → consult → adapt (address model-free; decision-prompt model-free) → "
      "clean default → 3 distinct fail-loud guards → R2 ride. MODEL-DEPENDENT (flagged): the WORDING the "
      "model emits honoring the pref.")
