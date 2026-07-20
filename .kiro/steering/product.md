# Product Overview

Quizz is intended to become a browser-based quiz impersonation platform. The current workspace contains the CLI and notebook foundation that already implements the quiz flow, while the project goal is to expose that experience through a client/server web application.

## Purpose

The product supports a two-stage game:

1. A player session that collects a participant's own answers and the same participant's answers while impersonating another person.
2. A judge workflow that compares impersonation answers against the target person's actual answers and reports how closely the impersonation matched.

The existing CLI and notebook artifacts are the implementation base. The future web app should preserve the same game rules and data formats while moving the user experience into a hosted UI.

## Users

- Player or impersonator: answers questions from two perspectives.
- Judge: reviews scored impersonation results.
- Operator: configures question files, runs the workflow, and manages generated artifacts.

## Current Product Scope

- Multiple-choice question sets are stored as YAML.
- Player sessions produce answer sheets for self and impersonation perspectives.
- Judge sessions score exact matches per question and render a breakdown.
- A notebook orchestrator exists for Google Colab and Google Drive-based workflows.
- The quiz engine itself is packaged as a Python CLI distribution.

## Target Product Direction

- A web client should let users play the quiz through a browser instead of only through a notebook or terminal.
- A backend should own game orchestration, persistence, and scoring logic.
- The web experience should reuse the existing quiz rules and data model rather than redefining the game.
- Deployment should support a simple hosted path so the project can ship with minimal changes to the current core logic.

## Core Requirements

- The system must present multiple-choice questions from a YAML question set.
- The system must collect answers for two perspectives in a single run.
- The system must validate that answers correspond to defined question options.
- The system must persist answer sheets as YAML files.
- The system must score impersonation accuracy using exact matches per question.
- The system must render a scoreboard and a per-question breakdown with visual markers.
- The orchestration layer must be able to drive the quiz flow without duplicating business rules in the UI layer.
