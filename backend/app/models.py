from __future__ import annotations

from pydantic import BaseModel, Field


class ReviewRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=102400, description="C source code to review")


class Risk(BaseModel):
    line: str = ""
    category: str = ""
    issue: str = ""
    risk: str = ""
    recommendation: str = ""


class ReviewResponse(BaseModel):
    risks: list[Risk] = []
    risk_count: int = 0
