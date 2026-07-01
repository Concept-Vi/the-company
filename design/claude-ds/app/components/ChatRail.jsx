// ChatRail.jsx — persistent AI conversation on the right
const { useState: useState_cr, useEffect: useEffect_cr, useRef: useRef_cr } = React;

const SUGGESTED = {
  overview:   ['Audit my system', 'What gaps should I fill first?', 'Show me what I have'],
  build:      ['Build me a property brochure', 'Generate a payment subsystem', 'What can the Build canvas do?'],
  inbox:      ['Tag everything for me', 'What should I do with these?'],
  icons:      ['Suggest icons I\'m missing', 'Generate a "payment" icon', 'Why use bronze vs gold?'],
  colors:     ['Suggest an accent palette', 'Is my palette accessible?', 'Add a chart palette'],
  type:       ['Recommend a body pair for Sora', 'How should I scale on mobile?'],
  logos:      ['Help me write usage rules', 'When to use the V mark vs wordmark?'],
  imagery:    ['Generate a hero render', 'Make a moodboard for Eclipse Tower', 'What photo style fits the brand?', 'Edit my last upload'],
  patterns:   ['Soften my shadow scale', 'Make corners sharper', 'Add a snap easing', 'Audit non-token usage'],
  components: ['Design a new button variant', 'Audit my form patterns'],
  templates:  ['Build a slide template', 'What does my brochure need?'],
  voice:      ['Rewrite this in brand voice', 'Add tone for error messages'],
};

const SCOPE_LABEL = {
  overview: 'whole system',
  build: 'Build',
  inbox: 'Inbox',
  icons: 'Icons',
  colors: 'Colors',
  type: 'Type',
  logos: 'Logos',
  imagery: 'Imagery',
  patterns: 'Motion & space',
  components: 'Components',
  templates: 'Templates',
  voice: 'Voice & tone',
  settings: 'Settings',
};

const SYSTEM_CONTEXT = `You are Vi, the AI assistant inside ConceptV Studio — a design-system manager for ConceptV, an Australian innovation-technology company.

ConceptV's brand is warm-paper-with-gold-ink: ivory canvas (#FBF7EC), warm ink (#1F1A12), saturated gold (#E0C010) for primary accents, bronze (#988058) for line illustrations and screen titles. Type is Sora (display) + DM Sans (body). The icon library is 99 line icons on a 24×24 grid, 1.5px stroke, rounded caps, no fills. Entities each have a canonical shape: User Portal → circle, Property Wizard → hexagon, Virtual Hubs → octagon, Vi → diamond. Voice is precise, sentence-case, second-person ("you"), no exclamation marks, no emoji in body copy.

You can also generate and edit images via OpenAI — when a user clearly asks for an image, the studio routes the request straight to image generation. If asked HOW image gen works, point them at Settings (to add an API key) and Imagery → AI Studio (for the full workflow). Don't claim to generate when no key is connected — say so and link to Settings.

Be concise — your replies appear in a narrow side rail. 2-4 short sentences. Use **bold** for emphasis, \`code\` for token names. Speak in the first person as Vi. End with one concrete suggestion or question.`;

