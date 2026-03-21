CREATE TABLE IF NOT EXISTS reviews (
    id          SERIAL PRIMARY KEY,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    code        TEXT NOT NULL,
    result      JSONB NOT NULL,
    risk_count  INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX idx_reviews_created_at ON reviews (created_at DESC);
