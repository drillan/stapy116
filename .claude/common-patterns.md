# 定型パターン

## CLI実装パターン

### Typer基本構造
```python
import typer
from rich.console import Console

app = typer.Typer(
    name="ツール名",
    help="ツール説明",
    no_args_is_help=True,
)
console = Console()

@app.command()
def command_name(
    path: str = typer.Argument(".", help="対象パス"),
    option: bool = typer.Option(False, "--option", help="オプション説明"),
) -> None:
    """コマンド説明."""
    console.print(f"🔍 処理中: {path}")
    # 実装
    console.print("✅ 完了")
```

### CLI引数・オプションパターン
```python
# 必須引数
path: str = typer.Argument(..., help="必須パス")

# オプション引数（デフォルト値あり）
path: str = typer.Argument(".", help="オプションパス")

# フラグオプション
verbose: bool = typer.Option(False, "--verbose", "-v", help="詳細出力")

# 選択肢オプション
format: str = typer.Option("text", "--format", help="出力形式: text, json, github")

# 複数値オプション
files: list[str] = typer.Option([], "--file", help="対象ファイル")

# サブコマンド引数
action: str = typer.Argument("default", help="実行アクション")
```

### Rich出力パターン
```python
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

# 基本メッセージ
console.print("✅ 成功", style="green")
console.print("❌ エラー", style="red")
console.print("⚠️ 警告", style="yellow")

# 進捗表示
console.print(f"🔍 チェック中: {file_count}ファイル")

# テーブル表示
table = Table(title="チェック結果")
table.add_column("ファイル")
table.add_column("エラー数")
table.add_row("main.py", "3")
console.print(table)

# パネル表示
panel = Panel("重要な情報", title="注意")
console.print(panel)
```

## 設定管理パターン

### Pydantic設定クラス
```python
from pydantic import BaseModel, Field
from pathlib import Path
from typing import Any

class ToolConfig(BaseModel):
    """ツール設定."""
    
    option1: str = Field(default="default", description="オプション1")
    option2: int = Field(default=0, gt=0, description="正の整数")
    option3: list[str] = Field(default_factory=list)
    
    model_config = {"extra": "forbid"}  # 未知フィールドを禁止

class MainConfig(BaseModel):
    """メイン設定."""
    
    tool: ToolConfig = Field(default_factory=ToolConfig)
    
    @classmethod
    def load_from_file(cls, path: Path) -> "MainConfig":
        """ファイルから設定を読み込み."""
        if path.suffix == ".toml":
            import tomllib
            with open(path, "rb") as f:
                data = tomllib.load(f)
        elif path.suffix in [".yml", ".yaml"]:
            import yaml
            with open(path) as f:
                data = yaml.safe_load(f)
        return cls.model_validate(data)
```

### Pydantic エイリアス対応パターン
```python
from pydantic import BaseModel, Field

class ConfigWithAliases(BaseModel):
    """エイリアス対応設定."""
    
    # kebab-case ↔ snake_case 変換
    line_length: int = Field(default=88, alias="line-length")
    type_checker: str = Field(default="mypy", alias="type-checker")
    
    # 両方の名前を受け付ける
    model_config = {"populate_by_name": True}
    
    @classmethod
    def load_from_file(cls, path: Path) -> "ConfigWithAliases":
        """ファイルから設定を読み込み（エイリアス対応）."""
        # ... データ読み込み
        return cls.model_validate(data, by_alias=True)
```

### 設定ファイル探索パターン
```python
from pathlib import Path

def find_config_file(start_dir: Path) -> Path | None:
    """設定ファイルを探索."""
    current = start_dir.resolve()
    
    while current != current.parent:
        for name in ["pyproject.toml", ".tool.yaml", ".tool.yml"]:
            config_path = current / name
            if config_path.exists():
                return config_path
        current = current.parent
    
    return None
```

### pyproject.toml統合パターン
```python
import tomllib
from pathlib import Path

def load_pyproject_config(path: Path) -> dict[str, Any]:
    """pyproject.tomlから設定を読み込み."""
    with open(path, "rb") as f:
        data = tomllib.load(f)
    
    # [tool.ツール名] セクションを取得
    return data.get("tool", {}).get("tool_name", {})
```

## テストパターン

