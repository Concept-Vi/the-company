"""runtime/supabase_principal.py — a least-privilege Supabase PRINCIPAL (authenticated login → JWT, Bearer).

The shared primitive for "a company-internal component authenticates AS a dedicated, RLS-scoped principal"
(the lead's security rule, 2026-06-18): NOT the service-role master key in a subprocess env (the
over-privileged-key hazard), but an authenticated login (email+password OR refresh_token → access_token),
RLS-scoped to exactly the tables it needs. The principal is itself a client-registry row, same pattern as
Claude Design + the factory SA. The REST URL + anon key are public/shared (the apikey PostgREST requires);
only the principal CRED is least-privilege + provisioned into the component's env out-of-channel.

ONE HOME (reuse-don't-parallel): this is the extracted, env-prefix-parameterized form of the principal-JWT
flow vi_vision.py grew first (option B: grant_type=password/refresh_token, cached + refreshed). The channel
boundary uses it from birth (prefix "COMPANY_CHANNEL"); runtime/vi_vision.py migrates onto it as a NAMED
follow-up (its VI_VISION_* env maps to prefix "VI_VISION") — so no parallel copy is ever created (this is the
single home) and the live vi_vision is not destabilized in this pass. Generic by env-prefix:
  {PREFIX}_SUPABASE_URL  (or SUPABASE_URL)          — the project URL (public)
  {PREFIX}_ANON_KEY      (or SUPABASE_ANON_KEY)     — the apikey (public; PostgREST requires it)
  {PREFIX}_SA_EMAIL + {PREFIX}_SA_PASSWORD          — grant_type=password (restart-robust; recommended)
  {PREFIX}_SA_REFRESH_TOKEN                         — grant_type=refresh_token (alternative)

Fail-loud (RAISES — never a silent token); offline-unit-testable via an injected token-fetcher (`fetch`).
The auth flow is byte-for-byte the vi_vision pattern (same Supabase /auth/v1/token endpoint), proven there.
"""
from __future__ import annotations

import os
import json
import time
import base64
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError


class SupabaseAuthError(RuntimeError):
    """The principal could not authenticate (fail-loud; a write/scoped-read needs the JWT)."""


def _b64url_json(segment: str) -> dict:
    pad = "=" * (-len(segment) % 4)
    return json.loads(base64.urlsafe_b64decode(segment + pad).decode("utf-8"))


def jwt_sub(access_token: str) -> str:
    """The principal's uid = the access token's `sub` claim (decode-only; our own token, no verify)."""
    try:
        return str(_b64url_json(access_token.split(".")[1])["sub"])
    except Exception as e:  # noqa: BLE001
        raise SupabaseAuthError(f"could not read sub from the access token: {e}. Fail loud.") from e


class SupabasePrincipal:
    """A dedicated, RLS-scoped Supabase login. `.access_token()` returns a cached, near-expiry-refreshed JWT;
    `.auth_headers()` is {apikey: anon, Authorization: Bearer <jwt>} for PostgREST/Realtime. Env-prefix
    parameterized so one class serves every internal principal (the channel boundary, vi_vision, …). RAISES
    SupabaseAuthError on a missing cred / failed auth — never a silent unauthenticated call."""

    def __init__(self, env_prefix: str, *, env: dict | None = None, fetch=None):
        self.prefix = env_prefix.rstrip("_")
        self._env = env if env is not None else os.environ
        self._fetch = fetch                      # test seam: fetch(grant, payload, url, anon) -> token dict
        self._token = {"access": None, "exp": 0.0}

    # --- env resolution (prefix-first, shared SUPABASE_* fallback) ---
    def _get(self, key: str, *fallbacks: str):
        v = self._env.get(f"{self.prefix}_{key}")
        if v:
            return v
        for fb in fallbacks:
            if self._env.get(fb):
                return self._env[fb]
        return None

    def url(self) -> str | None:
        return self._get("SUPABASE_URL", "SUPABASE_URL")

    def anon_key(self) -> str | None:
        return self._get("ANON_KEY", "SUPABASE_ANON_KEY")

    def _grant(self):
        """(grant_type, payload) from the configured cred — password preferred, else refresh_token. RAISES if none."""
        email = self._get("SA_EMAIL")
        pw = self._get("SA_PASSWORD")
        refresh = self._get("SA_REFRESH_TOKEN")
        if email and pw:
            return "password", {"email": email, "password": pw}
        if refresh:
            return "refresh_token", {"refresh_token": refresh}
        raise SupabaseAuthError(
            f"{self.prefix}: no principal cred — set {self.prefix}_SA_EMAIL+{self.prefix}_SA_PASSWORD or "
            f"{self.prefix}_SA_REFRESH_TOKEN. Fail loud (never an unauthenticated boundary).")

    def _post_token(self, grant: str, payload: dict) -> dict:
        url, anon = self.url(), self.anon_key()
        if not (url and anon):
            raise SupabaseAuthError(
                f"{self.prefix}: SUPABASE_URL + ANON key required to authenticate. Fail loud.")
        endpoint = f"{url.rstrip('/')}/auth/v1/token?grant_type={grant}"
        body = json.dumps(payload).encode("utf-8")
        req = Request(endpoint, data=body, method="POST",
                      headers={"Content-Type": "application/json", "apikey": anon})
        try:
            with urlopen(req, timeout=10) as r:  # noqa: S310
                status, raw = r.status, r.read().decode("utf-8")
        except HTTPError as e:
            status, raw = e.code, e.read().decode("utf-8", "replace")
        except (URLError, TimeoutError) as e:
            raise SupabaseAuthError(f"{self.prefix}: auth POST failed: {e}. Fail loud.") from e
        if status >= 300:
            raise SupabaseAuthError(f"{self.prefix}: auth ({grant}) failed [{status}]: {raw[:200]}. Fail loud.")
        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            raise SupabaseAuthError(f"{self.prefix}: auth returned non-JSON: {e}. Fail loud.") from e

    def access_token(self, *, force: bool = False) -> str:
        """A valid access token (cached; refreshed within 30s of expiry). RAISES SupabaseAuthError."""
        now = time.time()
        if not force and self._token["access"] and self._token["exp"] - 30 > now:
            return self._token["access"]
        grant, payload = self._grant()
        tok = self._fetch(grant, payload, self.url(), self.anon_key()) if self._fetch \
            else self._post_token(grant, payload)
        acc = tok.get("access_token")
        if not acc:
            raise SupabaseAuthError(f"{self.prefix}: auth returned no access_token: {str(tok)[:200]}. Fail loud.")
        self._token["access"] = acc
        self._token["exp"] = now + float(tok.get("expires_in", 3600))
        return acc

    def auth_headers(self) -> dict:
        """PostgREST/Realtime headers — apikey=anon (public), Authorization=Bearer <principal JWT> (scoped)."""
        anon = self.anon_key()
        if not anon:
            raise SupabaseAuthError(f"{self.prefix}: ANON key required (apikey). Fail loud.")
        return {"apikey": anon, "Authorization": f"Bearer {self.access_token()}"}

    def uid(self) -> str:
        """The principal's uid (the JWT `sub`) — for RLS owner checks / audit."""
        return jwt_sub(self.access_token())


