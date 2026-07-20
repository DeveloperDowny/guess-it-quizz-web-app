# Product Overview

This workspace contains a notebook-based orchestration layer for the Quizz CLI package.

## Purpose

The notebook workflow is intended to run the Quizz player and judge CLIs in a Google Colab environment against files stored in Google Drive. It installs the distributable wheel, runs the player flow for a selected participant, writes answer sheets into a dated artifacts folder, and then runs the judge flow over those saved YAML files.

## Users

- Notebook operator: the person who runs the notebook and provides the player identity.
- Judge: the person who reviews the scored impersonation results produced by the notebook.

## Core Requirements

- The notebook must install and run the Quizz distributable from a wheel in the Drive-based build output.
- The notebook must resolve the question set from the expected Drive path unless an override is supplied.
- The notebook must run the player workflow for a configured participant and persist generated answer sheets to a dated output directory.
- The notebook must run the judge workflow using the saved YAML files for both players and their impersonation sheets.
