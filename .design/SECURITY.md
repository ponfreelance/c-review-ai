---
project: c-review-ai
version: "1.0.0"
type: security
status: approved
last_updated: "2025-03-10"
---

# c-review-ai セキュリティ設計

## 1. APIキー管理

| 項目 | 方針 |
|------|------|
| CLAUDE_API_KEY | `.env` ファイルで管理。Gitにコミットしない |
| .env.example | キー値なしのテンプレートのみコミット |
| .gitignore | `.env` を必ず含める |

## 2. 入力バリデーション

| チェック | 実装箇所 | 内容 |
|---------|---------|------|
| コードサイズ | Pydantic / FastAPI | max_length=102400 (100KB) |
| ファイル拡張子 | upload エンドポイント | `.c` `.h` のみ許可 |
| ファイルサイズ | FastAPI | 100KB上限 |
| Content-Type | FastAPI | multipart/form-data 検証 |

## 3. プロンプトインジェクション対策

Claude APIへのプロンプトに以下を含める:

- SYSTEM_PROMPTで「コード生成しない」を明示
- ユーザー入力コードは```cコードブロック内に閉じる
- Claude APIの出力はJSON配列のみ期待し、パース失敗時はフォールバック処理

## 4. CORS

```python
allow_origins=["http://localhost:3000"]  # Frontend のみ許可
allow_methods=["POST", "GET"]
allow_headers=["*"]
```

本番デプロイ時は `allow_origins` をデプロイ先ドメインに変更すること。

## 5. データベース

| 項目 | 方針 |
|------|------|
| 認証 | docker-compose 内部ネットワーク限定 |
| パスワード | MVP: 固定値。本番: シークレット管理へ移行 |
| SQLインジェクション | asyncpg のパラメータバインドで防御 |

## 6. Docker

| 項目 | 方針 |
|------|------|
| ポート公開 | MVP: localhost バインドのみ |
| イメージ | 公式 slim / alpine ベース |
| root実行 | MVP許容。本番: 非rootユーザー追加 |

## 7. .gitignore 必須項目

```
.env
__pycache__/
node_modules/
.next/
*.pyc
```
