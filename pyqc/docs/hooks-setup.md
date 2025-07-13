# PyQC Hooks設定ガイド

PyQCは、Claude Code hooks と統合してコード品質を自動的にチェックできます。

**注意**: PyQCはv0.2.0よりClaude Code hooksに統合され、従来のpre-commit hooksは非推奨となりました。Claude Code hooksによりAI開発に最適化された統一的なhooks環境を提供します。

## Claude Code Hooks

Claude Codeのhooks機能を使用すると、ファイルの編集時とGitコミット時に自動的にPyQCチェックが実行されます。

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
           "command": "uv run python scripts/pyqc_hooks.py ${file}",
           "onFailure": "warn",
           "timeout": 15000
         }
       },
       "PreGitCommit": {
         "command": "uv run python scripts/git_pre_commit.py",
         "onFailure": "error",
         "timeout": 30000
       },
       "PostGitCommit": {
         "command": "uv run python scripts/git_post_commit.py",
         "onFailure": "warn",
         "timeout": 15000
       }
     }
   }
   ```

### 動作確認

**ファイル編集時（PostToolUse）**:
Claude Codeでファイルを編集すると、自動的にPyQCが実行され、GitHub Actions形式で結果が表示されます。

**Gitコミット時（PreGitCommit）**:
`git commit`実行時に包括的な品質チェック（PyQC + pytest）が自動実行されます。チェックが失敗するとコミットが阻止されます。

**Gitコミット後（PostGitCommit）**:
コミット完了後に品質統計とコミット情報がログに記録されます。

### カスタマイズ

- `onFailure`: エラー時の動作（`warn` または `error`）
- `timeout`: タイムアウト時間（ミリ秒）
- `--output github`: 出力形式の指定

## 従来のPre-commit Hooks（非推奨）

**⚠️ 非推奨**: 従来のpre-commit hooksはv0.2.0より非推奨となりました。Claude Code hooksをご利用ください。

~~Gitコミット時に自動的にPyQCチェックと包括的なテストを実行します。~~

### ~~設定方法~~（非推奨）

1. **~~pre-commitのインストール~~**:
   ```bash
   # 非推奨: uv add --dev pre-commit
   ```

2. **~~統合設定ファイルの作成~~**:
   
   自動設定:
   ```bash
   uv run pyqc init --with-pre-commit
   ```
   
   または `.pre-commit-config.yaml` を手動作成（推奨：完全統合版）:
   ```yaml
   repos:
     - repo: local
       hooks:
         - id: pyqc-check
           name: PyQC Quality Check
           entry: uv --directory pyqc run pyqc check
           language: system
           types: [python]
           pass_filenames: false
           always_run: true
           
         - id: pytest-check
           name: PyQC Test Suite
           entry: uv --directory pyqc run pytest
           args: [
             "--no-cov",             # カバレッジ無効化（速度優先）
             "--tb=short",           # 短いトレースバック表示
             "--maxfail=5",          # 5個失敗で停止（高速化）
             "-q",                   # 静かなモード（出力簡潔化）
             "--disable-warnings",   # 警告を無効化（速度優先）
             "-x",                   # 最初の失敗で停止（さらなる高速化）
             "-m", "not e2e"         # E2Eテスト除外（高速化）
           ]
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

## Git Hooks統合（新機能）

### Git Hooks概要

PyQCはClaude Code経由でGitコミットを検知し、pre-commit相当の処理を自動実行できます。

**主要機能:**
- **PreGitCommit**: コミット前の包括的品質チェック（PyQC + pytest並列実行）
- **PostGitCommit**: コミット後の統計記録とフィードバック
- **高速実行**: 並列処理により30秒以内での完了
- **専用ログ**: Git hooks専用のログファイル（`.pyqc/git_hooks.log`）

### Git Hooks設定例

```json
{
  "hooks": {
    "PreGitCommit": {
      "command": "uv run python scripts/git_pre_commit.py",
      "onFailure": "error",
      "timeout": 30000
    },
    "PostGitCommit": {
      "command": "uv run python scripts/git_post_commit.py", 
      "onFailure": "warn",
      "timeout": 15000
    }
  }
}
```

### Git Hooks実行フロー

#### Pre-commit処理
1. **並列品質チェック**:
   - PyQC check（全ファイル、GitHub Actions形式）
   - pytest（最適化済み: `--no-cov -x -m "not e2e"`）
2. **結果表示**:
   - GitHub Actions形式での問題報告
   - 失敗時はコミット阻止
3. **パフォーマンス**:
   - 目標: 30秒以内での完了
   - 並列実行による高速化

#### Post-commit処理
1. **コミット情報収集**:
   - コミットハッシュ、メッセージ、作者
   - 変更ファイル数の統計
2. **品質チェック**:
   - 変更ファイルのみを対象とした高速チェック
3. **統計記録**:
   - `.pyqc/git_hooks.log`への詳細ログ
   - パフォーマンスメトリクス記録

### Git Hooks統計確認

