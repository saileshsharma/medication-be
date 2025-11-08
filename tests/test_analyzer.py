"""
Tests for text analyzer service
"""

import pytest
from app.services.text_analyzer import text_analyzer


class TestTextAnalyzer:
    """Test cases for TextAnalyzer"""

    def test_analyze_fake_content(self):
        """Test that obviously fake content is detected"""
        fake_text = "SHOCKING! Doctors HATE this one weird trick! Click before it's deleted!"
        result = text_analyzer.analyze(fake_text)

        assert result['credibility_score'] < 50
        assert result['verdict'] in ['LIKELY_FAKE']
        assert 'sensational' in result['explanation']['summary'].lower() or \
               'misinformation' in result['explanation']['summary'].lower()

    def test_analyze_credible_content(self):
        """Test that credible content is recognized"""
        credible_text = (
            "According to a study published in Nature, researchers found "
            "that climate change is affecting global temperatures."
        )
        result = text_analyzer.analyze(credible_text)

        assert result['credibility_score'] > 50
        assert 'credible' in result['explanation']['summary'].lower() or \
               'verified' in result['verdict'].lower()

    def test_content_hash_generation(self):
        """Test that content hash is generated correctly"""
        text = "Sample text"
        hash1 = text_analyzer.generate_hash(text)
        hash2 = text_analyzer.generate_hash(text)

        # Same text should generate same hash
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hash length

    def test_suspicious_patterns(self):
        """Test suspicious pattern detection"""
        text_with_patterns = "BREAKING: SHOCKING news you won't believe!"
        score = text_analyzer._check_suspicious_patterns(text_with_patterns)

        assert score > 0.3  # Should detect multiple patterns

    def test_credible_patterns(self):
        """Test credible pattern detection"""
        text = "According to research published in peer-reviewed journal"
        score = text_analyzer._check_credible_patterns(text)

        assert score > 0.3  # Should detect credible patterns

    def test_empty_content(self):
        """Test handling of empty content"""
        result = text_analyzer.analyze("")

        assert 'credibility_score' in result
        assert 'verdict' in result
        assert result['credibility_score'] >= 0
        assert result['credibility_score'] <= 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
