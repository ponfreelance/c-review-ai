---
project: c-review-ai
version: "1.0.0"
type: architecture
status: approved
last_updated: "2025-03-10"
---

# c-review-ai アーキテクチャ設計

## 1. システム構成図

```
┌──────────────┐    HTTP     ┌──────────────┐    Claude API   ┌─────────┐
│   Frontend   │ ─────────> │   Backend    │ ──────────────> │  Claude │
│   Next.js    │ <───────── │   FastAPI    │ <────────────── │   API   │
│  :3000       │    JSON    │  :8000       │    JSON         └─────────┘
└──────────────┘            └──────┬───────┘
                                   │
                          ┌────────┴────────┐
                          │                 │
                   ┌──────▼──────┐   ┌──────▼──────┐
                   │  PostgreSQL │   │  ChromaDB   │
                   │  :5432      │   │  :8100      │
                   │  ログ保存    │   │  ベクトル保存 │
                   └─────────────┘   └─────────────┘
```

## 2. ディレクトリ構成

```
c-review-ai/
├── .design/                  # 設計書一式（本ディレクトリ）
├── agents/                   # Claude Code instruction
│   └── AGENTS.md
├── commands/                 # カスタムコマンド
│   └── review-sample.md
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── next.config.js
│   ├── tsconfig.json
│   └── src/
│       └── app/
│           ├── layout.tsx
│           ├── page.tsx       # / → /review へリダイレクト
│           └── review/
│               └── page.tsx   # メイン画面
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── __init__.py
│       ├── main.py            # FastAPIアプリ / CORS / lifespan
│       ├── review.py          # レビューロジック（Claude API呼出）
│       ├── prompt.py          # システムプロンプト / ユーザープロンプト
│       ├── database.py        # PostgreSQL + ChromaDB接続
│       └── models.py          # Pydanticスキーマ
├── database/
│   └── schema.sql             # DDL
├── samples/
│   └── vulnerable.c           # テスト用サンプルCコード
├── docker-compose.yml
├── .env.example
└── README.md
```

## 3. コンポーネント詳細

### 3.1 Frontend (Next.js)

| 項目 | 値 |
|------|-----|
| フレームワーク | Next.js 14 (App Router) |
| 言語 | TypeScript |
| スタイリング | Tailwind CSS |
| 状態管理 | React hooks (useState) |
| HTTP | fetch API |

**ページ構成:**
- `/` → `/review` にリダイレクト
- `/review` → メインレビュー画面

**コンポーネント分割（推奨）:**
- `CodeInput` — テキストエリア + ファイルアップロード
- `ReviewButton` — 実行ボタン（ローディング制御）
- `RiskCard` — 1リスクの表示カード
- `ResultPanel` — リスク一覧 + 合計件数

### 3.2 Backend (FastAPI)

| ファイル | 責務 |
|---------|------|
| main.py | アプリ初期化、CORS、lifespan（DB接続/切断）、ルーティング |
| review.py | Claude API呼出 → JSONパース → DB/Chroma保存 → レスポンス返却 |
| prompt.py | SYSTEM_PROMPT定数、build_user_prompt()関数 |
| database.py | asyncpg pool管理、ChromaDB client管理、save関数群 |
| models.py | ReviewRequest, Risk, ReviewResponse (Pydantic) |

**APIエンドポイント:**

| Method | Path | 説明 |
|--------|------|------|
| POST | /review | コード文字列を受けてレビュー |
| POST | /review/upload | ファイルアップロードでレビュー |
| GET | /health | ヘルスチェック |

### 3.3 Claude API連携フロー

```
1. ユーザーがコード送信
2. backend/review.py がリクエスト受信
3. prompt.py からSYSTEM_PROMPT + USER_PROMPT構築
4. anthropic.Anthropic().messages.create() 呼出
   - model: claude-sonnet-4-20250514
   - max_tokens: 4096
   - system: SYSTEM_PROMPT
   - messages: [{"role":"user", "content": USER_PROMPT}]
5. レスポンスからJSON配列をパース
6. PostgreSQLにログ保存
7. ChromaDBにembedding保存
8. ReviewResponseをフロントに返却
```

### 3.4 データベース

**PostgreSQL**: レビュー履歴の永続化（schema.sqlで初期化）
**ChromaDB**: コード+結果のベクトル保存（将来のナレッジ検索基盤）

## 4. Docker構成

| サービス | イメージ | ポート |
|---------|---------|--------|
| frontend | Node.js 20 (ビルド) | 3000 |
| backend | Python 3.11-slim | 8000 |
| postgres | postgres:16-alpine | 5432 |
| chromadb | chromadb/chroma:0.4.24 | 8100 |

## 5. 環境変数

| 変数名 | 必須 | 説明 |
|--------|------|------|
| CLAUDE_API_KEY | ✅ | Anthropic APIキー |
| DATABASE_URL | 自動 | docker-compose内で自動設定 |
| CHROMA_HOST | 自動 | docker-compose内で自動設定 |
| CHROMA_PORT | 自動 | docker-compose内で自動設定 |

## 6. エラーハンドリング方針

| ケース | 対処 |
|--------|------|
| Claude APIタイムアウト | 30秒タイムアウト → 503返却 |
| Claude APIレスポンスのJSONパース失敗 | テキストをそのまま1リスクとして返却 |
| DB接続失敗 | レビュー自体は実行、ログ保存をスキップしてwarning |
| 入力サイズ超過 | 422 Validation Error |
| ファイル形式不正 | 400 Bad Request |
