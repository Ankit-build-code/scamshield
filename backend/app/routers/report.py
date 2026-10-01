from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.report import ReportRequest, ReportResponse
from app.services.report_service import create_report
from app.core.limiter import limiter

router = APIRouter(prefix="/report", tags=["report"])

@router.post("", response_model=ReportResponse)
@limiter.limit("5/minute")
def report(request: Request, req: ReportRequest, db: Session = Depends(get_db)):
    result, total = create_report(db, req.report_type, req.content, req.note, req.device_id)

    if result.status == "verified":
        msg = "धन्यवाद! इसे कई लोगों ने report किया है, अब यह हमारे scam database में जुड़ गया है।"
    else:
        msg = f"धन्यवाद, आपकी report मिल गई है। (अब तक {total} बार report हुआ है)"

    return ReportResponse(id=result.id, status=result.status, message=msg)