// canvases/workshop/Layouts.jsx — slide layout templates + theme/motif system
// A layout = a named arrangement of blocks for one slide.
// A motif  = a slide background recipe (renders behind the block content).
// A theme  = a set of motifs that map onto slide kinds, giving the deck a coherent visual rhythm.

// ============================================================
// Slide kinds
// ============================================================
window.WS_KINDS = ['title', 'section', 'content', 'image', 'quote', 'stats', 'closing'];

// ============================================================
// Layout templates — sections array for each layout id
// ============================================================
window.WS_LAYOUTS = {
  blank: {
    name: 'Blank',
    kind: 'content',
    desc: 'Start from scratch.',
    icon: 'plus',
    forTypes: ['deck', 'brochure'],
    build: () => [],
  },
  title: {
    name: 'Title',
    kind: 'title',
    desc: 'Hero headline with eyebrow & subhead. Use for slide 1.',
    icon: 'star',
    forTypes: ['deck'],
    build: () => [
      { kind: 'headline', data: { eyebrow: 'ConceptV', text: 'Lead with a strong statement.' } },
      { kind: 'body',     data: { text: 'Set the context in one or two sentences. Plain, calm, declarative.' } },
    ],
  },
  section: {
    name: 'Section header',
    kind: 'section',
    desc: 'Marks a new chapter inside the deck.',
    icon: 'tag',
    forTypes: ['deck'],
    build: () => [
      { kind: 'headline', data: { eyebrow: 'Part 02', text: 'Section name.' } },
    ],
  },
  content: {
    name: 'Heading + body',
    kind: 'content',
    desc: 'Heading on top, paragraph below.',
    icon: 'document',
    forTypes: ['deck', 'brochure'],
    build: () => [
      { kind: 'headline', data: { eyebrow: '', text: 'A focused idea.' } },
      { kind: 'body',     data: { text: 'Explain in two or three lines. The brand voice is sentence case, second person, no exclamation marks.' } },
    ],
  },
  bullets: {
    name: 'Stat trio',
    kind: 'stats',
    desc: 'Three or four big numbers with labels.',
    icon: 'pie-chart',
    forTypes: ['deck', 'brochure'],
    build: () => [
      { kind: 'headline', data: { eyebrow: 'Why', text: 'Three reasons it works.' } },
      { kind: 'stats',    data: { items: [
        { v: '10×', l: 'Faster turnaround' },
        { v: '80%', l: 'Less revision' },
        { v: '24/7', l: 'Real-time updates' },
      ] } },
    ],
  },
  icons: {
    name: 'Icon row',
    kind: 'content',
    desc: 'Four iconic concepts in a row.',
    icon: 'star',
    forTypes: ['deck', 'brochure'],
    build: () => [
      { kind: 'headline', data: { eyebrow: '', text: 'Four moving parts.' } },
      { kind: 'icons',    data: { items: [
        { icon: 'house', label: 'Properties' },
        { icon: 'people', label: 'Stakeholders' },
        { icon: 'network', label: 'Engine' },
        { icon: 'browser', label: 'Outputs' },
      ] } },
    ],
  },
  hero: {
    name: 'Image + text',
    kind: 'image',
    desc: 'Big image, paragraph alongside.',
    icon: 'image',
    forTypes: ['deck', 'brochure'],
    build: () => [
      { kind: 'hero', data: { eyebrow: 'Spotlight', headline: 'A real example.', body: 'Anchor the abstract with one concrete instance.', cta: 'Read the case', imageLabel: 'Spotlight image' } },
    ],
  },
  quote: {
    name: 'Big quote',
    kind: 'quote',
    desc: 'A single statement that lands.',
    icon: 'chat',
    forTypes: ['deck', 'brochure'],
    build: () => [
      { kind: 'quote', data: { text: 'A short, opinionated statement that lands.', who: 'Attribution · role' } },
    ],
  },
  callout: {
    name: 'Callout + body',
    kind: 'content',
    desc: 'Emphasised callout above supporting text.',
    icon: 'lightbulb',
    forTypes: ['deck', 'brochure'],
    build: () => [
      { kind: 'callout', data: { label: 'Why now', text: 'The thing that changed that makes this the moment.' } },
      { kind: 'body',    data: { text: 'Continue with the context, briefly.' } },
    ],
  },
  closing: {
    name: 'Closing',
    kind: 'closing',
    desc: 'CTA + contact at the end of the deck.',
    icon: 'check',
    forTypes: ['deck'],
    build: () => [
      { kind: 'headline', data: { eyebrow: 'Next', text: 'Let\'s talk.' } },
      { kind: 'button',   data: { text: 'Schedule a walkthrough →' } },
    ],
  },
  process: {
    name: 'Staged process',
    kind: 'content',
    desc: 'Headline + three stages connected by dashed arrows. Inspired by the staged delivery diagram.',
    icon: 'path-flow',
    forTypes: ['deck', 'brochure'],
    build: () => [
      { kind: 'headline', data: { eyebrow: 'How it works', text: 'Three stages from concept to delivery.' } },
      { kind: 'process',  data: { steps: [
        { stage: 'Stage 1', title: 'Mobilisation',           body: 'Placeholders, basic visual quality. 1–2 weeks.' },
        { stage: 'Stage 2', title: 'Definition',             body: 'Some elements defined, improved visual quality.' },
        { stage: 'Stage 3', title: 'Final output',           body: 'Renders, brochures, and marketing collateral.' },
      ] } },
    ],
  },
  showcase: {
    name: 'Image grid',
    kind: 'image',
    desc: 'Headline + 3 image placeholders. Use for portfolios, project galleries.',
    icon: 'image-stack',
    forTypes: ['deck', 'brochure'],
    build: () => [
      { kind: 'headline',  data: { eyebrow: 'Spotlight', text: 'A look at recent work.' } },
      { kind: 'imageGrid', data: { items: [
        { label: 'Aerial render' },
        { label: 'Interior detail' },
        { label: 'Floor plan' },
      ] } },
    ],
  },
  threeFeatures: {
    name: 'Three-card feature',
    kind: 'stats',
    desc: 'The ConceptV signature: three large soft-gold cards with bronze titles and oversized gold stats.',
    icon: 'pie-chart',
    forTypes: ['deck', 'brochure'],
    build: () => [
      { kind: 'headline',     data: { eyebrow: 'Industry snapshot', text: 'Three things the data tells us.' } },
      { kind: 'featureCards', data: { items: [
        { title: 'Top drivers',  stat: '70%', body: 'Achieving greater accuracy and trustworthiness.' },
        { title: 'Top barriers', stat: '67%', body: 'High cost of software and licenses.' },
        { title: 'Why fail',     stat: '36%', body: 'Poor fit with current practices.' },
      ] } },
    ],
  },
  funnel: {
    name: 'Sales funnel',
    kind: 'content',
    desc: 'Horizontal funnel — research → developers → hub → repeat sales → awareness, with cycle-back duration.',
    icon: 'path-flow',
    forTypes: ['deck'],
    build: () => [
      { kind: 'headline', data: { eyebrow: 'Go-to-market', text: 'How customers find us, and stay.' } },
      { kind: 'funnel',   data: { steps: [
        { top: 'Research',  label: 'Networks',     bot: 'Referrals',    shape: 'card' },
        { top: 'Architects', label: 'Developers',  bot: 'Designers',    shape: 'card' },
        { top: '',           label: 'Virtual Hubs', bot: '',            shape: 'hex' },
        { top: 'Onsellers',  label: 'Repeat sales', bot: 'Subscribers', shape: 'card' },
        { top: '',           label: 'Organic awareness', bot: '',       shape: 'circle' },
      ], cycle: '3 to 6 months' } },
    ],
  },
  systemMap: {
    name: 'System map',
    kind: 'content',
    desc: 'Central hub with branching tagged children — for platform overviews and entity diagrams.',
    icon: 'network',
    forTypes: ['deck'],
    build: () => [
      { kind: 'headline',  data: { eyebrow: 'Platform', text: 'What sits inside a project.' } },
      { kind: 'tagCluster', data: {
        hub: 'Project master info',
        hubIcon: 'database',
        branches: [
          { side: 'left', items: [
            { icon: 'tag',      label: 'Brand Kit' },
            { icon: 'document', label: 'Files' },
            { icon: 'people',   label: 'Project team' },
          ] },
          { side: 'right', items: [
            { icon: 'link',  label: 'Hub Link' },
            { icon: 'image', label: 'Gallery Assets' },
            { icon: 'edit',  label: 'Project Description' },
            { icon: 'pie-chart', label: 'Analytics' },
          ] },
        ],
      } },
    ],
  },
  bigQuote: {
    name: 'Pull quote',
    kind: 'quote',
    desc: 'Editorial pull quote with oversized opening mark. Use for testimonials and statements that should land hard.',
    icon: 'chat-double',
    forTypes: ['deck', 'brochure'],
    build: () => [
      { kind: 'pullquote', data: {
        lead: 'ConceptV turned a six-month sales cycle into six weeks — and we sold the next stage off-plan.',
        who: 'Project Director · multi-stakeholder build',
      } },
    ],
  },
  metricSet: {
    name: 'Metric set',
    kind: 'stats',
    desc: 'Four metrics on a single rule-bracketed strip. Use under a headline.',
    icon: 'pie-chart',
    forTypes: ['deck', 'brochure'],
    build: () => [
      { kind: 'headline',   data: { eyebrow: 'By the numbers', text: 'What changes when teams adopt ConceptV.' } },
      { kind: 'metricRow',  data: { items: [
        { v: '5+',  l: 'stakeholder types coordinated' },
        { v: '10×', l: 'faster sign-off cycles' },
        { v: '80%', l: 'less rework' },
        { v: '24/7', l: 'real-time updates' },
      ] } },
      { kind: 'body', data: { text: 'Numbers reflect the median across multi-stakeholder Stage-3 deliveries in 2023-2024.' } },
    ],
  },
  pitchDeckPage: {
    name: 'Pitch slide',
    kind: 'content',
    desc: 'Inspo: title → bullets → small icon strip → highlight card. Matches deck pages 02-04.',
    icon: 'document',
    forTypes: ['deck'],
    build: () => [
      { kind: 'headline',    data: { eyebrow: '', text: "Property design and construction is a complex undertaking." } },
      { kind: 'bullets',     data: { items: [
        'Numerous stakeholders',
        'Information quality affects collaboration',
        'Persistent friction',
      ] } },
      { kind: 'iconStrip',   data: { items: ['house','document','chat','files-stack','calendar','crane','dollar-circle','pie-chart'], arrow: true } },
      { kind: 'labeledCard', data: {
        title: 'Consequences',
        lines: [
          { stat: '$430B+/year', body: 'in rework and' },
          { stat: '$1.4T',        body: 'in non-optimal labour' },
          { stat: '30%',          body: 'of global construction waste' },
          { stat: '9.4 hrs/wk',   body: 'wasted time for mid to high level professionals' },
        ],
      } },
    ],
  },
  comparison: {
    name: 'Side-by-side',
    kind: 'content',
    desc: 'Two-column comparison with bronze italic headings — for 3D vs 2D, before vs after, problem vs solution.',
    icon: 'swap',
    forTypes: ['deck'],
    build: () => [
      { kind: 'headline',  data: { eyebrow: '', text: 'Where users collaborate effortlessly and in real time.' } },
      { kind: 'comparison', data: {
        left:  { title: '3D Environment',  caption: 'Versatile interfaces · info and collaboration tools', label: 'Hub interior view' },
        right: { title: '2D Environment',  caption: '"Control panel" · project management tools',         label: 'Project dashboard' },
      } },
    ],
  },
  scienceBacked: {
    name: 'Science-backed',
    kind: 'stats',
    desc: 'Inspo p09: investment pills at top, a metric strip, and a side-by-side with hex badges in the middle.',
    icon: 'star',
    forTypes: ['deck'],
    build: () => [
      { kind: 'headline',  data: { eyebrow: '', text: 'Our innovation is science-based.' } },
      { kind: 'statPills', data: { items: [
        { v: '6 Years',  l: 'Research & Development' },
        { v: '$1.5M+',   l: 'Spent on IP' },
      ] } },
      { kind: 'metricRow', data: { items: [
        { v: '70+',      l: 'Virtual Hubs' },
        { v: '40+',      l: 'Unique clients' },
        { v: '$250k+',   l: 'Project sales' },
        { v: '41,500+',  l: 'Unique users' },
        { v: '100%',     l: 'Saw improved communication' },
        { v: '100%',     l: 'Recommend us to others' },
      ] } },
      { kind: 'hexBadge', data: { items: [
        { label: 'Property\nWizard', version: 'v9.0' },
        { label: 'Vi',               version: 'v3.0' },
      ] } },
    ],
  },
  capabilityRow: {
    name: 'Capability chips',
    kind: 'content',
    desc: 'Bottom-of-slide capability row: small icon → gold-outlined chip-tags. Use as a summary footer.',
    icon: 'tag',
    forTypes: ['deck'],
    build: () => [
      { kind: 'headline', data: { eyebrow: '', text: "We're launching SaaS and e-commerce applications." } },
      { kind: 'imageGrid', data: { items: [
        { label: 'Architects · designers' },
        { label: 'Sales · marketing' },
        { label: 'Brands · suppliers' },
      ] } },
      { kind: 'chipRow',  data: { lead: 'browser-house', items: ['Agnostic', 'Accessible', 'Intuitive', 'Seamless', 'Universal'] } },
    ],
  },
  achievements: {
    name: 'Achievements',
    kind: 'stats',
    desc: 'Inspo p11: two checklist cards side-by-side, then a logo strip of partner programs.',
    icon: 'check-square',
    forTypes: ['deck'],
    build: () => [
      { kind: 'headline', data: { eyebrow: '', text: 'Recent achievements put 6 years of planning into action.' } },
      { kind: 'comparison', data: {
        left:  { title: 'Conditions for SaaS Transition', caption: '', label: '' },
        right: { title: 'Milestones',                     caption: '', label: '' },
      } },
      { kind: 'logoStrip', data: {
        title: 'Development Partners and Incubator Programs',
        logos: ['NVIDIA · Inception', 'NVIDIA · Omniverse', 'AWS Activate', 'Google Cloud', 'Oracle for Startups'],
      } },
    ],
  },
  bioFacts: {
    name: 'Bio + facts',
    kind: 'content',
    desc: 'Inspo p14: bio card at top, gold ▶ key-fact list below. For introducing team members.',
    icon: 'people',
    forTypes: ['deck'],
    build: () => [
      { kind: 'headline', data: { eyebrow: '', text: 'Grant is bringing financial and strategic support.' } },
      { kind: 'bio', data: {
        name: 'Grant Plummer',
        role: 'Director at Gap Development Sales',
        avatarInitials: 'GP',
        stats: [
          { v: '25+',  l: 'Years of experience' },
          { v: '120+', l: 'Developments in sales portfolio' },
          { v: '$3B+', l: 'Sales in residential property' },
        ],
      } },
      { kind: 'bullets', data: { items: [
        'Investment to Date: $100k',
        'Committed: $800k by July 2025 and $400k ARR through GAP',
        'Start Date at ConceptV: 01 Nov 2024',
        'Role: Chief Sales Officer',
      ] } },
    ],
  },
  investmentTerms: {
    name: 'Investment terms',
    kind: 'stats',
    desc: 'Inspo p15: two-column terms layout — left side instrument + bullet conditions, right side cash-out option with hero pill and stat table.',
    icon: 'dollar-circle',
    forTypes: ['deck'],
    build: () => [
      { kind: 'headline',  data: { eyebrow: '', text: 'We have $800k committed to fuel our growth strategy.' } },
      { kind: 'statTable', data: {
        title: 'Capped Cash Out Option in 12 months',
        hero: { v: '$500M', l: 'Target valuation at exit event' },
        rows: [
          { v: '91x',     l: 'Multiple from investing this round' },
          { v: '5 Years', l: 'Exit event goal' },
          { v: '$6.5M',   l: 'Buy-back valuation in 12 months' },
          { v: '18.2%',   l: 'ROI on optional buy-back' },
          { v: '2 Years', l: 'Intended Series A raise' },
          { v: '$50M',    l: 'Target valuation at Series A' },
          { v: '$5M',     l: 'Planned Series A raise amount' },
        ],
      } },
    ],
  },
  rolloutTimeline: {
    name: 'Rollout timeline',
    kind: 'content',
    desc: 'Inspo p12: vertical month-axis with gold-outlined milestone pills branching to either side.',
    icon: 'calendar',
    forTypes: ['deck'],
    build: () => [
      { kind: 'headline', data: { eyebrow: '', text: 'Strategic rollout: adapting to market needs.' } },
      { kind: 'timeline', data: {
        unit: 'Months',
        ticks: ['6', '12', '18', '24'],
        milestones: [
          { tick: 0, side: 'right', label: 'Marketing & Sales' },
          { tick: 1, side: 'right', label: 'Architecture & Design' },
          { tick: 1, side: 'right', label: 'Property Developers',  offset: 1 },
          { tick: 2, side: 'left',  label: 'Brands & Suppliers' },
          { tick: 2, side: 'right', label: 'Marketplace' },
          { tick: 2, side: 'right', label: 'Volume Builders',      offset: 1 },
          { tick: 3, side: 'right', label: 'Construction Suite' },
          { tick: 3, side: 'left',  label: 'Kit Homes' },
        ],
      } },
    ],
  },
  partnerships: {
    name: 'Partnerships',
    kind: 'content',
    desc: 'Inspo p13: title + go-to-market pillars (4 chip cards) + key contacts (2 person cards).',
    icon: 'people',
    forTypes: ['deck'],
    build: () => [
      { kind: 'headline', data: { eyebrow: '', text: 'Partnerships power our growth.' } },
      { kind: 'pillars',  data: {
        subtitle: 'The Pillars of Our Go-to-Market Strategy',
        items: ['Key Industry Figures', 'Market Partnerships', 'Organic Recognition', 'Customer Base'],
      } },
      { kind: 'photoBio', data: { items: [
        { initials: 'TS', name: 'Tamara Smith — Key Industry Figure',
          desc: 'National Manager of Partnerships and Strategic Engagement at the AIA' },
        { initials: 'GP', name: 'Grant Plummer — Upcoming Chief Sales Officer',
          desc: 'Director at Gap Development Sales and investor at ConceptV' },
      ] } },
    ],
  },
  aiFramework: {
    name: 'AI framework',
    kind: 'content',
    desc: 'Inspo frame_19: small caption + diamond Vi hub + dashed arrows to 3 mixed-shape product nodes, each surrounded by icon-satellites.',
    icon: 'network',
    forTypes: ['deck'],
    build: () => [
      { kind: 'orgDiagram', data: {
        caption: 'The AI Framework powering our systems',
        hub: { label: 'Vi', shape: 'diamond' },
        nodes: [
          {
            label: 'User\nPortal', shape: 'circle',
            left:  [{ icon: 'dollar-circle', label: 'Order and contract' }],
            right: [{ icon: 'gear',          label: 'Manage updates' }],
            below: [{ icon: 'cloud',         label: 'Upload design files' }, { icon: 'gear', label: 'Configure Hubs' }],
          },
          {
            label: 'Property\nWizard', shape: 'hex',
            below: [{ icon: 'database',      label: 'Central database' }, { icon: 'network', label: 'Decision tree logic' }],
          },
          {
            label: 'Virtual\nHubs', shape: 'octagon',
            left:  [{ icon: 'people',        label: 'User-specific functions' }],
            right: [{ icon: 'info-circle',   label: 'Centralised information' }],
            below: [{ icon: 'chat',          label: 'Communication tools' }, { icon: 'edit', label: 'Annotation dashboard' }],
          },
        ],
      } },
    ],
  },
  contactClosing: {
    name: 'Contact closing',
    kind: 'closing',
    desc: 'Inspo p16: full-bleed bronze room + overlaid white contact card with brand + phone/email/web/office.',
    icon: 'email',
    forTypes: ['deck'],
    build: () => [
      { kind: 'contactCard', data: {
        brand: 'ConceptV',
        lines: [
          { label: 'Phone',     value: '0421 849 615' },
          { label: 'Email',     value: 't.geldard@conceptv.com.au' },
          { label: 'Website',   value: 'www.conceptv.com.au' },
          { label: 'Head Office', value: 'Level 1, 235 Boundary Street\nWest End, QLD 4101' },
        ],
      } },
    ],
  },
  // Brochure-specific layouts
  property: {
    name: 'Property sheet',
    kind: 'content',
    desc: 'Hero render + features + description + CTA. Real-estate sales.',
    icon: 'house',
    forTypes: ['brochure'],
    build: () => [
      { kind: 'hero',    data: { eyebrow: 'Tower East · Stage 1', headline: 'Light-filled corner apartments.', body: 'Two-bed homes on level 12 with north-east aspect and harbour glimpses.', cta: 'Enquire', imageLabel: 'Hero render' } },
      { kind: 'icons',   data: { items: [{icon:'house',label:'2 BED'},{icon:'people',label:'2 BATH'},{icon:'browser',label:'98 m²'},{icon:'gear',label:'1 CAR'}] } },
      { kind: 'body',    data: { text: 'Open-plan living anchored by a stone-topped island; a separate study nook; floor-to-ceiling glazing onto a wraparound balcony.' } },
      { kind: 'callout', data: { label: 'Starting price', text: 'From $2,450,000.' } },
      { kind: 'button',  data: { text: 'Book a private viewing →' } },
    ],
  },
  factsheet: {
    name: 'Fact sheet',
    kind: 'content',
    desc: 'Title + 4 stats + supporting paragraph. Product or service one-pagers.',
    icon: 'pie-chart',
    forTypes: ['brochure'],
    build: () => [
      { kind: 'headline', data: { eyebrow: 'Product', text: 'Virtual Hub.' } },
      { kind: 'body',     data: { text: 'Branded panotours for architects, developers and sales agencies. Built on Universal Mechanics — the engine for stakeholder-rich projects.' } },
      { kind: 'stats',    data: { items: [
        { v: '5+',  l: 'Stakeholder types' },
        { v: '24/7',l: 'Real-time updates' },
        { v: '10×', l: 'Faster sign-off' },
        { v: '80%', l: 'Less rework' },
      ] } },
      { kind: 'callout', data: { label: 'Pipeline', text: 'Revit → Enscape → ConceptV. No additional plug-ins required.' } },
    ],
  },
  oneSheet: {
    name: 'One sheet',
    kind: 'content',
    desc: 'Headline + 3 callouts + closing button. Generic sell sheet.',
    icon: 'document',
    forTypes: ['brochure'],
    build: () => [
      { kind: 'headline', data: { eyebrow: 'Why ConceptV', text: 'Three reasons firms switch to us.' } },
      { kind: 'callout',  data: { label: 'Speed', text: 'Cut review cycles from weeks to days.' } },
      { kind: 'callout',  data: { label: 'Clarity', text: 'Every stakeholder sees the same source of truth.' } },
      { kind: 'callout',  data: { label: 'Brand',   text: 'Your identity, applied automatically across every output.' } },
      { kind: 'button',   data: { text: 'Talk to us →' } },
    ],
  },
  event: {
    name: 'Event flyer',
    kind: 'content',
    desc: 'Big hero with date / venue + closing CTA.',
    icon: 'calendar',
    forTypes: ['brochure'],
    build: () => [
      { kind: 'hero',    data: { eyebrow: 'Sales preview · 14 June', headline: 'Tower East — open viewing.', body: 'Tour the model apartments and meet the design team. By appointment only.', cta: 'Reserve a slot', imageLabel: 'Venue image' } },
      { kind: 'icons',   data: { items: [{icon:'calendar',label:'14 June'},{icon:'house',label:'Sales suite'},{icon:'people',label:'By appt.'}] } },
      { kind: 'button',  data: { text: 'RSVP →' } },
    ],
  },
};

