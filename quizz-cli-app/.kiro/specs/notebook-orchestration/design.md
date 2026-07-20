# Design: Notebook Orchestration

## Overview

The notebook-level orchestration is implemented in [quizz-cli-app.ipynb](quizz-cli-app.ipynb) and acts as a thin wrapper around the Quizz package in [quizz](quizz). The design keeps the notebook responsible for environment setup, path resolution, and invocation while leaving the business rules inside the distributable package.

## Architecture

- The notebook defines the selected player and any date override.
- Helper functions resolve the Drive-backed paths for the questions file, the distributable wheel, and the dated answers directory.
- Environment variables are populated so the CLIs can consume the same runtime configuration without hard-coded paths.
- The player CLI is executed first, and the resulting answer files are copied into a dated folder.
- The judge CLI is then executed with the copied YAML file paths.

```text
Notebook -> Quizz player CLI
      -> copy artifacts to dated folder
      -> Quizz judge CLI
```

## Components and Interfaces

- get_player_config(player_name) -> Config
- get_questions_file_path(...) -> Path
- populate_env_vars(...) -> None
- get_formatted_date(...) -> str
- build_timestamp_answers_dir(...) -> Path
- populate_env_vars_judge(...) -> None
- copy_to_dir(src_dir, dest_dir) -> None
- main() -> None

## Data Models

- Config stores the impersonator and impersonatee names for the selected participant.
- The notebook uses plain filesystem paths and environment variables rather than introducing a new schema.

## Error Handling

- Missing files or directories are surfaced as filesystem errors.
- If the wheel or questions file is missing, the notebook will fail before CLI execution.
- The Quizz package itself handles invalid answer sheets and judge evaluation failures.

## Testing Strategy

- The notebook workflow is exercised indirectly through the package’s existing CLI and service tests.
- Manual validation is expected in Colab because the notebook depends on the Drive mount and local wheel path.
