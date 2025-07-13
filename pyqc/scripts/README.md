# PyQC Scripts Directory

This directory contains utility scripts for PyQC Claude Code hooks integration.

## Scripts

### `claude_hooks.py` (統合スクリプト)

**メインのClaude Code hooks統合スクリプト**。JSON入力を処理し、PyQC品質チェックを実行します。

**機能:**
- JSON入力からファイルパス自動抽出
- 統合されたPyQC品質チェック実行
- 非Pythonファイルの適切なスキップ
- 包括的なログ記録とエラーハンドリング
- AI開発ワークフロー最適化

**使用方法:**
```bash
# 手動実行（デバッグ用）
echo '{"tool_input":{"file_path":"/path/to/file.py"}}' | uv run scripts/claude_hooks.py

# Claude hooks経由（自動実行）
# Python ファイル編集時に自動実行
```

### `git_hooks_detector.py` (Git統合)

**Gitコミット検知・品質保証スクリプト**。Bashコマンドを監視し、Git操作時に包括的品質チェックを実行します。

**機能:**
- Gitコミットコマンドの自動検知
- pre-commit品質チェック（PyQC + pytest並列実行）
- post-commit処理とログ記録
- 非Gitコマンドの適切なスキップ
- 高頻度コミット環境への最適化

**使用方法:**
```bash
# 通常のGitコミット時に自動実行
git commit -m "commit message"

# 手動実行（デバッグ用）
echo '{"tool_input":{"command":"git commit -m test"}}' | uv run scripts/git_hooks_detector.py
```

### `pyqc_hooks.py` (レガシー)

**従来の引数ベースhooksスクリプト**。新しい統合方式移行後も互換性のために維持。

**使用方法:**
```bash
# 直接実行
uv run scripts/pyqc_hooks.py <file_path>
```

## Claude Code Hooks統合

### 最終形態設定

`.claude/settings.json`の推奨設定：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "uv --directory /path/to/pyqc run scripts/git_hooks_detector.py",
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
            "command": "uv --directory /path/to/pyqc run scripts/claude_hooks.py",
            "onFailure": "warn",
            "timeout": 15000
          }
        ]
      }
    ]
  }
}
```

### 実行フロー

#### 1. ファイル編集時（PostToolUse）
1. Claude Codeがファイル編集を検知
2. JSONデータを`claude_hooks.py`にstdin経由で送信
3. ファイルパスを抽出してPyQC品質チェックを実行
4. 結果をログに記録

#### 2. Gitコミット時（PreToolUse）
1. Claude CodeがBashコマンド（`git commit`）を検知
2. `git_hooks_detector.py`がGitコマンドか判定
3. pre-commit品質チェック（PyQC + pytest並列実行）
4. 成功時のみコミット許可、post-commit処理実行

## ログとモニタリング

### ログファイル

- **`.pyqc/hooks.log`**: PostToolUse hooks（ファイル編集）のログ
- **`.pyqc/git_hooks.log`**: PreToolUse hooks（Git操作）のログ

### ログ内容例

```
2025-07-13 16:53:24,492 | 🔍 Git commit detected: git commit -m "feat: 新機能追加"
2025-07-13 16:53:27,536 | ✅ pyqc check completed
2025-07-13 16:53:44,540 | ✅ pytest check completed  
2025-07-13 16:53:44,552 | 🎉 All pre-commit checks passed! (20.04s)
```

## AI開発最適化

### 高頻度コミット対応

- **並列実行**: PyQC + pytest同時実行で時間短縮
- **スキップ機能**: 非Pythonファイル・非Gitコマンドの適切なスキップ
- **タイムアウト管理**: 適切なタイムアウト設定でブロック回避
- **非ブロッキング**: ファイル編集時は警告レベルで継続可能

### パフォーマンス

- **PostToolUse**: ファイル編集時 < 3秒
- **PreToolUse**: Git pre-commit < 30秒（目標20秒）
- **キャッシュ活用**: PyQCの内蔵キャッシュで高速化

## トラブルシューティング

### 一般的な問題

1. **パス問題**: フルパス指定で解決（`/home/driller/repo/stapy116/pyqc`）
2. **権限エラー**: `uv run`使用で実行権限不要
3. **JSON解析エラー**: stdin入力の確認
4. **タイムアウト**: 大規模プロジェクトでの設定調整

### デバッグ方法

```bash
# 品質チェック状況確認
uv run pyqc check .

# hooks ログ確認  
tail -f .pyqc/hooks.log
tail -f .pyqc/git_hooks.log

# 手動Git hooks テスト
echo '{"tool_input":{"command":"git status"}}' | uv run scripts/git_hooks_detector.py
```

## 最適化のポイント

### 開発ワークフロー統合

- **リアルタイム品質保証**: ファイル編集時の即座なフィードバック
- **コミット時品質ゲート**: 包括的なpre-commit検証
- **非干渉設計**: 通常の開発作業をブロックしない
- **ログベース追跡**: 全操作の完全な記録

### AI開発特有の考慮事項

- **高頻度操作対応**: AI編集による頻繁なファイル変更に対応
- **自動品質管理**: 人間の品質チェック負荷を軽減
- **客観的品質指標**: 機械的な品質測定による一貫性
- **迅速なフィードバック**: AI開発の高速イテレーションサイクルに対応

この統合システムにより、Claude CodeとPyQCが完全に統合され、AI時代の開発ワークフローに最適化された品質保証システムが実現されます。