// ============================================================
// Canonical-archetype mapping (UNIFICATION.md W2/W3)
// Each legacy WS_LAYOUT reconciles to ONE core archetype
// (surface.deck-slide.<key>, single-sourced in core/archetype-catalog.js).
// Additive metadata only — proves every composer layout maps onto the 15
// canonical archetypes, and lets W3 migrate the renderer to RenderType.
// ============================================================
window.WS_LAYOUT_ARCHETYPE = {
  title: 'cover', section: 'statement', content: 'statement', bullets: 'metric-band',
  icons: 'gallery', hero: 'split', quote: 'statement', callout: 'statement',
  closing: 'closing', process: 'stepper', showcase: 'gallery', threeFeatures: 'triptych',
  funnel: 'timeline', systemMap: 'diagram', bigQuote: 'statement', metricSet: 'metric-band',
  pitchDeckPage: 'split', comparison: 'compare', scienceBacked: 'metric-band',
  capabilityRow: 'gallery', achievements: 'checklist', bioFacts: 'profile',
  investmentTerms: 'terms', rolloutTimeline: 'timeline', partnerships: 'profile',
  aiFramework: 'diagram', contactClosing: 'closing',
  property: 'split', factsheet: 'metric-band', oneSheet: 'statement', event: 'split',
};
Object.entries(window.WS_LAYOUTS).forEach(([k, L]) => {
  const a = window.WS_LAYOUT_ARCHETYPE[k];
  if (a) L.archetype = 'surface.deck-slide.' + a;   // canonical Type this layout maps to
});

