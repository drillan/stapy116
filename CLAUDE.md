# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Structure

This repository contains two main components:

1. **Presentation Project**: A sphinx-revealjs presentation for stapy116
2. **Sample Project**: PyQC (Python Quality Checker) specifications demonstrating Claude Code methodology

## Knowledge Organization

Project-specific knowledge is organized in the `.claude/` directory:

### Presentation Project Knowledge
- **@.claude/slides-project.md**: Complete guide for the sphinx-revealjs presentation
  - Development commands and workflow
  - Architecture and file structure
  - Slide writing guidelines and formatting rules

### Sample Project Knowledge
- **@.claude/sample-project.md**: Overview of PyQC sample project
  - Project purpose and learning objectives
  - Three key points demonstration
  - Technology stack and usage guidelines

### PyQC Specifications
- **@.claude/project-plan.md**: Project planning and implementation phases
- **@.claude/pyqc-spec.md**: Detailed functional specifications and CLI design
- **@.claude/implementation-notes.md**: Implementation guidelines and best practices

## Usage Guidelines

When working with this repository:

1. **For presentation work**: Refer to @.claude/slides-project.md
2. **For sample project**: Start with @.claude/sample-project.md for overview
3. **For PyQC implementation**: Use the three PyQC specification files

## Context Selection

Claude Code will automatically reference the appropriate knowledge files based on the task context:

- **Slide creation/editing**: Uses slides-project.md
- **PyQC development**: Uses pyqc-spec.md and implementation-notes.md
- **Project planning**: Uses project-plan.md and sample-project.md

This organization ensures efficient context usage and maintains clear separation of concerns between the presentation and sample projects.

## Implementation Plans

Implementation plans created by Claude Code are managed in @plans/index.md. This system provides:

- **Structured planning**: Each plan has a unique ID and clear objectives
- **Progress tracking**: Status and completion tracking for all plans
- **Historical record**: Completed plans are archived for future reference
- **Memory efficiency**: Plans are stored separately from core knowledge to avoid context bloat

Plans are organized in separate directories (`active/`, `completed/`, `archived/`) and follow a consistent template for documentation and tracking.