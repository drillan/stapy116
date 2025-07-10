# PyQC - Python Quality Checker

統合されたPythonコード品質チェック・修正ツール。Claude Codeの実践的アプローチのサンプルプロジェクト。

## 特徴

- **統合チェック**: ruff（リント・フォーマット）とmypy/ty（型チェック）を統合
- **自動修正**: 一般的なコード品質問題を自動修正
- **柔軟な設定**: pyproject.toml、YAML設定ファイルをサポート
- **CI/CD統合**: GitHub Actions形式出力、pre-commit hooksサポート
- **高速実行**: 並列チェックによるパフォーマンス最適化
- **Claude Code hooks**: リアルタイム品質チェック

## インストール

PyQCはPyPIに登録されていないため、GitHubから直接インストールする必要があります。

### 一般ユーザー向け（推奨）

```bash
# uvを使用（推奨）
uv add git+https://github.com/drillan/stapy116.git#subdirectory=pyqc

# pipを使用
uv pip install git+https://github.com/drillan/stapy116.git#subdirectory=pyqc
```

### 開発者向け

```bash
# リポジトリをクローン
git clone https://github.com/drillan/stapy116.git
cd stapy116/pyqc

# uvを使用（推奨）
uv sync
uv run pyqc --help

# pipを使用（editable install）
uv pip install -e .
```

### stapy116プロジェクト内での利用

```bash
# stapy116リポジトリ内で直接実行
git clone https://github.com/drillan/stapy116.git
cd stapy116
uv --directory pyqc run pyqc check
```

## クイックスタート

```bash
# コード品質チェック
uv run pyqc check

# 自動修正可能な問題を修正
uv run pyqc fix

# プロジェクトに初期化
uv run pyqc init --with-pre-commit --with-hooks
```

## サンプルプロジェクトでの試用

PyQCの機能を簡単に試すために、サンプルプロジェクトが用意されています。使用方法は、PyQCのインストール状況に応じて選択してください。

### パターン1: PyQCをインストール済みの場合（推奨）

```bash
# リポジトリをクローン（サンプルファイル取得のため）
git clone https://github.com/drillan/stapy116.git
cd stapy116

# サンプルプロジェクトをチェック
pyqc check pyqc/sample_project/

# 自動修正を試す
pyqc fix pyqc/sample_project/ --dry-run
```

### パターン2: stapy116リポジトリ内で開発する場合

```bash
# リポジトリをクローン
git clone https://github.com/drillan/stapy116.git
cd stapy116

# サンプルプロジェクトをチェック
uv --directory pyqc run pyqc check sample_project/

# 自動修正を試す
uv --directory pyqc run pyqc fix sample_project/ --dry-run
```

### ステップバイステップチュートリアル

以下の例は**パターン1（インストール済み）**で説明します。パターン2の場合は`pyqc`を`uv --directory pyqc run pyqc`に読み替えてください。

#### 1. 品質チェックの実行

```bash
# テキスト形式でチェック（デフォルト）
pyqc check pyqc/sample_project/
```

**期待される出力**:
```
🔍 Checking 1 Python file(s)...
✅ sample_project/example.py: 0 issues
```

#### 2. 異なる出力形式の確認

```bash
# JSON形式
pyqc check pyqc/sample_project/ --output json

# GitHub Actions形式
pyqc check pyqc/sample_project/ --output github
```

#### 3. 自動修正の確認

```bash
# ドライラン（実際の修正は行わない）
pyqc fix pyqc/sample_project/ --dry-run

# 実際の修正
pyqc fix pyqc/sample_project/
```

#### 4. 設定の確認

```bash
# 現在の設定を表示
pyqc config show
```

### 学習目的での活用

`sample_project/example.py` は以下の学習に活用できます：

1. **品質チェックの理解**
   - どのような問題が検出されるか
   - エラーメッセージの読み方

2. **自動修正の体験**
   - どの問題が自動修正されるか
   - 修正前後のコード比較

3. **出力形式の確認**
   - テキスト、JSON、GitHub Actions形式の違い
   - CI/CDでの活用方法の理解

4. **設定のカスタマイズ**
   - pyproject.tomlでの設定変更
   - 独自ルールの追加方法

## コマンド

### `pyqc check`
品質チェックを実行

```bash
# 基本的な使用法
uv run pyqc check

# 特定のパスをチェック
uv run pyqc check src/

# 出力形式の指定
uv run pyqc check --output json
uv run pyqc check --output github  # GitHub Actions用

# 特定のチェックのみ
uv run pyqc check --lint          # リントのみ
uv run pyqc check --types         # 型チェックのみ
uv run pyqc check --format        # フォーマットチェックのみ
```

