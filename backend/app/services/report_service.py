import hashlib
from sqlalchemy.orm import Session
from app.models.scam import UserReport, ScamNumber, ScamURL
from app.services.scam_detector import normalize_number, normalize_url

REPORT_THRESHOLD = 3  # itni baar report hone par auto-verify ho jayega

def hash_content(report_type: str, content: str) -> str:
    if report_type == "number":
        normalized = normalize_number(content)
    elif report_type == "url":
        normalized = normalize_url(content)
    else:
        normalized = content.strip().lower()
    return hashlib.sha256(normalized.encode()).hexdigest()

def create_report(db: Session, report_type: str, content: str, note: str | None, device_id: str):
    content_hash = hash_content(report_type, content)

    already_reported = db.query(UserReport).filter_by(
        report_type=report_type, content_hash=content_hash, device_id=device_id
    ).first()

    if already_reported:
        total_reports = db.query(UserReport).filter_by(
            report_type=report_type, content_hash=content_hash
        ).count()
        return already_reported, total_reports

    report = UserReport(
        report_type=report_type,
        content_hash=content_hash,
        device_id=device_id,
        note=note,
        status="pending",
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    total_reports = db.query(UserReport).filter_by(
        report_type=report_type, content_hash=content_hash
    ).count()

    if total_reports >= REPORT_THRESHOLD:
        _promote_to_scam_db(db, report_type, content, total_reports)
        db.query(UserReport).filter_by(
            report_type=report_type, content_hash=content_hash
        ).update({"status": "verified"})
        db.commit()
        report.status = "verified"

    return report, total_reports
def _promote_to_scam_db(db: Session, report_type: str, content: str, total_reports: int):
    if report_type == "number":
        n = normalize_number(content)
        existing = db.query(ScamNumber).filter_by(number=n).first()
        if existing:
            existing.report_count = max(existing.report_count, total_reports)
        else:
            db.add(ScamNumber(number=n, category="user_reported", report_count=total_reports))
    elif report_type == "url":
        u = normalize_url(content)
        h = hashlib.sha256(u.encode()).hexdigest()
        if not db.query(ScamURL).filter_by(url_hash=h).first():
            domain = u.split("/")[2] if "//" in u else u
            db.add(ScamURL(url_hash=h, domain=domain, category="user_reported"))
    db.commit()