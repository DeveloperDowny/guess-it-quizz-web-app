# Design: Browser Quiz Platform

## Overview

The browser platform will expose the current quiz experience through a thin React frontend and a FastAPI backend. The backend will reuse the existing Python quiz package rather than reimplementing the rules in the UI layer.

The implementation will preserve the current YAML contract, the validator behavior in the domain models, and the exact-match scoring semantics already used by the CLI workflow.

## Architecture

```text
Browser UI (React + Tailwind)
  -> FastAPI REST API
    -> SessionService
      -> QuestionSetService / YAML loader
      -> Existing quiz domain services (PlayerService, JudgeService)
      -> SessionStore (file-backed or in-memory repository)
```

### High-level responsibilities

- Frontend: render the session creation/join flow, collect answers for both perspectives, and display judge results.
- Backend: own session orchestration, persistence, answer validation, and scoring.
- Shared quiz package: remain the source of truth for validation, question parsing, answer-sheet structure, and match scoring.

## Components and Interfaces

### Frontend

- SessionStartView
  - Lets player 1 create a session and choose a question set.
  - Lets player 2 join an existing session via a session ID.
- PlayerFlowView
  - Presents the current question set and collects answers for both self and impersonation perspectives in one browser flow.
  - Uses browser-side session storage to keep the current session identifier available across refreshes.
- JudgeView
  - Requests completed session results and renders score totals plus a per-question breakdown.

### Backend API

- POST /api/sessions
  - Creates a new session for player 1.
  - Accepts a selected question set identifier and optional player metadata.
  - Returns the session ID and initial session state.
- GET /api/sessions/{session_id}
  - Returns the current session state, including status and available question-set metadata.
- GET /api/sessions/{session_id}/questions
  - Returns the question set snapshot bound to the session.
- POST /api/sessions/{session_id}/answers
  - Accepts one or more answer entries for the current player and perspective.
  - Validates values against the session's question options.
- GET /api/sessions/{session_id}/judge
  - Returns the scored result for the completed session.

### Backend services

- SessionService
  - Creates, joins, resumes, and completes sessions.
  - Stores session state and binds each session to the question set it started with.
- QuestionSetService
  - Scans the questions directory for <question-set-id>.yaml files.
  - Loads and validates the selected YAML question set at startup or on demand.
  - Exposes question-set metadata for selection in the UI using the filename-derived identifier.
- QuizAdapter
  - Wraps the existing domain models and services so the web backend reuses the same validation and scoring logic.

## Data Models

### Session record

```text
SessionRecord {
  id: string
  created_by: string
  joined_by: string | null
  status: "created" | "in_progress" | "completed" | "judged"
  question_set_id: string
  question_set_snapshot: QuestionSet
  player_answers: map[string, AnswerSheet]
  impersonation_answers: map[string, AnswerSheet]
  judge_result: JudgeResult | null
}
```

### Question-set configuration

- The backend will read question sets from a questions directory containing one YAML file per question set in the format <question-set-id>.yaml.
- The question-set identifier will be derived from the filename and used for selection, session binding, and UI display.
- A configured question set is loaded from YAML at startup.
- Each session stores a snapshot of the selected question set and the question-set identifier.
- New sessions use the currently active question set, while existing sessions remain bound to the snapshot they started with.

## Reuse Strategy for Existing Quiz Logic

The browser platform will import and reuse the existing quiz package modules directly:

- Domain models from the quiz package for questions, answer sheets, and validation
- YAML repository behavior for loading questions and persisting answer sheets
- PlayerService for answer validation and sheet assembly
- JudgeService for exact-match scoring and per-question reviews

This keeps the web app thin and avoids duplicating business rules in the frontend.

## Error Handling

- Invalid YAML payloads will be rejected during backend startup or session creation with clear validation errors.
- Invalid answer selections will return HTTP 400 and will not be persisted.
- Unknown session IDs will return HTTP 404.
- Refresh and reopen flows will recover the existing session from the backend store using the persisted session ID.
- Missing answer data for a judged session will return a friendly validation error instead of silently scoring a partial session.

## Testing Strategy

- Unit tests for SessionService and the quiz adapter to verify session lifecycle behavior and scoring reuse.
- API tests for session creation, answer submission, resume, and judging endpoints.
- Frontend component tests for the start/join flow, answer entry, and judge results rendering.
- Compatibility tests using the existing YAML fixtures to ensure the current question format remains supported.

## Implementation Considerations

- The initial implementation can use a file-backed session store for persistence during development and local testing.
- The storage layer should be abstracted behind a repository interface so it can later be replaced with Firebase, Redis, or a database without changing the API contract.
- The frontend should not validate quiz rules independently; it should rely on backend responses so the rules remain centralized.
