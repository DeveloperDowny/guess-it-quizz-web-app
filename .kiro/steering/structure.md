# Project Structure

## Top-Level Layout

- [AGENTS.md](AGENTS.md): workspace instructions and project intent.
- [quizz-cli-app/](quizz-cli-app): the current implementation workspace.
- [.kiro/](.kiro): workspace-level Kiro steering for the overall project.

## Current Workspace Layout

- [quizz-cli-app/quizz-cli-app.ipynb](quizz-cli-app/quizz-cli-app.ipynb): notebook orchestrator for Google Colab and Google Drive workflows.
- [quizz-cli-app/quizz/](quizz-cli-app/quizz): distributable Python package with CLI entry points, domain models, services, infrastructure, and tests.
- [quizz-cli-app/quizz/data/](quizz-cli-app/quizz/data): sample and generated YAML answer/question artifacts.
- [quizz-cli-app/quizz/questions/](quizz-cli-app/quizz/questions): question assets used by the package and tests.

## Package Boundaries

- [quizz-cli-app/quizz/src/quizz/cli/](quizz-cli-app/quizz/src/quizz/cli): command-line entry points for player and judge workflows.
- [quizz-cli-app/quizz/src/quizz/domain/](quizz-cli-app/quizz/src/quizz/domain): validated schemas and repository interfaces.
- [quizz-cli-app/quizz/src/quizz/services/](quizz-cli-app/quizz/src/quizz/services): orchestration, scoring, and path resolution logic.
- [quizz-cli-app/quizz/src/quizz/infrastructure/](quizz-cli-app/quizz/src/quizz/infrastructure): YAML-backed persistence and other adapters.
- [quizz-cli-app/quizz/tests/](quizz-cli-app/quizz/tests): regression coverage for CLI, services, and repository behavior.

## Orchestration Boundaries

- The notebook layer is responsible for environment setup, wheel installation, runtime configuration, and file movement.
- The packaged quiz engine is responsible for question parsing, answer validation, score calculation, and answer-sheet persistence.
- The future web client should sit above these rules and should not embed quiz-specific business logic.
- The future backend should become the primary orchestration boundary for browser-based play and judging.

## Artifact Locations

- Questions live in YAML files under the package and notebook data paths.
- Generated answers are written into dated output folders in the notebook workflow.
- Built wheels are expected to be consumed by the notebook from a dist-style output path.
