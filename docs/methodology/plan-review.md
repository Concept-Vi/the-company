---
name: plan-review
description: "Iterative multi-agent plan review. Write the plan to a file, send agents to discover what matters, build findings back in. Each round deepens. Use when you've written an implementation plan."
---

# Plan Review

**Trigger**: After writing an implementation plan to a file. Proactively use this before implementing any non-trivial plan.

**Core principle**: The plan file is the living document. Agents are sent to it. Their findings go back into it. Multiple rounds, each from a different angle. The document grows in structural accuracy with each pass.

## The Process

### 1. Write the plan to a persistent file

The plan MUST exist as a file, not just in conversation. Write it to the memory directory or a blueprint location. This is the artifact agents will read, and findings will be written back to.

### 2. Send agents to the file

Point each agent at:
- The plan file (primary)
- The surrounding directory (for patterns and context they find themselves)
- The actual source files the plan references

**DO NOT**:
- Tell agents what to look for
- Give them queries or search terms
- Provide examples of what they might find
- List optional questions
- Prescribe specifics

**DO**:
- Point them at the file
- Point them at the source
- Say "report what you find"

The agent discovers what matters. If you prescribe, you only get back what you already knew.

### 3. Build findings into the plan file

After each agent returns:
- Add confirmed references to a verification table
- Add discovered issues to the relevant sections
- Add new sections for structural findings
- Update the review history at the bottom
- Increment the round counter

The plan file accumulates evidence. Nothing is lost between rounds.

### 4. Send the next round from a different angle

Each round uses a different perspective:

**Round pattern** (adapt to context, not rigid):
- **Round 1**: Code reviewer — verify references, find what the plan missed in the source
- **Round 2**: Code reviewer or specialist — trace unification, how systems meet at the plan's proposed join points
- **Round 3**: Generalists in parallel — end-to-end flows through the actual code. Multiple agents, each tracing a different path
- **Round N**: As needed — adversarial review, edge cases, integration points
- **Design round (mandatory if the plan has ANY operator-facing surface)**: a design-critic checks the plan's FORM half — does every surface criterion name the design system's components + tokens (not bespoke), is there a Product Face group, does the verification section prescribe the design rubric + a separate design-critic + a design-lint? The AI default is a function-only plan; this round catches a plan that specs *what works* but never *what it looks/feels like* or *what it's built on*. Findings go back into the plan as FORM criteria. (See loop-prep principle 9 + AGENTS.md rule 9.)

Different agent types see different things. Reviewers find structural issues. Generalists find flow issues. Specialists find domain issues. A design-critic finds the missing form half.

### 5. Know when to stop

The plan is ready when:
- New rounds confirm what previous rounds found (convergence)
- No new structural issues emerge
- The file has enough verified evidence that an agent reading it cold could implement without the conversation

## What the plan file should contain after review

- **Source verification table**: Every code reference checked against actual source, with line numbers and status
- **Structural sections**: How the systems actually work (discovered, not assumed)
- **Implementation steps**: Updated with findings from each round
- **Pre-existing issues**: Things discovered that aren't caused by the plan but affect it
- **Review history**: What each round found, what changed, traceable decisions

## Anti-patterns

- Sending the same type of agent twice with the same prompt
- Telling agents "look for X" instead of "report what you find"
- Not building findings back into the file between rounds
- Implementing before the rounds converge
- Keeping findings only in conversation instead of the file
