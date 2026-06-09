// THE STUDIO — the design-review surface, as a REAL in-app region (supersedes design/mockups/STUDIO.html).
//
// WHAT THIS IS (the keystone, layer ①): the studio's SURFACE SKELETON — three regions composed from the
// named structural primitives (components/StudioKit.tsx): [ Rail │ Stage │ RhmPanel ]. This is the
// Application-Structure Pack made into a real, scoped FE surface that Claude Design DESIGNS INTO: real
// named parts, real integration seams wired to the live backend, empty token-slots, and the laws — the
// STRUCTURE the look plugs into. The deliberate aesthetic (the look) is Claude Design's; this is the socket.
//
// WHY IT REPLACES THE STANDALONE STUDIO (the failure it fixes — intent-studio finding §4): the old
// STUDIO.html was a STANDALONE file with a feedback TEXT BOX mislabelled "right-hand-man" — no model, no
// addresses, a private jsonl store. It REINVENTED primitives the Company already has. This surface COMPOSES
// on them instead: the RhmPanel mounts the REAL <RhmChat/> organ bound to the locus; the Composer posts to
// the SHARED address-keyed annotation store (/api/annotate, read back via /api/annotations) — the bespoke
// /api/mockup-feedback jsonl is RETIRED for this in-app surface (the legacy standalone file may still use it).
//
// THE LAWS (layer ⑤, code-level adherence + the note below):
//   · WHERE THIS GOES: the surface is a region (canvas/app/src/regions/Review.tsx); its named primitives are
//     components (canvas/app/src/components/StudioKit.tsx); its seams are StudioSeams.ts; tokens are
//     --studio-* CSS variables in app.css. (The regions-vs-components split the legibility mine flagged.)
//   · click INDICATES + CONSENTS, never click=execute — selecting a gallery Card INDICATES its reviewed-
//     surface locus (nothing runs); the RHM PROPOSES in chat; an action goes through see-and-approve.
//   · reflects-never-owns — the surface shows backend truth (corpus / annotations / address-help via api+SSE);
//     it never holds authoritative state. The locus is the one indicate() sink.
import { useEffect } from 'react'
import { useApp } from '../AppContext'
import { Rail, Stage, RhmPanel, Composer } from '../components/StudioKit'

function titleFor(corpus: { file: string; title: string }[], file: string | null): string {
  if (!file) return ''
  const hit = corpus.find(c => c.file === file)
  return hit ? hit.title : file
}

export function Review() {
  const { corpus, reviewMockup, reviewAddress, setReviewMockup, refreshCorpus } = useApp()
  // re-bind the corpus on mount (registry-is-truth) and open the first reviewable surface so the Stage is
  // never an empty void — INDICATING its locus (the second arg) so the RhmPanel/Composer bind immediately.
  useEffect(() => {
    void refreshCorpus()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])
  // LOCUS BINDING from the corpus (registry-is-truth). Two cases, both resolved here when the corpus is loaded:
  //   (1) nothing open → open the first reviewable surface (so the Stage is never an empty void).
  //   (2) a mockup IS open but its address was never bound → bind it from the corpus row. This is the deep-link
  //       fix: the ?mockup= effect (App.tsx) opens the mockup EAGERLY on mount — BEFORE the corpus loads — so it
  //       can't pass the address; the mockup showed but the locus stayed null and the Composer was disabled
  //       (a comment couldn't be placed). Now, once the corpus is in, we look up the open mockup's address and
  //       bind it. reflects-never-owns: the address comes FROM the corpus, never invented. We bind ONLY when no
  //       address is set yet (reviewAddress falsy) so a user's element selection / "whole screen" is never
  //       clobbered, and only when the corpus row HAS an address (a genuinely unmapped mockup stays null — honest).
  useEffect(() => {
    if (corpus.length === 0) return
    if (!reviewMockup) {
      const first = corpus[0]
      setReviewMockup(first.file, first.address)
    } else if (!reviewAddress) {
      const row = corpus.find(c => c.file === reviewMockup)
      if (row && row.address) setReviewMockup(reviewMockup, row.address)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [corpus.length, reviewMockup])

  return (
    <div className="studio-shell" data-ui-ref="ui://studio">
      {/* ① RAIL — the gallery (registry-bound corpus of Cards). */}
      <Rail />
      {/* ② STAGE — the device stage (the chosen mockup, sandboxed, phone/desktop). */}
      <Stage titleFor={(f) => titleFor(corpus, f)} />
      {/* ③ RHM-PANEL — the real right-hand-man organ at the locus + AddressHelp + the addressed-feedback Composer. */}
      <RhmPanel>
        <Composer />
      </RhmPanel>
    </div>
  )
}
