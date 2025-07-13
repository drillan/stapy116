# PythonエンジニアのためのAI協働開発

Claude Code活用術

[みんなのPython勉強会#116](https://startpython.connpass.com/event/361667/)

driller[@patrqushe](https://x.com/patraqushe) 2025-07-17

## 注意事項

- AIエディタは日々進化しており、本内容が陳腐化する可能性があります
- 発表者個人の経験による主観や感想が含まれています
- 各プロジェクトの特性に合わせて調整してください

## [Claude Code](https://docs.anthropic.com/en/docs/claude-code)とは

AnthropicのClaude AIを活用したCLIツール

- コーディング専用に設計されたAIエディタ
- ターミナルから直接利用可能
- プロジェクト全体を理解した開発支援
- 自律的なコード生成・編集・テスト実行

### Claude Codeのできること、できないこと

::::{grid}
:gutter: 2

:::{grid-item-card}
簡単にできること
^^^

「テトリス作って」

- 単一機能の実装
- 明確な仕様の小規模プロジェクト
- 即座の実行と確認が可能
:::

:::{grid-item-card}
簡単にはできないこと
^^^

「航空機の予約システムを作って」

- 複雑なビジネスロジック
- 多数のコンポーネント統合
- 企業レベルの要件
:::
::::

### 違いは何か

複雑さとスコープの違い

- 単純なタスク vs 複雑なシステム
- 明確な要件 vs 曖昧な要求
- 即座の実行 vs 長期的な計画

### 実践的アプローチの必要性

複雑なタスクには体系的な手法が必要

- 計画・設計の立案
- 知識の記録と蓄積
- 高品質なコード実装

### 開発アプローチの変遷

シンプルなプロンプトから体系的なアプローチへ移行

### Vibe Codingの特徴

優秀な料理の助手として

- 直感的な対話型開発
- 自然言語での即座生成
- プロトタイプ向け
- 品質管理に限界

「さっぱりした和食のイメージで」といった抽象的指示

### Agentic Codingの特徴

ベテランシェフとして

- 自律的な目標達成
- 計画から実行まで自動化
- 企業レベル対応
- 監督者への役割変化

「顧客満足度を上げる新作メニュー開発」といった高レベル目標

### 従来アプローチの限界

- 複雑な要求に対応困難
- 品質担保が困難
- 管理性の欠如

## 3つのポイント

- 計画・設計を立てる
- 記録を残す
- 高品質なコードを書く

## 計画・設計を立てる

### こんなことはありませんか？

- ユーザの意図と違うことをしている
- 思いつきのようにあらたな機能が追加される
- いつの間にか違う方向に進んでいる

### 計画・設計の重要性

- 自律的な開発を成功させるための重要な要素
- AIが長時間一貫した判断を下すには明確な指針が必要
- 複雑なタスクを検証可能な単位に分解

### [plan mode](https://docs.anthropic.com/en/docs/claude-code/common-workflows#planning-mode)の活用

Shift + Tabで計画モードに切り替え

- 複雑なタスクの事前計画立案
- 実装前の設計検討とリスク評価
- ユーザー承認を経てから実装開始

### plan modeの特徴

コードを書かずに計画のみ立案

- ToDoリスト形式での作業分解
- 実装の方向性と手順の明確化
  - タイムリーな軌道修正
- 失敗コストの事前削減

### 活用場面

- 大規模な機能追加や変更
- 複雑なアーキテクチャ変更
- 不明な要件の整理と設計

### 従来手法との違い

- 人間の即座修正に頼らない高品質な設計
- 「作りながら考える」から「考えてから作る」へ
- プロジェクト全体の一貫性確保

### [Extended Thinking](https://docs.anthropic.com/en/docs/build-with-claude/extended-thinking)（拡張思考）

複雑な問題を深く考え抜く機能

- 複雑なアーキテクチャ変更の計画立案
- 複雑な問題のデバッグ戦略構築
- 実装アプローチ間のトレードオフ評価

[「think」「think more」「think harder」「ultrathink」](https://www.anthropic.com/engineering/claude-code-best-practices)で深い思考を促進

### [CLAUDE.md](https://docs.anthropic.com/en/docs/claude-code/memory)による設計の一貫性確保

プロジェクトメモリで設計方針を永続化

- アーキテクチャパターンの文書化
- コーディング規約の統一
- チームワークフローの標準化

### [メモリ](https://docs.anthropic.com/en/docs/claude-code/memory)とは

- モデルの応答を「記憶」しておくためのスペース
- このスペースを「コンテキストウィンドウ」と呼ぶ
- メモリはMarkdown形式のファイルで管理する

### メモリタイプ

- プロジェクトメモリ: ./CLAUDE.md
- ユーザーメモリ: ~/.claude/CLAUDE.md
- プロジェクトメモリ（ローカル）: ./CLAUDE.local.md

### CLAUDE.mdの例

````{container} custom
```{literalinclude} ../.claude/sample-project.md
```
````

### 段階的アプローチ

複雑な問題を体系的に分解

- 複雑なタスクを小さな単位に分解
- 広範囲から具体的実装へ段階的絞り込み
- プロジェクト固有パターンの事前確認

### 完了条件の明確化

具体的な成果物とメトリクス

- 機能要件: 基本CLIコマンド動作
- 品質要件: テストカバレッジ >75%
- 統合要件: Claude Code hooks動作
- 文書要件: README.md完成

### 継続的な改善

設計の進化と共有

- メモリファイルの定期的な見直しと更新
- プロジェクト固有規約の段階的改善
- チーム全体での設計方針共有

### 計画フェーズの例

設計検討と準備の段階

- Extended Thinkingを活用した設計検討
- プロジェクト用語集作成とドメイン言語理解
- 実装計画書による構造化された計画立案

### サンプルプロジェクト: PyQC

- 統合品質チェック: Ruff + mypy/ty + 自動修正
- 開発統合: Claude Code/pre-commit hooks対応
- 高速実行: 品質チェック < 10秒、テスト < 30秒

> [https://github.com/drillan/stapy116](https://github.com/drillan/stapy116)

### PyQC実行例

````{container} custom
```{literalinclude} ./sample/pyqc-check.md
```
````

### 実装計画の例

````{container} custom
```{literalinclude} ../.claude/project-plan.md
```
````

### 実装ガイドラインの例

````{container} custom
```{literalinclude} ../.claude/implementation-notes.md
```
````

### まとめ: 計画・設計への投資

- 後の開発フェーズでの生産性向上と品質保証に直結する
- Claude Codeの自律的な能力を最大限に活用するための基盤となる

## 記録を残す

自律的な開発を成功させる重要な基盤

### こんなことはありませんか？

- 以前に発生した問題を繰り返す
- ユーザの期待する動作をしていなくても、できたと思い込む
- 試行錯誤した結果が次に活かされていない

### AIの認知特性への対応

AIは成功したと思い込む傾向がある

- 詳細なデバッグログが必要
- 構造化されたログでAIが過去を正確に把握
- 失敗パターンの蓄積で同じ過ちを回避

### 構造化されたログの実装

AI時代に適したログ形式

- 読みやすいログ形式
- デバッグ情報の階層的記録
- エラーパターンと解決策の文書化

### 知見の蓄積と活用

プロジェクト固有の知識を体系的に管理

- 「生きた文書」として継続的に更新
- チーム全体での知識共有
- 技術的負債の削減

### Claude Codeでの記録管理

### CLAUDE.mdファイルの活用

プロジェクトの核となる記録

- プロジェクト概要とアーキテクチャ
- 開発コマンドと設定の文書化
- コーディング規約とスタイルガイド

### .claudeディレクトリによる体系的管理

知識を構造化して管理

- `context.md`: 背景と制約
- `project-knowledge.md`: 技術的知見
- `project-improvements.md`: 改善履歴
- `common-patterns.md`: 定型パターン

### .claudeファイル実例

context.md

````{container} custom
```{literalinclude} ../.claude/context.md
```
````

### .claudeファイル実例

project-knowledge.md

````{container} custom
```{literalinclude} ../.claude/project-knowledge.md
```
````

### .claudeファイル実例

project-improvements.md

````{container} custom
```{literalinclude} ../.claude/project-improvements.md
```
````

### .claudeファイル実例

common-patterns.md

````{container} custom
```{literalinclude} ../.claude/common-patterns.md
```
````

### 実装計画管理

構造化された計画立案と進捗追跡

- 計画の採番システム（PLAN-YYYY-MM-DD-XXX）
- 進捗状況の追跡（planning/in_progress/completed）
- 完了条件の明確化と検証
- 実装履歴の保存とパターン学習

### 実装計画管理例

````{container} custom
```{literalinclude} ../plans/index.md
```
````

### 実装ログの実例

````{container} custom
```{literalinclude} ../plans/completed/PLAN-2025-07-10-001.md
```
````

### 完了時の振り返り実践

学習成果の体系的記録

- うまくいったこと: TDD実践、段階的実装
- 改善点: テストカバレッジ目標未達
- 学んだこと: AI時代の品質保証手法
- 今後の活用: プレゼンテーション素材として

### 効果的な記録の実践

### 即座の記録習慣

発見をその場で記録

- 重要な決定や発見を即座に記録
- 技術選定の理由と背景の明文化
- トラブルシューティングの過程と結果

### [カスタムスラッシュコマンド](https://docs.anthropic.com/en/docs/claude-code/slash-commands#custom-slash-commands)

Claude Codeが実行できる頻繁に使用されるプロンプトをMarkdownファイルとして定義

```````{container} custom
```{literalinclude} ../.claude/commands/learnings.md
```
```````

### 定期的な整理と更新

記録の鮮度を保つ

- 適切な頻度の情報整理
- 古い情報の精査と更新
- カスタムコマンドによるコンテキスト更新

### 記録がもたらす効果

### 開発効率の向上

過去の知見を活用

- 新しい課題に即座に適用
- 同じ問題での時間浪費を回避
- AIの自律的な問題解決能力向上

### 品質保証の強化

一貫性のある高品質な開発

- コーディングスタイルの維持
- ベストプラクティスの自動適用
- エラーパターンの事前回避

### チーム開発の円滑化

知識の共有と透明性

- 知識の属人化を防止
- 新規メンバーのオンボーディング効率化
- プロジェクト全体の透明性向上

### まとめ: 記録への投資

- Claude Codeの自律的な能力を最大限に引き出す
- 持続可能な開発プロセスを構築するための重要な要素

## 高品質なコードを書く

### こんなことはありませんか？

- 気がついたら大量にコードが生成されている
- 肥大化したコードから、バグの発生源がみつからない
- AIにエラーが握りつぶされる

### コード品質の重要性1

ガードレールなし

:::::{grid}
:gutter: 2

::::{grid-item}
- 安全機能の欠如
- 予期しない障害に対応できない  
- 開発者の即座の介入が必要
::::

::::{grid-item}
:::{figure} _static/images/ev01.jpeg
:alt: ガードレールなしの自動運転EV
:width: 80%
:::
::::

:::::

### コード品質の重要性2

ガードレールあり

:::::{grid}

::::{grid-item}
- 適切な安全機能
- 自律的な問題回避
- 継続的な安全運転
::::

::::{grid-item}
:::{figure} _static/images/ev02.jpeg
:alt: ガードレールありの自動運転EV
:width: 80%
:::
::::

:::::

### 自律的開発の前提条件

- 人間の即座修正に頼らない自己完結的な実装
- エラーの早期発見と自動修正による開発効率化
- 高品質なコードなくして自律開発は成立しない

### 一貫した品質維持と効率化

- 一貫したコード品質の維持
- バグの事前防止による手戻り削減
- チーム全体での品質基準の統一

### 1. ツールによる品質管理

### ツールの活用

高品質なコードを継続的に生成

- [Ruff](https://docs.astral.sh/ruff/): リンター・フォーマッターの統合
- [mypy](https://mypy.readthedocs.io/), [Pyright](https://microsoft.github.io/pyright/): 静的型チェッカー
- [pytest](https://docs.pytest.org/en/stable/): テスト

### 自動的な品質管理

特定のイベントをトリガーとしてコードの品質をチェック

- ファイルの追加・編集
- コミット

### [Claude Code Hooks](https://docs.anthropic.com/en/docs/claude-code/hooks)による自動化

AIコーディングワークフローに統合

- ファイル編集時に即座に実行
- 動的なコンテキスト認識
- プロジェクト固有の検証ルール

### Claude Code Hooksの仕組み

ファイル編集時のリアルタイム品質チェック

- フックイベント:
  - PreToolUse, PostToolUse, Notification, Stop, SubagentStop
- マッチャー:
  - Task, Bash, Glob, Grep, Read, Edit, MultiEdit, Write, WebFetch, WebSearch

### 2. テスト

ハルシネーションや認識のずれを防ぐ

- テストがターゲットとして機能
- 実装の方向性を明確化
- 反復的な改善プロセス

### テストの効果

安全で信頼性の高い開発

- 仕様の明文化と実装の検証
- リグレッションの防止
- 安全なリファクタリング

### 3. レビュー

### AI開発におけるレビュー

- 単一視点の限界: 一つのAIモデルだけでは見落としが発生
- 客観性の確保: 異なるAIによる多角的な品質評価
- 継続的改善: レビューサイクルによる品質向上

### AI同士のレビューの効果

- 高頻度生成: AIは大量のコードを短時間で生成
- 一貫性の維持: 人間の疲労や主観に影響されない
- 24時間対応: いつでも即座にレビュー実行可能

### 複数AIモデルによるレビューの価値

異なる学習データと設計思想による多角的評価

- 異なる視点: 各モデルの学習データや設計が異なるため、見落としを補完
- バイアス軽減: 単一モデルの偏見や盲点を他モデルが指摘
- 包括的検証: 複数の評価基準による総合的な品質判定

### まとめ: 品質への投資

- 高品質なコードへの投資はClaude Codeの自律性と安全性を両立するための要素
- ツールを活用し、属人性を回避

## まとめ: Claude Codeの実践的アプローチ

- 計画: 「作りながら考える」から「考えてから作る」へ 
- 記録: 「忘れるAI」から「覚えるAI」へ
- 品質: 「後手対応」から「先手防御」へ