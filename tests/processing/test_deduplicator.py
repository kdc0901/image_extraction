"""
중복 제거 모듈 테스트
"""

import pytest
import cv2
import numpy as np
from unittest.mock import MagicMock, patch

from src.processing import Deduplicator

@pytest.fixture
def deduplicator():
    """테스트용 중복 제거기 생성"""
    return Deduplicator(
        similarity_threshold=0.9,
        cache_size=1000
    )

@pytest.fixture
def test_images():
    """테스트용 이미지 생성"""
    # 기본 이미지
    base_image = np.ones((480, 640, 3), dtype=np.uint8) * 255
    
    # 약간 수정된 이미지 (중복)
    similar_image = base_image.copy()
    similar_image[100:200, 100:200] = 200
    
    # 완전히 다른 이미지
    different_image = np.zeros((480, 640, 3), dtype=np.uint8)
    
    return [base_image, similar_image, different_image]

@pytest.fixture
def test_texts():
    """테스트용 텍스트 생성"""
    base_text = "This is a test text."
    similar_text = "This is a test text!"
    different_text = "Completely different content."
    
    return [base_text, similar_text, different_text]

def test_initialization(deduplicator):
    """초기화 테스트"""
    assert deduplicator.similarity_threshold == 0.9
    assert deduplicator.cache_size == 1000
    assert len(deduplicator.image_cache) == 0
    assert len(deduplicator.text_cache) == 0

def test_calculate_image_hash(deduplicator, test_images):
    """이미지 해시 계산 테스트"""
    base_hash = deduplicator._calculate_image_hash(test_images[0])
    similar_hash = deduplicator._calculate_image_hash(test_images[1])
    different_hash = deduplicator._calculate_image_hash(test_images[2])
    
    assert base_hash == similar_hash  # 약간의 차이는 해시에 영향을 주지 않음
    assert base_hash != different_hash

def test_calculate_perceptual_hash(deduplicator, test_images):
    """퍼셉추얼 해시 계산 테스트"""
    base_hash = deduplicator._calculate_perceptual_hash(test_images[0])
    similar_hash = deduplicator._calculate_perceptual_hash(test_images[1])
    different_hash = deduplicator._calculate_perceptual_hash(test_images[2])
    
    assert base_hash == similar_hash  # 약간의 차이는 해시에 영향을 주지 않음
    assert base_hash != different_hash

def test_calculate_text_similarity(deduplicator, test_texts):
    """텍스트 유사도 계산 테스트"""
    similarity = deduplicator._calculate_text_similarity(test_texts[0], test_texts[1])
    assert 0.9 <= similarity <= 1.0  # 매우 유사한 텍스트
    
    similarity = deduplicator._calculate_text_similarity(test_texts[0], test_texts[2])
    assert similarity < 0.5  # 다른 텍스트

def test_calculate_image_similarity(deduplicator, test_images):
    """이미지 유사도 계산 테스트"""
    similarity = deduplicator._calculate_image_similarity(test_images[0], test_images[1])
    assert 0.9 <= similarity <= 1.0  # 매우 유사한 이미지
    
    similarity = deduplicator._calculate_image_similarity(test_images[0], test_images[2])
    assert similarity < 0.5  # 다른 이미지

def test_is_duplicate_image(deduplicator, test_images):
    """이미지 중복 검사 테스트"""
    assert not deduplicator.is_duplicate_image(test_images[0])  # 첫 번째 이미지는 중복 아님
    assert deduplicator.is_duplicate_image(test_images[1])  # 유사한 이미지는 중복
    assert not deduplicator.is_duplicate_image(test_images[2])  # 다른 이미지는 중복 아님

def test_is_duplicate_text(deduplicator, test_texts):
    """텍스트 중복 검사 테스트"""
    assert not deduplicator.is_duplicate_text(test_texts[0])  # 첫 번째 텍스트는 중복 아님
    assert deduplicator.is_duplicate_text(test_texts[1])  # 유사한 텍스트는 중복
    assert not deduplicator.is_duplicate_text(test_texts[2])  # 다른 텍스트는 중복 아님

def test_deduplicate_images(deduplicator, test_images):
    """이미지 중복 제거 테스트"""
    unique_images = deduplicator.deduplicate_images(test_images)
    assert len(unique_images) == 2  # 중복 제거 후 2개의 이미지만 남음
    assert test_images[0] in unique_images
    assert test_images[2] in unique_images

def test_deduplicate_texts(deduplicator, test_texts):
    """텍스트 중복 제거 테스트"""
    unique_texts = deduplicator.deduplicate_texts(test_texts)
    assert len(unique_texts) == 2  # 중복 제거 후 2개의 텍스트만 남음
    assert test_texts[0] in unique_texts
    assert test_texts[2] in unique_texts

def test_cache_management(deduplicator, test_images, test_texts):
    """캐시 관리 테스트"""
    # 캐시 크기 초과 테스트
    for i in range(1001):
        deduplicator.is_duplicate_image(test_images[0])
        deduplicator.is_duplicate_text(test_texts[0])
    
    assert len(deduplicator.image_cache) <= deduplicator.cache_size
    assert len(deduplicator.text_cache) <= deduplicator.cache_size 