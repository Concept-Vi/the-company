// app/registry/events.js
// ============================================================================
// CV_EVENTS — the TRIGGERS layer (the ninth single-source registry) + a bus.
//
// Info/Tim: the AI should be able to "select"/highlight things for me — but as a
// RULE / event-trigger, "what they're looking at would automatically highlight",
// rather than the AI intentionally calling a highlight. So: a process (the AI, a
// click, a selection) just EMITS where it is — `emit('ai.focus', {target})` —
// and a declared TRIGGER reacts by invoking an action. Attention → highlight is
// a rule, not an instruction.
//
// A TRIGGER (a Type, same shape as everything):
//   { id, on:'<event>', when?:<CV_COND>, do:'<action id>', args?:{…var-specs}, provenance }
// emit(event, payload, ctx):
//   builds ectx = { event: payload, ...ctx }, finds triggers whose `on` matches
//   and whose `when` passes (CV_COND), and CV_ACTIONS.invoke(do, args, ectx) with
//   args resolved by CV_VARS against ectx. Then notifies subscribers so the UI
//   re-renders. One mechanism: events compose actions + conditions + variables.
//
// Events are open strings; the seeded ones: ai.focus · ai.blur · selection.change
// · hover · action.before · action.after. Anything can emit; anything can trigger.
//
// Load after actions.js / conditions.js / vars.js.
// ============================================================================
(function () {
  'use strict';
  var ACT  = function () { return window.CV_ACTIONS; };
  var COND = function () { return window.CV_COND; };

  var byId = {};
  var order = [];
  var subs = [];                       // [{event, fn}] imperative subscribers (UI)
  var listeners = new Set();           // registry-change listeners

  function normalize(t) {
    if (!t || !t.id) throw new Error('CV_EVENTS: a trigger needs an id');
    if (!t.on) throw new Error('CV_EVENTS: trigger "' + t.id + '" needs an `on` event');
    return {
      id: t.id, on: t.on, when: t.when || null,
      do: t.do || null,                // an action id to invoke
      args: t.args || {},              // value-specs resolved by CV_VARS against ectx
      handler: typeof t.handler === 'function' ? t.handler : null, // escape hatch
      description: t.description || '',
      provenance: t.provenance || 'built-in',
    };
  }
  function register(t) { var n = normalize(t); if (!byId[n.id]) order.push(n.id); byId[n.id] = n; listeners.forEach(function (f) { try { f(); } catch (e) {} }); return n; }
  function registerMany(a) { a.forEach(register); }
  function resolve(id) { var t = byId[id]; if (!t) throw new Error('CV_EVENTS: no trigger "' + id + '"'); return t; }
  function all() { return order.map(function (id) { return byId[id]; }); }
  function query(q) { q = q || {}; return all().filter(function (t) { return (!q.on || t.on === q.on); }); }
  function triggersFor(event) { return all().filter(function (t) { return t.on === event; }); }

  // EMIT — the bus. Returns the list of action results fired.
  function emit(event, payload, ctx) {
    var ectx = Object.assign({ event: payload || {} }, ctx || {});
    var fired = [];
    triggersFor(event).forEach(function (t) {
      if (t.when && COND() && !COND().testAll(t.when, ectx)) return;
      try {
        if (t.handler) fired.push({ trigger: t.id, result: t.handler(ectx) });
        else if (t.do && ACT()) fired.push({ trigger: t.id, result: ACT().invoke(t.do, t.args, ectx) });
      } catch (e) { fired.push({ trigger: t.id, error: e.message }); }
    });
    // notify UI subscribers (so the view re-renders after a reactive change)
    subs.forEach(function (s) { if (s.event === '*' || s.event === event) { try { s.fn(event, payload, fired); } catch (e) {} } });
    return fired;
  }

  function on(event, fn) { var s = { event: event, fn: fn }; subs.push(s); return function () { var i = subs.indexOf(s); if (i >= 0) subs.splice(i, 1); }; }
  function subscribe(fn) { listeners.add(fn); return function () { listeners.delete(fn); }; }

  // ---- seed: attention → highlight, as RULES (not intentional calls) -------
  registerMany([
    {
      id: 'ai-focus-highlights', on: 'ai.focus', do: 'highlight',
      args: { target: '{{ event.target }}', source: 'ai' },
      description: 'When the AI focuses a node (resolving context / about to act), highlight it — so you SEE what Vi is looking at, automatically.',
    },
    {
      id: 'ai-blur-clears', on: 'ai.blur', do: 'highlight', args: { target: null },
      description: 'Clear the AI-attention highlight when Vi looks away.',
    },
    {
      id: 'selection-highlights', on: 'selection.change', do: 'highlight',
      args: { target: '{{ event.target }}', source: 'user' },
      description: 'When the selection changes, highlight the selected node.',
    },
  ]);

  window.CV_EVENTS = {
    register: register, registerMany: registerMany, resolve: resolve, all: all,
    query: query, triggersFor: triggersFor, emit: emit, on: on, subscribe: subscribe,
  };
})();
