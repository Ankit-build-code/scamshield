from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.check import CheckRequest, CheckResponse
from app.services import scam_detector as sd
from app.services.llm_analyzer import analyze_with_llm
from app.core.limiter import limiter

router = APIRouter(prefix="/check", tags=["check"])

@router.post("", response_model=CheckResponse)
@limiter.limit("10/minute")
def check(request: Request, req: CheckRequest, db: Session = Depends(get_db)):
    if req.input_type == "number":
        score, reasons = sd.check_number(db, req.content)
    elif req.input_type == "url":
        score, reasons = sd.check_url(db, req.content)
    else:
        score, reasons = sd.check_message(db, req.content)

    explanation, advice = None, None

    if req.input_type != "number" and score < 90:
        llm = analyze_with_llm(req.input_type, req.content)
        if llm:
            score = max(score, llm["risk_score"])
            explanation, advice = llm["explanation"], llm["advice"]

    score = min(score, 100)
    return CheckResponse(
        verdict=sd.to_verdict(score),
        score=score,
        reasons=reasons,
        explanation=explanation,
        advice=advice,
    )