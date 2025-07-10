# 技術的知見

## 開発ツール

### uv (パッケージ管理)
**学習内容:**
- `uv sync`: 依存関係解決と仮想環境作成
- `uv run`: コマンド実行（仮想環境自動活用）
- `uv add`: 依存関係追加
- `--extra dev`: オプショナル依存関係

**実践的知見:**
- pyproject.tomlベースの設定が効率的
- `uv run pytest` で即座にテスト実行可能
- VIRTUAL_ENV警告は無視して問題なし
- `uv sync --extra dev` で開発環境完全構築

### typer (CLI開発)
**学習内容:**
- `typer.Typer()`: アプリケーション作成
- `@app.command()`: コマンド定義
- `typer.Argument()`, `typer.Option()`: 引数定義
- Rich統合による美しい出力

**実践的知見:**
- `no_args_is_help=True` でヘルプ自動表示
- Richのconsole.print()で色付き出力
- 型ヒントによる自動バリデーション
- help文字列でドキュメント自動生成

### Pydantic (設定管理)
**学習内容:**
- `BaseModel`: 設定クラス定義
- 型ヒントによる自動バリデーション
- デフォルト値の設定
- ネストした設定構造

**実践的知見:**
- pyproject.tomlとの統合パターン
- 設定の階層化（RuffConfig, TypeCheckerConfig）
- クラスメソッドによるファクトリパターン
- `from __future__ import annotations` 必須

**エイリアス対応パターン:**
- `Field(alias="kebab-case")` でTOML形式対応
- `model_config = {"populate_by_name": True}` で両形式対応
- `model_validate(data, by_alias=True)` で読み込み時エイリアス適用

## アーキテクチャパターン

### プロジェクト構造
```
src/pyqc/
├── __init__.py          # パッケージエントリーポイント
├── cli.py               # CLI インターフェース
├── config.py            # 設定管理
├── checkers/            # チェッカーモジュール
│   ├── __init__.py
│   ├── ruff_checker.py
│   └── type_checker.py
└── utils/               # ユーティリティ
```

**設計原則:**
- 関心の分離（CLI, Config, Checkers）
- 依存性注入（設定をチェッカーに注入）
- プラグイン対応（checkers/ディレクトリ）

### テスト構造
```
tests/
├── unit/           # 単体テスト
├── integration/    # 統合テスト
└── fixtures/       # テストデータ
```

**テスト戦略:**
- typer.testing.CliRunner でCLIテスト
- モックによる外部依存分離
- fixturesによるテストデータ管理

## 依存関係の知見

### コア依存関係
- **typer**: CLI フレームワーク（Rich統合）
- **ruff**: リンター・フォーマッター
- **mypy**: 型チェッカー
- **pydantic**: 設定管理
- **rich**: 出力フォーマット
- **pyyaml**: YAML設定サポート
- **tomli-w**: TOML書き込み（Python 3.11+のtomlibは読み込みのみ）

### 開発依存関係
- **pytest**: テストフレームワーク
- **pytest-cov**: カバレッジ計測
- **pre-commit**: コミット前チェック

### 依存関係選択理由
- **typer over click**: Rich統合、型安全性
- **ruff over flake8/black**: 高速、統合環境
- **pydantic over dataclasses**: バリデーション、設定管理
- **uv over pip**: 高速、現代的ワークフロー

## パフォーマンス知見

### 実行時間最適化
- 並列実行: `concurrent.futures`
- キャッシュ: ファイルハッシュベース
- 増分チェック: 変更ファイルのみ

### メモリ最適化
- ストリーミング処理
- ジェネレーター活用
- 大ファイル分割処理

## 設定管理知見

### pyproject.toml統合
```toml
[tool.pyqc]
line-length = 88
type-checker = "mypy"

[tool.pyqc.ruff]
extend-select = ["I", "N", "UP"]
```

**パターン:**
- ツール固有セクション活用
- 既存ツール設定との共存
- 階層的設定構造

**TOMLネストセクション処理:**
- `[tool.pyqc.ruff]` は `{"tool": {"pyqc": {"ruff": {...}}}}` に自動変換
- 複雑な解析不要、標準tomlibで自然に処理される

### YAML設定サポート
```yaml
pyqc:
  line-length: 88
  ruff:
    extend-select: [I, N, UP]
```

**利点:**
- 複雑な設定の表現力
- コメント記述可能
- 既存YAML設定との統合

## エラーハンドリング知見

### カスタム例外設計
```python
class PyQCError(Exception):
    """Base exception"""

class ConfigurationError(PyQCError):
    """設定関連エラー"""
```

**原則:**
- 階層的例外クラス
- 具体的エラーメッセージ
- 解決方法の提示

### ユーザーフレンドリーなエラー
- 明確な問題の説明
- 修正方法の提案
- 関連ドキュメントへのリンク

## 外部プロセス実行知見

### subprocess実行パターン
```python
def run_external_tool(command: list[str], path: Path) -> subprocess.CompletedProcess[str]:
    """安全な外部ツール実行."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False  # 手動でエラーチェック
        )
    except FileNotFoundError as e:
        raise FileNotFoundError(f"{command[0]}: command not found") from e
    
    # 終了コード判定
    if result.returncode >= 2:
        raise RuntimeError(f"{command[0]} execution failed: {result.stderr}")
    
    return result
```

### 出力パーサー設計
**堅牢性の原則:**
- 空出力の適切な処理
- 不正JSON/テキストへの対応
- 複数行出力の正規表現解析
- ツールバージョン変更への耐性

**統一フォーマット:**
```python
class Issue:
    filename: str
    line: int
    column: int | None
    severity: str  # error, warning, info, note
    message: str
    code: str | None
    checker: str
    fixable: bool
```

### 結果集約パターン
**統一的な結果管理:**
- 複数チェッカーの結果をIssueクラスで統一
- 重要度別集計機能
- 修正可能問題の識別
- 実行時間・成功状態の追跡

## CI/CD統合知見

### GitHub Actions対応
- JSON形式出力
- アノテーション形式
- 終了コードによる判定

### pre-commit統合
- `language: system` による実行
- `types: [python]` によるフィルター
- local repo設定

## 学習リソース

### 公式ドキュメント
- [typer](https://typer.tiangolo.com/)
- [pydantic](https://docs.pydantic.dev/)
- [ruff](https://docs.astral.sh/ruff/)

### 実装参考
- [FastAPI](https://github.com/fastapi/fastapi) - typer使用例
- [ruff](https://github.com/astral-sh/ruff) - 実装パターン
- [mypy](https://github.com/python/mypy) - 型チェック統合