### CLIテストパターン
```python
import pytest
from typer.testing import CliRunner
from mypackage.cli import app

runner = CliRunner()

def test_command_success():
    """正常実行テスト."""
    result = runner.invoke(app, ["command", "arg"])
    assert result.exit_code == 0
    assert "期待される出力" in result.stdout

def test_command_error():
    """エラーテスト."""
    result = runner.invoke(app, ["command", "invalid"])
    assert result.exit_code != 0
    assert "エラーメッセージ" in result.stdout

def test_command_with_options():
    """オプション付きテスト."""
    result = runner.invoke(app, ["command", "--option", "value"])
    assert result.exit_code == 0

def test_command_with_directory_change():
    """ディレクトリ変更テスト."""
    import os
    original_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        result = runner.invoke(app, ["command"])
        assert result.exit_code == 0
    finally:
        os.chdir(original_cwd)
```

#### 外部プロセスモックパターン
```python
import pytest
from unittest.mock import Mock, patch
import subprocess

@patch("subprocess.run")
def test_external_tool_success(mock_run: Mock) -> None:
    """外部ツール成功テスト."""
    # モック設定
    mock_run.return_value = subprocess.CompletedProcess(
        args=["tool", "check"],
        returncode=0,
        stdout='[{"line": 1, "message": "test"}]',
        stderr=""
    )
    
    # テスト実行
    result = run_tool_check(Path("test.py"))
    
    # 検証
    assert len(result) == 1
    assert result[0]["line"] == 1
    mock_run.assert_called_once()

@patch("subprocess.run")
def test_external_tool_not_found(mock_run: Mock) -> None:
    """ツール未インストールテスト."""
    mock_run.side_effect = FileNotFoundError("tool: command not found")
    
    with pytest.raises(FileNotFoundError, match="tool: command not found"):
        run_tool_check(Path("test.py"))

@patch("subprocess.run")
def test_external_tool_execution_error(mock_run: Mock) -> None:
    """ツール実行エラーテスト."""
    mock_run.return_value = subprocess.CompletedProcess(
        args=["tool", "check"],
        returncode=2,  # 実行エラー
        stdout="",
        stderr="Fatal error occurred"
    )
    
    with pytest.raises(RuntimeError, match="tool execution failed"):
        run_tool_check(Path("test.py"))
```

### 設定テストパターン
```python
import pytest
from pathlib import Path
from mypackage.config import Config

def test_default_config():
    """デフォルト設定テスト."""
    config = Config()
    assert config.option1 == "default"
    assert config.option2 == 0

def test_config_validation():
    """設定バリデーションテスト."""
    with pytest.raises(ValueError):
        Config(option2=-1)  # 負の値は無効

def test_config_from_file(tmp_path):
    """ファイルからの設定読み込みテスト."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("option1: test\noption2: 42")
    
    config = Config.load_from_file(config_file)
    assert config.option1 == "test"
    assert config.option2 == 42

def test_config_with_aliases(tmp_path):
    """エイリアス対応設定テスト."""
    config_file = tmp_path / "pyproject.toml"
    config_file.write_text("""
[tool.mytool]
line-length = 100
type-checker = "mypy"
""")
    
    config = Config.load_from_file(config_file)
    assert config.line_length == 100
    assert config.type_checker == "mypy"
```

### フィクスチャパターン
```python
import pytest
from pathlib import Path

@pytest.fixture
def sample_python_file(tmp_path):
    """サンプルPythonファイル."""
    file_path = tmp_path / "sample.py"
    file_path.write_text("""
def hello(name: str) -> str:
    return f"Hello, {name}!"

if __name__ == "__main__":
    print(hello("World"))
""")
    return file_path

@pytest.fixture
def config_file(tmp_path):
    """設定ファイル."""
    config_path = tmp_path / "pyproject.toml"
    config_path.write_text("""
[tool.mytool]
option1 = "test"
option2 = 42
""")
    return config_path
```

## エラーハンドリングパターン

### カスタム例外階層
```python
class ToolError(Exception):
    """ベース例外."""
    pass

class ConfigurationError(ToolError):
    """設定エラー."""
    
    def __init__(self, message: str, config_path: Path | None = None):
        super().__init__(message)
        self.config_path = config_path

class ValidationError(ToolError):
    """バリデーションエラー."""
    
    def __init__(self, message: str, field: str | None = None):
        super().__init__(message)
        self.field = field

class ExecutionError(ToolError):
    """実行エラー."""
    
    def __init__(self, message: str, command: str | None = None):
        super().__init__(message)
        self.command = command
```

