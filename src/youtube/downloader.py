"""
YouTube video downloader module.
"""

import os
import logging
from typing import Optional, Tuple
from pathlib import Path
from pytube import YouTube
from tqdm import tqdm

from .validator import YouTubeValidator

class YouTubeDownloader:
    """YouTube 동영상 다운로더 클래스"""
    
    def __init__(self, output_path: str):
        """
        초기화 함수
        
        Args:
            output_path (str): 다운로드 파일 저장 경로
        """
        self.output_path = Path(output_path)
        
        # 출력 디렉토리 생성
        os.makedirs(self.output_path, exist_ok=True)
        
        # 로거 설정
        self.logger = logging.getLogger(__name__)
    
    def _on_progress(self, stream, chunk, bytes_remaining):
        """다운로드 진행률 콜백 함수"""
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage = (bytes_downloaded / total_size) * 100
        self.logger.info(f"다운로드 진행률: {percentage:.1f}%")
    
    def download_video(
        self,
        url: str,
        filename: Optional[str] = None,
        resolution: str = "720p"
    ) -> Tuple[bool, str]:
        """
        동영상 다운로드
        
        Args:
            url (str): YouTube 동영상 URL
            filename (Optional[str]): 저장 파일명 (기본값: 동영상 제목)
            resolution (str): 동영상 해상도
            
        Returns:
            Tuple[bool, str]: (성공 여부, 저장된 파일 경로)
        """
        try:
            # YouTube 객체 생성
            yt = YouTube(url)
            yt.register_on_progress_callback(self._on_progress)
            
            # 동영상 정보 로드
            self.logger.info(f"동영상 정보 로드 중: {yt.title}")
            
            # 해상도에 맞는 스트림 선택
            stream = yt.streams.filter(
                progressive=True,
                file_extension='mp4',
                resolution=resolution
            ).first()
            
            if not stream:
                self.logger.error(f"지원하지 않는 해상도: {resolution}")
                return False, ""
            
            # 파일명 설정
            if not filename:
                filename = f"{yt.title}.mp4"
                # 파일명 정규화
                filename = "".join(
                    c if c.isalnum() or c in (' ', '-', '_') else '_'
                    for c in filename
                )
            
            # 다운로드 경로 설정
            output_file = self.output_path / filename
            
            # 다운로드 진행
            self.logger.info(f"다운로드 시작: {filename}")
            with tqdm(total=stream.filesize, unit='B', unit_scale=True) as pbar:
                stream.download(
                    output_path=str(self.output_path),
                    filename=filename
                )
                pbar.update(stream.filesize)
            
            self.logger.info(f"다운로드 완료: {output_file}")
            return True, str(output_file)
            
        except Exception as e:
            self.logger.error(f"다운로드 중 오류 발생: {e}")
            return False, ""
    
    def get_video_info(self, url: str) -> Optional[dict]:
        """
        동영상 정보 조회
        
        Args:
            url (str): YouTube 동영상 URL
            
        Returns:
            Optional[dict]: 동영상 정보
        """
        try:
            # YouTube 객체 생성
            yt = YouTube(url)
            
            # 동영상 정보 반환
            return {
                'title': yt.title,
                'author': yt.author,
                'length': yt.length,
                'views': yt.views,
                'rating': yt.rating,
                'thumbnail_url': yt.thumbnail_url,
                'available_resolutions': [
                    stream.resolution
                    for stream in yt.streams.filter(
                        progressive=True,
                        file_extension='mp4'
                    )
                ]
            }
            
        except Exception as e:
            self.logger.error(f"동영상 정보 조회 중 오류 발생: {e}")
            return None

    def _get_best_stream(self, yt: YouTube) -> Optional[YouTube.streams.Stream]:
        """가장 적합한 스트림 선택"""
        try:
            # 비디오+오디오 스트림 중 최적의 해상도 선택
            streams = yt.streams.filter(progressive=True, file_extension='mp4')
            if not streams:
                # 비디오와 오디오를 따로 다운로드해야 하는 경우
                video_stream = yt.streams.filter(
                    only_video=True,
                    file_extension='mp4',
                    resolution=f'{self.max_resolution}p'
                ).first()
                
                audio_stream = yt.streams.filter(
                    only_audio=True,
                    file_extension='mp4'
                ).order_by('abr').desc().first()
                
                return (video_stream, audio_stream)
                
            return streams.order_by('resolution').desc().first()
            
        except Exception as e:
            self.logger.error(f"스트림 선택 중 오류 발생: {str(e)}")
            return None
    
    def download(self, url: str) -> Tuple[bool, Optional[str]]:
        """YouTube 영상 다운로드"""
        try:
            # URL 검증
            is_valid, video_id = YouTubeValidator.validate_and_extract(url)
            if not is_valid or not video_id:
                self.logger.error(f"유효하지 않은 YouTube URL: {url}")
                return False, None
            
            # YouTube 객체 생성
            yt = YouTube(url)
            yt.register_on_progress_callback(
                lambda stream, chunk, bytes_remaining: self._progress_callback(
                    stream, chunk, bytes_remaining, yt.filesize
                )
            )
            
            # 최적의 스트림 선택
            stream = self._get_best_stream(yt)
            if not stream:
                self.logger.error("적합한 스트림을 찾을 수 없습니다.")
                return False, None
            
            # 다운로드
            output_file = stream.download(
                output_path=self.output_path,
                filename=f"{video_id}.mp4"
            )
            
            self.logger.info(f"다운로드 완료: {output_file}")
            return True, output_file
            
        except Exception as e:
            self.logger.error(f"다운로드 중 오류 발생: {str(e)}")
            return False, None
    
    def _progress_callback(self, stream, chunk, bytes_remaining, total_size):
        """다운로드 진행률 콜백"""
        progress = (total_size - bytes_remaining) / total_size * 100
        print(f"\r다운로드 진행률: {progress:.1f}%", end="") 