// --- capital-raise archetypes (slice 28) reconciliation ------------
// The +12 new archetypes (product-cover/closing, photo-divider, logo-wall,
// team, dashboard, reasons, orbital, stacked, spectrum, manifold, fidelity)
// were added ONLY to the single source — core/archetype-catalog.js
// (window.CV_ARCHETYPE_CATALOG) — NOT duplicated into WS_LAYOUTS. So there is
// no parallel list to annotate; instead the composer DERIVES them from the
// catalogue, which makes coverage drift-proof: any archetype with no legacy
// WS_LAYOUT is surfaced here, computed, never re-typed.
//   WS_coreArchetypes() = the canonical archetypes that have no legacy composer
//   layout (the additive set, incl. the capital-raise grammar). They render
//   through the core Slide / RenderType, not WS_BLOCKS. Wiring them into the
//   layout picker + a RenderType-backed page builder is weld W3 (UNIFICATION.md);
//   this helper is the single-sourced bridge W3 will consume.
window.WS_coreArchetypes = function () {
  const cat = window.CV_ARCHETYPE_CATALOG;
  if (!cat) return [];   // catalogue not on this page (lean template) — no fork, just nothing to add
  const legacy = new Set(Object.values(window.WS_LAYOUT_ARCHETYPE));   // archetype keys already reachable via a WS_LAYOUT
  return cat
    .filter((t) => t && t.runtime && t.runtime.kind === 'core-archetype')
    .map((t) => ({ key: t.runtime.key, name: t.name, desc: t.description, icon: t.icon, archetype: t.id, coreArchetype: true }))
    .filter((a) => !legacy.has(a.key) && a.key !== 'diagram' && a.key !== 'section');
};

