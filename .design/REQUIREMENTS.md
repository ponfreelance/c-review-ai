---
project: c-review-ai
version: "1.0.0"
type: requirements
status: approved
last_updated: "2025-03-10"
---

# c-review-ai 要件定義書

## 1. プロジェクト概要

C言語ソースコードの**危険箇所のみを検出する**レビューAI MVP。

### 1.1 核心ルール（絶対遵守）

| ID | ルール |
|----|--------|
| CORE-1 | **コード生成をしない** |
| CORE-2 | **修正コードを書かない** |
| CORE-3 | **危険箇所の指摘のみ行う** |

> これはコード生成AIではなく **レビューAI** である。

### 1.2 ゴール

- `docker compose up` で起動
- ブラウザからCコードを入力
- AIレビュー結果を画面に表示

---

## 2. 技術スタック

| レイヤー | 技術 |
|---------|------|
| Frontend | Next.js (App Router) |
| Backend | Python FastAPI |
| LLM | Claude API (claude-sonnet-4-20250514) |
| Database | PostgreSQL 16 |
| VectorDB | ChromaDB 0.4.x |
| Infra | Docker Compose |

---

## 3. 機能要件

### F-001: Cコード入力

- **テキストエリア**: 直接コードを貼り付け
- **ファイルアップロード**: `.c` `.h` ファイル対応
- 入力サイズ上限: 100KB

### F-002: AIレビュー実行

入力されたCコードをClaude APIで解析し、危険箇所を検出する。

#### 出力形式（1リスクあたり）

```
Line:        行番号（特定可能な場合）
Category:    リスクカテゴリ
Issue:       検出内容
Risk:        想定される障害
Recommendation: 対処の方向性（修正コードは書かない）
```

### F-003: 検出対象パターン

#### メモリ系
- REQ-M1: NULLチェック漏れ
- REQ-M2: 未初期化変数
- REQ-M3: malloc戻り値未確認
- REQ-M4: free忘れ（メモリリーク）
- REQ-M5: 二重free

#### 配列系
- REQ-A1: buffer overflow
- REQ-A2: 境界チェック不足

#### API系
- REQ-R1: 戻り値未確認

#### 状態系
- REQ-S1: フラグ未初期化
- REQ-S2: 状態遷移抜け

### F-004: レビューログ保存

以下をPostgreSQLに保存:

| カラム | 型 | 説明 |
|--------|-----|------|
| id | SERIAL PK | 自動採番 |
| created_at | TIMESTAMPTZ | 実行日時 |
| code | TEXT | 入力コード |
| result | JSONB | 解析結果JSON |
| risk_count | INTEGER | 検出リスク数 |

### F-005: VectorDB保存

ChromaDBに以下を保存（将来のナレッジ検索用）:

- code（入力コード）
- analysis_result（解析結果）
- embedding（自動生成）

---

## 4. API仕様

### POST /review

**Request:**
```json
{
  "code": "C source code string"
}
```

**Response:**
```json
{
  "risks": [
    {
      "line": "120",
      "category": "NULL Pointer Risk",
      "issue": "Pointer may be NULL before dereference.",
      "risk": "Segmentation fault.",
      "recommendation": "Add NULL validation before usage."
    }
  ],
  "risk_count": 1
}
```

### POST /review/upload

**Request:** multipart/form-data (file: .c or .h)

**Response:** 同上

---

## 5. 非機能要件

| ID | 要件 | 値 |
|----|------|----|
| NF-1 | レスポンス時間 | 30秒以内（Claude API依存） |
| NF-2 | 入力サイズ上限 | 100KB |
| NF-3 | 同時接続 | MVP: 1ユーザー想定 |
| NF-4 | デプロイ | docker compose up のみ |
| NF-5 | 環境変数 | CLAUDE_API_KEY のみ必須 |

---

## 6. 画面仕様

### /review ページ

```
┌─────────────────────────────────────┐
│  c-review-ai                        │
├─────────────────────────────────────┤
│                                     │
│  [テキストエリア: Cコード入力]       │
│                                     │
│  [ファイル選択] (.c .h)             │
│                                     │
│  [レビュー実行ボタン]               │
│                                     │
├─────────────────────────────────────┤
│  検出結果                           │
│                                     │
│  ┌─ Risk 1 ──────────────────────┐  │
│  │ Line: 120                     │  │
│  │ Category: NULL Pointer Risk   │  │
│  │ Issue: ...                    │  │
│  │ Risk: ...                     │  │
│  │ Recommendation: ...           │  │
│  └───────────────────────────────┘  │
│                                     │
│  ┌─ Risk 2 ──────────────────────┐  │
│  │ ...                           │  │
│  └───────────────────────────────┘  │
│                                     │
│  リスク合計: 2件                    │
└─────────────────────────────────────┘
```
