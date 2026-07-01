// canvases/Build.jsx — cross-canvas Vi planner with 3-layer task tree
const { useState: useState_b, useEffect: useEffect_b, useRef: useRef_b } = React;

// Template seeds the user can start from
const SEEDS = [
  { id: 'brochure',  label: 'Property brochure',  brief: 'A one-page property brochure for a 2-bed apartment with hero render, 4 stat tiles, description, price, and agent contact' },
  { id: 'palette',   label: 'Marketing palette',  brief: 'A 5-color palette for marketing emails that sits beside my brand gold' },
  { id: 'icons',     label: 'Icons + colors for payments', brief: 'A new sub-system for handling payment flows: 6 icons (card, invoice, refund, etc.) and a 4-color status palette' },
  { id: 'voice',     label: 'Voice for error states', brief: 'Three error message variants for upload failures, length-limit issues, and login problems' },
  { id: 'slide',     label: 'Title slide',         brief: 'A pitch-deck title slide composition with logo, headline, subheadline, and date' },
  { id: 'widget',    label: 'Dashboard widget',    brief: 'A hybrid dashboard widget showing occupancy, linked hubs, capture count, and a 13-week capture sparkline for Tower East' },
  { id: 'wizard',    label: 'Onboarding wizard',   brief: 'A 4-step onboarding flow — sign up, set up workspace, drop in logo for brand kit, invite teammates' },
];