// Helper: list layouts that apply to a doc type
window.WS_layoutsForType = function(type) {
  return Object.entries(window.WS_LAYOUTS)
    .filter(([k, L]) => k !== 'blank' && (!L.forTypes || L.forTypes.includes(type)));
};

// Helper: build a fresh page from a layout id
window.WS_buildPage = function(layoutId, idx) {
  const L = window.WS_LAYOUTS[layoutId] || window.WS_LAYOUTS.blank;
  const sections = L.build().map((s, j) => ({
    id: 'sec-' + Date.now() + '-' + idx + '-' + j,
    kind: s.kind,
    data: { ...(window.WS_BLOCKS[s.kind]?.defaults || {}), ...(s.data || {}) },
  }));
  return {
    id: 'p-' + Date.now() + '-' + idx,
    title: L.name,
    kind: L.kind,
    sections,
  };
};

// ============================================================
// Motifs — slide background recipes
// Each renders a layer behind the .ws-slide-inner content.
// `bleed` hints whether content should be ink-on-light or cream-on-dark.
// ============================================================
window.WS_MOTIFS = {
  ivory:    { name: 'Ivory',        desc: 'Flat warm canvas. Default.',              bleed: 'light' },
  paper:    { name: 'Paper',        desc: 'Subtle stippled paper texture.',          bleed: 'light' },
  blueprint:{ name: 'Blueprint',    desc: 'Faint 24-pt gold grid.',                  bleed: 'light' },
  edgeband: { name: 'Edge band',    desc: 'Gold vertical band on the left edge.',    bleed: 'light' },
  watermark:{ name: 'Watermark',    desc: 'V-mark large at low opacity.',            bleed: 'light' },
  ink:      { name: 'Ink',          desc: 'Warm dark surface for emphasis.',         bleed: 'dark'  },
  goldBleed:{ name: 'Gold bleed',   desc: 'Full-bleed brand gold. Use sparingly.',   bleed: 'gold'  },
  section:  { name: 'Section marker', desc: 'Bronze full-bleed with V-mark.',        bleed: 'dark'  },
};

