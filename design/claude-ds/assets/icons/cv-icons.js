/**
 * ConceptV Icon Library — single source of truth
 * 
 * Every icon is designed on a 24×24 grid, with a 1.5 px stroke,
 * rounded caps and joins, no fills. Use `currentColor` for stroke
 * so the same SVG can be tinted bronze (#988058), gold (#E0C010),
 * dark, or any other context color.
 *
 * USAGE
 * -----
 * In React:        <CvIcon name="house" />  or  <CvIcon name="house" circle />
 * In raw HTML:     <svg ...><use href="../../assets/icons/svg/house.svg#i"/></svg>
 *                  — or just <img src="../../assets/icons/svg/house.svg"/>
 *
 * EXTENDING
 * ---------
 * Add a new entry to ICONS below. Keep the stroke style consistent:
 * - viewBox always "0 0 24 24"
 * - default stroke width 1.5 (rendered via the wrapper)
 * - rounded caps + joins
 * - no fills unless the icon is intentionally a filled shape
 * - aim for ~20×20 active area inside the 24×24 box
 * - prefer simple, "architectural" geometry over decoration
 *
 * After adding an entry, re-run `scripts/build-icon-svgs.html`
 * to regenerate the per-icon SVG files under assets/icons/svg/.
 */

window.CV_ICONS = window.CV_ICONS || {};
window.CV_ICONS.data = {

  // ===== People / roles =====
  'person':       `<path d="M12 12 a4 4 0 1 0 0 -8 a4 4 0 0 0 0 8 Z M4.5 20 a7.5 7.5 0 0 1 15 0"/>`,
  'people':       `<path d="M9 11 a3.5 3.5 0 1 0 0 -7 a3.5 3.5 0 0 0 0 7 Z M2.5 19.5 a6.5 6.5 0 0 1 13 0"/><path d="M15.5 6.5 a3.5 3.5 0 0 1 0 6.5 M21.5 19.5 a6.5 6.5 0 0 0 -5 -6.3"/>`,
  'person-add':   `<path d="M10 12 a4 4 0 1 0 0 -8 a4 4 0 0 0 0 8 Z M3 20 a7 7 0 0 1 14 0"/><path d="M19 6 V12 M16 9 H22"/>`,
  'person-clock': `<path d="M9 11 a3.5 3.5 0 1 0 0 -7 a3.5 3.5 0 0 0 0 7 Z M2.5 19 a6.5 6.5 0 0 1 13 0"/><circle cx="17.5" cy="16" r="4.5"/><path d="M17.5 13.5 V16 L19.5 17.5"/>`,
  'handshake':    `<path d="M2 11 L5.5 8 L11 12"/><path d="M22 11 L18.5 8 L13 12"/><path d="M11 12 L12 13 a1.4 1.4 0 0 0 2 0 L15 11.5"/><path d="M5.5 8 V13 a1.5 1.5 0 0 0 1.5 1.5 L11 18 a1.4 1.4 0 0 0 2 -0.3"/><path d="M18.5 8 V13 a1.5 1.5 0 0 1 -1.5 1.5"/><path d="M8.2 13.5 a1.3 1.3 0 0 1 1.9 0 M9.9 15.2 a1.3 1.3 0 0 1 1.9 0"/>`,
  'team':         `<circle cx="7" cy="8" r="2.6"/><path d="M2.6 16 a4.4 4.4 0 0 1 8.8 0"/><circle cx="17" cy="8" r="2.6"/><path d="M12.6 16 a4.4 4.4 0 0 1 8.8 0"/><circle cx="12" cy="13.5" r="2.8" fill="var(--cv-icon-bg)"/><path d="M6.6 22 a5.4 5.4 0 0 1 10.8 0" fill="var(--cv-icon-bg)"/>`,
  'user-network': `<circle cx="12" cy="5" r="2.2"/><path d="M9.4 9.5 a3 3 0 0 1 5.2 0"/><circle cx="5" cy="18" r="2.2"/><path d="M2.4 22 a3 3 0 0 1 5.2 0"/><circle cx="19" cy="18" r="2.2"/><path d="M16.4 22 a3 3 0 0 1 5.2 0"/><path d="M11 9.5 L6.2 14.5 M13 9.5 L17.8 14.5"/>`,
  'user-card':    `<rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="9" cy="12" r="2.5"/><path d="M5.5 17 a4 4 0 0 1 7 0"/><path d="M14.5 10 H19 M14.5 13 H18 M14.5 16 H17"/>`,

  // ===== Files / documents =====
  'file':         `<path d="M6 3 H14 L18 7 V21 H6 Z"/><path d="M14 3 V7 H18"/>`,
  'files-stack':  `<path d="M9 3.5 H15 L18.5 7 V14"/><path d="M15 3.5 V7 H18.5"/><path d="M5.5 8 H12 L15.5 11.5 V19.5 a1 1 0 0 1 -1 1 H6.5 a1 1 0 0 1 -1 -1 V9 a1 1 0 0 1 1 -1 Z"/><path d="M12 8 V11.5 H15.5"/>`,
  'file-upload':  `<path d="M6 3 H14 L18 7 V21 H6 Z M14 3 V7 H18"/><path d="M12 17 V11 M9 14 L12 11 L15 14"/>`,
  'file-download':`<path d="M6 3 H14 L18 7 V21 H6 Z M14 3 V7 H18"/><path d="M12 11 V17 M9 14 L12 17 L15 14"/>`,
  'file-pdf':     `<path d="M6 3 H14 L18 7 V21 H6 Z M14 3 V7 H18"/><text x="12" y="17" text-anchor="middle" font-family="DM Sans, sans-serif" font-size="5" font-weight="700" stroke="none" fill="currentColor">PDF</text>`,
  'file-list':    `<path d="M6 3 H14 L18 7 V21 H6 Z M14 3 V7 H18"/><path d="M9 12 H15 M9 15 H15 M9 18 H13"/><circle cx="8" cy="12" r="0.6" fill="currentColor" stroke="none"/><circle cx="8" cy="15" r="0.6" fill="currentColor" stroke="none"/><circle cx="8" cy="18" r="0.6" fill="currentColor" stroke="none"/>`,
  'file-edit':    `<path d="M6 3 H14 L18 7 V11"/><path d="M6 3 V21 H12"/><path d="M14 3 V7 H18"/><path d="M19.5 12.5 L21.5 14.5 L15.5 20.5 L13 21 L13.5 18.5 Z"/><path d="M18 14 L20 16"/>`,
  'file-gear':    `<path d="M6 3 H14 L18 7 V21 H6 Z M14 3 V7 H18"/><circle cx="12" cy="14" r="2"/><path d="M12 11 V12 M12 16 V17 M9 14 H10 M14 14 H15 M10 12 L10.7 12.7 M14 16 L13.3 15.3 M14 12 L13.3 12.7 M10 16 L10.7 15.3"/>`,
  'folder':       `<path d="M3 7 a2 2 0 0 1 2 -2 H9 L11 7 H19 a2 2 0 0 1 2 2 V18 a2 2 0 0 1 -2 2 H5 a2 2 0 0 1 -2 -2 Z"/>`,
  'folder-gear':  `<path d="M3 7 a2 2 0 0 1 2 -2 H9 L11 7 H19 a2 2 0 0 1 2 2 V18 a2 2 0 0 1 -2 2 H5 a2 2 0 0 1 -2 -2 Z"/><circle cx="12" cy="14.5" r="2"/><path d="M12 11.3 V12.5 M12 16.5 V17.7 M8.8 14.5 H10 M14 14.5 H15.2 M9.7 12.2 L10.6 13.1 M13.4 15.9 L14.3 16.8 M14.3 12.2 L13.4 13.1 M9.7 16.8 L10.6 15.9"/>`,
  'brochure':     `<path d="M3 6 L12 8 L21 6 V19 L12 21 L3 19 Z"/><path d="M12 8 V21"/><path d="M6 11 L10 11.9 M6 14 L10 14.9 M14 11.9 L18 11 M14 14.9 L18 14"/>`,
  'document':     `<path d="M6 3 H14 L18 7 V21 H6 Z M14 3 V7 H18"/><path d="M9 11 H15 M9 14 H15 M9 17 H13"/>`,
  'clipboard':    `<rect x="6" y="5" width="12" height="16" rx="1.5"/><rect x="9" y="3" width="6" height="3" rx="1"/><path d="M9 11 H15 M9 14 H15 M9 17 H13"/>`,

  // ===== Communication =====
  'chat':            `<path d="M4 5 a2 2 0 0 1 2 -2 H18 a2 2 0 0 1 2 2 V14 a2 2 0 0 1 -2 2 H10 L5 21 V16 a2 2 0 0 1 -1 -1.7 Z"/>`,
  'chat-double':     `<path d="M3 5 a2 2 0 0 1 2 -2 H14 a2 2 0 0 1 2 2 V11 a2 2 0 0 1 -2 2 H8 L5 16 V13 a2 2 0 0 1 -2 -2 Z"/><path d="M16 8 H20 a2 2 0 0 1 2 2 V15 a2 2 0 0 1 -2 2 V20 L17 17 H13 a2 2 0 0 1 -2 -2 V13"/>`,
  'chat-tree':       `<path d="M11 4 a1.5 1.5 0 0 1 1.5 -1.5 H19.5 a1.5 1.5 0 0 1 1.5 1.5 V8 a1.5 1.5 0 0 1 -1.5 1.5 H15 L12.5 12 V9.5 a1.5 1.5 0 0 1 -1.5 -1.5 Z"/><path d="M3 14 a1.5 1.5 0 0 1 1.5 -1.5 H10 a1.5 1.5 0 0 1 1.5 1.5 V18 a1.5 1.5 0 0 1 -1.5 1.5 H8 L5.5 22 V19.5 a1.5 1.5 0 0 1 -2.5 -1.1 Z"/><path d="M15.5 9.5 V12 a1.5 1.5 0 0 1 -1.5 1.5 H11.5"/>`,
  'megaphone':       `<path d="M3 10 a1.5 1.5 0 0 1 1.5 -1.5 H8 L19 4 V20 L8 15.5 H4.5 A1.5 1.5 0 0 1 3 14 Z"/><path d="M8 8.5 V15.5"/><path d="M8 15.5 V19 a1.5 1.5 0 0 0 3 0 V16.6"/><path d="M21.5 9 a4 4 0 0 1 0 6"/>`,
  'megaphone-link':  `<path d="M3 11 a1 1 0 0 1 1 -1 H7 L15 6 V18 L7 14 H4 a1 1 0 0 1 -1 -1 Z"/><path d="M7 10.5 V14"/><path d="M18 8.5 a5 5 0 0 1 0 7 M20.5 6 a8.5 8.5 0 0 1 0 12"/>`,
  'bell':            `<path d="M5 17 V11 a7 7 0 0 1 14 0 v6 L21 19 H3 Z"/><path d="M9 19.5 a3 3 0 0 0 6 0"/>`,
  'share':           `<circle cx="6" cy="12" r="2.5"/><circle cx="18" cy="6" r="2.5"/><circle cx="18" cy="18" r="2.5"/><path d="M8 11 L16 7 M8 13 L16 17"/>`,
  'link':            `<path d="M9.5 14.5 L14.5 9.5"/><path d="M11 7.5 L13 5.5 a3.5 3.5 0 0 1 5 5 L16 12.5"/><path d="M13 16.5 L11 18.5 a3.5 3.5 0 0 1 -5 -5 L8 11.5"/>`,
  'email':           `<rect x="3" y="6" width="18" height="13" rx="1.5"/><path d="M3 8 L12 14 L21 8"/>`,

  // ===== Architecture / building =====
  'house':         `<path d="M4 10.5 L12 4 L20 10.5"/><path d="M6 9 V20 H18 V9"/><path d="M10 20 V14 H14 V20"/>`,
  'house-multi':   `<path d="M2 21 V11 L7 7 L12 11 V21 Z"/><path d="M5 21 V16 H9 V21"/><path d="M12 21 V5 H21 V21 Z"/><path d="M15 9 H18 M15 12 H18 M15 15 H18"/>`,
  'building-tall': `<path d="M6 3 H14 V21 H6 Z"/><path d="M14 8 H20 V21 H14"/><path d="M8 6 H10 M8 9 H10 M8 12 H10 M8 15 H10 M8 18 H10 M16 11 H18 M16 14 H18 M16 17 H18"/>`,
  'building-dollar': `<path d="M5 7 H13 V21 H5 Z M8 10 H10 M8 13 H10 M8 16 H10"/><circle cx="17" cy="14" r="4"/><path d="M17 11.5 V16.5 M15.5 12.5 H17.5 a1 1 0 0 1 0 2 H16.5 a1 1 0 0 0 0 2 H18.5"/>`,
  'crane':         `<path d="M6 21 V4 M4 21 H8"/><path d="M6 4 H19.5"/><path d="M6 7.5 L17.5 4"/><path d="M3.5 4 H6 V6.5"/><path d="M17.5 4 V8 M16 8 H19 L17.5 10.5 Z"/>`,
  'm2':            `<path d="M6 4.5 V20 H21"/><path d="M6 4.5 L4.3 6.5 M6 4.5 L7.7 6.5"/><path d="M21 20 L19 18.3 M21 20 L19 21.7"/><text x="8.5" y="17.5" font-family="DM Sans, sans-serif" font-size="7" font-weight="700" stroke="none" fill="currentColor">m²</text>`,
  'floorplan':     `<path d="M4 5 H20 V19 H4 Z"/><path d="M4 12 H9 M13 12 H20 M13 5 V12 M9 12 V19"/><path d="M9 12 a3.4 3.4 0 0 1 -3.4 3.4"/><path d="M16 5 V9" stroke-dasharray="1.6 1.6"/>`,
  'blueprint':     `<rect x="3" y="5" width="14" height="14" rx="1"/><path d="M6 5 V19 M6 9 H10 V5 M10 12 H14 M14 19 V14 H10"/><path d="M17 7 a2.5 2.5 0 0 1 0 10 V7 Z"/><path d="M19.5 7 V17"/>`,
  'axes-3d':       `<path d="M5 19 V5 M5 5 L3.4 7 M5 5 L6.6 7"/><path d="M5 19 H19 M19 19 L17 17.4 M19 19 L17 20.6"/><path d="M5 19 L11.5 12.5 M11.5 12.5 L9.3 12.7 M11.5 12.5 L11.3 14.7"/>`,
  'floor-pattern': `<rect x="4" y="4" width="16" height="16" rx="1"/><path d="M9.33 4 V20 M14.67 4 V20 M4 9.33 H20 M4 14.67 H20"/>`,
  'vr-headset':    `<path d="M3 9 a2 2 0 0 1 2 -2 H19 a2 2 0 0 1 2 2 V14 a2 2 0 0 1 -2 2 H15 L13 13.7 a2 2 0 0 0 -2 0 L9 16 H5 a2 2 0 0 1 -2 -2 Z"/><circle cx="8" cy="11.4" r="1.6"/><circle cx="16" cy="11.4" r="1.6"/>`,
  'drone':         `<circle cx="5.5" cy="5.5" r="2.5"/><circle cx="18.5" cy="5.5" r="2.5"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/><path d="M7.3 7.3 L10 10 M16.7 7.3 L14 10 M7.3 16.7 L10 14 M16.7 16.7 L14 14"/><rect x="9.5" y="9.5" width="5" height="5" rx="1.3"/><circle cx="12" cy="12" r="1"/>`,
  '3d-cube':       `<path d="M12 3 L20 7.5 V16.5 L12 21 L4 16.5 V7.5 Z"/><path d="M4 7.5 L12 12 L20 7.5 M12 12 V21"/>`,

  // ===== Browser / dashboard surfaces =====
  'browser':         `<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 8 H21"/><circle cx="6" cy="6" r="0.7" fill="currentColor" stroke="none"/><circle cx="8.5" cy="6" r="0.7" fill="currentColor" stroke="none"/><circle cx="11" cy="6" r="0.7" fill="currentColor" stroke="none"/>`,
  'browser-house':   `<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 8 H21"/><circle cx="6" cy="6" r="0.6" fill="currentColor" stroke="none"/><circle cx="8" cy="6" r="0.6" fill="currentColor" stroke="none"/><circle cx="10" cy="6" r="0.6" fill="currentColor" stroke="none"/><path d="M6.5 14 L12 10 L17.5 14"/><path d="M8.5 13 V17.5 H15.5 V13"/><path d="M11 17.5 V14.5 H13 V17.5"/>`,
  'browser-info':    `<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 8 H21"/><circle cx="6" cy="6" r="0.6" fill="currentColor" stroke="none"/><circle cx="8" cy="6" r="0.6" fill="currentColor" stroke="none"/><circle cx="10" cy="6" r="0.6" fill="currentColor" stroke="none"/><circle cx="12" cy="14" r="3.6"/><path d="M12 13.5 V16"/><circle cx="12" cy="11.9" r="0.6" fill="currentColor" stroke="none"/>`,
  'browser-chart':   `<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 8 H21"/><circle cx="6" cy="6" r="0.6" fill="currentColor" stroke="none"/><circle cx="8" cy="6" r="0.6" fill="currentColor" stroke="none"/><circle cx="10" cy="6" r="0.6" fill="currentColor" stroke="none"/><path d="M6 17.5 V14.5 M9.5 17.5 V11.5 M13 17.5 V13 M16.5 17.5 V10.5"/><path d="M6 17.7 H17"/>`,
  'browser-pen':     `<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 8 H21"/><circle cx="6" cy="6" r="0.6" fill="currentColor" stroke="none"/><circle cx="8" cy="6" r="0.6" fill="currentColor" stroke="none"/><circle cx="10" cy="6" r="0.6" fill="currentColor" stroke="none"/><path d="M8 18 L8 15.5 L15 8.5 L17.5 11 L10.5 18 Z"/><path d="M13.5 10 L16 12.5"/>`,
  'monitor-house':   `<rect x="3" y="4" width="18" height="13" rx="1.5"/><path d="M9 20 H15 M12 17 V20"/><path d="M7 12 L12 7.5 L17 12"/><path d="M9 11 V14.5 H15 V11"/><path d="M11.3 14.5 V12 H12.7 V14.5"/>`,
  'devices':         `<rect x="2" y="4" width="14" height="10" rx="1.5"/><path d="M6 17 H11 M8.5 14 V17"/><rect x="16.5" y="9" width="5.5" height="11" rx="1.5"/><path d="M18.7 17.5 H19.8"/>`,
  'dashboard':       `<path d="M4 13 a8 8 0 0 1 16 0 V14 H4 Z"/><path d="M12 13 L15.5 9.5"/><circle cx="12" cy="13" r="1.1" fill="currentColor" stroke="none"/><path d="M6 13 V12.3 M8 9.5 L8.5 10.1 M16 9.5 L15.5 10.1 M18 13 V12.3"/><path d="M4 18 H20"/>`,
  'video-player':    `<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M10.5 9.2 L15 12 L10.5 14.8 Z" fill="currentColor" stroke="none"/>`,
  'image':           `<rect x="3" y="4" width="18" height="16" rx="1.5"/><circle cx="8" cy="10" r="1.5"/><path d="M3 16 L9 11 L14 16 L17 14 L21 18"/>`,
  'image-stack':     `<rect x="7" y="7" width="14" height="13" rx="1.5"/><circle cx="11.5" cy="12" r="1.5"/><path d="M7 17.5 L11.5 13.5 L15 16.5 L17.5 14.5 L21 17.5"/><path d="M4 5 H17 M4 5 V18 H7" fill="var(--cv-icon-bg)"/>`,

  // ===== Actions =====
  'plus':    `<path d="M12 5 V19 M5 12 H19"/>`,
  'minus':   `<path d="M5 12 H19"/>`,
  'check':   `<path d="M5 12.5 L10 17 L19 7"/>`,
  'close':   `<path d="M6 6 L18 18 M18 6 L6 18"/>`,
  'sidebar-close': `<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M9 4 V20"/><path d="M16 9 L13 12 L16 15"/>`,
  'edit':    `<path d="M4 16 L13.5 6.5 L17.5 10.5 L8 20 H4 Z"/><path d="M12 8 L16 12"/><path d="M5 19 L8 20"/>`,
  'eye':     `<path d="M2 12 a14 14 0 0 1 20 0 a14 14 0 0 1 -20 0 Z"/><circle cx="12" cy="12" r="3"/>`,
  'eye-off': `<path d="M4 4 L20 20"/><path d="M9.5 5.4 a14 14 0 0 1 2.5 -0.2 c5 0 9 3.5 10 6.8 a13 13 0 0 1 -2.4 3.6"/><path d="M6.4 7.2 a13 13 0 0 0 -4.4 4.8 c1 3.3 5 6.8 10 6.8 a11 11 0 0 0 4.2 -0.8"/><path d="M9.9 9.9 a3 3 0 0 0 4.2 4.2 M14.5 12 a2.5 2.5 0 0 0 -2.5 -2.5"/>`,
  'search':  `<circle cx="11" cy="11" r="6"/><path d="M16 16 L21 21"/>`,
  'filter':  `<path d="M4 5 H20 L14 13 V19 L10 21 V13 Z"/>`,
  'sort':    `<path d="M7 5 V19 M4 8 L7 5 L10 8 M17 19 V5 M14 16 L17 19 L20 16"/>`,
  'swap':    `<path d="M5 9 H19 M16 6 L19 9 L16 12"/><path d="M19 15 H5 M8 12 L5 15 L8 18"/>`,
  'refresh': `<path d="M4 12 a8 8 0 0 1 14 -5 M18 4 V8 H14"/><path d="M20 12 a8 8 0 0 1 -14 5 M6 20 V16 H10"/>`,
  'undo':    `<path d="M9 7 L4 11.5 L9 16"/><path d="M4 11.5 H14 a5.5 5.5 0 0 1 0 11 H10.5"/>`,
  'redo':    `<path d="M15 7 L20 11.5 L15 16"/><path d="M20 11.5 H10 a5.5 5.5 0 0 0 0 11 H13.5"/>`,
  'duplicate':`<rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8 V6 a2 2 0 0 0 -2 -2 H6 a2 2 0 0 0 -2 2 V14 a2 2 0 0 0 2 2 H8"/>`,
  'archive': `<rect x="3" y="4" width="18" height="4" rx="1"/><path d="M5 8 V18.5 a1.5 1.5 0 0 0 1.5 1.5 H17.5 a1.5 1.5 0 0 0 1.5 -1.5 V8"/><path d="M9.5 12 H14.5"/>`,
  'trash':   `<path d="M4 7 H20"/><path d="M9 7 V5 a1 1 0 0 1 1 -1 H14 a1 1 0 0 1 1 1 V7"/><path d="M6 7 L7 19.5 a1.5 1.5 0 0 0 1.5 1.5 H15.5 a1.5 1.5 0 0 0 1.5 -1.5 L18 7"/><path d="M10 11 V17 M14 11 V17"/>`,
  'ruler':   `<rect x="2.5" y="8.5" width="19" height="7" rx="1"/><path d="M6 8.5 V12 M9.5 8.5 V11 M13 8.5 V12 M16.5 8.5 V11"/>`,

  // ===== System / status =====
  'gear':         `<path d="M10.3 2.5 H13.7 L14.2 5 a7 7 0 0 1 1.9 .8 L18.3 4.5 L20.7 6.9 L19.2 9.1 a7 7 0 0 1 .8 1.9 L22.5 11.5 V14.9 L20 15.4 a7 7 0 0 1 -.8 1.9 L20.7 19.5 L18.3 21.9 L16.1 20.4 a7 7 0 0 1 -1.9 .8 L13.7 23.5 H10.3 L9.8 21 a7 7 0 0 1 -1.9 -.8 L5.7 21.9 L3.3 19.5 L4.8 17.3 a7 7 0 0 1 -.8 -1.9 L1.5 14.9 V11.5 L4 11 a7 7 0 0 1 .8 -1.9 L3.3 6.9 L5.7 4.5 L7.9 6 a7 7 0 0 1 1.9 -.8 Z"/><circle cx="12" cy="13.2" r="3"/>`,
  'cloud-upload': `<path d="M7 17 H17 a4 4 0 0 0 1 -8 a6 6 0 0 0 -12 0 a4 4 0 0 0 1 8 Z"/><path d="M12 14 V8 M9 11 L12 8 L15 11"/>`,
  'cloud-download':`<path d="M7 17 H17 a4 4 0 0 0 1 -8 a6 6 0 0 0 -12 0 a4 4 0 0 0 1 8 Z"/><path d="M12 8 V14 M9 11 L12 14 L15 11"/>`,
  'cloud':        `<path d="M7 18 H17 a4 4 0 0 0 1 -8 a6 6 0 0 0 -12 0 a4 4 0 0 0 1 8 Z"/>`,
  'database':     `<path d="M7 3 H17 L21 7 V17 L17 21 H7 L3 17 V7 Z"/><path d="M3 10.5 L12 12.5 L21 10.5 M3 14.5 L12 16.5 L21 14.5"/>`,
  'dollar-circle':`<circle cx="12" cy="12" r="9"/><path d="M14 8.5 H10.5 a1.5 1.5 0 0 0 0 3 H13.5 a1.5 1.5 0 0 1 0 3 H10"/><path d="M12 7 V8.5 M12 15.5 V17"/>`,
  'info-circle':  `<circle cx="12" cy="12" r="9"/><path d="M12 11 V16.5"/><circle cx="12" cy="8" r="0.8" fill="currentColor" stroke="none"/>`,
  'lightbulb':    `<path d="M9 17 H15 V19 a2 2 0 0 1 -6 0 Z"/><path d="M8 14 a5 5 0 1 1 8 0 a4 4 0 0 0 -1.5 3 H9.5 a4 4 0 0 0 -1.5 -3 Z"/>`,
  'location-pin': `<path d="M12 21 C7 15 5 12 5 9 a7 7 0 0 1 14 0 c0 3 -2 6 -7 12 Z"/><circle cx="12" cy="9" r="2.5"/>`,
  'pin-route':    `<path d="M6 3 a4 4 0 0 1 4 4 c0 2.8 -4 6 -4 6 s-4 -3.2 -4 -6 a4 4 0 0 1 4 -4 Z"/><circle cx="6" cy="7" r="1.4"/><circle cx="19" cy="19" r="2"/><path d="M6 15 V16.5 a3 3 0 0 0 3 3 H15.5" stroke-dasharray="0.4 2.4"/>`,
  'calendar':     `<rect x="3" y="6" width="18" height="15" rx="1.5"/><path d="M3 11 H21 M8 3 V8 M16 3 V8"/><circle cx="8" cy="15" r="0.8" fill="currentColor" stroke="none"/><circle cx="12" cy="15" r="0.8" fill="currentColor" stroke="none"/><circle cx="16" cy="15" r="0.8" fill="currentColor" stroke="none"/>`,
  'color-swatches':`<path d="M12 3 C6.5 3 2.5 6.8 2.5 11.3 C2.5 14.8 5 17.4 8 17.4 a1.8 1.8 0 0 0 1.7 -2.4 a1.7 1.7 0 0 1 1.6 -2.3 H15 C18.6 12.7 21.5 10.4 21.5 7.6 C21.5 4.7 17.2 3 12 3 Z"/><circle cx="7.5" cy="9" r="1" fill="currentColor" stroke="none"/><circle cx="12" cy="6.8" r="1" fill="currentColor" stroke="none"/><circle cx="16.5" cy="9" r="1" fill="currentColor" stroke="none"/>`,
  'sun-moon':     `<circle cx="8" cy="12" r="3.3"/><path d="M8 5.5 V7 M8 17 V18.5 M1.5 12 H3 M3.2 7.2 L4.3 8.3 M3.2 16.8 L4.3 15.7"/><path d="M21 13 a5.2 5.2 0 1 1 -5.7 -5.2 a4 4 0 0 0 5.7 5.2 Z"/>`,
  'adjustments':  `<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M7 8 H17 M7 12 H17 M7 16 H17"/><circle cx="10" cy="8" r="1.4" fill="white" stroke-width="1.5"/><circle cx="14" cy="12" r="1.4" fill="white" stroke-width="1.5"/><circle cx="9" cy="16" r="1.4" fill="white" stroke-width="1.5"/>`,

  // ===== Logic / flow =====
  'network':         `<circle cx="12" cy="12" r="2.3"/><circle cx="12" cy="4" r="2"/><circle cx="5" cy="19" r="2"/><circle cx="19" cy="19" r="2"/><path d="M12 6 V9.7 M10.2 13.3 L6.2 17.2 M13.8 13.3 L17.8 17.2"/>`,
  'decision-tree':   `<rect x="9" y="3" width="6" height="4" rx="0.5"/><rect x="3" y="14" width="6" height="4" rx="0.5"/><rect x="15" y="14" width="6" height="4" rx="0.5"/><path d="M12 7 V11 H6 V14 M12 11 H18 V14"/>`,
  'hierarchy':       `<rect x="9.5" y="3" width="5" height="3.6" rx="0.6"/><rect x="2.5" y="16.5" width="5" height="3.6" rx="0.6"/><rect x="9.5" y="16.5" width="5" height="3.6" rx="0.6"/><rect x="16.5" y="16.5" width="5" height="3.6" rx="0.6"/><path d="M12 6.6 V11 M5 16.5 V13 H19 V16.5 M12 11 V16.5"/>`,
  'atom':            `<circle cx="12" cy="12" r="1.8"/><ellipse cx="12" cy="12" rx="9.5" ry="3.6"/><ellipse cx="12" cy="12" rx="9.5" ry="3.6" transform="rotate(60 12 12)"/><ellipse cx="12" cy="12" rx="9.5" ry="3.6" transform="rotate(120 12 12)"/>`,
  'globe':           `<circle cx="12" cy="12" r="9"/><path d="M3 12 H21"/><path d="M12 3 a13 13 0 0 1 0 18 a13 13 0 0 1 0 -18 Z"/><path d="M4.5 7.5 Q 12 10 19.5 7.5 M4.5 16.5 Q 12 14 19.5 16.5"/>`,
  'pie-chart':       `<circle cx="12" cy="12" r="9"/><path d="M12 3 V12 L18.4 18.4"/>`,
  'path-flow':       `<rect x="3" y="4" width="5" height="5" rx="1"/><rect x="16" y="15" width="5" height="5" rx="1"/><path d="M8 6.5 H13 a3 3 0 0 1 3 3 V15"/><path d="M13.5 13 L16 15.5 L18.5 13"/>`,
  'check-square':    `<rect x="4" y="4" width="16" height="16" rx="2"/><path d="M8 12 L11 15 L17 9"/>`,
  'check-square-fill': `<rect x="4" y="4" width="16" height="16" rx="2" fill="currentColor"/><path d="M8 12 L11 15 L17 9" stroke="#FBF7EC"/>`,
  'no-symbol':       `<circle cx="12" cy="12" r="9"/><path d="M6 6 L18 18"/>`,

  // ===== Platform-specific =====
  'play':         `<polygon points="8,5 19,12 8,19" fill="currentColor" stroke-linejoin="round"/>`,
  'pause':        `<rect x="7" y="5" width="3.5" height="14" rx="0.5" fill="currentColor" stroke-linejoin="round"/><rect x="13.5" y="5" width="3.5" height="14" rx="0.5" fill="currentColor" stroke-linejoin="round"/>`,
  'lock':         `<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11 V7 a4 4 0 0 1 8 0 V11"/>`,
  'unlock':       `<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11 V7 a4 4 0 0 1 8 0"/>`,
  'star':         `<polygon points="12,3 14.5,9 21,9.5 16,14 17.5,21 12,17.5 6.5,21 8,14 3,9.5 9.5,9" stroke-linejoin="round"/>`,
  'tag':          `<path d="M3 4 H11 L21 14 L14 21 L4 11 V4 Z"/><circle cx="8" cy="8" r="1.5"/>`,
  'workstation':  `<rect x="3" y="4" width="18" height="13" rx="1.5"/><path d="M3 13 H21 M9 20 H15 M12 17 V20"/><circle cx="12" cy="9" r="2"/>`,
  'connector':    `<path d="M9 6 V4 M15 6 V4"/><rect x="7" y="6" width="10" height="5" rx="1"/><path d="M8.5 11 V13 a3.5 3.5 0 0 0 3.5 3.5 a3.5 3.5 0 0 1 3.5 3.5 V21"/>`,
  'shop-cart':    `<path d="M3 5 H6 L8 17 H18 L20 9 H8.5"/><circle cx="9" cy="20" r="1.5"/><circle cx="17" cy="20" r="1.5"/>`,

  // =====================================================================
  // ConceptV BRAND FEATURE SET
  // Vectorised from the gold/bronze source sheets. These are the named,
  // product-facing glyphs (Guided Tour, Change Style, Day/Night, etc.).
  // Drawn a touch bolder + rounder to read at display size, matching the
  // source. Tagged in CV_ICONS.brand below.
  // =====================================================================
  'guided-tour':   `<rect x="3" y="5" width="18" height="11" rx="2"/><path d="M10.3 8.4 L14.6 10.5 L10.3 12.6 Z" fill="currentColor" stroke="none"/><path d="M4 19.5 H20"/><circle cx="9" cy="19.5" r="1.4" fill="currentColor" stroke="none"/>`,
  'change-style':  `<rect x="3" y="4.5" width="11" height="4.5" rx="1.5"/><path d="M14 6.75 H17.5 a1.3 1.3 0 0 1 1.3 1.3 V10 a1.3 1.3 0 0 1 -1.3 1.3 H11 a1.3 1.3 0 0 0 -1.3 1.3 V20.5"/>`,
  'finishes':      `<rect x="3.5" y="4.5" width="4.6" height="15" rx="1"/><circle cx="5.8" cy="17" r="0.7" fill="currentColor" stroke="none"/><g transform="rotate(20 13 12)"><rect x="10.5" y="4.5" width="4.6" height="15" rx="1"/><circle cx="12.8" cy="17" r="0.7" fill="currentColor" stroke="none"/></g><path d="M18.5 9 L21 11.5 a1 1 0 0 1 0 1.4 L15 19 a1 1 0 0 1 -1.4 0"/>`,
  'drone-view':    `<ellipse cx="6.5" cy="5" rx="2.3" ry="1"/><ellipse cx="17.5" cy="5" rx="2.3" ry="1"/><path d="M6.5 5 H17.5"/><rect x="10.4" y="4" width="3.2" height="2.6" rx="0.7"/><path d="M11.2 7.6 L7 13.5 M12.8 7.6 L17 13.5" stroke-dasharray="1.6 1.6"/><path d="M8.5 20 V16 L12 13.2 L15.5 16 V20 Z"/>`,
  'day-night':     `<circle cx="8" cy="11" r="3.3"/><path d="M8 4.2 V5.7 M8 16.3 V17.8 M1.2 11 H2.7 M3.1 6.1 L4.2 7.2 M3.1 15.9 L4.2 14.8"/><path d="M21 12 a4.6 4.6 0 1 1 -5.2 -4.5 a3.5 3.5 0 0 0 5.2 4.5 Z"/><path d="M19 3.4 L19.6 4.8 L21 5.4 L19.6 6 L19 7.4 L18.4 6 L17 5.4 L18.4 4.8 Z" fill="currentColor" stroke="none"/>`,
  'filters':       `<rect x="3" y="4" width="18" height="16" rx="3.5"/><path d="M6 9.5 H18 M6 14.5 H18"/><circle cx="10" cy="9.5" r="2"/><circle cx="14" cy="14.5" r="2"/>`,
  'markup':        `<rect x="3.5" y="3.5" width="13" height="13" rx="2.5"/><path d="M10 20.5 H13.5 L21 13 a1.5 1.5 0 0 0 0 -2.1 L19.6 9.5 a1.5 1.5 0 0 0 -2.1 0 L10 17 Z"/><path d="M16.5 11 L19.5 14"/>`,
  'stages':        `<path d="M4 19 H14.5 a3.5 3.5 0 0 0 0 -7 H7.5 a3.5 3.5 0 0 1 0 -7 H21"/><path d="M18.5 2.5 L21 5 L18.5 7.5"/><circle cx="4" cy="19" r="1.9"/><circle cx="11" cy="12" r="1.9"/><circle cx="13.5" cy="5" r="1.9"/>`,
  'furniture':     `<path d="M5 13 V9 a2 2 0 0 1 2 -2 H17 a2 2 0 0 1 2 2 V13"/><path d="M2 17 V13 a2 2 0 0 1 4 0 V14 H18 V13 a2 2 0 0 1 4 0 V17"/><path d="M2 17 H22 V18.5 H2 Z"/><path d="M5 18.5 V20.5 M19 18.5 V20.5"/>`,
  'lighting':      `<path d="M9.5 18 H14.5 V19.5 a2 2 0 0 1 -5 0 Z"/><path d="M8 15 a5.5 5.5 0 1 1 8 0 a4 4 0 0 0 -1.5 3 H9.5 a4 4 0 0 0 -1.5 -3 Z"/><path d="M12 2.5 V4 M4.5 6 L5.6 7.1 M19.5 6 L18.4 7.1 M3 13 H4.5 M19.5 13 H21"/>`,
  'convenient':    `<circle cx="12" cy="6.5" r="3.5"/><path d="M12 4.5 V6.5 L13.6 7.5"/><path d="M8.5 2.2 L9 3.4 M12 1.7 V2.9 M15.5 2.2 L15 3.4"/><path d="M4 14 a1 1 0 0 1 2 0 M6 12.8 a1 1 0 0 1 2 0 M8 12.5 a1 1 0 0 1 2 0 M10 12.8 a1 1 0 0 1 2 0"/><path d="M4 14 V16.5 a4 4 0 0 0 4 4 H9.5 a2.5 2.5 0 0 0 2.5 -2.5 V13"/>`,
  'easy':          `<circle cx="12" cy="12" r="9"/><path d="M10 12 L11.8 8.2 a1.1 1.1 0 0 1 2 1 L13.1 11.3 H16 a1 1 0 0 1 1 1.2 L16.4 16 a1.2 1.2 0 0 1 -1.2 1 H10 Z"/><rect x="7.4" y="12" width="2.6" height="5" rx="0.6"/>`,
  'unique':        `<path d="M5 11 a7 7 0 0 1 13.5 -2.5"/><path d="M8 12 a4 4 0 0 1 8 0 V15"/><path d="M12 12 V17 a2 2 0 0 0 2 2"/><path d="M9 16 V18 a4 4 0 0 0 1 2.5"/><path d="M6 14 a6 6 0 0 0 1 8"/><path d="M19 13 a7 7 0 0 1 -1 5"/>`,
  'web':           `<rect x="2.5" y="4" width="12" height="9" rx="1.3"/><path d="M5.5 16 H11.5 M8.5 13 V16"/><rect x="16" y="8" width="5.5" height="12" rx="1"/><path d="M17.8 18 H19.7"/>`,
  'gyro':          `<circle cx="12" cy="12" r="9"/><ellipse cx="12" cy="12" rx="3.6" ry="9" transform="rotate(25 12 12)"/><ellipse cx="12" cy="12" rx="9" ry="3.6" transform="rotate(25 12 12)"/><circle cx="12" cy="12" r="1.7"/>`,
  'thumbs-up':     `<path d="M7 11 L10 4.5 a1.6 1.6 0 0 1 2.8 1.4 L12 10 H16.5 a1.3 1.3 0 0 1 1.3 1.5 L17 17 a1.6 1.6 0 0 1 -1.6 1.3 H7 Z"/><rect x="3.5" y="11" width="3.5" height="8" rx="0.8"/>`,
  'ownership':     `<circle cx="8.5" cy="9.5" r="3.6"/><circle cx="8.5" cy="9.5" r="1.1"/><path d="M11 12 L18.5 19.5"/><path d="M15.5 16.5 L17.5 14.5 M17.5 18.5 L19.5 16.5"/>`,
  'comments':      `<path d="M3 5 a1.5 1.5 0 0 1 1.5 -1.5 H13 a1.5 1.5 0 0 1 1.5 1.5 V10 a1.5 1.5 0 0 1 -1.5 1.5 H7.5 L4.5 14 V11.5 A1.5 1.5 0 0 1 3 10 Z"/><path d="M10 13.5 V15.5 a1.5 1.5 0 0 0 1.5 1.5 H17 L20 19.5 V17 a1.5 1.5 0 0 0 1.5 -1.5 V11 a1.5 1.5 0 0 0 -1.5 -1.5 H16.5"/><path d="M6 7 H11 M6 9 H9"/>`,

  // ===== Additional master line glyphs (from the image NN reference set) =====
  'people-network':    `<circle cx="12" cy="11" r="1.5"/><path d="M9.8 15 a2.4 2.4 0 0 1 4.4 0"/><circle cx="5" cy="5" r="1.4"/><path d="M3 8.3 a2.2 2.2 0 0 1 4 0"/><circle cx="19" cy="5" r="1.4"/><path d="M17 8.3 a2.2 2.2 0 0 1 4 0"/><path d="M7 7 L10.3 9.8 M17 7 L13.7 9.8"/>`,
  'world-network':     `<circle cx="12" cy="12" r="9"/><path d="M3 12 H21"/><path d="M12 3 a13 13 0 0 1 0 18 a13 13 0 0 1 0 -18 Z"/><path d="M4.5 7.5 Q 12 10 19.5 7.5 M4.5 16.5 Q 12 14 19.5 16.5"/><circle cx="12" cy="3" r="1.3" fill="var(--cv-icon-bg)"/><circle cx="4.5" cy="16.5" r="1.3" fill="var(--cv-icon-bg)"/><circle cx="19.5" cy="7.5" r="1.3" fill="var(--cv-icon-bg)"/>`,
  'checklist-double':  `<rect x="7" y="3" width="14" height="14" rx="2"/><rect x="3" y="7" width="14" height="14" rx="2" fill="var(--cv-icon-bg)"/><path d="M6.5 14 L9 16.5 L13.5 11"/>`,
  'comments-fill':     `<path d="M3 5 a1.5 1.5 0 0 1 1.5 -1.5 H13 a1.5 1.5 0 0 1 1.5 1.5 V10 a1.5 1.5 0 0 1 -1.5 1.5 H7.5 L4.5 14 V11.5 A1.5 1.5 0 0 1 3 10 Z" fill="currentColor" stroke="none"/><path d="M10 13.5 V15.5 a1.5 1.5 0 0 0 1.5 1.5 H17 L20 19.5 V17 a1.5 1.5 0 0 0 1.5 -1.5 V11 a1.5 1.5 0 0 0 -1.5 -1.5 H14.5" fill="currentColor" stroke="none"/>`,
  'transfer':          `<path d="M8 20 V5 M5 8 L8 5 L11 8"/><path d="M16 4 V19 M13 16 L16 19 L19 16"/>`,
  'tile-stack':        `<rect x="7" y="4" width="13" height="13" rx="1"/><rect x="4" y="7" width="13" height="13" rx="1" fill="var(--cv-icon-bg)"/><path d="M7 13.5 L10.5 10 M10.5 17 L17 10.5 M7 17 L13.5 10.5"/>`,
  'markup-box':        `<rect x="4" y="4" width="16" height="16" rx="2"/><path d="M11 16 L16 11 L18.5 13.5 L13.5 18.5 H11 Z"/><path d="M14.5 12.5 L17 15"/>`,
  'browser-analytics': `<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 8 H21"/><circle cx="6" cy="6" r="0.6" fill="currentColor" stroke="none"/><circle cx="8" cy="6" r="0.6" fill="currentColor" stroke="none"/><circle cx="10" cy="6" r="0.6" fill="currentColor" stroke="none"/><path d="M6 17 V11.5"/><path d="M6 17 H18"/><path d="M9 17 V13.5 M12 17 V11 M15 17 V14"/>`,

  // ── THE LANGUAGE FAMILY (minted 2026-07-03, the language seat) — the vocabulary the
  // one-system argument needs: frames, blocks, laws, the window, the loop's parts. Full
  // citizens: every one carries domain/kind/tags + name/description in facets, a gloss +
  // meaning in CV_MEANING's seed, and enters glyph_meaning on the next corpus re-emit.
  'frame':     `<path d="M4 8 V5.5 A1.5 1.5 0 0 1 5.5 4 H8 M16 4 h2.5 A1.5 1.5 0 0 1 20 5.5 V8 M20 16 v2.5 a1.5 1.5 0 0 1 -1.5 1.5 H16 M8 20 H5.5 A1.5 1.5 0 0 1 4 18.5 V16"/><circle cx="12" cy="12" r="2.2"/>`,
  'block':     `<path d="M12 3 L20 7.5 V16.5 L12 21 L4 16.5 V7.5 Z"/><path d="M4 7.5 L12 12 L20 7.5 M12 12 V21"/>`,
  'equation':  `<path d="M4 9.5 H14 M4 14.5 H14"/><path d="M17 12 H21 M19.2 9.8 L21.4 12 L19.2 14.2"/>`,
  'window':    `<rect x="4" y="5" width="16" height="14" rx="2"/><path d="M4 12 H20 M12 12 V19"/><circle cx="8" cy="8.5" r="1" fill="currentColor" stroke="none"/>`,
  'seed':      `<path d="M12 21 V12"/><path d="M12 12 C12 8.2 9.2 6 5.5 6 C5.5 9.8 8.2 12 12 12 Z"/><path d="M12 12 C12 9.2 14.6 7.2 18.5 7.2 C18.5 10.4 15.9 12 12 12"/><path d="M5 21 H19"/>`,
  'weave':     `<path d="M6 4 V20 M12 4 V20 M18 4 V20"/><path d="M3.5 8.5 H20.5 M3.5 15.5 H20.5" stroke-dasharray="3.4 2.6"/>`,
  'judge':     `<path d="M12 4.5 V19 M8 19 H16 M5 7 H19"/><path d="M7 7 L4.4 12 a2.9 2.9 0 0 0 5.2 0 Z"/><path d="M17 7 L14.4 12 a2.9 2.9 0 0 0 5.2 0 Z"/>`,
  'ring':      `<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="4.4" stroke-dasharray="2.6 2.6"/>`,
  'corpus':    `<path d="M5 4 H15 a2 2 0 0 1 2 2 V20 H7 a2 2 0 0 1 -2 -2 Z"/><path d="M17 8 h2 v10 a2 2 0 0 1 -2 2"/><path d="M8.5 9 h5 M8.5 12.5 h5 M8.5 16 h3"/>`,
  'room':      `<path d="M4 21 H20 M6 21 V10 a6 6 0 0 1 12 0 V21"/><circle cx="14.4" cy="13.5" r="0.9" fill="currentColor" stroke="none"/>`,
  'territory': `<path d="M12 2.8 L20.8 9.2 L17.4 19.6 H6.6 L3.2 9.2 Z"/><path d="M12 11.5 L12 2.8 M12 11.5 L20.8 9.2 M12 11.5 L17.4 19.6 M12 11.5 L6.6 19.6 M12 11.5 L3.2 9.2"/><circle cx="12" cy="11.5" r="1.6"/>`,
  'operator':  `<circle cx="12" cy="12" r="8.6"/><path d="M8.2 10 H15.8 M8.2 14 H15.8"/>`,

  // ===== W4a — the 32 used-but-undrawn (every id below was already referenced
  // by the registries/seeds; the vocabulary outran the drawings — registry/GAPS.md) =====
  'activity':    `<path d="M2.5 12 H7 L9.5 5.5 L14.5 18.5 L17 12 H21.5"/>`,
  'arrow-right': `<path d="M4 12 H20 M14 6 L20 12 L14 18"/>`,
  'bar-chart':   `<path d="M5 20 V10 M12 20 V4 M19 20 V14"/>`,
  'bolt':        `<path d="M13 2.5 L5.5 13.5 H11 L10 21.5 L18.5 10.5 H13 Z"/>`,
  'book':        `<path d="M20 22 H6.5 A2.5 2.5 0 0 1 4 19.5 V4.5 A2.5 2.5 0 0 1 6.5 2 H20 V17 H6.5 A2.5 2.5 0 0 0 4 19.5"/><path d="M20 17 V22"/>`,
  'book-open':   `<path d="M2.5 5 C5 4 8 4.5 12 6.5 C16 4.5 19 4 21.5 5 V18.5 C19 17.5 16 18 12 20 C8 18 5 17.5 2.5 18.5 Z"/><path d="M12 6.5 V20"/>`,
  'box':         `<path d="M12 2.5 L21 7 V17 L12 21.5 L3 17 V7 Z"/><path d="M3 7 L12 11.5 L21 7 M12 11.5 V21.5"/>`,
  'circle-check':`<circle cx="12" cy="12" r="9.5"/><path d="M7.5 12.5 L10.5 15.5 L16.5 8.5"/>`,
  'component':   `<path d="M12 2.5 L15 5.5 L12 8.5 L9 5.5 Z"/><path d="M18.5 9 L21.5 12 L18.5 15 L15.5 12 Z"/><path d="M12 15.5 L15 18.5 L12 21.5 L9 18.5 Z"/><path d="M5.5 9 L8.5 12 L5.5 15 L2.5 12 Z"/>`,
  'crosshair':   `<circle cx="12" cy="12" r="8"/><path d="M12 2 V6 M12 18 V22 M2 12 H6 M18 12 H22"/>`,
  'cursor':      `<path d="M5.5 3.5 L20 12 L13 13.5 L10 20.5 Z"/>`,
  'desktop':     `<rect x="3" y="4" width="18" height="12.5" rx="2"/><path d="M9.5 21 H14.5 M12 16.5 V21"/>`,
  'droplet':     `<path d="M12 3 C15.5 7.5 18.5 11 18.5 14.5 A6.5 6.5 0 0 1 5.5 14.5 C5.5 11 8.5 7.5 12 3 Z"/>`,
  'feather':     `<path d="M19.5 4.5 C16.5 1.5 11.5 2 9 5.5 L4.5 12 V19.5 H12 L18.5 15 C22 12.5 22.5 7.5 19.5 4.5 Z"/><path d="M4.5 19.5 L16 8 M9 15 H14.8"/>`,
  'file-plus':   `<path d="M6 3 H14 L18 7 V21 H6 Z M14 3 V7 H18"/><path d="M12 11 V17 M9 14 H15"/>`,
  'flag':        `<path d="M5.5 21.5 V3.5 C8 2 10.5 2 12.5 3.5 C14.5 5 17 5 19.5 3.5 V13.5 C17 15 14.5 15 12.5 13.5 C10.5 12 8 12 5.5 13.5"/>`,
  'grid':        `<rect x="3.5" y="3.5" width="7" height="7" rx="1"/><rect x="13.5" y="3.5" width="7" height="7" rx="1"/><rect x="3.5" y="13.5" width="7" height="7" rx="1"/><rect x="13.5" y="13.5" width="7" height="7" rx="1"/>`,
  'hash':        `<path d="M9.5 3.5 L7.5 20.5 M16.5 3.5 L14.5 20.5 M4 8.5 H20.5 M3.5 15.5 H20"/>`,
  'hexagon':     `<path d="M12 2.5 L20.2 7.25 V16.75 L12 21.5 L3.8 16.75 V7.25 Z"/>`,
  'layers':      `<path d="M12 2.5 L21.5 7.5 L12 12.5 L2.5 7.5 Z"/><path d="M2.5 12 L12 17 L21.5 12 M2.5 16.5 L12 21.5 L21.5 16.5"/>`,
  'layout':      `<rect x="3" y="3.5" width="18" height="17" rx="2"/><path d="M3 9 H21 M9.5 9 V20.5"/>`,
  'list':        `<path d="M8.5 6 H20.5 M8.5 12 H20.5 M8.5 18 H20.5"/><circle cx="4.5" cy="6" r="0.8" fill="currentColor" stroke="none"/><circle cx="4.5" cy="12" r="0.8" fill="currentColor" stroke="none"/><circle cx="4.5" cy="18" r="0.8" fill="currentColor" stroke="none"/>`,
  'mic':         `<rect x="9" y="2.5" width="6" height="11" rx="3"/><path d="M5 11.5 a7 7 0 0 0 14 0 M12 18.5 V21.5 M8.5 21.5 H15.5"/>`,
  'palette':     `<path d="M12 2.5 a9.5 9.5 0 1 0 0 19 c1.5 0 2.2 -1 1.6 -2.2 c-0.7 -1.4 0.2 -2.8 1.8 -2.8 H18 a3.5 3.5 0 0 0 3.5 -3.5 C21.5 7 17 2.5 12 2.5 Z"/><circle cx="7.5" cy="10" r="1" fill="currentColor" stroke="none"/><circle cx="12" cy="7" r="1" fill="currentColor" stroke="none"/><circle cx="16.5" cy="10" r="1" fill="currentColor" stroke="none"/>`,
  'plus-circle': `<circle cx="12" cy="12" r="9.5"/><path d="M12 8 V16 M8 12 H16"/>`,
  'plus-square': `<rect x="3.5" y="3.5" width="17" height="17" rx="2"/><path d="M12 8 V16 M8 12 H16"/>`,
  'server':      `<rect x="3" y="3.5" width="18" height="7" rx="1.5"/><rect x="3" y="13.5" width="18" height="7" rx="1.5"/><circle cx="7" cy="7" r="0.8" fill="currentColor" stroke="none"/><circle cx="7" cy="17" r="0.8" fill="currentColor" stroke="none"/>`,
  'shuffle':     `<path d="M3 6.5 H7 C9 6.5 10 8 11 10 M3 17.5 H7 C9 17.5 10 16 11 14 M13 10 C14 8 15 6.5 17 6.5 H21 M13 14 C14 16 15 17.5 17 17.5 H21"/><path d="M18 3.5 L21 6.5 L18 9.5 M18 14.5 L21 17.5 L18 20.5"/>`,
  'sparkles':    `<path d="M10 3.5 L11.8 8.7 L17 10.5 L11.8 12.3 L10 17.5 L8.2 12.3 L3 10.5 L8.2 8.7 Z"/><path d="M18 13.5 L18.9 16.1 L21.5 17 L18.9 17.9 L18 20.5 L17.1 17.9 L14.5 17 L17.1 16.1 Z"/><path d="M17.5 3 V7 M15.5 5 H19.5"/>`,
  'square':      `<rect x="4" y="4" width="16" height="16" rx="2"/>`,
  'type':        `<path d="M5 7 V4.5 H19 V7 M12 4.5 V19.5 M9 19.5 H15"/>`,
  'wand':        `<path d="M4 20 L13.5 10.5 M12 9 L15 12"/><path d="M18 2.5 V6.5 M16 4.5 H20 M20.5 9 V12 M19 10.5 H22 M13.5 3 V5.5 M12.25 4.25 H14.75"/>`,
};