### `pyqc fix`
自動修正を実行

```bash
# 基本的な修正
uv run pyqc fix

# ドライラン（プレビューのみ）
uv run pyqc fix --dry-run

# バックアップ付きで修正
uv run pyqc fix --backup
```

### `pyqc config`
設定管理

```bash
# 現在の設定を表示
uv run pyqc config show

# 設定を変更
uv run pyqc config set line_length 100
uv run pyqc config set type_checker ty
```

### `pyqc init`
プロジェクト初期化

```bash
# 基本的な初期化
uv run pyqc init

# pre-commit設定も生成
uv run pyqc init --with-pre-commit

# Claude Code hooks設定も生成
uv run pyqc init --with-hooks

# 型チェッカーを指定
uv run pyqc init --type-checker ty
```

## 設定

### pyproject.toml
```toml
[tool.pyqc]
line_length = 88
type_checker = "mypy"  # または "ty"
parallel = true

[tool.pyqc.ruff]
extend_select = ["I", "N", "UP"]
ignore = ["E501"]

[tool.pyqc.mypy]
strict = true
ignore_missing_imports = true
```

### .pyqc.yaml
```yaml
pyqc:
  line_length: 88
  type_checker: "mypy"
  ruff:
    extend_select: ["I", "N", "UP"]
    ignore: ["E501"]
  mypy:
    strict: true
    ignore_missing_imports: true
```

## Claude Code統合

### hooksファイル設定

`.claude/hooks.json`を作成：
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

**重要**: `${file}`変数により、編集されたファイルのパスが自動的に渡されます。

### pre-commit設定
```yaml
repos:
  - repo: local
    hooks:
      - id: pyqc-check
        name: PyQC Quality Check
        entry: uv run pyqc check
        language: system
        types: [python]
```

## 出力形式

### Text形式（デフォルト）
```
PyQC Report
===========
Total files checked: 15
Issues found: 3

src/main.py:10:1: E501 Line too long (92 > 88 characters)
src/utils.py:5:1: F401 'os' imported but unused
```

### JSON形式
```bash
uv run pyqc check --output json
```

### GitHub Actions形式
```bash
uv run pyqc check --output github
```

## パフォーマンス

- **並列実行**: CPUコア数に基づく自動スケーリング
- **キャッシュ機能**: ファイルハッシュベースのキャッシュ
- **インクリメンタルチェック**: 変更されたファイルのみチェック

## プロジェクト構造

PyQCは[stapy116](https://github.com/drillan/stapy116)リポジトリのサブプロジェクトとして開発されています：

```
stapy116/
├── pyproject.toml          # stapy116プレゼンテーション用
├── docs/                   # sphinx-revealjsプレゼンテーション
├── pyqc/                   # PyQCプロジェクト
│   ├── pyproject.toml      # PyQC本体の設定
│   ├── src/pyqc/           # PyQCソースコード
│   ├── tests/              # テストコード
│   └── README.md           # このファイル
└── plans/                  # 実装計画管理
```

この構成により、PyQCの開発過程とプレゼンテーション資料を一つのリポジトリで管理しています。

## 開発ステータス

このプロジェクトはClaude Codeの実践的アプローチを示すMVP（Minimum Viable Product）実装です。

**実装済み機能**:
- ✅ 統合品質チェック（ruff + mypy/ty）
- ✅ 自動修正機能
- ✅ 設定管理システム
- ✅ CLI インターフェース
- ✅ 並列実行
- ✅ Claude Code hooks統合
- ✅ pre-commit hooks統合

**計画中の機能**:
- 📋 プラグインシステム
- 📋 AI統合レビュー
- 📋 パフォーマンス監視
- 📋 Web UI

## 技術スタック

- **言語**: Python 3.12+
- **CLI**: typer + rich
- **品質ツール**: ruff, mypy/ty
- **設定**: pydantic + tomllib/yaml
- **テスト**: pytest（カバレッジ: 75%）

## Claude Code実践例

このプロジェクトは「Claude Codeの実践的アプローチ」の3つのポイントを実装しています：

1. **計画・設計を立てる**
   - 構造化されたプロジェクト計画
   - 段階的な実装フェーズ
   - 明確な仕様書と実装ガイドライン

2. **記録を残す**
   - 包括的なドキュメント
   - 実装ノートと意思決定記録
   - 進捗ログとマイルストーン

3. **堅牢なコードを書く**
   - TDD（テスト駆動開発）
   - 自動品質チェック
   - CI/CD統合

## ライセンス

MIT