### エラーハンドリング統合パターン
```python
from rich.console import Console

console = Console()

def handle_error(error: Exception) -> int:
    """エラーハンドリング."""
    if isinstance(error, ConfigurationError):
        console.print(f"❌ 設定エラー: {error}", style="red")
        if error.config_path:
            console.print(f"ファイル: {error.config_path}")
        console.print("💡 解決方法: tool init で設定を初期化してください")
        return 1
    
    elif isinstance(error, ValidationError):
        console.print(f"❌ バリデーションエラー: {error}", style="red")
        if error.field:
            console.print(f"フィールド: {error.field}")
        return 2
    
    else:
        console.print(f"❌ 予期しないエラー: {error}", style="red")
        return 3
```

## 外部プロセス実行パターン

### 安全なサブプロセス実行
```python
import subprocess
from pathlib import Path
from typing import Any

def run_external_tool(
    command: list[str], 
    path: Path,
    cwd: Path | None = None
) -> subprocess.CompletedProcess[str]:
    """安全な外部ツール実行."""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False  # 手動でエラーチェック
        )
        return result
    except FileNotFoundError as e:
        raise FileNotFoundError(f"{command[0]}: command not found") from e

def check_tool_exit_code(result: subprocess.CompletedProcess[str], tool_name: str) -> None:
    """ツール終了コードチェック."""
    # 一般的な終了コード規則
    # 0: 成功・問題なし
    # 1: 問題発見（修正可能）
    # 2+: 実行エラー
    if result.returncode >= 2:
        raise RuntimeError(f"{tool_name} execution failed: {result.stderr}")

# 使用例: Ruff実行
def run_ruff_check(path: Path) -> list[dict[str, Any]]:
    """Ruff リントチェック."""
    command = ["ruff", "check", "--output-format=json", str(path)]
    result = run_external_tool(command, path)
    check_tool_exit_code(result, "ruff")
    
    if not result.stdout.strip():
        return []
    
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON from ruff: {result.stdout}", "", 0) from e
```

### 出力パーサーパターン
```python
import re
import json
from typing import Any

def parse_tool_output(output: str, format_type: str) -> list[dict[str, Any]]:
    """ツール出力の統一パーサー."""
    if not output.strip():
        return []
    
    if format_type == "json":
        return parse_json_output(output)
    elif format_type == "text":
        return parse_text_output(output)
    else:
        raise ValueError(f"Unsupported format: {format_type}")

def parse_json_output(output: str) -> list[dict[str, Any]]:
    """JSON形式出力のパーサー."""
    try:
        data = json.loads(output)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON output: {output}", "", 0) from e

def parse_text_output(output: str) -> list[dict[str, Any]]:
    """テキスト形式出力のパーサー（mypy等）."""
    issues = []
    lines = output.strip().split('\n')
    
    for line in lines:
        # パターン: filename:line: severity: message [code]
        match = re.match(
            r'^(.+):(\d+):\s*(error|warning|note):\s*(.+?)(?:\s*\[([^\]]+)\])?$',
            line
        )
        
        if match:
            filename, line_num, severity, message, code = match.groups()
            issues.append({
                "filename": filename,
                "line": int(line_num),
                "severity": severity,
                "message": message.strip(),
                "code": code
            })
    
    return issues
```

### 統一結果データ構造
```python
from dataclasses import dataclass
from typing import Any

@dataclass
class Issue:
    """統一された問題レポート."""
    filename: str
    line: int
    column: int | None
    severity: str  # error, warning, info, note
    message: str
    code: str | None
    checker: str
    fixable: bool = False
    
    def to_dict(self) -> dict[str, Any]:
        """辞書形式に変換."""
        return {
            "filename": self.filename,
            "line": self.line,
            "column": self.column,
            "severity": self.severity,
            "message": self.message,
            "code": self.code,
            "checker": self.checker,
            "fixable": self.fixable
        }

@dataclass 
class CheckResult:
    """チェック結果."""
    path: Path
    issues: list[Issue]
    success: bool
    error_message: str | None = None
    execution_time: float = 0.0
    
    def get_issue_count_by_severity(self) -> dict[str, int]:
        """重要度別問題数."""
        counts = {"error": 0, "warning": 0, "info": 0, "note": 0}
        for issue in self.issues:
            if issue.severity in counts:
                counts[issue.severity] += 1
        return counts
```

