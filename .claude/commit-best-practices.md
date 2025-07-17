# コミットベストプラクティス

このドキュメントは、stapy116/PyQC プロジェクトでの高品質なコミット戦略を定義します。AI 開発時代における品質保証と Dogfooding 原則を重視した実践的なガイドラインです。

## 🎯 コミット品質基準

### 必須要件（Dogfooding 品質基準）

- ✅ **PyQC 統合チェック**: エラー 0 件（`uv run pyqc check --all`）
- ✅ **ruff format/lint**: エラー 0 件
- ✅ **mypy/ty 型チェック**: エラー 0 件
- ✅ **pytest**: 全テスト成功、警告 0 件
- ✅ **カバレッジ**: 80%以上維持
- ✅ **Dogfooding**: PyQC 自身が PyQC でチェック成功

### 推奨要件

- ⚡ **高速フィードバック**: 品質チェック < 30 秒
- 🎯 **ゼロトレランス**: 警告・エラー 0 件の厳格要求
- 📝 **明確なコミットメッセージ**: 目的と影響を説明
- 🔧 **原子的変更**: 1 つの明確な目的
- 📊 **テスト追加**: 新機能には対応するテスト

## ⏰ コミット頻度ガイドライン

### 基本原則

- **作業単位ごと**: 機能・修正・リファクタリングの完了時
- **品質チェック後**: 全品質基準をクリアした状態で
- **論理的結束**: 関連する変更を適切にグループ化
- **AI 最適化**: 高頻度コミットに対応した高速品質チェック

### 開発時代のコミット頻度戦略

# 🟢 推奨頻度（15 分〜1 時間間隔）

- PyQC 機能単位の実装完了時
- CLI コマンド追加・更新時
- チェッカー機能の実装完了時
- テスト追加・更新時（80%カバレッジ維持）
- 設定機能の実装完了時

# 🟡 特別対応（即座コミット）

- pyproject.toml 依存関係更新
- .claude/設定ファイル変更
- hooks 設定の追加・変更
- Dogfooding 設定の更新

# 🔴 避けるべきコミット

- PyQC 品質チェック失敗状態でのコミット
- 複数の無関係な PyQC 機能の一括コミット
- テスト警告が残存している状態でのコミット
- カバレッジ 80%を下回る状態でのコミット

### 生成コードの特殊考慮事項

高頻度コミット対応

- 品質チェック実行時間: < 30 秒を維持
- PyQC 自己適用: 常に Dogfooding 原則を適用
- 客観的品質保証: 主観的待機時間なしの自動検証
- エラー即修正: AI 生成コード特有のパターンエラーに即座対応

### タイミング判断フロー

```
変更実装完了
    ↓
PyQC統合チェック実行（uv run pyqc check --all）
    ↓
全チェックパス？ → NO → PyQC自動修正（uv run pyqc fix）→ 再チェック
    ↓ YES
Dogfooding確認？ → NO → PyQC自己適用修正
    ↓ YES
論理的に完結？ → NO → 追加実装継続
    ↓ YES
高速コミット実行（< 30秒以内）
```

## 📋 PyQC 段階的コミット戦略

### Phase 1: 依存関係とプロジェクト基盤

```bash
# 例: PyQC基本依存関係追加
git add pyproject.toml uv.lock
git commit -m "Add typer>=0.9.0 and rich for PyQC CLI

- Required for PyQC command-line interface
- Compatible with uv package management
- Maintains Python 3.12+ requirement"
```

### Phase 2: コア機能実装

```bash
# 例: 基本チェッカー実装
git add src/pyqc/checkers/ruff_checker.py
git commit -m "Implement Ruff integration checker

- Unified ruff format and lint checking
- Configurable rule selection and ignore patterns
- Parallel execution support for speed
- Comprehensive error reporting with file positions"
```

### Phase 3: CLI インターフェース

