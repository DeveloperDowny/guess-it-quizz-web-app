# Implementation Plan: Browser Quiz Platform

- [x] 1. Establish the web backend foundation
  - Create the FastAPI application structure, dependency wiring, and initial API routes for sessions and health checks.
  - Define the session and question-set models used by the API contract.
  - _Requirements: 0.1, 0.2, 0.3, 0.4, 0.5, 4.1, 4.2_

- [x] 2. Reuse the existing quiz engine in the backend
  - Adapt the existing domain models, YAML loading, answer validation, and scoring logic into backend-facing services.
  - Ensure the backend uses the same question schema, answer schema, and match-scoring semantics as the CLI package.
  - _Requirements: 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 4.3, 4.4_

- [x] 3. Implement session lifecycle and persistence
  - Add session creation, join-by-ID, resume, answer submission, and completion flows.
  - Persist session state server-side so refreshes and reopen flows can recover the same session.
  - _Requirements: 0.1, 0.2, 0.3, 0.4, 0.5, 1.3, 3.4_
  - _Depends on: 1, 2_

- [x] 4. Load and validate question sets for gameplay
  - Add backend discovery of question-set files from the questions directory using the <question-set-id>.yaml naming convention.
  - Load the selected YAML question set and reject invalid payloads before the game starts.
  - Keep sessions bound to the question set they started with, even if a new active set is configured later.
  - _Requirements: 3.1, 3.2, 3.3, 3.4_
  - _Depends on: 1, 2_

- [x] 5. Build the React player experience
  - Create the UI for session creation, joining, question-set selection from the discovered question-set files, and the two-perspective answer flow.
  - Allow players to participate without an account in v1 and keep the session ID available across refreshes.
  - _Requirements: 0.1, 0.2, 0.3, 0.4, 0.5, 1.1, 1.3, 1.4_
  - _Depends on: 3, 4_

- [x] 5.1 Configure backend CORS for the deployed frontend
  - Add an explicit, environment-configurable allowlist for frontend origins.
  - Cover preflight and credential-safe API requests without allowing unrestricted origins in production.
  - Add API coverage for permitted and rejected origins.
  - _Requirements: 4.1, 4.2_
  - _Depends on: 5_

- [x] 6. Build the judge review experience
  - Implement the judge view to request completed session results, render totals, and show the per-question match/miss breakdown.
  - Visually distinguish matches from misses using the same scoring semantics as the CLI judge workflow.
  - _Requirements: 2.1, 2.2, 2.3, 2.4_
  - _Depends on: 3, 5_

- [ ] 7. Add deployment and operational support
  - Add health checks, environment configuration, and clear frontend/backend separation for deployment.
  - Keep the app responsive on desktop and mobile layouts.
  - _Requirements: 1.3, 4.1, 4.2_
  - _Depends on: 5, 6_

- [ ] 8. Add automated coverage
  - Add unit tests for session orchestration and scoring reuse, API tests for the web lifecycle, and UI tests for player and judge flows.
  - Add compatibility tests against the existing YAML fixtures to preserve current question-file behavior.
  - _Requirements: 1.2, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 4.3, 4.4_
  - _Depends on: 2, 3, 4, 5, 6, 7_
