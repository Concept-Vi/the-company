// claude-design-gateway/index.ts — the OAuth-facing DOOR (a thin forwarder, NOT a second brain).
//
// Tim 2026-06-22 — UNIFY: there is ONE brain (the box's remote.py, which owns the live tool
// registry + the identity→posture access filter). This edge function exists ONLY because the
// OAuth resource must live at a stable cloud URL (the app connects HERE and the Supabase OAuth
// client / redirect URLs are bound HERE — unchanged). It does NO tool logic, holds NO tool list,
// makes NO access decision. It:
//   1. serves the OAuth discovery (resource = THIS gateway URL, AS = Supabase) — bootstraps login;
//   2. on a request with no Bearer token → 401 + WWW-Authenticate pointing at THIS gateway's
//      discovery (so the app runs OAuth against the resource it was configured for);
//   3. on a request WITH a token → forwards it verbatim (body + Authorization header) to the box
//      (remote.py over the Tailscale Funnel). The box does the REAL auth (validates the Supabase
//      JWT) + the tool list + dispatch. The 15-tool clients.allowed_tools column and the gateway's
//      own dispatch() are DELETED — no duplicated menu, no duplicated auth decision.
//
// The box URL is a PUBLIC address (the Funnel), not a secret — no gateway secrets needed beyond the
// auto-injected SUPABASE_URL. Auth is the forwarded user JWT; the box re-validates it (deny-all
// without a valid token; sub==operator → all 66; other valid user → posture-safe subset).

const SUPABASE_URL = Deno.env.get("SUPABASE_URL") ?? "";
// The box's public Funnel origin (remote.py). Overridable via COMPANY_BACKEND_URL; the default is
// Tim's workstation Funnel. Public URL, not a secret.
const BACKEND_URL = (Deno.env.get("COMPANY_BACKEND_URL") ?? "https://workstation001.tail777bc2.ts.net").replace(/\/+$/, "");

function publicOrigin(): string { return SUPABASE_URL; }
function json(code: number, obj: unknown): Response {
  return new Response(JSON.stringify(obj), { status: code, headers: { "Content-Type": "application/json" } });
}

async function handler(req: Request): Promise<Response> {
  const url = new URL(req.url);
  const origin = publicOrigin();
  const mcpResource = `${origin}/functions/v1/claude-design-gateway/mcp`;
  const discoveryUrl = `${origin}/functions/v1/claude-design-gateway/.well-known/oauth-protected-resource`;

  // 1. OAuth discovery — resource = THIS gateway (unchanged; the app's OAuth is bound here).
  if (url.pathname.endsWith("/.well-known/oauth-protected-resource"))
    return json(200, { resource: mcpResource, authorization_servers: [`${origin}/auth/v1`], bearer_methods_supported: ["header"] });

  if (url.pathname.endsWith("/healthz"))
    return json(200, { ok: true, service: "claude-design-gateway", role: "forwarder", backend: BACKEND_URL });

  if (url.pathname.endsWith("/mcp")) {
    if (req.method === "GET") return new Response(null, { status: 405 });
    if (req.method !== "POST") return json(404, { error: "unknown path" });

    // 2. no token → 401 pointing at THIS gateway's discovery (bootstraps the OAuth the app expects).
    const auth = req.headers.get("authorization") ?? "";
    if (!auth.startsWith("Bearer "))
      return new Response(null, { status: 401, headers: { "WWW-Authenticate": `Bearer resource_metadata="${discoveryUrl}"` } });

    // 3. token present → forward verbatim to the box. The BOX validates + lists + dispatches.
    const body = await req.text();
    let upstream: Response;
    try {
      upstream = await fetch(`${BACKEND_URL}/mcp`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "Authorization": auth },
        body,
      });
    } catch (e) {
      return json(502, { error: `gateway could not reach the company box: ${(e as Error).message}` });
    }
    // Pass the box's response straight back. If the box 401s (bad/expired token), re-point the
    // WWW-Authenticate at THIS gateway's discovery so the app re-auths against the right resource.
    const headers = new Headers({ "Content-Type": upstream.headers.get("Content-Type") ?? "application/json" });
    if (upstream.status === 401) headers.set("WWW-Authenticate", `Bearer resource_metadata="${discoveryUrl}"`);
    return new Response(await upstream.text(), { status: upstream.status, headers });
  }

  return json(404, { error: "unknown path" });
}

Deno.serve({ port: Number(Deno.env.get("PORT") ?? "8000"), hostname: Deno.env.get("HOST") ?? "127.0.0.1" }, handler);
