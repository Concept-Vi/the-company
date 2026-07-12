// The honest empty state (K3: nav items beyond Arrival render the DS's .state-block
// pattern — "not built yet", NEVER a fake surface). Rides tokens/states.css verbatim.
export default function NotBuilt({ what }: { what: string }) {
  return (
    <div className="state-block">
      <div className="glyph" aria-hidden="true">
        ◌
      </div>
      <div className="title">{what} is not built yet</div>
      <div className="body">
        This view lands in a later beat (K3 order: Arrival → Inbox → Chat → Channel → …). Nothing here is
        faked — when it exists, it will be real.
      </div>
    </div>
  )
}