```bash
# 例: メインCLI実装
git add src/pyqc/cli/main.py src/pyqc/cli/commands/
git commit -m "Add PyQC CLI with check and fix commands

- check: Unified quality checking with multiple output formats
- fix: Automated code fixing with dry-run support
- config: Configuration management and initialization
- Rich-based progress indicators and colored output"
```

### Phase 4: テスト・Dogfooding 品質保証

```bash
# 例: 包括的テスト追加
git add tests/unit/pyqc/ tests/integration/
git commit -m "Add comprehensive PyQC test suite with 85% coverage

- Unit tests for all checker implementations
- Integration tests with real Python projects
- Edge case handling for malformed configurations
- pytest markers properly defined (no warnings)
- Achieve 85% test coverage exceeding 80% requirement"
```

### Phase 5: Dogfooding・設定・ドキュメント

```bash
# 例: 自己適用設定
git add .claude/hooks.json pyproject.toml .pre-commit-config.yaml
git commit -m "Enable PyQC Dogfooding with Claude Code hooks

- Configure PyQC self-checking via hooks
- Pre-commit integration for automated quality assurance
- Zero-tolerance quality settings (warnings as errors)
- AI development optimized configuration (< 30s execution)"
```

## ⚡ PyQC 品質ファーストワークフロー

### 実装前チェック

```bash
# 1. PyQC現在の品質状態確認
uv run pyqc check --all

# 2. PyQC設定確認
uv run pyqc config show

# 3. 実装対象の明確化
echo "目標: <具体的なPyQC機能・修正>"
```

### 実装中プロセス（AI 最適化）

```bash
# 4. 段階的実装
# - 小さな単位で実装
# - 都度PyQCチェック実行
# - Dogfooding原則適用

# 5. PyQC統合品質保証
uv run pyqc fix --dry-run     # プレビュー確認
uv run pyqc fix               # 自動修正適用
uv run pyqc check --all       # 最終確認

# 6. 従来方式（詳細制御時）
uv run ruff format src/
uv run ruff check src/ --fix
uv run mypy src/
uv run pytest --no-warnings  # 警告0件要求
```

### コミット前最終確認（Dogfooding）

```bash
# 7. PyQC自己適用チェック
uv run pyqc check --format github --self-check

# 8. カバレッジ確認（80%以上）
uv run pytest --cov=src --cov-report=term-missing

# 9. 高速ステージング・コミット（< 30秒）
git add <specific-files>
git commit -m "<meaningful-message>"
```

## 📏 コミット粒度基準

### 適切な粒度の原則

#### ✅ 理想的な粒度（PyQC 単一責任）

```bash
# 🎯 PyQC機能追加: 1つの完結したチェッカー機能
git add src/pyqc/checkers/type_checker.py tests/unit/checkers/test_type_checker.py
git commit -m "Add mypy/ty type checker integration

- Support both mypy and ty type checkers
- Configurable strict mode and ignore patterns
- 85% test coverage with comprehensive edge cases"

# 🔧 PyQCバグ修正: 特定の問題の完全解決
git add src/pyqc/core/config.py
git commit -m "Fix configuration loading for nested pyproject.toml

- Handle missing [tool.pyqc] section gracefully
- Preserve user configuration precedence
- Add validation for configuration schema"

# 📝 Dogfoodingテスト追加: PyQC自己適用テスト
git add tests/integration/test_dogfooding.py
git commit -m "Add PyQC self-application integration tests

- Test PyQC checking itself with zero errors
- Verify Dogfooding principle compliance
- 82% test coverage exceeding 80% requirement"
```

#### 🟡 注意が必要な粒度

```bash
# PyQCリファクタリング: 影響範囲を明確に
git add src/pyqc/checkers/ src/pyqc/core/runner.py
git commit -m "Refactor checker base class for unified execution

- Extract common checker interface
- Standardize error reporting format
- Maintain backward compatibility for configuration"

# AI最適化設定変更: 関連する設定を一括
git add pyproject.toml .claude/hooks.json .pre-commit-config.yaml
git commit -m "Optimize PyQC for AI development workflow

- Reduce execution time to < 30 seconds
- Enable Claude Code hooks integration
- Configure zero-tolerance error handling"
```

