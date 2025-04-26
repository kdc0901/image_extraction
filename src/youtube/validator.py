"""
YouTube URL validation module.
"""

import re
import logging
from typing import Tuple, Optional
from urllib.parse import urlparse, parse_qs

class YouTubeValidator:
    """YouTube URL 유효성 검사 클래스"""
    
    # YouTube URL 패턴
    YOUTUBE_URL_PATTERNS = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([^&]+)',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([^/?]+)',
        r'(?:https?://)?(?:www\.)?youtube\.com/v/([^/?]+)',
        r'(?:https?://)?(?:www\.)?youtube\.com/shorts/([^/?]+)',
        r'(?:https?://)?(?:www\.)?youtu\.be/([^/?]+)',
        r'(?:https?://)?(?:www\.)?youtube\.com/live/([^/?]+)'
    ]
    
    def __init__(self):
        """초기화 함수"""
        self.logger = logging.getLogger(__name__)
    
    @classmethod
    def validate_and_extract(cls, url: str) -> Tuple[bool, Optional[str]]:
        """
        URL 유효성 검사 및 비디오 ID 추출
        
        Args:
            url (str): YouTube URL
            
        Returns:
            Tuple[bool, Optional[str]]: (유효성 여부, 비디오 ID)
        """
        try:
            # URL 파싱
            parsed_url = urlparse(url)
            
            # YouTube 도메인 확인
            if not any(domain in parsed_url.netloc for domain in ['youtube.com', 'youtu.be']):
                return False, None
            
            # 비디오 ID 추출
            video_id = None
            
            # URL 패턴 매칭
            for pattern in cls.YOUTUBE_URL_PATTERNS:
                match = re.search(pattern, url)
                if match:
                    video_id = match.group(1)
                    break
            
            # 쿼리 파라미터에서 비디오 ID 추출
            if not video_id and parsed_url.query:
                query_params = parse_qs(parsed_url.query)
                video_id = query_params.get('v', [None])[0]
            
            # 비디오 ID 유효성 검사
            if not video_id or not cls._is_valid_video_id(video_id):
                return False, None
            
            return True, video_id
            
        except Exception as e:
            logging.error(f"URL 검증 중 오류 발생: {e}")
            return False, None
    
    @staticmethod
    def _is_valid_video_id(video_id: str) -> bool:
        """
        비디오 ID 유효성 검사
        
        Args:
            video_id (str): YouTube 비디오 ID
            
        Returns:
            bool: 유효성 여부
        """
        # 비디오 ID 길이 검사 (일반적으로 11자)
        if len(video_id) != 11:
            return False
        
        # 비디오 ID 문자 검사
        valid_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_')
        return all(c in valid_chars for c in video_id)
    
    @classmethod
    def is_valid_url(cls, url: str) -> bool:
        """
        URL 유효성 검사
        
        Args:
            url (str): YouTube URL
            
        Returns:
            bool: 유효성 여부
        """
        is_valid, _ = cls.validate_and_extract(url)
        return is_valid
    
    @classmethod
    def normalize_url(cls, url: str) -> Optional[str]:
        """
        URL 정규화
        
        Args:
            url (str): YouTube URL
            
        Returns:
            Optional[str]: 정규화된 URL
        """
        is_valid, video_id = cls.validate_and_extract(url)
        if not is_valid or not video_id:
            return None
        
        return f"https://www.youtube.com/watch?v={video_id}" 