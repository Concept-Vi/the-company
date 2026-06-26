// content-router-oauth-patch-v2.ts — the UPDATED serveConsent (reuses content_login.html).
// Replace BLOCK 2 (the serveConsent function) in content-router with this version.
// BLOCK 1 (the if-check) stays the same.
//
// CHANGES FROM v1: instead of new email/phone OTP tabs, REUSES the existing content_login.html
// (the "Vi Content Access" page Tim knows) downloaded from Storage. Injects a consent-specific
// script that uses the SAME form IDs (phone-form, phone, otp-form, otp, etc.) + the SAME phone OTP
// flow (normalizePhone → signInWithOtp({phone}) → verifyOtp({phone,token,type:'sms'})) but:
//   • SKIPS content-auth-check (no content_id for consent — just authenticate any valid account).
//   • On load: checks session → if present, shows "Allow Vi" → approveAuthorization → redirect.
//   • After verifyOtp → redirects to location.href (back to /oauth/consent, now with session) →
//     page reloads → session present → "Allow Vi" → approve.
// Tim sees the SAME login page he's always used; only the post-login behavior is consent-specific.

function serveConsent(req: Request): Response {
  const anon = Deno.env.get('SUPABASE_ANON_KEY') ?? '';
  // Download the EXISTING content_login.html (the "Vi Content Access" page real users know)
  const { data, error } = await supabase.storage.from('pages').download('content_login.html');
  if (error || !data) {
    return new Response('Login page unavailable: ' + (error?.message || 'not found'), { status: 500, headers: { 'Content-Type': 'text/plain' } });
  }
  let html = await data.text();
  // Replace the content_id placeholder (content_login.html has CONTENT_ID_PLACEHOLDER)
  html = html.replace(/CONTENT_ID_PLACEHOLDER/g, 'consent');
  // Inject the consent script (same phone OTP flow, no content-auth-check, session check + Allow Vi)
  const consentScript = `<script>
const sb = supabase.createClient(${JSON.stringify(supabaseUrl)}, ${JSON.stringify(anon)});
const authId = new URLSearchParams(location.search).get('authorization_id');
function normalizePhone(value){if(!value)return'';var raw=String(value).trim().replace(/[\\s\\-().]/g,'');if(!raw)return'';if(raw.startsWith('+'))return'+'+raw.replace(/[^0-9]/g,'');if(/^04\\d{8}$/.test(raw))return'+61'+raw.slice(1);if(/^614\\d{8}$/.test(raw))return'+'+raw;if(/^\\d{10,15}$/.test(raw))return'+'+raw;return'+'+raw.replace(/[^0-9]/g,'');}
var userPhone='';
async function approve(){var r=await sb.auth.oauth.approveAuthorization(authId);if(r.error){document.getElementById('message').textContent=r.error.message;return;}location.assign(r.data.redirect_url);}
async function go(){
  if(!authId){document.getElementById('message').textContent='Error: missing authorization_id';return;}
  var s=await sb.auth.getSession();if(s.data.session){
    // already logged in — show Allow Vi
    var c=document.querySelector('.card')||document.body;
    c.innerHTML='<h2>Authorize Vi</h2><p>Signed in as '+(s.data.session.user.phone||s.data.session.user.email||s.data.session.user.id)+'.</p><p>Vi (Claude Design) wants to access your Company design channel + your design submissions.</p><button id="allow" style="font:inherit;padding:10px 18px;border:0;border-radius:8px;background:#111;color:#fff;cursor:pointer">Allow Vi</button>';
    document.getElementById('allow').onclick=approve;return;
  }
  // wire the existing phone form (same IDs as content_login.html)
  var pf=document.getElementById('phone-form'),pi=document.getElementById('phone');
  if(pf&&pi){pf.addEventListener('submit',async function(e){e.preventDefault();userPhone=normalizePhone(pi.value);if(!userPhone){document.getElementById('message').textContent='Enter your phone number';return;}var r=await sb.auth.signInWithOtp({phone:userPhone});if(r.error){document.getElementById('message').textContent=r.error.message;return;}document.querySelectorAll('.form-step').forEach(function(el){el.classList.remove('active');});var os=document.getElementById('otp-step');if(os)os.classList.add('active');document.getElementById('otp-message').textContent='Code sent — check your phone.';});}
  var of=document.getElementById('otp-form'),oi=document.getElementById('otp');
  if(of&&oi){of.addEventListener('submit',async function(e){e.preventDefault();var t=oi.value.trim();if(!t||t.length!==6){document.getElementById('otp-message').textContent='Enter the 6-digit code';return;}var r=await sb.auth.verifyOtp({phone:userPhone,token:t,type:'sms'});if(r.error){document.getElementById('otp-message').textContent=r.error.message;return;}location.assign(location.href);});oi.addEventListener('input',function(e){if(e.target.value.length===6)of.dispatchEvent(new Event('submit'));});}
}
go();
</script>`;
  if (html.includes('</body>')) { html = html.replace('</body>', consentScript + '\n</body>'); }
  else { html += '\n' + consentScript; }
  return new Response(html, { status: 200, headers: { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store' } });
}