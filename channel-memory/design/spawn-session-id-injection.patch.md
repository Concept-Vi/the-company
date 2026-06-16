# Proposed diff — COMPANY_SESSION_ID injection at supervisor /spawn (the injection half of the self-id keystone)

```
trust: fabric-derived — fork-authored PROPOSED diff for the LEAD's file (runtime/session_supervisor.py). Fork does NOT edit it; lead applies (file-disjoint). Pairs with fork's safe-consumer c66f392.
author: ch-8djrpmsl (fork)
date: 2026-06-16
```
> The injection half of the self-serve self-id keystone. fork built the SAFE CONSUMER (resolve_own_session fails loud on ambiguous self, c66f392). This injects the unambiguous self-id at the spawn the consumer reads. Lead applies + wires the clone-permission gate at the same spawn path (host's plan).

## The change (runtime/session_supervisor.py, in `spawn()`, at the Popen ~line 804)
A RESUME (non-fork) spawn CONTINUES under the resumed sid → that sid IS the child session's own id, so inject it as `COMPANY_SESSION_ID`. A fork mints a NEW id (≠ `resume`) and a fresh spawn's id is claude-assigned at launch — both unknown pre-launch, so leave them to the SessionStart hook; **never inject a wrong id** (a wrong COMPANY_SESSION_ID is worse than none — the consumer would resolve confidently to the wrong self).

```diff
         _apply_spawn_flags(cmd, flags, consent=False)   # R1.3 — the registry-declared remainder
-        s.proc = subprocess.Popen(cmd, cwd=s.cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
-                                  stderr=subprocess.PIPE, text=True, bufsize=1)
+        # SELF-ID INJECTION (pairs with fork's resolve_own_session safe-consumer, c66f392): a RESUME
+        # (non-fork) spawn continues under the resumed sid, so that sid IS the child's own session id →
+        # inject COMPANY_SESSION_ID so the child's resolve_own_session("self") resolves UNAMBIGUOUSLY
+        # instead of failing-loud on a multi-transcript project dir. A fork mints a NEW id (not `resume`)
+        # and a fresh spawn's id is claude-assigned at launch — both unknown here, left to the SessionStart
+        # hook; NEVER inject a wrong id (a confident wrong-self is worse than a loud no-self).
+        child_env = dict(os.environ)
+        if resume and not fork:
+            child_env["COMPANY_SESSION_ID"] = resume
+        s.proc = subprocess.Popen(cmd, cwd=s.cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
+                                  stderr=subprocess.PIPE, text=True, bufsize=1, env=child_env)
```

## Why it's safe / behavior-preserving
- For a fresh OR fork spawn (no `resume`, or `fork=True`): `child_env = dict(os.environ)` is byte-equivalent to inheriting the env (Popen env=None inherits os.environ; an explicit copy of the same values is identical) — so the cmd, cwd, pipes, and env are unchanged. ONLY a resume-non-fork spawn gains the one var.
- A resume-non-fork spawn is exactly the clone path (cc_clone materialize→/spawn resume=new_sid, no fork) → the clone gets COMPANY_SESSION_ID=new_sid = its own transcript sid → unambiguous self-id.
- No new failure mode: a wrong id is never injected (fork/fresh excluded); worst case unchanged = the consumer fails loud (already safe).

## Verify-after-apply (suggested, lead's call)
1. A resume-spawn's child env has COMPANY_SESSION_ID == resume (assert on a stub-spawn, lead-only law — no real claude).
2. resolve_own_session() inside a so-spawned session returns how="env COMPANY_SESSION_ID", ambiguous=False (the end-to-end: injection → safe consumer → unambiguous self).
3. session_supervisor's existing acceptance suite stays green (env-injection is additive).

## The SECOND injection point (flagged, lead's lane — not in this diff)
The SessionStart profile-hook should set COMPANY_SESSION_ID for FRESH/fork sessions (whose id is only known post-launch). Together: /spawn covers resume-clones (this diff); the hook covers everything else. Both live at the spawn/start path the lead is wiring the clone-permission gate into.
