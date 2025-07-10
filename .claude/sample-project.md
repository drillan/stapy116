# Sample Project: PyQC

## Overview

This repository includes specifications for PyQC (Python Quality Checker), a sample project demonstrating the practical approach of Claude Code. PyQC serves as a concrete example of how to implement the three key points from the presentation.

## Project Purpose

PyQC is designed to illustrate the concepts from the "Claude Codeの実践的なアプローチ" presentation by providing a real-world example of:

1. **Planning (計画・設計を立てる)**
2. **Recording (記録を残す)**  
3. **Robustness (堅牢なコードを書く)**

## Documentation Structure

Detailed specifications and implementation notes are available in the `.claude/` directory:

### Core Project Files
- **`.claude/project-plan.md`**: Overall project planning and phases
  - Project overview and scope
  - Implementation phases (MVP → Extensions)
  - Milestones and success metrics
  - Risk assessment and mitigation

- **`.claude/pyqc-spec.md`**: Detailed functional specifications
  - Feature specifications (quality checks, auto-fix, hooks)
  - CLI interface design
  - Configuration options
  - Output formats and error handling

- **`.claude/implementation-notes.md`**: Implementation guidelines and best practices
  - TDD approach and testing strategy
  - Error handling patterns
  - Logging and debugging
  - Security considerations

## Three Key Points Demonstration

### 1. Planning (計画・設計を立てる)
- **Structured project phases**: MVP → Extensions → Integration
- **Clear specifications**: Detailed functional requirements
- **Risk assessment**: Technical and adoption risks identified
- **Success metrics**: Quantifiable goals for quality and adoption

### 2. Recording (記録を残す)
- **Comprehensive documentation**: All aspects documented in `.claude/`
- **Structured knowledge base**: Organized by purpose and scope
- **Decision rationale**: Why specific technologies were chosen
- **Implementation guidance**: Step-by-step development approach

### 3. Robustness (堅牢なコードを書く)
- **Quality automation**: Integrated ruff, mypy/ty type checking
- **Hook integration**: Claude Code hooks for automatic quality checks
- **TDD approach**: Test-driven development methodology
- **Error handling**: Comprehensive error management strategy

## Technology Stack

- **Core**: Python 3.12 with typer for CLI
- **Quality Tools**: ruff (linting/formatting), mypy/ty (type checking)
- **Testing**: pytest with comprehensive test coverage
- **Automation**: pre-commit hooks and Claude Code hooks integration
- **Package Management**: uv for modern Python dependency management

## Usage as Learning Material

This sample project can be used to:

1. **Study project planning**: Review the structured approach to feature development
2. **Learn documentation practices**: See how to organize project knowledge
3. **Understand quality automation**: Examine the integration of quality tools
4. **Practice TDD**: Follow the test-driven development methodology
5. **Implement hooks**: Set up automated quality checks with Claude Code

## Future Extensions

The project is designed with extensibility in mind:

- **Plugin system**: Support for custom quality checkers
- **AI integration**: Potential integration with AI code review tools
- **Monitoring**: Performance and usage metrics
- **Community features**: Contribution guidelines and community engagement

This sample project serves as a practical blueprint for implementing the Claude Code methodology in real-world development scenarios.