function Build({ initialBrief, onAdoptIcons, onAdoptColors, onSaveAsTemplate, onNav, onOpenInWorkshop }) {
  const [brief, setBrief] = useState_b(initialBrief || SEEDS[0].brief);
  // stage: 1 = brief, 2 = plan review, 3 = generation, 4 = compose & adopt
  const [stage, setStage] = useState_b(1);
  const [planning, setPlanning] = useState_b(false);
  const [generating, setGenerating] = useState_b(false);
  const [composing, setComposing] = useState_b(false);
  const [plan, setPlan] = useState_b(null);
  const [error, setError] = useState_b(null);
  const [refining, setRefining] = useState_b(false);
  const [refineInput, setRefineInput] = useState_b('');
  const [refinements, setRefinements] = useState_b([]); // history of {message, changedKinds, ts}

  // If a brief gets pushed in from outside (e.g. from Templates), reset to stage 1 with that brief
  useEffect_b(() => {
    if (initialBrief) {
      setBrief(initialBrief);
      setStage(1);
      setPlan(null);
      setError(null);
    }
  }, [initialBrief]);

  const subtasksRef = useRef_b([]);
  subtasksRef.current = plan?.subtasks || [];

  const busy = planning || generating || composing || refining;

  async function generatePlan() {
    if (!brief.trim()) return;
    setPlanning(true);
    setError(null);
    setPlan(null);
    try {
      const planPrompt = `You are Vi, an AI planner inside ConceptV Studio. The user has given you a brief; your job is to decompose it into 2-4 parallel subtasks, each handled by a specialist sub-agent that touches ONE canvas of the design system.

The available sub-agents:
- icons-generator — generates 1-6 new SVG icons (24x24, 1.5px stroke, no fills, brand line style)
- colors-generator — generates a coherent palette of 3-6 named hex colors
- copy-writer — writes 1-3 short on-brand copy variants for a specific context (button/heading/body/error etc.)
- widget-builder — produces a ConceptV widget (dashboard tile / hub panel / partner embed) with title, KPIs, rows, CTA. Use when the brief mentions a dashboard tile, embedded card, hub widget, public-facing live data display.
- wizard-builder — produces a multi-step flow (Property Wizard, onboarding, signup, generic form). Use when the brief describes a step-by-step user flow.
- workshop-deck — produces a Workshop slide deck (multiple slides). Use when the brief mentions a pitch / investor / sales deck / all-hands / multiple slides.
- workshop-brochure — produces a one-page brochure. Use when the brief mentions a sell-sheet, A4 sheet, one-pager, property brochure.
- type-builder — registers a new Type in the universal Type Registry. Use when the user explicitly asks to create a new kind / system / template / archetype, or when the brief implies a reusable pattern (e.g. "we'll keep doing this for many properties"). Outputs the Type schema (name, layer, family, slots, defaults, variables).
- composer — composes a final output (a card preview, a slide preview, an asset listing) using whatever was generated above

Brief: "${brief.trim()}"

Plan the work. Output a JSON object describing:
- strategy: a one-sentence summary of your approach
- subtasks: an array of 2-4 subtasks. Each has:
  - kind: one of "icons-generator" | "colors-generator" | "copy-writer" | "widget-builder" | "wizard-builder" | "workshop-deck" | "workshop-brochure" | "composer"
  - label: a short human-readable task name (3-6 words)
  - brief: the specific brief you'd hand the sub-agent (1-2 sentences)

Always include exactly ONE composer subtask at the end, with a brief describing what the final output should look like (e.g. "Render a brochure card combining the icons + palette + copy" or "Hand off the generated widget for review").

If the brief asks for a Workshop doc (deck, brochure, widget, wizard) DIRECTLY (e.g. "make me an investor deck"), include the matching workshop-* / widget-builder / wizard-builder subtask alongside complementary subtasks (icons / colors / copy) if useful.

Respond as compact JSON only, no prose, no markdown fences.`;
      const planReply = await window.CV_AI.execute('build.plan', { params: { prompt: planPrompt }, surface: 'build' });
      let planObj;
      try { planObj = JSON.parse(planReply); }
      catch {
        const m = String(planReply).match(/\{[\s\S]*\}/);
        if (m) { try { planObj = JSON.parse(m[0]); } catch {} }
      }
      if (!planObj || !Array.isArray(planObj.subtasks) || !planObj.subtasks.length) {
        throw new Error("Couldn't parse plan");
      }
      const subtasks = planObj.subtasks.map((s, i) => ({ ...s, id: 'st-' + i, status: 'idle', result: null }));
      setPlan({ strategy: planObj.strategy || '', subtasks });
      setStage(2);
    } catch (err) {
      setError(String(err.message || err));
    } finally {
      setPlanning(false);
    }
  }

  function updateSubtaskBrief(id, newBrief) {
    setPlan(p => ({ ...p, subtasks: p.subtasks.map(s => s.id === id ? { ...s, brief: newBrief } : s) }));
  }
  function updateSubtaskLabel(id, newLabel) {
    setPlan(p => ({ ...p, subtasks: p.subtasks.map(s => s.id === id ? { ...s, label: newLabel } : s) }));
  }
  function removeSubtask(id) {
    setPlan(p => ({ ...p, subtasks: p.subtasks.filter(s => s.id !== id) }));
  }

  async function runGeneration() {
    if (!plan) return;
    setStage(3);
    setGenerating(true);
    setError(null);
    try {
      const composerIdx = plan.subtasks.findIndex(s => s.kind === 'composer');
      const nonComposers = plan.subtasks.filter((s, i) => i !== composerIdx);

      // mark all non-composers active, clear any prior results
      setPlan(p => ({
        ...p,
        subtasks: p.subtasks.map(s => s.kind !== 'composer'
          ? { ...s, status: 'active', result: null }
          : { ...s, status: 'idle', result: null }),
      }));

      const results = await Promise.all(nonComposers.map(async (s) => {
        try {
          const r = await runSubtask(s, brief);
          setPlan(p => ({
            ...p,
            subtasks: p.subtasks.map(x => x.id === s.id ? { ...x, status: 'done', result: r } : x),
          }));
          return { id: s.id, kind: s.kind, label: s.label, result: r };
        } catch (err) {
          setPlan(p => ({
            ...p,
            subtasks: p.subtasks.map(x => x.id === s.id ? { ...x, status: 'blocked', result: { error: String(err.message || err) } } : x),
          }));
          return { id: s.id, kind: s.kind, label: s.label, result: { error: true } };
        }
      }));
      setGenerating(false);
      // auto-advance to compose
      await runCompose(results);
    } catch (err) {
      setError(String(err.message || err));
      setGenerating(false);
    }
  }

  async function runCompose(results) {
    setStage(4);
    setComposing(true);
    try {
      const composer = plan?.subtasks.find(s => s.kind === 'composer');
      if (composer) {
        setPlan(p => ({ ...p, subtasks: p.subtasks.map(x => x.id === composer.id ? { ...x, status: 'active' } : x) }));
        try {
          const r = await runComposer(composer, brief, results);
          setPlan(p => ({ ...p, subtasks: p.subtasks.map(x => x.id === composer.id ? { ...x, status: 'done', result: r } : x) }));
        } catch (err) {
          setPlan(p => ({ ...p, subtasks: p.subtasks.map(x => x.id === composer.id ? { ...x, status: 'blocked', result: { error: String(err.message || err) } } : x) }));
        }
      }
    } finally {
      setComposing(false);
    }
  }

  async function recompose() {
    if (!plan) return;
    const parts = plan.subtasks.filter(s => s.kind !== 'composer')
      .map(s => ({ id: s.id, kind: s.kind, label: s.label, result: s.result }));
    await runCompose(parts);
  }

  function reset() {
    setStage(1);
    setPlan(null);
    setError(null);
    setRefinements([]);
    setRefineInput('');
  }

  function backToBrief() {
    if (busy) return;
    setStage(1);
  }
  function backToPlan() {
    if (busy) return;
    setStage(2);
  }

  async function refinePart(scope, message) {
    // scope: { kind: 'icon'|'color'|'copy'|'composed'|'icons-all'|'colors-all'|'copy-all', target?: name/index }
    if (!message || !plan) return;
    setRefining(true);
    try {
      const iconsSub = plan.subtasks.find(s => s.kind === 'icons-generator');
      const colorsSub = plan.subtasks.find(s => s.kind === 'colors-generator');
      const copySub = plan.subtasks.find(s => s.kind === 'copy-writer');
      const composerSub = plan.subtasks.find(s => s.kind === 'composer');

      const markActive = (id) => setPlan(p => ({ ...p, subtasks: p.subtasks.map(x => x.id === id ? { ...x, status: 'active' } : x) }));
      const markDone   = (id, result) => setPlan(p => ({ ...p, subtasks: p.subtasks.map(x => x.id === id ? { ...x, status: 'done', result } : x) }));

      let changedLabel = '';

      // ===== Per-item: single icon =====
      if (scope.kind === 'icon' && iconsSub) {
        markActive(iconsSub.id);
        const existing = iconsSub.result?.icons || [];
        const target = existing.find(i => i.name === scope.target);
        if (!target) throw new Error('Icon not found');
        const prompt = `You are revising one icon in ConceptV's style (24×24, 1.5px stroke, no fills, currentColor).

Original icon: "${target.name}"
Current SVG body: ${target.body}

User wants this change: "${message}"

Return ONLY the new icon body (path/circle/rect markup that goes inside <svg viewBox="0 0 24 24">). No wrapper, no fill or stroke attributes.

Respond as compact JSON only:
{"name": "${target.name}", "body": "<new svg body>"}`;
        const reply = await window.CV_AI.complete(prompt);
        const parsed = parseJsonLoose(reply);
        if (parsed?.body) {
          const newIcons = existing.map(i => i.name === target.name ? { ...i, body: parsed.body } : i);
          markDone(iconsSub.id, { ...iconsSub.result, icons: newIcons });
          changedLabel = `icon "${target.name}"`;
        }
      }
      // ===== Per-item: single color =====
      else if (scope.kind === 'color' && colorsSub) {
        markActive(colorsSub.id);
        const existing = colorsSub.result?.colors || [];
        const target = existing.find(c => c.name === scope.target);
        if (!target) throw new Error('Color not found');
        const prompt = `You are revising one color in ConceptV's warm-ivory palette (gold #E0C010, bronze #988058, no cool greys).

Original: ${target.name} ${target.hex} (${target.role})
User wants: "${message}"

Return ONLY the new color. JSON only:
{"name": "${target.name}", "hex": "#...", "role": "..."}`;
        const reply = await window.CV_AI.complete(prompt);
        const parsed = parseJsonLoose(reply);
        if (parsed?.hex) {
          const newColors = existing.map(c => c.name === target.name ? { ...c, hex: parsed.hex, role: parsed.role || c.role } : c);
          markDone(colorsSub.id, { ...colorsSub.result, colors: newColors });
          changedLabel = `color "${target.name}"`;
        }
      }
      // ===== Per-item: single copy variant =====
      else if (scope.kind === 'copy' && copySub) {
        markActive(copySub.id);
        const existing = copySub.result?.variants || [];
        const idx = scope.target;
        const target = existing[idx];
        if (target == null) throw new Error('Variant not found');
        const prompt = `Rewrite this one copy variant in ConceptV's voice (sentence case, second person, no exclamation marks, no emoji).

Original: "${target}"
User wants: "${message}"

Return ONLY the new variant. JSON only:
{"variant": "..."}`;
        const reply = await window.CV_AI.complete(prompt);
        const parsed = parseJsonLoose(reply);
        if (parsed?.variant) {
          const newVariants = existing.map((v, i) => i === idx ? parsed.variant : v);
          markDone(copySub.id, { ...copySub.result, variants: newVariants });
          changedLabel = `copy variant ${idx + 1}`;
        }
      }
      // ===== Section-level: all icons / colors / copy =====
      else if (scope.kind === 'icons-all' && iconsSub) {
        markActive(iconsSub.id);
        try {
          const r = await runIcons(iconsSub.brief + ' — also: ' + message, brief);
          if (r && Array.isArray(r.icons) && r.icons.length) {
            markDone(iconsSub.id, r);
            changedLabel = 'all icons';
          } else {
            // Bad response — restore previous result, don't blank the section
            markDone(iconsSub.id, iconsSub.result);
            window.dsaToast?.('Vi returned no icons — kept the previous set');
          }
        } catch {
          markDone(iconsSub.id, iconsSub.result);
          window.dsaToast?.('Icon refine failed — kept the previous set');
        }
      }
      else if (scope.kind === 'colors-all' && colorsSub) {
        markActive(colorsSub.id);
        try {
          const r = await runColors(colorsSub.brief + ' — also: ' + message, brief);
          if (r && Array.isArray(r.colors) && r.colors.length) {
            markDone(colorsSub.id, r);
            changedLabel = 'all colors';
          } else {
            markDone(colorsSub.id, colorsSub.result);
            window.dsaToast?.('Vi returned no colors — kept the previous set');
          }
        } catch {
          markDone(colorsSub.id, colorsSub.result);
          window.dsaToast?.('Color refine failed — kept the previous set');
        }
      }
      else if (scope.kind === 'copy-all' && copySub) {
        markActive(copySub.id);
        try {
          const r = await runCopy(copySub.brief + ' — also: ' + message, brief);
          if (r && Array.isArray(r.variants) && r.variants.length) {
            markDone(copySub.id, r);
            changedLabel = 'all copy';
          } else {
            markDone(copySub.id, copySub.result);
            window.dsaToast?.('Vi returned no copy — kept the previous set');
          }
        } catch {
          markDone(copySub.id, copySub.result);
          window.dsaToast?.('Copy refine failed — kept the previous set');
        }
      }
      // ===== Composed-only: re-run just composer =====
      else if (scope.kind === 'composed' && composerSub) {
        // fall through to composer rerun below
        changedLabel = 'composition';
      }

      // Always re-run composer with up-to-date parts
      if (composerSub) {
        markActive(composerSub.id);
        // Use latest plan state
        const latestPlan = await new Promise(r => setPlan(p => { r(p); return p; }));
        const allParts = latestPlan.subtasks.filter(s => s.kind !== 'composer').map(s => ({ id: s.id, kind: s.kind, label: s.label, result: s.result }));
        try {
          const r = await runComposer(composerSub, brief + ' (revised: ' + message + ')', allParts);
          markDone(composerSub.id, r);
        } catch {}
      }

      setRefinements(prev => [...prev, {
        message,
        summary: `Refined ${changedLabel || 'the output'}`,
        changedKinds: [changedLabel || scope.kind],
        ts: new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'}),
      }]);
      window.dsaToast?.(`Refined ${changedLabel || 'output'}`);
    } catch (err) {
      window.dsaToast?.('Refine failed: ' + (err.message || err));
    } finally {
      setRefining(false);
    }
  }

  async function refine() {
    const message = refineInput.trim();
    if (!message || !plan) return;
    setRefining(true);
    setRefineInput('');
    try {
      // Phase 1: ask Vi which subtasks to re-run, and with what new sub-briefs
      const partsSummary = plan.subtasks.map(s => {
        if (s.kind === 'icons-generator') return `[${s.kind}] ${s.label}\n  icons: ${(s.result?.icons || []).map(i => i.name).join(', ') || '(none)'}`;
        if (s.kind === 'colors-generator') return `[${s.kind}] ${s.label}\n  colors: ${(s.result?.colors || []).map(c => `${c.name} ${c.hex}`).join(', ') || '(none)'}`;
        if (s.kind === 'copy-writer') return `[${s.kind}] ${s.label}\n  variants:\n    ${(s.result?.variants || []).map((v,i)=>`${i+1}. ${v}`).join('\n    ')}`;
        if (s.kind === 'composer') return `[${s.kind}] ${s.label}\n  title: ${s.result?.title || ''}\n  body: ${s.result?.preview?.body || ''}`;
        return `[${s.kind}] ${s.label}`;
      }).join('\n\n');

      const triagePrompt = `You are revising a build. The original brief was: "${brief}"

Current parts:
${partsSummary}

The user wants this change: "${message}"

Decide which subtasks need to be re-run to make this change. For each, write a NEW sub-brief that captures both the original intent and the requested change. Return JSON only:
{
  "subtasks": [{"kind": "icons-generator|colors-generator|copy-writer", "newBrief": "..."}, ...],
  "summary": "<one-line description of what's changing>"
}

Always re-run the composer last (don't include it in subtasks — it's automatic). Only include subtasks that actually need to change. If only the copy needs an edit, only return copy-writer.`;

      const triageReply = await window.CV_AI.execute('build.triage', { params: { prompt: triagePrompt }, surface: 'build' });
      let triage;
      try { triage = JSON.parse(triageReply); }
      catch {
        const m = String(triageReply).match(/\{[\s\S]*\}/);
        if (m) { try { triage = JSON.parse(m[0]); } catch {} }
      }
      if (!triage || !Array.isArray(triage.subtasks)) {
        throw new Error("Couldn't parse refinement plan");
      }

      // Map triage subtasks to existing plan subtasks by kind, override brief, mark active
      const targetKinds = new Set(triage.subtasks.map(t => t.kind));
      setPlan(p => ({
        ...p,
        subtasks: p.subtasks.map(s => {
          if (s.kind === 'composer') return { ...s, status: 'idle' };
          if (!targetKinds.has(s.kind)) return s;
          const t = triage.subtasks.find(x => x.kind === s.kind);
          return { ...s, brief: t.newBrief || s.brief, status: 'active', result: null };
        }),
      }));

      // Re-run each affected subtask
      const affected = plan.subtasks.filter(s => targetKinds.has(s.kind));
      const newResults = await Promise.all(affected.map(async s => {
        const t = triage.subtasks.find(x => x.kind === s.kind);
        const newBrief = t.newBrief || s.brief;
        try {
          const r = await runSubtask({ ...s, brief: newBrief }, brief + ' ' + message);
          setPlan(p => ({ ...p, subtasks: p.subtasks.map(x => x.id === s.id ? { ...x, status: 'done', result: r } : x) }));
          return { id: s.id, kind: s.kind, label: s.label, result: r };
        } catch {
          setPlan(p => ({ ...p, subtasks: p.subtasks.map(x => x.id === s.id ? { ...x, status: 'blocked' } : x) }));
          return { id: s.id, kind: s.kind, label: s.label, result: { error: true } };
        }
      }));

      // Always re-run composer with full context (kept parts + new parts)
      const composer = plan.subtasks.find(s => s.kind === 'composer');
      if (composer) {
        setPlan(p => ({ ...p, subtasks: p.subtasks.map(x => x.id === composer.id ? { ...x, status: 'active' } : x) }));
        const allParts = plan.subtasks.filter(s => s.kind !== 'composer').map(s => {
          const updated = newResults.find(r => r.id === s.id);
          return { id: s.id, kind: s.kind, label: s.label, result: updated ? updated.result : s.result };
        });
        try {
          const r = await runComposer(composer, brief + ' (revised: ' + message + ')', allParts);
          setPlan(p => ({ ...p, subtasks: p.subtasks.map(x => x.id === composer.id ? { ...x, status: 'done', result: r } : x) }));
        } catch {
          setPlan(p => ({ ...p, subtasks: p.subtasks.map(x => x.id === composer.id ? { ...x, status: 'blocked' } : x) }));
        }
      }

      setRefinements(prev => [...prev, {
        message,
        summary: triage.summary || '',
        changedKinds: [...targetKinds],
        ts: new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'}),
      }]);
      window.dsaToast?.(`Applied "${message.slice(0, 30)}${message.length > 30 ? '…' : ''}"`);
    } catch (err) {
      window.dsaToast?.('Refinement failed: ' + (err.message || err));
    } finally {
      setRefining(false);
    }
  }

  const composerDone = plan?.subtasks.find(s => s.kind === 'composer')?.status === 'done';

  return (
    <>
      <CanvasHeader
        title="Build"
        sub="Hand Vi a brief. It plans the work, hands subtasks to specialist agents, and assembles the result — drawing icons, colors, and copy from across your system."
        actions={stage > 1 && <button className="dsa-btn dsa-btn--ghost" onClick={reset} disabled={busy}>↺ Start over</button>}
      />
      <div className="dsa-canvas-body">

        <Stepper stage={stage} planning={planning} generating={generating} composing={composing} composerDone={composerDone}
          onJumpTo={(n) => { if (busy) return; if (n < stage) setStage(n); }}/>

        {/* ===== STAGE 1: BRIEF ===== */}
        {stage === 1 && (
          <>
            <div className="dsa-section">
              <div className="dsa-section-head">
                <h3 className="dsa-section-title">1 · Write the brief</h3>
                <span className="dsa-section-meta">Or pick a template to seed it</span>
              </div>
              <div className="dsa-card" style={{padding:18}}>
                <textarea
                  style={{
                    width:'100%', border:'1.5px solid var(--accent-gold)', borderRadius:'var(--r-md)',
                    padding:'12px 14px', background:'var(--bg-canvas)', outline:'none',
                    font:'400 14px/1.55 var(--font-body)', color:'var(--fg-primary)',
                    resize:'vertical', minHeight:80, fontFamily:'var(--font-body)',
                    boxSizing:'border-box',
                  }}
                  rows="3"
                  placeholder="What do you want to build?"
                  value={brief} onChange={e => setBrief(e.target.value)}
                  disabled={planning}
                />
                <div style={{display:'flex',gap:6,flexWrap:'wrap',marginTop:14}}>
                  {SEEDS.map(s => (
                    <button key={s.id}
                      disabled={planning}
                      style={{
                        background:'transparent', border:'1px solid var(--border-default)',
                        borderRadius:999, padding:'6px 14px', cursor: planning ? 'not-allowed' : 'pointer',
                        font:'500 12px/1 var(--font-body)', color:'var(--fg-secondary)',
                        opacity: planning ? 0.5 : 1,
                      }}
                      onClick={() => setBrief(s.brief)}>{s.label}</button>
                  ))}
                </div>
                <div style={{display:'flex',alignItems:'center',gap:8,marginTop:14}}>
                  <button className="dsa-btn dsa-btn--ai" onClick={generatePlan} disabled={!brief.trim() || planning}>
                    <ViShape size={14} animated={planning}/> {planning ? 'Planning…' : 'Generate plan →'}
                  </button>
                  <span style={{font:'400 11px/1 var(--font-body)',color:'var(--fg-muted)'}}>
                    Vi will decompose this brief into specialist subtasks for you to review.
                  </span>
                </div>
              </div>
            </div>

            <div className="dsa-section" style={{marginTop:8}}>
              <div className="dsa-section-head">
                <h3 className="dsa-section-title">How Build works</h3>
              </div>
              <div style={{display:'grid',gridTemplateColumns:'repeat(4, 1fr)',gap:12}}>
                <BuildHowCard layer="1" title="Brief" desc="Tell Vi what you want to make. Start from a template or write it yourself."/>
                <BuildHowCard layer="2" title="Plan" desc="Vi decomposes the brief into 2-4 specialist subtasks — one per canvas. You review and tweak before anything runs."/>
                <BuildHowCard layer="3" title="Generate" desc="The subtasks run in parallel: icons, colors, copy. Each lights up live as it completes."/>
                <BuildHowCard layer="4" title="Compose" desc="A composer agent assembles the parts into a final preview you can refine, adopt, or save as a template."/>
              </div>
            </div>
          </>
        )}

        {/* ===== STAGE 2: PLAN REVIEW ===== */}
        {stage === 2 && plan && (
          <>
            <div className="dsa-section">
              <div className="dsa-section-head">
                <h3 className="dsa-section-title">2 · Review the plan</h3>
                <span className="dsa-section-meta">Edit any subtask brief, remove what you don't need, or regenerate the plan</span>
              </div>
              {plan.strategy && (
                <div style={{
                  background:'var(--accent-gold-faint)', borderLeft:'3px solid var(--accent-gold)',
                  borderRadius:'var(--r-sm)', padding:'10px 14px', marginBottom:14,
                  display:'flex',gap:10,alignItems:'flex-start',
                }}>
                  <ViShape size={14}/>
                  <div>
                    <div style={{font:'700 10px/1 var(--font-body)',color:'var(--accent-bronze)',letterSpacing:'0.08em',textTransform:'uppercase',marginBottom:4}}>Vi's strategy</div>
                    <div style={{font:'400 13px/1.5 var(--font-body)',color:'var(--fg-primary)'}}>{plan.strategy}</div>
                  </div>
                </div>
              )}
              <PlanEditor plan={plan} onChangeBrief={updateSubtaskBrief} onChangeLabel={updateSubtaskLabel} onRemove={removeSubtask}/>
              <div style={{display:'flex',gap:8,marginTop:14,alignItems:'center'}}>
                <button className="dsa-btn dsa-btn--ai" onClick={runGeneration} disabled={busy || !plan.subtasks.length}>
                  <ViShape size={14}/> Approve plan & generate →
                </button>
                <button className="dsa-btn dsa-btn--outline" onClick={generatePlan} disabled={planning}>
                  ↻ Regenerate plan
                </button>
                <button className="dsa-btn dsa-btn--ghost" onClick={backToBrief} disabled={busy}>
                  ← Edit brief
                </button>
                <span style={{marginLeft:'auto',font:'400 11px/1 var(--font-body)',color:'var(--fg-muted)'}}>
                  {plan.subtasks.filter(s => s.kind !== 'composer').length} parallel subtasks · 1 composer
                </span>
              </div>
            </div>
          </>
        )}

        {/* ===== STAGE 3: GENERATION ===== */}
        {stage === 3 && plan && (
          <>
            <div className="dsa-section">
              <div className="dsa-section-head">
                <h3 className="dsa-section-title">3 · {generating ? 'Vi is generating…' : 'Generation complete'}</h3>
                {plan.strategy && <span className="dsa-section-meta" style={{color:'var(--fg-secondary)',font:'400 12px/1.4 var(--font-body)'}}>{plan.strategy}</span>}
              </div>
              <TaskList subtasks={plan.subtasks}/>
              <div style={{display:'flex',gap:8,marginTop:14,alignItems:'center'}}>
                {!generating && (
                  <button className="dsa-btn dsa-btn--ai" onClick={async () => {
                    const parts = plan.subtasks.filter(s => s.kind !== 'composer')
                      .map(s => ({ id: s.id, kind: s.kind, label: s.label, result: s.result }));
                    await runCompose(parts);
                  }} disabled={busy}>
                    <ViShape size={14}/> Compose final output →
                  </button>
                )}
                {!generating && (
                  <button className="dsa-btn dsa-btn--outline" onClick={runGeneration} disabled={busy}>
                    ↻ Re-run generation
                  </button>
                )}
                {!generating && (
                  <button className="dsa-btn dsa-btn--ghost" onClick={backToPlan} disabled={busy}>
                    ← Edit plan
                  </button>
                )}
              </div>
              {/* Live previews of parts as they complete */}
              <PartsPreview plan={plan}/>
            </div>
          </>
        )}

        {/* ===== STAGE 4: COMPOSE & ADOPT ===== */}
        {stage === 4 && plan && (
          <>
            <div className="dsa-section">
              <div className="dsa-section-head">
                <h3 className="dsa-section-title">4 · {composing ? 'Vi is composing…' : 'Output'}</h3>
                <span className="dsa-section-meta">Adopt parts into your system, copy text, or save the whole run as a reusable template</span>
                <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" style={{marginLeft:'auto'}} onClick={backToPlan} disabled={busy}>← Edit plan</button>
              </div>
              {composing && (
                <div className="dsa-gen-loading" style={{margin:'0 0 14px'}}>
                  <ViShape size={16} animated/> Composing final output from the generated parts…
                </div>
              )}
              <Output plan={plan} brief={brief} onAdoptIcons={onAdoptIcons} onAdoptColors={onAdoptColors} onSaveAsTemplate={onSaveAsTemplate} onNav={onNav} onOpenInWorkshop={onOpenInWorkshop} onRefinePart={refinePart} refining={refining}/>}/>
            </div>

            {!composing && composerDone && (
              <div className="dsa-section">
                <div className="dsa-section-head">
                  <h3 className="dsa-section-title">Refine with Vi</h3>
                  <span className="dsa-section-meta">Ask for changes — Vi decides which subtasks to re-run and updates the output in place</span>
                </div>
                <div className="dsa-card" style={{padding:18}}>
                  {refinements.length > 0 && (
                    <div style={{display:'flex',flexDirection:'column',gap:8,marginBottom:14}}>
                      {refinements.map((r, i) => (
                        <div key={i} style={{
                          padding:'10px 12px',background:'var(--accent-gold-faint)',
                          borderRadius:'var(--r-sm)',borderLeft:'3px solid var(--accent-gold)',
                        }}>
                          <div style={{display:'flex',alignItems:'baseline',gap:8,marginBottom:4}}>
                            <span style={{font:'700 10px/1 var(--font-body)',color:'var(--accent-bronze)',letterSpacing:'0.08em',textTransform:'uppercase'}}>Revision {i+1}</span>
                            <span style={{font:'500 11px/1 var(--font-body)',color:'var(--fg-muted)'}}>{r.ts}</span>
                            <span style={{marginLeft:'auto',font:'500 10px/1 var(--font-body)',color:'var(--fg-muted)'}}>
                              {r.changedKinds.length ? `re-ran ${r.changedKinds.join(', ')}` : ''}
                            </span>
                          </div>
                          <div style={{font:'400 13px/1.4 var(--font-body)',color:'var(--fg-primary)',marginBottom:r.summary?4:0}}>{r.message}</div>
                          {r.summary && <div style={{font:'400 11px/1.4 var(--font-body)',color:'var(--fg-secondary)',fontStyle:'italic'}}>{r.summary}</div>}
                        </div>
                      ))}
                    </div>
                  )}
                  <div style={{display:'flex',gap:8,alignItems:'flex-end'}}>
                    <ViShape size={28} animated={refining}/>
                    <textarea
                      value={refineInput}
                      onChange={e => setRefineInput(e.target.value)}
                      onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); refine(); } }}
                      placeholder='Ask for changes. e.g. "Make the icons more rounded", "Use a cooler palette", "Shorten the body copy", "Add a card icon"'
                      rows="2"
                      disabled={refining}
                      style={{
                        flex:1, border:'1.5px solid var(--accent-gold)', borderRadius:'var(--r-md)',
                        padding:'10px 12px', background:'var(--bg-canvas)', outline:'none',
                        font:'400 13px/1.55 var(--font-body)', color:'var(--fg-primary)',
                        resize:'vertical', minHeight:48, fontFamily:'var(--font-body)',
                        opacity: refining ? 0.6 : 1,
                      }}
                    />
                    <button
                      className="dsa-btn dsa-btn--ai"
                      onClick={refine}
                      disabled={refining || !refineInput.trim()}
                    >
                      <ViShape size={14}/> {refining ? 'Iterating…' : 'Refine'}
                    </button>
                  </div>
                  <div style={{display:'flex',gap:8,marginTop:10,flexWrap:'wrap'}}>
                    <span style={{font:'400 11px/1.6 var(--font-body)',color:'var(--fg-muted)'}}>Try:</span>
                    {['Make the icons rounder', 'Cooler palette', 'Shorten the copy', 'Add a payment icon', 'Use a darker accent'].map(s => (
                      <button key={s}
                        disabled={refining}
                        onClick={() => setRefineInput(s)}
                        style={{
                          background:'transparent', border:'1px solid var(--border-default)',
                          borderRadius:999, padding:'4px 10px', cursor: refining ? 'not-allowed' : 'pointer',
                          font:'500 11px/1 var(--font-body)', color:'var(--fg-secondary)',
                          opacity: refining ? 0.5 : 1,
                        }}>{s}</button>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </>
        )}

        {error && (
          <div className="dsa-stub" style={{marginTop:14}}>
            <h3>Something went wrong</h3>
            <p>{error}</p>
            <button className="dsa-btn dsa-btn--outline" onClick={reset}>Start over</button>
          </div>
        )}

      </div>
    </>
  );
}

