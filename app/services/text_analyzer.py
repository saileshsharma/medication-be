"""
Text Analysis Service
Analyzes text content for credibility using NLP and pattern matching
"""

import re
import hashlib
from typing import Dict, List, Tuple
from textblob import TextBlob
import nltk
from datetime import datetime

# Download required NLTK data (run once)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)


class TextAnalyzer:
    """Analyzes text content for misinformation indicators"""

    # Patterns that indicate potential misinformation
    SUSPICIOUS_PATTERNS = [
        r'\bSHOCKING\b',
        r'\bBREAKING[:\s]',
        r'\bURGENT[:\s]',
        r'you won\'?t believe',
        r'doctors hate',
        r'this one (trick|secret|weird trick)',
        r'what .+ don\'?t want you to know',
        r'share (this )?before (it\'?s|they) (deleted?|remove)',
        r'big pharma',
        r'they don\'?t want you to know',
        r'mainstream media (won\'?t|refuses to)',
        r'\bcure for (cancer|aids|diabetes)',
        r'secret(s)? (they|the government)',
    ]

    # Credible news indicators
    CREDIBLE_PATTERNS = [
        r'according to (a )?(study|research|report)',
        r'published in',
        r'(scientists?|researchers?) (say|found|discovered)',
        r'peer[- ]reviewed',
        r'study shows?',
        r'research indicates?',
    ]

    # Emotional/sensational words
    EMOTIONAL_WORDS = [
        'shocking', 'amazing', 'incredible', 'unbelievable', 'mindblowing',
        'devastating', 'terrifying', 'outrageous', 'scandal', 'bombshell'
    ]

    def __init__(self):
        """Initialize the text analyzer"""
        self.suspicious_regex = re.compile('|'.join(self.SUSPICIOUS_PATTERNS), re.IGNORECASE)
        self.credible_regex = re.compile('|'.join(self.CREDIBLE_PATTERNS), re.IGNORECASE)

    def analyze(self, text: str) -> Dict:
        """
        Main analysis function
        Returns a dict with credibility score, verdict, and explanation
        """
        # Generate content hash
        content_hash = self.generate_hash(text)

        # Run various analyses
        suspicious_score = self._check_suspicious_patterns(text)
        credible_score = self._check_credible_patterns(text)
        sentiment_score = self._analyze_sentiment(text)
        complexity_score = self._analyze_complexity(text)
        emotional_score = self._check_emotional_language(text)

        # Calculate overall credibility score (0-100)
        credibility_score = self._calculate_credibility(
            suspicious_score,
            credible_score,
            sentiment_score,
            complexity_score,
            emotional_score
        )

        # Determine verdict
        verdict, confidence = self._determine_verdict(credibility_score, suspicious_score)

        # Generate explanation
        explanation = self._generate_explanation(
            text,
            suspicious_score,
            credible_score,
            emotional_score,
            credibility_score
        )

        return {
            'content_hash': content_hash,
            'credibility_score': credibility_score,
            'verdict': verdict,
            'confidence': confidence,
            'explanation': explanation,
            'analysis_details': {
                'suspicious_score': suspicious_score,
                'credible_score': credible_score,
                'sentiment_score': sentiment_score,
                'complexity_score': complexity_score,
                'emotional_score': emotional_score
            }
        }

    def generate_hash(self, text: str) -> str:
        """Generate SHA-256 hash of content"""
        return hashlib.sha256(text.encode()).hexdigest()

    def _check_suspicious_patterns(self, text: str) -> float:
        """Check for suspicious patterns (0-1, higher = more suspicious)"""
        matches = self.suspicious_regex.findall(text)
        # Each match increases suspicion
        score = min(len(matches) * 0.2, 1.0)
        return score

    def _check_credible_patterns(self, text: str) -> float:
        """Check for credible patterns (0-1, higher = more credible)"""
        matches = self.credible_regex.findall(text)
        score = min(len(matches) * 0.25, 1.0)
        return score

    def _analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment polarity (0-1, 0.5 = neutral)"""
        try:
            blob = TextBlob(text)
            # Polarity is -1 to 1, convert to 0 to 1
            polarity = (blob.sentiment.polarity + 1) / 2
            # Extreme sentiment (very positive or negative) can indicate bias
            # We want moderate sentiment for credible news
            distance_from_neutral = abs(polarity - 0.5)
            return 1 - distance_from_neutral
        except:
            return 0.5

    def _analyze_complexity(self, text: str) -> float:
        """
        Analyze text complexity (0-1)
        Too simple or too complex can indicate issues
        """
        words = text.split()
        if len(words) == 0:
            return 0.0

        # Average word length
        avg_word_length = sum(len(word) for word in words) / len(words)

        # Sentence count
        sentences = text.split('.')
        avg_sentence_length = len(words) / max(len(sentences), 1)

        # Ideal ranges: 4-6 chars per word, 15-25 words per sentence
        word_length_score = 1 - abs(avg_word_length - 5) / 10
        sentence_length_score = 1 - abs(avg_sentence_length - 20) / 30

        return (word_length_score + sentence_length_score) / 2

    def _check_emotional_language(self, text: str) -> float:
        """Check for emotional/sensational language (0-1, higher = more emotional)"""
        text_lower = text.lower()
        emotional_count = sum(1 for word in self.EMOTIONAL_WORDS if word in text_lower)

        # Check for excessive caps
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)

        # Check for excessive punctuation
        exclamation_count = text.count('!')
        question_count = text.count('?')

        emotional_score = min((emotional_count * 0.2 + caps_ratio * 2 + exclamation_count * 0.1), 1.0)
        return emotional_score

    def _calculate_credibility(
        self,
        suspicious: float,
        credible: float,
        sentiment: float,
        complexity: float,
        emotional: float
    ) -> int:
        """
        Calculate overall credibility score (0-100)

        Weights:
        - Suspicious patterns: -40 points
        - Credible patterns: +30 points
        - Sentiment neutrality: +15 points
        - Text complexity: +10 points
        - Low emotional language: +15 points
        """
        base_score = 50  # Start neutral

        # Deduct for suspicious patterns
        base_score -= suspicious * 40

        # Add for credible patterns
        base_score += credible * 30

        # Add for neutral sentiment
        base_score += sentiment * 15

        # Add for appropriate complexity
        base_score += complexity * 10

        # Deduct for emotional language
        base_score -= emotional * 15

        # Clamp to 0-100
        return max(0, min(100, int(base_score)))

    def _determine_verdict(self, credibility_score: int, suspicious_score: float) -> Tuple[str, float]:
        """
        Determine verdict based on credibility score
        Returns (verdict, confidence)
        """
        if credibility_score >= 70:
            return 'VERIFIED', 0.8
        elif credibility_score >= 50:
            return 'UNCLEAR', 0.6
        elif credibility_score >= 30:
            return 'LIKELY_FAKE', 0.7
        else:
            return 'LIKELY_FAKE', 0.9

    def _generate_explanation(
        self,
        text: str,
        suspicious: float,
        credible: float,
        emotional: float,
        score: int
    ) -> Dict:
        """Generate human-readable explanation"""
        reasons = []

        # Suspicious patterns
        if suspicious > 0.3:
            reasons.append('Sensational or clickbait language detected')
        if suspicious > 0.6:
            reasons.append('Multiple suspicious patterns found')

        # Credible patterns
        if credible > 0.3:
            reasons.append('References to studies or research found')
        if credible > 0.6:
            reasons.append('Multiple credible sources referenced')

        # Emotional language
        if emotional > 0.4:
            reasons.append('Excessive emotional or sensational language')
        elif emotional < 0.2:
            reasons.append('Neutral, factual tone')

        # Default reasons based on score
        if score >= 70:
            if not reasons:
                reasons.append('Content appears factual and well-sourced')
            summary = 'Content appears credible'
        elif score >= 50:
            if not reasons:
                reasons.append('Unable to verify with high confidence')
            summary = 'Credibility unclear - needs more verification'
        else:
            if not reasons:
                reasons.append('Multiple indicators of potential misinformation')
            summary = 'Content shows signs of misinformation'

        return {
            'summary': summary,
            'reasons': reasons[:3]  # Limit to top 3 reasons
        }


# Singleton instance
text_analyzer = TextAnalyzer()
