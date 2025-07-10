# サンプルプロジェクト要件

## 目的

プロジェクトの品質を管理する

- TDD
- リンター、フォーマッタ、型チェックを行う
- 常にログを残す
- 進捗を管理する

## キーワード、技術スタック

- Python3.12
- typer: コマンド
- pytest: テスト
- ruff: リンター、フォーマッタ
- mypy, ty: 型チェッカー、どちらを採用するかを要検討
- pre-commit: コミット前のチェック
- hooks: https://docs.anthropic.com/en/docs/claude-code/hooks#security-considerations
    - PostToolUse
    - Write|Edit|MultiEdit
    - フォーマット、リント、型チェックを行う
- vibe-logger: https://github.com/fladdict/vibe-logger