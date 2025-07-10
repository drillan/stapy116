# PyQC Scripts Directory

This directory contains utility scripts for PyQC Claude Code hooks integration.

## Scripts

### `pyqc_hooks.py`

A comprehensive wrapper script for PyQC that provides detailed logging and monitoring for Claude Code hooks.

**Features:**
- Comprehensive PyQC execution logging
- Real-time performance monitoring
- Context-aware output formatting
- Error handling and timeout management
- Integration with PyQC logging system

**Usage:**
```bash
# Direct execution
uv run python scripts/pyqc_hooks.py <file_path>

# With Claude hooks (automatic)
# Runs automatically when editing Python files
```

**Logging Output:**
The script records detailed execution information to `.pyqc/hooks.log`:
- Execution timestamp and file path
- Command executed and arguments
- Execution time and performance metrics
- Success/failure status
- Detailed error information

## Integration with Development Workflow

### Claude Hooks (Development Time)
- Automatically runs on Python file edits via `.claude/hooks.json`
- Provides immediate feedback with rich logging
- Records comprehensive execution history
- Helps maintain code quality during development

### Hooks Configuration
The script is integrated via `.claude/hooks.json`:
```json
{
  "hooks": {
    "PostToolUse": {
      "Write,Edit,MultiEdit": {
        "command": "uv run python scripts/pyqc_hooks.py ${file}",
        "onFailure": "warn",
        "timeout": 15000
      }
    }
  }
}
```

## Monitoring and Management

### CLI Commands
PyQC provides built-in commands to monitor hooks execution:

```bash
# View execution statistics
uv run pyqc hooks stats

# View recent log entries
uv run pyqc hooks log

# Clear log history
uv run pyqc hooks clear
```

### Log Analysis
The logging system provides:
- **Execution tracking**: Every hooks run is logged
- **Performance monitoring**: Execution time measurement
- **Success rate analysis**: Statistical overview
- **Error diagnostics**: Detailed failure information

## Troubleshooting

### Common Issues

1. **Script not found**: Ensure the script is in the `scripts/` directory
2. **Permission errors**: Make sure the script is executable (`chmod +x`)
3. **Import errors**: Verify PyQC is properly installed with `uv sync`
4. **Timeout issues**: Check if timeout setting (15s) is appropriate

### Debug Mode

For detailed debugging, check the hooks log:
```bash
# View recent executions
uv run pyqc hooks log --lines 50

# Check execution statistics
uv run pyqc hooks stats
```

### Performance Optimization

The script is optimized for hooks usage:
- **Timeout management**: 30-second command timeout
- **Error isolation**: Graceful handling of failures
- **Context switching**: Automatic directory management
- **Efficient logging**: Structured log format

## Dependencies

The script uses:
- `uv` for Python environment management
- PyQC CLI for quality checking
- PyQC logging utilities for structured logging
- Standard subprocess module for command execution

## Best Practices

### Hooks Usage
- **File targeting**: Only processes Python files
- **Non-blocking**: Continues development even on failures
- **Informative**: Provides clear success/failure feedback
- **Traceable**: Maintains complete execution history

### Development Integration
- **Real-time feedback**: Immediate quality check results
- **Performance awareness**: Execution time monitoring
- **Historical analysis**: Long-term quality trend tracking
- **Error resolution**: Detailed diagnostic information

This script serves as a bridge between Claude Code's hooks system and PyQC's quality checking capabilities, providing comprehensive monitoring and logging for AI-driven development workflows.