import React from 'react'
import ReactDOM from 'react-dom/client'
import 'tldraw/tldraw.css'
// F1: the corpus design-system is the single look-source. Its :root tokens (--bg, --s0..--s3,
// --acc, --await, --fail, --cache, --line, --r, --sp, --shadow, …) load app-wide BEFORE app.css,
// so app.css aliases the legacy var names onto corpus tokens and references corpus vars directly.
import '../../../design/design-system.css'
import './app.css'
import App from './App'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
