"""runtime/territory.py — territory_for(address): the address→territory composer (fork, ch-8djrpmsl).

The brain-agnostic context composer for the loadable-brain / drill→talk first slice. Given ANY
contracts.address (the projection:select handle — run://·code://·board://·ui://…), compose the TERRITORY
at that address (identity + context + relations) into a structured dict, and render it to the
`[Operator context]` prose block a Claude Code brain turn folds in (bridge._claude_stream / run_turn).

DESIGN: build-prep/front-interface/TERRITORY_FOR_DESIGN.md (advisor-hardened). Greenlit for LANE B
(first slice, 2026-06-16) — render NOW on the default brain.

LAWS:
  • BRAIN-AGNOSTIC (D2): composes the territory; the scale/rung decides FOCUS vs PANEL at handoff, not here.
  • REUSE-DON'T-PARALLEL: COMPOSES the existing resolvers — cognition.resolve_address (9 schemes),
    suite.address_help/context_at/chats_at (ui://), cc_board.relations (H1.2 graph) — never a parallel resolver.
  • GPU-FREE: every leg is a registry / structural read; nothing embeds (no :8007).
  • DEGRADE CONTRACT (advisor-hardened, the part that makes it behave like the wire it replaces):
      every leg is INDEPENDENTLY guarded → a dead leg becomes a noted-absent leg, not a void territory
      (mirrors suite.address_help's per-leg guard). The THREE failure cases:
        (1) non-address (no '://')          → territory_for RAISES (fail-loud-legible; good for the lib + tests)
        (2) non-resolvable scheme (vec://…) → identity noted-absent; relations still tried
        (3) nonexistent record (session://bogus, stale board://) → resolve_address RAISES → identity guard
            catches it → noted-absent (NOT a propagated crash — this is the regression-guard)
      `territory_prose` (the bridge-facing path) NEVER raises — an outer guard degrades even case (1) to a
      note, preserving _claude_stream's "context-gathering never kills the turn" contract.
  • LENS-INDEPENDENCE (FACE reconcile, 2026-06-16): the STRUCTURAL board-edge relations leg here is
    lens-independent (fine for the core slice); the lens-union / surfaced-neighbour-units enrichment waits
    on projection's multi-embedding answer — a FAST-FOLLOW, not wired here.
"""
from __future__ import annotations

import os

# The memory leg (recall_for_decision) reaches the embed service via query_corpus — a DOWN/SLOW embed would HANG
# the whole decision resolve (a HANG ≠ an exception; the per-leg try/except catches exceptions, not hangs). So
# the leg is BOUNDED by this hard timeout (env-overridable); on timeout it degrades clean — the decision still
# resolves to row+state+options (the card renders + is decidable), only the recall-grounding is absent. Live
# regression 2026-06-18: EVERY external-dependency leg needs a TIMEOUT, not just a guard.
_MEMORY_LEG_TIMEOUT_S = float(os.environ.get("COMPANY_MEMORY_LEG_TIMEOUT_S", "3.0"))

# Schemes cognition.resolve_address resolves to a record/content (its dispatch, cognition.py:842-1029).
# vi-vision added 2026-06-17 (islands-join-mainland): the identity leg resolves the AIMED factory asset via
# resolve_address → resolve_vi_vision (degrades clean if no transport; the LIBRARY leg adds the palette).
# decision added 2026-06-18 (decision-surface): the identity leg resolves the AIMED decision (row + composed
# state) via resolve_address → decision_registry + compose_state; territory_prose renders it humanly below.
_RESOLVABLE = ("run", "cas", "skill", "context", "session", "cap", "board", "clone", "mind", "vi-vision", "decision")


def _scheme_of(address: str):
    from contracts.address import scheme
    return scheme(address)


