---
type: contract-entry
resource: code-review
summary: Claude Code's AI code-review surfaces — the local `/code-review` and `/security-review` slash commands run in a session against a diff, the managed GitHub Code Review service (a fleet of agents posting inline PR comments, research preview), and self-hosted CI (GitHub Actions / GitLab via `claude -p`). All native/hosted; the company exposes NO review face — contracted as the native surface with the bridge gap named, and the real CI path (claude -p) noted.
schemes: []
status: building
relates-to: ["[[session]]", "[[headless-control]]", "[[permission]]", "[[knowledge-corpus]]"]
---

# Resource: code-review
## Identity
**Code review is keyed by what is reviewed — a local DIFF in a session, or a GitHub PULL REQUEST —
not by a standalone record; there is no `code-review://` scheme.** Atlas class CC-19 spans three
native/hosted surfaces, kept apart in the corpus: (1) LOCAL — the `/code-review` and
`/security-review` slash commands run in a Claude Code session against the current diff
(`code-review.md#review-a-diff-locally`, `commands.md`, vault `claude-code-atlas`); (2) MANAGED —
GitHub Code Review, a fleet of specialized agents that analyze a PR on Anthropic infrastructure and
post severity-tagged inline comments (`code-review.md`, research preview, Team/Enterprise, not for
ZDR orgs); (3) CI — Claude Code in GitHub Actions / GitLab CI/CD via headless `claude -p`
(`github-actions.md`, `gitlab-ci-cd.md`, `Custom Apps Integration.md`). HONEST STATUS: all three are
`planned` against the company — there is NO company review endpoint (verified: no
code-review/security-review/PR-review face in `runtime/`/`mcp_face/`/`ops/`). The genuinely-real
path is CI-shaped (a spawned `claude -p` session running a review prompt), which the company's own
session fabric COULD drive but does not package as a review capability; the gap and that path are
named per op.

## Representation
**A review is a set of findings over a change — severity-tagged comments anchored to lines, plus a
summary — produced by one of three surfaces; the shape a UI renders is the finding set.**
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/code-review.review",
  "type": "object",
  "description": "the native review output shape (source code-review.md). The company produces none of this through an endpoint today",
  "properties": {
    "surface": { "enum": ["local-slash", "managed-github", "ci-headless"],
                 "description": "local /code-review|/security-review · managed GitHub Code Review · self-hosted claude -p in CI" },
    "findings": { "type": "array", "items": {
        "type": "object",
        "properties": {
          "severity": { "type": "string", "description": "managed: severity-tagged; does NOT approve/block the PR (review workflows stay intact)" },
          "file": { "type": "string" }, "line": { "type": "integer" },
          "category": { "enum": ["logic-error", "security-vulnerability", "broken-edge-case", "regression"], "description": "the four classes the managed fleet hunts; each agent looks for one class, then a verification step checks candidates against actual code behavior to filter false positives" },
          "comment": { "type": "string" } } } },
    "summary": { "type": "string", "description": "managed: a summary in the review body; if no issues, the GitHub check run shows none-detected" },
    "tuning": { "type": "string", "description": "CLAUDE.md / REVIEW.md in the repo tune what gets flagged" } } }
```
| field | type | volatile? | changed-by | address? → resource | reality (2026-06-12) |
|---|---|---|---|---|---|
| surface | enum | n/a | — | — | NONE company-exposed. local-slash = a TUI command in a session; managed-github = Anthropic-hosted; ci-headless = `claude -p` in a CI runner |
| findings | array | n/a | the review run | — | managed: posted as INLINE PR comments on the exact lines, severity-tagged, non-blocking, ~20 min avg, scales in cost with PR size. The company sees none of this |
| tuning | string | yes | repo CLAUDE.md/REVIEW.md | — | repo-level config; the company does not manage review tuning files |
| (company endpoint) | — | — | — | — | DOES NOT EXIST — no review face in the company. The company HAS a self-hosted GitHub Actions runner (`pipeliner`, ops/services.json reach group) that COULD run a `claude -p` review workflow, but no review capability is packaged |

## State model
**State model: stateless (a review is a run over a fixed change).** A review has no lifecycle of its
own — it runs against a diff/PR and emits findings. The managed service has run states on the GitHub
side (triggered on PR-open / push / `@claude review`; check-run updated; comments auto-resolve when a
developer addresses the issue), but those live in GitHub + the Anthropic service, not in any company
state machine. A CI review is one `claude -p` invocation ([[headless-control]] / [[session]]
lifecycle).

## Caller
**A local review's caller is the operator in the session (running the slash command); a managed
review is triggered by a GitHub event or `@claude review` comment (the GitHub App's identity); a CI
review is the CI runner's job — none is a company caller, because no company endpoint exists.** If a
company review face were built, the nearest real seam is the session fabric: spawn a session
([[session#op: session.create]]) granted Read/Glob/Bash(git *) ([[permission#op: permission.act]]),
inject a review prompt ([[session#op: session.inject]]), and read the result off the stream
([[headless-control#op: headless-control.watch]]) — the exact `claude -p` review pattern the CI docs
show, run on the company's own fabric. All `planned`.

## Operations

## op: code-review.act
**`code-review.act` is the PLANNED review bridge: run a `/code-review` or `/security-review` over a
session's diff, or trigger/read a managed GitHub PR review — the native/hosted capabilities the
company does not expose, named here so a UI knows the real surfaces, the company's un-packaged-but-
buildable CI path (a fabric `claude -p` review), and the research-preview/ZDR constraints on the
managed service.**
```contract:op
op: code-review.act
resource: code-review
kind: act
status: building
direction: outbound
atlas: [CC-19.1, CC-19.2, CC-19.3]
tasks:
  - phrase: "review my current diff for bugs before I push"
    params: {act: review-local}
  - phrase: "run a security review on this change"
    params: {act: security-review-local}
  - phrase: "have claude review this pull request"
    params: {act: review-pr}
  - alias: "code review"
  - alias: "security review"
  - alias: "review this PR"
  - alias: "PR comments"
