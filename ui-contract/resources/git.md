---
type: contract-entry
resource: git
summary: Claude Code's git surface — automatic git context in every session, commit/branch/PR/rebase/stash via the Bash tool, PR-linked resume (--from-pr), and isolated parallel worktrees (--worktree / -w, the EnterWorktree tool, .worktreeinclude, worktree.baseRef, WorktreeCreate/Remove hooks for non-git VCS). The Company exposes no dedicated git face; the supervisor's spawn cwd/fork params are the real adjacent seam, and the build's own commit-to-main law is documented for honesty.
schemes: []
status: planned
relates-to: ["[[session]]", "[[permission]]", "[[ci]]", "[[agent-team]]"]
---

# Resource: git

## Identity
**The git surface is identified by the working directory a session runs in (`cwd`) and, for
isolation, by a worktree path (`.claude/worktrees/<name>/` on branch `worktree-<name>` by
default) — there is no `git://` scheme and no standalone git record, because git is operated
THROUGH a session's Bash tool and CLI launch flags, not as an addressable Company object.**
Claude Code carries automatic git context into every session (current branch, uncommitted
changes, recent commits) and runs git via Bash; worktrees are a launch-time and in-session
isolation mechanism (https://code.claude.com/docs/en/worktrees.md). This entry contracts those
native capabilities so a UI can present them, and names per op that the Company wraps none of
them — the closest real seam is the supervisor spawn's `cwd`/`fork` parameters
([[session#op: session.create]]).

## Representation
**Two layers: (1) GIT OPERATIONS — commit, branch, PR, rebase/merge/cherry-pick, stash — which
Claude performs by emitting `git`/`gh` commands through the Bash tool (gated by [[permission]]),
and (2) WORKTREE ISOLATION — a separate working directory + branch sharing the repo's history,
so parallel sessions/subagents never collide on file edits.** A worktree is the structural unit
a UI must model; git operations are just Bash calls under a permission posture.

```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/git.worktree",
  "type": "object",
  "description": "A worktree as the native CLI models it. NOT a company record — no company endpoint returns this; fields mirror worktrees.md.",
  "properties": {
    "name":    { "type": "string", "description": "the worktree value; if omitted, Claude generates one like `bright-running-fox`" },
    "path":    { "type": "string", "description": "default `.claude/worktrees/<name>/` at the repo root; relocate via a WorktreeCreate hook" },
    "branch":  { "type": "string", "description": "default `worktree-<name>` (new branch); or `pr-<number>` when created from a PR (`--worktree \"#1234\"` fetches pull/<number>/head)" },
    "baseRef": { "enum": ["fresh", "head"], "description": "worktree.baseRef setting: `fresh` (default) branches from origin/HEAD (clean, matches remote; falls back to local HEAD if no remote); `head` branches from local HEAD (carries unpushed commits / feature-branch state). Accepts ONLY these two values, not arbitrary refs" },
    "isolation_source": { "enum": ["--worktree", "EnterWorktree", "subagent", "desktop-auto"], "description": "--worktree/-w at launch; the EnterWorktree tool mid-session; `isolation: worktree` subagent frontmatter; the desktop app auto-creates one per new session" } } }
```
| field | type | volatile? | changed-by | address? → resource | reality (2026-06-12) |
|---|---|---|---|---|---|
| git context (branch, uncommitted, recent commits) | — | yes | every session start + each git op | — | NATIVE: surfaced into every session automatically (how-claude-code-works.md); NO company endpoint returns it |
| commit / branch / PR / rebase / stash | — | yes | Claude's Bash tool calls (`git …`, `gh pr …`) | — | NATIVE: performed via Bash under [[permission]]; the Company spawns headless `claude -p` (which CAN run these), but exposes no dedicated git op |
| worktree | object | yes | `--worktree`/`-w`, EnterWorktree tool, subagent isolation, desktop auto | — | NATIVE: `.claude/worktrees/<name>/`; cleanup depends on changes (see Operations). NO company worktree face |
| company self-build worktree | — | yes | the build loop's own `_git_self_commit` (runtime/suite.py:8430-8644) | — | INTERNAL to the Company's recursive self-build (commits its own changed_delta to its OWN tree, `git revert <sha>`-undoable) — NOT a consumer git face; documented for honesty (this is the Company building ITSELF, not offering git to a UI) |

## State model
**State model: stateless** (the Company holds no git state). A worktree has a native disk
lifecycle documented inline: created (launch/EnterWorktree/subagent/desktop) → live (locked via
`git worktree lock` while an agent runs, so concurrent cleanup can't remove it) → cleaned up on
exit (auto-removed if no uncommitted changes / untracked files / new commits AND unnamed;
prompt-to-keep if named or dirty; subagent/background worktrees swept after `cleanupPeriodDays`;
`--worktree` worktrees never auto-swept; `-p` runs never auto-cleaned — remove with
`git worktree remove`). None of these transitions is observable through a Company endpoint.

## Caller
**Git operations run as the session's identity at the session's `cwd` under its [[permission]]
posture — there is no separate git caller, and the Company adds none.** Commits carry the git
config `user.name`/`user.email` of the environment the session runs in (in CI, the GitHub
App/custom-app identity — see [[ci#Caller]]); co-author attribution is available but is disabled
by a hook in THIS operator's setup (the Company's commit law: commit to main, no Co-Authored-By
trailer — a build-side convention, not a consumer-facing git policy). Worktree creation needs the
workspace trust dialog accepted first when interactive (`--worktree` errors and prompts you to run
`claude` once in the dir); `claude -p --worktree` skips the trust check.

## Operations

## op: git.act
**`git.act` is the PLANNED named git steer (commit / branch / open-PR / resume-from-PR) — the
Company wraps none; natively Claude does these through the Bash tool inside a session under a
permission posture, and PR-linked resume is a launch flag (`--from-pr`).**
```contract:op
op: git.act
resource: git
kind: act
status: planned
direction: outbound
atlas: [CC-06.1, CC-06.2]
tasks:
  - phrase: "commit my changes with a descriptive message"
    params: {act: commit}
  - phrase: "create a pull request for this feature"
    params: {act: open-pr}
  - phrase: "resume the session linked to PR 456"
    params: {act: resume-from-pr, pr: 456}
  - phrase: "rebase this branch onto main"
    params: {act: rebase}
  - alias: "make a commit"
  - alias: "open a PR"
  - alias: "switch branches"
bindings:
  - { kind: cli, command: "(in-session) > commit my changes   — Claude emits `git add`/`git commit` via the Bash tool under [[permission]]", transport: tui-interactive, exposure: "n/a — interactive", status: planned, note: "GAP: no dedicated company git op. Native git context is automatic; ops are Bash calls. The Company supervisor spawns `claude -p` which CAN run git, but exposes no git verb" }
  - { kind: cli, command: "claude --from-pr <number|url>   (NATIVE — resume a session linked to a PR)", transport: tui-interactive, exposure: "n/a — interactive", status: planned, note: "GAP: a launch flag, not a company op. The Company's spawn (runtime/session_supervisor.py:254) takes cwd/resume/fork/name/source ONLY — no --from-pr passthrough" }
  - { kind: cli, command: "gh pr create / git branch / git rebase   — via the Bash tool", transport: tui-interactive, exposure: "n/a — interactive", status: planned, note: "GAP: PR creation needs the GitHub CLI/App in the session env; rebase/merge/cherry-pick/stash are plain git through Bash. None company-wrapped" }
liveness: none
emits: []
consequences:
  - when: "commit / PR (in a supervised company session)"
    expect: [agent_sessions.turn]
    bound: "the git command runs inside a turn; the turn event fires per [[session#op: session.post]]'s bounds. The git RESULT (sha, PR url) is in the turn's transcript, NOT a structured company field"
    evidence: "[[session#op: session.watch]] (the turn's text/tool frames carry the git output); there is no company `git.result` event — the outcome is behavioural/transcript-shaped"
correlate: [session]
verification:
  git-ops: {state: unverified, note: "no company git face — native Bash git under [[permission]]"}
```
### Description (purpose-free)
The everyday git workflow a session performs: stage and commit with a generated message, create a
branch, open a PR (descriptions generated from the actual diff), rebase/merge/cherry-pick, stash.
Claude has automatic git context (branch, uncommitted changes, recent commits, history for
project patterns) and performs operations by emitting commands through the Bash tool, so every
git op is gated by the session's [[permission]] posture (a `plan`-mode session plans the commit
but routes the actual write to approval; `acceptEdits`/`dontAsk`/`bypassPermissions` change that —
see [[permission#Interaction semantics]]). PR-linked resume (`--from-pr`) is a launch flag that
ties a new session to an existing PR. None of this is a Company operation; the Company's only
adjacent real lever is the spawn `cwd` (which working tree the headless session runs in).
### Errors
```contract:error
code: git.not-exposed | http: 501 | retryable: false
when: any git operation requested through a dedicated Company endpoint
teach: "The Company has no git verb. Git runs inside a session via the Bash tool under its [[permission]] posture (a `plan`-mode session won't auto-commit). To spawn a session in a chosen working tree, use [[session#op: session.create]] `cwd`. PR-linked resume is the native `claude --from-pr <n>` launch flag. For CI-triggered git (PR/MR creation on repo events) see [[ci]]."
```
```contract:example
captured: synthetic            # status=planned → synthetic legal AND loud (V11)
binding: cli
request: |
  > commit my changes with a descriptive message and open a PR
response: |
  (NATIVE, in-session) Claude reads the diff, runs `git add`/`git commit` and `gh pr create`
  through the Bash tool (each subject to the session's permission mode), and reports the sha +
  PR URL in the transcript. No company git endpoint participates; in a supervised company
  session the only company-visible signal is the agent_sessions.turn event (the git result
  rides the turn transcript, not a structured field).
```
Adjacent: [[git#op: git.worktree]] (isolation), [[session#op: session.create]] (the spawn `cwd`
seam), [[permission]] (what gates the Bash git calls), [[ci]] (CI-triggered git).

## op: git.worktree
**`git.worktree` is the PLANNED isolation steer — create/enter/clean an isolated git worktree so
parallel sessions and subagents never collide on file edits; natively `--worktree`/`-w` at launch,
the `EnterWorktree` tool mid-session, `isolation: worktree` subagent frontmatter, or `git worktree`
directly — the Company drives none, though it IS the Company's own self-build isolation mechanism
internally.**
```contract:op
op: git.worktree
resource: git
kind: act
status: planned
direction: outbound
atlas: [CC-06.3, CC-06.4]
tasks:
  - phrase: "run this session in an isolated worktree so it doesn't collide with my main checkout"
    params: {act: create}
  - phrase: "work in a worktree"
    params: {act: enter}
  - phrase: "isolate my subagents in their own worktrees"
    params: {act: subagent-isolate}
  - phrase: "branch a worktree from a specific PR"
    params: {act: create, base: "#1234"}
  - phrase: "clean up a worktree when I'm done"
    params: {act: remove}
  - alias: "parallel session isolation"
  - alias: "create a git worktree"
bindings:
  - { kind: cli, command: "claude --worktree <name>   (or -w; omit name to auto-generate)   (NATIVE)", transport: tui-interactive, exposure: "n/a — interactive", status: planned, note: "GAP: no company face. Default `.claude/worktrees/<name>/` on branch `worktree-<name>`; base = worktree.baseRef (`fresh`=origin/HEAD default, `head`=local HEAD). `#1234` or a PR URL branches from pull/<n>/head into `.claude/worktrees/pr-<n>`. Trust dialog required when interactive; `claude -p --worktree` skips it" }
  - { kind: cli, command: "EnterWorktree(name|path)   (NATIVE in-session tool — 'work in a worktree'; switch between worktrees under .claude/worktrees/)", transport: tui-interactive, exposure: "n/a — interactive", status: planned, note: "GAP: a Claude Code tool, not a company op. Switching leaves the previous worktree on disk untouched" }
  - { kind: cli, command: "subagent frontmatter `isolation: worktree`   (NATIVE — each subagent gets a temp worktree, auto-removed if it finishes without changes)", transport: agent-sdk, exposure: "n/a — Agent SDK in-process", status: planned, note: "GAP: a subagent config; relates to [[agent-team]]. Uses the same baseRef as --worktree" }
  - { kind: cli, command: "git worktree add/list/remove   (NATIVE git — full manual control)", transport: tui-interactive, exposure: "n/a — interactive", status: planned, note: "GAP: plain git via Bash. `git worktree remove --force` for a dirty/locked one. While an agent runs, Claude holds `git worktree lock` so cleanup can't remove it" }
liveness: none
emits: []
consequences:
  - when: "worktree created"
    expect: []
    evidence: "a new directory `.claude/worktrees/<name>/` on a new branch; the session starts in it. Cleanup on exit depends on changes (see [[git#State model]]). NO company event — worktree creation is a local FS/git act, not supervisor-spawned"
  - when: "company self-build (internal, NOT a consumer op)"
    expect: []
    evidence: "the build loop commits its own changed_delta path-scoped to its tree (runtime/suite.py:8430+); this is the Company editing ITSELF and is out of scope as a consumer capability — named here only so a UI never mistakes it for a git service"
correlate: []
verification:
  worktree: {state: unverified, note: "no company face — native --worktree / EnterWorktree / git worktree"}
```
### Description (purpose-free)
Isolate parallel work. A git worktree is a separate working directory with its own files and
branch that shares the repo's history and remote, so edits in one session never touch another's —
one terminal builds a feature, a second fixes a bug, no collision. Created at launch with
`--worktree`/`-w` (default location `.claude/worktrees/<name>/`, branch `worktree-<name>`,
relocatable via a `WorktreeCreate` hook), mid-session via the `EnterWorktree` tool ("work in a
worktree"), per-subagent via `isolation: worktree` frontmatter, or directly with `git worktree`.
Base branch is governed by `worktree.baseRef` (`fresh` = clean from origin/HEAD, the default;
`head` = local HEAD, carrying unpushed work — useful when isolating subagents that need in-progress
state). A `.worktreeinclude` file (`.gitignore` syntax) copies gitignored-but-needed files (e.g.
`.env`) into each fresh worktree. For non-git VCS (SVN/Perforce/Mercurial), `WorktreeCreate`/
`WorktreeRemove` hooks replace the default git logic (and disable `.worktreeinclude`). Worktrees
isolate FILES; coordinating the WORK across them is [[agent-team]] / subagents / the consult-fan
([[workflows]], [[session#op: session.post]]). The Company drives none of this for consumers,
though worktree isolation is exactly how the Company's own recursive self-build keeps its parallel
build lanes from colliding (internal — note the no-branches-in-~/company law means the build
commits to main, NOT to per-lane branches).
### Errors
```contract:error
code: git.worktree-not-exposed | http: 501 | retryable: false
when: any worktree operation requested through a Company endpoint
teach: "The Company has no worktree face. Create one natively: `claude --worktree <name>` (or ask 'work in a worktree' to use the EnterWorktree tool), set `isolation: worktree` on a subagent, or `git worktree add` directly. To spawn a supervised session in an already-created worktree path, pass it as [[session#op: session.create]] `cwd`. To coordinate work across worktrees, see [[agent-team]] and [[workflows]]."
```
```contract:error
code: git.worktree-trust-required | http: 403 | retryable: false
when: "`--worktree` used interactively in a directory whose workspace-trust dialog hasn't been accepted"
teach: "Run `claude` once in the directory and accept the trust dialog first; then `--worktree` works. Non-interactive `claude -p --worktree` skips the trust check (source: https://code.claude.com/docs/en/worktrees.md)."
```
```contract:example
captured: synthetic            # status=planned → synthetic legal AND loud (V11)
binding: cli
request: |
  claude --worktree feature-auth
response: |
  (NATIVE) Claude creates `.claude/worktrees/feature-auth/` on a new branch `worktree-feature-auth`
  (branched from origin/HEAD unless worktree.baseRef="head") and starts the session in it. On exit,
  a clean unnamed worktree is auto-removed; a named or dirty one prompts to keep/remove. No company
  endpoint participates.
```
Adjacent: [[git#op: git.act]] (commit/PR inside the worktree), [[session#op: session.create]]
(`cwd` = the seam to spawn a supervised session in a worktree), [[agent-team]] (coordinate
parallel isolated agents), [[workflows]] (the consult-fan parallel primitive).

## Errors
**Resource-level vocabulary: `git.not-exposed` / `git.worktree-not-exposed` (the honest 501 for
both layers) and `git.worktree-trust-required` (the native interactive trust gate).** Every code
teaches the native recovery and points at the one real adjacent Company lever — the spawn `cwd`
of [[session#op: session.create]]. No error claims a Company git service (verified 2026-06-12:
no git/worktree noun in `ops/cli/`; the only `git`/`worktree` references in `runtime/` are the
Company's OWN self-build self-commit, not a consumer face).

## Links
**No address-typed fields resolve to a Company entry: git operations act on a `cwd` (a filesystem
path, not a Company address) and worktrees are local `.claude/worktrees/` directories.** The
dereferenceable in-corpus relations are the seams: [[session#op: session.create]] accepts `cwd`
(spawn in a chosen tree) and `fork=true` (the Company's fork-a-session analogue of branching, see
[[session]] — distinct from a git worktree), [[permission]] gates the Bash git calls, [[ci]]
holds the CI-provider git (PR/MR creation on repo events), and [[agent-team]] coordinates the work
that worktrees isolate.
