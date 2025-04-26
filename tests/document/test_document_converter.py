"""
문서 변환 모듈 테스트
"""

import os
import pytest
import cv2
import numpy as np
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.document import DocumentConverter

@pytest.fixture
def output_dir(tmp_path):
    """테스트용 출력 디렉토리 생성"""
    output_path = tmp_path / "output"
    output_path.mkdir()
    return str(output_path)

@pytest.fixture
def document_converter(output_dir):
    """테스트용 문서 변환기 생성"""
    return DocumentConverter(
        output_path=output_dir,
        title="Test Document",
        image_width=5.0,
        font_size=11,
        line_spacing=1.5
    )

@pytest.fixture
def test_images():
    """테스트용 이미지 생성"""
    images = []
    for i in range(3):
        image = np.ones((480, 640, 3), dtype=np.uint8) * 255
        cv2.putText(
            image,
            f"Image {i}",
            (100, 240),
            cv2.FONT_HERSHEY_SIMPLEX,
            2,
            (0, 0, 0),
            2
        )
        images.append(image)
    return images

@pytest.fixture
def test_texts():
    """테스트용 텍스트 생성"""
    return [
        "First paragraph of text.",
        "Second paragraph with more content.",
        "Third paragraph with different information."
    ]

def test_initialization(document_converter, output_dir):
    """초기화 테스트"""
    assert document_converter.output_path == output_dir
    assert document_converter.title == "Test Document"
    assert document_converter.image_width == 5.0
    assert document_converter.font_size == 11
    assert document_converter.line_spacing == 1.5
    assert os.path.exists(output_dir)

def test_create_document(document_converter, test_images, test_texts):
    """문서 생성 테스트"""
    with patch('docx.Document') as mock_doc:
        # 문서 객체 모킹
        mock_doc_instance = MagicMock()
        mock_doc.return_value = mock_doc_instance
        
        # 문서 생성
        doc_path = document_converter.create_document(
            output_name="test_document",
            images=test_images,
            texts=test_texts
        )
        
        # 결과 검증
        assert doc_path.endswith("test_document.docx")
        assert os.path.exists(doc_path)
        
        # 문서 객체 메서드 호출 검증
        mock_doc.assert_called_once()
        assert mock_doc_instance.add_heading.call_count == 1
        assert mock_doc_instance.add_paragraph.call_count == len(test_texts)
        assert mock_doc_instance.add_picture.call_count == len(test_images)
        mock_doc_instance.save.assert_called_once()

def test_add_image(document_converter, test_images):
    """이미지 추가 테스트"""
    with patch('docx.Document') as mock_doc:
        mock_doc_instance = MagicMock()
        mock_doc.return_value = mock_doc_instance
        
        # 이미지 추가
        document_converter._add_image(mock_doc_instance, test_images[0])
        
        # 결과 검증
        mock_doc_instance.add_picture.assert_called_once()
        args = mock_doc_instance.add_picture.call_args[0]
        assert args[0].endswith('.jpg')  # 임시 이미지 파일
        assert os.path.exists(args[0])

def test_add_text(document_converter, test_texts):
    """텍스트 추가 테스트"""
    with patch('docx.Document') as mock_doc:
        mock_doc_instance = MagicMock()
        mock_doc.return_value = mock_doc_instance
        
        # 텍스트 추가
        document_converter._add_text(mock_doc_instance, test_texts[0])
        
        # 결과 검증
        mock_doc_instance.add_paragraph.assert_called_once_with(test_texts[0])

def test_save_image(document_converter, test_images):
    """이미지 저장 테스트"""
    # 이미지 저장
    saved_path = document_converter._save_image(test_images[0])
    
    # 결과 검증
    assert os.path.exists(saved_path)
    assert saved_path.endswith('.jpg')
    
    # 저장된 이미지 확인
    loaded_image = cv2.imread(saved_path)
    assert loaded_image.shape == test_images[0].shape

def test_invalid_image(document_converter):
    """잘못된 이미지 테스트"""
    invalid_image = np.array([])
    with pytest.raises(Exception):
        document_converter._save_image(invalid_image)

def test_empty_text(document_converter):
    """빈 텍스트 테스트"""
    with patch('docx.Document') as mock_doc:
        mock_doc_instance = MagicMock()
        mock_doc.return_value = mock_doc_instance
        
        # 빈 텍스트 추가
        document_converter._add_text(mock_doc_instance, "")
        
        # 결과 검증
        mock_doc_instance.add_paragraph.assert_called_once_with("")

def test_document_save_error(document_converter, test_images, test_texts):
    """문서 저장 오류 테스트"""
    with patch('docx.Document') as mock_doc:
        mock_doc_instance = MagicMock()
        mock_doc.return_value = mock_doc_instance
        mock_doc_instance.save.side_effect = Exception("Save error")
        
        # 문서 생성 시도
        with pytest.raises(Exception):
            document_converter.create_document(
                output_name="test_document",
                images=test_images,
                texts=test_texts
            ) 