## ファイル処理パターン

### ファイル探索
```python
from pathlib import Path

def find_python_files(directory: Path) -> list[Path]:
    """Pythonファイルを再帰的に探索."""
    return list(directory.rglob("*.py"))

def find_files_with_exclusions(
    directory: Path,
    patterns: list[str],
    exclude_patterns: list[str] | None = None
) -> list[Path]:
    """パターンマッチングでファイル探索."""
    exclude_patterns = exclude_patterns or [
        ".git/", "__pycache__/", ".pytest_cache/", ".venv/"
    ]
    
    files = []
    for pattern in patterns:
        for file_path in directory.rglob(pattern):
            # 除外パターンチェック
            if any(exclude in str(file_path) for exclude in exclude_patterns):
                continue
            files.append(file_path)
    
    return sorted(set(files))
```

### 並列処理パターン
```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Callable, Any

def process_files_parallel(
    files: list[Path],
    processor: Callable[[Path], Any],
    max_workers: int | None = None
) -> list[Any]:
    """ファイルを並列処理."""
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # ジョブ送信
        future_to_file = {
            executor.submit(processor, file_path): file_path 
            for file_path in files
        }
        
        # 結果収集
        for future in as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as exc:
                console.print(f"❌ エラー {file_path}: {exc}", style="red")
    
    return results

## Hooks統合パターン

### Claude Code hooks設定
```json
{
  "hooks": {
    "PostToolUse": {
      "Write,Edit,MultiEdit": {
        "command": "uv run pyqc check ${file} --output github",
        "onFailure": "warn",
        "timeout": 10000
      }
    }
  }
}
```

### pre-commit hooks設定
```yaml
repos:
  - repo: local
    hooks:
      - id: pyqc-check
        name: PyQC Check
        entry: uv --directory pyqc run pyqc check
        language: system
        types: [python]
        pass_filenames: false
        always_run: true
```

### hooks初期化コマンドパターン
```python
@app.command()
def init(
    with_pre_commit: bool = typer.Option(
        False, "--with-pre-commit", help="pre-commit設定も生成"
    ),
    with_hooks: bool = typer.Option(
        False, "--with-hooks", help="Claude Code hooks設定も生成"
    ),
) -> None:
    """プロジェクト初期化とhooks設定."""
    console.print("🚀 Initializing PyQC...")
    
    # 基本設定
    create_config_file(target_path)
    
    # pre-commit hooks
    if with_pre_commit:
        create_pre_commit_config(target_path)
    
    # Claude Code hooks
    if with_hooks:
        create_claude_hooks_config(target_path)
```

## Dogfoodingパターン（自己適用）

### 自己品質チェック実装
```python
def check_self_quality() -> None:
    """開発中のツール自身の品質をチェック."""
    # プロジェクトルート取得
    project_root = Path(__file__).parent.parent
    
    # 自分自身をチェック
    runner = PyQCRunner(config)
    results = runner.check_files(project_root)
    
    # 問題があれば報告
    total_issues = sum(len(r.issues) for r in results)
    if total_issues > 0:
        console.print(f"⚠️ {total_issues}件の品質問題を発見")
        console.print("💡 'uv run pyqc fix' で自動修正を試してください")
    else:
        console.print("✅ 品質問題なし")
```

### 段階的品質修正プロセス
```python
def fix_quality_issues_step_by_step(project_path: Path) -> None:
    """段階的な品質問題修正."""
    console.print("🔧 段階的品質修正を開始...")
    
    # 1. 自動修正
    console.print("Step 1: 自動修正実行")
    run_auto_fix(project_path)
    
    # 2. 残り問題確認
    console.print("Step 2: 残り問題確認")
    remaining_issues = check_remaining_issues(project_path)
    
    if remaining_issues:
        console.print(f"⚠️ {len(remaining_issues)}件の手動修正が必要")
        for issue in remaining_issues:
            console.print(f"  - {issue.filename}:{issue.line} {issue.message}")
        console.print("💡 手動修正後に再度チェックしてください")
    else:
        console.print("✅ すべての品質問題が解決されました")
```

## 環境非依存設定パターン

### 相対パス設定
```bash
# 問題: 絶対パス依存
entry: /home/user/project/tool run command

