# Requirements: Notebook Orchestration

## Introduction

The notebook workflow provides a repeatable way to run the Quizz player and judge CLIs from Google Colab. It bridges the interactive notebook environment with the packaged Quizz application so that answers and judging artifacts are stored in a predictable Drive-backed structure.

## Requirements

### Requirement 1: Notebook setup and installation

**User Story:** As a notebook operator, I want the notebook to prepare the runtime automatically, so that I can run the Quizz workflows without manual installation steps.

#### Acceptance Criteria
1. WHEN the notebook starts THE SYSTEM SHALL install the Quizz wheel from the configured distributable path.
2. WHEN the notebook resolves the questions location THE SYSTEM SHALL use the Drive-backed questions directory by default.
3. IF a custom date override is supplied THEN THE SYSTEM SHALL use that override when naming the output directory.

### Requirement 2: Player workflow orchestration

**User Story:** As a notebook operator, I want the notebook to launch the player CLI for a chosen participant, so that answer sheets are generated and stored automatically.

#### Acceptance Criteria
1. WHEN the player workflow runs THE SYSTEM SHALL map the selected player to the correct impersonator and impersonatee names.
2. WHEN the player workflow runs THE SYSTEM SHALL set the environment variables required by the Quizz player CLI.
3. WHEN the player workflow completes THE SYSTEM SHALL copy the generated answer files and the questions file into a timestamped output directory.

### Requirement 3: Judge workflow orchestration

**User Story:** As a judge, I want the notebook to invoke the judge CLI with the saved YAML files, so that impersonation results are produced from the collected answers.

#### Acceptance Criteria
1. WHEN the judge workflow starts THE SYSTEM SHALL resolve the answer file paths for both players and both impersonation sheets.
2. WHEN the judge workflow runs THE SYSTEM SHALL pass the resolved path values to the Quizz judge CLI.
3. WHEN the judge workflow completes THE SYSTEM SHALL leave the evaluation output available in the same dated artifacts directory.
