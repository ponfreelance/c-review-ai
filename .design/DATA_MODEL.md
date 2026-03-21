---
project: c-review-ai
version: "1.0.0"
type: data_model
status: approved
last_updated: "2025-03-10"
---

# c-review-ai データモデル設計

## 1. PostgreSQL

### reviews テーブル

```sql
CREATE TABLE IF NOT EXISTS reviews (
    id          SERIAL PRIMARY KEY,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    code        TEXT NOT NULL,
    result      JSONB NOT NULL,
    risk_count  INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX idx_reviews_created_at ON reviews (created_at DESC);
```

#### result カラム（JSONB）の構造

```json
[
  {
    "line": "120",
    "category": "NULL Pointer Risk",
    "issue": "Pointer 'ptr' may be NULL before dereference.",
    "risk": "Segmentation fault at runtime.",
    "recommendation": "Add NULL validation before usage."
  }
]
```

---

## 2. ChromaDB

### コレクション: `c_review_knowledge`

| フィールド | 型 | 説明 |
|-----------|-----|------|
| id | string | review_{postgres_id} |
| documents | string | 入力コード + 解析結果のテキスト結合 |
| metadatas | dict | {"review_id": int, "risk_count": int, "created_at": str} |

embedding は ChromaDB のデフォルトモデル（all-MiniLM-L6-v2）で自動生成。

将来的に「過去に似たコードでどんなリスクが出たか」の検索に使用する。

---

## 3. Pydantic スキーマ

### ReviewRequest

```python
class ReviewRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=102400)
```

### Risk

```python
class Risk(BaseModel):
    line: str = ""
    category: str = ""
    issue: str = ""
    risk: str = ""
    recommendation: str = ""
```

### ReviewResponse

```python
class ReviewResponse(BaseModel):
    risks: list[Risk] = []
    risk_count: int = 0
```

---

## 4. API リクエスト/レスポンス例

### POST /review

**Request:**
```json
{
  "code": "#include <stdlib.h>\nint main() {\n  int *p = malloc(sizeof(int));\n  *p = 42;\n  return 0;\n}"
}
```

**Response:**
```json
{
  "risks": [
    {
      "line": "3",
      "category": "Unchecked Return Value",
      "issue": "malloc() return value is not checked for NULL.",
      "risk": "NULL pointer dereference if allocation fails.",
      "recommendation": "Check malloc return value before use."
    },
    {
      "line": "5",
      "category": "Memory Leak",
      "issue": "Allocated memory is never freed before return.",
      "risk": "Memory leak in long-running processes.",
      "recommendation": "Add free(p) before return."
    }
  ],
  "risk_count": 2
}
```

### POST /review/upload

**Request:** multipart/form-data
- file: vulnerable.c (application/octet-stream)

**Response:** 同上
