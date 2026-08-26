# Project Conventions

Target-owned for this repository (the collaboration template itself).
Adopting projects get their own copy from `docs/templates/project-conventions.md`.
Template sync must not overwrite an adopting project's live file.

## Project

- Name: llm-project-template
- Domain: reusable AI-human collaboration process template
- Stack: Markdown process docs, bash adoption scripts, GitHub Actions

## External resources (ports)

- Git and GitHub CLI for branch, PR, and sync operations
- No application datastore
- No LLM provider SDK in this repository

## Runtime and trust boundaries

- The project is local-first documentation and scripts.
- No production application runtime.

## Current non-decisions

- Adopter application stack, datastore, and LLM provider

## Stack-specific architecture documents

- none beyond the shipped process architecture documents

## Additional project rules

- This repository maintains the reusable template. Target product facts do
  not belong in template context files.
