---
project: c-review-ai
version: "1.0.0"
type: tasks
status: approved
last_updated: "2025-03-10"
---

# c-review-ai 実装タスク

## Phase 1: プロジェクト基盤（まずここから）

### T-001: プロジェクト初期化
- [ ] ディレクトリ構成を作成（ARCHITECTURE.md 参照）
- [ ] `.env.example` を作成
- [ ] `.gitignore` を作成（SECURITY.md 参照）

### T-002: Docker Compose
- [ ] `docker-compose.yml` 作成（4サービス: frontend, backend, postgres, chromadb）
- [ ] PostgreSQL にて `database/schema.sql` を初期化スクリプトとしてマウント
- [ ] 各サービスのヘルスチェック設定

---

## Phase 2: Backend実装

### T-003: FastAPI アプリ基盤
- [ ] `backend/requirements.txt` 作成
- [ ] `backend/Dockerfile` 作成
- [ ] `backend/app/__init__.py` 作成
- [ ] `backend/app/main.py` — FastAPIアプリ, CORS, lifespan (DB init/close)
- [ ] `GET /health` エンドポイント

### T-004: Pydantic モデル
- [ ] `backend/app/models.py` — ReviewRequest, Risk, ReviewResponse
- [ ] バリデーション: code は1文字以上100KB以下

### T-005: プロンプト定義
- [ ] `backend/app/prompt.py` — SYSTEM_PROMPT 定数
- [ ] `build_user_prompt(code: str) -> str` 関数
- [ ] **重要**: SYSTEM_PROMPTに「コード生成しない」「JSON配列のみ出力」を明記

### T-006: データベース接続
- [ ] `backend/app/database.py` — asyncpg pool (init/close)
- [ ] `save_review(code, result, risk_count)` 関数
- [ ] ChromaDB client 初期化
- [ ] `save_to_chroma(review_id, code, result)` 関数
- [ ] DB接続失敗時はレビュー自体はスキップせずwarningログのみ

### T-007: レビューロジック
- [ ] `backend/app/review.py`
- [ ] `POST /review` エンドポイント
  1. コード受信
  2. Claude API呼出（anthropic SDK）
  3. レスポンスからJSON配列パース
  4. パース失敗フォールバック（テキストを1リスクとして扱う）
  5. PostgreSQL保存
  6. ChromaDB保存
  7. ReviewResponse返却
- [ ] `POST /review/upload` エンドポイント
  - ファイル拡張子チェック (.c .h のみ)
  - ファイル読み込み → /review と同じロジックへ

### T-008: database/schema.sql
- [ ] reviews テーブル DDL（DATA_MODEL.md 参照）
- [ ] インデックス作成

---

## Phase 3: Frontend実装

### T-009: Next.js プロジェクト初期化
- [ ] `npx create-next-app@latest` (TypeScript, Tailwind, App Router)
- [ ] `frontend/Dockerfile` 作成
- [ ] `next.config.js` — 環境変数設定

### T-010: レビュー画面
- [ ] `src/app/review/page.tsx` — メインページ
- [ ] コード入力テキストエリア（シンタックスハイライト不要、MVP）
- [ ] ファイルアップロードボタン (.c .h)
- [ ] レビュー実行ボタン（ローディング状態管理）
- [ ] 結果表示パネル — RiskCard のリスト
- [ ] リスク合計件数の表示
- [ ] エラー表示（API失敗時）

### T-011: トップページ
- [ ] `src/app/page.tsx` — `/review` へリダイレクト

---

## Phase 4: 仕上げ

### T-012: サンプルCコード
- [ ] `samples/vulnerable.c` — 全検出パターンを含む意図的に脆弱なサンプル
  - NULLチェック漏れ
  - 未初期化変数
  - malloc戻り値未確認
  - free忘れ
  - 二重free
  - buffer overflow
  - 戻り値未確認
  - フラグ未初期化

### T-013: README.md
- [ ] プロジェクト説明
- [ ] セットアップ手順
- [ ] 環境変数 (CLAUDE_API_KEY)
- [ ] 起動方法 (`docker compose up`)
- [ ] アクセス先 (http://localhost:3000)
- [ ] サンプルCコードの使い方

### T-014: 動作確認
- [ ] `docker compose up --build` で全サービス起動
- [ ] http://localhost:3000 にアクセス
- [ ] samples/vulnerable.c を入力してレビュー実行
- [ ] 結果が画面に表示されることを確認
- [ ] PostgreSQLにログが保存されていることを確認

---

## 実装順序

```
T-001 → T-002 → T-008
  ↓
T-003 → T-004 → T-005 → T-006 → T-007
  ↓
T-009 → T-010 → T-011
  ↓
T-012 → T-013 → T-014
```

**推定所要時間**: Claude Code で 1-2 セッション
