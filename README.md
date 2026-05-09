# c-review-ai

C言語コードの危険箇所を検出するレビューAI MVP。**ブラウザにコピペして即座に試せる入口**として設計されています。

> **注意**: これはコード生成AIではありません。修正コードは出力しません。危険箇所の指摘のみ行います。

## 4 層モデルでの位置づけ — L2' (PR を投げる前の自己チェック軽量版)

c-review-ai は **creview の前段ではない**。CLI 版の [creview](https://github.com/ponfreelance/creview) を本格運用するチーム向けに、**「PR を投げる前にコピペでひと舐めしておく軽量版」**として位置づけられる入口。環境構築不要で、ブラウザでテキストエリアに貼って即実行できる。

| 層 | ツール | 役割 |
|---|---|---|
| L0 ビルド時 | `gcc / clang` の警告 + `-Werror` | `-Wall -Wextra -Wpedantic -Werror -fanalyzer`。**警告ゼロにならない PR はそもそもレビューに入らない** |
| L1 PR チェック | clang-tidy / cppcheck | OSS 主流の静的解析を CI に組み込む |
| L2 PR レビュー | creview (CLI) | プロジェクト固有 / 日本語ナレッジ / severity / CWE/MISRA / `--preset pr` で diff のみ走査 / AI 補強 |
| **L2' 自己チェック** | **c-review-ai** ← ココ | **環境構築不要のブラウザ版軽量チェック。PR を投げる前にコピペで気軽に試す** |
| L3 監査 | CSAF | libclang AST + 依存グラフで risk A/B/C 自動昇格 / MISRA C 2012 準拠 |

### c-review-ai と creview の使い分け

- **c-review-ai**: ブラウザで開いて、書きかけのコードや短いスニペットをコピペで気軽に試したいとき。コピペ→レビュー実行→結果確認まで 30 秒。**まず「自分がやらかしてないか」を素早く確かめる**用途。
- **creview**: CI に組み込む / 大量ファイル / diff のみ / SARIF 出力 / プロジェクト全体の監査。本格運用は CLI 版へ。

c-review-ai で気になる検出があれば、そのプロジェクトを CLI 版 creview に移して `--preset pr` で diff のみ叩く運用が想定。CLI 版は GitHub: [ponfreelance/creview](https://github.com/ponfreelance/creview)。

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

## このツールでやらないこと

ブラウザでまず触ってみる体験版です。以下は **対象外** です:

- ❌ コマンドライン実行（`creview your.c`）→ [creview](https://github.com/ponfreelance/creview)
- ❌ Claude API による文脈レビュー → creview
- ❌ プロジェクト横断の依存解析・MISRA 監査 → [C-Safety-audit-framework](https://github.com/ponfreelance/C-Safety-audit-framework)
- ❌ CI 統合（SARIF / GitHub Actions）→ creview
- ❌ 商用サポート・規格対応 → creview / CSAF のカスタム対応

## 関連プロダクト

C言語レビュー / 監査の OSS 3 製品。用途で使い分けてください。

| プロダクト | 役割 | 形態 |
|---|---|---|
| **c-review-ai**（このリポ） | まず Web で触ってみる体験版 | Web (Docker) |
| [creview](https://github.com/ponfreelance/creview) | 手元で本気で使う C 言語レビュー（36パターン + Claude API） | CLI (Win/Mac/Linux バイナリ) |
| [C-Safety-audit-framework](https://github.com/ponfreelance/C-Safety-audit-framework) | プロジェクト横断の安全性監査（MISRA・依存グラフ） | Python パッケージ |
