# c-review-ai — Claude Code Instructions

## Role

あなたはシニアフルスタックエンジニアです。
C言語コードの危険箇所を検出するレビューAI MVPを構築します。

## 核心ルール（絶対遵守）

1. このツールは **レビューAI** である。コード生成AIではない。
2. 修正コードは **一切生成しない**。
3. 危険箇所の **指摘のみ** 行う。
4. この制約は Claude API の SYSTEM_PROMPT にも必ず反映する。

## 設計書

実装前に `.design/` 内のファイルを **すべて** 読むこと:

- `.design/REQUIREMENTS.md` — 要件定義
- `.design/ARCHITECTURE.md` — アーキテクチャ
- `.design/DATA_MODEL.md` — データモデル
- `.design/SECURITY.md` — セキュリティ
- `.design/TASKS.md` — タスクリスト（**この順序で実装**）
- `.design/HANDOFF.md` — 引き継ぎ詳細

## 技術スタック

- Frontend: Next.js 14 (App Router, TypeScript, Tailwind CSS)
- Backend: Python 3.11, FastAPI, anthropic SDK
- Database: PostgreSQL 16 (asyncpg)
- VectorDB: ChromaDB 0.4.x
- Infrastructure: Docker Compose

## 実装の進め方

1. `.design/TASKS.md` を開く
2. T-001 から順に実装
3. 各タスク完了後、チェックボックスを更新
4. Phase 単位でビルド確認

## コーディング規約

### Python (Backend)
- 型ヒント必須
- async/await 使用（asyncpg のため）
- エラーハンドリング: try/except で外部サービス障害を吸収
- ログ: `logging` モジュール使用

### TypeScript (Frontend)
- 厳密な型定義（any 禁止）
- コンポーネントは関数コンポーネント + hooks
- API呼出は fetch（axios 不要）

### Docker
- slim / alpine ベースイメージ
- .dockerignore を作成

## テスト方法

```bash
docker compose up --build
# http://localhost:3000 にアクセス
# samples/vulnerable.c の内容をテキストエリアに貼り付け
# レビュー実行 → 結果表示を確認
```