// ============================================================
// Themes — assign a motif to each slide kind
// ============================================================
window.WS_THEMES = {
  editorial: {
    name: 'Editorial',
    desc: 'Calm ivory for content, ink for section headers, gold bleed for opening + closing. The default for serious pitches.',
    map: {
      title: 'goldBleed',
      section: 'ink',
      content: 'ivory',
      image: 'ivory',
      quote: 'ink',
      stats: 'ivory',
      closing: 'goldBleed',
    },
  },
  architectural: {
    name: 'Architectural',
    desc: 'Blueprint grid throughout. Section headers get an edge band. Restrained gold, technical feel.',
    map: {
      title: 'edgeband',
      section: 'edgeband',
      content: 'blueprint',
      image: 'blueprint',
      quote: 'blueprint',
      stats: 'blueprint',
      closing: 'edgeband',
    },
  },
  quiet: {
    name: 'Quiet',
    desc: 'All ivory, all the time, with a subtle V-mark watermark. Use when content is dense.',
    map: {
      title: 'watermark',
      section: 'paper',
      content: 'ivory',
      image: 'ivory',
      quote: 'paper',
      stats: 'ivory',
      closing: 'watermark',
    },
  },
  bold: {
    name: 'Bold',
    desc: 'Gold opening, ink section starters, ivory content. Strong rhythm.',
    map: {
      title: 'goldBleed',
      section: 'section',
      content: 'ivory',
      image: 'ivory',
      quote: 'ink',
      stats: 'ivory',
      closing: 'ink',
    },
  },
};