#### ❌ 避けるべき粒度

```bash
# 複数の無関係なPyQC機能
git add src/pyqc/ tests/ .claude/ docs/
git commit -m "Various PyQC improvements and fixes"

# Dogfooding違反状態
git add src/pyqc/cli/main.py  # PyQCチェック失敗でもコミット
git commit -m "WIP: CLI implementation with known issues"

# カバレッジ不足状態
git add src/pyqc/new_feature.py  # 80%カバレッジを下回る
git commit -m "Add new feature without adequate tests"
```

### 分割判断基準

#### PyQC 機能実装時の分割

1. **依存関係追加** → **チェッカー実装** → **CLI 統合** → **テスト追加** → **Dogfooding 適用**
2. **設定スキーマ** → **インターフェース定義** → **具体実装** → **統合テスト** → **自己適用確認**
3. **エラーモデル定義** → **チェック実装** → **修正機能** → **レポート生成** → **品質保証**

#### ファイル数による判断

- **1-3 ファイル**: 密接に関連する変更（理想的）
- **4-7 ファイル**: 機能横断の変更（要注意、分割検討）
- **8+ファイル**: 複数機能の混在（分割必須）

#### 変更行数による判断

- **1-50 行**: 小規模修正・バグ修正
- **51-200 行**: 中規模機能追加・リファクタリング
- **201-500 行**: 大規模機能・要分割検討
- **500+行**: 必ず機能単位で分割

## 🔧 PyQC エラー対応パターン

### PyQC チェック失敗時（Dogfooding 対応）

```bash
# 1. PyQC自動修正優先
uv run pyqc fix --backup  # 安全な自動修正（バックアップ付き）
uv run pyqc check --all   # 修正結果確認

# 2. 段階的手動修正
uv run pyqc check --verbose  # 詳細エラー情報取得
# - エラー箇所を個別に修正
# - 都度 uv run pyqc check で確認

# 3. Dogfooding違反時の緊急対応
uv run pyqc check --all --self-check  # 自己適用チェック
# - PyQC自身がPyQCルールに従っているか確認
# - 必要に応じて .pyqc.yaml設定調整
```

### Pre-commit フック失敗時

```bash
# 1. PyQC統合対応
uv run pyqc fix           # PyQC自動修正適用
git add -u                # 修正されたファイルを再ステージング
git commit --amend --no-edit

# 2. 高速再チェック（AI開発対応）
uv run pyqc check --no-cache -q  # キャッシュなし高速チェック
git add -u && git commit --amend --no-edit

# 3. 従来方式フォールバック
# - 指示に従ってエラー修正
# - uv run pyqc check --all で再確認
# - 修正をステージング・コミット
```

### エラー対応

```bash
# 1. 高頻度コミット時のエラー蓄積
uv run pyqc check --format github  # GitHub Actions形式で一覧表示
uv run pyqc fix --unsafe           # 積極的自動修正（注意が必要）

# 2. カバレッジ不足エラー（80%要求）
uv run pytest --cov=src --cov-report=html  # カバレッジ詳細確認
# - 不足部分にテスト追加
# - uv run pytest --cov=src で80%以上確認

# 3. pytest警告エラー（0件要求）
uv run pytest --strict-markers  # マーカー定義確認
# - pyproject.tomlにマーカー定義追加
# - テストファイルのマーカー修正
```

## 📈 品質メトリクス追跡

### コミットサイズ指標

#### 推奨範囲

```bash
# 🎯 理想的なコミットサイズ
ファイル数: 1-3個
変更行数: 10-100行
影響範囲: 単一モジュール・機能

# 🟡 注意が必要なサイズ
ファイル数: 4-7個
変更行数: 101-300行
影響範囲: 複数モジュール

# 🔴 分割検討が必要
ファイル数: 8個以上
変更行数: 300行以上
影響範囲: アーキテクチャ横断
```