# 解決: プロジェクト相対
entry: uv --directory project_name run tool command
```

### 設定テンプレートパターン
```python
def create_config_template(project_name: str) -> str:
    """環境非依存の設定テンプレート生成."""
    return f"""
repos:
  - repo: local
    hooks:
      - id: {project_name}-check
        name: {project_name.title()} Check
        entry: uv --directory {project_name} run {project_name} check
        language: system
        types: [python]
        pass_filenames: false
        always_run: true
"""
```

## エンドツーエンドテストパターン

### 実プロセス実行テスト
```python
import subprocess
import pytest
from pathlib import Path

def test_real_cli_execution(tmp_path: Path) -> None:
    """実際のCLI実行テスト."""
    # テストプロジェクト作成
    test_file = tmp_path / "test.py"
    test_file.write_text("print('hello world')")
    
    # 実際のコマンド実行
    result = subprocess.run(
        ["uv", "run", "pyqc", "check", "."],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(PROJECT_ROOT)}
    )
    
    # 結果検証
    assert result.returncode == 0
    assert "Checking" in result.stdout

def test_hooks_integration(tmp_path: Path) -> None:
    """hooks統合テスト."""
    # Git初期化
    subprocess.run(["git", "init"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmp_path)
    
    # pre-commit設定
    create_pre_commit_config(tmp_path)
    subprocess.run(["pre-commit", "install"], cwd=tmp_path, check=True)
    
    # テストファイル作成・コミット
    test_file = tmp_path / "test.py"
    test_file.write_text("import os\nprint('hello')")  # 未使用インポート
    
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    
    # pre-commit実行（hooks動作確認）
    result = subprocess.run(
        ["git", "commit", "-m", "test"],
        cwd=tmp_path,
        capture_output=True,
        text=True
    )
    
    # hooksが実行され、問題を検出すること
    assert "PyQC Check" in result.stdout
```

## コマンド実行パターン

### uvコマンド統一実行
```bash
# プロジェクトディレクトリ指定
uv --directory project_name run command

# 開発依存含む同期
uv sync --extra dev

# スクリプト実行
uv run python -m package.module

# パッケージ実行
uv run package command

# 特定バージョン指定
uv run --python 3.12 python script.py
```

### Git操作パターン
```bash
# pre-commit初期化
pre-commit install

# 手動実行
pre-commit run --all-files

# Git設定（テスト用）
git config user.email "test@example.com"
git config user.name "Test User"

# hooks実行確認
git add . && git commit -m "test commit"
```

### 品質チェックコマンド
```bash
# 基本チェック
uv run pyqc check .

# 出力形式指定
uv run pyqc check . --output json
uv run pyqc check . --output github

# 自動修正
uv run pyqc fix .

# ドライラン
uv run pyqc fix . --dry-run

# 設定確認
uv run pyqc config show

# 初期化
uv run pyqc init --with-pre-commit --with-hooks
```

## Claude Code Hooks ログ記録パターン

### ログシステム設計
```python
from pathlib import Path
import logging
from rich.logging import RichHandler
from rich.console import Console

def setup_logger(
    name: str = "tool",
    level: str = "INFO", 
    log_file: Path | None = None,
    use_rich: bool = True
) -> logging.Logger:
    """ログシステム設定."""
    logger = logging.getLogger(name)
    
    # 重複防止
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    logger.setLevel(getattr(logging, level.upper()))
    
    # コンソールハンドラー（Rich対応）
    if use_rich:
        console_handler = RichHandler(
            console=Console(stderr=True),
            show_path=False,
            show_time=True,
            markup=True
        )
    else:
        console_handler = logging.StreamHandler()
    
    logger.addHandler(console_handler)
    
    # ファイルハンドラー
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_format = "%(asctime)s | %(name)s | %(levelname)s | %(message)s | %(pathname)s:%(lineno)d"
        file_handler.setFormatter(logging.Formatter(file_format))
        logger.addHandler(file_handler)
    
    return logger
```

### Hooks専用スクリプトパターン
```python
#!/usr/bin/env python3
"""Hooks統合スクリプト."""

import os
import subprocess
import sys
import time
from pathlib import Path

# パス設定
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

# フォールバック実装
try:
    from tool.utils.logger import get_hooks_logger, log_hooks_execution
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("tool.hooks.fallback")
    
    def get_hooks_logger():
        return logger
    
    def log_hooks_execution(file_path: str, command: str, success: bool, 
                          execution_time: float, output: str = "", error: str = ""):
        status = "SUCCESS" if success else "FAILED"
        logger.info(f"{status} | {file_path} | {execution_time:.2f}s")

def run_tool_check(file_path: Path) -> tuple[bool, str, str]:
    """ツール実行."""
    project_dir = Path(__file__).parent.parent
    original_cwd = os.getcwd()
    
    try:
        os.chdir(project_dir)
        
        command = ["uv", "run", "tool", "check", str(file_path), "--output", "github"]
        
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return result.returncode == 0, result.stdout, result.stderr
        
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", f"Error: {str(e)}"
    finally:
        os.chdir(original_cwd)

def process_file(file_path: Path) -> bool:
    """ファイル処理."""
    logger = get_hooks_logger()
    
    # Python ファイルのみ処理
    if file_path.suffix != '.py':
        return True
    
    logger.info(f"🔍 Processing {file_path}")
    
    start_time = time.time()
    success, stdout, stderr = run_tool_check(file_path)
    execution_time = time.time() - start_time
    
    # ログ記録
    command_str = f"uv run tool check {file_path} --output github"
    log_hooks_execution(
        file_path=str(file_path),
        command=command_str,
        success=success,
        execution_time=execution_time,
        output=stdout,
        error=stderr
    )
    
    # 結果表示
    if success:
        logger.info(f"✅ Success ({execution_time:.2f}s)")
    else:
        logger.warning(f"⚠️ Issues found ({execution_time:.2f}s)")
        
    # GitHub Actions形式出力
    if stdout.strip():
        for line in stdout.strip().split('\n'):
            if line.strip():
                print(line)
    
    return success

def main() -> int:
    """メイン関数."""
    if len(sys.argv) < 2:
        return 1
    
    file_paths = [Path(arg) for arg in sys.argv[1:]]
    all_success = True
    
    for file_path in file_paths:
        try:
            success = process_file(file_path)
            if not success:
                all_success = False
        except Exception as e:
            logger = get_hooks_logger()
            logger.error(f"Error processing {file_path}: {e}")
            all_success = False
    
    return 0 if all_success else 1

if __name__ == "__main__":
    sys.exit(main())
```

### Hooks設定パターン
```json
{
  "hooks": {
    "PostToolUse": {
      "Write,Edit,MultiEdit": {
        "command": "uv run python scripts/tool_hooks.py ${file}",
        "onFailure": "warn",
        "timeout": 15000
      }
    }
  }
}
```

### ログ統計分析パターン
```python
def get_hooks_stats() -> dict[str, any]:
    """ログファイルから統計を生成."""
    log_file = Path.cwd() / ".tool" / "hooks.log"
    
    if not log_file.exists():
        return {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "success_rate": 0.0,
            "average_execution_time": 0.0,
            "last_execution": None
        }
    
    total = successful = failed = 0
    execution_times = []
    last_execution = None
    
    try:
        with open(log_file, 'r') as f:
            for line in f:
                if "HOOKS EXECUTION" in line:
                    total += 1
                    if "SUCCESS" in line:
                        successful += 1
                    elif "FAILED" in line:
                        failed += 1
                    
                    # 実行時間抽出
                    try:
                        time_part = line.split("Time: ")[1].split("s")[0]
                        execution_times.append(float(time_part))
                    except (IndexError, ValueError):
                        pass
                    
                    # タイムスタンプ抽出
                    try:
                        timestamp = line.split(" | ")[0]
                        last_execution = timestamp
                    except IndexError:
                        pass
    except Exception:
        pass
    
    return {
        "total_executions": total,
        "successful_executions": successful,
        "failed_executions": failed,
        "success_rate": (successful / total * 100) if total > 0 else 0.0,
        "average_execution_time": sum(execution_times) / len(execution_times) if execution_times else 0.0,
        "last_execution": last_execution
    }
```

### CLI統合パターン
```python
@app.command()
def hooks(
    action: str = typer.Argument("stats", help="Action: stats, log, clear"),
    lines: int = typer.Option(20, "--lines", "-n", help="Lines to show"),
) -> None:
    """Hooks管理コマンド."""
    if action == "stats":
        show_hooks_stats()
    elif action == "log":
        show_hooks_log(lines)
    elif action == "clear":
        clear_hooks_log()
    else:
        console.print(f"❌ Unknown action: {action}", style="red")
        sys.exit(1)

def show_hooks_stats() -> None:
    """統計情報表示."""
    from tool.utils.logger import get_hooks_stats
    from rich.table import Table
    
    stats = get_hooks_stats()
    
    if stats["total_executions"] == 0:
        console.print("No hooks executions found.")
        return
    
    table = Table(title="Hooks Execution Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Total Executions", str(stats["total_executions"]))
    table.add_row("Successful", str(stats["successful_executions"]))
    table.add_row("Failed", str(stats["failed_executions"]))
    table.add_row("Success Rate", f"{stats['success_rate']:.1f}%")
    table.add_row("Average Time", f"{stats['average_execution_time']:.2f}s")
    table.add_row("Last Execution", stats["last_execution"] or "Never")
    
    console.print(table)

def show_hooks_log(lines: int) -> None:
    """ログ表示."""
    log_file = Path.cwd() / ".tool" / "hooks.log"
    
    if not log_file.exists():
        console.print("No hooks log file found.")
        return
    
    console.print(f"📋 Last {lines} hooks log entries:", style="bold blue")
    
    try:
        with open(log_file, 'r') as f:
            log_lines = f.readlines()
        
        recent_lines = log_lines[-lines:] if len(log_lines) > lines else log_lines
        
        for line in recent_lines:
            line = line.strip()
            if line:
                if "ERROR" in line:
                    console.print(line, style="red")
                elif "WARNING" in line:
                    console.print(line, style="yellow")
                elif "SUCCESS" in line:
                    console.print(line, style="green")
                else:
                    console.print(line)
                    
    except Exception as e:
        console.print(f"❌ Error reading log: {e}", style="red")
```

### フォールバック実装パターン
```python
# Import防御的実装
try:
    from tool.utils.logger import get_hooks_logger, log_hooks_execution, log_hooks_start
except ImportError:
    # フォールバック実装
    import logging
    logging.basicConfig(level=logging.INFO)
    fallback_logger = logging.getLogger("tool.hooks.fallback")
    
    def log_hooks_start(file_path: str, command: str) -> None:
        fallback_logger.info(f"START | {file_path}")
    
    def log_hooks_execution(file_path: str, command: str, success: bool, 
                          execution_time: float, output: str = "", error: str = "") -> None:
        status = "SUCCESS" if success else "FAILED"
        fallback_logger.info(f"{status} | {file_path} | {execution_time:.2f}s")
        if output:
            fallback_logger.debug(f"Output: {output}")
        if error:
            fallback_logger.error(f"Error: {error}")
    
    def get_hooks_logger():
        return fallback_logger
```

### Working Directory管理パターン
```python
def safe_working_directory_change(target_dir: Path):
    """安全なワーキングディレクトリ変更."""
    original_cwd = os.getcwd()
    
    try:
        os.chdir(target_dir)
        yield target_dir
    finally:
        os.chdir(original_cwd)

# 使用例
def run_in_project_directory():
    """プロジェクトディレクトリでの実行."""
    project_dir = Path(__file__).parent.parent
    
    with safe_working_directory_change(project_dir):
        # この中でプロジェクトディレクトリでコマンド実行
        result = subprocess.run(["uv", "run", "tool", "check"])
        return result
```

このパターン集により、Claude Code hooksの統合が標準化され、他のプロジェクトでも再利用可能なログ記録・監視システムを構築できます。

## Claude Code Hooks統合 最終形態パターン

### ${file}変数問題の解決
**問題**: Claude Code hooks設定の`${file}`変数が期待通りに動作しない
```json
// ❌ 動作しない設定
"command": "uv run scripts/tool_hooks.py ${file}"
// エラー: Usage: tool_hooks.py <file_path>
```

**解決**: JSON stdin処理パターン
```python
#!/usr/bin/env python3
"""claude_hooks.py - JSON stdin処理統合スクリプト"""
import json
import sys
from pathlib import Path

def process_json_input() -> str | None:
    """Claude Code hooks JSON入力を処理してファイルパスを抽出."""
    try:
        hook_input = json.load(sys.stdin)
        tool_input = hook_input.get("tool_input", {})
        file_path = tool_input.get("file_path", "")
        return str(file_path) if file_path else None
    except (json.JSONDecodeError, KeyError):
        return None

def main() -> int:
    """メイン処理."""
    file_path_str = process_json_input()
    if not file_path_str:
        return 0  # JSON処理失敗時は正常終了
    
    file_path = Path(file_path_str)
    
    # Python ファイルのみ処理
    if file_path.suffix != '.py':
        return 0
    
    # PyQC品質チェック実行
    return run_quality_check(file_path)

if __name__ == "__main__":
    sys.exit(main())
```

### Git hooks統合パターン（最終形態）
```python
#!/usr/bin/env python3
"""git_hooks_detector.py - Git操作検知・品質保証"""
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess
import time

def is_git_commit_command(command: str) -> bool:
    """Gitコミットコマンドの検知."""
    patterns = [
        "git commit",
        "git commit -m", 
        "git commit --message",
        "git commit -am",
        "git commit --all --message"
    ]
    normalized = command.strip().replace('"', "").replace("'", "")
    return any(normalized.startswith(pattern) for pattern in patterns)

def run_parallel_quality_checks() -> tuple[bool, float]:
    """並列品質チェック（PyQC + pytest）."""
    def run_pyqc_check():
        result = subprocess.run(
            ["uv", "run", "pyqc", "check", "."],
            capture_output=True, text=True, timeout=30
        )
        return result.returncode == 0
    
    def run_pytest_check():
        result = subprocess.run(
            ["uv", "run", "pytest"],
            capture_output=True, text=True, timeout=30
        )
        return result.returncode == 0
    
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(run_pyqc_check),
            executor.submit(run_pytest_check)
        ]
        results = [future.result() for future in as_completed(futures)]
    
    execution_time = time.time() - start_time
    return all(results), execution_time

