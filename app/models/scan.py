from sqlalchemy import Column, String, Integer, Float, DateTime, Text, JSON, Boolean
from sqlalchemy.sql import func
from app.db.database import Base
import uuid


class ScanResult(Base):
    """Scan result model matching the mobile app's ScanResult interface"""
    __tablename__ = "scan_results"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    content = Column(Text, nullable=False)
    content_type = Column(String(20), nullable=False, default="text")
    content_hash = Column(String(64), nullable=False, index=True)

    # Analysis results
    verdict = Column(String(20), nullable=False)  # VERIFIED, UNCLEAR, LIKELY_FAKE, CONFIRMED_FAKE
    credibility_score = Column(Integer, nullable=False)  # 0-100
    confidence = Column(Float, nullable=False)  # 0-1

    # Metadata
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    source_app = Column(String(100))
    processing_tier = Column(Integer, default=2)  # 1=device, 2=edge, 3=cloud
    processing_time_ms = Column(Integer)

    # Explanation
    explanation_summary = Column(Text)
    explanation_reasons = Column(JSON)  # Array of strings
    counter_evidence = Column(JSON)  # Optional array

    # Sources
    sources = Column(JSON)  # Array of source objects

    # Analytics
    cached = Column(Boolean, default=False)
    user_id_hash = Column(String(64), index=True)  # Privacy: hashed user ID

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SourceCredibility(Base):
    """Source credibility ratings"""
    __tablename__ = "source_credibility"

    domain = Column(String(255), primary_key=True)
    credibility_score = Column(Float, nullable=False)  # 0.0 to 1.0
    bias_rating = Column(String(50))
    fact_check_record = Column(JSON)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class KnownFake(Base):
    """Registry of known fake content"""
    __tablename__ = "known_fakes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    content_hash = Column(String(64), unique=True, nullable=False, index=True)
    content_type = Column(String(20))
    verified_fake = Column(Boolean, default=True)
    source_fact_checker = Column(String(100))
    report_count = Column(Integer, default=1)
    added_at = Column(DateTime(timezone=True), server_default=func.now())


class UserFeedback(Base):
    """User feedback on scan results"""
    __tablename__ = "user_feedback"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    scan_id = Column(String, nullable=False, index=True)
    user_id_hash = Column(String(64), index=True)
    feedback_type = Column(String(20), nullable=False)  # agree, disagree, report_error
    comment = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
