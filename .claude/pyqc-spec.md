# PyQC 詳細仕様書

## 概要
PyQC (Python Quality Checker) は、Pythonプロジェクトの品質を統合的に管理するCLIツールです。

## 機能仕様

### 1. 品質チェック機能

#### 1.1 Ruffチェッカー
**機能:**
- PEP 8準拠のコードスタイルチェック
- 一般的なコーディングエラーの検出
- インポート順序の検証
- 未使用変数・インポートの検出

**設定オプション:**
- `--extend-select`: 追加ルールの有効化
- `--ignore`: 特定ルールの無効化
- `--line-length`: 最大行長の設定（デフォルト: 88）

#### 1.2 型チェッカー
**機能:**
- 静的型チェック（mypy/ty選択可能）
- 型アノテーションの完全性チェック
- 型の不整合検出

**設定オプション:**
- `--type-checker`: mypy/tyの選択
- `--strict`: 厳密モードの有効化
- `--ignore-missing-imports`: 欠落インポートの無視

#### 1.3 フォーマッター
**機能:**
- Ruff formatによる自動フォーマット
- Black互換のフォーマットスタイル
- インポート文の自動整理

### 2. 自動修正機能

**対象:**
- フォーマット違反
- インポート順序
- 未使用インポートの削除
- 簡単なリント違反

**安全性:**
- 破壊的変更の事前確認
- バックアップオプション
- dry-runモード

### 3. Hooks統合

#### 3.1 Claude Code Hooks
```json
{
  "hooks": {
    "PostToolUse": {
      "Write,Edit,MultiEdit": "uv run pyqc check --format github"
    }
  }
}
```

#### 3.2 Pre-commit設定
```yaml
repos:
  - repo: local
    hooks:
      - id: pyqc
        name: PyQC Check
        entry: uv run pyqc check
        language: system
        types: [python]
```

## CLI仕様

### コマンド構造

```bash
uv run pyqc [OPTIONS] COMMAND [ARGS]...

Commands:
  check    品質チェックを実行
  fix      自動修正を実行
  config   設定管理
  init     プロジェクト初期化
```

### 詳細コマンド

#### `pyqc check`
```bash
Usage: uv run pyqc check [OPTIONS] [PATH]

Options:
  --all                    すべてのチェックを実行（デフォルト）
  --lint                   リントチェックのみ
  --types                  型チェックのみ
  --format                 フォーマットチェックのみ
  --output FORMAT          出力形式 [text|json|github]
  --no-cache              キャッシュを使用しない
  --parallel              並列実行（デフォルト）
  --config FILE           設定ファイルを指定
```

#### `pyqc fix`
```bash
Usage: uv run pyqc fix [OPTIONS] [PATH]

Options:
  --dry-run               変更をプレビューのみ
  --backup                変更前にバックアップ作成
  --unsafe                安全でない修正も実行
  --format-only           フォーマットのみ修正
```

#### `pyqc config`
```bash
Usage: uv run pyqc config [OPTIONS] COMMAND

Commands:
  show     現在の設定を表示
  set      設定値を変更
  init     設定ファイルを初期化

Options:
  --global    グローバル設定を操作
  --local     ローカル設定を操作
```

#### `pyqc init`
```bash
Usage: uv run pyqc init [OPTIONS]

Options:
  --with-pre-commit       pre-commit設定も生成
  --with-hooks           Claude Code hooks設定も生成
  --type-checker CHOICE   使用する型チェッカー [mypy|ty]
```

### 出力フォーマット

#### Text形式（デフォルト）
```
PyQC Report
===========
Total files checked: 15
Issues found: 3

src/main.py:10:1: E501 Line too long (92 > 88 characters)
src/utils.py:5:1: F401 'os' imported but unused
tests/test_main.py:20:5: Type error: Expected str, got int

Summary: 2 lint issues, 1 type error
```

#### JSON形式
```json
{
  "summary": {
    "files_checked": 15,
    "total_issues": 3,
    "lint_issues": 2,
    "type_errors": 1
  },
  "issues": [
    {
      "file": "src/main.py",
      "line": 10,
      "column": 1,
      "code": "E501",
      "message": "Line too long (92 > 88 characters)",
      "severity": "warning"
    }
  ]
}
```

#### GitHub Actions形式
```
::warning file=src/main.py,line=10,col=1::Line too long (92 > 88 characters)
::error file=tests/test_main.py,line=20,col=5::Type error: Expected str, got int
```

## 設定ファイル

### pyproject.toml
```toml
[tool.pyqc]
line-length = 88
type-checker = "mypy"

[tool.pyqc.ruff]
extend-select = ["I", "N", "UP"]
ignore = ["E501"]

[tool.pyqc.mypy]
strict = true
ignore_missing_imports = true
```

### .pyqc.yaml（代替形式）
```yaml
pyqc:
  line-length: 88
  type-checker: mypy
  parallel: true
  
  ruff:
    extend-select: [I, N, UP]
    ignore: [E501]
    
  mypy:
    strict: true
    ignore_missing_imports: true
```

## エラーコード体系

### PyQC固有コード
- `QC001`: 設定ファイルエラー
- `QC002`: 依存関係エラー
- `QC003`: 実行権限エラー

### 終了コード
- `0`: エラーなし
- `1`: チェックエラーあり
- `2`: 実行エラー
- `3`: 設定エラー

## パフォーマンス仕様

### キャッシュ戦略
- ファイルハッシュベースのキャッシュ
- `.pyqc_cache/`ディレクトリに保存
- 7日間で自動クリーンアップ

### 並列実行
- CPUコア数に基づく自動スケーリング
- ファイル単位での並列処理
- 大規模プロジェクト対応（1000+ファイル）

## 拡張性

### プラグインインターフェース（将来実装）
```python
from pyqc import CheckerPlugin

class CustomChecker(CheckerPlugin):
    name = "custom"
    
    def check(self, file_path: Path) -> List[Issue]:
        # カスタムチェックロジック
        pass
```

### 統合ポイント
- カスタムチェッカー
- カスタムフォーマッター
- カスタム出力形式
- 外部ツール連携