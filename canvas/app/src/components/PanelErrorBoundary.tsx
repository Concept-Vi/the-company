// F0 (carved from App.tsx:7–17) · per-panel error boundary — a malformed/throwing panel definition
// renders a CONTAINED card, never white-screening the canvas (the operator's only control surface).
// Recovery is bridge-side. PRESERVE-LIST item 1: used 5× across the carved components.
import { Component } from 'react'

export class PanelErrorBoundary extends Component<{ name: string; children: any }, { err: boolean }> {
  constructor(p: any) { super(p); this.state = { err: false } }
  static getDerivedStateFromError() { return { err: true } }
  render() {
    return this.state.err
      ? <div className="op-panel op-err">⚠ panel “{this.props.name}” failed to render — revert it from the grow panel (↩).</div>
      : this.props.children
  }
}