# ── VIEW grounding (the instrument SURFACE aim → the ACTIVE projection view's self-description) ────────
# ui://instrument/surface carries NO registered ui:// identity, but the meaning the OPERATOR sees on the
# surface is the ACTIVE projection view's meta — bindings/<id>.py `meta` {name,is,fills,why}. So the RHM
# grounds the surface aim on that registry meta (the SAME self-description the surface renders), instead of
# punting "thin pointer" (projection's stranger-Ask gap, fork's lane, 2026-06-18). registry-is-truth: read
# bindings/, never hardcode the copy. The active view rides the aim fragment (#binding=<id>, projection passes
# it — the surface knows which view is live); default 'raw' = "What's happening…" (the fallback, bridge.py:879).
def _instrument_view_binding(address):
    """If `address` is the instrument SURFACE aim (ui://instrument/surface[#binding=<id>]) → the active binding
    id (from the #binding= fragment; default 'raw'). Else None."""
    if not isinstance(address, str):
        return None
    if address.split("#", 1)[0].rstrip("/") != "ui://instrument/surface":
        return None
    binding = "raw"
    if "#" in address:
        for part in address.split("#", 1)[1].replace("&", ";").split(";"):
            if part.startswith("binding="):
                binding = part[len("binding="):].strip() or "raw"
    return binding


