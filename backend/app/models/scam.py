from sqlalchemy import Column, Integer, String, DateTime, Text, Index, func
from app.db.session import Base

class ScamNumber(Base):
    __tablename__ = "scam_numbers"
    id = Column(Integer, primary_key=True)
    number = Column(String(20), nullable=False, unique=True, index=True)
    category = Column(String(50))
    report_count = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())

class ScamURL(Base):
    __tablename__ = "scam_urls"
    id = Column(Integer, primary_key=True)
    url_hash = Column(String(64), nullable=False, unique=True, index=True)
    domain = Column(String(255), index=True)
    category = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())

class ScamKeyword(Base):
    __tablename__ = "scam_keywords"
    id = Column(Integer, primary_key=True)
    keyword = Column(String(100), nullable=False, unique=True, index=True)
    weight = Column(Integer, default=1)
    language = Column(String(10), default="en")

class UserReport(Base):
    __tablename__ = "user_reports"
    id = Column(Integer, primary_key=True)
    report_type = Column(String(10))
    content_hash = Column(String(64), index=True)
    device_id = Column(String(64), index=True) 
    note = Column(Text)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, server_default=func.now())

Index("ix_reports_type_status", UserReport.report_type, UserReport.status)