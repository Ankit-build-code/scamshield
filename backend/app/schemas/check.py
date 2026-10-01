from pydantic import BaseModel, Field
from typing import Literal, List, Optional

class CheckRequest(BaseModel):
    input_type: Literal["number", "url", "message"]
    content: str = Field(..., min_length=1, max_length=5000)

class CheckResponse(BaseModel):
    verdict: Literal["safe", "suspicious", "dangerous"]
    score: int
    reasons: List[str]
    explanation: Optional[str] = None
    advice: Optional[str] = None