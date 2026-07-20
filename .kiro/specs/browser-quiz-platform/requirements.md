# Requirements: Browser Quiz Platform

## Introduction

The project is moving from notebook-and-CLI orchestration to a browser-based client/server application. The new app must preserve the current quiz rules, reuse the existing YAML schemas, and minimize changes to the scoring and validation logic already implemented in the quiz package.

## Requirements

### Requirement 0: Browser-based 2-player game flow

**User Story:**: As a pair of player, we want to complete the quizz in a browser, so that we don't need to run a notebook or terminal workflow.

#### Acceptance Critria
1. WHEN player 1 starts a new session THE SYSTEM SHALL generate a unique session identifier and show it to the player
2. WHEN player 1 has started a new session THE SYSTEM SHALL present multiple question sets to choose from
3. WHEN player 1 chooses a question set to play THE SYSTEM SHALL save the question set id in the session data and then start the quizz for the player for the selected question set
4. WHEN player 2 joins an existing session THE SYSTEM SHALL ask it to enter the session identifier to identify the session they player wants to join
5. WHEN player 2 has entered the session id and joined the session THE SYSTEM SHALL shall retrieve the question set by the question set id saved in session data and immediately start the quizz game


### Requirement 1: Browser-based player flow

**User Story:** As a player, I want to complete the quiz in a browser, so that I do not need to run a notebook or terminal workflow.

#### Acceptance Criteria

1. WHEN a player starts a new session/joins an existing session THE SYSTEM SHALL display the active question set and collect answers for both the self perspective and the impersonation perspective in one browser flow.
2. WHEN the player selects an option THE SYSTEM SHALL accept only values that are present in the active question's defined option list.
3. IF the browser is refreshed or reopened with the same session identifier THEN THE SYSTEM SHALL restore the previously persisted session state.
4. THE SYSTEM SHALL allow a player to participate without requiring a managed account in v1.

### Requirement 2: Judge scoring and review

**User Story:** As a judge, I want the browser app to score impersonation answers exactly like the current CLI, so that the web version produces the same evaluation outcome.

#### Acceptance Criteria

1. WHEN a completed session is judged THE SYSTEM SHALL compare impersonation answers against the target player's actual answers by question ID.
2. WHEN the guessed answer exactly equals the correct answer THE SYSTEM SHALL count that question as a match.
3. WHEN the guessed answer is missing or different THE SYSTEM SHALL count that question as a miss.
4. WHEN the judge view renders THE SYSTEM SHALL show the total matched answers, the total number of questions, and a per-question breakdown that visually distinguishes matches from misses.

### Requirement 3: Question-set compatibility and versioning

**User Story:** As an operator, I want the web app to use the same question format as the current project, so that existing YAML files remain valid and reusable.

#### Acceptance Criteria

1. WHEN the backend loads a question set THE SYSTEM SHALL accept the current YAML schema with a top-level `questions` collection and nested `options` lists.
2. WHEN a question set contains duplicate question IDs, non-positive IDs, empty prompts, empty options, duplicate options, or fewer than two options THE SYSTEM SHALL reject the payload with validation errors.
3. WHEN answers are stored or exported THE SYSTEM SHALL preserve the current answer schema with `answers` entries and `question-id` field names.
4. WHEN a new active question set is configured THE SYSTEM SHALL apply it only to new sessions and SHALL keep existing sessions bound to the question set they started with.

### Requirement 4: Shared backend logic and API boundaries

**User Story:** As the development team, we want the browser app to reuse the existing quiz logic, so that the web version stays small and consistent with the current implementation.

#### Acceptance Criteria

1. WHEN the application is built THE SYSTEM SHALL expose a React frontend and a FastAPI backend as separate deployable components.
2. WHEN the frontend needs quiz data THE SYSTEM SHALL call backend endpoints for session creation, question retrieval, answer submission, and judge results.
3. WHEN backend code evaluates answers THE SYSTEM SHALL reuse shared domain and scoring logic rather than duplicating quiz rules in the frontend.
4. WHEN the application is extended THE SYSTEM SHALL keep business rules out of the UI layer.
