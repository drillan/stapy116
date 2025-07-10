# PyQC Hooks設定ガイド

PyQCは、Claude CodeおよびGitの pre-commit hooks と統合して、コード品質を自動的にチェックできます。

## Claude Code Hooks

Claude Codeのhooks機能を使用すると、ファイルの編集時に自動的にPyQCチェックが実行されます。

### 設定方法

1. **自動設定（推奨）**:
   ```bash
   uv run pyqc init --with-hooks
   ```

2. **手動設定**:
   `.claude/hooks.json` ファイルを作成:
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

### 動作確認

Claude Codeでファイルを編集すると、自動的にPyQCが実行され、GitHub Actions形式で結果が表示されます。

### カスタマイズ

- `onFailure`: エラー時の動作（`warn` または `error`）
- `timeout`: タイムアウト時間（ミリ秒）
- `--output github`: 出力形式の指定

## Pre-commit Hooks

Gitコミット時に自動的にPyQCチェックを実行します。

### 設定方法

1. **pre-commitのインストール**:
   ```bash
   uv add --dev pre-commit
   ```

2. **設定ファイルの作成**:
   
   自動設定:
   ```bash
   uv run pyqc init --with-pre-commit
   ```
   
   または `.pre-commit-config.yaml` を手動作成:
   ```yaml
   repos:
     - repo: local
       hooks:
         - id: pyqc-check
           name: PyQC Check
           entry: uv run python -m pyqc check
           language: system
           types: [python]
           pass_filenames: false
           always_run: true
   ```

3. **Git hooksのインストール**:
   ```bash
   uv run pre-commit install
   ```

### 動作確認

```bash
# 手動実行
uv run pre-commit run --all-files

# Git commit時に自動実行
git add .
git commit -m "Your commit message"
```

### 高度な設定

#### 特定のチェックのみ実行

```yaml
- id: pyqc-lint-only
  name: PyQC Lint Check
  entry: uv run python -m pyqc check --lint
  language: system
  types: [python]
```

#### 自動修正の追加

```yaml
- id: pyqc-fix
  name: PyQC Auto Fix
  entry: uv run python -m pyqc fix
  language: system
  types: [python]
  pass_filenames: false
```

## ベストプラクティス

### 開発フロー

1. **Claude Code hooks**: 編集時の即座のフィードバック
2. **Pre-commit hooks**: コミット前の最終チェック
3. **CI/CD**: プルリクエストでの完全なチェック

### パフォーマンス最適化

- **並列実行**: `parallel: true` を設定で有効化
- **特定チェック**: 必要なチェックのみ実行
- **キャッシュ活用**: PyQCの将来バージョンで対応予定

### トラブルシューティング

#### Claude Code hooksが動作しない

1. Claude Codeを再起動
2. `.claude/hooks.json` の構文を確認
3. PyQCがインストールされていることを確認

#### Pre-commit hooksが失敗する

1. `uv run pre-commit run --verbose` で詳細確認
2. PyQC単体で動作確認: `uv run pyqc check`
3. Python環境の確認: `uv run which python`

## 統合例

### GitHub Actions

```yaml
name: PyQC Check

on: [push, pull_request]

jobs:
  pyqc:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - run: pip install uv
      - run: uv sync
      - run: uv run pyqc check --output github
```

### VS Code統合

`.vscode/settings.json`:
```json
{
  "terminal.integrated.env.osx": {
    "PYQC_CONFIG": "${workspaceFolder}/pyproject.toml"
  },
  "python.linting.enabled": true
}
```

## まとめ

PyQCのhooks統合により、開発フロー全体で一貫した品質チェックが可能になります。Claude Codeでの編集時、Gitコミット時、CI/CDパイプラインで同じ品質基準を適用できます。