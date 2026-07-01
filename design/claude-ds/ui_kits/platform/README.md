# ConceptV Platform — UI Kit

The creator-side dashboard. Used by architects, developers, and sales/marketing agencies to package architectural visualisation projects (Revit → Enscape pipeline) into branded Virtual Hubs.

## Layout

Three fixed zones:

- **Left rail · 280 px** — colour-emoji sidebar nav (Projects, Dashboard Updates, Landing Pages, Files, Gallery, Brand Kit, …) plus collapsible Tools / Integrations / Support sections.
- **Top-right cluster** — notification bell with red count badge + circular avatar. Sits at the top of the content column, *not* across the page.
- **Floating** — bottom-right **Chats** pill (always visible).

The content column shows: screen title (bronze, 36 px) → toolbar row (Select / Filter / Sort / Search / Clear Filters / Create New / Upload) → the surface itself (Gallery grid, Calendar, settings forms, etc.).

## Components

| File | What it is |
| --- | --- |
| `Sidebar.jsx` | Full left rail with emoji nav, collapsing sections, active state |
| `TopBar.jsx` | Bell + avatar cluster |
| `ScreenHeader.jsx` | Bronze screen title + optional toolbar slot |
| `ActionToolbar.jsx` | Select / Filter / Sort / Search / Clear / Create New / Upload row |
| `Button.jsx` | Primary / outline / dashed / ghost / dark variants |
| `Checkbox.jsx` | Gold-fill checkbox with the tick |
| `SectionPanel.jsx` | The soft-gold-tinted grouped-settings container |
| `MediaTile.jsx` | Image / video placeholder tiles |
| `Dropzone.jsx` | Dashed-border empty upload state |
| `TaskChip.jsx` | Calendar task-chip with status dot |
| `Chats.jsx` | Floating bottom-right pill |
| `screens/Gallery.jsx` | Gallery surface |
| `screens/Calendar.jsx` | Calendar surface |
| `screens/BrandKit.jsx` | Customer brand-kit form |
| `screens/HubSettings.jsx` | Virtual Hub settings with the soft-gold panel |

## Demo

`index.html` mounts the full platform with **Gallery** as the default screen. Click any sidebar item to navigate between Gallery, Calendar, Brand Kit, and Virtual Hub Settings.