#### メトリクス計測コマンド

```bash
# コミット前のサイズ確認
git diff --cached --stat
git diff --cached --numstat | awk '{sum+=$1+$2} END {print "Total changes:", sum, "lines"}'

# 最近のコミットサイズ分析
git log --oneline --stat -10 | grep -E "files? changed"
```

### コミット品質指標

#### PyQC 自動チェック項目（Dogfooding）

- **PyQC 統合チェック**: エラー 0 件（`uv run pyqc check --all`）
- **ruff フォーマット**: エラー 0 件（必須）
- **ruff リント**: エラー 0 件（必須）
- **mypy/ty 型チェック**: エラー 0 件（必須）
- **pytest**: 全テスト成功、警告 0 件（必須）
- **カバレッジ**: 80%以上維持（必須）
- **Dogfooding 確認**: PyQC 自己適用成功（必須）

#### 手動チェック項目

- **メッセージ品質**: 目的と影響の明確な説明
- **原子性**: 単一 PyQC 機能の変更
- **可逆性**: 安全に revert できる粒度
- **関連性**: 論理的に結束した変更
- **AI 最適化**: 高速フィードバック対応

### 改善目標と KPI

#### 最適化開発効率 KPI

- **コミット頻度**: 1 日 5-12 回（AI 高頻度対応）
- **品質チェック時間**: 30 秒以内（AI 最適化）
- **コミット成功率**: 98%以上（AI 自動修正活用）
- **revert 率**: 3%以下（Dogfooding 品質担保）
- **自動修正成功率**: 95%以上（PyQC fix 効果）

#### PyQC 品質 KPI

- **メッセージ品質**: 動詞+目的語の明確な構造
- **影響範囲**: 85%が単一 PyQC 機能内
- **テストカバレッジ**: 新コードは 85%以上（80%基準超過）
- **Dogfooding 適用**: PyQC 機能追加時 100%自己適用
- **AI 品質保証**: 客観的検証による品質確保

## 💡 PyQC 実践的コミット例

### PyQC 開発の良い粒度実例

#### シナリオ 1: 新 PyQC 機能追加（Dogfooding 対応）

```bash
# ❌ 悪い例: 巨大な一括コミット
git add src/pyqc/ tests/ .claude/ pyproject.toml
git commit -m "Add PyQC type checking feature"

# ✅ 良い例: 段階的な5コミット（Dogfooding適用）
# コミット1: 依存関係追加
git add pyproject.toml uv.lock
git commit -m "Add mypy>=1.0.0 dependency for type checking

- Required for PyQC type checker integration
- Compatible with existing ty type checker support
- Maintains Python 3.12+ requirement"

# コミット2: チェッカー実装
git add src/pyqc/checkers/type_checker.py
git commit -m "Implement unified mypy/ty type checker

- Support both mypy and ty with configuration selection
- Configurable strict mode and ignore patterns
- Parallel execution with performance optimization"

# コミット3: CLI統合
git add src/pyqc/cli/commands/check.py
git commit -m "Add type checking to PyQC CLI check command

- Integrate type checker into unified check workflow
- Support --types-only flag for type-specific checking
- Rich progress indicators for type checking status"

# コミット4: テスト追加（80%カバレッジ達成）
git add tests/unit/checkers/test_type_checker.py tests/integration/test_type_integration.py
git commit -m "Add comprehensive type checker tests with 85% coverage

- Unit tests for mypy and ty integrations
- Integration tests with real Python projects
- Edge case handling for configuration errors
- Achieve 85% coverage exceeding 80% requirement"

# コミット5: Dogfooding適用
git add .claude/hooks.json pyproject.toml
git commit -m "Enable PyQC type checking Dogfooding

- Configure PyQC to check itself with type checking
- Claude Code hooks integration for real-time type validation
- Zero-tolerance type error configuration"
```

#### シナリオ 2: PyQC バグ修正

