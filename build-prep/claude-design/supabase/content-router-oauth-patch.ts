// content-router-oauth-patch.ts — the approved additive patch for content-router.
// Insert BLOCK 1 after `const pathParts = url.pathname.split('/').filter((p) => p)`
// and before `// --- App route: /app/{app_name} ---`.
// Append BLOCK 2 (the serveConsent function) after the Deno.serve closing `})`.
// Existing /r//p//app/ routes + the "Invalid URL format" fallback are UNTOUCHED (below the check).

// ── BLOCK 1: the if-check (insert after pathParts, before the App route) ──────────────
//
//   // --- OAuth consent (the OAuth Server's Authorization Path points here at /oauth/consent) ---
//   // ADDITIVE: intercept /oauth/consent BEFORE the existing /r//p//app/ routes (untouched below).
//   if (url.pathname.endsWith('/oauth/consent')) return serveConsent(req);
//

// ── BLOCK 2: the serveConsent function (append after Deno.serve's closing `})`) ──────────

function serveConsent(req: Request): Response {
  const anon = Deno.env.get('SUPABASE_ANON_KEY') ?? '';
  const html = `<!doctype html><html><head><meta charset="utf-8"><title>Authorize Vi</title>
<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
<style>body{font:15px/1.5 system-ui,sans-serif;max-width:520px;margin:60px auto;padding:0 20px;color:#111}.card{border:1px solid #ddd;border-radius:12px;padding:28px}button{font:inherit;padding:10px 18px;border:0;border-radius:8px;background:#111;color:#fff;cursor:pointer}input{font:inherit;padding:10px;border:1px solid #ccc;border-radius:8px;width:100%;box-sizing:border-box;margin:4px 0}.muted{color:#666;font-size:13px}</style></head><body>
<div class="card"><h2>Authorize Vi</h2><p><b>Vi (Claude Design)</b> wants to access your Company <b>design</b> channel + your design submissions.</p><div id="app">Checking session…</div><p class="muted">Tim's first-party connector.</p></div>
<script>
const sb = supabase.createClient(${JSON.stringify(supabaseUrl)}, ${JSON.stringify(anon)});
const authId = new URLSearchParams(location.search).get('authorization_id');
let loginMethod = 'email';
async function approve(){ document.getElementById('app').innerHTML='Authorizing…'; const {data,error}=await sb.auth.oauth.approveAuthorization(authId); if(error){document.getElementById('app').innerHTML='<b>Error:</b> '+error.message;return;} location.assign(data.redirect_url); }
function showAllow(){ document.getElementById('app').innerHTML='<p>Signed in.</p><button id="allow">Allow Vi</button>'; document.getElementById('allow').onclick=approve; }
async function go(){
  if(!authId){document.getElementById('app').innerHTML='<b>Error:</b> missing authorization_id';return;}
  const {data:{session}}=await sb.auth.getSession();
  if(session){document.getElementById('app').innerHTML='<p>Signed in as '+(session.user.email||session.user.id)+'.</p><button id="allow">Allow Vi</button>';document.getElementById('allow').onclick=approve;return;}
  document.getElementById('app').innerHTML='<p>Sign in to authorize Vi:</p><p><button id="tab-email">Email</button> <button id="tab-phone">Phone</button></p><div id="login"></div><div id="code-row" style="display:none"><input id="code" placeholder="6-digit code"/><button id="verify">Verify</button></div><div id="msg" class="muted"></div>';
  function showEmail(){ loginMethod='email'; document.getElementById('login').innerHTML='<input id="email" type="email" placeholder="your email"/> <button id="send">Send code</button>'; document.getElementById('send').onclick=sendOtp; }
  function showPhone(){ loginMethod='phone'; document.getElementById('login').innerHTML='<input id="phone" type="tel" placeholder="+61…"/> <button id="send">Send code</button>'; document.getElementById('send').onclick=sendOtp; }
  document.getElementById('tab-email').onclick=showEmail;
  document.getElementById('tab-phone').onclick=showPhone;
  showEmail();
  async function sendOtp(){
    const email=document.getElementById('email')?.value.trim();
    const phone=document.getElementById('phone')?.value.trim();
    let r;
    if(loginMethod==='email'&&email) r=await sb.auth.signInWithOtp({email});
    else if(loginMethod==='phone'&&phone) r=await sb.auth.signInWithOtp({phone});
    else {document.getElementById('msg').textContent='Enter your '+(loginMethod==='email'?'email':'phone')+'.';return;}
    if(r.error){document.getElementById('msg').textContent=r.error.message;return;}
    document.getElementById('code-row').style.display='block';
    document.getElementById('msg').textContent='Code sent — check your '+(loginMethod==='email'?'email':'phone')+'.';
  }
  document.getElementById('verify').onclick=async()=>{
    const email=document.getElementById('email')?.value.trim();
    const phone=document.getElementById('phone')?.value.trim();
    const token=document.getElementById('code').value.trim();
    let r;
    if(loginMethod==='email') r=await sb.auth.verifyOtp({email,token,type:'email'});
    else r=await sb.auth.verifyOtp({phone,token,type:'sms'});
    if(r.error){document.getElementById('msg').textContent=r.error.message;return;}
    showAllow();
  };
}
go();
</script></body></html>`;
  return new Response(html, { status: 200, headers: { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store' } });
}