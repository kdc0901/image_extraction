"""
시스템 테스트 스크립트
"""

import os
import cv2
import numpy as np
import logging
from pathlib import Path
import time
from src import YouTubeProcessor

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def download_test_video(output_path: str) -> str:
    """
    테스트용 동영상 다운로드
    
    Args:
        output_path: 저장 경로
        
    Returns:
        다운로드된 동영상 경로
    """
    try:
        import yt_dlp
        
        # YouTube 동영상 URL
        video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # 테스트용 동영상
        
        # 다운로드 옵션
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'quiet': True
        }
        
        # 다운로드
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            video_path = ydl.prepare_filename(info)
            
        logger.info(f"동영상 다운로드 완료: {video_path}")
        return video_path
        
    except Exception as e:
        logger.error(f"동영상 다운로드 중 오류 발생: {e}")
        raise

def test_system():
    """시스템 테스트 실행"""
    try:
        # 테스트 디렉토리 생성
        test_dir = Path("test_output")
        test_dir.mkdir(exist_ok=True)
        
        # 설정 파일 생성
        config_path = test_dir / "test_config.yaml"
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
        
        # 테스트 동영상 다운로드
        video_path = download_test_video(str(test_dir))
        
        # 프로세서 초기화
        processor = YouTubeProcessor(str(config_path))
        
        # 처리 시간 측정
        start_time = time.time()
        
        # 동영상 처리
        result = processor.process_video(video_path)
        
        # 처리 시간 계산
        processing_time = time.time() - start_time
        
        # 결과 검증
        if result:
            logger.info(f"처리 성공: {video_path}")
            logger.info(f"처리 시간: {processing_time:.2f}초")
            
            # 출력 파일 확인
            output_dir = Path(processor.output_dir)
            images_dir = output_dir / "images"
            texts_dir = output_dir / "texts"
            documents_dir = output_dir / "documents"
            
            # 디렉토리 존재 확인
            assert images_dir.exists(), "이미지 디렉토리가 생성되지 않음"
            assert texts_dir.exists(), "텍스트 디렉토리가 생성되지 않음"
            assert documents_dir.exists(), "문서 디렉토리가 생성되지 않음"
            
            # 파일 수 확인
            image_files = list(images_dir.glob("*.jpg"))
            text_files = list(texts_dir.glob("*.txt"))
            document_files = list(documents_dir.glob("*.docx"))
            
            logger.info(f"추출된 이미지 수: {len(image_files)}")
            logger.info(f"추출된 텍스트 수: {len(text_files)}")
            logger.info(f"생성된 문서 수: {len(document_files)}")
            
            # 성능 메트릭 출력
            logger.info("\n성능 메트릭:")
            logger.info(f"이미지 처리 속도: {len(image_files)/processing_time:.2f} 이미지/초")
            logger.info(f"텍스트 처리 속도: {len(text_files)/processing_time:.2f} 텍스트/초")
            
        else:
            logger.error("처리 실패")
            
    except Exception as e:
        logger.error(f"시스템 테스트 중 오류 발생: {e}")
        raise

if __name__ == "__main__":
    test_system() 