function ChatRail({ scope, onAction }) {
  const WSDiffCard = window.WSDiffCard;
  const [messages, setMessages] = useState_cr([
    { from: 'vi', text: `Hi — I'm V<span class="i">i</span>. I can help you audit, generate, and shape every part of your design system. What are we doing today?` },
  ]);
  const [input, setInput] = useState_cr('');
  const [thinking, setThinking] = useState_cr(false);
  const msgsRef = useRef_cr(null);

  useEffect_cr(() => {
    if (msgsRef.current) msgsRef.current.scrollTop = msgsRef.current.scrollHeight;
  }, [messages, thinking]);

  async function send(text) {
    const userText = (text ?? input).trim();
    if (!userText || thinking) return;
    setInput('');
    setMessages(m => [...m, { from: 'user', text: userText }]);
    setThinking(true);

    // === IMAGE INTENT ROUTE ===
    // If the user asks for an image (any canvas), route through cvOpenAI.
    // Imagery canvas is the natural home, but Vi will respond with an image
    // from any context if the request is unambiguous.
    const imageIntent = window.cvOpenAI?.classifyIntent?.(userText);
    if (imageIntent?.kind === 'image-generate' && window.cvOpenAI?.getSettings?.()?.enableForVi) {
      if (!window.cvOpenAI.isConfigured()) {
        setMessages(m => [...m, {
          from: 'vi',
          text: `I can generate images, but I need an <b>OpenAI key</b> first. <a class="link" data-nav="settings">Open Settings →</a>`,
        }]);
        setThinking(false);
        return;
      }
      try {
        // Brand-enrich the prompt before sending
        const enrich = `${userText}. Style: ConceptV's warm-paper-with-gold-ink palette — ivory canvas (#FBF7EC), warm ink, saturated gold (#E0C010), bronze illustration accents. Natural light, warm tones, no cool greys.`;
        const out = await window.CV_AI.resolveProvider('openai-image').generateImage({ prompt: enrich, n: 1 });
        const img = out[0];
        if (img) {
          // Persist into AI history so it's available across the app
          try { await window.cvImageStore.addFromSrc('ai', null, img.src, { name: userText.slice(0, 60), prompt: userText, source: 'ai' }); } catch {}
          setMessages(m => [...m, {
            from: 'vi',
            kind: 'image',
            image: img.src,
            prompt: userText,
            text: `Here's a first pass. Adopt it into your system library or edit it from <a class="link" data-nav="imagery">Imagery →</a>`,
          }]);
          setThinking(false);
          return;
        }
      } catch (e) {
        setMessages(m => [...m, { from: 'vi', text: `Image generation failed: ${escapeHtml(e.message)}. <a class="link" data-nav="settings">Check Settings →</a>` }]);
        setThinking(false);
        return;
      }
    }

    // Workshop-aware path — if there's a live doc and the user's message looks
    // like an edit instruction, propose a diff inline instead of just answering.
    const bridgeDoc = scope === 'workshop' ? window.WS_AI?.bridge?.getActive?.() : null;
    if (bridgeDoc) {
      try {
        const intent = await window.WS_AI.classifyIntent({ doc: bridgeDoc, message: userText });
        if (intent.kind === 'edit') {
          const proposal = await window.WS_AI.generateEdit({ doc: bridgeDoc, message: userText });
          if (proposal && proposal.diff && (proposal.diff.diffs?.length || proposal.diff.kind !== 'batch')) {
            setMessages(m => [...m, {
              from: 'vi',
              kind: 'diff',
              proposal,
              text: `I can make this change: <b>${escapeHtml(proposal.summary)}</b>`,
            }]);
            setThinking(false);
            return;
          }
        }
      } catch {}
    }

    try {
      const history = messages.slice(-6).map(m => ({
        role: m.from === 'user' ? 'user' : 'assistant',
        content: typeof m.text === 'string' ? m.text.replace(/<[^>]+>/g, '') : '',
      }));
      const docHint = bridgeDoc ? `\n\nThe user is currently editing this ${bridgeDoc.type}: "${bridgeDoc.title}" (${bridgeDoc.pages?.length ? `${bridgeDoc.pages.length} pages` : bridgeDoc.steps?.length ? `${bridgeDoc.steps.length} steps` : ''}). Speak in terms of it when relevant.` : '';
      const prompt = `${SYSTEM_CONTEXT}\n\nCurrent canvas: ${SCOPE_LABEL[scope] || scope}.${docHint}`;
      const reply = await window.CV_AI.complete({
        messages: [
          { role: 'user', content: prompt },
          ...history,
          { role: 'user', content: userText },
        ],
      });
      setMessages(m => [...m, { from: 'vi', text: formatReply(reply) }]);
    } catch (err) {
      setMessages(m => [...m, { from: 'vi', text: 'I had trouble reaching the model just now. Try again, or rephrase.' }]);
    } finally {
      setThinking(false);
    }
  }

  function applyDiffMessage(i) {
    const m = messages[i];
    if (!m?.proposal) return;
    const ok = window.WS_AI.bridge.apply(m.proposal.diff);
    if (ok) {
      setMessages(prev => prev.map((mm, j) => j === i ? { ...mm, kind: 'diff-applied', text: `Applied: <b>${escapeHtml(m.proposal.summary)}</b>` } : mm));
      window.dsaToast?.('Applied — ⌘Z to undo');
    } else {
      window.dsaToast?.('Apply failed');
    }
  }
  function discardDiffMessage(i) {
    setMessages(prev => prev.map((mm, j) => j === i ? { ...mm, kind: 'diff-discarded', text: 'Edit discarded.' } : mm));
  }

  const suggested = SUGGESTED[scope] || [];

  return (
    <aside className="dsa-chat">
      <div className="dsa-chat-head">
        <ViShape size={20}/>
        <h3 className="title">V<span style={{color:'var(--accent-gold)'}}>i</span></h3>
        <span className="scope">{SCOPE_LABEL[scope] || scope}</span>
      </div>
      <div className="dsa-chat-msgs" ref={msgsRef}>
        {messages.map((m, i) => (
          <div className="dsa-msg" key={i}>
            <div className={`dsa-msg-avatar ${m.from === 'user' ? 'user' : ''}`}>
              {m.from === 'user'
                ? <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 12 a4 4 0 1 0 0-8 a4 4 0 0 0 0 8 Z M4 22 a8 8 0 0 1 16 0 Z"/></svg>
                : <ViShape size={28}/>
              }
            </div>
            <div className="dsa-msg-body">
              <div className="dsa-msg-name">{m.from === 'user' ? 'You' : <>V<span className="i">i</span></>}</div>
              <div className="dsa-msg-text" dangerouslySetInnerHTML={{ __html: m.text }}
                onClick={(e) => {
                  const navTarget = e.target?.dataset?.nav;
                  if (navTarget) { e.preventDefault(); window.cvNav?.(navTarget); }
                }}/>
              {m.kind === 'image' && m.image && (
                <div className="cv-msg-image">
                  <img src={m.image} alt={m.prompt || ''}/>
                  <div className="cv-msg-image-actions">
                    <button className="primary" onClick={async () => {
                      try {
                        await window.cvImageStore.addFromSrc('system', null, m.image, { name: m.prompt?.slice(0, 60) || 'From Vi', prompt: m.prompt, source: 'ai', tags: ['AI'] });
                        window.dsaToast?.('Added to system library');
                      } catch { window.dsaToast?.('Could not adopt'); }
                    }}>Adopt to system</button>
                    <button onClick={() => window.cvNav?.('imagery')}>Open in Imagery</button>
                    <button onClick={() => {
                      const a = document.createElement('a');
                      a.href = m.image; a.download = 'vi-generation.png'; a.click();
                    }}>Download</button>
                  </div>
                </div>
              )}
              {m.kind === 'diff' && m.proposal && (
                <WSDiffCard
                  proposal={m.proposal}
                  doc={window.WS_AI?.bridge?.getActive?.()}
                  onApply={() => applyDiffMessage(i)}
                  onDiscard={() => discardDiffMessage(i)}
                />
              )}
            </div>
          </div>
        ))}
        {thinking && (
          <div className="dsa-msg">
            <div className="dsa-msg-avatar"><ViShape size={28} animated/></div>
            <div className="dsa-msg-body">
              <div className="dsa-msg-name">V<span className="i">i</span></div>
              <div className="dsa-msg-text" style={{color:'var(--fg-secondary)'}}>thinking…</div>
            </div>
          </div>
        )}
        {messages.length === 1 && !thinking && (
          <div className="dsa-suggested-actions">
            {suggested.map(s => (
              <button key={s} className="dsa-sugg-pill" onClick={() => send(s)}>{s}</button>
            ))}
          </div>
        )}
      </div>
      <div className="dsa-chat-composer">
        <div className="input-row">
          <textarea
            placeholder={(() => {
              const bd = scope === 'workshop' && window.WS_AI?.bridge?.getActive?.();
              if (bd) {
                return `Ask Vi or tell Vi to edit "${bd.title || bd.type}"… try "make page 2 more urgent"`;
              }
              return `Ask Vi anything about ${SCOPE_LABEL[scope] || 'your system'}…`;
            })()}
            value={input}
            rows="1"
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => {
              if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
            }}
            disabled={thinking}
          />
          <button className="send" onClick={() => send()} disabled={thinking || !input.trim()}>→</button>
        </div>
        <div className="hint">
          {scope === 'workshop' && window.WS_AI?.bridge?.getActive?.()
            ? 'Enter to send · Vi will either answer or propose an editable diff'
            : `Enter to send · Shift+Enter for newline · Vi reads ${SCOPE_LABEL[scope] || 'your system'}`}
        </div>
      </div>
    </aside>
  );
}

function formatReply(text) {
  // Light markdown-ish transforms for the chat rail
  return String(text || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/\*\*(.+?)\*\*/g, '<b>$1</b>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>');
}

function escapeHtml(s) {
  return String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

window.ChatRail = ChatRail;
