// assets/icons/icon-paths.js
// ⚠️ DEPRECATED — DO NOT EXTEND. The single home for icons is `cv-icons.js`
// (`window.CV_ICONS.data`), rendered by `CvIcon.jsx`. That set carries the brand
// stroke weight, the named feature glyphs, aliases, and the node-shape containers.
// This file (`window.CONCEPTV_ICONS` + `ConceptVIcon.jsx`) is a legacy parallel list
// kept only so older consumers don't break; migrate them to CvIcon and delete this.
//
// Canonical ConceptV icon library — source of truth for SVG inner content.
// Render each via the ConceptVIcon component. All icons share:
//   viewBox: 0 0 24 24
//   stroke:  currentColor
//   stroke-width: 1.5 (default; pass `weight` prop to override)
//   stroke-linecap / linejoin: round
//   fill: none (unless the icon's path explicitly fills)
//
// Icons are tagged with their `set`:
//   "core"        — vectorised from the source bronze sheet
//   "ext-status"  — semantic status icons (success/error/info/warning)
//   "ext-ui"      — common UI controls (plus/minus/close/chevrons/dots/menu)
//   "ext-media"   — play/pause/volume/etc.
//   "ext-files"   — file-type variants
//   "ext-arch"    — additional architecture-specific (ruler/compass/grid)
//   "ext-time"    — time/clock variants
//   "ext-comms"   — additional messaging / collab
//
// Path strings inside `body` are inserted as-is; <path>, <circle>, <rect>, <line>, <polyline> all valid.