if __name__ == "__main__":
    # OFFLINE self-test — env resolution · grant selection · cached/refresh · fail-loud · jwt_sub.
    # Injected fetch (no network): returns a hand-made unsigned token; proves the flow without a backend.
    fake_sub = "company-channel-boundary-1"
    payload_b64 = base64.urlsafe_b64encode(json.dumps({"sub": fake_sub}).encode()).decode().rstrip("=")
    fake_jwt = f"h.{payload_b64}.s"
    calls = {"n": 0}

    def _fake_fetch(grant, payload, url, anon):
        calls["n"] += 1
        assert grant == "password" and payload["email"] == "boundary@x", (grant, payload)
        assert url == "https://gctunhsuwpaxeatwlmuv.supabase.co" and anon == "anon-key", (url, anon)
        return {"access_token": fake_jwt, "expires_in": 3600}

    env = {"COMPANY_CHANNEL_SUPABASE_URL": "https://gctunhsuwpaxeatwlmuv.supabase.co",
           "COMPANY_CHANNEL_ANON_KEY": "anon-key",
           "COMPANY_CHANNEL_SA_EMAIL": "boundary@x", "COMPANY_CHANNEL_SA_PASSWORD": "pw"}
    p = SupabasePrincipal("COMPANY_CHANNEL", env=env, fetch=_fake_fetch)
    assert p.url().endswith("supabase.co") and p.anon_key() == "anon-key"
    assert p.access_token() == fake_jwt and calls["n"] == 1
    assert p.access_token() == fake_jwt and calls["n"] == 1, "cached — no second fetch"
    h = p.auth_headers()
    assert h["apikey"] == "anon-key" and h["Authorization"] == f"Bearer {fake_jwt}", h
    assert p.uid() == fake_sub, p.uid()

    # refresh_token grant when no password
    env2 = {"COMPANY_CHANNEL_SUPABASE_URL": "https://x.supabase.co", "COMPANY_CHANNEL_ANON_KEY": "a",
            "COMPANY_CHANNEL_SA_REFRESH_TOKEN": "rt"}
    p2 = SupabasePrincipal("COMPANY_CHANNEL", env=env2,
                           fetch=lambda g, pl, u, a: {"access_token": fake_jwt} if g == "refresh_token" else None)
    assert p2.access_token() == fake_jwt

    # fail-loud: no cred
    p3 = SupabasePrincipal("COMPANY_CHANNEL", env={"COMPANY_CHANNEL_SUPABASE_URL": "u", "COMPANY_CHANNEL_ANON_KEY": "a"})
    try:
        p3.access_token(); raise SystemExit("FAIL: no-cred did not raise")
    except SupabaseAuthError:
        pass
    # shared SUPABASE_* fallback
    p4 = SupabasePrincipal("VI_VISION", env={"SUPABASE_URL": "https://shared.supabase.co",
                                             "SUPABASE_ANON_KEY": "shared-anon", "VI_VISION_SA_REFRESH_TOKEN": "rt"},
                           fetch=lambda *_: {"access_token": fake_jwt})
    assert p4.url() == "https://shared.supabase.co" and p4.anon_key() == "shared-anon" and p4.access_token() == fake_jwt
    print("supabase_principal OFFLINE self-test: ALL PASS (env-resolve·grant·cache·refresh·fail-loud·jwt_sub·shared-fallback)")