bindings:
  - { kind: mcp, tool: dev_code_review, op-param: "op=act", server: company, exposure: "exposure.json#mcp-company", status: building, note: "L-④-dev: RAIL R2 — the handler writes a wire-job intent + returns a job-id + watch cursor; the operator-only /api/resolve seam + the wire-loop (implement.py) dispatch the headless `claude -p` review. Findings ride dispatch events (events.watch). The handler NEVER spawns. live-verify pending (lead): a REAL review round-trip is the lead's slice" }
  - { kind: tui, command: "/code-review   ·   /security-review   (in a session, against the current diff)", transport: tui-interactive, exposure: "n/a — interactive", status: planned, note: "NATIVE local slash commands (code-review.md#review-a-diff-locally, commands.md). Run inside a session; the company spawns headless sessions with NO interactive TUI ([[headless-control#Caller]]) so it cannot drive these slash commands. A fabric equivalent = inject the review PROMPT into a spawned session (planned)" }
  - { kind: http, method: "@claude review (GitHub comment) / PR-open trigger", path: "GitHub-hosted (Anthropic infra)", transport: bridge-http, exposure: "n/a — Anthropic-hosted", status: planned, note: "MANAGED GitHub Code Review (research preview, Team/Enterprise, NOT for ZDR orgs). Anthropic-hosted fleet posts inline comments. The COMPANY does not run or proxy this — verified no code-review face in the company" }
  - { kind: cli, command: "claude -p \"Review this PR for bugs\" --allowedTools \"Read,Glob,Bash(git *)\" --output-format json   (in CI)", transport: cli-local, exposure: "exposure.json#cli-local", status: planned, note: "CI path (github-actions.md, Custom Apps Integration.md). The REAL buildable path: the company HAS a self-hosted runner (pipeliner) + a session fabric that runs claude -p; a review workflow is NOT yet packaged as a company capability — the gap" }
liveness: none
emits: []
consequences:
  - when: "local /code-review (planned — would run in a spawned session)"
    expect: []
    bound: "n/a — not built; the company cannot drive a TUI slash command (headless spawn has no TUI)"
    evidence: "no company-visible outcome; a fabric equivalent would inject a review prompt and surface findings on the session stream ([[headless-control#op: headless-control.watch]]) — planned"
  - when: "managed GitHub review (planned — Anthropic-hosted)"
    expect: []
    bound: "n/a — ~20 min avg on Anthropic infra; not a company endpoint"
    evidence: "findings appear as inline PR comments on GitHub; the company sees nothing — it neither runs nor proxies the managed service"
  - when: "CI review via claude -p (planned — buildable on the fabric)"
    expect: []
    bound: "n/a — not packaged; a single claude -p invocation's bound is the session turn timeout ([[session]])"
    evidence: "the --output-format json result carries the review; on the fabric this would be a session.create+inject+watch chain — the real path, un-packaged"
correlate: [session]
verification:
  review-local:    {state: unverified, note: "/code-review is a TUI slash command; the headless fabric has no TUI — planned"}
  review-managed:  {state: unverified, note: "managed GitHub Code Review is Anthropic-hosted, not company-run/proxied — planned"}
  review-ci:       {state: unverified, note: "the claude -p CI review pattern is buildable on the fabric (pipeliner runner + session fabric) but NOT packaged as a company capability — planned"}
