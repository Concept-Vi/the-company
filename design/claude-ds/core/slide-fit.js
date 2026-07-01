// core/slide-fit.js
// ------------------------------------------------------------
// THE PAGED-SURFACE FITTER (the surface axis, presentation side).
// `design = f(content, axis)` recomputes a layout for a surface; for the
// PAGED surfaces (slide / print) the artifact is a FIXED-RATIO canvas that must
// be letterboxed into whatever container shows it (per the system rule:
// "fixed-size content implements its own JS scaling"). This is that one
// mechanism — universal, so no template re-implements it (anti-drift).
//
// Contract (consumed by every deck template, e.g. templates/*/<Deck>.dc.html):
//   <div class="cv-slide-frame">           ← locks the surface ratio, clips
//     <div class="cv-slide-stage"> …band… </div>  ← fixed design width, scaled
//   </div>
// The stage holds the slide at its DESIGN width (--cv-stage-w, default 1280);
// the fitter scales the stage so its full natural height fits the frame —
// nothing is ever clipped (the cause of "missing lines"), and short content is
// centered (letterboxed). WEB surface does NOT use this — it reflows.
//
// `.cv-slide-frame`/`.cv-slide-stage` styles live in core/containers.css; this
// file is the behaviour. Loaded by ds-base.js for every consumer.
(function () {
  if (typeof window === "undefined") return;
  var VERSION = 3;
  // version-aware install: a newer build REPLACES an older one (fixes the
  // cache/load race where a stale copy installs first and a fresh copy would
  // otherwise bail at this guard). Only skip if a same-or-newer build won.
  if (window.CV_SLIDE_FIT && (window.CV_SLIDE_FIT.__v | 0) >= VERSION) return;

  function fitOne(frame) {
    var stage = frame.querySelector(":scope > .cv-slide-stage");
    if (!stage) return;
    var fw = frame.clientWidth;
    if (!fw) return;
    var designW = parseFloat(getComputedStyle(frame).getPropertyValue("--cv-stage-w")) || 1280;
    // frame height: an explicit pixel height wins; else derive from its ratio.
    var fh = frame.clientHeight;
    if (!fh) {
      var ar = getComputedStyle(frame).getPropertyValue("aspect-ratio").trim();
      var parts = ar && ar !== "auto" ? ar.split("/") : null;
      fh = parts && parts.length === 2 ? fw * (parseFloat(parts[1]) / parseFloat(parts[0])) : fw * 9 / 16;
    }
    stage.style.width = designW + "px";
    stage.style.transformOrigin = "top left";
    stage.style.transform = "none";
    var h = stage.scrollHeight || (fh);
    var s = Math.min(fw / designW, fh / h);
    stage.style.transform = "scale(" + s + ")";
    var used = h * s;
    stage.style.top = used < fh ? ((fh - used) / 2) + "px" : "0px";
    stage.style.left = "0px";
  }

  function fitAll(root) {
    (root || document).querySelectorAll(".cv-slide-frame").forEach(fitOne);
  }

  var raf = null;
  function schedule() { if (raf) cancelAnimationFrame(raf); raf = requestAnimationFrame(function () { raf = null; fitAll(); }); }

  // observe size + DOM changes so async-mounted slides (<x-import>) settle right
  var ro = (typeof ResizeObserver !== "undefined") ? new ResizeObserver(schedule) : null;
  function observe() {
    if (!ro) return;
    document.querySelectorAll(".cv-slide-frame, .cv-slide-stage").forEach(function (el) { try { ro.observe(el); } catch (e) {} });
  }
  var mo = (typeof MutationObserver !== "undefined") ? new MutationObserver(function () { observe(); schedule(); }) : null;

  // A layout signature: per-frame width + stage natural height. The <x-import>
  // slides mount ASYNC (after the bundle loads) and may live in a tree the body
  // MutationObserver can't see — so we can't rely on events alone. Instead we
  // re-fit on a heartbeat until the signature is STABLE for a while (content has
  // settled), then stop. This guarantees the fit fires after the real mount,
  // whenever that is, without spinning forever.
  function signature() {
    var s = "";
    document.querySelectorAll(".cv-slide-frame").forEach(function (fr) {
      var st = fr.querySelector(":scope > .cv-slide-stage");
      s += (fr.clientWidth | 0) + ":" + (st ? (st.scrollHeight | 0) : 0) + "|";
    });
    return s;
  }
  var beat = null;
  function heartbeat() {
    if (beat) return;                 // already running
    var last = "", stable = 0, n = 0;
    beat = setInterval(function () {
      fitAll();
      var sig = signature();
      if (sig && sig === last && sig.indexOf(":0|") === -1) stable++; else { stable = 0; last = sig; }
      n++;
      if (stable >= 8 || n >= 120) { clearInterval(beat); beat = null; }   // ~2s stable, or 30s cap
    }, 250);
  }
  function kick() { heartbeat(); schedule(); }   // public: restart the settle loop

  function start() {
    observe();
    if (mo) mo.observe(document.body, { childList: true, subtree: true });
    heartbeat();                      // the reliable path
  }
  // install FIRST (so the API — incl. kick — is present immediately and any
  // older copy that runs after us bails at its guard), then start the loop.
  window.CV_SLIDE_FIT = { refit: fitAll, fitOne: fitOne, kick: kick, __v: VERSION };
  window.addEventListener("resize", function () { schedule(); kick(); });
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
  else start();
})();