def _binding_meta(binding_id):
    """The projection view's legibility meta {name,is,fills,why} from bindings/<id>.py (the SAME self-description
    the surface renders). None if absent/malformed/path-unsafe — degrade-clean, never raises."""
    try:
        import importlib.util
        import os
        if not isinstance(binding_id, str) or not binding_id or "/" in binding_id or ".." in binding_id:
            return None
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(root, "bindings", f"{binding_id}.py")
        if not os.path.isfile(path):
            return None
        spec = importlib.util.spec_from_file_location(f"_binding_{binding_id}", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        b = getattr(mod, "BINDING", None)
        m = b.get("meta") if isinstance(b, dict) else None
        return m if isinstance(m, dict) and m.get("name") else None
    except Exception:
        return None


def territory_for(address, *, suite=None, store=None, max_relations: int = 20) -> dict:
    """Compose the territory at `address` → a structured, brain-agnostic dict:
      {address, scheme, identity, identity_kind, context_items, chats, relations, notes, legs_present}

    Per-leg guarded (a dead leg → a noted-absent leg, never a void territory). RAISES only on a genuine
    non-address (no '://'). `suite` supplies ui:// legs + the store; `store` (or suite.store) drives
    resolve_address + cc_board.relations. Either handle from projection:select works:
    territory_for(detail.address) OR territory_for(detail.record) (the run:// wrapper — resolvable today).
    """
    if not isinstance(address, str) or "://" not in address:
        raise ValueError(
            f"territory_for: {address!r} is not an address (needs '<scheme>://…', a contracts.address). "
            f"Bare names / None are not territories — fail loud.")
    if store is None and suite is not None:
        store = getattr(suite, "store", None)
    try:
        sch = _scheme_of(address)
    except Exception:
        sch = None

    terr: dict = {"address": address, "scheme": sch, "identity": None, "identity_kind": None,
                  "context_items": [], "chats": [], "relations": None, "notes": [], "legs_present": {}}

    # ── IDENTITY leg (per-scheme strategy; each in its own guard) ──
    try:
        if sch == "ui":
            if suite is not None:
                terr["identity"] = suite.address_help(address)
                terr["identity_kind"] = "ui.affordance_bundle"
            else:
                terr["notes"].append("ui:// identity needs a suite (address_help) — none supplied")
        elif sch in _RESOLVABLE:
            # ALWAYS call resolve_address inside the guard: store-INDEPENDENT schemes (skill/context/cap/
            # board/clone/mind — registry reads) resolve even when store=None; store-DEPENDENT schemes
            # (run/cas/session) raise here when store is missing/None → the guard catches it → noted-absent.
            from runtime.cognition import resolve_address
            terr["identity"] = resolve_address(store, address)
            terr["identity_kind"] = f"{sch}.record"
        else:
            # code://·blob://·vec://·exchange://·file://·project:// — no content-resolver wired here yet.
            # code:// scope/blast-radius leg = the FAST-FOLLOW refinement (needs resolve_scope-takes-code:// check).
            terr["notes"].append(
                f"{sch}:// has no content-resolver in territory_for yet — identity degrade-clean (absent)")
    except Exception as e:
        # Case (3): a well-formed resolvable scheme pointing at a NONEXISTENT record raises here → noted-absent.
        terr["notes"].append(f"identity leg unresolved ({type(e).__name__}: {e})")
        terr["identity"] = None

    # ── VIEW leg: the instrument SURFACE aim → OVERRIDE the thin ui:// identity with the ACTIVE projection
    # view's meta (bindings/ registry), so the RHM grounds on the real on-screen view meaning, not "(unregistered)".
    _vb = _instrument_view_binding(address)
    if _vb is not None:
        _vmeta = _binding_meta(_vb)
        if _vmeta is not None:
            terr["identity"] = _vmeta
            terr["identity_kind"] = "view.meta"
            terr["view_binding"] = _vb
            terr["notes"] = [n for n in terr["notes"] if "unregistered" not in n and "needs a suite" not in n]
    terr["legs_present"]["identity"] = terr["identity"] is not None

    # ── CORPUS-RECORD leg (the comprehended/embedded record AT this address — what DNA's renderGallery
    # actually renders, via /api/cognition/corpus?address= → SUITE.read_corpus_record, keyed by
    # source_address). This is how a gallery unit resolves to real content even when resolve_address has no
    # branch for its scheme (e.g. code://<path> corpus points — projection:select's dominant detail.source).
    # Promotes to identity when resolve_address gave nothing (the code:// degrade → the real corpus record).
    if suite is not None and hasattr(suite, "read_corpus_record"):
        try:
            cr = suite.read_corpus_record(address)        # keyed by the record's `address` (the run:// wrapper)
            if not cr and hasattr(suite, "find_corpus"):
                # a code:// SOURCE address (projection:select's detail.source) is the record's `source_address`,
                # NOT its `address` key — read_corpus_record misses it. find_corpus(source_address=…) resolves it.
                # (Verified live: corpus records are keyed by run://corpus/…/common_knowledge with code:// as
                # source_address; find_corpus(source_address=code://…) → the record.)
                hits = suite.find_corpus(source_address=address) or []
                cr = hits[0] if hits else None
            if cr:
                terr["corpus_record"] = cr
                # the record is METADATA + a cas:// content pointer (no inline text) — dereference the cas
                # so the brain gets the actual comprehended CONTENT, not just {seq,ts,address,source_address}.
                cas = cr.get("cas") if isinstance(cr, dict) else None
                if cas and store is not None:
                    try:
                        from runtime.cognition import resolve_address as _ra
                        terr["corpus_content"] = _ra(store, cas)
                    except Exception as e:
                        terr["notes"].append(f"corpus content (cas) unresolved ({type(e).__name__}: {e})")
                if terr["identity"] is None:
                    terr["identity"] = terr.get("corpus_content") or cr   # prefer the content; else the record
                    terr["identity_kind"] = "corpus.content" if terr.get("corpus_content") else "corpus.record"
                    # drop the now-superseded "no content-resolver" note (the corpus content/record IS it)
                    terr["notes"] = [n for n in terr["notes"] if "no content-resolver" not in n]
        except Exception as e:
            terr["notes"].append(f"corpus_record leg unresolved ({type(e).__name__}: {e})")
    terr["legs_present"]["corpus_record"] = bool(terr.get("corpus_record"))

    # ── CONTEXT leg (ui:// only — scored R2 items + chats at the locus; guarded) ──
    if sch == "ui" and suite is not None:
        try:
            terr["context_items"] = (suite.context_at(address) or {}).get("items", [])
        except Exception as e:
            terr["notes"].append(f"context_at leg unresolved ({type(e).__name__}: {e})")
        try:
            terr["chats"] = suite.chats_at(address) or []
        except Exception as e:
            terr["notes"].append(f"chats_at leg unresolved ({type(e).__name__}: {e})")
    terr["legs_present"]["context"] = bool(terr["context_items"] or terr["chats"])

    # ── RELATIONS leg (H1.2 typed-edge graph, ANY scheme; structural, store-optional; guarded) ──
    try:
        from runtime import cc_board
        rel = cc_board.relations(address, direction="both", store=store)
        for k in ("edges_in", "edges_out"):
            if isinstance(rel.get(k), list) and len(rel[k]) > max_relations:
                rel[k] = rel[k][:max_relations]
                rel[f"{k}_truncated"] = True
        terr["relations"] = rel
    except Exception as e:
        terr["notes"].append(f"relations leg unresolved ({type(e).__name__}: {e})")
    terr["legs_present"]["relations"] = terr["relations"] is not None

    # ── LIBRARY leg (vi-vision:// only — the compose-PALETTE for the credential-free brain, 2026-06-17) ──
    # islands-join-mainland read-model (A): the brain holds NO factory cred; the BRIDGE (where territory_for
    # runs for context-composition) enriches the brain's context with the global library PALETTE so it can
    # describe a valid composition from real pieces (→ operator build-this → the gated write). Reuses
    # composition's read-only vi_vision_catalog (runs in-bridge, anon; NEVER the brain). Capped to a SUMMARY
    # (not the whole registry dumped into context). Guarded → degrade-clean (a dead catalog never kills the turn).
    if sch == "vi-vision":
        try:
            from runtime.vi_vision import vi_vision_catalog
            rows = vi_vision_catalog("global") or []     # always 'global' = the compose-palette (anon scope)
            cap = 25
            terr["library"] = {"items": rows[:cap], "total": len(rows), "capped": len(rows) > cap}
        except Exception as e:
            terr["notes"].append(f"library leg unresolved ({type(e).__name__}: {e})")
    terr["legs_present"]["library"] = bool(terr.get("library"))

    # ── MEMORY leg (decision:// → the RHM's explanation grounding; guarded → degrade-clean, 2026-06-18) ──
    # unify-to-ONE step-1 (the lead's independent early win): the orphaned recall_for_decision is now WIRED —
    # a decision's explanation RESOLVES through recall, not stored (resolution-first). recall_for_decision
    # composes the corpus-grounded bundle (multi-space query + jina rerank + prior-decisions + neighbours) the
    # RHM explains FROM. KEYED on decision:// so the HEAVY bundle fires only when a decision is explained, NOT
    # every turn. Needs the suite (query_corpus/rerank); GUARDED → a down embedder/space degrades clean (the
    # never-raises contract holds — never kills the explain turn). recollection owns recall_for_decision; this
    # is the territory_prose path (auto-grounds every decision:// resolve), projection's optional route serves
    # the same compute (no conflict). ANCHOR = the decision's `meaning` (confirmed: decision://'s resolved
    # identity IS the row {id,meaning,options,...}+state). SUBJECT (neighbours) = a code:// the decision
    # decides-on (the schema's `address`/`explanation_source` when code://); else skip neighbours (clean no-op).
    if sch == "decision" and suite is not None:
        try:
            from runtime.decision_memory import recall_for_decision
            ident = terr.get("identity") if isinstance(terr.get("identity"), dict) else {}
            anchor = ident.get("meaning")
            cand = ident.get("address") or ident.get("explanation_source")
            subj = cand if (isinstance(cand, str) and cand.startswith("code://")) else None
            if anchor:
                # BOUNDED (timeout, NOT just try/except — a HANG ≠ an exception): recall hits the embed service
                # (query_corpus); a down/slow embed would HANG the whole resolve → the surface goes down (live
                # regression 2026-06-18). Run it in a daemon thread + join with a hard timeout; on timeout the
                # resolve PROCEEDS without the recall-grounding (the card renders + is decidable; the hung thread
                # is a daemon — it dies with the process, never blocks). A working recall completes well under it.
                import threading as _th
                _box = {}
                def _recall(_b=_box):
                    try:
                        # HOT-PATH: rerank=False → cosine grounding within the 3s budget. The CPU jina rerank
                        # (13-20s for ~24 hits, 2026-06-18 measured) is OFF the live resolve — it would blow
                        # the budget and re-trigger the timeout-degrade (the surface would resolve UNGROUNDED
                        # every time). rerank stays available for the unbounded paths (projection's route /
                        # a background refinement). With the X12-FAST index cache, the 6-space cosine recall
                        # completes well under budget → the decision resolves WITH its grounding.
                        _b["m"] = recall_for_decision(suite, anchor, address=subj, rerank=False)
                    except Exception as _e:  # noqa: BLE001
                        _b["e"] = _e
                _t = _th.Thread(target=_recall, daemon=True)
                _t.start()
                _t.join(timeout=_MEMORY_LEG_TIMEOUT_S)
                if _t.is_alive():
                    terr["notes"].append(
                        f"memory leg timed out (>{_MEMORY_LEG_TIMEOUT_S}s — recall/embed slow or down; "
                        f"degrade-clean, the decision still resolves + is decidable)")
                elif "e" in _box:
                    terr["notes"].append(f"memory leg unresolved ({type(_box['e']).__name__}: {_box['e']})")
                elif "m" in _box:
                    terr["memory"] = _box["m"]
        except Exception as e:
            terr["notes"].append(f"memory leg unresolved ({type(e).__name__}: {e})")
    terr["legs_present"]["memory"] = bool(terr.get("memory"))

    return terr


def territory_prose(territory_or_address, *, suite=None, store=None, max_chars: int = 2400) -> str:
    """Render a territory (or compose+render from an address) → the `[Operator context]` block a CC brain
    turn folds in. NEVER raises (the bridge-facing path: context-gathering must never kill a brain turn,
    the contract bridge._claude_stream already holds at bridge.py:1670-1681). The drop-in replacement for
    that inline ui://-only composer: `ctx = territory_prose(address, suite=SUITE)`.

    DNA voice note (operator_voice.rhm_spoken — "territory_prose frames to it"): this is the STRUCTURAL
    explanation scaffold the RHM speaks FROM — labelled meaning fields ("What this is", "The decision",
    "The options are…"), already operator-law-safe (human meaning only, no addresses/jargon). It carries
    no spoken-VOICE register of its own; the voice (second-person, brief-lead+offer-deeper, phone-aware,
    translate-not-leak, answer-from-context) is RESOLVED once in the brain's system prompt — PANEL_BRIEFING
    in ui_claude_session.py, which composes from the DNA rhm_spoken standard. So this frame inherits DNA's
    voice calibration through the brain with no per-field voice wording here (resolve-not-hardcode upheld;
    do not author voice copy into these structural labels)."""
    try:
        terr = (territory_or_address if isinstance(territory_or_address, dict)
                else territory_for(territory_or_address, suite=suite, store=store))
    except Exception as e:
        return f"(context unavailable: {type(e).__name__})"   # no raw address in the fail line (operator-law)
    try:
        bits = []
        # ★ The raw address is DELIBERATELY ABSENT from this operator-facing block (projection by-use 2026-06-18:
        # the brain PARROTED the old "[internal handle — never shown]" line into its reply despite the label —
        # the model can't echo what it isn't given). Operator-law: the brain answers from the RESOLVED MEANING
        # below; it never needs the raw scheme:// to orient. The address stays server-side (the bridge holds the
        # request param; build-intent uses it) — passed out-of-band if a tool genuinely needs it, never inline here.
        # WHAT THIS IS — HUMAN meaning ONLY (territory_label: address-safe + jargon-safe). Was json.dumps(the
        # raw address_help dict) — which dumped the blast_radius/scope developer-diagnostics + the "(unregistered)"
        # raw address into context, so the brain narrated system-readout jargon + leaked the address (2026-06-17 fix).
        bits.append("What this is: " + territory_label(terr, max_len=200))
        # VIEW meta (the instrument-surface aim → the ACTIVE projection view's self-description, the SAME the
        # operator sees) — the RHM's grounding so it answers "what am I looking at?" from the real view meaning,
        # not a thin pointer. is=what-kind · fills=what-each-element-is · why=what-it's-for (bindings/<id>.py meta).
        if terr.get("identity_kind") == "view.meta" and isinstance(terr.get("identity"), dict):
            _vm = terr["identity"]
            _vparts = [s for s in (_vm.get("is"), _vm.get("fills"), _vm.get("why"))
                       if isinstance(s, str) and s.strip()]
            if _vparts:
                bits.append("What this view shows: " + _clip(" ".join(_vparts), 600))
        # the comprehended CONTENT (the readable meaning) — corpus units / content identities.
        content = terr.get("identity") if (terr.get("identity_kind") == "corpus.content"
                                            and isinstance(terr.get("identity"), str)) else None
        if content is None and isinstance(terr.get("corpus_content"), str):
            content = terr["corpus_content"]
        if content and content.strip():
            bits.append("Details: " + " ".join(content.split())[:1400])
        # context items at the locus (human text).
        items = terr.get("context_items") or []
        if items:
            bits.append("Context here: " + " | ".join(str(it.get("text", it))[:160] for it in items[:6]))
        # connections — a HUMAN summary (counts + edge KINDS; raw target ADDRESSES omitted, operator-law).
        rel = terr.get("relations") or {}
        ein, eout = (rel.get("edges_in") or []), (rel.get("edges_out") or [])
        if ein or eout:
            kinds = sorted({e.get("kind") for e in (list(eout) + list(ein)) if e.get("kind")})
            line = f"Connections: {len(eout)} outgoing, {len(ein)} incoming"
            if kinds:
                line += " (" + ", ".join(kinds[:5]) + ")"
            bits.append(line + ".")
        # library PALETTE (vi-vision:// compose-set) — HUMAN name+type, NEVER the raw component_id (operator-law).
        # So the credential-free brain knows the real pieces it can compose a new asset from.
        lib = terr.get("library") or {}
        libitems = lib.get("items") or []
        if libitems:
            named = ", ".join(f"{(it.get('name') or '').strip() or 'a piece'} ({it.get('type')})"
                              for it in libitems[:12] if isinstance(it, dict))
            more = lib.get("total", len(libitems)) - min(12, len(libitems))
            bits.append("Available pieces in this library: " + named + (f" (+{more} more)" if more > 0 else "") + ".")
        # DECISION (decision:// resolved row+state) — the question + options + resolved state, all HUMAN. The
        # "What this is" line above already gave the decision's name (territory_label → legibility.name/meaning);
        # this adds the question to decide, the choices (label + what each entails, the suggested one flagged),
        # and whether it's still open or already decided. Operator-law: meaning-words only, never a machine id.
        ident = terr.get("identity")
        if terr.get("scheme") == "decision" and isinstance(ident, dict):
            meaning = (ident.get("meaning") or "").strip()
            if meaning:
                bits.append("The decision: " + _clip(meaning, 320))
            rendered = []
            for o in (ident.get("options") or []):
                if not isinstance(o, dict):
                    continue
                lab = (o.get("label") or "").strip()
                if not lab:
                    continue
                piece = lab
                impl = (o.get("implication") or o.get("description") or "").strip()
                if impl:
                    piece += " — " + _clip(impl, 220)
                if o.get("recommended"):
                    piece += " (suggested)"
                rendered.append(piece)
            if rendered:
                bits.append("The options are: " + "  ||  ".join(rendered[:6]))
            st = ident.get("state")
            if st == "decided":
                dv = str(ident.get("decided_value") or "").strip()
                bits.append(f"This has already been decided — the choice was: {dv}." if dv
                            else "This has already been decided.")
            elif st == "pending":
                bits.append("This is still open — no choice has been made yet.")
        # MEMORY leg (decision:// → recalled grounding for the RHM) — surface the digest MEANING now, NEVER the
        # raw source ids/addresses (operator-law). recall_for_decision attaches each item's clean digest text
        # (recollection 5d9e645, legibility-safe — no JSON, no ids); we render the top meanings so the grounding
        # is CONTENT, not just a count. DEGRADE-CLEAN: ~half the items lack text today (the corpus-write
        # non-string-output gap, recollection-tracked) → they still count toward the resurfacing signal, and if
        # NONE carry text we fall back to the count line. Operator-law safety belt: drop any text leaking an address.
        mem = terr.get("memory") if isinstance(terr.get("memory"), dict) else {}
        ctx = mem.get("context") or []
        if ctx:
            ctexts = [str(c.get("text") or "").strip() for c in ctx if isinstance(c, dict)]
            ctexts = [t for t in ctexts if t and "://" not in t]
            if ctexts:
                shown = ctexts[:2]
                line = "What's known about this: " + "  |  ".join(_clip(t, 160) for t in shown)
                extra = len(ctx) - len(shown)
                if extra > 0:
                    line += f" (plus {extra} more relevant piece{'s' if extra != 1 else ''} to draw on)"
                bits.append(line)
            else:
                bits.append(f"What's known about this: {len(ctx)} relevant piece(s) in your memory to draw on.")
        prior = mem.get("prior_decisions") or []
        if prior:
            ptexts = [str(p.get("text") or p.get("meaning") or p.get("decision") or "").strip()
                      for p in prior if isinstance(p, dict)]
            ptexts = [t for t in ptexts if t and "://" not in t]
            if ptexts:
                bits.append("Decided before: " + " | ".join(_clip(t, 120) for t in ptexts[:3]) + ".")
            else:
                bits.append(f"Decided before: {len(prior)} earlier decision(s) on this.")
        nbrs = mem.get("neighbours") or []
        if nbrs:
            bits.append(f"Related: {len(nbrs)} connected piece(s).")
        return "\n".join(bits)[:max_chars]
    except Exception as e:
        return f"(context render error: {type(e).__name__})"   # no raw address (operator-law)


# ── THE HUMAN AIM LABEL (operator-law: the V/RHM shows MEANING, never the raw address) ────────────────
# The FE getAimLabel helper (fork-v-brain.attach) is backed by this via a thin bridge route (proposed:
# GET /api/territory/label?address=… → {label}). The operator NEVER sees code/files/machine names — so this
# NEVER returns the raw address; it reads the identity leg's human meaning and degrades to a human NOUN.
_HUMAN_IDENTITY_KEYS = ("what_this_is", "title", "name", "heading", "label", "summary", "meaning", "desc", "description")
_SCHEME_HUMAN_NOUN = {
    "ui": "this part of the surface", "run": "a result", "cas": "a stored piece",
    "skill": "a skill", "context": "a working context", "session": "a past conversation",
    "cap": "a capability", "board": "a noticeboard item", "clone": "a past self",
    "mind": "a way of thinking", "code": "a piece of the work", "corpus": "a piece of the work",
    "decision": "a decision to make",
}


def _clip(s, n):
    s = " ".join(str(s).split())                       # collapse whitespace/newlines to one line
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def _human_from_identity(ident):
    """Pull a HUMAN one-liner from an identity value. A dict → a whitelisted human field (never a machine
    key like source_address/cas/id). A string (comprehended corpus content) → its first real line, with a
    leading markdown '#' stripped. Returns None if nothing human is found (caller degrades to a scheme noun)."""
    if isinstance(ident, str):
        for ln in ident.splitlines():
            ln = ln.strip().lstrip("#").strip()
            if ln:
                return ln
        return None
    if isinstance(ident, dict):
        # legibility-bearing types (a decision, and any type carrying the legibility meaning-fields) put THIS
        # thing's human name under legibility.name — the operator-legibility law's anchor (prefer it first).
        leg = ident.get("legibility")
        if isinstance(leg, dict) and isinstance(leg.get("name"), str) and leg["name"].strip():
            return leg["name"]
        # ui:// address_help nests its human line under what_this_is (a dict or str) — reach one level in.
        wti = ident.get("what_this_is")
        if isinstance(wti, dict):
            for k in _HUMAN_IDENTITY_KEYS:
                if isinstance(wti.get(k), str) and wti[k].strip():
                    return wti[k]
        for k in _HUMAN_IDENTITY_KEYS:
            v = ident.get(k)
            if isinstance(v, str) and v.strip():
                return v
    return None


def territory_label(address, *, suite=None, store=None, max_len: int = 80) -> str:
    """Resolve a HUMAN one-line 'what-this-is' for an address — the operator-facing label the V/RHM shows.
    OPERATOR-LAW: NEVER returns the raw address or a machine name; reads the identity leg's human meaning and
    degrades to a human NOUN by scheme. NEVER raises (a label must never kill a render). Reuses territory_for
    (no parallel resolver). Accepts an address OR a pre-composed territory dict (like territory_prose)."""
    try:
        terr = (address if isinstance(address, dict)
                else territory_for(address, suite=suite, store=store))
    except Exception:
        return "this"                                   # non-address / total failure → safe generic (never the raw input)
    label = _human_from_identity(terr.get("identity"))
    if (not label or "://" in label) and terr.get("corpus_content") is not None:
        label = _human_from_identity(terr.get("corpus_content"))
    # OPERATOR-LAW guard: reject any candidate that leaks a raw address (e.g. address_help echoes the address
    # for an UNREGISTERED ui:// → "ui://… (unregistered)"). A leaking label degrades to the human scheme noun.
    if label and "://" not in label:
        return _clip(label, max_len)
    return _SCHEME_HUMAN_NOUN.get(terr.get("scheme"), "this")   # degrade: a human noun, NEVER the address


# ── THE ROUTE-BACK WRITE (mutation-at-address) — the loadable-brain loop's write half ────────────────
# gallery:direction (wildcard's binder) → group by element_id → territory_write each to its sub-address →
# re-render. Uses the company's SCHEME-AGNOSTIC mark mechanism (suite.mark — any target string), NOT the
# ui://-gated annotate, NOT vi-visual's /api/submit_response (lead's directive). Re-render reads
# territory_directions_at. Requires the direction mark_types (comment/reaction/favour) registered.
# = wildcard's gallery:direction item.type values. decision_take added 2026-06-18 (decision-surface): a
# decision-card TAKE is the same route-back — wildcard emits {type:"decision_take", value:<chosen option label>,
# element_id:<canonical decision://global/<id>>}; territory_write routes it generically (suite.mark) and the
# decision:// resolver composes the decided state from it. The take's `value` MUST be the option LABEL (the
# decided_value); the target MUST be the CANONICAL decision address (contracts.address.decision_address).
# decision_retract added 2026-06-20 (fork): decision_take's symmetric TWIN — the operator's UN-DECIDE (decided→
# pending). SAME route-back/write-path/gate; value empty (optional note); the LATEST decision EVENT by ts wins
# (compose_state folds take|retract). Gives the un-decide a LEGITIMATE gated write (the gate refused it before,
# unregistered) — never a raw ungated store-append (the contamination pattern). Inherits the same #1b floor.
DIRECTION_MARK_TYPES = ("comment", "reaction", "favour", "decision_take", "decision_retract")


def territory_write(element_id, item, *, suite):
    """Persist ONE gallery:direction item at its sub-address. `element_id` = the element's sub-address
    (`<base-address>#elem`, ANY scheme — mark takes any target string). `item` = wildcard's payload:
    {type: comment|reaction|favour, ...}; the sub-type + payload (annotation_type / reaction / score / text)
    ride as fields, the routing keys (id/type/element_id) are dropped. Returns the mark record. Fail-loud on
    a missing type/target. (The direction mark_type must be registered — registry-is-truth.)"""
    if not isinstance(item, dict):
        raise ValueError(f"territory_write: item must be a dict (a gallery:direction payload), got {type(item).__name__}")
    mark_type = item.get("type")
    if not mark_type:
        raise ValueError(f"territory_write: item has no 'type' (comment|reaction|favour) — fail loud. item={item!r}")
    target = element_id or item.get("element_id")
    if not target:
        raise ValueError("territory_write: no element_id/target sub-address — fail loud (nothing to write at).")
    # HOLE-1 (wildcard, lead-authorized + fork-greenlit 2026-06-21): a decision take/retract MUST land +
    # signal on the CANONICAL decision address — else the mark lands at a non-canonical string the
    # decision:// resolver never sees (decided silently reads pending) AND decision_decided_signal emits a
    # non-canonical address a gated_on lane never matches. Canonicalize ONCE here (single-source:
    # contracts.address, never reimplemented), so BOTH suite.mark(target,…) and decision_decided_signal(…,
    # target,…) below use the canonical form (line :502's stated requirement). Idempotent on already-
    # canonical input (the happy path is unchanged); fail-loud on a malformed decision address
    # (parse_decision_address raises) — a visible refusal, not a silent miss. retract is the symmetric twin.
    if mark_type in ("decision_take", "decision_retract"):
        from contracts.address import decision_address, parse_decision_address
        target = decision_address(parse_decision_address(target))
    fields = {k: v for k, v in item.items() if k not in ("type", "element_id", "id")}
    # canonical `value` per type, matching the mark_type's value_shape (comment=free→text · reaction=label
    # →reaction · favour=score→score) — so render reads a mark's value uniformly (the marks-layer convention).
    if "value" not in fields:
        if mark_type == "comment" and fields.get("text") is not None:
            fields["value"] = fields["text"]
        elif mark_type == "reaction" and fields.get("reaction") is not None:
            fields["value"] = fields["reaction"]
        elif mark_type == "favour" and fields.get("score") is not None:
            fields["value"] = fields["score"]
    fields.setdefault("source", "operator")
    rec = suite.mark(target, mark_type, **fields)
    # L3 (the decide→SIGNAL→resume wire): a decision_take IS the operator deciding — emit the
    # decision.decided SIGNAL so the work gated on this decision can RESUME with the chosen option.
    # ONLY on decision_take (comment/reaction/favour are not decides; decision_retract is the twin
    # decided→pending — a re-pend, not a decided-signal). Floor-clean (a record emit, not a post/spawn).
    # Surface a signal failure on the record (no-silent-failures) WITHOUT failing the decide — the mark
    # already landed (the decided state is correct); only the resume-signal would be missing.
    if mark_type == "decision_take":
        try:
            from runtime.decision_registry import decision_decided_signal
            rec["decided_signal"] = decision_decided_signal(
                suite, target, fields.get("value"), by=fields.get("by"))
        except Exception as e:
            rec["decided_signal_error"] = f"{type(e).__name__}: {e}"
    return rec


def territory_directions_at(address, *, suite):
    """READ the directions written at an address (the route-back read side, for re-render). Scheme-agnostic
    (suite.marks_for). Returns [] on absence/error (a clean empty, never a crash mid-render)."""
    try:
        return suite.marks_for(address)
    except Exception:
        return []
