"""
Main Analysis Service
Orchestrates text analysis, fact checking, and result generation
"""

import time
from typing import Dict
from datetime import datetime
from sqlalchemy.orm import Session

from app.services.text_analyzer import text_analyzer
from app.services.fact_checker import fact_checker
from app.services.cache import cache
from app.models.scan import ScanResult, KnownFake
from app.models.schemas import AnalyzeResponse, Source, Explanation


class AnalyzerService:
    """Main service for analyzing content"""

    async def analyze_content(
        self,
        content: str,
        content_type: str,
        source_app: str,
        user_id_hash: str,
        db: Session
    ) -> AnalyzeResponse:
        """
        Analyze content and return credibility assessment
        """
        start_time = time.time()

        # Generate content hash
        content_hash = text_analyzer.generate_hash(content)

        # Check cache first
        cache_key = f"scan:{content_hash}"
        cached_result = cache.get(cache_key)
        if cached_result:
            cached_result['cached'] = True
            cached_result['processing_time_ms'] = int((time.time() - start_time) * 1000)
            return AnalyzeResponse(**cached_result)

        # Check if content is known fake
        known_fake = db.query(KnownFake).filter(
            KnownFake.content_hash == content_hash
        ).first()

        if known_fake:
            # Return immediate fake verdict
            result = self._create_known_fake_response(
                content, content_hash, source_app, start_time
            )
        else:
            # Perform full analysis
            result = await self._perform_analysis(
                content, content_hash, content_type, source_app, start_time, db
            )

        # Save to database
        scan_record = ScanResult(
            id=result['id'],
            content=content,
            content_type=content_type,
            content_hash=content_hash,
            verdict=result['verdict'],
            credibility_score=result['credibility_score'],
            confidence=result['confidence'],
            timestamp=datetime.fromtimestamp(result['timestamp'] / 1000),
            source_app=source_app,
            processing_tier=result['processing_tier'],
            processing_time_ms=result['processing_time_ms'],
            explanation_summary=result['explanation']['summary'],
            explanation_reasons=result['explanation']['reasons'],
            sources=[dict(s) for s in result['sources']],
            cached=result['cached'],
            user_id_hash=user_id_hash
        )
        db.add(scan_record)
        db.commit()

        # Cache the result
        cache.set(cache_key, result, ttl=3600)  # 1 hour

        return AnalyzeResponse(**result)

    async def _perform_analysis(
        self,
        content: str,
        content_hash: str,
        content_type: str,
        source_app: str,
        start_time: float,
        db: Session
    ) -> Dict:
        """Perform full text analysis and fact checking"""

        # Run text analysis
        text_analysis = text_analyzer.analyze(content)

        # Run fact checking
        fact_check_results = await fact_checker.check_facts(content)

        # Combine results
        credibility_score = text_analysis['credibility_score']
        sources = fact_check_results['sources']

        # Adjust credibility based on sources
        if fact_check_results['trusted_source_count'] > 0:
            # Boost score if trusted sources found
            credibility_score = min(100, credibility_score + 10)
        elif fact_check_results['source_count'] == 0:
            # Reduce score if no sources found
            credibility_score = max(0, credibility_score - 15)

        # Determine final verdict
        verdict, confidence = self._determine_final_verdict(
            credibility_score,
            text_analysis['verdict'],
            sources
        )

        # Generate explanation
        explanation = self._generate_final_explanation(
            text_analysis['explanation'],
            fact_check_results,
            credibility_score
        )

        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)

        # Generate unique ID
        import uuid
        scan_id = str(uuid.uuid4())

        return {
            'id': scan_id,
            'content': content,
            'content_type': content_type,
            'verdict': verdict,
            'credibility_score': credibility_score,
            'confidence': confidence,
            'timestamp': int(datetime.now().timestamp() * 1000),
            'source_app': source_app,
            'sources': sources,
            'explanation': explanation,
            'processing_tier': 2,  # Edge processing
            'processing_time_ms': processing_time_ms,
            'cached': False
        }

    def _create_known_fake_response(
        self,
        content: str,
        content_hash: str,
        source_app: str,
        start_time: float
    ) -> Dict:
        """Create response for known fake content"""
        import uuid

        return {
            'id': str(uuid.uuid4()),
            'content': content,
            'content_type': 'text',
            'verdict': 'CONFIRMED_FAKE',
            'credibility_score': 5,
            'confidence': 0.99,
            'timestamp': int(datetime.now().timestamp() * 1000),
            'source_app': source_app,
            'sources': [],
            'explanation': {
                'summary': 'This content is in our database of known misinformation',
                'reasons': [
                    'Previously verified as false by fact-checkers',
                    'Reported multiple times',
                    'Contradicts verified information'
                ]
            },
            'processing_tier': 1,
            'processing_time_ms': int((time.time() - start_time) * 1000),
            'cached': False
        }

    def _determine_final_verdict(
        self,
        credibility_score: int,
        initial_verdict: str,
        sources: list
    ) -> tuple:
        """Determine final verdict with confidence"""

        # Count how many sources agree/disagree
        agreeing_sources = [s for s in sources if s.get('agrees_with_content') is True]
        disagreeing_sources = [s for s in sources if s.get('agrees_with_content') is False]

        if len(disagreeing_sources) >= 2:
            return 'LIKELY_FAKE', 0.85

        if credibility_score >= 70 and len(agreeing_sources) >= 2:
            return 'VERIFIED', 0.9
        elif credibility_score >= 70:
            return 'VERIFIED', 0.75
        elif credibility_score >= 50:
            return 'UNCLEAR', 0.65
        elif credibility_score >= 30:
            return 'LIKELY_FAKE', 0.75
        else:
            return 'LIKELY_FAKE', 0.85

    def _generate_final_explanation(
        self,
        text_explanation: Dict,
        fact_check_results: Dict,
        final_score: int
    ) -> Dict:
        """Generate comprehensive explanation"""

        reasons = list(text_explanation['reasons'])

        # Add fact-check insights
        source_count = fact_check_results['source_count']
        trusted_count = fact_check_results['trusted_source_count']

        if trusted_count > 0:
            reasons.append(f'{trusted_count} trusted sources found')
        elif source_count == 0:
            reasons.append('No verifying sources found')

        # Adjust summary based on final score
        if final_score >= 70:
            summary = 'Content appears credible and well-sourced'
        elif final_score >= 50:
            summary = 'Unable to verify - proceed with caution'
        else:
            summary = 'Content shows multiple signs of misinformation'

        return {
            'summary': summary,
            'reasons': reasons[:3]  # Top 3 reasons
        }


# Singleton instance
analyzer_service = AnalyzerService()