// =====================================================================
// ALIASES — semantic ⇄ brand names resolve to the same single body.
// Resolution order is always: data[name] first, then aliases[name].
// (So an alias never shadows a real key.)
// =====================================================================
window.CV_ICONS.aliases = {
  // brand feature names → existing semantic bodies (no duplicate drawing)
  'square-meters': 'm2',
  'area':          'm2',
  'price':         'dollar-circle',
  'settings':      'gear',
  'output':        'cloud-download',
  'update':        'refresh',
  'sync':          'refresh',
  'upload':        'cloud-upload',
  'users':         'people',
  'maps':          'location-pin',
  'info':          'info-circle',
  'easy-setup':    'folder-gear',
  'comment':       'comments',
  'responsive':    'web',
  'tour':          'guided-tour',
  'restyle':       'change-style',
  'paint':         'change-style',
  'samples':       'finishes',
  'partnership':   'handshake',
  'fpv':           'drone-view',
  'flythrough':    'drone-view',
  'daynight':      'day-night',
  'sliders':       'filters',
  'annotate':      'markup',
  'like':          'thumbs-up',
};

// Names that belong to the ConceptV brand feature set (vs the general
// system/UI set). The explorer uses this to split the two groups.
window.CV_ICONS.brand = [
  'guided-tour', 'change-style', 'finishes', 'drone-view', 'drone', 'day-night',
  'filters', 'markup', 'stages', 'furniture', 'lighting', 'convenient', 'easy',
  'unique', 'web', 'gyro', 'thumbs-up', 'ownership', 'comments', 'm2',
  'vr-headset', 'floorplan', 'location-pin', 'dollar-circle', 'info-circle',
  'color-swatches', 'handshake', 'house', 'monitor-house',
];

