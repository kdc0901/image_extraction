"""
이미지 추출 모듈 테스트
"""

import os
import pytest
import cv2
import numpy as np
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.content import ImageExtractor

@pytest.fixture
def output_dir(tmp_path):
    """테스트용 출력 디렉토리 생성"""
    output_path = tmp_path / "output"
    output_path.mkdir()
    return str(output_path)

@pytest.fixture
def image_extractor(output_dir):
    """테스트용 이미지 추출기 생성"""
    return ImageExtractor(
        output_path=output_dir,
        frame_interval=1,
        min_quality=0.9
    )

@pytest.fixture
def test_video(tmp_path):
    """테스트용 동영상 파일 생성"""
    video_path = tmp_path / "test.mp4"
    
    # 간단한 동영상 생성
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(video_path), fourcc, 20.0, (640, 480))
    
    for _ in range(10):  # 10프레임 생성
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        out.write(frame)
    
    out.release()
    return str(video_path)

def test_initialization(image_extractor, output_dir):
    """초기화 테스트"""
    assert image_extractor.output_path == output_dir
    assert image_extractor.frame_interval == 1
    assert image_extractor.min_quality == 0.9
    assert os.path.exists(output_dir)

def test_extract_frames(image_extractor, test_video):
    """프레임 추출 테스트"""
    frames = image_extractor.extract_frames(test_video)
    assert len(frames) > 0
    assert all(isinstance(frame, np.ndarray) for frame in frames)
    assert all(frame.shape == (480, 640, 3) for frame in frames)

def test_extract_slides(image_extractor, test_video):
    """슬라이드 추출 테스트"""
    slides = image_extractor.extract_slides(test_video)
    assert len(slides) > 0
    assert all(isinstance(slide, np.ndarray) for slide in slides)
    assert all(slide.shape == (480, 640, 3) for slide in slides)

def test_calculate_image_quality(image_extractor):
    """이미지 품질 계산 테스트"""
    # 고품질 이미지 생성
    high_quality = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    high_quality[100:200, 100:200] = 255  # 고대비 영역 추가
    
    # 저품질 이미지 생성
    low_quality = np.random.randint(100, 150, (480, 640, 3), dtype=np.uint8)
    
    high_score = image_extractor._calculate_image_quality(high_quality)
    low_score = image_extractor._calculate_image_quality(low_quality)
    
    assert high_score > low_score
    assert 0 <= high_score <= 1
    assert 0 <= low_score <= 1

def test_save_image(image_extractor):
    """이미지 저장 테스트"""
    image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    filename = "test_image.jpg"
    
    saved_path = image_extractor._save_image(image, filename)
    assert os.path.exists(saved_path)
    assert saved_path.endswith(filename)
    
    # 저장된 이미지 확인
    loaded_image = cv2.imread(saved_path)
    assert loaded_image.shape == image.shape

def test_invalid_video(image_extractor, tmp_path):
    """잘못된 동영상 파일 테스트"""
    invalid_path = str(tmp_path / "invalid.mp4")
    with pytest.raises(Exception):
        image_extractor.extract_frames(invalid_path)

def test_empty_video(image_extractor, tmp_path):
    """빈 동영상 파일 테스트"""
    empty_path = str(tmp_path / "empty.mp4")
    with open(empty_path, 'w') as f:
        f.write("")
    
    with pytest.raises(Exception):
        image_extractor.extract_frames(empty_path) 