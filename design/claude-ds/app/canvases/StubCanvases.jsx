// canvases/StubCanvases.jsx — placeholder canvases for surfaces not yet built
const STUB_DEFS = {
  type: {
    title: 'Type',
    sub: 'Your typographic system — fonts, scale, leading, tracking, and pairings.',
    desc: "Manage the brand's faces and ramp.",
    features: [
      'Inspect & adjust the Sora + DM Sans scale across display, headlines, body, captions',
      'Generate alternative pairings → A/B test against existing components',
      'Upload custom fonts to replace the substitutes',
      'Auto-check minimum sizes against your component patterns',
    ],
  },
  logos: {
    title: 'Logos & marks',
    sub: 'Wordmark, V-mark, and lockups across surfaces and contexts.',
    desc: 'A single home for every logo variation.',
    features: [
      'Upload new lockups → Vi tags by light / dark / mono / colour automatically',
      'See clear-space rules and minimum sizes side-by-side',
      "Generate context-aware variants (favicon, social avatar, signature)",
      'Co-brand presets — pair the ConceptV mark with partner logos',
    ],
  },
  imagery: {
    title: 'Imagery',
    sub: 'Photography, renders, and illustration styles.',
    desc: 'Curate the visual mood of every output.',
    features: [
      'Tag photos by mood, lighting, palette match, and architectural subject',
      "Detect off-brand uploads automatically (cold tones, harsh light, etc.)",
      'Generate alternate crops + treatments for hero, card, and thumbnail uses',
      'Preview how an image looks across the brand surfaces before adopting',
    ],
  },
  components: {
    title: 'Components',
    sub: 'Buttons, inputs, cards, dropzones — every reusable pattern.',
    desc: 'Browse, generate, and refine components from a single canvas.',
    features: [
      'Render every component in every state (default / hover / active / disabled)',
      'Generate a new variant — describe what you need, Vi proposes JSX + CSS',
      'See where each component is used across UI kits',
      'Audit for accessibility (focus rings, contrast, hit targets)',
    ],
  },
  templates: {
    title: 'Templates',
    sub: 'Slide decks, brochures, landing pages, and email layouts.',
    desc: 'Pre-composed surfaces that pull from the entire system.',
    features: [
      'Pitch-deck template with title / section-header / comparison / quote slides',
      'A4 brochure template — multi-page with header / hero / spec / contact',
      'Email template with the Voice rules baked into every block',
      'Generate a new template from a brief — Vi assembles the right components',
    ],
  },
  voice: {
    title: 'Voice & tone',
    sub: "Sentence-case, second-person, no exclamation marks. Concrete examples and a rewriter.",
    desc: 'The brand\'s language, made operational.',
    features: [
      "Audit any block of copy against your voice rules — Vi flags violations",
      'Rewrite paste-in text in the ConceptV voice in one click',
      'Vocabulary anchors (Hub, Linked Hubs, Capture, Vi, …) with examples',
      "Generate context-specific tone variants — error vs success vs onboarding",
    ],
  },
};

function StubCanvas({ id }) {
  const def = STUB_DEFS[id];
  if (!def) return <div>Unknown canvas: {id}</div>;
  return (
    <>
      <CanvasHeader title={def.title} sub={def.sub}/>
      <div className="dsa-canvas-body">
        <div className="dsa-stub">
          <h3>{def.desc}</h3>
          <p>This canvas is scaffolded but not fully built out yet. It will work just like Icons and Colors — gallery on the left, Vi generation, drop-zone for new uploads, applied to the rest of the system automatically.</p>
          <div className="features">
            {def.features.map((f, i) => (
              <div className="feat" key={i}><span>◆</span><span>{f}</span></div>
            ))}
          </div>
          <div style={{display:'flex',gap:8,justifyContent:'center'}}>
            <button className="dsa-btn dsa-btn--ai"><ViShape size={14}/> Ask Vi to build this canvas</button>
            <button className="dsa-btn dsa-btn--outline">Skip · view another</button>
          </div>
        </div>
      </div>
    </>
  );
}

window.StubCanvas = StubCanvas;