// Helper: resolve the motif for a slide given the doc's theme + the slide's own override
window.WS_resolveMotif = function(doc, page) {
  if (page?.motif) return page.motif;
  const theme = window.WS_THEMES[doc?.theme || 'editorial'];
  return theme?.map?.[page?.kind || 'content'] || 'ivory';
};

// ============================================================
// Motif renderer — fills .ws-slide-frame with the right layer
// Takes a motif id and returns a JSX <div>.
// ============================================================
window.WSMotifLayer = function MotifLayer({ motif }) {
  const m = window.WS_MOTIFS[motif] || window.WS_MOTIFS.ivory;
  return (
    <div className={`ws-motif ws-motif--${motif}`} aria-hidden="true">
      {motif === 'watermark' && (
        <svg className="ws-motif-mark" viewBox="0 0 100 100">
          <polygon points="50,8 92,50 50,92 8,50" fill="none" stroke="#E0C010" strokeWidth="1.5" opacity="0.16"/>
          <polygon points="50,8 92,50 50,92 8,50" fill="#E0C010" opacity="0.04"/>
        </svg>
      )}
      {motif === 'section' && (
        <svg className="ws-motif-mark ws-motif-mark--center" viewBox="0 0 100 100">
          <polygon points="50,8 92,50 50,92 8,50" fill="none" stroke="#FBF7EC" strokeWidth="1" opacity="0.5"/>
          <polygon points="50,8 92,50 50,92 8,50" fill="#FBF7EC" opacity="0.06"/>
        </svg>
      )}
      {motif === 'blueprint' && (
        <svg className="ws-motif-blueprint" viewBox="0 0 1280 720" preserveAspectRatio="xMidYMid slice">
          {/* faded architectural drawings: floor plan + section + labels */}
          <g stroke="var(--accent-bronze)" strokeWidth="0.8" fill="none" opacity="0.18">
            {/* floor plan, top-left */}
            <rect x="40" y="30" width="220" height="140"/>
            <line x1="120" y1="30" x2="120" y2="170"/>
            <line x1="40" y1="100" x2="260" y2="100"/>
            <line x1="170" y1="30" x2="170" y2="100"/>
            <line x1="170" y1="135" x2="260" y2="135"/>
            <circle cx="80" cy="135" r="8"/>
            <circle cx="215" cy="60" r="10"/>
            <text x="50" y="22" fontSize="7" fontFamily="DM Sans, sans-serif" fill="#988058" stroke="none">LEVEL 02 · PLAN</text>
            {/* north arrow */}
            <g transform="translate(290,50)">
              <circle r="10"/>
              <polygon points="0,-9 -4,4 0,1 4,4" fill="#988058" stroke="none"/>
              <text x="-3" y="-12" fontSize="7" fontFamily="DM Sans, sans-serif" fill="#988058" stroke="none">N</text>
            </g>
            {/* elevation, top-right */}
            <path d="M900 40 L900 160 L1240 160 L1240 40 Z"/>
            <path d="M900 80 L1240 80 M900 120 L1240 120"/>
            <path d="M940 80 L940 160 M980 80 L980 120 M1020 120 L1020 160 M1060 80 L1060 120 M1100 120 L1100 160 M1140 80 L1140 120 M1180 120 L1180 160 M1220 80 L1220 120"/>
            <text x="906" y="34" fontSize="7" fontFamily="DM Sans, sans-serif" fill="#988058" stroke="none">SECTION A-A</text>
            {/* dimension lines */}
            <g stroke="#988058">
              <line x1="40" y1="190" x2="260" y2="190"/>
              <line x1="40" y1="187" x2="40" y2="193"/>
              <line x1="260" y1="187" x2="260" y2="193"/>
            </g>
            <text x="135" y="200" fontSize="6" fontFamily="DM Sans, sans-serif" fill="#988058" stroke="none">3500 mm</text>
            {/* small isometric cube, bottom-left */}
            <g transform="translate(80,560)">
              <path d="M0 0 L40 -20 L80 0 L80 50 L40 70 L0 50 Z"/>
              <path d="M0 0 L0 50 M40 -20 L40 30 M80 0 L80 50 M0 0 L40 30 L80 0 M40 30 L40 70"/>
            </g>
            <text x="60" y="650" fontSize="6" fontFamily="DM Sans, sans-serif" fill="#988058" stroke="none">VOL · 240 m³</text>
            {/* site plan, bottom-right */}
            <g transform="translate(960,520)">
              <rect width="260" height="160" rx="2"/>
              <path d="M30 30 L230 30 L230 130 L30 130 Z M30 90 L230 90 M130 30 L130 130"/>
              <circle cx="70" cy="60" r="12"/>
              <circle cx="180" cy="60" r="14"/>
              <rect x="50" y="100" width="40" height="20"/>
              <rect x="160" y="100" width="50" height="20"/>
            </g>
            <text x="966" y="514" fontSize="7" fontFamily="DM Sans, sans-serif" fill="#988058" stroke="none">SITE · BUILDING ENVELOPE</text>
          </g>
          {/* gold grid overlay */}
          <g stroke="var(--accent-gold)" strokeWidth="0.4" opacity="0.12">
            {Array.from({length: 53}, (_, i) => <line key={'v'+i} x1={i*24} y1="0" x2={i*24} y2="720"/>)}
            {Array.from({length: 30}, (_, i) => <line key={'h'+i} x1="0" y1={i*24} x2="1280" y2={i*24}/>)}
          </g>
        </svg>
      )}
    </div>
  );
};