// =====================================================================
// FACETED TAXONOMY — the single source for what a symbol MEANS.
// Replaces the old ad-hoc section comments + flat `brand` list with a
// real two-facet classification (domain + kind) plus free tags. The
// Glyphic registry (cv-glyphics.js) and the explorer both read this;
// neither keeps its own category list. Add a symbol → add its facets.
// =====================================================================

// The domain facet: the subject area a symbol belongs to. id → {label, desc}.
window.CV_ICONS.taxonomy = {
  domains: {
    people:        { label: 'People',        desc: 'Roles, users, teams, relationships' },
    property:      { label: 'Property',      desc: 'Homes, buildings, plans, area, construction' },
    visualization: { label: 'Visualization', desc: 'The capture / render tech — drone, VR, 3D, blueprint' },
    document:      { label: 'Document',      desc: 'Files, folders, brochures, records' },
    communication: { label: 'Communication', desc: 'Chat, mail, share, notify, broadcast' },
    interface:     { label: 'Interface',     desc: 'Browsers, dashboards, devices, screens' },
    media:         { label: 'Media',         desc: 'Images, video, playback' },
    data:          { label: 'Data',          desc: 'Networks, charts, hierarchy, storage' },
    commerce:      { label: 'Commerce',      desc: 'Price, payment, cart, ownership' },
    place:         { label: 'Place',         desc: 'Location, maps, routes, world' },
    action:        { label: 'Action',        desc: 'Verbs & controls — add, edit, search, filter' },
    system:        { label: 'System',        desc: 'Settings, cloud, security, status, time' },
    feature:       { label: 'Feature',       desc: 'ConceptV product features (named, customer-facing)' },
    language:      { label: 'Language',      desc: 'The generative language itself — frames, blocks, laws, operators, the window, the loop' },
  },
  // The kind facet: what TYPE of thing the symbol denotes.
  kinds: {
    object:  { label: 'Object',  desc: 'A thing / noun' },
    action:  { label: 'Action',  desc: 'A verb / operation' },
    state:   { label: 'State',   desc: 'A status / condition' },
    concept: { label: 'Concept', desc: 'An abstract idea / relationship' },
  },
};

