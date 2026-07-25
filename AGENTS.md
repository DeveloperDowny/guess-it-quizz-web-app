## Project  Intent

- I've built a quizz app whose kiro artifacts can be found at `D:\DMisc\quizz-web-app\quizz-cli-app\quizz\.kiro`
- I've built a notebook orchestrator `quizz-cli-app\quizz-cli-app.ipynb` which helps player play the quizz app on Google colab notebook easily. The kiro artifacts for the same can be found at `D:\DMisc\quizz-web-app\quizz-cli-app\.kiro`
- The intent of the project is to build a client + server orchestrator so that users can play the quizz game via website

## Project Preference

- vite + react + tailwind for frontend
- FastAPI + uv + uv_build + pydantic v2 + google cloud run + google cloud firebase for the backend
- Use uv and uv_build for dependency management, packaging, and build workflows across the project

# AGENTS.md — Spec-Driven Development (Kiro-style workflow)

This file configures any AGENTS.md-compatible coding agent (Claude Code, Cursor,
Codex CLI, etc.) to follow Kiro's spec-driven development methodology: structured
context via "steering" documents, and a three-phase Requirements → Design → Tasks
workflow before any implementation code is written.

---

## 1. Project Context: Steering Documents

Before starting any nontrivial work, load or generate persistent project context
from `.kiro/steering/`. If these files don't exist yet, create them by analyzing
the existing codebase (or asking the user, for a greenfield project).

```
.kiro/
  steering/
    product.md      # Business context: what the product does, who it's for, key requirements
    tech.md          # Technical stack: languages, frameworks, libraries, conventions, constraints
    structure.md      # Codebase architecture: directory layout, module boundaries, naming patterns
```

Rules:

- Always read all three steering files at the start of a session, if present.
- Keep steering files in sync with reality — update them when the stack or
  architecture materially changes, but don't rewrite them for every small edit.
- Steering files are the agent's "long-term memory" for the project. Prefer
  referencing them over re-deriving the same context from scratch each session.
- Additional steering files (e.g. `security.md`, `testing.md`) may be added for
  domain-specific standing context; include them in the same directory.

---

## 2. Specs: The Core Workflow

For any new feature, non-trivial change, or bug fix, do **not** jump straight to
code. Create a spec: a folder of markdown artifacts that captures intent before
implementation.

```
.kiro/
  specs/
    {feature-name}/
      requirements.md
      design.md
      tasks.md
```

Use a short, kebab-case `{feature-name}` derived from the user's request
(e.g. `user-authentication`, `csv-export`).

### 2.1 Workflow variants

Choose the variant that matches the situation:

- **Requirements-First** (default): Requirements → Design → Tasks. Start from
  desired system behavior.
- **Design-First**: Design → Requirements → Tasks. Use when the user already has
  a technical architecture in mind, or for brownfield work where the design is
  constrained by existing systems.
- **Bugfix**: Use `bugfix.md` instead of `requirements.md`, capturing current
  behavior, expected behavior, and what must remain unchanged. Then proceed to
  `design.md` (root cause + fix approach) and `tasks.md`.
- **Quick Plan**: For small, well-understood changes, generate all three
  artifacts in one pass without stopping for approval between phases. Still
  produce the files — just skip the gates. Reserve this for cases where the
  scope is genuinely low-risk.

### 2.2 Phase 1 — Requirements

Write `requirements.md` using **EARS notation** (Easy Approach to Requirements
Syntax) for testable acceptance criteria. Structure:

```markdown
# Requirements: {Feature Name}

## Introduction

Brief summary of the feature and why it's needed.

## Requirements

### Requirement 1: {Short name}

**User Story:** As a {role}, I want {capability}, so that {benefit}.

#### Acceptance Criteria

1. WHEN {condition/event} THE SYSTEM SHALL {expected behavior}
2. WHEN {condition/event} THE SYSTEM SHALL {expected behavior}
3. IF {precondition} THEN THE SYSTEM SHALL {expected behavior}

### Requirement 2: {Short name}

...
```

EARS patterns to use:

- `WHEN [trigger] THE SYSTEM SHALL [response]` — event-driven behavior
- `IF [precondition] THEN THE SYSTEM SHALL [response]` — conditional behavior
- `WHILE [state] THE SYSTEM SHALL [response]` — state-driven behavior
- `THE SYSTEM SHALL [behavior]` — ubiquitous (always-true) requirements

