"""
텍스트 추출 모듈 테스트
"""

import os
import pytest
import cv2
import numpy as np
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.content import TextExtractor

@pytest.fixture
def output_dir(tmp_path):
    """테스트용 출력 디렉토리 생성"""
    output_path = tmp_path / "output"
    output_path.mkdir()
    return str(output_path)

@pytest.fixture
def text_extractor(output_dir):
    """테스트용 텍스트 추출기 생성"""
    return TextExtractor(output_path=output_dir)

@pytest.fixture
def test_image():
    """테스트용 이미지 생성"""
    # 흰 배경에 텍스트가 있는 이미지 생성
    image = np.ones((480, 640, 3), dtype=np.uint8) * 255
    
    # 텍스트 영역 추가
    cv2.putText(
        image,
        "Test Text",
        (100, 240),
        cv2.FONT_HERSHEY_SIMPLEX,
        2,
        (0, 0, 0),
        2
    )
    
    return image

def test_initialization(text_extractor, output_dir):
    """초기화 테스트"""
    assert text_extractor.output_path == output_dir
    assert os.path.exists(output_dir)

def test_preprocess_image(text_extractor, test_image):
    """이미지 전처리 테스트"""
    processed = text_extractor._preprocess_image(test_image)
    
    assert isinstance(processed, np.ndarray)
    assert processed.shape == test_image.shape[:2]  # 그레이스케일
    assert processed.dtype == np.uint8

def test_extract_text_from_image(text_extractor, test_image):
    """이미지에서 텍스트 추출 테스트"""
    with patch('pytesseract.image_to_string') as mock_ocr:
        mock_ocr.return_value = "Test Text"
        
        text = text_extractor._extract_text_from_image(test_image)
        
        assert text == "Test Text"
        mock_ocr.assert_called_once()

def test_extract_text_from_images(text_extractor, test_image):
    """여러 이미지에서 텍스트 추출 테스트"""
    images = [test_image, test_image]
    
    with patch('pytesseract.image_to_string') as mock_ocr:
        mock_ocr.return_value = "Test Text"
        
        texts = text_extractor.extract_text_from_images(images)
        
        assert len(texts) == 2
        assert all(text == "Test Text" for text in texts)
        assert mock_ocr.call_count == 2

def test_extract_text_from_video(text_extractor, tmp_path):
    """동영상에서 텍스트 추출 테스트"""
    # 테스트용 동영상 생성
    video_path = tmp_path / "test.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(video_path), fourcc, 20.0, (640, 480))
    
    # 텍스트가 있는 프레임 생성
    for i in range(5):
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 255
        cv2.putText(
            frame,
            f"Frame {i}",
            (100, 240),
            cv2.FONT_HERSHEY_SIMPLEX,
            2,
            (0, 0, 0),
            2
        )
        out.write(frame)
    
    out.release()
    
    with patch('pytesseract.image_to_string') as mock_ocr:
        mock_ocr.side_effect = [f"Frame {i}" for i in range(5)]
        
        texts = text_extractor.extract_text_from_video(str(video_path))
        
        assert len(texts) == 5
        assert all(f"Frame {i}" in texts for i in range(5))
        assert mock_ocr.call_count == 5

def test_save_text(text_extractor):
    """텍스트 저장 테스트"""
    text = "Test Text"
    filename = "test_text.txt"
    
    saved_path = text_extractor._save_text(text, filename)
    assert os.path.exists(saved_path)
    assert saved_path.endswith(filename)
    
    # 저장된 텍스트 확인
    with open(saved_path, 'r', encoding='utf-8') as f:
        loaded_text = f.read()
    assert loaded_text == text

def test_invalid_image(text_extractor):
    """잘못된 이미지 테스트"""
    invalid_image = np.array([])
    with pytest.raises(Exception):
        text_extractor._extract_text_from_image(invalid_image)

def test_empty_image(text_extractor):
    """빈 이미지 테스트"""
    empty_image = np.zeros((480, 640, 3), dtype=np.uint8)
    text = text_extractor._extract_text_from_image(empty_image)
    assert text == "" 