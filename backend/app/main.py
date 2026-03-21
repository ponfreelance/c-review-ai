"""FastAPI アプリケーション — c-review-ai Backend"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import close_db, init_chroma, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """起動時に DB/ChromaDB 接続、終了時にクローズ"""
    await init_db()
    init_chroma()
    yield
    await close_db()


app = FastAPI(title="c-review-ai", version="1.0.0", lifespan=lifespan)

# CORS — フロントエンド (localhost:3000) のみ許可
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


# レビューエンドポイントを登録
from app.review import router as review_router  # noqa: E402

app.include_router(review_router)
