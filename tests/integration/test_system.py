"""
시스템 통합 테스트 모듈
"""

import os
import pytest
import cv2
import numpy as np
from pathlib import Path
from unittest.mock import MagicMock, patch

from src import YouTubeProcessor

@pytest.fixture
def test_config(tmp_path):
    """테스트용 설정 파일 생성"""
    config_path = tmp_path / "test_config.yaml"
    config_content = """
logging:
  level: DEBUG
  file: test.log

output:
  directory: test_output

extraction:
  frame_interval: 1
  slide_threshold: 0.9

processing:
  similarity_threshold: 0.9
  cache_size: 100

document:
  title: "테스트 문서"
  image_width: 5.0
  font_size: 10
  line_spacing: 1.2
"""
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(config_content)
    return str(config_path)

@pytest.fixture
def test_video(tmp_path):
    """테스트용 동영상 파일 생성"""
    video_path = tmp_path / "test.mp4"
    
    # 간단한 동영상 생성
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(video_path), fourcc, 20.0, (640, 480))
    
    # 텍스트가 있는 프레임 생성
    for i in range(10):
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
    return str(video_path)

def test_full_pipeline(test_config, test_video):
    """전체 처리 파이프라인 테스트"""
    # 프로세서 초기화
    processor = YouTubeProcessor(test_config)
    
    # 모듈 메서드 모킹
    with patch('src.content.ImageExtractor.extract_frames') as mock_extract_frames, \
         patch('src.processing.Deduplicator.deduplicate_images') as mock_deduplicate_images, \
         patch('src.content.TextExtractor.extract_text_from_image') as mock_extract_text, \
         patch('src.processing.Deduplicator.deduplicate_texts') as mock_deduplicate_texts, \
         patch('src.document.DocumentConverter.create_document') as mock_create_document:
        
        # 모킹된 메서드 설정
        mock_extract_frames.return_value = ["frame1", "frame2"]
        mock_deduplicate_images.return_value = ["frame1"]
        mock_extract_text.return_value = "test text"
        mock_deduplicate_texts.return_value = ["test text"]
        mock_create_document.return_value = "test.docx"
        
        # 동영상 처리 실행
        result = processor.process_video(test_video)
        
        # 결과 검증
        assert result is True
        mock_extract_frames.assert_called_once_with(test_video)
        mock_deduplicate_images.assert_called_once_with(["frame1", "frame2"])
        assert mock_extract_text.call_count == 1
        mock_deduplicate_texts.assert_called_once_with(["test text"])
        mock_create_document.assert_called_once()

def test_multiple_videos(test_config, test_video, tmp_path):
    """여러 동영상 처리 테스트"""
    # 두 번째 동영상 생성
    video2_path = str(tmp_path / "test2.mp4")
    os.symlink(test_video, video2_path)
    
    # 프로세서 초기화
    processor = YouTubeProcessor(test_config)
    
    # 모듈 메서드 모킹
    with patch('src.YouTubeProcessor.process_video') as mock_process_video:
        mock_process_video.return_value = True
        
        # 여러 동영상 처리 실행
        processor.process_videos([test_video, video2_path])
        
        # 결과 검증
        assert mock_process_video.call_count == 2
        mock_process_video.assert_any_call(test_video)
        mock_process_video.assert_any_call(video2_path)

def test_output_structure(test_config, test_video):
    """출력 디렉토리 구조 테스트"""
    # 프로세서 초기화
    processor = YouTubeProcessor(test_config)
    
    # 모듈 메서드 모킹
    with patch('src.content.ImageExtractor.extract_frames'), \
         patch('src.processing.Deduplicator.deduplicate_images'), \
         patch('src.content.TextExtractor.extract_text_from_image'), \
         patch('src.processing.Deduplicator.deduplicate_texts'), \
         patch('src.document.DocumentConverter.create_document'):
        
        # 동영상 처리 실행
        processor.process_video(test_video)
        
        # 출력 디렉토리 구조 검증
        output_dir = Path(processor.output_dir)
        assert output_dir.exists()
        assert (output_dir / 'images').exists()
        assert (output_dir / 'texts').exists()
        assert (output_dir / 'documents').exists()

def test_error_handling(test_config, test_video):
    """에러 처리 테스트"""
    # 프로세서 초기화
    processor = YouTubeProcessor(test_config)
    
    # 모듈 메서드 모킹 - 에러 발생
    with patch('src.content.ImageExtractor.extract_frames') as mock_extract_frames:
        mock_extract_frames.side_effect = Exception("Test error")
        
        # 동영상 처리 실행
        result = processor.process_video(test_video)
        
        # 결과 검증
        assert result is False

def test_config_loading(test_config):
    """설정 파일 로딩 테스트"""
    # 프로세서 초기화
    processor = YouTubeProcessor(test_config)
    
    # 설정 값 검증
    assert processor.config.get('logging', 'level') == 'DEBUG'
    assert processor.config.get('extraction', 'frame_interval') == 1
    assert processor.config.get('processing', 'similarity_threshold') == 0.9
    assert processor.config.get('document', 'title') == '테스트 문서'

def test_resource_cleanup(test_config, test_video):
    """리소스 정리 테스트"""
    # 프로세서 초기화
    processor = YouTubeProcessor(test_config)
    
    # 모듈 메서드 모킹
    with patch('src.content.ImageExtractor.extract_frames'), \
         patch('src.processing.Deduplicator.deduplicate_images'), \
         patch('src.content.TextExtractor.extract_text_from_image'), \
         patch('src.processing.Deduplicator.deduplicate_texts'), \
         patch('src.document.DocumentConverter.create_document'):
        
        # 동영상 처리 실행
        processor.process_video(test_video)
        
        # 임시 파일 정리 확인
        output_dir = Path(processor.output_dir)
        temp_files = list(output_dir.glob('**/*.tmp'))
        assert len(temp_files) == 0 