// Per-symbol facets: name → { domain, kind, tags[] }. The one home for
// each symbol's meaning. `brand:true` flags the customer-facing set.
window.CV_ICONS.facets = {
  // people
  'person':{domain:'people',kind:'object',tags:['user','profile','avatar']},
  'people':{domain:'people',kind:'object',tags:['users','group','audience']},
  'person-add':{domain:'people',kind:'action',tags:['invite','signup','add user']},
  'person-clock':{domain:'people',kind:'state',tags:['pending','waiting','schedule']},
  'handshake':{domain:'people',kind:'concept',tags:['partnership','deal','agreement']},
  'team':{domain:'people',kind:'object',tags:['group','staff','collaborators']},
  'user-network':{domain:'people',kind:'concept',tags:['org','connections','referral']},
  'user-card':{domain:'people',kind:'object',tags:['profile','contact','id']},
  'people-network':{domain:'people',kind:'concept',tags:['org','connections','community']},
  // property
  'house':{domain:'property',kind:'object',tags:['home','listing','residence']},
  'house-multi':{domain:'property',kind:'object',tags:['estate','development','units']},
  'building-tall':{domain:'property',kind:'object',tags:['tower','apartment','commercial']},
  'building-dollar':{domain:'property',kind:'concept',tags:['valuation','investment','price']},
  'crane':{domain:'property',kind:'object',tags:['construction','development','build']},
  'm2':{domain:'property',kind:'concept',tags:['area','size','square meters']},
  'floorplan':{domain:'property',kind:'object',tags:['layout','plan','rooms']},
  'floor-pattern':{domain:'property',kind:'object',tags:['tiling','material','floor']},
  'monitor-house':{domain:'property',kind:'object',tags:['listing','virtual tour','preview']},
  // visualization
  'blueprint':{domain:'visualization',kind:'object',tags:['plan','draft','technical']},
  'axes-3d':{domain:'visualization',kind:'concept',tags:['3d','space','coordinates']},
  'vr-headset':{domain:'visualization',kind:'object',tags:['vr','immersive','virtual']},
  'drone':{domain:'visualization',kind:'object',tags:['aerial','uav','quadcopter']},
  '3d-cube':{domain:'visualization',kind:'object',tags:['3d','model','volume']},
  // document
  'file':{domain:'document',kind:'object',tags:['document','page']},
  'files-stack':{domain:'document',kind:'object',tags:['documents','batch']},
  'file-upload':{domain:'document',kind:'action',tags:['upload','import']},
  'file-download':{domain:'document',kind:'action',tags:['download','export']},
  'file-pdf':{domain:'document',kind:'object',tags:['pdf','export']},
  'file-list':{domain:'document',kind:'object',tags:['report','listing']},
  'file-edit':{domain:'document',kind:'action',tags:['edit','revise']},
  'file-gear':{domain:'document',kind:'action',tags:['process','config']},
  'folder':{domain:'document',kind:'object',tags:['directory','collection']},
  'folder-gear':{domain:'document',kind:'action',tags:['manage','config','setup']},
  'brochure':{domain:'document',kind:'object',tags:['marketing','collateral','flyer']},
  'document':{domain:'document',kind:'object',tags:['page','text']},
  'clipboard':{domain:'document',kind:'object',tags:['form','checklist','notes']},
  'checklist-double':{domain:'document',kind:'state',tags:['tasks','done','approved']},
  // communication
  'chat':{domain:'communication',kind:'object',tags:['message','talk']},
  'chat-double':{domain:'communication',kind:'object',tags:['conversation','thread']},
  'chat-tree':{domain:'communication',kind:'concept',tags:['threads','branching']},
  'megaphone':{domain:'communication',kind:'object',tags:['announce','broadcast']},
  'megaphone-link':{domain:'communication',kind:'concept',tags:['campaign','reach']},
  'bell':{domain:'communication',kind:'object',tags:['notify','alert','reminder']},
  'share':{domain:'communication',kind:'action',tags:['send','distribute']},
  'link':{domain:'communication',kind:'action',tags:['url','connect']},
  'email':{domain:'communication',kind:'object',tags:['mail','message']},
  'comments':{domain:'communication',kind:'object',tags:['feedback','discussion']},
  'comments-fill':{domain:'communication',kind:'object',tags:['feedback','active']},
  // interface
  'browser':{domain:'interface',kind:'object',tags:['web','window','page']},
  'browser-house':{domain:'interface',kind:'object',tags:['listing page','portal']},
  'browser-info':{domain:'interface',kind:'object',tags:['details','about']},
  'browser-chart':{domain:'interface',kind:'object',tags:['analytics','report']},
  'browser-pen':{domain:'interface',kind:'object',tags:['edit page','design']},
  'browser-analytics':{domain:'interface',kind:'object',tags:['stats','metrics']},
  'devices':{domain:'interface',kind:'object',tags:['responsive','multi-device']},
  'dashboard':{domain:'interface',kind:'object',tags:['gauge','overview','control']},
  'workstation':{domain:'interface',kind:'object',tags:['desktop','studio']},
  'tile-stack':{domain:'interface',kind:'object',tags:['cards','gallery','grid']},
  // media
  'video-player':{domain:'media',kind:'object',tags:['video','playback']},
  'image':{domain:'media',kind:'object',tags:['photo','picture']},
  'image-stack':{domain:'media',kind:'object',tags:['gallery','photos']},
  'play':{domain:'media',kind:'action',tags:['start','run']},
  'pause':{domain:'media',kind:'action',tags:['hold','stop']},
  // data
  'network':{domain:'data',kind:'concept',tags:['graph','nodes','mesh']},
  'decision-tree':{domain:'data',kind:'concept',tags:['logic','branching','flow']},
  'hierarchy':{domain:'data',kind:'concept',tags:['org','structure','tree']},
  'atom':{domain:'data',kind:'concept',tags:['core','engine','science']},
  'pie-chart':{domain:'data',kind:'object',tags:['stats','share','breakdown']},
  'path-flow':{domain:'data',kind:'concept',tags:['process','pipeline','flow']},
  'database':{domain:'data',kind:'object',tags:['storage','records','db']},
  // commerce
  'dollar-circle':{domain:'commerce',kind:'object',tags:['price','money','cost']},
  'shop-cart':{domain:'commerce',kind:'object',tags:['buy','checkout','order']},
  'ownership':{domain:'commerce',kind:'concept',tags:['title','own','rights']},
  // place
  'location-pin':{domain:'place',kind:'object',tags:['map','location','address']},
  'pin-route':{domain:'place',kind:'concept',tags:['directions','journey','path']},
  'globe':{domain:'place',kind:'object',tags:['world','global','international']},
  'world-network':{domain:'place',kind:'concept',tags:['global','reach','worldwide']},
  // action
  'plus':{domain:'action',kind:'action',tags:['add','create','new']},
  'minus':{domain:'action',kind:'action',tags:['remove','subtract']},
  'check':{domain:'action',kind:'action',tags:['confirm','done','approve']},
  'close':{domain:'action',kind:'action',tags:['cancel','dismiss','x']},
  'sidebar-close':{domain:'action',kind:'action',tags:['collapse','panel']},
  'edit':{domain:'action',kind:'action',tags:['modify','pencil','write']},
  'eye':{domain:'action',kind:'action',tags:['view','show','preview']},
  'eye-off':{domain:'action',kind:'action',tags:['hide','conceal']},
  'search':{domain:'action',kind:'action',tags:['find','lookup','magnify']},
  'filter':{domain:'action',kind:'action',tags:['refine','narrow']},
  'sort':{domain:'action',kind:'action',tags:['order','arrange']},
  'swap':{domain:'action',kind:'action',tags:['exchange','toggle']},
  'refresh':{domain:'action',kind:'action',tags:['reload','sync','update']},
  'transfer':{domain:'action',kind:'action',tags:['move','migrate','exchange']},
  'undo':{domain:'action',kind:'action',tags:['undo','revert','back','history']},
  'redo':{domain:'action',kind:'action',tags:['redo','forward','history']},
  'duplicate':{domain:'action',kind:'action',tags:['copy','clone','duplicate']},
  'archive':{domain:'action',kind:'action',tags:['archive','store','box','stow']},
  'trash':{domain:'action',kind:'action',tags:['delete','remove','bin','discard']},
  'ruler':{domain:'action',kind:'object',tags:['size','measure','scale','dimension']},
  'adjustments':{domain:'action',kind:'object',tags:['controls','settings','sliders']},
  'check-square':{domain:'action',kind:'state',tags:['checkbox','selected']},
  'check-square-fill':{domain:'action',kind:'state',tags:['checked','complete']},
  'no-symbol':{domain:'action',kind:'state',tags:['forbidden','blocked','none']},
  'star':{domain:'action',kind:'state',tags:['favorite','rate','feature']},
  'thumbs-up':{domain:'action',kind:'state',tags:['like','approve','positive']},
  // system
  'gear':{domain:'system',kind:'object',tags:['settings','config','cog']},
  'cloud-upload':{domain:'system',kind:'action',tags:['upload','backup','sync']},
  'cloud-download':{domain:'system',kind:'action',tags:['download','fetch','output']},
  'cloud':{domain:'system',kind:'object',tags:['storage','hosting','sync']},
  'info-circle':{domain:'system',kind:'state',tags:['info','help','detail']},
  'lightbulb':{domain:'system',kind:'concept',tags:['idea','tip','insight']},
  'calendar':{domain:'system',kind:'object',tags:['date','schedule','time']},
  'lock':{domain:'system',kind:'state',tags:['secure','private','locked']},
  'unlock':{domain:'system',kind:'state',tags:['open','access','unlocked']},
  'tag':{domain:'system',kind:'object',tags:['label','category','meta']},
  'connector':{domain:'system',kind:'object',tags:['plug','integration','api']},
  // feature (ConceptV customer-facing)
  'guided-tour':{domain:'feature',kind:'concept',tags:['tour','walkthrough','play'],brand:true},
  'change-style':{domain:'feature',kind:'concept',tags:['restyle','theme','paint'],brand:true},
  'finishes':{domain:'feature',kind:'object',tags:['materials','samples','swatch'],brand:true},
  'drone-view':{domain:'feature',kind:'concept',tags:['fpv','aerial','flythrough'],brand:true},
  'day-night':{domain:'feature',kind:'concept',tags:['lighting','time of day','toggle'],brand:true},
  'filters':{domain:'feature',kind:'object',tags:['refine','options','sliders'],brand:true},
  'markup':{domain:'feature',kind:'action',tags:['annotate','comment','draw'],brand:true},
  'markup-box':{domain:'feature',kind:'action',tags:['annotate','region','note'],brand:true},
  'stages':{domain:'feature',kind:'concept',tags:['process','phases','progress'],brand:true},
  'furniture':{domain:'feature',kind:'object',tags:['staging','interior','sofa'],brand:true},
  'lighting':{domain:'feature',kind:'object',tags:['lamp','illumination','mood'],brand:true},
  'convenient':{domain:'feature',kind:'concept',tags:['easy','quick','time-saving'],brand:true},
  'easy':{domain:'feature',kind:'concept',tags:['simple','effortless'],brand:true},
  'unique':{domain:'feature',kind:'concept',tags:['fingerprint','distinct','custom'],brand:true},
  'web':{domain:'feature',kind:'object',tags:['responsive','browser','online'],brand:true},
  'gyro':{domain:'feature',kind:'concept',tags:['360','orbit','rotate'],brand:true},
  'color-swatches':{domain:'feature',kind:'object',tags:['palette','colours','style'],brand:true},

  // ── THE LANGUAGE FAMILY (2026-07-03) — full facet records: name, description, family, kind, tags.
  'frame':{domain:'language',kind:'concept',name:'Frame',description:'A way of seeing — rules of projection over data that never changes; every viewer is one, and is a node in the space it views.',tags:['view','lens','perspective','coordinate','reader']},
  'block':{domain:'language',kind:'object',name:'Block',description:'The atomic composable unit — typed, addressed, nestable; every boundary the root of its own cascade.',tags:['unit','composable','atom','nest','boundary']},
  'equation':{domain:'language',kind:'concept',name:'Equation',description:'A law that computes — a value derived from relations, never placed by hand.',tags:['law','derive','rule','calculate','invariant']},
  'window':{domain:'language',kind:'object',name:'Window',description:'The visible half of the world — the coordinate space made touchable: see, point, direct.',tags:['see','point','direct','world-map','interface']},
  'seed':{domain:'language',kind:'object',name:'Seed',description:'The start that carries the whole — every telling grows root-first from it, complete at every stage.',tags:['root','start','grow','origin','generation']},
  'weave':{domain:'language',kind:'concept',name:'Weave',description:'Descent and traverse woven — the multiaxial reading; any forward walk through the lattice is a valid telling.',tags:['warp','weft','descend','traverse','lattice','walk']},
  'judge':{domain:'language',kind:'action',name:'Judge',description:'The one that weighs — extraction proposes in parallel, judgment composes the one answer.',tags:['decide','weigh','verify','compose','abstain']},
  'ring':{domain:'language',kind:'concept',name:'Ring',description:'The boundary that carries identity through change — interior change is state, boundary change is becoming.',tags:['boundary','identity','becoming','anchor','continuity']},
  'corpus':{domain:'language',kind:'object',name:'Corpus',description:'The remembered whole — everything spoken, kept addressed; the transcripts are the root of all data.',tags:['memory','store','transcript','vault','provenance']},
  'room':{domain:'language',kind:'object',name:'Room',description:'A place of work — a session, a bench, a gallery; rooms are places and the camera slides between them.',tags:['session','place','workshop','bench','gallery']},
  'territory':{domain:'language',kind:'concept',name:'Territory',description:'A subject around its origin — soft-edged sectors radial about a centre; the cut and the route make a telling of it.',tags:['subject','sector','polygon','origin','map']},
  'operator':{domain:'language',kind:'concept',name:'Operator',description:'A universal sign — a relation whose meaning arrives free because everyone already holds it.',tags:['sign','relation','universal','logic','edge']},
};

