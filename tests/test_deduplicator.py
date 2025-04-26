import os
import pytest
import numpy as np
import cv2
from pathlib import Path
from src.processing.deduplicator import Deduplicator

class TestDeduplicator:
    """Deduplicator 클래스 테스트"""
    
    @pytest.fixture
    def deduplicator(self):
        """Deduplicator 인스턴스 생성"""
        return Deduplicator(
            similarity_threshold=0.95,
            method='content_hash',
            cache_size=1000
        )
    
    @pytest.fixture
    def sample_images(self, tmp_path):
        """테스트용 샘플 이미지 생성"""
        images = []
        
        # 원본 이미지 생성
        img1 = np.zeros((100, 100, 3), dtype=np.uint8)
        img1[25:75, 25:75] = 255
        path1 = tmp_path / "image1.png"
        cv2.imwrite(str(path1), img1)
        images.append(str(path1))
        
        # 약간 수정된 이미지 생성
        img2 = img1.copy()
        img2[30:70, 30:70] = 255
        path2 = tmp_path / "image2.png"
        cv2.imwrite(str(path2), img2)
        images.append(str(path2))
        
        # 완전히 다른 이미지 생성
        img3 = np.zeros((100, 100, 3), dtype=np.uint8)
        img3[50:100, 0:50] = 255
        path3 = tmp_path / "image3.png"
        cv2.imwrite(str(path3), img3)
        images.append(str(path3))
        
        return images
    
    @pytest.fixture
    def sample_texts(self):
        """테스트용 샘플 텍스트"""
        return [
            "인공지능은 중요한 기술이다.",
            "인공지능은 매우 중요한 기술이다.",
            "머신러닝은 인공지능의 한 분야이다.",
            "딥러닝은 머신러닝의 한 분야이다."
        ]
    
    def test_calculate_image_hash(self, deduplicator, sample_images):
        """이미지 해시 계산 테스트"""
        # 이미지 로드
        img1 = cv2.imread(sample_images[0])
        img2 = cv2.imread(sample_images[1])
        img3 = cv2.imread(sample_images[2])
        
        # 해시 계산
        hash1 = deduplicator._calculate_image_hash(img1)
        hash2 = deduplicator._calculate_image_hash(img2)
        hash3 = deduplicator._calculate_image_hash(img3)
        
        # 유사한 이미지의 해시는 유사해야 함
        assert hash1 == hash2
        # 다른 이미지의 해시는 다르야 함
        assert hash1 != hash3
    
    def test_calculate_perceptual_hash(self, deduplicator, sample_images):
        """지각 해시 계산 테스트"""
        # 이미지 로드
        img1 = cv2.imread(sample_images[0])
        img2 = cv2.imread(sample_images[1])
        img3 = cv2.imread(sample_images[2])
        
        # 해시 계산
        hash1 = deduplicator._calculate_perceptual_hash(img1)
        hash2 = deduplicator._calculate_perceptual_hash(img2)
        hash3 = deduplicator._calculate_perceptual_hash(img3)
        
        # 유사한 이미지의 해시는 유사해야 함
        assert hash1 == hash2
        # 다른 이미지의 해시는 다르야 함
        assert hash1 != hash3
    
    def test_calculate_text_similarity(self, deduplicator, sample_texts):
        """텍스트 유사도 계산 테스트"""
        # 유사한 텍스트
        similarity1 = deduplicator._calculate_text_similarity(
            sample_texts[0],
            sample_texts[1]
        )
        assert similarity1 > 0.8
        
        # 다른 텍스트
        similarity2 = deduplicator._calculate_text_similarity(
            sample_texts[0],
            sample_texts[2]
        )
        assert similarity2 < 0.5
    
    def test_calculate_image_similarity(self, deduplicator, sample_images):
        """이미지 유사도 계산 테스트"""
        # 이미지 로드
        img1 = cv2.imread(sample_images[0])
        img2 = cv2.imread(sample_images[1])
        img3 = cv2.imread(sample_images[2])
        
        # 유사도 계산
        similarity1 = deduplicator._calculate_image_similarity(img1, img2)
        similarity2 = deduplicator._calculate_image_similarity(img1, img3)
        
        # 유사한 이미지의 유사도는 높아야 함
        assert similarity1 > 0.9
        # 다른 이미지의 유사도는 낮아야 함
        assert similarity2 < 0.5
    
    def test_is_duplicate_image(self, deduplicator, sample_images):
        """이미지 중복 여부 확인 테스트"""
        # 유사한 이미지
        is_duplicate1, _ = deduplicator.is_duplicate_image(
            sample_images[0],
            [sample_images[1]]
        )
        assert is_duplicate1
        
        # 다른 이미지
        is_duplicate2, _ = deduplicator.is_duplicate_image(
            sample_images[0],
            [sample_images[2]]
        )
        assert not is_duplicate2
    
    def test_is_duplicate_text(self, deduplicator, sample_texts):
        """텍스트 중복 여부 확인 테스트"""
        # 유사한 텍스트
        is_duplicate1, _ = deduplicator.is_duplicate_text(
            sample_texts[0],
            [sample_texts[1]]
        )
        assert is_duplicate1
        
        # 다른 텍스트
        is_duplicate2, _ = deduplicator.is_duplicate_text(
            sample_texts[0],
            [sample_texts[2]]
        )
        assert not is_duplicate2
    
    def test_deduplicate_images(self, deduplicator, sample_images):
        """이미지 중복 제거 테스트"""
        unique_images, duplicates = deduplicator.deduplicate_images(sample_images)
        
        # 고유 이미지 수 확인
        assert len(unique_images) == 2
        # 중복 이미지 수 확인
        assert len(duplicates) == 1
    
    def test_deduplicate_texts(self, deduplicator, sample_texts):
        """텍스트 중복 제거 테스트"""
        unique_texts, duplicates = deduplicator.deduplicate_texts(sample_texts)
        
        # 고유 텍스트 수 확인
        assert len(unique_texts) == 3
        # 중복 텍스트 수 확인
        assert len(duplicates) == 1
    
    def test_error_handling(self, deduplicator):
        """오류 처리 테스트"""
        # 존재하지 않는 이미지 파일
        is_duplicate, _ = deduplicator.is_duplicate_image(
            "nonexistent.jpg",
            ["test.jpg"]
        )
        assert not is_duplicate
        
        # 빈 텍스트
        is_duplicate, _ = deduplicator.is_duplicate_text("", ["test"])
        assert not is_duplicate 