def main() -> int:
    """メイン処理."""
    try:
        hook_input = json.load(sys.stdin)
        tool_input = hook_input.get("tool_input", {})
        command = tool_input.get("command", "")
        
        # Gitコミットコマンドの検知
        if not is_git_commit_command(command):
            return 0  # 非Gitコマンドはスキップ
        
        logger.info(f"🔍 Git commit detected: {command}")
        
        # 並列品質チェック実行
        success, execution_time = run_parallel_quality_checks()
        
        if success:
            logger.info(f"🎉 All pre-commit checks passed! ({execution_time:.2f}s)")
            return 0
        else:
            logger.error(f"❌ Pre-commit checks failed ({execution_time:.2f}s)")
            return 1
            
    except Exception as e:
        logger.error(f"Error in git hooks detector: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

### 最終形態設定パターン
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "uv --directory /full/path/to/project run scripts/git_hooks_detector.py",
            "onFailure": "block",
            "timeout": 60000
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "uv --directory /full/path/to/project run scripts/claude_hooks.py",
            "onFailure": "warn",
            "timeout": 15000
          }
        ]
      }
    ]
  }
}
```

### フルパス要件の重要性
```bash
# ❌ 動作不安定（相対パス）
"command": "uv --directory pyqc run scripts/claude_hooks.py"