window.CONCEPTV_ICONS = {
  // ============================================================
  // CORE — from the bronze sheet (row by row, left to right)
  // ============================================================

  // Row 1
  'chat-arrow':         { set: 'core', cat: 'Comms', body: `<path d="M3 5 h13 a2 2 0 0 1 2 2 v6 a2 2 0 0 1 -2 2 H8 L4 18 V15 H3 V5 Z"/><path d="M9 11 L13 11 L11.5 9.5 M13 11 L11.5 12.5"/>` },
  'chats-double':       { set: 'core', cat: 'Comms', body: `<path d="M3 5 h11 a2 2 0 0 1 2 2 v5 a2 2 0 0 1 -2 2 H7 L4 16 V14 H3 V5 Z"/><path d="M8 9 h10 a2 2 0 0 1 2 2 v6 a2 2 0 0 1 -2 2 h-3 L12 21 V19 H8 a2 2 0 0 1 -2 -2 v-6 a2 2 0 0 1 2 -2 Z"/>` },
  'checklist-double':   { set: 'core', cat: 'Files', body: `<rect x="5" y="3" width="14" height="16" rx="1"/><rect x="3" y="5" width="14" height="16" rx="1" fill="var(--cv-icon-bg, #fff)"/><path d="M6 11 l2 2 l4 -4"/>` },
  'filter':             { set: 'core', cat: 'Action', body: `<path d="M3 5 H21 L14 13 V20 L10 18 V13 L3 5 Z"/>` },
  'sort-vertical':      { set: 'core', cat: 'Action', body: `<path d="M7 3 V21 M4 6 L7 3 L10 6"/><path d="M17 21 V3 M14 18 L17 21 L20 18"/>` },
  'search':             { set: 'core', cat: 'Action', body: `<circle cx="11" cy="11" r="7"/><path d="M16 16 L21 21"/>` },
  'building-house':     { set: 'core', cat: 'Arch',   body: `<path d="M3 21 V11 L9 7 L15 11 V21 Z"/><path d="M11 21 V15 H13 V21"/><path d="M15 21 V13 H21 V21 Z"/><path d="M18 13 V10 M18 17 V18"/>` },
  'building-cost':      { set: 'core', cat: 'Arch',   body: `<path d="M3 21 V8 L10 5 L17 8 V21 Z"/><path d="M6 11 H8 M11 11 H13 M6 15 H8 M11 15 H13"/><circle cx="18" cy="17" r="4"/><path d="M18 15 V19 M16.5 16 H19 M16.5 18 H19"/>` },
  'people-network':     { set: 'core', cat: 'People', body: `<circle cx="6" cy="6" r="2.2"/><circle cx="18" cy="6" r="2.2"/><circle cx="6" cy="18" r="2.2"/><circle cx="18" cy="18" r="2.2"/><circle cx="12" cy="12" r="2.2"/><path d="M8 7 L10.5 11 M16 7 L13.5 11 M8 17 L10.5 13 M16 17 L13.5 13"/>` },
  'crane':              { set: 'core', cat: 'Arch',   body: `<path d="M4 21 H8 V10 H4 Z"/><path d="M6 10 V4 H20"/><path d="M20 4 V8 M16 8 H22 L20 11 L16 8 Z"/><path d="M14 6 H17"/>` },

  // Row 2
  'checkbox-empty':     { set: 'core', cat: 'Action', body: `<rect x="4" y="4" width="16" height="16" rx="2"/>` },
  'checkbox-checked':   { set: 'core', cat: 'Action', body: `<rect x="4" y="4" width="16" height="16" rx="2" fill="currentColor"/><path d="M8 12 L11 15 L16 9" stroke="var(--cv-icon-bg, #fff)"/>` },
  'network-people-bg':  { set: 'core', cat: 'People', body: `<circle cx="6" cy="9" r="2.2"/><circle cx="18" cy="9" r="2.2"/><circle cx="12" cy="17" r="2.2"/><path d="M8 9 H16 M7 11 L11 15 M17 11 L13 15"/>` },
  'hand-clock':         { set: 'core', cat: 'Action', body: `<path d="M3 19 a5 5 0 0 1 5 -5 h6 a5 5 0 0 1 5 5 V21 H3 Z"/><circle cx="11" cy="8" r="5"/><path d="M11 6 V8 L12.5 9.5"/>` },
  'file-settings':      { set: 'core', cat: 'Files',  body: `<path d="M5 3 H14 L19 8 V21 H5 Z"/><path d="M14 3 V8 H19"/><circle cx="12" cy="15" r="2.5"/><path d="M12 11.5 V12.5 M12 17.5 V18.5 M15.5 15 H14.5 M9.5 15 H8.5"/>` },
  'globe-thumb':        { set: 'core', cat: 'Action', body: `<circle cx="12" cy="12" r="9"/><path d="M3 12 H21 M12 3 a14 14 0 0 1 0 18 M12 3 a14 14 0 0 0 0 18"/><path d="M10 10 L12 8 L14 10 V14 H10 Z" fill="var(--cv-icon-bg, #fff)"/>` },
  'handshake':          { set: 'core', cat: 'People', body: `<path d="M2 11 L7 6 L12 8 L17 6 L22 11"/><path d="M5 14 L9 10 L13 12 L17 9 L21 13"/><path d="M9 18 L12 15 L15 18"/>` },
  'team-bulb':          { set: 'core', cat: 'People', body: `<circle cx="8" cy="9" r="2.5"/><circle cx="16" cy="9" r="2.5"/><path d="M3 19 a5 5 0 0 1 5 -5 h0 a5 5 0 0 1 5 5"/><path d="M11 19 a5 5 0 0 1 5 -5 h0 a5 5 0 0 1 5 5"/><circle cx="12" cy="4" r="1.5"/><path d="M12 5.5 V7"/>` },
  'devices-multi':      { set: 'core', cat: 'Tech',   body: `<rect x="3" y="6" width="13" height="9" rx="1"/><rect x="14" y="9" width="7" height="11" rx="1"/><path d="M5 18 H10 M8 15 V18"/>` },

  // Row 3
  'drone':              { set: 'core', cat: 'Tech',   body: `<rect x="9" y="10" width="6" height="4" rx="0.5"/><circle cx="5" cy="8" r="2.5"/><circle cx="19" cy="8" r="2.5"/><path d="M7 10 L9 11 M17 10 L15 11"/><path d="M10 15 L9 18 M14 15 L15 18"/><path d="M12 17 V19 M10 19 H14"/>` },
  'palette-swatches':   { set: 'core', cat: 'Brand',  body: `<path d="M5 5 L12 3 L19 5 L18 14 L12 17 L6 14 Z"/><path d="M9 6 L12 5 L15 6"/><path d="M8 9 L12 8 L16 9"/><path d="M8 12 L12 11 L16 12"/>` },
  'lamp-sofa':          { set: 'core', cat: 'Arch',   body: `<path d="M7 11 L9 7 H11 L9.5 11 Z"/><path d="M10 11 V19"/><path d="M3 19 V16 a2 2 0 0 1 2 -2 h13 a2 2 0 0 1 2 2 v3"/><path d="M3 19 H21 V21 H3 Z"/><path d="M5 14 V12 a2 2 0 0 1 2 -2"/>` },
  'lightbulb':          { set: 'core', cat: 'Action', body: `<path d="M9 17 V14 a5 5 0 1 1 6 0 V17 Z"/><path d="M10 19 H14 M11 21 H13"/>` },
  'megaphone':          { set: 'core', cat: 'Comms',  body: `<path d="M4 11 L16 7 V17 L4 13 Z"/><path d="M16 9 L20 8 V16 L16 15"/><circle cx="8" cy="12" r="2"/><path d="M9 15 V19"/>` },
  'file-pdf':           { set: 'core', cat: 'Files',  body: `<path d="M5 3 H14 L19 8 V21 H5 Z"/><path d="M14 3 V8 H19"/><text x="7" y="17" font-size="5" font-weight="700" fill="currentColor" stroke="none">PDF</text>` },
  'file-upload':        { set: 'core', cat: 'Files',  body: `<path d="M5 3 H14 L19 8 V21 H5 Z"/><path d="M14 3 V8 H19"/><path d="M12 18 V13 M10 15 L12 13 L14 15"/>` },
  'file-list':          { set: 'core', cat: 'Files',  body: `<path d="M5 3 H14 L19 8 V21 H5 Z"/><path d="M14 3 V8 H19"/><circle cx="8" cy="13" r=".7" fill="currentColor"/><circle cx="8" cy="16" r=".7" fill="currentColor"/><circle cx="8" cy="19" r=".7" fill="currentColor"/><path d="M10 13 H16 M10 16 H16 M10 19 H14"/>` },

  // Row 4
  'flow-diagram':       { set: 'core', cat: 'Process',body: `<rect x="3" y="14" width="7" height="6" rx="1"/><rect x="14" y="14" width="7" height="6" rx="1"/><rect x="9" y="4"  width="6" height="5" rx="1"/><path d="M12 9 V12 L6.5 14 M12 12 L17.5 14"/>` },
  'cube-iso':           { set: 'core', cat: 'Arch',   body: `<path d="M12 3 L21 8 V17 L12 22 L3 17 V8 Z"/><path d="M12 12 V22 M3 8 L12 12 L21 8"/>` },
  'world-network':      { set: 'core', cat: 'Tech',   body: `<circle cx="12" cy="12" r="9"/><circle cx="6" cy="6" r="1.5"/><circle cx="18" cy="6" r="1.5"/><circle cx="6" cy="18" r="1.5"/><circle cx="18" cy="18" r="1.5"/><circle cx="12" cy="12" r="1.5"/><path d="M7.5 7.5 L10.5 10.5 M16.5 7.5 L13.5 10.5 M7.5 16.5 L10.5 13.5 M16.5 16.5 L13.5 13.5"/>` },
  'handshake-simple':   { set: 'core', cat: 'People', body: `<path d="M3 12 L7 8 L12 13 L17 8 L21 12"/><path d="M7 13 L12 18 L17 13"/>` },
  'pie-chart':          { set: 'core', cat: 'Data',   body: `<path d="M12 3 a9 9 0 1 0 9 9 H12 Z" fill="currentColor" stroke="none"/><path d="M12 3 a9 9 0 1 0 9 9 H12 Z"/><path d="M14 3 a9 9 0 0 1 7 7 H14 Z" fill="var(--cv-icon-bg, #fff)"/>` },
  'browser-house':      { set: 'core', cat: 'Tech',   body: `<rect x="3" y="5" width="18" height="14" rx="1"/><path d="M3 9 H21"/><circle cx="6" cy="7" r=".5" fill="currentColor"/><circle cx="8" cy="7" r=".5" fill="currentColor"/><path d="M9 17 V13 L12 11 L15 13 V17 Z M11 17 V15 H13 V17"/>` },
  'browser-house-info': { set: 'core', cat: 'Tech',   body: `<rect x="3" y="5" width="18" height="14" rx="1"/><path d="M3 9 H21"/><circle cx="6" cy="7" r=".5" fill="currentColor"/><circle cx="8" cy="7" r=".5" fill="currentColor"/><path d="M5 16 V13 L8 11 L11 13 V16 Z"/><path d="M13 13 H19 M13 15 H17"/>` },
  'browser-analytics':  { set: 'core', cat: 'Data',   body: `<rect x="3" y="5" width="18" height="14" rx="1"/><path d="M3 9 H21"/><circle cx="6" cy="7" r=".5" fill="currentColor"/><circle cx="8" cy="7" r=".5" fill="currentColor"/><circle cx="8" cy="14" r="2.2"/><path d="M11 17 L14 13 L16 15 L19 12"/>` },
  'browser-info':       { set: 'core', cat: 'Tech',   body: `<rect x="3" y="5" width="18" height="14" rx="1"/><path d="M3 9 H21"/><circle cx="6" cy="7" r=".5" fill="currentColor"/><circle cx="8" cy="7" r=".5" fill="currentColor"/><path d="M5 16 V13 L8 11 L11 13 V16 Z"/><circle cx="16" cy="14" r="2.5"/><path d="M16 13 V14 M16 15.5 V15.51"/>` },

  // Row 5
  'gear':               { set: 'core', cat: 'Action', body: `<circle cx="12" cy="12" r="3"/><path d="M12 3 V5 M12 19 V21 M21 12 H19 M5 12 H3 M18.4 5.6 L17 7 M7 17 L5.6 18.4 M18.4 18.4 L17 17 M7 7 L5.6 5.6"/>` },
  'cloud-up':           { set: 'core', cat: 'Action', body: `<path d="M6 17 a4 4 0 1 1 1 -7.9 a5 5 0 0 1 9.9 1 a3.5 3.5 0 0 1 -1 6.9 H7"/><path d="M12 19 V13 M10 15 L12 13 L14 15"/>` },
  'sync':               { set: 'core', cat: 'Action', body: `<path d="M4 12 a8 8 0 0 1 14 -5"/><path d="M18 3 V7 H14"/><path d="M20 12 a8 8 0 0 1 -14 5"/><path d="M6 21 V17 H10"/>` },
  'cloud-down':         { set: 'core', cat: 'Action', body: `<path d="M6 17 a4 4 0 1 1 1 -7.9 a5 5 0 0 1 9.9 1 a3.5 3.5 0 0 1 -1 6.9 H7"/><path d="M12 13 V19 M10 17 L12 19 L14 17"/>` },
  'files-copy':         { set: 'core', cat: 'Files',  body: `<rect x="8" y="3" width="11" height="14" rx="1"/><path d="M5 7 V21 H16"/>` },
  'user-circle':        { set: 'core', cat: 'People', body: `<circle cx="12" cy="9" r="3.5"/><path d="M5 20 a7 7 0 0 1 14 0"/>` },
  'database-stack':     { set: 'core', cat: 'Data',   body: `<ellipse cx="12" cy="5" rx="8" ry="2.5"/><path d="M4 5 V11 a8 2.5 0 0 0 16 0 V5"/><path d="M4 11 V17 a8 2.5 0 0 0 16 0 V11"/>` },
  'dollar-circle':      { set: 'core', cat: 'Data',   body: `<circle cx="12" cy="12" r="9"/><path d="M14.5 9 H10.5 a1.5 1.5 0 0 0 0 3 H13.5 a1.5 1.5 0 0 1 0 3 H9.5 M12 7 V17"/>` },
  'info-circle':        { set: 'core', cat: 'Action', body: `<circle cx="12" cy="12" r="9"/><path d="M12 11 V16 M12 8 V8.01"/>` },

  // Row 6
  'info-circle-thin':   { set: 'core', cat: 'Action', body: `<circle cx="12" cy="12" r="9"/><path d="M11 11 H13 V16 H11 Z M12 7 V9"/>` },
  'video-window':       { set: 'core', cat: 'Media',  body: `<rect x="3" y="5" width="14" height="14" rx="1"/><path d="M9 9 L13 12 L9 15 Z"/><path d="M17 9 L21 7 V17 L17 15"/>` },
  'route':              { set: 'core', cat: 'Process',body: `<circle cx="5" cy="7" r="2"/><circle cx="19" cy="17" r="2"/><path d="M7 7 H11 a4 4 0 0 1 4 4 v2 a4 4 0 0 0 4 4"/><path d="M13 5 H15 M13 9 H15"/>` },
  'vr-headset':         { set: 'core', cat: 'Tech',   body: `<rect x="2" y="8" width="20" height="9" rx="3"/><circle cx="7" cy="12.5" r="2.2"/><circle cx="17" cy="12.5" r="2.2"/>` },
  'swap-arrows':        { set: 'core', cat: 'Action', body: `<path d="M3 9 H17 M14 6 L17 9 L14 12"/><path d="M21 15 H7 M10 18 L7 15 L10 12"/>` },
  'no-atom':            { set: 'core', cat: 'Action', body: `<circle cx="12" cy="12" r="9"/><path d="M5 5 L19 19"/><ellipse cx="12" cy="12" rx="9" ry="3.5" transform="rotate(-30 12 12)"/><ellipse cx="12" cy="12" rx="9" ry="3.5" transform="rotate(30 12 12)"/>` },
  'location-pin':       { set: 'core', cat: 'Place',  body: `<path d="M12 22 C12 22 5 14 5 10 a7 7 0 1 1 14 0 c0 4 -7 12 -7 12 Z"/><circle cx="12" cy="10" r="2.5"/>` },
  'floorplan-tag':      { set: 'core', cat: 'Arch',   body: `<rect x="3" y="3" width="14" height="14" rx="1"/><path d="M9 3 V11 M3 11 H17 M14 11 V17"/><path d="M18 16 L22 20 V22 H20 L18 20 Z"/>` },
  'share-network':      { set: 'core', cat: 'Action', body: `<circle cx="6" cy="12" r="2.5"/><circle cx="18" cy="6" r="2.5"/><circle cx="18" cy="18" r="2.5"/><path d="M8 11 L16 7 M8 13 L16 17"/>` },

  // Row 7
  'eye-off':            { set: 'core', cat: 'Action', body: `<path d="M3 12 s3 -7 9 -7 a8 8 0 0 1 5 1.5"/><path d="M21 12 s-2 4 -6 6"/><path d="M9 9 a3 3 0 0 0 4 4"/><path d="M3 3 L21 21"/>` },
  'eye-glow':           { set: 'core', cat: 'Action', body: `<path d="M3 12 s3 -7 9 -7 s9 7 9 7 s-3 7 -9 7 s-9 -7 -9 -7 Z"/><circle cx="12" cy="12" r="2.5"/><path d="M12 1 V3 M3 12 H1 M21 12 H23 M12 21 V23 M5 5 L4 4 M19 5 L20 4 M5 19 L4 20 M19 19 L20 20"/>` },
  'pencil-edit':        { set: 'core', cat: 'Action', body: `<rect x="3" y="5" width="14" height="14" rx="1"/><path d="M16 4 L20 8 L12 16 L8 17 L9 13 Z"/>` },
  'chat-bubbles':       { set: 'core', cat: 'Comms',  body: `<path d="M3 5 h11 a2 2 0 0 1 2 2 v5 a2 2 0 0 1 -2 2 H7 L4 16 V14 H3 V5 Z"/><path d="M10 11 h10 a2 2 0 0 1 2 2 v5 a2 2 0 0 1 -2 2 h-3 L14 22 V20 H10 a2 2 0 0 1 -2 -2"/>` },
  '3d-edit':            { set: 'core', cat: 'Arch',   body: `<rect x="4" y="4" width="16" height="16" rx="1"/><path d="M8 16 L12 8 L16 16 M9.5 13 H14.5"/><path d="M18 7 L20 9 L15 14 L13 14 L13 12 Z"/>` },
  'monitor-house':      { set: 'core', cat: 'Tech',   body: `<rect x="3" y="5" width="18" height="11" rx="1"/><path d="M3 9 H21"/><circle cx="6" cy="7" r=".5" fill="currentColor"/><path d="M7 14 V11 L10 9 L13 11 V14 Z"/><path d="M14 11 H19 M14 13 H17"/><path d="M9 19 H15 M12 16 V19"/>` },
  'brochure':           { set: 'core', cat: 'Files',  body: `<path d="M3 18 V6 a2 2 0 0 1 2 -2 h14 a2 2 0 0 1 2 2 V18 H13 a2 2 0 0 0 -2 2 a2 2 0 0 0 -2 -2 Z"/><path d="M11 7 V20 M7 9 H9 M7 12 H9 M15 9 H17 M15 12 H17"/>` },

  // Row 8
  'floorplan-xyz':      { set: 'core', cat: 'Arch',   body: `<path d="M5 19 L9 14 H15 L19 19 H5 Z"/><path d="M9 14 L11 11 H13 L15 14"/><path d="M11 11 V9"/><path d="M3 21 L3 20 L4 20 M4 17 L4 18 M6 22 L7 22"/><text x="2" y="23" font-size="2.5" fill="currentColor" stroke="none">x</text><text x="3.5" y="16" font-size="2.5" fill="currentColor" stroke="none">y</text><text x="6" y="24" font-size="2.5" fill="currentColor" stroke="none">z</text>` },
  'skyline':            { set: 'core', cat: 'Arch',   body: `<path d="M3 21 V10 L9 7 V21 Z"/><path d="M9 21 V12 L15 9 V21 Z"/><path d="M15 21 V14 L21 11 V21 Z"/><circle cx="6" cy="13" r=".5" fill="currentColor"/><circle cx="6" cy="16" r=".5" fill="currentColor"/><circle cx="12" cy="15" r=".5" fill="currentColor"/><circle cx="12" cy="18" r=".5" fill="currentColor"/><circle cx="18" cy="17" r=".5" fill="currentColor"/>` },
  'house-trees':        { set: 'core', cat: 'Arch',   body: `<path d="M5 21 V14 L11 10 L17 14 V21 Z"/><path d="M9 21 V16 H13 V21"/><circle cx="20" cy="16" r="2.5"/><path d="M20 19 V21"/><circle cx="3" cy="18" r="2"/><path d="M3 20 V21"/>` },
  'house-roof':         { set: 'core', cat: 'Arch',   body: `<path d="M3 12 L12 4 L21 12"/><path d="M5 11 V21 H19 V11"/><path d="M10 21 V14 H14 V21"/>` },
  'area-m2':            { set: 'core', cat: 'Arch',   body: `<path d="M4 4 V20 H20"/><path d="M4 7 H6 M4 10 H7 M4 13 H6 M4 16 H7"/><path d="M7 20 V18 M10 20 V17 M13 20 V18 M16 20 V17"/><text x="9" y="11" font-size="6" font-weight="700" fill="currentColor" stroke="none">m</text><text x="15" y="9" font-size="3.5" fill="currentColor" stroke="none">2</text>` },
  'tile-stack':         { set: 'core', cat: 'Arch',   body: `<path d="M4 11 L12 7 L20 11 L12 15 Z"/><path d="M4 15 L12 19 L20 15"/><path d="M8 9 L12 11 M14 9 L10 11"/>` },
  'calendar':           { set: 'core', cat: 'Time',   body: `<rect x="3" y="5" width="18" height="16" rx="1"/><path d="M3 9 H21 M8 3 V7 M16 3 V7"/><path d="M7 13 H8 M11 13 H12 M15 13 H16 M7 17 H8 M11 17 H12 M15 17 H16"/>` },
  'image-stack':        { set: 'core', cat: 'Media',  body: `<rect x="3" y="7" width="14" height="11" rx="1"/><rect x="7" y="5" width="14" height="11" rx="1" fill="var(--cv-icon-bg, #fff)"/><circle cx="11" cy="9" r="1.5"/><path d="M7 14 L11 11 L15 14 L18 12 L21 14"/>` },
  'sitemap':            { set: 'core', cat: 'Process',body: `<rect x="9"  y="3"  width="6" height="4" rx="1"/><rect x="3"  y="17" width="6" height="4" rx="1"/><rect x="9"  y="17" width="6" height="4" rx="1"/><rect x="15" y="17" width="6" height="4" rx="1"/><path d="M12 7 V12 M6 17 V14 H18 V17 M12 14 V12"/>` },

  // ============================================================
  // EXT-STATUS — semantic status icons (fill-style for emphasis)
  // ============================================================
  'success':            { set: 'ext-status', cat: 'Status', body: `<circle cx="12" cy="12" r="9" fill="currentColor" stroke="none"/><path d="M7.5 12.5 L11 16 L16.5 9" stroke="var(--cv-icon-bg, #fff)"/>` },
  'success-outline':    { set: 'ext-status', cat: 'Status', body: `<circle cx="12" cy="12" r="9"/><path d="M7.5 12.5 L11 16 L16.5 9"/>` },
  'warning':            { set: 'ext-status', cat: 'Status', body: `<path d="M12 3 L22 20 H2 Z" fill="currentColor" stroke="none"/><path d="M12 10 V14 M12 17 V17.01" stroke="var(--cv-icon-bg, #fff)"/>` },
  'warning-outline':    { set: 'ext-status', cat: 'Status', body: `<path d="M12 3 L22 20 H2 Z"/><path d="M12 10 V14 M12 17 V17.01"/>` },
  'error':              { set: 'ext-status', cat: 'Status', body: `<circle cx="12" cy="12" r="9" fill="currentColor" stroke="none"/><path d="M8.5 8.5 L15.5 15.5 M15.5 8.5 L8.5 15.5" stroke="var(--cv-icon-bg, #fff)"/>` },
  'error-outline':      { set: 'ext-status', cat: 'Status', body: `<circle cx="12" cy="12" r="9"/><path d="M8.5 8.5 L15.5 15.5 M15.5 8.5 L8.5 15.5"/>` },
  'info':               { set: 'ext-status', cat: 'Status', body: `<circle cx="12" cy="12" r="9" fill="currentColor" stroke="none"/><path d="M12 11 V16.5 M12 7.5 V8.5" stroke="var(--cv-icon-bg, #fff)"/>` },
  'pending-dot':        { set: 'ext-status', cat: 'Status', body: `<circle cx="12" cy="12" r="9"/><circle cx="8" cy="12" r="1" fill="currentColor"/><circle cx="12" cy="12" r="1" fill="currentColor"/><circle cx="16" cy="12" r="1" fill="currentColor"/>` },

  // ============================================================
  // EXT-UI — common UI controls
  // ============================================================
  'plus':               { set: 'ext-ui',     cat: 'UI',     body: `<path d="M12 5 V19 M5 12 H19"/>` },
  'minus':              { set: 'ext-ui',     cat: 'UI',     body: `<path d="M5 12 H19"/>` },
  'close':              { set: 'ext-ui',     cat: 'UI',     body: `<path d="M6 6 L18 18 M18 6 L6 18"/>` },
  'check':              { set: 'ext-ui',     cat: 'UI',     body: `<path d="M5 13 L10 18 L20 7"/>` },
  'menu':               { set: 'ext-ui',     cat: 'UI',     body: `<path d="M4 7 H20 M4 12 H20 M4 17 H20"/>` },
  'dots-vertical':      { set: 'ext-ui',     cat: 'UI',     body: `<circle cx="12" cy="6"  r="1.4" fill="currentColor"/><circle cx="12" cy="12" r="1.4" fill="currentColor"/><circle cx="12" cy="18" r="1.4" fill="currentColor"/>` },
  'dots-horizontal':    { set: 'ext-ui',     cat: 'UI',     body: `<circle cx="6"  cy="12" r="1.4" fill="currentColor"/><circle cx="12" cy="12" r="1.4" fill="currentColor"/><circle cx="18" cy="12" r="1.4" fill="currentColor"/>` },
  'chevron-up':         { set: 'ext-ui',     cat: 'UI',     body: `<path d="M6 15 L12 9 L18 15"/>` },
  'chevron-down':       { set: 'ext-ui',     cat: 'UI',     body: `<path d="M6 9 L12 15 L18 9"/>` },
  'chevron-left':       { set: 'ext-ui',     cat: 'UI',     body: `<path d="M15 6 L9 12 L15 18"/>` },
  'chevron-right':      { set: 'ext-ui',     cat: 'UI',     body: `<path d="M9 6 L15 12 L9 18"/>` },
  'arrow-up':           { set: 'ext-ui',     cat: 'UI',     body: `<path d="M12 5 V19 M6 11 L12 5 L18 11"/>` },
  'arrow-down':         { set: 'ext-ui',     cat: 'UI',     body: `<path d="M12 5 V19 M6 13 L12 19 L18 13"/>` },
  'arrow-left':         { set: 'ext-ui',     cat: 'UI',     body: `<path d="M19 12 H5 M11 6 L5 12 L11 18"/>` },
  'arrow-right':        { set: 'ext-ui',     cat: 'UI',     body: `<path d="M5 12 H19 M13 6 L19 12 L13 18"/>` },
  'arrow-up-right':     { set: 'ext-ui',     cat: 'UI',     body: `<path d="M7 17 L17 7 M9 7 H17 V15"/>` },
  'external-link':      { set: 'ext-ui',     cat: 'UI',     body: `<path d="M14 4 H20 V10 M20 4 L11 13 M19 14 V19 a1 1 0 0 1 -1 1 H5 a1 1 0 0 1 -1 -1 V6 a1 1 0 0 1 1 -1 h5"/>` },
  'expand':             { set: 'ext-ui',     cat: 'UI',     body: `<path d="M4 9 V4 H9 M15 4 H20 V9 M4 15 V20 H9 M20 15 V20 H15"/>` },
  'collapse':           { set: 'ext-ui',     cat: 'UI',     body: `<path d="M9 4 V9 H4 M15 9 H20 V4 M4 15 H9 V20 M20 15 H15 V20"/>` },
  'maximize':           { set: 'ext-ui',     cat: 'UI',     body: `<rect x="4" y="4" width="16" height="16" rx="1"/>` },
  'lock':               { set: 'ext-ui',     cat: 'UI',     body: `<rect x="5" y="11" width="14" height="9" rx="1.5"/><path d="M8 11 V8 a4 4 0 0 1 8 0 V11"/>` },
  'lock-open':          { set: 'ext-ui',     cat: 'UI',     body: `<rect x="5" y="11" width="14" height="9" rx="1.5"/><path d="M8 11 V8 a4 4 0 0 1 7.5 -2"/>` },
  'star':               { set: 'ext-ui',     cat: 'UI',     body: `<path d="M12 3 L14.5 9 L21 9.5 L16 14 L17.5 20.5 L12 17 L6.5 20.5 L8 14 L3 9.5 L9.5 9 Z"/>` },
  'star-fill':          { set: 'ext-ui',     cat: 'UI',     body: `<path d="M12 3 L14.5 9 L21 9.5 L16 14 L17.5 20.5 L12 17 L6.5 20.5 L8 14 L3 9.5 L9.5 9 Z" fill="currentColor" stroke="none"/>` },
  'heart':              { set: 'ext-ui',     cat: 'UI',     body: `<path d="M12 20 S4 14.5 4 9 a4.5 4.5 0 0 1 8 -3 a4.5 4.5 0 0 1 8 3 c0 5.5 -8 11 -8 11 Z"/>` },
  'bookmark':           { set: 'ext-ui',     cat: 'UI',     body: `<path d="M6 4 H18 V20 L12 16 L6 20 Z"/>` },
  'trash':              { set: 'ext-ui',     cat: 'UI',     body: `<path d="M5 7 H19 M8 7 V5 a1 1 0 0 1 1 -1 H15 a1 1 0 0 1 1 1 V7 M6 7 L7 20 a1 1 0 0 0 1 1 H16 a1 1 0 0 0 1 -1 L18 7"/><path d="M10 11 V18 M14 11 V18"/>` },
  'download':           { set: 'ext-ui',     cat: 'UI',     body: `<path d="M12 4 V16 M7 11 L12 16 L17 11 M4 20 H20"/>` },
  'upload':             { set: 'ext-ui',     cat: 'UI',     body: `<path d="M12 16 V4 M7 9 L12 4 L17 9 M4 20 H20"/>` },
  'send':               { set: 'ext-ui',     cat: 'UI',     body: `<path d="M3 12 L21 4 L13 21 L11 13 Z"/><path d="M11 13 L21 4"/>` },
  'home':               { set: 'ext-ui',     cat: 'UI',     body: `<path d="M3 12 L12 4 L21 12 M5 10 V20 H19 V10 M10 20 V14 H14 V20"/>` },

  // ============================================================
  // EXT-MEDIA — media controls + media types
  // ============================================================
  'play':               { set: 'ext-media',  cat: 'Media',  body: `<path d="M7 4 L20 12 L7 20 Z"/>` },
  'pause':              { set: 'ext-media',  cat: 'Media',  body: `<rect x="6" y="4" width="4" height="16" rx="1"/><rect x="14" y="4" width="4" height="16" rx="1"/>` },
  'stop':               { set: 'ext-media',  cat: 'Media',  body: `<rect x="5" y="5" width="14" height="14" rx="1"/>` },
  'play-circle':        { set: 'ext-media',  cat: 'Media',  body: `<circle cx="12" cy="12" r="9"/><path d="M10 8 L16 12 L10 16 Z" fill="currentColor"/>` },
  'volume':             { set: 'ext-media',  cat: 'Media',  body: `<path d="M4 9 H7 L12 5 V19 L7 15 H4 Z"/><path d="M15 9 a4 4 0 0 1 0 6 M17 7 a7 7 0 0 1 0 10"/>` },
  'volume-mute':        { set: 'ext-media',  cat: 'Media',  body: `<path d="M4 9 H7 L12 5 V19 L7 15 H4 Z"/><path d="M16 9 L22 15 M22 9 L16 15"/>` },
  'camera':             { set: 'ext-media',  cat: 'Media',  body: `<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7 L9.5 4 H14.5 L16 7"/><circle cx="12" cy="13.5" r="3.5"/>` },
  'video-camera':       { set: 'ext-media',  cat: 'Media',  body: `<rect x="3" y="7" width="13" height="10" rx="1.5"/><path d="M16 10 L21 7 V17 L16 14 Z"/>` },
  'image':              { set: 'ext-media',  cat: 'Media',  body: `<rect x="3" y="5" width="18" height="14" rx="1"/><circle cx="9" cy="10" r="2"/><path d="M3 17 L9 12 L13 16 L16 13 L21 17"/>` },

  // ============================================================
  // EXT-FILES — additional file types
  // ============================================================
  'file':               { set: 'ext-files',  cat: 'Files',  body: `<path d="M5 3 H14 L19 8 V21 H5 Z"/><path d="M14 3 V8 H19"/>` },
  'file-text':          { set: 'ext-files',  cat: 'Files',  body: `<path d="M5 3 H14 L19 8 V21 H5 Z"/><path d="M14 3 V8 H19"/><path d="M8 12 H16 M8 15 H16 M8 18 H13"/>` },
  'file-image':         { set: 'ext-files',  cat: 'Files',  body: `<path d="M5 3 H14 L19 8 V21 H5 Z"/><path d="M14 3 V8 H19"/><circle cx="9" cy="13" r="1.3"/><path d="M5 19 L9 15 L13 18 L19 14"/>` },
  'file-video':         { set: 'ext-files',  cat: 'Files',  body: `<path d="M5 3 H14 L19 8 V21 H5 Z"/><path d="M14 3 V8 H19"/><path d="M9 13 L14 16 L9 19 Z"/>` },
  'file-csv':           { set: 'ext-files',  cat: 'Files',  body: `<path d="M5 3 H14 L19 8 V21 H5 Z"/><path d="M14 3 V8 H19"/><text x="7" y="17" font-size="4.5" font-weight="700" fill="currentColor" stroke="none">CSV</text>` },
  'file-doc':           { set: 'ext-files',  cat: 'Files',  body: `<path d="M5 3 H14 L19 8 V21 H5 Z"/><path d="M14 3 V8 H19"/><text x="7" y="17" font-size="4.5" font-weight="700" fill="currentColor" stroke="none">DOC</text>` },
  'file-zip':           { set: 'ext-files',  cat: 'Files',  body: `<path d="M5 3 H14 L19 8 V21 H5 Z"/><path d="M14 3 V8 H19"/><path d="M10 11 H12 V13 H10 Z M10 15 H12 V17 H10 Z"/>` },
  'folder':             { set: 'ext-files',  cat: 'Files',  body: `<path d="M3 7 a1 1 0 0 1 1 -1 H10 L12 8 H20 a1 1 0 0 1 1 1 V19 a1 1 0 0 1 -1 1 H4 a1 1 0 0 1 -1 -1 Z"/>` },
  'folder-open':        { set: 'ext-files',  cat: 'Files',  body: `<path d="M3 7 V19 a1 1 0 0 0 1 1 H19 L22 11 H5 L3 19"/><path d="M3 7 a1 1 0 0 1 1 -1 H10 L12 8 H20 a1 1 0 0 1 1 1 V11"/>` },

  // ============================================================
  // EXT-ARCH — architecture-specific extensions
  // ============================================================
  'ruler':              { set: 'ext-arch',   cat: 'Arch',   body: `<path d="M3 14 L14 3 L21 10 L10 21 Z"/><path d="M7 10 L9 12 M9 8 L12 11 M11 6 L13 8 M14 13 L16 15 M16 11 L18 13"/>` },
  'compass':            { set: 'ext-arch',   cat: 'Arch',   body: `<circle cx="12" cy="12" r="9"/><path d="M9 15 L12 8 L15 15 L12 13 Z"/>` },
  'north-arrow':        { set: 'ext-arch',   cat: 'Arch',   body: `<circle cx="12" cy="12" r="9"/><path d="M12 5 L15 13 L12 11 L9 13 Z" fill="currentColor"/><text x="11" y="20" font-size="4" font-weight="700" fill="currentColor" stroke="none">N</text>` },
  'level':              { set: 'ext-arch',   cat: 'Arch',   body: `<rect x="3" y="9" width="18" height="6" rx="1"/><circle cx="12" cy="12" r="1.8"/><path d="M7 9 V15 M17 9 V15"/>` },
  'blueprint':          { set: 'ext-arch',   cat: 'Arch',   body: `<rect x="3" y="4" width="18" height="16" rx="1"/><path d="M3 8 H21 M7 8 V20 M14 8 V14 M14 14 H21 M7 14 H14"/>` },
  'door':               { set: 'ext-arch',   cat: 'Arch',   body: `<rect x="5" y="3" width="14" height="18" rx="1"/><circle cx="15" cy="12" r=".8" fill="currentColor"/><path d="M3 21 H21"/>` },
  'window':             { set: 'ext-arch',   cat: 'Arch',   body: `<rect x="4" y="4" width="16" height="16" rx="1"/><path d="M12 4 V20 M4 12 H20"/>` },
  'stairs':             { set: 'ext-arch',   cat: 'Arch',   body: `<path d="M3 21 H7 V17 H11 V13 H15 V9 H19 V5"/>` },
  'staged-flow':        { set: 'ext-arch',   cat: 'Process',body: `<rect x="2"  y="9" width="6" height="6" rx="1"/><rect x="9"  y="9" width="6" height="6" rx="1"/><rect x="16" y="9" width="6" height="6" rx="1"/><path d="M8 12 L9 12 M15 12 L16 12" stroke-dasharray="1.5 1.5"/>` },

  // ============================================================
  // EXT-TIME — time / calendar variants
  // ============================================================
  'clock':              { set: 'ext-time',   cat: 'Time',   body: `<circle cx="12" cy="12" r="9"/><path d="M12 7 V12 L15 14"/>` },
  'clock-revision':     { set: 'ext-time',   cat: 'Time',   body: `<circle cx="12" cy="12" r="9"/><path d="M12 8 V12 L14.5 13.5"/><path d="M18 5 L19 7 L17 8"/>` },
  'calendar-add':       { set: 'ext-time',   cat: 'Time',   body: `<rect x="3" y="5" width="18" height="16" rx="1"/><path d="M3 9 H21 M8 3 V7 M16 3 V7"/><path d="M12 12 V18 M9 15 H15"/>` },
  'calendar-check':     { set: 'ext-time',   cat: 'Time',   body: `<rect x="3" y="5" width="18" height="16" rx="1"/><path d="M3 9 H21 M8 3 V7 M16 3 V7"/><path d="M9 15 L11 17 L15 13"/>` },
  'timer':              { set: 'ext-time',   cat: 'Time',   body: `<path d="M9 3 H15"/><path d="M12 8 V13"/><circle cx="12" cy="13" r="8"/><path d="M18 6 L20 4"/>` },
  'history':            { set: 'ext-time',   cat: 'Time',   body: `<path d="M4 12 a8 8 0 1 0 2.5 -5.8 L4 9 V4"/><path d="M12 8 V12 L15 14"/>` },

  // ============================================================
  // EXT-COMMS — additional comms / collaboration
  // ============================================================
  'bell':               { set: 'ext-comms',  cat: 'Comms',  body: `<path d="M6 17 V11 a6 6 0 0 1 12 0 v6 l1.5 2 H4.5 Z"/><path d="M9.5 19.5 a2.5 2.5 0 0 0 5 0"/>` },
  'bell-off':           { set: 'ext-comms',  cat: 'Comms',  body: `<path d="M6 17 V11 a6 6 0 0 1 6 -6"/><path d="M18 11 v6 l1.5 2 H6"/><path d="M3 3 L21 21"/>` },
  'mail':               { set: 'ext-comms',  cat: 'Comms',  body: `<rect x="3" y="5" width="18" height="14" rx="1"/><path d="M3 7 L12 13 L21 7"/>` },
  'at-sign':            { set: 'ext-comms',  cat: 'Comms',  body: `<circle cx="12" cy="12" r="4"/><path d="M16 12 V14 a3 3 0 0 0 6 0 V12 a10 10 0 1 0 -4 8"/>` },
  'at-mention':         { set: 'ext-comms',  cat: 'Comms',  body: `<circle cx="12" cy="12" r="3"/><path d="M15 12 V13 a2 2 0 0 0 4 0 V12 a7 7 0 1 0 -3 5.7"/>` },
  'speech-question':    { set: 'ext-comms',  cat: 'Comms',  body: `<path d="M3 5 h18 a1 1 0 0 1 1 1 V16 a1 1 0 0 1 -1 1 H9 L5 21 V17 H3 a1 1 0 0 1 -1 -1 V6 a1 1 0 0 1 1 -1 Z"/><path d="M10 9 a2 2 0 1 1 2 2 V13 M12 15 V15.01"/>` },
  'thread':             { set: 'ext-comms',  cat: 'Comms',  body: `<rect x="3" y="3" width="11" height="9" rx="1"/><rect x="10" y="12" width="11" height="9" rx="1"/><path d="M14 18 H17 M14 16 H17"/>` },

  // ============================================================
  // EXT-DATA — extra data / charts
  // ============================================================
  'chart-bar':          { set: 'ext-arch',   cat: 'Data',   body: `<path d="M4 21 V11 H8 V21 Z M10 21 V5 H14 V21 Z M16 21 V14 H20 V21 Z"/>` },
  'chart-line':         { set: 'ext-arch',   cat: 'Data',   body: `<path d="M3 20 H21 M3 20 V4"/><path d="M5 16 L9 11 L13 14 L17 7 L21 10"/>` },
  'trend-up':           { set: 'ext-arch',   cat: 'Data',   body: `<path d="M3 17 L9 11 L13 15 L21 7 M21 7 H15 M21 7 V13"/>` },
  'tag':                { set: 'ext-ui',     cat: 'UI',     body: `<path d="M2 12 L12 2 H21 V11 L11 21 Z"/><circle cx="16" cy="8" r="1.5"/>` },
  'link':               { set: 'ext-ui',     cat: 'UI',     body: `<path d="M9 15 L15 9"/><path d="M10 6 L13 3 a4 4 0 0 1 5.5 5.5 L16 11"/><path d="M14 18 L11 21 a4 4 0 0 1 -5.5 -5.5 L8 13"/>` },
  'pin':                { set: 'ext-ui',     cat: 'UI',     body: `<path d="M9 3 V8 L5 12 H12 V19 L9 22 V12 H19 L15 8 V3 Z"/>` },
};
