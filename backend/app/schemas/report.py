from pydantic import BaseModel, Field
from typing import Literal, Optional

class ReportRequest(BaseModel):
    report_type: Literal["number", "url", "message"]
    content: str = Field(..., min_length=1, max_length=5000)
    note: Optional[str] = Field(None, max_length=500)
    device_id: str = Field(..., min_length=8, max_length=64)

class ReportResponse(BaseModel):
    id: int
    status: str
    message: str