# ✅ 動作安定（フルパス）
"command": "uv --directory /home/user/project/pyqc run scripts/claude_hooks.py"
```

**重要**: Claude Code再起動後の設定保持には絶対パスが必須

### ログ分離パターン
```python
# ファイル編集時ログ
hooks_logger = setup_logger("pyqc_hooks", log_file=".pyqc/hooks.log")

# Git操作時ログ  
git_logger = setup_logger("git_hooks", log_file=".pyqc/git_hooks.log")

# 使用例
hooks_logger.info("🔍 PyQC check started: main.py") 
git_logger.info("🔍 Git commit detected: git commit -m 'fix'")
```

### AI開発特化設計原則
- **PostToolUse**: 非ブロッキング（onFailure: "warn"）
- **PreToolUse**: 品質ゲート（onFailure: "block"）
- **並列実行**: PyQC + pytest同時実行による時間短縮
- **適切なスキップ**: 非Python/非Gitコマンドの効率的な除外
- **包括的ログ**: 全操作の完全な記録と追跡

### 運用実績指標
```text
PostToolUse（ファイル編集時）: < 3秒
PreToolUse（Git pre-commit）: ~20秒（並列実行）
品質チェック成功率: 100%
Total issues: 0達成
```

この最終形態により、Claude CodeとPyQCが完全に統合され、AI時代の開発ワークフローに最適化された品質保証システムが実現されました。
```