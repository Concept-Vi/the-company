---
type: contract-entry
resource: ci
summary: CI/CD-triggered Claude Code — GitHub Actions (anthropics/claude-code-action@v1, installed via /install-github-app, auto-detecting @claude-mention vs prompt mode, fired by any GitHub event incl. schedule:) and GitLab CI/CD (a .gitlab-ci.yml job running headless `claude -p` with the mcp__gitlab tool). Both run on YOUR CI runners with provider secrets (Claude API / Bedrock-OIDC / Vertex-WIF); the Company exposes neither — they are external CI-provider integrations, contracted with the auth/secret model named.
schemes: []
status: planned
relates-to: ["[[routines]]", "[[git]]", "[[session]]", "[[permission]]", "[[model]]"]
---

# Resource: ci

## Identity
**A CI integration is identified by the CI provider's own job/workflow (a GitHub Actions workflow
file `.github/workflows/*.yml` running the `anthropics/claude-code-action`, or a GitLab job in
`.gitlab-ci.yml`) — there is no `ci://` scheme and no Company record, because CI-triggered Claude
runs entirely on the CI provider's runners, not on this machine and not through any Company
service.** GitHub Actions is the Anthropic-maintained action
(https://code.claude.com/docs/en/github-actions.md); GitLab CI/CD is a GitLab-maintained beta
built on the Claude Code CLI + Agent SDK (https://code.claude.com/docs/en/gitlab-ci-cd.md). This
entry contracts the real trigger and auth/secret model of both so a UI can present and reason
about them; every binding names that the Company proxies none of it.

## Representation
**A CI integration has: a TRIGGER (a CI event — PR/issue comment with `@claude`, `pull_request`,
`push`, `schedule:` cron, manual/web/API), a PROVIDER (Claude API via an API-key secret, or
Amazon Bedrock / Google Vertex AI via keyless OIDC/Workload-Identity-Federation), an IDENTITY
(the GitHub App / GitLab job token that lets Claude write comments and open PRs/MRs), and a
PROMPT (a `@claude` mention, an explicit `prompt:` input, or a `claude -p` argument).** Sourced to
github-actions.md (action params, secrets, the @claude vs prompt auto-detection) and
gitlab-ci-cd.md (the `.gitlab-ci.yml` job, AI_FLOW_* variables, `mcp__gitlab`).

```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/ci.integration",
  "type": "object",
  "description": "A CI integration as the native surfaces model it. NOT a company record — no company endpoint returns this; fields mirror github-actions.md / gitlab-ci-cd.md.",
  "properties": {
    "provider":  { "enum": ["github-actions", "gitlab-ci"] },
    "trigger":   { "type": "object",
      "description": "GitHub: any GitHub event — issue_comment/pull_request_review_comment/issues with `@claude` (interactive mode, auto-detected), pull_request [opened,synchronize], `schedule: cron` (custom automation mode), push, etc. GitLab: rules on $CI_PIPELINE_SOURCE == web|merge_request_event, manual run, or a comment-note webhook that triggers the pipeline with AI_FLOW_* vars" },
    "model_provider": { "enum": ["claude-api", "bedrock", "vertex"], "description": "claude-api uses ANTHROPIC_API_KEY (a repo/CI secret); bedrock uses GitHub-OIDC→IAM-role or GitLab-OIDC→assume-role (no static keys, AWS_ROLE_TO_ASSUME); vertex uses Workload Identity Federation (GCP_WORKLOAD_IDENTITY_PROVIDER + GCP_SERVICE_ACCOUNT, no downloaded keys)" },
    "identity":  { "type": "string", "description": "GitHub: the Claude GitHub App (official `apps/claude`) or a custom GitHub App (APP_ID + APP_PRIVATE_KEY → actions/create-github-app-token). GitLab: CI_JOB_TOKEN by default, or a Project Access Token (GITLAB_ACCESS_TOKEN) with `api` scope" },
    "claude_args": { "type": "string", "description": "GitHub: claude_args passes any CLI flag (--max-turns/--model/--allowedTools/--mcp-config/--append-system-prompt). GitLab: the `claude -p` invocation passes --permission-mode/--allowedTools/--model directly" },
    "version":   { "type": "string", "description": "GitHub Action v1 (GA; @v1 auto-detects mode; replaces the @beta `mode:`/`direct_prompt:` inputs). GitLab integration is beta" } } }
```
| field | type | volatile? | changed-by | address? → resource | reality (2026-06-12) |
|---|---|---|---|---|---|
| workflow / job definition | — | no (config) | edit `.github/workflows/*.yml` or `.gitlab-ci.yml` in the repo | — | NATIVE: lives in the consumer's repo; the Company stores/returns none of it |
| run | — | yes | a CI event matches the trigger | — | runs on the CI provider's runners (GitHub-hosted runners / GitLab runners), consuming CI minutes + API tokens. NO company endpoint and NO company [[events]] — observable only in the CI provider's UI |
| secrets | — | no | repo/CI settings | — | ANTHROPIC_API_KEY / APP_PRIVATE_KEY / AWS_ROLE_TO_ASSUME / GCP_* held as CI provider secrets; NEVER committed. The Company neither stores nor injects them |

## State model
**State model: stateless** (the Company holds no CI state). A CI run's lifecycle belongs entirely
to the CI provider (queued → running on a runner → success/failure), observable only in GitHub
Actions / GitLab pipeline UIs — not through any Company endpoint. The Company's own `up`/build is
NOT CI in this sense (it is the recursive self-build on this host, [[git]]'s self-commit note),
and is deliberately out of scope as a consumer CI capability.

## Caller
**CI-triggered Claude runs as the CI identity, NOT a Company caller: on GitHub, commits/PRs are
authored by the Claude GitHub App (or your custom App) — and CI on Claude's commits requires the
App/custom-app identity (not the Actions user) or follow-up workflows won't fire; on GitLab, the
job writes comments/MRs via `CI_JOB_TOKEN` or a PAT with `api` scope.** Authentication to the
model provider is keyed (ANTHROPIC_API_KEY) or keyless (Bedrock via GitHub/GitLab OIDC → IAM
role; Vertex via Workload Identity Federation), always from CI-provider secrets, never hardcoded.
Permission posture in CI is set by `claude_args`/the `claude -p` flags (GitLab examples run
`--permission-mode acceptEdits` so the job is autonomous) — the [[permission]] subagent-inheritance
and deny-beats-everything rules still apply. There is no Company identity story because there is no
Company face.

## Operations

## op: ci.create
**`ci.create` is the PLANNED scaffolding of a CI integration (a GitHub Actions workflow or a
GitLab job) — the Company generates neither; natively you run `/install-github-app` (the
guided GitHub setup) or add a `claude` job to `.gitlab-ci.yml` plus a masked secret.**
```contract:op
op: ci.create
resource: ci
kind: create
status: planned
direction: outbound
atlas: [CC-30.1, CC-30.3]
tasks:
  - phrase: "set up Claude to respond to @claude mentions in my PRs"
    params: {provider: github-actions}
  - phrase: "add Claude to my GitHub Actions on every new PR"
    params: {provider: github-actions, trigger: "pull_request.opened"}
  - phrase: "run Claude in my GitLab pipeline to turn issues into MRs"
    params: {provider: gitlab-ci}
  - phrase: "run Claude on Bedrock from CI without static keys"
    params: {model_provider: bedrock}
  - alias: "install the Claude GitHub app"
  - alias: "add a claude job to gitlab-ci"
  - alias: "automate PR review in CI"
bindings:
  - { kind: cli, command: "/install-github-app   (NATIVE CLI command — guided GitHub App + secrets setup; repo admin only; direct Claude API only)", transport: tui-interactive, exposure: "n/a — interactive", status: planned, note: "GAP: no company face. Installs `apps/claude` (Contents/Issues/Pull-requests read&write), adds ANTHROPIC_API_KEY secret, copies the example workflow. Manual path: install the App, add the secret, copy examples/claude.yml into .github/workflows/. Bedrock/Vertex skip the quickstart (custom-App + OIDC/WIF setup)" }
  - { kind: cli, command: ".gitlab-ci.yml `claude` job + masked ANTHROPIC_API_KEY variable   (NATIVE GitLab — beta, GitLab-maintained)", transport: tui-interactive, exposure: "n/a — interactive", status: planned, note: "GAP: no company face. Job installs the CLI (curl claude.ai/install.sh), optionally starts a gitlab-mcp-server, runs `claude -p \"$AI_FLOW_INPUT\" --permission-mode acceptEdits --allowedTools \"Bash Read Edit Write mcp__gitlab\"`. Rules gate on $CI_PIPELINE_SOURCE; a note webhook can pass AI_FLOW_INPUT/AI_FLOW_CONTEXT when a comment has @claude" }
liveness: none
emits: []
consequences:
  - when: "GitHub workflow runs (event or schedule)"
    expect: []
    evidence: "a GitHub Actions run on a GitHub-hosted runner; Claude posts comments / opens PRs as the GitHub App. Observable in the Actions tab + the PR/issue — NOT on company [[events]]. A `green` Actions run means the job ran, not that the task succeeded — read the PR/run"
  - when: "GitLab job runs"
    expect: []
    evidence: "a GitLab pipeline job on your runner; Claude proposes/updates an MR via mcp__gitlab. Observable in CI/CD → Pipelines + the MR — NOT company-side"
correlate: []
verification:
  github: {state: unverified, note: "no company face — native claude-code-action / /install-github-app"}
  gitlab: {state: unverified, note: "no company face — native .gitlab-ci.yml job"}
```
### Description (purpose-free)
Scaffold a CI integration. GITHUB ACTIONS: the quickest path is `/install-github-app` in the
terminal (repo admin only; direct Claude API only) — it installs the Claude GitHub App (Contents /
Issues / Pull-requests read & write), adds the `ANTHROPIC_API_KEY` repo secret, and copies a
workflow file. The action is `anthropics/claude-code-action@v1`, whose v1 GA auto-detects mode:
with no prompt on issue/PR comment events it responds to `@claude` mentions (interactive mode);
with a `prompt:` input on any event (e.g. `schedule:` cron, `pull_request`) it runs immediately
(automation mode). `claude_args` passes any CLI flag (`--max-turns`, `--model`, `--allowedTools`,
`--mcp-config`). GITLAB CI/CD (beta, GitLab-maintained, built on the CLI + Agent SDK): add a job
to `.gitlab-ci.yml` that installs the CLI and runs `claude -p "<prompt>" --permission-mode
acceptEdits --allowedTools "Bash Read Edit Write mcp__gitlab"`, plus a masked `ANTHROPIC_API_KEY`
variable; trigger on `$CI_PIPELINE_SOURCE` rules, manual runs, or a comment-note webhook passing
`AI_FLOW_*` variables. Both run on YOUR runners (your branch protection + approvals apply; changes
flow through PRs/MRs for review). None of this is a Company operation — it is external CI.
### Errors
```contract:error
code: ci.not-exposed | http: 501 | retryable: false
when: any attempt to scaffold or run a CI integration through a Company endpoint
teach: "The Company exposes no CI face. For GitHub, run `/install-github-app` (or manually install apps/claude, add the ANTHROPIC_API_KEY secret, copy examples/claude.yml). For GitLab, add a `claude` job to .gitlab-ci.yml with a masked ANTHROPIC_API_KEY. For Bedrock/Vertex use OIDC/WIF (no static keys). For durable cron WITHOUT CI infra, see [[routines]] (cloud routines) — and note a GitHub Actions `schedule:` trigger is the CI alternative to a scheduled routine."
```
```contract:error
code: ci.no-trigger-match | http: 400 | retryable: false
when: "Claude does not respond to @claude in CI"
teach: "Verify the GitHub App is installed, workflows are enabled, the API key secret is set, and the comment contains `@claude` (not `/claude`). On GitLab, confirm the pipeline is being triggered, CI/CD variables are present, and `mcp__gitlab` is in --allowedTools so the job can write comments/MRs (sources: github-actions.md / gitlab-ci-cd.md troubleshooting)."
```
```contract:example
captured: synthetic            # status=planned → synthetic legal AND loud (V11); GitHub Actions, the real model
binding: cli
request: |
  # .github/workflows/claude.yml — automation mode on a schedule (no @claude needed)
  name: Daily Report
  on:
    schedule:
      - cron: "0 9 * * *"
  jobs:
    report:
      runs-on: ubuntu-latest
      steps:
        - uses: anthropics/claude-code-action@v1
          with:
            anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
            prompt: "Generate a summary of yesterday's commits and open issues"
            claude_args: "--model opus"
response: |
  (NATIVE CI) GitHub Actions runs the job on its runner at 9am UTC; the action runs Claude Code
  with the prompt and posts the result. No company endpoint participates; the run is visible only
  in the Actions tab. (source: github-actions.md "Custom automation with prompts".)
```
```contract:example
captured: synthetic            # GitLab CI/CD — headless claude -p with mcp__gitlab
binding: cli
request: |
  # .gitlab-ci.yml (Claude API)
  claude:
    stage: ai
    image: node:24-alpine3.21
    rules:
      - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    before_script:
      - apk add --no-cache git curl bash
      - curl -fsSL https://claude.ai/install.sh | bash
    script:
      - /bin/gitlab-mcp-server || true
      - >
        claude -p "${AI_FLOW_INPUT:-'Review this MR and implement the requested changes'}"
        --permission-mode acceptEdits
        --allowedTools "Bash Read Edit Write mcp__gitlab"
    # ANTHROPIC_API_KEY comes from a masked CI/CD variable
response: |
  (NATIVE CI) The GitLab runner installs the CLI and runs headless `claude -p`; Claude proposes
  changes in a branch and opens/updates an MR via the mcp__gitlab tool. Branch protection and
  approvals apply. No company endpoint participates. (source: gitlab-ci-cd.md.)
```
Adjacent: [[ci#op: ci.act]] (trigger a run / @claude mention), [[routines]] (cloud cron + the
cloud GitHub-event trigger — the no-CI-infra alternative), [[git]] (the commits/PRs CI produces),
[[model]] (the `--model`/`use_bedrock`/`use_vertex` selection in CI).

## op: ci.act
**`ci.act` is the PLANNED in-CI invocation — mention `@claude` on an issue/PR/MR or fire a
prompt-driven run — none Company-wrapped; natively a `@claude` comment (auto-detected interactive
mode) or a CI event matching the workflow trigger.**
```contract:op
op: ci.act
resource: ci
kind: act
status: planned
direction: inbound
atlas: [CC-30.2]
tasks:
  - phrase: "ask Claude to implement this issue from a comment"
    params: {act: mention}
  - phrase: "have Claude fix a bug from a PR comment"
    params: {act: mention}
  - phrase: "trigger the CI Claude job on a merge request"
    params: {act: event}
  - alias: "@claude in a PR"
  - alias: "turn an issue into a PR via CI"
bindings:
  - { kind: http, method: COMMENT, path: "@claude <instruction>   (NATIVE — a GitHub/GitLab issue/PR/MR comment; the workflow's `if:` gate matches the mention)", transport: tui-interactive, exposure: "n/a — external CI provider", status: planned, note: "GAP: not a company face. The action auto-detects interactive mode from comment events; the trigger phrase defaults to `@claude` (configurable via trigger_phrase). On GitLab a note webhook forwards the mention as AI_FLOW_INPUT" }
  - { kind: http, method: EVENT, path: "a CI event (pull_request/push/schedule) matching the workflow trigger", transport: tui-interactive, exposure: "n/a — external CI provider", status: planned, note: "GAP: not a company face. Automation mode (a `prompt:` input) runs immediately on the event without a mention" }
liveness: none
direction-note: "direction:inbound — the CI PROVIDER drives this: it receives the repo event/comment, builds context, and invokes Claude Code on its runner. The 'contract the consumer implements' is the workflow/job file. No company face participates"
emits: []
consequences:
  - when: "@claude mention or matching event"
    expect: []
    evidence: "Claude analyzes the issue/PR, writes a branch, opens/updates a PR (GitHub) or MR (GitLab), and may leave inline comments. Observable in the PR/MR + the CI run — NOT company [[events]]"
correlate: []
verification:
  mention: {state: unverified, note: "no company face — native @claude / CI event"}
```
### Description (purpose-free)
Invoke an installed CI integration. Two shapes: a `@claude` mention in an issue, PR, or MR comment
(interactive mode — the action auto-detects it from comment events; the phrase defaults to
`@claude`, configurable) makes Claude analyze the context and respond (implement a feature, answer
an approach question, fix a bug); or a CI event matching the workflow trigger (a `pull_request`, a
`schedule:` cron, a manual/web run) drives an automation-mode run with a fixed `prompt:`. Either
way the run happens on the CI provider's runner under the CI identity, and changes arrive as a PR
or MR for review under your branch protection. The Company drives none of it; this is the inverse
of the Company's own out-bound [[events]] stream — here an external provider pushes work IN to the
CI runner, not to a Company session.
### Errors
```contract:error
code: ci.no-trigger-match | http: 400 | retryable: false
when: a mention/event does not start a run
teach: "Confirm the comment contains `@claude` (not `/claude`), the GitHub App/workflow is enabled, and the secret is set; on GitLab confirm the pipeline triggers and mcp__gitlab is in --allowedTools. CI not running on Claude's own commits usually means the Actions user (not the App) authored them — use the App/custom-app identity (github-actions.md troubleshooting)."
```
```contract:example
captured: synthetic            # status=planned → synthetic legal AND loud (V11)
binding: http
request: |
  (a comment on a GitHub PR)
  @claude fix the TypeError in the user dashboard component
response: |
  (NATIVE CI) The workflow's `if:` condition matches the @claude mention, the action runs Claude
  Code on a runner; Claude locates the bug, implements a fix, and pushes to the branch / opens a
  PR as the GitHub App. No company endpoint participates.
```
Adjacent: [[ci#op: ci.create]] (scaffold the integration first), [[git]] (the resulting commits/
PRs/MRs), [[routines]] (the cloud GitHub-event trigger alternative that needs no CI runner),
[[permission]] (the `--permission-mode` the CI job runs under).

## Errors
**Resource-level vocabulary: `ci.not-exposed` (the honest 501 for any Company CI endpoint),
`ci.no-trigger-match` (the native mention/event mis-fire condition).** Each teaches the real
native recovery (install the App / add the GitLab job / check the trigger), and the cron-class
errors redirect to [[routines]] for the no-CI-infra alternative. No error claims a Company CI
service (verified 2026-06-12: no github-actions/gitlab/ci surface in `ops/cli/`, `runtime/`, or
`mcp_face/`).

## Links
**No address-typed fields resolve to a Company entry: a CI integration lives in the consumer's
repo (`.github/workflows/` / `.gitlab-ci.yml`) and runs on the CI provider's infrastructure, and
its outputs are PRs/MRs/comments in the provider's UI — none are Company addresses or
[[events]].** The in-corpus relations are conceptual and dereferenceable: [[routines]] (the cloud
GitHub-event trigger overlaps CI's `@claude` model but needs no runner; the cloud `schedule`
trigger is the routine analogue of a GitHub Actions `schedule:`), [[git]] (the commits/branches/
PRs the CI run produces), [[model]] (the `--model` / `use_bedrock` / `use_vertex` selection inside
the CI job), and [[permission]] (the `--permission-mode` the autonomous CI job runs under).
