// core/archetype-catalog.js
// ------------------------------------------------------------
// SINGLE SOURCE of the deck-slide ARCHETYPE catalogue, in the CV_REGISTRY
// Type schema (analysis/UNIFICATION.md W2). Before this, the archetype list
// existed three times (app stubs · WS_LAYOUTS · core/Slide). This module is
// the one catalogue both halves read:
//   • the bundle's core/RenderType.jsx (CoreTypes.archetypeSeeds) reads it,
//   • the app's app/registry/types-seed.js seeds CV_REGISTRY from it.
//
// SCHEMA lives here; the RENDERER for each archetype is its builder in
// core/Slide.jsx keyed by the same `key` (Type vs runtime, exactly like a
// block.* Type vs WS_BLOCKS[k].render). Add an archetype = add one entry here
// + one builder there. Plain JS (no compile) so the app can load it without
// the whole bundle. Token/voice-pure — metadata only, no new design.
(function () {
  const META = {
    cover:         { name: "Cover",                 icon: "image",         desc: "Full-bleed photographic cover — logo lockup + bronze subtitle." },
    split:         { name: "Split visual / content", icon: "browser",      desc: "Bleeding visual left, title + bullets + synthesis note right." },
    statement:     { name: "Statement",             icon: "edit",          desc: "Centered title + lede + body — the workhorse." },
    compare:       { name: "Two-panel compare",     icon: "swap",          desc: "Soft warm/neutral panels + italic synthesis footer." },
    modes:         { name: "Mode columns",          icon: "browser-chart", desc: "Parallel screenshot columns + captions." },
    triptych:      { name: "Triptych cards",        icon: "pie-chart",     desc: "Three cards, two warm + one neutral, with hero metrics." },
    "metric-band": { name: "Metric band",           icon: "pie-chart",     desc: "Full-width row of embossed KPIs." },
    checklist:     { name: "Dual checklist",        icon: "check-square",  desc: "Two checklists + logo strip." },
    timeline:      { name: "Timeline / flow",       icon: "calendar",      desc: "Axis + outlined nodes — a graph diagram." },
    profile:       { name: "Profile panel",         icon: "people",        desc: "Entity badge + name/role + stats + bullets." },
    terms:         { name: "Terms panels",          icon: "dollar-circle", desc: "Soft panels with a hero-number chip + bullet list." },
    gallery:       { name: "Gallery grid",          icon: "image-stack",   desc: "Lede + tiled image placeholders." },
    closing:       { name: "Contact / closing",     icon: "email",         desc: "Info card + action pills." },
    stepper:       { name: "Chevron stepper",       icon: "path-flow",     desc: "Ramp-tinted stage progression with an active cutoff." },
    diagram:       { name: "Diagram",               icon: "network",       desc: "Hosts any graph spec (hub/network/morph/pipeline/quadrant…)." },
    // ---- capital-raise archetypes (slice 28) ----
    "product-cover":   { name: "Product cover",       icon: "image",         desc: "Full-bleed live-product surface + frosted title lockup." },
    "product-closing": { name: "Product closing",     icon: "email",         desc: "Full-bleed product surface + frosted contact card." },
    "photo-divider":   { name: "Photo divider",       icon: "image",         desc: "Full-bleed photographic section break — a single word." },
    "logo-wall":       { name: "Logo wall",           icon: "grid",          desc: "Client/partner grid bracketed by hatch-framed stat strips." },
    team:              { name: "Team / org",          icon: "people",        desc: "Core rows (alternating tint) + advisory icon row + upcoming hires." },
    dashboard:         { name: "Dashboard",           icon: "browser-chart", desc: "Grid of raised panels — metrics, charts, milestone text." },
    reasons:           { name: "Reason cards",        icon: "check-square",  desc: "Ramp-bordered card row bridging two summary zones." },
    orbital:           { name: "Orbital ring",        icon: "network",       desc: "Central node ringed by verb labels — the process around it." },
    stacked:           { name: "Stacked pipeline",    icon: "path-flow",     desc: "Pipeline of collapsed-set nodes; members peek above/below." },
    spectrum:          { name: "Spectrum axis",       icon: "path-flow",     desc: "1-D gold→bronze gradient axis with plotted cards + segments." },
    manifold:          { name: "Converging total",    icon: "pie-chart",     desc: "N branches → a dashed manifold → one summed total." },
    fidelity:          { name: "Fidelity stepper",    icon: "calendar",      desc: "Vertical stepper paired to media that escalates in detail." },
  };

  // Representative sample content per archetype — the Type's `defaults`. Doubles
  // as the registry preview seed (like WS_BLOCKS[k].defaults). ConceptV content.
  const SAMPLES = {
    cover: { title: "Virtual Hubs for stakeholder-rich projects", kicker: "ConceptV", image: "warm coastal-luxury interior render", subtitle: "Turn architectural design files into interactive panotour experiences." },
    split: { title: "Translation, not re-drawing", visual: "chaos → order diagram", heading: "The shift", bullets: [{ title: "One source of truth", text: "tokens flow to every surface.", bullet: "leads" }, { title: "Computed, not hand-set", text: "same spec, every ratio." }, { title: "Nothing drifts", bullet: "done" }], note: "The layout itself makes the pitch." },
    statement: { title: "Property design is a complex undertaking", lede: "Numerous stakeholders, fragmented information, persistent friction.", body: "ConceptV works as an overlay that translates and connects the fragments.", note: "We simplify the complex process." },
    compare: { title: "Current practice vs Virtual Hubs", left: { title: "Current practice", bullets: ["Files emailed around", "Versions drift", "Sign-off takes weeks"] }, right: { title: "Virtual Hubs", bullets: [{ text: "Single live source", bullet: "done" }, { text: "Everyone sees the same thing", bullet: "done" }] }, note: "Same inputs, a calmer process." },
    modes: { title: "Two environments, one source", columns: [{ title: "3D environment", image: "hub interior view", caption: "Versatile interfaces" }, { title: "2D environment", image: "project dashboard", caption: "Control panel" }], note: "Synchronised 2D and 3D data." },
    triptych: { title: "Three things the data tells us", cards: [{ title: "Top drivers", value: "70%", metricLabel: "want accuracy" }, { title: "Top barriers", value: "67%", metricLabel: "cost of software" }, { title: "Why fail", value: "36%", metricLabel: "poor fit" }] },
    "metric-band": { title: "Our innovation is science-based", metrics: [{ value: "70+", label: "Virtual Hubs delivered" }, { value: "$1.5M+", label: "spent on IP" }, { value: "41,500+", label: "unique users" }], note: "100% reported improved communication." },
    checklist: { title: "Recent achievements", columns: [{ title: "Conditions for SaaS", items: ["Engine built", "IP secured", "Pilots live"] }, { title: "Milestones", items: ["70+ hubs", "40+ clients"] }], logos: ["NVIDIA Inception", "AWS Activate", "Google Cloud"], note: "Six years of planning into action." },
    timeline: { title: "Strategic rollout", steps: ["Marketing & Sales", "Architecture", "Brands", "Construction"], note: "Adapting to market needs." },
    profile: { title: "Grant brings financial and strategic support", name: "Grant Plummer", role: "Chief Sales Officer", initials: "GP", shape: "circle", stats: [{ value: "25+", label: "years experience" }, { value: "$3B+", label: "residential sales" }], bullets: ["$100k invested to date", "$800k committed by July"] },
    terms: { title: "$800k committed to fuel growth", panels: [{ title: "This round", hero: { value: "91×", label: "multiple from this round" }, bullets: ["5-year exit goal", "$6.5M buy-back in 12 months"] }, { title: "Series A", hero: { value: "$50M", label: "target valuation" }, bullets: ["$5M planned raise"] }] },
    gallery: { title: "A look at recent work", lede: "Hubs delivered across residential and commercial.", items: ["Aerial render", "Interior detail", "Floor plan", "Hub viewer", "Capture", "Dashboard"] },
    closing: { title: "Let's talk", subtitle: "Book a walkthrough of a live Virtual Hub.", lines: [{ label: "Phone", value: "0421 849 615" }, { label: "Email", value: "t.geldard@conceptv.com.au" }, { label: "Web", value: "conceptv.com.au" }], actions: ["Schedule a call", "See a hub"], note: "Revit → Enscape → ConceptV." },
    stepper: { title: "A rollout across disciplines", steps: ["Design", "Marketing", "Sales", "Construction"], active: 1, lede: "The accent slides along the ramp as stages activate." },
    diagram: { title: "The AI framework powering our systems", lede: "Vi sits at the centre.", graph: { type: "hub", center: "Vi", nodes: [{ id: "Vi", shape: "diamond", tone: "active" }, { id: "Portal", label: "User Portal", shape: "circle" }, { id: "Wizard", label: "Property Wizard", shape: "hex" }, { id: "Hubs", label: "Virtual Hubs", shape: "octagon" }], edges: ["Portal", "Wizard", "Hubs"].map((t) => ({ from: "Vi", to: t, kind: "flow" })) } },
    "product-cover": { kicker: "ConceptV", title: "Streamlining property design and development", subtitle: "Turn architectural files into interactive Virtual Hubs.", image: "warm coastal-luxury interior (panotour viewer chrome)" },
    "product-closing": { kicker: "ConceptV", subtitle: "Let's build your first Hub", lines: [{ label: "Phone", value: "0421 849 615" }, { label: "Email", value: "t.geldard@conceptv.com.au" }, { label: "Web", value: "conceptv.com.au" }], image: "luxury interior, panotour viewer chrome" },
    "photo-divider": { title: "Appendix", image: "full-bleed architectural render at golden hour" },
    "logo-wall": { title: "Market-tested and sold", top: [{ value: "60+", label: "Projects delivered" }, { value: "41,500+", label: "Unique users" }], logos: ["Penfold", "Brookmoore", "Ellivo", "Baahouse", "Habitat", "Feltham", "Arco", "Vida", "Kitome", "Heran", "Focus", "G.J. Gardner"], bottom: [{ value: "100%", label: "Improved communication" }, { value: "89%", label: "Easy integration" }, { value: "100%", label: "Would recommend" }] },
    team: { title: "The people behind ConceptV", core: [{ name: "Tim Geldard", role: "CEO & Founder", initials: "TG", credential: "Bachelor of Property Economics, major in Residential Construction" }, { name: "Michael Baggott", role: "CTO & Founder", initials: "MB", credential: "Bachelor of Technology & Computing; Diploma of Interactive Games" }, { name: "Jackie Nishimura", role: "CPO", initials: "JN", credential: "Bachelor of Industrial Design, major in Product Development" }], advisory: ["Private Equity", "Operations", "Sales & Growth", "Risk", "Construction", "Financial Strategy"], upcoming: [{ name: "Christian Hodges", role: "Automation", initials: "CH" }, { name: "Shane Begovic", role: "Integration", initials: "SB" }] },
    dashboard: { title: "Because we know how to spend it", panels: [{ title: "Deal size", metrics: [{ value: "$1M", label: "Capital round" }, { value: "$5.5M", label: "Pre-money valuation" }] }, { title: "Future outlook", chart: { kind: "spark", points: [2, 3, 3, 5, 6, 9, 12], label: "Sales revenue → Q4" } }, { title: "Use of funds", chart: { kind: "gauge", value: 61, label: "Sales & marketing" } }, { title: "Key milestones", bullets: [{ title: "6 mo", text: "10 luxury customers" }, { title: "24 mo", text: "NZ, USA & UK" }] }] },
    reasons: { title: "But why raise capital now?", lede: "We weren't planning to — recent market movements created a time-sensitive opportunity.", cards: [{ title: "Current climate", text: "Markets are pressured to reduce waste and gain an edge." }, { title: "Market partnerships", text: "Industry bodies are inviting us to educate members." }, { title: "AI development", text: "Systems years in design are now possible." }, { title: "Existing demand", text: "Clients we've had to turn away on capacity." }], zones: [{ title: "People and markets", bullets: ["A director of the AIA joins as Growth Director", "Invited to deliver seminars to target markets"] }, { title: "Investment spend", bullets: ["Automated delegation and consolidation", "Develop V3.0 of the Property Wizard"] }] },
    orbital: { title: "One system for a variety of use cases", lede: "Stakeholders and files flow through the Property Wizard.", center: { label: "Property Wizard", shape: "hex" }, verbs: [{ label: "Configure" }, { label: "Output" }, { label: "Update" }, { label: "Upload" }] },
    stacked: { title: "Our go-to-market is organic and recyclable", nodes: [{ label: "Networks", top: ["Research"], bottom: ["Referrals"] }, { label: "Developers", top: ["Architects"], bottom: ["Designers"] }, { label: "User Portal", shape: "circle" }, { label: "Virtual Tours", shape: "octagon" }, { label: "Sales", top: ["Onsellers"], bottom: ["Subscribers"] }, { label: "Organic Awareness", shape: "circle", join: "plus" }] },
    spectrum: { title: "In a siloed competitive landscape", ends: ["Technical · strictly professional", "Non-technical · public facing"], segments: [{ label: "Design process", at: 0.28 }, { label: "Marketing & sales", at: 0.72 }], cards: [{ label: "Architect software", at: 0.08 }, { label: "Visualisation", at: 0.34 }, { label: "Rendering", at: 0.62 }, { label: "360° tours", at: 0.9 }], hatch: [0, 0.18] },
    manifold: { title: "Which has generated a diverse pipeline", branches: [{ title: "Architect clients", value: "$120–210k", label: "sum AR potential" }, { title: "Developer clients", value: "$440–720k", label: "sum AR potential" }, { title: "Home builder clients", value: "$215–365k", label: "sum ARR potential" }], total: { value: "$1,035,000", label: "ARR in 6-month pipeline" } },
    fidelity: { title: "Our communication tools streamline updates", steps: [{ label: "Stage 1", text: "Placeholders, basic visual quality", inter: "1–2 weeks", image: "grey massing render" }, { label: "Stage 2", text: "Some elements defined", inter: "Revision", image: "part-textured render" }, { label: "Stage 3", text: "High detail and quality", inter: "Revision", image: "full interior render" }, { label: "Marketing package", text: "Renders, brochures, collateral", image: "hero kitchen render" }] },
  };

  const seeds = Object.keys(META).map((key) => {
    const m = META[key];
    return {
      id: "surface.deck-slide." + key,
      name: m.name,
      layer: "surface",
      family: "deck-slide",
      icon: m.icon,
      description: m.desc,
      tags: ["deck", "slide", "archetype", key],
      runtime: { kind: "core-archetype", key },   // rendered by core/RenderType → Slide builder `key`
      defaults: SAMPLES[key] || {},               // representative content (also the preview seed)
      provenance: "built-in",
    };
  });

  if (typeof window !== "undefined") {
    window.CV_ARCHETYPE_META = META;
    window.CV_ARCHETYPE_CATALOG = seeds;
  }
  if (typeof module !== "undefined" && module.exports) module.exports = { META, seeds };
})();
