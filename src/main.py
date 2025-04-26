"""
YouTube 동영상 처리 시스템 메인 모듈
"""

import os
import cv2
import numpy as np
import logging
from pathlib import Path
import time
from typing import List, Optional, Callable
from tqdm import tqdm
import yt_dlp
import shutil

from utils import Config, setup_logger
from content import ImageExtractor, TextExtractor
from processing import Deduplicator
from document import DocumentConverter

class YouTubeProcessor:
    """YouTube 동영상 처리 클래스"""
    
    def __init__(self, config_path: str = 'youtube_config.yaml'):
        """
        초기화
        
        Args:
            config_path: 설정 파일 경로
        """
        # 설정 로드
        self.config = Config(config_path)
        
        # 로깅 설정
        log_level = self.config.get('logging', 'level', 'INFO')
        log_file = self.config.get('logging', 'file')
        self.logger = setup_logger(__name__, log_level, log_file)
        
        # 출력 디렉토리 설정
        self.output_dir = Path(self.config.get('output', 'directory', '.'))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 다운로드 디렉토리 설정
        self.download_dir = self.output_dir / 'downmovie'
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # 이미지 추출기 초기화
        self.image_extractor = ImageExtractor(
            output_dir=str(self.output_dir / 'images'),
            frame_interval=self.config.get('extraction', 'frame_interval', 1),
            slide_threshold=self.config.get('extraction', 'slide_threshold', 0.95)
        )
        
        # 텍스트 추출기 초기화
        self.text_extractor = TextExtractor(
            output_dir=str(self.output_dir / 'texts')
        )
        
        # 중복 제거기 초기화
        self.deduplicator = Deduplicator(
            similarity_threshold=self.config.get('processing', 'similarity_threshold', 0.95),
            cache_size=self.config.get('processing', 'cache_size', 1000)
        )
        
        # 진행 상태 콜백
        self._progress_callback = None
        
    def set_progress_callback(self, callback: Callable[[int, str], bool]):
        """
        진행 상태 업데이트 콜백 설정
        
        Args:
            callback: 진행률(0-100)과 상태 메시지를 받는 콜백 함수
        """
        self._progress_callback = callback

    def _update_progress(self, progress: int, message: str) -> bool:
        """
        진행 상태 업데이트
        
        Args:
            progress: 진행률(0-100)
            message: 상태 메시지
            
        Returns:
            계속 진행 여부
        """
        if self._progress_callback:
            return self._progress_callback(progress, message)
        return True  # 콜백이 없으면 계속 진행

    def _download_youtube_video(self, url: str) -> Optional[str]:
        """
        YouTube 동영상 다운로드
        
        Args:
            url: YouTube URL
            
        Returns:
            다운로드된 동영상 파일 경로 또는 None
        """
        try:
            timestamp = int(time.time())
            output_path = str(self.download_dir / f"video_{timestamp}.mp4")
            
            ydl_opts = {
                'format': 'best[ext=mp4]',  # 최고 품질의 MP4
                'outtmpl': output_path,     # 출력 파일 경로
                'quiet': True,              # 진행 상태 출력 안 함
                'no_warnings': True         # 경고 메시지 출력 안 함
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
            if os.path.exists(output_path):
                return output_path
            return None
            
        except Exception as e:
            self.logger.error(f"YouTube 동영상 다운로드 중 오류 발생: {str(e)}")
            return None
        
    def _initialize_directories(self):
        """작업 디렉토리 초기화"""
        try:
            # 초기화할 디렉토리 목록
            work_dirs = [
                self.output_dir / 'downmovie',
                self.output_dir / 'images',
                self.output_dir / 'texts',
                self.output_dir / 'documents'
            ]
            
            # 각 작업 디렉토리 초기화
            for dir_path in work_dirs:
                # 기존 디렉토리가 있으면 삭제
                if dir_path.exists():
                    self.logger.info(f"기존 디렉토리 삭제 중: {dir_path}")
                    shutil.rmtree(dir_path)
                
                # 새 디렉토리 생성
                self.logger.info(f"새 디렉토리 생성 중: {dir_path}")
                dir_path.mkdir(parents=True, exist_ok=True)
            
            self.logger.info("작업 디렉토리 초기화 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"디렉토리 초기화 중 오류 발생: {str(e)}")
            return False

    def process_video(self, url: str) -> bool:
        """
        동영상 처리
        
        Args:
            url: YouTube URL
            
        Returns:
            처리 성공 여부
        """
        try:
            self.logger.info(f"동영상 처리 시작: {url}")
            if not self._update_progress(0, "동영상 처리 시작"):
                self.logger.info("사용자 요청으로 처리 중단")
                return False
            
            # 작업 디렉토리 초기화
            if not self._initialize_directories():
                self.logger.error("작업 디렉토리 초기화 실패")
                return False

            # 비디오 다운로드
            if not self._update_progress(10, "영상 다운로드 중..."):
                self.logger.info("사용자 요청으로 처리 중단")
                return False
            
            video_path = self._download_youtube_video(url)
            if not video_path:
                self.logger.error("동영상 다운로드 실패")
                return False

            if not self._update_progress(30, "이미지 추출 중..."):
                self.logger.info("사용자 요청으로 처리 중단")
                return False

            # 이미지 추출기 초기화 및 실행
            self.image_extractor = ImageExtractor(
                output_dir=str(self.output_dir / 'images'),
                frame_interval=self.config.get('extraction', 'frame_interval', 1),
                slide_threshold=self.config.get('extraction', 'slide_threshold', 0.95)
            )
            
            # 이미지 추출 시도
            try:
                extracted_frames = self.image_extractor.extract_frames(video_path)
                if not extracted_frames:
                    self.logger.error("이미지 추출 실패")
                    return False
            except Exception as e:
                self.logger.error(f"이미지 추출 중 오류 발생: {str(e)}")
                return False

            if not self._update_progress(60, "텍스트 추출 중..."):
                self.logger.info("사용자 요청으로 처리 중단")
                return False

            # 텍스트 추출기 초기화 및 실행
            self.text_extractor = TextExtractor(
                output_dir=str(self.output_dir / 'texts')
            )
            extracted_texts = self.text_extractor.extract_text(str(video_path))
            if not extracted_texts:
                self.logger.error("텍스트 추출 실패")
                return False

            if not self._update_progress(80, "문서 생성 중..."):
                self.logger.info("사용자 요청으로 처리 중단")
                return False

            # 문서 변환기 초기화 및 실행
            doc_converter = DocumentConverter(str(self.output_dir / 'documents'))
            # 모든 텍스트를 하나의 문자열로 결합
            combined_text = "\n\n".join(extracted_texts)
            doc_result = doc_converter.create_document(combined_text)
            if not doc_result:
                self.logger.error("문서 생성 실패")
                return False

            if not self._update_progress(90, "정리 중..."):
                self.logger.info("사용자 요청으로 처리 중단")
                return False

            # 설정에 따라 임시 파일 처리
            keep_video = self.config.get('processing', 'keep_video', False)
            if keep_video:
                # 영상 파일을 temp 디렉토리에 유지
                self.logger.info(f"영상 파일 유지됨: {video_path}")
            else:
                # 임시 파일 삭제
                if os.path.exists(video_path):
                    os.remove(video_path)
                    self.logger.info("임시 영상 파일 삭제됨")

            self.logger.info(f"동영상 처리 완료: {url}")
            self._update_progress(100, "처리 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"동영상 처리 중 오류 발생: {str(e)}")
            return False
            
    def process_videos(self, video_paths: List[str]) -> List[bool]:
        """
        여러 동영상 처리
        
        Args:
            video_paths: 동영상 파일 경로 목록
            
        Returns:
            각 동영상의 처리 성공 여부 목록
        """
        results = []
        for video_path in tqdm(video_paths, desc="동영상 처리"):
            result = self.process_video(video_path)
            results.append(result)
        return results 