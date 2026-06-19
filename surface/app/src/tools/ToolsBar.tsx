import { openTools } from './toolsStore'

// THE TOOL FACE ENTRY — the way into the pilot palette. A small fixed pill at the bottom-LEFT (clear of the V handle
// at bottom-right and the centred decisions bar below the header), so it's reachable on every form factor without
// touching the 3 layout modules. App-root sibling (like the V / source panel). On DNA tokens. Copy is AI-draft,
// marked for Tim's steer. (Placement is scaffold-grade — when the palette becomes the north-star surface it gets
// DNA's real placement; the seam is just openTools().)
export function ToolsBar() {
  return (
    <div className="tools-bar">
      <button className="tools-entry" onClick={openTools} aria-label="Open the tools — pick a tool and run it">
        <span className="tools-entry-glyph" aria-hidden="true">⛭</span>
        <span className="tools-entry-label">Tools</span>
      </button>
    </div>
  )
}
