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

### サブプロセス実行
```python
import subprocess
from pathlib import Path
from typing import Any

def run_command(
    command: list[str], 
    cwd: Path | None = None,
    capture_output: bool = True
) -> subprocess.CompletedProcess[str]:
    """コマンド実行."""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=capture_output,
            text=True,
            check=False  # 手動でチェック
        )
        return result
    except FileNotFoundError:
        raise ExecutionError(f"コマンドが見つかりません: {command[0]}")

# 使用例
def run_ruff(path: Path) -> dict[str, Any]:
    """Ruff実行."""
    result = run_command(["ruff", "check", "--output-format=json", str(path)])
    
    if result.returncode != 0 and result.returncode != 1:
        # 0: 問題なし, 1: リントエラーあり, その他: 実行エラー
        raise ExecutionError(f"Ruff実行エラー: {result.stderr}")
    
    import json
    return json.loads(result.stdout) if result.stdout else []
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
```