function Stepper({ stage, planning, generating, composing, composerDone, onJumpTo }) {
  const steps = [
    { n: 1, label: 'Brief',    sub: 'Tell Vi what you want' },
    { n: 2, label: 'Plan',     sub: 'Review the decomposition' },
    { n: 3, label: 'Generate', sub: 'Run parallel subtasks' },
    { n: 4, label: 'Compose',  sub: 'Assemble & adopt' },
  ];
  // Determine running step
  let running = 0;
  if (planning && stage === 1) running = 1;
  else if (planning) running = 2;
  else if (generating) running = 3;
  else if (composing) running = 4;

  return (
    <div style={{
      display:'flex', alignItems:'stretch', gap:0, marginBottom:24,
      background:'var(--bg-surface)', border:'1px solid var(--border-default)',
      borderRadius:'var(--r-md)', padding:6, overflow:'hidden',
    }}>
      {steps.map((s, i) => {
        const isActive = s.n === stage;
        const isDone = s.n < stage;
        const isRunning = running === s.n;
        const isClickable = isDone && onJumpTo;
        const color = isActive ? 'var(--accent-gold)'
          : isDone ? 'var(--status-success)'
          : 'var(--fg-muted)';
        return (
          <React.Fragment key={s.n}>
            <button
              type="button"
              onClick={() => isClickable && onJumpTo(s.n)}
              disabled={!isClickable}
              style={{
                flex:1, display:'flex', alignItems:'center', gap:10,
                padding:'10px 14px',
                background: isActive ? 'var(--accent-gold-faint)' : 'transparent',
                border:'none', borderRadius:'var(--r-sm)',
                cursor: isClickable ? 'pointer' : 'default',
                textAlign:'left', minWidth:0,
                transition:'background 150ms var(--ease-out)',
              }}
              title={isClickable ? 'Jump back to this step' : ''}>
              <span style={{
                width:26, height:26, borderRadius:'50%',
                background: isActive ? 'var(--accent-gold)' : isDone ? 'var(--status-success)' : 'transparent',
                border: isActive || isDone ? 'none' : '1.5px solid var(--border-default)',
                color: isActive || isDone ? '#fff' : 'var(--fg-muted)',
                display:'flex', alignItems:'center', justifyContent:'center',
                font:'700 12px/1 var(--font-body)', flex:'none',
                animation: isRunning ? 'dsa-pulse 1.2s ease-in-out infinite' : 'none',
              }}>{isDone ? '✓' : s.n}</span>
              <span style={{minWidth:0,display:'flex',flexDirection:'column'}}>
                <span style={{
                  font:'700 12px/1.1 var(--font-display)',
                  color: isActive ? 'var(--accent-bronze)' : isDone ? 'var(--fg-primary)' : 'var(--fg-muted)',
                  letterSpacing:'0.02em',
                  whiteSpace:'nowrap',overflow:'hidden',textOverflow:'ellipsis',
                }}>{s.label}</span>
                <span style={{
                  font:'400 10px/1.3 var(--font-body)',
                  color:'var(--fg-muted)', marginTop:2,
                  whiteSpace:'nowrap',overflow:'hidden',textOverflow:'ellipsis',
                }}>{s.sub}</span>
              </span>
            </button>
            {i < steps.length - 1 && (
              <span style={{
                alignSelf:'center', flex:'none',
                width:18, height:1,
                background: s.n < stage ? 'var(--status-success)' : 'var(--border-default)',
                margin:'0 2px',
              }}/>
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
}

const SUBTASK_META = {
  'icons-generator':  { tone:'#6E5BBE', label:'Icons generator' },
  'colors-generator': { tone:'#B3793A', label:'Colors generator' },
  'copy-writer':      { tone:'#3A7F6E', label:'Copy writer' },
  'widget-builder':   { tone:'#1F1A12', label:'Widget builder' },
  'wizard-builder':   { tone:'#988058', label:'Wizard builder' },
  'workshop-deck':    { tone:'#E0C010', label:'Deck builder' },
  'workshop-brochure':{ tone:'#E0C010', label:'Brochure builder' },
  'type-builder':     { tone:'#5B4628', label:'Type builder' },
  'composer':         { tone:'var(--accent-bronze)', label:'Composer' },
};

function PlanEditor({ plan, onChangeBrief, onChangeLabel, onRemove }) {
  const others = plan.subtasks.filter(s => s.kind !== 'composer');
  const composer = plan.subtasks.find(s => s.kind === 'composer');
  return (
    <div>
      <div style={{
        display:'grid',
        gridTemplateColumns:`repeat(${Math.min(Math.max(others.length,1), 3)}, 1fr)`,
        gap:10,
      }}>
        {others.map(s => (
          <PlanEditorCard key={s.id} sub={s} onChangeBrief={onChangeBrief} onChangeLabel={onChangeLabel} onRemove={onRemove} removable/>
        ))}
      </div>
      {composer && (
        <>
          <div style={{display:'flex',justifyContent:'center',padding:'6px 0'}}>
            <span style={{width:2,height:18,background:'var(--accent-gold)',opacity:0.5,display:'block'}}/>
          </div>
          <PlanEditorCard sub={composer} onChangeBrief={onChangeBrief} onChangeLabel={onChangeLabel} onRemove={onRemove} removable={false} wide/>
        </>
      )}
    </div>
  );
}

function PlanEditorCard({ sub, onChangeBrief, onChangeLabel, onRemove, removable, wide }) {
  const meta = SUBTASK_META[sub.kind] || { tone:'var(--fg-muted)', label:sub.kind };
  return (
    <div style={{
      background:'var(--bg-surface)', border:'1.5px solid var(--border-default)',
      borderRadius:'var(--r-md)', padding:'12px 14px', width: wide ? '100%' : 'auto',
      display:'flex', flexDirection:'column', gap:6,
    }}>
      <div style={{display:'flex',alignItems:'center',gap:6}}>
        <span style={{
          width:8,height:8,borderRadius:2,background:meta.tone,flex:'none',
        }}/>
        <span style={{
          font:'700 10px/1 var(--font-body)',color:meta.tone,
          letterSpacing:'0.06em',textTransform:'uppercase',
        }}>{meta.label}</span>
        {removable && (
          <button
            type="button"
            onClick={() => onRemove(sub.id)}
            title="Remove this subtask"
            style={{
              marginLeft:'auto', background:'transparent', border:'none',
              color:'var(--fg-muted)', cursor:'pointer', padding:2, lineHeight:1,
              font:'500 14px/1 var(--font-body)',
            }}>×</button>
        )}
      </div>
      <input
        value={sub.label}
        onChange={e => onChangeLabel(sub.id, e.target.value)}
        style={{
          border:'none', background:'transparent', padding:0, outline:'none',
          font:'600 13px/1.2 var(--font-display)', color:'var(--fg-primary)',
          width:'100%',
        }}
      />
      <textarea
        value={sub.brief}
        onChange={e => onChangeBrief(sub.id, e.target.value)}
        rows={wide ? 2 : 3}
        style={{
          border:'1px solid var(--border-default)', borderRadius:'var(--r-sm)',
          background:'var(--bg-canvas)', padding:'8px 10px', outline:'none',
          font:'400 12px/1.45 var(--font-body)', color:'var(--fg-secondary)',
          resize:'vertical', fontFamily:'var(--font-body)', boxSizing:'border-box',
          width:'100%', minHeight:60,
        }}
      />
    </div>
  );
}

function PartsPreview({ plan }) {
  const icons = plan.subtasks.find(s => s.kind === 'icons-generator' && s.result && !s.result.error)?.result;
  const colors = plan.subtasks.find(s => s.kind === 'colors-generator' && s.result && !s.result.error)?.result;
  const copy = plan.subtasks.find(s => s.kind === 'copy-writer' && s.result && !s.result.error)?.result;
  const typeDrafts = plan.subtasks.filter(s => s.kind === 'type-builder' && s.result?.kind === 'type-draft');
  if (!icons && !colors && !copy && !typeDrafts.length) return null;
  return (
    <div style={{
      marginTop:18, padding:16, background:'var(--bg-surface)',
      border:'1px dashed var(--border-default)', borderRadius:'var(--r-md)',
    }}>
      <div style={{font:'700 10px/1 var(--font-body)',color:'var(--fg-muted)',letterSpacing:'0.08em',textTransform:'uppercase',marginBottom:10}}>
        Generated so far
      </div>
      <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16}}>
        {icons && icons.icons && (
          <div>
            <div style={{font:'600 11px/1 var(--font-body)',color:'var(--fg-secondary)',marginBottom:6}}>Icons · {icons.icons.length}</div>
            <div style={{display:'flex',gap:6,flexWrap:'wrap'}}>
              {icons.icons.map((ic, i) => (
                <div key={i} title={ic.name} style={{
                  width:32,height:32,borderRadius:'var(--r-sm)',
                  background:'var(--bg-canvas)',border:'1px solid var(--border-default)',
                  display:'flex',alignItems:'center',justifyContent:'center',
                }}>
                  <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="var(--accent-bronze)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" dangerouslySetInnerHTML={{__html: ic.body}}/>
                </div>
              ))}
            </div>
          </div>
        )}
        {colors && colors.colors && (
          <div>
            <div style={{font:'600 11px/1 var(--font-body)',color:'var(--fg-secondary)',marginBottom:6}}>Colors · {colors.colors.length}</div>
            <div style={{display:'flex',gap:0,borderRadius:'var(--r-sm)',overflow:'hidden',border:'1px solid var(--border-default)'}}>
              {colors.colors.map((c, i) => (
                <div key={i} title={`${c.name} · ${c.hex}`} style={{flex:1,height:32,background:c.hex}}/>
              ))}
            </div>
          </div>
        )}
        {copy && copy.variants && (
          <div style={{gridColumn:'1 / -1'}}>
            <div style={{font:'600 11px/1 var(--font-body)',color:'var(--fg-secondary)',marginBottom:6}}>Copy · {copy.variants.length}</div>
            <div style={{display:'flex',flexDirection:'column',gap:4}}>
              {copy.variants.map((v, i) => (
                <div key={i} style={{
                  font:'400 12px/1.5 var(--font-body)', color:'var(--fg-primary)',
                  padding:'6px 10px', background:'var(--bg-canvas)',
                  border:'1px solid var(--border-default)', borderRadius:'var(--r-sm)',
                }}>{v}</div>
              ))}
            </div>
          </div>
        )}
        {typeDrafts.length > 0 && (
          <div style={{gridColumn:'1 / -1'}}>
            <div style={{font:'600 11px/1 var(--font-body)',color:'var(--fg-secondary)',marginBottom:6}}>New Types · {typeDrafts.length}</div>
            <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fill, minmax(240px, 1fr))',gap:8}}>
              {typeDrafts.map(s => {
                const d = s.result.draft;
                return (
                  <div key={s.id} style={{padding:12,background:'var(--bg-canvas)',border:'1px dashed var(--accent-gold)',borderRadius:'var(--r-sm)'}}>
                    <div style={{display:'flex',alignItems:'center',gap:6,marginBottom:4}}>
                      {window.TypeLayerBadge && <window.TypeLayerBadge layer={d.layer} size="sm"/>}
                      <strong style={{font:'700 12px/1.1 var(--font-display)',color:'var(--fg-primary)'}}>{d.name}</strong>
                    </div>
                    <p style={{margin:0,font:'400 11px/1.4 var(--font-body)',color:'var(--fg-secondary)'}}>{d.description}</p>
                    <button className="dsa-btn dsa-btn--ai dsa-btn--sm" style={{marginTop:8}} onClick={() => {
                      window.CV_TYPES_PROMPT.open(d);
                    }}>
                      <ViShape size={10}/> Review & register
                    </button>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function BuildHowCard({ layer, title, desc }) {
  return (
    <div className="dsa-card">
      <div style={{display:'flex',alignItems:'center',gap:8,marginBottom:6}}>
        <span style={{
          background:'var(--accent-gold-faint)', color:'var(--accent-bronze)',
          font:'700 10px/1 var(--font-body)', letterSpacing:'0.08em', textTransform:'uppercase',
          padding:'4px 8px', borderRadius:'var(--r-sm)',
        }}>Layer {layer}</span>
        <h4 style={{font:'700 14px/1 var(--font-display)',color:'var(--fg-primary)',margin:0}}>{title}</h4>
      </div>
      <p style={{font:'400 12px/1.55 var(--font-body)',color:'var(--fg-secondary)',margin:0}}>{desc}</p>
    </div>
  );
}

function TaskList({ subtasks }) {
  // Composer is always last; non-composers display as parallel row
  const composer = subtasks.find(s => s.kind === 'composer');
  const others = subtasks.filter(s => s.kind !== 'composer');
  return (
    <div>
      <div style={{display:'grid',gridTemplateColumns:`repeat(${Math.max(others.length,1)}, 1fr)`,gap:8,marginBottom: composer ? 10 : 0}}>
        {others.map(s => <TaskNode key={s.id} sub={s}/>)}
      </div>
      {composer && (
        <>
          <div style={{display:'flex',justifyContent:'center',padding:'2px 0'}}>
            <span style={{width:2,height:14,background:'var(--accent-gold-dashed)',display:'block'}}/>
          </div>
          <TaskNode sub={composer} wide/>
        </>
      )}
    </div>
  );
}

function TaskNode({ sub, wide }) {
  const stateColor = sub.status === 'active' ? 'var(--accent-gold)'
    : sub.status === 'done' ? 'var(--status-success)'
    : sub.status === 'blocked' ? 'var(--status-error)'
    : 'var(--fg-muted)';
  return (
    <div style={{
      background: sub.status === 'active' ? 'var(--accent-gold-faint)' : 'var(--bg-surface)',
      borderRadius: 'var(--r-md)',
      border: '1.5px solid ' + (sub.status === 'active' ? 'var(--accent-gold)' : sub.status === 'blocked' ? 'var(--status-error)' : 'var(--border-default)'),
      padding: '12px 14px',
      width: wide ? '100%' : 'auto',
      opacity: sub.status === 'idle' ? 0.55 : 1,
      transition: 'all 200ms var(--ease-out)',
    }}>
      <div style={{display:'flex',alignItems:'center',gap:8}}>
        <span style={{
          width:8, height:8, borderRadius:'50%', background:stateColor,
          animation: sub.status === 'active' ? 'dsa-pulse 1.2s ease-in-out infinite' : 'none',
        }}/>
        <span style={{font:'700 10px/1 var(--font-body)',color:'var(--accent-bronze)',letterSpacing:'0.06em',textTransform:'uppercase'}}>{sub.kind}</span>
      </div>
      <div style={{font:'600 13px/1.2 var(--font-display)',color:'var(--fg-primary)',marginTop:6}}>{sub.label}</div>
      <div style={{font:'400 11px/1.4 var(--font-body)',color:'var(--fg-secondary)',marginTop:4}}>{sub.brief}</div>
    </div>
  );
}

function Output({ plan, brief, onAdoptIcons, onAdoptColors, onSaveAsTemplate, onNav, onOpenInWorkshop, onRefinePart, refining }) {
  const icons = plan.subtasks.find(s => s.kind === 'icons-generator' && s.result && !s.result.error)?.result;
  const colors = plan.subtasks.find(s => s.kind === 'colors-generator' && s.result && !s.result.error)?.result;
  const copy = plan.subtasks.find(s => s.kind === 'copy-writer' && s.result && !s.result.error)?.result;
  const composed = plan.subtasks.find(s => s.kind === 'composer' && s.result && !s.result.error)?.result;
  // Workshop-doc subtask outputs (widget, wizard, deck, brochure)
  const workshopDocResults = plan.subtasks.filter(s => s.result?.kind === 'workshop-doc' && !s.result.error);
  const [saving, setSaving] = useState_b(false);
  const [saved, setSaved] = useState_b(false);

  async function saveTemplate() {
    setSaving(true);
    try {
      // Ask Vi to extract parameters from the brief
      const prompt = `Given this build brief, identify the 1-3 parameters most worth turning into reusable inputs. Replace each in the brief with {{paramKey}} placeholders.

Brief: "${brief}"

Respond as compact JSON only, no prose:
{"name": "<short template name 2-5 words>", "description": "<one-line description>", "pattern": "<brief with {{params}} substituted>", "params":[{"key":"camelCase","label":"Human label","default":"original value"}]}`;
      const reply = await window.CV_AI.complete(prompt);
      let parsed = null;
      try { parsed = JSON.parse(reply); }
      catch {
        const m = String(reply).match(/\{[\s\S]*\}/);
        if (m) { try { parsed = JSON.parse(m[0]); } catch {} }
      }
      if (!parsed) {
        // Fallback: no parameters extracted
        parsed = { name: (composed?.title || 'Untitled template').slice(0, 40), description: composed?.summary || brief.slice(0, 80), pattern: brief, params: [] };
      }
      onSaveAsTemplate({
        id: 'tpl-' + Date.now(),
        name: parsed.name,
        description: parsed.description,
        briefPattern: parsed.pattern || brief,
        params: parsed.params || [],
        savedAt: new Date().toLocaleDateString(),
      });
      setSaved(true);
      window.dsaToast?.(`Saved "${parsed.name}" to Templates`);
    } catch {
      window.dsaToast?.('Save failed');
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="dsa-card" style={{padding: 22}}>
      <div style={{display:'flex',alignItems:'baseline',gap:12,marginBottom:14}}>
        {composed?.title && <h3 style={{font:'700 22px/1.1 var(--font-display)',color:'var(--accent-bronze)',margin:0,letterSpacing:'-0.02em',flex:1}}>{composed.title}</h3>}
        <button
          className={`dsa-btn ${saved ? 'dsa-btn--outline' : 'dsa-btn--ai'} dsa-btn--sm`}
          onClick={saveTemplate} disabled={saving || saved}
        >
          {saved ? '✓ Saved' : saving ? 'Saving…' : <><ViShape size={12}/> Save as template</>}
        </button>
        {!saved && onNav && (
          <button
            className="dsa-btn dsa-btn--primary dsa-btn--sm"
            onClick={async () => { await saveTemplate(); setTimeout(() => onNav('templates'), 200); }}
            disabled={saving}
          >
            Save & open →
          </button>
        )}
      </div>

      {composed?.summary && <p style={{font:'400 13px/1.55 var(--font-body)',color:'var(--fg-secondary)',margin:'0 0 16px'}}>{composed.summary}</p>}

      {/* Live composed preview */}
      {composed?.preview && <ComposedPreview preview={composed.preview} icons={icons?.icons || []} colors={colors?.colors || []} copy={copy?.variants || []}/>}

      {/* Workshop-doc results (widget / wizard / deck / brochure) */}
      {workshopDocResults.length > 0 && (
        <div style={{marginTop: composed?.preview ? 18 : 0, marginBottom: 18}}>
          <div style={{font:'600 11px/1 var(--font-body)',color:'var(--fg-muted)',letterSpacing:'0.08em',textTransform:'uppercase',marginBottom:10}}>
            Workshop docs · {workshopDocResults.length}
          </div>
          <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit, minmax(280px, 1fr))',gap:10}}>
            {workshopDocResults.map(s => (
              <WorkshopDocResult key={s.id} subtask={s} onOpen={onOpenInWorkshop} brief={brief}/>
            ))}
          </div>
        </div>
      )}

      {/* Adoptable parts */}
      <div style={{display:'grid',gridTemplateColumns:icons && colors ? '1fr 1fr' : '1fr', gap:14, marginTop: composed?.preview ? 18 : 0}}>
        {icons && icons.icons && (
          <div>
            <div style={{display:'flex',alignItems:'baseline',marginBottom:8,gap:8}}>
              <span style={{font:'600 11px/1 var(--font-body)',color:'var(--fg-muted)',letterSpacing:'0.08em',textTransform:'uppercase'}}>Generated icons · {icons.icons.length}</span>
              {onRefinePart && <RefineChip scope={{kind:'icons-all'}} onRefine={onRefinePart} disabled={refining} label="Refine all" placeholder="e.g. Make them all rounder"/>}
              <button className="dsa-btn dsa-btn--primary dsa-btn--sm" style={{marginLeft:'auto'}} onClick={() => { onAdoptIcons(icons.icons); window.dsaToast?.(`Adopted ${icons.icons.length} icons`); }}>Adopt all</button>
            </div>
            <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fill, minmax(80px, 1fr))',gap:6}}>
              {icons.icons.map((ic, i) => (
                <div key={i} style={{background:'var(--bg-canvas)',borderRadius:'var(--r-sm)',padding:'10px 6px 6px',display:'flex',flexDirection:'column',alignItems:'center',gap:6,position:'relative'}} className="dsa-part-tile">
                  <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="var(--accent-bronze)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" dangerouslySetInnerHTML={{__html: ic.body}}/>
                  <div style={{font:'500 10px/1.2 var(--font-mono)',color:'var(--fg-secondary)',textAlign:'center'}}>{ic.name}</div>
                  {onRefinePart && <RefineDot scope={{kind:'icon',target:ic.name}} onRefine={onRefinePart} disabled={refining} placeholder={`Change "${ic.name}"`}/>}
                </div>
              ))}
            </div>
          </div>
        )}

        {colors && colors.colors && (
          <div>
            <div style={{display:'flex',alignItems:'baseline',marginBottom:8,gap:8}}>
              <span style={{font:'600 11px/1 var(--font-body)',color:'var(--fg-muted)',letterSpacing:'0.08em',textTransform:'uppercase'}}>Generated colors · {colors.colors.length}</span>
              {onRefinePart && <RefineChip scope={{kind:'colors-all'}} onRefine={onRefinePart} disabled={refining} label="Refine all" placeholder="e.g. Cooler / warmer / more saturated"/>}
              <button className="dsa-btn dsa-btn--primary dsa-btn--sm" style={{marginLeft:'auto'}} onClick={() => { onAdoptColors(colors.colors.map(c => ({ ...c, group: colors.group || 'Build' }))); window.dsaToast?.(`Adopted ${colors.colors.length} colors`); }}>Adopt all</button>
            </div>
            <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fill, minmax(110px, 1fr))',gap:6}}>
              {colors.colors.map((c, i) => (
                <div key={i} style={{background:'var(--bg-canvas)',borderRadius:'var(--r-sm)',overflow:'hidden',position:'relative'}} className="dsa-part-tile">
                  <div style={{height:36,background:c.hex}}/>
                  <div style={{padding:'6px 8px'}}>
                    <div style={{font:'600 11px/1.1 var(--font-body)',color:'var(--fg-primary)'}}>{c.name}</div>
                    <div style={{font:'500 10px/1 var(--font-mono)',color:'var(--fg-muted)',marginTop:2}}>{c.hex?.toUpperCase()}</div>
                  </div>
                  {onRefinePart && <RefineDot scope={{kind:'color',target:c.name}} onRefine={onRefinePart} disabled={refining} placeholder={`Change "${c.name}"`}/>}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {copy && copy.variants && (
        <div style={{marginTop:18}}>
          <div style={{display:'flex',alignItems:'baseline',marginBottom:8,gap:8}}>
            <span style={{font:'600 11px/1 var(--font-body)',color:'var(--fg-muted)',letterSpacing:'0.08em',textTransform:'uppercase'}}>Copy variants · {copy.variants.length}</span>
            {onRefinePart && <RefineChip scope={{kind:'copy-all'}} onRefine={onRefinePart} disabled={refining} label="Refine all" placeholder="e.g. Shorter, warmer, more confident"/>}
          </div>
          <div style={{display:'flex',flexDirection:'column',gap:6}}>
            {copy.variants.map((v, i) => (
              <div key={i} style={{background:'var(--bg-canvas)',borderRadius:'var(--r-sm)',padding:'10px 12px',display:'flex',alignItems:'flex-start',gap:10,position:'relative'}}>
                <span style={{font:'700 10px/1 var(--font-body)',color:'var(--accent-bronze)',letterSpacing:'0.08em',textTransform:'uppercase',flex:'none',paddingTop:3}}>v{i+1}</span>
                <span style={{flex:1,font:'400 13px/1.5 var(--font-body)',color:'var(--fg-primary)'}}>{v}</span>
                {onRefinePart && <RefineChip scope={{kind:'copy',target:i}} onRefine={onRefinePart} disabled={refining} label="↻" placeholder={`Change variant ${i+1}`}/>}
                <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" onClick={() => { navigator.clipboard?.writeText(v); window.dsaToast?.('Copied'); }}>Copy</button>
              </div>
            ))}
          </div>
        </div>
      )}

      {onRefinePart && (
        <div style={{marginTop:18,paddingTop:14,borderTop:'1px solid var(--border-faint)',display:'flex',gap:10,alignItems:'center'}}>
          <span style={{font:'400 12px/1.4 var(--font-body)',color:'var(--fg-muted)',flex:1}}>
            Only the composed preview not landing? Re-render it without touching the parts.
          </span>
          <RefineChip scope={{kind:'composed'}} onRefine={onRefinePart} disabled={refining} label="↻ Refine composition" placeholder="e.g. Use variant 2 for the headline"/>
        </div>
      )}
    </div>
  );
}

function ComposedPreview({ preview, icons, colors, copy }) {
  // The composer returns a `preview` string that describes how to render.
  // For simplicity render a generic preview card: a hero with primary color, stats with icons, copy text.
  const primary = (colors[0]?.hex) || 'var(--accent-gold)';
  const accent = (colors[1]?.hex) || 'var(--accent-bronze)';
  const heading = copy[0] || preview?.heading || 'Composed preview';
  const body = copy[1] || preview?.body || '';
  return (
    <div style={{
      background: 'var(--bg-canvas)',
      borderRadius: 'var(--r-lg)',
      padding: '18px 20px 20px',
      border: '1.5px solid ' + accent,
    }}>
      <div style={{display:'flex',alignItems:'center',gap:8,marginBottom:12}}>
        {icons.slice(0,4).map((ic, i) => (
          <div key={i} style={{
            width:36, height:36, borderRadius:'50%',
            border:'1.5px solid ' + primary,
            display:'flex', alignItems:'center', justifyContent:'center',
            color: primary,
          }}>
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" dangerouslySetInnerHTML={{__html: ic.body}}/>
          </div>
        ))}
      </div>
      <h4 style={{font:'700 18px/1.2 var(--font-display)',color:'var(--fg-primary)',margin:'0 0 6px',letterSpacing:'-0.01em'}}>{heading}</h4>
      <p style={{font:'400 13px/1.55 var(--font-body)',color:'var(--fg-secondary)',margin:0}}>{body}</p>
      {colors.length > 0 && (
        <div style={{display:'flex',gap:4,marginTop:14}}>
          {colors.map((c, i) => (
            <div key={i} style={{flex:1,height:8,borderRadius:2,background:c.hex}} title={c.name}/>
          ))}
        </div>
      )}
    </div>
  );
}

function WorkshopDocResult({ subtask, onOpen, brief }) {
  const result = subtask.result || {};
  const docType = result.docType;
  const payload = result.payload || {};
  const title = result.title || subtask.label || 'Workshop doc';
  // Build a thumbnail
  let preview = null;
  if (docType === 'widget' && window.WidgetRender) {
    preview = (
      <div style={{transform:'scale(0.55)',transformOrigin:'top left',width:'182%',pointerEvents:'none'}}>
        <window.WidgetRender doc={payload} hovered={false}/>
      </div>
    );
  } else if (docType === 'wizard') {
    preview = (
      <div style={{display:'flex',flexDirection:'column',gap:4,padding:'4px 0'}}>
        {(payload.steps || []).slice(0, 5).map((st, i) => (
          <div key={i} style={{display:'flex',alignItems:'center',gap:8,font:'500 11px/1.2 var(--font-body)',color:'var(--fg-primary)'}}>
            <span style={{width:18,height:18,borderRadius:'50%',background:'var(--accent-gold)',color:'var(--fg-primary)',display:'flex',alignItems:'center',justifyContent:'center',font:'700 9px/1 var(--font-mono)'}}>{i + 1}</span>
            <span>{st.title}</span>
            <span style={{font:'500 9px/1 var(--font-mono)',color:'var(--fg-muted)',letterSpacing:'0.08em',textTransform:'uppercase',marginLeft:'auto'}}>{st.kind}</span>
          </div>
        ))}
      </div>
    );
  } else if (docType === 'deck' || docType === 'brochure') {
    preview = (
      <div style={{display:'flex',flexDirection:'column',gap:6,padding:'4px 0'}}>
        {(payload.pages || []).slice(0, 5).map((p, i) => (
          <div key={i} style={{display:'flex',alignItems:'center',gap:8,font:'500 11px/1.2 var(--font-body)',color:'var(--fg-primary)'}}>
            <span style={{width:14,height:14,background:'var(--accent-gold)',transform:'rotate(45deg)',display:'inline-block',flex:'none'}}/>
            <span style={{font:'700 italic 11px/1 var(--font-display)',color:'var(--accent-bronze)'}}>{i + 1}.</span>
            <span style={{overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>{p.title}</span>
            <span style={{font:'500 9px/1 var(--font-mono)',color:'var(--fg-muted)',marginLeft:'auto'}}>{(p.sections || []).length}b</span>
          </div>
        ))}
      </div>
    );
  }

  function open() {
    if (!onOpen) { window.dsaToast?.('Workshop open handler not wired'); return; }
    // Build a full Workshop doc shape and route via App's runWorkshopTemplate
    const id = 'doc-' + Date.now() + '-' + Math.random().toString(36).slice(2, 5);
    const draftBase = {
      id, type: docType,
      title: title || brief.slice(0, 40),
      pages: payload.pages || [{ id: 'p-' + Date.now(), title: docType, kind: docType, sections: [] }],
      theme: 'editorial',
      createdAt: Date.now(),
    };
    // Merge extra top-level fields (widget/wizard)
    const merged = { ...draftBase, ...payload };
    onOpen(merged);
  }

  return (
    <div style={{
      background:'var(--bg-canvas)',border:'1px solid var(--border-faint)',
      borderRadius:'var(--r-md)', padding:'12px 14px',
      display:'flex',flexDirection:'column',gap:8,
      overflow:'hidden',
    }}>
      <div style={{display:'flex',alignItems:'center',gap:6}}>
        <span style={{font:'700 9px/1 var(--font-body)',color:'var(--accent-bronze)',letterSpacing:'0.1em',textTransform:'uppercase',padding:'3px 7px',background:'var(--accent-gold-50)',borderRadius:'var(--r-pill)'}}>
          {docType}
        </span>
        <h4 style={{font:'700 13px/1.2 var(--font-display)',color:'var(--fg-primary)',letterSpacing:'-0.01em',margin:0,flex:1,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>{title}</h4>
      </div>
      <div style={{maxHeight:170,overflow:'hidden',background:'var(--bg-surface)',borderRadius:'var(--r-sm)',border:'1px solid var(--border-faint)',padding:8}}>
        {preview}
      </div>
      <button className="dsa-btn dsa-btn--primary dsa-btn--sm" onClick={open} style={{alignSelf:'flex-start'}}>
        Open in Workshop →
      </button>
    </div>
  );
}

async function runSubtask(s, mainBrief) {
  if (s.kind === 'icons-generator') return runIcons(s.brief, mainBrief);
  if (s.kind === 'colors-generator') return runColors(s.brief, mainBrief);
  if (s.kind === 'copy-writer') return runCopy(s.brief, mainBrief);
  if (s.kind === 'widget-builder')  return runWidget(s.brief, mainBrief);
  if (s.kind === 'wizard-builder')  return runWizard(s.brief, mainBrief);
  if (s.kind === 'workshop-deck')   return runWorkshopDoc('deck',     s.brief, mainBrief);
  if (s.kind === 'workshop-brochure') return runWorkshopDoc('brochure', s.brief, mainBrief);
  if (s.kind === 'type-builder')    return runTypeBuilder(s.brief, mainBrief);
  throw new Error('Unknown subtask kind: ' + s.kind);
}

async function runTypeBuilder(subBrief, mainBrief) {
  if (!window.CV_TYPES_VI) throw new Error('Type Registry not loaded');
  // Heuristic: infer the layer from the brief
  const b = (subBrief + ' ' + (mainBrief || '')).toLowerCase();
  let layer = null;
  if (/widget|tile|dashboard/.test(b)) layer = 'surface';
  else if (/system|composition/.test(b)) layer = 'system';
  else if (/step|wizard step|onboarding step/.test(b)) layer = 'surface';
  else if (/block|kpi tile|sparkline|hero block/.test(b)) layer = 'block';
  else if (/wizard|flow|onboarding|funnel/.test(b)) layer = 'doc';
  else if (/deck|brochure|document/.test(b)) layer = 'doc';
  const draft = await window.CV_TYPES_VI.proposeType({ brief: subBrief || mainBrief || '', layerHint: layer });
  return { kind: 'type-draft', draft, title: draft.name };
}

async function runWidget(subBrief, mainBrief) {
  if (!window.viDraftWidget) throw new Error('Widget engine not loaded');
  const draft = await window.viDraftWidget(subBrief || mainBrief || '', null, null);
  return { kind: 'workshop-doc', docType: 'widget', payload: draft, title: draft?.data?.title || 'Widget' };
}

async function runWizard(subBrief, mainBrief) {
  if (!window.viDraftWizard) throw new Error('Wizard engine not loaded');
  const draft = await window.viDraftWizard(subBrief || mainBrief || '', null);
  return { kind: 'workshop-doc', docType: 'wizard', payload: draft, title: draft?.title || 'Wizard' };
}

async function runWorkshopDoc(type, subBrief, mainBrief) {
  // Use Workshop's viDraft (deck/brochure) — produces an array of pages
  const fn = window.WS_viDraft || null;
  if (!fn) {
    // Fallback: produce a single blank page
    return { kind: 'workshop-doc', docType: type, payload: { pages: [{ id: 'p-' + Date.now(), title: 'Page 1', kind: 'content', sections: [] }] }, title: subBrief.slice(0, 40) };
  }
  const pages = await fn(type, subBrief || mainBrief || '');
  return { kind: 'workshop-doc', docType: type, payload: { pages }, title: (subBrief || mainBrief || '').slice(0, 50) };
}

async function runIcons(subBrief, mainBrief) {
  const prompt = `You are the ConceptV icons specialist. Generate icons in the brand style: 24×24 viewBox, 1.5 px stroke, rounded caps and joins, no fills (use stroke="currentColor", fill="none"), geometric/architectural.

Main brief: ${mainBrief}
Your job: ${subBrief}

Generate the icons. Each: a short kebab-case name + the inner SVG body markup (no <svg> wrapper, no fill/stroke attributes on elements).

Respond as compact JSON only, no prose:
{"icons": [{"name":"...","body":"<path d=\\"...\\"/>..."}, ...]}`;
  const reply = await window.CV_AI.execute('build.icons', { params: { prompt }, surface: 'build' });
  return parseJson(reply);
}

async function runColors(subBrief, mainBrief) {
  const prompt = `You are the ConceptV colors specialist. The brand sits on warm ivory (#FBF7EC) with near-black ink (#1F1A12), gold #E0C010, bronze #988058. Warm-shifted only, no cool greys.

Main brief: ${mainBrief}
Your job: ${subBrief}

Generate a coherent palette.

Respond as compact JSON only, no prose:
{"group":"<short group name>","colors":[{"name":"...","hex":"#...","role":"..."}, ...]}`;
  const reply = await window.CV_AI.execute('build.colors', { params: { prompt }, surface: 'build' });
  return parseJson(reply);
}

async function runCopy(subBrief, mainBrief) {
  const prompt = `You are the ConceptV voice specialist. ${window.CV_AI.get('voice.conceptv').text} Imperative for actions; calm and precise.

Main brief: ${mainBrief}
Your job: ${subBrief}

Generate 1-3 short copy variants.

Respond as compact JSON only, no prose:
{"variants":["...","...","..."]}`;
  const reply = await window.CV_AI.execute('build.copy', { params: { prompt }, surface: 'build' });
  return parseJson(reply);
}

async function runComposer(s, mainBrief, results) {
  const summary = results.map(r => {
    if (r.kind === 'icons-generator') return `Icons available: ${(r.result?.icons || []).map(i => i.name).join(', ') || 'none'}`;
    if (r.kind === 'colors-generator') return `Colors available: ${(r.result?.colors || []).map(c => `${c.name} ${c.hex}`).join(', ') || 'none'}`;
    if (r.kind === 'copy-writer') return `Copy variants:\n${(r.result?.variants || []).map((v,i) => `${i+1}. ${v}`).join('\n')}`;
    return '';
  }).filter(Boolean).join('\n\n');
  const prompt = `You are the ConceptV composer. Assemble a final output from the parts below.

Main brief: ${mainBrief}
Your job: ${s.brief}

Available parts:
${summary || '(no parts generated)'}

Compose a final preview spec. Output a JSON object:
{"title":"<short title>","summary":"<one-sentence description of what was built>","preview":{"heading":"<headline>","body":"<one paragraph of body copy>"}}

The heading and body should USE the copy variants if available. Be concrete and on-brand.

Respond as compact JSON only, no prose, no markdown fences.`;
  const reply = await window.CV_AI.complete(prompt);
  return parseJson(reply);
}

// ============================================================
// RefineChip + RefineDot — small inline UI for per-part refinement
// ============================================================
function RefineChip({ scope, onRefine, disabled, label, placeholder }) {
  const [open, setOpen] = React.useState(false);
  const [val, setVal] = React.useState('');
  function go() {
    if (!val.trim()) return;
    onRefine(scope, val.trim());
    setVal(''); setOpen(false);
  }
  return (
    <span style={{position:'relative',display:'inline-flex'}}>
      <button
        onClick={() => setOpen(o => !o)}
        disabled={disabled}
        style={{
          background:'transparent', border:'1px solid var(--accent-gold)',
          color:'var(--fg-primary)', borderRadius:999, padding:'4px 10px',
          font:'500 11px/1 var(--font-body)', cursor: disabled ? 'not-allowed' : 'pointer',
          display:'inline-flex',alignItems:'center',gap:4,
          opacity: disabled ? 0.5 : 1,
        }}>
        <ViShape size={11}/> {label}
      </button>
      {open && (
        <div style={{
          position:'absolute',top:'calc(100% + 6px)',right:0,zIndex:50,
          background:'var(--bg-surface)',border:'1.5px solid var(--accent-gold)',
          borderRadius:'var(--r-md)',padding:10,boxShadow:'var(--shadow-pop)',
          width:280,
        }}>
          <textarea
            autoFocus value={val} onChange={e => setVal(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); go(); } if (e.key === 'Escape') setOpen(false); }}
            placeholder={placeholder} rows="2"
            style={{
              width:'100%',border:'1px solid var(--border-default)',borderRadius:'var(--r-sm)',
              padding:'7px 9px',outline:'none',resize:'none',
              font:'400 12px/1.4 var(--font-body)',color:'var(--fg-primary)',
              background:'var(--bg-canvas)',fontFamily:'var(--font-body)',boxSizing:'border-box',
            }}
          />
          <div style={{display:'flex',gap:6,marginTop:8,justifyContent:'flex-end'}}>
            <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" onClick={() => setOpen(false)}>Cancel</button>
            <button className="dsa-btn dsa-btn--ai dsa-btn--sm" onClick={go} disabled={!val.trim()}><ViShape size={11}/> Refine</button>
          </div>
        </div>
      )}
    </span>
  );
}

function RefineDot({ scope, onRefine, disabled, placeholder }) {
  const [open, setOpen] = React.useState(false);
  const [val, setVal] = React.useState('');
  function go() {
    if (!val.trim()) return;
    onRefine(scope, val.trim());
    setVal(''); setOpen(false);
  }
  return (
    <>
      <button
        onClick={() => setOpen(o => !o)}
        disabled={disabled}
        title="Refine just this one"
        style={{
          position:'absolute',top:4,right:4,
          width:18,height:18,borderRadius:'50%',
          background:'var(--accent-gold)',border:'none',cursor: disabled ? 'not-allowed' : 'pointer',
          color:'var(--fg-primary)',font:'700 11px/1 var(--font-body)',
          display:'flex',alignItems:'center',justifyContent:'center',
          opacity: disabled ? 0.4 : 0.85, padding:0, zIndex:2,
        }}>↻</button>
      {open && (
        <div style={{
          position:'absolute',top:24,right:0,zIndex:50,
          background:'var(--bg-surface)',border:'1.5px solid var(--accent-gold)',
          borderRadius:'var(--r-md)',padding:10,boxShadow:'var(--shadow-pop)',
          width:240,textAlign:'left',
        }} onClick={e => e.stopPropagation()}>
          <textarea
            autoFocus value={val} onChange={e => setVal(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); go(); } if (e.key === 'Escape') setOpen(false); }}
            placeholder={placeholder} rows="2"
            style={{
              width:'100%',border:'1px solid var(--border-default)',borderRadius:'var(--r-sm)',
              padding:'6px 8px',outline:'none',resize:'none',
              font:'400 11px/1.4 var(--font-body)',color:'var(--fg-primary)',
              background:'var(--bg-canvas)',fontFamily:'var(--font-body)',boxSizing:'border-box',
            }}
          />
          <div style={{display:'flex',gap:6,marginTop:6,justifyContent:'flex-end'}}>
            <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" onClick={() => setOpen(false)}>Cancel</button>
            <button className="dsa-btn dsa-btn--ai dsa-btn--sm" onClick={go} disabled={!val.trim()}>Refine</button>
          </div>
        </div>
      )}
    </>
  );
}

function parseJsonLoose(reply) {
  try { return JSON.parse(reply); } catch {}
  const m = String(reply || '').match(/\{[\s\S]*\}/);
  if (m) { try { return JSON.parse(m[0]); } catch {} }
  return null;
}

function parseJson(reply) {
  let parsed = null;
  try { parsed = JSON.parse(reply); }
  catch {
    const m = String(reply).match(/\{[\s\S]*\}/);
    if (m) { try { parsed = JSON.parse(m[0]); } catch {} }
    if (!parsed) {
      const arr = String(reply).match(/\[[\s\S]*\]/);
      if (arr) { try { parsed = JSON.parse(arr[0]); } catch {} }
    }
  }
  if (!parsed) throw new Error('Could not parse response');
  return parsed;
}

window.Build = Build;
