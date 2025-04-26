"""
메인 애플리케이션 테스트 모듈
"""

import os
import pytest
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
def processor(test_config):
    """테스트용 프로세서 생성"""
    return YouTubeProcessor(test_config)

def test_processor_initialization(processor, test_config):
    """프로세서 초기화 테스트"""
    assert processor.config.config_path == test_config
    assert processor.output_dir.name == "test_output"
    assert processor.image_extractor.frame_interval == 1
    assert processor.deduplicator.similarity_threshold == 0.9

def test_process_video_success(processor, tmp_path):
    """동영상 처리 성공 테스트"""
    # 테스트용 동영상 파일 생성
    video_path = tmp_path / "test_video.mp4"
    video_path.touch()
    
    # 모듈 메서드 모킹
    processor.image_extractor.extract_frames = MagicMock(return_value=["image1", "image2"])
    processor.deduplicator.deduplicate_images = MagicMock(return_value=["image1"])
    processor.text_extractor.extract_text_from_image = MagicMock(return_value="test text")
    processor.deduplicator.deduplicate_texts = MagicMock(return_value=["test text"])
    processor.document_converter.create_document = MagicMock(return_value="test.docx")
    
    # 동영상 처리 실행
    result = processor.process_video(str(video_path))
    
    # 결과 검증
    assert result is True
    processor.image_extractor.extract_frames.assert_called_once()
    processor.deduplicator.deduplicate_images.assert_called_once()
    processor.text_extractor.extract_text_from_image.assert_called()
    processor.deduplicator.deduplicate_texts.assert_called_once()
    processor.document_converter.create_document.assert_called_once()

def test_process_video_failure(processor, tmp_path):
    """동영상 처리 실패 테스트"""
    # 존재하지 않는 동영상 파일
    video_path = tmp_path / "nonexistent.mp4"
    
    # 동영상 처리 실행
    result = processor.process_video(str(video_path))
    
    # 결과 검증
    assert result is False

def test_process_videos(processor, tmp_path):
    """여러 동영상 처리 테스트"""
    # 테스트용 동영상 파일 생성
    video_paths = [
        tmp_path / "video1.mp4",
        tmp_path / "video2.mp4"
    ]
    for path in video_paths:
        path.touch()
    
    # process_video 메서드 모킹
    with patch.object(processor, 'process_video') as mock_process:
        mock_process.return_value = True
        
        # 여러 동영상 처리 실행
        processor.process_videos([str(p) for p in video_paths])
        
        # 결과 검증
        assert mock_process.call_count == 2
        mock_process.assert_any_call(str(video_paths[0]))
        mock_process.assert_any_call(str(video_paths[1]))

def test_output_directory_creation(processor):
    """출력 디렉토리 생성 테스트"""
    assert processor.output_dir.exists()
    assert (processor.output_dir / 'images').exists()
    assert (processor.output_dir / 'texts').exists()
    assert (processor.output_dir / 'documents').exists() 