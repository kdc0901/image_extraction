"""
Text summarization module for extracting key points and generating summaries.
"""

import os
import re
import logging
from typing import List, Dict, Tuple, Optional
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from langdetect import detect
from collections import defaultdict
from tqdm import tqdm

class TextSummarizer:
    """텍스트 요약 및 핵심 포인트 추출 클래스"""
    
    # 한국어 불용어 목록
    KOREAN_STOPWORDS = {
        '이', '그', '저', '것', '수', '등', '들', '및', '에', '의', '가', '을', '를', '이다', '있다',
        '하다', '이런', '저런', '그런', '한', '이번', '저번', '그번', '때', '로', '으로', '에서',
        '이고', '이며', '이면', '이거나', '이든지', '이야', '이에', '이와', '이는', '이가', '이를',
        '이를', '이와', '이는', '이랑', '이든', '이야말로', '이자', '이라도', '이라면', '이라서',
        '이라고', '이라는', '이라니', '이라든지', '이라든가', '이라서는', '이라도', '이라면서',
        '이라면', '이래서', '이래도', '이래야', '이러면', '이러니', '이러한', '이런', '이렇게'
    }
    
    def __init__(
        self,
        min_sentence_length: int = 5,
        max_sentence_length: int = 200,
        summary_ratio: float = 0.3,
        key_points_count: int = 3
    ):
        """
        초기화 함수
        
        Args:
            min_sentence_length (int): 최소 문장 길이
            max_sentence_length (int): 최대 문장 길이
            summary_ratio (float): 요약 비율 (0.0 ~ 1.0)
            key_points_count (int): 핵심 포인트 개수
        """
        self.min_sentence_length = min_sentence_length
        self.max_sentence_length = max_sentence_length
        self.summary_ratio = summary_ratio
        self.key_points_count = key_points_count
        
        # 로거 설정
        self.logger = logging.getLogger(__name__)
        
        # NLTK 리소스 다운로드
        self._download_nltk_resources()
        
        # 언어별 불용어 설정
        self.stopwords = {
            'ko': self.KOREAN_STOPWORDS,
            'en': set(stopwords.words('english'))
        }
    
    def _download_nltk_resources(self) -> None:
        """NLTK 리소스 다운로드"""
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
        except Exception as e:
            self.logger.error(f"NLTK 리소스 다운로드 중 오류 발생: {e}")
    
    def _preprocess_text(self, text: str) -> str:
        """
        텍스트 전처리
        
        Args:
            text (str): 입력 텍스트
            
        Returns:
            str: 전처리된 텍스트
        """
        # 특수 문자 제거
        text = re.sub(r'[^\w\s]', ' ', text)
        # 여러 공백 제거
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _detect_language(self, text: str) -> str:
        """
        텍스트 언어 감지
        
        Args:
            text (str): 입력 텍스트
            
        Returns:
            str: 언어 코드 ('ko' 또는 'en')
        """
        try:
            return detect(text)
        except:
            return 'en'  # 기본값
    
    def _tokenize_sentences(self, text: str) -> List[str]:
        """
        문장 토큰화
        
        Args:
            text (str): 입력 텍스트
            
        Returns:
            List[str]: 토큰화된 문장 목록
        """
        sentences = sent_tokenize(text)
        return [
            s for s in sentences
            if self.min_sentence_length <= len(s) <= self.max_sentence_length
        ]
    
    def _calculate_sentence_scores(
        self,
        sentences: List[str],
        language: str
    ) -> Dict[str, float]:
        """
        문장 점수 계산
        
        Args:
            sentences (List[str]): 문장 목록
            language (str): 언어 코드
            
        Returns:
            Dict[str, float]: 문장별 점수
        """
        # 단어 토큰화 및 정규화
        words = [
            word.lower()
            for sentence in sentences
            for word in word_tokenize(self._preprocess_text(sentence))
            if word.lower() not in self.stopwords.get(language, set())
        ]
        
        # 단어 빈도 계산
        word_frequencies = FreqDist(words)
        
        # 문장 점수 계산
        sentence_scores = {}
        for sentence in sentences:
            words = word_tokenize(self._preprocess_text(sentence))
            if words:
                score = sum(
                    word_frequencies[word.lower()]
                    for word in words
                    if word.lower() not in self.stopwords.get(language, set())
                ) / len(words)
                sentence_scores[sentence] = score
        
        return sentence_scores
    
    def _extract_key_phrases(
        self,
        text: str,
        language: str,
        n: int = 10
    ) -> List[str]:
        """
        핵심 구문 추출
        
        Args:
            text (str): 입력 텍스트
            language (str): 언어 코드
            n (int): 추출할 구문 개수
            
        Returns:
            List[str]: 핵심 구문 목록
        """
        # 단어 토큰화
        words = [
            word.lower()
            for word in word_tokenize(self._preprocess_text(text))
            if word.lower() not in self.stopwords.get(language, set())
        ]
        
        # 단어 빈도 계산
        word_frequencies = FreqDist(words)
        
        # 가장 빈번한 단어 추출
        return [word for word, _ in word_frequencies.most_common(n)]
    
    def generate_summary(self, texts: List[str]) -> str:
        """
        텍스트 요약 생성
        
        Args:
            texts (List[str]): 입력 텍스트 목록
            
        Returns:
            str: 생성된 요약
        """
        try:
            # 텍스트 결합
            combined_text = ' '.join(texts)
            
            # 언어 감지
            language = self._detect_language(combined_text)
            
            # 문장 토큰화
            sentences = self._tokenize_sentences(combined_text)
            
            # 문장 점수 계산
            sentence_scores = self._calculate_sentence_scores(sentences, language)
            
            # 요약 문장 선택
            summary_length = max(1, int(len(sentences) * self.summary_ratio))
            summary_sentences = sorted(
                sentence_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )[:summary_length]
            
            # 요약 생성
            summary = ' '.join(sentence for sentence, _ in summary_sentences)
            return summary
            
        except Exception as e:
            self.logger.error(f"요약 생성 중 오류 발생: {e}")
            return ""
    
    def extract_key_points(self, texts: List[str]) -> List[str]:
        """
        핵심 포인트 추출
        
        Args:
            texts (List[str]): 입력 텍스트 목록
            
        Returns:
            List[str]: 핵심 포인트 목록
        """
        try:
            # 텍스트 결합
            combined_text = ' '.join(texts)
            
            # 언어 감지
            language = self._detect_language(combined_text)
            
            # 핵심 구문 추출
            key_phrases = self._extract_key_phrases(
                combined_text,
                language,
                self.key_points_count
            )
            
            # 핵심 포인트 생성
            key_points = []
            for phrase in key_phrases:
                # 핵심 구문이 포함된 문장 찾기
                for text in texts:
                    if phrase in text.lower():
                        # 문장 정제
                        sentence = text.strip()
                        if sentence and sentence not in key_points:
                            key_points.append(sentence)
                            break
                
                if len(key_points) >= self.key_points_count:
                    break
            
            return key_points
            
        except Exception as e:
            self.logger.error(f"핵심 포인트 추출 중 오류 발생: {e}")
            return [] 