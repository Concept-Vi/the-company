# ConceptV Virtual Hub — UI Kit

The buyer-facing side. When a customer of ConceptV publishes a project, end-users land on a **Virtual Hub** — a panotour-style immersive view of the property with a minimal dark overlay UI on top.

## Layout

The viewer is **photo-first**. The architectural render fills the viewport edge-to-edge. All UI sits on dark, slightly-translucent surfaces over the photo.

- **Bottom-centre** — the `MENU` button. Click to reveal the Quick Menu.
- **Bottom-right** of the Quick Menu — `CLOSE` to dismiss.
- **Side panels** — Info Panel and Share Panel anchor to the right at 360 px wide. Floorplan Overlay is full-bleed.
- **Top-left** — the brand bug + Hub switcher (Entry / Apartment A / Apartment B / …).
- **Floating** — comment-capture popup, anchored to whichever point the user clicks.

## Components

| File | What it is |
| --- | --- |
| `HubFrame.jsx` | Full-bleed photo background + child slots |
| `HubBug.jsx` | Top-left wordmark + hub switcher |
| `MenuButton.jsx` | Bottom-centre dark MENU pill |
| `QuickMenu.jsx` | The dark Info / Floorplan / Share / Gyro / CLOSE column |
| `InfoPanel.jsx` | Right-side info card (Title Text · features · description · CTA) |
| `SharePanel.jsx` | Share by link / email / social |
| `FloorplanOverlay.jsx` | Floorplan with hub-position dots |
| `CaptureComment.jsx` | The comment-capture popup with status + message + attachments |

## Demo

`index.html` mounts the full hub experience. Click `MENU` to open the Quick Menu, then any item to swap the right-side panel. Click anywhere on the photo to drop a capture comment.