// Symbol-level queries (read the facets above — single source).
window.CV_ICONS.byDomain = function (domain) {
  const f = window.CV_ICONS.facets;
  return Object.keys(f).filter(n => f[n].domain === domain);
};
window.CV_ICONS.byKind = function (kind) {
  const f = window.CV_ICONS.facets;
  return Object.keys(f).filter(n => f[n].kind === kind);
};
// Search across name, tags, domain label, and kind.
window.CV_ICONS.search = function (q) {
  q = (q || '').toLowerCase().trim();
  if (!q) return Object.keys(window.CV_ICONS.facets);
  const f = window.CV_ICONS.facets, tax = window.CV_ICONS.taxonomy;
  return Object.keys(f).filter(n => {
    const e = f[n], dom = (tax.domains[e.domain] || {}).label || e.domain;
    return n.includes(q) || e.domain.includes(q) || e.kind.includes(q) ||
           dom.toLowerCase().includes(q) || (e.tags || []).some(t => t.includes(q));
  });
};

// Resolve an icon name (following one alias hop) to its canonical key.
window.CV_ICONS.resolve = function (name) {
  const d = window.CV_ICONS.data;
  if (d[name]) return name;
  const a = window.CV_ICONS.aliases[name];
  return (a && d[a]) ? a : name;
};

