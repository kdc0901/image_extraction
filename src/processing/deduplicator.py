"""
Deduplication module for images and text.
"""

import os
import cv2
import numpy as np
from typing import List, Dict, Set, Tuple, Optional
import logging
from tqdm import tqdm
from PIL import Image
import hashlib
from difflib import SequenceMatcher
from skimage.metrics import structural_similarity as ssim
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import OrderedDict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class Deduplicator:
    """중복 제거 클래스"""
    
    def __init__(self, similarity_threshold: float = 0.9, cache_size: int = 1000):
        """
        중복 제거기 초기화
        
        Args:
            similarity_threshold: 유사도 임계값 (0-1)
            cache_size: 최대 캐시 크기
        """
        self.similarity_threshold = similarity_threshold
        self.cache_size = cache_size
        
        # 이미지 캐시 (OrderedDict 사용)
        self.image_cache = OrderedDict()
        
        # 텍스트 캐시 (OrderedDict 사용)
        self.text_cache = OrderedDict()
        
        # 스레드 풀 생성
        self.thread_pool = ThreadPoolExecutor(max_workers=os.cpu_count())
        
        # TF-IDF 벡터라이저 초기화
        self.vectorizer = TfidfVectorizer(
            strip_accents='unicode',
            stop_words='english'
        )
    
    def _normalize_image(self, image: np.ndarray) -> np.ndarray:
        """
        이미지 정규화 함수
        
        Args:
            image (np.ndarray): 입력 이미지
            
        Returns:
            np.ndarray: 정규화된 이미지
        """
        # 그레이스케일 변환
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
        # 크기 조정
        image = cv2.resize(image, (800, 600))
        
        return image
    
    def calculate_image_hash(self, image: np.ndarray) -> str:
        """
        이미지 해시 계산
        
        Args:
            image: OpenCV 이미지
            
        Returns:
            이미지 해시 문자열
        """
        # 이미지 크기 조정
        resized = cv2.resize(image, (8, 8))
        
        # 그레이스케일 변환
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        
        # 평균값 계산
        avg = gray.mean()
        
        # 해시 계산
        diff = gray > avg
        return ''.join(['1' if d else '0' for d in diff.flatten()])

    def calculate_perceptual_hash(self, image: np.ndarray) -> str:
        """
        지각 해시 계산
        
        Args:
            image: OpenCV 이미지
            
        Returns:
            지각 해시 문자열
        """
        # 이미지 크기 조정
        resized = cv2.resize(image, (32, 32))
        
        # 그레이스케일 변환
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        
        # DCT 변환
        dct = cv2.dct(np.float32(gray))
        dct_low = dct[:8, :8]
        
        # 평균값 계산
        avg = dct_low.mean()
        
        # 해시 계산
        diff = dct_low > avg
        return ''.join(['1' if d else '0' for d in diff.flatten()])

    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        텍스트 유사도 계산
        
        Args:
            text1: 첫 번째 텍스트
            text2: 두 번째 텍스트
            
        Returns:
            코사인 유사도
        """
        try:
            # 벡터화
            vectors = self.vectorizer.fit_transform([text1, text2])
            
            # 유사도 계산
            similarity = cosine_similarity(vectors)[0, 1]
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"텍스트 유사도 계산 중 오류 발생: {e}")
            return 0.0

    def calculate_image_similarity(self, hash1: str, hash2: str) -> float:
        """
        이미지 해시 유사도 계산
        
        Args:
            hash1: 첫 번째 해시
            hash2: 두 번째 해시
            
        Returns:
            해밍 거리 기반 유사도
        """
        if len(hash1) != len(hash2):
            return 0.0
            
        # 해밍 거리 계산
        hamming_distance = sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
        
        # 유사도 계산
        similarity = 1.0 - (hamming_distance / len(hash1))
        
        return similarity

    def _process_image(self, image: np.ndarray, image_hash: str) -> bool:
        """이미지 중복 검사"""
        # 캐시에서 유사한 이미지 검색
        for cached_hash, cached_image in self.image_cache.items():
            similarity = self.calculate_image_similarity(image_hash, cached_hash)
            if similarity >= self.similarity_threshold:
                return True
        
        # 캐시에 추가
        if len(self.image_cache) >= self.cache_size:
            self.image_cache.popitem(last=False)
        self.image_cache[image_hash] = image
        
        return False

    def is_duplicate_image(self, image: np.ndarray) -> bool:
        """
        이미지 중복 검사
        
        Args:
            image: 검사할 이미지
            
        Returns:
            중복 여부
        """
        try:
            # 해시 계산
            image_hash = self.calculate_image_hash(image)
            perceptual_hash = self.calculate_perceptual_hash(image)
            
            # 중복 검사
            return self._process_image(image, image_hash)
            
        except Exception as e:
            logger.error(f"이미지 중복 검사 중 오류 발생: {e}")
            return False

    def _process_text(self, text: str, text_hash: str) -> bool:
        """텍스트 중복 검사"""
        # 캐시에서 유사한 텍스트 검색
        for cached_hash, cached_text in self.text_cache.items():
            similarity = self.calculate_text_similarity(text, cached_text)
            if similarity >= self.similarity_threshold:
                return True
        
        # 캐시에 추가
        if len(self.text_cache) >= self.cache_size:
            self.text_cache.popitem(last=False)
        self.text_cache[text_hash] = text
        
        return False

    def is_duplicate_text(self, text: str) -> bool:
        """
        텍스트 중복 검사
        
        Args:
            text: 검사할 텍스트
            
        Returns:
            중복 여부
        """
        try:
            # 텍스트 해시 계산
            text_hash = hash(text)
            
            # 중복 검사
            return self._process_text(text, str(text_hash))
            
        except Exception as e:
            logger.error(f"텍스트 중복 검사 중 오류 발생: {e}")
            return False

    def deduplicate_images(self, images: List[np.ndarray]) -> List[np.ndarray]:
        """
        이미지 중복 제거
        
        Args:
            images: 중복 제거할 이미지 리스트
            
        Returns:
            중복 제거된 이미지 리스트
        """
        try:
            unique_images = []
            futures = []
            
            # 병렬 처리
            for image in images:
                future = self.thread_pool.submit(self.is_duplicate_image, image)
                futures.append((image, future))
            
            # 결과 수집
            for image, future in futures:
                if not future.result():
                    unique_images.append(image)
            
            return unique_images
            
        except Exception as e:
            logger.error(f"이미지 중복 제거 중 오류 발생: {e}")
            return images

    def deduplicate_texts(self, texts: List[str]) -> List[str]:
        """
        텍스트 중복 제거
        
        Args:
            texts: 중복 제거할 텍스트 리스트
            
        Returns:
            중복 제거된 텍스트 리스트
        """
        try:
            unique_texts = []
            futures = []
            
            # 병렬 처리
            for text in texts:
                future = self.thread_pool.submit(self.is_duplicate_text, text)
                futures.append((text, future))
            
            # 결과 수집
            for text, future in futures:
                if not future.result():
                    unique_texts.append(text)
            
            return unique_texts
            
        except Exception as e:
            logger.error(f"텍스트 중복 제거 중 오류 발생: {e}")
            return texts

    def __del__(self):
        """리소스 정리"""
        self.thread_pool.shutdown()
        self.image_cache.clear()
        self.text_cache.clear() 