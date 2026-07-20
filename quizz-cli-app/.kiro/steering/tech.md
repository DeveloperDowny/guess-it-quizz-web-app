# Technical Overview

## Stack

- Python 3.11+
- Google Colab notebook execution
- Python shell commands and IPython magic commands for installation and CLI execution
- The packaged Quizz library under [quizz](quizz) with Typer-based CLIs
- YAML files for questions and answer sheets
- Google Drive as the persistence layer for questions, built artifacts, and generated answers

## Architectural Style

The notebook is an orchestration layer, not the core product implementation. It coordinates:

- environment setup in the notebook runtime,
- installation of the distributable wheel,
- invocation of the Quizz CLIs using environment variables and CLI arguments,
- copying of generated files into a dated directory for later judging.

## Conventions

- Environment variables are used to pass runtime values such as impersonator, impersonatee, and question file paths.
- The notebook uses a date-based output layout under the Drive answers directory.
- The notebook keeps the business logic in the distributable package and uses the notebook only to wire execution and persistence.
