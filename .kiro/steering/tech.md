# Technical Overview

## Stack

Current implementation:

- Python 3.11+
- Typer for CLI applications
- Pydantic v2 and pydantic-settings for validation and settings
- PyYAML for YAML parsing and serialization
- pytest for automated tests
- uv and uv_build for dependency management, packaging, and build workflows
- Google Colab notebook execution for the notebook orchestrator
- Google Drive as the notebook persistence layer for questions, wheels, and generated answers

Target implementation preferences:

- Vite + React + Tailwind for the frontend
- FastAPI for the backend API
- uv, uv_build, and Pydantic v2 on the backend
- Google Cloud Run for backend deployment
- Google Firebase for authentication and/or app-facing persistence if needed

## Architectural Style

The codebase is split between a reusable quiz engine and orchestration layers:

- The quiz package owns domain models, services, CLI flows, and YAML-backed persistence.
- The notebook orchestrator coordinates installation and execution of the packaged CLI in a Colab environment.
- The future web client should remain a thin presentation layer over backend APIs.
- The future backend should preserve the existing scoring and persistence rules rather than reimplementing them in the frontend.

## Conventions

- Business rules live outside the UI layer.
- Environment-specific paths are resolved through a dedicated path resolver or settings object.
- YAML is the canonical interchange format for questions and answer sheets.
- Answer persistence uses date-based artifact directories in notebook-based workflows.
- CLI commands should remain explicit and scriptable so they can be reused by automation.

## Constraints

- The current code should not be refactored heavily unless needed to support the web transition.
- New layers should reuse the existing domain and scoring logic where possible.
- Any future API should expose the same quiz semantics already used by the CLI and notebook workflows.