```
### Description (purpose-free)
Three native/hosted review surfaces, contracted as a planned company bridge. (1) LOCAL: in a
session, `/code-review` checks the current diff and `/security-review` focuses on vulnerabilities —
no GitHub App needed; these are interactive slash commands (source
`code-review.md#review-a-diff-locally`, `commands.md`). (2) MANAGED: GitHub Code Review runs a fleet
of specialized agents over a PR's diff + surrounding code in parallel on Anthropic infrastructure —
each agent hunts one issue class (logic errors, security vulnerabilities, broken edge cases,
regressions), a verification step filters false positives against actual code behavior, and findings
are deduplicated, severity-ranked, and posted as inline comments with a body summary; non-blocking,
tunable via repo `CLAUDE.md`/`REVIEW.md`, research preview, Team/Enterprise, excluded for ZDR orgs.
(3) CI: `claude -p "Review this PR..." --allowedTools "Read,Glob,Bash(git *)" --output-format json`
in GitHub Actions / GitLab CI/CD. The company exposes none of these. Note the boundary precisely: the
local slash commands cannot run on the headless fabric (no TUI); the managed service is
Anthropic-hosted and un-proxied; but the CI pattern is BUILDABLE on the company's own fabric (it has
a self-hosted runner and a `claude -p` session fabric) — just not packaged as a review capability.
This op names the gap and that real path.
### Request (PLANNED shape — the contract the seam should fulfil)
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/code-review.act.request",
  "type": "object",
  "required": ["act"],
  "properties": {
    "act":     { "enum": ["review-local", "security-review-local", "review-pr"] },
    "session": { "type": "string", "description": "act=review-local/security-review-local: session://<id> whose diff to review (the fabric path injects a review prompt)" },
    "diff_ref": { "type": "string", "description": "act=review-local: a git ref/range to review (defaults to the working diff)" },
    "pr":      { "type": "string", "description": "act=review-pr: the GitHub PR (managed service or CI workflow target)" },
    "focus":   { "enum": ["bugs", "security", "regressions", "all"], "description": "narrows the review (security-review-local pins security)" } },
  "additionalProperties": false }
```
### Interaction semantics
Native rules a consumer MUST respect when this op lands (sourced to the docs):
- **Managed review is non-blocking.** Findings are severity-tagged but do NOT approve/block the PR —
  existing review workflows stay intact.
- **Availability gates.** Managed GitHub Code Review is research preview, Team/Enterprise only,
  off-by-default until an admin enables it, and NOT available for ZDR orgs. For self-hosted, use
  GitHub Actions / GitLab CI/CD instead.
- **Local needs no App.** `/code-review` runs in any session without installing the GitHub App — but
  it is a TUI command, so the headless fabric cannot invoke it; a fabric review would inject the
  prompt instead.
- **Tuning is repo-level.** `CLAUDE.md`/`REVIEW.md` shape what gets flagged.
### Errors
```contract:error
code: code-review.not-exposed | http: 501 | retryable: false
when: any call against this op today
teach: "Code review is PLANNED — no company endpoint runs it. Locally, run /code-review or /security-review in a session (TUI, not the headless fabric). For PRs, use the managed GitHub Code Review (research preview, Team/Enterprise, not ZDR) or a claude -p review in GitHub Actions/GitLab CI. On the fabric, the buildable path is session.create + inject(review prompt) + watch ([[headless-control]]) — named in this op's bindings."
```
```contract:error
code: code-review.managed-unavailable | http: 403 | retryable: false
when: (re: the managed service) the org is ZDR, or Code Review is not admin-enabled
teach: "Managed GitHub Code Review is unavailable for Zero-Data-Retention orgs and is off until an admin enables it (Team/Enterprise). Use a self-hosted claude -p review in GitHub Actions/GitLab CI instead (https://code.claude.com/docs/en/github-actions.md / https://code.claude.com/docs/en/gitlab-ci-cd.md)."
```
```contract:example
captured: synthetic            # status=planned → synthetic legal AND loud; no company review endpoint exists (V11)
binding: cli
request: |
  (the REAL native path — in CI, outside any company endpoint)
  $ claude -p "Review this PR for bugs and style issues" \
      --allowedTools "Read,Glob,Bash(git *)" --output-format json
response: |
  {"result":"3 findings: ...","is_error":false}
  (the company offers NO review endpoint; on the fabric this same prompt would be session.create + inject + watch — planned)
```
Adjacent: [[session#op: session.create]] (the spawn a fabric review would use),
[[session#op: session.inject]] (inject the review prompt), [[headless-control#op: headless-control.watch]]
(read the findings off the stream), [[knowledge-corpus#op: knowledge-corpus.search]] (the review docs).

## Errors
**Resource-level error vocabulary: `code-review.not-exposed` (the honest 501 — no company review
endpoint; the three surfaces are TUI/Anthropic-hosted/CI) and `code-review.managed-unavailable` (the
ZDR / not-admin-enabled gate on the managed service).** Both teach the live recovery — local slash
command, managed GitHub service, or a `claude -p` CI review — and name the buildable fabric path
(session.create + inject + watch). No error claims a review face the company has not built.

## Links
**No address-typed fields: a review references the `session://` whose diff it reviews (dereferences
to [[session]]) and a GitHub PR (an external GitHub resource, not a corpus address).** Findings are
line-anchored comments on a diff/PR, not fabric records — they never resolve to a corpus entry, by
design, since every review surface here is native, hosted, or an un-packaged CI pattern.