```bash
# Git hooks統計表示（将来実装予定）
uv run pyqc git-hooks stats

# Git hooksログ表示（将来実装予定）
uv run pyqc git-hooks log
```

## Claude Code Hooks 実行ログとモニタリング

### ログ記録機能

PyQCのClaude Code hooksは詳細な実行ログを記録します：

**ログファイル場所**: `.pyqc/hooks.log`

**記録内容**:
- 実行日時とファイルパス
- 実行コマンドと引数
- 実行時間（パフォーマンス情報）
- 成功/失敗ステータス
- 詳細なエラー情報

### ログ確認コマンド

#### 統計情報表示
```bash
uv run pyqc hooks stats
```
実行回数、成功率、平均実行時間を表示

#### ログ履歴表示
```bash
# 最新20行を表示
uv run pyqc hooks log

# 最新50行を表示
uv run pyqc hooks log --lines 50
```

#### ログクリア
```bash
uv run pyqc hooks clear
```

### 実行例

#### Claude Code hooks による自動実行
```
🚀 PyQC hooks starting - processing 1 file(s)
🔍 Starting PyQC quality check for src/pyqc/cli.py
✅ PyQC check completed successfully for src/pyqc/cli.py (0.98s)
🎉 All PyQC hooks completed successfully
```

#### 統計情報表示例
```
📊 Claude Code Hooks Statistics
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Metric           ┃ Value                   ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Total Executions │ 15                      │
│ Successful       │ 14                      │
│ Failed           │ 1                       │
│ Success Rate     │ 93.3%                   │
│ Average Time     │ 1.2s                    │
│ Last Execution   │ 2025-07-10 14:21:49,576 │
└──────────────────┴─────────────────────────┘
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

### AI時代の開発フロー

1. **Claude Code hooks**: 編集時の即座のフィードバック（< 10秒）
2. **Pre-commit hooks**: PyQC + pytest統合による包括的品質保証（< 30秒）
3. **CI/CD**: 完全なテストスイートとカバレッジレポート

#### 実測パフォーマンス
```bash
# 最適化されたpre-commit実行時間
PyQC Quality Check.......................................Passed (2.1s)
PyQC Test Suite.........................................Passed (9.9s)
Total execution time: ~11.3 seconds
```

### パフォーマンス最適化

#### pytest高速実行のための最適化
- **カバレッジ無効化**: `--no-cov` で約50%高速化
- **早期終了**: `-x` で最初の失敗時に停止
- **テスト除外**: `-m "not e2e"` でE2Eテスト除外
- **出力簡潔化**: `-q` で冗長な出力を抑制

#### 品質チェック最適化
- **並列実行**: PyQC内蔵の並列処理活用
- **特定チェック**: 必要に応じて `--lint` や `--types` のみ実行
- **キャッシュ活用**: PyQCの将来バージョンで対応予定

### AI開発における運用指針

#### Dogfooding原則
- **自己適用**: PyQC自身がPyQCとpytestを通ること
- **ゼロトレラント**: 品質ツール自体に品質問題があってはならない
- **継続改善**: PyQCの知見でPyQC自体を改善

#### エラーハンドリング戦略
```bash
# 品質問題が見つかった場合の対処フロー
1. PyQC自動修正: uv run pyqc fix .
2. 手動修正確認: uv run pyqc check .
3. テスト実行: uv run pytest --no-cov -x
4. 統合確認: pre-commit run --all-files
```

#### AI-specific考慮事項
- **高頻度コミット**: AI生成コードの頻繁なコミットに対応
- **予測不可能なエラー**: AI特有のバグパターンに対応
- **客観的品質指標**: 人間の主観に依存しない品質評価

### トラブルシューティング

#### Claude Code hooksが動作しない

1. Claude Codeを再起動
2. `.claude/hooks.json` の構文を確認
3. PyQCがインストールされていることを確認

#### Pre-commit hooksが失敗する

1. `uv run pre-commit run --verbose` で詳細確認
2. PyQC単体で動作確認: `uv run pyqc check`
3. Python環境の確認: `uv run which python`

#### pytest統合で発生する一般的な問題

**pytest実行が遅い**
```bash
# 問題：E2Eテストも含めて実行している
# 解決：マーカーでテスト除外
pytest -m "not e2e" --no-cov -x
```

**pytest警告が表示される**
```bash
# 問題：未定義のマーカー使用
# 解決：pyproject.tomlにマーカー定義を追加
[tool.pytest.ini_options]
markers = [
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
    "e2e: marks tests as end-to-end tests"
]
```

**ファイル名衝突エラー**
```bash
# 問題：import file mismatch
# 解決：テストファイル名の重複を避ける
# tests/test_cli.py と tests/integration/test_cli.py の同時存在を避ける
```

#### パフォーマンス問題の診断

**pre-commit実行時間の測定**
```bash
time pre-commit run --all-files
# 目標：< 30秒（AI開発に適した速度）
```

**個別コンポーネントの性能測定**
```bash
# PyQC単体
time uv run pyqc check .

# pytest単体  
time uv run pytest --no-cov -x -m "not e2e"
```

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