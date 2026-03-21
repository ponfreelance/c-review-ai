# c-review-ai

C言語コードの危険箇所を検出するレビューAI MVP。

> **注意**: これはコード生成AIではありません。修正コードは出力しません。危険箇所の指摘のみ行います。

## セットアップ

### 1. 環境変数の設定

```bash
cp .env.example .env
```

`.env` ファイルを編集し、`GROQ_API_KEY` に Groq API キーを設定してください（[console.groq.com](https://console.groq.com) で無料取得可能）。

```
GROQ_API_KEY=gsk_your-actual-key-here
```

### 2. 起動

```bash
docker compose up --build
```

4つのサービスが起動します:
- **Frontend** (Next.js): http://localhost:3000
- **Backend** (FastAPI): http://localhost:8000
- **PostgreSQL**: localhost:5432
- **ChromaDB**: localhost:8100

### 3. アクセス

ブラウザで http://localhost:3000 を開いてください。

## 使い方

1. テキストエリアにCコードを貼り付け → 「レビュー実行」ボタン
2. または `.c` / `.h` ファイルを「ファイル選択」からアップロード
3. 検出されたリスクが Line / Category / Issue / Risk / Recommendation 形式で表示されます

## サンプルコード

`samples/vulnerable.c` に全検出パターンを含むテスト用コードがあります。
このファイルをアップロードするか、内容をコピー&ペーストしてレビューを試せます。

## 設計書

`.design/` ディレクトリに設計書一式があります。