// Get an icon body, following aliases. Returns undefined if unknown.
window.CV_ICONS.get = function (name) {
  return window.CV_ICONS.data[window.CV_ICONS.resolve(name)];
};

/**
 * Render an icon as an SVG element (browser-side only).
 * @param {string} name - one of the keys in CV_ICONS.data
 * @param {object} opts - { size, color, strokeWidth, circle }
 * @returns {SVGSVGElement}
 */
window.CV_ICONS.svg = function(name, opts = {}) {
  const { size = 24, color = 'currentColor', strokeWidth = 1.5, circle = false } = opts;
  const body = window.CV_ICONS.get(name);
  if (!body) throw new Error(`Unknown icon "${name}"`);
  const ns = 'http://www.w3.org/2000/svg';
  const svg = document.createElementNS(ns, 'svg');
  svg.setAttribute('viewBox', '0 0 24 24');
  svg.setAttribute('width', size);
  svg.setAttribute('height', size);
  svg.setAttribute('fill', 'none');
  svg.setAttribute('stroke', color);
  svg.setAttribute('stroke-width', strokeWidth);
  svg.setAttribute('stroke-linecap', 'round');
  svg.setAttribute('stroke-linejoin', 'round');
  svg.innerHTML = body;
  return svg;
};

/**
 * Get the full inline SVG markup for an icon as a string.
 */
