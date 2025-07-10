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
```