Stop and present `requirements.md` to the user for approval before proceeding.
Do not move to design until the user confirms the requirements are correct, or
explicitly asks to skip ahead (Quick Plan).

### 2.3 Phase 2 — Design

Write `design.md` documenting the technical approach:

```markdown
# Design: {Feature Name}

## Overview

High-level summary of the technical approach.

## Architecture

Components, their responsibilities, and how they interact.
Include a diagram (mermaid or ASCII) where it clarifies data flow.

## Components and Interfaces

Concrete interfaces, function signatures, types/schemas, API endpoints.

## Data Models

Database schemas, data structures, state shapes.

## Error Handling

Failure modes and how each is handled.

## Testing Strategy

What will be tested and how (unit, integration, e2e).

## Implementation Considerations

Tradeoffs, alternatives considered, open questions.
```

Design must trace back to the requirements it satisfies. Flag any requirement
that turns out to be infeasible or ambiguous rather than silently reinterpreting
it. Stop and present `design.md` for approval before proceeding.

### 2.4 Phase 3 — Tasks

Write `tasks.md` as a discrete, trackable, dependency-ordered checklist:

```markdown
# Implementation Plan: {Feature Name}

- [ ] 1. {Task title}
  - {Sub-step or detail}
  - {Sub-step or detail}
  - _Requirements: 1.1, 1.2_

- [ ] 2. {Task title}
  - _Requirements: 2.1_
  - _Depends on: 1_

- [ ] 2.1 {Sub-task title}
  - _Requirements: 2.1_
```

Rules:

- Each task should be small enough to implement and verify independently.
- Each task references the requirement(s) it fulfills.
- Note dependencies between tasks explicitly (`_Depends on: N_`) so independent
  tasks can be identified.
- Tasks with no unmet dependencies can be treated as parallelizable; tasks with
  dependencies run only after their prerequisites are marked complete.

Stop and present `tasks.md` for approval before implementing.

---

## 3. Implementation

Once a spec is approved:

1. Work through `tasks.md` **one task at a time**, top to bottom respecting
   dependencies — do not silently batch unrelated tasks together.
2. Before implementing a task, re-read the relevant sections of `requirements.md`
   and `design.md` so the implementation matches documented intent rather than
   improvising.
3. After completing a task, mark it done in `tasks.md`:
   - `[ ]` → not started
   - `[-]` → in progress
   - `[x]` → complete
4. If implementation reveals that a requirement or design decision was wrong or
   incomplete, stop and update `requirements.md` / `design.md` first, then
   propagate the change to `tasks.md`, rather than quietly diverging from the
   spec in code.
5. Do not start unrelated new specs mid-implementation without finishing or
   explicitly pausing the current one.

---

## 4. Keeping Specs in Sync

Specs are living documents, not one-time scaffolding:

- **Requirement changes:** edit `requirements.md` directly, or describe the
  change and regenerate the affected sections.
- **Design changes:** edit `design.md`; if the change affects scope, regenerate
  `tasks.md` to add/remove/modify tasks accordingly (a "sync" pass).
- **Never** let `tasks.md` drift out of alignment with `requirements.md` /
  `design.md` — if one changes in a way that invalidates a task, update the task
  list in the same turn.

---

## 5. Operating Rules Summary

- Steering docs (`product.md`, `tech.md`, `structure.md`) = durable project
  context, loaded every session.
- Specs (`requirements.md`, `design.md`, `tasks.md`) = per-feature planning
  artifacts, created before code.
- Default to the three-phase gated workflow (Requirements → Design → Tasks →
  Implementation) with user approval between phases.
- Use Quick Plan only for small, well-understood changes, and say so explicitly
  when doing it.
- Use the Bugfix variant (`bugfix.md`) for defect fixes instead of
  `requirements.md`.
- Never generate code before a spec exists for nontrivial work — this is the
  core discipline that distinguishes this workflow from ad hoc "vibe coding."
- All spec and steering files are plain markdown, checked into the repo under
  `.kiro/`, so they're versioned, diffable, and reviewable like code.

---

## 6. Note on Agent Hooks

Kiro also supports **Agent Hooks**: event-driven automations (e.g., "on file
save, update tests") configured through its IDE UI. That mechanism is IDE-specific
and can't be faithfully replicated in a plain AGENTS.md file. If your agent
supports comparable automation (file-watch triggers, CI hooks, custom slash
commands), configure those separately — this file only covers the portable
spec-driven workflow and steering-context conventions.
