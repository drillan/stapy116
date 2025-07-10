# PyQC 実装ガイドライン

## TDD実践方針

### テスト戦略
1. **単体テスト優先**
   - 各チェッカーモジュールの独立したテスト
   - モックを使用した外部依存の分離
   - エッジケースの網羅的なテスト

2. **統合テスト**
   - 実際のPythonファイルを使用したE2Eテスト
   - 各種設定ファイルとの統合テスト
   - CLIコマンドの動作確認

3. **テストファイル構造**
   ```
   tests/
   ├── unit/
   │   ├── test_ruff_checker.py
   │   ├── test_type_checker.py
   │   └── test_config.py
   ├── integration/
   │   ├── test_cli.py
   │   └── test_hooks.py
   └── fixtures/
       ├── sample_project/
       └── config_files/
   ```

### テスト実装順序
1. 設定管理のテスト
2. 個別チェッカーのテスト
3. 統合実行のテスト
4. CLIインターフェースのテスト

## エラーハンドリング設計

### エラー分類
1. **ユーザーエラー**
   - 明確でアクションable なエラーメッセージ
   - 修正方法の提案
   - 関連ドキュメントへのリンク

2. **システムエラー**
   - 詳細なスタックトレース（デバッグモード時）
   - エラーコードによる分類
   - 自動リトライ機構（該当する場合）

3. **依存関係エラー**
   - 欠落している依存関係の明示
   - インストールコマンドの提示
   - 代替ツールの提案

### エラーメッセージ例
```python
class PyQCError(Exception):
    """Base exception for PyQC"""
    
class ConfigurationError(PyQCError):
    """設定ファイルに関するエラー"""
    def __init__(self, config_path: Path, issue: str):
        super().__init__(
            f"設定ファイルエラー: {config_path}\n"
            f"問題: {issue}\n"
            f"修正方法: uv run pyqc config init を実行するか、"
            f"https://docs.pyqc.dev/config を参照してください"
        )
```

## ログ出力方針

### ログレベル
1. **DEBUG**: 詳細な実行フロー
2. **INFO**: 主要な処理ステップ
3. **WARNING**: 非致命的な問題
4. **ERROR**: エラー情報

### 構造化ログ形式
```python
import structlog

logger = structlog.get_logger()

# 使用例
logger.info(
    "check_started",
    files_count=len(files),
    checker="ruff",
    config_path=str(config_path)
)
```

### vibe-logger統合（将来）
- セッション単位のログ管理
- 視覚的なログビューアー
- パフォーマンスメトリクス

## Claude Code Hooks設定

### 推奨設定
```json
{
  "hooks": {
    "PostToolUse": {
      "Write,Edit,MultiEdit": {
        "command": "uv run pyqc check ${file} --output github",
        "onFailure": "warn",
        "timeout": 5000
      }
    }
  }
}
```

### フック実装の考慮事項
1. **高速実行**
   - インクリメンタルチェック
   - キャッシュの活用
   - 必要最小限のチェック

2. **非ブロッキング**
   - エラー時も開発を継続可能
   - 警告レベルの調整可能

3. **コンテキスト認識**
   - 編集されたファイルのみチェック
   - 関連ファイルの影響を考慮

## コード品質基準

### コーディング規約
1. **型アノテーション**
   - すべての関数に型ヒント必須
   - `from __future__ import annotations`使用
   - 型エイリアスの活用

2. **ドキュメンテーション**
   - すべての公開APIにdocstringを推奨
   - スタイルは自由（Google Style、numpy styleなど）
   - 使用例の記載は任意

3. **エラー処理**
   - 明示的な例外処理
   - カスタム例外クラスの使用
   - リソースの適切なクリーンアップ

### パフォーマンス基準
1. **レスポンスタイム**
   - 単一ファイル: < 100ms
   - 100ファイル: < 3秒
   - 1000ファイル: < 30秒

2. **メモリ使用量**
   - ベースライン: < 50MB
   - 大規模プロジェクト: < 500MB

## セキュリティ考慮事項

### 入力検証
- パス traversal攻撃の防止
- 設定ファイルのサニタイゼーション
- コマンドインジェクションの防止

### 依存関係管理
- 最小限の依存関係
- セキュリティアップデートの追跡
- ライセンス互換性の確認

## 開発ワークフロー

### ブランチ戦略
```
main
├── develop
│   ├── feature/ruff-integration
│   ├── feature/type-checker
│   └── feature/cli-interface
└── release/v0.1.0
```

### コミットメッセージ規約
```
feat: Ruff統合を追加
fix: 型チェックエラーの修正
docs: CLI使用例を追加
test: Ruffチェッカーのテスト追加
refactor: 設定管理の再構築
```

### リリースプロセス
1. feature → develop へのマージ
2. develop → release ブランチ作成
3. リリースノート作成
4. タグ付けとuv publishでPyPIへの公開

## デバッグとトラブルシューティング

### デバッグモード
```bash
PYQC_DEBUG=1 uv run pyqc check
PYQC_PROFILE=1 uv run pyqc check  # パフォーマンスプロファイリング
```

### 一般的な問題と解決策
1. **インポートエラー**
   - PYTHONPATH確認
   - 仮想環境の確認

2. **パフォーマンス問題**
   - キャッシュクリア
   - 並列度の調整

3. **設定の競合**
   - 設定ファイルの優先順位確認
   - `uv run pyqc config show`で現在の設定確認