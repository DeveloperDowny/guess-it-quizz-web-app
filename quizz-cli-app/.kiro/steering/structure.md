# Project Structure

## Top-Level Layout

- [quizz-cli-app.ipynb](quizz-cli-app.ipynb): the notebook that orchestrates the workflow.
- [quizz](quizz): the distributable Quizz package with CLI entry points, domain models, services, and tests.
- [.kiro](.kiro): workspace-level Kiro documentation for the notebook workflow.

## Notebook-Orchestration Responsibilities

- [quizz-cli-app.ipynb](quizz-cli-app.ipynb): installs the wheel, configures environment variables, runs the player CLI, copies answer files, and runs the judge CLI.
- [quizz](quizz): owns the actual question parsing, answer-sheet validation, judging logic, and CLI behavior.

## Artifact Locations

- Questions live in the Drive-backed questions directory and default to questions/questions.yaml.
- Output artifacts are written to answers/YYYYMMDD under the Drive-based workspace.
- The notebook expects the distributable wheel to be available under dist/quizz-0.1.0-py3-none-any.whl.
