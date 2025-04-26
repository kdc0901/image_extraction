import os
import pytest
from pathlib import Path
from src.processing.summarizer import TextSummarizer

class TestTextSummarizer:
    """TextSummarizer 클래스 테스트"""
    
    @pytest.fixture
    def summarizer(self):
        """TextSummarizer 인스턴스 생성"""
        return TextSummarizer(
            min_sentence_length=5,
            max_sentence_length=200,
            summary_ratio=0.3,
            key_points_count=3
        )
    
    @pytest.fixture
    def sample_texts(self):
        """테스트용 샘플 텍스트"""
        return [
            "인공지능은 인간의 학습능력과 추론능력, 지각능력, 자연언어의 이해능력 등을 컴퓨터 프로그램으로 실현한 기술이다.",
            "머신러닝은 인공지능의 한 분야로, 컴퓨터가 데이터로부터 학습할 수 있도록 하는 알고리즘과 기술을 개발하는 분야이다.",
            "딥러닝은 머신러닝의 한 분야로, 인공신경망을 기반으로 한 학습 방법이다.",
            "자연어 처리(NLP)는 컴퓨터가 인간의 언어를 이해하고 생성하는 기술이다.",
            "컴퓨터 비전은 컴퓨터가 이미지나 비디오를 이해하고 분석하는 기술이다."
        ]
    
    def test_preprocess_text(self, summarizer):
        """텍스트 전처리 테스트"""
        text = "Hello, World!  This is a test."
        expected = "Hello World This is a test"
        assert summarizer._preprocess_text(text) == expected
    
    def test_detect_language(self, summarizer):
        """언어 감지 테스트"""
        # 한국어 테스트
        korean_text = "안녕하세요. 이것은 테스트입니다."
        assert summarizer._detect_language(korean_text) == 'ko'
        
        # 영어 테스트
        english_text = "Hello. This is a test."
        assert summarizer._detect_language(english_text) == 'en'
    
    def test_tokenize_sentences(self, summarizer):
        """문장 토큰화 테스트"""
        text = "첫 번째 문장. 두 번째 문장! 세 번째 문장?"
        sentences = summarizer._tokenize_sentences(text)
        assert len(sentences) == 3
        assert "첫 번째 문장" in sentences[0]
        assert "두 번째 문장" in sentences[1]
        assert "세 번째 문장" in sentences[2]
    
    def test_calculate_sentence_scores(self, summarizer):
        """문장 점수 계산 테스트"""
        sentences = [
            "인공지능은 중요한 기술이다.",
            "머신러닝은 인공지능의 한 분야이다.",
            "이것은 테스트 문장이다."
        ]
        scores = summarizer._calculate_sentence_scores(sentences, 'ko')
        
        # 점수가 계산되었는지 확인
        assert len(scores) == 3
        
        # 관련 문장의 점수가 더 높아야 함
        assert scores[sentences[0]] > scores[sentences[2]]
        assert scores[sentences[1]] > scores[sentences[2]]
    
    def test_extract_key_phrases(self, summarizer):
        """핵심 구문 추출 테스트"""
        text = "인공지능과 머신러닝은 중요한 기술이다. 인공지능은 다양한 분야에서 활용된다."
        phrases = summarizer._extract_key_phrases(text, 'ko', n=2)
        
        # 핵심 구문이 추출되었는지 확인
        assert len(phrases) == 2
        assert "인공지능" in phrases
        assert "머신러닝" in phrases
    
    def test_generate_summary(self, summarizer, sample_texts):
        """요약 생성 테스트"""
        summary = summarizer.generate_summary(sample_texts)
        
        # 요약이 생성되었는지 확인
        assert summary
        assert len(summary.split()) > 0
        
        # 원본 텍스트의 핵심 내용이 포함되어 있는지 확인
        assert "인공지능" in summary
        assert "머신러닝" in summary
    
    def test_extract_key_points(self, summarizer, sample_texts):
        """핵심 포인트 추출 테스트"""
        key_points = summarizer.extract_key_points(sample_texts)
        
        # 핵심 포인트가 추출되었는지 확인
        assert len(key_points) <= summarizer.key_points_count
        assert len(key_points) > 0
        
        # 핵심 포인트가 원본 텍스트에서 추출되었는지 확인
        for point in key_points:
            assert any(point in text for text in sample_texts)
    
    def test_error_handling(self, summarizer):
        """오류 처리 테스트"""
        # 빈 텍스트 리스트
        assert summarizer.generate_summary([]) == ""
        assert summarizer.extract_key_points([]) == []
        
        # 잘못된 언어 감지
        text = "12345" * 100  # 언어 감지가 어려운 텍스트
        assert summarizer._detect_language(text) == 'en'  # 기본값 반환 