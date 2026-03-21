# /review-sample

samples/vulnerable.c を使って動作確認を行うコマンド。

## 手順

1. `docker compose up --build` で全サービス起動を確認
2. `samples/vulnerable.c` の内容を読み取る
3. `curl` で backend API にリクエストを送信:

```bash
curl -X POST http://localhost:8000/review \
  -H "Content-Type: application/json" \
  -d @- <<EOF
{
  "code": "$(cat samples/vulnerable.c)"
}
EOF
```

4. レスポンスの `risks` 配列に以下のカテゴリが含まれていることを確認:
   - NULL Pointer Risk
   - Unchecked Return Value
   - Memory Leak
   - Buffer Overflow
   - Uninitialized Variable

5. PostgreSQL にログが保存されていることを確認:

```bash
docker compose exec postgres psql -U creview -c "SELECT id, risk_count, created_at FROM reviews ORDER BY id DESC LIMIT 5;"
```
