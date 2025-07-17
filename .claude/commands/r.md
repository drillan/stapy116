次のルールにしたがって実装を継続してください

## 🎯 実行フロー

### 1. 計画確認・作成

- $ARGUMENTS の計画にしたがって実行する
  - なければ、実行中( @plans/active ) の計画があれば、その計画にしたがって実行する
- 計画がなければ、TodoWrite で計画を立てるところから始める
- 複雑なタスクの場合、Extended Thinking（「think」「think more」「think harder」「ultrathink」）で設計検討

### 2. uv 統一ルール（必須遵守）

**このプロジェクトでは、すべての Python コマンドを uv 経由で実行**

```bash
# ✅ 正しい実行方法
uv run pyqc check --all          # PyQC統合チェック
uv run pyqc fix                  # PyQC自動修正
uv run pytest                   # テスト実行
uv run mypy src                  # 型チェック
uv run ruff check .              # リントチェック
uv run python scripts/quality_check.py

# ❌ 直接実行は禁止
pyqc check
pytest
mypy src
ruff check .
python scripts/quality_check.py
```

### 2.1 品質保証原則

- 高速フィードバック: < 30 秒での品質チェック
- ゼロトレランス: 警告・エラー 0 件要求
- 自己適用原則: PyQC 自身が PyQC でチェックされる
- 客観的検証: 主観的待機時間なしの自動化品質管理

```bash
# AI開発ワークフロー最適化
uv run pyqc check --no-cache -q    # 高速チェック（キャッシュなし）
uv run pytest --no-cov -x -q      # 高速テスト（カバレッジなし、初回失敗で停止）
```

### 3. 品質保証（必須実行）

実装前・実装中・コミット前の 3 段階で品質チェック実行：

#### 実装前チェック

```bash
# PyQC統合品質チェック（推奨）
uv run pyqc check --all

# 従来方式（PyQC未利用時）
uv run python scripts/quality_check.py
```

#### 実装中チェック（段階的実行）

```bash
# PyQC統合アプローチ（推奨）
# 1. 自動修正プレビュー
uv run pyqc fix --dry-run

# 2. 自動修正適用
uv run pyqc fix

# 3. 統合チェック実行
uv run pyqc check --all


# 従来の個別実行（詳細制御時）
# 1. フォーマット適用
uv run ruff format src/

# 2. リント修正
uv run ruff check src/ --fix

# 3. 型チェック
uv run mypy src/

# 4. テスト実行
uv run pytest

# 5. カバレッジ確認（80%以上必須）
uv run pytest --cov=src --cov-report=term-missing
```

#### コミット前最終チェック（必須）

```bash
# PyQC統合最終チェック（推奨）
uv run pyqc check --format github

# 従来方式（フォールバック）
uv run python scripts/quality_check.py --format github
```

#### 品質基準（全て必須クリア）

- ✅ **PyQC 総合**: エラー 0 件（pyqc check）
- ✅ **ruff format**: エラー 0 件
- ✅ **ruff check**: エラー 0 件
- ✅ **mypy/ty**: エラー 0 件
- ✅ **pytest**: 全テスト成功、警告 0 件
- ✅ **coverage**: 80%以上維持

#### エラー対応（immediate action）

```bash
# PyQC自動修正による対応
uv run pyqc fix --backup     # 安全な自動修正（バックアップ付き）

# pre-commitフック失敗時
git add -u                    # 自動修正をステージング
git commit --amend --no-edit  # コミット再実行

# Dogfooding違反時（PyQC自己チェック失敗）
uv run pyqc check --all --verbose   # 詳細エラー確認
uv run pyqc fix               # 自動修正適用
# 手動修正が必要な場合は必ず対処してから再実行

# AI開発時代の高速エラー修正
uv run pyqc check --no-cache -q --format github  # 高速再チェック
```

### 4. TodoWrite 活用（必須実行）

実装開始時、進捗管理、完了確認の各段階で TodoWrite を活用：

#### 実装開始時

複雑・多段階タスクの場合（必須）

- 具体的な todo に分解（3 つ以上のステップがある場合）
- 優先度設定（high/medium/low）
- 明確な完了条件を定義

#### 実装中

リアルタイム進捗更新

- 作業開始時：pending → in_progress
- 完了即座：in_progress → completed
- 新たな発見時：追加 todo を作成
- 同時進行は 1 つの in_progress のみ

#### 完了時

最終確認

- 全 todo の completed 状態確認
- 未完了があれば継続実行
- 品質チェック 0 エラー確認
- 知見記録の完了確認

#### TodoWrite 判断基準

- **使用必須**: 3 ステップ以上、複数ファイル変更、新機能実装
- **使用推奨**: バグ修正、リファクタリング、テスト追加
- **使用不要**: 単純な 1 ファイル修正、ドキュメント更新のみ

### 5. コミット戦略

- @.claude/commit-best-practices.md にしたがって、適切なタイミングで行う
- 品質チェック 0 エラー確認後のみコミット実行
- pre-commit 時のエラーやワーニングは軽微なものでも無視しないで、必ず対処する

### 6. 知見記録（即座実行）

重要な決定や発見が得られた場合は即座に記録する：

- @.claude/context.md: プロジェクト背景・制約・リスク要因
- @.claude/project-knowledge.md: 技術的知見・実装パターン・アーキテクチャ
- @.claude/project-improvements.md: 開発プロセス改善履歴・学習成果
- @.claude/common-patterns.md: 再利用可能なコードパターン・テンプレート
- @.claude/commit-best-practices.md: コミット頻度・粒度・品質の包括的ガイドライン

---

## 🔄 統合実行フロー

### Phase 1: 開始準備

1. 計画確認

```bash
ls plans/active/           # 進行中計画の確認
cat plans/index.md         # 計画システム概要確認
```

2. 現状品質チェック

```bash
uv run pyqc check --all    # PyQC統合チェック（推奨）
uv run python scripts/quality_check.py  # フォールバック
```

3. PyQC 設定確認・初期化

```bash
uv run pyqc config show    # 現在の設定確認
uv run pyqc init           # 未設定時の初期化
```

4. TodoWrite 初期化

- 複雑タスクの場合：具体的 todo に分解
- 単純タスクの場合：直接実装開始

### Phase 2: 実装実行

5. 実装サイクル

- todo in_progress 化
- 段階的実装
- 都度品質チェック
- 完了時 todo completed 化

6. 品質確保（PyQC 統合）

```bash
uv run pyqc fix --dry-run     # 自動修正プレビュー
uv run pyqc fix               # 自動修正適用
uv run pyqc check --all       # 総合チェック

# 従来方式（詳細制御時）
uv run ruff format src/
uv run ruff check src/ --fix
uv run mypy src/
uv run pytest
```

### Phase 3: 完了処理

7. 最終品質確認（Dogfooding 原則）

```bash
uv run pyqc check --format github  # PyQC自己適用チェック
uv run python scripts/quality_check.py --format github  # フォールバック
```

8. 知見記録

重要な決定・発見を.claude/に即座記録

9. コミット実行

commit-best-practices.md に従って品質保証後コミット

10. TodoWrite 完了確認

全 todo の completed 状態確認

### チェックリスト

- [ ] uv 統一ルール遵守
- [ ] PyQC 統合品質チェック 0 エラー
- [ ] テスト成功（警告 0 件、80%カバレッジ維持）
- [ ] Dogfooding 原則適用（PyQC 自己チェック成功）
- [ ] todo 管理適切実行
- [ ] 知見記録完了
- [ ] コミット品質確保
- [ ] pre-commit フック成功
