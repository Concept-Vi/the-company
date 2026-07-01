# AUDIT-INDEX — the existing system, mapped (read-only, whole-system)

> Cheap whole-system **content-TYPE map** + the critical **reconciliation tensions** between
> what the v1 docs codify and what the source material (analysis/) actually shows. Per the
> audit method: this is the territory map; each build slice then deep-audits only its type.
> **Rule when they conflict: the SOURCE material is authoritative for the DNA; v1 docs are
> authoritative for what was built.** The current system "interpreted the decks too narrowly"
> (the original brief) — this index is where we catch that.

## Content-TYPE map (what kinds of content exist + where)
| Type | Where | Audit owner (slice) |
|---|---|---|
| **Source-of-truth tokens** | `colors_and_type.css` (+ my `tokens/*.css`) | slice 1–2 |
| **App chrome CSS** | `app/app.css`, `deck.css`, `imagery.css`, `registry.css`, `workshop.css` | slice 3 (consumers) |
| **App React** | `app/App.jsx`, `app/components/*`, `app/canvases/*`, `app/registry/*`, `app/services/*` | slice 3–4 |
| **UI kits** | `ui_kits/platform`, `ui_kits/vi`, `ui_kits/virtual-hub` (each: index.html + *.jsx + css) | slice 3–4 |
| **Icon library** | `assets/icons/` — `cv-icons.js` (99 glyphs, `window.CV_ICONS`), `CvIcon.jsx`, `svg/`, explorer | slice 2/4 (diagram+icon) |
| **Logos** | `assets/logos/` (real wordmark + V marks: light/white/yellow PNG) | keep |
| **Illustrations** | `assets/illustrations/` (arch diagrams, staged flow, Vi framework, stats panels) | slice 4 (diagram gen) |
| **Reference screenshots** | `assets/reference/dashboard_*.jpg`, `comment_popup.png` | reference |
| **DS-tab cards** | `preview/` (~35) + `specimens/` (mine: 4) + root `Tonal Zoning System.html` | every slice (keep in sync) |
| **Docs** | `README.md` (242L), `SKILL.md` (75L), `DESIGN-LANGUAGE.md` (mine) | update as DNA changes |
| **Compiler outputs** | `_ds_bundle.js`, `_ds_manifest.json`, `_adherence.oxlintrc.json` | never hand-edit |
| **My analysis** | `analysis/*` (model, requirements, diagrams, integration, per-folder) | the spec |
| **Archive** | `_archive-v1/` (pre-overhaul snapshot) | safety net |

## ★ Reconciliation tensions — v1 docs vs source DNA (the "shallow/flat" gaps)
These are the high-value deepenings. Each: what v1 says → what the source shows → resolution.
1. **Backgrounds "flat ivory, NO gradients/patterns/textures"** (README) → source has **subtle diagonal hatch bands, blueprint-ghost linework, hatch baseline rule**. → *Resolve: add the texture layer as low-opacity tokens; "flat" was the narrow read.* (REQUIREMENTS A5)
2. **"The system feels still. No entry animations. No motion."** (README) → decks are **motion-ready** (GIF slots), encode latent motion (directional cues, layered z, state-morph diagrams). → *Resolve: add the motion language; stillness is a per-register choice, not a global law.* (E1–E3)
3. **Single gold `#E0C010` ("the only loud colour")** → source uses a **gold→bronze→tan RAMP** (`#d6bf57→#c09d5d→#b98664`) and the working gold is **softer** than `#E0C010`. → *Resolve: soften + add ramp; keep `#E0C010` as legacy.* (A3)
4. **Canvas `#FBF7EC` ivory; soft-gold panel `#FBF4C8`** (fairly saturated) → source surfaces are a **near-white ~1–3% ladder** (`#fdfcf7`/`#f8f8f8`…), far subtler. → *Resolve: recalibrate the zone ladder to sampled values; the v1 panels are too saturated (the original brief's exact complaint).* (A1)
5. **Zoning = "soft-gold section panel" (one warm wash)** → source zoning is a **multi-undertone containment-depth ladder** (warm-ivory vs neutral-grey marks nesting, not category). → *Resolve: reframe zoning as depth; v1 had one wash, not the ladder.* (A2, B1)
6. **Bronze `#988058` "almost never UI chrome, only illustrations"** → source uses bronze as a **structural/quiet type voice** (section headers, connective captions) across UI too, and lighter (`#c09d5d`). → *Resolve: warm/lighten + expand bronze's role per colour-role logic.* (A4)
7. **Flat applied tokens, hand-authored per surface** → source implies a **computed/parametric system** (axes, containment, block+graph solvers, templates). → *Resolve: the generative core (slice 3) is the real depth fix — this is what makes it stop feeling "handwritten".* (AXES, C1–C6)
8. **Shape system (circle/hex/octagon/diamond) — KEEP, it's right.** README + source agree; this is genuine brand DNA. Reuse as diagram node shapes + entity badges. ✅
9. **99-icon bronze library + gold-circle badge + desaturated state-gradient — KEEP, strong.** Aligns with DIAGRAMS.md (icons as first-class node content). Build the diagram generator ON this, don't replace it. ✅
10. **Status dots (Pending/Approved/Resolved/Rejected, warm-shifted)** → matches the traffic-light finding; *reconcile my saturated status chips with the existing warm dots — extend, don't fork.* (F3)

## Vigilance notes (avoid "technical success")
- The system is **documented-deep but applied-flat**. The fix is not more docs — it's the **computed core + texture + depth + motion + ramp** actually wired through consumers, so it stops feeling handwritten.
- Several README rules are **v1 narrow-reads** that must be *rewritten* as the DNA lands (tensions 1–7). Update README/SKILL in lockstep so docs don't contradict the new system.
- **Keep what's genuinely right** (8–10): shape system, icon library, voice, sentence-case, URL-preview copy pattern, entity vocabulary. Don't churn these.

## → Next
Slice-1 scoped audit: enumerate every token in `colors_and_type.css` + `tokens/*.css` and every consumer, tag keep/recalibrate/deprecate against tensions 3–6, then recalibrate in place.
