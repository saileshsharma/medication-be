"""
API Routes
Defines all API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, text
from typing import List, Optional
from datetime import datetime, timedelta

from app.db.database import get_db
from app.models.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    ScanHistoryResponse,
    StatsResponse,
    FeedbackRequest,
    HealthResponse
)
from app.models.scan import ScanResult, UserFeedback
from app.services.analyzer_service import analyzer_service
from app.services.cache import cache
from app.core.config import settings

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse, tags=["Analysis"])
async def analyze_content(
    request: AnalyzeRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze content for credibility

    This endpoint analyzes text content using AI/NLP and fact-checking APIs
    to determine its credibility and identify potential misinformation.

    **Parameters:**
    - content: The text content to analyze (required)
    - content_type: Type of content (default: "text")
    - source_app: The app where content was found (optional)
    - user_id_hash: Hashed user identifier for history (optional)

    **Returns:**
    - Complete analysis with credibility score, verdict, sources, and explanation
    """
    try:
        result = await analyzer_service.analyze_content(
            content=request.content,
            content_type=request.content_type,
            source_app=request.source_app or "Unknown",
            user_id_hash=request.user_id_hash or "anonymous",
            db=db
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/history", response_model=ScanHistoryResponse, tags=["History"])
def get_scan_history(
    user_id_hash: str = Query(..., description="Hashed user identifier"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    Get scan history for a user

    Returns paginated list of previous scans performed by the user.
    """
    offset = (page - 1) * page_size

    # Get total count
    total = db.query(ScanResult).filter(
        ScanResult.user_id_hash == user_id_hash
    ).count()

    # Get scans for current page
    scans = db.query(ScanResult).filter(
        ScanResult.user_id_hash == user_id_hash
    ).order_by(desc(ScanResult.timestamp)).offset(offset).limit(page_size).all()

    # Convert to response format
    scan_responses = []
    for scan in scans:
        scan_responses.append(AnalyzeResponse(
            id=scan.id,
            content=scan.content,
            content_type=scan.content_type,
            verdict=scan.verdict,
            credibility_score=scan.credibility_score,
            confidence=scan.confidence,
            timestamp=int(scan.timestamp.timestamp() * 1000),
            source_app=scan.source_app,
            sources=scan.sources or [],
            explanation={
                'summary': scan.explanation_summary,
                'reasons': scan.explanation_reasons or []
            },
            processing_tier=scan.processing_tier,
            processing_time_ms=scan.processing_time_ms,
            cached=scan.cached
        ))

    return ScanHistoryResponse(
        scans=scan_responses,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/stats", response_model=StatsResponse, tags=["Statistics"])
def get_user_stats(
    user_id_hash: str = Query(..., description="Hashed user identifier"),
    days: int = Query(30, ge=1, le=365, description="Number of days to include"),
    db: Session = Depends(get_db)
):
    """
    Get user statistics

    Returns aggregated statistics about user's scan history including:
    - Total scans
    - Breakdown by verdict
    - Average credibility score
    - Scans per day
    - Top sources
    """
    # Date range
    start_date = datetime.now() - timedelta(days=days)

    # Get all scans in range
    scans = db.query(ScanResult).filter(
        ScanResult.user_id_hash == user_id_hash,
        ScanResult.timestamp >= start_date
    ).all()

    total_scans = len(scans)

    if total_scans == 0:
        return StatsResponse(
            total_scans=0,
            verified_count=0,
            unclear_count=0,
            fake_count=0,
            average_credibility_score=0.0,
            scans_by_day={},
            top_sources=[]
        )

    # Count by verdict
    verified_count = len([s for s in scans if s.verdict == 'VERIFIED'])
    unclear_count = len([s for s in scans if s.verdict == 'UNCLEAR'])
    fake_count = len([s for s in scans if s.verdict in ['LIKELY_FAKE', 'CONFIRMED_FAKE']])

    # Average score
    avg_score = sum(s.credibility_score for s in scans) / total_scans

    # Scans by day
    scans_by_day = {}
    for scan in scans:
        date_key = scan.timestamp.strftime('%Y-%m-%d')
        scans_by_day[date_key] = scans_by_day.get(date_key, 0) + 1

    # Top sources
    source_counts = {}
    for scan in scans:
        if scan.sources:
            for source in scan.sources:
                name = source.get('name', 'Unknown')
                source_counts[name] = source_counts.get(name, 0) + 1

    top_sources = [
        {'name': name, 'count': count}
        for name, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    ]

    return StatsResponse(
        total_scans=total_scans,
        verified_count=verified_count,
        unclear_count=unclear_count,
        fake_count=fake_count,
        average_credibility_score=round(avg_score, 2),
        scans_by_day=scans_by_day,
        top_sources=top_sources
    )


@router.post("/feedback", tags=["Feedback"])
def submit_feedback(
    feedback: FeedbackRequest,
    user_id_hash: str = Query("anonymous", description="Hashed user identifier"),
    db: Session = Depends(get_db)
):
    """
    Submit feedback on a scan result

    Allows users to provide feedback on the accuracy of scan results.
    This helps improve the system over time.
    """
    # Verify scan exists
    scan = db.query(ScanResult).filter(ScanResult.id == feedback.scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    # Create feedback record
    feedback_record = UserFeedback(
        scan_id=feedback.scan_id,
        user_id_hash=user_id_hash,
        feedback_type=feedback.feedback_type,
        comment=feedback.comment
    )

    db.add(feedback_record)
    db.commit()

    return {"status": "success", "message": "Feedback submitted successfully"}


@router.get("/health", response_model=HealthResponse, tags=["System"])
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint

    Returns the health status of the API and its dependencies.
    """
    # Check database
    try:
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    # Check Redis
    redis_status = "healthy" if cache.is_healthy() else "unhealthy"

    return HealthResponse(
        status="healthy" if db_status == "healthy" else "degraded",
        version=settings.APP_VERSION,
        timestamp=datetime.now(),
        database=db_status,
        redis=redis_status
    )


@router.get("/cache/stats", tags=["System"])
def get_cache_stats():
    """
    Get cache statistics

    Returns information about the Redis cache performance.
    """
    return cache.get_stats()


@router.delete("/cache/clear", tags=["System"])
def clear_cache():
    """
    Clear all cache entries

    **Warning:** This will clear all cached analysis results.
    Use with caution in production.
    """
    if cache.clear_all():
        return {"status": "success", "message": "Cache cleared"}
    else:
        raise HTTPException(status_code=500, detail="Failed to clear cache")
