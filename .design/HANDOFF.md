---
project: c-review-ai
version: "1.0.0"
type: handoff
status: approved
last_updated: "2025-03-10"
---

# c-review-ai Claude Code ハンドオフ

## 1. 概要

C言語コードの**危険箇所のみを検出する**レビューAI MVPを構築する。

### 絶対遵守ルール

1. **コード生成をしない** — 修正コードは一切出力しない
2. **危険箇所の指摘のみ** — レビューAIであってコード生成AIではない
3. この制約はSYSTEM_PROMPTにも明記すること

## 2. 設計書の場所

すべて `.design/` ディレクトリ内:

| ファイル | 内容 |
|---------|------|
| REQUIREMENTS.md | 要件定義（機能要件、検出パターン、画面仕様） |
| ARCHITECTURE.md | アーキテクチャ（構成図、ディレクトリ、コンポーネント詳細） |
| DATA_MODEL.md | データモデル（PostgreSQL DDL、ChromaDB、Pydanticスキーマ） |
| SECURITY.md | セキュリティ方針 |
| TASKS.md | 実装タスクリスト（実装順序付き） |

## 3. 実装指示

### Step 1: 設計書を全部読む

```
まず .design/ 内の全ファイルを読んでください。
特に TASKS.md の実装順序に従って進めてください。
```

### Step 2: タスク実行

TASKS.md に記載の T-001 〜 T-014 を順に実行する。

### Step 3: 実装時の注意点

#### Backend (Python / FastAPI)

- **Python 3.11** を使用
- **anthropic SDK** を使用（REST直叩きしない）
- Claude APIモデル: `claude-sonnet-4-20250514`
- Claude APIレスポンスのパースに注意:
  - `response.content[0].text` からJSON文字列を取得
  - ```json ``` のフェンスが含まれる可能性があるので除去してからパース
  - パース失敗時はテキスト全体を1リスクとして返す
- asyncpg を使用（psycopg2ではなく）
- ChromaDB 接続失敗時もレビュー自体は完了させる（保存だけスキップ）

#### Frontend (Next.js)

- **Next.js 14** App Router + TypeScript
- **Tailwind CSS** でスタイリング
- API通信は `fetch` でOK（axios不要）
- 環境変数: `NEXT_PUBLIC_API_URL=http://localhost:8000`
- ファイルアップロードは `FormData` を使用

#### Docker

- `docker-compose.yml` でfrontend / backend / postgres / chromadb の4サービス
- PostgreSQL の schema.sql は `/docker-entrypoint-initdb.d/` にマウント
- backend は postgres の healthcheck 後に起動（depends_on + condition）

## 4. 完了条件

以下をすべて満たすこと:

- [ ] `docker compose up --build` でエラーなく4サービス起動
- [ ] http://localhost:3000 でレビュー画面が表示
- [ ] テキストエリアにCコードを貼り付けてレビュー実行可能
- [ ] .c / .h ファイルアップロードでレビュー実行可能
- [ ] レビュー結果が Line / Category / Issue / Risk / Recommendation 形式で表示
- [ ] samples/vulnerable.c で複数リスクが検出される
- [ ] PostgreSQLにレビューログが保存される

## 5. やらなくていいこと（MVPスコープ外）

- ユーザー認証
- レビュー履歴画面
- ナレッジ検索（ChromaDB保存のみ、検索UIは不要）
- シンタックスハイライト
- 本番デプロイ設定
- テストコード
- CI/CD

## 6. トラブルシューティング

| 問題 | 対処 |
|------|------|
| ChromaDB起動遅い | backend側で接続リトライ（3回、5秒間隔） |
| Claude APIレスポンスがJSON以外 | ```json フェンス除去 → パース再試行 → 失敗時フォールバック |
| PostgreSQL接続エラー | lifespan内でリトライ、失敗時はログのみでAPI自体は動作させる |
| フロントのCORS | backend の allow_origins に http://localhost:3000 を設定済みか確認 |