```bash
# ❌ 悪い例: 実装とテストの混在
git add src/pyqc/core/config.py tests/unit/core/test_config.py src/pyqc/cli/main.py
git commit -m "Fix various PyQC configuration issues"

# ✅ 良い例: 問題別の分離（AI高速対応）
# コミット1: 設定修正（< 30秒で完了）
git add src/pyqc/core/config.py
git commit -m "Fix pyproject.toml configuration loading

- Handle missing [tool.pyqc] section gracefully
- Preserve user configuration precedence
- Add schema validation for configuration values"

# コミット2: 対応テスト（警告0件達成）
git add tests/unit/core/test_config.py
git commit -m "Add edge case tests for configuration loading

- Test missing configuration section handling
- Verify configuration precedence rules
- 82% test coverage with zero pytest warnings"

# コミット3: CLI修正（別の問題、Dogfooding確認）
git add src/pyqc/cli/main.py
git commit -m "Handle configuration errors gracefully in CLI

- Display helpful error messages for invalid config
- Suggest pyqc init for missing configuration
- PyQC self-check passes with zero errors"
```

#### シナリオ 3: PyQC リファクタリング

```bash
# ❌ 悪い例: 広範囲の無計画変更
git add src/pyqc/
git commit -m "Refactor PyQC code structure"

# ✅ 良い例: 段階的リファクタリング（Dogfooding維持）
# コミット1: インターフェース抽出
git add src/pyqc/checkers/base.py
git commit -m "Extract common checker base class

- Define unified interface for all checkers
- Standardize error reporting and configuration
- Maintain backward compatibility for existing checkers"

# コミット2: 実装クラス更新（PyQC自動修正活用）
git add src/pyqc/checkers/ruff_checker.py src/pyqc/checkers/type_checker.py
git commit -m "Update checkers to use common base interface

- Refactor ruff and type checkers to inherit from base
- Unified error handling and configuration management
- PyQC fix applied automatically during refactoring"

# コミット3: テスト更新（Dogfooding確認）
git add tests/unit/checkers/ tests/integration/test_checker_interface.py
git commit -m "Update tests for refactored checker architecture

- Test common interface functionality
- Verify backward compatibility maintained
- PyQC Dogfooding passes with 83% coverage"
```

### 判断に迷うケースの対処法

#### ケース 1: 相互依存する変更

```bash
# 問題: ModelAとModelBが相互に依存する新機能
# 解決: 段階的な依存関係構築

# ステップ1: 基本構造
git add src/core/models/base_model.py
git commit -m "Add shared base model for mutual dependencies"

# ステップ2: 第一モデル
git add src/core/models/model_a.py
git commit -m "Implement ModelA with forward references"

# ステップ3: 第二モデル完成
git add src/core/models/model_b.py src/core/models/model_a.py
git commit -m "Complete ModelB and resolve ModelA forward references"
```

#### ケース 2: 設定とコードの同時変更

```bash
# 問題: 新機能に設定とコードの両方が必要
# 解決: 後方互換性を保った段階的導入

# ステップ1: 設定スキーマ
git add src/core/config/models.py
git commit -m "Add configuration schema for new feature X"

# ステップ2: 機能実装（デフォルト値使用）
git add src/services/feature_x.py
git commit -m "Implement feature X with sensible defaults"

# ステップ3: 設定統合
git add config/settings.yaml src/core/config/loader.py
git commit -m "Integrate feature X configuration"
```

## 🚨 アンチパターン回避

### ❌ 避けるべきパターン

- 品質チェック失敗でのコミット強行
- 複数機能の一括コミット
- 曖昧なコミットメッセージ
- テスト未作成での新機能追加

### ✅ 推奨パターン

- 品質ファーストアプローチ
- 機能別・段階別のコミット分割
- 影響範囲を明確にしたメッセージ
- TDD（テスト駆動開発）の実践

---

このベストプラクティスにより、高品質で追跡可能な開発履歴を維持し、安全で効率的なプロジェクト運営を実現します。
