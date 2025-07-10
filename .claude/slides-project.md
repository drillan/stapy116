# Slides Project Knowledge

## Project Overview

This is a sphinx-revealjs presentation project for stapy116. The project creates HTML-based reveal.js presentations using Sphinx with MyST parser for Markdown support.

## Development Commands

### Presentation Building
```bash
# Build presentation slides
uv run sphinx-build -M revealjs docs docs/_build

# Clean build artifacts
uv run sphinx-build -M clean docs docs/_build

# Build HTML documentation (alternative output)
uv run sphinx-build -M html docs docs/_build

# Watch for changes and rebuild (if sphinx-autobuild is installed)
uv run sphinx-autobuild docs docs/_build/revealjs --builder revealjs
```

### Package Management
```bash
# Install dependencies
uv sync

# Add new dependency
uv add package_name

# Install Node.js dependencies for textlint
npm install
```

### Text Linting
```bash
# Run textlint on documentation
npm run textlint

# Auto-fix textlint issues
npm run textlint:fix
```

## Architecture

- **docs/**: Sphinx source files for presentation
  - `conf.py`: Sphinx configuration with MyST parser and sphinx-revealjs extensions
  - `index.md`: Main presentation slides using MyST syntax
  - `Makefile`: Standard Sphinx build commands
  - `_build/revealjs/`: Generated presentation output
  - `_static/`, `_templates/`: Static assets and custom templates

- **pyproject.toml**: Project configuration with dependencies:
  - `myst-parser>=4.0.1`: Markdown parsing for Sphinx
  - `sphinx-revealjs>=3.2.0`: Reveal.js presentation generation

## Presentation Format

The project uses MyST (Markedly Structured Text) format for creating slides. Slides are automatically created based on heading levels (H3 maximum):

- `# Title` (H1): Title slide
- `## Section` (H2): New horizontal slide
- `### Subsection` (H3): New vertical slide (sub-slide)

Note: Heading levels H4 and below are not used for slide separation and will appear as regular content within slides.

Slides are built as reveal.js presentations and can be viewed in a web browser with navigation controls.

## Slide Writing Guidelines

When creating presentation content, follow these guidelines for optimal readability and presentation effectiveness:

### Content Structure
- **Lines per slide**: 3-5 lines maximum
- **Characters per line**: Maximum 50 characters
- **Text style**: Use concise, declarative form ("である" instead of "です・ます")

### Formatting Rules
- **Emphasis**: Minimize use of bold text (`**`) - use sparingly for key terms only
- **Bullet points**: Use simple lists for clear information hierarchy
- **Consistency**: Maintain uniform formatting throughout all slides

### Writing Style
- Keep sentences short and direct
- Focus on key points rather than detailed explanations
- Use bullet points for complex information
- Ensure each slide has a single, clear message

These guidelines ensure that slides are readable during presentation and maintain audience engagement.