window.CV_ICONS.markup = function(name, opts = {}) {
  const { size = 24, color = 'currentColor', strokeWidth = 1.5 } = opts;
  const body = window.CV_ICONS.get(name);
  if (!body) throw new Error(`Unknown icon "${name}"`);
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="${size}" height="${size}" fill="none" stroke="${color}" stroke-width="${strokeWidth}" stroke-linecap="round" stroke-linejoin="round">${body}</svg>`;
};

// =====================================================================
// ADD — the write path for the AI glyphic-foundry (and manual authoring).
// A new SYMBOL drops into the SAME single sources every reader uses:
// .data (the body) + .facets (its meaning) — so a Vi-generated symbol is
// first-class and instantly available to the explorer, CV_GLYPHIC and the
// registry. Validates against CV_GLYPHIC.schema when present (loud, never
// silent-coerce). Optionally persists user/vi symbols to localStorage.
// =====================================================================
window.CV_ICONS.STORAGE_KEY = 'cv:icons:user-symbols';

window.CV_ICONS.add = function (rec, opts = {}) {
  opts = opts || {};
  if (window.CV_GLYPHIC && window.CV_GLYPHIC.validateSymbol) {
    const probs = window.CV_GLYPHIC.validateSymbol(rec);
    if (probs.length) throw new Error('CV_ICONS.add: invalid symbol — ' + probs.join('; '));
  } else if (!rec || !rec.id || !rec.svg) {
    throw new Error('CV_ICONS.add: symbol needs at least { id, svg, name }');
  }
  window.CV_ICONS.data[rec.id] = rec.svg;
  const f = (rec.facets || {});
  window.CV_ICONS.facets[rec.id] = {
    domain: f.domain || 'feature',
    kind: f.kind || 'object',
    tags: f.tags || [],
    name: rec.name,
    description: rec.description || '',
    provenance: rec.provenance || 'vi',
  };
  if (opts.persist !== false) window.CV_ICONS._persist();
  return rec.id;
};

window.CV_ICONS._persist = function () {
  try {
    const out = [];
    const f = window.CV_ICONS.facets;
    for (const id in f) {
      if (f[id] && (f[id].provenance === 'vi' || f[id].provenance === 'user')) {
        out.push({ id, svg: window.CV_ICONS.data[id], name: f[id].name, description: f[id].description, facets: f[id], provenance: f[id].provenance });
      }
    }
    localStorage.setItem(window.CV_ICONS.STORAGE_KEY, JSON.stringify(out));
  } catch (e) {}
};

window.CV_ICONS._loadPersisted = function () {
  try {
    const raw = localStorage.getItem(window.CV_ICONS.STORAGE_KEY);
    if (!raw) return;
    JSON.parse(raw).forEach(r => window.CV_ICONS.add(r, { persist: false }));
  } catch (e) {}
};
window.CV_ICONS._loadPersisted();

