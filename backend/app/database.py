"""PostgreSQL + ChromaDB 接続管理"""
from __future__ import annotations

import json
import logging
import os

import asyncpg
import chromadb

logger = logging.getLogger(__name__)

# --- PostgreSQL ---

_pool: asyncpg.Pool | None = None


async def init_db() -> None:
    """PostgreSQL コネクションプール初期化（リトライ3回）"""
    global _pool
    database_url = os.environ.get(
        "DATABASE_URL", "postgresql://creview:creview@postgres:5432/creview"
    )
    for attempt in range(1, 4):
        try:
            _pool = await asyncpg.create_pool(database_url, min_size=1, max_size=5)
            logger.info("PostgreSQL 接続成功")
            return
        except Exception as e:
            logger.warning("PostgreSQL 接続失敗 (試行 %d/3): %s", attempt, e)
            if attempt < 3:
                import asyncio
                await asyncio.sleep(5)
    logger.error("PostgreSQL に接続できませんでした。ログ保存は無効です。")


async def close_db() -> None:
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


async def save_review(code: str, result: list[dict], risk_count: int) -> int | None:
    """レビュー結果を PostgreSQL に保存。失敗時は warning のみ。"""
    if _pool is None:
        logger.warning("PostgreSQL 未接続のためログ保存をスキップ")
        return None
    try:
        row = await _pool.fetchrow(
            "INSERT INTO reviews (code, result, risk_count) VALUES ($1, $2::jsonb, $3) RETURNING id",
            code,
            json.dumps(result),
            risk_count,
        )
        return row["id"]
    except Exception as e:
        logger.warning("レビューログ保存失敗: %s", e)
        return None


# --- ChromaDB ---

_chroma_collection = None


def init_chroma() -> None:
    """ChromaDB クライアント初期化（リトライ3回）"""
    global _chroma_collection
    host = os.environ.get("CHROMA_HOST", "chromadb")
    port = int(os.environ.get("CHROMA_PORT", "8100"))
    for attempt in range(1, 4):
        try:
            client = chromadb.HttpClient(host=host, port=port)
            _chroma_collection = client.get_or_create_collection("c_review_knowledge")
            logger.info("ChromaDB 接続成功")
            return
        except Exception as e:
            logger.warning("ChromaDB 接続失敗 (試行 %d/3): %s", attempt, e)
            if attempt < 3:
                import time
                time.sleep(5)
    logger.error("ChromaDB に接続できませんでした。ベクトル保存は無効です。")


def save_to_chroma(review_id: int, code: str, result: list[dict]) -> None:
    """ChromaDB にコード + 解析結果を保存。失敗時は warning のみ。"""
    if _chroma_collection is None:
        logger.warning("ChromaDB 未接続のためベクトル保存をスキップ")
        return
    try:
        document = f"CODE:\n{code}\n\nANALYSIS:\n{json.dumps(result, indent=2)}"
        _chroma_collection.add(
            ids=[f"review_{review_id}"],
            documents=[document],
            metadatas=[{
                "review_id": review_id,
                "risk_count": len(result),
            }],
        )
    except Exception as e:
        logger.warning("ChromaDB 保存失敗: %s", e)
