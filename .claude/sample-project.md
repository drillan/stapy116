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
- **Continuous quality assurance**: Systematic testing and quality control

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

## Quality Assurance Workflow

### Testing Standards

#### Required Quality Metrics
- **Test Coverage**: Minimum 80% coverage maintained
- **Test Failures**: 0 failed tests (all tests must pass)
- **pytest Warnings**: 0 warnings (all markers properly defined)
- **Quality Issues**: 0 issues reported by PyQC self-check

#### Test Environment Standards
- **Environment Isolation**: All tests use `tmp_path` for file operations
- **Working Directory Management**: Use `os.chdir()` with try/finally cleanup
- **External Dependencies**: Mock all subprocess calls and external tools
- **Global State**: Avoid modifying global state; restore if necessary

### pytest Configuration

#### Required Markers in pyproject.toml
```toml
[tool.pytest.ini_options]
markers = [
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests", 
    "e2e: marks tests as end-to-end tests"
]
```

#### Test Execution Patterns
```bash
# Full test suite with coverage
uv run pytest

# Unit tests only
uv run pytest -m "unit"

# Exclude integration tests for faster feedback
uv run pytest -m "not integration"

# Coverage report
uv run pytest --cov-report=html
```

### Development Quality Workflow

#### Pre-Commit Checklist
1. **Run all tests**: `uv run pytest`
2. **Quality check**: `uv run pyqc check .`
3. **Coverage verification**: Ensure 80%+ coverage maintained
4. **Zero warnings**: All pytest warnings resolved
5. **Clean commit**: All quality checks pass

#### Troubleshooting Common Issues

##### File Name Conflicts
- **Problem**: `import file mismatch` errors in pytest
- **Solution**: Use unique test file names across directories
- **Prevention**: Avoid duplicate `test_*.py` names in different folders

##### Environment Dependencies
- **Problem**: Tests failing due to existing configuration files
- **Solution**: Use `tmp_path` fixture and `os.chdir()` for isolation
- **Pattern**: Always restore original working directory in finally block

##### Missing Test Markers
- **Problem**: `Unknown pytest.mark.integration` warnings
- **Solution**: Define all markers in `pyproject.toml`
- **Verification**: Run `pytest --markers` to check definitions

### Quality Assurance Automation

#### Continuous Testing
- **Pre-commit hooks**: Automatic test execution before Git commits
- **Claude Code hooks**: Real-time quality checks during development
- **CI/CD integration**: Automated testing on all branches

#### Quality Metrics Monitoring
- **Coverage tracking**: Monitor test coverage trends
- **Performance benchmarks**: Track test execution time
- **Quality regression**: Prevent introduction of quality issues

#### Dogfooding Practice
- **Self-application**: PyQC must pass its own quality checks
- **Zero tolerance**: No quality issues in the tool itself
- **Continuous improvement**: Use PyQC insights to improve PyQC

This quality assurance framework ensures consistent, high-quality code throughout the development lifecycle while providing clear guidelines for maintaining and improving code quality standards.

## AI-Era Quality Assurance Guidelines

### AI-Driven Development Quality Principles

#### Unique Characteristics of AI-Generated Code
- **Higher commit frequency**: AI editors generate commits more frequently than human developers
- **Different error patterns**: AI may introduce unique types of bugs not typically seen in human code
- **Objective quality metrics**: AI-generated code requires measurable, automated quality validation
- **No subjective waiting time**: AI doesn't experience "stress" from waiting for quality checks

#### Enhanced Quality Assurance for AI Development

##### Pre-Commit Integration Benefits
1. **AI Code Quality Guarantee**: Ensures all AI-generated code passes existing test suites
2. **Early Regression Detection**: Catches AI-introduced breaking changes immediately
3. **Trust Building**: Increases confidence in AI-generated code through consistent validation
4. **Debug Cost Reduction**: Prevents broken code from entering CI/CD pipelines
5. **Feedback Loop Acceleration**: Provides immediate feedback for AI model improvement
6. **CI/CD Efficiency**: Reduces unnecessary pipeline executions from failing tests

##### Quality Assurance Strategy
```yaml
# Optimized pre-commit configuration for AI development
repos:
  - repo: local
    hooks:
      - id: pyqc-check
        name: PyQC Quality Check
        # Real-time quality validation for AI-generated code
        
      - id: pytest-check  
        name: PyQC Test Suite
        # Comprehensive test validation with speed optimization
        args: ["--no-cov", "-x", "-m", "not e2e"]
```

#### Dogfooding Philosophy for AI Tools

##### Self-Application Excellence
- **Zero tolerance policy**: Quality tools must pass their own quality checks
- **Reference implementation**: Serve as exemplary implementation for AI-era best practices
- **Continuous improvement**: Use PyQC insights to enhance PyQC itself
- **Trust through transparency**: Demonstrate quality commitment through self-validation

##### AI-Specific Quality Requirements
- **Automated validation**: All code must pass automated quality checks
- **Regression prevention**: Comprehensive test coverage to prevent AI-introduced bugs
- **Performance monitoring**: Track quality check execution time for AI workflow optimization
- **Error pattern analysis**: Study AI-generated code issues to improve quality rules

#### Implementation Guidelines

##### Speed-Optimized Testing for AI Workflows
```bash
# High-frequency AI commits require fast feedback
pytest --no-cov -x -m "not e2e" --disable-warnings -q
```

##### Quality Metrics for AI Development
- **Test execution time**: < 30 seconds for pre-commit hooks
- **Quality check latency**: < 10 seconds for real-time feedback
- **False positive rate**: < 5% to maintain AI development velocity
- **Coverage maintenance**: 80%+ despite speed optimization

##### Workflow Integration
1. **Claude Code hooks**: Real-time quality checks during development
2. **Pre-commit validation**: Comprehensive checks before Git commits
3. **CI/CD verification**: Full test suite execution for release preparation
4. **Continuous monitoring**: Quality metrics tracking for process improvement

This AI-era quality assurance framework addresses the unique challenges and opportunities of AI-driven development, ensuring high-quality code output while maintaining development velocity and providing rapid feedback for continuous improvement.