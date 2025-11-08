from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# Source schemas
class Source(BaseModel):
    """Source verification info"""
    name: str
    url: str
    credibility_rating: float = Field(ge=0.0, le=1.0)
    agrees_with_content: Optional[bool] = None


class Explanation(BaseModel):
    """Explanation for the verdict"""
    summary: str
    reasons: List[str]
    counter_evidence: Optional[List[str]] = None


# Request schemas
class AnalyzeRequest(BaseModel):
    """Request to analyze content"""
    content: str = Field(min_length=1, max_length=10000)
    content_type: str = Field(default="text", pattern="^(text|image|video|mixed)$")
    source_app: Optional[str] = None
    user_id_hash: Optional[str] = None  # For personalized history


# Response schemas
class AnalyzeResponse(BaseModel):
    """Analysis result response"""
    id: str
    content: str
    content_type: str
    verdict: str  # VERIFIED, UNCLEAR, LIKELY_FAKE, CONFIRMED_FAKE
    credibility_score: int = Field(ge=0, le=100)
    confidence: float = Field(ge=0.0, le=1.0)
    timestamp: int  # Unix timestamp in milliseconds
    source_app: Optional[str] = None
    sources: List[Source]
    explanation: Explanation
    processing_tier: int = Field(ge=1, le=3)
    processing_time_ms: int
    cached: bool

    class Config:
        from_attributes = True


class ScanHistoryResponse(BaseModel):
    """Scan history response"""
    scans: List[AnalyzeResponse]
    total: int
    page: int
    page_size: int


class StatsResponse(BaseModel):
    """User statistics response"""
    total_scans: int
    verified_count: int
    unclear_count: int
    fake_count: int
    average_credibility_score: float
    scans_by_day: dict  # Date -> count mapping
    top_sources: List[dict]


class FeedbackRequest(BaseModel):
    """User feedback request"""
    scan_id: str
    feedback_type: str = Field(pattern="^(agree|disagree|report_error)$")
    comment: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: datetime
    database: str
    redis: str
