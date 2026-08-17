"""レビューロジック — Groq API 呼出 + DB 保存"""
from __future__ import annotations

import json
import logging
import os
import re

from openai import OpenAI, APITimeoutError, APIError
from fastapi import APIRouter, HTTPException, UploadFile, File

from app.database import save_review, save_to_chroma
from app.models import ReviewRequest, ReviewResponse, Risk
from app.prompt import SYSTEM_PROMPT, build_user_prompt

logger = logging.getLogger(__name__)
router = APIRouter()

ALLOWED_EXTENSIONS = {".c", ".h"}
MAX_FILE_SIZE = 102400  # 100KB


def _parse_risks(text: str) -> list[dict]:
    """API レスポンスから JSON 配列をパース。
    ```json フェンスが含まれる場合は除去してからパース。
    パース失敗時はテキスト全体を1リスクとして返す。
    """
    # ```json ... ``` フェンス除去
    cleaned = re.sub(r"```(?:json)?\s*", "", text).strip()
    cleaned = cleaned.rstrip("`").strip()

    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, list):
            return parsed
    except json.JSONDecodeError:
        pass

    # フォールバック: テキスト全体を1リスクとして扱う
    logger.warning("JSON パース失敗。フォールバック処理を適用")
    return [{
        "line": "N/A",
        "category": "Parse Error",
        "issue": text[:500],
        "risk": "Could not parse structured response from AI.",
        "recommendation": "Review the raw output above.",
    }]


async def _do_review(code: str) -> ReviewResponse:
    """コードを受け取り、Groq API でレビュー → DB 保存 → レスポンス返却"""
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY が設定されていません")

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
    )

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            max_tokens=4096,
            # gpt-oss は reasoning もこの枠を消費する。長考不要・本文へ枠を回す
            # （openai==1.30.1 は reasoning_effort 引数未対応のため extra_body で渡す）
            extra_body={"reasoning_effort": "low"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(code)},
            ],
        )
    except APITimeoutError:
        raise HTTPException(status_code=503, detail="Groq API タイムアウト")
    except APIError as e:
        raise HTTPException(status_code=503, detail=f"Groq API エラー: {e}")

    raw_text = response.choices[0].message.content or ""
    risk_dicts = _parse_risks(raw_text)

    risks = []
    for r in risk_dicts:
        risks.append(Risk(
            line=str(r.get("line", "")),
            category=str(r.get("category", "")),
            issue=str(r.get("issue", "")),
            risk=str(r.get("risk", "")),
            recommendation=str(r.get("recommendation", "")),
        ))

    # DB 保存（失敗してもレビュー結果は返す）
    review_id = await save_review(code, risk_dicts, len(risks))
    if review_id is not None:
        save_to_chroma(review_id, code, risk_dicts)

    return ReviewResponse(risks=risks, risk_count=len(risks))


@router.post("/review", response_model=ReviewResponse)
async def review_code(request: ReviewRequest):
    """テキストで送信されたコードをレビュー"""
    return await _do_review(request.code)


@router.post("/review/upload", response_model=ReviewResponse)
async def review_upload(file: UploadFile = File(...)):
    """ファイルアップロードでレビュー（.c .h のみ）"""
    # 拡張子チェック
    filename = file.filename or ""
    ext = ""
    if "." in filename:
        ext = "." + filename.rsplit(".", 1)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="許可されるファイル形式は .c .h のみです")

    # ファイル読み込み
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="ファイルサイズが100KBを超えています")

    code = content.decode("utf-8", errors="replace")
    return await _do_review(code)
